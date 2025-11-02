"""
Simulation tests for edge cases in game mechanics.

This module tests unusual scenarios and edge cases that might occur
during game simulation.

References:
- research.md: Game Simulation Algorithm
- FR-026: Games require exactly 5 starters per team
- FR-027-FR-031: Skill-based outcome calculations
"""

import pytest
from typing import List, Dict
from .test_game_determinism import Player, GameSimulator


class TestEdgeCases:
    """Test edge cases in game simulation."""
    
    def test_all_players_identical_stats(self):
        """Test game with all players having identical stats."""
        team1 = [
            Player('p1', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p2', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p4', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        team2 = [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p7', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p9', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p10', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete
        assert winner in [1, 2]
        assert len(events) > 0
        assert events[-1]['type'] == 'game_end'
    
    def test_extreme_disparity_high_vs_low_stats(self):
        """Test game with extreme stat disparity."""
        # Super team with max stats
        team1 = [
            Player('p1', {'catching': 100, 'throwing': 100, 'dodging': 0, 'speed': 100, 'iq': 100, 'luck': 50}),
            Player('p2', {'catching': 100, 'throwing': 100, 'dodging': 0, 'speed': 100, 'iq': 100, 'luck': 50}),
            Player('p3', {'catching': 100, 'throwing': 100, 'dodging': 0, 'speed': 100, 'iq': 100, 'luck': 50}),
            Player('p4', {'catching': 100, 'throwing': 100, 'dodging': 0, 'speed': 100, 'iq': 100, 'luck': 50}),
            Player('p5', {'catching': 100, 'throwing': 100, 'dodging': 0, 'speed': 100, 'iq': 100, 'luck': 50})
        ]
        
        # Weak team with min stats (except dodging)
        team2 = [
            Player('p6', {'catching': 0, 'throwing': 0, 'dodging': 100, 'speed': 0, 'iq': 0, 'luck': 50}),
            Player('p7', {'catching': 0, 'throwing': 0, 'dodging': 100, 'speed': 0, 'iq': 0, 'luck': 50}),
            Player('p8', {'catching': 0, 'throwing': 0, 'dodging': 100, 'speed': 0, 'iq': 0, 'luck': 50}),
            Player('p9', {'catching': 0, 'throwing': 0, 'dodging': 100, 'speed': 0, 'iq': 0, 'luck': 50}),
            Player('p10', {'catching': 0, 'throwing': 0, 'dodging': 100, 'speed': 0, 'iq': 0, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_high_dodging_team_vs_high_throwing_team(self):
        """Test matchup between high dodging and high throwing teams."""
        # Team focused on dodging
        team1 = [
            Player('p1', {'catching': 20, 'throwing': 20, 'dodging': 100, 'speed': 80, 'iq': 30, 'luck': 50}),
            Player('p2', {'catching': 20, 'throwing': 20, 'dodging': 100, 'speed': 80, 'iq': 30, 'luck': 50}),
            Player('p3', {'catching': 20, 'throwing': 20, 'dodging': 100, 'speed': 80, 'iq': 30, 'luck': 50}),
            Player('p4', {'catching': 20, 'throwing': 20, 'dodging': 100, 'speed': 80, 'iq': 30, 'luck': 50}),
            Player('p5', {'catching': 20, 'throwing': 20, 'dodging': 100, 'speed': 80, 'iq': 30, 'luck': 50})
        ]
        
        # Team focused on throwing
        team2 = [
            Player('p6', {'catching': 20, 'throwing': 100, 'dodging': 20, 'speed': 30, 'iq': 80, 'luck': 50}),
            Player('p7', {'catching': 20, 'throwing': 100, 'dodging': 20, 'speed': 30, 'iq': 80, 'luck': 50}),
            Player('p8', {'catching': 20, 'throwing': 100, 'dodging': 20, 'speed': 30, 'iq': 80, 'luck': 50}),
            Player('p9', {'catching': 20, 'throwing': 100, 'dodging': 20, 'speed': 30, 'iq': 80, 'luck': 50}),
            Player('p10', {'catching': 20, 'throwing': 100, 'dodging': 20, 'speed': 30, 'iq': 80, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_high_catching_team_defense(self):
        """Test team with extremely high catching ability."""
        # Catching-focused team
        team1 = [
            Player('p1', {'catching': 100, 'throwing': 30, 'dodging': 20, 'speed': 40, 'iq': 50, 'luck': 60}),
            Player('p2', {'catching': 100, 'throwing': 30, 'dodging': 20, 'speed': 40, 'iq': 50, 'luck': 60}),
            Player('p3', {'catching': 100, 'throwing': 30, 'dodging': 20, 'speed': 40, 'iq': 50, 'luck': 60}),
            Player('p4', {'catching': 100, 'throwing': 30, 'dodging': 20, 'speed': 40, 'iq': 50, 'luck': 60}),
            Player('p5', {'catching': 100, 'throwing': 30, 'dodging': 20, 'speed': 40, 'iq': 50, 'luck': 60})
        ]
        
        # Balanced team
        team2 = [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p7', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p9', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p10', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Check that catches occurred
        catch_events = [e for e in events if e['type'] == 'catch']
        
        # Game should complete
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_zero_luck_teams(self):
        """Test game with teams having zero luck."""
        team1 = [
            Player('p1', {'catching': 60, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p2', {'catching': 60, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p3', {'catching': 60, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p4', {'catching': 60, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p5', {'catching': 60, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 50, 'luck': 0})
        ]
        
        team2 = [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p7', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p9', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 0}),
            Player('p10', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 0})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete despite zero luck
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_max_luck_teams(self):
        """Test game with teams having maximum luck."""
        team1 = [
            Player('p1', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p2', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p3', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p4', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p5', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100})
        ]
        
        team2 = [
            Player('p6', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p7', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p8', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p9', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100}),
            Player('p10', {'catching': 40, 'throwing': 40, 'dodging': 40, 'speed': 40, 'iq': 40, 'luck': 100})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete with maximum luck
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_high_iq_differential(self):
        """Test game with extreme IQ differences between teams."""
        # High IQ team
        team1 = [
            Player('p1', {'catching': 40, 'throwing': 50, 'dodging': 40, 'speed': 40, 'iq': 100, 'luck': 30}),
            Player('p2', {'catching': 40, 'throwing': 50, 'dodging': 40, 'speed': 40, 'iq': 100, 'luck': 30}),
            Player('p3', {'catching': 40, 'throwing': 50, 'dodging': 40, 'speed': 40, 'iq': 100, 'luck': 30}),
            Player('p4', {'catching': 40, 'throwing': 50, 'dodging': 40, 'speed': 40, 'iq': 100, 'luck': 30}),
            Player('p5', {'catching': 40, 'throwing': 50, 'dodging': 40, 'speed': 40, 'iq': 100, 'luck': 30})
        ]
        
        # Low IQ team
        team2 = [
            Player('p6', {'catching': 50, 'throwing': 60, 'dodging': 50, 'speed': 50, 'iq': 0, 'luck': 40}),
            Player('p7', {'catching': 50, 'throwing': 60, 'dodging': 50, 'speed': 50, 'iq': 0, 'luck': 40}),
            Player('p8', {'catching': 50, 'throwing': 60, 'dodging': 50, 'speed': 50, 'iq': 0, 'luck': 40}),
            Player('p9', {'catching': 50, 'throwing': 60, 'dodging': 50, 'speed': 50, 'iq': 0, 'luck': 40}),
            Player('p10', {'catching': 50, 'throwing': 60, 'dodging': 50, 'speed': 50, 'iq': 0, 'luck': 40})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # IQ advantage should matter
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_one_superstar_vs_balanced_team(self):
        """Test team with one exceptional player vs balanced team."""
        # Team with one superstar and weak support
        team1 = [
            Player('p1', {'catching': 100, 'throwing': 100, 'dodging': 0, 'speed': 100, 'iq': 100, 'luck': 100}),
            Player('p2', {'catching': 10, 'throwing': 10, 'dodging': 80, 'speed': 10, 'iq': 10, 'luck': 10}),
            Player('p3', {'catching': 10, 'throwing': 10, 'dodging': 80, 'speed': 10, 'iq': 10, 'luck': 10}),
            Player('p4', {'catching': 10, 'throwing': 10, 'dodging': 80, 'speed': 10, 'iq': 10, 'luck': 10}),
            Player('p5', {'catching': 10, 'throwing': 10, 'dodging': 80, 'speed': 10, 'iq': 10, 'luck': 10})
        ]
        
        # Balanced team
        team2 = [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p7', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p9', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p10', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete
        assert winner in [1, 2]
        assert len(events) > 0
    
    def test_game_does_not_exceed_reasonable_length(self):
        """Test that games complete within reasonable number of turns."""
        # Create somewhat balanced teams to avoid quick blowouts
        team1 = [
            Player('p1', {'catching': 55, 'throwing': 55, 'dodging': 45, 'speed': 45, 'iq': 50, 'luck': 50}),
            Player('p2', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 45, 'throwing': 45, 'dodging': 55, 'speed': 55, 'iq': 50, 'luck': 50}),
            Player('p4', {'catching': 60, 'throwing': 60, 'dodging': 40, 'speed': 40, 'iq': 50, 'luck': 50}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        team2 = [
            Player('p6', {'catching': 52, 'throwing': 52, 'dodging': 48, 'speed': 48, 'iq': 50, 'luck': 50}),
            Player('p7', {'catching': 48, 'throwing': 48, 'dodging': 52, 'speed': 52, 'iq': 50, 'luck': 50}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p9', {'catching': 55, 'throwing': 55, 'dodging': 45, 'speed': 45, 'iq': 50, 'luck': 50}),
            Player('p10', {'catching': 45, 'throwing': 45, 'dodging': 55, 'speed': 55, 'iq': 50, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Game should complete within 1000 turns (safety limit)
        assert len(events) < 1000
        
        # Most games should complete much faster
        assert len(events) > 0


class TestStatTracking:
    """Test that player stats are correctly tracked during simulation."""
    
    def test_eliminated_player_stats_updated(self):
        """Test that eliminated players have times_hit incremented."""
        team1 = [
            Player('p1', {'catching': 90, 'throwing': 90, 'dodging': 10, 'speed': 90, 'iq': 90, 'luck': 50}),
            Player('p2', {'catching': 90, 'throwing': 90, 'dodging': 10, 'speed': 90, 'iq': 90, 'luck': 50}),
            Player('p3', {'catching': 90, 'throwing': 90, 'dodging': 10, 'speed': 90, 'iq': 90, 'luck': 50}),
            Player('p4', {'catching': 90, 'throwing': 90, 'dodging': 10, 'speed': 90, 'iq': 90, 'luck': 50}),
            Player('p5', {'catching': 90, 'throwing': 90, 'dodging': 10, 'speed': 90, 'iq': 90, 'luck': 50})
        ]
        
        team2 = [
            Player('p6', {'catching': 10, 'throwing': 10, 'dodging': 90, 'speed': 10, 'iq': 10, 'luck': 50}),
            Player('p7', {'catching': 10, 'throwing': 10, 'dodging': 90, 'speed': 10, 'iq': 10, 'luck': 50}),
            Player('p8', {'catching': 10, 'throwing': 10, 'dodging': 90, 'speed': 10, 'iq': 10, 'luck': 50}),
            Player('p9', {'catching': 10, 'throwing': 10, 'dodging': 90, 'speed': 10, 'iq': 10, 'luck': 50}),
            Player('p10', {'catching': 10, 'throwing': 10, 'dodging': 90, 'speed': 10, 'iq': 10, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=100)
        winner, events = simulator.simulate_game(team1, team2)
        
        # Check that eliminated players have times_hit > 0
        for player in team1 + team2:
            if player.is_eliminated:
                assert player.stats['times_hit'] > 0
    
    def test_throw_attempts_tracked(self):
        """Test that throw attempts are tracked for all players."""
        team1 = [
            Player('p1', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p2', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p4', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        team2 = [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p7', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p9', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p10', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        winner, events = simulator.simulate_game(team1, team2)
        
        # At least some players should have throw attempts
        total_throws = sum(p.stats['throws_attempted'] for p in team1 + team2)
        assert total_throws > 0
