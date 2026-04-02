#!/usr/bin/env python3
"""
Groq API Diagnostic Tool
Helps identify and debug Groq API configuration issues
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def diagnose_env_setup():
    """Check if .env file exists and has GROQ_API_KEY"""
    print("\n" + "="*70)
    print("CHECKING ENVIRONMENT SETUP")
    print("="*70)
    
    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✓ .env file found at:", env_file)
        with open(env_file, 'r') as f:
            lines = f.readlines()
            has_groq_key = any("GROQ_API_KEY" in line for line in lines)
            if has_groq_key:
                print("✓ GROQ_API_KEY found in .env")
            else:
                print("✗ GROQ_API_KEY NOT found in .env")
                print("  → Add: GROQ_API_KEY=gsk_your_key_here")
    else:
        print("✗ .env file NOT found")
        print("  → Create .env in project root with GROQ_API_KEY=gsk_your_key")
        return False
    
    return True

def diagnose_api_key():
    """Check if GROQ_API_KEY environment variable is set"""
    print("\n" + "="*70)
    print("CHECKING API KEY CONFIGURATION")
    print("="*70)
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("✗ GROQ_API_KEY environment variable is NOT set")
        print("  → Make sure .env file is in project root")
        print("  → Restart Python/backend after creating .env")
        return False
    
    print(f"✓ GROQ_API_KEY is set: {api_key[:20]}...")
    
    if not api_key.startswith("gsk_"):
        print(f"✗ Invalid API key format: starts with '{api_key[:10]}'")
        print("  → Groq keys must start with 'gsk_'")
        print("  → Get a new key from: https://console.groq.com/keys")
        return False
    
    print("✓ API key format is valid (starts with gsk_)")
    return True

def diagnose_groq_sdk():
    """Check if Groq SDK is installed"""
    print("\n" + "="*70)
    print("CHECKING GROQ SDK")
    print("="*70)
    
    try:
        from groq import Groq
        print("✓ Groq SDK is installed")
        return True
    except ImportError:
        print("✗ Groq SDK is NOT installed")
        print("  → Run: pip install groq")
        return False

def diagnose_groq_connection():
    """Test actual Groq API connection"""
    print("\n" + "="*70)
    print("TESTING GROQ API CONNECTION")
    print("="*70)
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("⊘ Skipping connection test - API key not set")
        return False
    
    if not api_key.startswith("gsk_"):
        print("⊘ Skipping connection test - Invalid API key format")
        return False
    
    try:
        from groq import Groq
        
        print("Testing connection to Groq API...")
        client = Groq(api_key=api_key)
        
        message = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "Say 'OK' in one word"}],
            max_tokens=5,
        )
        
        response = message.choices[0].message.content
        if response:
            print(f"✓ Groq API connection successful!")
            print(f"  Response: '{response}'")
            return True
        else:
            print("✗ Groq API returned empty response")
            return False
            
    except Exception as e:
        error_str = str(e)
        print(f"✗ Groq API connection failed: {error_str}")
        
        if "401" in error_str or "Unauthorized" in error_str:
            print("  → API key is invalid or expired")
            print("  → Get a new key: https://console.groq.com/keys")
        elif "429" in error_str or "Rate limit" in error_str:
            print("  → Rate limit exceeded, try again in a moment")
        elif "500" in error_str or "503" in error_str:
            print("  → Groq servers are temporarily unavailable")
            print("  → Check: https://status.groq.com/")
        
        return False

def diagnose_groq_service():
    """Test the groq_service module"""
    print("\n" + "="*70)
    print("TESTING GROQ_SERVICE MODULE")
    print("="*70)
    
    try:
        from app.services.groq_service import get_groq_status
        
        print("Testing groq_service.get_groq_status()...")
        status = get_groq_status()
        
        print(f"Status: {status}")
        
        if status.get("configured"):
            print("✓ Groq service is properly configured")
            if status.get("available") or status.get("status") == "ready":
                print("✓ Groq API is accessible")
                return True
            else:
                print("✗ Groq API is not accessible")
                print(f"  Error: {status.get('error', 'Unknown')}")
                return False
        else:
            print("✗ Groq service is NOT configured")
            print(f"  Error: {status.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing groq_service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_character_extraction_test():
    """Test character extraction with Groq"""
    print("\n" + "="*70)
    print("TESTING CHARACTER EXTRACTION")
    print("="*70)
    
    try:
        from app.services.groq_service import extract_characters_with_groq
        
        test_text = "john in dark woods with max and mayank travelling"
        print(f"Test text: '{test_text}'")
        print("Extracting characters...")
        
        result = extract_characters_with_groq(test_text, max_characters=10)
        
        print(f"✓ Character extraction successful!")
        print(f"  Characters: {result['characters']}")
        print(f"  Count: {result['count']}")
        
        # Check if all expected characters are there
        expected = ["john", "max", "mayank"]
        extracted_lower = [c.lower() for c in result['characters']]
        
        missing = [e for e in expected if e.lower() not in extracted_lower]
        if missing:
            print(f"  ⚠ Missing characters: {missing}")
            return False
        else:
            print(f"  ✓ All expected characters found!")
            return True
            
    except Exception as e:
        print(f"✗ Character extraction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostics"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "GROQ API DIAGNOSTIC TOOL" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    results = []
    
    # Run diagnostics in order
    results.append(("Environment Setup", diagnose_env_setup()))
    results.append(("API Key Configuration", diagnose_api_key()))
    results.append(("Groq SDK", diagnose_groq_sdk()))
    results.append(("Groq Connection", diagnose_groq_connection()))
    results.append(("Groq Service", diagnose_groq_service()))
    
    if all(r[1] for r in results[:4]):  # If first 4 checks pass
        results.append(("Character Extraction", run_character_extraction_test()))
    
    # Print summary
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All diagnostics passed! Your Groq API is properly configured.")
        print("  You can now run character extraction and story generation.")
    else:
        print("\n✗ Some diagnostics failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  1. Create .env file with: GROQ_API_KEY=gsk_your_key")
        print("  2. Get key from: https://console.groq.com/keys")
        print("  3. Restart backend: python run.py")
        print("\nFor detailed setup guide, see: GROQ_API_SETUP.md")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
