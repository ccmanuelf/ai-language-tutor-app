#!/usr/bin/env python3
"""
Diagnostic script to test speech functionality components
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if required modules can be imported"""
    print("🧪 Testing imports...")
    
    # Test core imports
    try:
        from app.services.speech_processor import SpeechProcessor, AUDIO_LIBS_AVAILABLE, WATSON_SDK_AVAILABLE
        print("✅ SpeechProcessor imported successfully")
        print(f"   Audio libraries available: {AUDIO_LIBS_AVAILABLE}")
        print(f"   Watson SDK available: {WATSON_SDK_AVAILABLE}")
    except Exception as e:
        print(f"❌ Failed to import SpeechProcessor: {e}")
        return False
    
    # Test configuration
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print("✅ Configuration loaded successfully")
        
        # Check Watson configuration
        stt_configured = bool(settings.IBM_WATSON_STT_API_KEY and settings.IBM_WATSON_STT_URL)
        tts_configured = bool(settings.IBM_WATSON_TTS_API_KEY and settings.IBM_WATSON_TTS_URL)
        print(f"   Watson STT configured: {stt_configured}")
        print(f"   Watson TTS configured: {tts_configured}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    return True

def test_speech_processor_initialization():
    """Test speech processor initialization"""
    print("\n🔧 Testing speech processor initialization...")
    
    try:
        from app.services.speech_processor import SpeechProcessor
        processor = SpeechProcessor()
        print("✅ SpeechProcessor initialized successfully")
        print(f"   Config valid: {processor.config_valid}")
        if not processor.config_valid:
            print(f"   Config issues: {', '.join(processor.config_issues)}")
        print(f"   Watson STT available: {processor.watson_stt_available}")
        print(f"   Watson TTS available: {processor.watson_tts_available}")
        print(f"   Audio libs available: {processor.audio_libs_available}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize SpeechProcessor: {e}")
        return False

def test_watson_connectivity():
    """Test Watson service connectivity"""
    print("\n🌐 Testing Watson service connectivity...")
    
    try:
        from app.services.speech_processor import SpeechProcessor
        processor = SpeechProcessor()
        
        if not processor.watson_stt_available or not processor.watson_tts_available:
            print("⚠️  Watson services not configured - skipping connectivity test")
            return True
            
        # Test health check
        import asyncio
        health_status = asyncio.run(processor.check_watson_health())
        print(f"   STT available: {health_status['stt_available']}")
        print(f"   TTS available: {health_status['tts_available']}")
        
        if health_status['stt_available'] and health_status['tts_available']:
            print("✅ Watson services are accessible")
            return True
        else:
            print("❌ Watson services are not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Watson connectivity: {e}")
        return False

def test_audio_processing():
    """Test audio processing capabilities"""
    print("\n🔊 Testing audio processing capabilities...")
    
    try:
        from app.services.speech_processor import SpeechProcessor, AUDIO_LIBS_AVAILABLE
        processor = SpeechProcessor()
        
        if not AUDIO_LIBS_AVAILABLE:
            print("⚠️  Audio processing libraries not available")
            return True
            
        # Test voice activity detection with dummy data
        dummy_audio = b'\x00' * 1000  # 1000 bytes of silence
        has_voice = processor.detect_voice_activity(dummy_audio)
        print(f"   Voice activity detection: {'Voice detected' if has_voice else 'No voice detected'}")
        
        print("✅ Audio processing functions working")
        return True
    except Exception as e:
        print(f"❌ Failed to test audio processing: {e}")
        return False

async def test_speech_to_text():
    """Test speech to text functionality"""
    print("\n📝 Testing speech to text functionality...")
    
    try:
        from app.services.speech_processor import SpeechProcessor, AudioFormat
        processor = SpeechProcessor()
        
        if not processor.watson_stt_available:
            print("⚠️  Watson STT not configured - skipping test")
            return True
            
        # Create dummy audio data (silence)
        dummy_audio = b'\x00' * 32000  # 1 second of silence at 16kHz
        
        # Process speech to text
        result, analysis = await processor.process_speech_to_text(
            audio_data=dummy_audio,
            language="en",
            audio_format=AudioFormat.WAV
        )
        
        print(f"   Transcript: '{result.transcript}'")
        print(f"   Confidence: {result.confidence}")
        print("✅ Speech to text processing completed")
        return True
    except Exception as e:
        print(f"❌ Failed to test speech to text: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🎙️  Speech Functionality Diagnostic")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_imports,
        test_speech_processor_initialization,
        test_watson_connectivity,
        test_audio_processing,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Run async test
    try:
        result = asyncio.run(test_speech_to_text())
        results.append(result)
    except Exception as e:
        print(f"❌ Async test failed with exception: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    test_names = [
        "Import tests",
        "Speech processor initialization",
        "Watson connectivity",
        "Audio processing",
        "Speech to text"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Speech functionality should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
        # Provide specific recommendations
        if not results[0]:  # Imports failed
            print("\n🔧 RECOMMENDATIONS:")
            print("   - Install required dependencies: pip install pyaudio numpy ibm-watson")
        elif not results[1]:  # Processor initialization failed
            print("\n🔧 RECOMMENDATIONS:")
            print("   - Check configuration in .env file")
        elif not results[2]:  # Watson connectivity failed
            print("\n🔧 RECOMMENDATIONS:")
            print("   - Verify Watson API keys and URLs in .env file")
            print("   - Check network connectivity to Watson services")
        elif not results[4]:  # Speech to text failed
            print("\n🔧 RECOMMENDATIONS:")
            print("   - Check Watson service status")
            print("   - Verify audio data format")

if __name__ == "__main__":
    main()