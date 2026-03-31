"""Text preprocessing helpers for story pipelines."""

import re
from typing import Optional


def _find_last_sentence_end(text: str) -> int:
    """Find the index of the last proper sentence-ending punctuation."""
    for i in range(len(text) - 1, -1, -1):
        if text[i] in ".!?":
            return i + 1
    return 0


def postprocess_generated_story(text: str) -> str:
    """
    Clean generated story text:
    - Remove parenthetical fragments like (Dec) or (Dec) C
    - Trim to last complete sentence (avoid hanging mid-sentence)
    - Normalize whitespace
    """
    if not text or not text.strip():
        return text

    # Remove "glitch" blocks: runs of ALL-CAPS words (often model artifacts)
    # Example: "LOGINNSWATION OF THE TURD BEK. ... TRY. ASMENTER – 1103 AM"
    text = re.sub(
        r"(?:\b[A-Z]{2,}\b\s+){2,}\b[A-Z]{8,}\b(?:\s+\b[A-Z]{2,}\b){0,}",
        " ",
        text,
    )
    text = re.sub(
        r"\b[A-Z]{8,}\b(?:\s+\b[A-Z]{2,}\b){2,}",
        " ",
        text,
    )

    # Remove dangling timestamp fragments like "– 1103 AM" that sometimes trail glitch blocks
    text = re.sub(r"\s*[–-]\s*\d{1,4}\s*(?:AM|PM)\b", " ", text, flags=re.IGNORECASE)

    # Remove parenthetical fragments: (Word) or (Word) single_letter
    text = re.sub(r"\s*\(\s*[A-Za-z]+\s*\)\s*[A-Za-z]?\s*", " ", text)
    # Remove orphaned fragments like ". (Dec)" or "g." (Dec)
    text = re.sub(r"\.[\s]*\(\s*[A-Za-z]+\s*\)[\s]*", ". ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Trim to last complete sentence so story doesn't end mid-sentence
    last_end = _find_last_sentence_end(text)
    if last_end > 0 and last_end < len(text):
        remainder = text[last_end:].strip()
        # If there's trailing content that looks incomplete, trim it
        if not remainder or len(remainder) < 30 or not remainder.rstrip().endswith((".", "!", "?")):
            text = text[:last_end].rstrip()

    return text


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
