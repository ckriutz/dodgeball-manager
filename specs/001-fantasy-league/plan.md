# Implementation Plan: Dodgeball Fantasy League Core System

**Branch**: `001-fantasy-league` | **Date**: October 24, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fantasy-league/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a web application for a dodgeball fantasy league with three core components: Player Management (50-100 randomly generated players with stats and values), Team Management (teams with $100k budgets drafting 8-12 players), and Game Simulation (deterministic dodgeball game engine using player stats). Initial milestone uses in-memory storage, single-user mode, and focuses on core gameplay mechanics. Technical approach: React + Tailwind frontend, Python FastAPI backend, containerized deployment.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Node.js 18+ with TypeScript (frontend)  
**Primary Dependencies**: FastAPI (backend), React 18, Tailwind CSS 3 (frontend)  
**Storage**: In-memory only for this milestone (no database)  
**Testing**: pytest (backend), Jest + React Testing Library (frontend)  
**Target Platform**: Web application (browser-based), Docker containers for deployment
**Project Type**: Web application (separate frontend and backend)  
**Performance Goals**: League/player generation <1min, team draft <5min, game simulation <30sec  
**Constraints**: Single-user mode, deterministic simulation with seed, no persistence  
**Scale/Scope**: 50-100 players, multiple teams per league, sequential game simulation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Frontend MUST use React with Tailwind CSS - **COMPLIANT**: Using React 18 with Tailwind CSS 3
- ✅ Backend MUST use Python FastAPI - **COMPLIANT**: Using FastAPI for REST API
- ✅ Code MUST remain simple; complexity must be justified - **COMPLIANT**: In-memory storage, no auth, single-user keeps initial implementation simple
- ⚠️ Databases MUST use PostgreSQL if needed - **N/A**: No database for this milestone (in-memory only per FR-033)
- ✅ Deployment MUST use Docker containers - **COMPLIANT**: Docker-based deployment planned

**Gate Status**: ✅ PASS - All applicable requirements met

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/              # Domain entities (Player, Team, League, Game, Injury)
│   ├── services/            # Business logic (PlayerService, TeamService, GameSimulator)
│   ├── api/                 # FastAPI routes and endpoints
│   │   ├── players.py
│   │   ├── teams.py
│   │   ├── leagues.py
│   │   └── games.py
│   ├── storage/             # In-memory storage manager
│   └── main.py              # FastAPI application entry point
├── tests/
│   ├── unit/                # Unit tests for services and models
│   ├── integration/         # API endpoint tests
│   └── simulation/          # Game simulation tests
├── Dockerfile
└── requirements.txt

frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── player/          # PlayerCard, PlayerList, PlayerStats
│   │   ├── team/            # TeamCard, TeamRoster, TeamBudget
│   │   ├── league/          # LeagueStandings, LeagueSettings
│   │   └── game/            # GameSimulator, GameHistory, GameStats
│   ├── pages/               # Page-level components
│   │   ├── LeaguePage.tsx
│   │   ├── PlayersPage.tsx
│   │   ├── TeamsPage.tsx
│   │   └── GamesPage.tsx
│   ├── services/            # API client services
│   │   └── api.ts
│   ├── types/               # TypeScript type definitions
│   └── App.tsx              # Main application component
├── tests/
│   ├── components/          # Component tests
│   └── integration/         # E2E tests
├── Dockerfile
├── package.json
└── tailwind.config.js

docker-compose.yml           # Orchestration for local development
README.md                    # Setup and run instructions
```

**Structure Decision**: Web application structure selected based on React frontend + FastAPI backend requirements from constitution. Separation allows independent scaling and development of UI and API layers. In-memory storage simplifies backend by eliminating database layer for this milestone.

## Complexity Tracking

> **No violations requiring justification** - All constitution requirements are met without compromise.

## Phase 0: Research Complete ✅

**Output**: [research.md](./research.md)

**Key Decisions Made**:
1. **Player Value Formula**: Weighted skill sum with age discount (skills × $100 × age_factor)
2. **Game Simulation**: Turn-based probabilistic combat with stat-based outcomes
3. **Storage Strategy**: Singleton in-memory storage manager with typed collections
4. **Injury Mechanics**: 5% probability on hits, 3 severity levels, time-based healing
5. **Schedule Algorithm**: Round-robin tournament with optional repeat rounds
6. **State Management**: React Context API for global state
7. **API Design**: RESTful with resource-based endpoints
8. **Testing Strategy**: Multi-layered (unit, simulation, integration, component)

**Technology Stack**:
- Backend: Python 3.11+, FastAPI 0.104+, pytest, Pydantic v2
- Frontend: React 18, TypeScript 5+, Tailwind CSS 3, Vite, Jest
- Infrastructure: Docker, docker-compose

All NEEDS CLARIFICATION items resolved. No open research questions.

## Phase 1: Design & Contracts Complete ✅

**Outputs**:
- [data-model.md](./data-model.md) - Entity definitions and relationships
- [contracts/openapi.yaml](./contracts/openapi.yaml) - REST API specification
- [quickstart.md](./quickstart.md) - Setup and usage guide
- [.github/copilot-instructions.md](../../.github/copilot-instructions.md) - Agent context updated

**Data Model Summary**:
- 5 core entities: Player, Team, League, Game, Injury
- All validation rules from functional requirements mapped
- State transitions defined for each entity
- Calculated fields specified (value, effective_skills, standings)
- In-memory indexes designed for O(1) lookups

**API Contracts Summary**:
- 15 REST endpoints covering all user stories
- Full OpenAPI 3.1 specification with schemas
- Request/response examples for all operations
- Error responses defined
- Resource-based URL structure

**Agent Context Update**:
- GitHub Copilot context file created
- Technologies: Python 3.11+, TypeScript, FastAPI, React 18, Tailwind CSS 3
- Project type: Web application (frontend + backend)
- Storage: In-memory only for this milestone

## Constitution Re-check (Post-Design) ✅

- ✅ Frontend uses React with Tailwind CSS - **CONFIRMED**: React 18 + Tailwind CSS 3
- ✅ Backend uses Python FastAPI - **CONFIRMED**: FastAPI with async endpoints
- ✅ Code remains simple - **CONFIRMED**: No over-engineering, YAGNI principles applied
- ✅ Database would use PostgreSQL - **N/A**: In-memory only, no database this milestone
- ✅ Deployment uses Docker - **CONFIRMED**: Dockerfile for both services, docker-compose orchestration

**Final Gate Status**: ✅✅ PASS - Design maintains constitution compliance

## Phase 2: Task Breakdown

**Status**: ⏳ NOT STARTED - Run `/speckit.tasks` to generate task breakdown

The planning phase is complete. The next step is to run `/speckit.tasks` to break down the implementation into concrete development tasks based on the user stories and technical design.

## Summary

**Feature**: Dodgeball Fantasy League Core System  
**Branch**: 001-fantasy-league  
**Status**: Planning Complete, Ready for Task Breakdown

**What Was Delivered**:
1. ✅ Technical context and architecture decisions
2. ✅ Constitution compliance verification (passed)
3. ✅ Research document with 8 key design decisions
4. ✅ Data model with 5 entities and relationships
5. ✅ OpenAPI contract with 15 REST endpoints
6. ✅ Quickstart guide for developers
7. ✅ Agent context updated (GitHub Copilot)

**Next Command**: `/speckit.tasks` to create implementation tasks

**Key Technical Choices**:
- **Architecture**: Separate React frontend + FastAPI backend
- **Storage**: In-memory (no database) for simplicity
- **State**: React Context API (no Redux)
- **Testing**: Multi-layered (80%+ coverage target)
- **Deployment**: Docker containers with docker-compose

**Performance Targets**:
- League/player generation: <1 minute
- Team draft: <5 minutes  
- Game simulation: <30 seconds

**Scope Boundaries**:
- ✅ Player generation with stats and values
- ✅ Team creation and roster management
- ✅ Game simulation with dodgeball rules
- ✅ Schedule and standings tracking
- ❌ User authentication (future)
- ❌ Persistent storage (future)
- ❌ Multi-user support (future)
