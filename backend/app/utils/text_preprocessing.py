"""Text preprocessing helpers for story pipelines."""

import re
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """Normalize whitespace and strip."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text).strip())


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate to at most max_length characters, on a word boundary if possible."""
    if len(text) <= max_length:
        return text
    truncated = text[: max_length + 1]
    last_space = truncated.rfind(" ")
    if last_space > max_length // 2:
        return truncated[:last_space].strip()
    return truncated.strip()


def count_words(text: str) -> int:
    """Count words (split on whitespace)."""
    return len(text.split()) if text and text.strip() else 0
