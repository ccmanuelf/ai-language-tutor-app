"""
Frontend Chat Route
AI Language Tutor App - AI Conversation Interface

Provides comprehensive conversation interface with:
- Multi-language AI selection
- Speech recognition and synthesis
- Real-time conversation management
- Voice interaction controls
"""

from fasthtml.common import *
from .layout import create_layout


def create_chat_route(app):
    """Create AI conversation interface route"""

    @app.route("/chat")
    def chat():
        """AI conversation practice interface with speech integration"""
        return create_layout(
            Div(
                H1("AI Conversation Practice", style="margin-bottom: 2rem;"),
                # Language selection
                Div(
                    H2("Select Language & AI"),
                    Div(
                        Select(
                            Option("English (Claude)", value="en-claude"),
                            Option("Spanish (Claude)", value="es-claude"),
                            Option("French (Mistral)", value="fr-mistral"),
                            Option("Chinese (Qwen)", value="zh-qwen"),
                            Option("Japanese (Claude)", value="ja-claude"),
                            id="language-select",
                            cls="form-input",
                            style="margin-bottom: 1rem;",
                        ),
                        cls="form-group",
                    ),
                    cls="card",
                ),
                # Conversation area
                Div(
                    H2("Conversation", style="margin-bottom: 1rem;"),
                    Div(
                        Div(
                            Div(
                                Strong("AI Tutor: "),
                                "Hello! I'm your AI language tutor with natural voice interactions! 🎙️ "
                                "• Click the mic once for single recording "
                                "• Hold the mic for 1 second to enable continuous conversation mode "
                                "• Use the 'Continuous' button to toggle always-listening mode "
                                "• Try different languages and I'll adapt my personality and expressions!",
                                cls="message message-ai",
                            ),
                            id="conversation-history",
                        ),
                        cls="conversation-area",
                    ),
                    # Speech controls
                    Div(
                        Button(
                            "🎤",
                            id="mic-button",
                            cls="mic-button",
                            title="Click to speak",
                        ),
                        Span(
                            "Click microphone to speak",
                            id="speech-status",
                            style="font-size: 0.9rem; color: var(--text-secondary);",
                        ),
                        cls="speech-controls",
                    ),
                    # Text input
                    Div(
                        Input(
                            type="text",
                            id="text-input",
                            placeholder="Or type your message here...",
                            cls="form-input",
                            style="margin-bottom: 1rem;",
                        ),
                        Button("Send Message", id="send-button", cls="btn btn-primary"),
                        cls="form-group",
                    ),
                    cls="card",
                ),
                # Conversation controls
                Div(
                    H2("Practice Tools"),
                    Div(
                        Button(
                            "Clear Conversation",
                            cls="btn btn-secondary",
                            id="clear-button",
                        ),
                        Button(
                            "Download Audio",
                            cls="btn btn-secondary",
                            id="download-audio",
                        ),
                        Button(
                            "Pronunciation Analysis",
                            cls="btn btn-secondary",
                            id="pronunciation-analysis",
                        ),
                        style="display: flex; gap: 1rem; flex-wrap: wrap;",
                    ),
                    cls="card",
                ),
                _create_chat_scripts(),
            ),
            current_page="chat",
            title="AI Conversation - AI Language Tutor",
        )


def _create_chat_scripts():
    """Create JavaScript for enhanced conversation management"""
    return Script("""
        class EnhancedConversationManager {
            constructor() {
                this.isRecording = false;
                this.isContinuousMode = false;
                this.currentLanguage = 'en-claude';
                this.conversationHistory = [];
                this.interimTranscript = '';
                this.finalTranscript = '';
                this.silenceTimer = null;
                this.vadInterval = null;
                this.lastSpeechTime = 0;
                this.isProcessingAI = false;
                this.mediaRecorder = null;
                this.audioChunks = [];

                this.setupEventListeners();
                this.initializeAudioContext();
            }

            async initializeAudioContext() {
                try {
                    // Request microphone permission explicitly
                    console.log('Requesting microphone permissions...');

                    const stream = await navigator.mediaDevices.getUserMedia({
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true,
                            sampleRate: 16000
                        }
                    });

                    this.audioStream = stream;
                    this.updateSpeechStatus('🎤 Microphone ready - Click to start speaking');

                    // Initialize MediaRecorder for audio capture
                    this.mediaRecorder = new MediaRecorder(stream, {
                        mimeType: 'audio/webm;codecs=opus'
                    });

                    this.mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            this.audioChunks.push(event.data);
                        }
                    };

                    this.mediaRecorder.onstop = () => {
                        this.processAudioData();
                    };

                } catch (error) {
                    console.error('Audio initialization failed:', error);
                    this.updateSpeechStatus('❌ Microphone access denied. Please enable microphone permissions.');
                }
            }

            setupEventListeners() {
                // Microphone button
                document.getElementById('mic-button')?.addEventListener('click', () => this.toggleRecording());

                // Send button
                document.getElementById('send-button')?.addEventListener('click', () => this.sendTextMessage());

                // Text input enter key
                document.getElementById('text-input')?.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.sendTextMessage();
                });

                // Language selection
                document.getElementById('language-select')?.addEventListener('change', (e) => {
                    this.currentLanguage = e.target.value;
                    this.updateLanguagePersonality();
                });

                // Control buttons
                document.getElementById('clear-button')?.addEventListener('click', () => this.clearConversation());
                document.getElementById('download-audio')?.addEventListener('click', () => this.downloadAudio());
                document.getElementById('pronunciation-analysis')?.addEventListener('click', () => this.analyzePronunciation());
            }

            toggleRecording() {
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    this.startRecording();
                }
            }

            startRecording() {
                if (!this.audioStream) {
                    this.updateSpeechStatus('❌ Microphone not available');
                    return;
                }

                this.isRecording = true;
                this.audioChunks = [];
                this.mediaRecorder.start();

                document.getElementById('mic-button').classList.add('active');
                this.updateSpeechStatus('🔴 Recording... Click again to stop');

                console.log('Started recording');
            }

            stopRecording() {
                if (!this.isRecording) return;

                this.isRecording = false;
                this.mediaRecorder.stop();

                document.getElementById('mic-button').classList.remove('active');
                this.updateSpeechStatus('⏳ Processing speech...');

                console.log('Stopped recording');
            }

            async processAudioData() {
                if (this.audioChunks.length === 0) {
                    this.updateSpeechStatus('🎤 No audio recorded. Click to try again.');
                    return;
                }

                try {
                    // Create audio blob from recorded chunks
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });

                    // Convert to base64 for sending to backend
                    const arrayBuffer = await audioBlob.arrayBuffer();
                    const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

                    // Send to backend for processing
                    await this.sendAudioToBackend(base64Audio);

                } catch (error) {
                    console.error('Audio processing error:', error);
                    this.updateSpeechStatus('❌ Audio processing failed');
                }
            }

            async sendAudioToBackend(audioData) {
                try {
                    // Get authentication token
                    const token = localStorage.getItem('auth_token');

                    if (!token) {
                        this.updateSpeechStatus('❌ Authentication required');
                        return;
                    }

                    const response = await fetch('http://localhost:8000/api/v1/conversations/speech-to-text', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            audio_data: audioData,
                            language: this.currentLanguage.split('-')[0]
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.transcript && data.transcript.trim()) {
                            this.finalTranscript = data.transcript;
                            this.addMessageToHistory('user', this.finalTranscript);
                            await this.getAIResponse(this.finalTranscript);
                        } else {
                            this.updateSpeechStatus('🎤 No speech detected. Try speaking louder.');
                        }
                    } else {
                        const errorData = await response.json();
                        console.error('Speech-to-text error:', errorData);
                        this.updateSpeechStatus('❌ Speech recognition failed');
                    }

                } catch (error) {
                    console.error('Backend communication error:', error);
                    this.updateSpeechStatus('❌ Connection error');
                }
            }

            async sendTextMessage() {
                const textInput = document.getElementById('text-input');
                const message = textInput.value.trim();

                if (!message) return;

                textInput.value = '';
                this.addMessageToHistory('user', message);
                await this.getAIResponse(message);
            }

            async getAIResponse(userMessage) {
                if (this.isProcessingAI) return;

                this.isProcessingAI = true;
                this.showLoadingIndicator();

                try {
                    const token = localStorage.getItem('auth_token');

                    if (!token) {
                        this.addMessageToHistory('system', 'Authentication required. Please log in from the Profile page.');
                        return;
                    }

                    const response = await fetch('http://localhost:8000/api/v1/conversations/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            message: userMessage,
                            language: this.currentLanguage,
                            use_speech: true
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.hideLoadingIndicator();
                        this.addMessageToHistory('ai', data.response);

                        // Play AI response audio if available
                        if (data.audio_data) {
                            this.playAudioResponse(data.audio_data);
                        }

                        this.updateSpeechStatus('🎤 Click microphone to speak');

                    } else {
                        const errorData = await response.json();
                        console.error('AI response error:', errorData);
                        this.hideLoadingIndicator();
                        this.addMessageToHistory('system', 'Sorry, I had trouble understanding. Please try again.');
                        this.updateSpeechStatus('🎤 Click microphone to speak');
                    }

                } catch (error) {
                    console.error('AI response error:', error);
                    this.hideLoadingIndicator();
                    this.addMessageToHistory('system', 'Connection error. Please check your internet connection.');
                    this.updateSpeechStatus('🎤 Click microphone to speak');
                } finally {
                    this.isProcessingAI = false;
                }
            }

            addMessageToHistory(sender, message) {
                const conversationDiv = document.getElementById('conversation-history');

                const messageDiv = document.createElement('div');
                messageDiv.className = `message message-${sender}`;

                const timestamp = new Date().toLocaleTimeString();

                if (sender === 'user') {
                    messageDiv.innerHTML = `
                        <div class="message-content"><strong>You:</strong> ${message}</div>
                        <div class="message-time">${timestamp}</div>
                    `;
                } else if (sender === 'ai') {
                    messageDiv.innerHTML = `
                        <div class="message-content"><strong>AI Tutor:</strong> ${message}</div>
                        <div class="message-time">${timestamp}</div>
                    `;
                } else {
                    messageDiv.innerHTML = `
                        <div class="message-content"><strong>System:</strong> ${message}</div>
                        <div class="message-time">${timestamp}</div>
                    `;
                }

                conversationDiv.appendChild(messageDiv);
                conversationDiv.scrollTop = conversationDiv.scrollHeight;

                // Store in conversation history
                this.conversationHistory.push({ sender, message, timestamp });
            }

            showLoadingIndicator() {
                const conversationDiv = document.getElementById('conversation-history');
                const loadingDiv = document.createElement('div');
                loadingDiv.id = 'loading-indicator';
                loadingDiv.className = 'loading-indicator';
                loadingDiv.innerHTML = `
                    <div class="loading-dots">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                    <span>AI is thinking...</span>
                `;
                conversationDiv.appendChild(loadingDiv);
                conversationDiv.scrollTop = conversationDiv.scrollHeight;
            }

            hideLoadingIndicator() {
                const loadingDiv = document.getElementById('loading-indicator');
                if (loadingDiv) {
                    loadingDiv.remove();
                }
            }

            playAudioResponse(audioData) {
                try {
                    // Convert base64 to audio blob and play
                    const audioBlob = this.base64ToBlob(audioData, 'audio/wav');
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);

                    audio.play().catch(error => {
                        console.error('Audio playback error:', error);
                    });

                    // Clean up URL after playback
                    audio.addEventListener('ended', () => {
                        URL.revokeObjectURL(audioUrl);
                    });

                } catch (error) {
                    console.error('Audio processing error:', error);
                }
            }

            base64ToBlob(base64, contentType) {
                const byteCharacters = atob(base64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                return new Blob([byteArray], { type: contentType });
            }

            updateSpeechStatus(message) {
                const statusElement = document.getElementById('speech-status');
                if (statusElement) {
                    statusElement.textContent = message;
                }
            }

            updateLanguagePersonality() {
                // Add visual indication of language change
                this.addMessageToHistory('system', `Language changed to ${this.currentLanguage}. I'll adapt my responses accordingly!`);
            }

            clearConversation() {
                const conversationDiv = document.getElementById('conversation-history');
                conversationDiv.innerHTML = `
                    <div class="message message-ai">
                        <div class="message-content"><strong>AI Tutor:</strong> Conversation cleared! Ready for a fresh start. 🎯</div>
                        <div class="message-time">${new Date().toLocaleTimeString()}</div>
                    </div>
                `;
                this.conversationHistory = [];
            }

            downloadAudio() {
                // Implementation for downloading conversation audio
                alert('Audio download feature coming soon!');
            }

            analyzePronunciation() {
                // Implementation for pronunciation analysis
                alert('Pronunciation analysis feature coming soon!');
            }
        }

        // Initialize conversation manager when page loads
        document.addEventListener('DOMContentLoaded', () => {
            window.conversationManager = new EnhancedConversationManager();
        });
    """)
