"""
Integration tests for schedule generation API endpoints.

Tests the schedule creation and management endpoints to ensure:
- POST /api/leagues/{league_id}/schedule creates valid schedules
- GET /api/leagues/{league_id}/schedule retrieves schedule with status
- Schedule integrates correctly with league data
- Next game identification works

Test Coverage:
- T090: Integration test for schedule generation
- FR-024: Schedule creation and management

References:
- spec.md: US4 - Schedule generation requirements
- contracts/openapi.yaml: Schedule API specifications
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestScheduleGenerationAPI:
    """Integration tests for schedule generation endpoints."""
    
    def test_create_schedule_for_league(self, populated_league):
        """Test POST /api/leagues/{league_id}/schedule creates schedule."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert len(data["schedule"]) > 0
        
        # Verify schedule structure
        first_game = data["schedule"][0]
        assert "game_number" in first_game
        assert "team1_id" in first_game
        assert "team2_id" in first_game
        assert "completed" in first_game
        assert first_game["completed"] is False
    
    def test_create_schedule_requires_minimum_teams(self, create_league):
        """Test schedule creation fails with fewer than 2 teams."""
        # Arrange: League with only 1 team
        league = create_league(name="Small League")
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert
        assert response.status_code == 400
        assert "at least 2 teams" in response.json()["detail"].lower()
    
    def test_create_schedule_with_multiple_rounds(self, populated_league):
        """Test creating schedule with multiple rounds."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 3}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # With 2 teams, 3 rounds = 3 games
        expected_games = 1 * 3  # C(2,2) * 3 rounds
        assert len(data["schedule"]) == expected_games
    
    def test_retrieve_schedule(self, populated_league):
        """Test GET /api/leagues/{league_id}/schedule retrieves schedule."""
        # Arrange: Create schedule first
        league = populated_league["league"]
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/schedule")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert len(data["schedule"]) > 0
    
    def test_schedule_game_numbers_sequential(self, populated_league):
        """Test schedule games are numbered sequentially from 1."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert
        assert response.status_code == 200
        schedule = response.json()["schedule"]
        game_numbers = [game["game_number"] for game in schedule]
        expected_numbers = list(range(1, len(schedule) + 1))
        assert game_numbers == expected_numbers
    
    def test_schedule_includes_all_teams(self, populated_league):
        """Test schedule ensures all teams play."""
        # Arrange
        league = populated_league["league"]
        team_ids = league["team_ids"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert
        schedule = response.json()["schedule"]
        teams_in_schedule = set()
        for game in schedule:
            teams_in_schedule.add(game["team1_id"])
            teams_in_schedule.add(game["team2_id"])
        
        assert teams_in_schedule == set(team_ids)
    
    def test_replace_existing_schedule(self, populated_league):
        """Test creating new schedule replaces existing one."""
        # Arrange: Create initial schedule
        league = populated_league["league"]
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Act: Create new schedule with different rounds
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 2}
        )
        
        # Assert: New schedule replaces old
        assert response.status_code == 200
        schedule = response.json()["schedule"]
        # 2 teams, 2 rounds = 2 games
        assert len(schedule) == 2
    
    def test_schedule_not_found_for_invalid_league(self):
        """Test retrieving schedule for non-existent league."""
        # Act
        response = client.get("/api/leagues/invalid-id/schedule")
        
        # Assert
        assert response.status_code == 404


class TestScheduleStatusTracking:
    """Integration tests for schedule status indicators."""
    
    def test_initial_schedule_all_pending(self, populated_league):
        """Test newly created schedule has all games pending."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert
        schedule = response.json()["schedule"]
        assert all(game["completed"] is False for game in schedule)
    
    def test_next_game_identification(self, populated_league):
        """Test identifying next game in schedule."""
        # Arrange: Create schedule
        league = populated_league["league"]
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/schedule/next")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "game_number" in data
        assert data["game_number"] == 1
        assert data["completed"] is False
    
    def test_mark_game_completed(self, populated_league):
        """Test marking a game as completed after simulation."""
        # Arrange: Create schedule
        league = populated_league["league"]
        teams = populated_league["teams"]
        
        create_response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        schedule = create_response.json()["schedule"]
        first_game = schedule[0]
        
        # Simulate the game
        game_response = client.post(
            "/api/games",
            json={
                "league_id": league["id"],
                "team1_id": teams[0]["id"],
                "team2_id": teams[1]["id"]
            }
        )
        
        # Act: Retrieve schedule again
        response = client.get(f"/api/leagues/{league['id']}/schedule")
        
        # Assert: First game should be marked completed
        updated_schedule = response.json()["schedule"]
        assert updated_schedule[0]["completed"] is True
    
    def test_next_game_after_completion(self, populated_league):
        """Test next game moves to second game after first completes."""
        # Arrange: Create schedule with multiple games
        league = populated_league["league"]
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 2}
        )
        
        # Simulate first game
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        first_game = schedule[0]
        
        client.post(
            "/api/games",
            json={
                "league_id": league["id"],
                "team1_id": first_game["team1_id"],
                "team2_id": first_game["team2_id"]
            }
        )
        
        # Act: Get next game
        response = client.get(f"/api/leagues/{league['id']}/schedule/next")
        
        # Assert: Should be game 2
        assert response.status_code == 200
        next_game = response.json()
        assert next_game["game_number"] == 2
    
    def test_no_next_game_when_season_complete(self, populated_league):
        """Test next game returns null when all games completed."""
        # Arrange: Create schedule with 1 game
        league = populated_league["league"]
        teams = populated_league["teams"]
        
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Complete the only game
        client.post(
            "/api/games",
            json={
                "league_id": league["id"],
                "team1_id": teams[0]["id"],
                "team2_id": teams[1]["id"]
            }
        )
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/schedule/next")
        
        # Assert
        assert response.status_code == 200
        assert response.json() is None


class TestScheduleWithMultipleTeams:
    """Integration tests for schedules with various team counts."""
    
    def test_schedule_with_4_teams(self, storage, create_league, create_team, create_player):
        """Test schedule generation with 4 teams."""
        # Arrange: Create league with 4 teams
        league = create_league(name="Four Team League")
        
        for i in range(4):
            team = create_team(
                name=f"Team {i+1}",
                owner_name=f"Owner {i+1}",
                league_id=league["id"]
            )
            league["team_ids"].append(team["id"])
            
            # Add minimum roster
            for j in range(5):
                player = create_player(
                    name=f"Team{i+1} Player{j+1}",
                    team_id=team["id"],
                    is_starter=True
                )
                team["roster"].append(player["id"])
            
            storage.update_team(team["id"], team)
        
        storage.update_league(league["id"], league)
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert: 4 teams = C(4,2) = 6 games
        assert response.status_code == 200
        schedule = response.json()["schedule"]
        assert len(schedule) == 6
    
    def test_schedule_with_6_teams(self, storage, create_league, create_team, create_player):
        """Test schedule generation with 6 teams (realistic league size)."""
        # Arrange: Create league with 6 teams
        league = create_league(name="Six Team League")
        
        for i in range(6):
            team = create_team(
                name=f"Team {i+1}",
                owner_name=f"Owner {i+1}",
                league_id=league["id"]
            )
            league["team_ids"].append(team["id"])
            
            # Add minimum roster
            for j in range(5):
                player = create_player(
                    name=f"Team{i+1} Player{j+1}",
                    team_id=team["id"],
                    is_starter=True
                )
                team["roster"].append(player["id"])
            
            storage.update_team(team["id"], team)
        
        storage.update_league(league["id"], league)
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert: 6 teams = C(6,2) = 15 games
        assert response.status_code == 200
        schedule = response.json()["schedule"]
        assert len(schedule) == 15


class TestScheduleEdgeCases:
    """Test edge cases for schedule generation."""
    
    def test_schedule_with_zero_rounds_fails(self, populated_league):
        """Test schedule creation fails with 0 rounds."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 0}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_schedule_with_negative_rounds_fails(self, populated_league):
        """Test schedule creation fails with negative rounds."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": -1}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_schedule_preserves_team_ids(self, populated_league):
        """Test schedule uses exact team ID strings."""
        # Arrange
        league = populated_league["league"]
        original_team_ids = set(league["team_ids"])
        
        # Act
        response = client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Assert
        schedule = response.json()["schedule"]
        schedule_team_ids = set()
        for game in schedule:
            schedule_team_ids.add(game["team1_id"])
            schedule_team_ids.add(game["team2_id"])
        
        assert schedule_team_ids == original_team_ids
