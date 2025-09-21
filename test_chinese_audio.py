#!/usr/bin/env python3
"""
Individual Chinese Audio Test - User Validation
Generate Chinese audio for actual listening validation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService


async def test_chinese_audio():
    """Generate Chinese audio for user listening validation"""
    print("🇨🇳 CHINESE AUDIO VALIDATION TEST")
    print("=" * 50)

    piper_service = PiperTTSService()

    # Chinese test phrase (Simplified Chinese)
    chinese_text = "你好！欢迎使用我们的人工智能语言学习平台。这是使用Piper TTS进行中文语音合成的测试。"

    print(f"📝 Text to synthesize: {chinese_text}")
    print(f"🎤 Expected voice: zh_CN-huayan-medium")

    try:
        print("\n🔄 Generating Chinese audio...")
        start_time = time.time()

        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=chinese_text, language="zh"
        )

        generation_time = time.time() - start_time

        if audio_bytes and len(audio_bytes) > 0:
            # Save audio file for user to listen
            audio_file = "chinese_test_audio.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Chinese audio generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"🎤 Voice used: {metadata.get('voice', 'zh_CN-huayan-medium')}")
            print(f"⏱️ Generation time: {generation_time:.2f} seconds")

            print(f"\n🎧 Please play '{audio_file}' to validate:")
            print("   • Clarity: Is the Chinese speech clear and understandable?")
            print("   • Naturalness: Does the voice sound natural for Chinese?")
            print("   • Pronunciation: Is Mandarin pronunciation accurate?")
            print("   • Tone Quality: Are Chinese tones correctly pronounced?")
            print("   • Speed: Is the speaking rate appropriate?")
            print("   • Overall Quality: Rate overall Chinese voice quality")

            return True

        else:
            print("❌ Failed to generate Chinese audio")
            print("   Error: No audio data generated")
            return False

    except Exception as e:
        print(f"❌ Error during Chinese audio test: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_chinese_audio())
    if success:
        print(f"\n🎯 CHINESE AUDIO TEST COMPLETED")
        print(f"📋 Please validate the audio quality and provide feedback.")
    else:
        print(f"\n❌ CHINESE AUDIO TEST FAILED")
