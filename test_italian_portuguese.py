"""
Quick test to verify Italian and Portuguese language support
"""

import asyncio

from app.services.ai_router import EnhancedAIRouter
from app.services.piper_tts_service import PiperTTSService


async def test_italian_conversation():
    """Test Italian conversation"""
    print("\n=== Testing Italian Conversation ===")
    router = EnhancedAIRouter()

    messages = [
        {
            "role": "system",
            "content": "You are an Italian language tutor. Respond in Italian.",
        },
        {"role": "user", "content": "Ciao! Come stai?"},
    ]

    try:
        response = await router.chat(
            messages=messages, provider="ollama", model="llama3.2:latest", language="it"
        )
        print(f"✅ Italian conversation successful!")
        print(f"Response: {response.get('content', '')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Italian conversation failed: {e}")
        return False


async def test_portuguese_conversation():
    """Test Portuguese conversation"""
    print("\n=== Testing Portuguese Conversation ===")
    router = EnhancedAIRouter()

    messages = [
        {
            "role": "system",
            "content": "You are a Portuguese language tutor. Respond in Portuguese.",
        },
        {"role": "user", "content": "Olá! Como está?"},
    ]

    try:
        response = await router.chat(
            messages=messages, provider="ollama", model="llama3.2:latest", language="pt"
        )
        print(f"✅ Portuguese conversation successful!")
        print(f"Response: {response.get('content', '')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Portuguese conversation failed: {e}")
        return False


def test_italian_tts():
    """Test Italian TTS"""
    print("\n=== Testing Italian TTS ===")
    try:
        tts_service = PiperTTSService()

        # Check if Italian voice is available
        voices = tts_service.get_available_voices()
        italian_voices = [v for v in voices if v.get("language") == "it"]

        if italian_voices:
            print(f"✅ Found {len(italian_voices)} Italian voice(s)")
            for voice in italian_voices:
                print(f"  - {voice.get('name')}")

            # Test TTS generation
            audio_data = tts_service.synthesize("Ciao, come stai?", language="it")
            if audio_data and len(audio_data) > 0:
                print(
                    f"✅ Italian TTS generation successful! ({len(audio_data)} bytes)"
                )
                return True
            else:
                print(f"❌ Italian TTS generated empty audio")
                return False
        else:
            print(f"❌ No Italian voices found")
            return False
    except Exception as e:
        print(f"❌ Italian TTS failed: {e}")
        return False


def test_portuguese_tts():
    """Test Portuguese TTS"""
    print("\n=== Testing Portuguese TTS ===")
    try:
        tts_service = PiperTTSService()

        # Check if Portuguese voice is available
        voices = tts_service.get_available_voices()
        portuguese_voices = [v for v in voices if v.get("language") == "pt"]

        if portuguese_voices:
            print(f"✅ Found {len(portuguese_voices)} Portuguese voice(s)")
            for voice in portuguese_voices:
                print(f"  - {voice.get('name')}")

            # Test TTS generation
            audio_data = tts_service.synthesize("Olá, como está?", language="pt")
            if audio_data and len(audio_data) > 0:
                print(
                    f"✅ Portuguese TTS generation successful! ({len(audio_data)} bytes)"
                )
                return True
            else:
                print(f"❌ Portuguese TTS generated empty audio")
                return False
        else:
            print(f"❌ No Portuguese voices found")
            return False
    except Exception as e:
        print(f"❌ Portuguese TTS failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Italian and Portuguese Language Support")
    print("=" * 60)

    results = []

    # Test Italian
    results.append(("Italian Conversation", await test_italian_conversation()))
    results.append(("Italian TTS", test_italian_tts()))

    # Test Portuguese
    results.append(("Portuguese Conversation", await test_portuguese_conversation()))
    results.append(("Portuguese TTS", test_portuguese_tts()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n🎉 All Italian and Portuguese tests PASSED!")
    else:
        print(f"\n⚠️  {len(results) - total_passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())
