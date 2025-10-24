# Data Model: Dodgeball Fantasy League Core System

**Feature**: 001-fantasy-league  
**Date**: October 24, 2025  
**Phase**: 1 - Design & Contracts

## Entity Definitions

### Player

Represents an individual dodgeball athlete in the league.

**Fields**:
- `id` (string, UUID): Unique identifier
- `name` (string): Placeholder name (e.g., "Player 1")
- `age` (integer): Player age, initial range 18-20
- `avatar` (string): Placeholder avatar URL/identifier
- `skills` (object):
  - `catching` (integer, 0-100): Ability to catch thrown balls
  - `throwing` (integer, 0-100): Throwing accuracy and power
  - `dodging` (integer, 0-100): Evasion capability
  - `speed` (integer, 0-100): Movement and reaction speed
  - `iq` (integer, 0-100): Strategic thinking and positioning
  - `luck` (integer, 0-100): Random variance influence
- `value` (integer): Calculated dollar value (no cents)
- `injury` (object, nullable):
  - `severity` (enum): "minor" | "moderate" | "severe"
  - `affected_reduction` (float): Percentage reduction (0.2-0.5)
  - `games_remaining` (integer): Games until healed (1-3)
- `stats` (object):
  - `throws_attempted` (integer): Total throws made
  - `catches_made` (integer): Successful catches
  - `times_hit` (integer): Times eliminated by being hit
  - `missed_throws` (integer): Throws that missed
  - `successful_hits` (integer): Successful eliminations
- `team_id` (string, UUID, nullable): Assigned team or null if free agent
- `is_starter` (boolean): Whether designated as starter

**Validation Rules**:
- Sum of all skills must equal 10 for new players (FR-002)
- Each skill must be 0-100 (FR-003)
- Age 18-20 for new players (FR-001)
- Value must be recalculated when age or skills change

**Relationships**:
- Belongs to zero or one Team (many-to-one)
- Participates in many Games (many-to-many through GamePlayer)

### Team

Represents a fantasy team with roster and budget.

**Fields**:
- `id` (string, UUID): Unique identifier
- `name` (string): Team name
- `description` (string): Team description
- `logo` (string): Logo URL/identifier
- `budget` (integer): Remaining budget in dollars (0-100000)
- `player_ids` (list of strings): Roster player IDs (8-12 players)
- `starter_ids` (list of strings): Designated starter IDs (exactly 5)
- `wins` (integer): Number of wins
- `losses` (integer): Number of losses
- `awards` (list of strings): Team achievements
- `league_id` (string, UUID): Parent league

**Validation Rules**:
- Roster size 8-12 players (FR-012)
- Exactly 5 starters (FR-013)
- All starters must be in roster
- Budget cannot be negative
- Cannot add player if value exceeds budget (FR-014)
- Can add player if value equals budget (FR-014a)

**Relationships**:
- Has many Players (one-to-many)
- Belongs to one League (many-to-one)
- Participates in many Games (one-to-many)

### League

Central management entity for the fantasy league.

**Fields**:
- `id` (string, UUID): Unique identifier
- `name` (string): League name
- `settings` (object):
  - `player_count` (integer): Number of generated players (50-100)
  - `season_rounds` (integer): Number of times each pairing plays
- `team_ids` (list of strings): Teams in league
- `game_ids` (list of strings): Historical game records
- `schedule` (list of objects): Upcoming games
  - `game_number` (integer)
  - `team1_id` (string)
  - `team2_id` (string)
  - `completed` (boolean)
- `created_at` (datetime): League creation timestamp

**Validation Rules**:
- Must have at least 2 teams to create schedule
- Player count 50-100 (FR-001a)

**Relationships**:
- Has many Teams (one-to-many)
- Has many Players (one-to-many through free agent pool)
- Has many Games (one-to-many)

### Game

Represents a match between two teams.

**Fields**:
- `id` (string, UUID): Unique identifier
- `league_id` (string, UUID): Parent league
- `team1_id` (string, UUID): Home team
- `team2_id` (string, UUID): Away team
- `team1_starters` (list of strings): Player IDs that started
- `team2_starters` (list of strings): Player IDs that started
- `events` (list of objects): Play-by-play events
  - `turn` (integer)
  - `type` (enum): "throw" | "hit" | "catch" | "miss" | "elimination"
  - `thrower_id` (string)
  - `target_id` (string)
  - `outcome` (string): Description of what happened
- `winner_id` (string, UUID): Winning team ID
- `completed_at` (datetime): Game completion timestamp
- `seed` (integer): Random seed for deterministic replay

**Validation Rules**:
- Both teams must have 5 starters (FR-026)
- Game must end when one team fully eliminated (FR-029)
- Winner must be one of the participating teams

**Relationships**:
- Belongs to one League (many-to-one)
- Involves two Teams (many-to-one for each)
- Involves many Players (many-to-many through game_players)

### Injury

Represents a temporary condition affecting a player.

**Fields**:
- `player_id` (string, UUID): Affected player
- `severity` (enum): "minor" | "moderate" | "severe"
- `stat_reduction` (float): Percentage reduction (0.2, 0.35, or 0.5)
- `healing_games` (integer): Total games to heal (1, 2, or 3)
- `games_remaining` (integer): Games until fully healed
- `occurred_at` (datetime): When injury happened

**Validation Rules**:
- Minor: 20% reduction, 1 game
- Moderate: 35% reduction, 2 games
- Severe: 50% reduction, 3 games
- games_remaining must be ≤ healing_games

**Relationships**:
- Belongs to one Player (one-to-one or zero-to-one)

## State Transitions

### Player States
```
[Free Agent] --draft--> [On Team]
[On Team] --release--> [Free Agent]
[Healthy] --injury--> [Injured]
[Injured] --heal after N games--> [Healthy]
[Age < 30] --birthday--> [Age ≥ 30] (triggers skill cap reduction)
```

### Team States
```
[Created] --add players--> [Roster Building]
[Roster Building] --designate starters--> [Game Ready]
[Game Ready] --play game--> [Update Record]
```

### Game States
```
[Scheduled] --start--> [In Progress]
[In Progress] --team eliminated--> [Completed]
[Completed] --stats updated--> [Archived]
```

### League States
```
[Created] --generate players--> [Player Pool Ready]
[Player Pool Ready] --teams created--> [Team Formation]
[Team Formation] --schedule created--> [Season Active]
[Season Active] --all games played--> [Season Complete]
```

## Calculated Fields

### Player.value
```python
base_value = sum(skills.values()) * 100
age_factor = 1.0 if age < 30 else max(0.5, 1.0 - ((age - 30) * 0.05))
value = int(base_value * age_factor)
```

### Player.effective_skills (when injured)
```python
if injury:
    reduction = injury.stat_reduction
    effective_skills = {
        skill: int(value * (1 - reduction))
        for skill, value in skills.items()
    }
else:
    effective_skills = skills
```

### Team.remaining_budget
```python
spent = sum(player.value for player in roster)
remaining_budget = 100000 - spent
```

### League.standings
```python
standings = sorted(teams, key=lambda t: (t.wins, -t.losses), reverse=True)
```

## Indexes & Performance

Since this milestone uses in-memory storage, indexes are implemented as dictionary lookups:

- `players_by_id`: O(1) lookup by player ID
- `players_by_team`: O(1) lookup by team ID → list of players
- `free_agents`: Computed list of players where team_id is null
- `teams_by_league`: O(1) lookup by league ID → list of teams
- `games_by_league`: O(1) lookup by league ID → list of games

## Data Consistency Rules

1. **Budget Integrity**: Sum of player values in roster + remaining budget = $100,000
2. **Roster Integrity**: All starter IDs must exist in player_ids
3. **Assignment Integrity**: Player can only be on one team at a time
4. **Game Integrity**: All player IDs in game must belong to participating teams
5. **Injury Integrity**: Injury can only exist if player exists
6. **Schedule Integrity**: Each team pair can appear at most N times (where N = season_rounds)

## Migration Notes

Future database migration considerations:
- Add created_at/updated_at timestamps to all entities
- Add soft delete flags instead of hard deletes
- Consider separate tables for game_events and player_stats for query efficiency
- Add indexes on foreign keys (team_id, league_id) and frequently filtered fields (is_starter, team_id null)
