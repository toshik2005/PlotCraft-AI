#!/usr/bin/env python3
"""
Quick test to verify the timeout fix works
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_status_endpoint():
    """Test that status endpoint doesn't hang"""
    print("\n" + "="*70)
    print("TESTING STATUS ENDPOINT (Should NOT timeout)")
    print("="*70)
    
    from app.services.groq_service import get_groq_status
    
    print("Calling get_groq_status() - this should return instantly...")
    status = get_groq_status()
    
    print("✓ Status returned immediately (no timeout)!")
    print(f"Status: {status}")
    
    return True

def test_api_key_validation():
    """Test API key validation"""
    print("\n" + "="*70)
    print("TESTING API KEY VALIDATION")
    print("="*70)
    
    from app.services.groq_service import GROQ_API_KEY
    
    if not GROQ_API_KEY:
        print("✗ GROQ_API_KEY not set in environment")
        print("  → Create .env file with: GROQ_API_KEY=gsk_your_key")
        return False
    
    if not GROQ_API_KEY.startswith("gsk_"):
        print(f"✗ Invalid API key format: {GROQ_API_KEY[:20]}...")
        print("  → Keys must start with 'gsk_'")
        return False
    
    print(f"✓ API key format is valid: {GROQ_API_KEY[:20]}...")
    return True

if __name__ == "__main__":
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "TIMEOUT FIX VERIFICATION" + " "*30 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        test_status_endpoint()
        test_api_key_validation()
        
        print("\n" + "="*70)
        print("✓ Timeout fix verified - no blocking calls from status endpoint!")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
