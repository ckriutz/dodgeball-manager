# Tasks: Dodgeball Fantasy League Core System

**Input**: Design documents from `/specs/001-fantasy-league/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included for critical paths as specified in the feature requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure (backend/src/models/, backend/src/services/, backend/src/api/, backend/src/storage/)
- [X] T002 Create frontend directory structure (frontend/src/components/, frontend/src/pages/, frontend/src/services/, frontend/src/types/)
- [X] T003 Initialize Python project with FastAPI dependencies in backend/requirements.txt
- [X] T004 Initialize Node.js project with React, TypeScript, Tailwind CSS in frontend/package.json
- [X] T005 [P] Configure Python linting tools (Black, Ruff, mypy) in backend/
- [X] T006 [P] Configure TypeScript and ESLint in frontend/
- [X] T007 [P] Create backend/Dockerfile for Python FastAPI service
- [X] T008 [P] Create frontend/Dockerfile for React application
- [X] T009 Create docker-compose.yml for local development orchestration
- [X] T010 [P] Setup pytest configuration in backend/pytest.ini
- [X] T011 [P] Setup Jest configuration in frontend/jest.config.js
- [X] T012 Configure Tailwind CSS in frontend/tailwind.config.js
- [X] T013 Create README.md with setup instructions at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T014 Implement in-memory storage manager singleton in backend/src/storage/memory_storage.py
- [X] T015 Create FastAPI application entry point in backend/src/main.py with CORS configuration
- [X] T016 [P] Implement error handling middleware in backend/src/api/errors.py
- [X] T017 [P] Create base Pydantic models for API responses in backend/src/api/schemas.py
- [X] T018 [P] Setup API client service structure in frontend/src/services/api.ts
- [X] T019 [P] Create React Context for league state in frontend/src/contexts/LeagueContext.tsx
- [X] T020 Create main App component with routing in frontend/src/App.tsx
- [X] T021 [P] Create common TypeScript types in frontend/src/types/index.ts
- [X] T022 [P] Implement utility functions for player value calculation in backend/src/services/utils.py
- [X] T023 [P] Create test fixtures for in-memory storage in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - League Setup and Player Generation (Priority: P1) 🎯 MVP

**Goal**: Create leagues and generate 50-100 players with random stats (age 18-20, 10 skill points distributed across 6 skills, calculated values)

**Independent Test**: Create a league, generate players, view player pool with all attributes (name, age, avatar, skills, value). All free agents are visible and browsable.

### Tests for User Story 1

- [X] T024 [P] [US1] Unit test for player value calculation formula in backend/tests/unit/test_player_value.py
- [X] T025 [P] [US1] Unit test for skill distribution validation in backend/tests/unit/test_player_generation.py
- [X] T026 [P] [US1] Integration test for league creation endpoint in backend/tests/integration/test_leagues.py
- [X] T027 [P] [US1] Integration test for player generation endpoint in backend/tests/integration/test_players.py

### Implementation for User Story 1

- [X] T028 [P] [US1] Create Player model with validation in backend/src/models/player.py
- [X] T029 [P] [US1] Create League model in backend/src/models/league.py
- [X] T030 [US1] Implement PlayerService with player generation logic in backend/src/services/player_service.py
- [X] T031 [US1] Implement LeagueService with league creation logic in backend/src/services/league_service.py
- [X] T032 [US1] Implement POST /api/leagues endpoint in backend/src/api/leagues.py
- [X] T033 [US1] Implement GET /api/leagues/{league_id} endpoint in backend/src/api/leagues.py
- [X] T034 [US1] Implement POST /api/leagues/{league_id}/players (generate players) in backend/src/api/leagues.py
- [X] T035 [US1] Implement GET /api/leagues/{league_id}/players endpoint in backend/src/api/leagues.py
- [X] T036 [P] [US1] Create PlayerCard component in frontend/src/components/player/PlayerCard.tsx
- [X] T037 [P] [US1] Create PlayerList component in frontend/src/components/player/PlayerList.tsx
- [X] T038 [P] [US1] Create LeagueForm component in frontend/src/components/league/LeagueForm.tsx
- [X] T039 [US1] Create LeaguePage with league creation and player generation in frontend/src/pages/LeaguePage.tsx
- [X] T040 [US1] Create PlayersPage for browsing player pool in frontend/src/pages/PlayersPage.tsx
- [X] T041 [US1] Add league and player API methods to frontend/src/services/api.ts
- [X] T042 [P] [US1] Component test for PlayerCard in frontend/tests/components/PlayerCard.test.tsx
- [X] T043 [P] [US1] Component test for PlayerList in frontend/tests/components/PlayerList.test.tsx

**Checkpoint**: User Story 1 complete - can create leagues, generate players, view player pool

---

## Phase 4: User Story 2 - Team Creation and Player Draft (Priority: P2)

**Goal**: Create teams with $100k budgets, draft 8-12 players from free agent pool, designate 5 starters, enforce budget constraints

**Independent Test**: Create team, view available players, add players within budget, designate starters, confirm roster limits (8-12 players, exactly 5 starters). Budget constraints prevent overspending.

### Tests for User Story 2

- [X] T044 [P] [US2] Unit test for budget validation in backend/tests/unit/test_team_budget.py
- [X] T045 [P] [US2] Unit test for roster size validation in backend/tests/unit/test_team_roster.py
- [X] T046 [P] [US2] Integration test for team creation endpoint in backend/tests/integration/test_teams.py
- [X] T047 [P] [US2] Integration test for adding player to roster in backend/tests/integration/test_teams.py
- [X] T048 [P] [US2] Integration test for designating starters in backend/tests/integration/test_teams.py

### Implementation for User Story 2

- [X] T049 [P] [US2] Create Team model with validation in backend/src/models/team.py
- [X] T050 [US2] Implement TeamService with roster management logic in backend/src/services/team_service.py
- [X] T051 [US2] Implement POST /api/teams endpoint in backend/src/api/teams.py
- [X] T052 [US2] Implement GET /api/teams/{team_id} endpoint in backend/src/api/teams.py
- [X] T053 [US2] Implement POST /api/teams/{team_id}/players (add to roster) in backend/src/api/teams.py
- [X] T054 [US2] Implement DELETE /api/teams/{team_id}/players/{player_id} in backend/src/api/teams.py
- [X] T055 [US2] Implement PATCH /api/teams/{team_id}/starters in backend/src/api/teams.py
- [X] T056 [P] [US2] Create TeamCard component in frontend/src/components/team/TeamCard.tsx
- [X] T057 [P] [US2] Create TeamRoster component in frontend/src/components/team/TeamRoster.tsx
- [X] T058 [P] [US2] Create TeamBudget component in frontend/src/components/team/TeamBudget.tsx
- [X] T059 [P] [US2] Create TeamForm component in frontend/src/components/team/TeamForm.tsx
- [X] T060 [US2] Create TeamsPage with team creation and roster management in frontend/src/pages/TeamsPage.tsx
- [X] T061 [US2] Add team API methods to frontend/src/services/api.ts
- [X] T062 [P] [US2] Component test for TeamRoster in frontend/tests/components/TeamRoster.test.tsx
- [X] T063 [P] [US2] Component test for TeamBudget in frontend/tests/components/TeamBudget.test.tsx

**Checkpoint**: User Story 2 complete - can create teams, draft players, manage rosters with budget constraints

---

## Phase 5: User Story 3 - Game Simulation and Stats Tracking (Priority: P3)

**Goal**: Simulate games between teams using dodgeball rules, player skills determine outcomes, update player stats and team records

**Independent Test**: Select two teams with complete rosters, simulate game with deterministic seed, view play-by-play results, confirm stat updates and win/loss records

### Tests for User Story 3

- [X] T064 [P] [US3] Unit test for throw outcome calculation in backend/tests/unit/test_game_mechanics.py
- [X] T065 [P] [US3] Unit test for injury probability in backend/tests/unit/test_injury_system.py
- [X] T066 [P] [US3] Simulation test with deterministic seed in backend/tests/simulation/test_game_determinism.py
- [X] T067 [P] [US3] Simulation test for edge cases in backend/tests/simulation/test_game_edge_cases.py
- [X] T068 [P] [US3] Integration test for game simulation endpoint in backend/tests/integration/test_games.py

### Implementation for User Story 3

- [X] T069 [US3] Create Game model in backend/src/models/game.py
- [X] T070 [US3] Create Injury model in backend/src/models/injury.py
- [X] T071 [US3] Implement GameSimulator with turn-based combat logic in backend/src/services/game_simulator.py
- [X] T072 [US3] Implement injury system in backend/src/services/injury_service.py
- [X] T073 [US3] Implement stat tracking and update logic in backend/src/services/stats_service.py
- [X] T074 [US3] Implement POST /api/games (create and simulate) in backend/src/api/games.py
- [X] T075 [US3] Implement GET /api/games/{game_id} endpoint in backend/src/api/games.py
- [X] T076 [US3] Implement GET /api/games (list/history) endpoint in backend/src/api/games.py
- [X] T077 [P] [US3] Create GameSimulator component in frontend/src/components/game/GameSimulator.tsx
- [X] T078 [P] [US3] Create GameHistory component in frontend/src/components/game/GameHistory.tsx
- [X] T079 [P] [US3] Create GameStats component in frontend/src/components/game/GameStats.tsx
- [X] T080 [P] [US3] Create PlayerStats component in frontend/src/components/player/PlayerStats.tsx
- [X] T081 [US3] Create GamesPage with game simulation interface in frontend/src/pages/GamesPage.tsx
- [X] T082 [US3] Add game API methods to frontend/src/services/api.ts
- [X] T083 [P] [US3] Component test for GameSimulator in frontend/tests/components/GameSimulator.test.tsx
- [X] T084 [P] [US3] Component test for GameHistory in frontend/tests/components/GameHistory.test.tsx

**Checkpoint**: User Story 3 complete - can simulate games, view play-by-play, track stats

---

## Phase 6: User Story 4 - League Schedule and Season Management (Priority: P4)

**Goal**: Generate schedules with game status tracking, track season-long performance including standings/MVPs/awards. Implement XP-based skill progression with manual skill point allocation. Support multi-season play with age progression and historical season archives.

**Independent Test**: Create schedule for all teams, simulate multiple games using "Play Next Game" button, view updated standings and cumulative stats, allocate skill points for leveled players, complete season with age updates, view historical season data. Delivers a complete multi-season league experience.

### Tests for User Story 4

- [X] T085 [P] [US4] Unit test for round-robin schedule generation in backend/tests/unit/test_schedule.py
- [X] T086 [P] [US4] Unit test for standings calculation in backend/tests/unit/test_standings.py
- [X] T087 [P] [US4] Unit test for MVP/awards calculation in backend/tests/unit/test_awards.py
- [X] T088 [P] [US4] Unit test for XP calculation and leveling logic in backend/tests/unit/test_skill_progression.py
- [X] T089 [P] [US4] Unit test for age progression and stat penalties in backend/tests/unit/test_age_progression.py
- [X] T090 [P] [US4] Integration test for schedule generation in backend/tests/integration/test_schedule.py
- [X] T091 [P] [US4] Integration test for season completion and archiving in backend/tests/integration/test_seasons.py

### Implementation for User Story 4

#### Backend - Data Models
- [X] T092 [P] [US4] Add Season model with lifecycle states in backend/src/models/league.py
- [X] T093 [P] [US4] Add Schedule model with game status tracking in backend/src/models/game.py
- [X] T094 [P] [US4] Add SeasonArchive model for historical records in backend/src/models/league.py
- [X] T095 [US4] Update Player model with progression fields (experience_points, level, available_skill_points) in backend/src/models/player.py
- [X] T096 [US4] Update Game model to track per-player XP awards in backend/src/models/game.py

#### Backend - Services
- [X] T097 [US4] Implement ScheduleService with round-robin algorithm and status tracking in backend/src/services/schedule_service.py
- [X] T098 [US4] Implement StandingsService with ranking logic in backend/src/services/standings_service.py
- [X] T099 [US4] Implement AwardsService with MVP calculation in backend/src/services/awards_service.py
- [X] T100 [US4] Implement SkillProgressionService with XP calculation and leveling in backend/src/services/skill_progression.py
- [X] T101 [US4] Implement AgeProgressionService with stat penalties in backend/src/services/age_service.py
- [X] T102 [US4] Implement SeasonService with lifecycle management and archiving in backend/src/services/season_service.py
- [X] T103 [US4] Update GameService to award XP after simulation in backend/src/services/game_service.py
- [X] T104 [US4] Update PlayerService to handle skill point spending in backend/src/services/player_service.py
- [X] T105 [US4] Update player value calculation formula to include level and games_played in backend/src/services/utils.py

#### Backend - API Endpoints
- [X] T106 [US4] Implement POST /api/leagues/{league_id}/schedule in backend/src/api/leagues.py
- [X] T107 [US4] Implement GET /api/leagues/{league_id}/schedule (with status indicators) in backend/src/api/leagues.py
- [X] T108 [US4] Implement GET /api/leagues/{league_id}/standings in backend/src/api/leagues.py
- [X] T109 [US4] Implement GET /api/leagues/{league_id}/awards in backend/src/api/leagues.py
- [X] T110 [US4] Implement POST /api/leagues/{league_id}/seasons/finish in backend/src/api/leagues.py
- [X] T111 [US4] Implement POST /api/leagues/{league_id}/seasons/start in backend/src/api/leagues.py
- [X] T112 [US4] Implement GET /api/leagues/{league_id}/seasons/history in backend/src/api/leagues.py
- [X] T113 [US4] Implement GET /api/players/{player_id}/progression in backend/src/api/players.py
- [X] T114 [US4] Implement POST /api/players/{player_id}/spend-skill-point in backend/src/api/players.py
- [X] T115 [US4] Implement POST /api/players/{player_id}/spend-skill-points in backend/src/api/players.py
- [X] T116 [US4] Update POST /api/games to return XP awards and level-ups in backend/src/api/games.py

#### Frontend - Components
- [X] T117 [P] [US4] Create ProgressionBadge component in frontend/src/components/player/ProgressionBadge.tsx
- [X] T118 [P] [US4] Create SkillPointAllocator component in frontend/src/components/player/SkillPointAllocator.tsx
- [X] T119 [P] [US4] Create LeagueStandings component in frontend/src/components/league/LeagueStandings.tsx
- [X] T120 [P] [US4] Create LeagueSchedule component with status indicators in frontend/src/components/league/LeagueSchedule.tsx
- [X] T121 [P] [US4] Create LeagueAwards component in frontend/src/components/league/LeagueAwards.tsx
- [X] T122 [P] [US4] Create SeasonHistory component in frontend/src/components/league/SeasonHistory.tsx
- [X] T123 [P] [US4] Create SeasonCompletionModal component in frontend/src/components/league/SeasonCompletionModal.tsx
- [X] T124 [P] [US4] Update GameResultsModal to show level-up notifications in frontend/src/components/game/GameResultsModal.tsx

#### Frontend - Pages & Integration
- [X] T125 [US4] Update PlayerDetailPage to show progression and skill allocation in frontend/src/pages/PlayerDetailPage.tsx
- [X] T126 [US4] Update LeaguePage to include standings, schedule, and season history tabs in frontend/src/pages/LeaguePage.tsx
- [X] T127 [US4] Update GamesPage with "Play Next Game" button and schedule status in frontend/src/pages/GamesPage.tsx
- [X] T128 [US4] Add season and progression API methods to frontend/src/services/api.ts
- [X] T129 [US4] Update PlayerCard to show progression badge when skill points available in frontend/src/components/player/PlayerCard.tsx
- [X] T130 [US4] Update TypeScript types for Season, Schedule, PlayerProgression in frontend/src/types/index.ts

#### Frontend - Tests
- [ ] T131 [P] [US4] Component test for ProgressionBadge in frontend/tests/components/ProgressionBadge.test.tsx
- [ ] T132 [P] [US4] Component test for SkillPointAllocator in frontend/tests/components/SkillPointAllocator.test.tsx
- [ ] T133 [P] [US4] Component test for LeagueStandings in frontend/tests/components/LeagueStandings.test.tsx
- [ ] T134 [P] [US4] Component test for SeasonHistory in frontend/tests/components/SeasonHistory.test.tsx

**Checkpoint**: User Story 4 complete - full multi-season management with XP/leveling, skill progression, age updates, and historical archives

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T135 [P] Add comprehensive error handling across all backend endpoints
- [ ] T136 [P] Add loading states and error displays to all frontend components
- [ ] T137 [P] Implement responsive design for mobile viewing in frontend/
- [ ] T138 [P] Add API documentation with Swagger UI configuration in backend/src/main.py
- [ ] T139 [P] Add data export functionality (JSON) in backend/src/api/export.py
- [ ] T140 [P] Performance optimization for large player pools
- [ ] T141 [P] Add visual feedback for budget constraints in frontend UI
- [ ] T142 [P] Add visual feedback for XP gain and level-up animations
- [ ] T143 Run quickstart.md validation end-to-end
- [ ] T144 [P] Update README.md with final deployment instructions
- [ ] T145 [P] Create developer documentation in docs/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Integrates with US1 (needs players)
  - User Story 3 (P3): Can start after Foundational - Integrates with US1 & US2 (needs teams)
  - User Story 4 (P4): Can start after Foundational - Integrates with US1, US2, US3 (needs games)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Foundation for all other stories
- **User Story 2 (P2)**: Should complete US1 first (needs player pool) - Can be independently tested
- **User Story 3 (P3)**: Should complete US1 & US2 first (needs teams with rosters) - Can be independently tested
- **User Story 4 (P4)**: Should complete US1, US2, US3 first (needs game simulation) - Can be independently tested

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints/API routes
- Backend endpoints before frontend integration
- Core implementation before UI polish
- Story complete before moving to next priority

### Parallel Opportunities

#### Phase 1 (Setup) - 6 parallel tasks
- T005 (Backend linting) + T006 (Frontend linting)
- T007 (Backend Dockerfile) + T008 (Frontend Dockerfile)
- T010 (pytest config) + T011 (Jest config)

#### Phase 2 (Foundational) - 7 parallel tasks
- T016 (Error handling) + T017 (Base schemas) + T018 (API client) + T019 (React Context) + T021 (Types) + T022 (Utils) + T023 (Test fixtures)

#### User Story 1 - 4 parallel test tasks, 2 parallel model tasks, 6 parallel component tasks
- Tests: T024 + T025 + T026 + T027
- Models: T028 (Player) + T029 (League)
- Components: T036 + T037 + T038 + T042 + T043

#### User Story 2 - 5 parallel test tasks, 6 parallel component tasks
- Tests: T044 + T045 + T046 + T047 + T048
- Components: T056 + T057 + T058 + T059 + T062 + T063

#### User Story 3 - 5 parallel test tasks, 2 parallel model tasks, 6 parallel component tasks
- Tests: T064 + T065 + T066 + T067 + T068
- Models: T069 (Game) + T070 (Injury)
- Components: T077 + T078 + T079 + T080 + T083 + T084

#### User Story 4 - 7 parallel test tasks, 4 parallel model tasks, 8 parallel component tasks
- Tests: T085 + T086 + T087 + T088 + T089 + T090 + T091
- Models: T092 + T093 + T094 + T095 + T096
- Components: T117 + T118 + T119 + T120 + T121 + T122 + T123 + T124
- Frontend Tests: T131 + T132 + T133 + T134

#### Phase 7 (Polish) - 10 parallel tasks
- T135 + T136 + T137 + T138 + T139 + T140 + T141 + T142 + T144 + T145

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T024: "Unit test for player value calculation formula in backend/tests/unit/test_player_value.py"
Task T025: "Unit test for skill distribution validation in backend/tests/unit/test_player_generation.py"
Task T026: "Integration test for league creation endpoint in backend/tests/integration/test_leagues.py"
Task T027: "Integration test for player generation endpoint in backend/tests/integration/test_players.py"

# Launch both models together:
Task T028: "Create Player model with validation in backend/src/models/player.py"
Task T029: "Create League model in backend/src/models/league.py"

# Launch all frontend components together:
Task T036: "Create PlayerCard component in frontend/src/components/player/PlayerCard.tsx"
Task T037: "Create PlayerList component in frontend/src/components/player/PlayerList.tsx"
Task T038: "Create LeagueForm component in frontend/src/components/league/LeagueForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (13 tasks)
2. Complete Phase 2: Foundational (10 tasks) - CRITICAL
3. Complete Phase 3: User Story 1 (20 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Create league via API
   - Generate 75 players
   - View player pool in UI
   - Verify all stats calculated correctly
5. Deploy/demo if ready

**Total MVP**: 43 tasks to deliver league creation and player generation

### Incremental Delivery

1. **Foundation (Phases 1-2)**: 23 tasks → Foundation ready
2. **MVP (+ Phase 3)**: +20 tasks → League & Players working (43 total)
3. **Teams (+ Phase 4)**: +20 tasks → Team drafting working (63 total)
4. **Games (+ Phase 5)**: +21 tasks → Game simulation working (84 total)
5. **Season (+ Phase 6)**: +50 tasks → Full season management with XP/leveling (134 total)
6. **Polish (+ Phase 7)**: +11 tasks → Production ready (145 total)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Story 1 (20 tasks) - Priority P1
- **Developer B**: User Story 2 (20 tasks) - Priority P2
- **Developer C**: User Story 3 (21 tasks) - Priority P3

All can work simultaneously since foundational work is complete. User Story 4 and Polish follow sequentially or are distributed based on completion.

---

## Task Summary

**Total Tasks**: 145

**By Phase**:
- Phase 1 (Setup): 13 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (User Story 1): 20 tasks
- Phase 4 (User Story 2): 20 tasks
- Phase 5 (User Story 3): 21 tasks
- Phase 6 (User Story 4): 50 tasks
- Phase 7 (Polish): 11 tasks

**Test Tasks**: 31 (21% test coverage tasks)
**Backend Tasks**: ~75 (models, services, API endpoints, tests)
**Frontend Tasks**: ~58 (components, pages, tests)
**Infrastructure Tasks**: ~12 (setup, config, Docker)

**Parallel Opportunities**: 70 tasks marked [P] can run in parallel

**MVP Scope**: 43 tasks (Phases 1-3) delivers User Story 1

---

## Notes

- [P] tasks = different files, no dependencies - can be parallelized
- [US1/US2/US3/US4] labels map tasks to specific user stories for traceability
- Each user story should be independently testable at its checkpoint
- Tests should fail before implementing corresponding functionality
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are absolute from repository root
- Backend uses Python/FastAPI, Frontend uses React/TypeScript
- In-memory storage means no database migrations needed
- Docker containers for deployment per constitution requirements
