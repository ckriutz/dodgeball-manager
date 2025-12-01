"""
API endpoints for league operations.

This module provides REST endpoints for:
- Creating leagues
- Retrieving league information
- Generating players for leagues
- Listing players in leagues
- Generating and managing schedules
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..models.league import League, LeagueCreate, SeasonArchive
from ..models.player import Player
from ..models.team import Team
from ..services.league_service import LeagueService
from ..services.team_service import TeamService
from ..services.player_service import PlayerService
from ..services.season_service import SeasonService
from ..storage.memory_storage import MemoryStorage


router = APIRouter(prefix="/api/leagues", tags=["leagues"])

# Service instances (shared across requests)
storage = MemoryStorage()
player_service = PlayerService(storage)
league_service = LeagueService(storage, player_service)
team_service = TeamService(storage, player_service)
season_service = SeasonService(storage)


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
def generate_players(
    league_id: str,
    count: Optional[int] = Query(None, description="Number of players to generate (overrides league default)")
) -> List[Player]:
    """
    Generate players for a league.
    
    This endpoint creates players for the league. If count is not specified,
    it uses the league's player_count setting (default 75). If count is specified,
    it generates that many additional players.
    
    Args:
        league_id: League UUID
        count: Optional number of players to generate
        
    Returns:
        List of generated players
        
    Raises:
        HTTPException: 404 if league not found
        HTTPException: 400 if validation fails
        
    Examples:
        POST /api/leagues/123e4567-e89b-12d3-a456-426614174000/players
        POST /api/leagues/123e4567-e89b-12d3-a456-426614174000/players?count=25
    """
    try:
        if count is not None:
            # Generate specific count of additional players
            league = league_service.get_league(league_id)
            if league is None:
                raise ValueError(f"League {league_id} not found")
            players = player_service.generate_players(count=count, league_id=league_id)
        else:
            # Generate default player pool
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


@router.get("/{league_id}/teams", response_model=List[Team])
def list_teams(league_id: str) -> List[Team]:
    """
    Get all teams in a league.
    
    Args:
        league_id: League UUID
        
    Returns:
        List of teams in the league
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/teams
    """
    try:
        # Verify league exists
        league = league_service.get_league(league_id)
        if league is None:
            raise ValueError(f"League {league_id} not found")
        
        # Get teams in league
        teams = team_service.get_teams_by_league(league_id)
        return teams
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


# --- Schedule Management Endpoints ---

class ScheduleCreateRequest(BaseModel):
    """Request body for schedule creation."""
    rounds: int = Field(default=1, ge=1, description="Number of rounds (each team plays every other team this many times)")


class ScheduleResponse(BaseModel):
    """Response model for schedule operations."""
    games_scheduled: Optional[int] = None
    total_games: Optional[int] = None
    completed_games: Optional[int] = None
    remaining_games: Optional[int] = None
    next_game: Optional[dict] = None
    schedule: List[dict]
    season_number: Optional[int] = None
    season_status: Optional[str] = None
    is_season_complete: Optional[bool] = None


@router.post("/{league_id}/schedule", response_model=ScheduleResponse)
def create_schedule(
    league_id: str,
    request: Optional[ScheduleCreateRequest] = None
) -> ScheduleResponse:
    """
    Generate a round-robin schedule for the league.
    
    Creates a schedule where each team plays every other team the specified
    number of rounds. This replaces any existing schedule and starts the
    season if not already started.
    
    Args:
        league_id: League UUID
        request: Optional schedule creation parameters
        
    Returns:
        Schedule with game pairings and metadata
        
    Raises:
        HTTPException: 404 if league not found
        HTTPException: 400 if league has less than 2 teams
        
    Example:
        POST /api/leagues/123e4567-e89b-12d3-a456-426614174000/schedule
        {
            "rounds": 1
        }
    """
    try:
        rounds = request.rounds if request else 1
        result = league_service.generate_schedule(league_id, rounds=rounds)
        return ScheduleResponse(**result)
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)


@router.get("/{league_id}/schedule", response_model=ScheduleResponse)
def get_schedule(league_id: str) -> ScheduleResponse:
    """
    Get the current schedule for a league with status indicators.
    
    Returns the schedule with game completion status, total/completed/remaining
    game counts, and identifies the next game to play.
    
    Args:
        league_id: League UUID
        
    Returns:
        Schedule with status indicators and metadata
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/schedule
        
    Response includes:
        - schedule: List of games with game_number, team1_id, team2_id, completed
        - total_games: Total number of games in the schedule
        - completed_games: Number of games already played
        - remaining_games: Number of games yet to play
        - next_game: The next scheduled game to play (or null if all complete)
        - season_number: Current season number
        - season_status: Current season status (not_started, in_progress, completed)
        - is_season_complete: Whether all scheduled games have been played
    """
    try:
        result = league_service.get_schedule(league_id)
        return ScheduleResponse(**result)
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)


# --- Standings and Awards Endpoints ---

class StandingsEntryResponse(BaseModel):
    """Response model for a single standings entry."""
    team_id: str
    team_name: str
    wins: int
    losses: int
    rank: int


class StandingsResponse(BaseModel):
    """Response model for league standings."""
    league_id: str
    standings: List[StandingsEntryResponse]


@router.get("/{league_id}/standings", response_model=StandingsResponse)
def get_standings(league_id: str) -> StandingsResponse:
    """
    Get current standings for a league.
    
    Returns teams ranked by wins (descending), then losses (ascending).
    Each team includes their win/loss record and rank position.
    
    Args:
        league_id: League UUID
        
    Returns:
        Standings with ranked teams
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/standings
        
    Response includes:
        - league_id: The league identifier
        - standings: List of teams with team_id, team_name, wins, losses, rank
    """
    try:
        standings = league_service.get_league_standings(league_id)
        return StandingsResponse(
            league_id=standings.league_id,
            standings=[
                StandingsEntryResponse(
                    team_id=entry.team_id,
                    team_name=entry.team_name,
                    wins=entry.wins,
                    losses=entry.losses,
                    rank=entry.rank
                )
                for entry in standings.standings
            ]
        )
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)


class AwardWinnerResponse(BaseModel):
    """Response model for an award winner."""
    player_id: str
    name: str
    reason: Optional[str] = None
    mvp_score: Optional[float] = None
    successful_hits: Optional[int] = None
    catches_made: Optional[int] = None
    times_hit: Optional[int] = None
    accuracy: Optional[float] = None


class AwardsResponse(BaseModel):
    """Response model for league awards."""
    league_id: str
    mvp: Optional[AwardWinnerResponse] = None
    most_hits: Optional[AwardWinnerResponse] = None
    most_catches: Optional[AwardWinnerResponse] = None
    accuracy_leader: Optional[AwardWinnerResponse] = None
    best_defense: Optional[AwardWinnerResponse] = None


@router.get("/{league_id}/awards", response_model=AwardsResponse)
def get_awards(league_id: str) -> AwardsResponse:
    """
    Get awards (MVP and statistical leaders) for a league.
    
    Calculates awards based on current player stats:
    - mvp: Most Valuable Player (combined performance score)
    - most_hits: Player with most successful eliminations
    - most_catches: Player with most catches made
    - accuracy_leader: Player with best throw accuracy (min 10 throws)
    - best_defense: Player with fewest times eliminated
    
    Args:
        league_id: League UUID
        
    Returns:
        Awards with winners for each category
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/awards
    """
    try:
        awards = league_service.get_league_awards(league_id)
        
        def convert_winner(winner_data: Optional[dict]) -> Optional[AwardWinnerResponse]:
            if winner_data is None:
                return None
            return AwardWinnerResponse(
                player_id=winner_data.get("player_id", ""),
                name=winner_data.get("name", "Unknown"),
                reason=winner_data.get("reason"),
                mvp_score=winner_data.get("mvp_score"),
                successful_hits=winner_data.get("successful_hits"),
                catches_made=winner_data.get("catches_made"),
                times_hit=winner_data.get("times_hit"),
                accuracy=winner_data.get("accuracy")
            )
        
        return AwardsResponse(
            league_id=awards["league_id"],
            mvp=convert_winner(awards.get("mvp")),
            most_hits=convert_winner(awards.get("most_hits")),
            most_catches=convert_winner(awards.get("most_catches")),
            accuracy_leader=convert_winner(awards.get("accuracy_leader")),
            best_defense=convert_winner(awards.get("best_defense"))
        )
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)


# --- Season Lifecycle Endpoints ---

class ChampionResponse(BaseModel):
    """Response model for season champion."""
    team_id: str
    team_name: str
    wins: int
    losses: int


class FinishSeasonResponse(BaseModel):
    """Response model for finishing a season."""
    season_number: int
    final_standings: List[dict]
    champion: Optional[ChampionResponse] = None
    mvp: Optional[AwardWinnerResponse] = None
    statistical_leaders: Optional[dict] = None
    message: str = "Season completed successfully"


@router.post("/{league_id}/seasons/finish", response_model=FinishSeasonResponse)
def finish_season(league_id: str) -> FinishSeasonResponse:
    """
    Finish the current season and create an archive.
    
    This endpoint:
    1. Validates all games are complete
    2. Calculates final standings
    3. Determines champion (top team by standings)
    4. Calculates MVP and statistical leaders
    5. Creates immutable season archive
    6. Marks season as completed
    
    Args:
        league_id: League UUID
        
    Returns:
        Season results including final_standings, champion, mvp, and statistical_leaders
        
    Raises:
        HTTPException: 404 if league not found
        HTTPException: 400 if season cannot be finished (incomplete games, wrong status)
        
    Example:
        POST /api/leagues/123e4567-e89b-12d3-a456-426614174000/seasons/finish
        
    Response includes:
        - season_number: The completed season number
        - final_standings: Ranked list of teams with wins/losses
        - champion: The winning team details
        - mvp: Most Valuable Player details
        - statistical_leaders: Leaders in various categories
    """
    try:
        result = season_service.finish_season(league_id)
        
        champion_data = result.get("champion")
        champion = None
        if champion_data and champion_data.get("team_id"):
            champion = ChampionResponse(
                team_id=champion_data["team_id"],
                team_name=champion_data.get("team_name", "Unknown"),
                wins=champion_data.get("wins", 0),
                losses=champion_data.get("losses", 0)
            )
        
        mvp_data = result.get("mvp")
        mvp = None
        if mvp_data and mvp_data.get("player_id"):
            mvp = AwardWinnerResponse(
                player_id=mvp_data["player_id"],
                name=mvp_data.get("name", "Unknown"),
                reason=mvp_data.get("reason"),
                mvp_score=mvp_data.get("mvp_score"),
                successful_hits=mvp_data.get("successful_hits"),
                catches_made=mvp_data.get("catches_made"),
                times_hit=mvp_data.get("times_hit"),
                accuracy=mvp_data.get("accuracy")
            )
        
        return FinishSeasonResponse(
            season_number=result["season_number"],
            final_standings=result["final_standings"],
            champion=champion,
            mvp=mvp,
            statistical_leaders=result.get("statistical_leaders"),
            message=f"Season {result['season_number']} completed successfully"
        )
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)


class StartSeasonRequest(BaseModel):
    """Request body for starting a new season."""
    apply_age_progression: bool = Field(
        default=True,
        description="Whether to apply age progression to all players (adds 1 year, applies skill changes for 30+ players)"
    )


class AgeProgressionResult(BaseModel):
    """Result of age progression for a single player."""
    player_id: str
    name: str
    old_age: int
    new_age: int
    skill_changes: dict = Field(default_factory=dict)


class StartSeasonResponse(BaseModel):
    """Response model for starting a new season."""
    season_number: int
    status: str
    age_progression_results: List[AgeProgressionResult] = Field(default_factory=list)
    message: str = "Season started successfully"


@router.post("/{league_id}/seasons/start", response_model=StartSeasonResponse)
def start_season(
    league_id: str,
    request: Optional[StartSeasonRequest] = None
) -> StartSeasonResponse:
    """
    Start a new season with optional age progression.
    
    This endpoint:
    1. Validates previous season is complete (if not first season)
    2. Applies age progression to all players (optional, adds 1 year)
    3. Resets team win/loss records to 0-0
    4. Creates new season with incremented number
    
    Note: A schedule must be generated separately via POST /api/leagues/{league_id}/schedule
    after starting the season.
    
    Args:
        league_id: League UUID
        request: Optional parameters including apply_age_progression
        
    Returns:
        New season info including season_number, status, and age_progression_results
        
    Raises:
        HTTPException: 404 if league not found
        HTTPException: 400 if new season cannot be started (previous not complete)
        
    Example:
        POST /api/leagues/123e4567-e89b-12d3-a456-426614174000/seasons/start
        {
            "apply_age_progression": true
        }
        
    Response includes:
        - season_number: The new season number
        - status: Current season status (should be "in_progress")
        - age_progression_results: List of player age changes and skill modifications
    """
    try:
        apply_age = request.apply_age_progression if request else True
        result = season_service.start_new_season(
            league_id=league_id,
            apply_age_progression=apply_age
        )
        
        age_results = [
            AgeProgressionResult(
                player_id=r["player_id"],
                name=r["name"],
                old_age=r["old_age"],
                new_age=r["new_age"],
                skill_changes=r.get("skill_changes", {})
            )
            for r in result.get("age_progression_results", [])
        ]
        
        return StartSeasonResponse(
            season_number=result["season_number"],
            status=result["status"],
            age_progression_results=age_results,
            message=f"Season {result['season_number']} started successfully"
        )
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)


class SeasonHistoryResponse(BaseModel):
    """Response model for season history."""
    season_archives: List[SeasonArchive] = Field(
        default_factory=list,
        description="List of all completed seasons for the league, sorted by season number"
    )
    count: int = Field(description="Total number of completed seasons")


@router.get("/{league_id}/seasons/history", response_model=SeasonHistoryResponse)
def get_season_history(league_id: str) -> SeasonHistoryResponse:
    """
    Retrieve the history of all completed seasons for a league.
    
    This endpoint returns an immutable archive of all past seasons including:
    - Final standings with rankings
    - Champion and MVP for each season
    - Statistical leaders (most hits, best catch %, etc.)
    - Team rosters at season end
    - Player statistics from each season
    
    Args:
        league_id: League UUID
        
    Returns:
        List of season archives sorted by season_number, with total count
        
    Raises:
        HTTPException: 404 if league not found
        
    Example:
        GET /api/leagues/123e4567-e89b-12d3-a456-426614174000/seasons/history
        
    Response:
        {
            "season_archives": [
                {
                    "season_number": 1,
                    "champion_team_id": "team-123",
                    "mvp_player_id": "player-456",
                    "final_standings": [...],
                    "team_rosters": {...},
                    "player_stats": {...},
                    "statistical_leaders": {...},
                    "completed_at": "2025-11-30T00:52:32Z",
                    "archived_at": "2025-11-30T00:52:35Z"
                }
            ],
            "count": 1
        }
    """
    try:
        league = league_service.get_league(league_id)
        if league is None:
            raise HTTPException(status_code=404, detail=f"League {league_id} not found")
        
        # Season archives are already sorted in the league object
        return SeasonHistoryResponse(
            season_archives=league.season_archives,
            count=len(league.season_archives)
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
