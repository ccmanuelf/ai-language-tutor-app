#!/usr/bin/env python3
"""
Individual Portuguese Audio Test - User Validation
Generate Portuguese audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_portuguese_audio():
    """Generate Portuguese audio for user listening validation"""
    print("🇧🇷 PORTUGUESE AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # Portuguese test phrase
    portuguese_text = "Olá! Bem-vindo à nossa plataforma de aprendizado de idiomas com inteligência artificial. Este é um teste de síntese de voz em português brasileiro usando Piper TTS."

    print(f"📝 Text to synthesize: {portuguese_text}")
    print(f"🎤 Expected voice: pt_BR-faber-medium")

    try:
        print("\n🔄 Generating Portuguese audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=portuguese_text, language="pt"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "portuguese_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Portuguese audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"🎤 Voice used: {metadata.get('voice', 'pt_BR-faber-medium')}")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")

            print(f"\n🎧 Please play '{audio_file}' to validate:")
            print("   • Clarity: Is the speech clear and understandable?")
            print("   • Naturalness: Does the voice sound natural?")
            print("   • Pronunciation: Is Portuguese pronunciation accurate?")
            print("   • Accent: Brazilian Portuguese accent quality?")
            print("   • Speed: Is the speaking rate appropriate?")
            print("   • Overall Quality: Rate overall voice quality")

            return True

        else:
            print("❌ Failed to generate Portuguese audio")
            print("   Error: No audio data generated")
            return False

    except Exception as e:
        print(f"❌ Error during Portuguese audio test: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_portuguese_audio())
    if success:
        print(f"\n🎯 PORTUGUESE AUDIO TEST COMPLETED")
        print(f"📋 Please validate the audio quality and provide feedback.")
    else:
        print(f"\n❌ PORTUGUESE AUDIO TEST FAILED")
