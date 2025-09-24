#!/usr/bin/env python3
"""
Debug Test for Real-Time Analysis Timeout Issues
"""

import asyncio
import sys
import time

sys.path.append(".")

from app.services.realtime_analyzer import RealTimeAnalyzer, AudioSegment


async def test_with_timeout():
    """Test multi-language functionality with timeout controls"""

    print("🔍 Testing multi-language with timeout controls...")

    analyzer = RealTimeAnalyzer()
    supported_languages = ["en", "es", "fr", "de", "zh"]
    language_results = {}

    test_texts = {
        "en": "Hello, how are you?",
        "es": "Hola, ¿cómo estás?",
        "fr": "Bonjour, comment allez-vous?",
        "de": "Hallo, wie geht es dir?",
        "zh": "你好，你怎么样？",
    }

    for lang in supported_languages:
        print(f"\nTesting language: {lang}")

        try:
            # Start session with timeout
            print(f"  Starting session for {lang}...")
            session_id = await asyncio.wait_for(
                analyzer.start_analysis_session("test_user", lang), timeout=10.0
            )
            print(f"  ✅ Session created: {session_id}")

            # Create audio segment
            audio_segment = AudioSegment(
                audio_data=b"fake_audio_data",
                text=test_texts.get(lang, "Hello"),
                start_time=0.0,
                end_time=2.0,
                duration=2.0,
                language=lang,
                confidence=0.9,
            )

            # Analyze with timeout
            print(f"  Analyzing audio for {lang}...")
            start_time = time.time()

            feedback_list = await asyncio.wait_for(
                analyzer.analyze_audio_segment(session_id, audio_segment),
                timeout=30.0,  # 30 second timeout per language
            )

            elapsed = time.time() - start_time
            print(
                f"  ✅ Analysis completed in {elapsed:.2f}s, feedback items: {len(feedback_list)}"
            )

            language_results[lang] = {
                "session_created": True,
                "analysis_completed": True,
                "feedback_count": len(feedback_list),
                "elapsed_time": elapsed,
            }

            # End session
            await analyzer.end_analysis_session(session_id)
            print(f"  ✅ Session ended for {lang}")

        except asyncio.TimeoutError:
            print(f"  ❌ TIMEOUT for {lang}")
            language_results[lang] = {"error": "timeout"}

        except Exception as e:
            print(f"  ❌ ERROR for {lang}: {e}")
            language_results[lang] = {"error": str(e)}

    # Summary
    print("\n📊 RESULTS SUMMARY:")
    successful_languages = []
    for lang, result in language_results.items():
        if "session_created" in result:
            successful_languages.append(lang)
            print(f"  ✅ {lang}: Success ({result.get('elapsed_time', 0):.2f}s)")
        else:
            print(f"  ❌ {lang}: {result.get('error', 'unknown error')}")

    print(
        f"\nSuccessful languages: {len(successful_languages)}/{len(supported_languages)}"
    )
    return len(successful_languages) >= 3


if __name__ == "__main__":
    result = asyncio.run(test_with_timeout())
    print(f"\n🎯 Test Result: {'PASSED' if result else 'FAILED'}")
