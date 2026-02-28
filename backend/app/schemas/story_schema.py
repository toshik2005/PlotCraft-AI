"""Pydantic schemas for story-related requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ============================================================================
# MULTI-GENRE STORY GENERATION PIPELINE (NEW)
# ============================================================================

class GenerateStoryRequest(BaseModel):
    """Request body for complete story generation pipeline."""
    
    user_id: str = Field(..., description="Unique user/session identifier")
    story: str = Field(..., min_length=10, max_length=5000, description="Story prompt or continuation request")
    genre: str = Field("scifi", description="Story genre: action, horror, or scifi (default: scifi)")
    
    # Advanced options
    twist: Optional[str] = Field(
        None,
        description="Twist type: unexpected, reversal, revelation, betrayal, or discovery"
    )
    refine: bool = Field(False, description="Refine generated story for coherence (default: false)")
    measure: bool = Field(True, description="Score the generated story (default: true)")
    
    # Generation parameters
    temperature: float = Field(0.8, ge=0.1, le=2.0, description="Sampling temperature (default: 0.8)")
    max_tokens: int = Field(300, ge=50, le=1000, description="Max tokens to generate (default: 300)")
    
    class Config:
        """Pydantic config."""
        examples = [
            {
                "user_id": "user_123",
                "story": "Alice walked through the dark forest when she heard a mysterious sound.",
                "genre": "horror",
                "twist": "revelation",
                "refine": True,
                "measure": True,
                "temperature": 0.85,
                "max_tokens": 300
            }
        ]


class GenerateStoryResponse(BaseModel):
    """Response for complete story generation pipeline."""
    
    genre: str = Field(..., description="The genre used for generation")
    detected_characters: List[str] = Field(..., description="Characters detected in the prompt")
    persisted_characters: List[str] = Field(..., description="All characters for this user session")
    twist_applied: Optional[str] = Field(None, description="Twist type applied if any")
    generated_text: str = Field(..., description="The generated story continuation")
    refined: bool = Field(False, description="Whether story was refined")
    score: Optional[float] = Field(None, description="Story quality score if measured")
    character_focus_required: bool = Field(False, description="Whether second-pass generation was needed")
    
    class Config:
        """Pydantic config."""
        examples = [
            {
                "genre": "horror",
                "detected_characters": ["Alice"],
                "persisted_characters": ["Alice", "Bob"],
                "twist_applied": "revelation",
                "generated_text": "As Alice ventured deeper, she realized the truth about the forest...",
                "refined": True,
                "score": 3.87,
                "character_focus_required": False
            }
        ]


# ============================================================================
# LEGACY ENDPOINTS (BACKWARD COMPATIBLE)
# ============================================================================

class StoryRequest(BaseModel):
    """Request body for story continuation pipeline (legacy)."""
    story: str = Field(..., min_length=1, max_length=5000, description="Story text to continue")
    genre: Optional[str] = Field(None, description="Optional genre; if null, genre is detected from story")


class StoryResponse(BaseModel):
    """Response for story continuation pipeline (legacy)."""
    detected_genre: str
    characters: List[str]
    continuation: str
    score: int


# ---- Other legacy endpoints ----

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

