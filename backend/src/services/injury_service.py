"""
InjuryService for managing player injuries.

This service handles injury application, healing progression, and
stat modifications due to injuries.

References:
- FR-006: Injuries reduce effective stats by percentage
- FR-006a: Injured players can still play
"""

import random
from typing import Optional
from datetime import datetime, timezone

from ..models.player import Player, Injury, InjurySeverity


class InjuryService:
    """
    Service for managing player injuries during games.
    
    Handles probabilistic injury application, healing progression,
    and stat modifications.
    """

    def apply_injury(self, player: Player) -> Player:
        """
        Apply a random injury to a player.
        
        Uses the injury probability distribution from research.md:
        - 60% minor injuries
        - 30% moderate injuries
        - 10% severe injuries
        
        Args:
            player: Player to injure
            
        Returns:
            Player with injury applied
        """
        # Generate random severity
        severity_weights = [0.6, 0.3, 0.1]  # minor, moderate, severe
        severity = random.choices(
            [InjurySeverity.MINOR, InjurySeverity.MODERATE, InjurySeverity.SEVERE],
            weights=severity_weights
        )[0]
        
        # Create injury based on severity
        if severity == InjurySeverity.MINOR:
            injury = Injury(severity=severity, affected_reduction=0.2, games_remaining=1)
        elif severity == InjurySeverity.MODERATE:
            injury = Injury(severity=severity, affected_reduction=0.35, games_remaining=2)
        else:  # SEVERE
            injury = Injury(severity=severity, affected_reduction=0.5, games_remaining=3)
        
        # Apply injury to player
        player.injury = injury
        
        return player

    def heal_injury(self, player: Player) -> Player:
        """
        Progress healing for a player's injury by one game.
        
        Args:
            player: Player with injury to heal
            
        Returns:
            Player with updated injury status
        """
        if player.injury and not player.injury.progress_healing():
            # Injury is fully healed
            player.injury = None
        
        return player

    def get_effective_skills(self, player: Player) -> dict:
        """
        Get player's effective skills accounting for injury.
        
        Args:
            player: Player to get skills for
            
        Returns:
            Dictionary of skill name to effective value
        """
        if not player.injury:
            return {
                'catching': player.skills.catching,
                'throwing': player.skills.throwing,
                'dodging': player.skills.dodging,
                'speed': player.skills.speed,
                'iq': player.skills.iq,
                'luck': player.skills.luck
            }
        
        multiplier = player.injury.get_effective_stat_multiplier()
        return {
            'catching': int(player.skills.catching * multiplier),
            'throwing': int(player.skills.throwing * multiplier),
            'dodging': int(player.skills.dodging * multiplier),
            'speed': int(player.skills.speed * multiplier),
            'iq': int(player.skills.iq * multiplier),
            'luck': int(player.skills.luck * multiplier)
        }
