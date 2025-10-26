"""
API endpoints for league operations.

This module provides REST endpoints for:
- Creating leagues
- Retrieving league information
- Generating players for leagues
- Listing players in leagues
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models.league import League, LeagueCreate
from ..models.player import Player
from ..services.league_service import LeagueService


router = APIRouter(prefix="/api/leagues", tags=["leagues"])

# Service instance (shared across requests)
league_service = LeagueService()


@router.post("", response_model=League, status_code=201)
def create_league(league_data: LeagueCreate) -> League:
    """
    Create a new fantasy dodgeball league.
    
    Args:
        league_data: League creation data including name and settings
        
    Returns:
        Created league with generated ID
        
    Example:
        POST /api/leagues
        {
            "name": "My League",
            "player_count": 75,
            "season_rounds": 10
        }
    """
    try:
        league = league_service.create_league(league_data)
        return league
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{league_id}", response_model=League)
def get_league(league_id: str) -> League:
    """
    Get a league by ID.
    
    Args:
        league_id: League UUID
        
    Returns:
        League information
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000
    """
    league = league_service.get_league(league_id)
    if league is None:
        raise HTTPException(status_code=404, detail=f"League {league_id} not found")
    
    return league


@router.get("", response_model=List[League])
def list_leagues() -> List[League]:
    """
    Get all leagues in the system.
    
    Returns:
        List of all leagues
        
    Example:
        GET /api/leagues
    """
    return league_service.get_all_leagues()


@router.post("/{league_id}/players", response_model=List[Player], status_code=201)
def generate_players(league_id: str) -> List[Player]:
    """
    Generate players for a league.
    
    This endpoint creates the initial player pool based on the league's
    player_count setting (50-100 players).
    
    Args:
        league_id: League UUID
        
    Returns:
        List of generated players
        
    Raises:
        HTTPException: 404 if league not found
        HTTPException: 400 if validation fails
        
    Example:
        POST /api/leagues/123e4567-e89b-12d3-a456-426614174000/players
    """
    try:
        players = league_service.generate_players_for_league(league_id)
        return players
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{league_id}/players", response_model=List[Player])
def list_players(
    league_id: str,
    free_agents_only: bool = Query(False, description="Only return free agents")
) -> List[Player]:
    """
    Get all players in a league.
    
    Args:
        league_id: League UUID
        free_agents_only: If True, only return players not assigned to teams
        
    Returns:
        List of players
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/players
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/players?free_agents_only=true
    """
    try:
        players = league_service.get_league_players(
            league_id=league_id,
            free_agents_only=free_agents_only
        )
        return players
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{league_id}", status_code=204)
def delete_league(league_id: str) -> None:
    """
    Delete a league from the system.
    
    Args:
        league_id: League UUID
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        DELETE /api/leagues/123e4567-e89b-12d3-a456-426614174000
    """
    deleted = league_service.delete_league(league_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"League {league_id} not found")
