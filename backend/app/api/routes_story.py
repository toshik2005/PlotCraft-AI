"""Story pipeline API routes."""

from fastapi import APIRouter, HTTPException
# from fastapi import Request
from typing import Optional, Union

from app.schemas.story_schema import StoryRequest, StoryResponse, StoryInput
from app.services.genre_service import get_genre
from app.services.memory_service import get_characters
from app.services.story_service import continue_story_pipeline

router = APIRouter(tags=["Story"])


@router.post("/continue", response_model=StoryResponse)
async def continue_story(request: StoryRequest):

    """
    Full story pipeline: validate → detect genre → extract characters
    → build prompt → generate continuation → score → response.
    
    Accepts both formats:
    - New: {"story": "...", "genre": "..."}
    - Legacy: {"text": "...", "max_length": 150, "temperature": 0.8}
    """
    try:
        story = request.story
        genre = request.genre
        
        detected_genre = get_genre(story, genre)
        characters = get_characters(story)

        continuation, score = continue_story_pipeline(
            story,
            detected_genre,
            characters,
        )

        return StoryResponse(
            detected_genre=detected_genre,
            characters=characters,
            continuation=continuation,
            score=score,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
