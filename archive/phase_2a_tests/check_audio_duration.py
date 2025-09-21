#!/usr/bin/env python3
"""
Check duration and properties of both audio files
"""

import wave
import os


def analyze_audio_file(filename):
    """Analyze audio file properties"""
    print(f"\n=== {filename} ===")

    if not os.path.exists(filename):
        print(f"File does not exist: {filename}")
        return

    file_size = os.path.getsize(filename)
    print(f"File size: {file_size:,} bytes")

    try:
        with wave.open(filename, "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            channels = wav.getnchannels()
            width = wav.getsampwidth()

            duration = frames / rate

            print(f"Frames: {frames:,}")
            print(f"Sample rate: {rate} Hz")
            print(f"Channels: {channels}")
            print(f"Sample width: {width} bytes")
            print(f"Duration: {duration:.3f} seconds")
            print(
                f"Calculated size: {frames * channels * width + 44} bytes (including WAV header)"
            )

    except Exception as e:
        print(f"Error reading WAV file: {e}")


# Analyze both files
analyze_audio_file("test_direct_piper.wav")
analyze_audio_file("test_speech_processor.wav")

# Also check if system volume is configured
print("\n=== System Audio Check ===")
print("If you cannot hear the audio files, please check:")
print("1. System volume is not muted")
print("2. Output device is set correctly")
print("3. Try: osascript -e 'set volume output volume 50'")
