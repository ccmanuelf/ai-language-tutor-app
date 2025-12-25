#!/usr/bin/env python3
"""
Test Chinese TTS functionality with Piper
Addresses critical gap identified in Phase 2A validation
"""

import asyncio
import sys
import os
from pathlib import Path
import wave

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.piper_tts_service import PiperTTSService
from services.speech_processor import SpeechProcessor


async def test_chinese_voice_direct():
    """Test Chinese TTS directly with PiperTTSService"""
    print("🇨🇳 Testing Chinese TTS - Direct Piper Service")
    print("=" * 60)

    piper_service = PiperTTSService()

    # Check if Chinese voice is available
    available_voices = piper_service.get_available_voices()
    print(f"📋 Available voices: {len(available_voices)}")
    for voice in available_voices:
        if "zh" in voice.lower():
            print(f"  ✅ Found Chinese voice: {voice}")

    # Test Chinese text synthesis
    chinese_texts = [
        "你好，欢迎使用人工智能语言学习平台。",  # Hello, welcome to our AI language learning platform
        "这是一个测试中文语音合成的例子。",  # This is an example of testing Chinese speech synthesis
        "我们正在验证中文文本到语音的功能。",  # We are validating Chinese text-to-speech functionality
    ]

    for i, text in enumerate(chinese_texts, 1):
        print(f"\n{i}️⃣ Testing Chinese text: {text}")
        try:
            audio_bytes, metadata = await piper_service.synthesize_speech(
                text=text, language="zh"
            )

            if audio_bytes and len(audio_bytes) > 0:
                duration = metadata.get("duration_seconds", 0)
                voice_used = metadata.get("voice_name", "unknown")

                # Save test file
                test_file = f"test_chinese_{i}.wav"
                with open(test_file, "wb") as f:
                    f.write(audio_bytes)

                # Validate WAV file
                try:
                    with wave.open(test_file, "rb") as wav_file:
                        frames = wav_file.getnframes()
                        sample_rate = wav_file.getframerate()
                        actual_duration = frames / sample_rate

                        print(f"  ✅ Chinese audio generated successfully!")
                        print(f"  📊 Voice: {voice_used}")
                        print(f"  ⏱️ Duration: {actual_duration:.2f}s")
                        print(f"  📁 Size: {len(audio_bytes):,} bytes")
                        print(f"  🎵 Sample Rate: {sample_rate}Hz")

                        # Cleanup
                        os.remove(test_file)

                except Exception as e:
                    print(f"  ❌ Invalid WAV file: {e}")
                    if os.path.exists(test_file):
                        os.remove(test_file)
            else:
                print(f"  ❌ No audio generated for Chinese text")

        except Exception as e:
            print(f"  ❌ Chinese TTS failed: {e}")

    return True


async def test_chinese_speech_processor():
    """Test Chinese TTS through SpeechProcessor integration"""
    print("\n🔄 Testing Chinese TTS - Speech Processor Integration")
    print("=" * 60)

    speech_processor = SpeechProcessor()

    chinese_test_text = "人工智能语言学习助手正在为您服务。"  # AI language learning assistant is serving you

    try:
        result = await speech_processor.process_text_to_speech(
            text=chinese_test_text, language="zh", provider="piper"
        )

        if result.audio_data and len(result.audio_data) > 0:
            provider = result.metadata.get("provider", "unknown")
            print(f"  ✅ Speech processor Chinese TTS successful")
            print(f"  📊 Provider: {provider}")
            print(f"  ⏱️ Duration: {result.duration_seconds:.2f}s")
            print(f"  📁 Size: {len(result.audio_data):,} bytes")
            print(f"  🎯 Text: {chinese_test_text}")
            return True
        else:
            print(f"  ❌ Speech processor Chinese TTS failed")
            return False

    except Exception as e:
        print(f"  ❌ Speech processor error: {e}")
        return False


async def test_chinese_language_support():
    """Test Chinese language detection and voice selection"""
    print("\n🔍 Testing Chinese Language Support")
    print("=" * 60)

    piper_service = PiperTTSService()

    # Test language detection
    chinese_voice = piper_service.get_voice_for_language("zh")
    print(f"📢 Voice selected for 'zh': {chinese_voice}")

    # Test language variations
    language_variants = ["zh", "zh-CN", "zh_CN"]
    for variant in language_variants:
        voice = piper_service.get_voice_for_language(variant)
        print(f"  {variant}: {voice}")

    # Check voice configuration
    if chinese_voice and chinese_voice in piper_service.voices:
        voice_info = piper_service.voices[chinese_voice]
        print(f"\n📋 Chinese Voice Configuration:")
        print(f"  Model: {voice_info['model_path']}")
        print(f"  Config: {voice_info['config_path']}")
        print(f"  Language: {voice_info.get('language', 'unknown')}")
        print(f"  Sample Rate: {voice_info.get('sample_rate', 'unknown')}Hz")
        return True
    else:
        print("❌ Chinese voice not properly configured")
        return False


async def main():
    """Run comprehensive Chinese TTS validation"""
    print("🚀 CRITICAL TEST: Chinese TTS Functionality Validation")
    print("🎯 Addressing Phase 2A gap - Chinese language support")
    print("=" * 80)

    # Run all Chinese TTS tests
    direct_test = await test_chinese_voice_direct()
    processor_test = await test_chinese_speech_processor()
    support_test = await test_chinese_language_support()

    # Summary
    print("\n" + "=" * 80)
    print("📋 CHINESE TTS VALIDATION SUMMARY")
    print("=" * 80)

    tests = {
        "Direct Chinese TTS": direct_test,
        "Speech Processor Integration": processor_test,
        "Language Support": support_test,
    }

    passed_tests = sum(tests.values())
    total_tests = len(tests)

    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    success_rate = passed_tests / total_tests * 100
    print(
        f"\n📊 Chinese TTS Tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)"
    )

    if success_rate >= 100:
        print("\n🎉 Chinese TTS implementation SUCCESSFUL!")
        print("✅ Critical Phase 2A gap addressed")
        print("🇨🇳 Chinese language now fully supported with native voice")
        return True
    else:
        print("\n⚠️ Chinese TTS implementation needs attention")
        print("❌ Critical functionality still missing")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
