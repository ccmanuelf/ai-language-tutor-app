#!/usr/bin/env python3
"""
Spanish Voices Comparison Test
Test different Spanish voices to find the most natural one
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_spanish_voices():
    """Test different Spanish voices for naturalness comparison"""
    print("🇪🇸 SPANISH VOICES COMPARISON TEST")
    print("=" * 60)

    piper_service = PiperTTSService()

    # Spanish test phrase
    spanish_text = "Hola! Bienvenido a nuestra plataforma de aprendizaje de idiomas con inteligencia artificial. Este es un test de síntesis de voz en español."

    print(f"📝 Text to synthesize: {spanish_text}")

    # Test Mexican Spanish voice (current)
    print("\n" + "=" * 60)
    print("🇲🇽 Testing Mexican Spanish Voice (es_MX-claude-high)")
    print("=" * 60)

    try:
        start_time = time.time()

        # Temporarily change the mapping to use Mexican voice
        original_mapping = piper_service.language_voice_map["es"]
        piper_service.language_voice_map["es"] = "es_MX-claude-high"

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=spanish_text, language="es"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            audio_file = "spanish_mexican_test.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Mexican Spanish audio generated!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"🎤 Voice: {metadata.get('voice', 'es_MX-claude-high')}")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
        else:
            print("❌ Failed to generate Mexican Spanish audio")

    except Exception as e:
        print(f"❌ Error with Mexican Spanish: {str(e)}")

    # Test Spain Spanish voice
    print("\n" + "=" * 60)
    print("🇪🇸 Testing Spain Spanish Voice (es_ES-davefx-medium)")
    print("=" * 60)

    try:
        start_time = time.time()

        # Change mapping to use Spain voice
        piper_service.language_voice_map["es"] = "es_ES-davefx-medium"

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=spanish_text, language="es"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            audio_file = "spanish_spain_test.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Spain Spanish audio generated!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"🎤 Voice: {metadata.get('voice', 'es_ES-davefx-medium')}")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
        else:
            print("❌ Failed to generate Spain Spanish audio")

    except Exception as e:
        print(f"❌ Error with Spain Spanish: {str(e)}")

    # Restore original mapping
    piper_service.language_voice_map["es"] = original_mapping

    print(f"\n🎧 VOICE COMPARISON COMPLETED!")
    print("📋 Please listen to both audio files:")
    print("   • spanish_mexican_test.wav (🇲🇽 Mexican - es_MX-claude-high)")
    print("   • spanish_spain_test.wav (🇪🇸 Spain - es_ES-davefx-medium)")
    print("\n📊 Evaluation criteria:")
    print("   • Naturalness: Which sounds more human-like?")
    print("   • Clarity: Which is clearer and easier to understand?")
    print("   • Accent preference: Mexican vs Iberian Spanish")
    print("   • Overall quality: Which would you prefer for the app?")


if __name__ == "__main__":
    asyncio.run(test_spanish_voices())
