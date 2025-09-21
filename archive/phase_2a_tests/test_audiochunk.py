#!/usr/bin/env python3
"""
Debug script to explore AudioChunk structure
"""

import os
from piper import PiperVoice


def explore_audiochunk():
    """Explore AudioChunk structure"""

    model_path = "app/data/piper_voices/en_US-lessac-medium.onnx"
    config_path = "app/data/piper_voices/en_US-lessac-medium.onnx.json"

    print("Loading Piper voice...")
    voice = PiperVoice.load(model_path, config_path)
    print("Voice loaded successfully!")

    text = "Hello test."
    print(f"Synthesizing: '{text}'")

    print("\n=== Exploring AudioChunk structure ===")
    chunks = list(voice.synthesize(text))
    print(f"Generated {len(chunks)} chunks")

    if chunks:
        first_chunk = chunks[0]
        print(f"\nFirst chunk type: {type(first_chunk)}")
        print(f"First chunk attributes: {dir(first_chunk)}")

        for attr in dir(first_chunk):
            if not attr.startswith("_"):
                try:
                    value = getattr(first_chunk, attr)
                    print(
                        f"  {attr}: {type(value)} = {value if not hasattr(value, '__len__') or len(str(value)) < 100 else f'{type(value)} (length: {len(value) if hasattr(value, "__len__") else "unknown"})'}"
                    )
                except Exception as e:
                    print(f"  {attr}: Error getting value - {e}")

    # Try to find the actual audio data
    print("\n=== Trying to extract audio data ===")
    total_audio_bytes = 0
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}:")
        for attr in ["audio", "data", "samples", "wav", "pcm"]:
            if hasattr(chunk, attr):
                val = getattr(chunk, attr)
                print(
                    f"  Has {attr}: {type(val)} - {val if isinstance(val, (str, int, float)) else f'length={len(val) if hasattr(val, "__len__") else "unknown"}'}"
                )
                if hasattr(val, "__len__") and len(val) > 0:
                    total_audio_bytes += (
                        len(val) if isinstance(val, bytes) else len(val) * 4
                    )  # assume float32

    print(f"\nTotal estimated audio bytes: {total_audio_bytes}")


if __name__ == "__main__":
    explore_audiochunk()
