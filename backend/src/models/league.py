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
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator, model_validator


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
