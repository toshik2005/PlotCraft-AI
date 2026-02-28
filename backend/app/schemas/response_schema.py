"""Common response schemas."""

from pydantic import BaseModel
from typing import Optional, Any, List


class APIResponse(BaseModel):
    """Standard API response schema."""
    success: bool
    message: str = ""
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    message: str
    error: str
    detail: Optional[str] = None
