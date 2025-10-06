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
                # Language and scenario selection
                Div(
                    H2("Select Language & Practice Mode"),
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
                        Div(
                            Label(
                                "Practice Mode:",
                                style="font-weight: bold; margin-bottom: 0.5rem; display: block;",
                            ),
                            Select(
                                Option("Free Conversation", value="free"),
                                Option("Scenario-Based Practice", value="scenario"),
                                Option("Tutor Modes", value="tutor"),
                                id="practice-mode-select",
                                cls="form-input",
                                style="margin-bottom: 1rem;",
                            ),
                            cls="form-group",
                        ),
                        # Scenario selection (hidden by default)
                        Div(
                            Label(
                                "Choose Scenario:",
                                style="font-weight: bold; margin-bottom: 0.5rem; display: block;",
                            ),
                            Select(
                                Option("Loading scenarios...", value="", disabled=True),
                                id="scenario-select",
                                cls="form-input",
                                style="margin-bottom: 1rem;",
                            ),
                            Button(
                                "📖 View Scenario Details",
                                id="scenario-details-btn",
                                cls="btn btn-outline",
                                style="margin-bottom: 1rem;",
                                disabled=True,
                            ),
                            id="scenario-selection",
                            style="display: none;",
                            cls="form-group",
                        ),
                        # Tutor mode selection (hidden by default)
                        Div(
                            Label(
                                "Choose Tutor Mode:",
                                style="font-weight: bold; margin-bottom: 0.5rem; display: block;",
                            ),
                            Select(
                                Option(
                                    "Loading tutor modes...", value="", disabled=True
                                ),
                                id="tutor-mode-select",
                                cls="form-input",
                                style="margin-bottom: 1rem;",
                            ),
                            # Difficulty selection
                            Div(
                                Label(
                                    "Difficulty Level:",
                                    style="font-weight: bold; margin-bottom: 0.5rem; display: block;",
                                ),
                                Select(
                                    Option("Beginner", value="beginner"),
                                    Option(
                                        "Intermediate",
                                        value="intermediate",
                                        selected=True,
                                    ),
                                    Option("Advanced", value="advanced"),
                                    Option("Expert", value="expert"),
                                    id="difficulty-select",
                                    cls="form-input",
                                    style="margin-bottom: 1rem;",
                                ),
                                cls="form-group",
                            ),
                            # Topic input (for modes that require it)
                            Div(
                                Label(
                                    "Topic (if required):",
                                    style="font-weight: bold; margin-bottom: 0.5rem; display: block;",
                                ),
                                Input(
                                    type="text",
                                    id="tutor-topic-input",
                                    cls="form-input",
                                    placeholder="Enter topic for modes that require it...",
                                    style="margin-bottom: 1rem;",
                                ),
                                cls="form-group",
                            ),
                            Button(
                                "ℹ️ Mode Details",
                                id="tutor-mode-details-btn",
                                cls="btn btn-outline",
                                style="margin-bottom: 1rem;",
                                disabled=True,
                            ),
                            id="tutor-mode-selection",
                            style="display: none;",
                            cls="form-group",
                        ),
                        # Start conversation button
                        Div(
                            Button(
                                "🚀 Start Conversation",
                                id="start-conversation-btn",
                                cls="btn btn-primary",
                                style="width: 100%; padding: 1rem; font-size: 1.1rem;",
                            ),
                            cls="form-group",
                        ),
                        cls="form-group",
                    ),
                    cls="card",
                ),
                # Scenario details modal (hidden by default)
                Div(
                    Div(
                        Div(
                            H3("Scenario Details", style="margin-bottom: 1rem;"),
                            Button(
                                "✕",
                                id="close-modal",
                                cls="btn btn-outline",
                                style="float: right; margin-top: -2rem;",
                            ),
                            Div(
                                id="scenario-details-content",
                                style="clear: both; margin-top: 1rem;",
                            ),
                            cls="modal-content",
                        ),
                        cls="modal-dialog",
                    ),
                    id="scenario-details-modal",
                    cls="modal",
                    style="display: none;",
                ),
                # Tutor mode details modal (hidden by default)
                Div(
                    Div(
                        Div(
                            H3("Tutor Mode Details", style="margin-bottom: 1rem;"),
                            Button(
                                "✕",
                                id="close-tutor-modal",
                                cls="btn btn-outline",
                                style="float: right; margin-top: -2rem;",
                            ),
                            Div(
                                id="tutor-mode-details-content",
                                style="clear: both; margin-top: 1rem;",
                            ),
                            cls="modal-content",
                        ),
                        cls="modal-dialog",
                    ),
                    id="tutor-mode-details-modal",
                    cls="modal",
                    style="display: none;",
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
                # Real-Time Analysis Panel
                Div(
                    H2(
                        "🎯 Real-Time Analysis (Fluently)", style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Div(
                            Button(
                                "🚀 Start Analysis",
                                id="start-analysis-btn",
                                cls="btn btn-success",
                                style="margin-right: 1rem;",
                            ),
                            Button(
                                "⏹️ Stop Analysis",
                                id="stop-analysis-btn",
                                cls="btn btn-danger",
                                style="margin-right: 1rem; display: none;",
                            ),
                            Span(
                                "Analysis ready",
                                id="analysis-status",
                                cls="analysis-status status-info",
                            ),
                            style="margin-bottom: 1rem;",
                        ),
                        # Live Analytics Display
                        Div(
                            H3(
                                "📊 Live Performance Metrics",
                                style="margin-bottom: 0.5rem;",
                            ),
                            Div(
                                id="analytics-display",
                                style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;",
                            ),
                            # Real-time Feedback Feed
                            H3("💡 Live Feedback", style="margin-bottom: 0.5rem;"),
                            Div(
                                id="realtime-feedback",
                                style="""
                                    background: rgba(255,255,255,0.05);
                                    padding: 1rem;
                                    border-radius: 8px;
                                    height: 300px;
                                    overflow-y: auto;
                                    border: 1px solid rgba(255,255,255,0.1);
                                """,
                            ),
                            style="display: none;",
                            id="realtime-panel",
                        ),
                    ),
                    cls="card",
                    style="border: 2px solid var(--accent-color); background: linear-gradient(135deg, rgba(168,85,247,0.1), rgba(59,130,246,0.1));",
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

                // Initialize real-time analysis
                this.initializeRealTimeAnalysis();
                this.silenceTimer = null;
                this.vadInterval = null;
                this.lastSpeechTime = 0;
                this.isProcessingAI = false;
                this.mediaRecorder = null;
                this.audioChunks = [];

                // Scenario-related properties
                this.currentConversationId = null;
                this.isScenarioBased = false;
                this.currentScenario = null;
                this.availableScenarios = [];
                // Tutor mode properties
                this.isTutorMode = false;
                this.currentTutorMode = null;
                this.availableTutorModes = [];
                this.activeTutorSession = null;
                this.conversationStarted = false;

                this.setupEventListeners();
                this.initializeAudioContext();
                this.loadScenarios();
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

                // Practice mode selection
                document.getElementById('practice-mode-select')?.addEventListener('change', (e) => {
                    this.toggleScenarioMode(e.target.value === 'scenario');
                    this.toggleTutorModeSelection(e.target.value === 'tutor');
                });

                // Scenario selection
                document.getElementById('scenario-select')?.addEventListener('change', (e) => {
                    this.selectScenario(e.target.value);
                });

                // Tutor mode selection
                document.getElementById('tutor-mode-select')?.addEventListener('change', (e) => {
                    this.selectTutorMode(e.target.value);
                });

                // Tutor mode details button
                document.getElementById('tutor-mode-details-btn')?.addEventListener('click', () => this.showTutorModeDetails());

                // Tutor modal close button
                document.getElementById('close-tutor-modal')?.addEventListener('click', () => this.closeTutorModal());

                // Start conversation button
                document.getElementById('start-conversation-btn')?.addEventListener('click', () => this.startConversation());

                // Scenario details button
                document.getElementById('scenario-details-btn')?.addEventListener('click', () => this.showScenarioDetails());

                // Modal close button
                document.getElementById('close-modal')?.addEventListener('click', () => this.closeModal());

                // Control buttons
                document.getElementById('clear-button')?.addEventListener('click', () => this.clearConversation());
                document.getElementById('download-audio')?.addEventListener('click', () => this.downloadAudio());
                document.getElementById('pronunciation-analysis')?.addEventListener('click', () => this.analyzePronunciation());

                // Real-time analysis buttons
                document.getElementById('start-analysis-btn')?.addEventListener('click', () => this.startRealTimeAnalysis());
                document.getElementById('stop-analysis-btn')?.addEventListener('click', () => this.stopRealTimeAnalysis());
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

                    let aiResponse;

                    // Route to appropriate service based on conversation mode
                    if (this.isTutorMode && this.activeTutorSession) {
                        // Route to tutor mode
                        aiResponse = await this.sendTutorMessage(userMessage);
                        if (!aiResponse) {
                            throw new Error('Failed to get tutor response');
                        }

                        this.hideLoadingIndicator();
                        this.addMessageToHistory('ai', aiResponse);
                        this.updateSpeechStatus('🎤 Click microphone to speak');

                    } else {
                        // Route to standard conversation API (for free conversation and scenarios)
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

            // Real-Time Analysis Integration
            initializeRealTimeAnalysis() {
                this.analysisSession = null;
                this.analysisWebSocket = null;
                this.realTimeFeedback = [];
                this.analysisEnabled = false;
            }

            async startRealTimeAnalysis() {
                try {
                    const token = localStorage.getItem('auth_token');
                    if (!token) {
                        this.showFeedback('Please log in to use real-time analysis', 'error');
                        return;
                    }

                    const language = this.currentLanguage.split('-')[0]; // Extract language code

                    const response = await fetch('http://localhost:8000/api/realtime/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            language: language,
                            analysis_types: ['comprehensive'],
                            user_preferences: {
                                feedback_frequency: 'medium',
                                correction_level: 'helpful'
                            }
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.analysisSession = data;
                        this.analysisEnabled = true;

                        // Connect WebSocket for real-time feedback
                        this.connectAnalysisWebSocket(data.session_id);

                        this.updateAnalysisStatus('Real-time analysis active', 'success');
                        this.showRealTimePanel(true);

                        console.log('Real-time analysis started:', data);
                    } else {
                        throw new Error(`Failed to start analysis: ${response.statusText}`);
                    }

                } catch (error) {
                    console.error('Error starting real-time analysis:', error);
                    this.updateAnalysisStatus('Failed to start analysis', 'error');
                }
            }

            async stopRealTimeAnalysis() {
                try {
                    if (!this.analysisSession) return;

                    const token = localStorage.getItem('auth_token');
                    const response = await fetch(`http://localhost:8000/api/realtime/end/${this.analysisSession.session_id}`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.ok) {
                        const finalAnalytics = await response.json();
                        this.showAnalyticsSummary(finalAnalytics.final_analytics);
                    }

                } catch (error) {
                    console.error('Error stopping analysis:', error);
                } finally {
                    // Cleanup
                    if (this.analysisWebSocket) {
                        this.analysisWebSocket.close();
                        this.analysisWebSocket = null;
                    }

                    this.analysisSession = null;
                    this.analysisEnabled = false;
                    this.updateAnalysisStatus('Analysis stopped', 'info');
                    this.showRealTimePanel(false);
                }
            }

            connectAnalysisWebSocket(sessionId) {
                const wsUrl = `ws://localhost:8000/api/realtime/ws/${sessionId}`;

                this.analysisWebSocket = new WebSocket(wsUrl);

                this.analysisWebSocket.onopen = () => {
                    console.log('Analysis WebSocket connected');
                };

                this.analysisWebSocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleRealTimeFeedback(data);
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                };

                this.analysisWebSocket.onclose = () => {
                    console.log('Analysis WebSocket disconnected');
                };

                this.analysisWebSocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateAnalysisStatus('Connection error', 'error');
                };
            }

            handleRealTimeFeedback(data) {
                switch (data.type) {
                    case 'realtime_feedback':
                        this.displayRealTimeFeedback(data.feedback);
                        break;
                    case 'analytics_update':
                        this.updateAnalyticsDisplay(data.analytics);
                        break;
                    case 'session_ended':
                        this.showAnalyticsSummary(data.final_analytics);
                        break;
                    case 'connected':
                        console.log('WebSocket connected:', data);
                        break;
                    case 'error':
                        console.error('WebSocket error:', data.message);
                        this.updateAnalysisStatus(data.message, 'error');
                        break;
                }
            }

            async analyzeSpokenText(text, audioData, confidence) {
                if (!this.analysisEnabled || !this.analysisSession) return;

                try {
                    const token = localStorage.getItem('auth_token');

                    // Convert audio to base64 if needed
                    let audioBase64 = audioData;
                    if (audioData instanceof Blob) {
                        audioBase64 = await this.blobToBase64(audioData);
                    }

                    const response = await fetch('http://localhost:8000/api/realtime/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            session_id: this.analysisSession.session_id,
                            audio_data: audioBase64,
                            text: text,
                            confidence: confidence || 0.9,
                            timestamp: new Date().toISOString()
                        })
                    });

                    if (response.ok) {
                        const feedback = await response.json();
                        this.displayRealTimeFeedback(feedback);
                    }

                } catch (error) {
                    console.error('Error analyzing speech:', error);
                }
            }

            displayRealTimeFeedback(feedbackList) {
                if (!feedbackList || feedbackList.length === 0) return;

                const feedbackContainer = document.getElementById('realtime-feedback');
                if (!feedbackContainer) return;

                feedbackList.forEach(feedback => {
                    const feedbackElement = this.createFeedbackElement(feedback);
                    feedbackContainer.appendChild(feedbackElement);

                    // Auto-scroll to latest feedback
                    feedbackContainer.scrollTop = feedbackContainer.scrollHeight;

                    // Store feedback for analytics
                    this.realTimeFeedback.push(feedback);
                });

                // Limit displayed feedback items
                const maxItems = 10;
                while (feedbackContainer.children.length > maxItems) {
                    feedbackContainer.removeChild(feedbackContainer.firstChild);
                }
            }

            createFeedbackElement(feedback) {
                const div = document.createElement('div');
                div.className = `feedback-item priority-${feedback.priority}`;

                const priorityIcon = this.getPriorityIcon(feedback.priority);
                const typeIcon = this.getAnalysisTypeIcon(feedback.analysis_type);

                div.innerHTML = `
                    <div class="feedback-header">
                        <span class="feedback-type">${typeIcon} ${feedback.analysis_type}</span>
                        <span class="feedback-priority">${priorityIcon}</span>
                        <span class="feedback-time">${new Date(feedback.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div class="feedback-message">${feedback.message}</div>
                    ${feedback.correction ? `<div class="feedback-correction">Suggestion: ${feedback.correction}</div>` : ''}
                    ${feedback.explanation ? `<div class="feedback-explanation">${feedback.explanation}</div>` : ''}
                    <div class="feedback-confidence">Confidence: ${Math.round(feedback.confidence * 100)}%</div>
                `;

                return div;
            }

            getPriorityIcon(priority) {
                const icons = {
                    'critical': '🔴',
                    'important': '🟡',
                    'minor': '🟢',
                    'suggestion': '💡'
                };
                return icons[priority] || '📝';
            }

            getAnalysisTypeIcon(type) {
                const icons = {
                    'pronunciation': '🗣️',
                    'grammar': '📝',
                    'fluency': '⚡',
                    'vocabulary': '📚',
                    'comprehensive': '🎯'
                };
                return icons[type] || '📊';
            }

            updateAnalysisStatus(message, type = 'info') {
                const statusElement = document.getElementById('analysis-status');
                if (statusElement) {
                    statusElement.textContent = message;
                    statusElement.className = `analysis-status status-${type}`;
                }
            }

            showRealTimePanel(show) {
                const panel = document.getElementById('realtime-panel');
                if (panel) {
                    panel.style.display = show ? 'block' : 'none';
                }
            }

            updateAnalyticsDisplay(analytics) {
                const analyticsContainer = document.getElementById('analytics-display');
                if (!analyticsContainer) return;

                analyticsContainer.innerHTML = `
                    <div class="analytics-section">
                        <h4>Performance Metrics</h4>
                        <div class="metrics-grid">
                            <div class="metric">
                                <span class="metric-label">Pronunciation</span>
                                <span class="metric-value">${Math.round(analytics.performance_metrics.pronunciation?.average_score || 0)}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Grammar</span>
                                <span class="metric-value">${Math.round(analytics.performance_metrics.grammar?.average_score || 0)}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Fluency</span>
                                <span class="metric-value">${Math.round(analytics.performance_metrics.fluency?.average_score || 0)}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Overall</span>
                                <span class="metric-value">${Math.round(analytics.overall_score || 0)}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="analytics-section">
                        <h4>Session Info</h4>
                        <div class="session-stats">
                            <div>Words spoken: ${analytics.session_info.total_words}</div>
                            <div>Errors found: ${analytics.session_info.total_errors}</div>
                            <div>Duration: ${Math.round(analytics.session_info.duration / 60)}m</div>
                        </div>
                    </div>
                `;
            }

            showAnalyticsSummary(analytics) {
                // Create and show analytics modal
                const modal = document.createElement('div');
                modal.className = 'modal analytics-modal';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Session Analytics Summary</h3>
                            <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
                        </div>
                        <div class="modal-body">
                            ${this.generateAnalyticsSummary(analytics)}
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-primary" onclick="this.closest('.modal').remove()">Close</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);
                modal.style.display = 'block';
            }

            generateAnalyticsSummary(analytics) {
                return `
                    <div class="analytics-summary">
                        <div class="summary-section">
                            <h4>Overall Performance</h4>
                            <div class="score-circle">
                                <span class="score">${Math.round(analytics.overall_score)}%</span>
                            </div>
                        </div>

                        <div class="summary-section">
                            <h4>Detailed Breakdown</h4>
                            <div class="breakdown-grid">
                                <div class="breakdown-item">
                                    <span>Pronunciation</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${analytics.performance_metrics.pronunciation?.average_score || 0}%"></div>
                                    </div>
                                    <span>${Math.round(analytics.performance_metrics.pronunciation?.average_score || 0)}%</span>
                                </div>
                                <div class="breakdown-item">
                                    <span>Grammar</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${analytics.performance_metrics.grammar?.average_score || 0}%"></div>
                                    </div>
                                    <span>${Math.round(analytics.performance_metrics.grammar?.average_score || 0)}%</span>
                                </div>
                                <div class="breakdown-item">
                                    <span>Fluency</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${analytics.performance_metrics.fluency?.average_score || 0}%"></div>
                                    </div>
                                    <span>${Math.round(analytics.performance_metrics.fluency?.average_score || 0)}%</span>
                                </div>
                            </div>
                        </div>

                        <div class="summary-section">
                            <h4>Areas for Improvement</h4>
                            <ul class="improvement-list">
                                ${analytics.improvement_areas.map(area => `<li>${area}</li>`).join('')}
                            </ul>
                        </div>

                        <div class="summary-section">
                            <h4>Session Statistics</h4>
                            <div class="stats-grid">
                                <div class="stat">
                                    <span class="stat-value">${analytics.session_info.total_words}</span>
                                    <span class="stat-label">Words Spoken</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value">${analytics.session_info.total_errors}</span>
                                    <span class="stat-label">Issues Found</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value">${Math.round(analytics.session_info.duration / 60)}</span>
                                    <span class="stat-label">Minutes</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value">${analytics.feedback_summary.total_feedback}</span>
                                    <span class="stat-label">Feedback Items</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }

            blobToBase64(blob) {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const base64 = reader.result.split(',')[1];
                        resolve(base64);
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
            }

            showFeedback(message, type = 'info') {
                // Create temporary feedback message
                const feedback = document.createElement('div');
                feedback.className = `feedback-toast toast-${type}`;
                feedback.textContent = message;
                feedback.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--gradient-primary);
                    color: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    z-index: 1000;
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                `;

                document.body.appendChild(feedback);

                // Animate in
                setTimeout(() => {
                    feedback.style.opacity = '1';
                    feedback.style.transform = 'translateX(0)';
                }, 100);

                // Remove after 3 seconds
                setTimeout(() => {
                    feedback.style.opacity = '0';
                    feedback.style.transform = 'translateX(100%)';
                    setTimeout(() => feedback.remove(), 300);
                }, 3000);
            }

            // Scenario-related methods
            async loadScenarios() {
                try {
                    const token = localStorage.getItem('auth_token');
                    if (!token) return;

                    const response = await fetch('http://localhost:8000/api/v1/scenarios/', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.availableScenarios = data.data.scenarios;
                        this.populateScenarioSelect();
                    }
                } catch (error) {
                    console.error('Failed to load scenarios:', error);
                }
            }

            populateScenarioSelect() {
                const scenarioSelect = document.getElementById('scenario-select');
                if (!scenarioSelect) return;

                scenarioSelect.innerHTML = '<option value="">Select a scenario...</option>';

                this.availableScenarios.forEach(scenario => {
                    const option = document.createElement('option');
                    option.value = scenario.scenario_id;
                    option.textContent = `${scenario.name} (${scenario.difficulty})`;
                    scenarioSelect.appendChild(option);
                });
            }

            toggleScenarioMode(isScenario) {
                this.isScenarioBased = isScenario;
                const scenarioSelection = document.getElementById('scenario-selection');

                if (isScenario) {
                    scenarioSelection.style.display = 'block';
                    if (this.availableScenarios.length === 0) {
                        this.loadScenarios();
                    }
                } else {
                    scenarioSelection.style.display = 'none';
                    this.currentScenario = null;
                }
            }

            selectScenario(scenarioId) {
                this.currentScenario = this.availableScenarios.find(s => s.scenario_id === scenarioId);
                const detailsBtn = document.getElementById('scenario-details-btn');

                if (this.currentScenario) {
                    detailsBtn.disabled = false;
                } else {
                    detailsBtn.disabled = true;
                }
            }

            async showScenarioDetails() {
                if (!this.currentScenario) return;

                try {
                    const token = localStorage.getItem('auth_token');
                    const response = await fetch(`http://localhost:8000/api/v1/scenarios/${this.currentScenario.scenario_id}`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.displayScenarioDetails(data.data);
                        document.getElementById('scenario-details-modal').style.display = 'block';
                    }
                } catch (error) {
                    console.error('Failed to load scenario details:', error);
                }
            }

            displayScenarioDetails(scenarioData) {
                const content = document.getElementById('scenario-details-content');

                content.innerHTML = `
                    <div class="scenario-info">
                        <h4>${scenarioData.name}</h4>
                        <p><strong>Category:</strong> ${scenarioData.category}</p>
                        <p><strong>Difficulty:</strong> ${scenarioData.difficulty}</p>
                        <p><strong>Duration:</strong> ~${scenarioData.duration_minutes} minutes</p>
                        <p><strong>Setting:</strong> ${scenarioData.setting}</p>
                        <p><strong>Description:</strong> ${scenarioData.description}</p>

                        <h5>Learning Goals:</h5>
                        <ul>
                            ${scenarioData.learning_goals.map(goal => `<li>${goal}</li>`).join('')}
                        </ul>

                        <h5>Key Vocabulary:</h5>
                        <div class="vocabulary-tags">
                            ${scenarioData.vocabulary_focus.slice(0, 10).map(word =>
                                `<span class="vocab-tag">${word}</span>`
                            ).join('')}
                        </div>

                        <h5>Conversation Phases:</h5>
                        <ol>
                            ${scenarioData.phases.map(phase =>
                                `<li><strong>${phase.name}</strong> - ${phase.description}</li>`
                            ).join('')}
                        </ol>
                    </div>
                `;
            }

            closeModal() {
                document.getElementById('scenario-details-modal').style.display = 'none';
            }

            // ===== TUTOR MODE METHODS =====

            async toggleTutorModeSelection(isTutorMode) {
                this.isTutorMode = isTutorMode;
                const tutorSelection = document.getElementById('tutor-mode-selection');

                if (isTutorMode) {
                    tutorSelection.style.display = 'block';
                    await this.loadTutorModes();
                } else {
                    tutorSelection.style.display = 'none';
                    this.currentTutorMode = null;
                    this.activeTutorSession = null;
                }
            }

            async loadTutorModes() {
                try {
                    const token = localStorage.getItem('auth_token');
                    const response = await fetch('http://localhost:8000/api/tutor-modes/available', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.availableTutorModes = data;
                        this.populateTutorModeSelect();
                    } else {
                        console.error('Failed to load tutor modes:', response.statusText);
                        this.updateSpeechStatus('❌ Failed to load tutor modes');
                    }
                } catch (error) {
                    console.error('Error loading tutor modes:', error);
                    this.updateSpeechStatus('❌ Error loading tutor modes');
                }
            }

            populateTutorModeSelect() {
                const select = document.getElementById('tutor-mode-select');
                if (!select || !this.availableTutorModes) return;

                // Clear existing options
                select.innerHTML = '<option value="" disabled selected>Select a tutor mode...</option>';

                // Group modes by category
                const categories = {
                    casual: 'Casual Practice',
                    professional: 'Professional Communication',
                    educational: 'Structured Learning'
                };

                Object.entries(categories).forEach(([categoryId, categoryName]) => {
                    const modesInCategory = this.availableTutorModes.filter(mode => mode.category === categoryId);
                    if (modesInCategory.length > 0) {
                        const optgroup = document.createElement('optgroup');
                        optgroup.label = categoryName;

                        modesInCategory.forEach(mode => {
                            const option = document.createElement('option');
                            option.value = mode.mode;
                            option.textContent = mode.name + (mode.requires_topic ? ' (requires topic)' : '');
                            optgroup.appendChild(option);
                        });

                        select.appendChild(optgroup);
                    }
                });
            }

            selectTutorMode(modeId) {
                this.currentTutorMode = this.availableTutorModes?.find(m => m.mode === modeId);
                const detailsBtn = document.getElementById('tutor-mode-details-btn');
                const topicInput = document.getElementById('tutor-topic-input');

                if (this.currentTutorMode) {
                    detailsBtn.disabled = false;

                    // Show/hide topic input based on mode requirements
                    if (this.currentTutorMode.requires_topic) {
                        topicInput.parentElement.style.display = 'block';
                        topicInput.required = true;
                        topicInput.placeholder = `Enter topic for ${this.currentTutorMode.name}...`;
                    } else {
                        topicInput.parentElement.style.display = 'none';
                        topicInput.required = false;
                    }
                } else {
                    detailsBtn.disabled = true;
                    topicInput.parentElement.style.display = 'none';
                }
            }

            async showTutorModeDetails() {
                if (!this.currentTutorMode) return;

                try {
                    const token = localStorage.getItem('auth_token');
                    const response = await fetch(`http://localhost:8000/api/tutor-modes/modes/${this.currentTutorMode.mode}/details`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.displayTutorModeDetails(data);
                        document.getElementById('tutor-mode-details-modal').style.display = 'block';
                    }
                } catch (error) {
                    console.error('Failed to load tutor mode details:', error);
                }
            }

            displayTutorModeDetails(modeData) {
                const content = document.getElementById('tutor-mode-details-content');

                const exampleHtml = modeData.example_interactions?.map(example => `
                    <div class="example-interaction">
                        <div class="user-example"><strong>You:</strong> "${example.user}"</div>
                        <div class="ai-example"><strong>AI Tutor:</strong> "${example.assistant}"</div>
                    </div>
                `).join('') || '';

                content.innerHTML = `
                    <div class="tutor-mode-info">
                        <h4>${modeData.name}</h4>
                        <p class="mode-description">${modeData.description}</p>

                        <div class="mode-details">
                            <div class="detail-section">
                                <h5>📂 Category</h5>
                                <p>${modeData.category.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</p>
                            </div>

                            <div class="detail-section">
                                <h5>🎯 Focus Areas</h5>
                                <ul>${modeData.focus_areas.map(area => `<li>${area}</li>`).join('')}</ul>
                            </div>

                            <div class="detail-section">
                                <h5>✅ Success Criteria</h5>
                                <ul>${modeData.success_criteria.map(criteria => `<li>${criteria}</li>`).join('')}</ul>
                            </div>

                            <div class="detail-section">
                                <h5>🎭 Correction Approach</h5>
                                <p>${modeData.correction_approach.charAt(0).toUpperCase() + modeData.correction_approach.slice(1)}</p>
                            </div>

                            ${modeData.requires_topic ? '<div class="detail-section"><h5>📝 Topic Required</h5><p>This mode requires you to specify a topic</p></div>' : ''}

                            ${exampleHtml ? `<div class="detail-section"><h5>💬 Example Interactions</h5>${exampleHtml}</div>` : ''}
                        </div>
                    </div>
                `;
            }

            closeTutorModal() {
                document.getElementById('tutor-mode-details-modal').style.display = 'none';
            }

            async startTutorSession() {
                if (!this.currentTutorMode) {
                    this.updateSpeechStatus('❌ Please select a tutor mode first');
                    return;
                }

                const language = document.getElementById('language-select').value.split('-')[0];
                const difficulty = document.getElementById('difficulty-select').value;
                const topic = document.getElementById('tutor-topic-input').value.trim();

                // Validate topic if required
                if (this.currentTutorMode.requires_topic && !topic) {
                    this.updateSpeechStatus('❌ This tutor mode requires a topic');
                    return;
                }

                try {
                    const token = localStorage.getItem('auth_token');
                    const response = await fetch('http://localhost:8000/api/tutor-modes/session/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            mode: this.currentTutorMode.mode,
                            language: language,
                            difficulty: difficulty,
                            topic: topic || null
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.activeTutorSession = data;

                        // Add AI's conversation starter
                        this.addMessage('ai', data.conversation_starter);
                        this.updateSpeechStatus(`✅ ${this.currentTutorMode.name} session started!`);

                        return true;
                    } else {
                        const error = await response.json();
                        this.updateSpeechStatus(`❌ Failed to start tutor session: ${error.detail}`);
                        return false;
                    }
                } catch (error) {
                    console.error('Error starting tutor session:', error);
                    this.updateSpeechStatus('❌ Error starting tutor session');
                    return false;
                }
            }

            async sendTutorMessage(message) {
                if (!this.activeTutorSession) {
                    console.error('No active tutor session');
                    return null;
                }

                try {
                    const token = localStorage.getItem('auth_token');
                    const response = await fetch('http://localhost:8000/api/tutor-modes/conversation', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            session_id: this.activeTutorSession.session_id,
                            message: message,
                            context_messages: this.getRecentContext()
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        return data.response;
                    } else {
                        console.error('Failed to send tutor message:', response.statusText);
                        return null;
                    }
                } catch (error) {
                    console.error('Error sending tutor message:', error);
                    return null;
                }
            }

            getRecentContext() {
                // Get last 10 messages for context
                const messages = Array.from(document.querySelectorAll('#conversation-history .message'))
                    .slice(-10)
                    .map(msg => ({
                        role: msg.classList.contains('message-user') ? 'user' : 'assistant',
                        content: msg.textContent.replace(/^(You|AI Tutor):\\s*/, '')
                    }));
                return messages;
            }

            async startConversation() {
                if (this.conversationStarted) {
                    this.updateSpeechStatus('🎤 Conversation already active. Click microphone to speak.');
                    return;
                }

                try {
                    const token = localStorage.getItem('auth_token');
                    if (!token) {
                        this.addMessageToHistory('system', 'Please log in from the Profile page to start conversations.');
                        return;
                    }

                    const language = this.currentLanguage.split('-')[0];

                    if (this.isTutorMode && this.currentTutorMode) {
                        // Start tutor mode session
                        const success = await this.startTutorSession();
                        if (success) {
                            this.conversationStarted = true;
                            // Disable controls
                            document.getElementById('start-conversation-btn').disabled = true;
                            document.getElementById('practice-mode-select').disabled = true;
                            document.getElementById('tutor-mode-select').disabled = true;
                            document.getElementById('difficulty-select').disabled = true;
                        } else {
                            throw new Error('Failed to start tutor mode session');
                        }
                    } else if (this.isScenarioBased && this.currentScenario) {
                        // Start scenario conversation
                        const response = await fetch('http://localhost:8000/api/v1/scenarios/start', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                            },
                            body: JSON.stringify({
                                scenario_id: this.currentScenario.scenario_id,
                                language: language,
                                learning_focus: 'conversation'
                            })
                        });

                        if (response.ok) {
                            const data = await response.json();
                            this.currentConversationId = data.data.conversation_id;
                            this.conversationStarted = true;

                            this.addMessageToHistory('system',
                                `🎬 Started scenario: "${this.currentScenario.name}". You are now in the scenario setting. Let's begin!`
                            );

                            // Disable start button and scenario selection
                            document.getElementById('start-conversation-btn').disabled = true;
                            document.getElementById('practice-mode-select').disabled = true;
                            document.getElementById('scenario-select').disabled = true;
                        } else {
                            throw new Error('Failed to start scenario conversation');
                        }
                    } else {
                        // Start free conversation
                        this.conversationStarted = true;
                        this.addMessageToHistory('system',
                            `🗣️ Free conversation mode started in ${language}. Start speaking or typing!`
                        );

                        // Disable start button
                        document.getElementById('start-conversation-btn').disabled = true;
                        document.getElementById('practice-mode-select').disabled = true;
                    }

                    this.updateSpeechStatus('🎤 Conversation started! Click microphone to speak.');

                } catch (error) {
                    console.error('Failed to start conversation:', error);
                    this.addMessageToHistory('system', 'Failed to start conversation. Please try again.');
                }
            }

            async sendTextMessage() {
                if (!this.conversationStarted) {
                    this.addMessageToHistory('system', 'Please start a conversation first using the "Start Conversation" button.');
                    return;
                }

                const textInput = document.getElementById('text-input');
                const message = textInput.value.trim();

                if (!message) return;

                textInput.value = '';
                this.addMessageToHistory('user', message);
                await this.getAIResponse(message);
            }
        }

        // Initialize conversation manager when page loads
        document.addEventListener('DOMContentLoaded', () => {
            window.conversationManager = new EnhancedConversationManager();
        });
    """)
