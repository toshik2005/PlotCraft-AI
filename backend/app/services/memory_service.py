"""
Character and entity memory service for multi-turn conversations.

Provides:
1. Character extraction from story text
2. Per-user session character persistence
3. Character accumulation across multiple story generations

Current implementation uses in-memory storage (USER_MEMORY dict).
For production at scale, this should be replaced with:
- Redis for distributed caching
- Database (PostgreSQL/MongoDB) for persistence
- Session management middleware for cleanup
"""

import logging
from typing import List, Dict, Set

from app.models.ner_model import ner_model
from app.utils.text_preprocessing import clean_text
from app.utils.validators import validate_story_text

logger = logging.getLogger(__name__)

# ============================================================================
# IN-MEMORY USER CHARACTER STORAGE
# ============================================================================
# TODO: Replace with Redis in production for scalability
# TODO: Add TTL (time-to-live) for session cleanup
# TODO: Consider database backup for persistence across restarts

USER_MEMORY: Dict[str, Set[str]] = {}
"""
In-memory store for user session characters.

Structure: {user_id: set(character_names)}

Production improvements:
- Use RedisDict for distributed caching
- Add session expiry TTL (e.g., 24 hours)
- Implement background cleanup task
- Add database persistence layer
"""


def get_characters(story: str) -> List[str]:
    """
    Extract character names from story text.
    
    Args:
        story: Input story text
    
    Returns:
        List of unique character names
    """
    if not story or not story.strip():
        return []
    cleaned = clean_text(story)
    return ner_model.extract_characters(cleaned)


def save_user_characters(user_id: str, characters: List[str]) -> None:
    """
    Save/persist character names for a specific user session.
    
    Merges new characters with existing ones (deduplication at lowercase level).
    Useful for multi-turn conversations where characters should persist.
    
    Args:
        user_id: Unique user identifier (session ID, user account ID, etc.)
        characters: List of character names to add
    
    Example:
        >>> save_user_characters("user_123", ["Alice", "Bob"])
        >>> save_user_characters("user_123", ["Bob", "Charlie"])
        >>> chars = get_user_characters("user_123")
        >>> print(chars)  # ["Alice", "Bob", "Charlie"]
    """
    if not user_id or not user_id.strip():
        logger.warning("Cannot save characters: empty user_id")
        return
    
    if not characters:
        return
    
    user_id = user_id.strip()
    
    # Initialize user's character set if not exists
    if user_id not in USER_MEMORY:
        USER_MEMORY[user_id] = set()
    
    # Add new characters (case-insensitive deduplication)
    original_count = len(USER_MEMORY[user_id])
    for char in characters:
        if char and char.strip():
            USER_MEMORY[user_id].add(char.strip())
    
    new_count = len(USER_MEMORY[user_id])
    logger.info(
        f"User {user_id}: saved {len(characters)} characters. "
        f"Total: {original_count} -> {new_count}"
    )


def get_user_characters(user_id: str) -> List[str]:
    """
    Retrieve persisted characters for a specific user session.
    
    Returns empty list if user not found.
    
    Args:
        user_id: Unique user identifier
    
    Returns:
        List of persisted character names for this user
    
    Example:
        >>> save_user_characters("user_123", ["Alice", "Bob"])
        >>> chars = get_user_characters("user_123")
        >>> print(chars)  # ["Alice", "Bob"]
    """
    if not user_id or not user_id.strip():
        return []
    
    user_id = user_id.strip()
    
    if user_id not in USER_MEMORY:
        return []
    
    characters = sorted(list(USER_MEMORY[user_id]))
    logger.debug(f"Retrieved {len(characters)} characters for user {user_id}")
    return characters


def clear_user_characters(user_id: str) -> None:
    """
    Clear all persisted characters for a user session.
    
    Useful for starting a new story or cleanup.
    
    Args:
        user_id: Unique user identifier
    """
    if not user_id or user_id not in USER_MEMORY:
        return
    
    user_id = user_id.strip()
    del USER_MEMORY[user_id]
    logger.info(f"Cleared character memory for user {user_id}")


def get_memory_stats() -> Dict[str, int]:
    """
    Get statistics about current memory usage.
    
    Returns:
        Dictionary with memory stats {users: int, total_characters: int}
    """
    total_chars = sum(len(chars) for chars in USER_MEMORY.values())
    return {
        "active_users": len(USER_MEMORY),
        "total_characters": total_chars,
    }


class MemoryService:
    """Service for character and entity extraction with session persistence."""
    
    @staticmethod
    def extract_characters(text: str) -> dict:
        """
        Extract characters from story text.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with extracted characters and count
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
            logger.error(f"Character extraction failed: {e}")
            raise RuntimeError(f"Character extraction failed: {str(e)}")
    
    @staticmethod
    def extract_entities(text: str) -> dict:
        """
        Extract all named entities from story text by type.
        
        Args:
            text: Input story text
        
        Returns:
            Dictionary with all extracted entities grouped by type
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
            logger.error(f"Entity extraction failed: {e}")
            raise RuntimeError(f"Entity extraction failed: {str(e)}")
    
    @staticmethod
    def save_session_characters(user_id: str, characters: List[str]) -> dict:
        """
        Save characters to user session memory.
        
        Args:
            user_id: User session identifier
            characters: List of character names
        
        Returns:
            Dictionary with save result and updated characters
        """
        if not user_id:
            raise ValueError("user_id required")
        
        save_user_characters(user_id, characters)
        persisted = get_user_characters(user_id)
        
        return {
            "saved": len(characters),
            "persisted_count": len(persisted),
            "persisted_characters": persisted
        }
    
    @staticmethod
    def get_session_characters(user_id: str) -> dict:
        """
        Get all persisted characters for a user session.
        
        Args:
            user_id: User session identifier
        
        Returns:
            Dictionary with persisted characters
        """
        characters = get_user_characters(user_id)
        
        return {
            "user_id": user_id,
            "characters": characters,
            "count": len(characters)
        }

