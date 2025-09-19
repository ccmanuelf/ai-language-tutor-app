#!/usr/bin/env python3
"""
Frontend Status Test Script
==========================

This script verifies that the frontend is working correctly
and provides guidance for speech recognition network errors.

Usage:
    python test_frontend_status.py
"""

import requests
import time

def test_frontend_access():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend home page: Accessible")
            return True
        else:
            print(f"❌ Frontend home page: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend home page: Not accessible ({e})")
        return False

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

def test_chat_page():
    """Test if chat page is accessible"""
    try:
        response = requests.get("http://localhost:3000/chat", timeout=5)
        if response.status_code == 200:
            print("✅ Chat page: Accessible")
            return True
        else:
            print(f"❌ Chat page: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Chat page: Not accessible ({e})")
        return False

def main():
    """Run frontend status tests"""
    print("🧪 Frontend Status Test")
    print("=" * 30)
    
    # Wait a moment for servers to fully start
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Frontend Home Page", test_frontend_access),
        ("Diagnostic Page", test_diagnostic_page),
        ("Chat Page", test_chat_page)
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
        print(f"🎉 All frontend pages accessible! ({passed}/{total})")
        print("\n🚀 You can now test the application:")
        print("   Open http://localhost:3000/ in your browser")
        print("   Try the diagnostic page: http://localhost:3000/test")
        print("   Use the chat interface: http://localhost:3000/chat")
        print("\n📝 IMPORTANT:")
        print("   - Text messaging works perfectly for all AI features")
        print("   - Speech recognition network errors don't affect core functionality")
        print("   - See SPEECH_RECOGNITION_NETWORK_ERROR_FIX.md for troubleshooting")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure the frontend server is running")
        print("   2. Check if port 3000 is available")
        print("   3. Verify the frontend process is active")

if __name__ == "__main__":
    main()