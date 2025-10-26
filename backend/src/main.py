"""
FastAPI application entry point for the Dodgeball Fantasy League.

This module configures the FastAPI application with CORS, routing, and middleware.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Import storage to initialize singleton
from .storage.memory_storage import MemoryStorage

# Import error handlers
from .api.errors import (
    APIError,
    api_error_handler,
    validation_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting Dodgeball Fantasy League API")
    storage = MemoryStorage()  # Initialize storage singleton
    logger.info(f"Storage initialized with stats: {storage.get_stats()}")

    yield

    # Shutdown
    logger.info("Shutting down Dodgeball Fantasy League API")


# Create FastAPI application
app = FastAPI(
    title="Dodgeball Fantasy League API",
    description="REST API for managing fantasy dodgeball leagues, teams, and games",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend dev server
        "http://localhost",       # Production frontend
        "http://127.0.0.1:3000", # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    storage = MemoryStorage()
    stats = storage.get_stats()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "storage_stats": stats,
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dodgeball Fantasy League API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Register error handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# Import and include routers
from .api import leagues, teams

app.include_router(leagues.router)
app.include_router(teams.router)
# Additional routers will be added as we implement them:
# from .api import games, players
# app.include_router(games.router, prefix="/api", tags=["games"])
# app.include_router(players.router, prefix="/api", tags=["players"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )