"""
FastHTML Frontend Server Entry Point
AI Language Tutor App - Personal Family Educational Tool

Modern FastHTML frontend with:
- User authentication and profiles
- AI conversation interface
- Speech input/output
- Multi-language support
- Family-safe design
"""

from fasthtml.common import *
import uvicorn
from pathlib import Path
import asyncio
from datetime import datetime

# Import core configuration and services
from app.core.config import get_settings
from app.database.config import get_primary_db_session
from app.services.speech_processor import speech_processor


# CSS Framework - MonsterUI-inspired components
def load_styles():
    """Load comprehensive CSS styles"""
    return Style("""
    /* AI Language Tutor - Modern UI Styles */
    :root {
        --primary-color: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary-color: #10b981;
        --accent-color: #f59e0b;
        --danger-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: var(--text-primary);
        background-color: var(--bg-secondary);
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }

    .header {
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 0;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }

    .nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        text-decoration: none;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        list-style: none;
    }

    .nav-links a {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }

    .nav-links a:hover {
        color: var(--primary-color);
    }

    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 0.5rem;
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: var(--shadow);
    }

    .btn-primary {
        background: var(--primary-color);
        color: white;
    }

    .btn-primary:hover {
        background: var(--primary-dark);
        box-shadow: var(--shadow-lg);
    }

    .btn-secondary {
        background: var(--bg-primary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
        background: var(--bg-secondary);
    }

    .card {
        background: var(--bg-primary);
        border-radius: 0.75rem;
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }

    .grid {
        display: grid;
        gap: 2rem;
    }

    .grid-2 {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }

    .grid-3 {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-success {
        background: #dcfce7;
        color: #166534;
    }

    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }

    .status-error {
        background: #fee2e2;
        color: #dc2626;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    .form-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: border-color 0.2s;
    }

    .form-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    .speech-controls {
        display: flex;
        gap: 1rem;
        align-items: center;
        justify-content: center;
        margin: 2rem 0;
    }

    .mic-button {
        width: 4rem;
        height: 4rem;
        border-radius: 50%;
        border: none;
        background: var(--secondary-color);
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: var(--shadow-lg);
    }

    .mic-button:hover {
        transform: scale(1.05);
    }

    .mic-button.recording {
        background: var(--danger-color);
        animation: pulse 1s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .conversation-area {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: var(--bg-secondary);
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
    }

    .message {
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 0.75rem;
    }

    .message-user {
        background: var(--primary-color);
        color: white;
        margin-left: 2rem;
        text-align: right;
    }

    .message-ai {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        margin-right: 2rem;
    }

    .loading {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid var(--border-color);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    @media (max-width: 768px) {
        .nav {
            flex-direction: column;
            gap: 1rem;
        }

        .nav-links {
            gap: 1rem;
        }

        .grid-2, .grid-3 {
            grid-template-columns: 1fr;
        }

        .speech-controls {
            flex-wrap: wrap;
        }
    }
    """)


def create_frontend_app():
    """Create and configure comprehensive FastHTML application"""
    settings = get_settings()

    # FastHTML app with enhanced configuration
    app = FastHTML(
        debug=settings.DEBUG,
        static_path=str(Path(__file__).parent / "static"),
        title="AI Language Tutor - Family Educational Tool",
    )

    # Component functions for reusable UI elements
    def create_header(current_page="home"):
        """Create navigation header"""
        return Header(
            Nav(
                A("🎯 AI Language Tutor", href="/", cls="logo"),
                Ul(
                    Li(
                        A(
                            "Home",
                            href="/",
                            cls="active" if current_page == "home" else "",
                        )
                    ),
                    Li(
                        A(
                            "Profile",
                            href="/profile",
                            cls="active" if current_page == "profile" else "",
                        )
                    ),
                    Li(
                        A(
                            "Conversation",
                            href="/chat",
                            cls="active" if current_page == "chat" else "",
                        )
                    ),
                    Li(
                        A(
                            "Progress",
                            href="/progress",
                            cls="active" if current_page == "progress" else "",
                        )
                    ),
                    cls="nav-links",
                ),
                cls="nav",
            ),
            cls="header",
        )

    def create_layout(content, current_page="home", title="AI Language Tutor"):
        """Create consistent page layout"""
        return Html(
            Head(
                Title(title),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                load_styles(),
                Script("""
                // Initialize speech features to use backend Watson services
                window.speechRecognition = null;
                window.speechSynthesis = null;
                window.currentUtterance = null;
                window.isAISpeaking = false;
                window.voiceActivityDetected = false;

                // Audio context for basic audio processing (not speech recognition)
                window.audioContext = null;
                window.microphone = null;
                window.analyser = null;
                window.vadThreshold = 0.02;  // Voice activity detection threshold

                console.log('Speech features initialized to use backend IBM Watson services');
                """),
            ),
            Body(
                create_header(current_page),
                Main(content, cls="container"),
                # Footer
                Footer(
                    Div(
                        P("AI Language Tutor - Personal Family Educational Tool"),
                        P(
                            f"Backend: Operational | Speech: Ready | Database: Connected"
                        ),
                        cls="container",
                        style="text-align: center; padding: 2rem; color: var(--text-secondary); border-top: 1px solid var(--border-color); margin-top: 4rem;",
                    )
                ),
            ),
        )

    # Route: Diagnostic Tests
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
                Script("""
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

                    // 1. Check browser support
                    function checkBrowserSupport() {
                        const features = {
                            'Speech Recognition': 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
                            'Speech Synthesis': 'speechSynthesis' in window,
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
                            log(`Sending test message: "${message}"`);
                            updateStatus('text-status', 'Sending message...', 'warning');

                            const response = await fetch('http://localhost:8000/api/v1/conversations/chat', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Bearer test_token_placeholder'
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
                    function testSpeechRecognition() {
                        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                            updateStatus('speech-status', '❌ Speech recognition not supported', 'error');
                            log('Speech recognition not supported in this browser');
                            return;
                        }

                        try {
                            const recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
                            recognition.continuous = false;
                            recognition.interimResults = false;
                            recognition.lang = 'en-US';

                            updateStatus('speech-status', '🎤 Listening... say something!', 'warning');
                            log('Speech recognition started - please speak');

                            recognition.onresult = (event) => {
                                const transcript = event.results[0][0].transcript;
                                log(`✅ Speech recognized: "${transcript}"`);
                                updateStatus('speech-status', `✅ Heard: "${transcript}"`, 'success');
                            };

                            recognition.onerror = (event) => {
                                log(`❌ Speech recognition error: ${event.error}`);
                                let errorMessage = `❌ Error: ${event.error}`;

                                // Provide specific guidance for common errors
                                switch(event.error) {
                                    case 'network':
                                        errorMessage = '⚠️ Network error - check internet connection or try again';
                                        log('Network error: This may be a temporary issue with Google\'s speech service');
                                        log('Try: 1) Check your internet connection 2) Try again in a minute 3) Use Chrome browser');
                                        log('Alternative: All functionality works with text input - speech is optional');
                                        log('🔧 TROUBLESHOOTING TIPS:');
                                        log('  • Use Chrome or Edge (best Web Speech API support)');
                                        log('  • Check if you can access https://www.google.com');
                                        log('  • Try disabling VPN/firewall temporarily');
                                        log('  • Test on a different network (mobile hotspot)');
                                        log('  • Wait 5-10 minutes and try again');
                                        log('  • All AI features work perfectly with text input');
                                        log('  • See detailed guide: SPEECH_RECOGNITION_NETWORK_ERROR_FIX.md');
                                        break;
                                    case 'no-speech':
                                        errorMessage = '⚠️ No speech detected - try speaking louder';
                                        break;
                                    case 'audio-capture':
                                        errorMessage = '⚠️ Microphone not accessible - check permissions';
                                        break;
                                    case 'not-allowed':
                                        errorMessage = '⚠️ Microphone permission denied';
                                        break;
                                    default:
                                        log(`Speech recognition error details: ${JSON.stringify(event)}`);
                                        break;
                                }

                                updateStatus('speech-status', errorMessage, 'error');
                            };

                            recognition.onend = () => {
                                log('Speech recognition ended');
                            };

                            recognition.start();

                        } catch (error) {
                            log(`❌ Speech recognition initialization error: ${error.message}`);
                            updateStatus('speech-status', `❌ Error: ${error.message}`, 'error');
                        }
                    }

                    // Initialize tests on page load
                    document.addEventListener('DOMContentLoaded', () => {
                        log('Diagnostic page loaded');
                        checkBrowserSupport();
                    });
                """),
            ),
        )

    # Route: Home page
    @app.route("/")
    def home():
        return create_layout(
            Div(
                # Welcome section
                Div(
                    H1(
                        "Welcome to AI Language Tutor",
                        style="text-align: center; margin-bottom: 2rem;",
                    ),
                    P(
                        "Your personal AI-powered language learning companion for the whole family.",
                        style="text-align: center; font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 3rem;",
                    ),
                    cls="card",
                ),
                # System status
                Div(
                    H2("System Status", style="margin-bottom: 1.5rem;"),
                    Div(
                        Div(
                            Span("🎤", style="font-size: 2rem;"),
                            H3("Speech Processing"),
                            Span(
                                "Watson STT/TTS Operational",
                                cls="status-indicator status-success",
                            ),
                            P("Real-time speech recognition and synthesis ready"),
                        ),
                        Div(
                            Span("🤖", style="font-size: 2rem;"),
                            H3("AI Services"),
                            Span(
                                "Claude + Mistral + Qwen Active",
                                cls="status-indicator status-success",
                            ),
                            P("Multi-language AI conversation partners available"),
                        ),
                        Div(
                            Span("🗄️", style="font-size: 2rem;"),
                            H3("Database"),
                            Span(
                                "Multi-DB Architecture Ready",
                                cls="status-indicator status-success",
                            ),
                            P("SQLite + ChromaDB + DuckDB operational"),
                        ),
                        cls="grid grid-3",
                    ),
                    cls="card",
                ),
                # Quick actions
                Div(
                    H2("Quick Start", style="margin-bottom: 1.5rem;"),
                    Div(
                        A(
                            Span(
                                "👤",
                                style="font-size: 2rem; margin-bottom: 1rem; display: block;",
                            ),
                            H3("Create Profile"),
                            P("Set up your language learning profile"),
                            href="/profile",
                            cls="btn btn-primary card",
                            style="text-decoration: none; display: block; text-align: center;",
                        ),
                        A(
                            Span(
                                "💬",
                                style="font-size: 2rem; margin-bottom: 1rem; display: block;",
                            ),
                            H3("Start Conversation"),
                            P("Begin AI-powered language practice"),
                            href="/chat",
                            cls="btn btn-primary card",
                            style="text-decoration: none; display: block; text-align: center;",
                        ),
                        cls="grid grid-2",
                    ),
                    cls="card",
                ),
            ),
            current_page="home",
        )

    # Route: Health check
    @app.route("/health")
    def frontend_health():
        return {
            "status": "healthy",
            "service": "ai-language-tutor-frontend",
            "timestamp": str(datetime.now()),
        }

    # Route: Profile management
    @app.route("/profile")
    def profile():
        return create_layout(
            Div(
                H1("User Profile Management", style="margin-bottom: 2rem;"),
                # Login/Registration Section
                Div(
                    H2("Login or Register"),
                    Div(
                        # Login Form
                        Div(
                            H3("Login"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(
                                        type="text",
                                        name="user_id",
                                        id="login-user-id",
                                        placeholder="Enter your user ID",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label(
                                        "Password (optional for demo)", cls="form-label"
                                    ),
                                    Input(
                                        type="password",
                                        name="password",
                                        id="login-password",
                                        placeholder="Enter password",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Button(
                                    "Login",
                                    type="button",
                                    id="login-btn",
                                    cls="btn btn-primary",
                                ),
                                style="margin-bottom: 2rem;",
                            ),
                            cls="card",
                        ),
                        # Registration Form
                        Div(
                            H3("Create New Profile"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(
                                        type="text",
                                        name="user_id",
                                        id="reg-user-id",
                                        placeholder="Choose a unique user ID",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Username", cls="form-label"),
                                    Input(
                                        type="text",
                                        name="username",
                                        id="reg-username",
                                        placeholder="Your display name",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Email (optional)", cls="form-label"),
                                    Input(
                                        type="email",
                                        name="email",
                                        id="reg-email",
                                        placeholder="Your email address",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Account Type", cls="form-label"),
                                    Select(
                                        Option("Child (default)", value="child"),
                                        Option("Parent/Adult", value="parent"),
                                        name="role",
                                        id="reg-role",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Button(
                                    "Register",
                                    type="button",
                                    id="register-btn",
                                    cls="btn btn-secondary",
                                ),
                                method="post",
                                action="/profile/register",
                            ),
                            cls="card",
                        ),
                        cls="grid grid-2",
                    ),
                    id="auth-section",
                ),
                # Current User Profile (hidden by default)
                Div(
                    H2("Your Profile"),
                    Div(
                        Div(
                            H3("Profile Information", id="profile-username"),
                            P(id="profile-details"),
                            Span("Active", cls="status-indicator status-success"),
                            Button(
                                "Logout",
                                type="button",
                                id="logout-btn",
                                cls="btn btn-secondary",
                                style="margin-top: 1rem;",
                            ),
                        ),
                        cls="card",
                    ),
                    id="profile-section",
                    style="display: none;",
                ),
                # Family Profiles (for parents/admins)
                Div(
                    H2("Family Management"),
                    Div(
                        # Add Family Member Form
                        Div(
                            H3("Add Family Member"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(
                                        type="text",
                                        id="new-member-user-id",
                                        placeholder="Choose unique user ID",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Name", cls="form-label"),
                                    Input(
                                        type="text",
                                        id="new-member-name",
                                        placeholder="Family member's name",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Age Group", cls="form-label"),
                                    Select(
                                        Option("Child (0-12)", value="child"),
                                        Option("Teen (13-17)", value="teen"),
                                        Option("Adult (18+)", value="adult"),
                                        id="new-member-age",
                                        cls="form-input",
                                    ),
                                    cls="form-group",
                                ),
                                Div(
                                    Label("Learning Languages", cls="form-label"),
                                    Select(
                                        Option("English", value="en"),
                                        Option("Spanish", value="es"),
                                        Option("French", value="fr"),
                                        Option("Chinese", value="zh"),
                                        Option("Japanese", value="ja"),
                                        id="new-member-languages",
                                        cls="form-input",
                                        multiple=True,
                                    ),
                                    cls="form-group",
                                ),
                                Button(
                                    "Add Family Member",
                                    type="button",
                                    id="add-member-btn",
                                    cls="btn btn-primary",
                                ),
                            ),
                            cls="card",
                        ),
                        # Family Members List
                        Div(
                            H3("Current Family Members"),
                            Div(
                                Div(
                                    H4("👨‍💼 familia_admin (You)"),
                                    P("Role: Parent/Admin"),
                                    P("Languages: English, Spanish, French"),
                                    P("Level: Advanced"),
                                    P("Total Sessions: 15 | This Week: 3"),
                                    Span(
                                        "Active", cls="status-indicator status-success"
                                    ),
                                    cls="card",
                                ),
                                Div(
                                    H4("👧 estudiante_1"),
                                    P("Role: Child"),
                                    P("Languages: Spanish"),
                                    P("Level: Beginner"),
                                    P("Total Sessions: 8 | This Week: 2"),
                                    Span(
                                        "Active", cls="status-indicator status-success"
                                    ),
                                    Div(
                                        Button(
                                            "View Progress",
                                            cls="btn btn-secondary",
                                            style="margin: 0.5rem 0.5rem 0 0;",
                                        ),
                                        Button(
                                            "Manage Settings",
                                            cls="btn btn-secondary",
                                            style="margin: 0.5rem 0.5rem 0 0;",
                                        ),
                                        Button(
                                            "Safety Controls", cls="btn btn-secondary"
                                        ),
                                    ),
                                    cls="card",
                                ),
                                Div(
                                    H4("👦 Add Another Child"),
                                    P("Create profiles for all family members"),
                                    P("Each member gets personalized learning"),
                                    Button(
                                        "Add Member",
                                        cls="btn btn-primary",
                                        onclick="document.getElementById('new-member-user-id').focus()",
                                    ),
                                    cls="card",
                                    style="border: 2px dashed var(--border-color); text-align: center;",
                                ),
                                cls="grid grid-3",
                            ),
                            id="family-members-list",
                        ),
                        cls="grid grid-1",
                    ),
                    cls="card",
                    id="family-section",
                    style="display: none;",
                ),
                # Parental Controls (for parents only)
                Div(
                    H2("Parental Controls & Safety"),
                    Div(
                        Div(
                            H3("⚡ Usage Limits"),
                            P("Set daily conversation limits"),
                            Div(
                                Label("Daily Sessions per Child:", cls="form-label"),
                                Select(
                                    Option("3 sessions", value="3"),
                                    Option("5 sessions", value="5"),
                                    Option("Unlimited", value="unlimited"),
                                    cls="form-input",
                                ),
                                cls="form-group",
                            ),
                            Button("Update Limits", cls="btn btn-secondary"),
                            cls="card",
                        ),
                        Div(
                            H3("🛡️ Content Safety"),
                            P("AI conversation monitoring"),
                            Div(
                                Label("Safety Level:", cls="form-label"),
                                Select(
                                    Option("High (Strict filtering)", value="high"),
                                    Option(
                                        "Medium (Balanced)",
                                        value="medium",
                                        selected=True,
                                    ),
                                    Option("Low (Minimal filtering)", value="low"),
                                    cls="form-input",
                                ),
                                cls="form-group",
                            ),
                            Button("Update Safety", cls="btn btn-secondary"),
                            cls="card",
                        ),
                        Div(
                            H3("📊 Activity Reports"),
                            P("Monitor learning progress"),
                            Button(
                                "View Weekly Report",
                                cls="btn btn-secondary",
                                style="margin-bottom: 1rem;",
                            ),
                            Button("Download CSV", cls="btn btn-secondary"),
                            cls="card",
                        ),
                        cls="grid grid-3",
                    ),
                    cls="card",
                    id="parental-controls",
                    style="display: none;",
                ),
                # Authentication JavaScript
                Script("""
                class AuthManager {
                    constructor() {
                        this.token = localStorage.getItem('auth_token');
                        this.currentUser = null;
                        this.setupEventListeners();
                        this.checkAuthStatus();
                    }

                    setupEventListeners() {
                        // Login button
                        document.getElementById('login-btn')?.addEventListener('click', () => this.login());

                        // Register button
                        document.getElementById('register-btn')?.addEventListener('click', () => this.register());

                        // Logout button
                        document.getElementById('logout-btn')?.addEventListener('click', () => this.logout());

                        // Add family member button
                        document.getElementById('add-member-btn')?.addEventListener('click', () => this.addFamilyMember());
                    }

                    async checkAuthStatus() {
                        try {
                            const response = await fetch('http://localhost:8000/api/v1/auth/me', {
                                headers: this.token ? {'Authorization': `Bearer ${this.token}`} : {}
                            });
                            const data = await response.json();

                            if (data.authenticated) {
                                this.currentUser = data.user;
                                this.showAuthenticatedView();
                            } else {
                                this.showUnauthenticatedView();
                            }
                        } catch (error) {
                            console.error('Auth check failed:', error);
                            this.showUnauthenticatedView();
                        }
                    }

                    async login() {
                        const userId = document.getElementById('login-user-id').value;
                        const password = document.getElementById('login-password').value;

                        if (!userId) {
                            alert('Please enter a user ID');
                            return;
                        }

                        try {
                            const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    user_id: userId,
                                    password: password || ''
                                })
                            });

                            if (response.ok) {
                                const data = await response.json();
                                this.token = data.access_token;
                                this.currentUser = data.user;
                                localStorage.setItem('auth_token', this.token);
                                this.showAuthenticatedView();
                                alert('Login successful!');
                            } else {
                                const error = await response.json();
                                alert(`Login failed: ${error.detail}`);
                            }
                        } catch (error) {
                            console.error('Login error:', error);
                            alert('Login failed: Network error');
                        }
                    }

                    async register() {
                        const userId = document.getElementById('reg-user-id').value;
                        const username = document.getElementById('reg-username').value;
                        const email = document.getElementById('reg-email').value;
                        const role = document.getElementById('reg-role').value;

                        if (!userId || !username) {
                            alert('Please fill in User ID and Username');
                            return;
                        }

                        try {
                            const response = await fetch('http://localhost:8000/api/v1/auth/register', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    user_id: userId,
                                    username: username,
                                    email: email || null,
                    // 4. Test speech recognition
                    async function testSpeechRecognition() {
                        try {
                            log('Testing backend IBM Watson speech recognition...');
                            updateStatus('speech-status', '🎤 Testing backend speech recognition...', 'warning');

                            // In a real implementation, this would capture audio and send it to the backend
                            // For now, we'll test the backend endpoint directly
                            const response = await fetch('http://localhost:8000/api/v1/conversations/speech-to-text', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Bearer test_token_placeholder'
                                }
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

                    register() {
                        const username = document.getElementById('register-username').value;
                        const password = document.getElementById('register-password').value;
                        const role = document.getElementById('register-role').value;

                        if (!username || !password) {
                            alert('Please fill in Username and Password');
                            return;
                        }

                        try {
                            const response = await fetch('http://localhost:8000/api/v1/auth/register', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    username: username,
                                    password: password,
                                    role: role
                                })
                            });

                            if (response.ok) {
                                const data = await response.json();
                                this.token = data.access_token;
                                this.currentUser = data.user;
                                localStorage.setItem('auth_token', this.token);
                                this.showAuthenticatedView();
                                alert('Registration successful!');
                            } else {
                                const error = await response.json();
                                alert(`Registration failed: ${error.detail}`);
                            }
                        } catch (error) {
                            console.error('Registration error:', error);
                            alert('Registration failed: Network error');
                        }
                    }

                    logout() {
                        this.token = null;
                        this.currentUser = null;
                        localStorage.removeItem('auth_token');
                        this.showUnauthenticatedView();
                        alert('Logged out successfully!');
                    }

                    async addFamilyMember() {
                        const userId = document.getElementById('new-member-user-id').value;
                        const name = document.getElementById('new-member-name').value;
                        const ageGroup = document.getElementById('new-member-age').value;
                        const languages = Array.from(document.getElementById('new-member-languages').selectedOptions).map(opt => opt.value);

                        if (!userId || !name) {
                            alert('Please fill in User ID and Name');
                            return;
                        }

                        try {
                            const response = await fetch('http://localhost:8000/api/v1/auth/register', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${this.token}`
                                },
                                body: JSON.stringify({
                                    user_id: userId,
                                    username: name,
                                    role: ageGroup === 'adult' ? 'parent' : 'child'
                                })
                            });

                            if (response.ok) {
                                alert(`Family member '${name}' added successfully!`);
                                this.refreshFamilyList();
                                this.clearAddMemberForm();
                            } else {
                                const error = await response.json();
                                alert(`Failed to add family member: ${error.detail}`);
                            }
                        } catch (error) {
                            console.error('Add member error:', error);
                            alert('Failed to add family member: Network error');
                        }
                    }

                    clearAddMemberForm() {
                        ['new-member-user-id', 'new-member-name'].forEach(id => {
                            const element = document.getElementById(id);
                            if (element) element.value = '';
                        });
                        const ageSelect = document.getElementById('new-member-age');
                        if (ageSelect) ageSelect.selectedIndex = 0;
                        const langSelect = document.getElementById('new-member-languages');
                        if (langSelect) {
                            for (let option of langSelect.options) {
                                option.selected = false;
                            }
                        }
                    }

                    async refreshFamilyList() {
                        // In a full implementation, this would fetch and update the family list
                        console.log('Refreshing family member list...');
                    }

                    showAuthenticatedView() {
                        document.getElementById('auth-section').style.display = 'none';
                        document.getElementById('profile-section').style.display = 'block';

                        // Update profile display
                        if (this.currentUser) {
                            document.getElementById('profile-username').textContent = this.currentUser.username;
                            document.getElementById('profile-details').innerHTML = `
                                <strong>User ID:</strong> ${this.currentUser.user_id}<br>
                                <strong>Role:</strong> ${this.currentUser.role}<br>
                                <strong>Joined:</strong> ${new Date(Date.now()).toLocaleDateString()}
                            `;

                            // Show family section for parents
                            if (this.currentUser.role === 'parent' || this.currentUser.role === 'admin') {
                                document.getElementById('family-section').style.display = 'block';
                                document.getElementById('parental-controls').style.display = 'block';
                            }
                        }
                    }

                    showUnauthenticatedView() {
                        document.getElementById('auth-section').style.display = 'block';
                        document.getElementById('profile-section').style.display = 'none';
                        document.getElementById('family-section').style.display = 'none';
                        document.getElementById('parental-controls').style.display = 'none';

                        // Clear form fields
                        ['login-user-id', 'login-password', 'reg-user-id', 'reg-username', 'reg-email'].forEach(id => {
                            const element = document.getElementById(id);
                            if (element) element.value = '';
                        });
                    }
                }

                // Initialize auth manager when page loads
                document.addEventListener('DOMContentLoaded', () => {
                    window.authManager = new AuthManager();
                });
                """),
            ),
            current_page="profile",
            title="Profile Management - AI Language Tutor",
        )

    # Route: AI Conversation Interface
    @app.route("/chat")
    def chat():
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
                                "Hello! I'm your enhanced AI language tutor with natural voice interactions! 🎙️ "
                                "• Click the mic once for single recording"
                                "• Hold the mic for 1 second to enable continuous conversation mode"
                                "• Use the 'Continuous' button to toggle always-listening mode"
                                "• You can interrupt me while I'm speaking - just start talking!"
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
                # Enhanced JavaScript for speech and conversation
                Script("""
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

                            console.log('Microphone permission granted!');

                            // Set up MediaRecorder for audio capture
                            this.mediaRecorder = new MediaRecorder(stream);
                            this.mediaRecorder.ondataavailable = (event) => {
                                if (event.data.size > 0) {
                                    this.audioChunks.push(event.data);
                                }
                            };

                            this.mediaRecorder.onstop = async () => {
                                await this.processAudioRecording();
                            };

                            console.log('Audio recording context initialized successfully');

                            // Update UI to show microphone is ready
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'Microphone ready! Click to speak or try typing a message.';
                            }

                        } catch (error) {
                            console.warn('Audio recording features not available:', error);

                            // Update UI to show basic mode
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'Basic mode: Click microphone to speak or type messages';
                            }
                        }
                    }

                    startRecording() {
                        if (!this.mediaRecorder) {
                            console.error('MediaRecorder not initialized');
                            return;
                        }

                        this.audioChunks = [];
                        this.mediaRecorder.start();
                        this.isRecording = true;

                        console.log('Audio recording started');

                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');

                        if (micButton) micButton.classList.add('recording');
                        if (statusSpan) statusSpan.textContent = 'Listening... speak now';
                    }

                    stopRecording() {
                        if (!this.mediaRecorder || !this.isRecording) {
                            return;
                        }

                        this.mediaRecorder.stop();
                        this.isRecording = false;

                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');

                        if (micButton) micButton.classList.remove('recording');
                        if (statusSpan) statusSpan.textContent = 'Processing your speech...';

                        console.log('Audio recording stopped');
                    }

                    async processAudioRecording() {
                        if (this.audioChunks.length === 0) {
                            console.warn('No audio data to process');
                            return;
                        }

                        try {
                            // Create audio blob
                            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

                            // Convert to base64 for transmission
                            const base64Audio = await this.blobToBase64(audioBlob);

                            // Send to backend for speech-to-text processing
                            const transcript = await this.sendAudioToBackend(base64Audio);

                            if (transcript) {
                                // Add transcript to text input
                                const textInput = document.getElementById('text-input');
                                if (textInput) {
                                    textInput.value = transcript;
                                    this.sendMessage();
                                }
                            }

                        } catch (error) {
                            console.error('Error processing audio recording:', error);

                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'Speech recognition failed. Try again or type your message.';
                                statusSpan.className = 'error';
                            }
                        }
                    }

                    async blobToBase64(blob) {
                        return new Promise((resolve, reject) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result.split(',')[1]);
                            reader.onerror = reject;
                            reader.readAsDataURL(blob);
                        });
                    }

                    async sendAudioToBackend(base64Audio) {
                        try {
                            const token = localStorage.getItem('auth_token') || 'demo-token';

                            const response = await fetch('http://localhost:8000/api/v1/conversations/speech-to-text', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${token}`
                                },
                                body: JSON.stringify({
                                    audio_data: base64Audio,
                                    language: this.currentLanguage.split('-')[0]
                                })
                            });

                            if (response.ok) {
                                const data = await response.json();
                                return data.text || data.transcript || '';
                            } else {
                                console.error('Backend speech recognition error:', response.status);
                                return null;
                            }
                        } catch (error) {
                            console.error('Error sending audio to backend:', error);
                            return null;
                        }
                    }

                    detectVoiceActivity() {
                        if (!window.analyser) return false;

                        const bufferLength = window.analyser.frequencyBinCount;
                        const dataArray = new Uint8Array(bufferLength);
                        window.analyser.getByteFrequencyData(dataArray);

                        // Calculate average volume
                        let sum = 0;
                        for (let i = 0; i < bufferLength; i++) {
                            sum += dataArray[i];
                        }
                        const average = sum / bufferLength;

                        // Detect voice activity
                        const isVoiceDetected = average > (window.vadThreshold * 255);

                        if (isVoiceDetected) {
                            this.lastSpeechTime = Date.now();
                            window.voiceActivityDetected = true;
                        } else if (window.voiceActivityDetected && (Date.now() - this.lastSpeechTime) > 1500) {
                            // 1.5 seconds of silence after voice detected
                            window.voiceActivityDetected = false;
                            this.handleSilenceDetected();
                        }

                        return isVoiceDetected;
                    }

                    handleSilenceDetected() {
                        if (this.finalTranscript.trim() && !this.isProcessingAI) {
                            console.log('Silence detected, processing final transcript:', this.finalTranscript);
                            this.sendTranscriptMessage(this.finalTranscript.trim());
                            this.finalTranscript = '';
                        }
                    }

                    startVoiceActivityDetection() {
                        if (this.vadInterval) return;

                        this.vadInterval = setInterval(() => {
                            this.detectVoiceActivity();
                        }, 100); // Check every 100ms
                    }

                    stopVoiceActivityDetection() {
                        if (this.vadInterval) {
                            clearInterval(this.vadInterval);
                            this.vadInterval = null;
                        }
                    }

                    setupSpeechRecognition() {
                        if (!window.speechRecognition) return;

                        // Reinitialize speech recognition for current language
                        const langMap = {
                            'en-claude': 'en-US',
                            'es-claude': 'es-ES',
                            'fr-mistral': 'fr-FR',
                            'zh-qwen': 'zh-CN',
                            'ja-claude': 'ja-JP'
                        };

                        const speechLang = langMap[this.currentLanguage] || 'en-US';
                        window.speechRecognition.lang = speechLang;

                        // Enhanced speech recognition event handlers
                        window.speechRecognition.onresult = (event) => {
                            let interimTranscript = '';
                            let finalTranscript = '';

                            for (let i = event.resultIndex; i < event.results.length; i++) {
                                const transcript = event.results[i][0].transcript;
                                if (event.results[i].isFinal) {
                                    finalTranscript += transcript;
                                } else {
                                    interimTranscript += transcript;
                                }
                            }

                            this.finalTranscript += finalTranscript;
                            this.interimTranscript = interimTranscript;

                            // Update UI with interim results for better UX
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                const displayText = (this.finalTranscript + interimTranscript).trim();
                                if (displayText) {
                                    statusSpan.textContent = `Hearing: "${displayText}..."`;
                                }
                            }

                            // Handle interruption - if AI is speaking and user starts talking
                            if ((finalTranscript || interimTranscript) && window.isAISpeaking) {
                                this.handleUserInterruption();
                            }
                        };

                        window.speechRecognition.onerror = (event) => {
                            console.error('Speech recognition error:', event.error);

                            // Handle network errors specifically
                            if (event.error === 'network') {
                                console.error('Network error with speech recognition - likely connectivity issue with Google service');

                                // Update UI with specific guidance
                                const statusSpan = document.getElementById('speech-status');
                                if (statusSpan) {
                                    statusSpan.textContent = '⚠️ Network error with speech service. Try again or use text input.';
                                    statusSpan.className = 'error';
                                }

                                // Show detailed guidance in console
                                console.log('Speech recognition network error troubleshooting:');
                                console.log('1. Check your internet connection');
                                console.log('2. Try refreshing the page');
                                console.log('3. Use Chrome or Edge browser (best Web Speech API support)');
                                console.log('4. All functionality works with text input - speech is optional enhancement');
                                console.log('5. Google speech services may be temporarily unavailable');
                                console.log('6. Try disabling VPN/firewall temporarily');
                                console.log('7. Test on a different network (mobile hotspot)');
                                console.log('8. Wait 5-10 minutes and try again');
                                console.log('9. See detailed guide: SPEECH_RECOGNITION_NETWORK_ERROR_FIX.md');

                                // Show user-friendly alert
                                setTimeout(() => {
                                    const userResponse = confirm(
                                        'Speech recognition encountered a network error. This is usually temporary.\n\n' +
                                        'All AI features work perfectly with text input.\n\n' +
                                        'Click OK to continue using text input, or Cancel to try speech again.'
                                    );
                                    if (statusSpan) {
                                        statusSpan.textContent = userResponse ?
                                            'Using text input - all features work perfectly!' :
                                            'Click microphone to try speech again';
                                        statusSpan.className = userResponse ? 'success' : '';
                                    }
                                }, 1000);
                            } else if (event.error !== 'no-speech') {
                                this.restartContinuousListening();
                            }
                        };

                        window.speechRecognition.onend = () => {
                            if (this.isContinuousMode && !this.isProcessingAI) {
                                // Restart recognition for continuous mode
                                setTimeout(() => this.restartContinuousListening(), 100);
                            }
                        };

                        console.log(`Enhanced speech recognition configured for: ${speechLang}`);
                    }

                    handleUserInterruption() {
                        console.log('User interruption detected - stopping AI speech');

                        // Stop current AI speech
                        if (window.speechSynthesis.speaking) {
                            window.speechSynthesis.cancel();
                        }

                        window.isAISpeaking = false;

                        // Update UI to show interruption
                        const statusSpan = document.getElementById('speech-status');
                        if (statusSpan) {
                            statusSpan.textContent = 'You interrupted - go ahead and speak!';
                        }
                    }

                    setupSpeechRecognition() {
                        // Speech recognition is handled by backend Watson services
                        // This function is kept for compatibility but does nothing
                        console.log('Speech recognition handled by backend IBM Watson services');
                    }

                    handleUserInterruption() {
                        console.log('User interruption detected');
                        // Stop current AI speech if using backend TTS
                        // In this implementation, we'll handle this through the UI
                    }

                    restartContinuousListening() {
                        // Not using continuous listening with Web Speech API
                        // Audio recording is handled manually
                    }

                    setupEventListeners() {
                        // Enhanced microphone button with mode toggle
                        const micButton = document.getElementById('mic-button');
                        micButton?.addEventListener('click', () => this.toggleListeningMode());

                        // Long press for continuous mode
                        let longPressTimer;
                        micButton?.addEventListener('mousedown', () => {
                            longPressTimer = setTimeout(() => {
                                this.startContinuousMode();
                            }, 1000); // 1 second long press
                        });

                        micButton?.addEventListener('mouseup', () => {
                            clearTimeout(longPressTimer);
                            // If it wasn't a long press, treat as single click
                            if (!this.isContinuousMode) {
                                this.startSingleRecording();
                                // Auto-stop after 5 seconds
                                setTimeout(() => {
                                    if (this.isRecording) {
                                        this.stopRecording();
                                    }
                                }, 5000);
                            }
                        });

                        micButton?.addEventListener('mouseleave', () => {
                            clearTimeout(longPressTimer);
                        });

                        // Send button
                        const sendButton = document.getElementById('send-button');
                        sendButton?.addEventListener('click', () => this.sendMessage());

                        // Enhanced text input with voice integration
                        const textInput = document.getElementById('text-input');
                        textInput?.addEventListener('keypress', (e) => {
                            if (e.key === 'Enter') {
                                e.preventDefault();
                                this.sendMessage();
                            }
                        });

                        // Language selection with enhanced voice features
                        const languageSelect = document.getElementById('language-select');
                        languageSelect?.addEventListener('change', (e) => {
                            this.currentLanguage = e.target.value;

                            // Clear conversation for new language context
                            this.conversationHistory = [];
                            this.addMessage('system', `Switched to ${e.target.options[e.target.selectedIndex].text}. Starting fresh conversation!`);
                        });

                        // Clear button
                        const clearButton = document.getElementById('clear-button');
                        clearButton?.addEventListener('click', () => this.clearConversation());
                    }

                    startSingleRecording() {
                        console.log('Starting single recording');
                        this.startRecording();
                    }

                    stopSingleRecording() {
                        console.log('Stopping single recording');
                        this.stopRecording();
                    }

                    toggleListeningMode() {
                        const statusSpan = document.getElementById('speech-status');

                        if (this.isRecording) {
                            this.stopRecording();
                        } else {
                            this.startSingleRecording();
                        }
                    }

                    toggleContinuousMode() {
                        if (this.isContinuousMode) {
                            this.stopContinuousMode();
                        } else {
                            this.startContinuousMode();
                        }
                    }

                    startContinuousMode() {
                        console.log('Starting continuous conversation mode');
                        this.isContinuousMode = true;

                        // Update UI
                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');
                        const continuousBtn = document.getElementById('continuous-mode-btn');

                        if (micButton) {
                            micButton.classList.add('recording');
                            micButton.title = 'Click to stop continuous mode';
                        }

                        if (statusSpan) {
                            statusSpan.textContent = '🎙️ Continuous mode: I\'m always listening...';
                        }

                        if (continuousBtn) {
                            continuousBtn.textContent = '⏹️ Stop';
                            continuousBtn.classList.add('btn-danger');
                            continuousBtn.classList.remove('btn-secondary');
                        }

                        // Start continuous listening
                        this.startContinuousListening();
                        this.startVoiceActivityDetection();
                    }

                    stopContinuousMode() {
                        console.log('Stopping continuous conversation mode');
                        this.isContinuousMode = false;

                        // Update UI
                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');
                        const continuousBtn = document.getElementById('continuous-mode-btn');

                        if (micButton) {
                            micButton.classList.remove('recording');
                            micButton.title = 'Click to start continuous mode';
                        }

                        if (statusSpan) {
                            statusSpan.textContent = 'Voice recognition stopped';
                        }

                        if (continuousBtn) {
                            continuousBtn.textContent = '🔄 Continuous';
                            continuousBtn.classList.add('btn-secondary');
                            continuousBtn.classList.remove('btn-danger');
                        }

                        // Stop continuous listening
                        this.stopContinuousListening();
                        this.stopVoiceActivityDetection();
                    }

                    async sendMessage() {
                        const textInput = document.getElementById('text-input');
                        const text = textInput?.value.trim();
                        if (!text) return;

                        this.addMessage('user', text);
                        textInput.value = '';

                        this.isProcessingAI = true;
                        this.addMessage('system', '...');

                        try {
                            const response = await this.fetchResponse(text);
                            this.addMessage('assistant', response);
                        } catch (error) {
                            console.error('Error fetching response:', error);
                            this.addMessage('system', 'Failed to get response. Please try again.');
                        } finally {
                            this.isProcessingAI = false;
                        }
                    }

                    async fetchResponse(text) {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                message: text,
                                language: this.currentLanguage,
                            }),
                        });

                        const data = await response.json();
                        return data.response;
                    }

                    addMessage(role, content) {
                        const chatContainer = document.getElementById('chat-container');
                        const messageElement = document.createElement('div');
                        messageElement.className = `message ${role}`;
                        messageElement.textContent = content;
                        chatContainer?.appendChild(messageElement);
                        chatContainer?.scrollTo(0, chatContainer.scrollHeight);
                    }

                    clearConversation() {
                        const chatContainer = document.getElementById('chat-container');
                        if (chatContainer) {
                            chatContainer.innerHTML = '';
                        }
                        this.conversationHistory = [];
                    }
                    }

                    stopContinuousMode() {
                        console.log('Stopping continuous conversation mode');
                        this.isContinuousMode = false;

                        // Stop all activities
                        this.stopAllVoiceActivities();

                        // Update UI
                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');
                        const continuousBtn = document.getElementById('continuous-mode-btn');

                        if (micButton) {
                            micButton.classList.remove('recording');
                            micButton.title = 'Click to speak (or hold for continuous mode)';
                        }

                        if (statusSpan) {
                            statusSpan.textContent = 'Click microphone to speak';
                        }

                        if (continuousBtn) {
                            continuousBtn.textContent = '🔄 Continuous';
                            continuousBtn.classList.remove('btn-danger');
                            continuousBtn.classList.add('btn-secondary');
                        }
                    }

                    startContinuousListening() {
                        if (!window.speechRecognition || this.isRecording) return;

                        try {
                            window.speechRecognition.start();
                            this.isRecording = true;
                            console.log('Continuous listening started');
                        } catch (error) {
                            console.log('Could not start continuous listening:', error.message);
                            setTimeout(() => this.startContinuousListening(), 1000);
                        }
                    }

                    startSingleRecording() {
                        if (!window.speechRecognition || this.isRecording) return;

                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');

                        try {
                            // Configure for single recording
                            window.speechRecognition.continuous = false;
                            window.speechRecognition.interimResults = false;

                            window.speechRecognition.onresult = (event) => {
                                const transcript = event.results[0][0].transcript;
                                document.getElementById('text-input').value = transcript;
                                if (statusSpan) statusSpan.textContent = `Heard: "${transcript}"`;
                            };

                            window.speechRecognition.onend = () => {
                                this.isRecording = false;
                                if (micButton) micButton.classList.remove('recording');
                                if (statusSpan) statusSpan.textContent = 'Speech captured! Click Send or speak again';
                            };

                            window.speechRecognition.start();
                            this.isRecording = true;

                            if (micButton) micButton.classList.add('recording');
                            if (statusSpan) statusSpan.textContent = 'Listening... speak now';

                        } catch (error) {
                            console.error('Failed to start single recording:', error);
                            if (statusSpan) statusSpan.textContent = 'Speech recognition failed to start';
                        }
                    }

                    stopSingleRecording() {
                        if (window.speechRecognition && this.isRecording) {
                            window.speechRecognition.stop();
                        }
                    }

                    async sendMessage() {
                        const textInput = document.getElementById('text-input');
                        const message = textInput.value.trim();

                        if (!message) {
                            // If no text, show instruction
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'Please type a message or click the microphone to speak';
                            }
                            return;
                        }

                        console.log('Sending text message:', message);
                        await this.sendTranscriptMessage(message);
                        textInput.value = '';
                    }

                    async sendTranscriptMessage(message) {
                        if (!message.trim() || this.isProcessingAI) return;

                        this.isProcessingAI = true;

                        // Add user message to history
                        this.conversationHistory.push({
                            role: 'user',
                            content: message,
                            timestamp: new Date().toISOString()
                        });

                        // Add user message to UI
                        this.addMessage('user', message);

                        // Update status
                        const statusSpan = document.getElementById('speech-status');
                        if (statusSpan) statusSpan.textContent = 'AI is thinking...';

                        // Add loading indicator
                        const loadingId = this.addMessage('ai', '<span class="loading"></span> Processing your message...');

                        try {
                            // Send message with conversation history
                            await this.getAIResponse(message, loadingId);
                        } catch (error) {
                            this.updateMessage(loadingId, 'Sorry, I encountered an error. Please try again.');
                        } finally {
                            this.isProcessingAI = false;

                            // Update status for continuous mode
                            if (this.isContinuousMode && statusSpan) {
                                statusSpan.textContent = '🎙️ Continuous mode: I\'m listening...';
                            } else if (statusSpan) {
                                statusSpan.textContent = 'Click microphone to speak';
                            }
                        }
                    }

                    async getAIResponse(userMessage, loadingId) {
                        try {
                            // Get auth token
                            const token = localStorage.getItem('auth_token');

                            let aiResponse = '';

                            // Call real backend API with conversation history
                            if (token) {
                                const response = await fetch('http://localhost:8000/api/v1/conversations/chat', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'Authorization': `Bearer ${token}`
                                    },
                                    body: JSON.stringify({
                                        message: userMessage,
                                        language: this.currentLanguage,
                                        use_speech: true,
                                        conversation_history: this.conversationHistory.slice(-6) // Last 6 messages
                                    })
                                });

                                if (response.ok) {
                                    const data = await response.json();
                                    aiResponse = data.response;

                                    // Add AI response to conversation history
                                    this.conversationHistory.push({
                                        role: 'assistant',
                                        content: aiResponse,
                                        timestamp: new Date().toISOString()
                                    });

                                    // Update message in UI
                                    this.updateMessage(loadingId, aiResponse);

                                    // Play audio response if available
                                    if (data.audio_url) {
                                        await this.playAudioResponse(data.audio_url);
                                    }
                                } else {
                                    throw new Error(`API error: ${response.status}`);
                                }
                            } else {
                                // Enhanced fallback with more natural responses
                                aiResponse = await this.getEnhancedFallbackResponse(userMessage);
                                this.updateMessage(loadingId, aiResponse);
                            }

                        } catch (error) {
                            console.error('AI Response Error:', error);
                            const fallbackResponse = await this.getEnhancedFallbackResponse(userMessage);
                            this.updateMessage(loadingId, `[Connection Issue] ${fallbackResponse}`);
                        } finally {
                            this.isProcessingAI = false;

                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'Click microphone to speak';
                            }
                        }
                    }

                    async playAudioResponse(audioUrl) {
                        try {
                            // In a real implementation, this would play the audio from the backend
                            console.log('Playing audio response from:', audioUrl);

                            // For now, we'll just log that audio would be played
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'AI is speaking...';
                                setTimeout(() => {
                                    statusSpan.textContent = 'Click microphone to respond';
                                }, 3000);
                            }
                        } catch (error) {
                            console.error('Error playing audio response:', error);
                        }
                    }

                    async getEnhancedFallbackResponse(userMessage) {
                        // Ensure we always have a response for testing
                        console.log('Generating fallback response for:', userMessage);

                        const messageType = this.detectMessageType(userMessage);
                        const langCode = this.currentLanguage.split('-')[0];

                        const responses = {
                            en: {
                                greeting: `Hey there! I heard you say "${userMessage}" - that's wonderful! I'm Alex, your conversation partner. How are you doing today?`,
                                question: `That's a really interesting question! You asked "${userMessage}" and I love how curious you are. What made you think about that?`,
                                emotion: `I can feel the emotion in "${userMessage}"! Tell me more about what you're experiencing. I'm here to listen!`,
                                default: `I love that you said "${userMessage}"! That's really fascinating. What else would you like to talk about?`
                            },
                            es: {
                                greeting: `¡Hola! Escuché que dijiste "${userMessage}" - ¡qué padre! Soy María, tu compañera de conversación. ¿Cómo estás hoy?`,
                                question: `¡Órale! Esa es una pregunta súper interesante. Dijiste "${userMessage}" y me encanta lo curioso que eres. ¿Qué te hizo pensar en eso?`,
                                emotion: `¡Puedo sentir la emoción en "${userMessage}"! Cuéntame más sobre lo que estás sintiendo. ¡Estoy aquí para escucharte!`,
                                default: `¡Me encanta que dijeras "${userMessage}"! Es muy fascinante. ¿De qué más quieres hablar?`
                            },
                            fr: {
                                greeting: `Salut ! J'ai entendu que tu as dit "${userMessage}" - c'est génial ! Je suis Sophie. Comment ça va aujourd'hui ?`,
                                question: `C'est une question très intéressante ! Tu as demandé "${userMessage}" et j'adore ta curiosité. Qu'est-ce qui t'a fait penser à ça ?`,
                                emotion: `Je peux sentir l'émotion dans "${userMessage}" ! Dis-moi plus sur ce que tu ressens. Je suis là pour t'écouter !`,
                                default: `J'adore que tu aies dit "${userMessage}" ! C'est vraiment fascinant. De quoi d'autre veux-tu parler ?`
                            },
                            zh: {
                                greeting: `你好！我听到你说"${userMessage}" - 太好了！我是小李。你今天怎么样？`,
                                question: `这是一个很有趣的问题！你问了"${userMessage}"，我喜欢你的好奇心。是什么让你想到这个的？`,
                                emotion: `我能感受到"${userMessage}"中的情感！告诉我更多关于你的感受。我在这里倾听！`,
                                default: `我喜欢你说的"${userMessage}"！很有意思。你还想聊什么？`
                            }
                        };

                        const langResponses = responses[langCode] || responses.en;
                        const response = langResponses[messageType] || langResponses.default;

                        console.log('Generated fallback response:', response);
                        return response;
                    }

                    detectMessageType(message) {
                        const lowerMessage = message.toLowerCase();

                        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hola')) {
                            return 'greeting';
                        }
                        if (lowerMessage.includes('?') || lowerMessage.includes('what') || lowerMessage.includes('how') || lowerMessage.includes('why')) {
                            return 'question';
                        }
                        if (lowerMessage.includes('love') || lowerMessage.includes('hate') || lowerMessage.includes('excited') || lowerMessage.includes('sad')) {
                            return 'emotion';
                        }
                    async speakResponseNaturally(text) {
                        if (!window.speechSynthesis || !text.trim()) return;

                        // Clean text for speech synthesis
                        let cleanText = text
                            .replace(/\\*[^*]*\\*/g, '') // Remove *actions*
                            .replace(/\\[[^\\]]*\\]/g, '') // Remove [notes]
                            .replace(/\\([^)]*\\)/g, '') // Remove (parentheticals)
                            .replace(/\s+/g, ' ')      // Clean multiple spaces
                            .trim();

                        if (!cleanText) return;

                        // Stop any current speech
                        if (window.speechSynthesis.speaking) {
                            window.speechSynthesis.cancel();
                        }

                        window.isAISpeaking = true;

                        const utterance = new SpeechSynthesisUtterance(cleanText);

                        // Enhanced voice settings for natural conversation
                        const langCode = this.currentLanguage.split('-')[0];
                        const voiceSettings = {
                            'en': { lang: 'en-US', rate: 0.9, pitch: 1.1, volume: 0.9 },
                            'es': { lang: 'es-ES', rate: 0.95, pitch: 1.15, volume: 0.9 },
                            'fr': { lang: 'fr-FR', rate: 0.9, pitch: 1.05, volume: 0.9 },
                            'zh': { lang: 'zh-CN', rate: 0.85, pitch: 1.0, volume: 0.9 },
                            'ja': { lang: 'ja-JP', rate: 0.9, pitch: 1.1, volume: 0.9 }
                        };

                        const settings = voiceSettings[langCode] || voiceSettings['en'];
                        utterance.lang = settings.lang;
                        utterance.rate = settings.rate;
                        utterance.pitch = settings.pitch;
                        utterance.volume = settings.volume;

                        // Find the best voice for natural conversation
                        await this.waitForVoices();
                        const voices = window.speechSynthesis.getVoices();

                        // Prefer neural/natural voices
                        let selectedVoice = voices.find(voice =>
                            voice.lang.startsWith(langCode) &&
                            (voice.name.includes('Neural') || voice.name.includes('Enhanced') || voice.name.includes('Premium'))
                        );

                        // Fallback to any native voice
                        if (!selectedVoice) {
                            selectedVoice = voices.find(voice => voice.lang.startsWith(langCode));
                        }

                        if (selectedVoice) {
                            utterance.voice = selectedVoice;
                            console.log(`Using voice: ${selectedVoice.name} for ${langCode}`);
                        }

                        // Enhanced event handlers
                        utterance.onstart = () => {
                            console.log('AI started speaking');
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan && !this.isContinuousMode) {
                                statusSpan.textContent = 'AI is speaking... (you can interrupt anytime)';
                            }
                        };

                        utterance.onend = () => {
                            console.log('AI finished speaking');
                            window.isAISpeaking = false;

                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                if (this.isContinuousMode) {
                                    statusSpan.textContent = '🎙️ Continuous mode: I\'m listening...';
                                } else {
                                    statusSpan.textContent = 'Click microphone to respond';
                                }
                            }
                        };

                        utterance.onerror = (event) => {
                            console.error('Speech synthesis error:', event.error);
                            window.isAISpeaking = false;
                        };

                        // Speak the response
                        window.speechSynthesis.speak(utterance);
                    }

                    async waitForVoices() {
                        return new Promise((resolve) => {
                            const voices = window.speechSynthesis.getVoices();
                            if (voices.length > 0) {
                                resolve(voices);
                            } else {
                                window.speechSynthesis.onvoiceschanged = () => {
                                    resolve(window.speechSynthesis.getVoices());
                                };
                            }
                        });
                    }
                                    })
                                });

                                if (response.ok) {
                                    const data = await response.json();

                                    // Add AI response to history
                                    this.conversationHistory.push({
                                        role: 'assistant',
                                        content: data.response,
                                        timestamp: new Date().toISOString()
                                    });

                                    this.updateMessage(loadingId, data.response);
                                    this.speakText(data.response);

                                    // Show cost information
                                    if (data.estimated_cost > 0) {
                                        console.log(`AI Response cost: $${data.estimated_cost.toFixed(4)}`);
                                    }
                                    return;
                                } else {
                                    const error = await response.json();
                                    console.error('API Error:', error);
                                }
                            }

                            // Fallback to more dynamic simulation if API fails
                            await this.dynamicFallbackResponse(userMessage, loadingId);

                        } catch (error) {
                            console.error('AI Response error:', error);
                            await this.dynamicFallbackResponse(userMessage, loadingId);
                        }
                    }

                    async dynamicFallbackResponse(userMessage, loadingId) {
                        // More dynamic fallback responses
                        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

                        const conversationStarters = {
                            'en-claude': [
                                `Oh wow, "${userMessage}" - that's really interesting! I'm Alex, and I'm super curious about that. Can you tell me more? What got you thinking about this?`,
                                `"${userMessage}"? No way! That's so cool! I love hearing about stuff like this. What's your experience been like with that?`,
                                `Wait, you mentioned "${userMessage}" - that caught my attention! I've been wondering about that myself. What's your take on it?`
                            ],
                            'es-claude': [
                                `¡Órale! Dijiste "${userMessage}" - ¡qué interesante! Soy María y me encanta platicar sobre estas cosas. ¿Me puedes contar más? ¿Cómo te sientes al respecto?`,
                                `"${userMessage}"? ¡No manches! Eso está súper padre. Me da mucha curiosidad. ¿Qué opinas tú de todo eso?`,
                                `¡Ay, qué padre que mencionaste "${userMessage}"! Yo también he pensado en eso. ¿Tú qué experiencia has tenido?`
                            ],
                            'fr-mistral': [
                                `Oh là là! Tu as dit "${userMessage}" - c'est vraiment fascinant! Moi c'est Sophie, et ça m'intrigue énormément. Tu peux m'en dire plus? Qu'est-ce qui t'a amené à y penser?`,
                                `"${userMessage}"? Dis donc! C'est dingue ça! J'adore quand on parle de trucs comme ça. Comment tu vois les choses de ton côté?`,
                                `Attends, tu as mentionné "${userMessage}" - ça c'est intéressant! Moi aussi je me pose des questions là-dessus. Ton avis là-dessus?`
                            ],
                            'zh-qwen': [
                                `哇！你刚才说了"${userMessage}" - 太有意思了！我是小李，对这个话题超级好奇。能跟我多聊聊吗？你是怎么想到这个的？`,
                                `"${userMessage}"？真的假的！太棒了！我最喜欢聊这种话题了。你的经历是什么样的？`,
                                `等等，你提到了"${userMessage}" - 这个我也一直在想！你觉得怎么样？`
                            ],
                            'ja-claude': [
                                `えー！"${userMessage}"って言ったよね - めっちゃ面白い！私優子やねん、すごく興味あるわ。もっと教えて？どんなきっかけでそう思ったん？`,
                                `"${userMessage}"？マジで！すごいやん！そういう話大好きやねん。あなたはどんな感じ？`,
                                `ちょっと待って、"${userMessage}"って言ったよね - それ気になってたねん！あなたの経験はどんな感じ？`
                            ]
                        };

                        const responses = conversationStarters[this.currentLanguage] || conversationStarters['en-claude'];
                        const randomResponse = responses[Math.floor(Math.random() * responses.length)];

                        // Add to conversation history
                        this.conversationHistory.push({
                            role: 'assistant',
                            content: randomResponse,
                            timestamp: new Date().toISOString()
                        });

                        this.updateMessage(loadingId, `[Demo Mode] ${randomResponse}`);
                    }

                    addMessage(sender, content) {
                        const history = document.getElementById('conversation-history');
                        const messageId = 'msg-' + Date.now();
                        const messageClass = sender === 'user' ? 'message-user' : 'message-ai';

                        const messageDiv = document.createElement('div');
                        messageDiv.id = messageId;
                        messageDiv.className = `message ${messageClass}`;
                        messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'AI Tutor'}:</strong> ${content}`;

                        history.appendChild(messageDiv);
                        history.scrollTop = history.scrollHeight;

                        return messageId;
                    }

                    updateMessage(messageId, newContent) {
                        const messageEl = document.getElementById(messageId);
                        if (messageEl) {
                            messageEl.innerHTML = `<strong>AI Tutor:</strong> ${newContent}`;
                        }
                    }

                    clearConversation() {
                        const history = document.getElementById('conversation-history');
                        history.innerHTML = `
                            <div class="message message-ai">
                                <strong>AI Tutor:</strong> Conversation cleared! Ready for a fresh start. What would you like to practice?
                            </div>
                        `;
                    }
                }

                // Initialize enhanced conversation manager when page loads
                document.addEventListener('DOMContentLoaded', () => {
                    console.log('Initializing conversation manager with backend IBM Watson services...');

                    // Set up authentication token for demo
                    if (!localStorage.getItem('auth_token')) {
                        localStorage.setItem('auth_token', 'demo-token');
                        console.log('Demo authentication token set');
                    }

                    try {
                        window.conversationManager = new EnhancedConversationManager();
                        console.log('Conversation manager initialized successfully');
                    } catch (error) {
                        console.error('Failed to initialize conversation manager:', error);

                        // Show error message to user
                        const statusSpan = document.getElementById('speech-status');
                        if (statusSpan) {
                            statusSpan.textContent = 'Initialization error - please refresh page or use text input';
                        }
                    }
                });
                """),
            ),
            current_page="chat",
            title="AI Conversation - AI Language Tutor",
        )

    # Route: Progress tracking
    @app.route("/progress")
    def progress():
        return create_layout(
            Div(
                H1("Learning Progress", style="margin-bottom: 2rem;"),
                # Progress overview
                Div(
                    H2("Overview"),
                    Div(
                        Div(
                            H3("Current Streak"),
                            P(
                                "5 days",
                                style="font-size: 2rem; font-weight: bold; color: var(--primary-color);",
                            ),
                            cls="card",
                        ),
                        Div(
                            H3("Total Conversations"),
                            P(
                                "23",
                                style="font-size: 2rem; font-weight: bold; color: var(--secondary-color);",
                            ),
                            cls="card",
                        ),
                        Div(
                            H3("Words Learned"),
                            P(
                                "147",
                                style="font-size: 2rem; font-weight: bold; color: var(--accent-color);",
                            ),
                            cls="card",
                        ),
                        cls="grid grid-3",
                    ),
                    cls="card",
                ),
                # Language progress
                Div(
                    H2("Language Progress"),
                    Div(
                        Div(
                            H3("Spanish"),
                            P("Intermediate - 67% complete"),
                            Div(
                                style="background: var(--border-color); height: 8px; border-radius: 4px; margin: 1rem 0;",
                                children=[
                                    Div(
                                        style="background: var(--secondary-color); height: 100%; width: 67%; border-radius: 4px;"
                                    )
                                ],
                            ),
                        ),
                        Div(
                            H3("French"),
                            P("Beginner - 34% complete"),
                            Div(
                                style="background: var(--border-color); height: 8px; border-radius: 4px; margin: 1rem 0;",
                                children=[
                                    Div(
                                        style="background: var(--accent-color); height: 100%; width: 34%; border-radius: 4px;"
                                    )
                                ],
                            ),
                        ),
                        cls="grid grid-2",
                    ),
                    cls="card",
                ),
            ),
            current_page="progress",
            title="Progress Tracking - AI Language Tutor",
        )

    return app


# Create frontend app
frontend_app = create_frontend_app()


def run_frontend_server():
    """Run the FastHTML frontend server - extracted for testing"""
    settings = get_settings()
    uvicorn.run(
        "frontend_main:frontend_app",
        host=settings.HOST,
        port=settings.FRONTEND_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )


if __name__ == "__main__":
    run_frontend_server()
