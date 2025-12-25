#!/usr/bin/env python3
"""
Comprehensive Spanish Voices Test
Test all available Spanish voices to find the most natural Latin American option
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_all_spanish_voices():
    """Test all available Spanish voices for naturalness comparison"""
    print("🇪🇸 COMPREHENSIVE SPANISH VOICES TEST")
    print("=" * 70)

    piper_service = PiperTTSService()

    # Spanish test phrase - typical for language learning app
    spanish_text = "Hola! Bienvenido a nuestra plataforma de aprendizaje de idiomas con inteligencia artificial. Esta aplicación te ayudará a mejorar tu pronunciación y comprensión del español."

    print(f"📝 Text to synthesize: {spanish_text}")
    print("🎯 Testing 4 Spanish voice models for naturalness comparison")

    voices_to_test = [
        {
            "name": "🇦🇷 Argentina - Daniela (High Quality)",
            "voice_id": "es_AR-daniela-high",
            "file": "spanish_argentina_test.wav",
            "description": "Argentina Spanish - High quality, neutral Latin American accent",
        },
        {
            "name": "🇲🇽 Mexico - Ald (Medium Quality)",
            "voice_id": "es_MX-ald-medium",
            "file": "spanish_mexico_ald_test.wav",
            "description": "Mexican Spanish alternative - Medium quality",
        },
        {
            "name": "🇲🇽 Mexico - Claude (High Quality)",
            "voice_id": "es_MX-claude-high",
            "file": "spanish_mexico_claude_test.wav",
            "description": "Mexican Spanish current - High quality (currently used)",
        },
        {
            "name": "🇪🇸 Spain - Davefx (Medium Quality)",
            "voice_id": "es_ES-davefx-medium",
            "file": "spanish_spain_test.wav",
            "description": "Iberian Spanish - Medium quality, European accent",
        },
    ]

    results = []

    for voice_info in voices_to_test:
        print(f"\n" + "=" * 70)
        print(f"Testing: {voice_info['name']}")
        print(f"Voice ID: {voice_info['voice_id']}")
        print(f"Description: {voice_info['description']}")
        print("=" * 70)

        try:
            start_time = time.time()

            # Temporarily change the mapping to test this specific voice
            original_mapping = piper_service.language_voice_map.get("es", "")
            piper_service.language_voice_map["es"] = voice_info["voice_id"]

            audio_bytes, metadata = await piper_service.synthesize_speech(
                text=spanish_text, language="es"
            )

            generation_time = time.time() - start_time

            if audio_bytes and len(audio_bytes) > 0:
                # Save audio file
                with open(voice_info["file"], "wb") as f:
                    f.write(audio_bytes)

                print(f"✅ {voice_info['name']} audio generated!")
                print(f"📁 Audio file: {voice_info['file']}")
                print(f"📊 File size: {len(audio_bytes):,} bytes")
                print(
                    f"🎤 Voice confirmed: {metadata.get('voice', voice_info['voice_id'])}"
                )
                print(f"⏱️ Generation time: {generation_time:.2f} seconds")

                results.append(
                    {
                        "name": voice_info["name"],
                        "file": voice_info["file"],
                        "success": True,
                        "size": len(audio_bytes),
                        "time": generation_time,
                    }
                )

            else:
                print(f"❌ Failed to generate audio for {voice_info['name']}")
                results.append(
                    {
                        "name": voice_info["name"],
                        "file": voice_info["file"],
                        "success": False,
                    }
                )

        except Exception as e:
            print(f"❌ Error with {voice_info['name']}: {str(e)}")
            results.append(
                {
                    "name": voice_info["name"],
                    "file": voice_info["file"],
                    "success": False,
                    "error": str(e),
                }
            )

        # Restore original mapping
        if original_mapping:
            piper_service.language_voice_map["es"] = original_mapping

    # Summary
    print(f"\n" + "=" * 70)
    print("🎧 VOICE COMPARISON SUMMARY")
    print("=" * 70)

    successful_voices = [r for r in results if r.get("success", False)]

    print(f"✅ Successfully generated: {len(successful_voices)}/4 voices")
    print("\n📋 Audio files for listening comparison:")

    for result in successful_voices:
        print(f"   • {result['file']} - {result['name']}")
        print(f"     Size: {result['size']:,} bytes | Time: {result['time']:.2f}s")

    print(f"\n🎯 EVALUATION CRITERIA:")
    print("   • Naturalness: Which sounds most human-like and less robotic?")
    print("   • Clarity: Which has the clearest pronunciation?")
    print("   • Accent preference: Which Latin American accent do you prefer?")
    print("   • Overall quality: Best voice for language learning app?")
    print("   • Regional preference: Argentina vs Mexico vs Spain")

    print(f"\n📝 RECOMMENDATION FOCUS:")
    print("   🇦🇷 Argentina (daniela-high): Neutral Latin American, high quality")
    print("   🇲🇽 Mexico (ald-medium): Alternative Mexican voice")
    print("   🇲🇽 Mexico (claude-high): Current voice (reported as robotic)")
    print("   🇪🇸 Spain (davefx-medium): European Spanish for comparison")


if __name__ == "__main__":
    asyncio.run(test_all_spanish_voices())
