"""
Standings service for calculating league standings from team records.
"""
from typing import List, Dict


def calculate_standings(teams: List[Dict]) -> List[Dict]:
    """
    Calculate standings from team records.
    
    Ranks teams by:
    1. Wins (descending)
    2. Losses (ascending) - for tiebreaker
    
    Adds computed fields:
    - rank: Position in standings (1-based)
    - games_played: wins + losses
    - win_percentage: wins / games_played (0.0 if no games)
    
    Args:
        teams: List of dicts with team_id, team_name, wins, losses
        
    Returns:
        List of standings entries with rank and computed fields
        
    Raises:
        ValueError: If wins/losses are negative or non-integer
        ValueError: If required fields are missing
    """
    if not teams:
        return []
    
    # Validate all team entries
    for team in teams:
        _validate_team_entry(team)
    
    # Create standings entries with computed fields (don't mutate original)
    standings = []
    for team in teams:
        games_played = team["wins"] + team["losses"]
        win_percentage = team["wins"] / games_played if games_played > 0 else 0.0
        
        standings.append({
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "wins": team["wins"],
            "losses": team["losses"],
            "games_played": games_played,
            "win_percentage": win_percentage,
            "rank": 0  # Will be set after sorting
        })
    
    # Sort by wins descending, then losses ascending (fewer losses = better)
    standings.sort(key=lambda x: (-x["wins"], x["losses"]))
    
    # Assign ranks (1-based)
    for i, entry in enumerate(standings):
        entry["rank"] = i + 1
    
    return standings


def _validate_team_entry(team: Dict) -> None:
    """
    Validate a team entry has all required fields with valid values.
    
    Args:
        team: Team dict to validate
        
    Raises:
        ValueError: If validation fails
    """
    # Check required fields
    if "team_name" not in team:
        raise ValueError("team_name is required")
    
    if "team_id" not in team:
        raise ValueError("team_id is required")
    
    if "wins" not in team:
        raise ValueError("wins is required")
    
    if "losses" not in team:
        raise ValueError("losses is required")
    
    # Validate wins and losses are integers
    wins = team["wins"]
    losses = team["losses"]
    
    if not isinstance(wins, int) or isinstance(wins, bool):
        raise ValueError("wins and losses must be integers")
    
    if not isinstance(losses, int) or isinstance(losses, bool):
        raise ValueError("wins and losses must be integers")
    
    # Validate non-negative
    if wins < 0:
        raise ValueError("wins cannot be negative")
    
    if losses < 0:
        raise ValueError("losses cannot be negative")
