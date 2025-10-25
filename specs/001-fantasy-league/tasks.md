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
- [ ] T022 [P] Implement utility functions for player value calculation in backend/src/services/utils.py
- [ ] T023 [P] Create test fixtures for in-memory storage in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - League Setup and Player Generation (Priority: P1) 🎯 MVP

**Goal**: Create leagues and generate 50-100 players with random stats (age 18-20, 10 skill points distributed across 6 skills, calculated values)

**Independent Test**: Create a league, generate players, view player pool with all attributes (name, age, avatar, skills, value). All free agents are visible and browsable.

### Tests for User Story 1

- [ ] T024 [P] [US1] Unit test for player value calculation formula in backend/tests/unit/test_player_value.py
- [ ] T025 [P] [US1] Unit test for skill distribution validation in backend/tests/unit/test_player_generation.py
- [ ] T026 [P] [US1] Integration test for league creation endpoint in backend/tests/integration/test_leagues.py
- [ ] T027 [P] [US1] Integration test for player generation endpoint in backend/tests/integration/test_players.py

### Implementation for User Story 1

- [ ] T028 [P] [US1] Create Player model with validation in backend/src/models/player.py
- [ ] T029 [P] [US1] Create League model in backend/src/models/league.py
- [ ] T030 [US1] Implement PlayerService with player generation logic in backend/src/services/player_service.py
- [ ] T031 [US1] Implement LeagueService with league creation logic in backend/src/services/league_service.py
- [ ] T032 [US1] Implement POST /api/leagues endpoint in backend/src/api/leagues.py
- [ ] T033 [US1] Implement GET /api/leagues/{league_id} endpoint in backend/src/api/leagues.py
- [ ] T034 [US1] Implement POST /api/leagues/{league_id}/players (generate players) in backend/src/api/leagues.py
- [ ] T035 [US1] Implement GET /api/leagues/{league_id}/players endpoint in backend/src/api/leagues.py
- [ ] T036 [P] [US1] Create PlayerCard component in frontend/src/components/player/PlayerCard.tsx
- [ ] T037 [P] [US1] Create PlayerList component in frontend/src/components/player/PlayerList.tsx
- [ ] T038 [P] [US1] Create LeagueForm component in frontend/src/components/league/LeagueForm.tsx
- [ ] T039 [US1] Create LeaguePage with league creation and player generation in frontend/src/pages/LeaguePage.tsx
- [ ] T040 [US1] Create PlayersPage for browsing player pool in frontend/src/pages/PlayersPage.tsx
- [ ] T041 [US1] Add league and player API methods to frontend/src/services/api.ts
- [ ] T042 [P] [US1] Component test for PlayerCard in frontend/tests/components/PlayerCard.test.tsx
- [ ] T043 [P] [US1] Component test for PlayerList in frontend/tests/components/PlayerList.test.tsx

**Checkpoint**: User Story 1 complete - can create leagues, generate players, view player pool

---

## Phase 4: User Story 2 - Team Creation and Player Draft (Priority: P2)

**Goal**: Create teams with $100k budgets, draft 8-12 players from free agent pool, designate 5 starters, enforce budget constraints

**Independent Test**: Create team, view available players, add players within budget, designate starters, confirm roster limits (8-12 players, exactly 5 starters). Budget constraints prevent overspending.

### Tests for User Story 2

- [ ] T044 [P] [US2] Unit test for budget validation in backend/tests/unit/test_team_budget.py
- [ ] T045 [P] [US2] Unit test for roster size validation in backend/tests/unit/test_team_roster.py
- [ ] T046 [P] [US2] Integration test for team creation endpoint in backend/tests/integration/test_teams.py
- [ ] T047 [P] [US2] Integration test for adding player to roster in backend/tests/integration/test_teams.py
- [ ] T048 [P] [US2] Integration test for designating starters in backend/tests/integration/test_teams.py

### Implementation for User Story 2

- [ ] T049 [P] [US2] Create Team model with validation in backend/src/models/team.py
- [ ] T050 [US2] Implement TeamService with roster management logic in backend/src/services/team_service.py
- [ ] T051 [US2] Implement POST /api/teams endpoint in backend/src/api/teams.py
- [ ] T052 [US2] Implement GET /api/teams/{team_id} endpoint in backend/src/api/teams.py
- [ ] T053 [US2] Implement POST /api/teams/{team_id}/players (add to roster) in backend/src/api/teams.py
- [ ] T054 [US2] Implement DELETE /api/teams/{team_id}/players/{player_id} in backend/src/api/teams.py
- [ ] T055 [US2] Implement PATCH /api/teams/{team_id}/starters in backend/src/api/teams.py
- [ ] T056 [P] [US2] Create TeamCard component in frontend/src/components/team/TeamCard.tsx
- [ ] T057 [P] [US2] Create TeamRoster component in frontend/src/components/team/TeamRoster.tsx
- [ ] T058 [P] [US2] Create TeamBudget component in frontend/src/components/team/TeamBudget.tsx
- [ ] T059 [P] [US2] Create TeamForm component in frontend/src/components/team/TeamForm.tsx
- [ ] T060 [US2] Create TeamsPage with team creation and roster management in frontend/src/pages/TeamsPage.tsx
- [ ] T061 [US2] Add team API methods to frontend/src/services/api.ts
- [ ] T062 [P] [US2] Component test for TeamRoster in frontend/tests/components/TeamRoster.test.tsx
- [ ] T063 [P] [US2] Component test for TeamBudget in frontend/tests/components/TeamBudget.test.tsx

**Checkpoint**: User Story 2 complete - can create teams, draft players, manage rosters with budget constraints

---

## Phase 5: User Story 3 - Game Simulation and Stats Tracking (Priority: P3)

**Goal**: Simulate games between teams using dodgeball rules, player skills determine outcomes, update player stats and team records

**Independent Test**: Select two teams with complete rosters, simulate game with deterministic seed, view play-by-play results, confirm stat updates and win/loss records

### Tests for User Story 3

- [ ] T064 [P] [US3] Unit test for throw outcome calculation in backend/tests/unit/test_game_mechanics.py
- [ ] T065 [P] [US3] Unit test for injury probability in backend/tests/unit/test_injury_system.py
- [ ] T066 [P] [US3] Simulation test with deterministic seed in backend/tests/simulation/test_game_determinism.py
- [ ] T067 [P] [US3] Simulation test for edge cases in backend/tests/simulation/test_game_edge_cases.py
- [ ] T068 [P] [US3] Integration test for game simulation endpoint in backend/tests/integration/test_games.py

### Implementation for User Story 3

- [ ] T069 [P] [US3] Create Game model in backend/src/models/game.py
- [ ] T070 [P] [US3] Create Injury model in backend/src/models/injury.py
- [ ] T071 [US3] Implement GameSimulator with turn-based combat logic in backend/src/services/game_simulator.py
- [ ] T072 [US3] Implement injury system in backend/src/services/injury_service.py
- [ ] T073 [US3] Implement stat tracking and update logic in backend/src/services/stats_service.py
- [ ] T074 [US3] Implement POST /api/games (create and simulate) in backend/src/api/games.py
- [ ] T075 [US3] Implement GET /api/games/{game_id} endpoint in backend/src/api/games.py
- [ ] T076 [US3] Implement GET /api/games (list/history) endpoint in backend/src/api/games.py
- [ ] T077 [P] [US3] Create GameSimulator component in frontend/src/components/game/GameSimulator.tsx
- [ ] T078 [P] [US3] Create GameHistory component in frontend/src/components/game/GameHistory.tsx
- [ ] T079 [P] [US3] Create GameStats component in frontend/src/components/game/GameStats.tsx
- [ ] T080 [P] [US3] Create PlayerStats component in frontend/src/components/player/PlayerStats.tsx
- [ ] T081 [US3] Create GamesPage with game simulation interface in frontend/src/pages/GamesPage.tsx
- [ ] T082 [US3] Add game API methods to frontend/src/services/api.ts
- [ ] T083 [P] [US3] Component test for GameSimulator in frontend/tests/components/GameSimulator.test.tsx
- [ ] T084 [P] [US3] Component test for GameHistory in frontend/tests/components/GameHistory.test.tsx

**Checkpoint**: User Story 3 complete - can simulate games, view play-by-play, track stats

---

## Phase 6: User Story 4 - League Schedule and Season Management (Priority: P4)

**Goal**: Generate schedules, simulate multiple games in sequence, view standings ranked by wins/losses, track MVPs and statistical leaders

**Independent Test**: Create schedule for all teams, simulate multiple games, view updated standings and cumulative stats, verify MVP tracking

### Tests for User Story 4

- [ ] T085 [P] [US4] Unit test for round-robin schedule generation in backend/tests/unit/test_schedule.py
- [ ] T086 [P] [US4] Unit test for standings calculation in backend/tests/unit/test_standings.py
- [ ] T087 [P] [US4] Unit test for MVP/awards calculation in backend/tests/unit/test_awards.py
- [ ] T088 [P] [US4] Integration test for schedule generation in backend/tests/integration/test_schedule.py

### Implementation for User Story 4

- [ ] T089 [US4] Implement ScheduleService with round-robin algorithm in backend/src/services/schedule_service.py
- [ ] T090 [US4] Implement StandingsService with ranking logic in backend/src/services/standings_service.py
- [ ] T091 [US4] Implement AwardsService with MVP calculation in backend/src/services/awards_service.py
- [ ] T092 [US4] Implement POST /api/leagues/{league_id}/schedule in backend/src/api/leagues.py
- [ ] T093 [US4] Implement GET /api/leagues/{league_id}/standings in backend/src/api/leagues.py
- [ ] T094 [US4] Implement GET /api/leagues/{league_id}/awards endpoint in backend/src/api/leagues.py
- [ ] T095 [P] [US4] Create LeagueStandings component in frontend/src/components/league/LeagueStandings.tsx
- [ ] T096 [P] [US4] Create LeagueSchedule component in frontend/src/components/league/LeagueSchedule.tsx
- [ ] T097 [P] [US4] Create LeagueAwards component in frontend/src/components/league/LeagueAwards.tsx
- [ ] T098 [US4] Update LeaguePage to include standings and awards in frontend/src/pages/LeaguePage.tsx
- [ ] T099 [US4] Add schedule and standings API methods to frontend/src/services/api.ts
- [ ] T100 [P] [US4] Component test for LeagueStandings in frontend/tests/components/LeagueStandings.test.tsx

**Checkpoint**: User Story 4 complete - full season management with schedules, standings, and awards

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T101 [P] Add comprehensive error handling across all backend endpoints
- [ ] T102 [P] Add loading states and error displays to all frontend components
- [ ] T103 [P] Implement responsive design for mobile viewing in frontend/
- [ ] T104 [P] Add API documentation with Swagger UI configuration in backend/src/main.py
- [ ] T105 [P] Create age progression system (players age after each season) in backend/src/services/age_service.py
- [ ] T106 [P] Implement skill improvement after games in backend/src/services/skill_progression.py
- [ ] T107 [P] Add data export functionality (JSON) in backend/src/api/export.py
- [ ] T108 [P] Performance optimization for large player pools
- [ ] T109 [P] Add visual feedback for budget constraints in frontend UI
- [ ] T110 Run quickstart.md validation end-to-end
- [ ] T111 [P] Update README.md with final deployment instructions
- [ ] T112 [P] Create developer documentation in docs/

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

#### User Story 4 - 4 parallel test tasks, 3 parallel component tasks
- Tests: T085 + T086 + T087 + T088
- Components: T095 + T096 + T097 + T100

#### Phase 7 (Polish) - 10 parallel tasks
- T101 + T102 + T103 + T104 + T105 + T106 + T107 + T108 + T109 + T111 + T112

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
5. **Season (+ Phase 6)**: +16 tasks → Full season management (100 total)
6. **Polish (+ Phase 7)**: +12 tasks → Production ready (112 total)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Story 1 (20 tasks) - Priority P1
- **Developer B**: User Story 2 (20 tasks) - Priority P2
- **Developer C**: User Story 3 (21 tasks) - Priority P3

All can work simultaneously since foundational work is complete. User Story 4 and Polish follow sequentially or are distributed based on completion.

---

## Task Summary

**Total Tasks**: 112

**By Phase**:
- Phase 1 (Setup): 13 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (User Story 1): 20 tasks
- Phase 4 (User Story 2): 20 tasks
- Phase 5 (User Story 3): 21 tasks
- Phase 6 (User Story 4): 16 tasks
- Phase 7 (Polish): 12 tasks

**Test Tasks**: 20 (18% test coverage tasks)
**Backend Tasks**: ~55 (models, services, API endpoints, tests)
**Frontend Tasks**: ~45 (components, pages, tests)
**Infrastructure Tasks**: ~12 (setup, config, Docker)

**Parallel Opportunities**: 47 tasks marked [P] can run in parallel

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
