#!/usr/bin/env python3
"""
Quick diagnostic script to test backend connectivity and endpoint health.
Helps debug socket hang up and connection reset errors.

Usage:
    python debug_test.py
"""

import sys
import time
import json
import requests
from pathlib import Path

# Ensure backend is on path
sys.path.insert(0, str(Path(__file__).parent))

# Test configuration
BACKEND_URL = "http://localhost:8000"
ENDPOINTS = [
    ("/health", "GET", None),
    ("/api/v1/story/continue", "POST", {
        "story": "Once upon a time, there was a young girl who found a mysterious door.",
        "genre": "horror"
    }),
]

def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint and return result."""
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30, headers=headers)
        else:
            print(f"Unknown method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text}")
        
        return response.status_code < 400
    
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: Backend is not running or unreachable")
        print(f"   Error: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"⏱️  TIMEOUT: Request took too long")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Error: {e}")
        return False

def main():
    """Run all diagnostics."""
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║     PlotCraft Backend Diagnostic Tool                         ║
╚════════════════════════════════════════════════════════════════╝

Testing backend at: {BACKEND_URL}
""")
    
    # Check connectivity
    print("\n1️⃣  Checking backend connectivity...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"   ✅ Backend is running (Status: {response.status_code})")
    except Exception as e:
        print(f"""
   ❌ Backend is NOT running!
   
   Please start the backend with:
   
   cd backend
   python run.py
   
   Error details: {e}
""")
        return
    
    # Test each endpoint
    print("\n2️⃣  Testing endpoints...")
    results = []
    for endpoint, method, data in ENDPOINTS:
        success = test_endpoint(method, endpoint, data)
        results.append((endpoint, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {endpoint}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} endpoints working")
    
    if passed == total:
        print("\n✅ All tests passed! Backend is working correctly.")
    else:
        print("""
❌ Some tests failed. Troubleshooting steps:

1. Check backend logs for errors
2. Verify all dependencies are installed: pip install -r requirements.txt
3. Check if models are loaded properly (check console output)
4. Increase timeout values if generation is slow
5. Check available disk space and memory
""")

if __name__ == "__main__":
    main()
