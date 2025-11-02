"""
GameService for managing game operations.

This service handles game creation, simulation, and retrieval operations.
It coordinates with TeamService and PlayerService to ensure proper game setup.

References:
- FR-026: Both teams must have 5 starters
- FR-029: Game must end when one team fully eliminated
- NFR-003: Deterministic simulation with seed
"""

from typing import List, Optional
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
        
        # Simulate the game
        simulated_game = self.simulate_game(game_id)
        
        return simulated_game

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
        
        # Update storage with completed game
        self.storage.update_game(game_id, completed_game.model_dump())
        
        # Update player and team stats
        self._update_stats_after_game(completed_game)
        
        return completed_game

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

    def _update_stats_after_game(self, game: Game) -> None:
        """
        Update player and team statistics after a game completes.
        
        Args:
            game: Completed Game instance
        """
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
        
        # Player stats are updated by the GameSimulator during simulation
        # The simulator already updates the storage, so no additional work needed here

    def count_games(self) -> int:
        """
        Get total number of games in the system.
        
        Returns:
            Total game count
        """
        return len(self.storage.list_games())