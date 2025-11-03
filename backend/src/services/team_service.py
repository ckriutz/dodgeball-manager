"""
TeamService for managing team operations.

This service handles team creation, roster management, budget tracking,
and starter designation. It coordinates with PlayerService and LeagueService
to ensure proper team-player relationships.

References:
- FR-012: Team rosters must have 8-12 players
- FR-013: Exactly 5 starters must be designated
- FR-014: Cannot add player if value exceeds budget
- FR-014a: Can add player if value equals budget
"""

from typing import List, Optional

from ..models.team import Team, TeamCreate
from ..models.player import Player
from ..storage.memory_storage import MemoryStorage
from .player_service import PlayerService


class TeamService:
    """Service for team-related operations."""

    def __init__(
        self,
        storage: Optional[MemoryStorage] = None,
        player_service: Optional[PlayerService] = None
    ):
        """
        Initialize TeamService.
        
        Args:
            storage: Optional storage instance (defaults to singleton)
            player_service: Optional PlayerService instance
        """
        self.storage = storage or MemoryStorage()
        self.player_service = player_service or PlayerService(storage=self.storage)

    def create_team(self, team_create: 'TeamCreate') -> Team:
        """
        Create a new team with $15,000 budget.
        
        Args:
            team_create: Team creation data
            
        Returns:
            New Team instance
            
        Raises:
            ValueError: If team data is invalid
        """
        # Verify league exists
        league = self.storage.get_league(team_create.league_id)
        if league is None:
            raise ValueError(f"League {team_create.league_id} not found")

        # Create team
        team = team_create.to_team()

        # Store team and get the actual ID assigned by storage
        team_id = self.storage.create_team(team.model_dump())
        
        # Update team with correct ID from storage
        team_dict = team.model_dump()
        team_dict['id'] = team_id
        team = Team(**team_dict)

        # Add team to league
        if team_id not in league['team_ids']:
            league['team_ids'].append(team_id)
            self.storage.update_league(team_create.league_id, league)

        return team

    def get_team(self, team_id: str) -> Optional[Team]:
        """
        Get a team by ID.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Team instance or None if not found
        """
        team_data = self.storage.get_team(team_id)
        if team_data is None:
            return None

        return Team(**team_data)

    def get_all_teams(self) -> List[Team]:
        """
        Get all teams in the system.
        
        Returns:
            List of all Team instances
        """
        all_teams = self.storage.list_teams()
        return [Team(**team_data) for team_data in all_teams]

    def get_teams_by_league(self, league_id: str) -> List[Team]:
        """
        Get all teams in a specific league.
        
        Args:
            league_id: League UUID
            
        Returns:
            List of Team instances in the league
        """
        all_teams = self.get_all_teams()
        return [team for team in all_teams if team.league_id == league_id]

    def update_team(self, team_id: str, team: Team) -> Team:
        """
        Update a team in storage.
        
        Args:
            team_id: Team UUID
            team: Updated Team instance
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team not found
        """
        existing = self.get_team(team_id)
        if existing is None:
            raise ValueError(f"Team {team_id} not found")

        self.storage.update_team(team_id, team.model_dump())
        return team

    def delete_team(self, team_id: str) -> bool:
        """
        Delete a team from the system.
        
        Also removes team from league and releases all players.
        
        Args:
            team_id: Team UUID
            
        Returns:
            True if deleted, False if not found
        """
        team = self.get_team(team_id)
        if team is None:
            return False

        # Release all players on the roster
        for player_id in team.player_ids:
            player = self.player_service.get_player(player_id)
            if player:
                self.player_service.release_player_from_team(player_id)

        # Remove team from league
        league = self.storage.get_league(team.league_id)
        if league and team_id in league['team_ids']:
            league['team_ids'].remove(team_id)
            self.storage.update_league(team.league_id, league)

        return self.storage.delete_team(team_id)

    def add_player_to_roster(self, team_id: str, player_id: str) -> Team:
        """
        Add a player to team roster (FR-014, FR-014a).
        
        Validates budget constraints and roster size limits.
        Updates player's team assignment.
        
        Args:
            team_id: Team UUID
            player_id: Player UUID
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team/player not found, budget exceeded,
                       roster full, or player already on a team
        """
        # Get team
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        # Get player
        player = self.player_service.get_player(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found")

        # Check if player is already on a team
        if not player.is_free_agent():
            if player.team_id == team_id:
                raise ValueError(f"Player {player_id} is already on this team")
            else:
                raise ValueError(
                    f"Player {player_id} is already on team {player.team_id}. "
                    "Players must be released before joining another team."
                )

        # Check if roster has room
        if not team.can_add_player():
            raise ValueError(
                f"Team {team_id} roster is full (maximum 12 players)"
            )

        # Check if team can afford player (FR-014)
        if not team.can_afford_player(player.value):
            raise ValueError(
                f"Insufficient budget: Player costs ${player.value}, "
                f"but team only has ${team.budget} remaining. "
                "Cannot add player if cost exceeds budget (FR-014)."
            )

        # Add player to roster (this updates budget)
        team.add_player_to_roster(player_id, player.value)

        # Update player's team assignment
        self.player_service.assign_player_to_team(player_id, team_id)

        # Update team in storage
        self.storage.update_team(team_id, team.model_dump())

        return team

    def remove_player_from_roster(self, team_id: str, player_id: str) -> Team:
        """
        Remove a player from team roster.
        
        Refunds player value to budget and releases player to free agency.
        
        Args:
            team_id: Team UUID
            player_id: Player UUID
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team/player not found, roster at minimum,
                       or player not on team
        """
        # Get team
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        # Get player
        player = self.player_service.get_player(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found")

        # Check if player is on this team
        if player.team_id != team_id:
            raise ValueError(f"Player {player_id} is not on team {team_id}")

        # Check if removal would go below minimum roster size
        if not team.can_remove_player():
            raise ValueError(
                f"Cannot remove player: Team {team_id} roster is at minimum size (8 players). "
                "Roster must have 8-12 players (FR-012)."
            )

        # Remove player from roster (this refunds budget)
        team.remove_player_from_roster(player_id, player.value)

        # Release player to free agency
        self.player_service.release_player_from_team(player_id)

        # Update team in storage
        self.storage.update_team(team_id, team.model_dump())

        return team

    def set_starters(self, team_id: str, starter_ids: List[str]) -> Team:
        """
        Designate starting lineup for team (FR-013).
        
        Allows setting 0-5 starters. Validates all starters are on roster.
        Note: Exactly 5 starters are required for game simulation, but teams
        can have partial starter lists during roster building.
        
        Args:
            team_id: Team UUID
            starter_ids: List of up to 5 player IDs
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team not found, duplicates exist, or starters not on roster
        """
        # Get team
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        # Validate and set starters (Team model handles validation)
        team.set_starters(starter_ids)

        # Update is_starter flag for all players on the team
        for player_id in team.player_ids:
            player = self.player_service.get_player(player_id)
            if player:
                should_be_starter = player_id in starter_ids
                self.player_service.set_starter_status(player_id, should_be_starter)

        # Update team in storage
        self.storage.update_team(team_id, team.model_dump())

        return team

    def clear_starters(self, team_id: str) -> Team:
        """
        Clear all starters for a team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team not found
        """
        # Get team
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        # Clear starters
        team.clear_starters()

        # Update is_starter flag for all players on the team
        for player_id in team.player_ids:
            player = self.player_service.get_player(player_id)
            if player:
                self.player_service.set_starter_status(player_id, False)

        # Update team in storage
        self.storage.update_team(team_id, team.model_dump())

        return team

    def get_team_roster(self, team_id: str) -> List[Player]:
        """
        Get all players on a team's roster.
        
        Args:
            team_id: Team UUID
            
        Returns:
            List of Player instances on the roster
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        roster = []
        for player_id in team.player_ids:
            player = self.player_service.get_player(player_id)
            if player:
                roster.append(player)

        return roster

    def get_team_starters(self, team_id: str) -> List[Player]:
        """
        Get all starting players for a team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            List of Player instances who are starters
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        starters = []
        for player_id in team.starter_ids:
            player = self.player_service.get_player(player_id)
            if player:
                starters.append(player)

        return starters

    def get_team_bench(self, team_id: str) -> List[Player]:
        """
        Get all bench players for a team (non-starters).
        
        Args:
            team_id: Team UUID
            
        Returns:
            List of Player instances who are on roster but not starters
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        bench_ids = team.get_bench_player_ids()
        bench = []
        for player_id in bench_ids:
            player = self.player_service.get_player(player_id)
            if player:
                bench.append(player)

        return bench

    def calculate_roster_value(self, team_id: str) -> int:
        """
        Calculate total value of all players on roster.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Total dollar value of roster
            
        Raises:
            ValueError: If team not found
        """
        roster = self.get_team_roster(team_id)
        return sum(player.value for player in roster)

    def validate_budget_integrity(self, team_id: str) -> bool:
        """
        Verify that roster value + remaining budget equals initial budget.
        
        Formula: roster_value + remaining_budget = 15,000
        
        Args:
            team_id: Team UUID
            
        Returns:
            True if budget integrity is maintained
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")
        
        roster_value = sum(
            player.value
            for player_id in team.player_ids
            if (player := self.player_service.get_player(player_id))
        )
        
        return roster_value + team.budget == 15000

    def is_team_ready_for_game(self, team_id: str) -> bool:
        """
        Check if team is ready to play a game.
        
        Requirements:
        - Roster size 8-12 players (FR-012)
        - Exactly 5 starters designated (FR-013)
        
        Args:
            team_id: Team UUID
            
        Returns:
            True if team meets all requirements
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        return team.is_roster_valid_size() and team.is_starters_valid_count()

    def record_win(self, team_id: str) -> Team:
        """
        Record a win for the team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        team.record_win()
        self.storage.update_team(team_id, team.model_dump())

        return team

    def record_loss(self, team_id: str) -> Team:
        """
        Record a loss for the team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        team.record_loss()
        self.storage.update_team(team_id, team.model_dump())

        return team

    def add_award(self, team_id: str, award: str) -> Team:
        """
        Add an award/achievement to the team.
        
        Args:
            team_id: Team UUID
            award: Award description
            
        Returns:
            Updated Team instance
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        team.add_award(award)
        self.storage.update_team(team_id, team.model_dump())

        return team

    def get_team_stats(self, team_id: str) -> dict:
        """
        Get comprehensive statistics for a team.
        
        Args:
            team_id: Team UUID
            
        Returns:
            Dictionary with team statistics
            
        Raises:
            ValueError: If team not found
        """
        team = self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        roster_value = self.calculate_roster_value(team_id)

        return {
            'team_id': team_id,
            'name': team.name,
            'wins': team.wins,
            'losses': team.losses,
            'games_played': team.get_games_played(),
            'win_percentage': team.get_win_percentage(),
            'roster_size': team.get_roster_size(),
            'roster_value': roster_value,
            'budget_remaining': team.budget,
            'budget_spent': roster_value,
            'starters_count': len(team.starter_ids),
            'ready_for_game': self.is_team_ready_for_game(team_id)
        }

    def count_teams(self) -> int:
        """
        Get total number of teams in the system.
        
        Returns:
            Total team count
        """
        return len(self.storage.list_teams())

    def count_teams_in_league(self, league_id: str) -> int:
        """
        Get number of teams in a specific league.
        
        Args:
            league_id: League UUID
            
        Returns:
            Team count in the league
        """
        return len(self.get_teams_by_league(league_id))
