"""
Integration tests for the new Character Identification API.

Test the identify character endpoints to ensure they work correctly.
"""

import requests
import json
from typing import List, Dict

# API Configuration
BASE_URL = "http://localhost:8000/api/v1/character"
TIMEOUT = 10


class CharacterAPITester:
    """Test the Character Identification API."""
    
    @staticmethod
    def test_single_character_identification():
        """Test the single character identification endpoint."""
        print("\n" + "="*60)
        print("TEST 1: Single Character Identification")
        print("="*60)
        
        payload = {
            "text": "Alice found a mysterious door in the forest. Bob was waiting outside.",
            "max_characters": 5
        }
        
        print(f"\nRequest URL: POST {BASE_URL}/identify")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/identify",
                json=payload,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Body:")
            print(json.dumps(result, indent=2))
            
            # Verify response
            assert result["success"] == True
            assert isinstance(result["characters"], list)
            assert result["count"] == len(result["characters"])
            assert result["method"] in ["spacy", "regex"]
            
            print("\n✅ TEST PASSED")
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"\n❌ TEST FAILED: {e}")
            return None
    
    @staticmethod
    def test_batch_character_identification():
        """Test the batch character identification endpoint."""
        print("\n" + "="*60)
        print("TEST 2: Batch Character Identification")
        print("="*60)
        
        payload = [
            {
                "text": "Alice met Bob in the forest",
                "max_characters": 5
            },
            {
                "text": "Charlie and Diana went to the party",
                "max_characters": 5
            },
            {
                "text": "A boy named mayank was walking with naitik",
                "max_characters": 5
            }
        ]
        
        print(f"\nRequest URL: POST {BASE_URL}/batch-identify")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/batch-identify",
                json=payload,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Body:")
            print(json.dumps(result, indent=2))
            
            # Verify response
            assert result["total_requests"] == len(payload)
            assert result["successful"] + result["failed"] == len(payload)
            assert isinstance(result["results"], list)
            
            print("\n✅ TEST PASSED")
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"\n❌ TEST FAILED: {e}")
            return None
    
    @staticmethod
    def test_empty_text_error():
        """Test error handling for empty text."""
        print("\n" + "="*60)
        print("TEST 3: Error Handling - Empty Text")
        print("="*60)
        
        payload = {
            "text": "   ",
            "max_characters": 5
        }
        
        print(f"\nRequest URL: POST {BASE_URL}/identify")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/identify",
                json=payload,
                timeout=TIMEOUT
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Body:")
            print(json.dumps(response.json(), indent=2))
            
            # Verify error response
            assert response.status_code == 400
            
            print("\n✅ TEST PASSED (Expected Error Handled)")
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"\n❌ TEST FAILED: {e}")
            return None
    
    @staticmethod
    def test_complex_narrative():
        """Test with a more complex narrative."""
        print("\n" + "="*60)
        print("TEST 4: Complex Narrative Analysis")
        print("="*60)
        
        complex_text = """
        In a small village lived a boy named mayank. He was best friends with naitik and toshik.
        One day, mayank discovered a mysterious manuscript written by a scholar named professor kumar.
        The three friends - mayank, naitik, and toshik - decided to meet with professor kumar to 
        understand the ancient script. Along the way, they encountered a traveler named sarah who 
        joined their quest.
        """
        
        payload = {
            "text": complex_text,
            "max_characters": 10
        }
        
        print(f"\nRequest URL: POST {BASE_URL}/identify")
        print(f"Payload Text (truncated): {complex_text[:100]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/identify",
                json=payload,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"\nResponse Status: {response.status_code}")
            print(f"Identified Characters: {result['characters']}")
            print(f"Character Count: {result['count']}")
            print(f"Extraction Method: {result['method']}")
            
            print("\n✅ TEST PASSED")
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"\n❌ TEST FAILED: {e}")
            return None
    
    @staticmethod
    def run_all_tests():
        """Run all tests."""
        print("\n" + "🧪 CHARACTER IDENTIFICATION API - TEST SUITE 🧪".center(80))
        
        results = {
            "single_identification": CharacterAPITester.test_single_character_identification(),
            "batch_identification": CharacterAPITester.test_batch_character_identification(),
            "empty_text_error": CharacterAPITester.test_empty_text_error(),
            "complex_narrative": CharacterAPITester.test_complex_narrative(),
        }
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result is not None else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        return results


if __name__ == "__main__":
    """Run the test suite."""
    print("""
    ⚠️  Before running these tests:
    
    1. Ensure the backend server is running on http://localhost:8000
    2. Install requests package: pip install requests
    3. Run this script: python tests_character_api.py
    
    Expected behavior:
    - Tests 1, 2, 4 should extract character names
    - Test 3 should properly handle the empty text error with 400 status code
    """)
    
    CharacterAPITester.run_all_tests()
