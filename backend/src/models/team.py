"""
Team model for the Dodgeball Fantasy League.

This module defines the Team entity with budget management, roster validation,
and starter designation capabilities.

References:
- data-model.md: Team entity definition
- FR-012: Team rosters must have 8-12 players
- FR-013: Exactly 5 starters must be designated
- FR-014: Cannot add player if value exceeds budget
- FR-014a: Can add player if value equals budget
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator, model_validator


class Team(BaseModel):
    """
    Team entity representing a fantasy dodgeball team.
    
    A team has a budget ($15,000), manages a roster of 8-12 players,
    designates 5 starters, and tracks wins/losses.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, description="Team name")
    description: str = Field(default="", description="Team description")
    logo: str = Field(default="team-avatar-1.png", description="Team avatar image filename")
    budget: int = Field(
        default=15000,
        ge=0,
        le=15000,
        description="Remaining budget in dollars (0-15,000)"
    )
    player_ids: List[str] = Field(
        default_factory=list,
        description="Roster player IDs (8-12 players for valid team)"
    )
    starter_ids: List[str] = Field(
        default_factory=list,
        description="Designated starter IDs (exactly 5 required)"
    )
    wins: int = Field(default=0, ge=0, description="Number of wins")
    losses: int = Field(default=0, ge=0, description="Number of losses")
    awards: List[str] = Field(
        default_factory=list,
        description="Team achievements"
    )
    league_id: str = Field(description="Parent league ID")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator('player_ids')
    @classmethod
    def validate_no_duplicate_players(cls, v: List[str]) -> List[str]:
        """Validate that roster has no duplicate player IDs."""
        if len(v) != len(set(v)):
            raise ValueError("Roster cannot contain duplicate player IDs")
        return v

    @field_validator('starter_ids')
    @classmethod
    def validate_no_duplicate_starters(cls, v: List[str]) -> List[str]:
        """Validate that starters have no duplicate player IDs."""
        if len(v) != len(set(v)):
            raise ValueError("Starters cannot contain duplicate player IDs")
        return v

    @model_validator(mode='after')
    def validate_starters_on_roster(self) -> 'Team':
        """
        Validate that all starters are on the roster (FR-013).
        
        This ensures data integrity - you can't designate a starter
        who isn't on your team.
        """
        if self.starter_ids:
            roster_set = set(self.player_ids)
            for starter_id in self.starter_ids:
                if starter_id not in roster_set:
                    raise ValueError(
                        f"Starter {starter_id} is not on the roster. "
                        "All starters must be roster members."
                    )
        return self

    def get_roster_size(self) -> int:
        """Get the current roster size."""
        return len(self.player_ids)

    def is_roster_valid_size(self) -> bool:
        """
        Check if roster size is valid (8-12 players per FR-012).
        
        Returns:
            True if roster has 8-12 players
        """
        return 8 <= len(self.player_ids) <= 12

    def can_add_player(self) -> bool:
        """
        Check if roster has room for another player.
        
        Returns:
            True if roster size is less than 12
        """
        return len(self.player_ids) < 12

    def can_remove_player(self) -> bool:
        """
        Check if a player can be removed without going below minimum.
        
        Returns:
            True if roster size is greater than 8
        """
        return len(self.player_ids) > 8

    def is_starters_valid_count(self) -> bool:
        """
        Check if exactly 5 starters are designated (FR-013).
        
        Returns:
            True if exactly 5 starters
        """
        return len(self.starter_ids) == 5

    def can_afford_player(self, player_value: int) -> bool:
        """
        Check if team can afford to add a player (FR-014, FR-014a).
        
        Args:
            player_value: Dollar value of the player
            
        Returns:
            True if player_value <= budget (allows exact match per FR-014a)
        """
        return player_value <= self.budget

    def add_player_to_roster(self, player_id: str, player_value: int) -> None:
        """
        Add a player to the team roster.
        
        Args:
            player_id: UUID string of the player
            player_value: Dollar value of the player
            
        Raises:
            ValueError: If roster is full, player already on roster, 
                       or budget insufficient
        """
        if not self.can_add_player():
            raise ValueError("Roster is full (maximum 12 players)")
        
        if player_id in self.player_ids:
            raise ValueError(f"Player {player_id} is already on the roster")
        
        if not self.can_afford_player(player_value):
            raise ValueError(
                f"Insufficient budget: Player costs ${player_value}, "
                f"but only ${self.budget} remaining"
            )
        
        self.player_ids.append(player_id)
        self.budget -= player_value

    def remove_player_from_roster(self, player_id: str, player_value: int) -> None:
        """
        Remove a player from the team roster.
        
        Args:
            player_id: UUID string of the player
            player_value: Dollar value of the player (for refund)
            
        Raises:
            ValueError: If roster at minimum size or player not on roster
        """
        if not self.can_remove_player():
            raise ValueError(
                "Cannot remove player: Roster at minimum size (8 players)"
            )
        
        if player_id not in self.player_ids:
            raise ValueError(f"Player {player_id} is not on the roster")
        
        self.player_ids.remove(player_id)
        
        # Remove from starters if they were a starter
        if player_id in self.starter_ids:
            self.starter_ids.remove(player_id)
        
        # Refund the player's value to the budget
        self.budget += player_value

    def set_starters(self, starter_ids: List[str]) -> None:
        """
        Designate the starting lineup (FR-013).
        
        Allows setting 0-5 starters during roster building.
        Exactly 5 starters required for game simulation.
        
        Args:
            starter_ids: List of up to 5 player IDs
            
        Raises:
            ValueError: If more than 5 starters, duplicates exist,
                       or starters not on roster
        """
        if len(starter_ids) > 5:
            raise ValueError(
                f"Maximum 5 starters allowed, got {len(starter_ids)}"
            )
        
        # Check for duplicates
        if len(starter_ids) != len(set(starter_ids)):
            raise ValueError("Starters cannot contain duplicate player IDs")
        
        # Check all starters are on roster
        roster_set = set(self.player_ids)
        for starter_id in starter_ids:
            if starter_id not in roster_set:
                raise ValueError(
                    f"Starter {starter_id} is not on the roster. "
                    "All starters must be roster members."
                )
        
        self.starter_ids = starter_ids

    def clear_starters(self) -> None:
        """Clear the starting lineup."""
        self.starter_ids = []

    def get_bench_player_ids(self) -> List[str]:
        """
        Get list of bench player IDs (players not in starting lineup).
        
        Returns:
            List of player IDs who are on roster but not starters
        """
        starter_set = set(self.starter_ids)
        return [pid for pid in self.player_ids if pid not in starter_set]

    def is_player_starter(self, player_id: str) -> bool:
        """
        Check if a player is in the starting lineup.
        
        Args:
            player_id: UUID string of the player
            
        Returns:
            True if player is a starter
        """
        return player_id in self.starter_ids

    def record_win(self) -> None:
        """Record a win for the team."""
        self.wins += 1

    def record_loss(self) -> None:
        """Record a loss for the team."""
        self.losses += 1

    def add_award(self, award: str) -> None:
        """
        Add an award/achievement to the team.
        
        Args:
            award: Award description
        """
        if award not in self.awards:
            self.awards.append(award)

    def get_record(self) -> str:
        """
        Get the team's win-loss record as a string.
        
        Returns:
            Record in format "W-L" (e.g., "5-3")
        """
        return f"{self.wins}-{self.losses}"

    def get_games_played(self) -> int:
        """Get total number of games played."""
        return self.wins + self.losses

    def get_win_percentage(self) -> float:
        """
        Calculate win percentage.
        
        Returns:
            Win percentage as float (0.0 to 1.0), 0.0 if no games played
        """
        games_played = self.get_games_played()
        if games_played == 0:
            return 0.0
        return self.wins / games_played

    def calculate_spent_budget(self, player_values: dict) -> int:
        """
        Calculate total budget spent based on current roster.
        
        Args:
            player_values: Dict mapping player_id to player value
            
        Returns:
            Total value of all players on roster
        """
        return sum(player_values.get(pid, 0) for pid in self.player_ids)

    def validate_budget_integrity(self) -> bool:
        """
        Verify that spent + remaining equals initial budget.
        
        Formula: spent + remaining = 15,000
        
        Returns:
            True if budget integrity is maintained, False otherwise
        """
        spent = self.get_spent_budget()
        return spent + self.budget == 15000

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Brooklyn Dodgers",
                "description": "The best dodgeball team in Brooklyn",
                "logo": "team-avatar-1.png",
                "league_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
                "budget": 15000,
                "player_ids": [],
                "starter_ids": [],
                "wins": 0,
                "losses": 0
            }
        }


class TeamCreate(BaseModel):
    """Schema for creating a new team."""
    name: str = Field(min_length=1, description="Team name")
    description: Optional[str] = Field(default="", description="Team description")
    logo: Optional[str] = Field(default="team-avatar-1.png", description="Team avatar image filename")
    league_id: str = Field(description="League ID this team belongs to")

    def to_team(self) -> Team:
        """
        Convert creation schema to Team entity.
        
        Returns:
            New Team instance with $15,000 budget and empty roster
        """
        return Team(
            name=self.name,
            description=self.description or "",
            logo=self.logo or "team-avatar-1.png",
            budget=15000,
            player_ids=[],
            starter_ids=[],
            wins=0,
            losses=0,
            awards=[],
            league_id=self.league_id
        )


class TeamUpdate(BaseModel):
    """Schema for updating team fields."""
    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    logo: Optional[str] = None

    def apply_to(self, team: Team) -> Team:
        """
        Apply updates to a team instance.
        
        Args:
            team: Team to update
            
        Returns:
            Updated team instance
        """
        if self.name is not None:
            team.name = self.name
        if self.description is not None:
            team.description = self.description
        if self.logo is not None:
            team.logo = self.logo
        return team


class TeamResponse(BaseModel):
    """Schema for team API responses."""
    id: str
    name: str
    description: str
    logo: str
    budget: int
    player_ids: List[str]
    starter_ids: List[str]
    wins: int
    losses: int
    awards: List[str]
    league_id: str
    created_at: datetime

    @classmethod
    def from_team(cls, team: Team) -> 'TeamResponse':
        """
        Create response schema from Team entity.
        
        Args:
            team: Team entity
            
        Returns:
            TeamResponse instance
        """
        return cls(
            id=team.id,
            name=team.name,
            description=team.description,
            logo=team.logo,
            budget=team.budget,
            player_ids=team.player_ids,
            starter_ids=team.starter_ids,
            wins=team.wins,
            losses=team.losses,
            awards=team.awards,
            league_id=team.league_id,
            created_at=team.created_at
        )


class AddPlayerRequest(BaseModel):
    """Request schema for adding a player to team roster."""
    player_id: str = Field(description="ID of the player to add")


class SetStartersRequest(BaseModel):
    """Request schema for setting team starters."""
    starter_ids: List[str] = Field(
        description="List of up to 5 player IDs for starting lineup",
        max_length=5
    )

    @field_validator('starter_ids')
    @classmethod
    def validate_no_duplicates(cls, v: List[str]) -> List[str]:
        """Validate that starters have no duplicate player IDs."""
        if len(v) != len(set(v)):
            raise ValueError("Starters cannot contain duplicate player IDs")
        return v
