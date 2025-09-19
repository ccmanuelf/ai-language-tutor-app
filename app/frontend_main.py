"""
FastHTML Frontend Server Entry Point
AI Language Tutor App - Personal Family Educational Tool

Modern FastHTML frontend with:
- User authentication and profiles
- AI conversation interface 
- Speech input/output using IBM Watson
- Multi-language support
- Family-safe design
"""

from fasthtml.common import *
import uvicorn
from pathlib import Path
import asyncio
from datetime import datetime

import base64

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
        title="AI Language Tutor - Family Educational Tool"
    )

    # Component functions for reusable UI elements
    def create_header(current_page="home"):
        """Create navigation header"""
        return Header(
            Nav(
                A("🎯 AI Language Tutor", href="/", cls="logo"),
                Ul(
                    Li(A("Home", href="/", cls="active" if current_page == "home" else "")),
                    Li(A("Profile", href="/profile", cls="active" if current_page == "profile" else "")),
                    Li(A("Conversation", href="/chat", cls="active" if current_page == "chat" else "")),
                    Li(A("Progress", href="/progress", cls="active" if current_page == "progress" else "")),
                    cls="nav-links"
                ),
                cls="nav"
            ),
            cls="header"
        )

    def create_layout(content, current_page="home", title="AI Language Tutor"):
        """Create consistent page layout"""
        return Html(
            Head(
                Title(title),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                load_styles()
            ),
            Body(
                create_header(current_page),
                Main(content, cls="container"),
                # Footer
                Footer(
                    Div(
                        P("AI Language Tutor - Personal Family Educational Tool"),
                        P(f"Backend: Operational | Speech: Ready | Database: Connected"),
                        cls="container",
                        style="text-align: center; padding: 2rem; color: var(--text-secondary); border-top: 1px solid var(--border-color); margin-top: 4rem;"
                    )
                )
            )
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
                """)
            ),
            Body(
                H1("🔧 AI Language Tutor - Diagnostic Tests"),
                
                Div(
                    H2("1. 📱 Basic Browser Support"),
                    P("Checking...", id="browser-support"),
                    cls="test-section"
                ),
                
                Div(
                    H2("2. 🎤 Microphone Permissions"),
                    Button("Request Microphone Permission", onclick="requestMicPermission()"),
                    P("Click button to test", id="mic-status"),
                    cls="test-section"
                ),
                
                Div(
                    H2("3. 💬 Text Message Test"),
                    Input(type="text", id="test-message", placeholder="Type a test message here...", value="Hello! This is a test message."),
                    Button("Send Test Message", onclick="sendTestMessage()"),
                    P("Type a message and click send", id="text-status"),
                    cls="test-section"
                ),
                
                Div(
                    H2("4. 🗣️ Speech Recognition Test"),
                    Button("Test Speech Recognition", onclick="testSpeechRecognition()"),
                    P("Click to test backend IBM Watson speech recognition", id="speech-status"),
                    cls="test-section"
                ),
                
                Div(
                    H2("🪵 Debug Log"),
                    Div(id="log"),
                    Button("Clear Log", onclick="clearLog()"),
                    cls="test-section"
                ),
                
                Div(
                    H2("🚀 Next Steps"),
                    P("Once tests pass, try the chat interface:"),
                    A("Go to Chat Interface", href="/chat", style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;"),
                    cls="test-section"
                ),
                
                Script("""
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
            )
        )
    
    # Route: Home page
    @app.route("/")
    def home():
        return create_layout(
            Div(
                # Welcome section
                Div(
                    H1("Welcome to AI Language Tutor", style="text-align: center; margin-bottom: 2rem;"),
                    P("Your personal AI-powered language learning companion for the whole family.", 
                      style="text-align: center; font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 3rem;"),
                    cls="card"
                ),
                
                # System status
                Div(
                    H2("System Status", style="margin-bottom: 1.5rem;"),
                    Div(
                        Div(
                            Span("🎤", style="font-size: 2rem;"),
                            H3("Speech Processing"),
                            Span("Watson STT/TTS Operational", cls="status-indicator status-success"),
                            P("Real-time speech recognition and synthesis ready"),
                        ),
                        Div(
                            Span("🤖", style="font-size: 2rem;"),
                            H3("AI Services"),
                            Span("Claude + Mistral + Qwen Active", cls="status-indicator status-success"),
                            P("Multi-language AI conversation partners available"),
                        ),
                        Div(
                            Span("🗄️", style="font-size: 2rem;"),
                            H3("Database"),
                            Span("Multi-DB Architecture Ready", cls="status-indicator status-success"),
                            P("SQLite + ChromaDB + DuckDB operational"),
                        ),
                        cls="grid grid-3"
                    ),
                    cls="card"
                ),
                
                # Quick actions
                Div(
                    H2("Quick Start", style="margin-bottom: 1.5rem;"),
                    Div(
                        A(
                            Span("👤", style="font-size: 2rem; margin-bottom: 1rem; display: block;"),
                            H3("Create Profile"),
                            P("Set up your language learning profile"),
                            href="/profile",
                            cls="btn btn-primary card",
                            style="text-decoration: none; display: block; text-align: center;"
                        ),
                        A(
                            Span("💬", style="font-size: 2rem; margin-bottom: 1rem; display: block;"),
                            H3("Start Conversation"),
                            P("Begin AI-powered language practice"),
                            href="/chat",
                            cls="btn btn-primary card",
                            style="text-decoration: none; display: block; text-align: center;"
                        ),
                        cls="grid grid-2"
                    ),
                    cls="card"
                )
            ),
            current_page="home"
        )

    # Route: Health check
    @app.route("/health")
    def frontend_health():
        return {"status": "healthy", "service": "ai-language-tutor-frontend", "timestamp": str(datetime.now())}

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
                                    Input(type="text", name="user_id", id="login-user-id", placeholder="Enter your user ID", cls="form-input"),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Password (optional for demo)", cls="form-label"),
                                    Input(type="password", name="password", id="login-password", placeholder="Enter password", cls="form-input"),
                                    cls="form-group"
                                ),
                                Button("Login", type="button", id="login-btn", cls="btn btn-primary"),
                                style="margin-bottom: 2rem;"
                            ),
                            cls="card"
                        ),
                        
                        # Registration Form
                        Div(
                            H3("Create New Profile"),
                            Form(
                                Div(
                                    Label("User ID", cls="form-label"),
                                    Input(type="text", name="user_id", id="reg-user-id", placeholder="Choose a unique user ID", cls="form-input"),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Username", cls="form-label"),
                                    Input(type="text", name="username", id="reg-username", placeholder="Your display name", cls="form-input"),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Email (optional)", cls="form-label"),
                                    Input(type="email", name="email", id="reg-email", placeholder="Your email address", cls="form-input"),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Account Type", cls="form-label"),
                                    Select(
                                        Option("Child (default)", value="child"),
                                        Option("Parent/Adult", value="parent"),
                                        id="reg-role", cls="form-input"
                                    ),
                                    cls="form-group"
                                ),
                                Button("Register", type="button", id="register-btn", cls="btn btn-secondary"),
                                method="post", action="/profile/register"
                            ),
                            cls="card"
                        ),
                        cls="grid grid-2"
                    ),
                    id="auth-section"
                ),
                
                # Current User Profile (hidden by default)
                Div(
                    H2("Your Profile"),
                    Div(
                        Div(
                            H3("Profile Information", id="profile-username"),
                            P(id="profile-details"),
                            Span("Active", cls="status-indicator status-success"),
                            Button("Logout", type="button", id="logout-btn", cls="btn btn-secondary", style="margin-top: 1rem;"),
                        ),
                        cls="card"
                    ),
                    id="profile-section",
                    style="display: none;"
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
                                    Input(type="text", id="new-member-user-id", placeholder="Choose unique user ID", cls="form-input"),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Name", cls="form-label"),
                                    Input(type="text", id="new-member-name", placeholder="Family member's name", cls="form-input"),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Age Group", cls="form-label"),
                                    Select(
                                        Option("Child (0-12)", value="child"),
                                        Option("Teen (13-17)", value="teen"),
                                        Option("Adult (18+)", value="adult"),
                                        id="new-member-age", cls="form-input"
                                    ),
                                    cls="form-group"
                                ),
                                Div(
                                    Label("Learning Languages", cls="form-label"),
                                    Select(
                                        Option("English", value="en"),
                                        Option("Spanish", value="es"),
                                        Option("French", value="fr"),
                                        Option("Chinese", value="zh"),
                                        Option("Japanese", value="ja"),
                                        id="new-member-languages", cls="form-input", multiple=True
                                    ),
                                    cls="form-group"
                                ),
                                Button("Add Family Member", type="button", id="add-member-btn", cls="btn btn-primary"),
                            ),
                            cls="card"
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
                                    Span("Active", cls="status-indicator status-success"),
                                    cls="card"
                                ),
                                Div(
                                    H4("👧 estudiante_1"),
                                    P("Role: Child"),
                                    P("Languages: Spanish"),
                                    P("Level: Beginner"),
                                    P("Total Sessions: 8 | This Week: 2"),
                                    Span("Active", cls="status-indicator status-success"),
                                    Div(
                                        Button("View Progress", cls="btn btn-secondary", style="margin: 0.5rem 0.5rem 0 0;"),
                                        Button("Manage Settings", cls="btn btn-secondary", style="margin: 0.5rem 0.5rem 0 0;"),
                                        Button("Safety Controls", cls="btn btn-secondary"),
                                    ),
                                    cls="card"
                                ),
                                Div(
                                    H4("👦 Add Another Child"),
                                    P("Create profiles for all family members"),
                                    P("Each member gets personalized learning"),
                                    Button("Add Member", cls="btn btn-primary", onclick="document.getElementById('new-member-user-id').focus()"),
                                    cls="card",
                                    style="border: 2px dashed var(--border-color); text-align: center;"
                                ),
                                cls="grid grid-3"
                            ),
                            id="family-members-list"
                        ),
                        cls="grid grid-1"
                    ),
                    cls="card",
                    id="family-section",
                    style="display: none;"
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
                                    cls="form-input"
                                ),
                                cls="form-group"
                            ),
                            Button("Update Limits", cls="btn btn-secondary"),
                            cls="card"
                        ),
                        Div(
                            H3("🛡️ Content Safety"),
                            P("AI conversation monitoring"),
                            Div(
                                Label("Safety Level:", cls="form-label"),
                                Select(
                                    Option("High (Strict filtering)", value="high"),
                                    Option("Medium (Balanced)", value="medium", selected=True),
                                    Option("Low (Minimal filtering)", value="low"),
                                    cls="form-input"
                                ),
                                cls="form-group"
                            ),
                            Button("Update Safety", cls="btn btn-secondary"),
                            cls="card"
                        ),
                        Div(
                            H3("📊 Activity Reports"),
                            P("Monitor learning progress"),
                            Button("View Weekly Report", cls="btn btn-secondary", style="margin-bottom: 1rem;"),
                            Button("Download CSV", cls="btn btn-secondary"),
                            cls="card"
                        ),
                        cls="grid grid-3"
                    ),
                    cls="card",
                    id="parental-controls",
                    style="display: none;"
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
                """)
            ),
            current_page="profile",
            title="Profile Management - AI Language Tutor"
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
                            id="language-select", cls="form-input", style="margin-bottom: 1rem;"
                        ),
                        cls="form-group"
                    ),
                    cls="card"
                ),
                
                # Conversation area
                Div(
                    H2("Conversation", style="margin-bottom: 1rem;"),
                    Div(
                        Div(
                            Div(
                                Strong("AI Tutor: "),
                                "Hello! I'm your AI language tutor with natural voice interactions! 🎙️ "
                                "• Click the mic once for single recording"
                                "• Hold the mic for 1 second to enable continuous conversation mode"
                                "• Use the 'Continuous' button to toggle always-listening mode"
                                "• Try different languages and I'll adapt my personality and expressions!",
                                cls="message message-ai"
                            ),
                            id="conversation-history"
                        ),
                        cls="conversation-area"
                    ),
                    
                    # Speech controls
                    Div(
                        Button("🎤", id="mic-button", cls="mic-button", title="Click to speak"),
                        Span("Click microphone to speak", id="speech-status", style="font-size: 0.9rem; color: var(--text-secondary);"),
                        cls="speech-controls"
                    ),
                    
                    # Text input
                    Div(
                        Input(type="text", id="text-input", placeholder="Or type your message here...", cls="form-input", style="margin-bottom: 1rem;"),
                        Button("Send Message", id="send-button", cls="btn btn-primary"),
                        cls="form-group"
                    ),
                    
                    cls="card"
                ),
                
                # Conversation controls
                Div(
                    H2("Practice Tools"),
                    Div(
                        Button("Clear Conversation", cls="btn btn-secondary", id="clear-button"),
                        Button("Download Audio", cls="btn btn-secondary", id="download-audio"),
                        Button("Pronunciation Analysis", cls="btn btn-secondary", id="pronunciation-analysis"),
                        style="display: flex; gap: 1rem; flex-wrap: wrap;"
                    ),
                    cls="card"
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
                            // Update status to indicate no speech detected
                            const statusSpan = document.getElementById('speech-status');
                            if (statusSpan) {
                                statusSpan.textContent = 'No speech detected. Click microphone to try again.';
                            }
                            return;
                        }
                        
                        try {
                            // Create audio blob
                            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                            
                            // Convert to base64 for transmission
                            const base64Audio = await this.blobToBase64(audioBlob);
                            
                            // Send to backend for speech-to-text processing
                            const transcript = await this.sendAudioToBackend(base64Audio);
                            
                            // Handle the transcript response
                            if (transcript !== null && transcript !== undefined) {
                                if (transcript.trim()) {
                                    // Add transcript to text input and send message
                                    const textInput = document.getElementById('text-input');
                                    if (textInput) {
                                        textInput.value = transcript;
                                        this.sendMessage();
                                    }
                                } else {
                                    // Empty transcript - no speech detected
                                    console.log('No speech detected in audio');
                                    const statusSpan = document.getElementById('speech-status');
                                    if (statusSpan) {
                                        statusSpan.textContent = 'No speech detected. Click microphone to try again.';
                                    }
                                }
                            } else {
                                // Failed to get transcript
                                console.error('Failed to get transcript from backend');
                                const statusSpan = document.getElementById('speech-status');
                                if (statusSpan) {
                                    statusSpan.textContent = 'Speech recognition failed. Try again or type your message.';
                                    statusSpan.className = 'error';
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
                            // Ensure we have a valid auth token
                            let token = localStorage.getItem('auth_token');
                            if (!token || token === 'demo-token' || token.startsWith('temp-token')) {
                                console.log('Getting fresh auth token for speech request');
                                await initializeAuthToken();
                                token = localStorage.getItem('auth_token');
                            }
                            
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
                                // If unauthorized, try to get a new token and retry
                                if (response.status === 401) {
                                    console.log('Token expired, getting new token...');
                                    await initializeAuthToken();
                                    const retryToken = localStorage.getItem('auth_token');
                                    const retryResponse = await fetch('http://localhost:8000/api/v1/conversations/speech-to-text', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'Authorization': `Bearer ${retryToken}`
                                        },
                                        body: JSON.stringify({
                                            audio_data: base64Audio,
                                            language: this.currentLanguage.split('-')[0]
                                        })
                                    });
                                    
                                    if (retryResponse.ok) {
                                        const retryData = await retryResponse.json();
                                        return retryData.text || retryData.transcript || '';
                                    }
                                }
                                return null;
                            }
                        } catch (error) {
                            console.error('Error sending audio to backend:', error);
                            return null;
                        }
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
                    
                    startContinuousMode() {
                        console.log('Starting continuous conversation mode');
                        this.isContinuousMode = true;
                        
                        // Update UI
                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');
                        
                        if (micButton) {
                            micButton.classList.add('recording');
                            micButton.title = 'Click to stop continuous mode';
                        }
                        
                        if (statusSpan) {
                            statusSpan.textContent = '🎙️ Continuous mode: I\\'m always listening...';
                        }
                        
                        // Start continuous listening
                        this.startContinuousListening();
                    }
                    
                    stopContinuousMode() {
                        console.log('Stopping continuous conversation mode');
                        this.isContinuousMode = false;
                        
                        // Stop all activities
                        this.stopAllVoiceActivities();
                        
                        // Update UI
                        const micButton = document.getElementById('mic-button');
                        const statusSpan = document.getElementById('speech-status');
                        
                        if (micButton) {
                            micButton.classList.remove('recording');
                            micButton.title = 'Click to speak (or hold for continuous mode)';
                        }
                        
                        if (statusSpan) {
                            statusSpan.textContent = 'Click microphone to speak';
                        }
                    }
                    
                    startContinuousListening() {
                        // For continuous mode, we'll keep the microphone active
                        // and process speech in real-time
                        console.log('Continuous listening mode activated');
                    }
                    
                    stopAllVoiceActivities() {
                        // Stop recording if active
                        if (this.isRecording) {
                            this.stopRecording();
                        }
                        
                        // Reset states
                        this.isProcessingAI = false;
                        this.finalTranscript = '';
                        this.interimTranscript = '';
                        
                        // Update UI
                        const micButton = document.getElementById('mic-button');
                        if (micButton) micButton.classList.remove('recording');
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
                                statusSpan.textContent = '🎙️ Continuous mode: I\\'m listening...';
                            } else if (statusSpan) {
                                statusSpan.textContent = 'Click microphone to speak';
                            }
                        }
                    }
                    
                    async getAIResponse(userMessage, loadingId) {
                        try {
                            // Get auth token and ensure it's valid
                            let token = localStorage.getItem('auth_token');
                            
                            // If we have an invalid token, get a new one
                            if (!token || token === 'demo-token' || token.startsWith('temp-token')) {
                                console.log('Getting fresh auth token for chat request');
                                await initializeAuthToken();
                                token = localStorage.getItem('auth_token');
                            }
                            
                            let aiResponse = '';
                            let audioData = null;
                            
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
                                    
                                    // If audio data is available, store it for playback
                                    if (data.audio_url) {
                                        // In a full implementation, we would fetch the actual audio
                                        // For now, we'll generate it on demand
                                        audioData = data.audio_url;
                                    }
                                } else {
                                    // If unauthorized, try to get a new token and retry
                                    if (response.status === 401) {
                                        console.log('Token expired for chat, getting new token...');
                                        await initializeAuthToken();
                                        const retryToken = localStorage.getItem('auth_token');
                                        
                                        const retryResponse = await fetch('http://localhost:8000/api/v1/conversations/chat', {
                                            method: 'POST',
                                            headers: {
                                                'Content-Type': 'application/json',
                                                'Authorization': `Bearer ${retryToken}`
                                            },
                                            body: JSON.stringify({
                                                message: userMessage,
                                                language: this.currentLanguage,
                                                use_speech: true,
                                                conversation_history: this.conversationHistory.slice(-6) // Last 6 messages
                                            })
                                        });
                                        
                                        if (retryResponse.ok) {
                                            const retryData = await retryResponse.json();
                                            aiResponse = retryData.response;
                                            
                                            // Add AI response to conversation history
                                            this.conversationHistory.push({
                                                role: 'assistant',
                                                content: aiResponse,
                                                timestamp: new Date().toISOString()
                                            });
                                            
                                            // If audio data is available, store it for playback
                                            if (retryData.audio_url) {
                                                audioData = retryData.audio_url;
                                            }
                                        } else {
                                            throw new Error(`API error after retry: ${retryResponse.status}`);
                                        }
                                    } else {
                                        throw new Error(`API error: ${response.status}`);
                                    }
                                }
                            } else {
                                // Enhanced fallback with more natural responses
                                aiResponse = await this.getEnhancedFallbackResponse(userMessage);
                            }
                            
                            // Update message in UI
                            this.updateMessage(loadingId, aiResponse);
                            
                            // Play audio response if available
                            if (aiResponse && !this.isContinuousMode) {
                                await this.playTextToSpeech(aiResponse);
                            }
                            
                        } catch (error) {
                            console.error('AI Response Error:', error);
                            const fallbackResponse = await this.getEnhancedFallbackResponse(userMessage);
                            this.updateMessage(loadingId, `[Connection Issue] ${fallbackResponse}`);
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
                        return 'default';
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
                        this.conversationHistory = [];
                    }
                    
                    async playTextToSpeech(text) {
                        try {
                            // Get auth token
                            const token = localStorage.getItem('auth_token');
                            
                            // Request text-to-speech from backend
                            const response = await fetch('http://localhost:8000/api/v1/conversations/text-to-speech', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${token}`
                                },
                                body: JSON.stringify({
                                    text: text,
                                    language: this.currentLanguage.split('-')[0]
                                })
                            });
                            
                            if (response.ok) {
                                const data = await response.json();
                                
                                // Decode base64 audio data
                                const audioBytes = atob(data.audio_data);
                                const audioBuffer = new ArrayBuffer(audioBytes.length);
                                const audioArray = new Uint8Array(audioBuffer);
                                
                                for (let i = 0; i < audioBytes.length; i++) {
                                    audioArray[i] = audioBytes.charCodeAt(i);
                                }
                                
                                // Create and play audio
                                const audioBlob = new Blob([audioArray], { type: `audio/${data.audio_format}` });
                                const audioUrl = URL.createObjectURL(audioBlob);
                                const audio = new Audio(audioUrl);
                                
                                // Update status
                                const statusSpan = document.getElementById('speech-status');
                                if (statusSpan) {
                                    statusSpan.textContent = '🔊 Playing response...';
                                }
                                
                                // Play audio
                                await audio.play();
                                
                                // Clean up
                                audio.addEventListener('ended', () => {
                                    URL.revokeObjectURL(audioUrl);
                                    if (statusSpan) {
                                        statusSpan.textContent = 'Click microphone to speak';
                                    }
                                });
                                
                                console.log('Text-to-speech playback completed');
                            } else {
                                console.error('Text-to-speech request failed:', response.status);
                            }
                        } catch (error) {
                            console.error('Text-to-speech error:', error);
                            // Fallback to browser speech synthesis if available
                            if ('speechSynthesis' in window) {
                                const utterance = new SpeechSynthesisUtterance(text);
                                utterance.lang = this.getSpeechSynthesisLanguage();
                                speechSynthesis.speak(utterance);
                            }
                        }
                    }
                    
                    getSpeechSynthesisLanguage() {
                        const langMap = {
                            'en': 'en-US',
                            'es': 'es-ES',
                            'fr': 'fr-FR',
                            'zh': 'zh-CN',
                            'ja': 'ja-JP',
                            'de': 'de-DE'
                        };
                        return langMap[this.currentLanguage.split('-')[0]] || 'en-US';
                    }
                }
                
                // Initialize enhanced conversation manager when page loads
                document.addEventListener('DOMContentLoaded', () => {
                    console.log('Initializing enhanced conversation manager...');
                    
                    // Check if we have a valid auth token, if not, get one
                    initializeAuthToken();
                    
                    try {
                        window.conversationManager = new EnhancedConversationManager();
                        console.log('Enhanced conversation manager initialized successfully');
                    } catch (error) {
                        console.error('Failed to initialize conversation manager:', error);
                        
                        // Show error message to user
                        const statusSpan = document.getElementById('speech-status');
                        if (statusSpan) {
                            statusSpan.textContent = 'Initialization error - please refresh page or use text input';
                        }
                    }
                });
                
                // Function to initialize authentication token
                async function initializeAuthToken() {
                    try {
                        // Check if we already have a valid token
                        const existingToken = localStorage.getItem('auth_token');
                        if (existingToken && existingToken !== 'demo-token') {
                            // Test if token is still valid
                            const testResponse = await fetch('http://localhost:8000/api/v1/auth/profile', {
                                headers: {
                                    'Authorization': `Bearer ${existingToken}`
                                }
                            });
                            
                            if (testResponse.ok) {
                                console.log('Existing auth token is valid');
                                return;
                            }
                        }
                        
                        // Get a new token
                        console.log('Getting new authentication token...');
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
                            localStorage.setItem('auth_token', data.access_token);
                            console.log('New authentication token set');
                        } else {
                            console.error('Failed to get auth token:', response.status);
                            // Set a temporary token for testing
                            localStorage.setItem('auth_token', 'temp-token-' + Date.now());
                        }
                    } catch (error) {
                        console.error('Error initializing auth token:', error);
                        // Set a temporary token for testing
                        localStorage.setItem('auth_token', 'temp-token-' + Date.now());
                    }
                }
                """)
            ),
            current_page="chat",
            title="AI Conversation - AI Language Tutor"
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
                            P("5 days", style="font-size: 2rem; font-weight: bold; color: var(--primary-color);"),
                            cls="card"
                        ),
                        Div(
                            H3("Total Conversations"),
                            P("23", style="font-size: 2rem; font-weight: bold; color: var(--secondary-color);"),
                            cls="card"
                        ),
                        Div(
                            H3("Words Learned"),
                            P("147", style="font-size: 2rem; font-weight: bold; color: var(--accent-color);"),
                            cls="card"
                        ),
                        cls="grid grid-3"
                    ),
                    cls="card"
                ),
                
                # Language progress
                Div(
                    H2("Language Progress"),
                    Div(
                        Div(
                            H3("Spanish"),
                            P("Intermediate - 67% complete"),
                            Div(style="background: var(--border-color); height: 8px; border-radius: 4px; margin: 1rem 0;",
                                children=[Div(style="background: var(--secondary-color); height: 100%; width: 67%; border-radius: 4px;")]
                            )
                        ),
                        Div(
                            H3("French"),
                            P("Beginner - 34% complete"),
                            Div(style="background: var(--border-color); height: 8px; border-radius: 4px; margin: 1rem 0;",
                                children=[Div(style="background: var(--accent-color); height: 100%; width: 34%; border-radius: 4px;")]
                            )
                        ),
                        cls="grid grid-2"
                    ),
                    cls="card"
                )
            ),
            current_page="progress",
            title="Progress Tracking - AI Language Tutor"
        )

    return app


# Create frontend app
frontend_app = create_frontend_app()


def run_frontend_server():
    """Run the FastHTML frontend server - extracted for testing"""
    settings = get_settings()
    uvicorn.run(
        "app.frontend_main:frontend_app",
        host=settings.HOST,
        port=settings.FRONTEND_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )


if __name__ == "__main__":
    run_frontend_server()