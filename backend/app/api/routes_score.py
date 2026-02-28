"""Story scoring API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import ScoreInput, ScoreResponse, CharacterInput, CharacterResponse
from app.schemas.response_schema import APIResponse
from app.services.scoring_service import ScoringService
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/score", tags=["Scoring"])


@router.post("/story", response_model=APIResponse)
async def score_story(input_data: ScoreInput):
    """
    Score a story based on multiple criteria.
    
    - **text**: Story text to score
    """
    try:
        result = ScoringService.score_story(input_data.text)
        
        return APIResponse(
            success=True,
            message="Story scored successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/characters", response_model=APIResponse)
async def extract_characters(input_data: CharacterInput):
    """
    Extract characters from story text.
    
    - **text**: Story text to extract characters from
    """
    try:
        result = MemoryService.extract_characters(input_data.text)
        
        return APIResponse(
            success=True,
            message="Characters extracted successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
