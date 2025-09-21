#!/usr/bin/env python3
"""
Comprehensive Voice Validation Test

This script tests all available language voices with actual audio playback
and user evaluation for optimal voice selection.
"""

import asyncio
import sys
import logging
import os
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceValidationTest:
    def __init__(self):
        self.test_phrases = {
            "en": "Hello! This is a test of English speech synthesis. How does this voice sound to you?",
            "es": "¡Hola! Esta es una prueba de síntesis de voz en español. ¿Cómo te suena esta voz?",
            "fr": "Bonjour! Ceci est un test de synthèse vocale française. Comment trouvez-vous cette voix?",
            "de": "Hallo! Das ist ein Test der deutschen Sprachsynthese. Wie klingt diese Stimme für Sie?",
            "it": "Ciao! Questo è un test di sintesi vocale italiana. Come ti sembra questa voce?",
            "pt": "Olá! Este é um teste de síntese de voz em português. Como você acha que essa voz soa?",
            "zh": "Hello! This is Chinese text spoken with English voice as fallback.",
            "ja": "Hello! This is Japanese text spoken with English voice as fallback.",
            "ko": "Hello! This is Korean text spoken with English voice as fallback.",
        }

        self.language_names = {
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

        self.results = {}

    async def test_piper_service_direct(self):
        """Test Piper TTS service directly for all languages"""
        logger.info("=== Testing Direct Piper TTS Service ===")

        try:
            from app.services.piper_tts_service import PiperTTSService

            service = PiperTTSService()

            info = service.get_service_info()
            logger.info(f"Available voices: {info['available_voices']}")
            logger.info(f"Supported languages: {info['supported_languages']}")

            for language, phrase in self.test_phrases.items():
                await self._test_language_direct(service, language, phrase)

            return True

        except Exception as e:
            logger.error(f"Direct Piper service test failed: {e}")
            return False

    async def _test_language_direct(self, service, language, phrase):
        """Test a specific language with direct Piper service"""
        language_name = self.language_names[language]

        print(f"\n{'=' * 60}")
        print(f"🗣️  TESTING: {language_name} ({language.upper()})")
        print(f"📝 Phrase: {phrase}")
        print(f"{'=' * 60}")

        try:
            # Synthesize speech
            audio_data, metadata = await service.synthesize_speech(
                text=phrase, language=language
            )

            # Save audio file
            filename = f"test_voice_{language}.wav"
            with open(filename, "wb") as f:
                f.write(audio_data)

            logger.info(f"✅ Generated: {filename}")
            logger.info(f"📊 Voice: {metadata['voice']}")
            logger.info(f"📏 Size: {len(audio_data):,} bytes")
            logger.info(f"⏱️  Duration: {metadata.get('duration_estimate', 'unknown')}s")

            # Play audio
            print(f"🔊 Playing {language_name} audio...")
            os.system(f"afplay {filename}")

            # Get user feedback
            feedback = await self._get_user_feedback(language_name)
            self.results[language] = {
                "voice": metadata["voice"],
                "size": len(audio_data),
                "feedback": feedback,
                "filename": filename,
            }

        except Exception as e:
            logger.error(f"❌ Failed to test {language_name}: {e}")
            self.results[language] = {"error": str(e)}

    async def test_speech_processor_integration(self):
        """Test speech processor integration for key languages"""
        logger.info("\n=== Testing Speech Processor Integration ===")

        try:
            from app.services.speech_processor import SpeechProcessor

            processor = SpeechProcessor()

            # Test key languages through speech processor
            key_languages = ["en", "es", "fr", "de"]

            for language in key_languages:
                await self._test_speech_processor_language(processor, language)

            return True

        except Exception as e:
            logger.error(f"Speech processor integration test failed: {e}")
            return False

    async def _test_speech_processor_language(self, processor, language):
        """Test specific language through speech processor"""
        phrase = self.test_phrases[language]
        language_name = self.language_names[language]

        print(f"\n📡 SPEECH PROCESSOR TEST: {language_name}")

        try:
            # Test with auto provider (should prefer Piper)
            result = await processor.process_text_to_speech(
                text=phrase, language=language, provider="auto"
            )

            filename = f"test_processor_{language}.wav"
            with open(filename, "wb") as f:
                f.write(result.audio_data)

            logger.info(f"✅ Processor: {filename}")
            logger.info(f"🔧 Provider: {result.metadata.get('provider', 'unknown')}")
            logger.info(f"⚡ Processing time: {result.processing_time:.3f}s")

            # Play and compare
            print(f"🔊 Playing {language_name} via speech processor...")
            os.system(f"afplay {filename}")

            # Quick comparison question
            comparison = (
                input(
                    f"How does this compare to the direct Piper version? (better/same/worse): "
                )
                .strip()
                .lower()
            )

            if language in self.results:
                self.results[language]["processor_comparison"] = comparison

        except Exception as e:
            logger.error(f"❌ Processor test failed for {language_name}: {e}")

    async def _get_user_feedback(self, language_name):
        """Get user feedback about voice quality"""
        print(f"\n🎤 FEEDBACK for {language_name}:")

        # Simple rating system
        quality = input("Rate voice quality (1-5, where 5=excellent): ").strip()
        clarity = input("Rate speech clarity (1-5, where 5=very clear): ").strip()
        naturalness = input("Rate naturalness (1-5, where 5=very natural): ").strip()

        # Optional comments
        comments = input("Any comments? (optional): ").strip()

        return {
            "quality": quality,
            "clarity": clarity,
            "naturalness": naturalness,
            "comments": comments,
        }

    def generate_report(self):
        """Generate comprehensive validation report"""
        print(f"\n{'=' * 80}")
        print("📋 COMPREHENSIVE VOICE VALIDATION REPORT")
        print(f"{'=' * 80}")

        print(f"\n📊 LANGUAGES TESTED: {len(self.results)}")

        for language, result in self.results.items():
            language_name = self.language_names[language]
            print(f"\n🗣️  {language_name} ({language.upper()})")
            print("-" * 50)

            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue

            print(f"🎵 Voice Model: {result['voice']}")
            print(f"📏 Audio Size: {result['size']:,} bytes")
            print(f"📁 File: {result['filename']}")

            if "feedback" in result:
                feedback = result["feedback"]
                print(f"⭐ Quality: {feedback.get('quality', 'N/A')}/5")
                print(f"🔍 Clarity: {feedback.get('clarity', 'N/A')}/5")
                print(f"🤖 Naturalness: {feedback.get('naturalness', 'N/A')}/5")

                if feedback.get("comments"):
                    print(f"💬 Comments: {feedback['comments']}")

            if "processor_comparison" in result:
                print(f"🔄 Processor vs Direct: {result['processor_comparison']}")

        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS")
        print("-" * 30)

        native_voices = [
            lang
            for lang in ["en", "es", "fr", "de", "it", "pt"]
            if lang in self.results and "error" not in self.results[lang]
        ]
        fallback_voices = [lang for lang in ["zh", "ja", "ko"] if lang in self.results]

        print(f"✅ Native Voice Support: {len(native_voices)} languages")
        print(f"   {', '.join([self.language_names[lang] for lang in native_voices])}")

        if fallback_voices:
            print(f"🔄 English Fallback: {len(fallback_voices)} languages")
            print(
                f"   {', '.join([self.language_names[lang] for lang in fallback_voices])}"
            )

        print(f"\n💡 Next Steps:")
        print(
            f"   • Download additional voice models for {', '.join(fallback_voices) if fallback_voices else 'no additional languages needed'}"
        )
        print(f"   • Consider voice quality improvements for low-rated voices")
        print(f"   • Validate speech processor integration is working correctly")


async def main():
    """Run comprehensive voice validation"""
    print("🎵 Starting Comprehensive Voice Validation Test")
    print("This will test all available language voices with actual audio playback")

    validator = VoiceValidationTest()

    # Test direct Piper service
    success1 = await validator.test_piper_service_direct()

    if success1:
        # Test speech processor integration
        success2 = await validator.test_speech_processor_integration()

    # Generate final report
    validator.generate_report()

    print(f"\n🎉 Voice validation complete!")
    print(f"📁 Audio files saved for review: test_voice_*.wav, test_processor_*.wav")


if __name__ == "__main__":
    asyncio.run(main())
