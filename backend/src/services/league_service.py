"""
LeagueService for managing league operations.

This service handles league creation, retrieval, and management operations.
It coordinates with PlayerService for player generation and team management.

References:
- FR-001: League setup with 50-100 players
- FR-005: Team management and draft
"""

from typing import List, Optional

from ..models.league import League, LeagueCreate, LeagueStandings, StandingsEntry
from ..models.player import Player
from ..storage.memory_storage import MemoryStorage
from .player_service import PlayerService


class LeagueService:
    """Service for league-related operations."""

    def __init__(
        self,
        storage: Optional[MemoryStorage] = None,
        player_service: Optional[PlayerService] = None
    ):
        """
        Initialize LeagueService.
        
        Args:
            storage: Optional storage instance (defaults to singleton)
            player_service: Optional PlayerService instance
        """
        self.storage = storage or MemoryStorage()
        self.player_service = player_service or PlayerService(storage=self.storage)

    def create_league(self, league_create: LeagueCreate) -> League:
        """
        Create a new league.
        
        Args:
            league_create: League creation schema
            
        Returns:
            Created League instance
        """
        league = league_create.to_league()

        # Store league and get the actual ID assigned by storage
        league_id = self.storage.create_league(league.model_dump())
        
        # Update league with correct ID from storage
        league_dict = league.model_dump()
        league_dict['id'] = league_id
        league = League(**league_dict)

        return league

    def get_league(self, league_id: str) -> Optional[League]:
        """
        Get a league by ID.
        
        Args:
            league_id: League UUID
            
        Returns:
            League instance or None if not found
        """
        league_data = self.storage.get_league(league_id)
        if league_data is None:
            return None

        return League(**league_data)

    def get_all_leagues(self) -> List[League]:
        """
        Get all leagues in the system.
        
        Returns:
            List of all League instances
        """
        all_leagues = self.storage.list_leagues()
        return [League(**league_data) for league_data in all_leagues]

    def update_league(self, league_id: str, league: League) -> League:
        """
        Update a league in storage.
        
        Args:
            league_id: League UUID
            league: Updated League instance
            
        Returns:
            Updated League instance
            
        Raises:
            ValueError: If league not found
        """
        existing = self.get_league(league_id)
        if existing is None:
            raise ValueError(f"League {league_id} not found")

        self.storage.update_league(league_id, league.model_dump())
        return league

    def delete_league(self, league_id: str) -> bool:
        """
        Delete a league from the system.
        
        Args:
            league_id: League UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete_league(league_id)

    def generate_players_for_league(self, league_id: str) -> List[Player]:
        """
        Generate players for a league based on its settings.
        
        Args:
            league_id: League UUID
            
        Returns:
            List of generated Player instances
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        # Generate players using the league's player count setting
        players = self.player_service.generate_players(
            count=league.settings.player_count,
            league_id=league_id
        )

        return players

    def add_team_to_league(self, league_id: str, team_id: str) -> League:
        """
        Add a team to a league.
        
        Args:
            league_id: League UUID
            team_id: Team UUID
            
        Returns:
            Updated League instance
            
        Raises:
            ValueError: If league not found or team already exists
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        league.add_team(team_id)

        # Update storage
        self.storage.update_league(league_id, league.model_dump())

        return league

    def remove_team_from_league(self, league_id: str, team_id: str) -> League:
        """
        Remove a team from a league.
        
        Args:
            league_id: League UUID
            team_id: Team UUID
            
        Returns:
            Updated League instance
            
        Raises:
            ValueError: If league not found or team doesn't exist
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        league.remove_team(team_id)

        # Update storage
        self.storage.update_league(league_id, league.model_dump())

        return league

    def get_league_players(
        self,
        league_id: str,
        free_agents_only: bool = False
    ) -> List[Player]:
        """
        Get all players associated with a league.
        
        Args:
            league_id: League UUID
            free_agents_only: If True, only return free agents
            
        Returns:
            List of Player instances
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        return self.player_service.get_players_by_league(
            league_id=league_id,
            free_agents_only=free_agents_only
        )

    def get_league_standings(self, league_id: str) -> LeagueStandings:
        """
        Get current standings for a league.
        
        Args:
            league_id: League UUID
            
        Returns:
            LeagueStandings with all teams ranked
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        # TODO: Calculate standings from team records
        # For now, return empty standings
        standings = []
        for i, team_id in enumerate(league.team_ids, start=1):
            entry = StandingsEntry(
                rank=i,
                team_id=team_id,
                wins=0,
                losses=0,
                points_for=0,
                points_against=0
            )
            standings.append(entry)

        return LeagueStandings(
            league_id=league_id,
            standings=standings
        )

    def is_league_ready_for_season(self, league_id: str) -> bool:
        """
        Check if a league has enough teams to start a season.
        
        Args:
            league_id: League UUID
            
        Returns:
            True if league can start season, False otherwise
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        # Need at least 2 teams to start a season
        return len(league.team_ids) >= 2

    def start_season(self, league_id: str) -> League:
        """
        Start a season for a league (generate schedule).
        
        Args:
            league_id: League UUID
            
        Returns:
            Updated League instance with schedule
            
        Raises:
            ValueError: If league not found or not ready for season
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        if not self.is_league_ready_for_season(league_id):
            raise ValueError(f"League {league_id} needs at least 2 teams to start season")

        # TODO: Generate full season schedule
        # For now, just mark as started
        # This will be implemented when game simulation is added

        self.storage.update_league(league_id, league.model_dump())

        return league

    def count_leagues(self) -> int:
        """
        Get total number of leagues in the system.
        
        Returns:
            Total league count
        """
        return len(self.storage.list_leagues())
