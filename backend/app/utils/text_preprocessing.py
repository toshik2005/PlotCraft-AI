"""Text preprocessing utilities."""

import re
from typing import List


def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text."""
    if not text:
        return []
    
    # Simple sentence splitting (can be enhanced with NLP)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    
    words = text.split()
    return len(words)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length."""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."
