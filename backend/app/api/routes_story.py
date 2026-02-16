"""Story generation API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import StoryInput, StoryResponse
from app.schemas.response_schema import APIResponse
from app.services.story_service import StoryService

router = APIRouter(prefix="/story", tags=["Story"])


@router.post("/continue", response_model=APIResponse)
async def continue_story(input_data: StoryInput):
    """
    Generate story continuation.
    
    - **text**: Story text to continue
    - **max_length**: Maximum length for generation (default: 150)
    - **temperature**: Sampling temperature (default: 0.8)
    """
    try:
        result = StoryService.continue_story(
            text=input_data.text,
            max_length=input_data.max_length,
            temperature=input_data.temperature
        )
        
        return APIResponse(
            success=True,
            message="Story continuation generated successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
