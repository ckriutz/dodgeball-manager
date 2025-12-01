"""
Unit tests for age progression and stat penalties.

Tests the age system to ensure:
- Players age correctly at season end
- Stat penalties applied after age 30
- Skills reduced to new maximum when cap lowered
- Age updates are bulk operations

Test Coverage:
- T089: Age progression and stat penalties
- FR-007: Age-related skill reduction
- FR-010: Age increases at season completion

References:
- spec.md: US4 - Age progression requirements  
- data-model.md: Player age and skill mechanics
"""

import pytest
from typing import Dict

from src.services.age_service import (
    apply_age_progression,
    apply_bulk_age_progression,
    calculate_age_penalty,
    calculate_stat_penalties,
    get_max_skill_levels,
    preview_age_progression,
)


class TestAgeProgression:
    """Test suite for player age progression."""
    
    def test_age_increases_by_one_year(self):
        """Players age by 1 year at season end."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Alice",
            "age": 20,
            "skills": {"catching": 50, "throwing": 50, "dodging": 50, "speed": 50, "iq": 50, "luck": 50}
        }
        
        # Act
        aged_player = apply_age_progression(player)
        
        # Assert
        assert aged_player["age"] == 21
    
    def test_age_progression_multiple_years(self):
        """Can age player multiple times (for testing)."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Alice",
            "age": 18,
            "skills": {"catching": 50, "throwing": 50, "dodging": 50, "speed": 50, "iq": 50, "luck": 50}
        }
        
        # Act: Age multiple times
        for _ in range(5):
            player = apply_age_progression(player)
        
        # Assert
        assert player["age"] == 23
    
    def test_young_player_no_penalties(self):
        """Players under 30 have no age-related penalties."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Youth",
            "age": 25,
            "skills": {"catching": 80, "throwing": 75, "dodging": 70, "speed": 85, "iq": 60, "luck": 55}
        }
        
        # Act
        aged_player = apply_age_progression(player)
        
        # Assert: Age increases but skills unchanged
        assert aged_player["age"] == 26
        assert aged_player["skills"] == player["skills"]
    
    def test_age_29_to_30_no_penalty_yet(self):
        """Age 30 is the threshold - no penalty at 30."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Turning30",
            "age": 29,
            "skills": {"catching": 80, "throwing": 75, "dodging": 70, "speed": 85, "iq": 60, "luck": 55}
        }
        
        # Act
        aged_player = apply_age_progression(player)
        
        # Assert: Now 30, no penalty yet (penalties start AFTER 30)
        assert aged_player["age"] == 30
        assert aged_player["skills"] == player["skills"]
    
    def test_age_30_to_31_first_penalty(self):
        """First penalty applies when turning 31."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Aging",
            "age": 30,
            "skills": {"catching": 80, "throwing": 75, "dodging": 70, "speed": 85, "iq": 60, "luck": 55}
        }
        
        # Act
        aged_player = apply_age_progression(player)
        
        # Assert: Now 31, penalty applied
        assert aged_player["age"] == 31
        # Skills should be reduced (specific formula to be defined)
        assert aged_player["skills"]["speed"] < player["skills"]["speed"]
    
    def test_bulk_age_progression(self):
        """Can age multiple players at once."""
        # Arrange
        players = [
            {"player_id": "p1", "age": 20, "skills": {"catching": 50, "throwing": 50, "dodging": 50, "speed": 50, "iq": 50, "luck": 50}},
            {"player_id": "p2", "age": 25, "skills": {"catching": 60, "throwing": 60, "dodging": 60, "speed": 60, "iq": 60, "luck": 60}},
            {"player_id": "p3", "age": 30, "skills": {"catching": 70, "throwing": 70, "dodging": 70, "speed": 70, "iq": 70, "luck": 70}},
        ]
        
        # Act
        aged_players = apply_bulk_age_progression(players)
        
        # Assert
        assert aged_players[0]["age"] == 21
        assert aged_players[1]["age"] == 26
        assert aged_players[2]["age"] == 31


class TestStatPenalties:
    """Test suite for age-related stat penalties."""
    
    def test_physical_stats_decline_faster(self):
        """Physical stats (speed, dodging) decline faster than mental stats."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Veteran",
            "age": 30,
            "skills": {
                "catching": 80,
                "throwing": 80,
                "dodging": 80,
                "speed": 80,
                "iq": 80,
                "luck": 80
            }
        }
        
        # Act: Age to 35
        for _ in range(5):
            player = apply_age_progression(player)
        
        # Assert: Physical stats declined more than mental
        assert player["age"] == 35
        assert player["skills"]["speed"] < player["skills"]["iq"]
        assert player["skills"]["dodging"] < player["skills"]["iq"]
    
    def test_iq_unaffected_by_age(self):
        """IQ does not decline with age (wisdom increases)."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Wise",
            "age": 30,
            "skills": {
                "catching": 70,
                "throwing": 70,
                "dodging": 70,
                "speed": 70,
                "iq": 70,
                "luck": 70
            }
        }
        original_iq = player["skills"]["iq"]
        
        # Act: Age to 40
        for _ in range(10):
            player = apply_age_progression(player)
        
        # Assert: IQ unchanged or increased
        assert player["age"] == 40
        assert player["skills"]["iq"] >= original_iq
    
    def test_skills_cannot_go_below_zero(self):
        """Skills have a floor of 0 (cannot be negative)."""
        # Arrange: Old player with low skills
        player = {
            "player_id": "p1",
            "name": "Ancient",
            "age": 30,
            "skills": {
                "catching": 10,
                "throwing": 10,
                "dodging": 10,
                "speed": 10,
                "iq": 50,
                "luck": 10
            }
        }
        
        # Act: Age many years
        for _ in range(20):
            player = apply_age_progression(player)
        
        # Assert: Skills at 0 minimum
        assert player["age"] == 50
        assert all(skill >= 0 for skill in player["skills"].values())
    
    def test_skill_reduction_formula(self):
        """Test specific penalty formula for each age bracket."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "TestSubject",
            "age": 30,
            "skills": {
                "catching": 100,
                "throwing": 100,
                "dodging": 100,
                "speed": 100,
                "iq": 100,
                "luck": 100
            }
        }
        
        # Test ages 31-35: Specific penalties
        penalties = []
        for year in range(31, 36):
            player = apply_age_progression(player)
            penalty = calculate_age_penalty(player["age"])
            penalties.append((player["age"], penalty))
        
        # Assert: Penalties increase with age
        assert all(penalties[i][1] < penalties[i+1][1] for i in range(len(penalties)-1))
    
    def test_maximum_skill_reduction(self):
        """Skills reduced when max skill level decreases."""
        # Arrange: Player at high skill level
        player = {
            "player_id": "p1",
            "name": "Skilled",
            "age": 30,
            "skills": {
                "catching": 95,
                "throwing": 90,
                "dodging": 92,
                "speed": 88,
                "iq": 85,
                "luck": 80
            }
        }
        
        # Act: Age until significant penalty
        for _ in range(10):
            player = apply_age_progression(player)
        
        # Assert: Skills capped at new maximum
        max_skills = get_max_skill_levels(player["age"])
        for skill_name, skill_value in player["skills"].items():
            assert skill_value <= max_skills[skill_name]


class TestAgePreview:
    """Test suite for age progression preview."""
    
    def test_preview_age_changes(self):
        """Can preview age changes before applying."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Alice", "age": 20},
            {"player_id": "p2", "name": "Bob", "age": 30},
            {"player_id": "p3", "name": "Charlie", "age": 35},
        ]
        
        # Act
        preview = preview_age_progression(players)
        
        # Assert: Preview shows changes without modifying originals
        assert preview[0]["old_age"] == 20
        assert preview[0]["new_age"] == 21
        assert preview[1]["old_age"] == 30
        assert preview[1]["new_age"] == 31
        assert preview[2]["old_age"] == 35
        assert preview[2]["new_age"] == 36
        
        # Original players unchanged
        assert players[0]["age"] == 20
        assert players[1]["age"] == 30
        assert players[2]["age"] == 35
    
    def test_preview_includes_stat_changes(self):
        """Preview shows which stats will be affected."""
        # Arrange
        players = [
            {"player_id": "p1", "name": "Aging", "age": 30, 
             "skills": {"catching": 80, "throwing": 80, "dodging": 80, "speed": 80, "iq": 80, "luck": 80}}
        ]
        
        # Act
        preview = preview_age_progression(players)
        
        # Assert: Shows stat changes
        assert "skill_changes" in preview[0]
        if preview[0]["new_age"] > 30:
            # Should show which skills will decrease
            assert len(preview[0]["skill_changes"]) > 0


class TestAgeEdgeCases:
    """Test edge cases for age progression."""
    
    def test_age_cannot_exceed_100(self):
        """Players cannot age beyond 100."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Ancient",
            "age": 99,
            "skills": {"catching": 10, "throwing": 10, "dodging": 10, "speed": 10, "iq": 50, "luck": 10}
        }
        
        # Act
        aged_player = apply_age_progression(player)
        
        # Assert
        assert aged_player["age"] == 100
        
        # Try to age again
        aged_player = apply_age_progression(aged_player)
        assert aged_player["age"] == 100  # Still capped
    
    def test_age_minimum_18(self):
        """Players cannot be younger than 18 (new players start at 18-20)."""
        # This is more of a validation test for player generation
        # Age progression doesn't go backwards
        pass
    
    def test_age_with_zero_skills(self):
        """Can age player even with zero skills."""
        # Arrange
        player = {
            "player_id": "p1",
            "name": "Retired",
            "age": 40,
            "skills": {"catching": 0, "throwing": 0, "dodging": 0, "speed": 0, "iq": 0, "luck": 0}
        }
        
        # Act
        aged_player = apply_age_progression(player)
        
        # Assert: Ages normally
        assert aged_player["age"] == 41
        assert aged_player["skills"] == player["skills"]  # Already at minimum


class TestAgePenaltyFormula:
    """Test suite for specific age penalty calculations."""
    
    def test_penalty_age_31(self):
        """Age 31: First year of decline."""
        penalty = calculate_age_penalty(31)
        assert penalty > 0
    
    def test_penalty_age_35(self):
        """Age 35: Moderate decline."""
        penalty = calculate_age_penalty(35)
        assert penalty > calculate_age_penalty(31)
    
    def test_penalty_age_40(self):
        """Age 40: Significant decline."""
        penalty = calculate_age_penalty(40)
        assert penalty > calculate_age_penalty(35)
    
    def test_penalty_different_per_stat(self):
        """Different stats have different penalty rates."""
        penalties = calculate_stat_penalties(35)
        
        # Physical stats decline faster
        assert penalties["speed"] > penalties["iq"]
        assert penalties["dodging"] > penalties["iq"]
    
    def test_max_skill_levels_by_age(self):
        """Maximum skill levels decrease with age."""
        max_20 = get_max_skill_levels(20)
        max_35 = get_max_skill_levels(35)
        max_50 = get_max_skill_levels(50)
        
        # Physical stats have lower maximums as age increases
        assert max_35["speed"] < max_20["speed"]
        assert max_50["speed"] < max_35["speed"]
        
        # IQ maximum stays the same or increases
        assert max_35["iq"] >= max_20["iq"]

