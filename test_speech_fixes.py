#!/usr/bin/env python3
"""
Test script to verify the fixes for speech processing errors
"""

import asyncio
import logging
import numpy as np
from app.services.speech_processor import SpeechProcessor, AudioFormat

# Set up logging to see detailed messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_noise_reduction_fix():
    """Test that noise reduction handles read-only arrays properly"""
    print("Testing noise reduction fix...")
    
    processor = SpeechProcessor()
    
    # Create test audio data
    test_audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16).tobytes()
    
    # Test noise reduction
    try:
        result = processor._reduce_noise(test_audio)
        print("✅ Noise reduction completed successfully")
        return True
    except Exception as e:
        print(f"❌ Noise reduction failed: {e}")
        return False

async def test_audio_normalization_fix():
    """Test that audio normalization handles read-only arrays properly"""
    print("Testing audio normalization fix...")
    
    processor = SpeechProcessor()
    
    # Create test audio data
    test_audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16).tobytes()
    
    # Test normalization
    try:
        result = processor._normalize_audio(test_audio)
        print("✅ Audio normalization completed successfully")
        return True
    except Exception as e:
        print(f"❌ Audio normalization failed: {e}")
        return False

async def test_empty_audio_handling():
    """Test that functions handle empty audio properly"""
    print("Testing empty audio handling...")
    
    processor = SpeechProcessor()
    
    # Test with empty audio
    try:
        result = processor._reduce_noise(b"")
        result = processor._normalize_audio(b"")
        result = processor._apply_speech_enhancement(b"")
        print("✅ Empty audio handling completed successfully")
        return True
    except Exception as e:
        print(f"❌ Empty audio handling failed: {e}")
        return False

async def test_wav_format_conversion():
    """Test WAV format conversion"""
    print("Testing WAV format conversion...")
    
    processor = SpeechProcessor()
    
    # Create test audio data
    test_audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16).tobytes()
    
    # Test WAV format conversion
    try:
        result = await processor._ensure_proper_wav_format(test_audio)
        print("✅ WAV format conversion completed successfully")
        return True
    except Exception as e:
        print(f"❌ WAV format conversion failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Testing fixes for speech processing errors")
    print("=" * 50)
    
    tests = [
        test_noise_reduction_fix,
        test_audio_normalization_fix,
        test_empty_audio_handling,
        test_wav_format_conversion
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
        print("🎉 All fixes are working correctly!")
    else:
        print("⚠️  Some fixes need attention")

if __name__ == "__main__":
    asyncio.run(main())