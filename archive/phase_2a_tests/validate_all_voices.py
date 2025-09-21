#!/usr/bin/env python3
"""
Comprehensive validation test for all Piper TTS voices
Tests audio generation, quality, and language-specific functionality
"""

import asyncio
import sys
import os
from pathlib import Path
import wave
import tempfile

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService
from services.speech_processor import SpeechProcessor


async def test_voice_synthesis(piper_service, language, text_sample):
    """Test voice synthesis for a specific language"""
    print(f"\n🎯 Testing {language.upper()} voice synthesis...")

    try:
        # Get voice for language
        voice_name = piper_service.get_voice_for_language(language)
        if not voice_name:
            print(f"  ❌ No voice available for {language}")
            return False

        print(f"  📢 Using voice: {voice_name}")

        # Synthesize audio
        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=text_sample, language=language
        )

        if not audio_bytes:
            print(f"  ❌ No audio generated for {language}")
            return False

        # Save test file
        test_file = f"test_{language}_voice.wav"
        with open(test_file, "wb") as f:
            f.write(audio_bytes)

        # Validate WAV file
        try:
            with wave.open(test_file, "rb") as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / sample_rate

                print(
                    f"  ✅ Audio generated: {duration:.2f}s, {sample_rate}Hz, {len(audio_bytes)} bytes"
                )

                if duration < 0.5:
                    print(f"  ⚠️  Warning: Very short audio duration")

                return True

        except Exception as e:
            print(f"  ❌ Invalid WAV file: {e}")
            return False

    except Exception as e:
        print(f"  ❌ Synthesis failed: {e}")
        return False
    finally:
        # Cleanup test file
        if os.path.exists(f"test_{language}_voice.wav"):
            os.remove(f"test_{language}_voice.wav")


async def test_speech_processor_integration(speech_processor, language, text_sample):
    """Test integration with speech processor"""
    print(f"\n🔄 Testing {language.upper()} speech processor integration...")

    try:
        result = await speech_processor.process_text_to_speech(
            text=text_sample,
            language=language,
            voice_type="standard",
            speaking_rate=1.0,
            provider="piper",
        )

        if result.audio_data and len(result.audio_data) > 0:
            provider = result.metadata.get("provider", "unknown")
            print(f"  ✅ Speech processor integration successful")
            print(
                f"  📊 Provider: {provider}, Duration: {result.duration_seconds:.2f}s"
            )
            return True
        else:
            print(f"  ❌ Speech processor integration failed")
            return False

    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False


async def main():
    """Run comprehensive validation tests"""
    print("🚀 Starting comprehensive Piper TTS validation...")

    # Test samples for each language
    test_samples = {
        "en": "Hello! Welcome to our AI language learning platform.",
        "es": "¡Hola! Bienvenido a nuestra plataforma de aprendizaje de idiomas.",
        "fr": "Bonjour! Bienvenue sur notre plateforme d'apprentissage des langues.",
        "de": "Hallo! Willkommen auf unserer Sprachlernplattform.",
        "it": "Ciao! Benvenuto nella nostra piattaforma di apprendimento linguistico.",
        "pt": "Olá! Bem-vindo à nossa plataforma de aprendizado de idiomas.",
    }

    # Initialize services
    print("\n🔧 Initializing services...")
    piper_service = PiperTTSService()
    speech_processor = SpeechProcessor()

    # Check available voices
    available_voices = piper_service.get_available_voices()
    print(f"📋 Available voices: {len(available_voices)}")
    for voice in available_voices:
        print(f"  - {voice}")

    # Test each language
    results = {}
    for language, text_sample in test_samples.items():
        print(f"\n{'=' * 60}")
        print(f"🌍 TESTING LANGUAGE: {language.upper()}")
        print(f"{'=' * 60}")

        # Test direct voice synthesis
        synthesis_success = await test_voice_synthesis(
            piper_service, language, text_sample
        )

        # Test speech processor integration
        integration_success = await test_speech_processor_integration(
            speech_processor, language, text_sample
        )

        results[language] = {
            "synthesis": synthesis_success,
            "integration": integration_success,
            "overall": synthesis_success and integration_success,
        }

    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'=' * 60}")

    total_tests = len(test_samples)
    passed_synthesis = sum(1 for r in results.values() if r["synthesis"])
    passed_integration = sum(1 for r in results.values() if r["integration"])
    passed_overall = sum(1 for r in results.values() if r["overall"])

    print(f"Direct Synthesis Tests: {passed_synthesis}/{total_tests} passed")
    print(f"Integration Tests: {passed_integration}/{total_tests} passed")
    print(
        f"Overall Success Rate: {passed_overall}/{total_tests} ({passed_overall / total_tests * 100:.1f}%)"
    )

    # Detailed results
    print(f"\n📋 Detailed Results:")
    for language, result in results.items():
        status = "✅ PASS" if result["overall"] else "❌ FAIL"
        print(f"  {language.upper()}: {status}")
        if not result["synthesis"]:
            print(f"    - Synthesis failed")
        if not result["integration"]:
            print(f"    - Integration failed")

    # Special note about Spanish voice update
    if results.get("es", {}).get("overall"):
        print(
            f"\n🎉 Spanish voice successfully updated to Mexican accent (es_MX-claude-high)"
        )

    print(f"\n🎯 Task 2A.2 (Local TTS Implementation) validation complete!")

    if passed_overall == total_tests:
        print("✅ All tests passed - Ready for production!")
        return True
    else:
        print("⚠️  Some tests failed - Review required")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
