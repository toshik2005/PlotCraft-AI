"""Story pipeline API routes for multi-genre story generation."""

import logging
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.schemas.story_schema import (
    GenerateStoryRequest,
    GenerateStoryResponse,
    StoryRequest,
    StoryResponse,
    StoryInput,
)
from app.services.genre_service import get_genre
from app.services.memory_service import get_characters
from app.services.story_service import (
    continue_story_pipeline,
    generate_story_pipeline,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Story"])


# ============================================================================
# MAIN ENDPOINT: Complete multi-genre story generation pipeline
# ============================================================================

@router.post("/generate", response_model=GenerateStoryResponse)
async def generate_story(request: GenerateStoryRequest) -> GenerateStoryResponse:
    """
    Generate a story with advanced features: character persistence, twist injection,
    refinement, and scoring.
    
    Supports three genres:
    - **action**: High-paced action stories with conflict and resolution
    - **horror**: Suspenseful and scary narrative with atmosphere
    - **scifi**: Science fiction with futuristic concepts and technology
    
    Features:
    - Multi-turn character persistence across requests
    - Twist injection (unexpected, reversal, revelation, betrayal, discovery)
    - Optional story refinement for narrative coherence
    - Quality scoring based on multiple metrics
    - Automatic character-focus regeneration if needed
    
    Args:
        user_id: Unique identifier for the user session
        story: Story prompt or continuation request
        genre: One of [action, horror, scifi]
        twist: Optional twist type
        refine: Whether to improve story coherence
        measure: Whether to score the story
        temperature: Creativity parameter (0.1=focused, 2.0=creative)
        max_tokens: Maximum tokens to generate
    
    Returns:
        GenerateStoryResponse with generated story and metadata
    
    Example request:
    ```json
    {
        "user_id": "user_123",
        "story": "Alice found a mysterious door in the forest",
        "genre": "horror",
        "twist": "revelation",
        "refine": true,
        "measure": true,
        "temperature": 0.85,
        "max_tokens": 350
    }
    ```
    
    Raises:
        HTTPException 400: Invalid input or validation failed
        HTTPException 500: Generation failed
    """
    try:
        logger.info(f"POST /api/story/generate for user {request.user_id}")
        
        # Validate user_id
        if not request.user_id or not request.user_id.strip():
            logger.warning("Missing user_id")
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Run the complete pipeline
        result = generate_story_pipeline(
            user_id=request.user_id,
            prompt=request.story,
            genre=request.genre,
            twist=request.twist,
            refine=request.refine,
            measure=request.measure,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        # Map to response model
        response = GenerateStoryResponse(
            genre=result["genre"],
            detected_characters=result["detected_characters"],
            persisted_characters=result["persisted_characters"],
            twist_applied=result.get("twist_applied"),
            generated_text=result["generated_text"],
            refined=result.get("refined", False),
            score=result.get("score"),
            character_focus_required=result.get("character_focus_required", False),
        )
        
        logger.info(f"Story generated successfully for user {request.user_id}")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Story generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


# ============================================================================
# LEGACY ENDPOINT: Simple story continuation (backward compatible)
# ============================================================================

@router.post("/continue", response_model=StoryResponse)
async def continue_story(request: StoryRequest) -> StoryResponse:
    """
    Continue a story with basic features (legacy endpoint).
    
    This endpoint maintains backward compatibility with the original API.
    For new features, use POST /api/story/generate instead.
    
    Automatically detects:
    - Genre from story content
    - Character names
    - Quality score
    
    Args:
        story: Story text to continue
        genre: Optional genre override
    
    Returns:
        StoryResponse with continuation and metadata
    
    Deprecated:
        Use POST /api/story/generate for advanced features
    """
    try:
        logger.info("POST /api/story/continue (legacy endpoint) - starting")
        
        # Validate input
        if not request.story or not request.story.strip():
            logger.warning("Missing or empty story text")
            raise HTTPException(status_code=400, detail="Story text is required")
        
        story = request.story.strip()
        genre = request.genre
        
        # Detect genre
        logger.info("Detecting genre...")
        try:
            detected_genre = get_genre(story, genre)
            logger.info(f"Detected genre: {detected_genre}")
        except Exception as e:
            logger.error(f"Genre detection failed: {e}")
            detected_genre = "general"
        
        # Extract characters
        logger.info("Extracting characters...")
        try:
            characters = get_characters(story)
            logger.info(f"Extracted {len(characters)} characters")
        except Exception as e:
            logger.error(f"Character extraction failed: {e}")
            characters = []

        # Generate continuation and score with timeout protection
        logger.info("Generating continuation and calculating score...")
        try:
            continuation, score = continue_story_pipeline(
                story,
                detected_genre,
                characters,
            )
            logger.info(f"Generated continuation ({len(continuation)} chars), score: {score}")
        except TimeoutError as e:
            logger.error(f"Generation timeout: {e}")
            raise HTTPException(status_code=504, detail="Story generation timed out. Please try with a shorter prompt.")
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

        logger.info("Legacy story continuation successful - returning response")
        return StoryResponse(
            detected_genre=detected_genre,
            characters=characters,
            continuation=continuation,
            score=score,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please check the logs.")
