#!/usr/bin/env python3
"""
Individual German Audio Test - User Validation
Generate German audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_german_audio():
    """Generate German audio for user listening validation"""
    print("🇩🇪 GERMAN AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # German test phrase
    german_text = "Hallo! Willkommen auf unserer Sprachlernplattform mit künstlicher Intelligenz. Dies ist ein Test der deutschen Sprachsynthese mit Piper TTS."

    print(f"📝 Text to synthesize: {german_text}")
    print(f"🎤 Expected voice: de_DE-thorsten-medium (German)")

    try:
        print("\n🔄 Generating German audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=german_text, language="de"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "german_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ German audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
            print(
                f"🎵 Voice used: {metadata.get('voice_name', 'de_DE-thorsten-medium')}"
            )

            print(f"\n🎧 PLEASE LISTEN TO THE AUDIO FILE:")
            print(f"   File location: {Path.cwd()}/{audio_file}")
            print(f"   Expected: Clear German speech")
            print(f"   Quality check: Natural German pronunciation, appropriate speed")
            print(f"   Note: Should sound like native German speaker")

            return True
        else:
            print("❌ No German audio generated")
            return False

    except Exception as e:
        print(f"❌ German audio generation failed: {e}")
        return False


async def main():
    """Run German audio validation test"""
    print("🎯 INDIVIDUAL LANGUAGE AUDIO VALIDATION - GERMAN")
    print("👂 Testing language 4/7 for actual audio playback")
    print("=" * 60)

    success = await test_german_audio()

    print("\n" + "=" * 60)
    if success:
        print("✅ German audio file generated for your validation")
        print("👂 Please listen to 'german_test_audio.wav' and confirm:")
        print("   1. Audio plays correctly")
        print("   2. Voice quality is acceptable")
        print("   3. Pronunciation is clear")
        print("   4. Sounds natural (like English/French) or robotic (like Spanish)?")
        print("   5. Speed is appropriate")
        print("\n📋 After listening, let me know if this passes your validation")
        print("🔄 Then we'll proceed to Italian audio test")
        print(
            "\n📊 Progress: English ✅ | Spanish ⚠️ (robotic) | French ✅ | German ⏳ TESTING | 3 remaining"
        )
    else:
        print("❌ German audio generation failed - needs investigation")

    print(f"\n🎯 This is 4/7 languages - testing individually as requested")


if __name__ == "__main__":
    asyncio.run(main())
