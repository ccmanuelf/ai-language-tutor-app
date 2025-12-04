"""
Tests for app/api/conversations.py - Conversation API endpoints
Session 80 - Target: TRUE 100% coverage
"""

import base64
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.security import require_auth
from app.database.config import get_primary_db_session
from app.main import app
from app.models.simple_user import SimpleUser

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_user():
    """Create a sample authenticated user"""
    user = SimpleUser(
        id=1,
        user_id="testuser123",
        username="testuser",
        email="test@example.com",
        role="parent",
    )
    return user


@pytest.fixture
def mock_db():
    """Create mock database session"""
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def mock_ai_response():
    """Create mock AI response object"""
    response = Mock()
    response.content = "Hello! How can I help you today?"
    response.cost = 0.01
    return response


@pytest.fixture
def mock_tts_result():
    """Create mock TTS result object"""
    result = Mock()
    result.audio_data = b"fake_audio_data"
    result.audio_format = Mock(value="wav")
    result.sample_rate = 22050
    result.duration_seconds = 2.5
    return result


@pytest.fixture
def mock_stt_result():
    """Create mock STT recognition result"""
    result = Mock()
    result.transcript = "Hello, this is a test"
    result.confidence = 0.95
    result.language = "en"
    return result


# ============================================================================
# TEST CLASS 1: GET /languages - Supported Languages
# ============================================================================


class TestGetSupportedLanguages:
    """Test the GET /languages endpoint"""

    def test_get_languages_success(self, client):
        """Test getting supported languages list"""
        response = client.get("/api/v1/conversations/languages")

        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert isinstance(data["languages"], list)
        assert len(data["languages"]) > 0

        # Verify first language has required fields
        first_lang = data["languages"][0]
        assert "code" in first_lang
        assert "name" in first_lang
        assert "providers" in first_lang
        assert "display" in first_lang

    def test_get_languages_includes_all_major_languages(self, client):
        """Test that response includes major supported languages"""
        response = client.get("/api/v1/conversations/languages")
        data = response.json()

        language_codes = [lang["code"] for lang in data["languages"]]
        assert "en" in language_codes
        assert "es" in language_codes
        assert "fr" in language_codes
        assert "zh" in language_codes
        assert "ja" in language_codes


# ============================================================================
# TEST CLASS 2: GET /history - Conversation History
# ============================================================================


class TestGetConversationHistory:
    """Test the GET /history endpoint"""

    def test_get_history_requires_auth(self, client):
        """Test that history endpoint requires authentication"""
        # Don't override auth dependency - should get 401/403
        response = client.get("/api/v1/conversations/history")
        assert response.status_code in [401, 403]

    def test_get_history_success(self, client, sample_user, mock_db):
        """Test getting conversation history for authenticated user"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.get("/api/v1/conversations/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Verify demo data structure
        if len(data) > 0:
            conv = data[0]
            assert "messages" in conv
            assert "total_messages" in conv
            assert "conversation_id" in conv
            assert "started_at" in conv

        app.dependency_overrides.clear()

    def test_get_history_returns_demo_data(self, client, sample_user, mock_db):
        """Test that history returns demo data (current implementation)"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.get("/api/v1/conversations/history")
        data = response.json()

        # Current implementation returns demo data
        assert len(data) == 1
        assert data[0]["conversation_id"] == "demo_conv_001"
        assert data[0]["total_messages"] == 2

        app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 3: GET /stats - Conversation Statistics
# ============================================================================


class TestGetConversationStats:
    """Test the GET /stats endpoint"""

    def test_get_stats_requires_auth(self, client):
        """Test that stats endpoint requires authentication"""
        response = client.get("/api/v1/conversations/stats")
        assert response.status_code in [401, 403]

    def test_get_stats_success(self, client, sample_user, mock_db):
        """Test getting conversation statistics"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.get("/api/v1/conversations/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_conversations" in data
        assert "total_messages" in data
        assert "languages_practiced" in data
        assert "favorite_language" in data
        assert "total_practice_time" in data
        assert "this_week" in data

        app.dependency_overrides.clear()

    def test_get_stats_returns_demo_statistics(self, client, sample_user, mock_db):
        """Test that stats returns demo data (current implementation)"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.get("/api/v1/conversations/stats")
        data = response.json()

        # Verify demo data values
        assert data["total_conversations"] == 5
        assert data["total_messages"] == 47
        assert isinstance(data["languages_practiced"], list)

        app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 4: DELETE /clear/{conversation_id} - Clear Conversation
# ============================================================================


class TestClearConversation:
    """Test the DELETE /clear/{conversation_id} endpoint"""

    def test_clear_conversation_requires_auth(self, client):
        """Test that clear endpoint requires authentication"""
        response = client.delete("/api/v1/conversations/clear/test_conv_123")
        assert response.status_code in [401, 403]

    def test_clear_conversation_success(self, client, sample_user, mock_db):
        """Test clearing a conversation"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        conversation_id = "test_conv_123"
        response = client.delete(f"/api/v1/conversations/clear/{conversation_id}")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert conversation_id in data["message"]
        assert "cleared successfully" in data["message"]

        app.dependency_overrides.clear()

    def test_clear_conversation_with_special_characters(
        self, client, sample_user, mock_db
    ):
        """Test clearing conversation with special characters in ID"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        conversation_id = "conv_user_20251203_143022"
        response = client.delete(f"/api/v1/conversations/clear/{conversation_id}")

        assert response.status_code == 200

        app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 5: Helper Functions
# ============================================================================


class TestHelperFunctions:
    """Test private helper functions"""

    def test_parse_language_and_provider_with_provider(self):
        """Test parsing language code with provider"""
        from app.api.conversations import _parse_language_and_provider

        language_code, ai_provider = _parse_language_and_provider("es-claude")
        assert language_code == "es"
        assert ai_provider == "claude"

        language_code, ai_provider = _parse_language_and_provider("fr-mistral")
        assert language_code == "fr"
        assert ai_provider == "mistral"

    def test_parse_language_and_provider_without_provider(self):
        """Test parsing language code without provider (defaults to claude)"""
        from app.api.conversations import _parse_language_and_provider

        language_code, ai_provider = _parse_language_and_provider("en")
        assert language_code == "en"
        assert ai_provider == "claude"

    def test_parse_language_and_provider_empty_string(self):
        """Test parsing empty language string"""
        from app.api.conversations import _parse_language_and_provider

        language_code, ai_provider = _parse_language_and_provider("")
        assert language_code == ""  # Empty string returns empty
        assert ai_provider == "claude"  # Provider defaults to claude

    def test_generate_conversation_ids(self):
        """Test conversation and message ID generation"""
        from app.api.conversations import _generate_conversation_ids

        user_id = "testuser123"
        conversation_id, message_id = _generate_conversation_ids(user_id)

        # Verify conversation ID format
        assert conversation_id.startswith(f"conv_{user_id}_")
        assert len(conversation_id) > len(f"conv_{user_id}_")

        # Verify message ID is UUID format
        try:
            uuid.UUID(message_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        assert is_valid_uuid

    def test_get_fallback_texts_contains_all_languages(self):
        """Test that fallback texts dictionary contains all supported languages"""
        from app.api.conversations import _get_fallback_texts

        fallback_texts = _get_fallback_texts()

        assert "en" in fallback_texts
        assert "es" in fallback_texts
        assert "fr" in fallback_texts
        assert "zh" in fallback_texts
        assert "ja" in fallback_texts

        # Verify all values are non-empty strings
        for lang, text in fallback_texts.items():
            assert isinstance(text, str)
            assert len(text) > 0
            assert "{message}" in text  # Should have placeholder

    def test_get_demo_fallback_responses_contains_all_languages(self):
        """Test that demo fallback responses contain all supported languages"""
        from app.api.conversations import _get_demo_fallback_responses

        demo_responses = _get_demo_fallback_responses()

        assert "en" in demo_responses
        assert "es" in demo_responses
        assert "fr" in demo_responses
        assert "zh" in demo_responses
        assert "ja" in demo_responses

        # Verify all values are non-empty strings
        for lang, text in demo_responses.items():
            assert isinstance(text, str)
            assert len(text) > 0
            assert "{message}" in text  # Should have placeholder


# ============================================================================
# TEST CLASS 6: POST /speech-to-text - Speech Recognition
# ============================================================================


class TestSpeechToText:
    """Test the POST /speech-to-text endpoint"""

    def test_speech_to_text_requires_auth(self, client):
        """Test that speech-to-text endpoint requires authentication"""
        response = client.post("/api/v1/conversations/speech-to-text", json={})
        assert response.status_code in [401, 403]

    def test_speech_to_text_success(self, client, sample_user):
        """Test speech-to-text endpoint response structure"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        # Create test audio data
        test_audio = base64.b64encode(b"fake_audio_data").decode("utf-8")

        response = client.post(
            "/api/v1/conversations/speech-to-text",
            json={"audio_data": test_audio, "language": "en"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        # Text will be actual STT result or error message
        assert isinstance(data["text"], str)

        app.dependency_overrides.clear()

    def test_speech_to_text_no_audio_data(self, client, sample_user):
        """Test speech-to-text with no audio data provided"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/speech-to-text", json={"language": "en"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "No audio data provided"

        app.dependency_overrides.clear()

    def test_speech_to_text_with_different_language(self, client, sample_user):
        """Test speech-to-text with different language"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        test_audio = base64.b64encode(b"fake_spanish_audio").decode("utf-8")

        response = client.post(
            "/api/v1/conversations/speech-to-text",
            json={"audio_data": test_audio, "language": "es"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert isinstance(data["text"], str)

        app.dependency_overrides.clear()

    def test_speech_to_text_processing_error(self, client, sample_user):
        """Test speech-to-text with bad audio data"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        test_audio = base64.b64encode(b"bad_audio_data").decode("utf-8")

        response = client.post(
            "/api/v1/conversations/speech-to-text",
            json={"audio_data": test_audio, "language": "en"},
        )

        assert response.status_code == 200
        data = response.json()
        # Will get error message or fallback text
        assert "text" in data
        assert isinstance(data["text"], str)

        app.dependency_overrides.clear()

    def test_speech_to_text_default_language(self, client, sample_user):
        """Test speech-to-text uses default language when not provided"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post("/api/v1/conversations/speech-to-text", json={})

        # Should not crash, should use default 'en'
        assert response.status_code == 200

        app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 7: POST /text-to-speech - Text to Speech
# ============================================================================


class TestTextToSpeech:
    """Test the POST /text-to-speech endpoint"""

    def test_text_to_speech_requires_auth(self, client):
        """Test that text-to-speech endpoint requires authentication"""
        response = client.post("/api/v1/conversations/text-to-speech", json={})
        assert response.status_code in [401, 403]

    def test_text_to_speech_success(self, client, sample_user):
        """Test text-to-speech endpoint response structure"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/text-to-speech",
            json={
                "text": "Hello, this is a test",
                "language": "en",
                "voice_type": "neural",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_data" in data
        assert "audio_format" in data
        assert "sample_rate" in data
        assert "duration" in data

        # Verify audio data is base64 encoded
        try:
            base64.b64decode(data["audio_data"])
        except Exception:
            pytest.fail("Audio data is not valid base64")

        app.dependency_overrides.clear()

    def test_text_to_speech_no_text(self, client, sample_user):
        """Test text-to-speech with no text provided"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/text-to-speech", json={"language": "en"}
        )

        # HTTPException(400) is raised but caught and re-raised as 500
        assert response.status_code == 500
        data = response.json()
        assert "No text provided" in data["detail"]

        app.dependency_overrides.clear()

    def test_text_to_speech_with_different_language(self, client, sample_user):
        """Test text-to-speech with different language"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/text-to-speech",
            json={
                "text": "Hola, esto es una prueba",
                "language": "es",
                "voice_type": "neural",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_data" in data
        assert "duration" in data

        app.dependency_overrides.clear()

    def test_text_to_speech_default_values(self, client, sample_user):
        """Test text-to-speech with default language and voice_type"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/text-to-speech", json={"text": "Test message"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_data" in data
        # Should use defaults: language='en', voice_type='neural'

        app.dependency_overrides.clear()

    def test_text_to_speech_empty_text(self, client, sample_user):
        """Test text-to-speech with empty text string"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/text-to-speech",
            json={"text": "", "language": "en"},
        )

        # Empty text should be caught
        assert response.status_code in [400, 500]

        app.dependency_overrides.clear()

    def test_text_to_speech_with_standard_voice(self, client, sample_user):
        """Test text-to-speech with standard (non-neural) voice"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        response = client.post(
            "/api/v1/conversations/text-to-speech",
            json={
                "text": "Test with standard voice",
                "language": "en",
                "voice_type": "standard",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_data" in data

        app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 8: Advanced Helper Function Tests
# ============================================================================


class TestChatHelperFunctionsAdvanced:
    """Test advanced helper function scenarios for coverage"""

    @pytest.mark.asyncio
    @patch("app.api.conversations.ai_router")
    async def test_get_ai_response_no_service_available(self, mock_router):
        """Test _get_ai_response when no AI service is available"""
        from app.api.conversations import ChatRequest, _get_ai_response

        # Mock provider selection with no service
        mock_selection = Mock()
        mock_selection.service = None
        mock_router.select_provider = AsyncMock(return_value=mock_selection)

        request = ChatRequest(message="Hello", language="en-claude")

        # Should raise exception when no service available
        with pytest.raises(Exception) as exc_info:
            await _get_ai_response(request, "en", "testuser123")

        assert "No AI service available" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("app.api.conversations.speech_processor")
    async def test_generate_speech_if_requested_success(self, mock_processor):
        """Test _generate_speech_if_requested returns audio URL"""
        from app.api.conversations import ChatRequest, _generate_speech_if_requested

        # Mock TTS result
        mock_tts = Mock()
        mock_tts.audio_data = b"fake_audio"
        mock_processor.process_text_to_speech = AsyncMock(return_value=mock_tts)

        request = ChatRequest(message="Hello", use_speech=True)
        audio_url = await _generate_speech_if_requested(
            request, "Test response", "en", "test_msg_123"
        )

        assert audio_url == "/api/v1/audio/test_msg_123.wav"

    @pytest.mark.asyncio
    @patch("app.api.conversations.speech_processor")
    async def test_generate_speech_if_requested_failure(self, mock_processor):
        """Test _generate_speech_if_requested returns None on error"""
        from app.api.conversations import ChatRequest, _generate_speech_if_requested

        # Mock TTS to raise exception
        mock_processor.process_text_to_speech = AsyncMock(
            side_effect=Exception("TTS failed")
        )

        request = ChatRequest(message="Hello", use_speech=True)
        audio_url = await _generate_speech_if_requested(
            request, "Test response", "en", "test_msg_123"
        )

        assert audio_url is None

    @pytest.mark.asyncio
    async def test_generate_speech_when_not_requested(self):
        """Test _generate_speech_if_requested returns None when speech not requested"""
        from app.api.conversations import ChatRequest, _generate_speech_if_requested

        request = ChatRequest(message="Hello", use_speech=False)
        audio_url = await _generate_speech_if_requested(
            request, "Test response", "en", "test_msg_123"
        )

        assert audio_url is None


# ============================================================================
# TEST CLASS 9: POST /chat - Main Chat Endpoint
# ============================================================================


class TestChatEndpoint:
    """Test the POST /chat endpoint - main conversation functionality"""

    def test_chat_requires_auth(self, client):
        """Test that chat endpoint requires authentication"""
        response = client.post("/api/v1/conversations/chat", json={"message": "Hello"})
        assert response.status_code in [401, 403]

    def test_chat_basic_message(self, client, sample_user, mock_db):
        """Test basic chat message"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "Hello, how are you?",
                "language": "en-claude",
                "use_speech": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "message_id" in data
        assert "conversation_id" in data
        assert "language" in data
        assert "ai_provider" in data
        assert "estimated_cost" in data

        # Verify conversation ID format
        assert data["conversation_id"].startswith(f"conv_{sample_user.user_id}_")

        app.dependency_overrides.clear()

    def test_chat_with_different_languages(self, client, sample_user, mock_db):
        """Test chat with different language codes"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        languages = ["en-claude", "es-claude", "fr-mistral", "zh-qwen", "ja-claude"]

        for lang in languages:
            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": "Hello", "language": lang},
            )
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            # Verify language code extracted correctly
            expected_lang_code = lang.split("-")[0]
            assert data["language"] == expected_lang_code

        app.dependency_overrides.clear()

    def test_chat_with_conversation_history(self, client, sample_user, mock_db):
        """Test chat with conversation history"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "How are you?",
                "language": "en-claude",
                "conversation_history": conversation_history,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data

        app.dependency_overrides.clear()

    def test_chat_with_speech_enabled(self, client, sample_user, mock_db):
        """Test chat with speech generation enabled"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "Tell me a story",
                "language": "en-claude",
                "use_speech": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        # audio_url may be None if TTS fails, but should be present
        assert "audio_url" in data

        app.dependency_overrides.clear()

    def test_chat_language_only_without_provider(self, client, sample_user, mock_db):
        """Test chat with language code only (no provider specified)"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "Hello",
                "language": "en",  # No provider suffix
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert data["ai_provider"] == "claude"  # Should default to claude

        app.dependency_overrides.clear()

    def test_chat_empty_message(self, client, sample_user, mock_db):
        """Test chat with empty message"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat", json={"message": "", "language": "en-claude"}
        )

        # Should still return 200 with some response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

        app.dependency_overrides.clear()

    def test_chat_default_language(self, client, sample_user, mock_db):
        """Test chat uses default language when not specified"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post("/api/v1/conversations/chat", json={"message": "Hello"})

        assert response.status_code == 200
        data = response.json()
        # Should use default 'en-claude'
        assert data["language"] == "en"

        app.dependency_overrides.clear()

    def test_chat_response_structure(self, client, sample_user, mock_db):
        """Test chat response has all required fields"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Test message", "language": "en-claude"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all fields from ChatResponse model
        required_fields = [
            "response",
            "message_id",
            "conversation_id",
            "audio_url",
            "language",
            "ai_provider",
            "estimated_cost",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify types
        assert isinstance(data["response"], str)
        assert isinstance(data["message_id"], str)
        assert isinstance(data["conversation_id"], str)
        assert isinstance(data["language"], str)
        assert isinstance(data["ai_provider"], str)
        assert isinstance(data["estimated_cost"], (int, float))

        app.dependency_overrides.clear()

    def test_chat_generates_unique_message_ids(self, client, sample_user, mock_db):
        """Test that each chat generates unique message IDs"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        message_ids = set()

        for i in range(3):
            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": f"Message {i}", "language": "en-claude"},
            )
            data = response.json()
            message_ids.add(data["message_id"])

        # All message IDs should be unique
        assert len(message_ids) == 3

        app.dependency_overrides.clear()

    def test_chat_with_special_characters(self, client, sample_user, mock_db):
        """Test chat with special characters in message"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        special_messages = [
            "Hello! How are you? 😊",
            "¿Cómo estás?",
            "Café & crème",
            "Test <html> tags",
            "Quotes 'single' and \"double\"",
        ]

        for msg in special_messages:
            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": msg, "language": "en-claude"},
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_chat_cost_estimate(self, client, sample_user, mock_db):
        """Test that chat returns cost estimate"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Hello", "language": "en-claude"},
        )

        data = response.json()
        assert "estimated_cost" in data
        assert data["estimated_cost"] >= 0

        app.dependency_overrides.clear()

    def test_chat_uses_fallback_on_unsupported_language(
        self, client, sample_user, mock_db
    ):
        """Test chat handles unsupported language gracefully"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "Hello",
                "language": "xy-unknown",  # Unsupported language
            },
        )

        # Should still return 200 with fallback
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

        app.dependency_overrides.clear()

    @patch("app.api.conversations._generate_speech_if_requested")
    @patch("app.api.conversations._get_ai_response")
    def test_chat_outer_exception_handler(
        self, mock_ai_response, mock_speech, client, sample_user, mock_db
    ):
        """Test chat outer exception handler triggers demo mode"""
        app.dependency_overrides[require_auth] = lambda: sample_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        # Make both AI response AND speech generation fail to trigger outer except
        mock_ai_response.side_effect = Exception("Complete failure")
        mock_speech.side_effect = Exception("Speech also fails")

        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Hello", "language": "en-claude"},
        )

        # Should return 200 with demo mode response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "[Demo Mode]" in data["response"]
        assert data["audio_url"] is None

        app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 10: STT Exception Handler Coverage
# ============================================================================


class TestSTTExceptionHandler:
    """Test STT exception handler that returns error details"""

    @patch("app.services.speech_processor.speech_processor")
    def test_speech_to_text_exception_with_error_field(
        self, mock_processor, client, sample_user
    ):
        """Test STT exception path that includes error field"""
        app.dependency_overrides[require_auth] = lambda: sample_user

        # Make processor raise exception to trigger except block
        mock_processor.process_speech_to_text = AsyncMock(
            side_effect=ValueError("Invalid audio format")
        )

        test_audio = base64.b64encode(b"invalid_audio").decode("utf-8")

        response = client.post(
            "/api/v1/conversations/speech-to-text",
            json={"audio_data": test_audio, "language": "en"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "error" in data
        assert "Speech recognition failed" in data["text"]

        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
