"""
Simulation tests with deterministic outcomes.

This module tests game simulation with fixed random seeds to ensure
deterministic and reproducible results.

References:
- research.md: Game Simulation Algorithm
- NFR-003: Deterministic simulation with seed
- FR-026: Games require exactly 5 starters per team
- FR-029: Game ends when one team is fully eliminated
"""

import pytest
import random
from typing import List, Dict, Tuple


class Player:
    """Simplified player for simulation testing."""
    
    def __init__(self, player_id: str, skills: Dict[str, int]):
        self.id = player_id
        self.skills = skills
        self.is_eliminated = False
        self.stats = {
            'throws_attempted': 0,
            'catches_made': 0,
            'times_hit': 0,
            'missed_throws': 0,
            'successful_hits': 0
        }
    
    def eliminate(self):
        """Mark player as eliminated."""
        self.is_eliminated = True
        self.stats['times_hit'] += 1
    
    def record_throw_attempt(self):
        """Record a throw attempt."""
        self.stats['throws_attempted'] += 1
    
    def record_hit(self):
        """Record a successful hit."""
        self.stats['successful_hits'] += 1
    
    def record_miss(self):
        """Record a missed throw."""
        self.stats['missed_throws'] += 1
    
    def record_catch(self):
        """Record a successful catch."""
        self.stats['catches_made'] += 1


class GameSimulator:
    """Simplified game simulator for testing."""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.events = []
    
    def simulate_game(
        self,
        team1_starters: List[Player],
        team2_starters: List[Player]
    ) -> Tuple[int, List[Dict]]:
        """
        Simulate a game between two teams.
        
        Args:
            team1_starters: List of 5 starting players for team 1
            team2_starters: List of 5 starting players for team 2
            
        Returns:
            Tuple of (winning_team_id, events)
            where winning_team_id is 1 or 2
        """
        # Reset seed at start of game for determinism
        if self.seed is not None:
            random.seed(self.seed)
        
        self.events = []
        
        # Validate both teams have 5 starters
        if len(team1_starters) != 5:
            raise ValueError(f"Team 1 must have exactly 5 starters, got {len(team1_starters)}")
        if len(team2_starters) != 5:
            raise ValueError(f"Team 2 must have exactly 5 starters, got {len(team2_starters)}")
        
        turn = 0
        attacking_team = 1  # Alternate between 1 and 2
        
        # Continue until one team is eliminated
        while True:
            turn += 1
            
            # Get active players
            team1_active = [p for p in team1_starters if not p.is_eliminated]
            team2_active = [p for p in team2_starters if not p.is_eliminated]
            
            # Check for game end
            if len(team1_active) == 0:
                self.events.append({
                    'turn': turn,
                    'type': 'game_end',
                    'outcome': 'Team 2 wins - Team 1 eliminated'
                })
                return 2, self.events
            
            if len(team2_active) == 0:
                self.events.append({
                    'turn': turn,
                    'type': 'game_end',
                    'outcome': 'Team 1 wins - Team 2 eliminated'
                })
                return 1, self.events
            
            # Determine thrower and target
            if attacking_team == 1:
                thrower = self._select_thrower(team1_active)
                target = random.choice(team2_active)
                attacking_team = 2
            else:
                thrower = self._select_thrower(team2_active)
                target = random.choice(team1_active)
                attacking_team = 1
            
            # Record throw attempt
            thrower.record_throw_attempt()
            
            # Calculate hit probability
            hit_prob = self._calculate_hit_probability(thrower.skills, target.skills)
            
            # Roll for hit
            roll = random.random()
            
            if roll < hit_prob:
                # Hit successful - target eliminated
                target.eliminate()
                thrower.record_hit()
                
                self.events.append({
                    'turn': turn,
                    'type': 'hit',
                    'thrower_id': thrower.id,
                    'target_id': target.id,
                    'outcome': f'{thrower.id} hit {target.id} - eliminated!'
                })
            else:
                # Miss - check for catch
                thrower.record_miss()
                catch_prob = target.skills['catching'] / 100.0
                catch_roll = random.random()
                
                if catch_roll < catch_prob:
                    # Catch successful - thrower eliminated
                    thrower.eliminate()
                    target.record_catch()
                    
                    self.events.append({
                        'turn': turn,
                        'type': 'catch',
                        'thrower_id': thrower.id,
                        'target_id': target.id,
                        'outcome': f'{target.id} caught {thrower.id}\'s throw - {thrower.id} eliminated!'
                    })
                else:
                    # Miss with no catch
                    self.events.append({
                        'turn': turn,
                        'type': 'miss',
                        'thrower_id': thrower.id,
                        'target_id': target.id,
                        'outcome': f'{thrower.id} missed {target.id}'
                    })
            
            # Safety limit to prevent infinite loops in tests
            if turn > 1000:
                raise RuntimeError("Game exceeded maximum turns (1000)")
    
    def _select_thrower(self, active_players: List[Player]) -> Player:
        """Select the player with highest throwing + IQ."""
        return max(
            active_players,
            key=lambda p: p.skills['throwing'] + p.skills['iq']
        )
    
    def _calculate_hit_probability(
        self,
        thrower_skills: Dict[str, int],
        target_skills: Dict[str, int]
    ) -> float:
        """Calculate hit probability based on skills."""
        base_prob = thrower_skills['throwing'] / 100.0
        iq_modifier = (thrower_skills['iq'] - target_skills['iq']) * 0.01
        dodge_modifier = -target_skills['dodging'] * 0.01
        
        prob = base_prob + iq_modifier + dodge_modifier
        
        # Apply luck variance
        avg_luck = (thrower_skills['luck'] + target_skills['luck']) / 2
        luck_variance = (avg_luck / 100.0) * 0.1
        prob += luck_variance
        
        return max(0.0, min(1.0, prob))


class TestDeterministicSimulation:
    """Test that game simulation is deterministic with fixed seed."""
    
    def test_same_seed_produces_same_outcome(self):
        """Test that using the same seed produces identical results."""
        # Create identical teams
        team1_game1 = [
            Player('p1', {'catching': 50, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 55, 'luck': 45}),
            Player('p2', {'catching': 55, 'throwing': 55, 'dodging': 45, 'speed': 45, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 60, 'throwing': 50, 'dodging': 50, 'speed': 40, 'iq': 45, 'luck': 55}),
            Player('p4', {'catching': 45, 'throwing': 65, 'dodging': 55, 'speed': 55, 'iq': 60, 'luck': 40}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        team2_game1 = [
            Player('p6', {'catching': 52, 'throwing': 58, 'dodging': 42, 'speed': 48, 'iq': 53, 'luck': 47}),
            Player('p7', {'catching': 57, 'throwing': 53, 'dodging': 47, 'speed': 43, 'iq': 52, 'luck': 48}),
            Player('p8', {'catching': 62, 'throwing': 48, 'dodging': 52, 'speed': 38, 'iq': 47, 'luck': 53}),
            Player('p9', {'catching': 47, 'throwing': 63, 'dodging': 57, 'speed': 53, 'iq': 62, 'luck': 38}),
            Player('p10', {'catching': 52, 'throwing': 48, 'dodging': 48, 'speed': 52, 'iq': 48, 'luck': 52})
        ]
        
        # Simulate first game with seed 42
        simulator1 = GameSimulator(seed=42)
        winner1, events1 = simulator1.simulate_game(team1_game1, team2_game1)
        
        # Create identical teams again
        team1_game2 = [
            Player('p1', {'catching': 50, 'throwing': 60, 'dodging': 40, 'speed': 50, 'iq': 55, 'luck': 45}),
            Player('p2', {'catching': 55, 'throwing': 55, 'dodging': 45, 'speed': 45, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 60, 'throwing': 50, 'dodging': 50, 'speed': 40, 'iq': 45, 'luck': 55}),
            Player('p4', {'catching': 45, 'throwing': 65, 'dodging': 55, 'speed': 55, 'iq': 60, 'luck': 40}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        team2_game2 = [
            Player('p6', {'catching': 52, 'throwing': 58, 'dodging': 42, 'speed': 48, 'iq': 53, 'luck': 47}),
            Player('p7', {'catching': 57, 'throwing': 53, 'dodging': 47, 'speed': 43, 'iq': 52, 'luck': 48}),
            Player('p8', {'catching': 62, 'throwing': 48, 'dodging': 52, 'speed': 38, 'iq': 47, 'luck': 53}),
            Player('p9', {'catching': 47, 'throwing': 63, 'dodging': 57, 'speed': 53, 'iq': 62, 'luck': 38}),
            Player('p10', {'catching': 52, 'throwing': 48, 'dodging': 48, 'speed': 52, 'iq': 48, 'luck': 52})
        ]
        
        # Simulate second game with same seed 42
        simulator2 = GameSimulator(seed=42)
        winner2, events2 = simulator2.simulate_game(team1_game2, team2_game2)
        
        # Winners should be the same
        assert winner1 == winner2
        
        # Number of events should be the same
        assert len(events1) == len(events2)
        
        # Event sequence should be identical
        for event1, event2 in zip(events1, events2):
            assert event1['type'] == event2['type']
            assert event1['turn'] == event2['turn']
    
    def test_different_seeds_produce_different_outcomes(self):
        """Test that different seeds can produce different outcomes."""
        team1_a = [
            Player('p1', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p2', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p4', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        team2_a = [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p7', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p8', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p9', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p10', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        # Simulate with different seeds multiple times
        outcomes = set()
        for seed in [1, 2, 3, 4, 5, 10, 20, 30, 40, 50]:
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
            
            simulator = GameSimulator(seed=seed)
            winner, _ = simulator.simulate_game(team1, team2)
            outcomes.add(winner)
        
        # With equal teams and different seeds, we should see both teams win at least once
        # (statistically very likely with 10 different seeds)
        assert len(outcomes) > 1, "Different seeds should produce varied outcomes"
    
    def test_game_ends_when_team_eliminated(self):
        """Test that game ends when all players on one team are eliminated."""
        # Create unbalanced teams to ensure one team wins
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
        
        # Game should have a winner
        assert winner in [1, 2]
        
        # Last event should be game_end
        assert events[-1]['type'] == 'game_end'
        
        # One team should be fully eliminated
        if winner == 1:
            assert all(p.is_eliminated for p in team2)
            assert any(not p.is_eliminated for p in team1)
        else:
            assert all(p.is_eliminated for p in team1)
            assert any(not p.is_eliminated for p in team2)
    
    def test_requires_exactly_five_starters(self):
        """Test that game requires exactly 5 starters per team (FR-026)."""
        valid_team = [
            Player('p1', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p2', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p4', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p5', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        # Test with too few starters
        too_few = [
            Player('p1', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p2', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p3', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50}),
            Player('p4', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        simulator = GameSimulator(seed=42)
        with pytest.raises(ValueError, match="must have exactly 5 starters"):
            simulator.simulate_game(too_few, valid_team)
        
        # Test with too many starters
        too_many = valid_team + [
            Player('p6', {'catching': 50, 'throwing': 50, 'dodging': 50, 'speed': 50, 'iq': 50, 'luck': 50})
        ]
        
        with pytest.raises(ValueError, match="must have exactly 5 starters"):
            simulator.simulate_game(valid_team, too_many)
