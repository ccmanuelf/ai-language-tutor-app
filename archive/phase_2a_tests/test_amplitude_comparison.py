#!/usr/bin/env python3
"""
Compare audio amplitude between direct Piper and speech processor paths
"""

import asyncio
import sys
import wave
import struct
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


async def test_amplitude_comparison():
    """Compare amplitude between direct Piper and speech processor"""

    text = "Hello, this is an amplitude test."

    print("=== Testing Direct Piper TTS Service ===")
    try:
        from app.services.piper_tts_service import PiperTTSService

        piper_service = PiperTTSService()
        audio_data, metadata = await piper_service.synthesize_speech(text, "en")

        print(f"Direct Piper - Audio size: {len(audio_data)} bytes")

        # Save and analyze
        with open("test_direct_piper.wav", "wb") as f:
            f.write(audio_data)

        # Analyze amplitude
        amplitude = analyze_wav_amplitude("test_direct_piper.wav")
        print(f"Direct Piper - Average amplitude: {amplitude:.2f}")

    except Exception as e:
        print(f"Direct Piper failed: {e}")
        return

    print("\n=== Testing Speech Processor Integration ===")
    try:
        from app.services.speech_processor import SpeechProcessor

        processor = SpeechProcessor()
        result = await processor.process_text_to_speech(
            text=text, language="en", provider="piper"
        )

        print(f"Speech Processor - Audio size: {len(result.audio_data)} bytes")

        # Save and analyze
        with open("test_speech_processor.wav", "wb") as f:
            f.write(result.audio_data)

        # Analyze amplitude
        amplitude = analyze_wav_amplitude("test_speech_processor.wav")
        print(f"Speech Processor - Average amplitude: {amplitude:.2f}")

        # Compare metadata
        print(f"Speech Processor metadata: {result.metadata}")

    except Exception as e:
        print(f"Speech Processor failed: {e}")
        import traceback

        traceback.print_exc()


def analyze_wav_amplitude(filename):
    """Analyze WAV file amplitude"""
    try:
        with wave.open(filename, "rb") as wav_file:
            frames = min(1000, wav_file.getnframes())
            raw_audio = wav_file.readframes(frames)

            if wav_file.getsampwidth() == 2:
                samples = struct.unpack(f"{len(raw_audio) // 2}h", raw_audio)
                return sum(abs(s) for s in samples) / len(samples)
    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        return 0.0


if __name__ == "__main__":
    asyncio.run(test_amplitude_comparison())
