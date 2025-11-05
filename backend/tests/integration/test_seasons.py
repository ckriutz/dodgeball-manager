"""
Integration tests for season completion and archiving.

Tests the season lifecycle management to ensure:
- POST /api/leagues/{league_id}/seasons/finish completes season
- Season archives preserve historical data
- POST /api/leagues/{league_id}/seasons/start begins new season
- Age progression occurs at season end

Test Coverage:
- T091: Integration test for season completion and archiving
- FR-030: Season history storage and retrieval
- FR-010: Age progression at season end

References:
- spec.md: US4 - Season management requirements
- contracts/openapi.yaml: Season API specifications
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestSeasonCompletion:
    """Integration tests for completing seasons."""
    
    def test_finish_season_after_all_games(self, populated_league):
        """Test POST /api/leagues/{league_id}/seasons/finish completes season."""
        # Arrange: Create and complete schedule
        league = populated_league["league"]
        teams = populated_league["teams"]
        
        # Create schedule
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Complete all games
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Act
        response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "season_number" in data
        assert "final_standings" in data
        assert "mvp" in data
        assert "champion" in data
    
    def test_finish_season_fails_if_games_remaining(self, populated_league):
        """Test cannot finish season with incomplete schedule."""
        # Arrange: Create schedule but don't complete games
        league = populated_league["league"]
        
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Act: Try to finish without completing games
        response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Assert
        assert response.status_code == 400
        assert "incomplete games" in response.json()["detail"].lower()
    
    def test_finish_season_identifies_champion(self, populated_league):
        """Test season completion identifies champion (team with most wins)."""
        # Arrange: Complete season
        league = populated_league["league"]
        teams = populated_league["teams"]
        
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Complete games
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Act
        response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["champion"]["team_id"] in [t["id"] for t in teams]
        assert data["champion"]["wins"] > 0
    
    def test_finish_season_calculates_mvp(self, populated_league):
        """Test season completion calculates MVP."""
        # Arrange: Complete season with games
        league = populated_league["league"]
        
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        # Complete games
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Act
        response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "mvp" in data
        assert data["mvp"] is not None
        assert "player_id" in data["mvp"]
        assert "name" in data["mvp"]
    
    def test_finish_season_returns_statistical_leaders(self, populated_league):
        """Test season completion returns statistical leaders."""
        # Arrange: Complete season
        league = populated_league["league"]
        
        client.post(
            f"/api/leagues/{league['id']}/schedule",
            json={"rounds": 1}
        )
        
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Act
        response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "statistical_leaders" in data
        leaders = data["statistical_leaders"]
        assert "most_hits" in leaders
        assert "most_catches" in leaders


class TestSeasonArchiving:
    """Integration tests for season history archiving."""
    
    def test_finished_season_added_to_history(self, populated_league):
        """Test completed season is stored in history."""
        # Arrange: Complete a season
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act: Get season history
        response = client.get(f"/api/leagues/{league['id']}/seasons/history")
        
        # Assert
        assert response.status_code == 200
        history = response.json()
        assert len(history) == 1
        assert history[0]["season_number"] == 1
        assert "champion" in history[0]
        assert "mvp" in history[0]
        assert "final_standings" in history[0]
    
    def test_season_history_preserves_player_stats(self, populated_league):
        """Test archived season includes player statistics snapshot."""
        # Arrange: Complete season
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/seasons/history")
        
        # Assert
        history = response.json()
        season_1 = history[0]
        assert "player_stats" in season_1
        assert len(season_1["player_stats"]) > 0
        
        # Verify stat structure
        first_player_stat = season_1["player_stats"][0]
        assert "player_id" in first_player_stat
        assert "successful_hits" in first_player_stat
        assert "catches_made" in first_player_stat
    
    def test_season_history_preserves_team_rosters(self, populated_league):
        """Test archived season includes team roster snapshot."""
        # Arrange: Complete season
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/seasons/history")
        
        # Assert
        history = response.json()
        season_1 = history[0]
        assert "team_rosters" in season_1
        assert len(season_1["team_rosters"]) > 0
    
    def test_multiple_seasons_in_history(self, populated_league):
        """Test multiple completed seasons are tracked."""
        # Arrange: Complete two seasons
        league = populated_league["league"]
        
        # Season 1
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Season 2
        client.post(f"/api/leagues/{league['id']}/seasons/start")
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/seasons/history")
        
        # Assert
        history = response.json()
        assert len(history) == 2
        assert history[0]["season_number"] == 1
        assert history[1]["season_number"] == 2
    
    def test_archived_data_immutable(self, populated_league):
        """Test that archived season data doesn't change with new seasons."""
        # Arrange: Complete season 1
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Get season 1 data
        history1 = client.get(f"/api/leagues/{league['id']}/seasons/history").json()
        season_1_data = history1[0]
        
        # Complete season 2
        client.post(f"/api/leagues/{league['id']}/seasons/start")
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act: Get history again
        history2 = client.get(f"/api/leagues/{league['id']}/seasons/history").json()
        
        # Assert: Season 1 data unchanged
        assert history2[0] == season_1_data


class TestNewSeasonStart:
    """Integration tests for starting new seasons."""
    
    def test_start_new_season(self, populated_league):
        """Test POST /api/leagues/{league_id}/seasons/start begins new season."""
        # Arrange: Complete previous season
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act
        response = client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["season_number"] == 2
        assert "schedule" not in data  # New season has no schedule yet
    
    def test_start_season_resets_team_records(self, populated_league):
        """Test starting new season resets team win/loss records."""
        # Arrange: Complete season 1
        league = populated_league["league"]
        teams = populated_league["teams"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act: Start season 2
        client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Assert: Team records reset
        for team_id in [t["id"] for t in teams]:
            team_response = client.get(f"/api/teams/{team_id}")
            team = team_response.json()
            assert team["wins"] == 0
            assert team["losses"] == 0
    
    def test_start_season_ages_all_players(self, populated_league):
        """Test starting new season ages all players by 1 year."""
        # Arrange: Get initial player ages
        league = populated_league["league"]
        players = populated_league["players"]
        
        initial_ages = {}
        for team_players in players.values():
            for player in team_players:
                player_data = client.get(f"/api/players/{player['id']}").json()
                initial_ages[player["id"]] = player_data["age"]
        
        # Complete season
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act: Start new season (triggers age progression)
        client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Assert: All players aged by 1
        for team_players in players.values():
            for player in team_players:
                player_data = client.get(f"/api/players/{player['id']}").json()
                assert player_data["age"] == initial_ages[player["id"]] + 1
    
    def test_start_season_maintains_rosters(self, populated_league):
        """Test starting new season maintains team rosters."""
        # Arrange: Complete season 1
        league = populated_league["league"]
        teams = populated_league["teams"]
        
        # Get initial rosters
        initial_rosters = {}
        for team in teams:
            team_data = client.get(f"/api/teams/{team['id']}").json()
            initial_rosters[team["id"]] = set(team_data["roster"])
        
        # Complete season
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Act: Start new season
        client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Assert: Rosters unchanged
        for team in teams:
            team_data = client.get(f"/api/teams/{team['id']}").json()
            assert set(team_data["roster"]) == initial_rosters[team["id"]]
    
    def test_start_season_fails_if_not_finished(self, populated_league):
        """Test cannot start new season before finishing current one."""
        # Arrange: Season in progress
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        
        # Act: Try to start new season without finishing
        response = client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Assert
        assert response.status_code == 400
        assert "must finish current season" in response.json()["detail"].lower()


class TestAgeProgressionAtSeasonEnd:
    """Integration tests for age progression during season transitions."""
    
    def test_age_preview_before_confirmation(self, populated_league):
        """Test can preview age changes before applying."""
        # Arrange: Complete season
        league = populated_league["league"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Act: Get age preview
        response = client.get(f"/api/leagues/{league['id']}/seasons/age-preview")
        
        # Assert
        assert response.status_code == 200
        preview = response.json()
        assert len(preview) > 0
        
        first_player = preview[0]
        assert "player_id" in first_player
        assert "old_age" in first_player
        assert "new_age" in first_player
        assert first_player["new_age"] == first_player["old_age"] + 1
    
    def test_xp_accumulates_across_seasons(self, populated_league):
        """Test player XP and levels persist across seasons."""
        # Arrange: Complete season with games
        league = populated_league["league"]
        players = populated_league["players"]
        
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Get player XP after season 1
        first_player_id = players["team1"][0]["id"]
        player_s1 = client.get(f"/api/players/{first_player_id}").json()
        xp_s1 = player_s1["stats"]["experience_points"]
        
        # Complete season and start new one
        client.post(f"/api/leagues/{league['id']}/seasons/finish")
        client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Play more games in season 2
        client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
        schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
        for game in schedule:
            client.post(
                "/api/games",
                json={
                    "league_id": league["id"],
                    "team1_id": game["team1_id"],
                    "team2_id": game["team2_id"]
                }
            )
        
        # Act: Get player XP after season 2
        player_s2 = client.get(f"/api/players/{first_player_id}").json()
        xp_s2 = player_s2["stats"]["experience_points"]
        
        # Assert: XP accumulated
        assert xp_s2 > xp_s1


class TestSeasonEdgeCases:
    """Test edge cases for season management."""
    
    def test_finish_season_with_no_schedule(self, populated_league):
        """Test cannot finish season without schedule."""
        # Arrange
        league = populated_league["league"]
        
        # Act: Try to finish without schedule
        response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
        
        # Assert
        assert response.status_code == 400
    
    def test_season_history_empty_initially(self, populated_league):
        """Test season history is empty for new league."""
        # Arrange
        league = populated_league["league"]
        
        # Act
        response = client.get(f"/api/leagues/{league['id']}/seasons/history")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
    
    def test_season_number_increments(self, populated_league):
        """Test season number increments correctly."""
        # Arrange & Act: Complete 3 seasons
        league = populated_league["league"]
        
        for expected_season in [1, 2, 3]:
            # Create and complete schedule
            client.post(f"/api/leagues/{league['id']}/schedule", json={"rounds": 1})
            schedule = client.get(f"/api/leagues/{league['id']}/schedule").json()["schedule"]
            for game in schedule:
                client.post(
                    "/api/games",
                    json={
                        "league_id": league["id"],
                        "team1_id": game["team1_id"],
                        "team2_id": game["team2_id"]
                    }
                )
            
            finish_response = client.post(f"/api/leagues/{league['id']}/seasons/finish")
            assert finish_response.json()["season_number"] == expected_season
            
            if expected_season < 3:
                client.post(f"/api/leagues/{league['id']}/seasons/start")
        
        # Assert: History has 3 seasons
        history = client.get(f"/api/leagues/{league['id']}/seasons/history").json()
        assert len(history) == 3
