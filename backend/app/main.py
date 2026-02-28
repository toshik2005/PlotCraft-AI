"""
FastAPI application entry point.

Mounts all API routers and middleware. Use run.py to start the server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import routes_story, routes_genre, routes_twist, routes_score

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
app.include_router(routes_twist.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_score.router, prefix=settings.API_V1_PREFIX)


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
    return {"status": "healthy"}
