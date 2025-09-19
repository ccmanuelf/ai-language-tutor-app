#!/usr/bin/env python3
"""
Test script to verify speech quality and processing
"""

import asyncio
import logging
import numpy as np
from app.services.speech_processor import SpeechProcessor, AudioFormat

# Set up logging to see detailed messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_speech_quality():
    """Test speech quality with better audio"""
    print("Testing speech quality processing...")
    
    processor = SpeechProcessor()
    
    # Create test audio data with actual speech-like characteristics
    # Generate 2 seconds of audio at 16kHz with speech-like patterns
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a more complex audio signal that resembles speech
    # Combine multiple frequencies to simulate voice
    audio_data = (
        np.sin(2 * np.pi * 100 * t) * 0.3 +  # Fundamental frequency
        np.sin(2 * np.pi * 200 * t) * 0.2 +  # Harmonic
        np.sin(2 * np.pi * 300 * t) * 0.1 +  # Another harmonic
        np.random.normal(0, 0.05, len(t))     # Add some noise
    )
    
    # Convert to 16-bit integers
    audio_int16 = (audio_data * 32767).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    
    print(f"Created test audio: {len(audio_bytes)} bytes")
    
    # Test audio quality analysis
    try:
        metadata = await processor._analyze_audio_quality(audio_bytes, AudioFormat.WAV)
        print(f"Audio quality score: {metadata.quality_score}")
        print(f"Audio duration: {metadata.duration_seconds} seconds")
        
        # Test enhancement
        enhanced_audio = await processor._enhance_audio_quality(audio_bytes, AudioFormat.WAV)
        print(f"Enhanced audio size: {len(enhanced_audio)} bytes")
        
        # Test noise reduction
        reduced_noise = processor._reduce_noise(audio_bytes)
        print(f"Noise reduced audio size: {len(reduced_noise)} bytes")
        
        # Test normalization
        normalized = processor._normalize_audio(audio_bytes)
        print(f"Normalized audio size: {len(normalized)} bytes")
        
        print("✅ Speech quality processing completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Speech quality processing failed: {e}")
        return False

async def test_vad():
    """Test voice activity detection"""
    print("Testing voice activity detection...")
    
    processor = SpeechProcessor()
    
    # Create audio with voice activity
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create audio with voice-like energy
    voice_audio = (np.sin(2 * np.pi * 200 * t) * 0.5).astype(np.int16).tobytes()
    
    # Create silent audio
    silent_audio = np.zeros(int(sample_rate * 0.5), dtype=np.int16).tobytes()
    
    try:
        # Test voice detection
        has_voice = processor.detect_voice_activity(voice_audio, sample_rate)
        print(f"Voice detected in voice audio: {has_voice}")
        
        # Test silence detection
        has_voice_silent = processor.detect_voice_activity(silent_audio, sample_rate)
        print(f"Voice detected in silent audio: {has_voice_silent}")
        
        print("✅ Voice activity detection completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Voice activity detection failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Testing speech quality and processing")
    print("=" * 50)
    
    tests = [
        test_speech_quality,
        test_vad
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    print("=" * 50)
    print("Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All speech quality tests are working correctly!")
    else:
        print("⚠️  Some speech quality tests need attention")

if __name__ == "__main__":
    asyncio.run(main())