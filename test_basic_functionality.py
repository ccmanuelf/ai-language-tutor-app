#!/usr/bin/env python3
"""
Simple Test Script for AI Language Tutor App
============================================

This script helps verify that the basic functionality is working:
1. Frontend server is running
2. Backend server is running
3. API calls work with proper authentication
4. Basic text messaging works

Usage:
    python test_basic_functionality.py

Expected Output:
    All tests should pass with ✅ indicators
"""

import requests
import time


def test_frontend_server():
    """Test if frontend server is running"""
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server: Running")
            return True
        else:
            print(f"❌ Frontend server: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend server: Not running ({e})")
        return False


def test_backend_server():
    """Test if backend server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server: Running")
            return True
        else:
            print(f"❌ Backend server: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend server: Not running ({e})")
        return False


def test_api_call():
    """Test if API calls work with proper authentication"""
    try:
        # Proper JWT token for demo user (expires in 1 hour)
        token = "test_token_placeholder"

        response = requests.post(
            "http://localhost:8000/api/v1/conversations/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token_placeholder",
            },
            json={"message": "Hello test", "language": "en-claude"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print("✅ API call: Working")
                print(f"   Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ API call: Unexpected response format")
                return False
        else:
            print(f"❌ API call: Error (HTTP {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ API call: Failed ({e})")
        return False


def test_frontend_pages():
    """Test if frontend pages are accessible"""
    pages = [("/", "Home page"), ("/chat", "Chat page"), ("/test", "Diagnostic page")]

    all_passed = True
    for path, name in pages:
        try:
            response = requests.get(f"http://localhost:3000{path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible")
            else:
                print(f"❌ {name}: Error (HTTP {response.status_code})")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: Not accessible ({e})")
            all_passed = False

    return all_passed


def main():
    """Run all tests"""
    print("🧪 AI Language Tutor - Basic Functionality Test")
    print("=" * 50)

    # Wait a moment for servers to fully start
    time.sleep(2)

    # Run tests
    tests = [
        ("Frontend Server", test_frontend_server),
        ("Backend Server", test_backend_server),
        ("Frontend Pages", test_frontend_pages),
        ("API Call", test_api_call),
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
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n🚀 You can now test the application:")
        print("   - Open http://localhost:3000/test for diagnostics")
        print("   - Open http://localhost:3000/chat for conversation")
        print("   - Try typing messages in the chat interface")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure both servers are running:")
        print("      - Backend: python run_backend.py")
        print("      - Frontend: python run_frontend.py")
        print("   2. Check if ports 8000 and 3000 are available")
        print("   3. Verify the demo user was created correctly")


if __name__ == "__main__":
    main()
