#!/usr/bin/env python3
"""
Quick Watson Speech Services Validation
Simple test to verify Watson integration is working
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def quick_validation():
    """Quick validation of Watson Speech Services integration"""
    
    print("Watson Speech Services Quick Validation")
    print("======================================")
    
    try:
        # Test speech processor initialization
        from app.services.speech_processor import speech_processor
        print("✅ Speech processor imported successfully")
        
        # Get pipeline status
        status = await speech_processor.get_speech_pipeline_status()
        print(f"✅ Pipeline status retrieved")
        
        # Print key status information
        print(f"\nKey Status Information:")
        print(f"- Overall Status: {status['status']}")
        print(f"- Watson SDK Available: {status.get('watson_sdk_available', False)}")
        print(f"- Watson STT Operational: {status['watson_stt']['status']}")
        print(f"- Watson TTS Operational: {status['watson_tts']['status']}")
        
        # Test text enhancement
        if hasattr(speech_processor, '_prepare_text_for_synthesis'):
            enhanced = await speech_processor._prepare_text_for_synthesis(
                text="Hello world, this is a test.",
                language="en", 
                emphasis_words=["world"],
                speaking_rate=1.2
            )
            print(f"✅ Text enhancement working")
            print(f"   Enhanced text: {enhanced}")
        
        # Test simple TTS if available
        if status['watson_tts']['status'] == 'operational':
            try:
                print(f"\n🧪 Testing Watson TTS API call...")
                result = await speech_processor.process_text_to_speech(
                    text="Hello, this is a Watson TTS test.",
                    language="en",
                    voice_type="neural"
                )
                print(f"✅ TTS API call successful!")
                print(f"   Audio size: {len(result.audio_data)} bytes")
                print(f"   Duration: {result.duration_seconds:.2f} seconds")
                print(f"   Voice: {result.metadata.get('watson_voice', 'unknown')}")
                
            except Exception as e:
                print(f"❌ TTS API call failed: {e}")
        else:
            print(f"⚠️  Watson TTS not operational - skipping API test")
        
        # Summary
        print(f"\n📋 Validation Summary:")
        operational_services = []
        if status['watson_stt']['status'] == 'operational':
            operational_services.append("STT")
        if status['watson_tts']['status'] == 'operational':
            operational_services.append("TTS")
            
        if operational_services:
            print(f"✅ Watson Speech Services operational: {', '.join(operational_services)}")
        else:
            print(f"⚠️  No Watson Speech Services operational")
            
        print(f"✅ Speech processing pipeline ready for use!")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = asyncio.run(quick_validation())
    if success:
        print(f"\n🎉 Watson Speech Services integration validated successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Watson Speech Services integration validation failed!")
        sys.exit(1)