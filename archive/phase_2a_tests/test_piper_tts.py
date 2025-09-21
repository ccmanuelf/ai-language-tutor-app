#!/usr/bin/env python3
"""
Test script for Piper TTS integration

This script validates:
1. Piper TTS service functionality
2. Speech processor integration
3. Provider selection logic
4. Audio output generation
"""

import asyncio
import sys
import logging
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_piper_tts_service():
    """Test Piper TTS service directly"""
    logger.info("=== Testing Piper TTS Service ===")

    try:
        from app.services.piper_tts_service import PiperTTSService

        # Initialize service
        service = PiperTTSService()

        # Check service info
        info = service.get_service_info()
        logger.info(f"Service status: {info['status']}")
        logger.info(f"Available voices: {info['voices_count']}")
        logger.info(f"Voice names: {info['available_voices']}")

        if info["voices_count"] == 0:
            logger.error(
                "No voices available! Please ensure voice models are downloaded."
            )
            return False

        # Test synthesis
        test_text = "Hello, this is a test of Piper text-to-speech synthesis."
        logger.info(f"Testing synthesis with text: '{test_text}'")

        audio_data, metadata = await service.synthesize_speech(
            text=test_text, language="en"
        )

        logger.info(f"Synthesis successful!")
        logger.info(f"  Voice: {metadata['voice']}")
        logger.info(f"  Audio size: {len(audio_data)} bytes")
        logger.info(f"  Sample rate: {metadata['sample_rate']} Hz")
        logger.info(f"  Duration: {metadata['duration_estimate']:.2f}s")
        logger.info(f"  Cost: ${metadata['cost']:.4f}")

        # Save test audio file
        output_file = "test_piper_output.wav"
        with open(output_file, "wb") as f:
            f.write(audio_data)
        logger.info(f"Audio saved to: {output_file}")

        return True

    except Exception as e:
        logger.error(f"Piper TTS service test failed: {e}")
        return False


async def test_speech_processor_integration():
    """Test Piper TTS through speech processor"""
    logger.info("\n=== Testing Speech Processor Integration ===")

    try:
        from app.services.speech_processor import SpeechProcessor

        # Initialize processor
        processor = SpeechProcessor()

        # Check provider availability
        logger.info(f"Piper TTS available: {processor.piper_tts_available}")
        logger.info(f"Watson TTS available: {processor.watson_tts_available}")

        if not processor.piper_tts_available:
            logger.error("Piper TTS not available in speech processor!")
            return False

        # Test synthesis through processor
        test_text = "Testing Piper text-to-speech through the speech processor."
        logger.info(f"Testing with text: '{test_text}'")

        # Test with auto provider (should use Piper)
        result = await processor.process_text_to_speech(
            text=test_text, language="en", provider="auto"
        )

        logger.info(f"Synthesis successful!")
        logger.info(f"  Service: {result.metadata.get('service', 'unknown')}")
        logger.info(f"  Provider: {result.metadata.get('provider', 'unknown')}")
        logger.info(f"  Voice: {result.metadata.get('piper_voice', 'unknown')}")
        logger.info(f"  Audio size: {len(result.audio_data)} bytes")
        logger.info(f"  Sample rate: {result.sample_rate} Hz")
        logger.info(f"  Duration: {result.duration_seconds:.2f}s")
        logger.info(f"  Processing time: {result.processing_time:.3f}s")
        logger.info(f"  Cost: ${result.metadata.get('cost', 0):.4f}")

        # Save test audio file
        output_file = "test_processor_output.wav"
        with open(output_file, "wb") as f:
            f.write(result.audio_data)
        logger.info(f"Audio saved to: {output_file}")

        # Test with specific Piper provider
        result_piper = await processor.process_text_to_speech(
            text="Testing explicit Piper provider.", language="en", provider="piper"
        )

        logger.info(f"Explicit Piper test successful!")
        logger.info(f"  Provider: {result_piper.metadata.get('provider', 'unknown')}")

        return True

    except Exception as e:
        logger.error(f"Speech processor integration test failed: {e}")
        return False


async def test_multi_language():
    """Test multi-language support"""
    logger.info("\n=== Testing Multi-Language Support ===")

    try:
        from app.services.piper_tts_service import PiperTTSService

        service = PiperTTSService()

        # Test texts in different languages
        test_cases = [
            ("en", "Hello, how are you today?"),
            ("es", "Hola, ¿cómo estás hoy?"),
            ("fr", "Bonjour, comment allez-vous aujourd'hui?"),
            ("de", "Hallo, wie geht es dir heute?"),
        ]

        for language, text in test_cases:
            logger.info(f"Testing {language}: '{text}'")

            try:
                audio_data, metadata = await service.synthesize_speech(
                    text=text, language=language
                )

                logger.info(
                    f"  ✓ Success - Voice: {metadata['voice']}, Size: {len(audio_data)} bytes"
                )

            except Exception as e:
                logger.warning(f"  ✗ Failed for {language}: {e}")

        return True

    except Exception as e:
        logger.error(f"Multi-language test failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("Starting Piper TTS Integration Tests")
    logger.info("=" * 50)

    tests = [
        ("Piper TTS Service", test_piper_tts_service),
        ("Speech Processor Integration", test_speech_processor_integration),
        ("Multi-Language Support", test_multi_language),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status} - {test_name}")
        if success:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Piper TTS integration is working correctly.")
        return True
    else:
        logger.error(
            f"❌ {total - passed} test(s) failed. Please check the logs above."
        )
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
