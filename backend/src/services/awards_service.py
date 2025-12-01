"""
Awards service for calculating MVP and statistical leaders.
"""
from typing import List, Dict, Optional


def calculate_mvp(players: List[Dict], min_games: int = 0) -> Optional[Dict]:
    """
    Calculate MVP based on combined performance score.
    
    Formula: (successful_hits * 2) + (catches_made * 1.5)
    
    The MVP formula weights eliminating opponents slightly higher than
    catching throws, reflecting the aggressive nature of dodgeball.
    
    Args:
        players: List of player stats with successful_hits, catches_made, games_played
        min_games: Minimum games required for eligibility (default 0)
        
    Returns:
        MVP player dict with player_id, name, mvp_score, reason, 
        or None if no eligible players
    """
    if not players:
        return None
    
    # Filter by minimum games requirement
    eligible = [p for p in players if p.get("games_played", 0) >= min_games]
    
    if not eligible:
        return None
    
    # Calculate MVP scores
    scored_players = []
    for player in eligible:
        hits = player.get("successful_hits", 0)
        catches = player.get("catches_made", 0)
        mvp_score = (hits * 2) + (catches * 1.5)
        scored_players.append({
            **player,
            "mvp_score": mvp_score
        })
    
    # Sort by MVP score descending, with player_id as tiebreaker for consistency
    scored_players.sort(key=lambda x: (-x["mvp_score"], x.get("player_id", "")))
    
    winner = scored_players[0]
    hits = winner.get("successful_hits", 0)
    catches = winner.get("catches_made", 0)
    
    # Generate a descriptive reason based on what made them MVP
    # If hits is dominant stat, mention eliminations
    # Otherwise use combined stats description
    if hits > 0 and (catches == 0 or hits * 2 > catches * 1.5):
        reason = f"Most eliminations ({hits})"
    else:
        reason = f"MVP with {hits} hits and {catches} catches"
    
    return {
        "player_id": winner["player_id"],
        "name": winner.get("name", "Unknown"),
        "mvp_score": winner["mvp_score"],
        "successful_hits": hits,
        "catches_made": catches,
        "reason": reason
    }


def calculate_mvp_per_game(players: List[Dict], min_games: int = 0) -> Optional[Dict]:
    """
    Calculate MVP using per-game averages for fairness.
    
    Uses the same formula but normalizes by games played, giving
    players who missed games a fair comparison.
    
    Args:
        players: List of player stats
        min_games: Minimum games required for eligibility
        
    Returns:
        MVP player dict with per-game stats
    """
    if not players:
        return None
    
    # Filter by minimum games requirement
    eligible = [p for p in players if p.get("games_played", 0) >= min_games]
    
    if not eligible:
        return None
    
    # Calculate per-game MVP scores
    scored_players = []
    for player in eligible:
        games = player.get("games_played", 1)
        if games == 0:
            games = 1  # Avoid division by zero
        
        hits = player.get("successful_hits", 0)
        catches = player.get("catches_made", 0)
        
        hits_per_game = hits / games
        catches_per_game = catches / games
        mvp_score_per_game = (hits_per_game * 2) + (catches_per_game * 1.5)
        
        scored_players.append({
            **player,
            "mvp_score_per_game": mvp_score_per_game,
            "hits_per_game": hits_per_game,
            "catches_per_game": catches_per_game
        })
    
    # Sort by per-game MVP score descending
    scored_players.sort(key=lambda x: (-x["mvp_score_per_game"], x.get("player_id", "")))
    
    return scored_players[0]


def get_stat_leader(
    players: List[Dict],
    stat_name: str,
    lowest: bool = False
) -> Optional[Dict]:
    """
    Get leader for a specific stat.
    
    Args:
        players: List of player stats
        stat_name: Name of stat to compare (e.g., "successful_hits", "catches_made")
        lowest: If True, lowest value wins (for defense stats like times_hit)
        
    Returns:
        Player with best stat value, or None if no players
    """
    if not players:
        return None
    
    # Filter out players who don't have the stat
    eligible = [p for p in players if stat_name in p]
    
    if not eligible:
        return None
    
    # Sort by stat value (ascending if lowest=True, descending otherwise)
    if lowest:
        eligible.sort(key=lambda x: (x[stat_name], x.get("player_id", "")))
    else:
        eligible.sort(key=lambda x: (-x[stat_name], x.get("player_id", "")))
    
    return eligible[0]


def get_accuracy_leader(
    players: List[Dict],
    min_throws: int = 0
) -> Optional[Dict]:
    """
    Get player with best throw accuracy.
    
    Accuracy = successful_hits / throws_attempted
    
    Args:
        players: List of player stats with successful_hits and throws_attempted
        min_throws: Minimum throws required for eligibility
        
    Returns:
        Player with best accuracy (hits / attempts), or None
    """
    if not players:
        return None
    
    # Filter by minimum throws
    eligible = [
        p for p in players 
        if p.get("throws_attempted", 0) >= min_throws and p.get("throws_attempted", 0) > 0
    ]
    
    if not eligible:
        return None
    
    # Calculate accuracy for each player
    for player in eligible:
        hits = player.get("successful_hits", 0)
        attempts = player.get("throws_attempted", 1)
        player["accuracy"] = hits / attempts if attempts > 0 else 0.0
    
    # Sort by accuracy descending, with player_id as tiebreaker
    eligible.sort(key=lambda x: (-x["accuracy"], x.get("player_id", "")))
    
    return eligible[0]


def get_all_stat_leaders(players: List[Dict]) -> Dict[str, Optional[Dict]]:
    """
    Get leaders for all statistical categories.
    
    Returns leaders for:
    - most_hits: Most successful eliminations
    - most_catches: Most catches made
    - accuracy_leader: Best hit percentage (min 10 throws)
    
    Args:
        players: List of player stats
        
    Returns:
        Dict mapping category names to leader player dicts
    """
    return {
        "most_hits": get_stat_leader(players, "successful_hits"),
        "most_catches": get_stat_leader(players, "catches_made"),
        "accuracy_leader": get_accuracy_leader(players, min_throws=10)
    }


def calculate_season_awards(players: List[Dict]) -> Dict[str, Optional[Dict]]:
    """
    Calculate all season awards.
    
    Computes:
    - mvp: Most Valuable Player (combined performance)
    - most_hits: Most successful eliminations
    - most_catches: Most catches made
    - accuracy_leader: Best throw accuracy (min 10 throws)
    - best_defense: Fewest times eliminated
    
    Args:
        players: List of player stats
        
    Returns:
        Dict with mvp, most_hits, most_catches, accuracy_leader, best_defense
    """
    if not players:
        return {
            "mvp": None,
            "most_hits": None,
            "most_catches": None,
            "accuracy_leader": None,
            "best_defense": None
        }
    
    return {
        "mvp": calculate_mvp(players),
        "most_hits": get_stat_leader(players, "successful_hits"),
        "most_catches": get_stat_leader(players, "catches_made"),
        "accuracy_leader": get_accuracy_leader(players, min_throws=10),
        "best_defense": get_stat_leader(players, "times_hit", lowest=True)
    }


def calculate_statistical_leaders(players: List[Dict]) -> Dict[str, str]:
    """
    Calculate statistical leaders and return simplified format for archiving.
    
    Returns a dict mapping category names to player IDs for easy reference.
    This format is suitable for storing in season archives.
    
    Args:
        players: List of player stats with player_id field
        
    Returns:
        Dict mapping category names to player_id strings
        e.g., {"most_hits": "player-123", "most_catches": "player-456"}
    """
    result = {}
    
    # Most hits (eliminations)
    most_hits = get_stat_leader(players, "successful_hits")
    if most_hits:
        result["most_hits"] = most_hits.get("player_id", "")
    
    # Most catches
    most_catches = get_stat_leader(players, "catches_made")
    if most_catches:
        result["most_catches"] = most_catches.get("player_id", "")
    
    # Best accuracy
    accuracy_leader = get_accuracy_leader(players, min_throws=5)
    if accuracy_leader:
        result["best_accuracy"] = accuracy_leader.get("player_id", "")
    
    return result
