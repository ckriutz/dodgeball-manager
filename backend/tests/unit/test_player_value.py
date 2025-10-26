"""
Unit tests for player value calculation formula.

Tests the calculate_player_value function from services/utils.py to ensure
correct value calculation based on skills and age, including age discount factors.

Test Coverage:
- Base case: young player (age < 30) with standard skills
- Age discount: players age 30+ receive progressive discounts
- Edge cases: minimum value, maximum value, boundary ages
- Formula validation: (sum(skills) * 100) * age_factor

References:
- FR-004: Player value must be calculated as (sum of skills × $100) × age_factor
- data-model.md: Player.value calculation formula
- research.md: Player value formula decision
"""

import pytest
from src.services.utils import calculate_player_value


class TestPlayerValueCalculation:
    """Test suite for player value calculation formula."""
    
    def test_base_case_young_player(self):
        """Test value calculation for player under 30 (no age discount)."""
        # Arrange: Young player with 10 total skill points
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        age = 19
        
        # Act
        value = calculate_player_value(skills, age)
        
        # Assert: 10 skills * $100 * 1.0 (no discount) = $1000
        assert value == 1000
        assert isinstance(value, int), "Value must be an integer (no cents)"
    
    def test_age_30_boundary(self):
        """Test that age 30 is the threshold for discounts."""
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        
        # Age 29: No discount
        value_29 = calculate_player_value(skills, 29)
        assert value_29 == 1000
        
        # Age 30: First discount (5%)
        value_30 = calculate_player_value(skills, 30)
        assert value_30 == 950  # 1000 * 0.95
    
    def test_progressive_age_discount(self):
        """Test that age discount increases 5% per year after 30."""
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        
        # Age 31: 10% discount
        value_31 = calculate_player_value(skills, 31)
        assert value_31 == 900  # 1000 * 0.90
        
        # Age 32: 15% discount
        value_32 = calculate_player_value(skills, 32)
        assert value_32 == 850  # 1000 * 0.85
        
        # Age 35: 30% discount
        value_35 = calculate_player_value(skills, 35)
        assert value_35 == 750  # 1000 * 0.75 (capped at 50% min)
    
    def test_minimum_age_discount_cap(self):
        """Test that age discount never reduces value below 50% of base."""
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        
        # Age 40: Should cap at 50% discount
        value_40 = calculate_player_value(skills, 40)
        assert value_40 == 500  # 1000 * 0.50 (minimum cap)
        
        # Age 50: Should still be capped at 50%
        value_50 = calculate_player_value(skills, 50)
        assert value_50 == 500  # 1000 * 0.50 (minimum cap)
    
    def test_high_skill_player(self):
        """Test value calculation for player with higher skill concentration."""
        skills = {
            'catching': 5,
            'throwing': 3,
            'dodging': 2,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        age = 20
        
        # Act
        value = calculate_player_value(skills, age)
        
        # Assert: Same total skills (10) should yield same value
        assert value == 1000
    
    def test_minimum_value_zero_skills(self):
        """Test edge case of player with no skills."""
        skills = {
            'catching': 0,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        age = 18
        
        # Act
        value = calculate_player_value(skills, age)
        
        # Assert: 0 skills * $100 = $0
        assert value == 0
    
    def test_maximum_value_perfect_skills(self):
        """Test theoretical maximum with all skills at 100."""
        skills = {
            'catching': 100,
            'throwing': 100,
            'dodging': 100,
            'speed': 100,
            'iq': 100,
            'luck': 100
        }
        age = 18
        
        # Act
        value = calculate_player_value(skills, age)
        
        # Assert: 600 skills * $100 = $60,000
        assert value == 60000
    
    def test_value_is_always_integer(self):
        """Test that value is always rounded to integer (no cents)."""
        skills = {
            'catching': 1,
            'throwing': 1,
            'dodging': 1,
            'speed': 1,
            'iq': 1,
            'luck': 1
        }
        age = 31  # Will produce non-integer intermediate value
        
        # Act
        value = calculate_player_value(skills, age)
        
        # Assert: Must be integer type
        assert isinstance(value, int)
        assert value == int(600 * 0.90)  # 540
    
    def test_age_discount_formula_accuracy(self):
        """Test precise formula: age_factor = max(0.5, 1.0 - ((age - 30) * 0.05))."""
        skills = {
            'catching': 2,
            'throwing': 2,
            'dodging': 2,
            'speed': 2,
            'iq': 1,
            'luck': 1
        }
        
        test_cases = [
            (18, 1.0),    # Young: no discount
            (25, 1.0),    # Young: no discount
            (29, 1.0),    # Boundary: no discount
            (30, 0.95),   # First discount: 5%
            (31, 0.90),   # 10% discount
            (35, 0.75),   # 25% discount
            (40, 0.50),   # Capped at 50%
            (50, 0.50),   # Still capped at 50%
        ]
        
        for age, expected_factor in test_cases:
            value = calculate_player_value(skills, age)
            expected_value = int(1000 * expected_factor)
            assert value == expected_value, f"Age {age}: expected {expected_value}, got {value}"
    
    def test_different_skill_distributions_same_sum(self):
        """Test that different skill distributions with same sum yield same value."""
        age = 20
        
        # Different distributions, all sum to 10
        distributions = [
            {'catching': 2, 'throwing': 2, 'dodging': 2, 'speed': 2, 'iq': 1, 'luck': 1},
            {'catching': 5, 'throwing': 5, 'dodging': 0, 'speed': 0, 'iq': 0, 'luck': 0},
            {'catching': 0, 'throwing': 0, 'dodging': 0, 'speed': 0, 'iq': 5, 'luck': 5},
            {'catching': 1, 'throwing': 2, 'dodging': 3, 'speed': 2, 'iq': 1, 'luck': 1},
        ]
        
        values = [calculate_player_value(skills, age) for skills in distributions]
        
        # All should equal $1000
        assert all(v == 1000 for v in values), "Same skill sum should yield same value"
    
    def test_value_scales_linearly_with_skills(self):
        """Test that value scales linearly with total skill points."""
        age = 20
        
        test_cases = [
            (5, 500),    # 5 skills * $100
            (10, 1000),  # 10 skills * $100
            (15, 1500),  # 15 skills * $100
            (20, 2000),  # 20 skills * $100
        ]
        
        for total_skills, expected_value in test_cases:
            skills = {
                'catching': total_skills,
                'throwing': 0,
                'dodging': 0,
                'speed': 0,
                'iq': 0,
                'luck': 0
            }
            value = calculate_player_value(skills, age)
            assert value == expected_value


class TestPlayerValueEdgeCases:
    """Test edge cases and boundary conditions for player value calculation."""
    
    def test_negative_age_theoretical(self):
        """Test behavior with negative age (should still calculate, though invalid input)."""
        skills = {'catching': 2, 'throwing': 2, 'dodging': 2, 'speed': 2, 'iq': 1, 'luck': 1}
        
        # Function doesn't validate age, just calculates
        value = calculate_player_value(skills, -5)
        assert value == 1000  # Treated as young player
    
    def test_extremely_old_player(self):
        """Test value calculation for extremely old player."""
        skills = {'catching': 2, 'throwing': 2, 'dodging': 2, 'speed': 2, 'iq': 1, 'luck': 1}
        
        # Age 100: Should be capped at 50% discount
        value = calculate_player_value(skills, 100)
        assert value == 500
    
    def test_single_skill_high_value(self):
        """Test player with all points in one skill."""
        skills = {
            'catching': 100,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
        age = 22
        
        value = calculate_player_value(skills, age)
        assert value == 10000  # 100 * $100
    
    def test_partial_skill_point_rounding(self):
        """Test that integer conversion handles rounding correctly."""
        # With age discount, ensure consistent rounding
        skills = {'catching': 1, 'throwing': 1, 'dodging': 1, 'speed': 1, 'iq': 1, 'luck': 1}
        
        # Age 33: 15% discount on 600 = 510
        value = calculate_player_value(skills, 33)
        assert value == 510
        assert isinstance(value, int)
