"""
Unit tests for league standings calculation.

Tests the standings ranking algorithm to ensure:
- Teams ranked by wins (descending)
- Ties broken by losses (ascending)
- Correct win percentage calculation
- Games played count

Test Coverage:
- T086: Standings calculation and ranking
- FR-025: Track league-wide statistics

References:
- spec.md: US4 - Standings and awards requirements
- data-model.md: League standings structure
"""

import pytest
from typing import List, Dict


class TestStandingsCalculation:
    """Test suite for standings calculation and ranking."""
    
    def test_standings_simple_ranking(self):
        """Test basic standings with clear winner."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 3, "losses": 0},
            {"team_id": "team-2", "team_name": "Beta", "wins": 2, "losses": 1},
            {"team_id": "team-3", "team_name": "Gamma", "wins": 1, "losses": 2},
            {"team_id": "team-4", "team_name": "Delta", "wins": 0, "losses": 3},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert: Teams ranked by wins descending
        assert standings[0]["team_id"] == "team-1"
        assert standings[0]["rank"] == 1
        assert standings[1]["team_id"] == "team-2"
        assert standings[1]["rank"] == 2
        assert standings[2]["team_id"] == "team-3"
        assert standings[2]["rank"] == 3
        assert standings[3]["team_id"] == "team-4"
        assert standings[3]["rank"] == 4
    
    def test_standings_tie_broken_by_losses(self):
        """Test that ties in wins are broken by losses (fewer is better)."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 2, "losses": 2},
            {"team_id": "team-2", "team_name": "Beta", "wins": 2, "losses": 1},
            {"team_id": "team-3", "team_name": "Gamma", "wins": 2, "losses": 3},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert: Same wins, ranked by losses ascending
        assert standings[0]["team_id"] == "team-2"  # 2-1
        assert standings[0]["rank"] == 1
        assert standings[1]["team_id"] == "team-1"  # 2-2
        assert standings[1]["rank"] == 2
        assert standings[2]["team_id"] == "team-3"  # 2-3
        assert standings[2]["rank"] == 3
    
    def test_standings_win_percentage_calculation(self):
        """Test win percentage is calculated correctly."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 3, "losses": 1},
            {"team_id": "team-2", "team_name": "Beta", "wins": 2, "losses": 2},
            {"team_id": "team-3", "team_name": "Gamma", "wins": 1, "losses": 0},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[0]["win_percentage"] == 0.75   # 3/4
        assert standings[1]["win_percentage"] == 1.0    # 1/1
        assert standings[2]["win_percentage"] == 0.5    # 2/4
    
    def test_standings_games_played(self):
        """Test games played count is correct."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 5, "losses": 3},
            {"team_id": "team-2", "team_name": "Beta", "wins": 2, "losses": 1},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[0]["games_played"] == 8  # 5 + 3
        assert standings[1]["games_played"] == 3  # 2 + 1
    
    def test_standings_with_no_games(self):
        """Test standings for teams that haven't played."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 0, "losses": 0},
            {"team_id": "team-2", "team_name": "Beta", "wins": 0, "losses": 0},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[0]["win_percentage"] == 0.0
        assert standings[0]["games_played"] == 0
        assert standings[1]["win_percentage"] == 0.0
        assert standings[1]["games_played"] == 0
    
    def test_standings_undefeated_team(self):
        """Test undefeated team ranks first."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 5, "losses": 0},
            {"team_id": "team-2", "team_name": "Beta", "wins": 4, "losses": 1},
            {"team_id": "team-3", "team_name": "Gamma", "wins": 3, "losses": 2},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[0]["team_id"] == "team-1"
        assert standings[0]["rank"] == 1
        assert standings[0]["win_percentage"] == 1.0
    
    def test_standings_winless_team(self):
        """Test winless team ranks last."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 2, "losses": 1},
            {"team_id": "team-2", "team_name": "Beta", "wins": 1, "losses": 2},
            {"team_id": "team-3", "team_name": "Gamma", "wins": 0, "losses": 5},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[2]["team_id"] == "team-3"
        assert standings[2]["rank"] == 3
        assert standings[2]["win_percentage"] == 0.0
    
    def test_standings_perfect_tie(self):
        """Test standings when teams have identical records."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 2, "losses": 2},
            {"team_id": "team-2", "team_name": "Beta", "wins": 2, "losses": 2},
            {"team_id": "team-3", "team_name": "Gamma", "wins": 2, "losses": 2},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert: All tied, maintain consistent ordering
        assert len(standings) == 3
        # All should have same stats
        for entry in standings:
            assert entry["wins"] == 2
            assert entry["losses"] == 2
            assert entry["win_percentage"] == 0.5
    
    def test_standings_preserves_team_names(self):
        """Test that team names are preserved in standings."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Thunder Dodgers", "wins": 3, "losses": 1},
            {"team_id": "team-2", "team_name": "Lightning Bolts", "wins": 2, "losses": 2},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[0]["team_name"] == "Thunder Dodgers"
        assert standings[1]["team_name"] == "Lightning Bolts"
    
    def test_standings_with_single_team(self):
        """Test standings with only one team."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Solo", "wins": 0, "losses": 0}
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert len(standings) == 1
        assert standings[0]["rank"] == 1
    
    def test_standings_ranks_are_sequential(self):
        """Test that rank numbers are sequential from 1."""
        # Arrange
        teams = [
            {"team_id": f"team-{i}", "team_name": f"Team {i}", 
             "wins": 10 - i, "losses": i}
            for i in range(1, 6)
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        ranks = [entry["rank"] for entry in standings]
        assert ranks == [1, 2, 3, 4, 5]
    
    def test_standings_after_one_game(self):
        """Test standings after exactly one game played."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Winner", "wins": 1, "losses": 0},
            {"team_id": "team-2", "team_name": "Loser", "wins": 0, "losses": 1},
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings[0]["team_id"] == "team-1"
        assert standings[0]["win_percentage"] == 1.0
        assert standings[1]["team_id"] == "team-2"
        assert standings[1]["win_percentage"] == 0.0
    
    def test_standings_many_teams(self):
        """Test standings with 10 teams (realistic league size)."""
        # Arrange
        teams = [
            {"team_id": f"team-{i}", "team_name": f"Team {i}",
             "wins": 10 - i, "losses": i}
            for i in range(1, 11)
        ]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert len(standings) == 10
        assert standings[0]["wins"] == 9   # Best record
        assert standings[9]["wins"] == 0   # Worst record
        
        # Verify ranking is correct
        for i in range(1, 10):
            assert standings[i]["wins"] < standings[i-1]["wins"]


class TestStandingsEdgeCases:
    """Test edge cases and boundary conditions for standings."""
    
    def test_standings_with_empty_list(self):
        """Test standings calculation with no teams."""
        # Arrange
        teams = []
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert
        assert standings == []
    
    def test_standings_negative_wins_invalid(self):
        """Test that negative wins are handled (validation)."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Invalid", "wins": -1, "losses": 0}
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_standings(teams)
    
    def test_standings_negative_losses_invalid(self):
        """Test that negative losses are handled (validation)."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Invalid", "wins": 0, "losses": -1}
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_standings(teams)
    
    def test_standings_float_wins_rounded(self):
        """Test that non-integer wins are handled (should not happen in real system)."""
        # This is a defensive test - wins should always be integers
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Floaty", "wins": 2.5, "losses": 1}
        ]
        
        # Act & Assert: Should either round or reject
        # Implementation decision: reject non-integer values
        with pytest.raises(ValueError, match="must be integers"):
            calculate_standings(teams)
    
    def test_standings_missing_team_name(self):
        """Test handling of missing team name."""
        # Arrange
        teams = [
            {"team_id": "team-1", "wins": 1, "losses": 0}  # Missing team_name
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="team_name is required"):
            calculate_standings(teams)
    
    def test_standings_preserves_input_data(self):
        """Test that standings calculation doesn't mutate input."""
        # Arrange
        teams = [
            {"team_id": "team-1", "team_name": "Alpha", "wins": 2, "losses": 1},
            {"team_id": "team-2", "team_name": "Beta", "wins": 1, "losses": 2},
        ]
        original_teams = [team.copy() for team in teams]
        
        # Act
        standings = calculate_standings(teams)
        
        # Assert: Original data unchanged
        assert teams == original_teams


# Helper function that would be implemented in standings_service.py

def calculate_standings(teams: List[Dict]) -> List[Dict]:
    """
    Calculate standings from team records.
    
    Ranks teams by:
    1. Wins (descending)
    2. Losses (ascending) - for tiebreaker
    
    Adds computed fields:
    - rank: Position in standings (1-based)
    - games_played: wins + losses
    - win_percentage: wins / games_played (0.0 if no games)
    
    Args:
        teams: List of dicts with team_id, team_name, wins, losses
        
    Returns:
        List of standings entries with rank and computed fields
        
    Raises:
        ValueError: If wins/losses are negative or non-integer
        ValueError: If required fields are missing
    """
    # This will be implemented in backend/src/services/standings_service.py
    raise NotImplementedError("To be implemented in T098")
