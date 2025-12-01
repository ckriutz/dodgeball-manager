"""
Unit tests for MVP and awards calculation.

Tests the awards system to ensure:
- MVP selection based on performance stats
- Statistical leader identification
- Tiebreaker logic
- Multiple award categories

Test Coverage:
- T087: MVP/awards calculation
- FR-027: Track MVP awards and statistical leaders

References:
- spec.md: US4 - Awards and MVP requirements
- data-model.md: Player statistics tracking
"""

import pytest
from typing import List, Dict, Optional

from src.services.awards_service import (
    calculate_mvp,
    calculate_mvp_per_game,
    get_stat_leader,
    get_accuracy_leader,
    get_all_stat_leaders,
    calculate_season_awards
)


class TestMVPCalculation:
    """Test suite for MVP (Most Valuable Player) calculation."""
    
    def test_mvp_most_eliminations(self):
        """Test MVP awarded to player with most eliminations."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 15, "catches_made": 5, "games_played": 10},
            {"player_id": "p2", "name": "Bob", "successful_hits": 12, "catches_made": 8, "games_played": 10},
            {"player_id": "p3", "name": "Charlie", "successful_hits": 10, "catches_made": 6, "games_played": 10},
        ]
        
        # Act
        mvp = calculate_mvp(players)
        
        # Assert
        assert mvp["player_id"] == "p1"
        assert mvp["name"] == "Alice"
        assert mvp["reason"] == "Most eliminations (15)"
    
    def test_mvp_combined_stats(self):
        """Test MVP uses combined performance score."""
        # Arrange: Player with best overall stats
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 10, "catches_made": 10, "games_played": 10},
            {"player_id": "p2", "name": "Bob", "successful_hits": 15, "catches_made": 2, "games_played": 10},
            {"player_id": "p3", "name": "Charlie", "successful_hits": 5, "catches_made": 15, "games_played": 10},
        ]
        
        # Act: MVP formula: (hits * 2) + (catches * 1.5)
        mvp = calculate_mvp(players)
        
        # Assert: Alice has best combined score (10*2 + 10*1.5 = 35)
        assert mvp["player_id"] == "p1"
        assert mvp["mvp_score"] > 30
    
    def test_mvp_tie_broken_by_catches(self):
        """Test MVP tie broken by catches when hits are equal."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 10, "catches_made": 8, "games_played": 10},
            {"player_id": "p2", "name": "Bob", "successful_hits": 10, "catches_made": 5, "games_played": 10},
        ]
        
        # Act
        mvp = calculate_mvp(players)
        
        # Assert
        assert mvp["player_id"] == "p1"  # More catches
    
    def test_mvp_requires_minimum_games(self):
        """Test MVP requires minimum games played (e.g., 5)."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 50, "catches_made": 30, "games_played": 2},
            {"player_id": "p2", "name": "Bob", "successful_hits": 10, "catches_made": 8, "games_played": 10},
        ]
        
        # Act: MVP requires at least 5 games
        mvp = calculate_mvp(players, min_games=5)
        
        # Assert: Alice ineligible due to games played
        assert mvp["player_id"] == "p2"
    
    def test_mvp_with_single_player(self):
        """Test MVP calculation with only one eligible player."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 5, "catches_made": 3, "games_played": 10}
        ]
        
        # Act
        mvp = calculate_mvp(players)
        
        # Assert
        assert mvp["player_id"] == "p1"
    
    def test_mvp_no_eligible_players(self):
        """Test MVP when no players meet minimum games requirement."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 10, "catches_made": 5, "games_played": 2},
            {"player_id": "p2", "name": "Bob", "successful_hits": 8, "catches_made": 4, "games_played": 3},
        ]
        
        # Act
        mvp = calculate_mvp(players, min_games=5)
        
        # Assert
        assert mvp is None
    
    def test_mvp_per_game_stats_normalized(self):
        """Test MVP considers per-game averages for fairness."""
        # Arrange: Player with fewer games but better average
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 20, "catches_made": 10, "games_played": 5},
            {"player_id": "p2", "name": "Bob", "successful_hits": 25, "catches_made": 12, "games_played": 10},
        ]
        
        # Act: Calculate using per-game averages
        mvp = calculate_mvp_per_game(players, min_games=5)
        
        # Assert: Alice has better per-game stats (4.0 hits/game vs 2.5)
        assert mvp["player_id"] == "p1"
        assert mvp["hits_per_game"] == 4.0  # 20 hits / 5 games


class TestStatisticalLeaders:
    """Test suite for statistical leader identification."""
    
    def test_leader_most_hits(self):
        """Test leader for most successful hits."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 25},
            {"player_id": "p2", "name": "Bob", "successful_hits": 30},
            {"player_id": "p3", "name": "Charlie", "successful_hits": 20},
        ]
        
        # Act
        leader = get_stat_leader(players, "successful_hits")
        
        # Assert
        assert leader["player_id"] == "p2"
        assert leader["successful_hits"] == 30
    
    def test_leader_most_catches(self):
        """Test leader for most catches."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "catches_made": 15},
            {"player_id": "p2", "name": "Bob", "catches_made": 20},
            {"player_id": "p3", "name": "Charlie", "catches_made": 12},
        ]
        
        # Act
        leader = get_stat_leader(players, "catches_made")
        
        # Assert
        assert leader["player_id"] == "p2"
        assert leader["catches_made"] == 20
    
    def test_leader_best_accuracy(self):
        """Test leader for best throw accuracy (hits / throws)."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 20, "throws_attempted": 40},  # 50%
            {"player_id": "p2", "name": "Bob", "successful_hits": 15, "throws_attempted": 20},    # 75%
            {"player_id": "p3", "name": "Charlie", "successful_hits": 10, "throws_attempted": 30}, # 33%
        ]
        
        # Act
        leader = get_accuracy_leader(players, min_throws=10)
        
        # Assert
        assert leader["player_id"] == "p2"
        assert leader["accuracy"] == 0.75
    
    def test_leader_fewest_eliminations(self):
        """Test leader for defensive stat (fewest times eliminated)."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "times_hit": 5, "games_played": 10},
            {"player_id": "p2", "name": "Bob", "times_hit": 3, "games_played": 10},
            {"player_id": "p3", "name": "Charlie", "times_hit": 8, "games_played": 10},
        ]
        
        # Act
        leader = get_stat_leader(players, "times_hit", lowest=True)
        
        # Assert
        assert leader["player_id"] == "p2"
        assert leader["times_hit"] == 3
    
    def test_multiple_statistical_leaders(self):
        """Test getting all statistical leaders at once."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 30, "catches_made": 15, "throws_attempted": 50},
            {"player_id": "p2", "name": "Bob", "successful_hits": 25, "catches_made": 25, "throws_attempted": 45},
            {"player_id": "p3", "name": "Charlie", "successful_hits": 20, "catches_made": 20, "throws_attempted": 40},
        ]
        
        # Act
        leaders = get_all_stat_leaders(players)
        
        # Assert
        assert leaders["most_hits"]["player_id"] == "p1"
        assert leaders["most_catches"]["player_id"] == "p2"
        assert "accuracy_leader" in leaders


class TestAwardsSystem:
    """Test suite for complete awards system."""
    
    def test_season_awards_structure(self):
        """Test complete season awards contain all categories."""
        # Arrange
        players = [
            {"player_id": f"p{i}", "name": f"Player {i}", 
             "successful_hits": 20-i, "catches_made": 15-i, 
             "throws_attempted": 40, "times_hit": i+5, "games_played": 10}
            for i in range(10)
        ]
        
        # Act
        awards = calculate_season_awards(players)
        
        # Assert
        assert "mvp" in awards
        assert "most_hits" in awards
        assert "most_catches" in awards
        assert "accuracy_leader" in awards
        assert "best_defense" in awards
    
    def test_awards_different_winners(self):
        """Test that different awards can go to different players."""
        # Arrange: Specialized players
        players = [
            {"player_id": "p1", "name": "Sniper", 
             "successful_hits": 30, "catches_made": 5, "throws_attempted": 35, 
             "times_hit": 10, "games_played": 10},
            {"player_id": "p2", "name": "Wall", 
             "successful_hits": 10, "catches_made": 30, "throws_attempted": 20, 
             "times_hit": 2, "games_played": 10},
            {"player_id": "p3", "name": "Balanced", 
             "successful_hits": 20, "catches_made": 20, "throws_attempted": 40, 
             "times_hit": 6, "games_played": 10},
        ]
        
        # Act
        awards = calculate_season_awards(players)
        
        # Assert: Different winners for different categories
        assert awards["most_hits"]["player_id"] == "p1"
        assert awards["most_catches"]["player_id"] == "p2"
        assert awards["best_defense"]["player_id"] == "p2"
    
    def test_awards_empty_player_list(self):
        """Test awards calculation with no players."""
        # Arrange
        players = []
        
        # Act
        awards = calculate_season_awards(players)
        
        # Assert: All awards should be None
        assert awards["mvp"] is None
        assert awards["most_hits"] is None
        assert awards["most_catches"] is None
    
    def test_awards_preserve_player_info(self):
        """Test that awards include player names and relevant stats."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 25, 
             "catches_made": 15, "throws_attempted": 50, "times_hit": 5, "games_played": 10},
            {"player_id": "p2", "name": "Bob", "successful_hits": 20, 
             "catches_made": 20, "throws_attempted": 45, "times_hit": 7, "games_played": 10},
        ]
        
        # Act
        awards = calculate_season_awards(players)
        
        # Assert
        assert awards["mvp"]["name"] in ["Alice", "Bob"]
        assert "successful_hits" in awards["most_hits"]
        assert "catches_made" in awards["most_catches"]


class TestAwardsEdgeCases:
    """Test edge cases for awards calculations."""
    
    def test_mvp_perfect_tie(self):
        """Test MVP when multiple players have identical stats."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 20, "catches_made": 15, "games_played": 10},
            {"player_id": "p2", "name": "Bob", "successful_hits": 20, "catches_made": 15, "games_played": 10},
        ]
        
        # Act
        mvp = calculate_mvp(players)
        
        # Assert: Should return one (consistent tiebreaker)
        assert mvp is not None
        assert mvp["player_id"] in ["p1", "p2"]
    
    def test_accuracy_leader_minimum_attempts(self):
        """Test accuracy leader requires minimum throw attempts."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Lucky", "successful_hits": 3, "throws_attempted": 3},  # 100%
            {"player_id": "p2", "name": "Consistent", "successful_hits": 20, "throws_attempted": 25},  # 80%
        ]
        
        # Act: Require at least 10 attempts
        leader = get_accuracy_leader(players, min_throws=10)
        
        # Assert: Lucky ineligible due to low attempts
        assert leader["player_id"] == "p2"
    
    def test_awards_with_zero_stats(self):
        """Test awards when all players have zero stats."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "successful_hits": 0, "catches_made": 0, "throws_attempted": 0, "times_hit": 0, "games_played": 0},
            {"player_id": "p2", "name": "Bob", "successful_hits": 0, "catches_made": 0, "throws_attempted": 0, "times_hit": 0, "games_played": 0},
        ]
        
        # Act
        awards = calculate_season_awards(players)
        
        # Assert: Should handle gracefully
        assert awards is not None

