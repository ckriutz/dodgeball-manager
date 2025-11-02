"""
Unit tests for game mechanics - throw outcome calculation.

This module tests the core game simulation mechanics including:
- Hit probability calculations based on player stats
- Catch probability calculations
- Luck variance impact on outcomes
- Edge cases with extreme stat values

References:
- research.md: Game Simulation Algorithm
- FR-027: Throwing skill affects hit probability
- FR-028: Catching skill affects catch probability
- FR-030: IQ affects targeting and evasion
- FR-031: Luck adds variance to outcomes
"""

import pytest
from typing import Dict


def calculate_hit_probability(
    thrower_skills: Dict[str, int],
    target_skills: Dict[str, int],
    luck_modifier: float = 0.0
) -> float:
    """
    Calculate the probability of a throw hitting the target.
    
    Formula (from research.md):
    - Base: thrower.throwing / 100
    - Modified by: (thrower.IQ - target.IQ) * 0.01
    - Modified by: -target.dodging * 0.01
    - Apply luck variance: ±10% based on both players' luck
    
    Args:
        thrower_skills: Dict with 'throwing', 'iq', 'luck' keys
        target_skills: Dict with 'dodging', 'iq', 'luck' keys
        luck_modifier: Pre-calculated luck modifier (for testing)
        
    Returns:
        Hit probability between 0.0 and 1.0
    """
    # Base probability from throwing skill
    base_prob = thrower_skills['throwing'] / 100.0
    
    # IQ differential modifier
    iq_modifier = (thrower_skills['iq'] - target_skills['iq']) * 0.01
    
    # Dodging penalty
    dodge_modifier = -target_skills['dodging'] * 0.01
    
    # Calculate base probability
    prob = base_prob + iq_modifier + dodge_modifier
    
    # Apply luck modifier
    prob += luck_modifier
    
    # Clamp to valid probability range
    return max(0.0, min(1.0, prob))


def calculate_catch_probability(
    target_skills: Dict[str, int],
    luck_modifier: float = 0.0
) -> float:
    """
    Calculate the probability of catching a missed throw.
    
    Formula (from research.md):
    - Base: target.catching / 100
    - Apply luck variance
    
    Args:
        target_skills: Dict with 'catching', 'luck' keys
        luck_modifier: Pre-calculated luck modifier (for testing)
        
    Returns:
        Catch probability between 0.0 and 1.0
    """
    base_prob = target_skills['catching'] / 100.0
    
    # Apply luck modifier
    prob = base_prob + luck_modifier
    
    return max(0.0, min(1.0, prob))


class TestHitProbabilityCalculation:
    """Test cases for hit probability calculations."""
    
    def test_base_hit_probability_high_throwing(self):
        """Test that high throwing skill gives high hit probability."""
        thrower = {'throwing': 80, 'iq': 50, 'luck': 50}
        target = {'dodging': 20, 'iq': 50, 'luck': 50}
        
        # With no luck modifier for deterministic testing
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.8 (throwing) - 0.2 (dodging) = 0.6
        assert prob == pytest.approx(0.6, abs=0.01)
    
    def test_base_hit_probability_low_throwing(self):
        """Test that low throwing skill gives low hit probability."""
        thrower = {'throwing': 20, 'iq': 50, 'luck': 50}
        target = {'dodging': 60, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.2 (throwing) - 0.6 (dodging) = -0.4 -> clamped to 0.0
        assert prob == 0.0
    
    def test_iq_advantage_increases_hit_probability(self):
        """Test that higher IQ increases hit probability."""
        thrower = {'throwing': 50, 'iq': 80, 'luck': 50}
        target = {'dodging': 30, 'iq': 40, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.5 (throwing) + 0.4 (IQ diff) - 0.3 (dodging) = 0.6
        assert prob == pytest.approx(0.6, abs=0.01)
    
    def test_iq_disadvantage_decreases_hit_probability(self):
        """Test that lower IQ decreases hit probability."""
        thrower = {'throwing': 50, 'iq': 30, 'luck': 50}
        target = {'dodging': 20, 'iq': 70, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.5 (throwing) - 0.4 (IQ diff) - 0.2 (dodging) = -0.1 -> clamped to 0.0
        assert prob == 0.0
    
    def test_high_dodging_reduces_hit_probability(self):
        """Test that high dodging skill reduces hit probability."""
        thrower = {'throwing': 70, 'iq': 50, 'luck': 50}
        target = {'dodging': 80, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.7 (throwing) - 0.8 (dodging) = -0.1 -> clamped to 0.0
        assert prob == 0.0
    
    def test_luck_modifier_increases_probability(self):
        """Test that positive luck modifier increases hit probability."""
        thrower = {'throwing': 50, 'iq': 50, 'luck': 50}
        target = {'dodging': 30, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.15)
        
        # Expected: 0.5 (throwing) - 0.3 (dodging) + 0.15 (luck) = 0.35
        assert prob == pytest.approx(0.35, abs=0.01)
    
    def test_luck_modifier_decreases_probability(self):
        """Test that negative luck modifier decreases hit probability."""
        thrower = {'throwing': 50, 'iq': 50, 'luck': 50}
        target = {'dodging': 30, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=-0.15)
        
        # Expected: 0.5 (throwing) - 0.3 (dodging) - 0.15 (luck) = 0.05
        assert prob == pytest.approx(0.05, abs=0.01)
    
    def test_probability_clamped_to_zero(self):
        """Test that probability is clamped to 0.0 minimum."""
        thrower = {'throwing': 10, 'iq': 20, 'luck': 50}
        target = {'dodging': 90, 'iq': 80, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=-0.5)
        
        # Should be clamped to 0.0
        assert prob == 0.0
    
    def test_probability_clamped_to_one(self):
        """Test that probability is clamped to 1.0 maximum."""
        thrower = {'throwing': 100, 'iq': 100, 'luck': 50}
        target = {'dodging': 0, 'iq': 0, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.5)
        
        # Should be clamped to 1.0
        assert prob == 1.0
    
    def test_equal_stats_baseline(self):
        """Test probability with equal stats on both sides."""
        thrower = {'throwing': 50, 'iq': 50, 'luck': 50}
        target = {'dodging': 50, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.5 (throwing) - 0.5 (dodging) = 0.0
        assert prob == 0.0


class TestCatchProbabilityCalculation:
    """Test cases for catch probability calculations."""
    
    def test_high_catching_skill(self):
        """Test that high catching skill gives high catch probability."""
        target = {'catching': 80, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=0.0)
        
        assert prob == pytest.approx(0.8, abs=0.01)
    
    def test_low_catching_skill(self):
        """Test that low catching skill gives low catch probability."""
        target = {'catching': 20, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=0.0)
        
        assert prob == pytest.approx(0.2, abs=0.01)
    
    def test_luck_modifier_positive(self):
        """Test that positive luck increases catch probability."""
        target = {'catching': 50, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=0.2)
        
        assert prob == pytest.approx(0.7, abs=0.01)
    
    def test_luck_modifier_negative(self):
        """Test that negative luck decreases catch probability."""
        target = {'catching': 50, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=-0.2)
        
        assert prob == pytest.approx(0.3, abs=0.01)
    
    def test_catch_probability_clamped_to_zero(self):
        """Test that catch probability is clamped to 0.0."""
        target = {'catching': 10, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=-0.5)
        
        assert prob == 0.0
    
    def test_catch_probability_clamped_to_one(self):
        """Test that catch probability is clamped to 1.0."""
        target = {'catching': 90, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=0.5)
        
        assert prob == 1.0


class TestEdgeCases:
    """Test edge cases with extreme stat values."""
    
    def test_zero_throwing_skill(self):
        """Test that zero throwing skill results in zero hit probability."""
        thrower = {'throwing': 0, 'iq': 50, 'luck': 50}
        target = {'dodging': 0, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        assert prob == 0.0
    
    def test_max_throwing_zero_dodging(self):
        """Test maximum throwing against zero dodging."""
        thrower = {'throwing': 100, 'iq': 50, 'luck': 50}
        target = {'dodging': 0, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 1.0 (throwing) = 1.0
        assert prob == 1.0
    
    def test_max_dodging_vs_high_throwing(self):
        """Test maximum dodging against high throwing."""
        thrower = {'throwing': 70, 'iq': 50, 'luck': 50}
        target = {'dodging': 100, 'iq': 50, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.7 (throwing) - 1.0 (dodging) = -0.3 -> clamped to 0.0
        assert prob == 0.0
    
    def test_zero_catching_skill(self):
        """Test that zero catching skill results in zero catch probability."""
        target = {'catching': 0, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=0.0)
        
        assert prob == 0.0
    
    def test_max_catching_skill(self):
        """Test that max catching skill results in high catch probability."""
        target = {'catching': 100, 'luck': 50}
        
        prob = calculate_catch_probability(target, luck_modifier=0.0)
        
        assert prob == 1.0
    
    def test_extreme_iq_advantage(self):
        """Test extreme IQ differential impact."""
        thrower = {'throwing': 50, 'iq': 100, 'luck': 50}
        target = {'dodging': 30, 'iq': 0, 'luck': 50}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 0.5 (throwing) + 1.0 (IQ diff) - 0.3 (dodging) = 1.2 -> clamped to 1.0
        assert prob == 1.0
    
    def test_all_stats_zero(self):
        """Test with all stats at zero."""
        thrower = {'throwing': 0, 'iq': 0, 'luck': 0}
        target = {'dodging': 0, 'iq': 0, 'luck': 0}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        assert prob == 0.0
    
    def test_all_stats_max(self):
        """Test with all stats at maximum."""
        thrower = {'throwing': 100, 'iq': 100, 'luck': 100}
        target = {'dodging': 100, 'iq': 100, 'luck': 100}
        
        prob = calculate_hit_probability(thrower, target, luck_modifier=0.0)
        
        # Expected: 1.0 (throwing) - 1.0 (dodging) = 0.0
        assert prob == 0.0
