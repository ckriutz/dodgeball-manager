"""
GameSimulator for simulating dodgeball games.

This module handles the turn-based combat simulation between two teams,
including skill calculations, random events, and stat tracking.

References:
- FR-029: Game must end when one team fully eliminated
- NFR-003: Deterministic simulation with seed
"""

from typing import List
import random
from datetime import datetime, timezone

from ..models.game import Game, GameEvent, GameEventType, GameStatus
from ..models.player import Player
from ..services.injury_service import InjuryService
from ..storage.memory_storage import MemoryStorage


class GameSimulator:
    """
    Simulates a dodgeball game between two teams.
    
    Uses deterministic random seeding for reproducible results.
    Implements turn-based combat with skill-based probabilities.
    """

    def __init__(self, game: Game, seed: int):
        """
        Initialize game simulator.
        
        Args:
            game: Game instance to simulate
            seed: Random seed for deterministic results
        """
        self.storage = MemoryStorage()
        self.injury_service = InjuryService()
        random.seed(seed)
        self.game = game
        self.active_team1: List[str] = list(game.team1_starters)
        self.active_team2: List[str] = list(game.team2_starters)
        self.turn = 0

    def get_player(self, player_id: str) -> Player:
        """
        Get player data from storage.
        
        Args:
            player_id: Player UUID string
            
        Returns:
            Player instance
        """
        player_data = self.storage.get_player(player_id)
        if player_data is None:
            raise ValueError(f"Player {player_id} not found")
        return Player(**player_data)

    def simulate(self) -> Game:
        """
        Simulate the complete dodgeball game.
        
        Implements turn-based combat until one team is eliminated.
        Updates player stats, team records, and game events.
        
        Returns:
            Completed Game instance with all events and results
        """
        # Mark game as in progress
        self.game.status = GameStatus.IN_PROGRESS
        
        while self.active_team1 and self.active_team2:
            self.turn += 1
            
            # Alternate throwing team starting with team1
            is_team1_throwing = self.turn % 2 == 1
            throwing_team = self.active_team1 if is_team1_throwing else self.active_team2
            defending_team = self.active_team2 if is_team1_throwing else self.active_team1

            # Determine thrower: highest throwing + iq
            thrower_id = max(
                throwing_team,
                key=lambda pid: self.get_player(pid).skills.throwing + self.get_player(pid).skills.iq
            )
            thrower = self.get_player(thrower_id)

            # Select random target
            target_id = random.choice(defending_team)
            target = self.get_player(target_id)

            # Calculate hit probability
            base = thrower.skills.throwing / 100.0
            mod_iq = (thrower.skills.iq - target.skills.iq) * 0.01
            mod_dodge = -target.skills.dodging * 0.01
            luck_var = (thrower.skills.luck - target.skills.luck) / 1000.0  # Small variance
            hit_prob = base + mod_iq + mod_dodge + random.uniform(-0.1, 0.1) + luck_var
            hit_prob = max(0.0, min(1.0, hit_prob))

            # Record throw attempt
            thrower.stats.throws_attempted += 1
            self.game.add_event(
                turn=self.turn,
                event_type=GameEventType.THROW,
                outcome=f"Player {thrower.name} throws at Player {target.name}",
                thrower_id=thrower_id,
                target_id=target_id
            )

            if random.random() < hit_prob:
                # Hit - target eliminated
                defending_team.remove(target_id)
                
                # Update stats
                thrower.stats.successful_hits += 1
                target.stats.times_hit += 1
                
                # Record hit event
                self.game.add_event(
                    turn=self.turn,
                    event_type=GameEventType.HIT,
                    outcome=f"Player {thrower.name} hits Player {target.name} - eliminated!",
                    thrower_id=thrower_id,
                    target_id=target_id
                )
                
                # Record elimination
                self.game.add_event(
                    turn=self.turn,
                    event_type=GameEventType.ELIMINATION,
                    outcome=f"Player {target.name} is eliminated",
                    target_id=target_id
                )

                # Check for injury (5% chance)
                if random.random() < 0.05:
                    injured_player = self.injury_service.apply_injury(target)
                    self.game.add_event(
                        turn=self.turn,
                        event_type=GameEventType.INJURY,
                        outcome=f"Player {target.name} injured: {injured_player.injury.severity.value}",
                        thrower_id=thrower_id,
                        target_id=target_id
                    )
                    # Update target with injury
                    target = injured_player

            else:
                # Miss - calculate catch probability
                catch_prob = target.skills.catching / 100.0 + random.uniform(-0.1, 0.1)
                catch_prob = max(0.0, min(1.0, catch_prob))

                if random.random() < catch_prob:
                    # Caught - thrower eliminated
                    throwing_team.remove(thrower_id)
                    
                    # Update stats
                    target.stats.catches_made += 1
                    thrower.stats.missed_throws += 1
                    
                    # Record catch event
                    self.game.add_event(
                        turn=self.turn,
                        event_type=GameEventType.CATCH,
                        outcome=f"Player {target.name} catches the throw - Player {thrower.name} eliminated!",
                        thrower_id=thrower_id,
                        target_id=target_id
                    )
                    
                    # Record elimination
                    self.game.add_event(
                        turn=self.turn,
                        event_type=GameEventType.ELIMINATION,
                        outcome=f"Player {thrower.name} is eliminated",
                        target_id=thrower_id
                    )
                    
                else:
                    # Complete miss
                    thrower.stats.missed_throws += 1
                    
                    # Record miss event
                    self.game.add_event(
                        turn=self.turn,
                        event_type=GameEventType.MISS,
                        outcome=f"Player {thrower.name}'s throw misses Player {target.name}",
                        thrower_id=thrower_id,
                        target_id=target_id
                    )

        # Determine winner and complete game
        winner_id = self.game.team1_id if self.active_team1 else self.game.team2_id
        
        self.game.complete_game(winner_id)
        
        # Update all modified players in storage
        all_player_ids = set(self.game.team1_starters + self.game.team2_starters)
        for player_id in all_player_ids:
            player = self.get_player(player_id)
            self.storage.update_player(player_id, player.model_dump())

        return self.game
