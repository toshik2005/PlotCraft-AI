"""Story generation model."""

from transformers import pipeline
from typing import Optional
import os

from app.core.config import settings


class StoryGenerator:
    """Text generation model for story continuation."""
    
    def __init__(self):
        self.generator: Optional[pipeline] = None
        self._is_loaded = False
    
    def _load_model(self):
        """Lazy load the generation model."""
        if not self._is_loaded:
            try:
                self.generator = pipeline(
                    "text-generation",
                    model=settings.TEXT_GENERATION_MODEL
                )
                self._is_loaded = True
            except Exception as e:
                raise RuntimeError(f"Failed to load story generator model: {e}")
    
    def generate(
        self,
        text: str,
        max_length: int = None,
        num_return_sequences: int = 1,
        temperature: float = 0.8,
        top_p: float = 0.9
    ) -> str:
        """
        Generate story continuation.
        
        Args:
            text: Input story text
            max_length: Maximum length of generated text
            num_return_sequences: Number of sequences to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated story text
        """
        if not self._is_loaded:
            self._load_model()
        
        max_length = max_length or settings.MAX_STORY_LENGTH
        
        try:
            result = self.generator(
                text,
                max_length=max_length,
                num_return_sequences=num_return_sequences,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            
            if result and len(result) > 0:
                generated_text = result[0]["generated_text"]
                # Remove the original input if it's included
                if generated_text.startswith(text):
                    generated_text = generated_text[len(text):].strip()
                return generated_text
            else:
                return text
        except Exception as e:
            raise RuntimeError(f"Story generation failed: {e}")


# Global generator instance
story_generator = StoryGenerator()
