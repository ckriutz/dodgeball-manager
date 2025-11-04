# Data Model: Dodgeball Fantasy League Core System

**Feature**: 001-fantasy-league  
**Date**: October 24, 2025 (Updated: November 4, 2025)  
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
- `value` (integer): Calculated dollar value (no cents) - **Updated formula (Nov 4)**
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
  - `games_played` (integer): Total games played as starter - **Added (Nov 4)**
  - `experience_points` (integer): Total XP earned - **Added (Nov 4)**
  - `level` (integer): Current level (1-100) - **Added (Nov 4)**
  - `available_skill_points` (integer): Unspent skill points - **Added (Nov 4)**
- `team_id` (string, UUID, nullable): Assigned team or null if free agent
- `is_starter` (boolean): Whether designated as starter
- `league_id` (string, UUID): Parent league

**Validation Rules**:
- Sum of all skills must equal 10 for new players (FR-002)
- Each skill must be 0-100 (FR-003)
- Age 18-20 for new players (FR-001)
- Value must be recalculated when age, skills, level, or games_played changes (FR-004b)
- Level must be 1-100 (FR-008b)
- Available skill points ≥ 0 (FR-008d)

**Relationships**:
- Belongs to zero or one Team (many-to-one)
- Belongs to one League (many-to-one)
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
- `wins` (integer): Number of wins (resets per season) - **Updated (Nov 4)**
- `losses` (integer): Number of losses (resets per season) - **Updated (Nov 4)**
- `awards` (list of strings): Team achievements
- `league_id` (string, UUID): Parent league

**Validation Rules**:
- Roster size 8-12 players (FR-013)
- Exactly 5 starters (FR-014)
- All starters must be in roster
- Budget cannot be negative
- Cannot add player if value exceeds budget (FR-015)
- Can add player if value equals budget (FR-015a)

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
- `game_ids` (list of strings): All historical game records
- `current_season` (object, nullable): Current active season - **Added (Nov 4)**
  - See Season entity below
- `season_archives` (list of objects): Past completed seasons - **Added (Nov 4)**
  - See SeasonArchive entity below
- `created_at` (datetime): League creation timestamp

**Validation Rules**:
- Must have at least 2 teams to create schedule (FR-024)
- Player count 50-100 (FR-001a)
- Can only have one current_season at a time
- Cannot start new season if current_season is in-progress (FR-031)

**Relationships**:
- Has many Teams (one-to-many)
- Has many Players (one-to-many through free agent pool)
- Has many Games (one-to-many)
- Has one current Season (one-to-one, nullable)
- Has many SeasonArchives (one-to-many)

### Season (Added November 4, 2025)

Represents a competitive period with schedule and standings.

**Fields**:
- `season_number` (integer): Sequential season identifier (1, 2, 3, ...)
- `status` (enum): "setup" | "in-progress" | "completed"
- `schedule` (object): Current season schedule
  - See Schedule entity below
- `standings` (list of objects): Current standings
  - `team_id` (string)
  - `wins` (integer)
  - `losses` (integer)
  - `rank` (integer)
- `statistical_leaders` (object): Current season leaders
  - `most_hits` (string, player_id)
  - `best_catch_pct` (string, player_id)
  - `most_catches` (string, player_id)
  - `highest_level` (string, player_id)
- `mvp_player_id` (string, nullable): Season MVP (calculated when status = completed)
- `champion_team_id` (string, nullable): Season champion (set when status = completed)
- `started_at` (datetime): When season began
- `completed_at` (datetime, nullable): When season finished

**State Transitions**:
```
setup → in-progress (when schedule generated)
in-progress → completed (when all games played and user confirms)
```

**Validation Rules**:
- Status "in-progress" requires non-empty schedule (FR-024)
- Status "completed" requires all games in schedule to be completed (FR-029)
- MVP and champion can only be set when status = "completed"

**Relationships**:
- Belongs to one League (embedded in current_season field)
- Has one Schedule (embedded)

### Schedule (Added November 4, 2025)

Represents the ordered list of games for a season.

**Fields**:
- `games` (list of objects): Ordered schedule of games
  - `game_number` (integer): Sequential position in schedule (1, 2, 3, ...)
  - `team1_id` (string, UUID): Home team
  - `team2_id` (string, UUID): Away team
  - `status` (enum): "pending" | "completed"
  - `game_id` (string, UUID, nullable): Reference to Game entity once played
  - `scheduled_order` (integer): Display order
- `total_games` (integer): Total number of games in schedule
- `completed_games` (integer): Number of completed games
- `next_game_number` (integer, nullable): Next pending game number (null if all complete)

**Computed Fields**:
- `is_complete`: true if completed_games == total_games
- `progress_percentage`: (completed_games / total_games) * 100

**Validation Rules**:
- Game pairings must use valid team_ids from league (FR-024)
- Round-robin format: each team pair appears at least once (FR-024)
- Game numbers must be sequential (1, 2, 3, ...)
- All games must have unique game_numbers
- Completed games must have non-null game_id

**Relationships**:
- Belongs to one Season (embedded in schedule field)
- References many Games (via game_id when status = "completed")

### SeasonArchive (Added November 4, 2025)

Immutable snapshot of a completed season for historical records.

**Fields**:
- `season_number` (integer): Which season this was (1, 2, 3, ...)
- `final_standings` (list of objects): End-of-season standings
  - `team_id` (string)
  - `team_name` (string): Snapshot of name at season end
  - `wins` (integer)
  - `losses` (integer)
  - `rank` (integer)
- `champion_team_id` (string): Season winner
- `champion_team_name` (string): Winner's name snapshot
- `mvp_player_id` (string): MVP
- `mvp_player_name` (string): MVP's name snapshot
- `statistical_leaders` (object): Season-end statistical leaders
  - `most_hits` (object): `{ player_id, player_name, value }`
  - `best_catch_pct` (object): `{ player_id, player_name, value }`
  - `most_catches` (object): `{ player_id, player_name, value }`
- `team_rosters` (dict): Snapshot of each team's roster at season end
  - Key: team_id (string)
  - Value: list of player_ids
- `player_stats_snapshot` (dict): Snapshot of player stats at season end
  - Key: player_id (string)
  - Value: PlayerStats object (copy of stats at that time)
- `total_games_played` (integer): Number of games in the season
- `started_at` (datetime): When season began
- `completed_at` (datetime): When season finished

**Immutability**: Once created, SeasonArchive entries are never modified. They preserve historical data even if current players/teams change.

**Validation Rules**:
- Champion must be one of the teams in final_standings
- MVP must be one of the players in player_stats_snapshot
- completed_at must be after started_at
- season_number must be unique within a league

**Relationships**:
- Belongs to one League (in season_archives list)
- References historical Players and Teams (by ID, but stores names as snapshots)

### Game

Represents a match between two teams.

**Fields**:
- `id` (string, UUID): Unique identifier
- `league_id` (string, UUID): Parent league
- `season_number` (integer): Which season this game belongs to - **Added (Nov 4)**
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
- `player_stats` (dict): Per-player stats for this game - **Added (Nov 4)**
  - Key: player_id (string)
  - Value: object with throws_attempted, catches_made, successful_hits, times_hit, xp_earned
- `winner_id` (string, UUID): Winning team ID
- `completed_at` (datetime): Game completion timestamp
- `seed` (integer): Random seed for deterministic replay

**Validation Rules**:
- Both teams must have 5 starters (FR-032)
- Game must end when one team fully eliminated (FR-035)
- Winner must be one of the participating teams
- All player_ids in team1_starters must belong to team1
- All player_ids in team2_starters must belong to team2

**Relationships**:
- Belongs to one League (many-to-one)
- Belongs to one Season (via season_number)
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
[Level N] --earn XP--> [Level N+1] (awards skill point) - Added (Nov 4)
[Has Skill Points] --allocate--> [Skill Increased, Points Decreased] - Added (Nov 4)
```

### Team States
```
[Created] --add players--> [Roster Building]
[Roster Building] --designate starters--> [Game Ready]
[Game Ready] --play game--> [Update Record]
[Season End] --reset record--> [Game Ready] (for next season) - Added (Nov 4)
```

### Game States
```
[Scheduled] --start--> [In Progress]
[In Progress] --team eliminated--> [Completed]
[Completed] --stats & XP updated--> [Archived] - Updated (Nov 4)
```

### League States
```
[Created] --generate players--> [Player Pool Ready]
[Player Pool Ready] --teams created--> [Team Formation]
[Team Formation] --schedule created--> [Season Active]
[Season Active] --all games played--> [Season Complete]
[Season Complete] --finish season--> [Historical Season Created] - Added (Nov 4)
[Historical Season Created] --start next season--> [Season Active] - Added (Nov 4)
```

### Season States (Added November 4, 2025)
```
[setup] --generate schedule--> [in-progress]
[in-progress] --all games completed--> [ready to finish]
[ready to finish] --user confirms--> [completed]
[completed] --archived to history--> [new season setup]
```

## Calculated Fields

### Player.value (Updated November 4, 2025)
```python
# Updated formula incorporating level, games_played, and age
base_value = (
    (sum(skills.values()) * 100) +    # Skills primary factor
    (stats.games_played * 50) +        # Experience bonus
    (stats.level * 200) -              # Progression bonus
    age_penalty
)

age_penalty = max(0, (age - 30) * 500) if age >= 30 else 0

value = max(0, int(base_value))  # Cannot be negative
```

### Player.progression_info (Added November 4, 2025)
```python
current_level_xp = sum(100 * (lvl ** 1.5) for lvl in range(1, stats.level))
next_level_xp = sum(100 * (lvl ** 1.5) for lvl in range(1, stats.level + 1))

xp_for_next = next_level_xp - current_level_xp
xp_progress = stats.experience_points - current_level_xp

progression_info = {
    'level': stats.level,
    'experience_points': stats.experience_points,
    'available_skill_points': stats.available_skill_points,
    'xp_for_next_level': xp_for_next,
    'xp_progress': xp_progress,
    'progress_percentage': (xp_progress / xp_for_next * 100) if xp_for_next > 0 else 100
}
```

### Player.xp_from_game (Added November 4, 2025)
```python
def calculate_game_xp(game_stats, is_winner):
    xp = 10  # Base participation
    xp += game_stats['successful_hits'] * 20  # Offense
    xp += game_stats['catches_made'] * 15     # Defense
    xp += game_stats['throws_attempted'] * 2  # Activity
    
    if game_stats['times_hit'] == 0:
        xp += 10  # Survival bonus
    
    if is_winner:
        xp += 25  # Win bonus
    
    return xp
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

### League.standings (Updated November 4, 2025)
```python
# Current season standings
standings = sorted(
    teams, 
    key=lambda t: (t.wins, -t.losses), 
    reverse=True
)

# Add rank
for i, team in enumerate(standings, 1):
    team.rank = i
```

### Season.is_complete (Added November 4, 2025)
```python
is_complete = schedule.completed_games == schedule.total_games
```

### Season.mvp_calculation (Added November 4, 2025)
```python
# MVP = Highest total eliminations + catch percentage bonus
def calculate_mvp(players):
    scores = {}
    for player in players:
        if player.stats.games_played == 0:
            continue
        
        eliminations_score = player.stats.successful_hits * 10
        catch_pct = (player.stats.catches_made / player.stats.throws_attempted 
                     if player.stats.throws_attempted > 0 else 0)
        catch_score = catch_pct * 50
        
        scores[player.id] = eliminations_score + catch_score
    
    mvp_id = max(scores, key=scores.get)
    return mvp_id
```

## Indexes & Performance

Since this milestone uses in-memory storage, indexes are implemented as dictionary lookups:

- `players_by_id`: O(1) lookup by player ID
- `players_by_team`: O(1) lookup by team ID → list of players
- `free_agents`: Computed list of players where team_id is null
- `teams_by_league`: O(1) lookup by league ID → list of teams
- `games_by_league`: O(1) lookup by league ID → list of games
- `games_by_season`: O(1) lookup by season_number → list of games - **Added (Nov 4)**
- `players_with_skill_points`: Computed list where available_skill_points > 0 - **Added (Nov 4)**

## Data Consistency Rules

1. **Budget Integrity**: Sum of player values in roster + remaining budget = $100,000
2. **Roster Integrity**: All starter IDs must exist in player_ids
3. **Assignment Integrity**: Player can only be on one team at a time
4. **Game Integrity**: All player IDs in game must belong to participating teams
5. **Injury Integrity**: Injury can only exist if player exists
6. **Schedule Integrity**: Each team pair can appear at most N times (where N = season_rounds)
7. **Season Integrity**: Only one current_season can exist per league (FR-029) - **Added (Nov 4)**
8. **XP Integrity**: experience_points must match sum of all XP awards from games - **Added (Nov 4)**
9. **Level Integrity**: level must match calculated level from experience_points - **Added (Nov 4)**
10. **Skill Points Integrity**: available_skill_points = total_earned - total_spent - **Added (Nov 4)**
11. **Archive Immutability**: SeasonArchive entries are never modified after creation - **Added (Nov 4)**
12. **Value Consistency**: Player value must recalculate when skills, level, games_played, or age changes - **Added (Nov 4)**

## Migration Notes

Future database migration considerations:
- Add created_at/updated_at timestamps to all entities
- Add soft delete flags instead of hard deletes
- Consider separate tables for game_events and player_stats for query efficiency
- Add indexes on foreign keys (team_id, league_id, season_number) and frequently filtered fields (is_starter, team_id null, available_skill_points > 0)
- SeasonArchive table for historical seasons with immutable constraint
- Player progression history table for tracking level-ups and skill point allocations
- Add triggers to automatically recalculate player value on stat changes
- Consider materialized views for standings and statistical leaders for performance
