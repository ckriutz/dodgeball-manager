"""
PlayerService for managing player operations.

This service handles player generation, retrieval, and management operations.
It uses the in-memory storage backend and implements business logic for
player-related operations.

References:
- FR-001: Players aged 18-20 with 10 skill points
- FR-002: Sum of all skills must equal 10
- FR-003: Each skill must be 0-100
- FR-004: Player value calculation
"""

import random
from typing import List, Optional
from uuid import uuid4

from ..models.player import Player, PlayerCreate, PlayerSkills
from ..storage.memory_storage import MemoryStorage
from .utils import (
    distribute_skill_points,
    generate_random_age,
    calculate_player_value,
    get_random_player_name,
)


class PlayerService:
    """Service for player-related operations."""

    def __init__(self, storage: Optional[MemoryStorage] = None):
        """
        Initialize PlayerService.
        
        Args:
            storage: Optional storage instance (defaults to singleton)
        """
        self.storage = storage or MemoryStorage()

    def generate_players(self, count: int, league_id: Optional[str] = None) -> List[Player]:
        """
        Generate multiple players with random attributes.
        
        Args:
            count: Number of players to generate
            league_id: Optional league ID to associate players with
            
        Returns:
            List of generated Player instances
            
        Raises:
            ValueError: If count is not between 1-100
        """
        if not (1 <= count <= 100):
            raise ValueError(f"Player count must be between 1-100, got {count}")

        # Get existing player count to continue numbering
        existing_players = self.get_players_by_league(league_id) if league_id else []
        start_number = len(existing_players) + 1

        players = []
        for i in range(count):
            player = self._generate_single_player(start_number + i, league_id=league_id)
            # Storage creates the ID, so we need to store first then recreate with correct ID
            player_dict = player.model_dump()
            player_id = self.storage.create_player(player_dict)
            # Get the player back with the correct ID from storage
            player_data = self.storage.get_player(player_id)
            player = Player(**player_data)
            players.append(player)

        return players

    def _generate_single_player(self, number: int, league_id: Optional[str] = None) -> Player:
        """
        Generate a single player with random attributes.
        
        Args:
            number: Player number for naming
            league_id: Optional league ID to associate player with
            
        Returns:
            Generated Player instance
        """
        # Generate random age (18-20 for new players - FR-001)
        age = generate_random_age(min_age=18, max_age=20)

        # Distribute 10 skill points randomly (FR-002)
        skill_values = distribute_skill_points(total_points=10, num_skills=6)
        skills = PlayerSkills(**skill_values)

        # Calculate player value (FR-004)
        value = calculate_player_value(skill_values, age)

        # Get random unique player name
        name = get_random_player_name()

        # Create player
        player_create = PlayerCreate(
            name=name,
            age=age,
            avatar=f"avatar-{random.randint(1, 14)}",  # 14 different avatar placeholders
            skills=skills,
            league_id=league_id
        )

        return player_create.to_player()

    def get_player(self, player_id: str) -> Optional[Player]:
        """
        Get a player by ID.
        
        Args:
            player_id: Player UUID
            
        Returns:
            Player instance or None if not found
        """
        player_data = self.storage.get_player(player_id)
        if player_data is None:
            return None

        # Convert storage dict to Player model
        return Player(**player_data)

    def get_players_by_league(
        self,
        league_id: str,
        free_agents_only: bool = False
    ) -> List[Player]:
        """
        Get all players in a league.
        
        Args:
            league_id: League UUID
            free_agents_only: If True, only return players without teams
            
        Returns:
            List of Player instances in the specified league
        """
        all_players = self.storage.list_players()

        players = []
        for player_data in all_players:
            player = Player(**player_data)

            # Filter by league_id - CRITICAL: only return players from this league
            if player.league_id != league_id:
                continue

            # Filter by free agent status if requested
            if free_agents_only and not player.is_free_agent():
                continue

            players.append(player)

        return players

    def get_all_players(self) -> List[Player]:
        """
        Get all players in the system.
        
        Returns:
            List of all Player instances
        """
        all_players = self.storage.list_players()
        return [Player(**player_data) for player_data in all_players]

    def get_free_agents(self) -> List[Player]:
        """
        Get all free agent players (not assigned to any team).
        
        Returns:
            List of free agent Player instances
        """
        all_players = self.get_all_players()
        return [player for player in all_players if player.is_free_agent()]

    def assign_player_to_team(self, player_id: str, team_id: str) -> Player:
        """
        Assign a player to a team.
        
        Args:
            player_id: Player UUID
            team_id: Team UUID
            
        Returns:
            Updated Player instance
            
        Raises:
            ValueError: If player not found
        """
        player = self.get_player(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found")

        player.assign_to_team(team_id)

        # Update storage
        self.storage.update_player(player_id, player.model_dump())

        return player

    def release_player_from_team(self, player_id: str) -> Player:
        """
        Release a player from their team.
        
        Args:
            player_id: Player UUID
            
        Returns:
            Updated Player instance
            
        Raises:
            ValueError: If player not found
        """
        player = self.get_player(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found")

        player.release_from_team()

        # Update storage
        self.storage.update_player(player_id, player.model_dump())

        return player

    def set_starter_status(self, player_id: str, is_starter: bool) -> Player:
        """
        Set whether a player is a starter.
        
        Args:
            player_id: Player UUID
            is_starter: True if player should be a starter
            
        Returns:
            Updated Player instance
            
        Raises:
            ValueError: If player not found or if trying to make free agent a starter
        """
        player = self.get_player(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found")

        player.set_starter_status(is_starter)

        # Update storage
        self.storage.update_player(player_id, player.model_dump())

        return player

    def update_player_stats(
        self,
        player_id: str,
        throws_attempted: int = 0,
        catches_made: int = 0,
        times_hit: int = 0,
        missed_throws: int = 0,
        successful_hits: int = 0
    ) -> Player:
        """
        Update player statistics after a game.
        
        Args:
            player_id: Player UUID
            throws_attempted: Number of throws made
            catches_made: Number of successful catches
            times_hit: Number of times eliminated
            missed_throws: Number of missed throws
            successful_hits: Number of successful eliminations
            
        Returns:
            Updated Player instance
            
        Raises:
            ValueError: If player not found
        """
        player = self.get_player(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found")

        player.update_stats(
            throws_attempted=throws_attempted,
            catches_made=catches_made,
            times_hit=times_hit,
            missed_throws=missed_throws,
            successful_hits=successful_hits
        )

        # Update storage
        self.storage.update_player(player_id, player.model_dump())

        return player

    def count_players(self) -> int:
        """
        Get total number of players in the system.
        
        Returns:
            Total player count
        """
        return len(self.storage.list_players())

    def count_free_agents(self) -> int:
        """
        Get number of free agent players.
        
        Returns:
            Free agent count
        """
        return len(self.get_free_agents())

    def delete_player(self, player_id: str) -> bool:
        """
        Delete a player from the system.
        
        Args:
            player_id: Player UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete_player(player_id)
