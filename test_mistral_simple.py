#!/usr/bin/env python3
"""
Simple Mistral STT Test - Minimal Dependencies
Tests just the Mistral STT service without complex integrations
"""

import asyncio
import sys
import os
import time
import struct

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment")

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))


# Simple test without complex dependencies
def create_minimal_wav():
    """Create minimal valid WAV file for testing"""
    # WAV header for 16-bit mono audio at 16kHz
    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    duration = 1  # 1 second
    num_samples = sample_rate * duration

    # Calculate byte rates
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8

    # Create header
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + num_samples * 2,  # File size - 8
        b"WAVE",
        b"fmt ",
        16,  # Subchunk1Size
        1,  # AudioFormat (PCM)
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        num_samples * 2,
    )

    # Create silent audio data
    audio_data = b"\x00\x00" * num_samples

    return header + audio_data


async def test_mistral_config():
    """Test Mistral configuration"""
    print("🔧 Testing Mistral Configuration...")

    try:
        # Simple config check
        api_key = os.getenv("MISTRAL_API_KEY")
        has_key = bool(api_key)
        key_length = len(api_key) if api_key else 0

        print(f"   Mistral API Key: {'✅ Found' if has_key else '❌ Not found'}")
        if has_key:
            print(f"   Key Length: {key_length} chars")
            print(
                f"   Key Preview: {api_key[:8]}..."
                if key_length > 8
                else "   Key too short"
            )

        return has_key and key_length > 10

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


async def test_mistral_api():
    """Test Mistral API directly"""
    print("\n🚀 Testing Mistral API...")

    try:
        import httpx

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("   ❌ No API key available")
            return False

        # Create simple HTTP client
        async with httpx.AsyncClient() as client:
            # Test API connectivity with a simple request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # Test with a simple models endpoint (if available)
            try:
                response = await client.get(
                    "https://api.mistral.ai/v1/models", headers=headers, timeout=10.0
                )

                if response.status_code == 200:
                    print("   ✅ API connectivity successful")
                    models = response.json()
                    if "data" in models:
                        print(f"   Available models: {len(models['data'])}")
                        # Look for Voxtral models
                        voxtral_models = [
                            m
                            for m in models["data"]
                            if "voxtral" in m.get("id", "").lower()
                        ]
                        if voxtral_models:
                            print(f"   Voxtral models found: {len(voxtral_models)}")
                            # Print the actual model names for debugging
                            print("   Available Voxtral models:")
                            for model in voxtral_models:
                                print(f"     - {model.get('id', 'unknown')}")
                        else:
                            print("   ⚠️  No Voxtral models found in response")
                    return True
                else:
                    print(f"   ❌ API returned status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return False

            except httpx.TimeoutException:
                print("   ❌ API request timed out")
                return False
            except httpx.RequestError as e:
                print(f"   ❌ API request failed: {e}")
                return False

    except ImportError:
        print("   ❌ httpx not available")
        return False
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False


async def test_audio_transcription():
    """Test audio transcription if API is working"""
    print("\n🎤 Testing Audio Transcription...")

    try:
        import httpx
        import io

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("   ❌ No API key available")
            return False

        # Create test audio
        audio_data = create_minimal_wav()
        print(f"   Created test audio: {len(audio_data)} bytes")

        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {api_key}"}

            # Prepare files for upload
            files = {"file": ("test_audio.wav", io.BytesIO(audio_data), "audio/wav")}

            data = {
                "model": "voxtral-mini-latest",
                "language": "en",
                "response_format": "json",
                "temperature": "0.0",
            }

            start_time = time.time()

            try:
                response = await client.post(
                    "https://api.mistral.ai/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                )

                processing_time = time.time() - start_time

                print(f"   Request completed in {processing_time:.2f}s")
                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print("   ✅ Transcription successful!")
                    print(f"   Result: {result}")

                    # Extract transcript
                    transcript = result.get("text", "")
                    confidence = result.get("confidence", 0.0)

                    print(f"   Transcript: '{transcript}'")
                    print(f"   Confidence: {confidence}")

                    return True
                else:
                    print(
                        f"   ❌ Transcription failed with status {response.status_code}"
                    )
                    print(f"   Response: {response.text}")
                    return False

            except httpx.TimeoutException:
                print("   ❌ Transcription request timed out")
                return False
            except Exception as e:
                print(f"   ❌ Transcription request failed: {e}")
                return False

    except ImportError:
        print("   ❌ Required libraries not available")
        return False
    except Exception as e:
        print(f"   ❌ Transcription test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 Simple Mistral STT Test")
    print("=" * 40)

    # Test configuration
    config_ok = await test_mistral_config()

    if not config_ok:
        print("\n❌ Configuration test failed!")
        print("Please ensure MISTRAL_API_KEY is set in your environment")
        return False

    # Test API connectivity
    api_ok = await test_mistral_api()

    # Test transcription if API is working
    transcription_ok = False
    if api_ok:
        transcription_ok = await test_audio_transcription()

    # Summary
    print("\n📊 Test Results")
    print("=" * 20)
    print(f"Configuration: {'✅' if config_ok else '❌'}")
    print(f"API Connectivity: {'✅' if api_ok else '❌'}")
    print(f"Transcription: {'✅' if transcription_ok else '❌'}")

    overall_success = config_ok and api_ok and transcription_ok

    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Mistral STT service is working correctly")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        if not config_ok:
            print("❌ Check your MISTRAL_API_KEY configuration")
        if not api_ok:
            print("❌ Check your API connectivity and key validity")
        if not transcription_ok:
            print("❌ Check transcription endpoint and model availability")

    return overall_success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
