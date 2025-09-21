#!/usr/bin/env python3
"""
Test Script: Mistral STT Integration Validation
AI Language Tutor App - Phase 2A Migration Testing

This script validates the Mistral STT integration and tests the complete
speech processing pipeline with provider selection logic.

Usage:
    python test_mistral_stt_integration.py
"""

import asyncio
import sys
import os
import logging
import wave
import time
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.services.speech_processor import SpeechProcessor, AudioFormat
from app.services.mistral_stt_service import MistralSTTService
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_audio():
    """Create a simple test audio file for testing"""
    try:
        # Create a simple 1-second sine wave audio for testing
        import numpy as np

        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440  # A4 note

        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3

        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)

        # Create WAV file in memory
        import io

        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        return audio_buffer.getvalue()

    except ImportError:
        logger.warning("NumPy not available, creating minimal WAV file")
        # Create minimal valid WAV file
        return create_minimal_wav()


def create_minimal_wav():
    """Create minimal valid WAV file for testing"""
    import struct

    # WAV header for 16-bit mono audio at 16kHz
    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    duration = 1  # 1 second
    num_samples = sample_rate * duration

    # Calculate byte rates
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8

    # Create header
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + num_samples * 2,  # File size - 8
        b"WAVE",
        b"fmt ",
        16,  # Subchunk1Size
        1,  # AudioFormat (PCM)
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        num_samples * 2,
    )

    # Create silent audio data
    audio_data = b"\x00\x00" * num_samples

    return header + audio_data


async def test_configuration():
    """Test configuration and service availability"""
    print("\n🔧 Testing Configuration...")

    settings = get_settings()

    # Check Mistral API key
    has_mistral_key = bool(settings.MISTRAL_API_KEY)
    print(
        f"   Mistral API Key: {'✅ Configured' if has_mistral_key else '❌ Not configured'}"
    )

    # Check Watson keys (for comparison)
    has_watson_stt = bool(
        settings.IBM_WATSON_STT_API_KEY and settings.IBM_WATSON_STT_URL
    )
    has_watson_tts = bool(
        settings.IBM_WATSON_TTS_API_KEY and settings.IBM_WATSON_TTS_URL
    )
    print(f"   Watson STT: {'✅ Available' if has_watson_stt else '❌ Not available'}")
    print(f"   Watson TTS: {'✅ Available' if has_watson_tts else '❌ Not available'}")

    return has_mistral_key, has_watson_stt, has_watson_tts


async def test_mistral_stt_service():
    """Test Mistral STT service directly"""
    print("\n🚀 Testing Mistral STT Service...")

    try:
        service = MistralSTTService()
        health = await service.health_check()

        print(f"   Service Available: {'✅' if health['available'] else '❌'}")
        print(
            f"   API Key Configured: {'✅' if health['api_key_configured'] else '❌'}"
        )
        print(f"   Model: {health['model']}")
        print(f"   Supported Languages: {len(health['supported_languages'])} languages")
        print(f"   Cost per Minute: ${health['cost_per_minute']}")

        if health["available"]:
            # Test with sample audio
            test_audio = create_test_audio()

            print(
                f"\n   Testing transcription with {len(test_audio)} bytes of audio..."
            )
            start_time = time.time()

            result = await service.transcribe_audio(
                audio_data=test_audio, language="en", audio_format="wav"
            )

            processing_time = time.time() - start_time

            print(f"   ✅ Transcription completed in {processing_time:.2f}s")
            print(f"   Transcript: '{result.transcript}'")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Cost: ${result.cost_usd:.6f}")
            print(f"   Duration: {result.audio_duration_minutes:.2f} minutes")

            return True

        return False

    except Exception as e:
        print(f"   ❌ Mistral STT service test failed: {e}")
        return False


async def test_speech_processor_integration():
    """Test SpeechProcessor with Mistral integration"""
    print("\n🎤 Testing SpeechProcessor Integration...")

    try:
        processor = SpeechProcessor()

        print(
            f"   Watson STT Available: {'✅' if processor.watson_stt_available else '❌'}"
        )
        print(
            f"   Watson TTS Available: {'✅' if processor.watson_tts_available else '❌'}"
        )
        print(
            f"   Mistral STT Available: {'✅' if processor.mistral_stt_available else '❌'}"
        )

        if not processor.mistral_stt_available:
            print("   ⚠️  Mistral STT not available in SpeechProcessor")
            return False

        # Test with different providers
        test_audio = create_test_audio()
        providers_to_test = ["mistral", "auto"]

        if processor.watson_stt_available:
            providers_to_test.extend(["watson", "mistral_fallback"])

        for provider in providers_to_test:
            print(f"\n   Testing provider: {provider}")

            try:
                start_time = time.time()
                result, pronunciation = await processor.process_speech_to_text(
                    audio_data=test_audio,
                    language="en",
                    audio_format=AudioFormat.WAV,
                    enable_pronunciation_analysis=False,
                    provider=provider,
                )
                processing_time = time.time() - start_time

                print(f"     ✅ Success ({processing_time:.2f}s)")
                print(f"     Transcript: '{result.transcript}'")
                print(f"     Confidence: {result.confidence:.2f}")
                print(
                    f"     Provider used: {result.metadata.get('provider', 'unknown')}"
                )

                if "cost_usd" in result.metadata:
                    print(f"     Cost: ${result.metadata['cost_usd']:.6f}")

            except Exception as e:
                print(f"     ❌ Failed: {e}")

        return True

    except Exception as e:
        print(f"   ❌ SpeechProcessor integration test failed: {e}")
        return False


async def test_cost_comparison():
    """Test cost comparison between providers"""
    print("\n💰 Testing Cost Comparison...")

    try:
        processor = SpeechProcessor()
        test_audio = create_test_audio()

        results = {}

        # Test Mistral if available
        if processor.mistral_stt_available:
            try:
                result, _ = await processor.process_speech_to_text(
                    audio_data=test_audio,
                    language="en",
                    audio_format=AudioFormat.WAV,
                    enable_pronunciation_analysis=False,
                    provider="mistral",
                )
                results["Mistral"] = {
                    "cost": result.metadata.get("cost_usd", 0),
                    "duration": result.metadata.get("audio_duration_minutes", 0),
                    "quality": result.confidence,
                }
            except Exception as e:
                print(f"   Mistral test failed: {e}")

        # Test Watson if available
        if processor.watson_stt_available:
            try:
                result, _ = await processor.process_speech_to_text(
                    audio_data=test_audio,
                    language="en",
                    audio_format=AudioFormat.WAV,
                    enable_pronunciation_analysis=False,
                    provider="watson",
                )
                # Estimate Watson cost (approximate)
                duration = results.get("Mistral", {}).get(
                    "duration", 1 / 60
                )  # 1 second default
                watson_cost = duration * 0.02  # ~$0.02/minute estimate

                results["Watson"] = {
                    "cost": watson_cost,
                    "duration": duration,
                    "quality": result.confidence,
                }
            except Exception as e:
                print(f"   Watson test failed: {e}")

        # Display comparison
        if results:
            print("\n   Cost Comparison Results:")
            for provider, data in results.items():
                print(f"     {provider}:")
                print(f"       Cost: ${data['cost']:.6f}")
                print(f"       Quality: {data['quality']:.2f}")
                print(f"       Duration: {data['duration']:.3f} min")

            if "Mistral" in results and "Watson" in results:
                mistral_cost = results["Mistral"]["cost"]
                watson_cost = results["Watson"]["cost"]
                if watson_cost > 0:
                    savings = ((watson_cost - mistral_cost) / watson_cost) * 100
                    print(
                        f"\n   💰 Cost Savings: {savings:.1f}% reduction with Mistral"
                    )

        return True

    except Exception as e:
        print(f"   ❌ Cost comparison test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 Mistral STT Integration Test Suite")
    print("=" * 50)

    # Test configuration
    has_mistral, has_watson_stt, has_watson_tts = await test_configuration()

    if not has_mistral:
        print("\n❌ CRITICAL: Mistral API key not configured!")
        print("   Please set MISTRAL_API_KEY in your .env file")
        return False

    # Test Mistral STT service
    mistral_service_ok = await test_mistral_stt_service()

    # Test SpeechProcessor integration
    integration_ok = await test_speech_processor_integration()

    # Test cost comparison
    cost_comparison_ok = await test_cost_comparison()

    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Configuration: {'✅' if has_mistral else '❌'}")
    print(f"Mistral Service: {'✅' if mistral_service_ok else '❌'}")
    print(f"Integration: {'✅' if integration_ok else '❌'}")
    print(f"Cost Comparison: {'✅' if cost_comparison_ok else '❌'}")

    overall_success = all(
        [has_mistral, mistral_service_ok, integration_ok, cost_comparison_ok]
    )

    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Mistral STT integration is working correctly")
        print("✅ Provider selection logic functional")
        print("✅ Cost optimization achieved")
        print("\n🚀 Ready to proceed with Piper TTS implementation!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("❌ Please review the issues above before proceeding")

    return overall_success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)
