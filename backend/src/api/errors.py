"""
Error handling middleware and custom exceptions for the Dodgeball Fantasy League API.

This module provides:
- Custom exception classes for API errors
- Error response models matching the OpenAPI specification
- Exception handlers for FastAPI
"""

import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Error response model matching OpenAPI specification."""
    message: str
    detail: Optional[str] = None


class APIError(HTTPException):
    """Base class for API-specific errors."""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.message = message
        self.detail = detail


class BadRequestError(APIError):
    """Exception for bad request errors (400)."""

    def __init__(self, message: str = "Bad request", detail: Optional[str] = None):
        super().__init__(status_code=400, message=message, detail=detail)


class NotFoundError(APIError):
    """Exception for resource not found errors (404)."""

    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(status_code=404, message=message, detail=detail)


class ValidationError(APIError):
    """Exception for validation errors (400)."""

    def __init__(self, message: str = "Validation error", detail: Optional[str] = None):
        super().__init__(status_code=400, message=message, detail=detail)


class ConflictError(APIError):
    """Exception for conflict errors (409)."""

    def __init__(self, message: str = "Conflict", detail: Optional[str] = None):
        super().__init__(status_code=409, message=message, detail=detail)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handler for custom API errors.

    Converts APIError exceptions to proper JSON responses matching the OpenAPI spec.
    """
    logger.warning(
        f"API Error: {exc.status_code} - {exc.message}",
        extra={
            "status_code": exc.status_code,
            "message": exc.message,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.message, detail=exc.detail).model_dump(),
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Converts validation errors to standardized API error responses.
    """
    if hasattr(exc, "errors") and callable(getattr(exc, "errors", None)):
        # Pydantic v2 ValidationError
        errors = exc.errors()
        error_details = []
        for error in errors:
            field = ".".join(str(loc) for loc in error.get("loc", []))
            message = error.get("msg", "Validation error")
            error_details.append(f"{field}: {message}")

        detail = "; ".join(error_details)
    else:
        # Fallback for other validation errors
        detail = str(exc)

    logger.warning(
        f"Validation Error: {detail}",
        extra={
            "path": str(request.url),
            "method": request.method,
            "error_details": detail,
        }
    )

    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            message="Validation error",
            detail=detail
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for standard FastAPI HTTPException.

    Converts HTTPException to standardized API error responses.
    """
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.detail).model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.

    Provides generic error response for unexpected errors.
    """
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
        }
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            detail="An unexpected error occurred. Please try again later."
        ).model_dump(),
    )


# Common error factory functions for business logic
def player_not_found(player_id: str) -> NotFoundError:
    """Factory for player not found errors."""
    return NotFoundError(
        message="Player not found",
        detail=f"No player found with ID: {player_id}"
    )


def team_not_found(team_id: str) -> NotFoundError:
    """Factory for team not found errors."""
    return NotFoundError(
        message="Team not found",
        detail=f"No team found with ID: {team_id}"
    )


def league_not_found(league_id: str) -> NotFoundError:
    """Factory for league not found errors."""
    return NotFoundError(
        message="League not found",
        detail=f"No league found with ID: {league_id}"
    )


def game_not_found(game_id: str) -> NotFoundError:
    """Factory for game not found errors."""
    return NotFoundError(
        message="Game not found",
        detail=f"No game found with ID: {game_id}"
    )


def insufficient_budget(team_name: str, budget: int, player_value: int) -> BadRequestError:
    """Factory for insufficient budget errors."""
    return BadRequestError(
        message="Insufficient budget",
        detail=f"Team '{team_name}' has ${budget} remaining budget but player costs ${player_value}"
    )


def roster_full(team_name: str, current_count: int, max_count: int = 12) -> BadRequestError:
    """Factory for roster full errors."""
    return BadRequestError(
        message="Roster full",
        detail=f"Team '{team_name}' already has {current_count} players (maximum {max_count})"
    )


def roster_too_small(team_name: str, current_count: int, min_count: int = 8) -> BadRequestError:
    """Factory for roster too small errors."""
    return BadRequestError(
        message="Roster too small",
        detail=f"Team '{team_name}' has {current_count} players (minimum {min_count} required)"
    )


def invalid_starters(team_name: str, starter_count: int, required_count: int = 5) -> BadRequestError:
    """Factory for invalid starters errors."""
    return BadRequestError(
        message="Invalid starters",
        detail=f"Team '{team_name}' has {starter_count} starters (exactly {required_count} required)"
    )


def player_already_assigned(player_name: str, current_team: str) -> ConflictError:
    """Factory for player already assigned errors."""
    return ConflictError(
        message="Player already assigned",
        detail=f"Player '{player_name}' is already assigned to team '{current_team}'"
    )


def player_not_on_team(player_name: str, team_name: str) -> BadRequestError:
    """Factory for player not on team errors."""
    return BadRequestError(
        message="Player not on team",
        detail=f"Player '{player_name}' is not on team '{team_name}'"
    )


def starter_not_on_roster(starter_name: str, team_name: str) -> BadRequestError:
    """Factory for starter not on roster errors."""
    return BadRequestError(
        message="Starter not on roster",
        detail=f"Starter '{starter_name}' is not on team '{team_name}' roster"
    )