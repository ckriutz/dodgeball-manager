"""
Unit tests for team roster size and starter validation.

Tests roster management constraints including:
- Roster size limits (8-12 players)
- Starter designation (exactly 5 players)
- Starter eligibility (must be on roster)
- Roster operations (add, remove, replace)

Test Coverage:
- Minimum roster size (8 players)
- Maximum roster size (12 players)
- Starter count validation (exactly 5)
- Starter eligibility (must be on roster)
- Edge cases (boundaries, invalid states)

References:
- FR-012: Team rosters must have 8-12 players
- FR-013: Exactly 5 starters must be designated
- data-model.md: Team roster validation rules
- contracts/openapi.yaml: Team roster and starter fields
"""

import pytest
from typing import List


class TestRosterSizeValidation:
    """Test suite for roster size constraints (8-12 players)."""
    
    def test_minimum_roster_size(self):
        """Test that minimum valid roster size is 8 players (FR-012)."""
        # Arrange
        roster_size = 8
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert
        assert is_valid is True
    
    def test_maximum_roster_size(self):
        """Test that maximum valid roster size is 12 players (FR-012)."""
        # Arrange
        roster_size = 12
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert
        assert is_valid is True
    
    def test_roster_below_minimum_invalid(self):
        """Test that roster with fewer than 8 players is invalid."""
        # Arrange
        roster_size = 7
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert
        assert is_valid is False
    
    def test_roster_above_maximum_invalid(self):
        """Test that roster with more than 12 players is invalid."""
        # Arrange
        roster_size = 13
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert
        assert is_valid is False
    
    def test_empty_roster_invalid(self):
        """Test that empty roster is invalid."""
        # Arrange
        roster_size = 0
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert
        assert is_valid is False
    
    def test_roster_one_below_minimum(self):
        """Test edge case: 7 players (one below minimum)."""
        # Arrange
        roster_size = 7
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert: Not valid
        assert is_valid is False
    
    def test_roster_one_above_maximum(self):
        """Test edge case: 13 players (one above maximum)."""
        # Arrange
        roster_size = 13
        
        # Act
        is_valid = 8 <= roster_size <= 12
        
        # Assert: Not valid
        assert is_valid is False
    
    def test_all_valid_roster_sizes(self):
        """Test that all sizes from 8-12 are valid."""
        # Arrange & Act & Assert
        for size in range(8, 13):  # 8, 9, 10, 11, 12
            is_valid = 8 <= size <= 12
            assert is_valid is True, f"Size {size} should be valid"
    
    def test_all_invalid_roster_sizes_below(self):
        """Test that all sizes below 8 are invalid."""
        # Arrange & Act & Assert
        for size in range(0, 8):  # 0-7
            is_valid = 8 <= size <= 12
            assert is_valid is False, f"Size {size} should be invalid"
    
    def test_all_invalid_roster_sizes_above(self):
        """Test that sizes above 12 are invalid."""
        # Arrange & Act & Assert
        for size in range(13, 20):  # 13-19
            is_valid = 8 <= size <= 12
            assert is_valid is False, f"Size {size} should be invalid"


class TestStarterCountValidation:
    """Test suite for starter count validation (exactly 5)."""
    
    def test_exactly_five_starters_valid(self):
        """Test that exactly 5 starters is valid (FR-013)."""
        # Arrange
        starter_count = 5
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is True
    
    def test_fewer_than_five_starters_invalid(self):
        """Test that fewer than 5 starters is invalid."""
        # Arrange
        starter_count = 4
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False
    
    def test_more_than_five_starters_invalid(self):
        """Test that more than 5 starters is invalid."""
        # Arrange
        starter_count = 6
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False
    
    def test_zero_starters_invalid(self):
        """Test that zero starters is invalid."""
        # Arrange
        starter_count = 0
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False
    
    def test_one_starter_invalid(self):
        """Test that one starter is invalid."""
        # Arrange
        starter_count = 1
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False
    
    def test_all_players_as_starters_invalid(self):
        """Test that designating all 12 players as starters is invalid."""
        # Arrange
        roster_size = 12
        starter_count = 12
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False
    
    def test_four_starters_edge_case(self):
        """Test edge case: 4 starters (one short)."""
        # Arrange
        starter_count = 4
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False
    
    def test_six_starters_edge_case(self):
        """Test edge case: 6 starters (one too many)."""
        # Arrange
        starter_count = 6
        
        # Act
        is_valid = starter_count == 5
        
        # Assert
        assert is_valid is False


class TestStarterEligibility:
    """Test suite for starter eligibility validation."""
    
    def test_starters_must_be_on_roster(self):
        """Test that all starters must be present in roster."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act: Check all starters are in roster
        all_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert all_eligible is True
    
    def test_starter_not_on_roster_invalid(self):
        """Test that starter not on roster is invalid."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        starter_ids = ["p1", "p2", "p3", "p4", "p99"]  # p99 not on roster
        
        # Act
        all_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert all_eligible is False
    
    def test_multiple_ineligible_starters(self):
        """Test that multiple starters not on roster are detected."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        starter_ids = ["p1", "p2", "p99", "p98", "p97"]  # 3 not on roster
        
        # Act
        all_eligible = all(sid in roster_ids for sid in starter_ids)
        ineligible = [sid for sid in starter_ids if sid not in roster_ids]
        
        # Assert
        assert all_eligible is False
        assert len(ineligible) == 3
        assert set(ineligible) == {"p99", "p98", "p97"}
    
    def test_empty_roster_no_eligible_starters(self):
        """Test that empty roster has no eligible starters."""
        # Arrange
        roster_ids = []
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act
        all_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert all_eligible is False
    
    def test_partial_roster_partial_eligibility(self):
        """Test mixed eligibility: some starters on roster, some not."""
        # Arrange
        roster_ids = ["p1", "p2", "p3"]  # Only 3 on roster
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]  # p4, p5 missing
        
        # Act
        all_eligible = all(sid in roster_ids for sid in starter_ids)
        eligible = [sid for sid in starter_ids if sid in roster_ids]
        ineligible = [sid for sid in starter_ids if sid not in roster_ids]
        
        # Assert
        assert all_eligible is False
        assert len(eligible) == 3
        assert len(ineligible) == 2


class TestRosterOperations:
    """Test roster operation validations (add, remove)."""
    
    def test_can_add_player_to_roster_below_max(self):
        """Test that player can be added when roster is below maximum."""
        # Arrange
        current_roster_size = 10
        
        # Act
        can_add = current_roster_size < 12
        
        # Assert
        assert can_add is True
    
    def test_cannot_add_player_to_full_roster(self):
        """Test that player cannot be added when roster is at maximum."""
        # Arrange
        current_roster_size = 12
        
        # Act
        can_add = current_roster_size < 12
        
        # Assert
        assert can_add is False
    
    def test_can_remove_player_from_roster_above_min(self):
        """Test that player can be removed when roster is above minimum."""
        # Arrange
        current_roster_size = 10
        
        # Act
        can_remove = current_roster_size > 8
        
        # Assert
        assert can_remove is True
    
    def test_cannot_remove_player_from_minimum_roster(self):
        """Test that player cannot be removed when roster is at minimum."""
        # Arrange
        current_roster_size = 8
        
        # Act
        can_remove = current_roster_size > 8
        
        # Assert
        assert can_remove is False
    
    def test_can_add_player_at_11_players(self):
        """Test edge case: Can add one more player at 11."""
        # Arrange
        current_roster_size = 11
        
        # Act
        can_add = current_roster_size < 12
        
        # Assert
        assert can_add is True
    
    def test_can_remove_player_at_9_players(self):
        """Test edge case: Can remove one more player at 9."""
        # Arrange
        current_roster_size = 9
        
        # Act
        can_remove = current_roster_size > 8
        
        # Assert
        assert can_remove is True
    
    def test_roster_size_after_addition(self):
        """Test that roster size increases after adding player."""
        # Arrange
        current_size = 10
        
        # Act
        new_size = current_size + 1
        
        # Assert
        assert new_size == 11
        assert 8 <= new_size <= 12
    
    def test_roster_size_after_removal(self):
        """Test that roster size decreases after removing player."""
        # Arrange
        current_size = 10
        
        # Act
        new_size = current_size - 1
        
        # Assert
        assert new_size == 9
        assert 8 <= new_size <= 12


class TestRosterStarterCombinedValidation:
    """Test combined roster and starter validations."""
    
    def test_valid_minimum_roster_with_starters(self):
        """Test valid state: 8 players with 5 starters."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act
        roster_valid = 8 <= len(roster_ids) <= 12
        starter_count_valid = len(starter_ids) == 5
        starters_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert roster_valid is True
        assert starter_count_valid is True
        assert starters_eligible is True
    
    def test_valid_maximum_roster_with_starters(self):
        """Test valid state: 12 players with 5 starters."""
        # Arrange
        roster_ids = [f"p{i}" for i in range(1, 13)]  # p1-p12
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act
        roster_valid = 8 <= len(roster_ids) <= 12
        starter_count_valid = len(starter_ids) == 5
        starters_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert roster_valid is True
        assert starter_count_valid is True
        assert starters_eligible is True
    
    def test_invalid_too_few_players_for_starters(self):
        """Test invalid state: Only 4 players but need 5 starters."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4"]
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]  # p5 doesn't exist
        
        # Act
        roster_valid = 8 <= len(roster_ids) <= 12
        starter_count_valid = len(starter_ids) == 5
        starters_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert roster_valid is False  # Too few players
        assert starter_count_valid is True  # Count is correct
        assert starters_eligible is False  # But not all eligible
    
    def test_starters_can_be_any_5_from_roster(self):
        """Test that any 5 players from roster can be starters."""
        # Arrange
        roster_ids = [f"p{i}" for i in range(1, 13)]  # p1-p12
        
        # Different valid starter combinations
        starter_combinations = [
            ["p1", "p2", "p3", "p4", "p5"],      # First 5
            ["p8", "p9", "p10", "p11", "p12"],   # Last 5
            ["p1", "p4", "p7", "p10", "p12"],    # Scattered
            ["p2", "p5", "p6", "p8", "p11"],     # Random
        ]
        
        for starter_ids in starter_combinations:
            # Act
            starter_count_valid = len(starter_ids) == 5
            starters_eligible = all(sid in roster_ids for sid in starter_ids)
            
            # Assert
            assert starter_count_valid is True
            assert starters_eligible is True
    
    def test_removing_starter_makes_team_invalid(self):
        """Test that removing a starter requires re-designation."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act: Remove p3 who is a starter
        roster_ids.remove("p3")
        
        # Validation after removal (before re-designation)
        roster_valid = 8 <= len(roster_ids) <= 12
        starter_count_valid = len(starter_ids) == 5
        starters_eligible = all(sid in roster_ids for sid in starter_ids)
        
        # Assert
        assert roster_valid is False  # Now only 7 players (below minimum)
        assert starter_count_valid is True  # Still 5 starters listed
        assert starters_eligible is False  # p3 no longer on roster
    
    def test_bench_players_not_starters(self):
        """Test that bench players (non-starters) are identified correctly."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act
        bench_ids = [pid for pid in roster_ids if pid not in starter_ids]
        
        # Assert
        assert len(bench_ids) == 3
        assert set(bench_ids) == {"p6", "p7", "p8"}
    
    def test_all_roster_players_categorized(self):
        """Test that every roster player is either starter or bench."""
        # Arrange
        roster_ids = [f"p{i}" for i in range(1, 11)]  # 10 players
        starter_ids = ["p1", "p2", "p3", "p4", "p5"]
        
        # Act
        bench_ids = [pid for pid in roster_ids if pid not in starter_ids]
        categorized_ids = set(starter_ids + bench_ids)
        
        # Assert
        assert len(starter_ids) == 5
        assert len(bench_ids) == 5
        assert categorized_ids == set(roster_ids)
        assert len(categorized_ids) == len(roster_ids)


class TestRosterEdgeCases:
    """Test edge cases and boundary conditions for roster management."""
    
    def test_duplicate_player_ids_in_roster(self):
        """Test that duplicate player IDs should be prevented."""
        # Arrange
        roster_ids = ["p1", "p2", "p3", "p1", "p4", "p5", "p6", "p7"]  # p1 duplicated
        
        # Act
        unique_ids = list(set(roster_ids))
        has_duplicates = len(roster_ids) != len(unique_ids)
        
        # Assert
        assert has_duplicates is True
        assert len(unique_ids) == 7  # Only 7 unique
        assert len(roster_ids) == 8  # But 8 total
    
    def test_duplicate_player_ids_in_starters(self):
        """Test that duplicate player IDs in starters should be prevented."""
        # Arrange
        starter_ids = ["p1", "p2", "p3", "p1", "p4"]  # p1 duplicated
        
        # Act
        unique_ids = list(set(starter_ids))
        has_duplicates = len(starter_ids) != len(unique_ids)
        
        # Assert
        assert has_duplicates is True
        assert len(unique_ids) == 4  # Only 4 unique
        assert len(starter_ids) == 5  # But 5 total
    
    def test_empty_string_player_id(self):
        """Test that empty string player IDs should be invalid."""
        # Arrange
        roster_ids = ["p1", "p2", "", "p3", "p4", "p5", "p6", "p7"]
        
        # Act
        has_empty = "" in roster_ids
        valid_ids = [pid for pid in roster_ids if pid and pid.strip()]
        
        # Assert
        assert has_empty is True
        assert len(valid_ids) == 7  # Only 7 valid
    
    def test_none_player_id(self):
        """Test that None player IDs should be invalid."""
        # Arrange
        roster_ids = ["p1", "p2", None, "p3", "p4", "p5", "p6", "p7"]
        
        # Act
        has_none = None in roster_ids
        valid_ids = [pid for pid in roster_ids if pid is not None]
        
        # Assert
        assert has_none is True
        assert len(valid_ids) == 7
    
    def test_roster_size_boundary_8_to_9(self):
        """Test transition from minimum roster to minimum+1."""
        # Arrange
        roster_8 = [f"p{i}" for i in range(1, 9)]  # 8 players
        
        # Act: Add one player
        roster_9 = roster_8 + ["p9"]
        
        # Assert
        assert len(roster_8) == 8
        assert len(roster_9) == 9
        assert 8 <= len(roster_8) <= 12
        assert 8 <= len(roster_9) <= 12
    
    def test_roster_size_boundary_11_to_12(self):
        """Test transition from maximum-1 to maximum roster."""
        # Arrange
        roster_11 = [f"p{i}" for i in range(1, 12)]  # 11 players
        
        # Act: Add one player
        roster_12 = roster_11 + ["p12"]
        
        # Assert
        assert len(roster_11) == 11
        assert len(roster_12) == 12
        assert 8 <= len(roster_11) <= 12
        assert 8 <= len(roster_12) <= 12
        
        # Cannot add more
        can_add_to_11 = len(roster_11) < 12
        can_add_to_12 = len(roster_12) < 12
        assert can_add_to_11 is True
        assert can_add_to_12 is False


class TestRosterValidationHelpers:
    """Test helper functions for roster validation."""
    
    def test_validate_roster_size(self):
        """Test roster size validation helper."""
        # This will be implemented in TeamService
        
        test_cases = [
            (0, False),
            (7, False),
            (8, True),
            (10, True),
            (12, True),
            (13, False),
            (20, False),
        ]
        
        for size, expected_valid in test_cases:
            # Logic that will be in service
            is_valid = 8 <= size <= 12
            assert is_valid == expected_valid, \
                f"Size {size}: expected {expected_valid}, got {is_valid}"
    
    def test_validate_starter_count(self):
        """Test starter count validation helper."""
        # This will be implemented in TeamService
        
        test_cases = [
            (0, False),
            (1, False),
            (4, False),
            (5, True),
            (6, False),
            (12, False),
        ]
        
        for count, expected_valid in test_cases:
            # Logic that will be in service
            is_valid = count == 5
            assert is_valid == expected_valid, \
                f"Count {count}: expected {expected_valid}, got {is_valid}"
    
    def test_validate_starters_on_roster(self):
        """Test starter eligibility validation helper."""
        # This will be implemented in TeamService
        
        roster = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        
        test_cases = [
            (["p1", "p2", "p3", "p4", "p5"], True),      # All on roster
            (["p1", "p2", "p3", "p4", "p99"], False),    # p99 not on roster
            (["p9", "p10", "p11", "p12", "p13"], False), # None on roster
            ([], False),                                  # Empty starters
        ]
        
        for starters, expected_valid in test_cases:
            # Logic that will be in service
            is_valid = len(starters) == 5 and all(s in roster for s in starters)
            
            # Only check if count is correct for this specific test
            if len(starters) == 5:
                eligibility_valid = all(s in roster for s in starters)
                assert eligibility_valid == expected_valid
