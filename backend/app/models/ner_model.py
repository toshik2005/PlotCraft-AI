"""
Named Entity Recognition model for character extraction.

Provides dual strategies for character extraction:
1. Primary: spaCy NER (PERSON label) - high accuracy
2. Fallback: Regex-based detection - graceful degradation when spaCy unavailable
"""

import re
import logging
from typing import List, Set

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class NERModel:
    """
    NER model for extracting character names from story text.
    
    Uses spaCy for accurate Named Entity Recognition with automatic fallback
    to regex-based character detection if spaCy is unavailable.
    """
    
    def __init__(self):
        self.nlp = None
        self._is_loaded = False
        self._spacy_failed = False
    
    def _load_model(self) -> bool:
        """
        Lazy load the spaCy model.
        
        Returns:
            True if loaded successfully, False if failed (fallback to regex)
        """
        if self._is_loaded:
            return True
        
        if self._spacy_failed:
            return False
        
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not available. Using regex fallback for character extraction.")
            self._spacy_failed = True
            return False
        
        try:
            logger.info(f"Loading spaCy model: {settings.SPACY_MODEL}")
            self.nlp = spacy.load(settings.SPACY_MODEL)
            self._is_loaded = True
            logger.info("spaCy model loaded successfully")
            return True
        except OSError as e:
            logger.warning(
                f"spaCy model '{settings.SPACY_MODEL}' not found. "
                f"Using regex fallback. To use spaCy, install with: "
                f"python -m spacy download {settings.SPACY_MODEL}"
            )
            self._spacy_failed = True
            return False
    
    @staticmethod
    def _extract_characters_regex(text: str, max_chars: int = 5) -> List[str]:
        """
        Fallback regex-based character detection.
        
        Detects capitalized Proper nouns (capitalized words not at sentence start).
        
        Args:
            text: Input text
            max_chars: Maximum number of characters to return
        
        Returns:
            List of detected character names
        """
        if not text or not text.strip():
            return []
        
        # Pattern: 
        # - Preceded by space or punctuation (not at sentence start)
        # - At least one capitalized letter
        # - Optional middle/last names
        pattern = r'(?:^|[.!?\s])([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        matches = re.findall(pattern, text, re.MULTILINE)
        
        # Remove duplicates while preserving order
        seen: Set[str] = set()
        unique_chars = []
        for match in matches:
            char = match.strip()
            if char.lower() not in seen and len(char.split()) <= 3:  # Max 3-word names
                seen.add(char.lower())
                unique_chars.append(char)
                if len(unique_chars) >= max_chars:
                    break
        
        logger.debug(f"Regex extraction found {len(unique_chars)} characters: {unique_chars}")
        return unique_chars
    
    def extract_characters(self, text: str, max_chars: int = 5) -> List[str]:
        """
        Extract character names from text using spaCy or fallback regex.
        
        Priority:
        1. Try spaCy NER (PERSON entities)
        2. Fall back to regex if spaCy unavailable
        3. Return empty list if text is empty
        
        Args:
            text: Input story text
            max_chars: Maximum number of characters to return (default: 5)
        
        Returns:
            List of unique character names (max 5)
        
        Example:
            >>> ner = NERModel()
            >>> chars = ner.extract_characters("Alice met Bob at the market.")
            >>> print(chars)  # ['Alice', 'Bob']
        """
        if not text or not text.strip():
            return []
        
        # Try spaCy first
        if self._load_model():
            try:
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
                        if len(unique_names) >= max_chars:
                            break
                
                logger.debug(f"spaCy extracted {len(unique_names)} characters: {unique_names}")
                return unique_names
            except Exception as e:
                logger.error(f"spaCy extraction failed: {e}. Falling back to regex.")
                self._spacy_failed = True
        
        # Fallback to regex
        logger.info("Using regex fallback for character extraction")
        return self._extract_characters_regex(text, max_chars)
    
    def extract_entities(self, text: str) -> dict[str, List[str]]:
        """
        Extract all named entities from text (spaCy only).
        
        Falls back to empty dict if spaCy unavailable.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary mapping entity types (PERSON, ORG, etc.) to lists of entities
        """
        if not text or not text.strip():
            return {}
        
        if not self._load_model():
            logger.warning("spaCy unavailable. Cannot extract full entities.")
            return {}
        
        try:
            doc = self.nlp(text)
            entities = {}
            
            for ent in doc.ents:
                label = ent.label_
                if label not in entities:
                    entities[label] = []
                if ent.text not in entities[label]:
                    entities[label].append(ent.text)
            
            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {}


# Global NER model instance
ner_model = NERModel()

