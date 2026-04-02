#!/usr/bin/env python3
"""
Quick test for improved story generation and character extraction.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.groq_service import (
    extract_characters_with_groq,
    generate_story_with_groq,
    GroqUnavailable
)

def test_character_extraction():
    """Test character extraction with the problematic text."""
    
    print("=" * 80)
    print("CHARACTER EXTRACTION TEST")
    print("=" * 80)
    print()
    
    # Test case from user screenshot
    text = "john in the dark woods with max and mayank travelling in the north to fight the wildings"
    
    print(f"Input text: {text}")
    print()
    print("Expected characters: john, max, mayank")
    print()
    
    try:
        result = extract_characters_with_groq(text, max_characters=10)
        
        print(f"Result:")
        print(f"  Success: {result['success']}")
        print(f"  Characters: {result['characters']}")
        print(f"  Count: {result['count']}")
        print(f"  Method: {result['method']}")
        print()
        
        # Verify all three characters are present
        expected = ["john", "max", "mayank"]
        extracted_lower = [c.lower() for c in result['characters']]
        
        all_found = all(exp.lower() in [e.lower() for e in result['characters']] for exp in expected)
        
        if all_found:
            print("✓ SUCCESS: All characters correctly extracted!")
            print(f"  ✓ john: {'john' in extracted_lower or 'John' in result['characters']}")
            print(f"  ✓ max: {'max' in extracted_lower or 'Max' in result['characters']}")
            print(f"  ✓ mayank: {'mayank' in extracted_lower or 'Mayank' in result['characters']}")
        else:
            print("✗ PARTIAL: Some characters missing")
            for exp in expected:
                found = any(exp.lower() == e.lower() for e in result['characters'])
                status = "✓" if found else "✗"
                print(f"  {status} {exp}")
                
    except GroqUnavailable as e:
        print(f"✗ Error: Groq unavailable - {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def test_story_generation():
    """Test story generation with detailed prompt."""
    
    print("=" * 80)
    print("STORY GENERATION TEST")
    print("=" * 80)
    print()
    
    # Test story generation
    prompt = "john in the dark woods with max and mayank travelling in the north to fight the wildings"
    genre = "action"
    
    print(f"Original prompt: {prompt}")
    print(f"Genre: {genre}")
    print()
    
    try:
        story = generate_story_with_groq(
            prompt=prompt,
            genre=genre,
            max_tokens=500,
            temperature=0.8,
            characters=["john", "max", "mayank"]
        )
        
        print("Generated story continuation:")
        print("-" * 80)
        print(story)
        print("-" * 80)
        print()
        
        # Check if story continues from premise (not repeating original)
        if prompt.lower() not in story.lower():
            print("✓ Story generates continuation (not repeating original)")
        else:
            print("⚠ Story may be repeating original prompt")
            
        # Check if characters are mentioned
        chars_mentioned = sum(1 for char in ["john", "max", "mayank"] if char.lower() in story.lower())
        print(f"✓ Characters mentioned: {chars_mentioned}/3")
        
        # Check length
        word_count = len(story.split())
        print(f"✓ Story length: {word_count} words")
        
    except GroqUnavailable as e:
        print(f"✗ Error: Groq unavailable - {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING IMPROVED GROQ TESTS")
    print("=" * 80)
    print()
    
    # Test character extraction
    test_character_extraction()
    
    # Test story generation
    test_story_generation()
    
    print("=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
