# Quickstart Guide: Dodgeball Fantasy League

**Feature**: 001-fantasy-league  
**Date**: October 24, 2025

## Prerequisites

- Docker & Docker Compose installed
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

## Quick Start (Docker)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd dodgeball-manager
git checkout 001-fantasy-league
```

### 2. Start All Services
```bash
docker-compose up --build
```

This starts:
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000
- API Docs: http://localhost:8000/docs

### 3. Verify Services
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
open http://localhost:3000
```

## Local Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server (with hot reload)
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm test

# Start development server (with hot reload)
npm run dev
```

Frontend will be available at http://localhost:3000

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## User Workflow

### 1. Create a League
```bash
curl -X POST http://localhost:8000/api/leagues \
  -H "Content-Type: application/json" \
  -d '{"name": "My First League", "player_count": 75}'
```

Response includes `league_id`.

### 2. Generate Players
```bash
curl -X POST http://localhost:8000/api/leagues/{league_id}/players
```

This creates 50-100 players with random stats.

### 3. View Available Players
```bash
curl http://localhost:8000/api/leagues/{league_id}/players?free_agents_only=true
```

### 4. Create a Team
```bash
curl -X POST http://localhost:8000/api/teams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thunder Dodgers",
    "description": "Fast team",
    "logo": "logo-1",
    "league_id": "{league_id}"
  }'
```

Response includes `team_id` and initial budget of $100,000.

### 5. Add Players to Roster
```bash
curl -X POST http://localhost:8000/api/teams/{team_id}/players \
  -H "Content-Type: application/json" \
  -d '{"player_id": "{player_id}"}'
```

Repeat until you have 8-12 players within budget.

### 6. Designate Starters
```bash
curl -X PATCH http://localhost:8000/api/teams/{team_id}/starters \
  -H "Content-Type: application/json" \
  -d '{
    "starter_ids": [
      "{player_id_1}",
      "{player_id_2}",
      "{player_id_3}",
      "{player_id_4}",
      "{player_id_5}"
    ]
  }'
```

### 7. Simulate a Game
```bash
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{
    "league_id": "{league_id}",
    "team1_id": "{team1_id}",
    "team2_id": "{team2_id}",
    "seed": 42
  }'
```

Response includes full play-by-play events and winner.

### 8. View Game History
```bash
curl http://localhost:8000/api/games?league_id={league_id}
```

### 9. Check Standings
```bash
curl http://localhost:8000/api/leagues/{league_id}/standings
```

## Frontend Usage

1. Open http://localhost:3000
2. Click "Create League" and enter a name
3. Click "Generate Players" to populate the pool
4. Click "Create Team" to make your first team
5. Browse available players and add them to your roster
6. Designate your 5 starters
7. Create more teams (or let CPU create opponents)
8. Click "Simulate Game" to watch a match
9. View updated stats and standings

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test

# Run with coverage
npm test -- --coverage
```

### Integration Tests
```bash
cd backend
pytest tests/integration/ -v
```

## Configuration

### Backend Environment Variables
Create `backend/.env`:
```
# Optional configurations
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables
Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Docker Issues
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Backend Not Starting
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Not Starting
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Key Files & Directories

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models/              # Data models (Player, Team, etc.)
│   ├── services/            # Business logic
│   ├── api/                 # API endpoints
│   └── storage/             # In-memory storage
├── tests/                   # Test suite
└── requirements.txt         # Python dependencies

frontend/
├── src/
│   ├── App.tsx              # Main React component
│   ├── components/          # Reusable components
│   ├── pages/               # Page components
│   └── services/api.ts      # API client
├── tests/                   # Test suite
└── package.json             # Node dependencies

specs/001-fantasy-league/
├── spec.md                  # Feature specification
├── plan.md                  # Implementation plan
├── research.md              # Technical research
├── data-model.md            # Data model design
├── contracts/openapi.yaml   # API contract
└── quickstart.md            # This file
```

## Next Steps

1. Review the [feature specification](./spec.md) for requirements
2. Check the [API contracts](./contracts/openapi.yaml) for endpoint details
3. Review the [data model](./data-model.md) for entity relationships
4. Read the [research document](./research.md) for design decisions

## Support

- API Documentation: http://localhost:8000/docs
- Feature Spec: `specs/001-fantasy-league/spec.md`
- Technical Plan: `specs/001-fantasy-league/plan.md`

## Known Limitations (This Milestone)

- Single-user only (no authentication)
- In-memory storage (data lost on restart)
- No persistence between sessions
- No real-time updates
- Browser-only (no mobile app)

These will be addressed in future milestones.
