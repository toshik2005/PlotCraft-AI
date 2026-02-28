"""Genre detection API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import GenreInput, GenreResponse
from app.schemas.response_schema import APIResponse
from app.services.genre_service import GenreService

router = APIRouter(prefix="/genre", tags=["Genre"])


@router.post("/detect", response_model=APIResponse)
async def detect_genre(input_data: GenreInput):
    """
    Detect genre from story text.
    
    - **text**: Story text to analyze
    """
    try:
        result = GenreService.detect_genre(input_data.text)
        
        return APIResponse(
            success=True,
            message="Genre detected successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
