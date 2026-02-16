"""Character and entity memory service."""

from app.models.ner_model import ner_model
from app.utils.text_preprocessing import clean_text
from app.utils.validators import validate_story_text


class MemoryService:
    """Service for character and entity extraction."""
    
    @staticmethod
    def extract_characters(text: str) -> dict:
        """
        Extract characters from story text.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with extracted characters
        """
        # Validate input
        is_valid, error = validate_story_text(text, min_length=5)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        try:
            characters = ner_model.extract_characters(cleaned_text)
            
            return {
                "characters": characters,
                "count": len(characters)
            }
        except Exception as e:
            raise RuntimeError(f"Character extraction failed: {str(e)}")
    
    @staticmethod
    def extract_entities(text: str) -> dict:
        """
        Extract all named entities from story text.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with all extracted entities by type
        """
        # Validate input
        is_valid, error = validate_story_text(text, min_length=5)
        if not is_valid:
            raise ValueError(error)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        try:
            entities = ner_model.extract_entities(cleaned_text)
            
            # Count total entities
            total_count = sum(len(entity_list) for entity_list in entities.values())
            
            return {
                "entities": entities,
                "total_count": total_count,
                "entity_types": list(entities.keys())
            }
        except Exception as e:
            raise RuntimeError(f"Entity extraction failed: {str(e)}")
