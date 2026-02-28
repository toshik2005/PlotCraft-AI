"""
Story twist generation service.

Provides functionality to inject plot twists into story generation.
Twists can be applied via prompt injection (recommended) or post-generation editing.

Philosophy: Inject twist directives into the generation prompt rather than
editing output afterward. This guides the model during generation for more
coherent twist integration.
"""

import logging
from typing import Optional
from enum import Enum

from app.utils.text_preprocessing import clean_text
from app.utils.validators import validate_story_text

logger = logging.getLogger(__name__)


class TwistType(str, Enum):
    """Supported twist types for story generation."""
    UNEXPECTED = "unexpected"
    REVERSAL = "reversal"
    REVELATION = "revelation"
    BETRAYAL = "betrayal"
    DISCOVERY = "discovery"


# Twist prompt templates - these guide the model during generation
TWIST_INSTRUCTIONS = {
    TwistType.UNEXPECTED: (
        "Introduce an unexpected twist at the midpoint of this story. "
        "The twist should surprise the reader but make sense in context."
    ),
    TwistType.REVERSAL: (
        "Include a reversal of expectations where the situation becomes "
        "the opposite of what the reader initially thought. "
        "This should redirect the narrative dramatically."
    ),
    TwistType.REVELATION: (
        "Introduce a shocking revelation that recontextualizes earlier events. "
        "A hidden truth should be uncovered that changes everything."
    ),
    TwistType.BETRAYAL: (
        "Include a betrayal by a trusted character that fundamentally changes "
        "the story's direction. The betrayal should impact the main character."
    ),
    TwistType.DISCOVERY: (
        "Feature a startling discovery that opens up new plot possibilities. "
        "The discovery should be significant and affect the story's trajectory."
    ),
}


def apply_twist_to_prompt(
    base_prompt: str,
    twist_type: str,
    main_character: Optional[str] = None,
) -> str:
    """
    Apply a twist directive to a generation prompt.
    
    Philosophy: Rather than editing the output after generation,
    append structured instruction to the prompt during generation.
    This guides the model to naturally incorporate the twist.
    
    Args:
        base_prompt: The original story prompt/prompt
        twist_type: One of [unexpected, reversal, revelation, betrayal, discovery]
        main_character: Optional character name. If provided, twist impacts this character.
    
    Returns:
        Enhanced prompt with twist instruction appended
    
    Example:
        >>> prompt = "Once upon a time"
        >>> enhanced = apply_twist_to_prompt(prompt, "betrayal", "Alice")
        >>> # Returns: "Once upon a time\n\n[Twist instruction about Alice's betrayal]..."
    """
    if not base_prompt or not base_prompt.strip():
        raise ValueError("base_prompt cannot be empty")
    
    # Normalize twist type
    twist_type = twist_type.strip().lower()
    
    # Get instruction template
    try:
        twist_enum = TwistType(twist_type)
        instruction = TWIST_INSTRUCTIONS[twist_enum]
    except ValueError:
        logger.warning(f"Unknown twist type '{twist_type}'. Using 'unexpected'.")
        instruction = TWIST_INSTRUCTIONS[TwistType.UNEXPECTED]
    
    # Enhance instruction with character if provided
    if main_character and main_character.strip():
        char = main_character.strip()
        instruction = f"{instruction} This twist should directly impact {char}."
    
    # Append instruction to prompt
    enhanced_prompt = f"{base_prompt}\n\n[Story direction: {instruction}]"
    
    logger.info(f"Applied twist '{twist_type}' to prompt" + 
                (f" (character: {main_character})" if main_character else ""))
    
    return enhanced_prompt


def validate_twist_type(twist_type: str) -> bool:
    """
    Check if a twist type is valid.
    
    Args:
        twist_type: Twist type string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        TwistType(twist_type.strip().lower())
        return True
    except ValueError:
        return False


class TwistService:
    """Service for generating and injecting story twists."""
    
    @staticmethod
    def build_twist_prompt(
        text: str,
        twist_type: str = "unexpected",
        main_character: Optional[str] = None,
    ) -> str:
        """
        Build an enhanced prompt with twist injection.
        
        Args:
            text: Input story text/prompt
            twist_type: Type of twist to apply
            main_character: Optional character name for twist focus
        
        Returns:
            Enhanced prompt with twist directive
        
        Raises:
            ValueError: If text empty or invalid
        """
        # Validate input
        is_valid, error = validate_story_text(text)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Apply twist to prompt
        enhanced_prompt = apply_twist_to_prompt(
            cleaned_text,
            twist_type,
            main_character
        )
        
        return enhanced_prompt
    
    @staticmethod
    def get_twist_instruction(twist_type: str) -> str:
        """
        Get the instruction text for a twist type.
        
        Args:
            twist_type: Type of twist
        
        Returns:
            Instruction text for the twist
        """
        twist_type = twist_type.strip().lower()
        try:
            twist_enum = TwistType(twist_type)
            return TWIST_INSTRUCTIONS[twist_enum]
        except ValueError:
            return TWIST_INSTRUCTIONS[TwistType.UNEXPECTED]
    
    @staticmethod
    def list_available_twists() -> dict:
        """
        Get list of all available twist types with descriptions.
        
        Returns:
            Dictionary mapping twist types to their instructions
        """
        return {
            twist_type.value: instruction
            for twist_type, instruction in TWIST_INSTRUCTIONS.items()
        }
    
    @staticmethod
    def generate_twist_variation(
        base_twist: str,
        twist_type: str,
        max_variations: int = 3,
    ) -> dict:
        """
        Generate variations of a twist instruction.
        
        Useful for A/B testing or user preference.
        
        Args:
            base_twist: Base twist instruction
            twist_type: Type of twist
            max_variations: Number of variations to generate
        
        Returns:
            Dictionary with variations (currently returns base template)
        
        Note: Full implementation would use LLM to generate variations.
        For now, returns the base instruction.
        
        TODO: Implement variation generation using LLM
        """
        base_instruction = TwistService.get_twist_instruction(twist_type)
        
        return {
            "base": base_instruction,
            "variations": [base_instruction],  # TODO: Generate actual variations
            "twist_type": twist_type
        }

