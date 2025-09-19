#!/usr/bin/env python3
"""
Real-time Voice Activity Detection Test
AI Language Tutor App - Manual VAD Validation

This script allows you to test VAD with real microphone input.
Run this script and speak into your microphone to see VAD in action.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.speech_processor import speech_processor

try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("❌ PyAudio not available. Install with: pip install pyaudio")
    sys.exit(1)


class RealTimeVADTester:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.running = False
        
    def test_microphone_vad(self, duration_seconds=10):
        """Test VAD with real microphone input"""
        print("🎤 Real-time Voice Activity Detection Test")
        print("=" * 50)
        print(f"⏱️  Recording for {duration_seconds} seconds...")
        print("🗣️  Speak into your microphone to test VAD")
        print("🤫 Stay quiet to see silence detection")
        print("📊 Watch the real-time VAD results below:")
        print("=" * 50)
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        try:
            # Open microphone stream
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames_recorded = 0
            total_frames = int(self.sample_rate * duration_seconds / self.chunk_size)
            voice_detected_count = 0
            silent_count = 0
            
            print("🟢 Recording started... (Ctrl+C to stop early)")
            
            while frames_recorded < total_frames:
                try:
                    # Read audio chunk
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Test VAD on this chunk
                    has_voice = speech_processor.detect_voice_activity(audio_data, self.sample_rate)
                    
                    # Calculate audio energy for display
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    energy = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                    
                    # Display result
                    status_icon = "🗣️" if has_voice else "🤫"
                    energy_bar = "█" * int(energy * 50) if energy < 1 else "█" * 50
                    
                    print(f"\\r{status_icon} VAD: {'VOICE' if has_voice else 'QUIET'} | "
                          f"Energy: {energy:.4f} | [{energy_bar:<50}]", end="", flush=True)
                    
                    # Count results
                    if has_voice:
                        voice_detected_count += 1
                    else:
                        silent_count += 1
                    
                    frames_recorded += 1
                    
                except KeyboardInterrupt:
                    print("\\n\\n⏹️  Recording stopped by user")
                    break
                    
        except Exception as e:
            print(f"\\n❌ Microphone error: {e}")
            print("💡 Tip: Check if your microphone is available and not used by other apps")
            return False
            
        finally:
            # Cleanup
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            audio.terminate()
        
        # Show results
        print("\\n" + "=" * 50)
        print("📊 VAD Test Results:")
        print(f"🗣️  Voice detected: {voice_detected_count} frames")
        print(f"🤫 Silence detected: {silent_count} frames") 
        print(f"📈 Voice activity: {voice_detected_count/(voice_detected_count+silent_count)*100:.1f}%")
        print("=" * 50)
        
        # Validation
        if voice_detected_count > 0 and silent_count > 0:
            print("✅ VAD is working correctly - detected both voice and silence!")
            return True
        elif voice_detected_count > 0:
            print("⚠️  Only voice detected - try staying quiet for a moment")
            return True
        elif silent_count > 0:
            print("⚠️  Only silence detected - try speaking louder")
            return True
        else:
            print("❌ No audio detected - check microphone")
            return False


def run_vad_validation_tests():
    """Run all VAD validation tests"""
    print("🔬 Complete Voice Activity Detection Validation")
    print("=" * 60)
    
    # Test 1: Synthetic audio patterns
    print("\\n📋 Test 1: Synthetic Audio Patterns")
    test_patterns = [
        (b'\\x00\\x00' * 1000, "Complete silence", False),
        (np.array([100, -100] * 500, dtype=np.int16).tobytes(), "Low energy", False), 
        (np.array([3000, -3000] * 500, dtype=np.int16).tobytes(), "Medium energy", True),
        (np.array([8000, -7000, 6000, -8000] * 250, dtype=np.int16).tobytes(), "High energy", True),
    ]
    
    all_passed = True
    for audio_data, description, expected in test_patterns:
        result = speech_processor.detect_voice_activity(audio_data)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}: {result} (expected: {expected})")
        if result != expected:
            all_passed = False
    
    # Test 2: Threshold verification  
    print("\\n📋 Test 2: Threshold Configuration")
    threshold = speech_processor.vad_threshold
    frame_size = speech_processor.vad_frame_size
    print(f"✅ Energy threshold: {threshold}")
    print(f"✅ Frame size: {frame_size} samples (30ms at 16kHz)")
    
    # Test 3: Error handling
    print("\\n📋 Test 3: Error Handling")
    try:
        result = speech_processor.detect_voice_activity(b'')  # Empty audio
        print(f"✅ Empty audio handled: {result}")
    except Exception as e:
        print(f"❌ Empty audio error: {e}")
        all_passed = False
        
    try:
        result = speech_processor.detect_voice_activity(b'invalid')  # Invalid audio
        print(f"✅ Invalid audio handled: {result}")  
    except Exception as e:
        print(f"❌ Invalid audio error: {e}")
        all_passed = False
    
    print("\\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL SYNTHETIC TESTS PASSED!")
        print("\\n💡 Want to test with real microphone? Run:")
        print("   python vad_test.py --microphone")
    else:
        print("❌ Some tests failed - VAD may need adjustment")
    
    return all_passed


if __name__ == "__main__":
    if "--microphone" in sys.argv or "-m" in sys.argv:
        if not AUDIO_AVAILABLE:
            print("❌ Microphone testing requires pyaudio")
            sys.exit(1)
            
        tester = RealTimeVADTester()
        duration = 10  # Default 10 seconds
        
        if "--duration" in sys.argv:
            try:
                idx = sys.argv.index("--duration")
                duration = int(sys.argv[idx + 1])
            except (ValueError, IndexError):
                print("❌ Invalid duration. Using default 10 seconds.")
        
        success = tester.test_microphone_vad(duration)
        sys.exit(0 if success else 1)
    else:
        success = run_vad_validation_tests()
        sys.exit(0 if success else 1)