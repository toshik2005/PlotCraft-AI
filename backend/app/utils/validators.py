"""Input validation for story text and API payloads."""

from typing import Optional, Tuple


def validate_story_text(
    text: Optional[str],
    min_length: int = 10,
    max_length: int = 5000,
) -> Tuple[bool, Optional[str]]:
    """
    Validate story text length and presence.
    Returns (is_valid, error_message).
    """
    if text is None:
        return False, "Text is required."
    s = text.strip()
    if not s:
        return False, "Text cannot be empty."
    if len(s) < min_length:
        return False, f"Text must be at least {min_length} characters."
    if len(s) > max_length:
        return False, f"Text must be at most {max_length} characters."
    return True, None
