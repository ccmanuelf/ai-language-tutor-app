#!/usr/bin/env python3
"""
Comprehensive Functionality Test Script
==========================

This script verifies that all functionality of the AI Language Tutor is working correctly
with the clean frontend implementation that properly integrates with IBM Watson services.

Usage:
    python test_comprehensive_functionality.py
"""

import requests
import time
import subprocess
import os

# Get a valid JWT token
def get_valid_token():
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json={"user_id": "demo-user", "password": ""}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Failed to get token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

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

def test_backend_speech_endpoint(token):
    """Test if backend speech-to-text endpoint is working"""
    try:
        # Test with a simple request (no audio data)
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/speech-to-text",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend speech-to-text endpoint: Working ({data.get('text', 'No text')})")
            return True
        else:
            print(f"❌ Backend speech-to-text endpoint: Error (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend speech-to-text endpoint: Error ({e})")
        return False

def test_text_messaging(token):
    """Test if text messaging is working"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
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

def test_frontend_compilation():
    """Test if frontend compiles without errors"""
    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", "app/frontend_main.py"],
            cwd="/Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Frontend compilation: No syntax errors")
            return True
        else:
            print(f"❌ Frontend compilation: Errors found ({result.stderr})")
            return False
    except Exception as e:
        print(f"❌ Frontend compilation test: Error ({e})")
        return False

def main():
    """Run comprehensive functionality tests"""
    print("🧪 COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Wait a moment for servers to fully start
    time.sleep(2)
    
    # Get a valid JWT token
    print("🔑 Getting authentication token...")
    token = get_valid_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    print("✅ Authentication token obtained")
    
    # Run tests
    tests = [
        ("Frontend Compilation", lambda: test_frontend_compilation()),
        ("Frontend Access", lambda: test_frontend_access()),
        ("Backend Access", lambda: test_backend_access()),
        ("Diagnostic Page", lambda: test_diagnostic_page()),
        ("Chat Page", lambda: test_chat_page()),
        ("Backend Speech Endpoint", lambda: test_backend_speech_endpoint(token)),
        ("Text Messaging", lambda: test_text_messaging(token))
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
        print("\n🚀 AI Language Tutor is fully functional!")
        print("   - Frontend and backend servers are running")
        print("   - Clean frontend implementation with no syntax errors")
        print("   - Backend speech-to-text endpoint is accessible")
        print("   - Text messaging with AI is working")
        print("   - Diagnostic and chat pages are accessible")
        print("\n📝 Next steps:")
        print("   - Open http://localhost:3000/test to run diagnostic tests")
        print("   - Try the chat interface: http://localhost:3000/chat")
        print("   - Click microphone to test speech recognition")
        print("   - Test all languages: English, Spanish, French, Chinese, Japanese")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check server logs for errors")
        print("   2. Verify IBM Watson credentials in .env file")
        print("   3. Ensure all required services are running")
        print("   4. Check network connectivity")

if __name__ == "__main__":
    main()