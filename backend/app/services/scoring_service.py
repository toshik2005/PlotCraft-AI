"""Story scoring service."""

import json
import logging

from textblob import TextBlob

from app.core.constants import SCORING_WEIGHTS
from app.utils.text_preprocessing import clean_text, count_words
from app.utils.validators import validate_story_text

logger = logging.getLogger(__name__)


def calculate_score(text: str) -> int:
    """Return a single score (0–100) for the given story text."""
    if not text or not text.strip():
        return 0
    result = ScoringService.score_story(text)
    return result["total_score"]


def _score_story_heuristic(text: str) -> dict:
    """Original TextBlob + heuristic scoring (fallback when Groq is unavailable)."""
    cleaned_text = clean_text(text)
    try:
        try:
            blob = TextBlob(cleaned_text)
            sentiment_polarity = blob.sentiment.polarity
            sentences = blob.sentences
        except Exception as e:
            logger.warning("TextBlob failed, using fallback: %s", e)
            sentiment_polarity = 0.0
            sentences = cleaned_text.split(".")

        sentiment_score = (sentiment_polarity + 1) * SCORING_WEIGHTS["sentiment"] / 2

        word_count = count_words(cleaned_text)
        length_score = min(word_count / 200, 1) * SCORING_WEIGHTS["length"]

        sentence_count = len([s for s in sentences if str(s).strip()])
        complexity_score = min(sentence_count / 10, 1) * SCORING_WEIGHTS["complexity"]

        words = cleaned_text.lower().split()
        unique_words = len(set(words))
        total_words = len(words)
        creativity_ratio = unique_words / total_words if total_words > 0 else 0
        creativity_score = creativity_ratio * SCORING_WEIGHTS["creativity"]

        total_score = int(sentiment_score + length_score + complexity_score + creativity_score)
        total_score = max(0, min(total_score, 100))

        return {
            "total_score": total_score,
            "breakdown": {
                "sentiment": round(sentiment_score, 2),
                "length": round(length_score, 2),
                "complexity": round(complexity_score, 2),
                "creativity": round(creativity_score, 2),
            },
            "metrics": {
                "word_count": float(word_count),
                "sentence_count": float(sentence_count),
                "sentiment_polarity": round(sentiment_polarity, 3),
                "unique_words_ratio": round(creativity_ratio, 3),
            },
        }
    except Exception as e:
        raise RuntimeError(f"Story scoring failed: {str(e)}") from e


class ScoringService:
    """Service for story scoring operations."""

    @staticmethod
    def score_story(text: str) -> dict:
        """
        Score a story using Groq when configured; fall back to local heuristics.

        Returns:
            Dictionary with score breakdown and total score
        """
        is_valid, error = validate_story_text(text)
        if not is_valid:
            raise ValueError(error)

        try:
            from app.services.groq_service import GroqUnavailable, score_story_with_groq

            return score_story_with_groq(text)
        except GroqUnavailable as e:
            logger.warning("Groq scoring unavailable, using heuristic fallback: %s", e)
            return _score_story_heuristic(text)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning("Groq scoring parse error, using heuristic fallback: %s", e)
            return _score_story_heuristic(text)
