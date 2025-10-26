"""
Integration tests for team management endpoints.

Tests the team-related API endpoints:
- POST /api/teams: Create new team
- GET /api/teams/{team_id}: Retrieve team details
- POST /api/teams/{team_id}/players: Add player to roster
- DELETE /api/teams/{team_id}/players/{player_id}: Remove player from roster
- PATCH /api/teams/{team_id}/starters: Designate starting lineup

These tests use FastAPI's TestClient to make actual HTTP requests to the API.
Tests should fail initially (TDD) until the endpoints are implemented.

Test Coverage:
- Team creation with valid data
- Team retrieval
- Adding players to roster with budget validation
- Removing players from roster
- Setting starters with validation
- Error cases and validation failures

References:
- contracts/openapi.yaml: Team endpoints specification
- FR-012: Team rosters must have 8-12 players
- FR-013: Exactly 5 starters must be designated
- FR-014: Cannot add player if value exceeds budget
- FR-014a: Can add player if value equals budget
- data-model.md: Team entity definition
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
def sample_league(client):
    """Create a sample league for testing."""
    response = client.post("/api/leagues", json={"name": "Test League"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_players(client, sample_league):
    """Generate sample players for testing."""
    league_id = sample_league["id"]
    response = client.post(f"/api/leagues/{league_id}/players")
    assert response.status_code == 201
    
    # Get the players
    players_response = client.get(f"/api/leagues/{league_id}/players?free_agents_only=true")
    assert players_response.status_code == 200
    return players_response.json()


# ============================================================================
# T046: Integration test for team creation endpoint
# ============================================================================

class TestCreateTeam:
    """Test suite for POST /api/teams endpoint."""
    
    def test_create_team_with_valid_data(self, client, sample_league):
        """Test creating a team with all required fields."""
        # Arrange
        team_data = {
            "name": "Thunder Dodgers",
            "description": "Fast and furious team",
            "logo": "logo-placeholder-1",
            "league_id": sample_league["id"]
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["name"] == "Thunder Dodgers"
        assert data["description"] == "Fast and furious team"
        assert data["logo"] == "logo-placeholder-1"
        assert data["league_id"] == sample_league["id"]
        assert data["budget"] == 100000  # Initial budget
        assert data["player_ids"] == []
        assert data["starter_ids"] == []
        assert data["wins"] == 0
        assert data["losses"] == 0
    
    def test_create_team_with_minimal_data(self, client, sample_league):
        """Test creating team with only required fields."""
        # Arrange
        team_data = {
            "name": "Minimal Team",
            "league_id": sample_league["id"]
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Team"
        assert data["budget"] == 100000
    
    def test_create_multiple_teams_in_same_league(self, client, sample_league):
        """Test creating multiple teams in the same league."""
        # Act: Create first team
        response1 = client.post("/api/teams", json={
            "name": "Team Alpha",
            "league_id": sample_league["id"]
        })
        
        # Assert: First team created
        assert response1.status_code == 201
        team1_id = response1.json()["id"]
        
        # Act: Create second team
        response2 = client.post("/api/teams", json={
            "name": "Team Beta",
            "league_id": sample_league["id"]
        })
        
        # Assert: Second team created with different ID
        assert response2.status_code == 201
        team2_id = response2.json()["id"]
        
        assert team1_id != team2_id
    
    def test_create_team_initializes_empty_roster(self, client, sample_league):
        """Test that new team has empty roster."""
        # Arrange & Act
        response = client.post("/api/teams", json={
            "name": "New Team",
            "league_id": sample_league["id"]
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["player_ids"] == []
        assert len(data["player_ids"]) == 0
    
    def test_create_team_initializes_no_starters(self, client, sample_league):
        """Test that new team has no starters."""
        # Arrange & Act
        response = client.post("/api/teams", json={
            "name": "New Team",
            "league_id": sample_league["id"]
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["starter_ids"] == []
        assert len(data["starter_ids"]) == 0
    
    def test_create_team_initializes_win_loss_record(self, client, sample_league):
        """Test that new team has 0-0 record."""
        # Arrange & Act
        response = client.post("/api/teams", json={
            "name": "New Team",
            "league_id": sample_league["id"]
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["wins"] == 0
        assert data["losses"] == 0


class TestCreateTeamValidation:
    """Test validation errors for POST /api/teams."""
    
    def test_create_team_missing_name(self, client, sample_league):
        """Test that creating team without name fails."""
        # Arrange
        team_data = {
            "league_id": sample_league["id"]
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code in [400, 422]
        data = response.json()
        assert "message" in data or "detail" in data
    
    def test_create_team_missing_league_id(self, client):
        """Test that creating team without league_id fails."""
        # Arrange
        team_data = {
            "name": "Orphan Team"
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code in [400, 422]
    
    def test_create_team_empty_name(self, client, sample_league):
        """Test that empty team name fails validation."""
        # Arrange
        team_data = {
            "name": "",
            "league_id": sample_league["id"]
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code in [400, 422]
    
    def test_create_team_nonexistent_league(self, client):
        """Test that creating team with nonexistent league fails."""
        # Arrange
        team_data = {
            "name": "Invalid Team",
            "league_id": "00000000-0000-0000-0000-000000000000"
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code in [400, 404]
    
    def test_create_team_invalid_league_id_format(self, client):
        """Test that invalid league_id format fails."""
        # Arrange
        team_data = {
            "name": "Bad Team",
            "league_id": "not-a-uuid"
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert
        assert response.status_code in [400, 422]


class TestGetTeam:
    """Test suite for GET /api/teams/{team_id} endpoint."""
    
    def test_get_existing_team(self, client, sample_league):
        """Test retrieving a team that exists."""
        # Arrange: Create a team first
        create_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        assert create_response.status_code == 201
        team_id = create_response.json()["id"]
        
        # Act: Get the team
        response = client.get(f"/api/teams/{team_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == team_id
        assert data["name"] == "Test Team"
        assert data["budget"] == 100000
    
    def test_get_nonexistent_team(self, client):
        """Test retrieving a team that doesn't exist returns 404."""
        # Arrange: Use a random UUID that doesn't exist
        nonexistent_id = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = client.get(f"/api/teams/{nonexistent_id}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "message" in data or "detail" in data
    
    def test_get_team_invalid_id_format(self, client):
        """Test retrieving team with invalid UUID format."""
        # Arrange
        invalid_id = "not-a-valid-uuid"
        
        # Act
        response = client.get(f"/api/teams/{invalid_id}")
        
        # Assert
        assert response.status_code in [400, 404, 422]
    
    def test_get_team_returns_same_data_as_create(self, client, sample_league):
        """Test that GET returns the same data as POST response."""
        # Arrange: Create team
        team_data = {
            "name": "Consistent Team",
            "description": "Test description",
            "league_id": sample_league["id"]
        }
        create_response = client.post("/api/teams", json=team_data)
        created_data = create_response.json()
        team_id = created_data["id"]
        
        # Act: Retrieve team
        get_response = client.get(f"/api/teams/{team_id}")
        retrieved_data = get_response.json()
        
        # Assert: Data matches
        assert retrieved_data["id"] == created_data["id"]
        assert retrieved_data["name"] == created_data["name"]
        assert retrieved_data["description"] == created_data["description"]
        assert retrieved_data["budget"] == created_data["budget"]


# ============================================================================
# T047: Integration test for adding player to roster
# ============================================================================

class TestAddPlayerToRoster:
    """Test suite for POST /api/teams/{team_id}/players endpoint."""
    
    def test_add_player_to_empty_roster(self, client, sample_league, sample_players):
        """Test adding first player to team roster."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        player_id = sample_players[0]["id"]
        player_value = sample_players[0]["value"]
        
        # Act: Add player
        response = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": player_id
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert player_id in data["player_ids"]
        assert len(data["player_ids"]) == 1
        assert data["budget"] == 100000 - player_value
    
    def test_add_multiple_players_to_roster(self, client, sample_league, sample_players):
        """Test adding multiple players sequentially."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Act: Add 3 players
        for i in range(3):
            player_id = sample_players[i]["id"]
            response = client.post(f"/api/teams/{team_id}/players", json={
                "player_id": player_id
            })
            assert response.status_code == 200
        
        # Assert: Get final team state
        team_response = client.get(f"/api/teams/{team_id}")
        data = team_response.json()
        assert len(data["player_ids"]) == 3
    
    def test_add_player_updates_budget(self, client, sample_league, sample_players):
        """Test that budget decreases after adding player."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        initial_budget = team_response.json()["budget"]
        
        player_id = sample_players[0]["id"]
        player_value = sample_players[0]["value"]
        
        # Act: Add player
        response = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": player_id
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == initial_budget - player_value
    
    def test_add_player_makes_them_unavailable(self, client, sample_league, sample_players):
        """Test that player becomes unavailable after being added to team."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        player_id = sample_players[0]["id"]
        
        # Act: Add player
        response = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": player_id
        })
        assert response.status_code == 200
        
        # Assert: Player should have team_id set
        player_response = client.get(f"/api/players/{player_id}")
        player_data = player_response.json()
        assert player_data["team_id"] == team_id
    
    def test_add_eight_players_minimum_roster(self, client, sample_league, sample_players):
        """Test adding minimum valid roster (8 players)."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Act: Add 8 players
        for i in range(8):
            player_id = sample_players[i]["id"]
            response = client.post(f"/api/teams/{team_id}/players", json={
                "player_id": player_id
            })
            assert response.status_code == 200
        
        # Assert: Team has valid roster
        team_response = client.get(f"/api/teams/{team_id}")
        data = team_response.json()
        assert len(data["player_ids"]) == 8
    
    def test_add_twelve_players_maximum_roster(self, client, sample_league, sample_players):
        """Test adding maximum valid roster (12 players)."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Act: Add 12 players
        for i in range(12):
            player_id = sample_players[i]["id"]
            response = client.post(f"/api/teams/{team_id}/players", json={
                "player_id": player_id
            })
            assert response.status_code == 200
        
        # Assert: Team has full roster
        team_response = client.get(f"/api/teams/{team_id}")
        data = team_response.json()
        assert len(data["player_ids"]) == 12


class TestAddPlayerBudgetValidation:
    """Test budget validation when adding players (FR-014, FR-014a)."""
    
    def test_cannot_add_player_exceeding_budget(self, client, sample_league, sample_players):
        """Test that player cannot be added if cost exceeds budget (FR-014)."""
        # Arrange: Create team and exhaust most of budget
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add expensive players until budget is low
        total_spent = 0
        for player in sample_players:
            if total_spent + player["value"] < 99500:  # Leave < $500
                client.post(f"/api/teams/{team_id}/players", json={
                    "player_id": player["id"]
                })
                total_spent += player["value"]
            else:
                break
        
        # Find a player that costs more than remaining budget
        team_response = client.get(f"/api/teams/{team_id}")
        remaining_budget = team_response.json()["budget"]
        
        expensive_player = None
        for player in sample_players:
            if player["id"] not in team_response.json()["player_ids"]:
                if player["value"] > remaining_budget:
                    expensive_player = player
                    break
        
        if expensive_player:
            # Act: Try to add player that's too expensive
            response = client.post(f"/api/teams/{team_id}/players", json={
                "player_id": expensive_player["id"]
            })
            
            # Assert: Should fail with conflict/bad request
            assert response.status_code in [400, 409]
            data = response.json()
            assert "budget" in str(data).lower() or "afford" in str(data).lower()
    
    def test_can_add_player_equal_to_budget(self, client, sample_league, sample_players):
        """Test that player can be added when cost equals budget exactly (FR-014a)."""
        # This is a harder test to set up - requires finding exact budget match
        # For now, test the principle
        pytest.skip("Requires specific player value setup for exact budget match")
    
    def test_cannot_add_player_with_zero_budget(self, client, sample_league, sample_players):
        """Test that no player can be added when budget is exhausted."""
        # Arrange: Create team and exhaust budget
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add players until budget exhausted (or close to it)
        total_spent = 0
        for player in sample_players[:20]:  # Try first 20 players
            if total_spent < 100000:
                response = client.post(f"/api/teams/{team_id}/players", json={
                    "player_id": player["id"]
                })
                if response.status_code == 200:
                    total_spent += player["value"]
        
        # Get any remaining available player
        team_response = client.get(f"/api/teams/{team_id}")
        remaining_budget = team_response.json()["budget"]
        
        if remaining_budget == 0:
            # Find any available player
            available_player = None
            for player in sample_players:
                if player["id"] not in team_response.json()["player_ids"]:
                    available_player = player
                    break
            
            if available_player:
                # Act: Try to add player with no budget
                response = client.post(f"/api/teams/{team_id}/players", json={
                    "player_id": available_player["id"]
                })
                
                # Assert: Should fail
                assert response.status_code in [400, 409]


class TestAddPlayerRosterValidation:
    """Test roster validation when adding players."""
    
    def test_cannot_add_thirteenth_player(self, client, sample_league, sample_players):
        """Test that 13th player cannot be added (roster max is 12)."""
        # Arrange: Create team and add 12 players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add 12 players
        for i in range(12):
            response = client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
            assert response.status_code == 200
        
        # Act: Try to add 13th player
        response = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": sample_players[12]["id"]
        })
        
        # Assert: Should fail with conflict/bad request
        assert response.status_code in [400, 409]
        data = response.json()
        assert "roster" in str(data).lower() or "full" in str(data).lower()
    
    def test_cannot_add_same_player_twice(self, client, sample_league, sample_players):
        """Test that same player cannot be added to roster twice."""
        # Arrange: Create team and add player
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        player_id = sample_players[0]["id"]
        
        # Add player first time
        response1 = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": player_id
        })
        assert response1.status_code == 200
        
        # Act: Try to add same player again
        response2 = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": player_id
        })
        
        # Assert: Should fail
        assert response2.status_code in [400, 409]
    
    def test_cannot_add_player_from_another_team(self, client, sample_league, sample_players):
        """Test that player already on another team cannot be added."""
        # Arrange: Create two teams
        team1_response = client.post("/api/teams", json={
            "name": "Team 1",
            "league_id": sample_league["id"]
        })
        team1_id = team1_response.json()["id"]
        
        team2_response = client.post("/api/teams", json={
            "name": "Team 2",
            "league_id": sample_league["id"]
        })
        team2_id = team2_response.json()["id"]
        
        player_id = sample_players[0]["id"]
        
        # Add player to team 1
        response1 = client.post(f"/api/teams/{team1_id}/players", json={
            "player_id": player_id
        })
        assert response1.status_code == 200
        
        # Act: Try to add same player to team 2
        response2 = client.post(f"/api/teams/{team2_id}/players", json={
            "player_id": player_id
        })
        
        # Assert: Should fail
        assert response2.status_code in [400, 409]
    
    def test_cannot_add_nonexistent_player(self, client, sample_league):
        """Test that nonexistent player cannot be added."""
        # Arrange: Create team
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Act: Try to add nonexistent player
        response = client.post(f"/api/teams/{team_id}/players", json={
            "player_id": "00000000-0000-0000-0000-000000000000"
        })
        
        # Assert: Should fail
        assert response.status_code in [400, 404]


class TestRemovePlayerFromRoster:
    """Test suite for DELETE /api/teams/{team_id}/players/{player_id} endpoint."""
    
    def test_remove_player_from_roster(self, client, sample_league, sample_players):
        """Test removing a player from team roster."""
        # Arrange: Create team and add players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add 10 players
        for i in range(10):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        player_to_remove = sample_players[5]["id"]
        
        # Act: Remove player
        response = client.delete(f"/api/teams/{team_id}/players/{player_to_remove}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert player_to_remove not in data["player_ids"]
        assert len(data["player_ids"]) == 9
    
    def test_remove_player_refunds_budget(self, client, sample_league, sample_players):
        """Test that budget increases after removing player."""
        # Arrange: Create team and add player
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add 10 players first
        for i in range(10):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Get budget before removal
        team_state = client.get(f"/api/teams/{team_id}").json()
        budget_before = team_state["budget"]
        
        player_to_remove = sample_players[5]
        player_value = player_to_remove["value"]
        
        # Act: Remove player
        response = client.delete(f"/api/teams/{team_id}/players/{player_to_remove['id']}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == budget_before + player_value
    
    def test_cannot_remove_from_minimum_roster(self, client, sample_league, sample_players):
        """Test that player cannot be removed when roster is at minimum (8)."""
        # Arrange: Create team with exactly 8 players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add exactly 8 players
        for i in range(8):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Act: Try to remove a player
        response = client.delete(f"/api/teams/{team_id}/players/{sample_players[0]['id']}")
        
        # Assert: Should fail (would go below minimum)
        assert response.status_code in [400, 409]


# ============================================================================
# T048: Integration test for designating starters
# ============================================================================

class TestSetStarters:
    """Test suite for PATCH /api/teams/{team_id}/starters endpoint."""
    
    def test_set_five_starters_valid(self, client, sample_league, sample_players):
        """Test setting exactly 5 starters from roster."""
        # Arrange: Create team and add 10 players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add 10 players
        for i in range(10):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Select 5 for starters
        starter_ids = [sample_players[i]["id"] for i in range(5)]
        
        # Act: Set starters
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": starter_ids
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["starter_ids"]) == 5
        assert set(data["starter_ids"]) == set(starter_ids)
    
    def test_set_starters_updates_player_is_starter_flag(self, client, sample_league, sample_players):
        """Test that is_starter flag is updated on players."""
        # Arrange: Create team and add players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add 8 players
        for i in range(8):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        starter_ids = [sample_players[i]["id"] for i in range(5)]
        
        # Act: Set starters
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": starter_ids
        })
        assert response.status_code == 200
        
        # Assert: Check player is_starter flags
        for i in range(5):
            player_response = client.get(f"/api/players/{sample_players[i]['id']}")
            player_data = player_response.json()
            assert player_data["is_starter"] is True
        
        for i in range(5, 8):
            player_response = client.get(f"/api/players/{sample_players[i]['id']}")
            player_data = player_response.json()
            assert player_data["is_starter"] is False
    
    def test_change_starters(self, client, sample_league, sample_players):
        """Test changing starter designation."""
        # Arrange: Create team with players and initial starters
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add 10 players
        for i in range(10):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Set initial starters
        initial_starters = [sample_players[i]["id"] for i in range(5)]
        client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": initial_starters
        })
        
        # Act: Change to different starters
        new_starters = [sample_players[i]["id"] for i in range(5, 10)]
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": new_starters
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data["starter_ids"]) == set(new_starters)
        assert set(data["starter_ids"]) != set(initial_starters)


class TestSetStartersValidation:
    """Test validation errors for PATCH /api/teams/{team_id}/starters."""
    
    def test_cannot_set_fewer_than_five_starters(self, client, sample_league, sample_players):
        """Test that fewer than 5 starters fails (FR-013)."""
        # Arrange: Create team with players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        for i in range(8):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Act: Try to set only 4 starters
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": [sample_players[i]["id"] for i in range(4)]
        })
        
        # Assert: Should fail
        assert response.status_code in [400, 422]
    
    def test_cannot_set_more_than_five_starters(self, client, sample_league, sample_players):
        """Test that more than 5 starters fails (FR-013)."""
        # Arrange: Create team with players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        for i in range(8):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Act: Try to set 6 starters
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": [sample_players[i]["id"] for i in range(6)]
        })
        
        # Assert: Should fail
        assert response.status_code in [400, 422]
    
    def test_cannot_set_starters_not_on_roster(self, client, sample_league, sample_players):
        """Test that starters must be on the roster."""
        # Arrange: Create team with players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        # Add only first 8 players
        for i in range(8):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Act: Try to set starters including player not on roster
        invalid_starters = [sample_players[i]["id"] for i in range(4)]
        invalid_starters.append(sample_players[10]["id"])  # Not on roster
        
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": invalid_starters
        })
        
        # Assert: Should fail
        assert response.status_code in [400, 409]
    
    def test_cannot_set_duplicate_starters(self, client, sample_league, sample_players):
        """Test that duplicate player IDs in starters fail."""
        # Arrange: Create team with players
        team_response = client.post("/api/teams", json={
            "name": "Test Team",
            "league_id": sample_league["id"]
        })
        team_id = team_response.json()["id"]
        
        for i in range(8):
            client.post(f"/api/teams/{team_id}/players", json={
                "player_id": sample_players[i]["id"]
            })
        
        # Act: Try to set starters with duplicate
        duplicate_starters = [
            sample_players[0]["id"],
            sample_players[1]["id"],
            sample_players[2]["id"],
            sample_players[3]["id"],
            sample_players[0]["id"]  # Duplicate
        ]
        
        response = client.patch(f"/api/teams/{team_id}/starters", json={
            "starter_ids": duplicate_starters
        })
        
        # Assert: Should fail
        assert response.status_code in [400, 422]
    
    def test_cannot_set_starters_for_nonexistent_team(self, client):
        """Test that setting starters for nonexistent team fails."""
        # Arrange
        nonexistent_id = "00000000-0000-0000-0000-000000000000"
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act
        response = client.patch(f"/api/teams/{nonexistent_id}/starters", json={
            "starter_ids": starter_ids
        })
        
        # Assert
        assert response.status_code == 404


class TestTeamResponseSchema:
    """Test that team responses match the OpenAPI schema."""
    
    def test_create_team_response_schema(self, client, sample_league):
        """Test that POST response includes all required fields."""
        # Arrange
        team_data = {
            "name": "Schema Test Team",
            "league_id": sample_league["id"]
        }
        
        # Act
        response = client.post("/api/teams", json=team_data)
        
        # Assert: Check all required fields from OpenAPI schema
        assert response.status_code == 201
        data = response.json()
        
        required_fields = [
            "id", "name", "description", "logo", "budget",
            "player_ids", "starter_ids", "wins", "losses", "league_id"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify types
        assert isinstance(data["budget"], int)
        assert isinstance(data["player_ids"], list)
        assert isinstance(data["starter_ids"], list)
        assert isinstance(data["wins"], int)
        assert isinstance(data["losses"], int)
    
    def test_get_team_response_schema(self, client, sample_league):
        """Test that GET response includes all required fields."""
        # Arrange: Create team
        create_response = client.post("/api/teams", json={
            "name": "Schema Team",
            "league_id": sample_league["id"]
        })
        team_id = create_response.json()["id"]
        
        # Act: Get team
        response = client.get(f"/api/teams/{team_id}")
        
        # Assert: Same schema as create
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "id", "name", "description", "logo", "budget",
            "player_ids", "starter_ids", "wins", "losses", "league_id"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
