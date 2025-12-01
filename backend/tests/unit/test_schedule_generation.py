"""
Unit tests for schedule generation logic.

Tests the round-robin scheduling algorithm to ensure:
- All teams play each other
- Correct number of games generated
- No duplicate pairings
- Support for multiple rounds

Test Coverage:
- T085: Round-robin schedule generation
- FR-024: Schedule must pair teams in balanced round-robin format

References:
- spec.md: US4 - Schedule generation requirements
- data-model.md: Schedule and Game entities
"""

import pytest
from typing import List, Tuple

from src.services.schedule_service import (
    generate_round_robin_schedule,
    generate_round_robin_schedule_with_numbers,
    calculate_expected_games
)


class TestRoundRobinSchedule:
    """Test suite for round-robin schedule generation algorithm."""
    
    def test_schedule_with_2_teams(self):
        """Test schedule generation with minimum teams (2)."""
        # Arrange
        teams = ["team-1", "team-2"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert
        assert len(schedule) == 1  # 2 teams = 1 game
        assert schedule[0] == ("team-1", "team-2") or schedule[0] == ("team-2", "team-1")
    
    def test_schedule_with_4_teams(self):
        """Test schedule generation with 4 teams."""
        # Arrange
        teams = ["team-1", "team-2", "team-3", "team-4"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert: 4 teams = C(4,2) = 6 games
        assert len(schedule) == 6
        
        # Verify all pairings are unique
        assert len(schedule) == len(set(schedule))
        
        # Verify each team appears in correct number of games (3 each)
        team_counts = {team: 0 for team in teams}
        for team1, team2 in schedule:
            team_counts[team1] += 1
            team_counts[team2] += 1
        
        assert all(count == 3 for count in team_counts.values())
    
    def test_schedule_with_odd_teams(self):
        """Test schedule generation with odd number of teams (3)."""
        # Arrange
        teams = ["team-1", "team-2", "team-3"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert: 3 teams = C(3,2) = 3 games
        assert len(schedule) == 3
        
        # Verify all pairs exist
        expected_pairs = {
            ("team-1", "team-2"),
            ("team-1", "team-3"),
            ("team-2", "team-3")
        }
        
        # Convert to set (order doesn't matter)
        schedule_set = {
            tuple(sorted([t1, t2])) for t1, t2 in schedule
        }
        expected_set = {
            tuple(sorted([t1, t2])) for t1, t2 in expected_pairs
        }
        
        assert schedule_set == expected_set
    
    def test_schedule_no_self_matchups(self):
        """Test that no team plays against itself."""
        # Arrange
        teams = ["team-1", "team-2", "team-3", "team-4"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert: No self-matchups
        for team1, team2 in schedule:
            assert team1 != team2
    
    def test_schedule_multiple_rounds(self):
        """Test schedule generation with multiple rounds."""
        # Arrange
        teams = ["team-1", "team-2", "team-3"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=3)
        
        # Assert: 3 teams, 3 rounds = 3 games * 3 rounds = 9 games
        assert len(schedule) == 9
        
        # Verify each pairing appears exactly 3 times
        pairing_counts = {}
        for team1, team2 in schedule:
            pair = tuple(sorted([team1, team2]))
            pairing_counts[pair] = pairing_counts.get(pair, 0) + 1
        
        assert all(count == 3 for count in pairing_counts.values())
        assert len(pairing_counts) == 3  # 3 unique pairings
    
    def test_schedule_with_single_team_fails(self):
        """Test that schedule generation fails with only 1 team."""
        # Arrange
        teams = ["team-1"]
        
        # Act & Assert
        with pytest.raises(ValueError, match="at least 2 teams"):
            generate_round_robin_schedule(teams, rounds=1)
    
    def test_schedule_with_zero_rounds_fails(self):
        """Test that schedule generation fails with 0 rounds."""
        # Arrange
        teams = ["team-1", "team-2"]
        
        # Act & Assert
        with pytest.raises(ValueError, match="at least 1 round"):
            generate_round_robin_schedule(teams, rounds=0)
    
    def test_schedule_with_negative_rounds_fails(self):
        """Test that schedule generation fails with negative rounds."""
        # Arrange
        teams = ["team-1", "team-2"]
        
        # Act & Assert
        with pytest.raises(ValueError, match="at least 1 round"):
            generate_round_robin_schedule(teams, rounds=-1)
    
    def test_schedule_game_numbers_sequential(self):
        """Test that games are numbered sequentially starting from 1."""
        # Arrange
        teams = ["team-1", "team-2", "team-3"]
        
        # Act
        schedule = generate_round_robin_schedule_with_numbers(teams, rounds=1)
        
        # Assert
        game_numbers = [game['game_number'] for game in schedule]
        expected_numbers = list(range(1, len(schedule) + 1))
        assert game_numbers == expected_numbers
    
    def test_schedule_maintains_home_away_consistency(self):
        """Test that schedule consistently assigns home/away roles."""
        # Arrange
        teams = ["team-1", "team-2", "team-3", "team-4"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert: Each pairing should be unique (no reverse duplicates)
        seen_pairs = set()
        for team1, team2 in schedule:
            pair = tuple(sorted([team1, team2]))
            assert pair not in seen_pairs, f"Duplicate pairing: {pair}"
            seen_pairs.add(pair)
    
    def test_schedule_with_6_teams(self):
        """Test schedule generation with 6 teams (realistic league size)."""
        # Arrange
        teams = [f"team-{i}" for i in range(1, 7)]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert: 6 teams = C(6,2) = 15 games
        assert len(schedule) == 15
        
        # Verify each team plays exactly 5 games
        team_counts = {team: 0 for team in teams}
        for team1, team2 in schedule:
            team_counts[team1] += 1
            team_counts[team2] += 1
        
        assert all(count == 5 for count in team_counts.values())
    
    def test_schedule_randomization_seed(self):
        """Test that schedule order can be randomized with seed."""
        # Arrange
        teams = ["team-1", "team-2", "team-3", "team-4"]
        
        # Act
        schedule1 = generate_round_robin_schedule(teams, rounds=1, shuffle=True, seed=42)
        schedule2 = generate_round_robin_schedule(teams, rounds=1, shuffle=True, seed=42)
        schedule3 = generate_round_robin_schedule(teams, rounds=1, shuffle=True, seed=99)
        
        # Assert: Same seed produces same order
        assert schedule1 == schedule2
        
        # Different seed likely produces different order (not guaranteed but very likely)
        # At least verify both are valid schedules
        assert len(schedule1) == len(schedule3) == 6
    
    def test_schedule_calculates_expected_games(self):
        """Test helper function to calculate expected game count."""
        # Formula: C(n, 2) * rounds = (n * (n-1) / 2) * rounds
        
        test_cases = [
            (2, 1, 1),    # 2 teams, 1 round = 1 game
            (3, 1, 3),    # 3 teams, 1 round = 3 games
            (4, 1, 6),    # 4 teams, 1 round = 6 games
            (5, 1, 10),   # 5 teams, 1 round = 10 games
            (6, 1, 15),   # 6 teams, 1 round = 15 games
            (4, 2, 12),   # 4 teams, 2 rounds = 12 games
            (3, 3, 9),    # 3 teams, 3 rounds = 9 games
        ]
        
        for team_count, rounds, expected_games in test_cases:
            actual = calculate_expected_games(team_count, rounds)
            assert actual == expected_games, \
                f"Failed for {team_count} teams, {rounds} rounds: expected {expected_games}, got {actual}"


class TestScheduleEdgeCases:
    """Test edge cases and boundary conditions for schedule generation."""
    
    def test_schedule_with_empty_team_list(self):
        """Test that schedule generation fails with empty team list."""
        # Arrange
        teams = []
        
        # Act & Assert
        with pytest.raises(ValueError, match="at least 2 teams"):
            generate_round_robin_schedule(teams, rounds=1)
    
    def test_schedule_preserves_team_ids(self):
        """Test that schedule preserves exact team ID strings."""
        # Arrange
        teams = ["550e8400-e29b-41d4-a716-446655440000", 
                 "6ba7b810-9dad-11d1-80b4-00c04fd430c8"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert
        all_teams_in_schedule = set()
        for team1, team2 in schedule:
            all_teams_in_schedule.add(team1)
            all_teams_in_schedule.add(team2)
        
        assert all_teams_in_schedule == set(teams)
    
    def test_schedule_with_large_number_of_teams(self):
        """Test schedule generation with many teams (10)."""
        # Arrange
        teams = [f"team-{i}" for i in range(1, 11)]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=1)
        
        # Assert: 10 teams = C(10,2) = 45 games
        assert len(schedule) == 45
    
    def test_schedule_with_many_rounds(self):
        """Test schedule generation with many rounds."""
        # Arrange
        teams = ["team-1", "team-2", "team-3"]
        
        # Act
        schedule = generate_round_robin_schedule(teams, rounds=10)
        
        # Assert: 3 games per round * 10 rounds = 30 games
        assert len(schedule) == 30
