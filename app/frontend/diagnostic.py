"""
Frontend Diagnostic Route
AI Language Tutor App - System Testing and Diagnostics

Provides comprehensive testing interface for:
- Browser compatibility checks
- Microphone permissions
- Text messaging functionality
- Speech recognition testing
"""

from fasthtml.common import *


def create_diagnostic_route(app):
    """Create diagnostic testing route"""

    @app.route("/test")
    def test_diagnostics():
        """Diagnostic page to test basic functionality"""
        return Html(
            Head(
                Title("AI Language Tutor - Diagnostics"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Style("""
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
                    .success { color: green; font-weight: bold; }
                    .error { color: red; font-weight: bold; }
                    .warning { color: orange; font-weight: bold; }
                    button { padding: 10px 20px; margin: 10px; font-size: 16px; }
                    input[type="text"] { padding: 10px; width: 300px; margin: 10px; }
                    #log { background: #f5f5f5; padding: 10px; height: 200px; overflow-y: scroll; font-family: monospace; }
                """),
            ),
            Body(
                H1("🔧 AI Language Tutor - Diagnostic Tests"),
                Div(
                    H2("1. 📱 Basic Browser Support"),
                    P("Checking...", id="browser-support"),
                    cls="test-section",
                ),
                Div(
                    H2("2. 🎤 Microphone Permissions"),
                    Button(
                        "Request Microphone Permission",
                        onclick="requestMicPermission()",
                    ),
                    P("Click button to test", id="mic-status"),
                    cls="test-section",
                ),
                Div(
                    H2("3. 💬 Text Message Test"),
                    Input(
                        type="text",
                        id="test-message",
                        placeholder="Type a test message here...",
                        value="Hello! This is a test message.",
                    ),
                    Button("Send Test Message", onclick="sendTestMessage()"),
                    P("Type a message and click send", id="text-status"),
                    cls="test-section",
                ),
                Div(
                    H2("4. 🗣️ Speech Recognition Test"),
                    Button(
                        "Test Speech Recognition", onclick="testSpeechRecognition()"
                    ),
                    P(
                        "Click to test backend IBM Watson speech recognition",
                        id="speech-status",
                    ),
                    cls="test-section",
                ),
                Div(
                    H2("🪵 Debug Log"),
                    Div(id="log"),
                    Button("Clear Log", onclick="clearLog()"),
                    cls="test-section",
                ),
                Div(
                    H2("🚀 Next Steps"),
                    P("Once tests pass, try the chat interface:"),
                    A(
                        "Go to Chat Interface",
                        href="/chat",
                        style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;",
                    ),
                    cls="test-section",
                ),
                _create_diagnostic_scripts(),
            ),
        )


def _create_diagnostic_scripts():
    """Create JavaScript for diagnostic testing functionality"""
    return Script("""
        // Global token storage
        window.authToken = localStorage.getItem('auth_token') || null;

        function log(message) {
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${timestamp}] ${message}<br>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }

        function updateStatus(id, message, type = 'success') {
            const element = document.getElementById(id);
            element.textContent = message;
            element.className = type;
        }

        // Function to get or refresh authentication token
        async function getAuthToken() {
            // If we already have a valid token, use it
            if (window.authToken) {
                return window.authToken;
            }

            try {
                // Try to login to get a new token
                const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: 'demo-user',
                        password: ''
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    window.authToken = data.access_token;
                    localStorage.setItem('auth_token', window.authToken);
                    log('✅ Authentication token obtained');
                    return window.authToken;
                } else {
                    log(`❌ Authentication failed: ${response.status}`);
                    return null;
                }
            } catch (error) {
                log(`❌ Authentication error: ${error.message}`);
                return null;
            }
        }

        // 1. Check browser support
        function checkBrowserSupport() {
            const features = {
                'Web Audio API': 'AudioContext' in window || 'webkitAudioContext' in window,
                'Media Devices': 'mediaDevices' in navigator,
                'Fetch API': 'fetch' in window
            };

            let supportMessage = '';
            let allSupported = true;

            for (const [feature, supported] of Object.entries(features)) {
                const status = supported ? '✅' : '❌';
                supportMessage += `${status} ${feature} `;
                if (!supported) allSupported = false;
                log(`${feature}: ${supported ? 'Supported' : 'Not supported'}`);
            }

            updateStatus('browser-support', supportMessage, allSupported ? 'success' : 'warning');
        }

        // 2. Request microphone permission
        async function requestMicPermission() {
            try {
                log('Requesting microphone permission...');
                updateStatus('mic-status', 'Requesting permission...', 'warning');

                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                log('Microphone permission granted!');
                updateStatus('mic-status', '✅ Microphone permission granted!', 'success');

                // Stop the stream since we just wanted permission
                stream.getTracks().forEach(track => track.stop());

            } catch (error) {
                log(`Microphone permission error: ${error.message}`);
                updateStatus('mic-status', `❌ Permission denied: ${error.message}`, 'error');
            }
        }

        // 3. Test text messaging
        async function sendTestMessage() {
            const message = document.getElementById('test-message').value.trim();
            if (!message) {
                updateStatus('text-status', '❌ Please enter a message', 'error');
                return;
            }

            try {
                // Get authentication token
                const token = await getAuthToken();
                if (!token) {
                    updateStatus('text-status', '❌ Authentication failed', 'error');
                    return;
                }

                log(`Sending test message: "${message}"`);
                updateStatus('text-status', 'Sending message...', 'warning');

                const response = await fetch('http://localhost:8000/api/v1/conversations/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        message: message,
                        language: 'en-claude',
                        use_speech: false
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    log(`✅ API Response: "${data.response.substring(0, 100)}..."`);
                    updateStatus('text-status', '✅ Text messaging works!', 'success');
                } else {
                    const errorText = await response.text();
                    log(`❌ API Error: ${response.status} - ${errorText}`);
                    updateStatus('text-status', `❌ API Error: ${response.status}`, 'error');
                }

            } catch (error) {
                log(`❌ Text message error: ${error.message}`);
                updateStatus('text-status', `❌ Error: ${error.message}`, 'error');
            }
        }

        // 4. Test speech recognition
        async function testSpeechRecognition() {
            try {
                // Get authentication token
                const token = await getAuthToken();
                if (!token) {
                    updateStatus('speech-status', '❌ Authentication failed', 'error');
                    return;
                }

                log('Testing backend IBM Watson speech recognition...');
                updateStatus('speech-status', '🎤 Testing backend speech recognition...', 'warning');

                // Test the backend endpoint with proper request format
                // For testing purposes, we'll send a minimal valid request
                const response = await fetch('http://localhost:8000/api/v1/conversations/speech-to-text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        language: 'en'
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    log(`✅ Backend speech recognition test: ${JSON.stringify(data)}`);
                    updateStatus('speech-status', '✅ Backend IBM Watson speech recognition ready!', 'success');
                } else {
                    const errorText = await response.text();
                    log(`❌ Backend speech recognition error: ${response.status} - ${errorText}`);
                    updateStatus('speech-status', `❌ Backend speech recognition error: ${response.status}`, 'error');
                }

            } catch (error) {
                log(`❌ Backend speech recognition test failed: ${error.message}`);
                updateStatus('speech-status', `❌ Error: ${error.message}`, 'error');
            }
        }

        // Initialize tests on page load
        document.addEventListener('DOMContentLoaded', () => {
            log('Diagnostic page loaded');
            checkBrowserSupport();
        });
    """)
