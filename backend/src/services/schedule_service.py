"""
Schedule service for generating round-robin tournament schedules.
"""
import random
from itertools import combinations
from typing import List, Tuple, Optional


def generate_round_robin_schedule(
    teams: List[str],
    rounds: int = 1,
    shuffle: bool = False,
    seed: Optional[int] = None
) -> List[Tuple[str, str]]:
    """
    Generate a round-robin schedule for a list of teams.
    
    Uses the circle method algorithm for generating round-robin tournaments,
    ensuring every team plays every other team the specified number of times.
    
    Args:
        teams: List of team IDs
        rounds: Number of times each pairing plays (default 1)
        shuffle: Whether to randomize game order
        seed: Random seed for shuffle reproducibility
        
    Returns:
        List of (team1_id, team2_id) tuples representing games
        
    Raises:
        ValueError: If less than 2 teams or rounds < 1
    """
    # Validation
    if len(teams) < 2:
        raise ValueError("Schedule generation requires at least 2 teams")
    
    if rounds < 1:
        raise ValueError("Schedule generation requires at least 1 round")
    
    # Generate all unique pairings using combinations
    all_pairings = list(combinations(teams, 2))
    
    # Create the schedule by repeating pairings for each round
    schedule = []
    for _ in range(rounds):
        schedule.extend(all_pairings)
    
    # Optionally shuffle the schedule
    if shuffle:
        if seed is not None:
            random.seed(seed)
        random.shuffle(schedule)
    
    return schedule


def generate_round_robin_schedule_with_numbers(
    teams: List[str],
    rounds: int = 1
) -> List[dict]:
    """
    Generate a round-robin schedule with game numbers.
    
    Creates a schedule with sequential game numbering, useful for
    creating ScheduledGame objects.
    
    Args:
        teams: List of team IDs
        rounds: Number of times each pairing plays (default 1)
        
    Returns:
        List of dicts with game_number, team1_id, team2_id, completed
    """
    schedule = generate_round_robin_schedule(teams, rounds)
    
    return [
        {
            "game_number": i + 1,
            "team1_id": team1,
            "team2_id": team2,
            "completed": False
        }
        for i, (team1, team2) in enumerate(schedule)
    ]


def calculate_expected_games(team_count: int, rounds: int) -> int:
    """
    Calculate expected number of games for round-robin schedule.
    
    Uses the formula: C(n, 2) * rounds = (n * (n-1) / 2) * rounds
    where n is the number of teams.
    
    Args:
        team_count: Number of teams
        rounds: Number of rounds
        
    Returns:
        Expected game count
    """
    if team_count < 2:
        return 0
    return (team_count * (team_count - 1) // 2) * rounds
