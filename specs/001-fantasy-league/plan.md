# Implementation Plan: Dodgeball Fantasy League Core System

**Branch**: `001-fantasy-league` | **Date**: 2025-11-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fantasy-league/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a complete fantasy dodgeball league web application with player generation, team management, game simulation, and season scheduling. The system supports multi-season play with player progression (XP/leveling), skill point allocation, age-based stat changes, and historical season tracking. All data stored in-memory (no persistent database). Single-user operation with React/Tailwind frontend and Python FastAPI backend, deployed via Docker containers.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Node.js 18+ with TypeScript (frontend)
**Primary Dependencies**: FastAPI, Pydantic (backend); React 18, Tailwind CSS 3 (frontend)
**Storage**: In-memory storage (Python dictionaries/objects, no database/Redis/files)
**Testing**: pytest with coverage (backend); Jest + React Testing Library (frontend)
**Target Platform**: Linux/macOS server containers (Docker), modern web browsers
**Project Type**: Web application (separate backend API + frontend SPA)
**Performance Goals**: 
  - Game simulation: <30 seconds per game
  - Player generation: <1 minute for 50-100 players
  - Full season completion: <15 minutes
  - API response times: <200ms for non-simulation endpoints
**Constraints**: 
  - Single-user system (no authentication, no concurrent access handling)
  - All data in-memory (resets on server restart)
  - Deterministic game simulation (given same seed and stats)
**Scale/Scope**: 
  - 50-100 players per league
  - 4-8 teams per league
  - 8-12 players per team
  - Round-robin scheduling (N*(N-1) games per season for N teams)
  - Multiple seasons with historical archives

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Frontend MUST use React with Tailwind CSS (React 18 + Tailwind CSS 3 specified)
- ✅ Backend MUST use Python FastAPI (Python 3.11+ with FastAPI specified)
- ✅ Code MUST remain simple; complexity must be justified (in-memory storage, no over-engineering)
- ✅ Databases MUST use PostgreSQL if needed (N/A - in-memory storage only for this milestone)
- ✅ Deployment MUST use Docker containers (Docker + docker-compose specified)

**Status**: ✅ PASSES - All constitution requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-fantasy-league/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (completed)
├── skill-progression-plan.md  # Detailed XP/leveling design (existing)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (existing, to be updated)
├── tasks.md             # Task list (existing, to be updated in Phase 2)
└── contracts/           # Phase 1 output (to be generated)
    └── openapi.yaml     # API contract (existing, to be updated)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── models/                  # Pydantic data models
│   │   ├── __init__.py
│   │   ├── player.py            # Player, PlayerSkills, PlayerStats, PlayerProgression
│   │   ├── team.py              # Team
│   │   ├── league.py            # League, Season
│   │   ├── game.py              # Game, Schedule
│   │   └── injury.py            # Injury
│   ├── services/                # Business logic
│   │   ├── player_service.py   # Player generation, value calc, progression
│   │   ├── team_service.py     # Roster management, budget
│   │   ├── league_service.py   # League/season management
│   │   ├── game_service.py     # Game orchestration
│   │   ├── game_simulator.py   # Turn-based combat logic
│   │   ├── stats_service.py    # Statistics tracking
│   │   ├── injury_service.py   # Injury mechanics
│   │   ├── skill_progression.py # XP calculation, leveling
│   │   └── utils.py            # Shared utilities
│   ├── api/                     # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── errors.py           # Error handling middleware
│   │   ├── schemas.py          # API request/response schemas
│   │   ├── leagues.py          # League endpoints
│   │   ├── teams.py            # Team endpoints
│   │   ├── players.py          # Player endpoints
│   │   └── games.py            # Game endpoints
│   ├── storage/                 # Data persistence
│   │   └── memory_storage.py  # In-memory storage singleton
│   └── data/                    # Static data
│       └── player_names.json   # Name generation data
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── test_player_generation.py
│   │   ├── test_player_value.py
│   │   ├── test_team_budget.py
│   │   ├── test_team_roster.py
│   │   ├── test_game_mechanics.py
│   │   ├── test_injury_system.py
│   │   └── test_skill_progression.py
│   ├── integration/            # API integration tests
│   │   ├── test_leagues.py
│   │   ├── test_teams.py
│   │   ├── test_players.py
│   │   └── test_games.py
│   └── simulation/             # Game simulation tests
│       ├── test_game_determinism.py
│       └── test_game_edge_cases.py
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── pytest.ini

frontend/
├── src/
│   ├── main.tsx                # React entry point
│   ├── App.tsx                 # Root component with routing
│   ├── index.css               # Tailwind imports
│   ├── vite-env.d.ts          # Vite type definitions
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts           # Shared types (Player, Team, Game, etc.)
│   ├── services/              # API client
│   │   └── api.ts             # HTTP client + all API methods
│   ├── contexts/              # React contexts
│   │   └── LeagueContext.tsx # Global league state
│   ├── pages/                 # Page components
│   │   ├── LeaguePage.tsx    # League overview, season history
│   │   ├── PlayersPage.tsx   # Player pool browsing
│   │   ├── PlayerDetailPage.tsx # Individual player + skill allocation
│   │   ├── TeamsPage.tsx     # Team list and management
│   │   └── GamesPage.tsx     # Schedule, game simulation
│   └── components/            # Reusable components
│       ├── common/            # Shared UI components
│       │   ├── Button.tsx
│       │   ├── Card.tsx
│       │   └── Badge.tsx
│       ├── player/            # Player-related components
│       │   ├── PlayerCard.tsx
│       │   ├── PlayerList.tsx
│       │   ├── PlayerStats.tsx
│       │   ├── ProgressionBadge.tsx
│       │   └── SkillPointAllocator.tsx
│       ├── team/              # Team-related components
│       │   ├── TeamCard.tsx
│       │   ├── TeamRoster.tsx
│       │   ├── TeamBudget.tsx
│       │   └── TeamForm.tsx
│       ├── game/              # Game-related components
│       │   ├── GameSimulator.tsx
│       │   ├── GameHistory.tsx
│       │   ├── GameStats.tsx
│       │   └── GameResultsModal.tsx
│       └── league/            # League-related components
│           ├── LeagueForm.tsx
│           ├── LeagueStandings.tsx
│           ├── LeagueSchedule.tsx
│           ├── LeagueAwards.tsx
│           └── SeasonHistory.tsx
├── tests/
│   ├── setup.ts
│   ├── __mocks__/
│   │   └── fileMock.js
│   └── components/
│       ├── PlayerCard.test.tsx
│       ├── PlayerList.test.tsx
│       ├── TeamRoster.test.tsx
│       ├── TeamBudget.test.tsx
│       ├── GameSimulator.test.tsx
│       └── GameHistory.test.tsx
├── public/
│   └── images/
│       ├── avatars/           # Player avatar placeholders
│       └── team_avatars/      # Team logo placeholders
├── Dockerfile
├── nginx.conf                 # Production nginx config
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── eslint.config.js
└── jest.config.js

# Root files
docker-compose.yml             # Orchestrates backend + frontend containers
README.md                      # Project setup and running instructions
```

**Structure Decision**: Web application with separate backend API and frontend SPA. Backend follows service-oriented architecture with clear separation of models, business logic, and API handlers. Frontend uses component-based architecture with pages for routing and reusable components. In-memory storage singleton manages all data. Docker containers for both services with docker-compose for local development.

## Complexity Tracking

> **No violations - section retained for reference only**

All constitution requirements are satisfied without exceptions. The project uses React + Tailwind CSS for frontend, Python FastAPI for backend, Docker for deployment, and maintains simplicity through in-memory storage and straightforward service architecture.
