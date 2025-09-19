#!/usr/bin/env python3
"""
Comprehensive Frontend Test Script
Tests all frontend functionality including authentication, chat, and speech
"""

import requests
import json
import base64
import numpy as np
import wave
import io
from datetime import datetime

def create_test_audio():
    """Create a simple test audio file"""
    # Generate 1 second of test tone at 440Hz (A4) at 16kHz
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    # Get the WAV data
    buffer.seek(0)
    return buffer.read()

def test_authentication():
    """Test user authentication"""
    print("=" * 50)
    print("1. TESTING AUTHENTICATION")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Try to register first (in case user doesn't exist)
    print("Attempting to register demo user...")
    register_data = {
        "user_id": "demo-user",
        "username": "Demo User",
        "email": "demo@example.com",
        "role": "child"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(register_data),
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Demo user registered successfully")
            token = response.json()["access_token"]
            print(f"   Access token obtained: {token[:20]}...")
            return token
        else:
            print(f"   Registration response: {response.status_code}")
            # Try to login instead
            print("Attempting to login...")
            login_data = {
                "user_id": "demo-user",
                "password": ""
            }
            
            response = requests.post(
                f"{base_url}/api/v1/auth/login",
                headers={"Content-Type": "application/json"},
                data=json.dumps(login_data),
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Demo user logged in successfully")
                token = response.json()["access_token"]
                print(f"   Access token obtained: {token[:20]}...")
                return token
            else:
                print(f"❌ Login failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on port 8000.")
        return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_chat_functionality(token):
    """Test chat functionality"""
    print("\n" + "=" * 50)
    print("2. TESTING CHAT FUNCTIONALITY")
    print("=" * 50)
    
    if not token:
        print("❌ Skipping chat test - no authentication token")
        return False
    
    base_url = "http://localhost:8000"
    
    # Test simple text chat
    print("Testing text chat...")
    chat_data = {
        "message": "Hello, this is a test message",
        "language": "en-claude",
        "use_speech": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/conversations/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps(chat_data),
            timeout=30
        )
        
        print(f"   Chat response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chat response received: {result.get('response', 'N/A')[:50]}...")
            return True
        else:
            print(f"   ❌ Chat failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat error: {e}")
        return False

def test_speech_to_text(token):
    """Test speech-to-text functionality"""
    print("\n" + "=" * 50)
    print("3. TESTING SPEECH-TO-TEXT")
    print("=" * 50)
    
    if not token:
        print("❌ Skipping speech test - no authentication token")
        return False
    
    base_url = "http://localhost:8000"
    
    # Create test audio
    print("Creating test audio...")
    test_audio = create_test_audio()
    print(f"   Created test audio: {len(test_audio)} bytes")
    
    # Encode as base64
    audio_base64 = base64.b64encode(test_audio).decode('utf-8')
    print("   Encoded audio as base64")
    
    # Test speech-to-text endpoint
    print("Testing speech-to-text...")
    stt_data = {
        "audio_data": audio_base64,
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/conversations/speech-to-text",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps(stt_data),
            timeout=30
        )
        
        print(f"   Speech-to-text response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Speech-to-text successful")
            print(f"   Transcript: '{result.get('text', 'N/A')}'")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            return True
        else:
            print(f"   ❌ Speech-to-text failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Speech-to-text error: {e}")
        return False

def test_text_to_speech(token):
    """Test text-to-speech functionality"""
    print("\n" + "=" * 50)
    print("4. TESTING TEXT-TO-SPEECH")
    print("=" * 50)
    
    if not token:
        print("❌ Skipping TTS test - no authentication token")
        return False
    
    base_url = "http://localhost:8000"
    
    # Test text-to-speech endpoint
    print("Testing text-to-speech...")
    tts_data = {
        "text": "Hello, this is a test of the text-to-speech functionality.",
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/conversations/text-to-speech",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps(tts_data),
            timeout=30
        )
        
        print(f"   Text-to-speech response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Text-to-speech successful")
            print(f"   Audio format: {result.get('audio_format', 'N/A')}")
            print(f"   Sample rate: {result.get('sample_rate', 'N/A')} Hz")
            print(f"   Duration: {result.get('duration', 'N/A')} seconds")
            print(f"   Audio data size: {len(result.get('audio_data', ''))} characters")
            return True
        else:
            print(f"   ❌ Text-to-speech failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Text-to-speech error: {e}")
        return False

def test_frontend_pages():
    """Test if frontend pages are accessible"""
    print("\n" + "=" * 50)
    print("5. TESTING FRONTEND PAGE ACCESS")
    print("=" * 50)
    
    frontend_url = "http://localhost:3000"
    pages = [
        ("/", "Home Page"),
        ("/test", "Diagnostic Page"),
        ("/chat", "Chat Page")
    ]
    
    results = []
    for path, name in pages:
        try:
            response = requests.get(f"{frontend_url}{path}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} is accessible")
                results.append(True)
            else:
                print(f"   ❌ {name} returned status {response.status_code}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {name} is not accessible (connection refused)")
            results.append(False)
        except Exception as e:
            print(f"   ❌ {name} error: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Run comprehensive frontend tests"""
    print("🤖 AI Language Tutor - Comprehensive Frontend Test")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test frontend page access
    frontend_accessible = test_frontend_pages()
    
    # Test authentication
    token = test_authentication()
    
    # Test chat functionality
    chat_works = test_chat_functionality(token) if token else False
    
    # Test speech-to-text
    speech_works = test_speech_to_text(token) if token else False
    
    # Test text-to-speech
    tts_works = test_text_to_speech(token) if token else False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    results = [
        ("Frontend Pages Accessible", frontend_accessible),
        ("Authentication", token is not None),
        ("Chat Functionality", chat_works),
        ("Speech-to-Text", speech_works),
        ("Text-to-Speech", tts_works)
    ]
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The frontend is working correctly.")
        print("\n📝 To use the application:")
        print("   1. Open your browser and go to http://localhost:3000/chat")
        print("   2. The microphone button should work without hanging")
        print("   3. Speech should be processed correctly")
        print("   4. AI responses will be played back as audio")
    else:
        print("\n⚠️  Some tests failed. Troubleshooting steps:")
        if not frontend_accessible:
            print("   - Make sure the frontend server is running on port 3000")
        if not token:
            print("   - Check backend server is running on port 8000")
            print("   - Verify database connectivity")
        if not chat_works:
            print("   - Check backend API endpoints")
        if not speech_works:
            print("   - Verify Watson credentials in .env file")
            print("   - Check network connectivity to Watson services")
        if not tts_works:
            print("   - Verify Watson TTS credentials")
            print("   - Check text-to-speech endpoint implementation")

if __name__ == "__main__":
    main()