"""Story twist API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import TwistInput, TwistResponse
from app.schemas.response_schema import APIResponse
from app.services.twist_service import TwistService

router = APIRouter(prefix="/twist", tags=["Twist"])


@router.post("/generate", response_model=APIResponse)
async def generate_twist(input_data: TwistInput):
    """
    Generate a plot twist for the story.
    
    - **text**: Story text to add twist to
    - **twist_type**: Type of twist (unexpected, reversal, revelation, betrayal, discovery)
    """
    try:
        result = TwistService.generate_twist(
            text=input_data.text,
            twist_type=input_data.twist_type
        )
        
        return APIResponse(
            success=True,
            message="Twist generated successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
