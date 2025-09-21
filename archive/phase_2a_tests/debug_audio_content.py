#!/usr/bin/env python3
"""
Debug script to examine actual audio content in generated WAV files
"""

import wave
import struct
import os


def analyze_wav_file(filename):
    """Analyze WAV file content to check for actual audio data"""

    if not os.path.exists(filename):
        print(f"File {filename} does not exist")
        return

    print(f"\n=== Analyzing {filename} ===")
    print(f"File size: {os.path.getsize(filename)} bytes")

    try:
        with wave.open(filename, "rb") as wav_file:
            # Get WAV file properties
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate

            print(f"Frames: {frames}")
            print(f"Sample rate: {sample_rate} Hz")
            print(f"Channels: {channels}")
            print(f"Sample width: {sample_width} bytes")
            print(f"Duration: {duration:.2f} seconds")

            # Read first 1000 samples to check for audio content
            wav_file.rewind()
            raw_audio = wav_file.readframes(min(1000, frames))

            if sample_width == 1:
                # 8-bit unsigned
                samples = struct.unpack(f"{len(raw_audio)}B", raw_audio)
            elif sample_width == 2:
                # 16-bit signed
                samples = struct.unpack(f"{len(raw_audio) // 2}h", raw_audio)
            else:
                print(f"Unsupported sample width: {sample_width}")
                return

            # Analyze samples
            if len(samples) > 0:
                min_sample = min(samples)
                max_sample = max(samples)
                avg_sample = sum(abs(s) for s in samples) / len(samples)
                non_zero_count = sum(1 for s in samples if s != 0)

                print(f"First 10 samples: {samples[:10]}")
                print(f"Sample range: {min_sample} to {max_sample}")
                print(f"Average absolute amplitude: {avg_sample:.2f}")
                print(
                    f"Non-zero samples: {non_zero_count}/{len(samples)} ({non_zero_count / len(samples) * 100:.1f}%)"
                )

                if avg_sample < 1.0:
                    print(
                        "⚠️  WARNING: Very low amplitude - likely silence or very quiet audio"
                    )
                elif non_zero_count == 0:
                    print("❌ ERROR: All samples are zero - this is complete silence")
                else:
                    print("✅ Audio content detected")
            else:
                print("❌ ERROR: No audio samples found")

    except Exception as e:
        print(f"Error analyzing WAV file: {e}")


def test_system_audio():
    """Test if system audio is working"""
    print("\n=== Testing system audio ===")
    try:
        # Try to generate a simple test tone
        import math
        import wave
        import struct

        # Generate a 1-second 440Hz tone
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0

        frames = int(duration * sample_rate)
        audio_data = []

        for i in range(frames):
            t = i / sample_rate
            sample = int(16383 * math.sin(2 * math.pi * frequency * t))
            audio_data.append(sample)

        # Save test tone
        with wave.open("test_tone.wav", "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack(f"{len(audio_data)}h", *audio_data))

        print("✅ Generated test_tone.wav (440Hz sine wave)")
        print("Try playing: afplay test_tone.wav")

    except Exception as e:
        print(f"Error generating test tone: {e}")


if __name__ == "__main__":
    # Analyze the Piper-generated files
    analyze_wav_file("test_piper_output.wav")
    analyze_wav_file("test_processor_output.wav")

    # Generate a test tone for comparison
    test_system_audio()
