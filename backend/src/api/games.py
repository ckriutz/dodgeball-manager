"""
API endpoints for game operations.

This module provides REST endpoints for:
- Creating and simulating games
- Retrieving game information
- Listing game history
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models.game import GameCreate, GameResponse, GameSummary
from ..services.game_service import GameService
from ..services.league_service import LeagueService
from ..services.team_service import TeamService
from ..storage.memory_storage import MemoryStorage


router = APIRouter(prefix="/api/games", tags=["games"])

# Service instances (shared across requests)
storage = MemoryStorage()
league_service = LeagueService(storage=storage)
team_service = TeamService(storage=storage)
game_service = GameService(
    storage=storage,
    team_service=team_service
)


@router.post("", response_model=GameResponse, status_code=201)
def create_and_simulate_game(game_data: GameCreate) -> GameResponse:
    """
    Create a new game between two teams and simulate it immediately.
    
    This endpoint creates a game, validates that both teams have 5 starters,
    simulates the complete dodgeball match, and returns the results.
    
    Args:
        game_data: Game creation data including teams and optional seed
        
    Returns:
        Completed game with full play-by-play events
        
    Raises:
        HTTPException: 404 if teams not found, 400 if validation fails
        
    Example:
        POST /api/games
        {
            "league_id": "123e4567-e89b-12d3-a456-426614174000",
            "team1_id": "456e7890-e89b-12d3-a456-426614174001",
            "team2_id": "789e0123-e89b-12d3-a456-426614174002",
            "seed": 42
        }
    """
    try:
        game = game_service.create_and_simulate_game(
            league_id=game_data.league_id,
            team1_id=game_data.team1_id,
            team2_id=game_data.team2_id,
            seed=game_data.seed
        )
        return GameResponse.from_game(game)
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: str) -> GameResponse:
    """
    Get a game by ID with full details.
    
    Args:
        game_id: Game UUID
        
    Returns:
        Complete game information including events and results
        
    Raises:
        HTTPException: 404 if game not found
        
    Example:
        GET /api/games/123e4567-e89b-12d3-a456-426614174000
    """
    game = game_service.get_game(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    
    return GameResponse.from_game(game)


@router.get("", response_model=List[GameSummary])
def list_games(
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    team_id: Optional[str] = Query(None, description="Filter by team ID (games involving this team)"),
    completed_only: bool = Query(True, description="Only return completed games")
) -> List[GameSummary]:
    """
    Get all games with optional filtering.
    
    Args:
        league_id: Optional league UUID to filter games
        team_id: Optional team UUID to filter games (shows games this team played in)
        completed_only: If True, only return completed games
        
    Returns:
        List of game summaries
        
    Example:
        GET /api/games
        GET /api/games?league_id=123e4567-e89b-12d3-a456-426614174000
        GET /api/games?team_id=456e7890-e89b-12d3-a456-426614174001
    """
    try:
        if team_id:
            # Filter by team
            games = game_service.get_games_by_team(team_id)
        else:
            # Filter by league or get all
            games = game_service.get_all_games(league_id=league_id)
        
        # Filter by completion status
        if completed_only:
            games = [game for game in games if game.is_completed()]
        
        return [GameSummary.from_game(game) for game in games]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))