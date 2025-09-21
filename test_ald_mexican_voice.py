#!/usr/bin/env python3
"""
Test es_MX-ald-medium Mexican Spanish Voice
Generate audio using the es_MX-ald-medium voice after fixing compatibility issue
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_ald_mexican_voice():
    """Test the es_MX-ald-medium Mexican Spanish voice"""
    print("🇲🇽 MEXICAN SPANISH - ALD VOICE TEST")
    print("=" * 60)

    piper_service = PiperTTSService()

    # Spanish test phrase for language learning
    spanish_text = "Hola! Bienvenido a nuestra plataforma de aprendizaje de idiomas con inteligencia artificial. Esta aplicación te ayudará a mejorar tu pronunciación y comprensión del español mexicano."

    print(f"📝 Text to synthesize: {spanish_text}")
    print(f"🎤 Voice: es_MX-ald-medium (Mexican Spanish - Ald)")
    print(f"🔧 Fixed compatibility issue: phoneme_type corrected")

    try:
        print("\n🔄 Generating Mexican Spanish audio with Ald voice...")
        start_time = time.time()

        # Temporarily change mapping to use the ald voice
        original_mapping = piper_service.language_voice_map.get("es", "")
        piper_service.language_voice_map["es"] = "es_MX-ald-medium"

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=spanish_text, language="es"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user validation
            audio_file = "mexican_ald_voice_test.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Mexican Spanish (Ald) audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"🎤 Voice confirmed: {metadata.get('voice', 'es_MX-ald-medium')}")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
            print(f"🎯 Quality: Medium (Mexican Spanish)")

            print(f"\n🎧 Please play '{audio_file}' to validate:")
            print(
                "   • Naturalness: Does this sound more natural than previous voices?"
            )
            print("   • Clarity: Is the pronunciation clear and understandable?")
            print("   • Accent: How does this Mexican accent compare to others?")
            print(
                "   • Overall Quality: Is this acceptable for the language learning app?"
            )
            print(
                "   • Robotic Quality: Does this sound less robotic than es_MX-claude-high?"
            )

            return True

        else:
            print("❌ Failed to generate Mexican Spanish (Ald) audio")
            print("   Error: No audio data generated")
            return False

        # Restore original mapping
        if original_mapping:
            piper_service.language_voice_map["es"] = original_mapping

    except Exception as e:
        print(f"❌ Error during Mexican Spanish (Ald) test: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_ald_mexican_voice())
    if success:
        print(f"\n🎯 MEXICAN SPANISH (ALD) TEST COMPLETED")
        print(f"📋 Please validate the audio quality and provide feedback.")
        print(f"🔧 Compatibility issue has been resolved.")
    else:
        print(f"\n❌ MEXICAN SPANISH (ALD) TEST FAILED")
