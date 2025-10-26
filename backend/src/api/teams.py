"""
Team API endpoints.

This module handles team creation, roster management, and starter designation.
Implements the following endpoints:
- POST /api/teams - Create a new team
- GET /api/teams/{team_id} - Get team details
- POST /api/teams/{team_id}/players - Add player to roster
- DELETE /api/teams/{team_id}/players/{player_id} - Remove player from roster
- PATCH /api/teams/{team_id}/starters - Set starting lineup

References:
- FR-012: Team rosters must have 8-12 players
- FR-013: Exactly 5 starters must be designated
- FR-014: Cannot add player if value exceeds budget
- FR-014a: Can add player if value equals budget
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..models.team import Team, TeamCreate, TeamResponse, AddPlayerRequest, SetStartersRequest
from ..services.team_service import TeamService
from ..services.league_service import LeagueService
from ..services.player_service import PlayerService
from ..storage.memory_storage import MemoryStorage

router = APIRouter(prefix="/api/teams", tags=["teams"])

# Initialize services (singleton storage)
storage = MemoryStorage()
league_service = LeagueService(storage)
player_service = PlayerService(storage)
team_service = TeamService(storage, player_service)


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team_data: TeamCreate) -> TeamResponse:
    """
    Create a new team with $100,000 budget.
    
    Args:
        team_data: Team creation data (name, league_id, optional description/logo)
        
    Returns:
        Created team with initial budget and empty roster
        
    Raises:
        HTTPException 404: League not found
        HTTPException 400: Invalid team data
    """
    try:
        # Verify league exists
        league = league_service.get_league(team_data.league_id)
        if league is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League {team_data.league_id} not found"
            )
        
        # Create team
        team = team_service.create_team(team_data)
        return TeamResponse.from_team(team)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str) -> TeamResponse:
    """
    Get team details by ID.
    
    Args:
        team_id: Team UUID
        
    Returns:
        Team details including roster and budget
        
    Raises:
        HTTPException 404: Team not found
    """
    team = team_service.get_team(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )
    
    return TeamResponse.from_team(team)


@router.post("/{team_id}/players", response_model=TeamResponse)
async def add_player_to_roster(team_id: str, request: AddPlayerRequest) -> TeamResponse:
    """
    Add a player to team roster (FR-012, FR-014, FR-014a).
    
    Validates:
    - Team exists
    - Player exists and is a free agent
    - Player value does not exceed remaining budget
    - Roster size does not exceed 12 players
    
    Args:
        team_id: Team UUID
        request: Player ID to add
        
    Returns:
        Updated team with player added to roster
        
    Raises:
        HTTPException 404: Team or player not found
        HTTPException 400: Player already on a team
        HTTPException 409: Budget exceeded or roster full
    """
    try:
        # Get team
        team = team_service.get_team(team_id)
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        
        # Get player
        player = player_service.get_player(request.player_id)
        if player is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player {request.player_id} not found"
            )
        
        # Check if player is already on a team
        if not player.is_free_agent():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Player {request.player_id} is already on team {player.team_id}"
            )
        
        # Add player to roster (this validates budget and roster size)
        team = team_service.add_player_to_roster(team_id, request.player_id)
        return TeamResponse.from_team(team)
        
    except ValueError as e:
        # Budget or roster validation errors
        error_msg = str(e).lower()
        if "budget" in error_msg or "cost" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        elif "roster" in error_msg or "maximum" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.delete("/{team_id}/players/{player_id}", response_model=TeamResponse)
async def remove_player_from_roster(team_id: str, player_id: str) -> TeamResponse:
    """
    Remove a player from team roster.
    
    Validates:
    - Team exists
    - Player is on the team's roster
    - Roster size will not go below minimum (8 players) if roster has players
    
    Args:
        team_id: Team UUID
        player_id: Player UUID
        
    Returns:
        Updated team with player removed from roster
        
    Raises:
        HTTPException 404: Team or player not found
        HTTPException 400: Player not on roster or would violate minimum roster size
    """
    try:
        # Get team
        team = team_service.get_team(team_id)
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        
        # Check if player is on the roster
        if player_id not in team.player_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Player {player_id} is not on team {team_id}"
            )
        
        # Remove player from roster
        team = team_service.remove_player_from_roster(team_id, player_id)
        return TeamResponse.from_team(team)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{team_id}/starters", response_model=TeamResponse)
async def set_starters(team_id: str, request: SetStartersRequest) -> TeamResponse:
    """
    Designate starting lineup for team (FR-013).
    
    Validates:
    - Exactly 5 starters provided
    - All starters are on the team's roster
    - No duplicate player IDs
    
    Args:
        team_id: Team UUID
        request: List of exactly 5 player IDs for starters
        
    Returns:
        Updated team with starters designated
        
    Raises:
        HTTPException 404: Team not found
        HTTPException 400: Invalid starter count, players not on roster, or duplicates
    """
    try:
        # Get team
        team = team_service.get_team(team_id)
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        
        # Set starters (this validates exactly 5, all on roster, no duplicates)
        team = team_service.set_starters(team_id, request.starter_ids)
        return TeamResponse.from_team(team)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
