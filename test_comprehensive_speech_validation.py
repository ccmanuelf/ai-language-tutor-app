#!/usr/bin/env python3
"""
COMPREHENSIVE SPEECH VALIDATION TEST
Proper validation methodology with actual audio output verification
"""

import asyncio
import os
import sys
import wave
import numpy as np
from pathlib import Path

sys.path.append(".")

from app.services.speech_processor import SpeechProcessor, AUDIO_LIBS_AVAILABLE


async def comprehensive_speech_validation():
    """Comprehensive validation with actual audio file generation and verification"""

    print("🔬 COMPREHENSIVE SPEECH VALIDATION - PROPER METHODOLOGY")
    print("=" * 70)
    print()

    processor = SpeechProcessor()

    # Create output directory for validation artifacts
    validation_dir = Path("validation_artifacts")
    validation_dir.mkdir(exist_ok=True)

    validation_results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "audio_files_generated": [],
        "critical_issues": [],
    }

    # Test 1: Service Availability Verification
    print("1️⃣ SERVICE AVAILABILITY VERIFICATION")
    print("-" * 40)

    services = {
        "Audio Libraries": AUDIO_LIBS_AVAILABLE,
        "Mistral STT": processor.mistral_stt_available,
        "Piper TTS": processor.piper_tts_available,
        "Watson STT": processor.watson_stt_available,
        "Watson TTS": processor.watson_tts_available,
    }

    for service, available in services.items():
        status = "✅ AVAILABLE" if available else "❌ NOT AVAILABLE"
        print(f"  {service}: {status}")
        if not available and service in ["Audio Libraries", "Piper TTS"]:
            validation_results["critical_issues"].append(f"{service} not available")

    print()

    # Test 2: Voice Activity Detection with Proper Test Audio
    print("2️⃣ VOICE ACTIVITY DETECTION - PROPER TEST SIGNALS")
    print("-" * 55)

    # Create proper test audio samples
    sample_rate = 16000

    # Strong voice signal (440Hz tone at 50% amplitude)
    t = np.linspace(0, 1.0, sample_rate, False)
    strong_voice = np.sin(2 * np.pi * 440 * t) * 0.5
    strong_voice_int16 = (strong_voice * 32767).astype(np.int16)
    strong_voice_bytes = strong_voice_int16.tobytes()

    # Weak voice signal (below threshold)
    weak_voice = np.sin(2 * np.pi * 440 * t) * 0.005  # Very weak
    weak_voice_int16 = (weak_voice * 32767).astype(np.int16)
    weak_voice_bytes = weak_voice_int16.tobytes()

    # Pure silence
    silence = np.zeros(sample_rate, dtype=np.int16)
    silence_bytes = silence.tobytes()

    # Calculate energies for verification
    strong_energy = np.sqrt(
        np.mean((strong_voice_int16.astype(np.float32) / 32767.0) ** 2)
    )
    weak_energy = np.sqrt(np.mean((weak_voice_int16.astype(np.float32) / 32767.0) ** 2))
    silence_energy = np.sqrt(np.mean((silence.astype(np.float32) / 32767.0) ** 2))

    print(f"  Strong Voice Signal:")
    print(f"    Energy: {strong_energy:.6f} (threshold: {processor.vad_threshold})")
    print(
        f"    Expected: TRUE, Actual: {processor.detect_voice_activity(strong_voice_bytes)}"
    )

    print(f"  Weak Voice Signal:")
    print(f"    Energy: {weak_energy:.6f} (threshold: {processor.vad_threshold})")
    print(
        f"    Expected: FALSE, Actual: {processor.detect_voice_activity(weak_voice_bytes)}"
    )

    print(f"  Pure Silence:")
    print(f"    Energy: {silence_energy:.6f} (threshold: {processor.vad_threshold})")
    print(
        f"    Expected: FALSE, Actual: {processor.detect_voice_activity(silence_bytes)}"
    )

    # Validate VAD results
    strong_result = processor.detect_voice_activity(strong_voice_bytes)
    weak_result = processor.detect_voice_activity(weak_voice_bytes)
    silence_result = processor.detect_voice_activity(silence_bytes)

    if strong_result and not weak_result and not silence_result:
        print("  ✅ Voice Activity Detection: PASSED")
        validation_results["tests_passed"] += 1
    else:
        print("  ❌ Voice Activity Detection: FAILED")
        validation_results["tests_failed"] += 1
        validation_results["critical_issues"].append("VAD logic failure")

    print()

    # Test 3: TTS with Actual Audio File Generation - MANDATORY CORE LANGUAGES
    print("3️⃣ TEXT-TO-SPEECH WITH AUDIO FILE VERIFICATION - MANDATORY LANGUAGES")
    print("-" * 68)

    # MANDATORY CORE LANGUAGES as per LANGUAGE_REQUIREMENTS.md
    # ALL 5 languages MUST be validated for completion
    mandatory_test_phrases = [
        ("Hello world, this is a test", "en-US"),  # English (US)
        ("Hola mundo, esto es una prueba", "es-MX"),  # Spanish (MX)
        ("Bonjour le monde, ceci est un test", "fr-FR"),  # French (EU)
        ("Hallo Welt, das ist ein Test", "de-DE"),  # German (DE)
        ("你好世界，这是一个测试", "zh-CN"),  # Chinese (CN)
    ]

    print("🚨 ENFORCING MANDATORY CORE LANGUAGES:")
    print("   1. English (US) - en-US")
    print("   2. Spanish (MX) - es-MX")
    print("   3. French (EU) - fr-FR")
    print("   4. German (DE) - de-DE")
    print("   5. Chinese (CN) - zh-CN")
    print()

    mandatory_languages_passed = 0
    required_languages = len(mandatory_test_phrases)

    for i, (phrase, language) in enumerate(mandatory_test_phrases, 1):
        try:
            print(f'  Test {i}: "{phrase}" ({language})')

            # Generate TTS audio
            result = await processor.process_text_to_speech(
                phrase, language, provider="piper"
            )

            # Save audio file
            filename = f"tts_test_{i}_{language}_{phrase.replace(' ', '_')}.wav"
            filepath = validation_dir / filename

            with open(filepath, "wb") as f:
                f.write(result.audio_data)

            # Verify file was created and has content
            if filepath.exists() and filepath.stat().st_size > 1000:  # At least 1KB
                print(
                    f"    ✅ Generated: {len(result.audio_data)} bytes, {result.duration_seconds:.2f}s"
                )
                print(f"    ✅ Saved to: {filename}")
                validation_results["audio_files_generated"].append(str(filepath))
                validation_results["tests_passed"] += 1
                mandatory_languages_passed += 1
            else:
                print(f"    ❌ File generation failed or too small")
                validation_results["tests_failed"] += 1
                validation_results["critical_issues"].append(
                    f"MANDATORY language {language} TTS failed"
                )

        except Exception as e:
            print(f"    ❌ Error: {e}")
            validation_results["tests_failed"] += 1
            validation_results["critical_issues"].append(
                f"MANDATORY language {language} TTS error: {e}"
            )

    # CRITICAL CHECK: All mandatory languages must pass
    print(f"\n🚨 MANDATORY LANGUAGE VALIDATION:")
    print(f"   Required: {required_languages}/5 core languages")
    print(f"   Achieved: {mandatory_languages_passed}/5 core languages")

    if mandatory_languages_passed < required_languages:
        print(
            f"   ❌ CRITICAL FAILURE: Missing {required_languages - mandatory_languages_passed} mandatory languages"
        )
        validation_results["critical_issues"].append(
            f"CRITICAL: Only {mandatory_languages_passed}/{required_languages} mandatory languages passed"
        )
    else:
        print(f"   ✅ SUCCESS: All {required_languages} mandatory languages validated")

    print()

    # Test 4: Audio File Format Verification
    print("4️⃣ AUDIO FILE FORMAT VERIFICATION")
    print("-" * 35)

    for audio_file in validation_results["audio_files_generated"]:
        try:
            with wave.open(audio_file, "rb") as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                duration = frames / sample_rate

                print(f"  {Path(audio_file).name}:")
                print(
                    f"    Format: {channels}ch, {sample_rate}Hz, {sample_width * 8}bit"
                )
                print(f"    Duration: {duration:.2f}s, Frames: {frames}")

                if sample_rate >= 16000 and duration > 0.5:
                    print(f"    ✅ Valid audio format")
                    validation_results["tests_passed"] += 1
                else:
                    print(f"    ❌ Invalid audio format")
                    validation_results["tests_failed"] += 1

        except Exception as e:
            print(f"    ❌ Format verification failed: {e}")
            validation_results["tests_failed"] += 1

    print()

    # Test 5: Performance Benchmarking
    print("5️⃣ PERFORMANCE BENCHMARKING")
    print("-" * 30)

    import time

    performance_text = (
        "This is a performance benchmark test for text-to-speech synthesis."
    )

    start_time = time.time()
    perf_result = await processor.process_text_to_speech(
        performance_text, "en", provider="piper"
    )
    processing_time = time.time() - start_time

    realtime_factor = processing_time / perf_result.duration_seconds

    print(f"  Processing Time: {processing_time:.2f}s")
    print(f"  Audio Duration: {perf_result.duration_seconds:.2f}s")
    print(f"  Realtime Factor: {realtime_factor:.2f}x")

    if realtime_factor < 1.0:
        print(f"  ✅ Faster than realtime")
        validation_results["tests_passed"] += 1
    elif realtime_factor < 2.0:
        print(f"  ✅ Acceptable performance")
        validation_results["tests_passed"] += 1
    else:
        print(f"  ⚠️  Slower than optimal")
        validation_results["tests_failed"] += 1

    print()

    # Final Results
    print("🎯 COMPREHENSIVE VALIDATION RESULTS")
    print("=" * 40)

    total_tests = (
        validation_results["tests_passed"] + validation_results["tests_failed"]
    )
    success_rate = (
        (validation_results["tests_passed"] / total_tests * 100)
        if total_tests > 0
        else 0
    )

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {validation_results['tests_passed']}")
    print(f"Failed: {validation_results['tests_failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Audio Files Generated: {len(validation_results['audio_files_generated'])}")

    if validation_results["critical_issues"]:
        print(f"\\nCritical Issues:")
        for issue in validation_results["critical_issues"]:
            print(f"  ❌ {issue}")

    print(f"\\nGenerated Audio Files:")
    for audio_file in validation_results["audio_files_generated"]:
        file_size = Path(audio_file).stat().st_size
        print(f"  📁 {Path(audio_file).name} ({file_size:,} bytes)")

    # ENHANCED VALIDATION CRITERIA: Mandatory languages + quality thresholds
    mandatory_languages_satisfied = mandatory_languages_passed >= required_languages
    quality_threshold_met = success_rate >= 90
    no_critical_issues = len(validation_results["critical_issues"]) == 0

    validation_passed = (
        mandatory_languages_satisfied and quality_threshold_met and no_critical_issues
    )

    if validation_passed:
        print(f"\\n🎉 VALIDATION STATUS: PASSED")
        print(f"🎉 All {required_languages} mandatory languages validated")
        print(f"🎉 Speech architecture migration is validated and functional")
        return True
    else:
        print(f"\\n❌ VALIDATION STATUS: FAILED")
        print(
            f"❌ Mandatory Languages: {'✅' if mandatory_languages_satisfied else '❌'} ({mandatory_languages_passed}/{required_languages})"
        )
        print(
            f"❌ Quality Threshold: {'✅' if quality_threshold_met else '❌'} ({success_rate:.1f}% >= 90%)"
        )
        print(
            f"❌ No Critical Issues: {'✅' if no_critical_issues else '❌'} ({len(validation_results['critical_issues'])} issues)"
        )
        print(f"❌ Critical issues must be resolved before production deployment")
        return False


if __name__ == "__main__":
    import asyncio

    success = asyncio.run(comprehensive_speech_validation())
    sys.exit(0 if success else 1)
