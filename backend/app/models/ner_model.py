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
    def _normalize_name(name: str) -> str:
        name = name.strip()
        # If the name is fully lowercase, title-case it for display ("mayank" -> "Mayank")
        if name and name == name.lower():
            return " ".join(part.capitalize() for part in name.split())
        return name

    @staticmethod
    def _is_name_like_token(token: str) -> bool:
        """Heuristic filter to avoid treating pronouns/verbs as names."""
        t = token.strip().lower()
        if not t:
            return False

        # Common pronouns + glue words + frequent story verbs (keep small & safe)
        stop = {
            "i", "me", "my", "mine", "we", "us", "our", "ours", "you", "your", "yours",
            "he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs",
            "it", "its",
            "a", "an", "the", "and", "or", "but", "so", "because", "as", "of", "to", "in", "on", "at", "for", "with", "from", "by",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "named", "called",
            "boy", "boys", "girl", "girls", "man", "men", "woman", "women", "kid", "kids", "child", "children",
            "student", "students", "friend", "friends", "boyfriend", "girlfriend", "husband", "wife",
        }
        if t in stop:
            return False

        # Keep tokens that look like names (letters, apostrophe, hyphen)
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z'\-]{1,30}", token.strip()):
            return False

        return True

    @staticmethod
    def _extract_explicit_name_introductions(text: str, max_chars: int = 5) -> List[str]:
        """
        Extract names from common explicit patterns like 'named X' / 'called X'.

        This improves extraction for lowercase names that spaCy often misses (e.g. 'mayank').
        """
        if not text or not text.strip():
            return []

        # Capture the phrase after "named/called" up to a clause break/punctuation, then split.
        # Examples:
        # - "a boy named mayank" -> ["Mayank"]
        # - "boys named mayank and naitik" -> ["Mayank", "Naitik"]
        # - "girl named she was student, ..." -> ignore (she/was/student aren't name-like)
        pattern = re.compile(r"\b(?:named|called)\s+([^.!?\n]+)", re.IGNORECASE)

        seen: Set[str] = set()
        out: List[str] = []

        for m in pattern.finditer(text):
            chunk = m.group(1).strip()
            if not chunk:
                continue

            # Stop early at common clause breaks / transitions
            chunk = re.split(
                r"\b(?:who|that|which|where|when|while|because|so|but)\b",
                chunk,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

            # Split "Mayank and Naitik", "Mayank, Naitik and Riya", etc.
            parts = [p.strip() for p in re.split(r"\s*(?:,|&|\band\b)\s*", chunk, flags=re.IGNORECASE) if p.strip()]

            for part in parts:
                words = re.findall(r"[A-Za-z][A-Za-z'\-]{1,30}", part)
                if not words:
                    continue

                # Walk all tokens; each contiguous run of name-like tokens becomes a candidate.
                current: List[str] = []
                for w in words:
                    if NERModel._is_name_like_token(w):
                        current.append(w)
                    else:
                        if current:
                            candidate = " ".join(current[:3]).strip()
                            name = NERModel._normalize_name(candidate)
                            key = name.lower()
                            if key not in seen:
                                seen.add(key)
                                out.append(name)
                                if len(out) >= max_chars:
                                    return out
                            current = []
                if current:
                    candidate = " ".join(current[:3]).strip()
                    name = NERModel._normalize_name(candidate)
                    key = name.lower()
                    if key not in seen:
                        seen.add(key)
                        out.append(name)
                        if len(out) >= max_chars:
                            return out

        return out

    @staticmethod
    def _extract_names_after_prepositions(text: str, max_chars: int = 5) -> List[str]:
        """
        Extract lowercase names from patterns like 'with X', 'met X', 'saw X'.
        This helps catch: '... cheated on him with naitik' -> ['Naitik'].
        """
        if not text or not text.strip():
            return []

        triggers = r"(?:with|met|meet|meets|saw|see|sees|found|finds)"
        pattern = re.compile(rf"\b{triggers}\s+([A-Za-z][A-Za-z'\-]{{1,30}})\b", re.IGNORECASE)

        seen: Set[str] = set()
        out: List[str] = []
        for m in pattern.finditer(text):
            token = m.group(1).strip()
            if not NERModel._is_name_like_token(token):
                continue
            name = NERModel._normalize_name(token)
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(name)
            if len(out) >= max_chars:
                break
        return out

    @staticmethod
    def _extract_name_lists_after_group_nouns(text: str, max_chars: int = 5) -> List[str]:
        """
        Extract simple name lists after group nouns like 'friends' when users omit 'named'.

        Example:
          'there were a group of friends mayank toshik naitik' -> ['Mayank', 'Toshik', 'Naitik']
        """
        if not text or not text.strip():
            return []

        # Keep this small and conservative; only triggers after these nouns.
        nouns = r"(?:friends?|boys?|girls?|brothers?|sisters?|students?|kids?|children)"
        pattern = re.compile(rf"\b{nouns}\b\s+([^.!?\n]+)", re.IGNORECASE)

        stop = {
            "a", "an", "the", "and", "or", "of", "to", "in", "on", "at", "for", "with", "without",
            "from", "by", "as", "is", "are", "was", "were", "be", "been", "being",
            "group", "named", "called",
        }

        seen: Set[str] = set()
        out: List[str] = []

        for m in pattern.finditer(text):
            chunk = m.group(1).strip()
            if not chunk:
                continue

            # Stop at common clause breaks if present
            chunk = re.split(
                r"\b(?:who|that|which|where|when|while|because|so)\b",
                chunk,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

            # Split on commas / conjunctions first, then into words
            parts = [p.strip() for p in re.split(r"\s*(?:,|&|\band\b)\s*", chunk, flags=re.IGNORECASE) if p.strip()]
            words: List[str] = []
            for p in parts:
                words.extend(re.findall(r"[A-Za-z][A-Za-z'\-]{1,30}", p))

            # If the chunk doesn't look like a short list, don't guess
            if len(words) < 2:
                continue

            for w in words[: max_chars * 2]:
                key = w.lower()
                if key in stop:
                    continue
                name = NERModel._normalize_name(w)
                k = name.lower()
                if k in seen:
                    continue
                seen.add(k)
                out.append(name)
                if len(out) >= max_chars:
                    return out

        return out

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
        
        # First: explicit introductions + simple group name lists + basic preposition patterns
        explicit = (
            NERModel._extract_explicit_name_introductions(text, max_chars=max_chars)
            + NERModel._extract_name_lists_after_group_nouns(text, max_chars=max_chars)
            + NERModel._extract_names_after_prepositions(text, max_chars=max_chars)
        )[:max_chars]

        # Second: capitalized proper noun sequences (best-effort heuristic)
        pattern = r"(?:^|[.!?\s])([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        matches = re.findall(pattern, text, re.MULTILINE)

        seen: Set[str] = {c.lower() for c in explicit}
        unique_chars: List[str] = list(explicit)

        for match in matches:
            raw = match.strip()
            tokens = raw.split()
            # Require that at least one token is name-like and all tokens pass a loose name check
            name_like_tokens = [t for t in tokens if NERModel._is_name_like_token(t)]
            if not name_like_tokens:
                continue
            candidate = " ".join(name_like_tokens[:3])
            char_norm = NERModel._normalize_name(candidate)
            key = char_norm.lower()
            if key not in seen and len(char_norm.split()) <= 3:  # Max 3-word names
                seen.add(key)
                unique_chars.append(char_norm)
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
        
        # Try spaCy first, but supplement with explicit/regex patterns for robustness
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
                    norm = self._normalize_name(name)
                    if norm.lower() not in seen:
                        seen.add(norm.lower())
                        unique_names.append(norm)
                        if len(unique_names) >= max_chars:
                            break
                
                # If spaCy misses (often with lowercase names), enrich with explicit introductions + regex
                if len(unique_names) < max_chars:
                    explicit = self._extract_explicit_name_introductions(text, max_chars=max_chars)
                    group_lists = self._extract_name_lists_after_group_nouns(text, max_chars=max_chars)
                    regex = self._extract_characters_regex(text, max_chars=max_chars)
                    for candidate in (explicit + group_lists + regex):
                        cand = self._normalize_name(candidate)
                        if cand.lower() in seen:
                            continue
                        seen.add(cand.lower())
                        unique_names.append(cand)
                        if len(unique_names) >= max_chars:
                            break

                logger.debug(f"spaCy extracted {len(unique_names)} characters (enriched): {unique_names}")
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

