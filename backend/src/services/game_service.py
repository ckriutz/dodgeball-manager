"""
GameService for managing game operations.

This service handles game creation, simulation, and retrieval operations.
It coordinates with TeamService and PlayerService to ensure proper game setup.

References:
- FR-026: Both teams must have 5 starters
- FR-029: Game must end when one team fully eliminated
- NFR-003: Deterministic simulation with seed
- T103: Award XP to players after game simulation
"""

from typing import List, Optional, Dict, Any
import random
from datetime import datetime, timezone

from ..models.game import Game, GameCreate, GameResponse, GameSummary
from ..models.team import Team
from ..models.player import Player
from ..storage.memory_storage import MemoryStorage
from .team_service import TeamService
from .player_service import PlayerService
from .stats_service import StatsService
from .game_simulator import GameSimulator
from .skill_progression import calculate_game_xp


class GameService:
    """Service for game-related operations."""

    def __init__(
        self,
        storage: Optional[MemoryStorage] = None,
        team_service: Optional[TeamService] = None,
        player_service: Optional[PlayerService] = None,
        stats_service: Optional[StatsService] = None
    ):
        """
        Initialize GameService.
        
        Args:
            storage: Optional storage instance (defaults to singleton)
            team_service: Optional TeamService instance
            player_service: Optional PlayerService instance
            stats_service: Optional StatsService instance
        """
        self.storage = storage or MemoryStorage()
        self.team_service = team_service or TeamService(storage=self.storage)
        self.player_service = player_service or PlayerService(storage=self.storage)
        self.stats_service = stats_service or StatsService()

    def create_and_simulate_game(
        self,
        league_id: str,
        team1_id: str,
        team2_id: str,
        seed: Optional[int] = None
    ) -> Game:
        """
        Create a new game between two teams and simulate it immediately.
        
        Args:
            league_id: League UUID
            team1_id: First team UUID
            team2_id: Second team UUID
            seed: Optional random seed for deterministic simulation
            
        Returns:
            Completed Game instance
            
        Raises:
            ValueError: If teams don't exist, aren't in league, or don't have starters
        """
        game, _ = self.create_and_simulate_game_with_xp(league_id, team1_id, team2_id, seed)
        return game

    def create_and_simulate_game_with_xp(
        self,
        league_id: str,
        team1_id: str,
        team2_id: str,
        seed: Optional[int] = None
    ) -> tuple[Game, Dict[str, Any]]:
        """
        Create a new game between two teams, simulate it, and return XP results.
        
        Args:
            league_id: League UUID
            team1_id: First team UUID
            team2_id: Second team UUID
            seed: Optional random seed for deterministic simulation
            
        Returns:
            Tuple of (Completed Game instance, XP results dictionary)
            XP results format:
            {
                "xp_awards": {player_id: {"xp_earned": int, "levels_gained": int, "new_level": int}},
                "level_ups": [list of player_ids who leveled up]
            }
            
        Raises:
            ValueError: If teams don't exist, aren't in league, or don't have starters
        """
        # Validate teams are different
        if team1_id == team2_id:
            raise ValueError("Cannot simulate a game between the same team")
        
        # Validate teams exist
        team1 = self.team_service.get_team(team1_id)
        team2 = self.team_service.get_team(team2_id)
        
        if team1 is None:
            raise ValueError(f"Team {team1_id} not found")
        if team2 is None:
            raise ValueError(f"Team {team2_id} not found")
        
        # Validate teams are in the same league
        if team1.league_id != league_id:
            raise ValueError(f"Team {team1_id} is not in league {league_id}")
        if team2.league_id != league_id:
            raise ValueError(f"Team {team2_id} is not in league {league_id}")
        
        # Validate teams have exactly 5 starters (FR-026)
        if len(team1.starter_ids) != 5:
            raise ValueError(f"Team {team1_id} must have exactly 5 starters")
        if len(team2.starter_ids) != 5:
            raise ValueError(f"Team {team2_id} must have exactly 5 starters")
        
        # Create game
        game_create = GameCreate(
            league_id=league_id,
            team1_id=team1_id,
            team2_id=team2_id,
            seed=seed
        )
        
        game = game_create.to_game(
            team1_starters=team1.starter_ids,
            team2_starters=team2.starter_ids
        )
        
        # Store game and get the actual ID assigned by storage
        game_id = self.storage.create_game(game.model_dump())
        
        # Update game with correct ID from storage
        game_dict = game.model_dump()
        game_dict['id'] = game_id
        game = Game(**game_dict)
        
        # Simulate the game and get XP results
        simulated_game, xp_results = self.simulate_game_with_xp(game_id)
        
        return simulated_game, xp_results

    def simulate_game(self, game_id: str) -> Game:
        """
        Simulate a game that has been created.
        
        Args:
            game_id: Game UUID
            
        Returns:
            Completed Game instance
            
        Raises:
            ValueError: If game not found or not ready to simulate
        """
        game, _ = self.simulate_game_with_xp(game_id)
        return game

    def simulate_game_with_xp(self, game_id: str) -> tuple[Game, Dict[str, Any]]:
        """
        Simulate a game and return XP results.
        
        Args:
            game_id: Game UUID
            
        Returns:
            Tuple of (Completed Game instance, XP results dictionary)
            XP results format:
            {
                "xp_awards": {player_id: {"xp_earned": int, "levels_gained": int, "new_level": int}},
                "level_ups": [list of player_ids who leveled up]
            }
            
        Raises:
            ValueError: If game not found or not ready to simulate
        """
        game = self.get_game(game_id)
        if game is None:
            raise ValueError(f"Game {game_id} not found")
        
        if not game.is_ready_to_start():
            raise ValueError(f"Game {game_id} is not ready to start")
        
        # Use the game's seed or generate a random one
        seed = game.seed
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
            game.seed = seed
        
        # Create simulator and run simulation
        simulator = GameSimulator(game, seed)
        completed_game = simulator.simulate()
        
        # Update player and team stats, and award XP
        # This also populates completed_game.player_xp_awards and player_level_ups
        xp_results = self._update_stats_after_game(completed_game)
        
        # Update storage with completed game (including XP awards and level-ups)
        self.storage.update_game(game_id, completed_game.model_dump())
        
        return completed_game, xp_results

    def get_game(self, game_id: str) -> Optional[Game]:
        """
        Get a game by ID.
        
        Args:
            game_id: Game UUID
            
        Returns:
            Game instance or None if not found
        """
        game_data = self.storage.get_game(game_id)
        if game_data is None:
            return None

        return Game(**game_data)

    def get_all_games(self, league_id: Optional[str] = None) -> List[Game]:
        """
        Get all games, optionally filtered by league.
        
        Args:
            league_id: Optional league UUID filter
            
        Returns:
            List of Game instances
        """
        all_games = self.storage.list_games(league_id=league_id)
        return [Game(**game_data) for game_data in all_games]

    def get_games_by_team(self, team_id: str) -> List[Game]:
        """
        Get all games involving a specific team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            List of Game instances
        """
        all_games = self.get_all_games()
        return [
            game for game in all_games
            if game.team1_id == team_id or game.team2_id == team_id
        ]

    def _update_stats_after_game(self, game: Game) -> Dict[str, Any]:
        """
        Update player and team statistics after a game completes.
        Awards XP to all participating players based on performance.
        Also updates the game entity with XP awards and level-ups.
        
        Args:
            game: Completed Game instance
            
        Returns:
            Dictionary with XP awards and level-ups for each player
            {
                "xp_awards": {player_id: {"xp_earned": int, "levels_gained": int, "new_level": int}},
                "level_ups": [list of player_ids who leveled up]
            }
        """
        xp_results = {
            "xp_awards": {},
            "level_ups": []
        }
        
        # Update team records
        winner_id = game.winner_id
        loser_id = game.get_loser_id()
        
        if winner_id:
            winner_team = self.team_service.get_team(winner_id)
            if winner_team:
                self.stats_service.update_team_record(winner_team, is_win=True)
                self.storage.update_team(winner_id, winner_team.model_dump())
        
        if loser_id:
            loser_team = self.team_service.get_team(loser_id)
            if loser_team:
                self.stats_service.update_team_record(loser_team, is_win=False)
                self.storage.update_team(loser_id, loser_team.model_dump())
        
        # Award XP to all starters from both teams
        # Get player stats from the game events
        player_game_stats = self._extract_player_stats_from_game(game)
        
        all_starters = game.team1_starters + game.team2_starters
        for player_id in all_starters:
            player = self.player_service.get_player(player_id)
            if not player:
                continue
            
            # Determine if player was on winning team
            is_winner = (
                (player_id in game.team1_starters and game.winner_id == game.team1_id) or
                (player_id in game.team2_starters and game.winner_id == game.team2_id)
            )
            
            # Get player's stats from this game
            stats = player_game_stats.get(player_id, {
                "throws_attempted": 0,
                "catches_made": 0,
                "successful_hits": 0,
                "times_hit": 0
            })
            
            # Calculate XP earned
            xp_earned = calculate_game_xp(
                throws_attempted=stats["throws_attempted"],
                catches_made=stats["catches_made"],
                successful_hits=stats["successful_hits"],
                times_hit=stats["times_hit"],
                is_winner=is_winner
            )
            
            # Award XP and track level-ups
            old_level = player.stats.level
            levels_gained = player.stats.award_xp(xp_earned)
            new_level = player.stats.level
            
            # Record XP award on the game entity (T116)
            game.award_player_xp(player_id, xp_earned)
            
            # Record level-up on the game entity if player leveled up (T116)
            if levels_gained > 0:
                game.record_player_level_up(player_id, new_level)
            
            # Store XP results
            xp_results["xp_awards"][player_id] = {
                "xp_earned": xp_earned,
                "levels_gained": levels_gained,
                "new_level": new_level,
                "old_level": old_level
            }
            
            if levels_gained > 0:
                xp_results["level_ups"].append(player_id)
            
            # Update player in storage
            self.storage.update_player(player_id, player.model_dump())
        
        return xp_results

    def _extract_player_stats_from_game(self, game: Game) -> Dict[str, Dict[str, int]]:
        """
        Extract per-player statistics from game events.
        
        This method analyzes game events to determine each player's
        performance stats for XP calculation.
        
        Args:
            game: Completed Game instance
            
        Returns:
            Dictionary mapping player_id to their game stats
        """
        stats = {}
        
        # Initialize stats for all starters
        for player_id in game.team1_starters + game.team2_starters:
            stats[player_id] = {
                "throws_attempted": 0,
                "catches_made": 0,
                "successful_hits": 0,
                "times_hit": 0
            }
        
        # Parse events to count stats
        for event in game.events:
            if event.type.value == "throw":
                # Thrower made a throw attempt
                if event.thrower_id and event.thrower_id in stats:
                    stats[event.thrower_id]["throws_attempted"] += 1
            
            elif event.type.value == "hit":
                # Thrower got a successful hit, target was hit
                if event.thrower_id and event.thrower_id in stats:
                    stats[event.thrower_id]["successful_hits"] += 1
                if event.target_id and event.target_id in stats:
                    stats[event.target_id]["times_hit"] += 1
            
            elif event.type.value == "catch":
                # Target caught the ball
                if event.target_id and event.target_id in stats:
                    stats[event.target_id]["catches_made"] += 1
        
        return stats

    def count_games(self) -> int:
        """
        Get total number of games in the system.
        
        Returns:
            Total game count
        """
        return len(self.storage.list_games())