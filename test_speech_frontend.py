#!/usr/bin/env python3
"""
Test script to verify frontend speech functionality
"""

import asyncio
import base64
import json
import requests
import time

def test_frontend_speech_endpoint():
    """Test the frontend speech-to-text endpoint"""
    print("🎙️  Testing frontend speech functionality...")
    
    # First, let's try to get an auth token
    try:
        login_data = {
            "user_id": "demo-user",
            "password": ""
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps(login_data)
        )
        
        if response.status_code != 200:
            print(f"⚠️  Failed to get auth token: {response.status_code}")
            print(response.text)
            # Let's try to register a demo user first
            register_data = {
                "user_id": "demo-user",
                "username": "Demo User",
                "email": "demo@example.com",
                "role": "child"
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/auth/register",
                headers={"Content-Type": "application/json"},
                data=json.dumps(register_data)
            )
            
            if response.status_code != 200:
                print(f"⚠️  Failed to register demo user: {response.status_code}")
                print(response.text)
                return False
                
            # Now try to login again
            response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                headers={"Content-Type": "application/json"},
                data=json.dumps(login_data)
            )
            
            if response.status_code != 200:
                print(f"⚠️  Failed to get auth token after registration: {response.status_code}")
                print(response.text)
                return False
        
        token = response.json()["access_token"]
        print(f"✅ Got auth token: {token[:10]}...")
        
    except Exception as e:
        print(f"❌ Failed to get auth token: {e}")
        return False
    
    # Create a simple WAV audio file (silence)
    try:
        import wave
        import numpy as np
        
        # Generate 1 second of silence at 16kHz
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.zeros_like(t)
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Create WAV file in memory
        import io
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        
        # Get the WAV data
        buffer.seek(0)
        wav_data = buffer.read()
        print(f"✅ Generated test audio: {len(wav_data)} bytes")
        
    except Exception as e:
        print(f"❌ Failed to generate test audio: {e}")
        return False
    
    # Encode as base64
    try:
        audio_base64 = base64.b64encode(wav_data).decode('utf-8')
        print("✅ Encoded audio as base64")
    except Exception as e:
        print(f"❌ Failed to encode audio: {e}")
        return False
    
    # Test speech-to-text endpoint
    try:
        stt_data = {
            "audio_data": audio_base64,
            "language": "en"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/speech-to-text",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps(stt_data)
        )
        
        print(f"✅ Speech-to-text response status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Transcript: '{result.get('text', 'N/A')}'")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            return True
        else:
            print(f"⚠️  Speech-to-text failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test speech-to-text: {e}")
        return False

def check_frontend_availability():
    """Check if the frontend is available"""
    print("\n🌐 Checking frontend availability...")
    
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend is not accessible: {e}")
        return False

def main():
    """Run frontend speech tests"""
    print(" Frontend Speech Functionality Test")
    print("=" * 50)
    
    # Check if frontend is running
    if not check_frontend_availability():
        print("\n⚠️  Frontend is not running. Please start it with:")
        print("   python run_frontend.py")
        return
    
    # Test speech functionality
    success = test_frontend_speech_endpoint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Frontend speech functionality test completed successfully!")
        print("\nTo test the full voice interaction:")
        print("1. Make sure both backend and frontend servers are running")
        print("2. Open your browser to http://localhost:3000/chat")
        print("3. Try clicking the microphone button")
        print("4. The system should now properly process your speech")
    else:
        print("❌ Frontend speech functionality test failed")
        print("\nTroubleshooting steps:")
        print("1. Check that Watson credentials in .env are correct")
        print("2. Verify network connectivity to Watson services")
        print("3. Check server logs for detailed error messages")

if __name__ == "__main__":
    main()