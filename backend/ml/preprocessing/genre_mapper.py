"""
Helpers for mapping raw genre labels into a normalized label set.
"""

from collections import Counter
from typing import Iterable, Mapping


def build_genre_mapping(raw_genres: Iterable[str]) -> Mapping[str, str]:
    """
    Given a collection of raw genre labels, build a mapping from
    noisy labels to a consolidated canonical label.

    For now this is a stub that lowercases and strips whitespace.
    Extend with project-specific rules or a lookup table.
    """
    counter = Counter(g.strip().lower() for g in raw_genres if g and isinstance(g, str))
    # In a real implementation you might collapse very rare genres into "other".
    return {g: g for g in counter.keys()}

"""Genre mapping and classification utilities."""


def map_genres(stories_data):
    """
    Map stories to their respective genres.
    
    Args:
        stories_data: List of story objects
        
    Returns:
        Mapped stories with genre information
    """
    pass
