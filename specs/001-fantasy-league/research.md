# Research: Dodgeball Fantasy League Core System

**Feature**: 001-fantasy-league  
**Date**: October 24, 2025 (Updated: November 4, 2025)  
**Phase**: 0 - Outline & Research

## Research Questions & Decisions

### 1. Player Value Calculation Formula (Updated November 4, 2025)

**Decision**: Use comprehensive weighted formula with skills, experience, level, and age

**Formula**:
```python
base_value = (
    (sum_of_skills * 100) +           # Skills: primary factor
    (games_played * 50) +             # Experience bonus
    (level * 200) -                   # Progression bonus
    (age_penalty_after_30)            # Age penalty
)

age_penalty = max(0, (age - 30) * 500)  # 500 per year over 30
```

**Example Calculations**:
- New player (age 20, 10 skill points, level 1, 0 games): ~1,200
- Growing player (age 22, 30 total skills, level 3, 10 games): ~4,100
- Average player (age 25, 60 total skills, level 8, 50 games): ~10,100
- Veteran player (age 32, 80 total skills, level 15, 100 games): ~14,000 (with -1,000 penalty)
- Elite player (age 28, 120 total skills, level 25, 200 games): ~27,000

**Rationale**:
- Skills remain primary value driver (100x multiplier) - aligns with original design
- Level provides significant progression reward (200x) - motivates skill point allocation
- Games played adds experience value (50x) - rewards longevity
- Age penalty creates strategic roster decisions - aging stars vs. young prospects
- All integer math per FR-004a
- Transparent and tunable weights for game balance

**Alternatives Considered**:
- Original formula (skills + age only): Rejected - doesn't reward player progression
- Multiplicative formula: Rejected - causes value explosion at high levels
- Equal weighting: Rejected - skills should matter most

### 2. Game Simulation Algorithm

**Decision**: Turn-based probabilistic combat with stat-based outcome calculation

**Algorithm**:
```
For each turn:
  1. Determine thrower (highest throwing + IQ on active team)
  2. Select random target from opposing active players
  3. Calculate hit probability:
     - Base: thrower.throwing / 100
     - Modified by: (thrower.IQ - target.IQ) * 0.01
     - Modified by: -target.dodging * 0.01
     - Apply luck variance: ±10% based on both players' luck
  4. Roll for outcome:
     - If hit: Target eliminated, update stats
     - If miss: Calculate catch probability
       - Base: target.catching / 100
       - Apply luck variance
     - If caught: Thrower eliminated
     - If not caught: No elimination
  5. Check for game end (all players eliminated on one side)
```

**Rationale**:
- Deterministic with seed for testing (NFR-003)
- All six stats have meaningful impact
- Sequential processing matches dodgeball flow
- Luck adds variance without dominating outcomes

**Alternatives Considered**:
- Simultaneous throws: Rejected - creates complex resolution scenarios
- Real-time simulation: Rejected - determinism requirement
- Team-level stats: Rejected - loses individual player impact

### 3. In-Memory Storage Strategy

**Decision**: Singleton storage manager with typed collections

**Implementation**:
```python
class MemoryStorage:
    _instance = None
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.teams: Dict[str, Team] = {}
        self.leagues: Dict[str, League] = {}
        self.games: List[Game] = []
```

**Rationale**:
- Simple singleton pattern for single-user requirement
- Direct dictionary access for O(1) lookups
- No serialization overhead
- Easy to migrate to database later (same interface)

**Alternatives Considered**:
- File-based pickle: Rejected - persistence out of scope
- SQLite in-memory: Rejected - adds SQL dependency unnecessarily
- Redis: Rejected - explicitly out of scope per FR-033

### 4. Injury System Mechanics

**Decision**: Probabilistic injury on hits with time-based healing

**Mechanics**:
- 5% injury probability when player is hit
- Injury severity levels: Minor (20% reduction), Moderate (35% reduction), Severe (50% reduction)
- Severity distribution: 60% minor, 30% moderate, 10% severe
- Healing time: Minor=1 game, Moderate=2 games, Severe=3 games
- Affected stats: All six skills reduced by percentage
- Injured players can still play (FR-006a)

**Rationale**:
- Low probability maintains gameplay flow
- Time-based healing is simple and predictable
- Percentage reduction scales with player ability
- Three severity levels provide variety without complexity

**Alternatives Considered**:
- Specific stat injuries: Rejected - adds tracking complexity
- Random healing: Rejected - determinism requirement
- Medical treatment system: Rejected - out of scope

### 5. Schedule Generation Algorithm

**Decision**: Round-robin tournament with optional repeat rounds

**Algorithm**:
```
For N teams:
  - Generate all unique pairings: N * (N-1) / 2 games
  - Shuffle pairings for variety
  - Optional: Repeat for multi-round seasons
```

**Rationale**:
- Ensures fairness (everyone plays everyone)
- Simple to implement and understand
- Scales to any number of teams
- Supports multiple rounds for longer seasons

**Alternatives Considered**:
- Playoff brackets: Deferred to future milestone
- Division-based scheduling: Rejected - premature for initial version
- Home/away games: Rejected - no venue concept in spec

### 6. Frontend State Management

**Decision**: React Context API for global state, component state for local

**Strategy**:
- LeagueContext: Current league, player pool, teams
- GameContext: Current game state during simulation
- Local state: Form inputs, UI toggles, filters
- No Redux or external state library

**Rationale**:
- Context API sufficient for single-user, moderate complexity
- Avoids dependency on Redux/MobX/Zustand
- Simpler debugging and less boilerplate
- Easy to upgrade later if needed

**Alternatives Considered**:
- Redux: Rejected - overkill for this scope
- Zustand: Rejected - additional dependency
- Props drilling: Rejected - poor scalability

### 7. API Design Patterns

**Decision**: RESTful API with resource-based endpoints

**Endpoints**:
```
POST   /api/leagues                    # Create league
POST   /api/leagues/{id}/players       # Generate players
GET    /api/leagues/{id}/players       # List players

POST   /api/teams                      # Create team
POST   /api/teams/{id}/players         # Add player to roster
DELETE /api/teams/{id}/players/{pid}   # Remove player
PATCH  /api/teams/{id}/starters        # Designate starters

POST   /api/games                      # Create/simulate game
GET    /api/games/{id}                 # Get game details
GET    /api/games                      # List games (history)

GET    /api/leagues/{id}/standings     # Get standings
GET    /api/leagues/{id}/awards        # Get MVPs and leaders
```

**Rationale**:
- Standard REST conventions for predictability
- Resource hierarchy matches domain model
- CRUD operations map to user stories
- Async FastAPI handlers for performance

**Alternatives Considered**:
- GraphQL: Rejected - over-engineered for simple CRUD
- RPC-style: Rejected - less standard than REST
- WebSockets: Rejected - no real-time requirements

### 8. Testing Strategy

**Decision**: Multi-layered testing with deterministic simulation tests

**Layers**:
1. **Unit Tests** (pytest):
   - Model validation and business logic
   - Player value calculation
   - Injury mechanics
   - XP calculation and leveling logic
   - Coverage target: 80%+

2. **Simulation Tests**:
   - Deterministic game outcomes with fixed seeds
   - Edge cases (all players equal stats, extreme disparities)
   - Injury probability verification
   - Statistical outcome validation

3. **Integration Tests**:
   - API endpoint contracts
   - End-to-end user flows (league creation → draft → game)
   - Budget enforcement
   - Data consistency checks

4. **Frontend Tests** (Jest + RTL):
   - Component rendering
   - User interactions
   - API integration mocks

**Rationale**:
- Simulation determinism enables regression testing
- Integration tests catch data consistency issues (SC-004)
- Component tests ensure UI reliability
- No E2E tests needed for single-user milestone

**Alternatives Considered**:
- Manual testing only: Rejected - insufficient for deterministic requirements
- Property-based testing: Deferred - nice-to-have but not critical
- Load testing: Rejected - single-user scope

### 9. XP and Leveling System (Added November 4, 2025)

**Decision**: Exponential leveling with action-based XP rewards and manual skill point allocation

**XP Award Formula**:
```python
xp = (
    10 +                           # Base participation
    (successful_hits * 20) +       # Offense reward
    (catches * 15) +               # Defense reward
    (throws_attempted * 2) +       # Activity reward
    (10 if not_hit else 0) +      # Survival bonus
    (25 if team_won else 0)        # Win bonus
)
```

**Level Progression Formula**:
```python
xp_for_next_level = 100 * (level ** 1.5)

# Examples:
# Level 1→2: 100 XP (1-2 games)
# Level 2→3: 183 XP
# Level 5→6: 1,118 XP (~15-20 games)
# Level 10→11: 3,162 XP
# Level 20→21: 8,944 XP
```

**Skill Point System**:
- 1 skill point awarded per level gained
- Multiple levels can be gained in one game
- Manual allocation only (no automatic distribution)
- Can allocate to any skill up to max of 100
- Visual indicators (badges) show unspent points
- Allocation via SkillPointAllocator UI component

**Expected XP Per Game**:
- Poor performance, loss: 30-50 XP
- Average performance: 60-80 XP
- Good performance, win: 100-130 XP
- Exceptional performance: 150+ XP

**Rationale**:
- Level 2 is achievable quickly (instant gratification)
- Level 10 requires sustained play (medium-term goal)
- Exponential curve prevents level cap issues
- Rewards both offense and defense
- Participation XP ensures all players progress
- Manual allocation creates strategic decisions
- Transparent formula easy to balance and tune

**Alternatives Considered**:
- Linear progression: Rejected - too predictable
- Fixed XP per game: Rejected - doesn't reward performance
- Automatic skill allocation: Rejected - removes player agency
- Skill-specific XP: Rejected - adds complexity without clear benefit

**Implementation Reference**: See `skill-progression-plan.md` for detailed implementation guide including backend models, API endpoints, and frontend components.

### 10. Season Management and Historical Data (Added November 4, 2025)

**Decision**: Lifecycle-based season management with immutable historical snapshots

**Season Lifecycle States**:
1. **Setup**: League exists, teams created, no schedule generated
2. **In-Progress**: Schedule exists with pending games
3. **Completed**: All games finished, awaiting season finalization

**Season Progression Flow**:
```
1. User clicks "Generate Schedule" → State: In-Progress
2. User clicks "Play Next Game" repeatedly → Games marked completed
3. All games done → Button changes to "Finish Season"
4. User clicks "Finish Season" → Show completion screen (standings, MVP, stats)
5. User confirms → Age all players +1 year, store season snapshot → State: Completed
6. User clicks "Start Next Season" → Generate new schedule → State: In-Progress (new season)
```

**Historical Season Storage**:
```python
class SeasonArchive:
    season_number: int
    final_standings: List[TeamStanding]  # Team ID, wins, losses, ranking
    champion_team_id: str
    mvp_player_id: str
    statistical_leaders: Dict[str, PlayerId]  # 'most_hits', 'best_catch_pct', etc.
    team_rosters: Dict[TeamId, List[PlayerId]]  # Snapshot of rosters
    player_stats: Dict[PlayerId, PlayerStats]  # Snapshot of end-season stats
    completed_date: datetime
```

**Schedule Interaction**:
- Schedule stored as list of Game objects with `status: pending | completed`
- UI shows games with visual indicators:
  - Completed games: grayed out
  - Next game: highlighted/bold
  - Future games: normal display
- "Play Next Game" button finds first pending game in order
- After simulation, marks game as completed
- Schedule view updates automatically

**Historical Data Access**:
- Current season data lives in memory (active League object)
- Past seasons stored in `League.season_archives: List[SeasonArchive]`
- UI provides "Current Season" and "Season History" tabs
- Season History shows list of past seasons with:
  - Season number
  - Champion
  - MVP
  - Final standings
  - Click to view detailed stats

**Age Progression**:
- Happens only at season completion (not during season)
- Preview screen shows all players with age changes highlighted
- User must confirm before ages update
- Age-related stat penalties apply immediately after confirmation
- Skills truncate to new maximum if age reduces cap (FR-007a)

**Rationale**:
- Clear lifecycle prevents ambiguous states
- Immutable snapshots preserve history accurately
- Sequential game play maintains narrative flow
- Explicit confirmation for age updates prevents accidents
- Separation of current/historical data simplifies queries

**Alternatives Considered**:
- Free-form game scheduling: Rejected - reduces narrative structure
- Automatic age progression: Rejected - user wants control
- Mutable historical data: Rejected - breaks historical accuracy
- Database-style versioning: Rejected - over-engineering for in-memory storage

### 11. API Design for Season and Progression Features (Added November 4, 2025)

**New Endpoints**:
```
# Season Management
POST   /api/leagues/{id}/schedule         # Generate season schedule
GET    /api/leagues/{id}/schedule         # Get current schedule with status
POST   /api/leagues/{id}/seasons/finish   # Complete current season
POST   /api/leagues/{id}/seasons/start    # Start next season
GET    /api/leagues/{id}/seasons/history  # Get past season archives
GET    /api/leagues/{id}/seasons/{num}    # Get specific historical season

# Player Progression
GET    /api/players/{id}/progression      # Get XP, level, available points, progress %
POST   /api/players/{id}/spend-skill-point # Allocate single skill point
POST   /api/players/{id}/spend-skill-points # Allocate multiple skill points

# Enhanced Game Endpoint
POST   /api/games                         # Returns game + XP awards + level-ups
```

**Response Enhancements**:
```json
// Game simulation response now includes:
{
  "game": { /* game details */ },
  "xp_awards": [
    { "player_id": "p1", "xp_earned": 85, "levels_gained": 1 }
  ],
  "level_ups": [
    { "player_id": "p1", "new_level": 5, "skill_points_awarded": 1 }
  ]
}
```

**Rationale**:
- RESTful patterns maintained
- Season endpoints nested under league (logical hierarchy)
- Progression endpoints on player resource
- Game simulation returns progression data for UI feedback
- Historical season access via collection + detail endpoints

**Alternatives Considered**:
- Separate progression service: Rejected - unnecessary separation
- WebSocket for level-up notifications: Rejected - REST sufficient for single-user
- Bulk progression endpoints: Deferred - not needed for MVP

## Technology Stack Summary

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Testing**: pytest, pytest-asyncio
- **Validation**: Pydantic v2
- **Dev Tools**: Black, Ruff, mypy

### Frontend
- **Framework**: React 18
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3
- **Testing**: Jest, React Testing Library
- **Build**: Vite
- **Dev Tools**: ESLint, Prettier

### Infrastructure
- **Containerization**: Docker, docker-compose
- **Development**: Hot reload for both frontend/backend
- **Deployment**: Multi-stage Docker builds

## Open Questions

None - all research questions resolved, including new requirements from November 4, 2025 session:
- XP/leveling system design finalized (see skill-progression-plan.md for detailed implementation)
- Season lifecycle and historical data storage patterns established
- Player value formula updated to include progression factors
- Schedule interaction model defined (Play Next Game button with status indicators)
- Skill point allocation approach confirmed (manual UI-based)
