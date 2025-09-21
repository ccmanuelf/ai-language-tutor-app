#!/usr/bin/env python3
"""
Test Spanish Voice Comparison: Spain vs Mexican Accent
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


async def test_spanish_voices():
    """Test and compare Spanish voice models"""

    # Test phrases covering different Spanish sounds
    test_phrases = {
        "basic": "¡Hola! Esta es una prueba de síntesis de voz en español.",
        "comprehensive": "El tutor de idiomas AI usa esta voz para lecciones en español. ¿Cómo te suena la pronunciación y el acento?",
        "common_words": "Gracias, por favor, de nada, buenos días, buenas noches, adiós.",
        "challenging": "Rápidamente, trabajador, desarrollar, oportunidad, responsabilidad.",
    }

    print("🎯 Spanish Voice Comparison Test")
    print("=" * 50)

    try:
        from app.services.piper_tts_service import PiperTTSService

        service = PiperTTSService()

        # Check available voices
        info = service.get_service_info()
        available_voices = info["available_voices"]

        print(f"📊 Available voices: {len(available_voices)}")
        spanish_voices = [v for v in available_voices if "es_" in v]
        print(f"🇪🇸 Spanish voices found: {spanish_voices}")
        print()

        results = {}

        for voice_name in spanish_voices:
            region = (
                "Spain"
                if "ES" in voice_name
                else "Mexico"
                if "MX" in voice_name
                else "Unknown"
            )
            print(f"🗣️  Testing: {voice_name} ({region})")
            print("-" * 40)

            voice_results = {}

            for test_name, phrase in test_phrases.items():
                print(
                    f"📝 {test_name}: {phrase[:50]}{'...' if len(phrase) > 50 else ''}"
                )

                try:
                    # Force specific voice by temporarily updating language map
                    original_map = service.language_voice_map.copy()
                    service.language_voice_map["es"] = voice_name

                    # Generate audio
                    audio_data, metadata = await service.synthesize_speech(
                        text=phrase, language="es"
                    )

                    # Restore original mapping
                    service.language_voice_map = original_map

                    # Save audio file
                    filename = f"spanish_test_{voice_name}_{test_name}.wav"
                    with open(filename, "wb") as f:
                        f.write(audio_data)

                    voice_results[test_name] = {
                        "filename": filename,
                        "size": len(audio_data),
                        "duration": metadata.get("duration_estimate", "unknown"),
                    }

                    print(f"  ✅ {filename} ({len(audio_data):,} bytes)")

                except Exception as e:
                    print(f"  ❌ Failed: {e}")
                    voice_results[test_name] = {"error": str(e)}

            results[voice_name] = voice_results
            print()

        # Generate comparison report
        print("🎧 VOICE COMPARISON INSTRUCTIONS")
        print("=" * 50)
        print("Listen to each voice and compare:")
        print("• Accent preference (Spain vs Mexican)")
        print("• Clarity and naturalness")
        print("• Pronunciation accuracy")
        print("• Overall suitability for language learning")
        print()

        for voice_name in spanish_voices:
            region = (
                "🇪🇸 Spain"
                if "ES" in voice_name
                else "🇲🇽 Mexico"
                if "MX" in voice_name
                else "❓ Unknown"
            )
            print(f"{region} - {voice_name}")
            print("-" * 30)

            if voice_name in results:
                for test_name, result in results[voice_name].items():
                    if "filename" in result:
                        print(f"# {test_name}")
                        print(f"afplay {result['filename']}")
                print()

        print("🎯 After listening, please tell me:")
        print("1. Which accent sounds better to you?")
        print("2. Which voice is clearer/more natural?")
        print("3. Which would be better for language learning?")
        print("4. Should we switch the default Spanish voice?")

        return results

    except Exception as e:
        logger.error(f"Spanish voice test failed: {e}")
        import traceback

        traceback.print_exc()
        return {}


if __name__ == "__main__":
    results = asyncio.run(test_spanish_voices())
