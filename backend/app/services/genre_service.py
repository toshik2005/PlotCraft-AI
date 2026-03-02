"""Genre detection service."""

from typing import Optional, Dict, Tuple

from app.models.genre_model import genre_model
from app.utils.text_preprocessing import clean_text
from app.utils.validators import validate_story_text


def _map_to_plotcraft_genres(probabilities: Dict[str, float]) -> Tuple[str, Dict[str, float]]:
    """
    Map raw genre model probabilities to PlotCraft's three canonical genres.

    The underlying classifier is trained on labels like:
    - fantasy, horror, sci-fi, romance, mystery

    But PlotCraft only has models for: action, horror, scifi.
    We aggregate the raw probabilities into these three buckets and renormalize.
    """
    # Aggregate raw probabilities into three buckets
    action_raw = (
        probabilities.get("fantasy", 0.0)
        + probabilities.get("mystery", 0.0)
        + probabilities.get("romance", 0.0)
    )
    scifi_raw = probabilities.get("sci-fi", 0.0)
    horror_raw = probabilities.get("horror", 0.0)

    total = action_raw + scifi_raw + horror_raw
    if total <= 0:
        # Degenerate case: fall back to scifi
        mapped = {"action": 0.0, "scfi": 1.0, "horror": 0.0}
        return "scfi", mapped

    mapped = {
        "action": action_raw / total,
        "scifi": scifi_raw / total,
        "horror": horror_raw / total,
    }

    # Choose the dominant PlotCraft genre
    predicted = max(mapped.items(), key=lambda kv: kv[1])[0]
    return predicted, mapped


def get_genre(story: str, user_genre: Optional[str] = None) -> str:
    """
    Return user-provided genre if set, otherwise detect from story,
    always mapped to one of: action, horror, scifi.
    """
    if user_genre and user_genre.strip():
        return user_genre.strip().lower()

    result = GenreService.detect_genre(story)
    return result["genre"]


class GenreService:
    """Service for genre detection operations."""
    
    @staticmethod
    def detect_genre(text: str) -> dict:
        """
        Detect genre from story text, mapped to PlotCraft's three models.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with detected genre and confidence scores:
            {
                "genre": "action" | "horror" | "scifi",
                "confidence": float,
                "all_probabilities": { "action": float, "horror": float, "scfi": float }
            }
        """
        # Validate input
        is_valid, error = validate_story_text(text, min_length=5)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        try:
            # Get raw probability distribution from the underlying classifier
            probabilities = genre_model.predict_proba(cleaned_text)

            # Map raw labels to PlotCraft's three genres
            mapped_genre, mapped_probs = _map_to_plotcraft_genres(probabilities)
            confidence = mapped_probs.get(mapped_genre, 0.0)
            
            return {
                "genre": mapped_genre,
                "confidence": round(confidence, 3),
                "all_probabilities": {
                    genre: round(prob, 3) 
                    for genre, prob in mapped_probs.items()
                },
            }
        except Exception as e:
            raise RuntimeError(f"Genre detection failed: {str(e)}")
