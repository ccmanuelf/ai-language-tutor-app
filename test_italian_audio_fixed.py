#!/usr/bin/env python3

import asyncio
import os
import sys
import numpy as np
import soundfile as sf
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from services.piper_tts_service import PiperTTSService


async def test_italian_audio_fixed():
    """Test Italian TTS with the new medium quality voice model (it_IT-paola-medium)"""

    print("🇮🇹 Testing Italian TTS with Medium Quality Voice (it_IT-paola-medium)")
    print("=" * 70)

    try:
        # Initialize Piper TTS service
        piper_service = PiperTTSService()

        # Italian test text
        italian_text = "Ciao! Benvenuto nell'applicazione di tutoring linguistico. Come stai oggi? Questo è un test della qualità audio italiana."

        print(f"📝 Text: {italian_text}")
        print(f"🔊 Language: Italian (it)")
        print("🎯 Expected Voice: it_IT-paola-medium")

        # Generate speech
        print("\n⏳ Generating Italian speech with medium quality voice...")
        audio_bytes, metadata = await piper_service.synthesize_speech(
            text=italian_text, language="it"
        )

        if audio_bytes and len(audio_bytes) > 0:
            # Save the audio file
            output_file = "test_italian_fixed.wav"
            with open(output_file, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Italian audio generated successfully!")
            print(f"📁 Audio file saved: {output_file}")
            print(f"📊 File size: {len(audio_bytes):,} bytes")
            print(f"🎤 Voice used: {metadata.get('voice', 'it_IT-paola-medium')}")

            # Audio quality analysis by reading the saved WAV file
            audio_data, sample_rate = sf.read(output_file)

            # Calculate RMS and peak levels
            rms = np.sqrt(np.mean(audio_data**2))
            peak = np.max(np.abs(audio_data))

            print(f"🔉 Audio Analysis:")
            print(f"   • RMS Level: {rms:.4f}")
            print(f"   • Peak Level: {peak:.4f}")
            print(f"   • Sample Rate: {sample_rate} Hz")
            print(f"   • Voice Model: it_IT-paola-medium (Medium Quality)")

            print(f"\n🎧 Please play '{output_file}' to validate:")
            print("   • Clarity: Should be clear without static/white noise")
            print("   • Naturalness: Should sound more natural than previous version")
            print("   • Pronunciation: Italian pronunciation should be accurate")
            print("   • Quality: No background static or distortion")

            return True

        else:
            print(f"❌ Failed to generate Italian speech")
            print(f"   Error: No audio data generated")
            return False

    except Exception as e:
        print(f"❌ Error during Italian audio test: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_italian_audio_fixed())
    if success:
        print(f"\n🎯 ITALIAN AUDIO TEST COMPLETED")
        print(
            f"📋 Please validate the audio quality and report if the static/white noise issue is resolved."
        )
    else:
        print(f"\n❌ ITALIAN AUDIO TEST FAILED")
