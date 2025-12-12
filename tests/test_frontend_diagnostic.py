"""
Tests for Diagnostic Frontend Module
Complete coverage for app/frontend/diagnostic.py
"""

import pytest
from fastapi.testclient import TestClient

from app.frontend_main import frontend_app


class TestDiagnosticRoute:
    """Test suite for diagnostic frontend route"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_diagnostic_route_accessible(self):
        """Test that diagnostic route is accessible at /test"""
        response = self.client.get("/test")
        assert response.status_code == 200

    def test_diagnostic_returns_html(self):
        """Test that diagnostic page returns valid HTML structure"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Validate HTML structure
        assert "<html" in content.lower()
        assert "AI Language Tutor - Diagnostics" in content

    def test_diagnostic_includes_browser_support_section(self):
        """Test that diagnostic page includes browser support check"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for browser support section
        assert "Basic Browser Support" in content
        assert "browser-support" in content

    def test_diagnostic_includes_microphone_section(self):
        """Test that diagnostic page includes microphone permission test"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for microphone section
        assert "Microphone Permissions" in content
        assert "Request Microphone Permission" in content
        assert "mic-status" in content

    def test_diagnostic_includes_text_message_section(self):
        """Test that diagnostic page includes text message test"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for text message section
        assert "Text Message Test" in content
        assert "test-message" in content
        assert "Send Test Message" in content
        assert "text-status" in content

    def test_diagnostic_includes_speech_recognition_section(self):
        """Test that diagnostic page includes speech recognition test"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for speech recognition section
        assert "Speech Recognition Test" in content
        assert "Test Speech Recognition" in content
        assert "speech-status" in content

    def test_diagnostic_includes_debug_log(self):
        """Test that diagnostic page includes debug log section"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for debug log
        assert "Debug Log" in content
        assert 'id="log"' in content
        assert "Clear Log" in content

    def test_diagnostic_includes_next_steps(self):
        """Test that diagnostic page includes next steps section"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for next steps
        assert "Next Steps" in content
        assert "Go to Chat Interface" in content
        assert 'href="/chat"' in content

    def test_diagnostic_includes_javascript_functions(self):
        """Test that diagnostic page includes required JavaScript functions"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for JavaScript functions
        assert "function log(" in content
        assert "function clearLog(" in content
        assert "function updateStatus(" in content
        assert "function getAuthToken(" in content
        assert "function checkBrowserSupport(" in content
        assert "function requestMicPermission(" in content
        assert "function sendTestMessage(" in content
        assert "function testSpeechRecognition(" in content

    def test_diagnostic_includes_styles(self):
        """Test that diagnostic page includes CSS styles"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for CSS styles
        assert ".test-section" in content
        assert ".success" in content
        assert ".error" in content
        assert ".warning" in content

    def test_diagnostic_includes_dom_content_loaded(self):
        """Test that diagnostic page includes DOMContentLoaded event listener"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for DOMContentLoaded listener
        assert "DOMContentLoaded" in content
        assert "addEventListener" in content

    def test_diagnostic_numbered_sections(self):
        """Test that diagnostic page has numbered test sections"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for numbered sections
        assert "1." in content
        assert "2." in content
        assert "3." in content
        assert "4." in content

    def test_diagnostic_emoji_icons(self):
        """Test that diagnostic page includes emoji icons"""
        response = self.client.get("/test")

        assert response.status_code == 200
        content = response.text

        # Check for emojis
        assert "🔧" in content
        assert "📱" in content
        assert "🎤" in content
        assert "💬" in content
        assert "🗣️" in content
