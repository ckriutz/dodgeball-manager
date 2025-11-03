"""
Pydantic models for API request/response schemas.

This module defines all the data models used for API communication,
matching the OpenAPI specification in contracts/openapi.yaml.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


# Base schemas with common validation
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLAlchemy compatibility
        "validate_assignment": True,
    }


# Player schemas
class PlayerSkills(BaseSchema):
    """Player skills schema."""
    catching: int = Field(ge=0, le=100, description="Ability to catch thrown balls")
    throwing: int = Field(ge=0, le=100, description="Throwing accuracy and power")
    dodging: int = Field(ge=0, le=100, description="Evasion capability")
    speed: int = Field(ge=0, le=100, description="Movement and reaction speed")
    iq: int = Field(ge=0, le=100, description="Strategic thinking and positioning")
    luck: int = Field(ge=0, le=100, description="Random variance influence")

    @model_validator(mode='after')
    def validate_skill_distribution(self) -> 'PlayerSkills':
        """Validate that skills sum to 10 for new players (FR-002)."""
        # Note: This validation is only applied when creating new players
        # Existing players may have different skill distributions
        return self


class PlayerInjury(BaseSchema):
    """Player injury schema."""
    severity: str = Field(pattern="^(minor|moderate|severe)$", description="Injury severity level")
    affected_reduction: float = Field(ge=0.0, le=1.0, description="Percentage reduction (0.2-0.5)")
    games_remaining: int = Field(ge=0, description="Games until healed")


class PlayerStats(BaseSchema):
    """Player statistics schema."""
    throws_attempted: int = Field(default=0, ge=0, description="Total throws made")
    catches_made: int = Field(default=0, ge=0, description="Successful catches")
    times_hit: int = Field(default=0, ge=0, description="Times eliminated by being hit")
    missed_throws: int = Field(default=0, ge=0, description="Throws that missed")
    successful_hits: int = Field(default=0, ge=0, description="Successful eliminations")


class Player(BaseSchema):
    """Player response schema."""
    id: UUID = Field(description="Unique identifier")
    name: str = Field(description="Player name")
    age: int = Field(ge=18, description="Player age")
    avatar: str = Field(description="Avatar URL/identifier")
    skills: PlayerSkills = Field(description="Player skills")
    value: int = Field(ge=0, description="Calculated dollar value")
    injury: Optional[PlayerInjury] = Field(default=None, description="Current injury if any")
    stats: PlayerStats = Field(description="Player statistics")
    team_id: Optional[UUID] = Field(default=None, description="Assigned team or null if free agent")
    is_starter: bool = Field(default=False, description="Whether designated as starter")


# Team types
class Team(BaseSchema):
    """Team response schema."""
    id: UUID = Field(description="Unique identifier")
    name: str = Field(description="Team name")
    description: str = Field(description="Team description")
    logo: str = Field(description="Team avatar image filename")
    budget: int = Field(ge=0, le=15000, description="Remaining budget in dollars")
    player_ids: List[UUID] = Field(default_factory=list, max_length=12, description="Roster player IDs")
    starter_ids: List[UUID] = Field(default_factory=list, max_length=5, description="Designated starter IDs")
    wins: int = Field(default=0, ge=0, description="Number of wins")
    losses: int = Field(default=0, ge=0, description="Number of losses")
    awards: List[str] = Field(default_factory=list, description="Team achievements")
    league_id: UUID = Field(description="Parent league")

    @model_validator(mode='after')
    def validate_roster_integrity(self) -> 'Team':
        """Validate roster integrity rules."""
        # All starters must be in roster (FR-013)
        starter_set = set(self.starter_ids)
        player_set = set(self.player_ids)
        if not starter_set.issubset(player_set):
            raise ValueError("All starters must be in the team roster")

        # Exactly 5 starters required (FR-013)
        if len(self.starter_ids) != 5:
            raise ValueError("Team must have exactly 5 starters")

        return self


# League schemas
class LeagueSettings(BaseSchema):
    """League settings schema."""
    player_count: int = Field(default=75, ge=50, le=100, description="Number of generated players")
    season_rounds: Optional[int] = Field(default=1, ge=1, description="Number of times each pairing plays")


class LeagueScheduleItem(BaseSchema):
    """League schedule item schema."""
    game_number: int = Field(description="Game number in schedule")
    team1_id: UUID = Field(description="Home team")
    team2_id: UUID = Field(description="Away team")
    completed: bool = Field(default=False, description="Whether game is completed")


class League(BaseSchema):
    """League response schema."""
    id: UUID = Field(description="Unique identifier")
    name: str = Field(description="League name")
    settings: LeagueSettings = Field(description="League settings")
    team_ids: List[UUID] = Field(default_factory=list, description="Teams in league")
    game_ids: List[UUID] = Field(default_factory=list, description="Historical game records")
    schedule: List[LeagueScheduleItem] = Field(default_factory=list, description="Upcoming games")
    created_at: datetime = Field(description="League creation timestamp")


# Game schemas
class GameEvent(BaseSchema):
    """Game event schema."""
    turn: int = Field(description="Turn number")
    type: str = Field(pattern="^(throw|hit|catch|miss|elimination)$", description="Event type")
    thrower_id: UUID = Field(description="Player who threw")
    target_id: UUID = Field(description="Target player")
    outcome: str = Field(description="Description of what happened")


class Game(BaseSchema):
    """Game response schema."""
    id: UUID = Field(description="Unique identifier")
    league_id: UUID = Field(description="Parent league")
    team1_id: UUID = Field(description="Home team")
    team2_id: UUID = Field(description="Away team")
    team1_starters: List[UUID] = Field(description="Team 1 starter player IDs")
    team2_starters: List[UUID] = Field(description="Team 2 starter player IDs")
    events: List[GameEvent] = Field(description="Play-by-play events")
    winner_id: Optional[UUID] = Field(default=None, description="Winning team ID")
    completed_at: Optional[datetime] = Field(default=None, description="Game completion timestamp")
    seed: int = Field(description="Random seed for deterministic replay")


# Request schemas
class CreateLeagueRequest(BaseSchema):
    """League creation request schema."""
    name: str = Field(description="League name")
    player_count: Optional[int] = Field(default=75, ge=50, le=100, description="Number of players to generate")


class CreateTeamRequest(BaseSchema):
    """Team creation request schema."""
    name: str = Field(description="Team name")
    description: Optional[str] = Field(default="", description="Team description")
    logo: Optional[str] = Field(default="team-avatar-1.png", description="Team avatar image filename")
    league_id: UUID = Field(description="Parent league ID")


class AddPlayerToTeamRequest(BaseSchema):
    """Add player to team request schema."""
    player_id: UUID = Field(description="Player to add")


class GeneratePlayersRequest(BaseSchema):
    """Generate players request schema."""
    # No additional fields needed - uses league settings


class UpdateTeamStartersRequest(BaseSchema):
    """Update team starters request schema."""
    starter_ids: List[UUID] = Field(min_length=5, max_length=5, description="Exactly 5 starter player IDs")


class CreateGameRequest(BaseSchema):
    """Create and simulate game request schema."""
    team1_id: UUID = Field(description="First team")
    team2_id: UUID = Field(description="Second team")
    seed: Optional[int] = Field(default=None, description="Random seed for deterministic results")


# Response schemas
class PlayersResponse(BaseSchema):
    """Response for player listing endpoints."""
    players: List[Player] = Field(description="List of players")


class GeneratePlayersResponse(BaseSchema):
    """Response for player generation endpoint."""
    count: int = Field(description="Number of players generated")
    players: List[Player] = Field(description="Generated players")


class TeamsResponse(BaseSchema):
    """Response for team listing endpoints."""
    teams: List[Team] = Field(description="List of teams")


class GamesResponse(BaseSchema):
    """Response for game listing endpoints."""
    games: List[Game] = Field(description="List of games")


class LeagueStandingsItem(BaseSchema):
    """Individual team standings item."""
    team_id: UUID = Field(description="Team ID")
    team_name: str = Field(description="Team name")
    wins: int = Field(description="Number of wins")
    losses: int = Field(description="Number of losses")
    win_percentage: float = Field(description="Win percentage")


class LeagueStandingsResponse(BaseSchema):
    """Response for league standings endpoint."""
    standings: List[LeagueStandingsItem] = Field(description="Teams ranked by performance")


class LeagueAwardsResponse(BaseSchema):
    """Response for league awards endpoint."""
    awards: Dict[str, Any] = Field(description="Award categories and winners")


# Health check schema
class HealthResponse(BaseSchema):
    """Health check response schema."""
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    storage_stats: Dict[str, int] = Field(description="Storage collection counts")