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
    Injury,
    InjurySeverity,
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

__all__ = [
    # Player models
    'Player',
    'PlayerCreate',
    'PlayerUpdate',
    'PlayerSkills',
    'PlayerStats',
    'Injury',
    'InjurySeverity',
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
]
