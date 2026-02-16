"""Genre detection service."""

from app.models.genre_model import genre_model
from app.utils.text_preprocessing import clean_text
from app.utils.validators import validate_story_text


class GenreService:
    """Service for genre detection operations."""
    
    @staticmethod
    def detect_genre(text: str) -> dict:
        """
        Detect genre from story text.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with detected genre and confidence scores
        """
        # Validate input
        is_valid, error = validate_story_text(text, min_length=5)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        try:
            # Predict genre
            predicted_genre = genre_model.predict(cleaned_text)
            
            # Get probability distribution
            probabilities = genre_model.predict_proba(cleaned_text)
            
            # Get confidence (probability of predicted genre)
            confidence = probabilities.get(predicted_genre, 0.0)
            
            return {
                "genre": predicted_genre,
                "confidence": round(confidence, 3),
                "all_probabilities": {
                    genre: round(prob, 3) 
                    for genre, prob in probabilities.items()
                }
            }
        except Exception as e:
            raise RuntimeError(f"Genre detection failed: {str(e)}")
