"""Character identification request/response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional


class IdentifyCharacterRequest(BaseModel):
    """Request schema for character identification."""
    text: str = Field(
        ...,
        description="Story text to extract characters from",
        min_length=1,
        example="Alice found a mysterious door in the forest. Bob was waiting outside."
    )
    max_characters: Optional[int] = Field(
        default=5,
        description="Maximum number of characters to return",
        ge=1,
        le=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Alice found a mysterious door in the forest. Bob was waiting outside.",
                "max_characters": 5
            }
        }


class IdentifyCharacterResponse(BaseModel):
    """Response schema for character identification."""
    success: bool = Field(
        default=True,
        description="Whether the character identification was successful"
    )
    characters: List[str] = Field(
        default_factory=list,
        description="List of identified character names",
        example=["Alice", "Bob"]
    )
    count: int = Field(
        default=0,
        description="Number of characters identified",
        example=2
    )
    method: str = Field(
        default="spacy",
        description="Method used for character extraction (spacy or regex)",
        example="spacy"
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message or status information",
        example=None
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "characters": ["Alice", "Bob"],
                "count": 2,
                "method": "spacy",
                "message": None
            }
        }
