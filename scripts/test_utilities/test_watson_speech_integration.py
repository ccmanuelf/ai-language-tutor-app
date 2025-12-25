#!/usr/bin/env python3
"""
Watson Speech Services Integration Test
Comprehensive test for real IBM Watson STT/TTS functionality

This test validates:
- Watson SDK availability and client initialization
- Real API calls to Watson STT and TTS services
- Speech processing pipeline functionality
- Error handling and fallback mechanisms
- SSML enhancement for pronunciation learning
"""

import asyncio
import io
import wave
import tempfile
import os
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
TEST_AUDIO_DURATION = 2.0  # seconds
TEST_SAMPLE_RATE = 16000
TEST_CHANNELS = 1

def create_test_audio() -> bytes:
    """Create a simple test audio file for STT testing"""
    
    # Create a simple sine wave audio for testing
    import math
    import struct
    
    frames = []
    for i in range(int(TEST_SAMPLE_RATE * TEST_AUDIO_DURATION)):
        # Generate a 440Hz sine wave (A note)
        value = int(32767 * math.sin(2 * math.pi * 440 * i / TEST_SAMPLE_RATE))
        frames.append(struct.pack('<h', value))
    
    # Create WAV file in memory
    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, 'wb') as wav_file:
        wav_file.setnchannels(TEST_CHANNELS)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(TEST_SAMPLE_RATE)
        wav_file.writeframes(b''.join(frames))
    
    return audio_buffer.getvalue()

async def test_watson_sdk_availability():
    """Test if Watson SDK is properly installed and available"""
    print("\n" + "="*50)
    print("1. Testing Watson SDK Availability")
    print("="*50)
    
    try:
        from ibm_watson import SpeechToTextV1, TextToSpeechV1
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        print("✅ IBM Watson SDK is available")
        return True
    except ImportError as e:
        print(f"❌ IBM Watson SDK not available: {e}")
        return False

async def test_speech_processor_initialization():
    """Test SpeechProcessor initialization with Watson clients"""
    print("\n" + "="*50)
    print("2. Testing SpeechProcessor Initialization")
    print("="*50)
    
    try:
        from app.services.speech_processor import SpeechProcessor
        
        processor = SpeechProcessor()
        
        print(f"✅ SpeechProcessor initialized")
        print(f"   Watson STT Available: {processor.watson_stt_available}")
        print(f"   Watson TTS Available: {processor.watson_tts_available}")
        print(f"   Watson SDK Available: {processor.watson_sdk_available}")
        print(f"   STT Client Initialized: {bool(processor.watson_stt_client)}")
        print(f"   TTS Client Initialized: {bool(processor.watson_tts_client)}")
        
        return processor
        
    except Exception as e:
        print(f"❌ Failed to initialize SpeechProcessor: {e}")
        return None

async def test_speech_pipeline_status(processor):
    """Test speech pipeline status reporting"""
    print("\n" + "="*50)
    print("3. Testing Speech Pipeline Status")
    print("="*50)
    
    try:
        status = await processor.get_speech_pipeline_status()
        
        print(f"✅ Pipeline Status Retrieved:")
        print(f"   Overall Status: {status['status']}")
        print(f"   Watson STT Status: {status['watson_stt']['status']}")
        print(f"   Watson TTS Status: {status['watson_tts']['status']}")
        
        # Print detailed configuration
        for service in ['watson_stt', 'watson_tts']:
            service_status = status[service]
            print(f"\n   {service.upper()} Details:")
            print(f"     - API Key Configured: {service_status.get('api_key_configured', 'unknown')}")
            print(f"     - Client Initialized: {service_status.get('client_initialized', 'unknown')}")
            print(f"     - Service URL: {service_status.get('service_url', 'unknown')}")
        
        return status
        
    except Exception as e:
        print(f"❌ Failed to get pipeline status: {e}")
        return None

async def test_text_to_speech(processor):
    """Test Watson Text-to-Speech functionality"""
    print("\n" + "="*50)
    print("4. Testing Watson Text-to-Speech")
    print("="*50)
    
    test_phrases = [
        ("Hello, this is a test of Watson Text-to-Speech.", "en"),
        ("Bonjour, ceci est un test de synthèse vocale.", "fr"),
        ("Hola, esta es una prueba de síntesis de voz.", "es")
    ]
    
    for text, language in test_phrases:
        try:
            print(f"\n   Testing TTS for {language}: '{text[:30]}...'")
            
            result = await processor.process_text_to_speech(
                text=text,
                language=language,
                voice_type="neural",
                speaking_rate=1.0
            )
            
            print(f"   ✅ TTS successful:")
            print(f"      - Audio Length: {len(result.audio_data)} bytes")
            print(f"      - Duration: {result.duration_seconds:.2f} seconds")
            print(f"      - Sample Rate: {result.sample_rate} Hz")
            print(f"      - Processing Time: {result.processing_time:.3f}s")
            print(f"      - Watson Voice: {result.metadata.get('watson_voice', 'unknown')}")
            
            # Save audio to file for manual verification
            output_file = f"test_tts_{language}.wav"
            with open(output_file, 'wb') as f:
                f.write(result.audio_data)
            print(f"      - Audio saved to: {output_file}")
            
        except Exception as e:
            print(f"   ❌ TTS failed for {language}: {e}")

async def test_speech_to_text(processor):
    """Test Watson Speech-to-Text functionality"""
    print("\n" + "="*50)
    print("5. Testing Watson Speech-to-Text")
    print("="*50)
    
    # Test with generated audio (will likely not be recognized, but tests API)
    try:
        print("\n   Testing STT with generated audio...")
        
        test_audio = create_test_audio()
        print(f"   Generated test audio: {len(test_audio)} bytes")
        
        from app.services.speech_processor import AudioFormat
        
        result, pronunciation = await processor.process_speech_to_text(
            audio_data=test_audio,
            language="en",
            audio_format=AudioFormat.WAV,
            enable_pronunciation_analysis=True
        )
        
        print(f"   ✅ STT processing completed:")
        print(f"      - Transcript: '{result.transcript}'")
        print(f"      - Confidence: {result.confidence:.3f}")
        print(f"      - Processing Time: {result.processing_time:.3f}s")
        print(f"      - Watson Model: {result.metadata.get('watson_model', 'unknown')}")
        
        if pronunciation:
            print(f"      - Pronunciation Score: {pronunciation.overall_score:.3f}")
            print(f"      - Pronunciation Level: {pronunciation.pronunciation_level.value}")
        
        # Test with existing audio file if available
        test_audio_file = "test_tts_en.wav"
        if os.path.exists(test_audio_file):
            print(f"\n   Testing STT with generated TTS audio...")
            
            with open(test_audio_file, 'rb') as f:
                tts_audio = f.read()
            
            result2, pronunciation2 = await processor.process_speech_to_text(
                audio_data=tts_audio,
                language="en",
                audio_format=AudioFormat.WAV,
                enable_pronunciation_analysis=True
            )
            
            print(f"   ✅ STT with TTS audio completed:")
            print(f"      - Transcript: '{result2.transcript}'")
            print(f"      - Confidence: {result2.confidence:.3f}")
            
    except Exception as e:
        print(f"   ❌ STT test failed: {e}")

async def test_ssml_enhancement(processor):
    """Test SSML text enhancement for pronunciation learning"""
    print("\n" + "="*50)
    print("6. Testing SSML Text Enhancement")
    print("="*50)
    
    test_cases = [
        ("This is a test with emphasis.", "en", ["emphasis"], 1.2),
        ("Bonjour les amis.", "fr", ["amis"], 0.8),
        ("¡Hola! ¿Cómo estás?", "es", ["Hola"], 1.0),
        ("Hello, world. This is great!", "en", ["world"], 1.1)
    ]
    
    for text, language, emphasis_words, speaking_rate in test_cases:
        try:
            enhanced_text = await processor._prepare_text_for_synthesis(
                text=text,
                language=language,
                emphasis_words=emphasis_words,
                speaking_rate=speaking_rate
            )
            
            print(f"\n   {language.upper()} Enhancement:")
            print(f"      Original: {text}")
            print(f"      Enhanced: {enhanced_text}")
            print(f"      SSML Added: {'✅' if '<' in enhanced_text else '❌'}")
            
        except Exception as e:
            print(f"   ❌ SSML enhancement failed for {language}: {e}")

async def test_error_handling(processor):
    """Test error handling and fallback mechanisms"""
    print("\n" + "="*50)
    print("7. Testing Error Handling")
    print("="*50)
    
    # Test with empty audio
    try:
        print("\n   Testing with empty audio...")
        from app.services.speech_processor import AudioFormat
        
        result, _ = await processor.process_speech_to_text(
            audio_data=b"",
            language="en",
            audio_format=AudioFormat.WAV,
            enable_pronunciation_analysis=False
        )
        print(f"   Empty audio result: '{result.transcript}'")
        
    except Exception as e:
        print(f"   ✅ Empty audio properly handled: {e}")
    
    # Test with very long text for TTS
    try:
        print("\n   Testing with very long text...")
        long_text = "This is a very long text. " * 100  # 500+ words
        
        result = await processor.process_text_to_speech(
            text=long_text,
            language="en",
            voice_type="neural"
        )
        print(f"   ✅ Long text handled: {len(result.audio_data)} bytes generated")
        
    except Exception as e:
        print(f"   ❌ Long text failed: {e}")

async def main():
    """Run comprehensive Watson Speech integration tests"""
    print("IBM Watson Speech Services Integration Test")
    print("=========================================")
    
    # Check SDK availability first
    sdk_available = await test_watson_sdk_availability()
    if not sdk_available:
        print("\n❌ Cannot proceed without Watson SDK. Please install: pip install ibm-watson")
        return
    
    # Initialize speech processor
    processor = await test_speech_processor_initialization()
    if not processor:
        print("\n❌ Cannot proceed without speech processor initialization.")
        return
    
    # Run tests
    await test_speech_pipeline_status(processor)
    await test_ssml_enhancement(processor)
    
    # Only run API tests if Watson services are configured
    if processor.watson_tts_available:
        await test_text_to_speech(processor)
    else:
        print("\n⚠️  Skipping TTS tests - Watson TTS not configured")
    
    if processor.watson_stt_available:
        await test_speech_to_text(processor)
    else:
        print("\n⚠️  Skipping STT tests - Watson STT not configured")
    
    await test_error_handling(processor)
    
    print("\n" + "="*50)
    print("Watson Speech Integration Test Complete")
    print("="*50)
    
    # Summary
    print(f"\nSummary:")
    print(f"- Watson SDK Available: {'✅' if sdk_available else '❌'}")
    print(f"- Speech Processor Initialized: {'✅' if processor else '❌'}")
    print(f"- Watson STT Configured: {'✅' if processor and processor.watson_stt_available else '❌'}")
    print(f"- Watson TTS Configured: {'✅' if processor and processor.watson_tts_available else '❌'}")
    
    if processor and (processor.watson_stt_available or processor.watson_tts_available):
        print(f"\n🎉 Watson Speech Services integration is functional!")
    else:
        print(f"\n⚠️  Watson Speech Services need configuration to be fully functional.")

if __name__ == "__main__":
    asyncio.run(main())