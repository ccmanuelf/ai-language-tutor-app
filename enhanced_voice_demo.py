#!/usr/bin/env python3
"""
Enhanced Voice Interaction Demo & Test Script
==============================================

This script demonstrates the new natural voice interaction features inspired by IBM Watson best practices:

🎯 NEW FEATURES IMPLEMENTED:

1. 🎙️ CONTINUOUS CONVERSATION MODE
   - Always-listening mode with smart voice activity detection
   - Natural turn-taking like real human conversations
   - No need to click microphone repeatedly

2. 🚫 INTERRUPTION HANDLING  
   - Users can interrupt AI while it's speaking
   - Natural conversation flow with real-time responses
   - Smart detection of when user wants to speak

3. 🧠 ENHANCED VOICE ACTIVITY DETECTION (VAD)
   - Real-time audio analysis using Web Audio API
   - Smart silence detection with configurable thresholds
   - Automatic processing when user finishes speaking

4. 🎭 NATURAL SPEECH SYNTHESIS
   - Enhanced TTS with emotional expressions
   - Preferred neural voices for more human-like speech
   - Language-specific voice settings and cadence

5. 📞 REAL-TIME SPEECH RECOGNITION
   - Continuous listening with interim results
   - Live transcription display for better UX
   - Enhanced error handling and recovery

6. 🌐 MULTI-MODAL INTERACTION
   - Seamless switching between voice and text
   - Language-specific optimizations
   - Enhanced fallback responses

USAGE INSTRUCTIONS:
==================

1. Ensure both servers are running:
   - Backend: python run_backend.py (port 8000)
   - Frontend: python run_frontend.py (port 3000)

2. Open browser to http://localhost:3000/chat

3. Try these interaction modes:
   📱 SINGLE RECORDING: Click microphone once
   🔄 CONTINUOUS MODE: Hold microphone for 1 second OR click "Continuous" button
   ⏹️ STOP: Click microphone again or "Stop" button
   ✋ INTERRUPT: Start speaking while AI is talking

4. Test different languages to see personality changes:
   - English: Alex (enthusiastic, casual)
   - Spanish: María (expressive, Mexican expressions)
   - French: Sophie (Parisian, sophisticated)
   - Chinese: 小李 (Beijing, warm)

TECHNICAL IMPROVEMENTS:
======================

✅ Web Audio API Integration: Real-time audio analysis
✅ Voice Activity Detection: Smart start/stop detection  
✅ Continuous Speech Recognition: Always-listening mode
✅ Interruption Handling: Natural conversation flow
✅ Enhanced TTS: Neural voices with emotions
✅ Real-time Transcription: Live feedback during speech
✅ Multi-language Support: Language-specific optimizations
✅ Error Recovery: Graceful handling of audio issues
✅ Conversation Memory: Context-aware responses
✅ Natural Language Processing: Emotional trigger detection

COMPARISON TO PREVIOUS VERSION:
==============================

BEFORE (Basic Web Speech API):
❌ Click-to-talk only
❌ No interruption support  
❌ Basic browser TTS
❌ No voice activity detection
❌ Simple timeout handling
❌ Limited language support

AFTER (Enhanced Natural Interactions):
✅ Continuous conversation mode
✅ Real-time interruption handling
✅ Enhanced neural TTS voices
✅ Smart voice activity detection
✅ Advanced audio processing
✅ Rich language personalities

The voice interactions now feel much more natural and human-like,
similar to modern voice assistants and IBM Watson implementations!
"""

import asyncio
import webbrowser
import time
import requests

def check_servers():
    """Check if both backend and frontend servers are running"""
    print("🔍 Checking server status...")
    
    try:
        # Check backend
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        backend_status = "✅ Running" if backend_response.status_code == 200 else "❌ Error"
    except:
        backend_status = "❌ Not running"
    
    try:
        # Check frontend  
        frontend_response = requests.get("http://localhost:3000/health", timeout=5)
        frontend_status = "✅ Running" if frontend_response.status_code == 200 else "❌ Error"
    except:
        frontend_status = "❌ Not running"
    
    print(f"Backend (port 8000): {backend_status}")
    print(f"Frontend (port 3000): {frontend_status}")
    
    if "❌" in backend_status or "❌" in frontend_status:
        print("\n⚠️  Please start the missing servers:")
        if "❌" in backend_status:
            print("   Backend: python run_backend.py")
        if "❌" in frontend_status:
            print("   Frontend: python run_frontend.py")
        return False
    
    return True

def demo_voice_features():
    """Demonstrate the enhanced voice interaction features"""
    
    print("\n" + "="*70)
    print("🎙️  ENHANCED VOICE INTERACTION DEMO")
    print("="*70)
    
    print("""
🎯 NEW FEATURES TO TEST:

1. 📱 SINGLE RECORDING MODE:
   • Click the microphone button once
   • Speak your message
   • System automatically detects when you stop speaking
   • Processes and responds naturally

2. 🔄 CONTINUOUS CONVERSATION MODE:
   • Hold microphone button for 1 second
   • OR click the "Continuous" button
   • System continuously listens for your voice
   • Natural turn-taking like real conversations
   • Smart voice activity detection

3. ✋ INTERRUPTION HANDLING:
   • Start speaking while AI is talking
   • AI automatically stops and listens to you
   • Natural conversation flow without buttons

4. 🎭 ENHANCED PERSONALITIES:
   • English: Alex (enthusiastic American)
   • Spanish: María (expressive Mexican)  
   • French: Sophie (sophisticated Parisian)
   • Chinese: 小李 (warm Beijing native)

5. 🧠 SMART FEATURES:
   • Real-time voice activity detection
   • Live transcription display
   • Enhanced neural voices
   • Emotional response triggers
   • Conversation memory and context

TRY THESE TEST PHRASES:
======================

English: "I'm so excited about my new job!"
Spanish: "¡Me encanta bailar salsa!"
French: "J'adore la cuisine française!"
Chinese: "我喜欢学习中文！"

INTERRUPTION TEST:
=================
1. Ask AI a long question
2. While AI is responding, start speaking
3. Notice how AI stops immediately and listens

CONTINUOUS MODE TEST:
====================
1. Enable continuous mode
2. Have a natural back-and-forth conversation
3. No need to click buttons - just speak naturally!
""")

def open_demo():
    """Open the demo in browser"""
    print("\n🌐 Opening enhanced voice interaction demo...")
    print("   URL: http://localhost:3000/chat")
    
    try:
        webbrowser.open("http://localhost:3000/chat")
        print("✅ Demo opened in browser!")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print("   Please manually open: http://localhost:3000/chat")

def main():
    """Main demo function"""
    print("""
🎙️  AI Language Tutor - Enhanced Voice Interaction Demo
======================================================

This demo showcases the new natural voice interaction features
inspired by IBM Watson and modern conversational AI systems.

The voice interactions are now significantly more human-like with:
• Continuous conversation mode
• Real-time interruption handling  
• Enhanced neural text-to-speech
• Smart voice activity detection
• Natural conversation personalities
""")
    
    # Check if servers are running
    if not check_servers():
        print("\n❌ Cannot start demo - servers not ready")
        return
    
    # Show feature overview
    demo_voice_features()
    
    # Ask user if they want to open the demo
    response = input("\n🚀 Open the enhanced voice demo in browser? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', '']:
        open_demo()
        
        print("""
🎉 DEMO IS NOW READY!

QUICK START GUIDE:
1. Select a language from the dropdown
2. Try single recording: Click mic once, speak, it auto-processes
3. Try continuous mode: Hold mic for 1 second or click "Continuous"
4. Try interrupting: Start speaking while AI is talking
5. Notice the natural personalities and expressions!

TIPS FOR BEST EXPERIENCE:
• Use Chrome/Edge for best Web Audio API support
• Allow microphone permissions when prompted
• Speak clearly and at normal volume
• Try different languages to see personality changes
• Test interruption feature during AI responses

The voice interactions should now feel much more natural
and human-like compared to the previous version! 🎯
""")
        
        input("\nPress Enter when done testing...")
        
    else:
        print("\n✅ Demo ready at: http://localhost:3000/chat")
        print("   Open manually when ready to test!")

if __name__ == "__main__":
    main()