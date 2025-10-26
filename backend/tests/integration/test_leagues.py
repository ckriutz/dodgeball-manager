"""
Integration tests for league creation endpoints.

Tests the POST /api/leagues and GET /api/leagues/{league_id} endpoints
to ensure correct league creation, retrieval, and error handling.

These tests use FastAPI's TestClient to make actual HTTP requests to the API.
Tests should fail initially (TDD) until the endpoints are implemented.

Test Coverage:
- POST /api/leagues: Create new league with valid data
- GET /api/leagues/{league_id}: Retrieve league by ID
- Error cases: Invalid data, missing league, validation failures
- Response schemas match OpenAPI contract

References:
- contracts/openapi.yaml: League endpoints specification
- FR-001a: Player count must be 50-100
- data-model.md: League entity definition
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


class TestCreateLeague:
    """Test suite for POST /api/leagues endpoint."""
    
    def test_create_league_with_defaults(self, client):
        """Test creating a league with minimal required data."""
        # Arrange
        league_data = {
            "name": "Elite Dodgeball League"
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["name"] == "Elite Dodgeball League"
        assert "settings" in data
        assert data["settings"]["player_count"] == 75  # Default value
        assert "team_ids" in data
        assert data["team_ids"] == []
        assert "game_ids" in data
        assert "created_at" in data
    
    def test_create_league_with_custom_player_count(self, client):
        """Test creating a league with custom player count."""
        # Arrange
        league_data = {
            "name": "Custom League",
            "player_count": 100
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["settings"]["player_count"] == 100
    
    def test_create_league_with_minimum_player_count(self, client):
        """Test creating league with minimum player count (50)."""
        # Arrange
        league_data = {
            "name": "Small League",
            "player_count": 50
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["settings"]["player_count"] == 50
    
    def test_create_league_with_maximum_player_count(self, client):
        """Test creating league with maximum player count (100)."""
        # Arrange
        league_data = {
            "name": "Large League",
            "player_count": 100
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["settings"]["player_count"] == 100
    
    def test_create_multiple_leagues(self, client):
        """Test creating multiple leagues with different names."""
        # Act: Create first league
        response1 = client.post("/api/leagues", json={"name": "League One"})
        
        # Assert: First league created
        assert response1.status_code == 201
        league1_id = response1.json()["id"]
        
        # Act: Create second league
        response2 = client.post("/api/leagues", json={"name": "League Two"})
        
        # Assert: Second league created with different ID
        assert response2.status_code == 201
        league2_id = response2.json()["id"]
        
        assert league1_id != league2_id


class TestCreateLeagueValidation:
    """Test validation errors for POST /api/leagues."""
    
    def test_create_league_missing_name(self, client):
        """Test that creating league without name fails."""
        # Arrange
        league_data = {}
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422
        data = response.json()
        assert "message" in data or "detail" in data
    
    def test_create_league_empty_name(self, client):
        """Test that empty league name fails validation."""
        # Arrange
        league_data = {
            "name": ""
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422
    
    def test_create_league_player_count_below_minimum(self, client):
        """Test that player count below 50 fails validation (FR-001a)."""
        # Arrange
        league_data = {
            "name": "Too Small League",
            "player_count": 49
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422
        data = response.json()
        # Should mention the minimum constraint
        message = str(data).lower()
        assert "50" in message or "minimum" in message
    
    def test_create_league_player_count_above_maximum(self, client):
        """Test that player count above 100 fails validation (FR-001a)."""
        # Arrange
        league_data = {
            "name": "Too Large League",
            "player_count": 101
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422
        data = response.json()
        # Should mention the maximum constraint
        message = str(data).lower()
        assert "100" in message or "maximum" in message
    
    def test_create_league_negative_player_count(self, client):
        """Test that negative player count fails validation."""
        # Arrange
        league_data = {
            "name": "Invalid League",
            "player_count": -10
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422
    
    def test_create_league_invalid_data_type(self, client):
        """Test that invalid data types fail validation."""
        # Arrange
        league_data = {
            "name": "Test League",
            "player_count": "not_a_number"
        }
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422


class TestGetLeague:
    """Test suite for GET /api/leagues/{league_id} endpoint."""
    
    def test_get_existing_league(self, client):
        """Test retrieving a league that exists."""
        # Arrange: Create a league first
        create_response = client.post("/api/leagues", json={"name": "Test League"})
        assert create_response.status_code == 201
        league_id = create_response.json()["id"]
        
        # Act: Get the league
        response = client.get(f"/api/leagues/{league_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == league_id
        assert data["name"] == "Test League"
        assert "settings" in data
        assert "team_ids" in data
        assert "created_at" in data
    
    def test_get_nonexistent_league(self, client):
        """Test retrieving a league that doesn't exist returns 404."""
        # Arrange: Use a random UUID that doesn't exist
        nonexistent_id = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = client.get(f"/api/leagues/{nonexistent_id}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "message" in data or "detail" in data
    
    def test_get_league_invalid_id_format(self, client):
        """Test retrieving league with invalid UUID format."""
        # Arrange
        invalid_id = "not-a-valid-uuid"
        
        # Act
        response = client.get(f"/api/leagues/{invalid_id}")
        
        # Assert
        # Should be either 400 (validation) or 404 (not found)
        assert response.status_code in [400, 404, 422]
    
    def test_get_league_returns_same_data_as_create(self, client):
        """Test that GET returns the same data as POST response."""
        # Arrange: Create league
        league_data = {
            "name": "Consistent League",
            "player_count": 80
        }
        create_response = client.post("/api/leagues", json=league_data)
        created_data = create_response.json()
        league_id = created_data["id"]
        
        # Act: Retrieve league
        get_response = client.get(f"/api/leagues/{league_id}")
        retrieved_data = get_response.json()
        
        # Assert: Data matches
        assert retrieved_data["id"] == created_data["id"]
        assert retrieved_data["name"] == created_data["name"]
        assert retrieved_data["settings"]["player_count"] == created_data["settings"]["player_count"]


class TestLeagueResponseSchema:
    """Test that league responses match the OpenAPI schema."""
    
    def test_create_league_response_schema(self, client):
        """Test that POST response includes all required fields."""
        # Arrange
        league_data = {"name": "Schema Test League"}
        
        # Act
        response = client.post("/api/leagues", json=league_data)
        
        # Assert: Check all required fields from OpenAPI schema
        assert response.status_code == 201
        data = response.json()
        
        # Required fields from openapi.yaml League schema
        required_fields = ["id", "name", "settings", "team_ids", "game_ids"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify nested settings structure
        assert "player_count" in data["settings"]
        assert isinstance(data["settings"]["player_count"], int)
        
        # Verify lists are initialized
        assert isinstance(data["team_ids"], list)
        assert isinstance(data["game_ids"], list)
    
    def test_get_league_response_schema(self, client):
        """Test that GET response includes all required fields."""
        # Arrange: Create league
        create_response = client.post("/api/leagues", json={"name": "Schema League"})
        league_id = create_response.json()["id"]
        
        # Act: Get league
        response = client.get(f"/api/leagues/{league_id}")
        
        # Assert: Same schema as create
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "name", "settings", "team_ids", "game_ids"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestLeagueStateManagement:
    """Test league state initialization and management."""
    
    def test_new_league_has_empty_teams_list(self, client):
        """Test that newly created league has no teams."""
        # Arrange & Act
        response = client.post("/api/leagues", json={"name": "New League"})
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["team_ids"] == []
    
    def test_new_league_has_empty_games_list(self, client):
        """Test that newly created league has no games."""
        # Arrange & Act
        response = client.post("/api/leagues", json={"name": "New League"})
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["game_ids"] == []
    
    def test_new_league_has_no_schedule(self, client):
        """Test that newly created league has no schedule."""
        # Arrange & Act
        response = client.post("/api/leagues", json={"name": "New League"})
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        # Schedule is optional initially, may be empty array or not present
        if "schedule" in data:
            assert data["schedule"] == []
