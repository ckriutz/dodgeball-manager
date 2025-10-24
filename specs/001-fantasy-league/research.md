# Research: Dodgeball Fantasy League Core System

**Feature**: 001-fantasy-league  
**Date**: October 24, 2025  
**Phase**: 0 - Outline & Research

## Research Questions & Decisions

### 1. Player Value Calculation Formula

**Decision**: Use weighted skill sum with age discount factor

**Formula**:
```
base_value = sum(all_skills) * 100
age_factor = 1.0 if age < 30 else max(0.5, 1.0 - ((age - 30) * 0.05))
player_value = int(base_value * age_factor)
```

**Rationale**:
- Simple formula based on total skill points (0-600 range for 6 skills)
- Each skill point worth $100 in base value
- No age penalty until 30, then 5% reduction per year
- Floor of 50% at extreme ages prevents zero value
- Integer-only values per FR-004a

**Alternatives Considered**:
- Position-specific weights: Rejected - no positions in dodgeball
- Non-linear scaling: Rejected - adds complexity without clear benefit
- Market-driven pricing: Rejected - out of scope for single-user milestone

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

None - all research questions resolved. Ready for Phase 1 design.
