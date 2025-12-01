"""
Unit tests for XP calculation and skill progression system.

Tests the experience point system to ensure:
- XP awarded correctly based on performance
- Level-up triggers at correct thresholds
- Skill points awarded on level-up
- Exponential XP scaling

Test Coverage:
- T088: XP calculation and leveling logic
- FR-008: XP-based skill progression system

References:
- spec.md: US4 - Skill progression requirements
- skill-progression-plan.md: Detailed XP system design
"""

import pytest

from src.services.skill_progression import (
    calculate_game_xp,
    calculate_xp_for_level,
    award_xp_and_level_up,
    calculate_xp_progress,
    spend_skill_point,
    spend_multiple_skill_points,
)


class TestXPCalculation:
    """Test suite for XP award calculation."""
    
    def test_base_participation_xp(self):
        """Players get base 10 XP just for participating."""
        # Act
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=0,
            successful_hits=0,
            times_hit=1,
            is_winner=False
        )
        
        # Assert
        assert xp == 10
    
    def test_successful_hit_xp(self):
        """Successful hits award 20 XP each."""
        # Act
        xp = calculate_game_xp(
            throws_attempted=3,
            catches_made=0,
            successful_hits=2,
            times_hit=0,
            is_winner=False
        )
        
        # Assert: 10 base + (2 hits * 20) + (3 throws * 2) + 10 survival = 66
        assert xp == 66
    
    def test_catch_xp(self):
        """Catches award 15 XP each."""
        # Act
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=3,
            successful_hits=0,
            times_hit=0,
            is_winner=False
        )
        
        # Assert: 10 base + (3 catches * 15) + 10 survival = 65
        assert xp == 65
    
    def test_throw_attempt_xp(self):
        """Each throw attempt awards 2 XP."""
        # Act
        xp = calculate_game_xp(
            throws_attempted=10,
            catches_made=0,
            successful_hits=0,
            times_hit=0,
            is_winner=False
        )
        
        # Assert: 10 base + (10 throws * 2) + 10 survival = 40
        assert xp == 40
    
    def test_survival_bonus(self):
        """Not getting hit awards 10 XP survival bonus."""
        # Arrange
        hit_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=1,  # Got hit
            is_winner=False
        )
        survive_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=0,  # Survived
            is_winner=False
        )
        
        # Assert
        assert survive_xp == hit_xp + 10
    
    def test_win_bonus(self):
        """Winning team gets 25 XP bonus."""
        # Arrange
        loss_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=0,
            is_winner=False
        )
        win_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=0,
            is_winner=True
        )
        
        # Assert
        assert win_xp == loss_xp + 25
    
    def test_poor_performance_xp(self):
        """Poor performance still earns minimum XP."""
        # Act: Got hit, did nothing
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=0,
            successful_hits=0,
            times_hit=1,
            is_winner=False
        )
        
        # Assert: Only base 10 XP
        assert xp == 10
    
    def test_excellent_performance_xp(self):
        """Excellent performance earns high XP."""
        # Act: 5 hits, 3 catches, 10 throws, survived, won
        xp = calculate_game_xp(
            throws_attempted=10,
            catches_made=3,
            successful_hits=5,
            times_hit=0,
            is_winner=True
        )
        
        # Assert: 10 + 100 + 45 + 20 + 10 + 25 = 210
        assert xp == 210
    
    def test_xp_never_negative(self):
        """XP cannot be negative."""
        # Act: Even with 0 stats
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=0,
            successful_hits=0,
            times_hit=0,
            is_winner=False
        )
        
        # Assert
        assert xp >= 0
    
    def test_average_game_xp_range(self):
        """Average performance yields reasonable XP."""
        # Act: Typical performance
        xp = calculate_game_xp(
            throws_attempted=8,
            catches_made=2,
            successful_hits=2,
            times_hit=0,
            is_winner=False
        )
        
        # Assert: Should be in expected range
        # 10 base + 40 hits + 30 catches + 16 throws + 10 survival = 106
        assert 50 <= xp <= 150


class TestLevelingMechanics:
    """Test suite for level-up system."""
    
    def test_level_1_to_2_threshold(self):
        """Level 2 requires 100 XP."""
        # Act
        xp_needed = calculate_xp_for_level(2)
        
        # Assert
        assert xp_needed == 100
    
    def test_level_2_to_3_threshold(self):
        """Level 3 requires more XP than level 2."""
        # Act
        xp_for_level_2 = calculate_xp_for_level(2)  # 100
        xp_for_level_3 = calculate_xp_for_level(3)  # 100 + 282 = 382
        
        # Assert
        assert xp_for_level_3 > xp_for_level_2
        # Formula: sum(100 * i^1.5) for i in 1..2 = 100 + 282 = 382
        assert xp_for_level_3 == 382
    
    def test_exponential_scaling(self):
        """XP requirements grow exponentially (level^1.5 * 100)."""
        # Act
        level_2 = calculate_xp_for_level(2)   # 141
        level_5 = calculate_xp_for_level(5)   # 1118
        level_10 = calculate_xp_for_level(10)  # 3162
        
        # Assert: Exponential growth
        assert level_5 > level_2 * 5  # More than linear
        assert level_10 > level_5 * 2
    
    def test_level_up_awards_skill_point(self):
        """Leveling up awards 1 skill point."""
        # Arrange
        player_stats = {
            "experience_points": 0,
            "level": 1,
            "available_skill_points": 0
        }
        
        # Act: Award enough XP to level up
        player_stats = award_xp_and_level_up(player_stats, 100)
        
        # Assert
        assert player_stats["level"] == 2
        assert player_stats["available_skill_points"] == 1
    
    def test_multiple_levels_at_once(self):
        """Can gain multiple levels from one XP award."""
        # Arrange
        player_stats = {
            "experience_points": 0,
            "level": 1,
            "available_skill_points": 0
        }
        
        # Act: Award enough XP for multiple levels
        player_stats = award_xp_and_level_up(player_stats, 1000)
        
        # Assert: Should reach multiple levels
        assert player_stats["level"] > 2
        assert player_stats["available_skill_points"] > 1
    
    def test_partial_xp_progress(self):
        """Partial XP progress doesn't level up."""
        # Arrange
        player_stats = {
            "experience_points": 0,
            "level": 1,
            "available_skill_points": 0
        }
        
        # Act: Award partial XP (not enough to level)
        player_stats = award_xp_and_level_up(player_stats, 50)
        
        # Assert
        assert player_stats["level"] == 1
        assert player_stats["available_skill_points"] == 0
        assert player_stats["experience_points"] == 50
    
    def test_level_cap_at_100(self):
        """Level cannot exceed 100."""
        # Arrange
        player_stats = {
            "experience_points": 999999,
            "level": 100,
            "available_skill_points": 50
        }
        
        # Act: Award more XP
        player_stats = award_xp_and_level_up(player_stats, 100)
        
        # Assert
        assert player_stats["level"] == 100  # Still capped
    
    def test_xp_accumulates_across_games(self):
        """XP accumulates across multiple games."""
        # Arrange
        player_stats = {
            "experience_points": 0,
            "level": 1,
            "available_skill_points": 0
        }
        
        # Act: Award XP from multiple games
        player_stats = award_xp_and_level_up(player_stats, 50)
        player_stats = award_xp_and_level_up(player_stats, 30)
        player_stats = award_xp_and_level_up(player_stats, 25)
        
        # Assert: Total 105 XP, should reach level 2
        assert player_stats["experience_points"] == 105
        assert player_stats["level"] == 2
    
    def test_xp_progress_to_next_level(self):
        """Can calculate XP progress toward next level."""
        # Arrange
        player_stats = {
            "experience_points": 150,
            "level": 2,
            "available_skill_points": 1
        }
        
        # Act
        progress = calculate_xp_progress(player_stats)
        
        # Assert
        assert "xp_for_next_level" in progress
        assert "xp_progress" in progress
        assert "progress_percentage" in progress
        assert 0 <= progress["progress_percentage"] <= 100


class TestSkillPointSpending:
    """Test suite for spending skill points."""
    
    def test_spend_skill_point_success(self):
        """Can spend available skill point to increase skill."""
        # Arrange
        player = {
            "skills": {"catching": 10},
            "available_skill_points": 1
        }
        
        # Act
        result = spend_skill_point(player, "catching")
        
        # Assert
        assert result["success"] is True
        assert result["skills"]["catching"] == 11
        assert result["available_skill_points"] == 0
    
    def test_spend_without_points_fails(self):
        """Cannot spend if no points available."""
        # Arrange
        player = {
            "skills": {"catching": 10},
            "available_skill_points": 0
        }
        
        # Act
        result = spend_skill_point(player, "catching")
        
        # Assert
        assert result["success"] is False
        assert result["skills"]["catching"] == 10
    
    def test_spend_on_maxed_skill_fails(self):
        """Cannot increase skill beyond 100."""
        # Arrange
        player = {
            "skills": {"catching": 100},
            "available_skill_points": 1
        }
        
        # Act
        result = spend_skill_point(player, "catching")
        
        # Assert
        assert result["success"] is False
        assert result["skills"]["catching"] == 100
        assert result["available_skill_points"] == 1  # Point not spent
    
    def test_spend_multiple_points(self):
        """Can spend multiple skill points."""
        # Arrange
        player = {
            "skills": {"throwing": 20, "catching": 15},
            "available_skill_points": 3
        }
        
        # Act
        result = spend_multiple_skill_points(player, {
            "throwing": 2,
            "catching": 1
        })
        
        # Assert
        assert result["success"] is True
        assert result["skills"]["throwing"] == 22
        assert result["skills"]["catching"] == 16
        assert result["available_skill_points"] == 0
    
    def test_spend_more_than_available_fails(self):
        """Cannot spend more points than available."""
        # Arrange
        player = {
            "skills": {"throwing": 20},
            "available_skill_points": 1
        }
        
        # Act
        result = spend_multiple_skill_points(player, {
            "throwing": 2  # Try to spend 2 when only 1 available
        })
        
        # Assert
        assert result["success"] is False
        assert result["skills"]["throwing"] == 20  # Unchanged
    
    def test_invalid_skill_name_fails(self):
        """Spending on invalid skill name fails."""
        # Arrange
        player = {
            "skills": {"throwing": 20},
            "available_skill_points": 1
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid skill name"):
            spend_skill_point(player, "invalid_skill")


class TestXPEdgeCases:
    """Test edge cases for XP system."""
    
    def test_xp_with_zero_stats(self):
        """XP calculation with all zero stats."""
        # Act
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=0,
            successful_hits=0,
            times_hit=0,
            is_winner=False
        )
        
        # Assert: Base + survival = 20
        assert xp == 20
    
    def test_negative_stats_invalid(self):
        """Negative stats should be rejected."""
        # Act & Assert
        with pytest.raises(ValueError):
            calculate_game_xp(
                throws_attempted=-1,
                catches_made=0,
                successful_hits=0,
                times_hit=0,
                is_winner=False
            )
    
    def test_level_0_invalid(self):
        """Level 0 is invalid."""
        # Act & Assert
        with pytest.raises(ValueError):
            calculate_xp_for_level(0)
    
    def test_level_above_100_invalid(self):
        """Level above 100 is invalid."""
        # Act & Assert
        with pytest.raises(ValueError):
            calculate_xp_for_level(101)
