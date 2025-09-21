#!/usr/bin/env python3
"""
Individual English Audio Test - User Validation
Generate English audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_english_audio():
    """Generate English audio for user listening validation"""
    print("🇺🇸 ENGLISH AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # English test phrase
    english_text = "Hello! Welcome to our AI language learning platform. This is a test of English text-to-speech using Piper TTS with the American English voice."

    print(f"📝 Text to synthesize: {english_text}")
    print(f"🎤 Expected voice: en_US-lessac-medium")

    try:
        print("\n🔄 Generating English audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=english_text, language="en"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "english_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ English audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
            print(f"🎵 Voice used: {metadata.get('voice_name', 'en_US-lessac-medium')}")

            print(f"\n🎧 PLEASE LISTEN TO THE AUDIO FILE:")
            print(f"   File location: {Path.cwd()}/{audio_file}")
            print(f"   Expected: Clear American English speech")
            print(f"   Quality check: Natural pronunciation, appropriate speed")

            return True
        else:
            print("❌ No English audio generated")
            return False

    except Exception as e:
        print(f"❌ English audio generation failed: {e}")
        return False


async def main():
    """Run English audio validation test"""
    print("🎯 INDIVIDUAL LANGUAGE AUDIO VALIDATION")
    print("👂 Testing ONE language at a time for actual audio playback")
    print("=" * 60)

    success = await test_english_audio()

    print("\n" + "=" * 60)
    if success:
        print("✅ English audio file generated for your validation")
        print("👂 Please listen to 'english_test_audio.wav' and confirm:")
        print("   1. Audio plays correctly")
        print("   2. Voice quality is acceptable")
        print("   3. Pronunciation is clear")
        print("   4. Speed is appropriate")
        print("\n📋 After listening, let me know if this passes your validation")
        print("🔄 Then we'll proceed to Spanish audio test")
    else:
        print("❌ English audio generation failed - needs investigation")

    print(f"\n🎯 This is 1/7 languages - testing individually as requested")


if __name__ == "__main__":
    asyncio.run(main())
