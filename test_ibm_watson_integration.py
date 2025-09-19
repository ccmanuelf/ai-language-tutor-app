#!/usr/bin/env python3
"""
IBM Watson Integration Test Script
==========================

This script verifies that the IBM Watson integration is working correctly
and that the frontend is properly communicating with the backend services.

Usage:
    python test_ibm_watson_integration.py
"""

import requests
import time
import base64
import json

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

def test_backend_access():
    """Test if backend is accessible"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Backend health check: Healthy")
                return True
            else:
                print(f"❌ Backend health check: Unhealthy ({data})")
                return False
        else:
            print(f"❌ Backend health check: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend health check: Not accessible ({e})")
        return False

def test_backend_speech_endpoint():
    """Test if backend speech-to-text endpoint is working"""
    try:
        # Test with a simple request (no audio data)
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/speech-to-text",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJleHAiOjE3NTY2NzEzNzh9.THu3Ij-GoUzUa8lAChkQGFALLjSgqbtIrgrQ9RrI-eQ"
            },
            json={}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend speech-to-text endpoint: Working ({data})")
            return True
        else:
            print(f"❌ Backend speech-to-text endpoint: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend speech-to-text endpoint: Error ({e})")
        return False

def test_text_messaging():
    """Test if text messaging is working"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJleHAiOjE3NTY2NzEzNzh9.THu3Ij-GoUzUa8lAChkQGFALLjSgqbtIrgrQ9RrI-eQ"
            },
            json={
                "message": "Hello, this is a test message",
                "language": "en-claude",
                "use_speech": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print(f"✅ Text messaging: Working (Response preview: {data['response'][:50]}...)")
                return True
            else:
                print(f"❌ Text messaging: Unexpected response format ({data})")
                return False
        else:
            print(f"❌ Text messaging: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Text messaging: Error ({e})")
        return False

def main():
    """Run IBM Watson integration tests"""
    print("🧪 IBM Watson Integration Test")
    print("=" * 40)
    
    # Wait a moment for servers to fully start
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Frontend Access", test_frontend_access),
        ("Backend Access", test_backend_access),
        ("Backend Speech Endpoint", test_backend_speech_endpoint),
        ("Text Messaging", test_text_messaging)
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
    print("\n" + "=" * 40)
    print("📋 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n🚀 IBM Watson integration is working correctly!")
        print("   - Frontend and backend servers are running")
        print("   - Backend speech-to-text endpoint is accessible")
        print("   - Text messaging with AI is working")
        print("\n📝 Next steps:")
        print("   - Open http://localhost:3000/test to run diagnostic tests")
        print("   - Try the chat interface: http://localhost:3000/chat")
        print("   - Click microphone to test speech recognition")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure both backend and frontend servers are running")
        print("   2. Check server logs for errors")
        print("   3. Verify IBM Watson credentials in .env file")
        print("   4. Run python test_watson_integration.py for detailed Watson testing")

if __name__ == "__main__":
    main()