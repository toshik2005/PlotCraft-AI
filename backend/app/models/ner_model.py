"""Named Entity Recognition model for character extraction."""

import spacy
from typing import List, Set
from app.core.config import settings


class NERModel:
    """NER model for extracting characters and entities."""
    
    def __init__(self):
        self.nlp = None
        self._is_loaded = False
    
    def _load_model(self):
        """Lazy load the spaCy model."""
        if not self._is_loaded:
            try:
                self.nlp = spacy.load(settings.SPACY_MODEL)
                self._is_loaded = True
            except OSError:
                raise RuntimeError(
                    f"spaCy model '{settings.SPACY_MODEL}' not found. "
                    f"Please install it with: python -m spacy download {settings.SPACY_MODEL}"
                )
    
    def extract_characters(self, text: str) -> List[str]:
        """
        Extract character names from text.
        
        Args:
            text: Input story text
        
        Returns:
            List of unique character names
        """
        if not self._is_loaded:
            self._load_model()
        
        if not text or not text.strip():
            return []
        
        doc = self.nlp(text)
        names = [
            ent.text for ent in doc.ents 
            if ent.label_ == "PERSON"
        ]
        
        # Remove duplicates while preserving order
        seen: Set[str] = set()
        unique_names = []
        for name in names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)
        
        return unique_names
    
    def extract_entities(self, text: str) -> dict[str, List[str]]:
        """
        Extract all named entities from text.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        if not self._is_loaded:
            self._load_model()
        
        if not text or not text.strip():
            return {}
        
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            if ent.text not in entities[label]:
                entities[label].append(ent.text)
        
        return entities


# Global NER model instance
ner_model = NERModel()
