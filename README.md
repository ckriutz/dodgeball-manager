# Dodgeball Fantasy League

A fun web application for managing a fantasy dodgeball league with player stats, team drafting, and game simulation.

## Features

- **League Management**: Create leagues and generate 50-100 players with random stats
- **Team Building**: Draft teams with $100k budgets, manage rosters of 8-12 players
- **Game Simulation**: Deterministic dodgeball game engine using player skills
- **Season Tracking**: Schedule games, view standings, and track MVP awards

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS 3, Vite
- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Testing**: pytest (backend), Jest + React Testing Library (frontend)
- **Deployment**: Docker + docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Run with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd dodgeball-manager
git checkout 001-fantasy-league

# Start all services
docker-compose up --build
```

**Services will be available at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server
c
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── models/        # Pydantic models (Player, Team, League, Game)
│   │   ├── services/      # Business logic
│   │   ├── api/           # FastAPI routes
│   │   └── storage/       # In-memory storage
│   ├── tests/
│   │   ├── unit/          # Unit tests
│   │   ├── integration/   # API tests
│   │   └── simulation/    # Game simulation tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   ├── tests/             # Component tests
│   ├── Dockerfile
│   └── package.json
│
├── specs/
│   └── 001-fantasy-league/
│       ├── spec.md        # Feature specification
│       ├── plan.md        # Implementation plan
│       ├── tasks.md       # Task breakdown
│       └── contracts/     # API contracts
│
└── docker-compose.yml
```

## Usage

### Creating a League

1. Navigate to http://localhost:3000
2. Click "Create League"
3. Enter league name and number of players (50-100)
4. Click "Generate Players" to populate the player pool

### Building a Team

1. Click "Create Team"
2. Enter team name and description
3. Browse available players and add to roster (8-12 players)
4. Designate 5 starters from your roster
5. Stay within your $100,000 budget

### Simulating Games

1. Select two teams with complete rosters
2. Click "Simulate Game"
3. View play-by-play results
4. Check updated player stats and team records

### Managing the Season

1. Generate a schedule for all teams
2. Simulate games individually or in bulk
3. View league standings ranked by wins/losses
4. Check MVP and statistical leaders

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m simulation     # Simulation tests only
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Development

### Code Quality

Backend uses:
- **Black**: Code formatting
- **Ruff**: Linting
- **mypy**: Type checking

Frontend uses:
- **ESLint**: Linting
- **TypeScript**: Type checking
- **Prettier**: Code formatting (optional)

### Running Linters

```bash
# Backend
cd backend
black src tests
ruff check src tests
mypy src

# Frontend
cd frontend
npm run lint
```

## Configuration

### Environment Variables

Backend (`backend/.env`):
```
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

Frontend (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000/api
```

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000
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

## Known Limitations (Current Milestone)

- **Single-user only**: No authentication or multi-user support
- **In-memory storage**: Data is lost when the application restarts
- **No persistence**: No database integration yet
- **Browser-only**: No mobile app

These limitations will be addressed in future milestones.

## Contributing

This is currently a development project. For questions or issues, please refer to the specification documents in `specs/001-fantasy-league/`.

## Documentation

- [Feature Specification](specs/001-fantasy-league/spec.md) - Complete requirements
- [Implementation Plan](specs/001-fantasy-league/plan.md) - Technical design decisions
- [Task Breakdown](specs/001-fantasy-league/tasks.md) - Development tasks
- [API Contracts](specs/001-fantasy-league/contracts/openapi.yaml) - REST API specification
- [Quickstart Guide](specs/001-fantasy-league/quickstart.md) - Detailed setup instructions

## License

[Add license information]

## Support

For issues or questions, please review the documentation in the `specs/` directory or contact the development team.
