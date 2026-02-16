"""Story twist generation service."""

from app.models.story_generator import story_generator
from app.utils.text_preprocessing import clean_text, truncate_text
from app.utils.validators import validate_story_text


class TwistService:
    """Service for generating story twists."""
    
    @staticmethod
    def generate_twist(text: str, twist_type: str = "unexpected") -> dict:
        """
        Generate a plot twist for the story.
        
        Args:
            text: Input story text
            twist_type: Type of twist (unexpected, reversal, revelation, etc.)
        
        Returns:
            Dictionary with twist text and metadata
        """
        # Validate input
        is_valid, error = validate_story_text(text)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        input_text = truncate_text(cleaned_text, max_length=500)
        
        # Create twist prompt based on type
        twist_prompts = {
            "unexpected": "Suddenly, something unexpected happened:",
            "reversal": "But then everything changed:",
            "revelation": "The shocking truth was revealed:",
            "betrayal": "Little did they know, someone had betrayed them:",
            "discovery": "They made a startling discovery:"
        }
        
        prompt = twist_prompts.get(twist_type.lower(), twist_prompts["unexpected"])
        twist_prompt = f"{input_text} {prompt}"
        
        try:
            # Generate twist with higher temperature for creativity
            twist_text = story_generator.generate(
                text=twist_prompt,
                max_length=100,
                temperature=0.9,
                top_p=0.95
            )
            
            # Extract just the twist part
            if prompt in twist_text:
                twist_only = twist_text.split(prompt, 1)[-1].strip()
            else:
                twist_only = twist_text[len(input_text):].strip()
            
            return {
                "twist": twist_only,
                "twist_type": twist_type,
                "full_story_with_twist": f"{cleaned_text} {prompt} {twist_only}",
                "prompt_used": prompt
            }
        except Exception as e:
            raise RuntimeError(f"Twist generation failed: {str(e)}")
