"""
GameSimulator for simulating dodgeball games.

This module handles the turn-based combat simulation between two teams,
including skill calculations, random events, and stat tracking.

References:
- FR-029: Game must end when one team fully eliminated
- NFR-003: Deterministic simulation with seed
"""

from typing import List, Dict
import random
import logging
from datetime import datetime, timezone

from ..models.game import Game, GameEvent, GameEventType, GameStatus
from ..models.player import Player
from ..services.injury_service import InjuryService
from ..storage.memory_storage import MemoryStorage

logger = logging.getLogger(__name__)


class GameSimulator:
    """
    Simulates a dodgeball game between two teams.
    
    Uses deterministic random seeding for reproducible results.
    Implements turn-based combat with skill-based probabilities.
    """
    
    # Game configuration constants
    MAX_TURNS = 1000  # Prevent infinite loops
    HIT_RANDOM_VARIANCE = 0.1
    CATCH_RANDOM_VARIANCE = 0.1
    INJURY_CHANCE = 0.05
    IQ_MODIFIER_SCALE = 0.01
    DODGE_MODIFIER_SCALE = 0.01
    LUCK_MODIFIER_SCALE = 0.001
    SPEED_THROWING_WEIGHT = 0.5  # Speed contribution to throw order
    SPEED_DODGE_WEIGHT = 0.3  # Speed contribution to dodging

    def __init__(self, game: Game, seed: int):
        """
        Initialize game simulator.
        
        Args:
            game: Game instance to simulate
            seed: Random seed for deterministic results
            
        Raises:
            ValueError: If game is not ready to start
        """
        self.storage = MemoryStorage()
        self.injury_service = InjuryService()
        random.seed(seed)
        self.game = game
        self.active_team1: List[str] = list(game.team1_starters)
        self.active_team2: List[str] = list(game.team2_starters)
        self.turn = 0
        
        # Cache players to avoid repeated fetches and ensure stat updates persist
        self.player_cache: Dict[str, Player] = {}
        self._load_players()
        
        # Cache team names for event descriptions
        team1_data = self.storage.get_team(game.team1_id)
        team2_data = self.storage.get_team(game.team2_id)
        self.team1_name = team1_data['name'] if team1_data else 'Team 1'
        self.team2_name = team2_data['name'] if team2_data else 'Team 2'

    def _load_players(self) -> None:
        """
        Load all players into cache once.
        
        Raises:
            ValueError: If any player is not found in storage
        """
        all_player_ids = set(self.game.team1_starters + self.game.team2_starters)
        for player_id in all_player_ids:
            player_data = self.storage.get_player(player_id)
            if player_data is None:
                raise ValueError(f"Player {player_id} not found")
            self.player_cache[player_id] = Player(**player_data)

    def get_player(self, player_id: str) -> Player:
        """
        Get player from cache.
        
        Args:
            player_id: Player UUID string
            
        Returns:
            Player instance from cache
            
        Raises:
            ValueError: If player not in game
        """
        if player_id not in self.player_cache:
            raise ValueError(f"Player {player_id} not in game")
        return self.player_cache[player_id]

    def calculate_hit_probability(self, thrower: Player, target: Player) -> float:
        """
        Calculate probability of thrower hitting target.
        
        Formula considers:
        - Thrower's throwing skill (base accuracy)
        - IQ differential (smart throwers, dumb targets = better hit)
        - Target's dodging skill (high dodge = harder to hit)
        - Target's speed (faster players dodge better)
        - Luck differential (small random variance)
        - Random variance (10% swing)
        
        Args:
            thrower: Player throwing the ball
            target: Player being targeted
            
        Returns:
            Hit probability between 0.0 and 1.0
        """
        base = thrower.skills.throwing / 100.0
        mod_iq = (thrower.skills.iq - target.skills.iq) * self.IQ_MODIFIER_SCALE
        mod_dodge = -(target.skills.dodging + target.skills.speed * self.SPEED_DODGE_WEIGHT) * self.DODGE_MODIFIER_SCALE
        luck_var = (thrower.skills.luck - target.skills.luck) * self.LUCK_MODIFIER_SCALE
        
        hit_prob = (
            base + 
            mod_iq + 
            mod_dodge + 
            random.uniform(-self.HIT_RANDOM_VARIANCE, self.HIT_RANDOM_VARIANCE) + 
            luck_var
        )
        
        return max(0.0, min(1.0, hit_prob))

    def calculate_catch_probability(self, player: Player) -> float:
        """
        Calculate probability of player catching the ball.
        
        Args:
            player: Player attempting to catch
            
        Returns:
            Catch probability between 0.0 and 1.0
        """
        catch_prob = player.skills.catching / 100.0 + random.uniform(-self.CATCH_RANDOM_VARIANCE, self.CATCH_RANDOM_VARIANCE)
        return max(0.0, min(1.0, catch_prob))

    def select_ball_picker(self) -> tuple[str, List[str], List[str], float, str]:
        """
        Determine which player picks up the ball based on IQ, speed, and luck.
        
        All active players from both teams compete for the ball each turn.
        Formula: random(IQ/2, IQ) + speed + random(0, luck)
        Higher IQ players have both higher minimum and maximum random values.
        
        Returns:
            Tuple of (thrower_id, throwing_team, defending_team, score, team_name)
        """
        all_active = self.active_team1 + self.active_team2
        
        # Calculate pickup score for each player
        scores = []
        for player_id in all_active:
            player = self.get_player(player_id)
            
            # IQ component: random from half of IQ to full IQ
            iq_min = player.skills.iq / 2
            iq_component = random.uniform(iq_min, player.skills.iq)
            
            # Full formula
            score = (
                iq_component +
                player.skills.speed +
                random.uniform(0, player.skills.luck)
            )
            scores.append((player_id, score, player.name))
        
        # Log all scores for debugging
        logger.debug(f"Turn {self.turn + 1} ball pickup scores:")
        for player_id, score, name in sorted(scores, key=lambda x: x[1], reverse=True):
            player = self.get_player(player_id)
            team_label = "Team1" if player_id in self.active_team1 else "Team2"
            logger.debug(
                f"  [{team_label}] {name}: {score:.2f} "
                f"(IQ:{player.skills.iq} Speed:{player.skills.speed} Luck:{player.skills.luck})"
            )
        
        # Find player with highest score
        winner = max(scores, key=lambda x: x[1])
        thrower_id = winner[0]
        winner_name = winner[2]
        winner_score = winner[1]
        
        # Determine which team has the ball
        if thrower_id in self.active_team1:
            throwing_team = self.active_team1
            defending_team = self.active_team2
            team_name = self.team1_name
        else:
            throwing_team = self.active_team2
            defending_team = self.active_team1
            team_name = self.team2_name
        
        logger.debug(f"  *** {winner_name} ({team_name}) wins the ball with score {winner_score:.2f} ***")
        
        return thrower_id, throwing_team, defending_team, winner_score, team_name

    def record_throw(self, thrower: Player, target: Player) -> None:
        """
        Record a throw attempt event.
        
        Args:
            thrower: Player throwing the ball
            target: Player being targeted
        """
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.THROW,
            outcome=f"Player {thrower.name} throws at Player {target.name}",
            thrower_id=thrower.id,
            target_id=target.id
        )

    def record_hit(self, thrower: Player, target: Player) -> None:
        """
        Record a successful hit event.
        
        Args:
            thrower: Player who threw the ball
            target: Player who was hit
        """
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.HIT,
            outcome=f"Player {thrower.name} hits Player {target.name} - eliminated!",
            thrower_id=thrower.id,
            target_id=target.id
        )

    def record_catch(self, catcher: Player, thrower: Player) -> None:
        """
        Record a successful catch event.
        
        Args:
            catcher: Player who caught the ball
            thrower: Player who threw the ball (and gets eliminated)
        """
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.CATCH,
            outcome=f"Player {catcher.name} catches the throw - Player {thrower.name} eliminated!",
            thrower_id=thrower.id,
            target_id=catcher.id
        )

    def record_miss(self, thrower: Player, target: Player) -> None:
        """
        Record a miss event.
        
        Args:
            thrower: Player who threw the ball
            target: Player who was targeted but not hit
        """
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.MISS,
            outcome=f"Player {thrower.name}'s throw misses Player {target.name}",
            thrower_id=thrower.id,
            target_id=target.id
        )

    def record_elimination(self, player: Player, reason: str) -> None:
        """
        Record a player elimination event.
        
        Args:
            player: Player being eliminated
            reason: Reason for elimination ("hit" or "caught")
        """
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.ELIMINATION,
            outcome=f"Player {player.name} is eliminated ({reason})",
            target_id=player.id
        )

    def record_injury(self, injured_player: Player, thrower: Player) -> None:
        """
        Record an injury event.
        
        Args:
            injured_player: Player who was injured
            thrower: Player who caused the injury
        """
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.INJURY,
            outcome=f"Player {injured_player.name} injured: {injured_player.injury.severity.value}",
            thrower_id=thrower.id,
            target_id=injured_player.id
        )

    def simulate(self) -> Game:
        """
        Simulate the complete dodgeball game.
        
        Implements turn-based combat until one team is eliminated.
        Updates player stats, team records, and game events.
        
        Returns:
            Completed Game instance with all events and results
            
        Raises:
            ValueError: If game is not ready to start
        """
        # Validate game is ready
        if self.game.status != GameStatus.SCHEDULED:
            raise ValueError(f"Game must be SCHEDULED to simulate, got {self.game.status}")
        
        if len(self.active_team1) != 5 or len(self.active_team2) != 5:
            raise ValueError("Both teams must have exactly 5 starters")
        
        # Mark game as in progress
        self.game.status = GameStatus.IN_PROGRESS
        logger.info(f"Starting game simulation with seed {self.game.seed}")
        
        # Main game loop
        while self.active_team1 and self.active_team2 and self.turn < self.MAX_TURNS:
            self.turn += 1
            
            # Determine who picks up the ball based on IQ, speed, and luck
            thrower_id, throwing_team, defending_team, pickup_score, team_name = self.select_ball_picker()
            thrower = self.get_player(thrower_id)
            
            # Record ball pickup event with score and team name
            self.game.add_event(
                turn=self.turn,
                event_type=GameEventType.BALL_PICKUP,
                outcome=f"{thrower.name} ({team_name}) picks up the ball with a score of {pickup_score:.1f}",
                thrower_id=thrower_id
            )

            # Select random target
            target_id = random.choice(defending_team)
            target = self.get_player(target_id)

            # Calculate hit probability
            hit_prob = self.calculate_hit_probability(thrower, target)

            # Log turn details for debugging
            logger.debug(
                f"Turn {self.turn}: {thrower.name} throws at {target.name} "
                f"(hit_prob={hit_prob:.2%})"
            )

            # Record throw attempt
            thrower.stats.throws_attempted += 1
            self.record_throw(thrower, target)

            if random.random() < hit_prob:
                # Hit - target eliminated
                defending_team.remove(target_id)
                
                # Update stats
                thrower.stats.successful_hits += 1
                target.stats.times_hit += 1
                
                # Record hit and elimination
                self.record_hit(thrower, target)
                self.record_elimination(target, "hit")

                # Check for injury
                if random.random() < self.INJURY_CHANCE:
                    self.player_cache[target_id] = self.injury_service.apply_injury(target)
                    self.record_injury(self.player_cache[target_id], thrower)
                    logger.debug(f"Player {target.name} injured!")

            else:
                # Miss - calculate catch probability
                catch_prob = self.calculate_catch_probability(target)
                
                logger.debug(f"Miss! Catch probability: {catch_prob:.2%}")

                if random.random() < catch_prob:
                    # Caught - thrower eliminated
                    throwing_team.remove(thrower_id)
                    
                    # Update stats
                    target.stats.catches_made += 1
                    thrower.stats.missed_throws += 1
                    
                    # Record catch and elimination
                    self.record_catch(target, thrower)
                    self.record_elimination(thrower, "caught")
                    
                else:
                    # Complete miss
                    thrower.stats.missed_throws += 1
                    self.record_miss(thrower, target)

        # Check if game ended due to turn limit
        if self.turn >= self.MAX_TURNS:
            logger.warning(f"Game reached max turns ({self.MAX_TURNS}), forcing completion")
            # Determine winner based on remaining players
            if len(self.active_team1) > len(self.active_team2):
                winner_id = self.game.team1_id
            elif len(self.active_team2) > len(self.active_team1):
                winner_id = self.game.team2_id
            else:
                # Tie - team1 wins by default
                winner_id = self.game.team1_id
                logger.info("Game tied, team1 wins by default")
        else:
            # Determine winner normally
            winner_id = self.game.team1_id if self.active_team1 else self.game.team2_id
        
        # Complete game
        self.game.complete_game(winner_id)
        
        # Add game_end event
        self.game.add_event(
            turn=self.turn,
            event_type=GameEventType.GAME_END,
            outcome=f"Game ended after {self.turn} turns. Winner: {winner_id}"
        )
        
        logger.info(f"Game completed in {self.turn} turns, winner: {winner_id}")
        
        # Increment games_played for all starters who participated
        all_starter_ids = self.game.team1_starters + self.game.team2_starters
        for player_id in all_starter_ids:
            player = self.player_cache[player_id]
            player.stats.games_played += 1
        
        # Update all modified players in storage from cache
        for player_id, player in self.player_cache.items():
            self.storage.update_player(player_id, player.model_dump())

        return self.game
