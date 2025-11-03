"""
In-memory storage manager singleton for the dodgeball fantasy league.

This module provides a simple in-memory storage solution for the current milestone.
All data is stored in memory and will be lost when the application restarts.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class StorageData:
    """Container for all stored data."""
    players: Dict[str, Dict[str, Any]]
    teams: Dict[str, Dict[str, Any]]
    leagues: Dict[str, Dict[str, Any]]
    games: List[Dict[str, Any]]
    injuries: Dict[str, Dict[str, Any]]  # player_id -> injury data

    def __init__(self):
        self.players = {}
        self.teams = {}
        self.leagues = {}
        self.games = []
        self.injuries = {}


class MemoryStorage:
    """
    Singleton in-memory storage manager.

    Provides thread-safe access to all application data.
    In a future milestone, this could be replaced with a database layer.
    """

    _instance: Optional['MemoryStorage'] = None
    _data: StorageData

    def __new__(cls) -> 'MemoryStorage':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = StorageData()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset storage for testing purposes."""
        if cls._instance is not None:
            cls._instance._data = StorageData()

    # Player operations
    def create_player(self, player_data: Dict[str, Any]) -> str:
        """Create a new player and return its ID."""
        player_id = str(uuid.uuid4())
        player_data['id'] = player_id
        self._data.players[player_id] = player_data
        return player_id

    def get_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get a player by ID."""
        return self._data.players.get(player_id)

    def update_player(self, player_id: str, player_data: Dict[str, Any]) -> bool:
        """Update a player. Returns True if player exists."""
        if player_id not in self._data.players:
            return False
        self._data.players[player_id].update(player_data)
        return True

    def delete_player(self, player_id: str) -> bool:
        """Delete a player. Returns True if player existed."""
        if player_id not in self._data.players:
            return False
        del self._data.players[player_id]
        # Also remove from any injuries
        self._data.injuries.pop(player_id, None)
        return True

    def list_players(self, league_id: Optional[str] = None, free_agents_only: bool = False) -> List[Dict[str, Any]]:
        """List all players, optionally filtered by league or free agents."""
        players = list(self._data.players.values())

        if league_id:
            # Filter players in this league (either on teams or free agents)
            league_teams = [t for t in self._data.teams.values() if t.get('league_id') == league_id]
            team_player_ids = set()
            for team in league_teams:
                team_player_ids.update(team.get('player_ids', []))

            players = [p for p in players if p.get('team_id') in team_player_ids or p.get('team_id') is None]

        if free_agents_only:
            players = [p for p in players if p.get('team_id') is None]

        return players

    # Team operations
    def create_team(self, team_data: Dict[str, Any]) -> str:
        """Create a new team and return its ID."""
        team_id = str(uuid.uuid4())
        team_data['id'] = team_id
        self._data.teams[team_id] = team_data
        return team_id

    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get a team by ID."""
        return self._data.teams.get(team_id)

    def update_team(self, team_id: str, team_data: Dict[str, Any]) -> bool:
        """Update a team. Returns True if team exists."""
        if team_id not in self._data.teams:
            return False
        self._data.teams[team_id].update(team_data)
        return True

    def delete_team(self, team_id: str) -> bool:
        """Delete a team. Returns True if team existed."""
        if team_id not in self._data.teams:
            return False
        del self._data.teams[team_id]
        return True

    def list_teams(self, league_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all teams, optionally filtered by league."""
        teams = list(self._data.teams.values())
        if league_id:
            teams = [t for t in teams if t.get('league_id') == league_id]
        return teams

    # League operations
    def create_league(self, league_data: Dict[str, Any]) -> str:
        """Create a new league and return its ID."""
        league_id = str(uuid.uuid4())
        league_data['id'] = league_id
        self._data.leagues[league_id] = league_data
        return league_id

    def get_league(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Get a league by ID."""
        return self._data.leagues.get(league_id)

    def update_league(self, league_id: str, league_data: Dict[str, Any]) -> bool:
        """Update a league. Returns True if league exists."""
        if league_id not in self._data.leagues:
            return False
        self._data.leagues[league_id].update(league_data)
        return True

    def delete_league(self, league_id: str) -> bool:
        """Delete a league. Returns True if league existed."""
        if league_id not in self._data.leagues:
            return False
        del self._data.leagues[league_id]
        return True

    def list_leagues(self) -> List[Dict[str, Any]]:
        """List all leagues."""
        return list(self._data.leagues.values())

    # Game operations
    def create_game(self, game_data: Dict[str, Any]) -> str:
        """Create a new game and return its ID."""
        game_id = str(uuid.uuid4())
        game_data['id'] = game_id
        self._data.games.append(game_data)
        return game_id

    def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get a game by ID."""
        return next((g for g in self._data.games if g.get('id') == game_id), None)

    def update_game(self, game_id: str, game_data: Dict[str, Any]) -> bool:
        """Update a game. Returns True if game exists."""
        for i, game in enumerate(self._data.games):
            if game.get('id') == game_id:
                self._data.games[i].update(game_data)
                return True
        return False

    def list_games(self, league_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all games, optionally filtered by league."""
        games = self._data.games
        if league_id:
            games = [g for g in games if g.get('league_id') == league_id]
        return games

    # Injury operations
    def set_injury(self, player_id: str, injury_data: Dict[str, Any]) -> None:
        """Set injury data for a player."""
        self._data.injuries[player_id] = injury_data

    def get_injury(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get injury data for a player."""
        return self._data.injuries.get(player_id)

    def clear_injury(self, player_id: str) -> bool:
        """Clear injury for a player. Returns True if injury existed."""
        return self._data.injuries.pop(player_id, None) is not None

    def list_injuries(self) -> List[Dict[str, Any]]:
        """List all current injuries."""
        return list(self._data.injuries.values())

    # Utility methods
    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about stored data."""
        return {
            'players': len(self._data.players),
            'teams': len(self._data.teams),
            'leagues': len(self._data.leagues),
            'games': len(self._data.games),
            'injuries': len(self._data.injuries),
        }