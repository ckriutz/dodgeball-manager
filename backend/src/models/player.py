"""
Player model for the Dodgeball Fantasy League.

This module defines the Player entity with all attributes, validation rules,
and business logic for player management.

References:
- data-model.md: Player entity definition
- FR-001: Players aged 18-20 with 10 skill points
- FR-002: Sum of all skills must equal 10 for new players
- FR-003: Each skill must be 0-100
- FR-004: Player value calculation formula
"""

from datetime import datetime, timezone
from typing import Optional, Dict
from uuid import uuid4, UUID
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

from ..services.utils import calculate_player_value, validate_skill_distribution


class InjurySeverity(str, Enum):
    """Injury severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class Injury(BaseModel):
    """Player injury information."""
    severity: InjurySeverity
    affected_reduction: float = Field(
        ge=0.0,
        le=1.0,
        description="Percentage reduction of skills (0.2-0.5)"
    )
    games_remaining: int = Field(
        ge=0,
        le=3,
        description="Number of games until fully healed"
    )

    @field_validator('affected_reduction')
    @classmethod
    def validate_reduction_range(cls, v: float, info) -> float:
        """Validate that reduction is within expected range (0.2-0.5)."""
        severity = info.data.get('severity')
        if severity == InjurySeverity.MINOR and v != 0.2:
            raise ValueError("Minor injury must have 20% reduction (0.2)")
        elif severity == InjurySeverity.MODERATE and v != 0.35:
            raise ValueError("Moderate injury must have 35% reduction (0.35)")
        elif severity == InjurySeverity.SEVERE and v != 0.5:
            raise ValueError("Severe injury must have 50% reduction (0.5)")
        return v

    @field_validator('games_remaining')
    @classmethod
    def validate_healing_time(cls, v: int, info) -> int:
        """Validate that healing time matches severity."""
        severity = info.data.get('severity')
        if severity == InjurySeverity.MINOR and v != 1:
            raise ValueError("Minor injury heals in 1 game")
        elif severity == InjurySeverity.MODERATE and v != 2:
            raise ValueError("Moderate injury heals in 2 games")
        elif severity == InjurySeverity.SEVERE and v != 3:
            raise ValueError("Severe injury heals in 3 games")
        return v


class PlayerStats(BaseModel):
    """Player game statistics and progression."""
    throws_attempted: int = Field(default=0, ge=0)
    catches_made: int = Field(default=0, ge=0)
    times_hit: int = Field(default=0, ge=0)
    missed_throws: int = Field(default=0, ge=0)
    successful_hits: int = Field(default=0, ge=0)
    games_played: int = Field(default=0, ge=0, description="Number of games played as starter")
    
    # Progression system fields (US4)
    experience_points: int = Field(
        default=0,
        ge=0,
        description="Total XP earned from gameplay"
    )
    level: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Player level (1-100)"
    )
    available_skill_points: int = Field(
        default=0,
        ge=0,
        description="Unspent skill points from leveling"
    )

    def calculate_xp_for_next_level(self) -> int:
        """
        Calculate XP required for next level.
        Uses exponential scaling: 100 * level^1.5
        
        Examples:
            - Level 1->2: 100 XP
            - Level 2->3: 283 XP  
            - Level 5->6: 1118 XP
            - Level 10->11: 3162 XP
        
        Returns:
            XP needed to reach next level
        """
        return int(100 * (self.level ** 1.5))

    def calculate_total_xp_for_level(self, target_level: int) -> int:
        """
        Calculate cumulative XP needed to reach a target level.
        
        Args:
            target_level: Level to calculate XP for
            
        Returns:
            Total XP needed from level 1 to reach target_level
        """
        total = 0
        for lvl in range(1, target_level):
            total += int(100 * (lvl ** 1.5))
        return total

    def can_level_up(self) -> bool:
        """
        Check if player has enough XP to level up.
        
        Returns:
            True if player can level up, False otherwise
        """
        if self.level >= 100:
            return False
        next_level_threshold = self.calculate_total_xp_for_level(self.level + 1)
        return self.experience_points >= next_level_threshold

    def level_up(self) -> int:
        """
        Level up the player if they have enough XP.
        Grants 1 skill point per level gained.
        
        Returns:
            Number of levels gained (can be multiple if enough XP)
        """
        if not self.can_level_up():
            return 0
        
        levels_gained = 0
        while self.can_level_up() and self.level < 100:
            self.level += 1
            self.available_skill_points += 1
            levels_gained += 1
        
        return levels_gained

    def award_xp(self, amount: int) -> int:
        """
        Award XP and automatically level up if thresholds reached.
        
        Args:
            amount: XP to award
            
        Returns:
            Number of levels gained
        """
        if amount < 0:
            raise ValueError("XP amount must be non-negative")
        
        self.experience_points += amount
        return self.level_up()


class PlayerSkills(BaseModel):
    """Player skill attributes."""
    catching: int = Field(ge=0, le=100, description="Ability to catch thrown balls")
    throwing: int = Field(ge=0, le=100, description="Throwing accuracy and power")
    dodging: int = Field(ge=0, le=100, description="Evasion capability")
    speed: int = Field(ge=0, le=100, description="Movement and reaction speed")
    iq: int = Field(ge=0, le=100, description="Strategic thinking and positioning")
    luck: int = Field(ge=0, le=100, description="Random variance influence")

    @model_validator(mode='after')
    def validate_skill_sum_for_new_players(self) -> 'PlayerSkills':
        """
        Validate that skills sum to 10 for new players (FR-002).
        
        Note: This validation is primarily for new player generation.
        Existing players may have different totals after skill progression.
        """
        # For now, we'll just validate the range of each skill (0-100)
        # The sum validation will be enforced at the service layer during creation
        return self

    def to_dict(self) -> Dict[str, int]:
        """Convert skills to dictionary format."""
        return {
            'catching': self.catching,
            'throwing': self.throwing,
            'dodging': self.dodging,
            'speed': self.speed,
            'iq': self.iq,
            'luck': self.luck
        }

    def sum(self) -> int:
        """Calculate total skill points."""
        return (
            self.catching + self.throwing + self.dodging +
            self.speed + self.iq + self.luck
        )


class Player(BaseModel):
    """
    Player entity representing a dodgeball athlete.
    
    A player has skills, stats, and can be assigned to a team.
    All new players start as free agents (team_id=None).
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, description="Player name")
    age: int = Field(ge=18, le=100, description="Player age")
    avatar: str = Field(default="avatar-placeholder", description="Avatar identifier")
    skills: PlayerSkills
    value: int = Field(ge=0, description="Calculated dollar value")
    injury: Optional[Injury] = Field(default=None)
    stats: PlayerStats = Field(default_factory=PlayerStats)
    league_id: Optional[str] = Field(default=None, description="League this player belongs to")
    team_id: Optional[str] = Field(default=None, description="Assigned team ID or null for free agent")
    is_starter: bool = Field(default=False, description="Whether designated as starter")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('age')
    @classmethod
    def validate_new_player_age(cls, v: int) -> int:
        """
        Validate age for new players (FR-001).
        
        New players should be aged 18-20. Older ages are allowed for
        existing players after aging progression.
        """
        # Note: For new players, service layer should enforce 18-20 range
        # This validator just ensures age is reasonable (18+)
        if v < 18:
            raise ValueError("Player age must be at least 18")
        return v

    @model_validator(mode='after')
    def validate_starter_requires_team(self) -> 'Player':
        """Validate that starters must belong to a team."""
        if self.is_starter and self.team_id is None:
            raise ValueError("Player cannot be a starter without being on a team")
        return self

    def calculate_effective_skills(self) -> Dict[str, int]:
        """
        Calculate effective skills considering injuries.
        
        Returns:
            Dictionary of skill name to effective value
        """
        base_skills = self.skills.to_dict()
        
        if self.injury is None:
            return base_skills
        
        reduction = self.injury.affected_reduction
        return {
            skill: int(value * (1 - reduction))
            for skill, value in base_skills.items()
        }

    def recalculate_value(self) -> int:
        """
        Recalculate player value based on current skills, age, level, and games played.
        
        Comprehensive Formula (Updated Nov 4, 2025):
            base_value = (
                (sum_of_skills * 100) +           # Skills: primary factor
                (games_played * 50) +             # Experience bonus
                (level * 200) -                   # Progression bonus
                (age_penalty_after_30)            # Age penalty
            )
            age_penalty = max(0, (age - 30) * 500)  # 500 per year over 30
        
        Returns:
            Calculated player value in dollars
        """
        return calculate_player_value(
            skills=self.skills.to_dict(),
            age=self.age,
            level=self.stats.level,
            games_played=self.stats.games_played
        )

    def is_free_agent(self) -> bool:
        """Check if player is a free agent (not on any team)."""
        return self.team_id is None

    def assign_to_team(self, team_id: str) -> None:
        """
        Assign player to a team.
        
        Args:
            team_id: UUID string of the team
        """
        self.team_id = team_id
        # Note: is_starter should be set separately via team management

    def release_from_team(self) -> None:
        """Release player from their team, making them a free agent."""
        self.team_id = None
        self.is_starter = False

    def set_starter_status(self, is_starter: bool) -> None:
        """
        Set whether player is a starter.
        
        Args:
            is_starter: True if player should be a starter
            
        Raises:
            ValueError: If trying to make free agent a starter
        """
        if is_starter and self.team_id is None:
            raise ValueError("Cannot set free agent as starter")
        self.is_starter = is_starter

    def apply_injury(self, severity: InjurySeverity) -> None:
        """
        Apply an injury to the player.
        
        Args:
            severity: Injury severity level
        """
        reduction_map = {
            InjurySeverity.MINOR: 0.2,
            InjurySeverity.MODERATE: 0.35,
            InjurySeverity.SEVERE: 0.5
        }
        healing_map = {
            InjurySeverity.MINOR: 1,
            InjurySeverity.MODERATE: 2,
            InjurySeverity.SEVERE: 3
        }
        
        self.injury = Injury(
            severity=severity,
            affected_reduction=reduction_map[severity],
            games_remaining=healing_map[severity]
        )

    def heal_after_game(self) -> bool:
        """
        Reduce injury healing time by one game.
        
        Returns:
            True if player is now fully healed, False otherwise
        """
        if self.injury is None:
            return True
        
        self.injury.games_remaining -= 1
        
        if self.injury.games_remaining <= 0:
            self.injury = None
            return True
        
        return False

    def update_stats(
        self,
        throws_attempted: int = 0,
        catches_made: int = 0,
        times_hit: int = 0,
        missed_throws: int = 0,
        successful_hits: int = 0
    ) -> None:
        """
        Update player statistics after a game.
        
        Args:
            throws_attempted: Number of throws made
            catches_made: Number of successful catches
            times_hit: Number of times eliminated
            missed_throws: Number of missed throws
            successful_hits: Number of successful eliminations
        """
        self.stats.throws_attempted += throws_attempted
        self.stats.catches_made += catches_made
        self.stats.times_hit += times_hit
        self.stats.missed_throws += missed_throws
        self.stats.successful_hits += successful_hits

    def spend_skill_point(self, skill_name: str) -> bool:
        """
        Spend an available skill point to increase a skill.
        
        Args:
            skill_name: Name of skill to increase (catching, throwing, dodging, speed, iq, luck)
            
        Returns:
            True if successful, False if not enough points or skill at max
            
        Raises:
            ValueError: If skill name is invalid
        """
        valid_skills = ['catching', 'throwing', 'dodging', 'speed', 'iq', 'luck']
        if skill_name not in valid_skills:
            raise ValueError(f"Invalid skill name: {skill_name}")
        
        # Check if player has available points
        if self.stats.available_skill_points <= 0:
            return False
        
        # Check if skill is already at max
        current_value = getattr(self.skills, skill_name)
        if current_value >= 100:
            return False
        
        # Increase skill and spend point
        setattr(self.skills, skill_name, current_value + 1)
        self.stats.available_skill_points -= 1
        
        # Recalculate value
        self.value = self.recalculate_value()
        
        return True

    def get_progression_info(self) -> Dict[str, any]:
        """
        Get player progression information for UI display.
        
        Returns:
            Dictionary with level, XP, and progress to next level
        """
        current_xp = self.stats.experience_points
        current_level = self.stats.level
        
        # Calculate XP for current and next level
        current_level_xp = self.stats.calculate_total_xp_for_level(current_level)
        next_level_xp = self.stats.calculate_total_xp_for_level(current_level + 1)
        
        # XP needed for next level
        xp_for_next = next_level_xp - current_level_xp
        xp_progress = current_xp - current_level_xp
        
        return {
            'level': current_level,
            'experience_points': current_xp,
            'available_skill_points': self.stats.available_skill_points,
            'xp_for_next_level': xp_for_next,
            'xp_progress': xp_progress,
            'progress_percentage': (xp_progress / xp_for_next * 100) if xp_for_next > 0 else 100
        }

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Player 1",
                "age": 19,
                "avatar": "avatar-placeholder",
                "skills": {
                    "catching": 2,
                    "throwing": 2,
                    "dodging": 2,
                    "speed": 2,
                    "iq": 1,
                    "luck": 1
                },
                "value": 1000,
                "injury": None,
                "stats": {
                    "throws_attempted": 0,
                    "catches_made": 0,
                    "times_hit": 0,
                    "missed_throws": 0,
                    "successful_hits": 0,
                    "games_played": 0,
                    "experience_points": 0,
                    "level": 1,
                    "available_skill_points": 0
                },
                "league_id": None,
                "team_id": None,
                "is_starter": False
            }
        }


class PlayerCreate(BaseModel):
    """Schema for creating a new player."""
    name: str = Field(min_length=1)
    age: int = Field(ge=18, le=20, description="New players must be aged 18-20 (FR-001)")
    avatar: str = Field(default="avatar-placeholder")
    skills: PlayerSkills
    league_id: Optional[str] = Field(default=None, description="League this player belongs to")

    @model_validator(mode='after')
    def validate_skill_sum(self) -> 'PlayerCreate':
        """Validate that skills sum to 10 for new players (FR-002)."""
        is_valid, error_msg = validate_skill_distribution(
            self.skills.to_dict(),
            total_required=10
        )
        if not is_valid:
            raise ValueError(f"Invalid skill distribution: {error_msg}")
        return self

    def to_player(self) -> Player:
        """
        Convert creation schema to Player entity.
        
        Automatically calculates player value and initializes stats.
        For new players, level=1 and games_played=0.
        """
        # New players start at level 1 with 0 games played
        value = calculate_player_value(
            skills=self.skills.to_dict(),
            age=self.age,
            level=1,
            games_played=0
        )
        
        return Player(
            name=self.name,
            age=self.age,
            avatar=self.avatar,
            skills=self.skills,
            value=value,
            stats=PlayerStats(),
            league_id=self.league_id,
            team_id=None,
            is_starter=False
        )


class PlayerUpdate(BaseModel):
    """Schema for updating player fields."""
    name: Optional[str] = None
    avatar: Optional[str] = None
    team_id: Optional[str] = None
    is_starter: Optional[bool] = None

    @model_validator(mode='after')
    def validate_starter_update(self) -> 'PlayerUpdate':
        """Validate starter status changes."""
        if self.is_starter is True and self.team_id is None:
            raise ValueError("Cannot set player as starter without team assignment")
        return self
