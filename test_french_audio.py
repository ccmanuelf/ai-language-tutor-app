#!/usr/bin/env python3
"""
Individual French Audio Test - User Validation
Generate French audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_french_audio():
    """Generate French audio for user listening validation"""
    print("🇫🇷 FRENCH AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # French test phrase
    french_text = "Bonjour ! Bienvenue sur notre plateforme d'apprentissage des langues avec intelligence artificielle. Ceci est un test de synthèse vocale en français utilisant Piper TTS."

    print(f"📝 Text to synthesize: {french_text}")
    print(f"🎤 Expected voice: fr_FR-siwis-medium (European French)")

    try:
        print("\n🔄 Generating French audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=french_text, language="fr"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "french_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ French audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
            print(f"🎵 Voice used: {metadata.get('voice_name', 'fr_FR-siwis-medium')}")

            print(f"\n🎧 PLEASE LISTEN TO THE AUDIO FILE:")
            print(f"   File location: {Path.cwd()}/{audio_file}")
            print(f"   Expected: Clear European French speech")
            print(f"   Quality check: Natural French pronunciation, appropriate speed")
            print(f"   Note: Should sound like native French speaker")

            return True
        else:
            print("❌ No French audio generated")
            return False

    except Exception as e:
        print(f"❌ French audio generation failed: {e}")
        return False


async def main():
    """Run French audio validation test"""
    print("🎯 INDIVIDUAL LANGUAGE AUDIO VALIDATION - FRENCH")
    print("👂 Testing language 3/7 for actual audio playback")
    print("=" * 60)

    success = await test_french_audio()

    print("\n" + "=" * 60)
    if success:
        print("✅ French audio file generated for your validation")
        print("👂 Please listen to 'french_test_audio.wav' and confirm:")
        print("   1. Audio plays correctly")
        print("   2. Voice quality is acceptable")
        print("   3. Pronunciation is clear")
        print("   4. Sounds like natural French (not robotic)")
        print("   5. Speed is appropriate")
        print("\n📋 After listening, let me know if this passes your validation")
        print("🔄 Then we'll proceed to German audio test")
        print(
            "\n📊 Progress: English ✅ | Spanish ⚠️ (robotic) | French ⏳ TESTING | 4 remaining"
        )
    else:
        print("❌ French audio generation failed - needs investigation")

    print(f"\n🎯 This is 3/7 languages - testing individually as requested")


if __name__ == "__main__":
    asyncio.run(main())
