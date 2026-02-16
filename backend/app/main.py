"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes_story, routes_genre, routes_twist, routes_score

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered story generation and analysis API",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Story pipeline: Available at both /api/story/continue and /api/v1/story/continue
app.include_router(routes_story.router, prefix="/api/story")
app.include_router(routes_story.router, prefix=settings.API_V1_PREFIX + "/story")

# Other endpoints under /api/v1
app.include_router(routes_genre.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_twist.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_score.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
