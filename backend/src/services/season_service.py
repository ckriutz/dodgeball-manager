"""
Season service for managing season lifecycle, archiving, and transitions.

This module handles:
- Season lifecycle management (start, complete, archive)
- Creating season archives with historical data
- Managing transitions between seasons
- Coordinating with other services (standings, awards, age progression)

References:
- data-model.md: Season and SeasonArchive entities
- FR-030: Season history storage and retrieval
- FR-010: Age progression at season end
- T102: Implement SeasonService
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..models.league import League, Season, SeasonArchive, SeasonStatus
from ..storage.memory_storage import MemoryStorage
from .standings_service import calculate_standings
from .awards_service import calculate_mvp, calculate_statistical_leaders
from .age_service import apply_bulk_age_progression, preview_age_progression


class SeasonService:
    """
    Service for managing season lifecycle, archiving, and transitions.
    
    This service orchestrates season management, including:
    - Starting new seasons
    - Finishing seasons and calculating final results
    - Creating immutable season archives
    - Managing the transition between seasons
    - Coordinating age progression
    """
    
    def __init__(self, storage: Optional[MemoryStorage] = None):
        """
        Initialize SeasonService.
        
        Args:
            storage: Optional storage instance (defaults to singleton)
        """
        self.storage = storage or MemoryStorage()
    
    def get_current_season(self, league_id: str) -> Optional[Season]:
        """
        Get the current season for a league.
        
        Args:
            league_id: League UUID
            
        Returns:
            Current Season or None if league not found
        """
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return None
        
        league = League(**league_data)
        return league.current_season
    
    def get_season_history(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of all completed seasons for a league.
        
        Args:
            league_id: League UUID
            
        Returns:
            List of season archive dicts ordered by season_number
        """
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return []
        
        league = League(**league_data)
        
        # Convert archives to dicts with all relevant info
        history = []
        for archive in league.season_archives:
            history.append({
                "season_number": archive.season_number,
                "champion": {
                    "team_id": archive.champion_team_id,
                    "team_name": self._get_team_name(archive.champion_team_id)
                },
                "mvp": self._format_mvp_info(archive.mvp_player_id),
                "final_standings": archive.final_standings,
                "team_rosters": archive.team_rosters,
                "player_stats": [
                    {"player_id": pid, **stats}
                    for pid, stats in archive.player_stats.items()
                ],
                "statistical_leaders": archive.statistical_leaders,
                "completed_at": archive.completed_at.isoformat() if archive.completed_at else None
            })
        
        return sorted(history, key=lambda x: x["season_number"])
    
    def can_finish_season(self, league_id: str) -> tuple:
        """
        Check if a season can be finished.
        
        Args:
            league_id: League UUID
            
        Returns:
            Tuple of (can_finish: bool, reason: str)
        """
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return False, "League not found"
        
        league = League(**league_data)
        
        # Check if there's a schedule
        if not league.schedule:
            return False, "No schedule exists. Create a schedule first."
        
        # Check if all games are complete
        if not league.is_season_complete():
            remaining = league.get_remaining_games_count()
            return False, f"Season has {remaining} incomplete games. Complete all scheduled games first."
        
        # Check if season is in progress
        if league.current_season.status != SeasonStatus.IN_PROGRESS:
            return False, f"Season is not in progress (status: {league.current_season.status})"
        
        return True, "Season can be finished"
    
    def finish_season(self, league_id: str) -> Dict[str, Any]:
        """
        Finish the current season, calculate results, and create archive.
        
        This operation:
        1. Validates all games are complete
        2. Calculates final standings
        3. Determines champion and MVP
        4. Creates immutable season archive
        5. Marks season as completed
        
        Args:
            league_id: League UUID
            
        Returns:
            Dict with season_number, final_standings, champion, mvp, statistical_leaders
            
        Raises:
            ValueError: If season cannot be finished
        """
        can_finish, reason = self.can_finish_season(league_id)
        if not can_finish:
            raise ValueError(reason)
        
        league_data = self.storage.get_league(league_id)
        league = League(**league_data)
        
        # Calculate final standings
        teams_data = self._get_teams_for_standings(league_id)
        final_standings = calculate_standings(teams_data)
        
        # Determine champion (team with best standing)
        champion = final_standings[0] if final_standings else None
        champion_team_id = champion["team_id"] if champion else None
        
        # Calculate MVP and statistical leaders
        player_stats = self._collect_season_player_stats(league_id)
        mvp = calculate_mvp(player_stats)
        mvp_player_id = mvp["player_id"] if mvp else None
        
        statistical_leaders = calculate_statistical_leaders(player_stats)
        
        # Collect team rosters
        team_rosters = self._collect_team_rosters(league_id)
        
        # Format player stats for archive
        player_stats_dict = {
            p["player_id"]: {
                "successful_hits": p.get("successful_hits", 0),
                "catches_made": p.get("catches_made", 0),
                "throws_attempted": p.get("throws_attempted", 0),
                "times_hit": p.get("times_hit", 0),
                "games_played": p.get("games_played", 0)
            }
            for p in player_stats
        }
        
        # Mark season as completed
        league.current_season.complete_season()
        
        # Create archive
        archive = league.archive_season(
            champion_team_id=champion_team_id or "",
            mvp_player_id=mvp_player_id,
            final_standings=final_standings,
            team_rosters=team_rosters,
            player_stats=player_stats_dict,
            statistical_leaders=statistical_leaders
        )
        
        # Save league
        self.storage.update_league(league_id, league.model_dump())
        
        return {
            "season_number": archive.season_number,
            "final_standings": final_standings,
            "champion": {
                "team_id": champion_team_id,
                "team_name": champion["team_name"] if champion else "Unknown",
                "wins": champion["wins"] if champion else 0,
                "losses": champion["losses"] if champion else 0
            } if champion_team_id else None,
            "mvp": mvp,
            "statistical_leaders": statistical_leaders
        }
    
    def can_start_season(self, league_id: str) -> tuple:
        """
        Check if a new season can be started.
        
        Args:
            league_id: League UUID
            
        Returns:
            Tuple of (can_start: bool, reason: str)
        """
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return False, "League not found"
        
        league = League(**league_data)
        
        # For the first season, it should be NOT_STARTED
        if league.current_season.season_number == 1:
            if league.current_season.status == SeasonStatus.NOT_STARTED:
                return True, "First season can be started"
            elif league.current_season.status == SeasonStatus.IN_PROGRESS:
                return False, "Season is already in progress. Must finish current season first."
        
        # For subsequent seasons, previous must be completed
        if league.current_season.status != SeasonStatus.COMPLETED:
            return False, f"Must finish current season first (status: {league.current_season.status})"
        
        return True, "New season can be started"
    
    def start_new_season(self, league_id: str, apply_age_progression: bool = True) -> Dict[str, Any]:
        """
        Start a new season with fresh schedule and reset team records.
        
        This operation:
        1. Validates previous season is complete
        2. Applies age progression to all players (optional)
        3. Resets team win/loss records
        4. Creates new season with incremented number
        
        Args:
            league_id: League UUID
            apply_age_progression: Whether to age players (default True)
            
        Returns:
            Dict with season_number and age_progression_results
            
        Raises:
            ValueError: If new season cannot be started
        """
        can_start, reason = self.can_start_season(league_id)
        if not can_start:
            raise ValueError(reason)
        
        league_data = self.storage.get_league(league_id)
        league = League(**league_data)
        
        age_results = []
        
        # Apply age progression if requested and not first season start
        if apply_age_progression and league.current_season.status == SeasonStatus.COMPLETED:
            age_results = self._apply_league_age_progression(league_id)
        
        # Reset team records
        self._reset_team_records(league_id)
        
        # Start new season (or the first season)
        if league.current_season.status == SeasonStatus.NOT_STARTED:
            # First season - just mark it as started
            league.current_season.start_season()
            new_season_number = 1
        else:
            # Subsequent season - create new one
            league.start_new_season()
            league.current_season.start_season()
            new_season_number = league.current_season.season_number
        
        # Save league
        self.storage.update_league(league_id, league.model_dump())
        
        return {
            "season_number": new_season_number,
            "status": "in_progress",
            "age_progression_results": age_results
        }
    
    def get_age_preview(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Preview age progression changes for all players in the league.
        
        Args:
            league_id: League UUID
            
        Returns:
            List of preview dicts showing age changes and skill impacts
        """
        players = self._get_all_players_for_league(league_id)
        
        # Format for preview function
        player_dicts = [
            {
                "player_id": p.get("id", p.get("player_id", "unknown")),
                "name": p.get("name", "Unknown"),
                "age": p.get("age", 18),
                "skills": p.get("skills", {})
            }
            for p in players
        ]
        
        return preview_age_progression(player_dicts)
    
    def _get_teams_for_standings(self, league_id: str) -> List[Dict[str, Any]]:
        """Get team data formatted for standings calculation."""
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return []
        
        league = League(**league_data)
        teams = []
        
        for team_id in league.team_ids:
            team_data = self.storage.get_team(team_id)
            if team_data:
                teams.append({
                    "team_id": team_id,
                    "team_name": team_data.get("name", "Unknown"),
                    "wins": team_data.get("wins", 0),
                    "losses": team_data.get("losses", 0)
                })
        
        return teams
    
    def _collect_season_player_stats(self, league_id: str) -> List[Dict[str, Any]]:
        """Collect all player statistics for the season."""
        players = self._get_all_players_for_league(league_id)
        
        return [
            {
                "player_id": p.get("id", p.get("player_id", "unknown")),
                "name": p.get("name", "Unknown"),
                "games_played": p.get("stats", {}).get("games_played", 0),
                "successful_hits": p.get("stats", {}).get("successful_hits", 0),
                "catches_made": p.get("stats", {}).get("catches_made", 0),
                "throws_attempted": p.get("stats", {}).get("throws_attempted", 0),
                "times_hit": p.get("stats", {}).get("times_hit", 0)
            }
            for p in players
        ]
    
    def _collect_team_rosters(self, league_id: str) -> Dict[str, List[str]]:
        """Collect current rosters for all teams."""
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return {}
        
        league = League(**league_data)
        rosters = {}
        
        for team_id in league.team_ids:
            team_data = self.storage.get_team(team_id)
            if team_data:
                rosters[team_id] = team_data.get("player_ids", [])
        
        return rosters
    
    def _get_all_players_for_league(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all players in a league."""
        players = self.storage.list_players()
        return [p for p in players if p.get("league_id") == league_id]
    
    def _get_team_name(self, team_id: str) -> str:
        """Get team name by ID."""
        team_data = self.storage.get_team(team_id)
        return team_data.get("name", "Unknown") if team_data else "Unknown"
    
    def _format_mvp_info(self, player_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Format MVP information for display."""
        if not player_id:
            return None
        
        player_data = self.storage.get_player(player_id)
        if not player_data:
            return {"player_id": player_id, "name": "Unknown"}
        
        return {
            "player_id": player_id,
            "name": player_data.get("name", "Unknown")
        }
    
    def _apply_league_age_progression(self, league_id: str) -> List[Dict[str, Any]]:
        """Apply age progression to all players in the league."""
        players = self._get_all_players_for_league(league_id)
        
        results = []
        for player_data in players:
            player_id = player_data.get("id", player_data.get("player_id"))
            old_age = player_data.get("age", 18)
            old_skills = dict(player_data.get("skills", {}))
            
            # Apply age progression
            from .age_service import apply_age_progression as age_player
            updated_data = age_player(player_data)
            
            # Track changes
            skill_changes = {}
            new_skills = updated_data.get("skills", {})
            for skill_name, old_value in old_skills.items():
                new_value = new_skills.get(skill_name, old_value)
                if new_value != old_value:
                    skill_changes[skill_name] = {
                        "old": old_value,
                        "new": new_value
                    }
            
            # Update player in storage
            self.storage.update_player(player_id, updated_data)
            
            results.append({
                "player_id": player_id,
                "name": player_data.get("name", "Unknown"),
                "old_age": old_age,
                "new_age": updated_data["age"],
                "skill_changes": skill_changes
            })
        
        return results
    
    def _reset_team_records(self, league_id: str) -> None:
        """Reset win/loss records for all teams in the league."""
        league_data = self.storage.get_league(league_id)
        if not league_data:
            return
        
        league = League(**league_data)
        
        for team_id in league.team_ids:
            team_data = self.storage.get_team(team_id)
            if team_data:
                team_data["wins"] = 0
                team_data["losses"] = 0
                self.storage.update_team(team_id, team_data)


def get_season_status(league_id: str, storage: Optional[MemoryStorage] = None) -> Dict[str, Any]:
    """
    Get current season status for a league.
    
    Args:
        league_id: League UUID
        storage: Optional storage instance
        
    Returns:
        Dict with season_number, status, schedule_info
    """
    storage = storage or MemoryStorage()
    league_data = storage.get_league(league_id)
    
    if not league_data:
        return {"error": "League not found"}
    
    league = League(**league_data)
    
    return {
        "season_number": league.current_season.season_number,
        "status": league.current_season.status.value,
        "started_at": league.current_season.started_at.isoformat() if league.current_season.started_at else None,
        "completed_at": league.current_season.completed_at.isoformat() if league.current_season.completed_at else None,
        "schedule": {
            "total_games": len(league.schedule),
            "completed_games": league.get_completed_games_count(),
            "remaining_games": league.get_remaining_games_count(),
            "is_complete": league.is_season_complete()
        }
    }
