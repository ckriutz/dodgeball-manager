from typing import Dict
from ..models.player import Player
from ..models.team import Team

class StatsService:
    def update_player_stat(self, player: Player, stat: str, increment: int = 1) -> None:
        """
        Increment a specific stat for a player.
        """
        if stat in player.stats:
            player.stats[stat] += increment
        else:
            raise ValueError(f"Invalid stat: {stat}")

    def update_team_record(self, team: Team, is_win: bool) -> None:
        """
        Update team win/loss record.
        """
        if is_win:
            team.wins += 1
        else:
            team.losses += 1

    def get_player_stats(self, player: Player) -> Dict[str, int]:
        """
        Get current stats for a player.
        """
        return player.stats

    def get_team_record(self, team: Team) -> Dict[str, int]:
        """
        Get current record for a team.
        """
        return {
            "wins": team.wins,
            "losses": team.losses
        }
