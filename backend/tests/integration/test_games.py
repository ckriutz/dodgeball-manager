"""
Integration tests for game simulation endpoint.

This module tests the game simulation API endpoint including:
- Creating and simulating games
- Retrieving game details and history
- Validating game outcomes and events
- Error handling for invalid inputs

References:
- contracts/openapi.yaml: Game API endpoints
- FR-026: Games require exactly 5 starters per team
- FR-029: Game ends when one team is fully eliminated
- NFR-003: Deterministic simulation with seed
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.storage.memory_storage import MemoryStorage
from src.models.league import League
from src.models.team import Team
from src.models.player import Player, PlayerSkills


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset storage before each test."""
    storage = MemoryStorage()
    storage.reset()
    yield storage


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def league_with_two_teams(client):
    """Create a league with two teams that have complete rosters."""
    # Create league
    league_response = client.post(
        "/api/leagues",
        json={"name": "Test League", "player_count": 75}
    )
    assert league_response.status_code == 201
    league_id = league_response.json()["id"]
    
    # Generate players
    players_response = client.post(f"/api/leagues/{league_id}/players")
    assert players_response.status_code == 201
    players = players_response.json()["players"]
    
    # Create team 1
    team1_response = client.post(
        "/api/teams",
        json={
            "name": "Thunder Dodgers",
            "description": "Team 1",
            "league_id": league_id
        }
    )
    assert team1_response.status_code == 201
    team1_id = team1_response.json()["id"]
    
    # Create team 2
    team2_response = client.post(
        "/api/teams",
        json={
            "name": "Lightning Strikers",
            "description": "Team 2",
            "league_id": league_id
        }
    )
    assert team2_response.status_code == 201
    team2_id = team2_response.json()["id"]
    
    # Add 8 players to team 1
    for i in range(8):
        player_id = players[i]["id"]
        add_response = client.post(
            f"/api/teams/{team1_id}/players",
            json={"player_id": player_id}
        )
        assert add_response.status_code == 200
    
    # Add 8 players to team 2
    for i in range(8, 16):
        player_id = players[i]["id"]
        add_response = client.post(
            f"/api/teams/{team2_id}/players",
            json={"player_id": player_id}
        )
        assert add_response.status_code == 200
    
    # Set starters for team 1 (first 5 players)
    team1 = client.get(f"/api/teams/{team1_id}").json()
    starter_ids_1 = team1["player_ids"][:5]
    starters_response_1 = client.patch(
        f"/api/teams/{team1_id}/starters",
        json={"starter_ids": starter_ids_1}
    )
    assert starters_response_1.status_code == 200
    
    # Set starters for team 2 (first 5 players)
    team2 = client.get(f"/api/teams/{team2_id}").json()
    starter_ids_2 = team2["player_ids"][:5]
    starters_response_2 = client.patch(
        f"/api/teams/{team2_id}/starters",
        json={"starter_ids": starter_ids_2}
    )
    assert starters_response_2.status_code == 200
    
    return {
        "league_id": league_id,
        "team1_id": team1_id,
        "team2_id": team2_id,
        "players": players
    }


class TestGameSimulationEndpoint:
    """Test cases for POST /api/games endpoint."""
    
    def test_create_and_simulate_game_success(self, client, league_with_two_teams):
        """Test successful game simulation between two valid teams."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Simulate game
        response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "seed": 42
            }
        )
        
        assert response.status_code == 201
        game = response.json()
        
        # Verify game structure
        assert "id" in game
        assert game["league_id"] == league_id
        assert game["team1_id"] == team1_id
        assert game["team2_id"] == team2_id
        assert "winner_id" in game
        assert game["winner_id"] in [team1_id, team2_id]
        assert "events" in game
        assert len(game["events"]) > 0
        assert game["seed"] == 42
        assert "completed_at" in game
        
        # Verify events structure
        for event in game["events"]:
            assert "turn" in event
            assert "type" in event
            assert "outcome" in event
            
        # Last event should be game_end
        assert game["events"][-1]["type"] == "game_end"
    
    def test_simulate_game_with_seed_deterministic(self, client, league_with_two_teams):
        """Test that same seed produces identical game outcomes."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Simulate game 1 with seed 100
        response1 = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "seed": 100
            }
        )
        assert response1.status_code == 201
        game1 = response1.json()
        
        # Simulate game 2 with same seed 100
        response2 = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "seed": 100
            }
        )
        assert response2.status_code == 201
        game2 = response2.json()
        
        # Winners should be the same
        assert game1["winner_id"] == game2["winner_id"]
        
        # Number of events should be the same
        assert len(game1["events"]) == len(game2["events"])
        
        # Event types and turns should match
        for event1, event2 in zip(game1["events"], game2["events"]):
            assert event1["type"] == event2["type"]
            assert event1["turn"] == event2["turn"]
    
    def test_simulate_game_without_seed(self, client, league_with_two_teams):
        """Test that game can be simulated without explicit seed."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Simulate game without seed
        response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id
            }
        )
        
        assert response.status_code == 201
        game = response.json()
        
        # Game should still complete successfully
        assert "id" in game
        assert "winner_id" in game
        assert len(game["events"]) > 0
    
    def test_simulate_game_missing_league_id(self, client, league_with_two_teams):
        """Test error when league_id is missing."""
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        response = client.post(
            "/api/games",
            json={
                "team1_id": team1_id,
                "team2_id": team2_id
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_simulate_game_invalid_league_id(self, client, league_with_two_teams):
        """Test error when league_id doesn't exist."""
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        response = client.post(
            "/api/games",
            json={
                "league_id": "invalid-league-id",
                "team1_id": team1_id,
                "team2_id": team2_id
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()
    
    def test_simulate_game_invalid_team_id(self, client, league_with_two_teams):
        """Test error when team_id doesn't exist."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        
        response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": "invalid-team-id"
            }
        )
        
        assert response.status_code == 404
    
    def test_simulate_game_team_without_starters(self, client):
        """Test error when team doesn't have 5 starters designated."""
        # Create league
        league_response = client.post(
            "/api/leagues",
            json={"name": "Test League", "player_count": 20}
        )
        league_id = league_response.json()["id"]
        
        # Generate players
        client.post(f"/api/leagues/{league_id}/players")
        
        # Create teams but don't set starters
        team1_response = client.post(
            "/api/teams",
            json={"name": "Team 1", "league_id": league_id}
        )
        team1_id = team1_response.json()["id"]
        
        team2_response = client.post(
            "/api/teams",
            json={"name": "Team 2", "league_id": league_id}
        )
        team2_id = team2_response.json()["id"]
        
        # Try to simulate without setting starters
        response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id
            }
        )
        
        assert response.status_code == 400
        assert "starters" in response.json()["message"].lower()
    
    def test_simulate_game_same_team_twice(self, client, league_with_two_teams):
        """Test error when trying to simulate team against itself."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        
        response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team1_id
            }
        )
        
        assert response.status_code == 400
        assert "same team" in response.json()["message"].lower()


class TestGetGameEndpoint:
    """Test cases for GET /api/games/{game_id} endpoint."""
    
    def test_get_game_by_id_success(self, client, league_with_two_teams):
        """Test retrieving game details by ID."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Create game
        create_response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "seed": 42
            }
        )
        game_id = create_response.json()["id"]
        
        # Get game details
        response = client.get(f"/api/games/{game_id}")
        
        assert response.status_code == 200
        game = response.json()
        
        assert game["id"] == game_id
        assert game["league_id"] == league_id
        assert game["team1_id"] == team1_id
        assert game["team2_id"] == team2_id
        assert "winner_id" in game
        assert "events" in game
        assert len(game["events"]) > 0
    
    def test_get_game_invalid_id(self, client):
        """Test error when getting game with invalid ID."""
        response = client.get("/api/games/invalid-game-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()


class TestListGamesEndpoint:
    """Test cases for GET /api/games endpoint."""
    
    def test_list_all_games(self, client, league_with_two_teams):
        """Test listing all games."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Create 3 games
        game_ids = []
        for seed in [1, 2, 3]:
            response = client.post(
                "/api/games",
                json={
                    "league_id": league_id,
                    "team1_id": team1_id,
                    "team2_id": team2_id,
                    "seed": seed
                }
            )
            game_ids.append(response.json()["id"])
        
        # List all games
        response = client.get("/api/games")
        
        assert response.status_code == 200
        games = response.json()
        
        assert len(games) == 3
        assert all(game["id"] in game_ids for game in games)
    
    def test_list_games_by_league(self, client, league_with_two_teams):
        """Test filtering games by league_id."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Create 2 games in this league
        for seed in [10, 20]:
            client.post(
                "/api/games",
                json={
                    "league_id": league_id,
                    "team1_id": team1_id,
                    "team2_id": team2_id,
                    "seed": seed
                }
            )
        
        # List games for this league
        response = client.get(f"/api/games?league_id={league_id}")
        
        assert response.status_code == 200
        games = response.json()
        
        assert len(games) == 2
        assert all(game["league_id"] == league_id for game in games)
    
    def test_list_games_empty(self, client):
        """Test listing games when none exist."""
        response = client.get("/api/games")
        
        assert response.status_code == 200
        games = response.json()
        
        assert len(games) == 0


class TestGameStatsUpdates:
    """Test that player and team stats are updated after games."""
    
    def test_winner_team_record_updated(self, client, league_with_two_teams):
        """Test that winning team's record is updated."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Get initial records
        team1_before = client.get(f"/api/teams/{team1_id}").json()
        team2_before = client.get(f"/api/teams/{team2_id}").json()
        
        initial_wins_1 = team1_before["wins"]
        initial_losses_1 = team1_before["losses"]
        initial_wins_2 = team2_before["wins"]
        initial_losses_2 = team2_before["losses"]
        
        # Simulate game
        game_response = client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "seed": 42
            }
        )
        winner_id = game_response.json()["winner_id"]
        
        # Get updated records
        team1_after = client.get(f"/api/teams/{team1_id}").json()
        team2_after = client.get(f"/api/teams/{team2_id}").json()
        
        # Verify winner got a win and loser got a loss
        if winner_id == team1_id:
            assert team1_after["wins"] == initial_wins_1 + 1
            assert team1_after["losses"] == initial_losses_1
            assert team2_after["wins"] == initial_wins_2
            assert team2_after["losses"] == initial_losses_2 + 1
        else:
            assert team1_after["wins"] == initial_wins_1
            assert team1_after["losses"] == initial_losses_1 + 1
            assert team2_after["wins"] == initial_wins_2 + 1
            assert team2_after["losses"] == initial_losses_2
    
    def test_player_stats_updated(self, client, league_with_two_teams):
        """Test that player stats are updated after game."""
        league_id = league_with_two_teams["league_id"]
        team1_id = league_with_two_teams["team1_id"]
        team2_id = league_with_two_teams["team2_id"]
        
        # Get a starter player ID
        team1 = client.get(f"/api/teams/{team1_id}").json()
        player_id = team1["starter_ids"][0]
        
        # Get initial stats
        player_before = client.get(f"/api/players/{player_id}").json()
        
        # Simulate game
        client.post(
            "/api/games",
            json={
                "league_id": league_id,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "seed": 42
            }
        )
        
        # Get updated stats
        player_after = client.get(f"/api/players/{player_id}").json()
        
        # Some stats should have changed (player participated in game)
        stats_changed = (
            player_after["stats"]["throws_attempted"] > player_before["stats"]["throws_attempted"] or
            player_after["stats"]["catches_made"] > player_before["stats"]["catches_made"] or
            player_after["stats"]["times_hit"] > player_before["stats"]["times_hit"] or
            player_after["stats"]["missed_throws"] > player_before["stats"]["missed_throws"] or
            player_after["stats"]["successful_hits"] > player_before["stats"]["successful_hits"]
        )
        
        assert stats_changed, "Player stats should be updated after participating in game"
