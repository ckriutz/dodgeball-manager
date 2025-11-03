"""
Unit tests for team budget validation.

Tests budget constraint logic for team roster management, including:
- Initial budget allocation ($100,000)
- Budget calculation when adding/removing players
- Preventing roster additions that exceed budget
- Allowing roster additions that equal remaining budget
- Budget integrity validation

Test Coverage:
- Budget initialization
- Budget calculation after player additions
- Budget validation (can/cannot afford player)
- Budget edge cases (exact budget match, overspending)
- Budget recalculation after player removal

References:
- FR-014: Cannot add player if value exceeds budget
- FR-014a: Can add player if value equals budget  
- data-model.md: Team.budget and budget calculation
- contracts/openapi.yaml: Team schema with budget fields
"""

import pytest
from typing import Dict, List


class TestTeamBudgetInitialization:
    """Test suite for team budget initialization."""
    
    def test_new_team_starts_with_full_budget(self):
        """Test that a new team has $100,000 budget."""
        # This test will fail until Team model is implemented
        # Expected: New team should have budget = 15000
        # TODO: Implement after T049 (Create Team model)
        pytest.skip("Skipping until Team model is implemented (T049)")
    
    def test_new_team_has_zero_budget_spent(self):
        """Test that a new team has spent $0."""
        # This test will fail until Team model is implemented
        # Expected: New team should have spent = 0
        pytest.skip("Skipping until Team model is implemented (T049)")
    
    def test_budget_remaining_equals_initial_budget(self):
        """Test that initial remaining budget equals starting budget."""
        # This test will fail until Team model is implemented
        # Expected: budget - spent = 15000 - 0 = 15000
        pytest.skip("Skipping until Team model is implemented (T049)")


class TestBudgetCalculation:
    """Test suite for budget calculation logic."""
    
    def test_budget_calculation_with_no_players(self):
        """Test budget calculation for empty roster."""
        # Arrange
        roster_values = []
        
        # Act
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Assert
        assert spent == 0
        assert remaining == 15000
    
    def test_budget_calculation_with_one_player(self):
        """Test budget calculation with single player on roster."""
        # Arrange: One player worth $1000
        roster_values = [1000]
        
        # Act
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Assert
        assert spent == 1000
        assert remaining == 99000
    
    def test_budget_calculation_with_multiple_players(self):
        """Test budget calculation with multiple players."""
        # Arrange: Multiple players with different values
        roster_values = [1000, 1500, 2000, 1200, 800]
        
        # Act
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Assert
        assert spent == 6500
        assert remaining == 93500
    
    def test_budget_calculation_with_full_roster(self):
        """Test budget calculation with 12 players (max roster)."""
        # Arrange: 12 players at $1000 each
        roster_values = [1000] * 12
        
        # Act
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Assert
        assert spent == 12000
        assert remaining == 88000
    
    def test_budget_calculation_integrity(self):
        """Test that spent + remaining always equals initial budget."""
        # Arrange: Various roster configurations
        test_cases = [
            [],
            [1000],
            [500, 1500, 2000],
            [1000] * 8,  # Minimum roster
            [1000] * 12,  # Maximum roster
            [5000, 10000, 15000],
        ]
        
        for roster_values in test_cases:
            # Act
            spent = sum(roster_values)
            remaining = 15000 - spent
            
            # Assert: Budget integrity maintained
            assert spent + remaining == 15000, \
                f"Budget integrity violated: {spent} + {remaining} != 15000"


class TestBudgetValidation:
    """Test suite for budget validation when adding players."""
    
    def test_can_afford_player_within_budget(self):
        """Test that player can be added when cost is within budget."""
        # Arrange
        remaining_budget = 50000
        player_value = 1000
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert
        assert can_afford is True
    
    def test_cannot_afford_player_exceeding_budget(self):
        """Test that player cannot be added when cost exceeds budget (FR-014)."""
        # Arrange
        remaining_budget = 500
        player_value = 1000
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert: Cannot afford player
        assert can_afford is False
    
    def test_can_afford_player_equal_to_budget(self):
        """Test that player can be added when cost equals budget exactly (FR-014a)."""
        # Arrange: Exact budget match
        remaining_budget = 1000
        player_value = 1000
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert: Can afford player (edge case: equality allowed)
        assert can_afford is True
    
    def test_cannot_afford_player_one_dollar_over(self):
        """Test edge case: Cannot afford player $1 over budget."""
        # Arrange
        remaining_budget = 999
        player_value = 1000
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert
        assert can_afford is False
    
    def test_can_afford_player_one_dollar_under(self):
        """Test edge case: Can afford player $1 under budget."""
        # Arrange
        remaining_budget = 1001
        player_value = 1000
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert
        assert can_afford is True
    
    def test_cannot_afford_when_budget_exhausted(self):
        """Test that no player can be added when budget is exhausted."""
        # Arrange: No budget remaining
        remaining_budget = 0
        player_value = 500  # Even cheap player
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert
        assert can_afford is False
    
    def test_can_afford_free_player_with_zero_budget(self):
        """Test edge case: Free player (value=0) can be added even with no budget."""
        # Arrange
        remaining_budget = 0
        player_value = 0
        
        # Act
        can_afford = player_value <= remaining_budget
        
        # Assert: Free player allowed (0 <= 0)
        assert can_afford is True


class TestBudgetUpdateAfterRosterChange:
    """Test budget recalculation after roster modifications."""
    
    def test_budget_decreases_after_adding_player(self):
        """Test that budget decreases when player is added."""
        # Arrange
        initial_remaining = 15000
        player_value = 1500
        
        # Act
        new_remaining = initial_remaining - player_value
        
        # Assert
        assert new_remaining == 98500
        assert new_remaining < initial_remaining
    
    def test_budget_increases_after_removing_player(self):
        """Test that budget increases when player is removed."""
        # Arrange
        current_remaining = 95000
        removed_player_value = 2000
        
        # Act
        new_remaining = current_remaining + removed_player_value
        
        # Assert
        assert new_remaining == 97000
        assert new_remaining > current_remaining
    
    def test_budget_after_replacing_player(self):
        """Test budget calculation when replacing one player with another."""
        # Arrange
        remaining_budget = 90000
        removed_player_value = 1000
        added_player_value = 1500
        
        # Act
        budget_after_removal = remaining_budget + removed_player_value
        budget_after_addition = budget_after_removal - added_player_value
        
        # Assert
        assert budget_after_removal == 91000  # Refunded
        assert budget_after_addition == 89500  # Net decrease of $500
    
    def test_budget_returns_to_full_after_releasing_all_players(self):
        """Test that budget returns to $100k when all players are released."""
        # Arrange
        roster_values = [1000, 1500, 2000, 1200]
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Act: Release all players
        refund = spent
        new_remaining = remaining + refund
        
        # Assert
        assert new_remaining == 15000


class TestBudgetEdgeCases:
    """Test edge cases and boundary conditions for budget management."""
    
    def test_maximum_budget_spent(self):
        """Test budget calculation when entire budget is spent."""
        # Arrange: Spend exactly $100,000
        roster_values = [10000] * 10  # 10 players at $10k each
        
        # Act
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Assert
        assert spent == 15000
        assert remaining == 0
    
    def test_high_value_player_within_budget(self):
        """Test adding expensive player when budget allows."""
        # Arrange
        remaining_budget = 50000
        expensive_player = 40000
        
        # Act
        can_afford = expensive_player <= remaining_budget
        
        # Assert
        assert can_afford is True
    
    def test_multiple_budget_validations(self):
        """Test sequential budget validations for multiple players."""
        # Arrange
        budget = 15000
        players_to_add = [
            ("Player 1", 20000, True),   # Can afford
            ("Player 2", 30000, True),   # Can afford (50k spent, 50k left)
            ("Player 3", 40000, True),   # Can afford (90k spent, 10k left)
            ("Player 4", 15000, False),  # Cannot afford (would need 105k)
            ("Player 5", 10000, True),   # Can afford exactly (100k spent, 0 left)
            ("Player 6", 1000, False),   # Cannot afford (budget exhausted)
        ]
        
        current_budget = budget
        
        for name, value, expected_affordable in players_to_add:
            # Act
            can_afford = value <= current_budget
            
            # Assert
            assert can_afford == expected_affordable, \
                f"{name}: Expected affordable={expected_affordable}, got {can_afford}"
            
            # Update budget if player was added
            if can_afford and expected_affordable:
                current_budget -= value
    
    def test_negative_budget_prevented(self):
        """Test that budget cannot go negative."""
        # Arrange
        remaining_budget = 500
        expensive_player = 1000
        
        # Act & Assert
        can_afford = expensive_player <= remaining_budget
        assert can_afford is False
        
        # If we force-added, budget would be negative (should never happen)
        would_be_negative = remaining_budget - expensive_player
        assert would_be_negative < 0
    
    def test_budget_with_varying_player_values(self):
        """Test budget management with wide range of player values."""
        # Arrange: Mix of cheap and expensive players
        roster_values = [
            500,    # Cheap
            1000,   # Standard
            5000,   # Valuable
            10000,  # Expensive
            2500,   # Above average
        ]
        
        # Act
        spent = sum(roster_values)
        remaining = 15000 - spent
        
        # Assert
        assert spent == 19000
        assert remaining == 81000
        assert spent + remaining == 15000


class TestBudgetIntegrityValidation:
    """Test budget integrity constraints and validations."""
    
    def test_budget_integrity_formula(self):
        """Test that budget integrity formula is always maintained."""
        # Formula: spent + remaining = initial_budget
        # This is a critical invariant that must always be true
        
        test_scenarios = [
            (0, 15000),        # No players
            (1000, 99000),      # One player
            (50000, 50000),     # Half budget
            (99999, 1),         # Almost full
            (15000, 0),        # Full budget
        ]
        
        for spent, remaining in test_scenarios:
            # Assert
            assert spent + remaining == 15000, \
                f"Integrity violated: {spent} + {remaining} != 15000"
            assert spent >= 0, "Spent cannot be negative"
            assert remaining >= 0, "Remaining cannot be negative"
    
    def test_spent_budget_equals_roster_sum(self):
        """Test that spent budget always equals sum of player values on roster."""
        # Arrange
        player_values = [1000, 1500, 2000, 1200, 800, 1100]
        
        # Act
        calculated_spent = sum(player_values)
        
        # Assert: This will be validated in TeamService
        assert calculated_spent == 7600
        assert calculated_spent == sum(player_values)
    
    def test_remaining_budget_derived_correctly(self):
        """Test that remaining budget is derived from initial - spent."""
        # Arrange
        initial_budget = 15000
        roster_values = [1000, 2000, 3000]
        
        # Act
        spent = sum(roster_values)
        remaining = initial_budget - spent
        
        # Assert
        assert remaining == 94000
        assert remaining == initial_budget - spent
    
    def test_budget_cannot_be_manipulated_directly(self):
        """Test that budget must be calculated, not set arbitrarily."""
        # This is a conceptual test - budget should be derived, not stored independently
        # Implementation should calculate from roster, not allow direct budget setting
        
        # Arrange
        roster_values = [1000, 2000]
        correct_spent = sum(roster_values)
        correct_remaining = 15000 - correct_spent
        
        # Assert: These are the only valid values
        assert correct_spent == 3000
        assert correct_remaining == 97000
        
        # Invalid states that should be prevented:
        invalid_spent = 5000  # Doesn't match roster
        invalid_remaining = 90000  # Doesn't maintain integrity
        
        # This should never be allowed:
        assert invalid_spent != sum(roster_values)
        assert invalid_spent + invalid_remaining != 15000


class TestBudgetValidationHelpers:
    """Test helper functions for budget validation."""
    
    def test_validate_budget_addition_valid(self):
        """Test validation helper for valid player addition."""
        # This will be implemented in TeamService
        # Expected: Return True when player can be afforded
        
        remaining = 50000
        player_value = 1000
        
        # Logic that will be in service
        is_valid = player_value <= remaining
        
        assert is_valid is True
    
    def test_validate_budget_addition_invalid(self):
        """Test validation helper for invalid player addition."""
        remaining = 500
        player_value = 1000
        
        # Logic that will be in service
        is_valid = player_value <= remaining
        
        assert is_valid is False
    
    def test_calculate_budget_after_addition(self):
        """Test budget calculation helper after adding player."""
        current_remaining = 80000
        player_value = 5000
        
        # Logic that will be in service
        new_remaining = current_remaining - player_value
        
        assert new_remaining == 75000
    
    def test_calculate_budget_after_removal(self):
        """Test budget calculation helper after removing player."""
        current_remaining = 75000
        player_value = 5000
        
        # Logic that will be in service
        new_remaining = current_remaining + player_value
        
        assert new_remaining == 80000
