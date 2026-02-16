"""Story generation service."""

from typing import List, Tuple

from app.models.story_generator import story_generator, generate_story
from app.services.scoring_service import calculate_score
from app.utils.text_preprocessing import clean_text, truncate_text
from app.utils.validators import validate_story_text


def continue_story_pipeline(story: str, genre: str, characters: List[str]) -> Tuple[str, int]:
    """
    Full pipeline: build prompt → generate continuation → score full text.
    Returns (continuation, score).
    """
    story_for_prompt = truncate_text(clean_text(story), max_length=500)
    prompt = f"""Continue this {genre} story.
Maintain character consistency: {characters}

Story:
{story_for_prompt}
"""
    continuation = generate_story(prompt)
    full_text = clean_text(story) + " " + continuation
    score = calculate_score(full_text)
    return continuation, score


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
