"""
Step 1: Clean raw Sci‑Fi text for training.

Loads backend/ml/data/raw/scifi.txt, applies cleaning, and saves to
backend/ml/data/processed/cleaned_scifi.txt.

Run from backend directory:
    python -m ml.preprocessing.clean_data
Or (from backend/ml):  python preprocessing/clean_data.py  (with path hacks).
"""

import re
from pathlib import Path

# Resolve paths relative to backend root (parent of ml/)
BACKEND_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = BACKEND_ROOT / "ml" / "data" / "raw" / "scifi.txt"
PROCESSED_PATH = BACKEND_ROOT / "ml" / "data" / "processed" / "cleaned_scifi.txt"


def clean_text(text: str) -> str:
    """
    Clean raw story text:
    - Remove empty lines
    - Keep only letters, digits, and punctuation
    - Lowercase
    - Normalize whitespace to single spaces
    """
    # Remove empty lines (and lines that are only whitespace)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    joined = " ".join(lines)

    # Lowercase
    joined = joined.lower()

    # Keep only letters, digits, and common punctuation
    # Remove other special characters (keep . , ! ? ' " - : ; ( ) etc.)
    joined = re.sub(r"[^a-z0-9\s.,!?\'\"\-:;()]", "", joined)

    # Normalize whitespace: collapse multiple spaces/newlines to single space
    joined = re.sub(r"\s+", " ", joined).strip()

    return joined


def main() -> None:
    print(f"Loading raw text from {RAW_PATH}")
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}")

    with open(RAW_PATH, "r", encoding="utf-8", errors="replace") as f:
        raw_text = f.read()

    full_cleaned = clean_text(raw_text)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        f.write(full_cleaned)

    print(f"Cleaned text saved to {PROCESSED_PATH} ({len(full_cleaned)} chars, {len(full_cleaned.split())} words)")


if __name__ == "__main__":
    main()
