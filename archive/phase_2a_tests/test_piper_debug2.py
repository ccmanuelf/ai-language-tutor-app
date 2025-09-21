#!/usr/bin/env python3
"""
Debug script for Piper TTS issue - try different synthesis approach
"""

import tempfile
import os
import wave
from pathlib import Path
from piper import PiperVoice


def test_piper_synthesis_methods():
    """Test different Piper synthesis approaches"""

    model_path = "app/data/piper_voices/en_US-lessac-medium.onnx"
    config_path = "app/data/piper_voices/en_US-lessac-medium.onnx.json"

    print("Loading Piper voice...")
    voice = PiperVoice.load(model_path, config_path)
    print("Voice loaded successfully!")

    text = "Hello, this is a test."
    print(f"Synthesizing: '{text}'")

    # Method 1: Try to collect audio chunks directly
    print("\n=== Method 1: Collect audio chunks ===")
    try:
        audio_chunks = []
        for audio_chunk in voice.synthesize_stream_raw(text):
            audio_chunks.append(audio_chunk)

        if audio_chunks:
            print(f"Generated {len(audio_chunks)} audio chunks")

            # Combine chunks
            audio_data = b"".join(audio_chunks)
            print(f"Total audio data: {len(audio_data)} bytes")

            # Save raw audio data
            with open("test_raw_audio.wav", "wb") as f:
                f.write(audio_data)
            print("Raw audio saved to test_raw_audio.wav")
        else:
            print("No audio chunks generated")

    except Exception as e:
        print(f"Method 1 failed: {e}")
        import traceback

        traceback.print_exc()

    # Method 2: Try with WAV header
    print("\n=== Method 2: Generate with WAV header ===")
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        # Try using synthesize method with proper WAV handling
        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(voice.config.sample_rate)

            # Get raw audio data
            audio_data = b""
            for audio_chunk in voice.synthesize_stream_raw(text):
                audio_data += audio_chunk

            if audio_data:
                wav_file.writeframes(audio_data)
                print(f"WAV file created with {len(audio_data)} bytes of audio data")
            else:
                print("No audio data to write")

        # Check file size
        file_size = os.path.getsize(temp_path)
        print(f"Generated WAV file size: {file_size} bytes")

        if file_size > 0:
            # Copy to permanent location
            with open(temp_path, "rb") as src, open("test_method2.wav", "wb") as dst:
                dst.write(src.read())
            print("WAV file saved to test_method2.wav")

        os.unlink(temp_path)

    except Exception as e:
        print(f"Method 2 failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_piper_synthesis_methods()
