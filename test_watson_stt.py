#!/usr/bin/env python3
"""
Test script for Watson Speech-to-Text service
"""

import wave
import numpy as np
import io
import base64
import requests
import json

def create_test_audio():
    """Create a simple test audio file with spoken text"""
    # Generate a simple sine wave as test audio
    sample_rate = 16000
    duration = 2.0  # seconds
    frequency = 440.0  # Hz (A4 note)
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit integers
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    # Get the WAV data
    buffer.seek(0)
    return buffer.read()

def test_watson_stt():
    """Test Watson Speech-to-Text service"""
    # Create test audio
    audio_data = create_test_audio()
    print(f"Generated audio data size: {len(audio_data)} bytes")
    
    # Encode as base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Get auth token
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
        print(f"Failed to get auth token: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    print(f"Got auth token: {token[:10]}...")
    
    # Test speech-to-text
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
    
    print(f"STT Response Status: {response.status_code}")
    print(f"STT Response: {response.text}")

if __name__ == "__main__":
    test_watson_stt()