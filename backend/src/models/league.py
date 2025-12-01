"""
League model for the Dodgeball Fantasy League.

This module defines the League entity with settings, team management,
game tracking, and scheduling capabilities.

References:
- data-model.md: League entity definition
- FR-001a: Player count must be 50-100
- research.md: League management decisions
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import uuid4
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


class SeasonStatus(str, Enum):
    """Season lifecycle states."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Season(BaseModel):
    """
    Season entity representing a single season within a league.
    
    A season tracks the current state of play, including the season number,
    status, and timestamps for key lifecycle events.
    
    References:
    - spec.md FR-043: Preserve player progression across seasons
    - spec.md US4: Season management with lifecycle states
    """
    season_number: int = Field(ge=1, description="Sequential season number (1, 2, 3, ...)")
    status: SeasonStatus = Field(
        default=SeasonStatus.NOT_STARTED,
        description="Current season status"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when season started (schedule created)"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when season was completed (all games finished)"
    )

    def start_season(self) -> None:
        """
        Mark the season as started.
        
        Raises:
            ValueError: If season is not in NOT_STARTED state
        """
        if self.status != SeasonStatus.NOT_STARTED:
            raise ValueError(
                f"Cannot start season: Season must be in NOT_STARTED status, "
                f"currently {self.status}"
            )
        
        self.status = SeasonStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)

    def complete_season(self) -> None:
        """
        Mark the season as completed.
        
        Raises:
            ValueError: If season is not in IN_PROGRESS state
        """
        if self.status != SeasonStatus.IN_PROGRESS:
            raise ValueError(
                f"Cannot complete season: Season must be in IN_PROGRESS status, "
                f"currently {self.status}"
            )
        
        self.status = SeasonStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def is_active(self) -> bool:
        """Check if season is currently active (in progress)."""
        return self.status == SeasonStatus.IN_PROGRESS

    def is_completed(self) -> bool:
        """Check if season has been completed."""
        return self.status == SeasonStatus.COMPLETED

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "season_number": 1,
                "status": "in_progress",
                "started_at": "2025-10-25T12:00:00Z",
                "completed_at": None
            }
        }


class SeasonArchive(BaseModel):
    """
    Historical record of a completed season.
    
    Archives preserve final standings, MVP/awards, team rosters,
    and player statistics from completed seasons for historical reference.
    
    References:
    - spec.md: Historical season data with standings, rosters, stats, MVP
    - spec.md US4: Season history with archives
    """
    season_number: int = Field(ge=1, description="Season number this archive represents")
    champion_team_id: str = Field(description="ID of the team that won the season")
    mvp_player_id: Optional[str] = Field(
        default=None,
        description="ID of the MVP player for this season"
    )
    final_standings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Final standings with team_id, wins, losses, rank"
    )
    team_rosters: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of team_id to list of player_ids at season end"
    )
    player_stats: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Map of player_id to their stats for this season"
    )
    statistical_leaders: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of stat category to player_id (e.g., 'most_hits': 'player-123')"
    )
    completed_at: datetime = Field(description="When this season was completed")
    archived_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this archive was created"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "season_number": 1,
                "champion_team_id": "team-123",
                "mvp_player_id": "player-456",
                "final_standings": [
                    {"team_id": "team-123", "team_name": "Champions", "wins": 10, "losses": 2, "rank": 1},
                    {"team_id": "team-456", "team_name": "Runners Up", "wins": 8, "losses": 4, "rank": 2}
                ],
                "team_rosters": {
                    "team-123": ["player-1", "player-2", "player-3"],
                    "team-456": ["player-4", "player-5", "player-6"]
                },
                "player_stats": {
                    "player-1": {"games_played": 12, "successful_hits": 25, "catches_made": 15}
                },
                "statistical_leaders": {
                    "most_hits": "player-456",
                    "most_catches": "player-789",
                    "highest_accuracy": "player-123"
                },
                "completed_at": "2025-11-01T18:00:00Z",
                "archived_at": "2025-11-01T18:05:00Z"
            }
        }


class LeagueSettings(BaseModel):
    """League configuration settings."""
    player_count: int = Field(
        default=75,
        ge=50,
        le=100,
        description="Number of players to generate (FR-001a)"
    )
    season_rounds: int = Field(
        default=1,
        ge=1,
        description="Number of times each team pairing plays"
    )


class ScheduleGame(BaseModel):
    """Scheduled game in the league."""
    game_number: int = Field(ge=1, description="Sequence number of the game")
    team1_id: str = Field(description="Home team ID")
    team2_id: str = Field(description="Away team ID")
    completed: bool = Field(default=False, description="Whether game has been played")


class League(BaseModel):
    """
    League entity representing a fantasy dodgeball league.
    
    A league contains teams, manages player pools, tracks games,
    and handles scheduling.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, description="League name")
    settings: LeagueSettings = Field(default_factory=LeagueSettings)
    team_ids: List[str] = Field(
        default_factory=list,
        description="IDs of teams in the league"
    )
    game_ids: List[str] = Field(
        default_factory=list,
        description="IDs of historical game records"
    )
    schedule: List[ScheduleGame] = Field(
        default_factory=list,
        description="Upcoming/scheduled games"
    )
    current_season: Season = Field(
        default_factory=lambda: Season(season_number=1),
        description="Current season state and lifecycle"
    )
    season_archives: List[SeasonArchive] = Field(
        default_factory=list,
        description="Historical records of completed seasons"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def add_team(self, team_id: str) -> None:
        """
        Add a team to the league.
        
        Args:
            team_id: UUID string of the team to add
            
        Raises:
            ValueError: If team is already in league
        """
        if team_id in self.team_ids:
            raise ValueError(f"Team {team_id} is already in the league")
        self.team_ids.append(team_id)

    def remove_team(self, team_id: str) -> None:
        """
        Remove a team from the league.
        
        Args:
            team_id: UUID string of the team to remove
            
        Raises:
            ValueError: If team is not in league
        """
        if team_id not in self.team_ids:
            raise ValueError(f"Team {team_id} is not in the league")
        self.team_ids.remove(team_id)

    def get_team_count(self) -> int:
        """Get the number of teams in the league."""
        return len(self.team_ids)

    def can_create_schedule(self) -> bool:
        """
        Check if league has enough teams to create a schedule.
        
        Returns:
            True if league has at least 2 teams
        """
        return len(self.team_ids) >= 2

    def add_game(self, game_id: str) -> None:
        """
        Add a completed game to the league history.
        
        Args:
            game_id: UUID string of the game
        """
        if game_id not in self.game_ids:
            self.game_ids.append(game_id)

    def set_schedule(self, schedule: List[ScheduleGame]) -> None:
        """
        Set the league schedule.
        
        Args:
            schedule: List of scheduled games
            
        Raises:
            ValueError: If league doesn't have enough teams
        """
        if not self.can_create_schedule():
            raise ValueError("League must have at least 2 teams to create schedule")
        self.schedule = schedule

    def clear_schedule(self) -> None:
        """Clear the current schedule."""
        self.schedule = []

    def get_next_game(self) -> Optional[ScheduleGame]:
        """
        Get the next unplayed game in the schedule.
        
        Returns:
            Next scheduled game or None if all games completed
        """
        for game in self.schedule:
            if not game.completed:
                return game
        return None

    def mark_game_completed(self, game_number: int) -> None:
        """
        Mark a scheduled game as completed.
        
        Args:
            game_number: Game number to mark as completed
            
        Raises:
            ValueError: If game not found in schedule
        """
        for game in self.schedule:
            if game.game_number == game_number:
                game.completed = True
                return
        raise ValueError(f"Game {game_number} not found in schedule")

    def get_completed_games_count(self) -> int:
        """Get the number of completed games."""
        return sum(1 for game in self.schedule if game.completed)

    def get_remaining_games_count(self) -> int:
        """Get the number of remaining games."""
        return sum(1 for game in self.schedule if not game.completed)

    def is_season_complete(self) -> bool:
        """
        Check if all scheduled games have been played.
        
        Returns:
            True if schedule exists and all games are completed
        """
        if not self.schedule:
            return False
        return all(game.completed for game in self.schedule)

    def start_new_season(self) -> None:
        """
        Start a new season after completing the previous one.
        
        Creates a new Season with incremented season_number and clears the schedule.
        
        Raises:
            ValueError: If current season is not completed
        """
        if not self.current_season.is_completed():
            raise ValueError(
                "Cannot start new season: Current season must be completed first"
            )
        
        # Create new season with incremented number
        self.current_season = Season(
            season_number=self.current_season.season_number + 1
        )
        
        # Clear schedule for new season
        self.schedule = []

    def archive_season(
        self,
        champion_team_id: str,
        mvp_player_id: Optional[str],
        final_standings: List[Dict[str, Any]],
        team_rosters: Dict[str, List[str]],
        player_stats: Dict[str, Dict[str, Any]],
        statistical_leaders: Dict[str, str]
    ) -> SeasonArchive:
        """
        Archive the completed season with final results.
        
        Args:
            champion_team_id: ID of the winning team
            mvp_player_id: Optional ID of the MVP player
            final_standings: List of standings entries
            team_rosters: Map of team_id to player_ids at season end
            player_stats: Map of player_id to season stats
            statistical_leaders: Map of category to player_id
            
        Returns:
            Created SeasonArchive
            
        Raises:
            ValueError: If season is not completed
        """
        if not self.current_season.is_completed():
            raise ValueError(
                "Cannot archive season: Season must be completed first"
            )
        
        archive = SeasonArchive(
            season_number=self.current_season.season_number,
            champion_team_id=champion_team_id,
            mvp_player_id=mvp_player_id,
            final_standings=final_standings,
            team_rosters=team_rosters,
            player_stats=player_stats,
            statistical_leaders=statistical_leaders,
            completed_at=self.current_season.completed_at or datetime.now(timezone.utc)
        )
        
        self.season_archives.append(archive)
        return archive

    def get_season_archive(self, season_number: int) -> Optional[SeasonArchive]:
        """
        Get archived data for a specific season.
        
        Args:
            season_number: Season number to retrieve
            
        Returns:
            SeasonArchive if found, None otherwise
        """
        for archive in self.season_archives:
            if archive.season_number == season_number:
                return archive
        return None

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Elite Dodgeball League",
                "settings": {
                    "player_count": 75,
                    "season_rounds": 1
                },
                "team_ids": [],
                "game_ids": [],
                "schedule": [],
                "created_at": "2025-10-25T12:00:00Z"
            }
        }


class LeagueCreate(BaseModel):
    """Schema for creating a new league."""
    name: str = Field(min_length=1, description="League name")
    player_count: Optional[int] = Field(
        default=75,
        ge=50,
        le=100,
        description="Number of players to generate (50-100, default 75)"
    )
    season_rounds: Optional[int] = Field(
        default=1,
        ge=1,
        description="Number of rounds in the season (default 1)"
    )

    def to_league(self) -> League:
        """
        Convert creation schema to League entity.
        
        Returns:
            New League instance with provided settings
        """
        settings = LeagueSettings(
            player_count=self.player_count or 75,
            season_rounds=self.season_rounds or 1
        )
        
        return League(
            name=self.name,
            settings=settings,
            team_ids=[],
            game_ids=[],
            schedule=[]
        )


class LeagueUpdate(BaseModel):
    """Schema for updating league fields."""
    name: Optional[str] = Field(default=None, min_length=1)
    season_rounds: Optional[int] = Field(default=None, ge=1)

    def apply_to(self, league: League) -> League:
        """
        Apply updates to a league instance.
        
        Args:
            league: League to update
            
        Returns:
            Updated league instance
        """
        if self.name is not None:
            league.name = self.name
        if self.season_rounds is not None:
            league.settings.season_rounds = self.season_rounds
        return league


class LeagueResponse(BaseModel):
    """Schema for league API responses."""
    id: str
    name: str
    settings: LeagueSettings
    team_ids: List[str]
    game_ids: List[str]
    schedule: List[ScheduleGame]
    current_season: Season
    season_archives: List[SeasonArchive]
    created_at: datetime

    @classmethod
    def from_league(cls, league: League) -> 'LeagueResponse':
        """
        Create response schema from League entity.
        
        Args:
            league: League entity
            
        Returns:
            LeagueResponse instance
        """
        return cls(
            id=league.id,
            name=league.name,
            settings=league.settings,
            team_ids=league.team_ids,
            game_ids=league.game_ids,
            schedule=league.schedule,
            current_season=league.current_season,
            season_archives=league.season_archives,
            created_at=league.created_at
        )


class ScheduleCreateRequest(BaseModel):
    """Request schema for creating a league schedule."""
    rounds: int = Field(
        default=1,
        ge=1,
        description="Number of times each team pairing plays"
    )


class StandingsEntry(BaseModel):
    """Single entry in league standings."""
    team_id: str
    team_name: str
    wins: int = Field(ge=0)
    losses: int = Field(ge=0)
    rank: int = Field(ge=1)

    @property
    def games_played(self) -> int:
        """Total games played."""
        return self.wins + self.losses

    @property
    def win_percentage(self) -> float:
        """Win percentage (0.0 to 1.0)."""
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played


class LeagueStandings(BaseModel):
    """League standings with ranked teams."""
    league_id: str
    standings: List[StandingsEntry] = Field(
        description="Teams ranked by wins (descending), then losses (ascending)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
