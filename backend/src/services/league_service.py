"""
LeagueService for managing league operations.

This service handles league creation, retrieval, and management operations.
It coordinates with PlayerService for player generation and team management.

References:
- FR-001: League setup with 50-100 players
- FR-005: Team management and draft
- FR-024: Schedule generation with round-robin algorithm
"""

from typing import List, Optional, Dict, Any

from ..models.league import League, LeagueCreate, LeagueStandings, StandingsEntry, ScheduleGame
from ..models.team import Team
from .schedule_service import generate_round_robin_schedule_with_numbers
from .standings_service import calculate_standings
from .awards_service import calculate_season_awards
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
            LeagueStandings with all teams ranked by wins (desc), losses (asc)
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        # Get team data for standings calculation
        teams_data = []
        for team_id in league.team_ids:
            team_data = self.storage.get_team(team_id)
            if team_data:
                team = Team(**team_data)
                teams_data.append({
                    "team_id": team.id,
                    "team_name": team.name,
                    "wins": team.wins,
                    "losses": team.losses
                })
        
        # Calculate standings using the standings service
        calculated_standings = calculate_standings(teams_data)
        
        # Convert to StandingsEntry objects
        standings = [
            StandingsEntry(
                team_id=entry["team_id"],
                team_name=entry["team_name"],
                wins=entry["wins"],
                losses=entry["losses"],
                rank=entry["rank"]
            )
            for entry in calculated_standings
        ]

        return LeagueStandings(
            league_id=league_id,
            standings=standings
        )

    def get_league_awards(self, league_id: str) -> Dict[str, Any]:
        """
        Get awards (MVP and statistical leaders) for a league.
        
        Calculates awards based on current player stats:
        - mvp: Most Valuable Player (combined performance)
        - most_hits: Most successful eliminations
        - most_catches: Most catches made
        - accuracy_leader: Best throw accuracy
        - best_defense: Fewest times eliminated
        
        Args:
            league_id: League UUID
            
        Returns:
            Dict with award categories and winners
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")

        # Get all players in the league (on teams)
        players = self.player_service.get_players_by_league(
            league_id=league_id,
            free_agents_only=False
        )
        
        # Convert players to stats dicts for awards calculation
        player_stats = []
        for player in players:
            # Only include players on teams (not free agents)
            if player.team_id:
                player_stats.append({
                    "player_id": player.id,
                    "name": player.name,
                    "successful_hits": player.stats.successful_hits,
                    "catches_made": player.stats.catches_made,
                    "times_hit": player.stats.times_hit,
                    "throws_attempted": player.stats.throws_attempted,
                    "games_played": player.stats.games_played
                })
        
        # Calculate awards
        awards = calculate_season_awards(player_stats)
        
        return {
            "league_id": league_id,
            "mvp": awards.get("mvp"),
            "most_hits": awards.get("most_hits"),
            "most_catches": awards.get("most_catches"),
            "accuracy_leader": awards.get("accuracy_leader"),
            "best_defense": awards.get("best_defense")
        }

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

    def generate_schedule(
        self,
        league_id: str,
        rounds: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a round-robin schedule for a league.
        
        Creates a schedule where every team plays every other team
        the specified number of rounds. Updates the league with the
        new schedule and starts the season if not already started.
        
        Args:
            league_id: League UUID
            rounds: Number of times each pairing plays (default 1)
            
        Returns:
            Dict with schedule info including games_scheduled and schedule
            
        Raises:
            ValueError: If league not found or has less than 2 teams
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")
        
        if not league.can_create_schedule():
            raise ValueError(
                f"League {league_id} needs at least 2 teams to create a schedule"
            )
        
        # Generate round-robin schedule
        schedule_data = generate_round_robin_schedule_with_numbers(
            teams=league.team_ids,
            rounds=rounds
        )
        
        # Convert to ScheduleGame objects
        schedule_games = [
            ScheduleGame(
                game_number=game["game_number"],
                team1_id=game["team1_id"],
                team2_id=game["team2_id"],
                completed=game["completed"]
            )
            for game in schedule_data
        ]
        
        # Set the schedule on the league
        league.set_schedule(schedule_games)
        
        # Start the season if not already started
        if not league.current_season.is_active():
            try:
                league.current_season.start_season()
            except ValueError:
                # Season might already be in progress or completed
                pass
        
        # Update storage
        self.storage.update_league(league_id, league.model_dump())
        
        return {
            "games_scheduled": len(schedule_games),
            "schedule": [game.model_dump() for game in schedule_games],
            "season_number": league.current_season.season_number,
            "season_status": league.current_season.status.value
        }

    def get_schedule(self, league_id: str) -> Dict[str, Any]:
        """
        Get the current schedule for a league.
        
        Args:
            league_id: League UUID
            
        Returns:
            Dict with schedule info including games, status counts
            
        Raises:
            ValueError: If league not found
        """
        league = self.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")
        
        schedule = [game.model_dump() for game in league.schedule]
        completed_count = league.get_completed_games_count()
        remaining_count = league.get_remaining_games_count()
        next_game = league.get_next_game()
        
        return {
            "schedule": schedule,
            "total_games": len(schedule),
            "completed_games": completed_count,
            "remaining_games": remaining_count,
            "next_game": next_game.model_dump() if next_game else None,
            "season_number": league.current_season.season_number,
            "season_status": league.current_season.status.value,
            "is_season_complete": league.is_season_complete()
        }

    def count_leagues(self) -> int:
        """
        Get total number of leagues in the system.
        
        Returns:
            Total league count
        """
        return len(self.storage.list_leagues())
