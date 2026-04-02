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
    
    prompt_text = f"""You are a highly skilled professional {genre} story author and novelist. Your task is to CONTINUE and EXPAND the user's story prompt into a rich, detailed narrative continuation that feels authentic and engaging.

CONTEXT - ORIGINAL PROMPT FROM USER:
═══════════════════════════════════
{prompt}
═══════════════════════════════════

{additional_context}

═══════════════════════════════════
DETAILED WRITING INSTRUCTIONS:
═══════════════════════════════════

1. CONTINUATION PRINCIPLES (CRITICAL):
   ✓ MUST continue DIRECTLY from where the user's prompt ends
   ✓ First sentence should flow naturally from the last line given
   ✓ Maintain ALL names, places, and story elements from user text
   ✓ DO NOT repeat or restate the user's prompt
   ✓ Write as if you are continuing the SAME narrative thread
   ✓ Preserve the tone and voice established by the user
   ✓ Build upon the events and emotions set up by the initial prompt

2. STYLE AND TONE FOR {genre.upper()} GENRE:
   • {genre_context}
   • Match the intensity level shown in the user's opening
   • Use vocabulary and pacing appropriate for this genre
   • Maintain narrative consistency with user's established voice

3. NARRATIVE DEVELOPMENT (DETAILED):
   
   OPENING (First 2-3 sentences):
   - Start with immediate continuation of action/scene
   - Reference or build from the last element in user's prompt
   - Maintain reader immersion without recapping
   
   MIDDLE SECTION (Main body - 60% of content):
   - Develop character interactions and relationships
   - Show environment through sensory details (sight, sound, smell, touch, taste)
   - Build tension and conflict appropriate to {genre}
   - Include natural dialogue with varied attributions (said, whispered, commanded, asked, replied, etc.)
   - Show character emotions through actions, not just telling
   - Add secondary details that make world feel lived-in and real
   - Include 1-2 minor unexpected plot elements (20% hallucination - small surprises, minor character quirks, unexpected obstacles)
   
   CLOSING (Last 2-3 sentences):
   - Lead toward a hook or cliffhanger
   - Leave room for further continuation
   - End at a moment of transition or decision
   - Don't resolve all tension - maintain reader curiosity

4. DIALOGUE GUIDELINES:
   - Use varied dialogue tags: said, asked, whispered, commanded, replied, muttered, shouted, gasped, etc.
   - Avoid using "said" more than 40% of the time
   - Dialogue should reveal character personality and mood
   - Include at least 2-3 exchanges between characters
   - Use dialogue punctuation correctly: "Text here," he said.
   - Let silences and pauses convey emotion

5. CHARACTER DEPTH:
   - Show characters' personalities through actions and decisions
   - Include internal thoughts or reactions to events
   - Display relationships between characters through interactions
   - Add small character details (mannerisms, speech patterns, quirks)
   - Keep all character names exactly as given by user

6. WORLD-BUILDING AND DESCRIPTION:
   - Paint vivid scenes with specific, sensory details
   - Describe locations as if the reader has never been there
   - Use comparisons and metaphors naturally (not forced)
   - Include environmental obstacles or elements that affect the narrative
   - Create atmosphere that matches genre expectations
   - Show passage of time subtly

7. TECHNICAL WRITING STANDARDS:
   - Correct grammar, spelling, and punctuation
   - Proper sentence structure with varied lengths
   - Paragraph breaks for pacing and emphasis
   - Writing should feel natural and flowing
   - Avoid clichés - be creative in descriptions
   - Show, don't tell (reveal character through action, not description)
   - Use active voice primarily (passive used strategically)

8. LENGTH AND STRUCTURE:
   - Write approximately 400-500 words of continuation
   - Vary paragraph length: some short (1-3 lines) for impact, some longer for detail
   - Break dialogue into separate paragraphs for different speakers
   - Consider pacing: quick sentences during action, longer during reflection

9. MINOR HALLUCINATION ALLOWANCE (20%):
   - You may introduce minor new story elements (objects, locations, NPC characters)
   - These should be plausible and fit the established world
   - Small unexpected obstacles or complications are good
   - Minor character quirks or reactions can surprise the reader
   - Do NOT contradict established facts from user's prompt
   - Keep hallucinated elements grounded in the story logic

10. GENRE-SPECIFIC REQUIREMENTS FOR {genre.upper()}:
"""
    
    if genre.lower() == "action":
        prompt_text += """   ACTION GENRE:
   - Include physical movement and combat if relevant
   - Build tension through obstacles and challenges
   - Show character competence through decisive actions
   - Include tactical thinking or strategy
   - Maintain sense of urgency and pacing
   - Use short sentences during high-tension moments
   - Include specific details about weapons, movements, terrain"""
    elif genre.lower() == "horror":
        prompt_text += """   HORROR GENRE:
   - Build dread and atmosphere gradually
   - Use suspense techniques: unknown threats, isolation, time pressure
   - Include visceral but not gratuitous descriptions
   - Create unsettling moments through suggestion and implication
   - Show fear through character reactions and behavior
   - Use darkness, cold, unusual sounds as tools
   - Include eerie or uncanny details in environment
   - Never fully reveal threats immediately - maintain mystery"""
    elif genre.lower() == "scifi":
        prompt_text += """   SCIENCE FICTION GENRE:
   - Explain technological or futuristic elements naturally
   - Use technical terminology but keep it understandable
   - Include world-specific details (how society works, tech limitations, etc.)
   - Show wonder and discovery where appropriate
   - Consider scientific/logical implications of story elements
   - Include detail about futuristic settings and tools
   - Balance wonder with realism and logic"""
    else:
        prompt_text += """   GENERAL GENRE:
   - Create engagement through characterization
   - Include emotional stakes and relationships
   - Balance action and introspection
   - Use sensory details liberally
   - Create moments of surprise and emotional impact"""
    
    prompt_text += f"""

═══════════════════════════════════
CRITICAL DO's AND DON'Ts:
═══════════════════════════════════

DO:
✓ Continue the exact story from exactly where it ends
✓ Use first names as established by user
✓ Immerse reader in the immediate action/scene
✓ Create vivid, sensory-rich descriptions
✓ Include meaningful dialogue between characters
✓ Build tension and emotional engagement
✓ Show character development through actions
✓ End with a hook or moment of transition

DON'T:
✗ Do NOT repeat or reiterate the user's original prompt
✗ Do NOT start a new story or different scenario
✗ Do NOT summarize what came before
✗ Do NOT change character names from what user provided
✗ Do NOT write in third person if user wrote first person (maintain POV)
✗ Do NOT include a summary or "The Story So Far" section
✗ Do NOT contradict facts established in user's prompt
✗ Do NOT write stilted, unnatural dialogue
✗ Do NOT over-describe - balance description with action
✗ Do NOT be overly safe - take narrative risks within reason

═══════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════

Write ONLY the story continuation below. No preamble, no explanations, no metadata.
Your first sentence begins the continuation. Start writing immediately:

"""
    
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


def _call_groq_api(prompt: str, temperature: float = 0.7, max_tokens: int = 2048, timeout: int = 60) -> str:
    """
    Call the Groq API with the given prompt using the official Groq SDK.
    
    Args:
        prompt: The prompt to send to Groq
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds (default: 60)
    
    Returns:
        The text response from Groq
    
    Raises:
        GroqUnavailable: If API call fails
    """
    # CRITICAL: Check if API key is properly configured
    if not GROQ_API_KEY:
        error_msg = "GROQ_API_KEY environment variable not set. Set it in .env file: GROQ_API_KEY=gsk_your_key_here"
        logger.error(error_msg)
        raise GroqUnavailable(error_msg)
    
    if not GROQ_API_KEY.startswith("gsk_"):
        logger.error(f"Invalid API key format. Groq keys must start with 'gsk_', got: {GROQ_API_KEY[:20]}...")
        raise GroqUnavailable("Invalid Groq API key format (must start with 'gsk_')")
    
    try:
        logger.debug(f"Calling Groq API: model={GROQ_MODEL}, tokens={max_tokens}, temp={temperature}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # Initialize Groq client with timeout
        client = Groq(api_key=GROQ_API_KEY, timeout=timeout)
        
        # Make API call using official SDK
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=max(0.0, min(2.0, temperature)),
            max_tokens=max(256, min(8192, max_tokens)),
            top_p=0.95,
        )
        
        # Extract the response
        if not message.choices:
            logger.error("Groq API returned empty choices")
            raise GroqUnavailable("Groq API returned no choices")
        
        if not message.choices[0].message.content:
            logger.error("Groq API returned empty content")
            raise GroqUnavailable("Groq API returned empty content")
        
        response_text = message.choices[0].message.content
        logger.debug(f"Groq API response received ({len(response_text)} chars)")
        return response_text
    
    except APIError as e:
        error_str = str(e)
        logger.error(f"Groq API error: {error_str}")
        
        # Provide helpful diagnostics
        if "401" in error_str or "Unauthorized" in error_str:
            raise GroqUnavailable("API key is invalid or expired. Get a new key from: https://console.groq.com/keys")
        elif "429" in error_str or "Rate limit" in error_str:
            raise GroqUnavailable("Rate limit exceeded. Please wait a moment and try again.")
        elif "500" in error_str or "503" in error_str:
            raise GroqUnavailable("Groq API server temporarily unavailable. Try again in a moment.")
        else:
            raise GroqUnavailable(f"Groq API error: {error_str}")
    
    except Exception as e:
        logger.error(f"Unexpected error calling Groq API: {str(e)}", exc_info=True)
        raise GroqUnavailable(f"Unexpected error: {str(e)}")


def get_groq_status() -> dict:
    """
    Check if Groq API is accessible and configured.
    
    Returns:
        Dictionary with status information and diagnostics
    """
    if not GROQ_API_KEY:
        return {
            "configured": False,
            "error": "GROQ_API_KEY environment variable not set",
            "instructions": "Set GROQ_API_KEY=gsk_your_key_here in .env file",
            "get_key_url": "https://console.groq.com/keys"
        }
    
    if not GROQ_API_KEY.startswith("gsk_"):
        return {
            "configured": False,
            "error": f"Invalid API key format: starts with {GROQ_API_KEY[:10]}... (must start with 'gsk_')",
            "get_key_url": "https://console.groq.com/keys"
        }
    
    status = {
        "configured": True,
        "model": GROQ_MODEL,
        "api_key_prefix": GROQ_API_KEY[:20] + "...",
    }
    
    return status


def extract_characters_with_groq(
    text: str,
    max_characters: int = 10,
) -> dict:
    """
    Extract character names from text using Groq LLM with intelligent analysis.
    
    This function uses Groq's advanced language understanding to identify all character
    names mentioned in the original text/prompt, including:
    - Named characters introduced with "named X", "called X"
    - Character names mentioned in conversations and interactions
    - Names appearing in group contexts ("friends mayank and naitik")
    - Names in narrative descriptions and actions
    - Correctly handles both proper and informal character introductions
    
    Args:
        text: The original story text/prompt to extract characters from
        max_characters: Maximum number of characters to extract (default: 10, max: 20)
    
    Returns:
        Dictionary containing:
        - success: bool - Whether extraction was successful
        - characters: list - Extracted character names
        - count: int - Number of characters found
        - message: str - Additional context or error message
        - method: str - "groq" to indicate Groq LLM was used
    
    Raises:
        ValueError: If text is empty or invalid
        GroqUnavailable: If Groq API call fails
    
    Example:
        >>> result = extract_characters_with_groq("Alice and Bob met in the forest.")
        >>> print(result)
        {'success': True, 'characters': ['Alice', 'Bob'], 'count': 2, 'method': 'groq', 'message': None}
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if len(text) > 10000:
        logger.warning("Text is very long (>10000 chars), truncating for API analysis")
        text = text[:10000]
    
    max_characters = min(max(1, max_characters), 20)  # Constrain between 1 and 20
    
    logger.info(f"Extracting characters from text ({len(text)} chars) using Groq LLM")
    
    # Build the character extraction prompt
    extraction_prompt = _build_character_extraction_prompt(text, max_characters)
    
    try:
        # Call Groq API
        response_text = _call_groq_api(
            extraction_prompt,
            temperature=0.1,  # Very low temperature for maximum consistency and accuracy
            max_tokens=2048   # Increased tokens to ensure complete response with reasoning
        )
        
        # Parse the response to extract character list
        characters = _parse_character_extraction_response(response_text, max_characters)
        
        logger.info(f"Groq extracted {len(characters)} characters: {characters}")
        
        return {
            "success": True,
            "characters": characters,
            "count": len(characters),
            "method": "groq",
            "message": None
        }
    
    except Exception as e:
        logger.error(f"Character extraction with Groq failed: {str(e)}", exc_info=True)
        raise GroqUnavailable(f"Failed to extract characters with Groq: {str(e)}")


def _build_character_extraction_prompt(text: str, max_characters: int) -> str:
    """
    Build an extremely detailed and comprehensive prompt for Groq to extract ALL character names.
    
    This enhanced prompt:
    - Lists every possible way characters can appear in text
    - Provides specific examples matching common patterns
    - Uses explicit, numbered extraction rules with detailed explanations
    - Includes multiple verification steps
    - Emphasizes completeness and separation of names
    - Handles specific edge cases that commonly cause missed extractions
    
    Args:
        text: The original text to analyze
        max_characters: Maximum number of characters to extract
    
    Returns:
        Formatted prompt for Groq
    """
    prompt = f"""You are a world-class expert at analyzing narrative text and extracting character names with 100% accuracy.

YOUR CRITICAL TASK: Extract EVERY SINGLE character name that appears in the text below. DO NOT MISS ANY NAMES.
Better to include a questionable name than to miss an actual character name.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
TEXT TO ANALYZE:
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
{text}
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
COMPREHENSIVE CHARACTER NAME EXTRACTION GUIDE:
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

SECTION 1: WHERE AND HOW CHARACTERS APPEAR IN TEXT
═══════════════════════════════════════════════════

A) DIRECT NAME INTRODUCTIONS (EXPLICIT CHARACTER INTRODUCTION):
   Patterns:
   - "a person named X" → Extract X
   - "called X" → Extract X
   - "known as X" → Extract X
   - "my name is X" → Extract X
   - "the warrior X" → Extract X
   - "X is..." (at start of sentence with capitalized word) → likely Extract X
   
   CONCRETE EXAMPLES:
   - "john in the dark woods" → Extract: john (first capitalized proper name used as subject)
   - "a boy named mayank" → Extract: mayank
   - "Alice called herself brave" → Extract: Alice

B) COMPOUND ACTION DESCRIPTIONS (VERY IMPORTANT - MOST COMMONLY MISSED):
   Patterns - Look for ALL of these:
   - "X and Y did Z" → Extract X AND Y (two separate names!)
   - "X with Y doing Z" → Extract X AND Y (two separate names!)
   - "X, Y, and Z" → Extract X, Y, AND Z (three separate names!)
   - "X traveling with Y" → Extract X AND Y (two separate names!)
   - "X beat Y" → Extract X AND Y (both are characters!)
   - "X fighting Y" → Extract X AND Y (both are characters!)
   - "X alongside Y" → Extract X AND Y
   - "X and Y together" → Extract X AND Y
   
   CONCRETE EXAMPLES FROM SIMILAR TEXT:
   - "john in dark woods with max and mayank travelling" 
     → Extract: john, max, mayank (THREE names, NOT one!)
   - "lisa was beating mayank while john watched"
     → Extract: lisa, mayank, john (THREE names!)
   - "the warriors max and naitik fought against the wildlings"
     → Extract: max, naitik (NOT "max and naitik" as one, but two separate!)

C) DIALOGUE AND SPEECH (NARRATOR MENTIONS OR CHARACTER ATTRIBUTION):
   Patterns:
   - Said X, Asked X, Replied X, Whispered X → Extract X
   - "Hello X" (addressing a character) → Extract X (if grammatically person name)
   - X said "..." → Extract X
   - Quoted speech attributed to X → Extract X
   - "X came back" (character name as subject) → Extract X
   
   CONCRETE EXAMPLES:
   - 'said John' → Extract: John
   - '"Hello," she said.' followed by attribution → Extract character name if given
   - 'John replied, "No"' → Extract: John

D) GROUP FORMATIONS AND LISTS (CRITICAL - DO NOT SKIP):
   YOU MUST separate names in lists/groups - DO NOT combine them
   Patterns:
   - "X and Y" → Extract X (one name), Extract Y (one name) - TWO ENTRIES
   - "X, Y, and Z" → Extract X (one), Y (one), Z (one) - THREE ENTRIES
   - "X or Y" → Extract X, Extract Y - TWO ENTRIES
   - "X with Y" → Extract X, Extract Y - TWO ENTRIES
   - "X, Y, Z" → Extract X, Y, Z as separate entries - NOT as one name
   - "X alongside Y" → Extract X, Extract Y - TWO ENTRIES
   - "friends X and Y" → Extract X, Extract Y - TWO ENTRIES
   - "between X and Y" → Extract X, Extract Y - TWO ENTRIES
   
   CRITICAL EXAMPLES SHOWING CORRECT EXTRACTION:
   - "max and mayank" → WRONG: Extract as "Max and Mayank" (one entry)
                        RIGHT: Extract as (1) max, (2) mayank (two entries)
   - "john with max and mayank" → Extract (1) john, (2) max, (3) mayank (three entries)
   - "lisa, mayank, john" → Extract (1) lisa, (2) mayank, (3) john (three entries)

E) NARRATIVE DESCRIPTIONS AND ACTIONS (SUBJECTS AND OBJECTS):
   Any character doing an action or having an action done to them is a character
   Patterns:
   - "[X] went to..." → Extract X (subject of action)
   - "[X] saw Y" → Extract X and Y (both involved in action)
   - "When [X] met [Y]" → Extract X and Y (both are characters in encounter)
   - "[X] challenged [Y]" → Extract X and Y
   - "[X]'s friend [Y]" → Extract Y (if a person's proper name), possibly X if person name too
   - "The [X] named [Y]" → Extract Y (Y is the character name)
   
   CONCRETE EXAMPLES:
   - "john traveled north" → Extract: john
   - "max encountered mayank" → Extract: max, mayank (both involved)
   - "when lisa met john" → Extract: lisa, john

F) POSSESSIVES AND RELATIONSHIPS:
   Patterns:
   - "[X]'s brother [Y]" → If Y is a name, extract Y; if X is person, may extract both
   - "[X] and his friend [Y]" → Extract Y (and X if it's a person name, not "his")
   - "[X]'s love [Y]" → Extract Y as character
   - "Between [X] and [Y]" → Extract X and Y
   
   CONCRETE EXAMPLES:
   - "john's companion mayank" → Extract: john, mayank (both are character names)

SECTION 2: SPECIFIC RULES FOR NAME EXTRACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE 1 - CAPITALIZATION AND WORD BOUNDARIES:
★ Any capitalized word (except at sentence start) is suspect as being a name
★ Multiple capitalized words in sequence might be multiple names or descriptors
★ Between "and" or "," connectors, if both words are capitalized, both are likely names
★ In "John in the dark woods with Max and Mayank" - all three are proper names

RULE 2 - THE CRITICAL "AND/OR" RULE:
★ WHENEVER YOU SEE "X and Y" OR "X or Y", extract as TWO names, not one
★ NEVER combine "X and Y" into a single entry
★ This is the most important rule for avoiding extraction failure
★ EXAMPLE WRONG: Entry "john and max" → WRONG!
★ EXAMPLE RIGHT: Entry 1: "john", Entry 2: "max" → RIGHT!

RULE 3 - ACTION VERB SUBJECTS AND OBJECTS:
★ Who is doing the action? → Likely a character
★ Who is the action being done to? → Likely a character
★ "X beat Y" → Both X and Y are characters
★ "X found Y" → Both X and Y are characters
★ "X traveled with Y" → Both X and Y are characters

RULE 4 - CONTEXT CLUES:
★ Names in "in the", "with the", etc. → Keep if appears to be person name
★ Names tied to actions with verbs → Usually characters
★ Names in lists or groups → Separate each one
★ Names followed by descriptors ("the brave X") → X is character, "brave" is descriptor

RULE 5 - FREQUENCY AND CONFIDENCE:
★ Names that appear multiple times → DEFINITELY characters (extract them)
★ Names with varied sentence positions → Usually characters (extract them)
★ Unique proper nouns → Extract (unless clearly location/object)

SECTION 3: WHAT TO INCLUDE VS EXCLUDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓✓✓ DEFINITELY EXTRACT (INCLUDE):
✓ Any proper noun that refers to a person
✓ First names, last names, nicknames, titles + names
✓ In "X and Y" constructions, extract BOTH separately
✓ In "X with Y with Z" constructions, extract ALL separately
✓ Names mentioned in description: "the warrior john"
✓ Names in group formations: "john, max, mayank"
✓ Names as subjects: "john traveled north"
✓ Names as objects: "john challenged max"
✓ Names mentioned even once (err on side of inclusion)
✓ Any word 3+ letters that is capitalized in middle of text (likely a name)

✗✗✗ DO NOT EXTRACT (EXCLUDE):
✗ Place names: forests, cities, countries (but "north" in "traveled north" ≠ char name)
✗ Direction words: "north", "south", "east", "west" (unless they're character names)
✗ Generic nouns: boy, girl, man, woman, warrior, friend (unless part of actual name)
✗ Pronouns: he, she, I, you, they, we, me, him, her
✗ Common verbs: is, was, be, go, do
✗ Articles: the, a, an
✗ Prepositions: in, with, on, at, by, from
✗ Adjectives: dark, brave, tall, strong (unless part of name)
✗ Objects: sword, door, fire, wood (unless personified as character)
✗ Group words: wildlings, army, rebels (unless explicitly a character name)

⚠️ BORDERLINE CASES (INCLUDE IF UNCERTAIN):
⚠ Capitalized person descriptor: "John" is name, "the warrior" is descriptor, but "John the warrior" → extract John
⚠ Single capitalized word after "with": if looks like name, extract it
⚠ Unfamiliar words: if could be a character name (fantasy setting), extract it
⚠ Better to over-extract than under-extract


SECTION 4: VERIFICATION CHECKLIST
═════════════════════════════════

Before finalizing, scan text again for:

☐ Did I find all instances of "and" connecting nouns? Are both nouns names? Extract both!
  Example: "john and max traveled" → Extract john, max separately
  
☐ Did I find all instances of "with" connecting nouns? Are they names? Extract both!
  Example: "john with max" → Extract john, max separately
  
☐ Did I find all subjects of verbs? Are they people's names? Extract them!
  Example: "john traveled" → Extract john
  
☐ Did I find all objects of action verbs? Are they names? Extract them!
  Example: "john challenged max" → Extract john, max
  
☐ Did I find all characters in dialogue tags?
  Example: "john said" → Extract john
  
☐ Did I find names in group formations?
  Example: "john, max, mayank" → Extract john, max, mayank (three entries!)
  
☐ Did I separate all "X and Y" constructions into individual entries?
  PARANOIA CHECK: Recount - how many "and"s are there? Each one might be joining two characters!


SECTION 5: EXACT OUTPUT FORMAT
═══════════════════════════════

Format your response EXACTLY as follows with NO other text before, after, or in between:

CHARACTER_NAMES:
1. FirstCharacterName
2. SecondCharacterName
3. ThirdCharacterName
4. FourthCharacterName
5. FifthCharacterName
(continue up to {max_characters} maximum)

EXTRACTION_REASONING:
1. FirstCharacterName - context: Exact phrase or description of where this name appears
2. SecondCharacterName - context: Exact phrase or description of where this name appears
3. ThirdCharacterName - context: Exact phrase or description of where this name appears
(continue for each name extracted)

STRICT OUTPUT COMPLIANCE RULES:
✓ Line 1 is EXACTLY "CHARACTER_NAMES:" with nothing before it
✓ Lines 2 onward are EXACTLY "N. NameHere" format (number, period, space, name)
✓ EACH NAME ON ITS OWN SEPARATE LINE
✓ MAXIMUM ONE NAME PER LINE (never "1. name1 and name2", always separate as "1. name1" then "2. name2")
✓ NAMES MUST BE EXTRACTED EXACTLY AS THEY APPEAR (preserve capitalization)
✓ Maximum total {max_characters} names
✓ SECOND SECTION starts with "EXTRACTION_REASONING:" on its own line
✓ Each reasoning follows "N. Name - context: description" format

ABSOLUTE REQUIREMENTS:
★ If text contains "john and max", output MUST include:
  1. john
  2. max
  (as two entries, NOT "1. john and max")
★ VERIFY: Did you separate ALL compound names correctly?
★ VERIFY: Did you extract ALL names that appear?
★ VERIFY: Did you preserve capitalization exactly?


Now extract. Begin your response with "CHARACTER_NAMES:" and follow no other format."""
    
    return prompt


def _parse_character_extraction_response(response_text: str, max_characters: int) -> list:
    """
    Parse Groq's response to extract the character names list.
    
    Enhanced parsing that:
    - Handles structured format from extraction prompt
    - Correctly separates multiple names on single lines
    - Splits compound names (e.g., "Lisa Beating Mayank" → ["Lisa", "Mayank"])
    - Handles names with particles (van, de, etc.)
    - Deduplicates while preserving order and capitalization
    
    Args:
        response_text: The raw response from Groq
        max_characters: Maximum characters to return
    
    Returns:
        List of extracted character names
    """
    characters = []
    
    try:
        import re
        
        # Split response into lines
        lines = response_text.strip().split('\n')
        
        in_character_section = False
        
        for line in lines:
            line = line.strip()
            
            # Look for the CHARACTER_NAMES section header
            if line.startswith('CHARACTER_NAMES:'):
                in_character_section = True
                continue
            
            # Stop when we hit other sections
            if line.startswith('EXTRACTION_CONTEXT:') or line.startswith('ANALYSIS_NOTES:') or line.startswith('---'):
                in_character_section = False
                if characters:  # We've found characters, so stop processing
                    break
                continue
            
            # Skip empty lines in character section
            if not line:
                continue
            
            if in_character_section:
                # Match pattern like "1. Character Name" or "1) Character Name"
                match = re.match(r'^\d+[\.\)]\s*(.+?)$', line)
                if match:
                    name_text = match.group(1).strip()
                    
                    # Remove any trailing comments or notes in parentheses
                    name_text = re.sub(r'\s*\([^)]*\)\s*$', '', name_text).strip()
                    
                    # Remove surrounding quotes if present
                    name_text = name_text.strip('\'"')
                    
                    if not name_text:
                        continue
                    
                    # Check if this line contains multiple names joined by "and", "or", etc.
                    # This catches cases like "Lisa and Mayank" or "John or Jane"
                    # Split by common separators but preserve each name
                    potential_names = []
                    
                    # First check for explicit separators: " and ", " or ", ", "
                    if ' and ' in name_text or ' or ' in name_text or ', ' in name_text:
                        # Split by these separators
                        parts = re.split(r'\s+(?:and|or)\s+|,\s*', name_text)
                        potential_names = [p.strip() for p in parts if p.strip()]
                    else:
                        # Check if this looks like multiple names (e.g., "Lisa Beating Mayank")
                        # heuristic: if there are multiple capitalized words that look like names
                        # we might need to extract them
                        words = name_text.split()
                        
                        # If we have 3+ words and some are proper nouns, try to extract names
                        if len(words) >= 3:
                            # Look for patterns like "Lisa Beating Mayank" where middle could be verb
                            # Simple heuristic: take first capital word, last capital word (if > 2 words)
                            capitalized_words = [w for w in words if w and w[0].isupper()]
                            
                            # If we have multiple capitalized words, they might be separate names
                            if len(capitalized_words) >= 2 and len(capitalized_words) != len(words):
                                # This might be "Name Action Name" pattern
                                potential_names = capitalized_words
                            else:
                                # Otherwise treat as single name
                                potential_names = [name_text]
                        else:
                            potential_names = [name_text]
                    
                    # Add all extracted names
                    for name in potential_names:
                        name = name.strip()
                        # Remove quotes again if present after splitting
                        name = name.strip('\'"')
                        if name and len(name) > 0:
                            characters.append(name)
                            if len(characters) >= max_characters:
                                break
                    
                    if len(characters) >= max_characters:
                        break
        
        # If we didn't find the structured format, try fallback parsing
        if not characters:
            logger.warning("Could not parse structured character extraction format, attempting fallback parsing")
            response_text_clean = response_text.lower()
            
            # Look for "character_names:" section more flexibly
            if 'character_names' in response_text_clean or 'characters:' in response_text_clean:
                # Find the section and extract names from following lines
                char_section_idx = max(
                    response_text_clean.find('character_names'),
                    response_text_clean.find('characters:')
                )
                
                if char_section_idx != -1:
                    section_text = response_text[char_section_idx:]
                    section_lines = section_text.split('\n')[1:]  # Skip header
                    
                    for line in section_lines[:max_characters * 2]:  # Look at reasonable number of lines
                        line = line.strip()
                        if not line or line.startswith('---') or ':' in line:
                            break
                        
                        # Extract text after number/dot
                        match = re.match(r'^\d+[\.\)]\s*(.+?)$', line)
                        if match:
                            name = match.group(1).strip()
                            # Basic cleanup
                            name = re.sub(r'\s*[(-].+', '', name).strip()  # Remove comments
                            name = name.strip('\'"')
                            if name:
                                characters.append(name)
        
        # Deduplicate while preserving order (case-insensitive comparison, but keep original case)
        seen = {}
        unique_chars = []
        for char in characters:
            char_lower = char.lower()
            if char_lower not in seen:
                seen[char_lower] = char
                unique_chars.append(char)
        
        # Final cleanup: remove very short names or names that look like artifacts
        final_chars = []
        for char in unique_chars[:max_characters]:
            # Skip single letter names and very common words
            if len(char) > 1 and char.lower() not in {'and', 'or', 'the', 'a', 'an', 'is', 'as', 'by'}:
                final_chars.append(char)
        
        return final_chars[:max_characters]
    
    except Exception as e:
        logger.error(f"Error parsing character extraction response: {str(e)}", exc_info=True)
        # Return empty list on parsing error
        return []
