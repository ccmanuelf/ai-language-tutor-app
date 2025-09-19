#!/usr/bin/env python3
"""
Diagnostic Page Test Script
==========================

This script helps verify that the diagnostic page is working correctly
with the updated JWT token.

Usage:
    python test_diagnostic_page.py

Expected Output:
    - Diagnostic page should be accessible
    - API calls from diagnostic page should work
    - All tests should pass
"""

import requests
import time

def test_diagnostic_page():
    """Test if diagnostic page is accessible"""
    try:
        response = requests.get("http://localhost:3000/test", timeout=5)
        if response.status_code == 200:
            print("✅ Diagnostic page: Accessible")
            return True
        else:
            print(f"❌ Diagnostic page: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Diagnostic page: Not accessible ({e})")
        return False

def test_api_with_new_token():
    """Test API call with the new JWT token"""
    try:
        # New JWT token (expires in 1 hour)
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJleHAiOjE3NTY2NzEzNzh9.THu3Ij-GoUzUa8lAChkQGFALLjSgqbtIrgrQ9RrI-eQ"
        
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "message": "Test message from diagnostic page",
                "language": "en-claude"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print("✅ API call with new token: Working")
                print(f"   Response preview: {data['response'][:80]}...")
                return True
            else:
                print("❌ API call with new token: Unexpected response format")
                return False
        else:
            print(f"❌ API call with new token: Error (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ API call with new token: Failed ({e})")
        return False

def main():
    """Run diagnostic tests"""
    print("🧪 Diagnostic Page Test")
    print("=" * 30)
    
    # Wait a moment for servers to fully start
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Diagnostic Page", test_diagnostic_page),
        ("API with New Token", test_api_with_new_token)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name}: Test failed with exception ({e})")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 30)
    print("📋 TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n🚀 You can now test the diagnostic page:")
        print("   Open http://localhost:3000/test in your browser")
        print("   Run through each test and check the debug log")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure both servers are running")
        print("   2. Check if the new JWT token has expired")
        print("   3. Verify the demo user exists in the database")

if __name__ == "__main__":
    main()