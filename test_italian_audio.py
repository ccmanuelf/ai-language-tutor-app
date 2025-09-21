#!/usr/bin/env python3
"""
Individual Italian Audio Test - User Validation
Generate Italian audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_italian_audio():
    """Generate Italian audio for user listening validation"""
    print("🇮🇹 ITALIAN AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # Italian test phrase
    italian_text = "Ciao! Benvenuto nella nostra piattaforma di apprendimento linguistico con intelligenza artificiale. Questo è un test di sintesi vocale italiana usando Piper TTS."

    print(f"📝 Text to synthesize: {italian_text}")
    print(f"🎤 Expected voice: it_IT-riccardo-x_low (Italian)")

    try:
        print("\n🔄 Generating Italian audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=italian_text, language="it"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "italian_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Italian audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")
            print(
                f"🎵 Voice used: {metadata.get('voice_name', 'it_IT-riccardo-x_low')}"
            )

            print(f"\n🎧 PLEASE LISTEN TO THE AUDIO FILE:")
            print(f"   File location: {Path.cwd()}/{audio_file}")
            print(f"   Expected: Clear Italian speech")
            print(f"   Quality check: Natural Italian pronunciation, appropriate speed")
            print(
                f"   Note: This voice is x_low quality - may be different from others"
            )

            return True
        else:
            print("❌ No Italian audio generated")
            return False

    except Exception as e:
        print(f"❌ Italian audio generation failed: {e}")
        return False


async def main():
    """Run Italian audio validation test"""
    print("🎯 INDIVIDUAL LANGUAGE AUDIO VALIDATION - ITALIAN")
    print("👂 Testing language 5/7 for actual audio playback")
    print("=" * 60)

    success = await test_italian_audio()

    print("\n" + "=" * 60)
    if success:
        print("✅ Italian audio file generated for your validation")
        print("👂 Please listen to 'italian_test_audio.wav' and confirm:")
        print("   1. Audio plays correctly")
        print("   2. Voice quality is acceptable")
        print("   3. Pronunciation is clear")
        print("   4. Quality: Perfect/Good/Robotic?")
        print("   5. Speed is appropriate")
        print("\n⚠️ NOTE: This is x_low quality model - may sound different")
        print("\n📋 After listening, let me know if this passes your validation")
        print("🔄 Then we'll proceed to Portuguese audio test")
        print(
            "\n📊 Progress: EN✅ | ES⚠️ | FR✅ | DE✅ | Italian ⏳ TESTING | 2 remaining"
        )
    else:
        print("❌ Italian audio generation failed - needs investigation")

    print(f"\n🎯 This is 5/7 languages - testing individually as requested")


if __name__ == "__main__":
    asyncio.run(main())
