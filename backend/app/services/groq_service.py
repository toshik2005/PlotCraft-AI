"""
Groq LLM integration service for story refinement.

Provides AI-powered story enhancement using Groq's fast inference API.
Refines generated stories for improved coherence, flow, and quality.
"""

import logging
import os
from typing import Optional

from groq import Groq, APIError

logger = logging.getLogger(__name__)

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"  # Fast, high-quality model (openai compatible)

# Note: Alternative models available:
# - "llama2-70b-4096"
# - "gemma-7b-it"
# - "openai/gpt-oss-120b" (recommended for story refinement)
# Full list at: https://console.groq.com/docs/models


class GroqUnavailable(Exception):
    """Raised when Groq API is unavailable or returns an error."""
    pass


def generate_story_with_groq(
    prompt: str,
    genre: str = "general",
    max_tokens: int = 1000,
    temperature: float = 0.8,
    characters: Optional[list] = None,
    twist_type: Optional[str] = None,
) -> str:
    """
    Generate a complete story using Groq LLM directly.
    
    Creates a story based on user prompt and genre without intermediate steps.
    
    Args:
        prompt: Story prompt/starting point (core narrative to continue from)
        genre: Story genre (action, horror, scifi, general)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.1-2.0)
        characters: Optional list of characters to include in story
        twist_type: Optional twist type (unexpected, reversal, revelation, betrayal, discovery)
    
    Returns:
        Generated story text
    
    Raises:
        GroqUnavailable: If API call fails
        ValueError: If input is empty or invalid
    """
    if not prompt or not prompt.strip():
        raise ValueError("Story prompt cannot be empty")
    
    if len(prompt) > 5000:
        logger.warning("Prompt is very long, truncating to 5000 chars")
        prompt = prompt[:5000]
    
    logger.info(f"Generating story with Groq (genre: {genre}, max_tokens: {max_tokens})")
    
    # Build the generation prompt with separate character/twist context
    generation_prompt = _build_story_generation_prompt(prompt, genre, characters, twist_type)
    
    try:
        # Call Groq API using official SDK
        generated_text = _call_groq_api(generation_prompt, temperature=temperature, max_tokens=max_tokens)
        logger.info(f"Groq story generation successful ({len(generated_text)} chars)")
        return generated_text.strip()
    
    except Exception as e:
        logger.error(f"Groq story generation failed: {str(e)}", exc_info=True)
        raise GroqUnavailable(f"Failed to generate story with Groq: {str(e)}")


def _build_story_generation_prompt(prompt: str, genre: str, characters: Optional[list] = None, twist_type: Optional[str] = None) -> str:
    """
    Build a prompt for story generation that continues from user's prompt.
    
    Keeps the user's core narrative separate from additional instructions
    to ensure Groq understands what text to continue from.
    
    Args:
        prompt: User's story prompt (core narrative to continue from)
        genre: Story genre
        characters: Optional list of characters to include
        twist_type: Optional twist type to apply
    
    Returns:
        Formatted prompt for Groq
    """
    genre_context = {
        "action": "high-paced, filled with tension, conflict, and exciting moments. Include physical challenges, obstacles to overcome, and dynamic action sequences with resolution.",
        "horror": "atmospheric and suspenseful with building dread and tension. Include eerie elements, psychological tension, unexpected scares, mysterious dangers, and a sense of foreboding.",
        "scifi": "futuristic setting with scientific concepts, advanced technology, and wonder. Include imaginative world-building, technological innovation, and thought-provoking elements about the future.",
        "general": "engaging, well-written, and entertaining for a broad audience",
    }.get(genre.lower(), "engaging and well-written")
    
    # Build additional context as separate section
    additional_context = ""
    
    if characters:
        additional_context += f"\nINCLUDE THESE CHARACTERS: {', '.join(characters)}"
    
    if twist_type:
        twist_details = {
            "unexpected": "Include an unexpected plot twist that surprises the reader.",
            "reversal": "Include a major reversal where everything changes.",
            "revelation": "Include a hidden truth that is revealed.",
            "betrayal": "Include a betrayal by a trusted character.",
            "discovery": "Include a startling discovery.",
        }.get(twist_type.lower(), "")
        if twist_details:
            additional_context += f"\nADD TWIST: {twist_details}"
    
    prompt_text = f"""You are a professional {genre} storyteller. Your task is to CONTINUE and EXPAND the following story that the user has started.

USER'S STORY START:
---
{prompt}
---

ADDITIONAL CONTEXT:{additional_context}

IMPORTANT INSTRUCTIONS:
1. You MUST continue the story DIRECTLY from where the user's text ends above
2. The continuation should flow NATURALLY from the user's prompt
3. Do NOT start a new story - EXTEND the existing one
4. Maintain any characters, settings, or elements from the user's prompt
5. Write in a {genre} style that is {genre_context}

WRITING GUIDELINES:
1. Continue seamlessly from the last line of the user's prompt
2. Expand the narrative with vivid descriptions and dialogue
3. Use proper grammar, spelling, and punctuation
4. Include dialogue with proper attribution (e.g., "said," "asked", "whispered")
5. Create tension and pacing appropriate for {genre}
6. Build toward a compelling resolution
7. Aim for 300-400 words of continuation

STORY CONTINUATION (write only the continuation - do NOT repeat the user's original text):"""
    
    return prompt_text


def refine_story_with_groq(
    generated_text: str,
    original_prompt: str = "",
    genre: str = "general",
    tone: str = "professional",
) -> str:
    """
    Refine a generated story using Groq LLM while maintaining connection to original prompt.
    
    Enhances the story for:
    - Better narrative flow and coherence
    - Improved grammar and punctuation
    - More engaging language
    - Stronger character development
    - Better pacing and structure
    - Maintains connection to the original user prompt
    
    Args:
        generated_text: The story text to refine (continuation)
        original_prompt: The original user prompt for context
        genre: Story genre (action, horror, scifi, general)
        tone: Desired tone (professional, casual, dramatic, etc.)
    
    Returns:
        Refined story text
    
    Raises:
        GroqUnavailable: If API call fails
        ValueError: If input is empty or invalid
    """
    if not generated_text or not generated_text.strip():
        raise ValueError("Story text cannot be empty")
    
    if len(generated_text) > 10000:
        logger.warning("Story text is very long, truncating to 10000 chars for API")
        generated_text = generated_text[:10000]
    
    logger.info(f"Starting Groq refinement (genre: {genre}, tone: {tone}, text_len: {len(generated_text)})")
    
    # Build the refinement prompt with context
    refinement_prompt = _build_refinement_prompt(generated_text, original_prompt, genre, tone)
    
    try:
        # Call Groq API using official SDK
        refined_text = _call_groq_api(refinement_prompt)
        logger.info(f"Groq refinement successful (refined_len: {len(refined_text)})")
        return refined_text.strip()
    
    except Exception as e:
        logger.error(f"Groq refinement failed: {str(e)}", exc_info=True)
        raise GroqUnavailable(f"Failed to refine story with Groq: {str(e)}")


def _build_refinement_prompt(story: str, original_prompt: str = "", genre: str = "general", tone: str = "professional") -> str:
    """
    Build a detailed prompt for story refinement while maintaining context.
    
    Args:
        story: The generated story continuation to refine
        original_prompt: The original user prompt for context
        genre: Story genre for context-specific refinement
        tone: Desired tone
    
    Returns:
        Formatted prompt for Groq
    """
    genre_context = {
        "action": "high-paced with exciting moments and conflict resolution",
        "horror": "atmospheric and suspenseful with building tension",
        "scifi": "futuristic with scientific authenticity and wonder",
        "general": "engaging and well-structured",
    }.get(genre.lower(), "engaging and well-structured")
    
    # Build prompt with original context if provided
    context_section = ""
    if original_prompt and original_prompt.strip():
        context_section = f"""ORIGINAL PROMPT (for context):
---
{original_prompt}
---

"""
    
    prompt = f"""You are an expert literary editor specializing in {genre} fiction.

Your task is to refine and enhance the following story continuation while maintaining its connection to the original prompt.

{context_section}CONTINUATION TO REFINE:
---
{story}
---

REFINEMENT GUIDELINES:
1. Improve narrative flow and coherence
2. Ensure the continuation naturally follows and connects to the original prompt
3. Enhance clarity and readability
4. Fix any grammar, spelling, or punctuation errors
5. Strengthen dialogue with proper attribution (e.g., "said," "asked")
6. Remove repetition, filler words, and awkward phrasing
7. Enhance descriptions and sensory details appropriately for {genre} genre
8. Ensure the story is {genre_context}
9. Maintain a {tone} tone throughout
10. Keep the story engaging from start to finish
11. Preserve all character names and key plot points from BOTH the original prompt and continuation
12. Do NOT change the core meaning or plot - only enhance the writing quality

OUTPUT ONLY the refined story continuation without any commentary or explanations. Do not add anything before or after the story."""
    
    return prompt


def _call_groq_api(prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """
    Call the Groq API with the given prompt using the official Groq SDK.
    
    Args:
        prompt: The prompt to send to Groq
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
    
    Returns:
        The refined story from Groq
    
    Raises:
        GroqUnavailable: If API call fails
    """
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("sk_"):
        logger.error("Invalid or missing GROQ_API_KEY")
        raise GroqUnavailable("Groq API key not configured")
    
    try:
        logger.debug(f"Calling Groq API with model {GROQ_MODEL} and max_tokens {max_tokens}")
        
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Make API call using official SDK
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert literary editor. Refine and enhance stories while preserving their essence."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=max(0.0, min(2.0, temperature)),
            max_tokens=max(256, min(8192, max_tokens)),
            top_p=0.95,
        )
        
        # Extract the refined story from response
        if not message.choices or not message.choices[0].message.content:
            raise GroqUnavailable("Empty response from Groq API")
        
        refined_text = message.choices[0].message.content
        logger.debug(f"Groq API response received ({len(refined_text)} chars)")
        return refined_text
    
    except APIError as e:
        logger.error(f"Groq API error: {str(e)}")
        raise GroqUnavailable(f"Groq API error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error calling Groq API: {str(e)}", exc_info=True)
        raise GroqUnavailable(f"Unexpected error: {str(e)}")


def get_groq_status() -> dict:
    """
    Check if Groq API is accessible and configured.
    
    Returns:
        Dictionary with status information
    """
    status = {
        "configured": bool(GROQ_API_KEY and not GROQ_API_KEY.startswith("sk_")),
        "model": GROQ_MODEL,
        "api_key_prefix": GROQ_API_KEY[:20] + "..." if GROQ_API_KEY else "Not set",
    }
    
    # Try a simple health check
    try:
        client = Groq(api_key=GROQ_API_KEY)
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
        )
        status["available"] = message.choices[0].message.content is not None
        logger.info("Groq API health check passed")
    except Exception as e:
        logger.warning(f"Groq health check failed: {str(e)}")
        status["available"] = False
    
    return status
