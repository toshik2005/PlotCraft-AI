"""Story generation service."""

from app.models.story_generator import story_generator
from app.utils.text_preprocessing import clean_text, truncate_text
from app.utils.validators import validate_story_text


class StoryService:
    """Service for story generation operations."""
    
    @staticmethod
    def continue_story(
        text: str,
        max_length: int = None,
        temperature: float = 0.8
    ) -> dict:
        """
        Generate story continuation.
        
        Args:
            text: Input story text
            max_length: Maximum length for generation
            temperature: Sampling temperature
        
        Returns:
            Dictionary with generated story and metadata
        """
        # Validate input
        is_valid, error = validate_story_text(text)
        if not is_valid:
            raise ValueError(error)
        
        # Clean and prepare text
        cleaned_text = clean_text(text)
        
        # Truncate if too long (to avoid model limits)
        input_text = truncate_text(cleaned_text, max_length=500)
        
        try:
            # Generate continuation
            generated_text = story_generator.generate(
                text=input_text,
                max_length=max_length,
                temperature=temperature
            )
            
            # Combine original and generated
            full_story = cleaned_text + " " + generated_text
            
            return {
                "original_text": cleaned_text,
                "generated_text": generated_text,
                "full_story": full_story,
                "input_length": len(cleaned_text),
                "generated_length": len(generated_text)
            }
        except Exception as e:
            raise RuntimeError(f"Story generation failed: {str(e)}")
