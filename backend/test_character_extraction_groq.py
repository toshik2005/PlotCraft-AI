#!/usr/bin/env python3
"""
Test script for improved Groq-based character extraction.

Tests the upgraded Groq character extraction with various scenarios,
including the "Lisa Beating Mayank" case that was failing before.
"""

import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.groq_service import extract_characters_with_groq, GroqUnavailable
from app.api.routes_character import (
    identify_characters_llm,
    identify_characters_hybrid
)
from app.schemas.character_schema import IdentifyCharacterRequest


def test_groq_extraction():
    """Test Groq-based character extraction with sample texts."""
    
    test_cases = [
        {
            "name": "Simple case - Two Characters",
            "text": "John and Lisa went to the party together.",
            "expected": ["John", "Lisa"]
        },
        {
            "name": "Complex case - Characters in Action (The failing case)",
            "text": "In the story, Lisa was beating Mayank while John watched from the doorway.",
            "expected": ["Lisa", "Mayank", "John"]
        },
        {
            "name": "Group Formation",
            "text": "Friends mayank and naitik decided to go camping with their friends sarah and emma.",
            "expected": ["mayank", "naitik", "sarah", "emma"]
        },
        {
            "name": "Named Introduction",
            "text": "A girl named Alice met a boy called Bob in the forest. Bob introduced her to Charlie.",
            "expected": ["Alice", "Bob", "Charlie"]
        },
        {
            "name": "Dialogue and Narrative",
            "text": '"Hello, I am David", said Sarah. "Nice to meet you David. This is Emma," replied John.',
            "expected": ["David", "Sarah", "Emma", "John"]
        },
        {
            "name": "Mixed Contexts",
            "text": "When Tom and Jerry met in the kitchen, Leo was already there. Diana and Frank entered together.",
            "expected": ["Tom", "Jerry", "Leo", "Diana", "Frank"]
        }
    ]
    
    print("=" * 80)
    print("GROQ CHARACTER EXTRACTION TEST SUITE")
    print("=" * 80)
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"Text: {test['text']}")
        print(f"Expected: {test['expected']}")
        
        try:
            result = extract_characters_with_groq(test['text'], max_characters=10)
            
            print(f"Result: {result['characters']}")
            print(f"Method: {result['method']}")
            print(f"Success: {result['success']}")
            
            # Check if extraction was successful
            if result['success']:
                found = all(char.lower() in [c.lower() for c in result['characters']] 
                           for char in test['expected'])
                status = "✓ PASS" if found else "⚠ PARTIAL"
            else:
                status = "✗ FAIL"
            
            print(f"Status: {status}")
            
        except GroqUnavailable as e:
            print(f"Status: ⚠ GROQ_UNAVAILABLE - {str(e)}")
        except Exception as e:
            print(f"Status: ✗ ERROR - {str(e)}")
        
        print("-" * 80)
        print()


async def test_groq_endpoint():
    """Test the Groq endpoint directly."""
    
    print("=" * 80)
    print("GROQ ENDPOINT TEST")
    print("=" * 80)
    print()
    
    # Test the failing case
    request = IdentifyCharacterRequest(
        text="In the story, Lisa was beating Mayank while John watched from the doorway.",
        max_characters=10
    )
    
    print("Input:")
    print(f"  Text: {request.text}")
    print(f"  Max Characters: {request.max_characters}")
    print()
    
    try:
        response = await identify_characters_llm(request)
        
        print("Groq Endpoint Response:")
        print(f"  Success: {response.success}")
        print(f"  Characters: {response.characters}")
        print(f"  Count: {response.count}")
        print(f"  Method: {response.method}")
        print(f"  Message: {response.message}")
        print()
        
        # Verify the critical fix: Lisa and Mayank should be separate
        if "Lisa" in response.characters and "Mayank" in response.characters:
            print("✓ SUCCESS: Lisa and Mayank correctly identified as separate characters!")
        else:
            print("✗ FAILED: Lisa and Mayank not correctly separated")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
    
    print()


async def test_hybrid_endpoint():
    """Test the hybrid endpoint."""
    
    print("=" * 80)
    print("HYBRID ENDPOINT TEST")
    print("=" * 80)
    print()
    
    request = IdentifyCharacterRequest(
        text="In the story, Lisa was beating Mayank while John watched from the doorway.",
        max_characters=10
    )
    
    print("Input:")
    print(f"  Text: {request.text}")
    print()
    
    try:
        response = await identify_characters_hybrid(request)
        
        print("Hybrid Endpoint Response:")
        print(f"  Success: {response.success}")
        print(f"  Characters: {response.characters}")
        print(f"  Count: {response.count}")
        print(f"  Method: {response.method}")
        print(f"  Message: {response.message}")
        print()
        
        if response.method == "llm":
            print("✓ Using advanced LLM method (preferred)")
        else:
            print(f"⚠ Using {response.method} fallback method")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
    
    print()


async def main():
    """Run all tests."""
    
    print("\n")
    print("🚀 STARTING CHARACTER EXTRACTION TESTS")
    print()
    
    # Test 1: Direct Groq extraction
    test_groq_extraction()
    
    # Test 2: Groq endpoint
    await test_groq_endpoint()
    
    # Test 3: Hybrid endpoint
    await test_hybrid_endpoint()
    
    print("=" * 80)
    print("TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    # Run async tests
    asyncio.run(main())
