"""Application settings loaded from environment."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "PlotCraft-AI"
    VERSION: str = "1.0.0"

    # Models
    SPACY_MODEL: str = "en_core_web_sm"
    TEXT_GENERATION_MODEL: str = "distilgpt2"
    MAX_STORY_LENGTH: int = 150

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
