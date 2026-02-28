"""Story scoring service."""

from textblob import TextBlob
from app.utils.text_preprocessing import clean_text, count_words
from app.utils.validators import validate_story_text
from app.core.constants import SCORING_WEIGHTS


def calculate_score(text: str) -> int:
    """Return a single score (0–100) for the given story text."""
    if not text or not text.strip():
        return 0
    result = ScoringService.score_story(text)
    return result["total_score"]


class ScoringService:
    """Service for story scoring operations."""
    
    @staticmethod
    def score_story(text: str) -> dict:
        """
        Score a story based on multiple criteria.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with score breakdown and total score
        """
        # Validate input
        is_valid, error = validate_story_text(text)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        try:
            # Sentiment analysis
            try:
                blob = TextBlob(cleaned_text)
                sentiment_polarity = blob.sentiment.polarity
                sentences = blob.sentences
            except Exception as e:
                # Fallback if TextBlob fails (e.g., missing nltk data)
                import logging
                logging.warning(f"TextBlob failed, using fallback: {e}")
                sentiment_polarity = 0.0
                sentences = cleaned_text.split('.')
            
            sentiment_score = (sentiment_polarity + 1) * SCORING_WEIGHTS["sentiment"] / 2
            
            # Length score (normalized to 0-1, then scaled)
            word_count = count_words(cleaned_text)
            length_score = min(word_count / 200, 1) * SCORING_WEIGHTS["length"]
            
            # Complexity score (based on sentence count and variety)
            sentence_count = len([s for s in sentences if s.strip()])
            complexity_score = min(sentence_count / 10, 1) * SCORING_WEIGHTS["complexity"]
            
            # Creativity score (based on unique words ratio)
            words = cleaned_text.lower().split()
            unique_words = len(set(words))
            total_words = len(words)
            creativity_ratio = unique_words / total_words if total_words > 0 else 0
            creativity_score = creativity_ratio * SCORING_WEIGHTS["creativity"]
            
            # Calculate total score
            total_score = int(sentiment_score + length_score + complexity_score + creativity_score)
            total_score = max(0, min(total_score, 100))
            
            return {
                "total_score": total_score,
                "breakdown": {
                    "sentiment": round(sentiment_score, 2),
                    "length": round(length_score, 2),
                    "complexity": round(complexity_score, 2),
                    "creativity": round(creativity_score, 2)
                },
                "metrics": {
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "sentiment_polarity": round(sentiment_polarity, 3),
                    "unique_words_ratio": round(creativity_ratio, 3)
                }
            }
        except Exception as e:
            raise RuntimeError(f"Story scoring failed: {str(e)}")
