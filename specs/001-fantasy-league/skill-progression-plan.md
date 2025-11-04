# Skill Progression System Implementation Plan

**Task**: T106 - Implement skill improvement after games  
**Related Requirements**: FR-008 (Skill improvement through gameplay)  
**Date Created**: November 4, 2025

---

## Overview

Implement an XP-based skill progression system where players earn experience points from in-game performance, level up when reaching XP thresholds, and gain skill points that can be manually allocated to improve their skills.

## Design Principles

1. **Transparent**: Players can see exactly how much XP they need and where it comes from
2. **Balanced**: Rewards performance while also recognizing participation
3. **Flexible**: Players can allocate skill points to any skill (up to max of 100)
4. **Engaging**: Adds RPG-like progression to increase player investment
5. **Controllable**: Easy to tune XP rewards and leveling curve for game balance

---

## Phase 1: Backend - Data Model Changes

### 1.1 Update PlayerStats Model

**File**: `backend/src/models/player.py`

Add three new fields to the `PlayerStats` class:

```python
class PlayerStats(BaseModel):
    """Player game statistics."""
    # Existing fields...
    throws_attempted: int = Field(default=0, ge=0)
    catches_made: int = Field(default=0, ge=0)
    times_hit: int = Field(default=0, ge=0)
    missed_throws: int = Field(default=0, ge=0)
    successful_hits: int = Field(default=0, ge=0)
    games_played: int = Field(default=0, ge=0, description="Number of games played as starter")
    
    # NEW: Progression system
    experience_points: int = Field(default=0, ge=0, description="Total XP earned from gameplay")
    level: int = Field(default=1, ge=1, le=100, description="Player level (1-100)")
    available_skill_points: int = Field(default=0, ge=0, description="Unspent skill points from leveling")
```

### 1.2 Add Progression Methods to PlayerStats

Add these helper methods to `PlayerStats`:

```python
def calculate_xp_for_next_level(self) -> int:
    """
    Calculate XP required for next level.
    Uses exponential scaling: 100 * level^1.5
    
    Examples:
    - Level 1->2: 100 XP
    - Level 2->3: 283 XP  
    - Level 5->6: 1118 XP
    - Level 10->11: 3162 XP
    """
    return int(100 * (self.level ** 1.5))

def calculate_total_xp_for_level(self, target_level: int) -> int:
    """Calculate cumulative XP needed to reach a target level."""
    total = 0
    for lvl in range(1, target_level):
        total += int(100 * (lvl ** 1.5))
    return total

def can_level_up(self) -> bool:
    """Check if player has enough XP to level up."""
    next_level_threshold = self.calculate_total_xp_for_level(self.level + 1)
    return self.experience_points >= next_level_threshold

def level_up(self) -> int:
    """
    Level up the player if they have enough XP.
    
    Returns:
        Number of skill points awarded (1 per level)
    """
    if not self.can_level_up():
        return 0
    
    levels_gained = 0
    while self.can_level_up() and self.level < 100:
        self.level += 1
        self.available_skill_points += 1
        levels_gained += 1
    
    return levels_gained

def award_xp(self, amount: int) -> int:
    """
    Award XP and automatically level up if thresholds reached.
    
    Args:
        amount: XP to award
        
    Returns:
        Number of levels gained
    """
    self.experience_points += amount
    return self.level_up()
```

### 1.3 Add Skill Point Spending to Player Model

Add these methods to the `Player` class in `backend/src/models/player.py`:

```python
def spend_skill_point(self, skill_name: str) -> bool:
    """
    Spend an available skill point to increase a skill.
    
    Args:
        skill_name: Name of skill to increase (catching, throwing, dodging, speed, iq, luck)
        
    Returns:
        True if successful, False if not enough points or skill at max
        
    Raises:
        ValueError: If skill name is invalid
    """
    valid_skills = ['catching', 'throwing', 'dodging', 'speed', 'iq', 'luck']
    if skill_name not in valid_skills:
        raise ValueError(f"Invalid skill name: {skill_name}")
    
    # Check if player has available points
    if self.stats.available_skill_points <= 0:
        return False
    
    # Check if skill is already at max
    current_value = getattr(self.skills, skill_name)
    if current_value >= 100:
        return False
    
    # Increase skill and spend point
    setattr(self.skills, skill_name, current_value + 1)
    self.stats.available_skill_points -= 1
    
    # Recalculate value
    self.value = self.recalculate_value()
    
    return True

def get_progression_info(self) -> Dict[str, any]:
    """
    Get player progression information for UI display.
    
    Returns:
        Dictionary with level, XP, and progress to next level
    """
    current_xp = self.stats.experience_points
    current_level = self.stats.level
    
    # Calculate XP for current and next level
    current_level_xp = self.stats.calculate_total_xp_for_level(current_level)
    next_level_xp = self.stats.calculate_total_xp_for_level(current_level + 1)
    
    # XP needed for next level
    xp_for_next = next_level_xp - current_level_xp
    xp_progress = current_xp - current_level_xp
    
    return {
        'level': current_level,
        'experience_points': current_xp,
        'available_skill_points': self.stats.available_skill_points,
        'xp_for_next_level': xp_for_next,
        'xp_progress': xp_progress,
        'progress_percentage': (xp_progress / xp_for_next * 100) if xp_for_next > 0 else 100
    }
```

---

## Phase 2: Backend - XP Calculation Service

### 2.1 Create XP Calculation Utility

**File**: `backend/src/services/skill_progression.py` (new file)

```python
"""
Skill progression service for XP calculation and leveling.

This module handles:
- XP award calculation based on game performance
- Level progression logic
- Skill point allocation
"""

from typing import Dict, Tuple
from ..models.player import Player


def calculate_game_xp(
    throws_attempted: int,
    catches_made: int,
    successful_hits: int,
    times_hit: int,
    is_winner: bool
) -> int:
    """
    Calculate XP earned from a game based on performance.
    
    XP Breakdown:
    - Base participation: 10 XP
    - Per successful hit: 20 XP (offense reward)
    - Per catch: 15 XP (defense reward)
    - Per throw attempted: 2 XP (activity reward)
    - Survival bonus (not eliminated): 10 XP
    - Win bonus: 25 XP
    
    Typical game XP ranges:
    - Poor performance, loss: 30-50 XP
    - Average performance, loss: 50-80 XP
    - Good performance, loss: 80-120 XP
    - Poor performance, win: 55-75 XP
    - Average performance, win: 75-105 XP
    - Good performance, win: 105-145 XP
    - Exceptional performance, win: 145-200+ XP
    
    Args:
        throws_attempted: Number of throws
        catches_made: Number of catches
        successful_hits: Number of eliminations
        times_hit: Number of times eliminated
        is_winner: Whether player's team won
        
    Returns:
        Total XP earned
    """
    xp = 10  # Base participation
    
    # Performance-based XP
    xp += successful_hits * 20  # Offense
    xp += catches_made * 15     # Defense
    xp += throws_attempted * 2  # Activity
    
    # Survival bonus (didn't get hit)
    if times_hit == 0:
        xp += 10
    
    # Win bonus
    if is_winner:
        xp += 25
    
    return xp


def award_xp_to_player(
    player: Player,
    xp_amount: int
) -> Tuple[Player, int, bool]:
    """
    Award XP to a player and handle leveling.
    
    Args:
        player: Player to award XP to
        xp_amount: Amount of XP to award
        
    Returns:
        Tuple of (updated_player, levels_gained, did_level_up)
    """
    levels_gained = player.stats.award_xp(xp_amount)
    did_level_up = levels_gained > 0
    
    return player, levels_gained, did_level_up


def spend_skill_points(
    player: Player,
    skill_allocations: Dict[str, int]
) -> Tuple[Player, bool, str]:
    """
    Spend multiple skill points at once.
    
    Args:
        player: Player spending points
        skill_allocations: Dict of skill_name -> points_to_spend
        
    Returns:
        Tuple of (updated_player, success, error_message)
        
    Example:
        spend_skill_points(player, {'catching': 2, 'throwing': 1})
    """
    total_points_needed = sum(skill_allocations.values())
    
    if total_points_needed > player.stats.available_skill_points:
        return player, False, f"Not enough skill points. Have {player.stats.available_skill_points}, need {total_points_needed}"
    
    # Validate all skills can be increased before spending any
    for skill_name, points in skill_allocations.items():
        current_value = getattr(player.skills, skill_name)
        if current_value + points > 100:
            return player, False, f"Cannot increase {skill_name} by {points}. Would exceed max of 100"
    
    # Spend all points
    for skill_name, points in skill_allocations.items():
        for _ in range(points):
            success = player.spend_skill_point(skill_name)
            if not success:
                return player, False, f"Failed to spend point on {skill_name}"
    
    return player, True, ""
```

### 2.2 Update GameService to Award XP

**File**: `backend/src/services/game_service.py`

Modify the game simulation completion to award XP:

```python
from .skill_progression import calculate_game_xp, award_xp_to_player

# In the game completion logic, after updating stats:
def _finalize_game(self, game: Game, team1: Team, team2: Team) -> None:
    """Finalize game by updating all player stats and awarding XP."""
    
    winner_id = game.winner_id
    
    # Process each team's starters
    for team_id, team in [(team1.id, team1), (team2.id, team2)]:
        is_winning_team = (team_id == winner_id)
        
        for player_id in team.starter_ids:
            player = self.player_service.get_player(player_id)
            if not player:
                continue
            
            # Get player's stats from this game (track during simulation)
            game_stats = self._get_player_game_stats(game, player_id)
            
            # Update base stats
            player.update_stats(
                throws_attempted=game_stats['throws_attempted'],
                catches_made=game_stats['catches_made'],
                times_hit=game_stats['times_hit'],
                missed_throws=game_stats['missed_throws'],
                successful_hits=game_stats['successful_hits']
            )
            player.stats.games_played += 1
            
            # Calculate and award XP
            xp_earned = calculate_game_xp(
                throws_attempted=game_stats['throws_attempted'],
                catches_made=game_stats['catches_made'],
                successful_hits=game_stats['successful_hits'],
                times_hit=game_stats['times_hit'],
                is_winner=is_winning_team
            )
            
            levels_gained = player.stats.award_xp(xp_earned)
            
            # Log level ups (optional, for debugging)
            if levels_gained > 0:
                print(f"🎉 {player.name} leveled up! Now level {player.stats.level} (+{levels_gained})")
            
            # Handle injuries
            player.heal_after_game()
            
            # Save player
            self.player_service.storage.update_player(player_id, player.model_dump())
```

---

## Phase 3: Backend - API Endpoints

### 3.1 Add Skill Point Spending Endpoint

**File**: `backend/src/api/players.py`

```python
from pydantic import BaseModel
from typing import Dict

class SpendSkillPointRequest(BaseModel):
    """Request to spend skill points."""
    skill_name: str
    
class SpendMultipleSkillPointsRequest(BaseModel):
    """Request to spend multiple skill points at once."""
    allocations: Dict[str, int]  # e.g., {"catching": 2, "throwing": 1}

@router.post("/{player_id}/spend-skill-point")
def spend_skill_point(player_id: str, request: SpendSkillPointRequest):
    """
    Spend an available skill point to increase a player's skill.
    
    Args:
        player_id: Player ID
        request: Skill name to increase
        
    Returns:
        Updated player with progression info
        
    Raises:
        404: Player not found
        400: Cannot spend point (no points available or skill at max)
    """
    player_service = PlayerService()
    player = player_service.get_player(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    success = player.spend_skill_point(request.skill_name)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Cannot spend skill point (no points available or skill at max)"
        )
    
    # Save changes
    player_service.storage.update_player(player_id, player.model_dump())
    
    return {
        "player": player,
        "message": f"Increased {request.skill_name} by 1 point",
        "progression": player.get_progression_info()
    }

@router.post("/{player_id}/spend-skill-points")
def spend_multiple_skill_points(player_id: str, request: SpendMultipleSkillPointsRequest):
    """
    Spend multiple skill points at once.
    
    Args:
        player_id: Player ID
        request: Dictionary of skill allocations
        
    Returns:
        Updated player with progression info
    """
    from ..services.skill_progression import spend_skill_points
    
    player_service = PlayerService()
    player = player_service.get_player(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player, success, error_msg = spend_skill_points(player, request.allocations)
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Save changes
    player_service.storage.update_player(player_id, player.model_dump())
    
    return {
        "player": player,
        "message": f"Spent {sum(request.allocations.values())} skill points",
        "allocations": request.allocations,
        "progression": player.get_progression_info()
    }

@router.get("/{player_id}/progression")
def get_player_progression(player_id: str):
    """
    Get player's progression information (level, XP, available points).
    
    Returns:
        Progression info with level, XP, progress percentage
    """
    player_service = PlayerService()
    player = player_service.get_player(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return player.get_progression_info()
```

### 3.2 Update Player Response Schema

**File**: `backend/src/api/schemas.py`

Add progression info to player response schema:

```python
class PlayerResponse(BaseModel):
    """Player response with optional progression info."""
    id: str
    name: str
    age: int
    avatar: str
    skills: Dict[str, int]
    value: int
    stats: Dict[str, int]
    league_id: Optional[str]
    team_id: Optional[str]
    is_starter: bool
    progression: Optional[Dict[str, any]] = None  # NEW
```

---

## Phase 4: Backend - Testing

### 4.1 Unit Tests for XP Calculation

**File**: `backend/tests/unit/test_skill_progression.py` (new file)

```python
"""
Unit tests for skill progression system.
"""

import pytest
from src.services.skill_progression import calculate_game_xp
from src.models.player import Player, PlayerSkills, PlayerStats


class TestXPCalculation:
    """Test XP calculation logic."""
    
    def test_base_participation_xp(self):
        """Players get base 10 XP just for participating."""
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=0,
            successful_hits=0,
            times_hit=1,
            is_winner=False
        )
        assert xp == 10
    
    def test_successful_hit_xp(self):
        """Successful hits award 20 XP each."""
        xp = calculate_game_xp(
            throws_attempted=3,
            catches_made=0,
            successful_hits=2,
            times_hit=0,
            is_winner=False
        )
        # 10 base + (2 hits * 20) + (3 throws * 2) + 10 survival = 66
        assert xp == 66
    
    def test_catch_xp(self):
        """Catches award 15 XP each."""
        xp = calculate_game_xp(
            throws_attempted=0,
            catches_made=3,
            successful_hits=0,
            times_hit=0,
            is_winner=False
        )
        # 10 base + (3 catches * 15) + 10 survival = 65
        assert xp == 65
    
    def test_win_bonus(self):
        """Winning team gets 25 XP bonus."""
        loss_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=0,
            is_winner=False
        )
        win_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=0,
            is_winner=True
        )
        assert win_xp == loss_xp + 25
    
    def test_survival_bonus(self):
        """Not getting hit awards 10 XP survival bonus."""
        hit_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=1,
            is_winner=False
        )
        survive_xp = calculate_game_xp(
            throws_attempted=5,
            catches_made=2,
            successful_hits=1,
            times_hit=0,
            is_winner=False
        )
        assert survive_xp == hit_xp + 10


class TestLeveling:
    """Test leveling mechanics."""
    
    def test_level_1_to_2_threshold(self):
        """Level 2 requires 100 XP."""
        stats = PlayerStats()
        assert stats.level == 1
        assert stats.calculate_xp_for_next_level() == 100
    
    def test_award_xp_levels_up(self):
        """Awarding enough XP levels up player."""
        stats = PlayerStats()
        levels_gained = stats.award_xp(100)
        assert levels_gained == 1
        assert stats.level == 2
        assert stats.available_skill_points == 1
    
    def test_multiple_levels_at_once(self):
        """Can gain multiple levels from one XP award."""
        stats = PlayerStats()
        # Award enough XP for levels 2 and 3
        total_needed = stats.calculate_total_xp_for_level(4)
        levels_gained = stats.award_xp(total_needed)
        assert levels_gained == 3
        assert stats.level == 4
        assert stats.available_skill_points == 3
    
    def test_exponential_scaling(self):
        """XP requirements grow exponentially."""
        stats = PlayerStats()
        lvl_2 = stats.calculate_xp_for_next_level()  # 100
        
        stats.level = 5
        lvl_6 = stats.calculate_xp_for_next_level()  # 1118
        
        stats.level = 10
        lvl_11 = stats.calculate_xp_for_next_level()  # 3162
        
        assert lvl_6 > lvl_2 * 5  # More than linear
        assert lvl_11 > lvl_6 * 2


class TestSkillPointSpending:
    """Test spending skill points."""
    
    def test_spend_skill_point_success(self):
        """Can spend available skill point."""
        player = Player(
            name="Test Player",
            age=20,
            skills=PlayerSkills(catching=10, throwing=10, dodging=10, speed=10, iq=10, luck=10),
            value=6000
        )
        player.stats.available_skill_points = 1
        
        success = player.spend_skill_point('catching')
        assert success is True
        assert player.skills.catching == 11
        assert player.stats.available_skill_points == 0
    
    def test_spend_without_points(self):
        """Cannot spend if no points available."""
        player = Player(
            name="Test Player",
            age=20,
            skills=PlayerSkills(catching=10, throwing=10, dodging=10, speed=10, iq=10, luck=10),
            value=6000
        )
        player.stats.available_skill_points = 0
        
        success = player.spend_skill_point('catching')
        assert success is False
        assert player.skills.catching == 10
    
    def test_spend_on_maxed_skill(self):
        """Cannot increase skill beyond 100."""
        player = Player(
            name="Test Player",
            age=20,
            skills=PlayerSkills(catching=100, throwing=10, dodging=10, speed=10, iq=10, luck=10),
            value=14000
        )
        player.stats.available_skill_points = 1
        
        success = player.spend_skill_point('catching')
        assert success is False
        assert player.skills.catching == 100
        assert player.stats.available_skill_points == 1
    
    def test_invalid_skill_name(self):
        """Raises error for invalid skill name."""
        player = Player(
            name="Test Player",
            age=20,
            skills=PlayerSkills(catching=10, throwing=10, dodging=10, speed=10, iq=10, luck=10),
            value=6000
        )
        player.stats.available_skill_points = 1
        
        with pytest.raises(ValueError, match="Invalid skill name"):
            player.spend_skill_point('invalid_skill')
    
    def test_value_recalculated_after_spending(self):
        """Player value updates when skills increase."""
        player = Player(
            name="Test Player",
            age=20,
            skills=PlayerSkills(catching=10, throwing=10, dodging=10, speed=10, iq=10, luck=10),
            value=6000
        )
        player.stats.available_skill_points = 1
        old_value = player.value
        
        player.spend_skill_point('catching')
        assert player.value > old_value  # Value increased
```

### 4.2 Integration Tests

**File**: `backend/tests/integration/test_skill_progression.py` (new file)

```python
"""
Integration tests for skill progression API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestSkillProgressionAPI:
    """Test skill progression endpoints."""
    
    def test_get_progression_info(self, test_league, test_player):
        """Can retrieve player progression info."""
        response = client.get(f"/api/players/{test_player.id}/progression")
        assert response.status_code == 200
        
        data = response.json()
        assert 'level' in data
        assert 'experience_points' in data
        assert 'available_skill_points' in data
        assert 'xp_for_next_level' in data
        assert 'progress_percentage' in data
    
    def test_spend_skill_point(self, test_league, test_player):
        """Can spend skill point via API."""
        # Give player a skill point
        test_player.stats.available_skill_points = 1
        # Save to storage...
        
        response = client.post(
            f"/api/players/{test_player.id}/spend-skill-point",
            json={"skill_name": "catching"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data['player']['skills']['catching'] == test_player.skills.catching + 1
        assert data['player']['stats']['available_skill_points'] == 0
    
    def test_spend_without_points_fails(self, test_league, test_player):
        """Cannot spend if no points available."""
        test_player.stats.available_skill_points = 0
        # Save to storage...
        
        response = client.post(
            f"/api/players/{test_player.id}/spend-skill-point",
            json={"skill_name": "catching"}
        )
        assert response.status_code == 400
    
    def test_xp_awarded_after_game(self, test_league, test_team1, test_team2):
        """Players earn XP after game simulation."""
        # Simulate game
        response = client.post(
            "/api/games",
            json={
                "league_id": test_league.id,
                "team1_id": test_team1.id,
                "team2_id": test_team2.id
            }
        )
        assert response.status_code == 200
        
        # Check that starters gained XP
        for player_id in test_team1.starter_ids[:1]:  # Check first starter
            player_response = client.get(f"/api/players/{player_id}")
            player = player_response.json()
            assert player['stats']['experience_points'] > 0
```

---

## Phase 5: Frontend - TypeScript Types

### 5.1 Update Player Type

**File**: `frontend/src/types/index.ts`

```typescript
export interface PlayerStats {
  throws_attempted: number;
  catches_made: number;
  times_hit: number;
  missed_throws: number;
  successful_hits: number;
  games_played: number;
  
  // NEW: Progression fields
  experience_points: number;
  level: number;
  available_skill_points: number;
}

export interface PlayerProgression {
  level: number;
  experience_points: number;
  available_skill_points: number;
  xp_for_next_level: number;
  xp_progress: number;
  progress_percentage: number;
}

export interface Player {
  id: string;
  name: string;
  age: number;
  avatar: string;
  skills: PlayerSkills;
  value: number;
  stats: PlayerStats;
  league_id: string | null;
  team_id: string | null;
  is_starter: boolean;
  created_at: string;
  injury: Injury | null;
  progression?: PlayerProgression; // Optional, loaded separately
}
```

---

## Phase 6: Frontend - API Client

### 6.1 Add Progression API Methods

**File**: `frontend/src/services/api.ts`

```typescript
// Player progression endpoints
export const playerApi = {
  // ... existing methods ...
  
  getProgression: async (playerId: string): Promise<ApiResponse<PlayerProgression>> => {
    return handleApiRequest(`/players/${playerId}/progression`);
  },
  
  spendSkillPoint: async (
    playerId: string, 
    skillName: string
  ): Promise<ApiResponse<{ player: Player; message: string; progression: PlayerProgression }>> => {
    return handleApiRequest(`/players/${playerId}/spend-skill-point`, {
      method: 'POST',
      body: JSON.stringify({ skill_name: skillName }),
    });
  },
  
  spendMultipleSkillPoints: async (
    playerId: string,
    allocations: Record<string, number>
  ): Promise<ApiResponse<{ player: Player; message: string; allocations: Record<string, number>; progression: PlayerProgression }>> => {
    return handleApiRequest(`/players/${playerId}/spend-skill-points`, {
      method: 'POST',
      body: JSON.stringify({ allocations }),
    });
  },
};
```

---

## Phase 7: Frontend - UI Components

### 7.1 Create ProgressionBadge Component

**File**: `frontend/src/components/player/ProgressionBadge.tsx` (new file)

```typescript
/**
 * ProgressionBadge Component
 * 
 * Displays player level and XP progress bar.
 */

import React from 'react';
import { PlayerProgression } from '../../types';

interface ProgressionBadgeProps {
  progression: PlayerProgression;
  size?: 'small' | 'medium' | 'large';
}

export const ProgressionBadge: React.FC<ProgressionBadgeProps> = ({ 
  progression,
  size = 'medium'
}) => {
  const sizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base'
  };

  return (
    <div className="flex items-center gap-2">
      {/* Level Badge */}
      <div className="bg-gradient-to-br from-yellow-400 to-yellow-600 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-md">
        {progression.level}
      </div>
      
      {/* XP Progress Bar */}
      <div className="flex-1 min-w-[100px]">
        <div className="flex items-center justify-between mb-1">
          <span className={`font-medium text-gray-700 ${sizeClasses[size]}`}>
            Level {progression.level}
          </span>
          <span className={`text-gray-500 ${sizeClasses[size]}`}>
            {progression.xp_progress} / {progression.xp_for_next_level} XP
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${Math.min(100, progression.progress_percentage)}%` }}
          />
        </div>
      </div>
      
      {/* Available Skill Points */}
      {progression.available_skill_points > 0 && (
        <div className="bg-green-100 border border-green-300 text-green-800 px-2 py-1 rounded-md font-semibold">
          +{progression.available_skill_points} SP
        </div>
      )}
    </div>
  );
};
```

### 7.2 Create SkillPointAllocator Component

**File**: `frontend/src/components/player/SkillPointAllocator.tsx` (new file)

```typescript
/**
 * SkillPointAllocator Component
 * 
 * UI for spending skill points on player skills.
 */

import React, { useState } from 'react';
import { Player, PlayerSkills } from '../../types';
import { playerApi } from '../../services/api';

interface SkillPointAllocatorProps {
  player: Player;
  onUpdate: (updatedPlayer: Player) => void;
}

const SKILL_NAMES: Record<keyof PlayerSkills, string> = {
  catching: 'Catching',
  throwing: 'Throwing',
  dodging: 'Dodging',
  speed: 'Speed',
  iq: 'IQ',
  luck: 'Luck',
};

export const SkillPointAllocator: React.FC<SkillPointAllocatorProps> = ({
  player,
  onUpdate,
}) => {
  const [allocations, setAllocations] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalAllocated = Object.values(allocations).reduce((sum, val) => sum + val, 0);
  const availablePoints = player.stats.available_skill_points - totalAllocated;

  const handleIncrement = (skillName: string) => {
    if (availablePoints <= 0) return;
    
    const currentSkillValue = player.skills[skillName as keyof PlayerSkills];
    const plannedIncrease = allocations[skillName] || 0;
    
    if (currentSkillValue + plannedIncrease >= 100) {
      setError(`${SKILL_NAMES[skillName as keyof PlayerSkills]} is at maximum`);
      return;
    }
    
    setAllocations(prev => ({
      ...prev,
      [skillName]: (prev[skillName] || 0) + 1
    }));
    setError(null);
  };

  const handleDecrement = (skillName: string) => {
    if (!allocations[skillName] || allocations[skillName] === 0) return;
    
    setAllocations(prev => ({
      ...prev,
      [skillName]: prev[skillName] - 1
    }));
    setError(null);
  };

  const handleReset = () => {
    setAllocations({});
    setError(null);
  };

  const handleConfirm = async () => {
    if (totalAllocated === 0) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await playerApi.spendMultipleSkillPoints(player.id, allocations);
      
      if (response.error) {
        setError(response.error.message);
        return;
      }

      onUpdate(response.data!.player);
      setAllocations({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to allocate skill points');
    } finally {
      setLoading(false);
    }
  };

  if (player.stats.available_skill_points === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <p className="text-gray-600">No skill points available</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Allocate Skill Points</h3>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{availablePoints}</div>
          <div className="text-xs text-gray-500">points remaining</div>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="space-y-3 mb-4">
        {Object.entries(SKILL_NAMES).map(([skillKey, skillLabel]) => {
          const currentValue = player.skills[skillKey as keyof PlayerSkills];
          const plannedIncrease = allocations[skillKey] || 0;
          const newValue = currentValue + plannedIncrease;

          return (
            <div key={skillKey} className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-gray-700">{skillLabel}</span>
                  <span className="text-sm text-gray-500">
                    {currentValue}
                    {plannedIncrease > 0 && (
                      <span className="text-green-600 font-semibold"> → {newValue}</span>
                    )}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${currentValue}%` }}
                  />
                  {plannedIncrease > 0 && (
                    <div 
                      className="bg-green-400 h-2 rounded-full -mt-2"
                      style={{ 
                        width: `${newValue}%`,
                        opacity: 0.6 
                      }}
                    />
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => handleDecrement(skillKey)}
                  disabled={!allocations[skillKey] || allocations[skillKey] === 0}
                  className="w-8 h-8 rounded-md bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-bold"
                >
                  −
                </button>
                <span className="w-6 text-center font-semibold">
                  {plannedIncrease || 0}
                </span>
                <button
                  onClick={() => handleIncrement(skillKey)}
                  disabled={availablePoints === 0 || newValue >= 100}
                  className="w-8 h-8 rounded-md bg-blue-500 hover:bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed font-bold"
                >
                  +
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleReset}
          disabled={totalAllocated === 0 || loading}
          className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed rounded-md font-semibold transition-colors"
        >
          Reset
        </button>
        <button
          onClick={handleConfirm}
          disabled={totalAllocated === 0 || loading}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed rounded-md font-semibold transition-colors"
        >
          {loading ? 'Applying...' : `Confirm (${totalAllocated})`}
        </button>
      </div>
    </div>
  );
};
```

### 7.3 Update PlayerDetailPage

**File**: `frontend/src/pages/PlayerDetailPage.tsx`

Add progression display and skill point allocation:

```typescript
// Add to imports
import { ProgressionBadge } from '../components/player/ProgressionBadge';
import { SkillPointAllocator } from '../components/player/SkillPointAllocator';

// In component:
<div className="space-y-6">
  {/* Existing player info... */}
  
  {/* Progression Section */}
  {player.progression && (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Progression</h3>
      <ProgressionBadge progression={player.progression} size="large" />
    </div>
  )}
  
  {/* Skill Point Allocation */}
  {player.stats.available_skill_points > 0 && (
    <SkillPointAllocator 
      player={player} 
      onUpdate={(updatedPlayer) => setPlayer(updatedPlayer)} 
    />
  )}
  
  {/* Existing stats sections... */}
</div>
```

### 7.4 Add Level-Up Notification

**File**: `frontend/src/components/game/GameResultsModal.tsx` (new file or add to existing)

```typescript
/**
 * Show level-up notifications after game simulation
 */

interface GameResultsModalProps {
  game: Game;
  levelUps: Array<{ playerId: string; playerName: string; newLevel: number; skillPointsGained: number }>;
  onClose: () => void;
}

export const GameResultsModal: React.FC<GameResultsModalProps> = ({
  game,
  levelUps,
  onClose
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Game results... */}
        
        {/* Level Up Notifications */}
        {levelUps.length > 0 && (
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-t border-yellow-200 p-6">
            <h3 className="text-xl font-bold text-yellow-900 mb-4 flex items-center gap-2">
              🎉 Level Up!
            </h3>
            <div className="space-y-2">
              {levelUps.map((levelUp) => (
                <div key={levelUp.playerId} className="bg-white rounded-lg p-3 border border-yellow-300">
                  <p className="font-semibold text-gray-900">
                    {levelUp.playerName} reached Level {levelUp.newLevel}!
                  </p>
                  <p className="text-sm text-gray-600">
                    +{levelUp.skillPointsGained} skill point{levelUp.skillPointsGained !== 1 ? 's' : ''} available
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="p-6 border-t">
          <button
            onClick={onClose}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

## Phase 8: Tuning and Balance

### 8.1 XP Tuning Parameters

Create configuration file for easy balance adjustments:

**File**: `backend/src/config/progression_config.py` (new file)

```python
"""
Configuration for skill progression system.
Easy to adjust for game balance.
"""

# XP Awards per action
XP_BASE_PARTICIPATION = 10
XP_PER_SUCCESSFUL_HIT = 20
XP_PER_CATCH = 15
XP_PER_THROW_ATTEMPTED = 2
XP_SURVIVAL_BONUS = 10
XP_WIN_BONUS = 25

# Leveling formula: BASE * (level ^ EXPONENT)
XP_LEVEL_BASE = 100
XP_LEVEL_EXPONENT = 1.5

# Skill points per level
SKILL_POINTS_PER_LEVEL = 1

# Maximum level
MAX_LEVEL = 100

# Maximum skill value
MAX_SKILL_VALUE = 100
```

### 8.2 Balance Testing Checklist

- [ ] Simulate 10 games, verify average XP gain per game (target: 50-100 XP)
- [ ] Verify level 2 achievable in 1-2 games for good performance
- [ ] Verify level 10 requires ~15-20 games
- [ ] Test that spending skill points increases player value appropriately
- [ ] Verify no exploits (e.g., throwing constantly for XP farming)
- [ ] Test UI displays correctly at various levels (1, 10, 50, 99, 100)

---

## Testing Checklist

### Backend Tests
- [ ] XP calculation unit tests pass
- [ ] Leveling logic unit tests pass
- [ ] Skill point spending unit tests pass
- [ ] API endpoint integration tests pass
- [ ] XP awarded correctly after game simulation
- [ ] Multiple level-ups handled correctly

### Frontend Tests
- [ ] ProgressionBadge renders correctly
- [ ] SkillPointAllocator UI works
- [ ] API calls succeed
- [ ] Error handling displays properly
- [ ] Level-up notifications appear

### End-to-End Tests
- [ ] Create player, play game, verify XP awarded
- [ ] Level up player, verify skill point available
- [ ] Spend skill point, verify skill increased and value recalculated
- [ ] Verify progression persists across page refreshes

---

## Future Enhancements (Post-T106)

### Possible additions after initial implementation:

1. **Skill-Specific XP**: Award bonus XP for actions related to specific skills
   - Catching bonus → catching XP → catching skill auto-increases
   
2. **Talent Trees**: Unlock special abilities at certain levels
   - Level 10: Choose offensive or defensive specialization
   - Level 25: Unlock signature move
   
3. **Prestige System**: Reset to level 1 with permanent bonuses
   - Keep some skills, gain multiplier
   
4. **Daily/Weekly Challenges**: Bonus XP objectives
   - "Get 5 catches in one game" → +50 XP bonus
   
5. **XP Events**: Double XP weekends, bonus XP for specific matchups

6. **Achievements**: One-time XP bonuses for milestones
   - First game → +25 XP
   - 10 games → +100 XP
   - First elimination → +50 XP

---

## Implementation Order

1. **Phase 1**: Backend data model changes (~2 hours)
2. **Phase 2**: XP calculation service (~2 hours)
3. **Phase 3**: API endpoints (~2 hours)
4. **Phase 4**: Backend testing (~3 hours)
5. **Phase 5**: Frontend types (~30 minutes)
6. **Phase 6**: API client (~1 hour)
7. **Phase 7**: UI components (~4 hours)
8. **Phase 8**: Tuning and balance (~2 hours)

**Total Estimated Time**: ~16-18 hours

---

## Success Criteria

✅ Players earn XP from games based on performance  
✅ Players level up automatically when reaching XP thresholds  
✅ Players receive skill points when leveling up  
✅ Players can spend skill points on any skill (up to max 100)  
✅ Player value recalculates when skills increase  
✅ UI clearly shows level, XP progress, and available skill points  
✅ Level-up notifications appear after games  
✅ All tests pass  
✅ System is balanced (reasonable progression pace)  

---

## Notes

- This system is additive - it doesn't break existing functionality
- Can be implemented incrementally (backend first, then frontend)
- Easy to tune numbers for balance without code changes
- Provides long-term engagement for players
- Creates strategic decisions (which skills to improve)
- Value system naturally reflects player growth
