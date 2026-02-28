"""
Multi-genre story generation service with advanced features.

Implements a complete pipeline:
1. Character detection and persistence
2. Prompt enhancement with twists and character focus
3. Genre-specific model generation (PlotCraft preferred, fallback to transformers)
4. Story refinement for coherence
5. Quality scoring
6. Character-centered regeneration if needed

Supports: Action, Horror, Sci-Fi genres with multi-turn session persistence.
"""

import logging
from typing import List, Tuple, Optional, Dict

from app.models.story_generator import story_generator, generate_story
from app.services.scoring_service import calculate_score
from app.services.memory_service import (
    get_characters,
    save_user_characters,
    get_user_characters,
)
from app.services.twist_service import apply_twist_to_prompt
from app.utils.text_preprocessing import clean_text, truncate_text
from app.utils.validators import validate_story_text

logger = logging.getLogger(__name__)

# Optional: PlotCraft trained model (backend/plotcraft). Used when available.
try:
    from plotcraft.src.plotcraft_generator import (
        generate_text as plotcraft_generate_text,
        PlotCraftUnavailable,
    )
except ImportError:
    plotcraft_generate_text = None
    PlotCraftUnavailable = Exception  # noqa: A001


# ============================================================================
# GENERATION HELPERS
# ============================================================================

def _strip_prompt_from_continuation(prompt: str, full_output: str) -> str:
    """Remove the prompt from model output to return only the continuation."""
    if full_output.startswith(prompt):
        return full_output[len(prompt) :].lstrip()
    return full_output


def _generate_with_plotcraft_fallback(
    prompt: str,
    genre: str,
    max_tokens: int = 300,
    temperature: float = 0.8,
) -> str:
    """
    Generate text using PlotCraft if available, otherwise fallback to transformers.
    
    Args:
        prompt: Generation prompt
        genre: Story genre (action, horror, scifi)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    
    Returns:
        Generated text continuation
    
    Raises:
        TimeoutError: If generation takes too long
        RuntimeError: If all generation methods fail
    """
    continuation: str
    last_error = None
    
    if plotcraft_generate_text is not None:
        try:
            # Map genre to PlotCraft model
            genre_key = (genre or "").strip().lower()
            if "horror" in genre_key:
                model_name = "horror"
            elif "action" in genre_key:
                model_name = "action"
            else:
                model_name = "scifi"
            
            logger.info(f"Generating with PlotCraft model: {model_name}")
            continuation = plotcraft_generate_text(
                prompt,
                max_tokens=max_tokens,
                model_name=model_name,
                temperature=temperature,
            )
            logger.info(f"PlotCraft generation successful ({len(continuation)} tokens)")
            return continuation
        except (PlotCraftUnavailable, Exception) as e:
            logger.warning(f"PlotCraft generation failed: {e}. Falling back to transformers.")
            last_error = e
    else:
        logger.info("PlotCraft unavailable. Using transformers as primary.")
    
    # Fallback to transformers
    try:
        logger.info("Generating with transformers model...")
        continuation = generate_story(prompt, max_length=max_tokens, temperature=temperature)
        logger.info(f"Transformers generation successful ({len(continuation)} tokens)")
        return continuation
    except Exception as e:
        logger.error(f"Transformers generation failed: {e}", exc_info=True)
        last_error = e
    
    # If we get here, both methods failed
    error_msg = f"All generation methods failed. Last error: {str(last_error)}"
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def _check_character_presence(text: str, characters: List[str]) -> Tuple[bool, float]:
    """
    Check if characters are present in generated text.
    
    Args:
        text: Generated text
        characters: List of character names to check
    
    Returns:
        Tuple of (all_present: bool, presence_ratio: float)
    """
    if not characters:
        return True, 1.0
    
    text_lower = text.lower()
    found = sum(1 for char in characters if char.lower() in text_lower)
    ratio = found / len(characters)
    all_present = found == len(characters)
    
    return all_present, ratio


def _refine_story(
    text: str,
    genre: str,
    temperature: float = 0.7,
) -> str:
    """
    Refine a generated story for coherence and narrative focus.
    
    Args:
        text: Story text to refine
        genre: Story genre
        temperature: Sampling temperature (usually lower for refinement)
    
    Returns:
        Refined story text
    """
    if not text or not text.strip():
        return text
    
    refinement_prompt = f"""You are an expert editor specializing in {genre} stories.

Rewrite the following story to:
- Improve narrative coherence and flow
- Reduce repetition and redundant phrases
- Strengthen character development and dialogue
- Enhance descriptive language and atmosphere
- Maintain the original plot and key events

Original Story:
{text}

Refined Story:
"""
    
    logger.info(f"Refining story ({genre} genre)")
    
    refined = _generate_with_plotcraft_fallback(
        refinement_prompt,
        genre,
        max_tokens=500,
        temperature=temperature,
    )
    
    return refined.strip()


def _regenerate_for_character_focus(
    base_prompt: str,
    genre: str,
    characters: List[str],
    main_character: Optional[str] = None,
    max_tokens: int = 300,
) -> str:
    """
    Perform second-pass generation focused on main character.
    
    Used when generation drifts away from character focus.
    
    Args:
        base_prompt: Original prompt
        genre: Story genre
        characters: List of characters
        main_character: Primary character to focus on
        max_tokens: Generation tokens
    
    Returns:
        Character-focused generated text
    """
    if not main_character or not main_character.strip():
        if characters:
            main_character = characters[0]
        else:
            return _generate_with_plotcraft_fallback(base_prompt, genre, max_tokens)
    
    focus_prompt = f"""{base_prompt}

IMPORTANT: The story must revolve primarily around {main_character}.
Ensure {main_character} is the central focus and key character in the narrative.
All events should significantly impact or involve {main_character}.
"""
    
    logger.info(f"Regenerating with character focus: {main_character}")
    
    return _generate_with_plotcraft_fallback(
        focus_prompt,
        genre,
        max_tokens=max_tokens,
    )


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def generate_story_pipeline(
    user_id: str,
    prompt: str,
    genre: str = "scifi",
    twist: Optional[str] = None,
    refine: bool = False,
    measure: bool = True,
    temperature: float = 0.8,
    max_tokens: int = 300,
) -> Dict:
    """
    Complete story generation pipeline with character persistence and twist injection.
    
    Pipeline steps:
    1. Detect characters from prompt
    2. Persist characters for user session
    3. Retrieve all persisted characters
    4. Build enhanced generation prompt with character focus
    5. Optionally add twist directive
    6. Generate story using PlotCraft or fallback
    7. Optionally refine story
    8. Optionally score story
    9. Ensure character focus (regenerate if needed)
    10. Return structured response
    
    Args:
        user_id: Unique user/session identifier
        prompt: Story prompt or continuation request
        genre: Story genre (action, horror, scifi). Default: scifi
        twist: Optional twist type (unexpected, reversal, revelation, betrayal, discovery)
        refine: Whether to refine generated story for coherence
        measure: Whether to score the generated story
        temperature: Sampling temperature (0.1-2.0). Default: 0.8
        max_tokens: Maximum tokens to generate. Default: 300
    
    Returns:
        Dictionary with:
        {
            "genre": str,
            "detected_characters": List[str],
            "persisted_characters": List[str],
            "twist_applied": Optional[str],
            "generated_text": str,
            "refined": bool,
            "score": Optional[float],
            "character_focus_required": bool,
        }
    
    Raises:
        ValueError: If prompt is empty or invalid
    
    Example:
        >>> result = generate_story_pipeline(
        ...     user_id="user_123",
        ...     prompt="Alice and Bob encounter a mysterious door",
        ...     genre="horror",
        ...     twist="revelation",
        ...     measure=True
        ... )
        >>> print(result["generated_text"])
    """
    logger.info(f"Starting story pipeline for user {user_id} (genre: {genre})")
    
    # Validate input
    is_valid, error = validate_story_text(prompt)
    if not is_valid:
        raise ValueError(f"Invalid prompt: {error}")
    
    # Normalize inputs
    prompt = prompt.strip()
    genre = genre.strip().lower() if genre else "scifi"
    temperature = max(0.1, min(2.0, temperature))  # Clamp to valid range
    max_tokens = max(50, min(1000, max_tokens))     # Clamp to valid range
    
    # STEP 1: Detect characters from prompt
    logger.info("Step 1: Detecting characters from prompt")
    detected_chars = get_characters(prompt)
    logger.info(f"Detected {len(detected_chars)} characters: {detected_chars}")
    
    # STEP 2-3: Persist and retrieve characters
    logger.info("Step 2-3: Persisting and retrieving user characters")
    if detected_chars:
        save_user_characters(user_id, detected_chars)
    persisted_chars = get_user_characters(user_id)
    logger.info(f"Persisted characters for user: {persisted_chars}")
    
    # STEP 4: Build enhanced prompt with character focus
    logger.info("Step 4: Building enhanced prompt")
    cleaned_prompt = clean_text(prompt)
    truncated_prompt = truncate_text(cleaned_prompt, max_length=500)
    
    # Build base generation prompt
    generation_prompt = f"""Continue this {genre} story in a compelling and coherent way.

{("Focus on these characters: " + ", ".join(persisted_chars) + ". " if persisted_chars else "")}
{"The story should revolve primarily around: " + persisted_chars[0] + "." if persisted_chars else ""}

Story so far:
{truncated_prompt}

Continue the story:
"""
    
    # STEP 5: Add twist if requested
    if twist and twist.strip():
        logger.info(f"Step 5: Applying twist ({twist})")
        main_char = persisted_chars[0] if persisted_chars else None
        generation_prompt = apply_twist_to_prompt(generation_prompt, twist, main_char)
        twist_applied = twist.lower()
    else:
        twist_applied = None
    
    # STEP 6: Generate
    logger.info("Step 6: Generating story")
    generated_text = _generate_with_plotcraft_fallback(
        generation_prompt,
        genre,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    # STEP 7: Optionally refine
    refined = False
    if refine:
        logger.info("Step 7: Refining story")
        generated_text = _refine_story(generated_text, genre, temperature=temperature * 0.7)
        refined = True
    
    # STEP 9: Check character focus
    all_present, presence_ratio = _check_character_presence(generated_text, persisted_chars)
    character_focus_required = False
    
    if persisted_chars and not all_present and presence_ratio < 0.5:
        logger.warning(
            f"Character focus deteriorated: {presence_ratio:.1%} of {len(persisted_chars)} characters present. "
            f"Performing second-pass regeneration."
        )
        generated_text = _regenerate_for_character_focus(
            generation_prompt,
            genre,
            persisted_chars,
            main_character=persisted_chars[0],
            max_tokens=max_tokens,
        )
        character_focus_required = True
    
    # STEP 8: Optionally score
    score = None
    if measure:
        logger.info("Step 8: Scoring story")
        full_story = cleaned_prompt + " " + generated_text
        score = calculate_score(full_story)
    
    logger.info(f"Story pipeline complete. Generated {len(generated_text)} characters.")
    
    return {
        "genre": genre,
        "detected_characters": detected_chars,
        "persisted_characters": persisted_chars,
        "twist_applied": twist_applied,
        "generated_text": generated_text.strip(),
        "refined": refined,
        "score": score,
        "character_focus_required": character_focus_required,
    }


# ============================================================================
# SERVICE CLASS (for backward compatibility)
# ============================================================================

class StoryService:
    """Service for story generation operations."""
    
    @staticmethod
    def continue_story(
        text: str,
        max_length: int = 300,
        temperature: float = 0.8
    ) -> dict:
        """
        Generate story continuation (legacy interface).
        
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
            logger.error(f"Story generation failed: {e}")
            raise RuntimeError(f"Story generation failed: {str(e)}")


# Backward compatibility wrapper
def continue_story_pipeline(story: str, genre: str, characters: List[str]) -> Tuple[str, int]:
    """
    Legacy pipeline function for backward compatibility.
    
    Returns (continuation, score) tuple.
    """
    prompt = f"""You are a creative AI storyteller.

Continue this {genre} story.
Maintain consistency with these characters: {characters}.
Do not repeat the original text.

Story:
{truncate_text(clean_text(story), max_length=500)}

Continuation:
"""
    
    continuation = _generate_with_plotcraft_fallback(prompt, genre, max_tokens=800)
    full_text = clean_text(story) + " " + continuation
    score = calculate_score(full_text)
    return continuation, score

