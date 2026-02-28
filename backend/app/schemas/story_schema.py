"""Pydantic schemas for story-related requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ---- Story pipeline (POST /api/story/continue) ----

class StoryRequest(BaseModel):
    """Request body for story continuation pipeline."""
    story: str = Field(..., min_length=1, max_length=5000, description="Story text to continue")
    genre: Optional[str] = Field(None, description="Optional genre; if null, genre is detected from story")


class StoryResponse(BaseModel):
    """Response for story continuation pipeline."""
    detected_genre: str
    characters: List[str]
    continuation: str
    score: int


# ---- Legacy / other endpoints ----

class StoryInput(BaseModel):
    """Input schema for story generation."""
    text: str = Field(..., min_length=10, max_length=5000, description="Story text to continue")
    max_length: Optional[int] = Field(150, ge=50, le=500, description="Maximum length for generation")
    temperature: Optional[float] = Field(0.8, ge=0.1, le=2.0, description="Sampling temperature")


class GenreInput(BaseModel):
    """Input schema for genre detection."""
    text: str = Field(..., min_length=5, max_length=5000, description="Story text to analyze")


class TwistInput(BaseModel):
    """Input schema for twist generation."""
    text: str = Field(..., min_length=10, max_length=5000, description="Story text to add twist to")
    twist_type: Optional[str] = Field("unexpected", description="Type of twist to generate")


class ScoreInput(BaseModel):
    """Input schema for story scoring."""
    text: str = Field(..., min_length=10, max_length=5000, description="Story text to score")


class CharacterInput(BaseModel):
    """Input schema for character extraction."""
    text: str = Field(..., min_length=5, max_length=5000, description="Story text to extract characters from")


class StoryDetailResponse(BaseModel):
    """Detailed response schema for story generation (legacy)."""
    original_text: str
    generated_text: str
    full_story: str
    input_length: int
    generated_length: int


class GenreResponse(BaseModel):
    """Response schema for genre detection."""
    genre: str
    confidence: float
    all_probabilities: Dict[str, float]


class TwistResponse(BaseModel):
    """Response schema for twist generation."""
    twist: str
    twist_type: str
    full_story_with_twist: str
    prompt_used: str


class ScoreResponse(BaseModel):
    """Response schema for story scoring."""
    total_score: int
    breakdown: Dict[str, float]
    metrics: Dict[str, float]


class CharacterResponse(BaseModel):
    """Response schema for character extraction."""
    characters: List[str]
    count: int
