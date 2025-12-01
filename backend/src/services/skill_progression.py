"""
Skill progression service for XP calculation and leveling.

This module handles:
- XP award calculation based on game performance
- Level progression logic with exponential scaling
- Skill point allocation and spending
- Progress tracking toward next level

References:
- skill-progression-plan.md: Detailed XP system design
- FR-008: XP-based skill progression system
- T100: Implement SkillProgressionService
"""

from typing import Dict, Tuple, Any


# XP award constants
BASE_PARTICIPATION_XP = 10
XP_PER_HIT = 20
XP_PER_CATCH = 15
XP_PER_THROW = 2
SURVIVAL_BONUS_XP = 10
WIN_BONUS_XP = 25

# Level constants
MAX_LEVEL = 100
MIN_LEVEL = 1

# Valid skill names
VALID_SKILLS = frozenset(['catching', 'throwing', 'dodging', 'speed', 'iq', 'luck'])


def calculate_game_xp(
    throws_attempted: int,
    catches_made: int,
    successful_hits: int,
    times_hit: int,
    is_winner: bool
) -> int:
    """
    Calculate XP earned from a game based on performance.
    
    XP Breakdown:
    - Base participation: 10 XP
    - Per successful hit: 20 XP (offense reward)
    - Per catch: 15 XP (defense reward)
    - Per throw attempted: 2 XP (activity reward)
    - Survival bonus (not eliminated): 10 XP
    - Win bonus: 25 XP
    
    Typical game XP ranges:
    - Poor performance, loss: 30-50 XP
    - Average performance, loss: 50-80 XP
    - Good performance, loss: 80-120 XP
    - Poor performance, win: 55-75 XP
    - Average performance, win: 75-105 XP
    - Good performance, win: 105-145 XP
    - Exceptional performance, win: 145-200+ XP
    
    Args:
        throws_attempted: Number of throws
        catches_made: Number of catches
        successful_hits: Number of eliminations
        times_hit: Number of times eliminated
        is_winner: Whether player's team won
        
    Returns:
        Total XP earned
        
    Raises:
        ValueError: If any stat is negative
    """
    # Validate inputs
    if throws_attempted < 0:
        raise ValueError("throws_attempted cannot be negative")
    if catches_made < 0:
        raise ValueError("catches_made cannot be negative")
    if successful_hits < 0:
        raise ValueError("successful_hits cannot be negative")
    if times_hit < 0:
        raise ValueError("times_hit cannot be negative")
    
    xp = BASE_PARTICIPATION_XP
    
    # Performance-based XP
    xp += successful_hits * XP_PER_HIT
    xp += catches_made * XP_PER_CATCH
    xp += throws_attempted * XP_PER_THROW
    
    # Survival bonus (didn't get hit)
    if times_hit == 0:
        xp += SURVIVAL_BONUS_XP
    
    # Win bonus
    if is_winner:
        xp += WIN_BONUS_XP
    
    return xp


def calculate_xp_for_level(level: int) -> int:
    """
    Calculate total XP required to reach a specific level.
    
    Uses exponential scaling: Sum of (100 * i^1.5) for i from 1 to level-1
    
    Level thresholds (cumulative):
    - Level 1: 0 XP (starting level)
    - Level 2: 100 XP
    - Level 3: 283 XP (100 + 183)
    - Level 5: 1118 XP
    - Level 10: 3162 XP
    
    Args:
        level: Target level (1-100)
        
    Returns:
        Total cumulative XP required to reach this level
        
    Raises:
        ValueError: If level is < 1 or > 100
    """
    if level < MIN_LEVEL:
        raise ValueError(f"Level cannot be less than {MIN_LEVEL}")
    if level > MAX_LEVEL:
        raise ValueError(f"Level cannot exceed {MAX_LEVEL}")
    
    if level == 1:
        return 0
    
    # Calculate cumulative XP: sum of (100 * i^1.5) for i from 1 to level-1
    total = 0
    for i in range(1, level):
        total += int(100 * (i ** 1.5))
    
    return total


def calculate_xp_for_next_level(current_level: int) -> int:
    """
    Calculate XP required to go from current level to next level.
    
    Formula: 100 * current_level^1.5
    
    Args:
        current_level: Current player level (1-99)
        
    Returns:
        XP required for next level
        
    Raises:
        ValueError: If level is invalid
    """
    if current_level < MIN_LEVEL:
        raise ValueError(f"Level cannot be less than {MIN_LEVEL}")
    if current_level >= MAX_LEVEL:
        raise ValueError(f"Cannot calculate next level XP for max level {MAX_LEVEL}")
    
    return int(100 * (current_level ** 1.5))


def award_xp_and_level_up(player_stats: dict, xp_amount: int) -> dict:
    """
    Award XP to player and handle automatic leveling.
    
    This function awards XP to a player and automatically levels them up
    if they've earned enough XP. Multiple levels can be gained from a
    single XP award if the amount is large enough.
    
    Args:
        player_stats: Dict with experience_points, level, available_skill_points
        xp_amount: Amount of XP to award (must be non-negative)
        
    Returns:
        Updated player stats dict with:
        - experience_points: Updated total XP
        - level: New level (may be same if not enough XP)
        - available_skill_points: Updated skill points (1 per level gained)
        
    Raises:
        ValueError: If xp_amount is negative
    """
    if xp_amount < 0:
        raise ValueError("XP amount must be non-negative")
    
    # Make a copy to avoid mutating input
    updated_stats = {
        "experience_points": player_stats.get("experience_points", 0) + xp_amount,
        "level": player_stats.get("level", 1),
        "available_skill_points": player_stats.get("available_skill_points", 0)
    }
    
    # Check for level ups
    while updated_stats["level"] < MAX_LEVEL:
        xp_needed_for_next = calculate_xp_for_level(updated_stats["level"] + 1)
        
        if updated_stats["experience_points"] >= xp_needed_for_next:
            updated_stats["level"] += 1
            updated_stats["available_skill_points"] += 1
        else:
            break
    
    return updated_stats


def calculate_xp_progress(player_stats: dict) -> dict:
    """
    Calculate XP progress toward next level.
    
    Args:
        player_stats: Dict with experience_points and level
        
    Returns:
        Dict containing:
        - level: Current level
        - experience_points: Total XP
        - xp_for_next_level: XP needed to reach next level from current
        - xp_progress: XP earned toward next level
        - progress_percentage: Percentage progress to next level (0-100)
    """
    current_level = player_stats.get("level", 1)
    current_xp = player_stats.get("experience_points", 0)
    available_points = player_stats.get("available_skill_points", 0)
    
    # Calculate thresholds
    current_level_threshold = calculate_xp_for_level(current_level)
    
    # Handle max level case
    if current_level >= MAX_LEVEL:
        return {
            "level": current_level,
            "experience_points": current_xp,
            "available_skill_points": available_points,
            "xp_for_next_level": 0,
            "xp_progress": 0,
            "progress_percentage": 100
        }
    
    next_level_threshold = calculate_xp_for_level(current_level + 1)
    xp_for_next = next_level_threshold - current_level_threshold
    xp_progress = current_xp - current_level_threshold
    
    # Ensure xp_progress is not negative (shouldn't happen in normal use)
    xp_progress = max(0, xp_progress)
    
    progress_percentage = (xp_progress / xp_for_next * 100) if xp_for_next > 0 else 100
    
    return {
        "level": current_level,
        "experience_points": current_xp,
        "available_skill_points": available_points,
        "xp_for_next_level": xp_for_next,
        "xp_progress": xp_progress,
        "progress_percentage": min(100, progress_percentage)
    }


def spend_skill_point(player: dict, skill_name: str) -> dict:
    """
    Spend a skill point to increase a specific skill by 1.
    
    Args:
        player: Player dict with 'skills' and 'available_skill_points'
        skill_name: Name of skill to increase (catching, throwing, dodging, speed, iq, luck)
        
    Returns:
        Dict containing:
        - success: Whether the point was spent
        - skills: Updated skills dict
        - available_skill_points: Remaining skill points
        - error: Error message if failed (optional)
        
    Raises:
        ValueError: If skill_name is not a valid skill
    """
    # Validate skill name
    if skill_name not in VALID_SKILLS:
        raise ValueError(f"Invalid skill name: {skill_name}. Valid skills: {', '.join(sorted(VALID_SKILLS))}")
    
    # Make copies to avoid mutating input
    skills = dict(player.get("skills", {}))
    available_points = player.get("available_skill_points", 0)
    
    # Check if points available
    if available_points <= 0:
        return {
            "success": False,
            "skills": skills,
            "available_skill_points": available_points,
            "error": "No skill points available"
        }
    
    # Check if skill is at max
    current_value = skills.get(skill_name, 0)
    if current_value >= 100:
        return {
            "success": False,
            "skills": skills,
            "available_skill_points": available_points,
            "error": f"{skill_name} is already at maximum (100)"
        }
    
    # Spend the point
    skills[skill_name] = current_value + 1
    available_points -= 1
    
    return {
        "success": True,
        "skills": skills,
        "available_skill_points": available_points
    }


def spend_multiple_skill_points(player: dict, allocations: Dict[str, int]) -> dict:
    """
    Spend multiple skill points at once across different skills.
    
    This function validates all allocations before spending any points,
    ensuring atomic behavior (all or nothing).
    
    Args:
        player: Player dict with 'skills' and 'available_skill_points'
        allocations: Dict mapping skill_name -> points_to_spend
                     e.g., {"throwing": 2, "catching": 1}
        
    Returns:
        Dict containing:
        - success: Whether all points were spent
        - skills: Updated skills dict
        - available_skill_points: Remaining skill points
        - error: Error message if failed (optional)
        
    Raises:
        ValueError: If any skill_name is invalid
    """
    # Validate all skill names first
    for skill_name in allocations:
        if skill_name not in VALID_SKILLS:
            raise ValueError(f"Invalid skill name: {skill_name}. Valid skills: {', '.join(sorted(VALID_SKILLS))}")
    
    # Make copies to avoid mutating input
    skills = dict(player.get("skills", {}))
    available_points = player.get("available_skill_points", 0)
    
    # Calculate total points needed
    total_points_needed = sum(allocations.values())
    
    # Check if enough points available
    if total_points_needed > available_points:
        return {
            "success": False,
            "skills": skills,
            "available_skill_points": available_points,
            "error": f"Not enough skill points. Have {available_points}, need {total_points_needed}"
        }
    
    # Validate all allocations won't exceed max
    for skill_name, points in allocations.items():
        if points < 0:
            return {
                "success": False,
                "skills": skills,
                "available_skill_points": available_points,
                "error": f"Cannot allocate negative points to {skill_name}"
            }
        
        current_value = skills.get(skill_name, 0)
        if current_value + points > 100:
            return {
                "success": False,
                "skills": skills,
                "available_skill_points": available_points,
                "error": f"Cannot increase {skill_name} by {points}. Would exceed max of 100"
            }
    
    # All validations passed, apply allocations
    for skill_name, points in allocations.items():
        skills[skill_name] = skills.get(skill_name, 0) + points
    
    available_points -= total_points_needed
    
    return {
        "success": True,
        "skills": skills,
        "available_skill_points": available_points
    }


class SkillProgressionService:
    """
    Service class for managing player skill progression.
    
    This service wraps the module-level functions and provides
    a more object-oriented interface for use with Player models.
    """
    
    def __init__(self):
        """Initialize the SkillProgressionService."""
        pass
    
    def calculate_game_xp(
        self,
        throws_attempted: int,
        catches_made: int,
        successful_hits: int,
        times_hit: int,
        is_winner: bool
    ) -> int:
        """Calculate XP from game performance. See module function for details."""
        return calculate_game_xp(
            throws_attempted, catches_made, successful_hits, times_hit, is_winner
        )
    
    def award_xp_to_player(self, player: Any, xp_amount: int) -> Tuple[Any, int, bool]:
        """
        Award XP to a Player model and handle leveling.
        
        Args:
            player: Player model instance
            xp_amount: Amount of XP to award
            
        Returns:
            Tuple of (player, levels_gained, did_level_up)
        """
        initial_level = player.stats.level
        
        # Award XP using the stats model's method
        levels_gained = player.stats.award_xp(xp_amount)
        did_level_up = levels_gained > 0
        
        # Recalculate player value since level affects it
        if hasattr(player, 'recalculate_value'):
            player.value = player.recalculate_value()
        
        return player, levels_gained, did_level_up
    
    def spend_skill_point_on_player(self, player: Any, skill_name: str) -> Tuple[bool, str]:
        """
        Spend a skill point on a Player model.
        
        Args:
            player: Player model instance
            skill_name: Name of skill to increase
            
        Returns:
            Tuple of (success, error_message)
        """
        if skill_name not in VALID_SKILLS:
            return False, f"Invalid skill name: {skill_name}"
        
        if player.stats.available_skill_points <= 0:
            return False, "No skill points available"
        
        current_value = getattr(player.skills, skill_name, 0)
        if current_value >= 100:
            return False, f"{skill_name} is already at maximum (100)"
        
        # Increase the skill
        setattr(player.skills, skill_name, current_value + 1)
        player.stats.available_skill_points -= 1
        
        # Recalculate value
        if hasattr(player, 'recalculate_value'):
            player.value = player.recalculate_value()
        
        return True, ""
    
    def get_player_progression_info(self, player: Any) -> dict:
        """
        Get progression information for a Player model.
        
        Args:
            player: Player model instance
            
        Returns:
            Dict with level, XP, progress to next level
        """
        return calculate_xp_progress({
            "experience_points": player.stats.experience_points,
            "level": player.stats.level,
            "available_skill_points": player.stats.available_skill_points
        })
