"""
Pytest configuration and shared fixtures for backend tests.

This module provides fixtures for testing the Dodgeball Fantasy League backend,
including in-memory storage setup, sample data, and common test utilities.
"""

import pytest
from typing import Dict, List
from datetime import datetime, timezone

from src.storage.memory_storage import MemoryStorage


@pytest.fixture(autouse=True)
def reset_storage():
    """
    Automatically reset the storage singleton before each test.
    
    This ensures tests are isolated and don't affect each other.
    """
    storage = MemoryStorage()
    storage.reset()
    yield storage
    storage.reset()


@pytest.fixture
def storage():
    """
    Provide the MemoryStorage singleton instance.
    
    Returns:
        MemoryStorage: The storage instance
    """
    return MemoryStorage()


@pytest.fixture
def sample_player_data() -> Dict:
    """
    Sample player data for testing.
    
    Returns:
        Dictionary with valid player creation data
    """
    return {
        "name": "Test Player",
        "age": 19,
        "skills": {
            "catching": 2,
            "throwing": 2,
            "dodging": 2,
            "speed": 2,
            "iq": 1,
            "luck": 1
        },
        "value": 1000,
        "team_id": None,
        "is_starter": False,
        "injury": None,
        "stats": {
            "games_played": 0,
            "eliminations": 0,
            "catches": 0,
            "hits": 0,
            "blocks": 0,
            "times_eliminated": 0,
            "mvp_count": 0
        }
    }


@pytest.fixture
def sample_team_data() -> Dict:
    """
    Sample team data for testing.
    
    Returns:
        Dictionary with valid team creation data
    """
    return {
        "name": "Test Team",
        "owner_name": "Test Owner",
        "league_id": None,
        "budget_spent": 0,
        "budget_remaining": 100000,
        "roster": [],
        "wins": 0,
        "losses": 0
    }


@pytest.fixture
def sample_league_data() -> Dict:
    """
    Sample league data for testing.
    
    Returns:
        Dictionary with valid league creation data
    """
    return {
        "name": "Test League",
        "season": 1,
        "current_week": 0,
        "status": "setup",
        "teams": [],
        "games": []
    }


@pytest.fixture
def sample_game_data() -> Dict:
    """
    Sample game data for testing.
    
    Returns:
        Dictionary with valid game creation data
    """
    return {
        "league_id": None,
        "week": 1,
        "home_team_id": None,
        "away_team_id": None,
        "status": "scheduled",
        "home_score": 0,
        "away_score": 0,
        "events": [],
        "mvp_player_id": None,
        "scheduled_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_skills() -> Dict[str, int]:
    """
    Sample skill distribution for testing.
    
    Returns:
        Dictionary with valid skill values (sum = 10)
    """
    return {
        "catching": 2,
        "throwing": 2,
        "dodging": 2,
        "speed": 2,
        "iq": 1,
        "luck": 1
    }


@pytest.fixture
def sample_injury() -> Dict:
    """
    Sample injury data for testing.
    
    Returns:
        Dictionary with valid injury data
    """
    return {
        "type": "minor",
        "weeks_remaining": 1,
        "skill_reduction": 0.2
    }


@pytest.fixture
def sample_stats() -> Dict:
    """
    Sample player stats for testing.
    
    Returns:
        Dictionary with valid player stats
    """
    return {
        "games_played": 5,
        "eliminations": 10,
        "catches": 8,
        "hits": 12,
        "blocks": 6,
        "times_eliminated": 3,
        "mvp_count": 1
    }


@pytest.fixture
def create_player(storage, sample_player_data):
    """
    Factory fixture for creating test players.
    
    Returns:
        Function that creates a player with optional overrides
    
    Usage:
        def test_something(create_player):
            player = create_player(name="Custom Name", age=25)
    """
    def _create_player(**overrides):
        data = {**sample_player_data, **overrides}
        return storage.create_player(data)
    
    return _create_player


@pytest.fixture
def create_team(storage, sample_team_data):
    """
    Factory fixture for creating test teams.
    
    Returns:
        Function that creates a team with optional overrides
    
    Usage:
        def test_something(create_team):
            team = create_team(name="Custom Team")
    """
    def _create_team(**overrides):
        data = {**sample_team_data, **overrides}
        return storage.create_team(data)
    
    return _create_team


@pytest.fixture
def create_league(storage, sample_league_data):
    """
    Factory fixture for creating test leagues.
    
    Returns:
        Function that creates a league with optional overrides
    
    Usage:
        def test_something(create_league):
            league = create_league(name="Custom League")
    """
    def _create_league(**overrides):
        data = {**sample_league_data, **overrides}
        return storage.create_league(data)
    
    return _create_league


@pytest.fixture
def create_game(storage, sample_game_data):
    """
    Factory fixture for creating test games.
    
    Returns:
        Function that creates a game with optional overrides
    
    Usage:
        def test_something(create_game):
            game = create_game(week=2)
    """
    def _create_game(**overrides):
        data = {**sample_game_data, **overrides}
        return storage.create_game(data)
    
    return _create_game


@pytest.fixture
def populated_league(storage, create_league, create_team, create_player):
    """
    Create a fully populated league with teams and players for integration testing.
    
    Returns:
        Dictionary with league, teams, and players
    
    Structure:
        {
            'league': League object,
            'teams': [Team1, Team2],
            'players': {
                'team1': [Player1, Player2, ...],
                'team2': [Player1, Player2, ...]
            }
        }
    """
    # Create league
    league = create_league(name="Test League")
    
    # Create two teams
    team1 = create_team(
        name="Team Alpha",
        owner_name="Owner Alpha",
        league_id=league["id"]
    )
    team2 = create_team(
        name="Team Beta",
        owner_name="Owner Beta",
        league_id=league["id"]
    )
    
    # Update league with teams
    league["teams"].append(team1["id"])
    league["teams"].append(team2["id"])
    storage.update_league(league["id"], league)
    
    # Create 8 players for each team (minimum roster size)
    team1_players = []
    for i in range(8):
        is_starter = i < 5  # First 5 are starters
        player = create_player(
            name=f"Player Alpha {i+1}",
            team_id=team1["id"],
            is_starter=is_starter
        )
        team1_players.append(player)
        team1["roster"].append(player["id"])
        team1["budget_spent"] += player["value"]
        team1["budget_remaining"] -= player["value"]
    
    team2_players = []
    for i in range(8):
        is_starter = i < 5  # First 5 are starters
        player = create_player(
            name=f"Player Beta {i+1}",
            team_id=team2["id"],
            is_starter=is_starter
        )
        team2_players.append(player)
        team2["roster"].append(player["id"])
        team2["budget_spent"] += player["value"]
        team2["budget_remaining"] -= player["value"]
    
    # Update teams with rosters
    storage.update_team(team1["id"], team1)
    storage.update_team(team2["id"], team2)
    
    return {
        "league": league,
        "teams": [team1, team2],
        "players": {
            "team1": team1_players,
            "team2": team2_players
        }
    }


@pytest.fixture
def scheduled_game(storage, populated_league, create_game):
    """
    Create a scheduled game between two teams.
    
    Returns:
        Dictionary with game, league, and teams
    """
    league = populated_league["league"]
    teams = populated_league["teams"]
    
    game = create_game(
        league_id=league["id"],
        week=1,
        home_team_id=teams[0]["id"],
        away_team_id=teams[1]["id"],
        status="scheduled"
    )
    
    # Add game to league
    league["games"].append(game["id"])
    storage.update_league(league["id"], league)
    
    return {
        "game": game,
        "league": league,
        "teams": teams,
        "players": populated_league["players"]
    }


@pytest.fixture
def injured_player(create_player, sample_injury):
    """
    Create a player with an injury.
    
    Returns:
        Player object with injury
    """
    return create_player(injury=sample_injury)


@pytest.fixture
def player_with_stats(create_player, sample_stats):
    """
    Create a player with statistics.
    
    Returns:
        Player object with stats
    """
    return create_player(stats=sample_stats)


@pytest.fixture
def high_value_player(create_player):
    """
    Create a high-value player with maxed skills.
    
    Returns:
        Player object with high skills
    """
    return create_player(
        name="Star Player",
        age=25,
        skills={
            "catching": 5,
            "throwing": 3,
            "dodging": 2,
            "speed": 0,
            "iq": 0,
            "luck": 0
        },
        value=1000  # Will be recalculated based on skills/age
    )


@pytest.fixture
def old_player(create_player):
    """
    Create an older player with age discount.
    
    Returns:
        Player object with reduced value due to age
    """
    return create_player(
        name="Veteran Player",
        age=35,
        skills={
            "catching": 2,
            "throwing": 2,
            "dodging": 2,
            "speed": 2,
            "iq": 1,
            "luck": 1
        },
        value=750  # Reduced due to age
    )


@pytest.fixture
def full_roster_team(storage, create_team, create_player):
    """
    Create a team with a full roster (12 players).
    
    Returns:
        Team object with full roster
    """
    team = create_team(name="Full Roster Team")
    
    players = []
    for i in range(12):
        is_starter = i < 5
        player = create_player(
            name=f"Player {i+1}",
            team_id=team["id"],
            is_starter=is_starter
        )
        players.append(player)
        team["roster"].append(player["id"])
        team["budget_spent"] += player["value"]
        team["budget_remaining"] -= player["value"]
    
    storage.update_team(team["id"], team)
    
    return team


@pytest.fixture
def budget_exhausted_team(create_team):
    """
    Create a team that has exhausted its budget.
    
    Returns:
        Team object with no remaining budget
    """
    return create_team(
        name="Broke Team",
        budget_spent=100000,
        budget_remaining=0
    )
