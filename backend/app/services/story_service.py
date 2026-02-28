"""Story generation service."""

from typing import List, Tuple

from app.models.story_generator import story_generator, generate_story
from app.services.scoring_service import calculate_score
from app.utils.text_preprocessing import clean_text, truncate_text
from app.utils.validators import validate_story_text

# Optional: PlotCraft trained model (backend/plotcraft). Used when available.
try:
    from plotcraft.src.plotcraft_generator import (
        generate_text as plotcraft_generate_text,
        PlotCraftUnavailable,
    )
except ImportError:
    plotcraft_generate_text = None
    PlotCraftUnavailable = Exception  # noqa: A001


def _strip_prompt_from_continuation(prompt: str, full_output: str) -> str:
    """Remove the prompt from model output so we return only the continuation."""
    if full_output.startswith(prompt):
        return full_output[len(prompt) :].lstrip()
    return full_output


def continue_story_pipeline(story: str, genre: str, characters: List[str]) -> Tuple[str, int]:
    """
    Full pipeline: build prompt → generate continuation (PlotCraft or fallback) → score.
    Uses PlotCraft model when checkpoint/tokenizer exist; otherwise uses transformers.
    Returns (continuation, score).
    """
    story_for_prompt = truncate_text(clean_text(story), max_length=500)
    prompt = f"""You are a creative AI storyteller.

Continue this {genre} story.
Maintain consistency with these characters: {characters}.
Do not repeat the original text.

Story:
{story_for_prompt}

Continuation:
"""

    continuation: str
    if plotcraft_generate_text is not None:
        try:
            # Select PlotCraft model by genre.
            genre_key = (genre or "").strip().lower()
            if "horror" in genre_key:
                model_name = "horror"
            elif "action" in genre_key:
                model_name = "action"
            else:
                model_name = "scifi"  # sci-fi, scifi, science fiction, auto-detected, etc.
            continuation = plotcraft_generate_text(prompt, max_tokens=800, model_name=model_name)
        except PlotCraftUnavailable:
            continuation = generate_story(prompt)
    else:
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
