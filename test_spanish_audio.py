#!/usr/bin/env python3
"""
Individual Spanish Audio Test - User Validation
Generate Spanish audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_spanish_audio():
    """Generate Spanish audio for user listening validation"""
    print("🇪🇸 SPANISH AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # Spanish test phrase (Mexican Spanish)
    spanish_text = "¡Hola! Bienvenido a nuestra plataforma de aprendizaje de idiomas con inteligencia artificial. Esta es una prueba de síntesis de voz en español mexicano usando Piper TTS."

    print(f"📝 Text to synthesize: {spanish_text}")
    print(f"🎤 Expected voice: es_MX-claude-high (Mexican Spanish)")

    try:
        print("\n🔄 Generating Spanish audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=spanish_text, language="es"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "spanish_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Spanish audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
            print(f"🎵 Voice used: {metadata.get('voice_name', 'es_MX-claude-high')}")

            print(f"\n🎧 PLEASE LISTEN TO THE AUDIO FILE:")
            print(f"   File location: {Path.cwd()}/{audio_file}")
            print(f"   Expected: Clear Mexican Spanish speech")
            print(f"   Quality check: Latin American accent, natural pronunciation")
            print(f"   Note: This should be Mexican Spanish, not Spain Spanish")

            return True
        else:
            print("❌ No Spanish audio generated")
            return False

    except Exception as e:
        print(f"❌ Spanish audio generation failed: {e}")
        return False


async def main():
    """Run Spanish audio validation test"""
    print("🎯 INDIVIDUAL LANGUAGE AUDIO VALIDATION - SPANISH")
    print("👂 Testing language 2/7 for actual audio playback")
    print("=" * 60)

    success = await test_spanish_audio()

    print("\n" + "=" * 60)
    if success:
        print("✅ Spanish audio file generated for your validation")
        print("👂 Please listen to 'spanish_test_audio.wav' and confirm:")
        print("   1. Audio plays correctly")
        print("   2. Voice quality is acceptable")
        print("   3. Pronunciation is clear")
        print("   4. Accent sounds Latin American (Mexican), not Spain Spanish")
        print("   5. Speed is appropriate")
        print("\n📋 After listening, let me know if this passes your validation")
        print("🔄 Then we'll proceed to French audio test")
        print("\n📊 Progress: English ✅ PASS | Spanish ⏳ TESTING | 5 remaining")
    else:
        print("❌ Spanish audio generation failed - needs investigation")

    print(f"\n🎯 This is 2/7 languages - testing individually as requested")


if __name__ == "__main__":
    asyncio.run(main())
