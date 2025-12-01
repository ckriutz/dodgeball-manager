"""
API endpoints for player operations.

This module provides REST endpoints for:
- Getting player progression information
- Spending skill points on player skills
"""

from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.player_service import PlayerService
from ..storage.memory_storage import MemoryStorage


router = APIRouter(prefix="/api/players", tags=["players"])

# Service instances (shared across requests)
storage = MemoryStorage()
player_service = PlayerService(storage)


# Request schemas
class SpendSkillPointRequest(BaseModel):
    """Request schema for spending a single skill point."""
    skill_name: str = Field(
        description="Name of skill to increase (catching, throwing, dodging, speed, iq, luck)"
    )


class SpendSkillPointsRequest(BaseModel):
    """Request schema for spending multiple skill points."""
    allocations: Dict[str, int] = Field(
        description="Map of skill_name to points to spend, e.g., {'throwing': 2, 'catching': 1}"
    )


# Response schemas
class PlayerSkillsResponse(BaseModel):
    """Response schema for player skills."""
    catching: int = Field(ge=0, le=100)
    throwing: int = Field(ge=0, le=100)
    dodging: int = Field(ge=0, le=100)
    speed: int = Field(ge=0, le=100)
    iq: int = Field(ge=0, le=100)
    luck: int = Field(ge=0, le=100)


class PlayerProgressionResponse(BaseModel):
    """Response schema for player progression information."""
    player_id: str = Field(description="Player UUID")
    player_name: str = Field(description="Player name")
    level: int = Field(ge=1, le=100, description="Current level")
    experience_points: int = Field(ge=0, description="Total XP earned")
    available_skill_points: int = Field(ge=0, description="Unspent skill points")
    xp_for_next_level: int = Field(ge=0, description="XP required to reach next level")
    xp_progress: int = Field(description="XP earned towards next level")
    progress_percentage: float = Field(ge=0, le=100, description="Progress percentage to next level")


class SpendSkillPointResponse(BaseModel):
    """Response schema for spending skill points."""
    player_id: str = Field(description="Player UUID")
    player_name: str = Field(description="Player name")
    skill_name: str = Field(description="Skill that was increased")
    new_skill_value: int = Field(ge=0, le=100, description="New value of the skill")
    remaining_skill_points: int = Field(ge=0, description="Remaining unspent skill points")
    skills: PlayerSkillsResponse = Field(description="Current skills after spending")
    new_value: int = Field(ge=0, description="New calculated player value")


class SpendSkillPointsResponse(BaseModel):
    """Response schema for spending multiple skill points."""
    player_id: str = Field(description="Player UUID")
    player_name: str = Field(description="Player name")
    points_spent: int = Field(ge=0, description="Total points spent")
    remaining_skill_points: int = Field(ge=0, description="Remaining unspent skill points")
    skills: PlayerSkillsResponse = Field(description="Current skills after spending")
    new_value: int = Field(ge=0, description="New calculated player value")
    allocations_applied: Dict[str, int] = Field(description="Points applied to each skill")


@router.get("/{player_id}/progression", response_model=PlayerProgressionResponse)
def get_player_progression(player_id: str) -> PlayerProgressionResponse:
    """
    Get a player's progression information.
    
    Returns the player's current level, XP, available skill points,
    and progress towards the next level.
    
    Args:
        player_id: Player UUID
        
    Returns:
        PlayerProgressionResponse with progression details
        
    Raises:
        HTTPException: 404 if player not found
        
    Example:
        GET /api/players/123e4567-e89b-12d3-a456-426614174000/progression
        
        Response:
        {
            "player_id": "123e4567-e89b-12d3-a456-426614174000",
            "player_name": "Player 1",
            "level": 1,
            "experience_points": 75,
            "available_skill_points": 0,
            "xp_for_next_level": 100,
            "xp_progress": 75,
            "progress_percentage": 75.0
        }
    """
    try:
        progression_info = player_service.get_player_progression(player_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Get player for name
    player = player_service.get_player(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    
    return PlayerProgressionResponse(
        player_id=player_id,
        player_name=player.name,
        level=progression_info['level'],
        experience_points=progression_info['experience_points'],
        available_skill_points=progression_info['available_skill_points'],
        xp_for_next_level=progression_info['xp_for_next_level'],
        xp_progress=progression_info['xp_progress'],
        progress_percentage=progression_info['progress_percentage']
    )


@router.post("/{player_id}/spend-skill-point", response_model=SpendSkillPointResponse)
def spend_skill_point(player_id: str, request: SpendSkillPointRequest) -> SpendSkillPointResponse:
    """
    Spend a single skill point to increase a player's skill by 1.
    
    The player must have available skill points (earned through leveling up).
    Each skill has a maximum value of 100.
    
    Args:
        player_id: Player UUID
        request: Request containing the skill name to increase
        
    Returns:
        SpendSkillPointResponse with updated skill values
        
    Raises:
        HTTPException: 404 if player not found
        HTTPException: 400 if no skill points available, skill at max, or invalid skill name
        
    Example:
        POST /api/players/123e4567-e89b-12d3-a456-426614174000/spend-skill-point
        {
            "skill_name": "throwing"
        }
        
        Response:
        {
            "player_id": "123e4567-e89b-12d3-a456-426614174000",
            "player_name": "Player 1",
            "skill_name": "throwing",
            "new_skill_value": 3,
            "remaining_skill_points": 1,
            "skills": {
                "catching": 2,
                "throwing": 3,
                "dodging": 2,
                "speed": 1,
                "iq": 1,
                "luck": 1
            },
            "new_value": 1400
        }
    """
    try:
        player = player_service.spend_skill_point(player_id, request.skill_name)
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    skills = player.skills
    new_skill_value = getattr(skills, request.skill_name)
    
    return SpendSkillPointResponse(
        player_id=player_id,
        player_name=player.name,
        skill_name=request.skill_name,
        new_skill_value=new_skill_value,
        remaining_skill_points=player.stats.available_skill_points,
        skills=PlayerSkillsResponse(
            catching=skills.catching,
            throwing=skills.throwing,
            dodging=skills.dodging,
            speed=skills.speed,
            iq=skills.iq,
            luck=skills.luck
        ),
        new_value=player.value
    )


@router.post("/{player_id}/spend-skill-points", response_model=SpendSkillPointsResponse)
def spend_skill_points(player_id: str, request: SpendSkillPointsRequest) -> SpendSkillPointsResponse:
    """
    Spend multiple skill points at once across different skills.
    
    This endpoint allows batch allocation of skill points in a single request.
    The operation is atomic - all allocations succeed or none are applied.
    
    Args:
        player_id: Player UUID
        request: Request containing skill allocations
        
    Returns:
        SpendSkillPointsResponse with updated skill values
        
    Raises:
        HTTPException: 404 if player not found
        HTTPException: 400 if not enough skill points, skill would exceed max, or invalid skill name
        
    Example:
        POST /api/players/123e4567-e89b-12d3-a456-426614174000/spend-skill-points
        {
            "allocations": {
                "throwing": 2,
                "catching": 1
            }
        }
        
        Response:
        {
            "player_id": "123e4567-e89b-12d3-a456-426614174000",
            "player_name": "Player 1",
            "points_spent": 3,
            "remaining_skill_points": 0,
            "skills": {
                "catching": 3,
                "throwing": 4,
                "dodging": 2,
                "speed": 1,
                "iq": 1,
                "luck": 1
            },
            "new_value": 1600,
            "allocations_applied": {
                "throwing": 2,
                "catching": 1
            }
        }
    """
    try:
        player = player_service.spend_skill_points(player_id, request.allocations)
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    skills = player.skills
    points_spent = sum(request.allocations.values())
    
    return SpendSkillPointsResponse(
        player_id=player_id,
        player_name=player.name,
        points_spent=points_spent,
        remaining_skill_points=player.stats.available_skill_points,
        skills=PlayerSkillsResponse(
            catching=skills.catching,
            throwing=skills.throwing,
            dodging=skills.dodging,
            speed=skills.speed,
            iq=skills.iq,
            luck=skills.luck
        ),
        new_value=player.value,
        allocations_applied=request.allocations
    )