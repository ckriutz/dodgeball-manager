"""
Utility functions for the Dodgeball Fantasy League backend.

This module provides common utility functions used across services,
including player value calculation, skill validation, and other helpers.
"""

from typing import Dict, List, Tuple, Set
import random
import json
import os
from pathlib import Path


# Track used names globally to prevent duplicates
_used_player_names: Set[str] = set()
_available_player_names: List[str] = []


def _load_player_names() -> List[str]:
    """
    Load player names from JSON file.
    
    Returns:
        List of available player names
    """
    # Get path to player names JSON file
    current_dir = Path(__file__).parent.parent
    names_file = current_dir / "data" / "player_names.json"
    
    with open(names_file, 'r') as f:
        data = json.load(f)
        return data.get('names', [])


def get_random_player_name() -> str:
    """
    Get a random unused player name.
    
    Returns:
        A unique player name
        
    Raises:
        ValueError: If all names have been used
    """
    global _available_player_names, _used_player_names
    
    # Load names if not already loaded
    if not _available_player_names and not _used_player_names:
        all_names = _load_player_names()
        _available_player_names = all_names.copy()
    
    # If all names used, raise error
    if not _available_player_names:
        raise ValueError("All player names have been used. Please add more names to player_names.json")
    
    # Pick a random name from available names
    name = random.choice(_available_player_names)
    _available_player_names.remove(name)
    _used_player_names.add(name)
    
    return name


def reset_player_names() -> None:
    """
    Reset the player names pool (useful for testing).
    """
    global _available_player_names, _used_player_names
    _available_player_names = []
    _used_player_names = set()


def calculate_player_value(
    skills: Dict[str, int],
    age: int,
    level: int = 1,
    games_played: int = 0
) -> int:
    """
    Calculate a player's dollar value based on skills, age, level, and games played.
    
    Comprehensive Formula (Updated Nov 4, 2025):
        base_value = (
            (sum_of_skills * 100) +           # Skills: primary factor
            (games_played * 50) +             # Experience bonus
            (level * 200) -                   # Progression bonus
            (age_penalty_after_30)            # Age penalty
        )
        age_penalty = max(0, (age - 30) * 500)  # 500 per year over 30
    
    Args:
        skills: Dictionary of skill name to skill value (0-100)
        age: Player age
        level: Player level (default 1 for new players)
        games_played: Number of games played (default 0 for new players)
    
    Returns:
        Integer dollar value (no cents)
    
    Examples:
        >>> skills = {'catching': 2, 'throwing': 2, 'dodging': 2, 'speed': 2, 'iq': 1, 'luck': 1}
        >>> calculate_player_value(skills, 19)  # New player
        1200
        >>> calculate_player_value(skills, 19, level=3, games_played=10)  # Growing player
        2100
        >>> skills_advanced = {'catching': 10, 'throwing': 10, 'dodging': 10, 'speed': 10, 'iq': 10, 'luck': 10}
        >>> calculate_player_value(skills_advanced, 25, level=8, games_played=50)
        10100
        >>> calculate_player_value(skills_advanced, 32, level=15, games_played=100)  # With age penalty
        14000
    """
    # Calculate skill component: sum of all skills * 100
    skill_value = sum(skills.values()) * 100
    
    # Calculate experience bonus: games_played * 50
    experience_bonus = games_played * 50
    
    # Calculate progression bonus: level * 200
    progression_bonus = level * 200
    
    # Calculate age penalty: 500 per year over 30 (minimum 0)
    age_penalty = max(0, (age - 30) * 500)
    
    # Calculate total value
    total_value = skill_value + experience_bonus + progression_bonus - age_penalty
    
    # Ensure value is never negative
    return max(0, int(total_value))


def validate_skill_distribution(skills: Dict[str, int], total_required: int = 10) -> Tuple[bool, str]:
    """
    Validate that skill points are distributed correctly for a new player.
    
    Rules:
        - Each skill must be 0-100 (FR-003)
        - Sum of all skills must equal total_required for new players (FR-002, default 10)
    
    Args:
        skills: Dictionary of skill name to skill value
        total_required: Required sum of all skills (default 10 for new players)
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Examples:
        >>> skills = {'catching': 2, 'throwing': 2, 'dodging': 2, 'speed': 2, 'iq': 1, 'luck': 1}
        >>> validate_skill_distribution(skills)
        (True, '')
        >>> skills = {'catching': 5, 'throwing': 5, 'dodging': 0, 'speed': 0, 'iq': 0, 'luck': 0}
        >>> validate_skill_distribution(skills)
        (False, 'Skill sum is 10 but required sum is 10')
    """
    required_skills = {'catching', 'throwing', 'dodging', 'speed', 'iq', 'luck'}
    
    # Check all required skills are present
    if set(skills.keys()) != required_skills:
        missing = required_skills - set(skills.keys())
        extra = set(skills.keys()) - required_skills
        msg = []
        if missing:
            msg.append(f"Missing skills: {missing}")
        if extra:
            msg.append(f"Extra skills: {extra}")
        return False, "; ".join(msg)
    
    # Validate each skill is in range 0-100
    for skill_name, skill_value in skills.items():
        if not (0 <= skill_value <= 100):
            return False, f"Skill '{skill_name}' value {skill_value} is outside range [0, 100]"
    
    # Validate sum equals required total
    skill_sum = sum(skills.values())
    if skill_sum != total_required:
        return False, f"Skill sum is {skill_sum} but required sum is {total_required}"
    
    return True, ""


def distribute_skill_points(total_points: int = 10, num_skills: int = 6) -> Dict[str, int]:
    """
    Randomly distribute skill points across skills.
    
    Ensures each skill gets at least 0 points and the total equals total_points.
    Uses a weighted random distribution for variety.
    
    Args:
        total_points: Total skill points to distribute (default 10)
        num_skills: Number of skills to distribute across (default 6)
    
    Returns:
        Dictionary mapping skill names to values
    
    Examples:
        >>> random.seed(42)
        >>> skills = distribute_skill_points(10, 6)
        >>> sum(skills.values())
        10
        >>> all(0 <= v <= 10 for v in skills.values())
        True
    """
    skill_names = ['catching', 'throwing', 'dodging', 'speed', 'iq', 'luck']
    
    if num_skills != len(skill_names):
        raise ValueError(f"num_skills must be {len(skill_names)}")
    
    # Initialize all skills to 0
    skills = {name: 0 for name in skill_names}
    
    # Distribute points one at a time
    remaining = total_points
    while remaining > 0:
        # Randomly select a skill to increment
        skill_name = random.choice(skill_names)
        skills[skill_name] += 1
        remaining -= 1
    
    return skills


def apply_skill_reduction(skills: Dict[str, int], reduction: float) -> Dict[str, int]:
    """
    Apply a percentage reduction to all skills (for injuries).
    
    Args:
        skills: Dictionary of skill name to skill value
        reduction: Reduction percentage as a decimal (e.g., 0.2 for 20%)
    
    Returns:
        Dictionary with reduced skill values (rounded down)
    
    Examples:
        >>> skills = {'catching': 10, 'throwing': 10, 'dodging': 10, 'speed': 10, 'iq': 10, 'luck': 10}
        >>> apply_skill_reduction(skills, 0.2)
        {'catching': 8, 'throwing': 8, 'dodging': 8, 'speed': 8, 'iq': 8, 'luck': 8}
    """
    return {
        name: int(value * (1 - reduction))
        for name, value in skills.items()
    }


def calculate_effective_skills(
    base_skills: Dict[str, int],
    injury_reduction: float = 0.0
) -> Dict[str, int]:
    """
    Calculate effective skills considering injuries.
    
    Args:
        base_skills: Base skill values
        injury_reduction: Injury reduction percentage (0.0 if not injured)
    
    Returns:
        Effective skill values
    
    Examples:
        >>> skills = {'catching': 10, 'throwing': 10, 'dodging': 10, 'speed': 10, 'iq': 10, 'luck': 10}
        >>> calculate_effective_skills(skills, 0.0)
        {'catching': 10, 'throwing': 10, 'dodging': 10, 'speed': 10, 'iq': 10, 'luck': 10}
        >>> calculate_effective_skills(skills, 0.2)
        {'catching': 8, 'throwing': 8, 'dodging': 8, 'speed': 8, 'iq': 8, 'luck': 8}
    """
    if injury_reduction <= 0:
        return base_skills.copy()
    
    return apply_skill_reduction(base_skills, injury_reduction)


def generate_random_age(min_age: int = 18, max_age: int = 20) -> int:
    """
    Generate a random age within the specified range.
    
    Args:
        min_age: Minimum age (default 18, per FR-001)
        max_age: Maximum age (default 20, per FR-001)
    
    Returns:
        Random age within range (inclusive)
    
    Examples:
        >>> random.seed(42)
        >>> age = generate_random_age(18, 20)
        >>> 18 <= age <= 20
        True
    """
    return random.randint(min_age, max_age)


def calculate_win_percentage(wins: int, losses: int) -> float:
    """
    Calculate win percentage.
    
    Args:
        wins: Number of wins
        losses: Number of losses
    
    Returns:
        Win percentage as decimal (0.0 to 1.0)
    
    Examples:
        >>> calculate_win_percentage(5, 5)
        0.5
        >>> calculate_win_percentage(10, 0)
        1.0
        >>> calculate_win_percentage(0, 10)
        0.0
        >>> calculate_win_percentage(0, 0)
        0.0
    """
    total_games = wins + losses
    if total_games == 0:
        return 0.0
    return wins / total_games


def validate_budget(spent: int, budget: int, player_value: int) -> Tuple[bool, str]:
    """
    Validate that adding a player would not exceed budget.
    
    Args:
        spent: Amount already spent
        budget: Total budget available
        player_value: Value of player to add
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Examples:
        >>> validate_budget(50000, 100000, 30000)
        (True, '')
        >>> validate_budget(50000, 100000, 50001)
        (False, 'Insufficient budget: need $50001 but only have $50000 remaining')
        >>> validate_budget(50000, 100000, 50000)
        (True, '')
    """
    remaining = budget - spent
    
    if player_value > remaining:
        return False, f"Insufficient budget: need ${player_value} but only have ${remaining} remaining"
    
    return True, ""


def validate_roster_size(
    current_size: int,
    min_size: int = 8,
    max_size: int = 12
) -> Tuple[bool, str]:
    """
    Validate roster size constraints.
    
    Args:
        current_size: Current number of players on roster
        min_size: Minimum roster size (default 8, per FR-012)
        max_size: Maximum roster size (default 12, per FR-012)
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Examples:
        >>> validate_roster_size(10)
        (True, '')
        >>> validate_roster_size(7)
        (False, 'Roster size 7 is below minimum of 8')
        >>> validate_roster_size(13)
        (False, 'Roster size 13 exceeds maximum of 12')
    """
    if current_size < min_size:
        return False, f"Roster size {current_size} is below minimum of {min_size}"
    
    if current_size > max_size:
        return False, f"Roster size {current_size} exceeds maximum of {max_size}"
    
    return True, ""


def validate_starters_count(starters_count: int, required: int = 5) -> Tuple[bool, str]:
    """
    Validate number of starters.
    
    Args:
        starters_count: Number of designated starters
        required: Required number of starters (default 5, per FR-013)
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Examples:
        >>> validate_starters_count(5)
        (True, '')
        >>> validate_starters_count(4)
        (False, 'Must have exactly 5 starters, but have 4')
        >>> validate_starters_count(6)
        (False, 'Must have exactly 5 starters, but have 6')
    """
    if starters_count != required:
        return False, f"Must have exactly {required} starters, but have {starters_count}"
    
    return True, ""
