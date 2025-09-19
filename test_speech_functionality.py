#!/usr/bin/env python3
"""
Test script to verify speech functionality with proper authentication
"""

import requests
import json
import base64
import numpy as np
import wave
import io

def create_test_audio():
    """Create a simple test audio file"""
    # Generate 1 second of silence at 16kHz
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.zeros_like(t)
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

def test_speech_functionality():
    """Test speech-to-text functionality with proper authentication"""
    base_url = "http://localhost:8000"
    
    # First, login to get auth token
    print("Logging in...")
    login_data = {
        "user_id": "demo-user",
        "password": ""
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps(login_data)
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed with status {response.status_code}")
            print(response.text)
            return
            
        token = response.json()["access_token"]
        print(f"✅ Logged in successfully")
        print(f"Access token: {token[:20]}...")
        
        # Create test audio
        print("\nCreating test audio...")
        test_audio = create_test_audio()
        print(f"✅ Created test audio: {len(test_audio)} bytes")
        
        # Encode as base64
        audio_base64 = base64.b64encode(test_audio).decode('utf-8')
        print("✅ Encoded audio as base64")
        
        # Test speech-to-text endpoint
        print("\nTesting speech-to-text...")
        stt_data = {
            "audio_data": audio_base64,
            "language": "en"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/conversations/speech-to-text",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps(stt_data)
        )
        
        print(f"✅ Speech-to-text response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Transcript: '{result.get('text', 'N/A')}'")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print("🎉 Speech functionality is working!")
        else:
            print(f"❌ Speech-to-text failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_speech_functionality()