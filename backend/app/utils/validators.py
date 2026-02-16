"""Input validation utilities."""

from typing import Optional, Tuple


def validate_story_text(text: Optional[str], min_length: int = 10, max_length: int = 5000) -> Tuple[bool, Optional[str]]:
    """
    Validate story text input.
    
    Returns:
        (is_valid, error_message)
    """
    if not text:
        return False, "Story text cannot be empty"
    
    if not isinstance(text, str):
        return False, "Story text must be a string"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Story text must be at least {min_length} characters long"
    
    if len(text) > max_length:
        return False, f"Story text must not exceed {max_length} characters"
    
    return True, None


def validate_genre(genre: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Validate genre input."""
    from app.core.constants import GENRES
    
    if not genre:
        return False, "Genre cannot be empty"
    
    if genre.lower() not in [g.lower() for g in GENRES]:
        return False, f"Genre must be one of: {', '.join(GENRES)}"
    
    return True, None
