"""
Integration tests for player generation endpoints.

Tests the POST /api/leagues/{league_id}/players and GET /api/leagues/{league_id}/players
endpoints to ensure correct player generation, retrieval, and filtering.

These tests use FastAPI's TestClient to make actual HTTP requests to the API.
Tests should fail initially (TDD) until the endpoints are implemented.

Test Coverage:
- POST /api/leagues/{league_id}/players: Generate players for a league
- GET /api/leagues/{league_id}/players: List all players in league
- Free agents filter: Query parameter to filter free agents only
- Player validation: Skills sum to 10, ages 18-20, values calculated correctly
- Error cases: Invalid league ID, duplicate generation, validation failures

References:
- contracts/openapi.yaml: Player endpoints specification
- FR-001: Players aged 18-20 with 10 skill points
- FR-002: Sum of all skills must equal 10
- FR-003: Each skill must be 0-100
- FR-004: Player value calculation
- data-model.md: Player entity definition
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.storage.memory_storage import MemoryStorage


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_storage_for_integration():
    """Reset storage before each integration test."""
    storage = MemoryStorage()
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def league_id(client):
    """Create a league and return its ID."""
    response = client.post("/api/leagues", json={"name": "Test League"})
    assert response.status_code == 201
    return response.json()["id"]


class TestGeneratePlayers:
    """Test suite for POST /api/leagues/{league_id}/players endpoint."""
    
    def test_generate_players_default_count(self, client, league_id):
        """Test generating players with default count (75)."""
        # Act
        response = client.post(f"/api/leagues/{league_id}/players")
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "count" in data
        assert "players" in data
        assert data["count"] == 75
        assert len(data["players"]) == 75
    
    def test_generate_players_custom_count(self, client, league_id):
        """Test generating specific number of players."""
        # Note: This assumes the endpoint supports player_count from league settings
        # If league was created with player_count=50, it should generate 50
        
        # Arrange: Create league with specific count
        league_response = client.post("/api/leagues", json={
            "name": "Custom Count League",
            "player_count": 50
        })
        custom_league_id = league_response.json()["id"]
        
        # Act
        response = client.post(f"/api/leagues/{custom_league_id}/players")
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["count"] == 50
        assert len(data["players"]) == 50
    
    def test_generate_players_maximum_count(self, client):
        """Test generating maximum number of players (100)."""
        # Arrange
        league_response = client.post("/api/leagues", json={
            "name": "Max Players League",
            "player_count": 100
        })
        max_league_id = league_response.json()["id"]
        
        # Act
        response = client.post(f"/api/leagues/{max_league_id}/players")
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["count"] == 100
        assert len(data["players"]) == 100
    
    def test_generate_players_for_nonexistent_league(self, client):
        """Test generating players for league that doesn't exist."""
        # Arrange
        nonexistent_id = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = client.post(f"/api/leagues/{nonexistent_id}/players")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "message" in data or "detail" in data


class TestGeneratedPlayerValidation:
    """Test that generated players meet all validation requirements."""
    
    def test_all_players_have_required_fields(self, client, league_id):
        """Test that all generated players have required fields."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        assert response.status_code == 201
        players = response.json()["players"]
        
        # Assert: Check each player has required fields
        required_fields = ["id", "name", "age", "avatar", "skills", "value", "stats", "team_id", "is_starter"]
        
        for player in players:
            for field in required_fields:
                assert field in player, f"Player missing required field: {field}"
    
    def test_all_players_age_in_valid_range(self, client, league_id):
        """Test that all players have age between 18-20 (FR-001)."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            assert 18 <= player["age"] <= 20, f"Player age {player['age']} outside range [18, 20]"
    
    def test_all_players_skills_sum_to_ten(self, client, league_id):
        """Test that all players have exactly 10 total skill points (FR-002)."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            skills = player["skills"]
            skill_sum = sum(skills.values())
            assert skill_sum == 10, f"Player {player['id']} has skill sum of {skill_sum}, expected 10"
    
    def test_all_players_skills_have_six_attributes(self, client, league_id):
        """Test that all players have all six skill attributes."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        required_skills = {"catching", "throwing", "dodging", "speed", "iq", "luck"}
        
        for player in players:
            skills = player["skills"]
            assert set(skills.keys()) == required_skills, f"Player {player['id']} missing skills"
    
    def test_all_players_skills_in_valid_range(self, client, league_id):
        """Test that all skill values are between 0-100 (FR-003)."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            skills = player["skills"]
            for skill_name, skill_value in skills.items():
                assert 0 <= skill_value <= 100, \
                    f"Player {player['id']} {skill_name} value {skill_value} outside [0, 100]"
    
    def test_all_players_have_calculated_value(self, client, league_id):
        """Test that all players have a value calculated correctly (FR-004)."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            # Verify value exists and is positive integer
            assert "value" in player
            assert isinstance(player["value"], int)
            assert player["value"] > 0
            
            # Verify formula: sum(skills) * 100 * age_factor
            skill_sum = sum(player["skills"].values())
            expected_base_value = skill_sum * 100
            
            # For ages 18-20, age factor is 1.0 (no discount)
            assert player["value"] == expected_base_value, \
                f"Player {player['id']} value {player['value']} != expected {expected_base_value}"
    
    def test_all_players_start_as_free_agents(self, client, league_id):
        """Test that all newly generated players have no team."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            assert player["team_id"] is None, f"Player {player['id']} should be free agent"
            assert player["is_starter"] is False, f"Player {player['id']} should not be starter"
    
    def test_all_players_have_initialized_stats(self, client, league_id):
        """Test that all players start with zero stats."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            stats = player["stats"]
            # All stat values should be 0 for new players
            assert all(value == 0 for value in stats.values()), \
                f"Player {player['id']} has non-zero initial stats"
    
    def test_all_players_have_no_injury(self, client, league_id):
        """Test that all newly generated players are healthy."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        for player in players:
            assert player.get("injury") is None, f"Player {player['id']} should not be injured"
    
    def test_all_players_have_unique_ids(self, client, league_id):
        """Test that all generated players have unique IDs."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert
        player_ids = [p["id"] for p in players]
        assert len(player_ids) == len(set(player_ids)), "Duplicate player IDs found"
    
    def test_players_have_variety_in_skills(self, client, league_id):
        """Test that generated players have different skill distributions."""
        # Arrange & Act
        response = client.post(f"/api/leagues/{league_id}/players")
        players = response.json()["players"]
        
        # Assert: Collect skill distributions
        skill_distributions = []
        for player in players:
            skills = player["skills"]
            # Create tuple of sorted skill values for comparison
            distribution = tuple(sorted(skills.values()))
            skill_distributions.append(distribution)
        
        # At least some variety should exist (not all identical)
        unique_distributions = set(skill_distributions)
        assert len(unique_distributions) > 1, "All players have identical skill distributions"


class TestListPlayers:
    """Test suite for GET /api/leagues/{league_id}/players endpoint."""
    
    def test_list_players_in_league(self, client, league_id):
        """Test listing all players in a league."""
        # Arrange: Generate players
        gen_response = client.post(f"/api/leagues/{league_id}/players")
        assert gen_response.status_code == 201
        generated_count = gen_response.json()["count"]
        
        # Act: List players
        response = client.get(f"/api/leagues/{league_id}/players")
        
        # Assert
        assert response.status_code == 200
        players = response.json()
        assert isinstance(players, list)
        assert len(players) == generated_count
    
    def test_list_players_empty_league(self, client, league_id):
        """Test listing players in league with no players."""
        # Act: List players without generating any
        response = client.get(f"/api/leagues/{league_id}/players")
        
        # Assert
        assert response.status_code == 200
        players = response.json()
        assert isinstance(players, list)
        assert len(players) == 0
    
    def test_list_players_nonexistent_league(self, client):
        """Test listing players for league that doesn't exist."""
        # Arrange
        nonexistent_id = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = client.get(f"/api/leagues/{nonexistent_id}/players")
        
        # Assert
        assert response.status_code == 404


class TestFilterFreeAgents:
    """Test suite for free agents filter on GET /api/leagues/{league_id}/players."""
    
    def test_filter_free_agents_only(self, client, league_id):
        """Test filtering to show only free agents."""
        # Arrange: Generate players (all should be free agents initially)
        client.post(f"/api/leagues/{league_id}/players")
        
        # Act: Request with free_agents_only=true
        response = client.get(f"/api/leagues/{league_id}/players?free_agents_only=true")
        
        # Assert
        assert response.status_code == 200
        players = response.json()
        
        # All players should be free agents (team_id is None)
        assert len(players) == 75  # Default count
        for player in players:
            assert player["team_id"] is None
    
    def test_filter_all_players_default(self, client, league_id):
        """Test that default behavior shows all players."""
        # Arrange: Generate players
        client.post(f"/api/leagues/{league_id}/players")
        
        # Act: Request without filter (or with free_agents_only=false)
        response = client.get(f"/api/leagues/{league_id}/players")
        
        # Assert
        assert response.status_code == 200
        players = response.json()
        assert len(players) == 75


class TestPlayerGenerationErrorCases:
    """Test error handling for player generation."""
    
    def test_cannot_generate_players_twice(self, client, league_id):
        """Test that generating players twice for same league may fail or be idempotent."""
        # Arrange: Generate players once
        first_response = client.post(f"/api/leagues/{league_id}/players")
        assert first_response.status_code == 201
        
        # Act: Try to generate again
        second_response = client.post(f"/api/leagues/{league_id}/players")
        
        # Assert: Either fails (409 conflict) or is idempotent (returns existing)
        # Implementation may choose either behavior
        assert second_response.status_code in [201, 409], \
            "Should either succeed (idempotent) or conflict (409)"
    
    def test_invalid_league_id_format(self, client):
        """Test player generation with invalid UUID format."""
        # Arrange
        invalid_id = "not-a-valid-uuid"
        
        # Act
        response = client.post(f"/api/leagues/{invalid_id}/players")
        
        # Assert
        assert response.status_code in [400, 404, 422]


class TestPlayerResponseConsistency:
    """Test consistency between generation and listing responses."""
    
    def test_generated_players_appear_in_list(self, client, league_id):
        """Test that generated players can be retrieved via list endpoint."""
        # Arrange & Act: Generate players
        gen_response = client.post(f"/api/leagues/{league_id}/players")
        generated_players = gen_response.json()["players"]
        generated_ids = {p["id"] for p in generated_players}
        
        # Act: List players
        list_response = client.get(f"/api/leagues/{league_id}/players")
        listed_players = list_response.json()
        listed_ids = {p["id"] for p in listed_players}
        
        # Assert: Same players
        assert generated_ids == listed_ids
    
    def test_player_data_consistent_between_endpoints(self, client, league_id):
        """Test that player data is identical in generation and list responses."""
        # Arrange & Act: Generate players
        gen_response = client.post(f"/api/leagues/{league_id}/players")
        generated_players = {p["id"]: p for p in gen_response.json()["players"]}
        
        # Act: List players
        list_response = client.get(f"/api/leagues/{league_id}/players")
        listed_players = {p["id"]: p for p in list_response.json()}
        
        # Assert: Data matches for each player
        for player_id in generated_players:
            assert player_id in listed_players
            gen_player = generated_players[player_id]
            list_player = listed_players[player_id]
            
            # Compare key fields
            assert gen_player["name"] == list_player["name"]
            assert gen_player["age"] == list_player["age"]
            assert gen_player["skills"] == list_player["skills"]
            assert gen_player["value"] == list_player["value"]


class TestMultipleLeaguesIsolation:
    """Test that players are isolated between different leagues."""
    
    def test_players_isolated_between_leagues(self, client):
        """Test that players generated in one league don't appear in another."""
        # Arrange: Create two leagues
        league1_resp = client.post("/api/leagues", json={"name": "League 1"})
        league1_id = league1_resp.json()["id"]
        
        league2_resp = client.post("/api/leagues", json={"name": "League 2"})
        league2_id = league2_resp.json()["id"]
        
        # Act: Generate players in league 1 only
        client.post(f"/api/leagues/{league1_id}/players")
        
        # Assert: League 1 has players
        league1_players = client.get(f"/api/leagues/{league1_id}/players").json()
        assert len(league1_players) == 75
        
        # Assert: League 2 has no players
        league2_players = client.get(f"/api/leagues/{league2_id}/players").json()
        assert len(league2_players) == 0
