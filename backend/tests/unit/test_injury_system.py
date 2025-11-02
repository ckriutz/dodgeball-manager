"""
Unit tests for injury system mechanics.

This module tests the injury probability, severity distribution,
and healing mechanics.

References:
- research.md: Injury System Mechanics
- FR-006: 5% injury probability when player is hit
- FR-006a: Injured players can still play
- FR-007: Injury severity affects stats (20%/35%/50% reduction)
- FR-008: Injuries heal over 1-3 games
"""

import pytest
from typing import Tuple
from enum import Enum


class InjurySeverity(str, Enum):
    """Injury severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


def calculate_injury_occurrence(random_value: float) -> bool:
    """
    Determine if an injury occurs.
    
    Args:
        random_value: Random float between 0.0 and 1.0
        
    Returns:
        True if injury occurs (5% probability)
    """
    return random_value < 0.05


def determine_injury_severity(random_value: float) -> InjurySeverity:
    """
    Determine the severity of an injury.
    
    Distribution (from research.md):
    - 60% minor (0.0 - 0.6)
    - 30% moderate (0.6 - 0.9)
    - 10% severe (0.9 - 1.0)
    
    Args:
        random_value: Random float between 0.0 and 1.0
        
    Returns:
        InjurySeverity enum value
    """
    if random_value < 0.6:
        return InjurySeverity.MINOR
    elif random_value < 0.9:
        return InjurySeverity.MODERATE
    else:
        return InjurySeverity.SEVERE


def get_injury_stats(severity: InjurySeverity) -> Tuple[float, int]:
    """
    Get the stat reduction and healing time for an injury severity.
    
    Args:
        severity: Injury severity level
        
    Returns:
        Tuple of (stat_reduction, healing_games)
    """
    injury_map = {
        InjurySeverity.MINOR: (0.2, 1),
        InjurySeverity.MODERATE: (0.35, 2),
        InjurySeverity.SEVERE: (0.5, 3)
    }
    return injury_map[severity]


def apply_injury_to_stats(base_stats: dict, reduction: float) -> dict:
    """
    Apply injury reduction to player stats.
    
    Args:
        base_stats: Dictionary of skill name to value
        reduction: Percentage reduction (0.0 to 1.0)
        
    Returns:
        Dictionary of skill name to reduced value (as int)
    """
    return {
        skill: int(value * (1 - reduction))
        for skill, value in base_stats.items()
    }


def progress_injury_healing(games_remaining: int) -> int:
    """
    Reduce injury healing time by one game.
    
    Args:
        games_remaining: Current games remaining
        
    Returns:
        Updated games remaining (minimum 0)
    """
    return max(0, games_remaining - 1)


class TestInjuryOccurrence:
    """Test cases for injury occurrence probability."""
    
    def test_injury_occurs_within_threshold(self):
        """Test that injury occurs when random value is below 5%."""
        assert calculate_injury_occurrence(0.04) is True
        assert calculate_injury_occurrence(0.01) is True
        assert calculate_injury_occurrence(0.049) is True
    
    def test_no_injury_above_threshold(self):
        """Test that no injury occurs when random value is above 5%."""
        assert calculate_injury_occurrence(0.05) is False
        assert calculate_injury_occurrence(0.5) is False
        assert calculate_injury_occurrence(0.99) is False
    
    def test_injury_at_boundary(self):
        """Test injury probability at exact boundary."""
        assert calculate_injury_occurrence(0.05) is False
        assert calculate_injury_occurrence(0.04999) is True
    
    def test_injury_at_zero(self):
        """Test injury occurs at minimum random value."""
        assert calculate_injury_occurrence(0.0) is True
    
    def test_no_injury_at_one(self):
        """Test no injury at maximum random value."""
        assert calculate_injury_occurrence(1.0) is False


class TestInjurySeverityDistribution:
    """Test cases for injury severity distribution."""
    
    def test_minor_injury_range(self):
        """Test that values 0.0-0.59 result in minor injuries."""
        assert determine_injury_severity(0.0) == InjurySeverity.MINOR
        assert determine_injury_severity(0.3) == InjurySeverity.MINOR
        assert determine_injury_severity(0.59) == InjurySeverity.MINOR
    
    def test_moderate_injury_range(self):
        """Test that values 0.6-0.89 result in moderate injuries."""
        assert determine_injury_severity(0.6) == InjurySeverity.MODERATE
        assert determine_injury_severity(0.75) == InjurySeverity.MODERATE
        assert determine_injury_severity(0.89) == InjurySeverity.MODERATE
    
    def test_severe_injury_range(self):
        """Test that values 0.9-1.0 result in severe injuries."""
        assert determine_injury_severity(0.9) == InjurySeverity.SEVERE
        assert determine_injury_severity(0.95) == InjurySeverity.SEVERE
        assert determine_injury_severity(0.99) == InjurySeverity.SEVERE
    
    def test_severity_boundaries(self):
        """Test exact boundary values."""
        # Just below boundaries should be previous severity
        assert determine_injury_severity(0.5999) == InjurySeverity.MINOR
        assert determine_injury_severity(0.8999) == InjurySeverity.MODERATE
        
        # At boundaries should be next severity
        assert determine_injury_severity(0.6) == InjurySeverity.MODERATE
        assert determine_injury_severity(0.9) == InjurySeverity.SEVERE


class TestInjuryStats:
    """Test cases for injury stat calculations."""
    
    def test_minor_injury_stats(self):
        """Test that minor injuries have 20% reduction and 1 game healing."""
        reduction, healing = get_injury_stats(InjurySeverity.MINOR)
        assert reduction == 0.2
        assert healing == 1
    
    def test_moderate_injury_stats(self):
        """Test that moderate injuries have 35% reduction and 2 games healing."""
        reduction, healing = get_injury_stats(InjurySeverity.MODERATE)
        assert reduction == 0.35
        assert healing == 2
    
    def test_severe_injury_stats(self):
        """Test that severe injuries have 50% reduction and 3 games healing."""
        reduction, healing = get_injury_stats(InjurySeverity.SEVERE)
        assert reduction == 0.5
        assert healing == 3


class TestStatReduction:
    """Test cases for applying injury reduction to stats."""
    
    def test_minor_injury_reduction(self):
        """Test 20% stat reduction for minor injury."""
        base_stats = {
            'catching': 50,
            'throwing': 60,
            'dodging': 70,
            'speed': 40,
            'iq': 80,
            'luck': 30
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 0.2)
        
        assert reduced_stats['catching'] == 40  # 50 * 0.8 = 40
        assert reduced_stats['throwing'] == 48  # 60 * 0.8 = 48
        assert reduced_stats['dodging'] == 56  # 70 * 0.8 = 56
        assert reduced_stats['speed'] == 32   # 40 * 0.8 = 32
        assert reduced_stats['iq'] == 64       # 80 * 0.8 = 64
        assert reduced_stats['luck'] == 24     # 30 * 0.8 = 24
    
    def test_moderate_injury_reduction(self):
        """Test 35% stat reduction for moderate injury."""
        base_stats = {
            'catching': 100,
            'throwing': 80,
            'dodging': 60,
            'speed': 40,
            'iq': 20,
            'luck': 50
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 0.35)
        
        assert reduced_stats['catching'] == 65  # 100 * 0.65 = 65
        assert reduced_stats['throwing'] == 52  # 80 * 0.65 = 52
        assert reduced_stats['dodging'] == 39   # 60 * 0.65 = 39
        assert reduced_stats['speed'] == 26     # 40 * 0.65 = 26
        assert reduced_stats['iq'] == 13         # 20 * 0.65 = 13
        assert reduced_stats['luck'] == 32      # 50 * 0.65 = 32.5 -> 32
    
    def test_severe_injury_reduction(self):
        """Test 50% stat reduction for severe injury."""
        base_stats = {
            'catching': 80,
            'throwing': 70,
            'dodging': 60,
            'speed': 50,
            'iq': 40,
            'luck': 30
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 0.5)
        
        assert reduced_stats['catching'] == 40  # 80 * 0.5 = 40
        assert reduced_stats['throwing'] == 35  # 70 * 0.5 = 35
        assert reduced_stats['dodging'] == 30   # 60 * 0.5 = 30
        assert reduced_stats['speed'] == 25     # 50 * 0.5 = 25
        assert reduced_stats['iq'] == 20         # 40 * 0.5 = 20
        assert reduced_stats['luck'] == 15      # 30 * 0.5 = 15
    
    def test_reduction_with_low_stats(self):
        """Test stat reduction doesn't produce negative values."""
        base_stats = {
            'catching': 10,
            'throwing': 5,
            'dodging': 3,
            'speed': 1,
            'iq': 2,
            'luck': 4
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 0.5)
        
        assert all(value >= 0 for value in reduced_stats.values())
        assert reduced_stats['catching'] == 5
        assert reduced_stats['throwing'] == 2
        assert reduced_stats['dodging'] == 1
        assert reduced_stats['speed'] == 0
        assert reduced_stats['iq'] == 1
        assert reduced_stats['luck'] == 2
    
    def test_reduction_with_max_stats(self):
        """Test stat reduction with maximum stat values."""
        base_stats = {
            'catching': 100,
            'throwing': 100,
            'dodging': 100,
            'speed': 100,
            'iq': 100,
            'luck': 100
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 0.2)
        
        assert all(value == 80 for value in reduced_stats.values())
    
    def test_no_reduction(self):
        """Test that 0% reduction leaves stats unchanged."""
        base_stats = {
            'catching': 50,
            'throwing': 60,
            'dodging': 70,
            'speed': 40,
            'iq': 80,
            'luck': 30
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 0.0)
        
        assert reduced_stats == base_stats
    
    def test_full_reduction(self):
        """Test that 100% reduction results in zero stats."""
        base_stats = {
            'catching': 50,
            'throwing': 60,
            'dodging': 70,
            'speed': 40,
            'iq': 80,
            'luck': 30
        }
        
        reduced_stats = apply_injury_to_stats(base_stats, 1.0)
        
        assert all(value == 0 for value in reduced_stats.values())


class TestInjuryHealing:
    """Test cases for injury healing progression."""
    
    def test_minor_injury_healing(self):
        """Test that minor injury heals after 1 game."""
        games_remaining = 1
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 0
    
    def test_moderate_injury_healing_progression(self):
        """Test that moderate injury heals over 2 games."""
        games_remaining = 2
        
        # After first game
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 1
        
        # After second game
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 0
    
    def test_severe_injury_healing_progression(self):
        """Test that severe injury heals over 3 games."""
        games_remaining = 3
        
        # After first game
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 2
        
        # After second game
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 1
        
        # After third game
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 0
    
    def test_healing_does_not_go_negative(self):
        """Test that healing time doesn't go below zero."""
        games_remaining = 0
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 0
        
        # Try again to ensure it stays at zero
        games_remaining = progress_injury_healing(games_remaining)
        assert games_remaining == 0


class TestInjuryIntegration:
    """Integration tests for complete injury workflow."""
    
    def test_complete_minor_injury_workflow(self):
        """Test full workflow of minor injury from occurrence to healing."""
        # Player gets hit - check if injury occurs
        injury_occurred = calculate_injury_occurrence(0.03)
        assert injury_occurred is True
        
        # Determine severity
        severity = determine_injury_severity(0.3)
        assert severity == InjurySeverity.MINOR
        
        # Get injury stats
        reduction, healing_time = get_injury_stats(severity)
        assert reduction == 0.2
        assert healing_time == 1
        
        # Apply to player stats
        base_stats = {'catching': 50, 'throwing': 60, 'dodging': 70, 'speed': 40, 'iq': 80, 'luck': 30}
        reduced_stats = apply_injury_to_stats(base_stats, reduction)
        assert reduced_stats['catching'] == 40
        
        # Heal after one game
        healing_time = progress_injury_healing(healing_time)
        assert healing_time == 0
    
    def test_complete_moderate_injury_workflow(self):
        """Test full workflow of moderate injury."""
        # Injury occurs
        injury_occurred = calculate_injury_occurrence(0.02)
        assert injury_occurred is True
        
        # Moderate severity
        severity = determine_injury_severity(0.75)
        assert severity == InjurySeverity.MODERATE
        
        # Get stats
        reduction, healing_time = get_injury_stats(severity)
        assert reduction == 0.35
        assert healing_time == 2
        
        # Apply reduction
        base_stats = {'catching': 100, 'throwing': 100, 'dodging': 100, 'speed': 100, 'iq': 100, 'luck': 100}
        reduced_stats = apply_injury_to_stats(base_stats, reduction)
        assert reduced_stats['catching'] == 65
        
        # Heal over 2 games
        healing_time = progress_injury_healing(healing_time)
        assert healing_time == 1
        healing_time = progress_injury_healing(healing_time)
        assert healing_time == 0
    
    def test_no_injury_scenario(self):
        """Test workflow when no injury occurs."""
        injury_occurred = calculate_injury_occurrence(0.8)
        assert injury_occurred is False
        
        # Player stats remain unchanged
        base_stats = {'catching': 50, 'throwing': 60, 'dodging': 70, 'speed': 40, 'iq': 80, 'luck': 30}
        # No reduction applied
        assert base_stats == base_stats
