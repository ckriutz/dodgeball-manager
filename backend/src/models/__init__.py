"""
Models package for the Dodgeball Fantasy League.

This package contains all domain entities and data models.
"""

from .player import (
    Player,
    PlayerCreate,
    PlayerUpdate,
    PlayerSkills,
    PlayerStats,
    Injury as PlayerInjury,  # Keep for backward compatibility
    InjurySeverity as PlayerInjurySeverity,  # Keep for backward compatibility
)

from .league import (
    League,
    LeagueCreate,
    LeagueUpdate,
    LeagueResponse,
    LeagueSettings,
    LeagueStandings,
    StandingsEntry,
    ScheduleGame,
    ScheduleCreateRequest,
)

from .game import (
    Game,
    GameCreate,
    GameResponse,
    GameSummary,
    GameEvent,
    GameEventType,
    GameStatus,
)

from .injury import (
    Injury,
    InjuryResponse,
    InjurySummary,
    InjurySeverity,
)

__all__ = [
    # Player models
    'Player',
    'PlayerCreate',
    'PlayerUpdate',
    'PlayerSkills',
    'PlayerStats',
    'PlayerInjury',
    'PlayerInjurySeverity',
    # League models
    'League',
    'LeagueCreate',
    'LeagueUpdate',
    'LeagueResponse',
    'LeagueSettings',
    'LeagueStandings',
    'StandingsEntry',
    'ScheduleGame',
    'ScheduleCreateRequest',
    # Game models
    'Game',
    'GameCreate',
    'GameResponse',
    'GameSummary',
    'GameEvent',
    'GameEventType',
    'GameStatus',
    # Injury models
    'Injury',
    'InjuryResponse',
    'InjurySummary',
    'InjurySeverity',
]
