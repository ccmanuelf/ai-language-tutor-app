#!/usr/bin/env python3
"""
Debug script to explore Piper TTS API methods
"""

import os
from piper import PiperVoice


def explore_piper_api():
    """Explore available Piper API methods"""

    model_path = "app/data/piper_voices/en_US-lessac-medium.onnx"
    config_path = "app/data/piper_voices/en_US-lessac-medium.onnx.json"

    print("Loading Piper voice...")
    voice = PiperVoice.load(model_path, config_path)
    print("Voice loaded successfully!")

    print("\n=== PiperVoice object methods and attributes ===")
    for attr in sorted(dir(voice)):
        if not attr.startswith("_"):
            attr_obj = getattr(voice, attr)
            attr_type = type(attr_obj).__name__
            print(f"{attr}: {attr_type}")
            if callable(attr_obj):
                try:
                    doc = attr_obj.__doc__
                    if doc:
                        print(f"    Doc: {doc.strip()}")
                except:
                    pass

    print("\n=== Testing synthesize method with different approaches ===")
    text = "Hello, this is a test."

    # Check if synthesize method exists and how to use it
    if hasattr(voice, "synthesize"):
        print("✓ synthesize method found")
        try:
            print("Checking synthesize method signature...")
            import inspect

            sig = inspect.signature(voice.synthesize)
            print(f"Signature: {sig}")
        except:
            pass

    # Try different approaches
    approaches = [
        ("synthesize", lambda f: voice.synthesize(text, f)),
        (
            "synthesize_stream",
            lambda: voice.synthesize_stream(text)
            if hasattr(voice, "synthesize_stream")
            else None,
        ),
    ]

    for method_name, method_call in approaches:
        print(f"\n--- Testing {method_name} ---")
        try:
            if method_name == "synthesize":
                import tempfile

                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_file:
                    temp_path = temp_file.name

                with open(temp_path, "wb") as wav_file:
                    result = method_call(wav_file)
                    print(f"Result: {result}")

                file_size = os.path.getsize(temp_path)
                print(f"Generated file size: {file_size} bytes")

                if file_size > 0:
                    with (
                        open(temp_path, "rb") as src,
                        open(f"test_{method_name}.wav", "wb") as dst,
                    ):
                        dst.write(src.read())
                    print(f"Audio saved to test_{method_name}.wav")

                os.unlink(temp_path)

            elif method_name == "synthesize_stream":
                result = method_call()
                if result:
                    chunks = list(result)
                    print(f"Generated {len(chunks)} chunks")
                    if chunks:
                        audio_data = b"".join(chunks)
                        print(f"Total audio data: {len(audio_data)} bytes")

                        with open(f"test_{method_name}.wav", "wb") as f:
                            f.write(audio_data)
                        print(f"Raw audio saved to test_{method_name}.wav")
                else:
                    print("No stream method available")

        except Exception as e:
            print(f"Method {method_name} failed: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    explore_piper_api()
