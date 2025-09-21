#!/usr/bin/env python3
"""
Debug script for Piper TTS issue
"""

import tempfile
import os
from pathlib import Path
from piper import PiperVoice


def test_direct_piper():
    """Test Piper TTS directly"""

    model_path = "app/data/piper_voices/en_US-lessac-medium.onnx"
    config_path = "app/data/piper_voices/en_US-lessac-medium.onnx.json"

    print(f"Model file exists: {os.path.exists(model_path)}")
    print(f"Config file exists: {os.path.exists(config_path)}")

    if not os.path.exists(model_path):
        print("Model file not found!")
        return

    if not os.path.exists(config_path):
        print("Config file not found!")
        return

    print("Loading Piper voice...")
    try:
        voice = PiperVoice.load(model_path, config_path)
        print("Voice loaded successfully!")
        print(f"Voice sample rate: {voice.config.sample_rate}")
        print(f"Voice phoneme type: {voice.config.phoneme_type}")
    except Exception as e:
        print(f"Failed to load voice: {e}")
        return

    # Test synthesis
    text = "Hello, this is a test."
    print(f"Synthesizing: '{text}'")

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        print(f"Writing to temporary file: {temp_path}")

        # Use binary mode for writing WAV file
        with open(temp_path, "wb") as wav_file:
            voice.synthesize(text, wav_file)

        # Check file size
        file_size = os.path.getsize(temp_path)
        print(f"Generated audio file size: {file_size} bytes")

        if file_size > 0:
            # Read and save as test output
            with open(temp_path, "rb") as f:
                audio_data = f.read()

            with open("test_direct_piper.wav", "wb") as f:
                f.write(audio_data)

            print("Success! Audio saved to test_direct_piper.wav")
        else:
            print("WARNING: Generated file is empty!")

    except Exception as e:
        print(f"Synthesis failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass


if __name__ == "__main__":
    test_direct_piper()
