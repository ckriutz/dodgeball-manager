"""
Age progression service for managing player aging and stat penalties.

This module handles:
- Aging players at the end of each season
- Calculating age-based stat penalties (physical stats decline, IQ preserved)
- Skill cap reduction for older players
- Bulk operations for season transitions

References:
- data-model.md: Age and skill penalty mechanics
- FR-007: Age-related skill reduction
- FR-010: Age increases at season completion
- T101: Implement AgeProgressionService
"""

from typing import Dict, List, Any


# Age constants
MAX_AGE = 100
AGE_PENALTY_START = 30  # Penalties begin after age 30

# Physical vs mental stats categorization
PHYSICAL_STATS = frozenset(['speed', 'dodging', 'catching', 'throwing'])
MENTAL_STATS = frozenset(['iq'])
LUCK_STATS = frozenset(['luck'])

# Base skill maximum at any age
BASE_MAX_SKILL = 100

# Physical stat decline rates (per year over 30)
# Physical stats decline faster than others
PHYSICAL_DECLINE_RATE = 2  # Points per year
LUCK_DECLINE_RATE = 1  # Minor decline
MENTAL_DECLINE_RATE = 0  # IQ doesn't decline (wisdom increases with age)


def calculate_age_penalty(age: int) -> float:
    """
    Calculate overall age penalty multiplier.
    
    The penalty is 0 for ages 30 and below, then increases
    based on how many years past 30 the player is.
    
    Penalty formula: years_over_30 * 0.02 (2% per year)
    
    Args:
        age: Player age (18-100)
        
    Returns:
        Penalty multiplier (0.0 = no penalty, up to 1.0 for very old)
        
    Examples:
        - Age 25: 0.0 (no penalty)
        - Age 31: 0.02 (2% penalty)
        - Age 35: 0.10 (10% penalty)
        - Age 40: 0.20 (20% penalty)
    """
    if age <= AGE_PENALTY_START:
        return 0.0
    
    years_over_threshold = age - AGE_PENALTY_START
    penalty = years_over_threshold * 0.02
    
    # Cap penalty at 1.0 (100%)
    return min(1.0, penalty)


def calculate_stat_penalties(age: int) -> Dict[str, int]:
    """
    Calculate stat-specific penalties for a given age.
    
    Different stats decline at different rates:
    - Physical stats (speed, dodging, catching, throwing): 2 points/year after 30
    - Luck: 1 point/year after 30
    - IQ: No decline (stays the same)
    
    Args:
        age: Player age
        
    Returns:
        Dict mapping skill names to penalty amounts (points to subtract)
    """
    if age <= AGE_PENALTY_START:
        return {
            'catching': 0,
            'throwing': 0,
            'dodging': 0,
            'speed': 0,
            'iq': 0,
            'luck': 0
        }
    
    years_over = age - AGE_PENALTY_START
    
    return {
        'catching': years_over * PHYSICAL_DECLINE_RATE,
        'throwing': years_over * PHYSICAL_DECLINE_RATE,
        'dodging': years_over * PHYSICAL_DECLINE_RATE,
        'speed': years_over * PHYSICAL_DECLINE_RATE,
        'iq': years_over * MENTAL_DECLINE_RATE,  # IQ doesn't decline
        'luck': years_over * LUCK_DECLINE_RATE
    }


def get_max_skill_levels(age: int) -> Dict[str, int]:
    """
    Get maximum skill levels for a given age.
    
    After age 30, maximum skill levels decrease for physical stats:
    - Physical stats: max = 100 - (years_over_30 * 2)
    - IQ: stays at 100 (no cap reduction)
    - Luck: max = 100 - (years_over_30 * 1)
    
    Args:
        age: Player age (18-100)
        
    Returns:
        Dict mapping skill names to maximum values (0-100)
    """
    if age <= AGE_PENALTY_START:
        return {
            'catching': BASE_MAX_SKILL,
            'throwing': BASE_MAX_SKILL,
            'dodging': BASE_MAX_SKILL,
            'speed': BASE_MAX_SKILL,
            'iq': BASE_MAX_SKILL,
            'luck': BASE_MAX_SKILL
        }
    
    years_over = age - AGE_PENALTY_START
    
    # Calculate reduced maximums
    physical_max = max(0, BASE_MAX_SKILL - (years_over * PHYSICAL_DECLINE_RATE))
    luck_max = max(0, BASE_MAX_SKILL - (years_over * LUCK_DECLINE_RATE))
    
    return {
        'catching': physical_max,
        'throwing': physical_max,
        'dodging': physical_max,
        'speed': physical_max,
        'iq': BASE_MAX_SKILL,  # IQ never declines
        'luck': luck_max
    }


def apply_age_progression(player: Dict) -> Dict:
    """
    Age a player by 1 year and apply stat penalties if over 30.
    
    This function:
    1. Increases age by 1 (up to max 100)
    2. If new age > 30, applies stat reductions based on decline rates:
       - Physical stats: reduce by PHYSICAL_DECLINE_RATE per year
       - Luck: reduce by LUCK_DECLINE_RATE per year
       - IQ: no decline
    3. Skills cannot go below 0
    
    Args:
        player: Player dict with 'age' and 'skills' fields
        
    Returns:
        Updated player dict with new age and adjusted skills
    """
    # Make a copy to avoid mutating input
    aged_player = {
        **player,
        'skills': dict(player.get('skills', {}))
    }
    
    current_age = aged_player.get('age', 18)
    
    # Cap at max age
    if current_age >= MAX_AGE:
        return aged_player
    
    # Increment age
    new_age = current_age + 1
    aged_player['age'] = new_age
    
    # Apply skill reductions if entering penalty age
    if new_age > AGE_PENALTY_START:
        skills = aged_player['skills']
        
        # Apply decline to physical stats
        for skill_name in PHYSICAL_STATS:
            if skill_name in skills:
                new_value = skills[skill_name] - PHYSICAL_DECLINE_RATE
                skills[skill_name] = max(0, new_value)
        
        # Apply decline to luck
        for skill_name in LUCK_STATS:
            if skill_name in skills:
                new_value = skills[skill_name] - LUCK_DECLINE_RATE
                skills[skill_name] = max(0, new_value)
        
        # IQ doesn't decline (stays the same)
    
    return aged_player


def apply_bulk_age_progression(players: List[Dict]) -> List[Dict]:
    """
    Age multiple players at once (typically at season end).
    
    This function applies age progression to all players in the list.
    Useful for end-of-season processing.
    
    Args:
        players: List of player dicts
        
    Returns:
        List of updated player dicts with new ages and adjusted skills
    """
    return [apply_age_progression(player) for player in players]


def preview_age_progression(players: List[Dict]) -> List[Dict]:
    """
    Preview age progression changes without applying them.
    
    This function shows what changes would occur if age progression
    were applied, useful for displaying to users before confirming.
    
    Args:
        players: List of player dicts
        
    Returns:
        List of preview dicts containing:
        - player_id: Player's ID
        - name: Player's name
        - old_age: Current age
        - new_age: Age after progression
        - skill_changes: Dict of skill changes (skill_name -> {old, new})
    """
    previews = []
    
    for player in players:
        player_id = player.get('player_id', player.get('id', 'unknown'))
        name = player.get('name', 'Unknown')
        old_age = player.get('age', 18)
        skills = player.get('skills', {})
        
        # Calculate new age (capped at MAX_AGE)
        new_age = min(old_age + 1, MAX_AGE)
        
        # Calculate skill changes
        skill_changes = {}
        
        if new_age > AGE_PENALTY_START:
            # Physical stats decline by PHYSICAL_DECLINE_RATE per year after 30
            for skill_name in PHYSICAL_STATS:
                if skill_name in skills:
                    current_value = skills[skill_name]
                    new_value = max(0, current_value - PHYSICAL_DECLINE_RATE)
                    if new_value != current_value:
                        skill_changes[skill_name] = {
                            'old': current_value,
                            'new': new_value,
                            'change': new_value - current_value
                        }
            
            # Luck declines by LUCK_DECLINE_RATE per year after 30
            for skill_name in LUCK_STATS:
                if skill_name in skills:
                    current_value = skills[skill_name]
                    new_value = max(0, current_value - LUCK_DECLINE_RATE)
                    if new_value != current_value:
                        skill_changes[skill_name] = {
                            'old': current_value,
                            'new': new_value,
                            'change': new_value - current_value
                        }
        
        previews.append({
            'player_id': player_id,
            'name': name,
            'old_age': old_age,
            'new_age': new_age,
            'skill_changes': skill_changes,
            'has_penalty': new_age > AGE_PENALTY_START
        })
    
    return previews


class AgeProgressionService:
    """
    Service class for managing player age progression.
    
    This service provides a more object-oriented interface for use
    with Player models and integrates with the storage system.
    """
    
    def __init__(self, storage=None):
        """
        Initialize AgeProgressionService.
        
        Args:
            storage: Optional storage instance for persistence
        """
        self.storage = storage
    
    def age_player(self, player: Any) -> tuple:
        """
        Age a Player model by 1 year.
        
        Args:
            player: Player model instance
            
        Returns:
            Tuple of (player, skill_changes_dict, did_have_penalty)
        """
        old_age = player.age
        old_skills = player.skills.to_dict() if hasattr(player.skills, 'to_dict') else dict(player.skills)
        
        # Apply age progression
        player_dict = {
            'age': player.age,
            'skills': old_skills
        }
        
        result = apply_age_progression(player_dict)
        
        # Update player model
        player.age = result['age']
        
        # Track skill changes
        skill_changes = {}
        for skill_name, new_value in result['skills'].items():
            old_value = old_skills.get(skill_name, 0)
            if new_value != old_value:
                setattr(player.skills, skill_name, new_value)
                skill_changes[skill_name] = {
                    'old': old_value,
                    'new': new_value
                }
        
        # Recalculate value if player has the method
        if hasattr(player, 'recalculate_value'):
            player.value = player.recalculate_value()
        
        did_have_penalty = result['age'] > AGE_PENALTY_START and len(skill_changes) > 0
        
        return player, skill_changes, did_have_penalty
    
    def age_all_players_in_league(self, league_id: str) -> List[Dict]:
        """
        Age all players in a league (season end operation).
        
        Args:
            league_id: League ID
            
        Returns:
            List of age progression results for each player
        """
        if not self.storage:
            raise ValueError("Storage must be configured to use this method")
        
        results = []
        
        # Get all players in the league
        players = self.storage.get_players_by_league(league_id)
        
        for player_data in players:
            # Apply age progression
            updated_data = apply_age_progression(player_data)
            
            # Track changes
            skill_changes = {}
            old_skills = player_data.get('skills', {})
            new_skills = updated_data.get('skills', {})
            
            for skill_name in old_skills:
                if old_skills[skill_name] != new_skills.get(skill_name, old_skills[skill_name]):
                    skill_changes[skill_name] = {
                        'old': old_skills[skill_name],
                        'new': new_skills[skill_name]
                    }
            
            # Save updated player
            player_id = player_data.get('id', player_data.get('player_id'))
            self.storage.update_player(player_id, updated_data)
            
            results.append({
                'player_id': player_id,
                'name': player_data.get('name', 'Unknown'),
                'old_age': player_data['age'],
                'new_age': updated_data['age'],
                'skill_changes': skill_changes
            })
        
        return results
    
    def get_retirement_candidates(self, league_id: str, min_age: int = 40) -> List[Dict]:
        """
        Get players who may be candidates for retirement based on age.
        
        Args:
            league_id: League ID
            min_age: Minimum age to be considered a retirement candidate
            
        Returns:
            List of player dicts who meet the age threshold
        """
        if not self.storage:
            raise ValueError("Storage must be configured to use this method")
        
        players = self.storage.get_players_by_league(league_id)
        
        return [
            {
                'player_id': p.get('id', p.get('player_id')),
                'name': p.get('name', 'Unknown'),
                'age': p.get('age', 18),
                'max_skills': get_max_skill_levels(p.get('age', 18))
            }
            for p in players
            if p.get('age', 18) >= min_age
        ]
