"""
Tests for Chat Frontend Module
Complete coverage for app/frontend/chat.py
"""

import pytest
from fastapi.testclient import TestClient

from app.frontend_main import frontend_app


class TestChatRoute:
    """Test suite for chat frontend route"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_chat_route_accessible(self):
        """Test that chat route is accessible"""
        response = self.client.get("/chat")
        assert response.status_code == 200

    def test_chat_returns_html(self):
        """Test that chat page returns valid HTML structure"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Validate HTML structure
        assert "<html" in content.lower()
        assert "AI Conversation Practice" in content

    def test_chat_includes_language_selection(self):
        """Test that chat page includes language selection"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for language selection
        assert "Select Language" in content
        assert "language-select" in content

    def test_chat_includes_practice_mode_selection(self):
        """Test that chat page includes practice mode selection"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for practice mode selection
        assert "Practice Mode" in content
        assert "practice-mode-select" in content

    def test_chat_includes_conversation_area(self):
        """Test that chat page includes conversation area"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for conversation area
        assert "Conversation" in content
        assert "conversation-history" in content

    def test_chat_includes_speech_controls(self):
        """Test that chat page includes speech controls"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for speech controls
        assert "mic-button" in content
        assert "speech-status" in content

    def test_chat_includes_text_input(self):
        """Test that chat page includes text input"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for text input
        assert "text-input" in content
        assert "send-button" in content

    def test_chat_includes_javascript(self):
        """Test that chat page includes JavaScript conversation manager"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for JavaScript class
        assert "EnhancedConversationManager" in content

    def test_chat_includes_realtime_analysis(self):
        """Test that chat page includes real-time analysis panel"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for real-time analysis
        assert "Real-Time Analysis" in content
        assert "start-analysis-btn" in content

    def test_chat_includes_voice_selection(self):
        """Test that chat page includes voice selection"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for voice selection
        assert "Voice Persona" in content
        assert "voice-select" in content

    def test_chat_includes_scenario_selection(self):
        """Test that chat page includes scenario selection"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for scenario selection
        assert "scenario-select" in content
        assert "scenario-selection" in content

    def test_chat_includes_tutor_mode_selection(self):
        """Test that chat page includes tutor mode selection"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for tutor mode selection
        assert "tutor-mode-select" in content
        assert "tutor-mode-selection" in content

    def test_chat_includes_conversation_controls(self):
        """Test that chat page includes conversation control buttons"""
        response = self.client.get("/chat")

        assert response.status_code == 200
        content = response.text

        # Check for control buttons
        assert "Clear Conversation" in content
        assert "Download Audio" in content
        assert "Pronunciation Analysis" in content
