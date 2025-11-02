"""
Injury model for the Dodgeball Fantasy League.

This module defines the Injury entity as a standalone model for tracking
player injuries, their severity, and healing progression.

References:
- data-model.md: Injury entity definition
- research.md: Injury system mechanics
- FR-006: Injuries reduce effective stats by percentage
- FR-006a: Injured players can still play
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class InjurySeverity(str, Enum):
    """
    Injury severity levels.
    
    Each severity level has a specific stat reduction percentage
    and healing time defined in the injury mechanics.
    """
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class Injury(BaseModel):
    """
    Injury entity representing a temporary condition affecting a player.
    
    Injuries occur probabilistically during games (5% chance on hits) and
    reduce all player skills by a percentage based on severity. They heal
    automatically after a fixed number of games.
    
    Injury Mechanics (from research.md):
    - 5% probability when player is hit
    - Minor: 20% reduction, heals in 1 game
    - Moderate: 35% reduction, heals in 2 games  
    - Severe: 50% reduction, heals in 3 games
    - Severity distribution: 60% minor, 30% moderate, 10% severe
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    player_id: str = Field(description="ID of the affected player")
    severity: InjurySeverity = Field(description="Injury severity level")
    stat_reduction: float = Field(
        ge=0.0,
        le=1.0,
        description="Percentage reduction of all skills (0.2, 0.35, or 0.5)"
    )
    healing_games: int = Field(
        ge=1,
        le=3,
        description="Total number of games required to heal (1, 2, or 3)"
    )
    games_remaining: int = Field(
        ge=0,
        le=3,
        description="Number of games until fully healed"
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when injury occurred"
    )

    @model_validator(mode='after')
    def validate_severity_parameters(self) -> 'Injury':
        """
        Validate that stat_reduction and healing_games match severity level.
        
        Ensures data integrity by enforcing the correct parameters for each
        severity level as defined in the injury mechanics specification.
        """
        expected_params = {
            InjurySeverity.MINOR: (0.2, 1),
            InjurySeverity.MODERATE: (0.35, 2),
            InjurySeverity.SEVERE: (0.5, 3)
        }
        
        expected_reduction, expected_healing = expected_params[self.severity]
        
        if self.stat_reduction != expected_reduction:
            raise ValueError(
                f"{self.severity.value} injury must have {expected_reduction*100}% "
                f"stat reduction, got {self.stat_reduction*100}%"
            )
        
        if self.healing_games != expected_healing:
            raise ValueError(
                f"{self.severity.value} injury must heal in {expected_healing} "
                f"game(s), got {self.healing_games}"
            )
        
        return self

    @field_validator('games_remaining')
    @classmethod
    def validate_games_remaining(cls, v: int, info) -> int:
        """Validate that games_remaining is not greater than healing_games."""
        healing_games = info.data.get('healing_games')
        if healing_games and v > healing_games:
            raise ValueError(
                f"games_remaining ({v}) cannot exceed healing_games ({healing_games})"
            )
        return v

    def is_healed(self) -> bool:
        """
        Check if the injury is fully healed.
        
        Returns:
            True if games_remaining is 0
        """
        return self.games_remaining == 0

    def progress_healing(self) -> bool:
        """
        Progress the injury healing by one game.
        
        This should be called after each game the player participates in.
        
        Returns:
            True if injury is now fully healed (games_remaining reached 0)
        """
        if self.games_remaining > 0:
            self.games_remaining -= 1
        
        return self.is_healed()

    def get_effective_stat_multiplier(self) -> float:
        """
        Get the multiplier to apply to player stats.
        
        Returns:
            Multiplier between 0.5 and 0.8 (1 - stat_reduction)
        """
        return 1.0 - self.stat_reduction

    def get_healing_progress(self) -> float:
        """
        Get the healing progress as a percentage.
        
        Returns:
            Percentage healed (0.0 to 1.0)
        """
        if self.healing_games == 0:
            return 1.0
        
        games_healed = self.healing_games - self.games_remaining
        return games_healed / self.healing_games

    def get_days_injured(self) -> int:
        """
        Calculate how many days the player has been injured.
        
        Returns:
            Number of days since injury occurred
        """
        now = datetime.now(timezone.utc)
        delta = now - self.occurred_at
        return delta.days

    @staticmethod
    def create_minor(player_id: str) -> 'Injury':
        """
        Factory method to create a minor injury.
        
        Args:
            player_id: ID of the affected player
            
        Returns:
            New Injury instance with minor severity
        """
        return Injury(
            player_id=player_id,
            severity=InjurySeverity.MINOR,
            stat_reduction=0.2,
            healing_games=1,
            games_remaining=1
        )

    @staticmethod
    def create_moderate(player_id: str) -> 'Injury':
        """
        Factory method to create a moderate injury.
        
        Args:
            player_id: ID of the affected player
            
        Returns:
            New Injury instance with moderate severity
        """
        return Injury(
            player_id=player_id,
            severity=InjurySeverity.MODERATE,
            stat_reduction=0.35,
            healing_games=2,
            games_remaining=2
        )

    @staticmethod
    def create_severe(player_id: str) -> 'Injury':
        """
        Factory method to create a severe injury.
        
        Args:
            player_id: ID of the affected player
            
        Returns:
            New Injury instance with severe severity
        """
        return Injury(
            player_id=player_id,
            severity=InjurySeverity.SEVERE,
            stat_reduction=0.5,
            healing_games=3,
            games_remaining=3
        )

    @staticmethod
    def create_random_severity(player_id: str, random_value: float) -> 'Injury':
        """
        Create an injury with random severity based on probability distribution.
        
        Severity distribution (from research.md):
        - 60% minor (0.0 to 0.6)
        - 30% moderate (0.6 to 0.9)
        - 10% severe (0.9 to 1.0)
        
        Args:
            player_id: ID of the affected player
            random_value: Random float between 0.0 and 1.0
            
        Returns:
            New Injury instance with randomly determined severity
        """
        if random_value < 0.6:
            return Injury.create_minor(player_id)
        elif random_value < 0.9:
            return Injury.create_moderate(player_id)
        else:
            return Injury.create_severe(player_id)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "injury-123",
                "player_id": "player-456",
                "severity": "moderate",
                "stat_reduction": 0.35,
                "healing_games": 2,
                "games_remaining": 1,
                "occurred_at": "2025-10-25T14:30:00Z"
            }
        }


class InjuryResponse(BaseModel):
    """Schema for injury API responses."""
    id: str
    player_id: str
    severity: InjurySeverity
    stat_reduction: float
    healing_games: int
    games_remaining: int
    occurred_at: datetime

    @classmethod
    def from_injury(cls, injury: Injury) -> 'InjuryResponse':
        """
        Create response schema from Injury entity.
        
        Args:
            injury: Injury entity
            
        Returns:
            InjuryResponse instance
        """
        return cls(
            id=injury.id,
            player_id=injury.player_id,
            severity=injury.severity,
            stat_reduction=injury.stat_reduction,
            healing_games=injury.healing_games,
            games_remaining=injury.games_remaining,
            occurred_at=injury.occurred_at
        )


class InjurySummary(BaseModel):
    """Condensed injury information for player displays."""
    severity: InjurySeverity
    games_remaining: int
    stat_reduction: float

    @classmethod
    def from_injury(cls, injury: Injury) -> 'InjurySummary':
        """
        Create summary from Injury entity.
        
        Args:
            injury: Injury entity
            
        Returns:
            InjurySummary instance
        """
        return cls(
            severity=injury.severity,
            games_remaining=injury.games_remaining,
            stat_reduction=injury.stat_reduction
        )
