"""
Game model for the Dodgeball Fantasy League.

This module defines the Game entity with play-by-play event tracking,
game state management, and simulation support with deterministic seeds.

References:
- data-model.md: Game entity definition
- research.md: Game simulation algorithm
- FR-026: Both teams must have 5 starters
- FR-029: Game must end when one team fully eliminated
- NFR-003: Deterministic simulation with seed
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class GameEventType(str, Enum):
    """Types of events that can occur during a game."""
    BALL_PICKUP = "ball_pickup"
    THROW = "throw"
    HIT = "hit"
    CATCH = "catch"
    MISS = "miss"
    ELIMINATION = "elimination"
    INJURY = "injury"
    GAME_END = "game_end"


class GameEvent(BaseModel):
    """
    Represents a single event in the game's play-by-play history.
    
    Events track all actions that occur during the game simulation,
    providing a complete record for replay and statistics.
    """
    turn: int = Field(ge=1, description="Turn number when event occurred")
    type: GameEventType = Field(description="Type of event")
    thrower_id: Optional[str] = Field(
        default=None,
        description="Player ID of the thrower (if applicable)"
    )
    target_id: Optional[str] = Field(
        default=None,
        description="Player ID of the target (if applicable)"
    )
    outcome: str = Field(description="Human-readable description of what happened")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "turn": 1,
                "type": "hit",
                "thrower_id": "player-123",
                "target_id": "player-456",
                "outcome": "Player 123 hits Player 456 - eliminated!"
            }
        }


class GameStatus(str, Enum):
    """Game status states."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Game(BaseModel):
    """
    Game entity representing a match between two teams.
    
    A game tracks the complete play-by-play simulation of a dodgeball match,
    including all events, player actions, and final outcome. Games use a
    random seed to ensure deterministic replay for testing and debugging.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    league_id: str = Field(description="Parent league ID")
    team1_id: str = Field(description="Home team ID")
    team2_id: str = Field(description="Away team ID")
    team1_starters: List[str] = Field(
        default_factory=list,
        description="Player IDs that started for team 1 (exactly 5)"
    )
    team2_starters: List[str] = Field(
        default_factory=list,
        description="Player IDs that started for team 2 (exactly 5)"
    )
    events: List[GameEvent] = Field(
        default_factory=list,
        description="Play-by-play event history"
    )
    status: GameStatus = Field(
        default=GameStatus.SCHEDULED,
        description="Current game status"
    )
    winner_id: Optional[str] = Field(
        default=None,
        description="ID of the winning team (null until game completed)"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when game was completed"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for deterministic replay (NFR-003)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator('team1_starters')
    @classmethod
    def validate_team1_starters(cls, v: List[str], info) -> List[str]:
        """Validate team 1 has exactly 5 starters (FR-026)."""
        # Only validate if starters are set
        if v and len(v) != 5:
            raise ValueError(
                f"Team 1 must have exactly 5 starters (FR-026), got {len(v)}"
            )
        # Check for duplicates
        if v and len(v) != len(set(v)):
            raise ValueError("Team 1 starters cannot contain duplicate player IDs")
        return v

    @field_validator('team2_starters')
    @classmethod
    def validate_team2_starters(cls, v: List[str], info) -> List[str]:
        """Validate team 2 has exactly 5 starters (FR-026)."""
        # Only validate if starters are set
        if v and len(v) != 5:
            raise ValueError(
                f"Team 2 must have exactly 5 starters (FR-026), got {len(v)}"
            )
        # Check for duplicates
        if v and len(v) != len(set(v)):
            raise ValueError("Team 2 starters cannot contain duplicate player IDs")
        return v

    def is_ready_to_start(self) -> bool:
        """
        Check if game is ready to start (both teams have 5 starters).
        
        Returns:
            True if both teams have exactly 5 starters
        """
        return (
            len(self.team1_starters) == 5 and
            len(self.team2_starters) == 5 and
            self.status == GameStatus.SCHEDULED
        )

    def start_game(self, seed: Optional[int] = None) -> None:
        """
        Mark the game as in progress and set the random seed.
        
        Args:
            seed: Optional random seed for deterministic simulation
            
        Raises:
            ValueError: If game is not ready to start
        """
        if not self.is_ready_to_start():
            raise ValueError(
                "Cannot start game: Both teams must have 5 starters and "
                "game must be in SCHEDULED status"
            )
        
        self.status = GameStatus.IN_PROGRESS
        self.seed = seed
        self.events = []  # Clear any previous events

    def add_event(
        self,
        turn: int,
        event_type: GameEventType,
        outcome: str,
        thrower_id: Optional[str] = None,
        target_id: Optional[str] = None
    ) -> None:
        """
        Add a new event to the game's play-by-play history.
        
        Args:
            turn: Turn number when event occurred
            event_type: Type of event
            outcome: Human-readable description
            thrower_id: Optional player ID of thrower
            target_id: Optional player ID of target
        """
        event = GameEvent(
            turn=turn,
            type=event_type,
            thrower_id=thrower_id,
            target_id=target_id,
            outcome=outcome
        )
        self.events.append(event)

    def complete_game(self, winner_id: str) -> None:
        """
        Mark the game as completed with a winner.
        
        Args:
            winner_id: ID of the winning team
            
        Raises:
            ValueError: If winner is not one of the participating teams
        """
        if winner_id not in [self.team1_id, self.team2_id]:
            raise ValueError(
                f"Winner {winner_id} must be one of the participating teams "
                f"({self.team1_id}, {self.team2_id})"
            )
        
        self.status = GameStatus.COMPLETED
        self.winner_id = winner_id
        self.completed_at = datetime.now(timezone.utc)

    def get_loser_id(self) -> Optional[str]:
        """
        Get the ID of the losing team.
        
        Returns:
            ID of the losing team, or None if game not completed
        """
        if self.winner_id is None:
            return None
        
        return (
            self.team2_id if self.winner_id == self.team1_id
            else self.team1_id
        )

    def is_completed(self) -> bool:
        """Check if the game is completed."""
        return self.status == GameStatus.COMPLETED

    def get_event_count(self) -> int:
        """Get the total number of events in the game."""
        return len(self.events)

    def get_events_by_type(self, event_type: GameEventType) -> List[GameEvent]:
        """
        Get all events of a specific type.
        
        Args:
            event_type: Type of events to retrieve
            
        Returns:
            List of events matching the type
        """
        return [event for event in self.events if event.type == event_type]

    def get_player_events(self, player_id: str) -> List[GameEvent]:
        """
        Get all events involving a specific player.
        
        Args:
            player_id: Player ID to search for
            
        Returns:
            List of events where player was thrower or target
        """
        return [
            event for event in self.events
            if event.thrower_id == player_id or event.target_id == player_id
        ]

    def get_throw_count(self) -> int:
        """Get the total number of throws in the game."""
        return len([e for e in self.events if e.type == GameEventType.THROW])

    def get_hit_count(self) -> int:
        """Get the total number of successful hits."""
        return len([e for e in self.events if e.type == GameEventType.HIT])

    def get_catch_count(self) -> int:
        """Get the total number of successful catches."""
        return len([e for e in self.events if e.type == GameEventType.CATCH])

    def get_injury_count(self) -> int:
        """Get the total number of injuries that occurred."""
        return len([e for e in self.events if e.type == GameEventType.INJURY])

    def get_duration_turns(self) -> int:
        """
        Get the game duration in turns.
        
        Returns:
            Maximum turn number from events, or 0 if no events
        """
        if not self.events:
            return 0
        return max(event.turn for event in self.events)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "game-123",
                "league_id": "league-456",
                "team1_id": "team-789",
                "team2_id": "team-012",
                "team1_starters": [
                    "player-1", "player-2", "player-3", "player-4", "player-5"
                ],
                "team2_starters": [
                    "player-6", "player-7", "player-8", "player-9", "player-10"
                ],
                "events": [
                    {
                        "turn": 1,
                        "type": "throw",
                        "thrower_id": "player-1",
                        "target_id": "player-6",
                        "outcome": "Player 1 throws at Player 6"
                    },
                    {
                        "turn": 1,
                        "type": "hit",
                        "thrower_id": "player-1",
                        "target_id": "player-6",
                        "outcome": "Player 1 hits Player 6 - eliminated!"
                    }
                ],
                "status": "completed",
                "winner_id": "team-789",
                "completed_at": "2025-10-25T14:30:00Z",
                "seed": 42,
                "created_at": "2025-10-25T14:00:00Z"
            }
        }


class GameCreate(BaseModel):
    """Schema for creating a new game."""
    league_id: str = Field(description="League ID this game belongs to")
    team1_id: str = Field(description="Home team ID")
    team2_id: str = Field(description="Away team ID")
    seed: Optional[int] = Field(
        default=None,
        description="Optional random seed for deterministic simulation"
    )

    @field_validator('team1_id')
    @classmethod
    def validate_different_teams(cls, v: str, info) -> str:
        """Validate that teams are different."""
        team2_id = info.data.get('team2_id')
        if team2_id and v == team2_id:
            raise ValueError("team1_id and team2_id must be different")
        return v

    def to_game(
        self,
        team1_starters: List[str],
        team2_starters: List[str]
    ) -> Game:
        """
        Convert creation schema to Game entity.
        
        Args:
            team1_starters: List of 5 player IDs for team 1
            team2_starters: List of 5 player IDs for team 2
            
        Returns:
            New Game instance ready to start
        """
        return Game(
            league_id=self.league_id,
            team1_id=self.team1_id,
            team2_id=self.team2_id,
            team1_starters=team1_starters,
            team2_starters=team2_starters,
            status=GameStatus.SCHEDULED,
            seed=self.seed,
            events=[],
            winner_id=None,
            completed_at=None
        )


class GameResponse(BaseModel):
    """Schema for game API responses."""
    id: str
    league_id: str
    team1_id: str
    team2_id: str
    team1_starters: List[str]
    team2_starters: List[str]
    events: List[GameEvent]
    status: GameStatus
    winner_id: Optional[str]
    completed_at: Optional[datetime]
    seed: Optional[int]
    created_at: datetime

    @classmethod
    def from_game(cls, game: Game) -> 'GameResponse':
        """
        Create response schema from Game entity.
        
        Args:
            game: Game entity
            
        Returns:
            GameResponse instance
        """
        return cls(
            id=game.id,
            league_id=game.league_id,
            team1_id=game.team1_id,
            team2_id=game.team2_id,
            team1_starters=game.team1_starters,
            team2_starters=game.team2_starters,
            events=game.events,
            status=game.status,
            winner_id=game.winner_id,
            completed_at=game.completed_at,
            seed=game.seed,
            created_at=game.created_at
        )


class GameSummary(BaseModel):
    """Condensed game information for lists/history."""
    id: str
    team1_id: str
    team2_id: str
    winner_id: Optional[str]
    completed_at: Optional[datetime]
    event_count: int

    @classmethod
    def from_game(cls, game: Game) -> 'GameSummary':
        """
        Create summary from Game entity.
        
        Args:
            game: Game entity
            
        Returns:
            GameSummary instance
        """
        return cls(
            id=game.id,
            team1_id=game.team1_id,
            team2_id=game.team2_id,
            winner_id=game.winner_id,
            completed_at=game.completed_at,
            event_count=len(game.events)
        )
