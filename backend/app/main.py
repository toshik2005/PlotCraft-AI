"""
FastAPI application entry point.

Mounts all API routers and middleware. Use run.py to start the server.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import routes_story, routes_score, routes_genre

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered story generation and analysis API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Story pipeline: /api/story and /api/v1/story
app.include_router(routes_story.router, prefix="/api/story")
app.include_router(routes_story.router, prefix=settings.API_V1_PREFIX + "/story")

# Other v1 endpoints
app.include_router(routes_genre.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_score.router, prefix=settings.API_V1_PREFIX)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and handle connection errors gracefully."""
    try:
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
