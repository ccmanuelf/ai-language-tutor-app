#!/usr/bin/env python3
"""
Generate Voice Samples for All Languages

This script generates audio samples for all available languages
so you can listen and evaluate voice quality.
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


async def generate_all_voice_samples():
    """Generate voice samples for all available languages"""

    test_phrases = {
        "en": "Hello! This is a test of English speech synthesis. The AI language tutor uses this voice for English lessons.",
        "es": "¡Hola! Esta es una prueba de síntesis de voz en español. El tutor de idiomas AI usa esta voz para lecciones en español.",
        "fr": "Bonjour! Ceci est un test de synthèse vocale française. Le tuteur de langues AI utilise cette voix pour les leçons françaises.",
        "de": "Hallo! Das ist ein Test der deutschen Sprachsynthese. Der AI Sprachtutor verwendet diese Stimme für deutsche Lektionen.",
        "it": "Ciao! Questo è un test di sintesi vocale italiana. Il tutor di lingue AI usa questa voce per le lezioni italiane.",
        "pt": "Olá! Este é um teste de síntese de voz em português. O tutor de idiomas AI usa esta voz para aulas em português.",
        "zh": "Hello! This is Chinese text spoken with English voice as fallback. We need to download Chinese voice models.",
        "ja": "Hello! This is Japanese text spoken with English voice as fallback. We need to download Japanese voice models.",
        "ko": "Hello! This is Korean text spoken with English voice as fallback. We need to download Korean voice models.",
    }

    language_names = {
        "en": "English (US)",
        "es": "Spanish (Spain)",
        "fr": "French (France)",
        "de": "German (Germany)",
        "it": "Italian (Italy)",
        "pt": "Portuguese (Brazil)",
        "zh": "Chinese (Mandarin) - English fallback",
        "ja": "Japanese - English fallback",
        "ko": "Korean - English fallback",
    }

    print("🎵 Generating Voice Samples for All Languages")
    print("=" * 60)

    try:
        from app.services.piper_tts_service import PiperTTSService

        service = PiperTTSService()

        info = service.get_service_info()
        print(f"📊 Service Status: {info['status']}")
        print(f"🗣️  Available Voices: {len(info['available_voices'])}")
        print(f"🌐 Available Languages: {len(info['supported_languages'])}")
        print(f"📁 Voices Directory: {info['voices_directory']}")
        print("")

        print("Available voice models:")
        for voice in info["available_voices"]:
            print(f"  • {voice}")
        print("")

        results = {}

        for language, phrase in test_phrases.items():
            language_name = language_names[language]

            print(f"🔊 Generating {language_name} ({language.upper()})...")
            print(f"📝 Text: {phrase[:50]}{'...' if len(phrase) > 50 else ''}")

            try:
                # Generate audio
                audio_data, metadata = await service.synthesize_speech(
                    text=phrase, language=language
                )

                # Save audio file
                filename = f"sample_voice_{language}_{metadata['voice']}.wav"
                with open(filename, "wb") as f:
                    f.write(audio_data)

                results[language] = {
                    "success": True,
                    "voice": metadata["voice"],
                    "size": len(audio_data),
                    "filename": filename,
                    "duration": metadata.get("duration_estimate", "unknown"),
                }

                print(f"  ✅ Generated: {filename}")
                print(f"  🎭 Voice: {metadata['voice']}")
                print(f"  📏 Size: {len(audio_data):,} bytes")
                print(f"  ⏱️  Duration: {metadata.get('duration_estimate', 'unknown')}s")
                print("")

            except Exception as e:
                print(f"  ❌ Failed: {e}")
                results[language] = {"success": False, "error": str(e)}
                print("")

        # Test Speech Processor Integration
        print("🔧 Testing Speech Processor Integration...")
        print("-" * 40)

        try:
            from app.services.speech_processor import SpeechProcessor

            processor = SpeechProcessor()

            # Test a few languages through speech processor
            test_languages = ["en", "es", "fr"]

            for language in test_languages:
                if language in test_phrases:
                    phrase = test_phrases[language]
                    language_name = language_names[language]

                    print(f"📡 Testing {language_name} via Speech Processor...")

                    try:
                        result = await processor.process_text_to_speech(
                            text=phrase, language=language, provider="auto"
                        )

                        filename = f"sample_processor_{language}.wav"
                        with open(filename, "wb") as f:
                            f.write(result.audio_data)

                        print(f"  ✅ Processor: {filename}")
                        print(
                            f"  🔧 Provider: {result.metadata.get('provider', 'unknown')}"
                        )
                        print(f"  ⚡ Processing time: {result.processing_time:.3f}s")
                        print(f"  📏 Size: {len(result.audio_data):,} bytes")

                        if language in results:
                            results[language]["processor_file"] = filename
                            results[language]["processor_provider"] = (
                                result.metadata.get("provider")
                            )

                    except Exception as e:
                        print(f"  ❌ Processor failed: {e}")

                    print("")

        except Exception as e:
            print(f"❌ Speech processor test failed: {e}")

        # Summary Report
        print("📋 VOICE SAMPLE GENERATION REPORT")
        print("=" * 50)

        successful = [lang for lang, result in results.items() if result.get("success")]
        failed = [lang for lang, result in results.items() if not result.get("success")]

        print(f"✅ Successful: {len(successful)}/{len(results)} languages")
        if successful:
            print(f"   {', '.join([language_names[lang] for lang in successful])}")

        if failed:
            print(f"❌ Failed: {len(failed)} languages")
            print(f"   {', '.join([language_names[lang] for lang in failed])}")

        print(f"\n🎧 LISTENING TEST INSTRUCTIONS:")
        print(f"   Run these commands to test each voice:")
        print(f"   ----------------------------------------")

        for language, result in results.items():
            if result.get("success"):
                language_name = language_names[language]
                filename = result["filename"]
                print(f"   # {language_name}")
                print(f"   afplay {filename}")

                if "processor_file" in result:
                    print(
                        f"   afplay {result['processor_file']}  # Speech processor version"
                    )
                print()

        print(f"🎯 EVALUATION CRITERIA:")
        print(f"   • Clarity: Can you understand the words clearly?")
        print(f"   • Naturalness: Does it sound human-like?")
        print(f"   • Pronunciation: Are words pronounced correctly?")
        print(f"   • Speed: Is the speaking rate appropriate?")
        print(f"   • Quality: Overall audio quality?")

        return results

    except Exception as e:
        logger.error(f"Voice sample generation failed: {e}")
        import traceback

        traceback.print_exc()
        return {}


if __name__ == "__main__":
    results = asyncio.run(generate_all_voice_samples())
