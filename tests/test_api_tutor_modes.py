"""
Comprehensive Test Suite for Tutor Modes API
app/api/tutor_modes.py

Session: 103
Target: TRUE 100% coverage (statements + branches + zero warnings)
Module Coverage: 41.36% → 100%

Test Coverage:
- Pydantic Models (7 models)
- API Endpoints (9 endpoints)
- Error Handling (all exception paths)
- Edge Cases (validation, authentication)

Endpoints Tested:
1. GET /available - Get available tutor modes
2. POST /session/start - Start tutor session
3. POST /conversation - Tutor conversation
4. GET /session/{session_id} - Get session info
5. POST /session/{session_id}/end - End session
6. GET /modes/{mode}/details - Mode details
7. GET /analytics - Get analytics
8. POST /session/{session_id}/feedback - Submit feedback
9. GET /categories - Get mode categories
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException

# Import module components directly for coverage measurement
from app.api.tutor_modes import (
    SessionInfo,
    StartTutorSessionRequest,
    TutorConversationRequest,
    TutorConversationResponse,
    TutorModeInfo,
    TutorSessionResponse,
    end_tutor_session,
    get_available_modes,
    get_mode_categories,
    get_mode_details,
    get_session_info,
    get_tutor_analytics,
    router,
    start_tutor_session,
    submit_session_feedback,
    tutor_conversation,
)
from app.models.database import User
from app.services.tutor_mode_manager import DifficultyLevel, TutorMode

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_user():
    """Create a mock user for authentication"""
    user = Mock(spec=User)
    user.id = "user_123"
    user.username = "testuser"
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_tutor_modes():
    """Sample tutor modes data"""
    return [
        {
            "mode": "chit_chat",
            "name": "Chit-chat Free Talking",
            "description": "Casual conversation practice",
            "category": "casual",
            "requires_topic": False,
        },
        {
            "mode": "interview_simulation",
            "name": "One-on-One Interview Simulation",
            "description": "Practice job interviews",
            "category": "professional",
            "requires_topic": True,
        },
    ]


@pytest.fixture
def sample_session_info():
    """Sample session info data"""
    return {
        "session_id": "session_123",
        "mode": "chit_chat",
        "language": "en",
        "topic": None,
        "difficulty": "intermediate",
        "start_time": "2024-01-01T12:00:00",
        "interaction_count": 5,
        "progress_metrics": {"turns": 5, "corrections": 2},
    }


@pytest.fixture
def sample_mode_config():
    """Sample mode configuration"""
    return Mock(
        name="Chit-chat Free Talking",
        description="Casual conversation practice",
        category=Mock(value="casual"),
        requires_topic_input=False,
        correction_approach="gentle",
        focus_areas=["fluency", "vocabulary"],
        success_criteria=["natural_flow", "engagement"],
        example_interactions=[
            "Hello, how are you?",
            "What did you do today?",
            "Tell me about your hobbies",
        ],
    )


@pytest.fixture
def sample_tutor_response():
    """Sample tutor response data"""
    return {
        "response": "That's great! Tell me more about it.",
        "mode": "chit_chat",
        "correction_approach": "gentle",
        "session_progress": {"turns": 6, "corrections": 2},
    }


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================


class TestPydanticModels:
    """Test Pydantic model validation and instantiation"""

    def test_start_tutor_session_request_valid(self):
        """Test StartTutorSessionRequest with valid data"""
        request = StartTutorSessionRequest(
            mode="chit_chat", language="en", difficulty="intermediate"
        )
        assert request.mode == "chit_chat"
        assert request.language == "en"
        assert request.difficulty == "intermediate"
        assert request.topic is None

    def test_start_tutor_session_request_with_topic(self):
        """Test StartTutorSessionRequest with topic"""
        request = StartTutorSessionRequest(
            mode="interview_simulation",
            language="en",
            difficulty="advanced",
            topic="software engineering",
        )
        assert request.topic == "software engineering"

    def test_tutor_session_response_creation(self):
        """Test TutorSessionResponse model"""
        response = TutorSessionResponse(
            session_id="session_123",
            mode="chit_chat",
            language="en",
            topic=None,
            difficulty="intermediate",
            status="active",
            conversation_starter="Hello! How are you today?",
            message="Session started successfully",
        )
        assert response.session_id == "session_123"
        assert response.conversation_starter == "Hello! How are you today?"

    def test_tutor_conversation_request_minimal(self):
        """Test TutorConversationRequest with minimal data"""
        request = TutorConversationRequest(session_id="session_123", message="Hello!")
        assert request.session_id == "session_123"
        assert request.message == "Hello!"
        assert request.context_messages is None

    def test_tutor_conversation_request_with_context(self):
        """Test TutorConversationRequest with context messages"""
        context = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        request = TutorConversationRequest(
            session_id="session_123", message="How are you?", context_messages=context
        )
        assert request.context_messages == context

    def test_tutor_conversation_response_creation(self):
        """Test TutorConversationResponse model"""
        response = TutorConversationResponse(
            response="I'm doing well, thank you!",
            mode="chit_chat",
            correction_approach="gentle",
            session_progress={"turns": 3},
            suggestions=["Try using more complex sentences"],
        )
        assert response.response == "I'm doing well, thank you!"
        assert response.suggestions == ["Try using more complex sentences"]

    def test_tutor_mode_info_creation(self):
        """Test TutorModeInfo model"""
        info = TutorModeInfo(
            mode="chit_chat",
            name="Chit-chat",
            description="Casual talk",
            category="casual",
            requires_topic=False,
        )
        assert info.mode == "chit_chat"
        assert info.requires_topic is False

    def test_session_info_creation(self):
        """Test SessionInfo model"""
        info = SessionInfo(
            session_id="session_123",
            mode="chit_chat",
            language="en",
            topic=None,
            difficulty="intermediate",
            start_time="2024-01-01T12:00:00",
            interaction_count=5,
            progress_metrics={"turns": 5},
        )
        assert info.session_id == "session_123"
        assert info.interaction_count == 5


# ============================================================================
# GET /available - Get Available Modes Tests
# ============================================================================


class TestGetAvailableModes:
    """Test GET /available endpoint"""

    @pytest.mark.asyncio
    async def test_get_available_modes_success(self, mock_user, sample_tutor_modes):
        """Test successful retrieval of available modes"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_available_modes"
        ) as mock_get_modes:
            mock_get_modes.return_value = sample_tutor_modes

            result = await get_available_modes(current_user=mock_user)

            assert len(result) == 2
            assert result[0].mode == "chit_chat"
            assert result[1].mode == "interview_simulation"
            mock_get_modes.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_modes_empty_list(self, mock_user):
        """Test when no modes are available"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_available_modes"
        ) as mock_get_modes:
            mock_get_modes.return_value = []

            result = await get_available_modes(current_user=mock_user)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_available_modes_exception(self, mock_user):
        """Test exception handling in get_available_modes"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_available_modes"
        ) as mock_get_modes:
            mock_get_modes.side_effect = Exception("Database error")

            with pytest.raises(HTTPException) as exc_info:
                await get_available_modes(current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve available modes" in exc_info.value.detail


# ============================================================================
# POST /session/start - Start Tutor Session Tests
# ============================================================================


class TestStartTutorSession:
    """Test POST /session/start endpoint"""

    @pytest.mark.asyncio
    async def test_start_session_success(self, mock_user):
        """Test successful session start"""
        request = StartTutorSessionRequest(
            mode="chit_chat", language="en", difficulty="intermediate"
        )

        with (
            patch(
                "app.api.tutor_modes.tutor_mode_manager.start_tutor_session"
            ) as mock_start,
            patch(
                "app.api.tutor_modes.tutor_mode_manager.get_conversation_starter"
            ) as mock_starter,
        ):
            mock_start.return_value = "session_123"
            mock_starter.return_value = "Hello! How are you today?"

            result = await start_tutor_session(request=request, current_user=mock_user)

            assert result.session_id == "session_123"
            assert result.mode == "chit_chat"
            assert result.status == "active"
            assert result.conversation_starter == "Hello! How are you today?"
            mock_start.assert_called_once_with(
                user_id=str(mock_user.id),
                mode=TutorMode.CHIT_CHAT,
                language="en",
                difficulty=DifficultyLevel.INTERMEDIATE,
                topic=None,
            )

    @pytest.mark.asyncio
    async def test_start_session_with_topic(self, mock_user):
        """Test session start with topic"""
        request = StartTutorSessionRequest(
            mode="interview_simulation",
            language="es",
            difficulty="advanced",
            topic="software engineering",
        )

        with (
            patch(
                "app.api.tutor_modes.tutor_mode_manager.start_tutor_session"
            ) as mock_start,
            patch(
                "app.api.tutor_modes.tutor_mode_manager.get_conversation_starter"
            ) as mock_starter,
        ):
            mock_start.return_value = "session_456"
            mock_starter.return_value = "Let's begin the interview."

            result = await start_tutor_session(request=request, current_user=mock_user)

            assert result.session_id == "session_456"
            assert result.topic == "software engineering"
            assert result.language == "es"
            assert result.difficulty == "advanced"

    @pytest.mark.asyncio
    async def test_start_session_invalid_mode(self, mock_user):
        """Test session start with invalid mode"""
        request = StartTutorSessionRequest(
            mode="invalid_mode", language="en", difficulty="intermediate"
        )

        # The ValueError is caught and re-raised as HTTPException with 500
        with pytest.raises(HTTPException) as exc_info:
            await start_tutor_session(request=request, current_user=mock_user)

        # The actual code raises HTTPException 500 when ValueError occurs
        assert exc_info.value.status_code == 500
        assert "Failed to start tutor session" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_session_invalid_difficulty(self, mock_user):
        """Test session start with invalid difficulty"""
        request = StartTutorSessionRequest(
            mode="chit_chat", language="en", difficulty="super_hard"
        )

        # The ValueError is caught and re-raised as HTTPException with 500
        with pytest.raises(HTTPException) as exc_info:
            await start_tutor_session(request=request, current_user=mock_user)

        assert exc_info.value.status_code == 500
        assert "Failed to start tutor session" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_session_value_error(self, mock_user):
        """Test session start with ValueError from manager"""
        request = StartTutorSessionRequest(
            mode="chit_chat", language="en", difficulty="intermediate"
        )

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.start_tutor_session"
        ) as mock_start:
            mock_start.side_effect = ValueError("Topic required for this mode")

            with pytest.raises(HTTPException) as exc_info:
                await start_tutor_session(request=request, current_user=mock_user)

            assert exc_info.value.status_code == 400
            assert "Topic required for this mode" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_session_general_exception(self, mock_user):
        """Test session start with general exception"""
        request = StartTutorSessionRequest(
            mode="chit_chat", language="en", difficulty="intermediate"
        )

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.start_tutor_session"
        ) as mock_start:
            mock_start.side_effect = Exception("Database connection failed")

            with pytest.raises(HTTPException) as exc_info:
                await start_tutor_session(request=request, current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to start tutor session" in exc_info.value.detail


# ============================================================================
# POST /conversation - Tutor Conversation Tests
# ============================================================================


class TestTutorConversation:
    """Test POST /conversation endpoint"""

    @pytest.mark.asyncio
    async def test_conversation_success(self, mock_user, sample_tutor_response):
        """Test successful conversation interaction"""
        request = TutorConversationRequest(
            session_id="session_123", message="Hello, how are you?"
        )

        with (
            patch(
                "app.api.tutor_modes.tutor_mode_manager.get_session_info"
            ) as mock_get_session,
            patch(
                "app.api.tutor_modes.tutor_mode_manager.generate_tutor_response"
            ) as mock_generate,
        ):
            mock_get_session.return_value = {"session_id": "session_123"}
            mock_generate.return_value = sample_tutor_response

            result = await tutor_conversation(request=request, current_user=mock_user)

            assert result.response == "That's great! Tell me more about it."
            assert result.mode == "chit_chat"
            assert result.correction_approach == "gentle"
            mock_generate.assert_called_once_with(
                session_id="session_123",
                user_message="Hello, how are you?",
                context_messages=[],
            )

    @pytest.mark.asyncio
    async def test_conversation_with_context(self, mock_user, sample_tutor_response):
        """Test conversation with context messages"""
        context = [{"role": "user", "content": "Hi"}]
        request = TutorConversationRequest(
            session_id="session_123", message="How are you?", context_messages=context
        )

        with (
            patch(
                "app.api.tutor_modes.tutor_mode_manager.get_session_info"
            ) as mock_get_session,
            patch(
                "app.api.tutor_modes.tutor_mode_manager.generate_tutor_response"
            ) as mock_generate,
        ):
            mock_get_session.return_value = {"session_id": "session_123"}
            mock_generate.return_value = sample_tutor_response

            result = await tutor_conversation(request=request, current_user=mock_user)

            mock_generate.assert_called_once_with(
                session_id="session_123",
                user_message="How are you?",
                context_messages=context,
            )

    @pytest.mark.asyncio
    async def test_conversation_session_not_found(self, mock_user):
        """Test conversation with non-existent session"""
        request = TutorConversationRequest(session_id="nonexistent", message="Hello")

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await tutor_conversation(request=request, current_user=mock_user)

            assert exc_info.value.status_code == 404
            assert "Tutor session not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_conversation_generation_exception(self, mock_user):
        """Test conversation with generation exception"""
        request = TutorConversationRequest(session_id="session_123", message="Hello")

        with (
            patch(
                "app.api.tutor_modes.tutor_mode_manager.get_session_info"
            ) as mock_get_session,
            patch(
                "app.api.tutor_modes.tutor_mode_manager.generate_tutor_response"
            ) as mock_generate,
        ):
            mock_get_session.return_value = {"session_id": "session_123"}
            mock_generate.side_effect = Exception("AI service unavailable")

            with pytest.raises(HTTPException) as exc_info:
                await tutor_conversation(request=request, current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to generate tutor response" in exc_info.value.detail


# ============================================================================
# GET /session/{session_id} - Get Session Info Tests
# ============================================================================


class TestGetSessionInfo:
    """Test GET /session/{session_id} endpoint"""

    @pytest.mark.asyncio
    async def test_get_session_info_success(self, mock_user, sample_session_info):
        """Test successful session info retrieval"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.return_value = sample_session_info

            result = await get_session_info(
                session_id="session_123", current_user=mock_user
            )

            assert result.session_id == "session_123"
            assert result.mode == "chit_chat"
            assert result.interaction_count == 5
            mock_get_session.assert_called_once_with("session_123")

    @pytest.mark.asyncio
    async def test_get_session_info_not_found(self, mock_user):
        """Test session info with non-existent session"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_session_info(session_id="nonexistent", current_user=mock_user)

            assert exc_info.value.status_code == 404
            assert "Tutor session not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_session_info_exception(self, mock_user):
        """Test session info with exception"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.side_effect = Exception("Database error")

            with pytest.raises(HTTPException) as exc_info:
                await get_session_info(session_id="session_123", current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve session information" in exc_info.value.detail


# ============================================================================
# POST /session/{session_id}/end - End Session Tests
# ============================================================================


class TestEndTutorSession:
    """Test POST /session/{session_id}/end endpoint"""

    @pytest.mark.asyncio
    async def test_end_session_success(self, mock_user):
        """Test successful session end"""
        summary = {
            "session_id": "session_123",
            "duration_minutes": 15,
            "total_interactions": 10,
        }

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.end_tutor_session"
        ) as mock_end:
            mock_end.return_value = summary

            result = await end_tutor_session(
                session_id="session_123", current_user=mock_user
            )

            assert result["success"] is True
            assert result["message"] == "Tutor session ended successfully"
            assert result["summary"] == summary
            mock_end.assert_called_once_with("session_123")

    @pytest.mark.asyncio
    async def test_end_session_not_found(self, mock_user):
        """Test ending non-existent session"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.end_tutor_session"
        ) as mock_end:
            mock_end.side_effect = ValueError("Session not found")

            with pytest.raises(HTTPException) as exc_info:
                await end_tutor_session(
                    session_id="nonexistent", current_user=mock_user
                )

            assert exc_info.value.status_code == 404
            assert "Tutor session not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_end_session_general_exception(self, mock_user):
        """Test end session with general exception"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.end_tutor_session"
        ) as mock_end:
            mock_end.side_effect = Exception("Database error")

            with pytest.raises(HTTPException) as exc_info:
                await end_tutor_session(
                    session_id="session_123", current_user=mock_user
                )

            assert exc_info.value.status_code == 500
            assert "Failed to end tutor session" in exc_info.value.detail


# ============================================================================
# GET /modes/{mode}/details - Get Mode Details Tests
# ============================================================================


class TestGetModeDetails:
    """Test GET /modes/{mode}/details endpoint"""

    @pytest.mark.asyncio
    async def test_get_mode_details_success(self, mock_user, sample_mode_config):
        """Test successful mode details retrieval"""
        with patch("app.api.tutor_modes.tutor_mode_manager.modes") as mock_modes:
            mock_modes.__getitem__.return_value = sample_mode_config

            result = await get_mode_details(mode="chit_chat", current_user=mock_user)

            assert result["mode"] == "chit_chat"
            # Access the mock's attributes properly
            assert result["name"] == sample_mode_config.name
            assert result["category"] == sample_mode_config.category.value
            assert result["requires_topic"] == sample_mode_config.requires_topic_input
            assert "difficulty_levels" in result
            assert len(result["example_interactions"]) == 2  # Limited to 2

    @pytest.mark.asyncio
    async def test_get_mode_details_invalid_mode(self, mock_user):
        """Test mode details with invalid mode"""
        with pytest.raises(HTTPException) as exc_info:
            await get_mode_details(mode="invalid_mode", current_user=mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid tutor mode" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_mode_details_exception(self, mock_user):
        """Test mode details with exception"""
        with patch("app.api.tutor_modes.tutor_mode_manager.modes") as mock_modes:
            mock_modes.__getitem__.side_effect = Exception("Configuration error")

            with pytest.raises(HTTPException) as exc_info:
                await get_mode_details(mode="chit_chat", current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve mode details" in exc_info.value.detail


# ============================================================================
# GET /analytics - Get Tutor Analytics Tests
# ============================================================================


class TestGetTutorAnalytics:
    """Test GET /analytics endpoint"""

    @pytest.mark.asyncio
    async def test_get_analytics_success(self, mock_user):
        """Test successful analytics retrieval"""
        analytics_data = {
            "total_sessions": 100,
            "active_sessions": 5,
            "most_popular_mode": "chit_chat",
        }

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_mode_analytics"
        ) as mock_analytics:
            mock_analytics.return_value = analytics_data

            result = await get_tutor_analytics(current_user=mock_user)

            assert result["success"] is True
            assert result["analytics"] == analytics_data
            assert "timestamp" in result
            mock_analytics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_analytics_empty(self, mock_user):
        """Test analytics with empty data"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_mode_analytics"
        ) as mock_analytics:
            mock_analytics.return_value = {}

            result = await get_tutor_analytics(current_user=mock_user)

            assert result["success"] is True
            assert result["analytics"] == {}

    @pytest.mark.asyncio
    async def test_get_analytics_exception(self, mock_user):
        """Test analytics with exception"""
        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_mode_analytics"
        ) as mock_analytics:
            mock_analytics.side_effect = Exception("Analytics service error")

            with pytest.raises(HTTPException) as exc_info:
                await get_tutor_analytics(current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve analytics" in exc_info.value.detail


# ============================================================================
# POST /session/{session_id}/feedback - Submit Feedback Tests
# ============================================================================


class TestSubmitSessionFeedback:
    """Test POST /session/{session_id}/feedback endpoint"""

    @pytest.mark.asyncio
    async def test_submit_feedback_active_session(self, mock_user):
        """Test feedback submission for active session"""
        feedback = {"rating": 5, "comment": "Great session!"}

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.return_value = {"session_id": "session_123"}

            result = await submit_session_feedback(
                session_id="session_123", feedback=feedback, current_user=mock_user
            )

            assert result["success"] is True
            assert result["message"] == "Feedback submitted successfully"
            assert result["feedback_id"] == "session_123_feedback"

    @pytest.mark.asyncio
    async def test_submit_feedback_ended_session(self, mock_user):
        """Test feedback submission for ended session (warning logged)"""
        feedback = {"rating": 4, "comment": "Good session"}

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.return_value = None  # Session ended

            result = await submit_session_feedback(
                session_id="session_123", feedback=feedback, current_user=mock_user
            )

            # Should still accept feedback
            assert result["success"] is True
            assert result["message"] == "Feedback submitted successfully"

    @pytest.mark.asyncio
    async def test_submit_feedback_complex_data(self, mock_user):
        """Test feedback with complex data structure"""
        feedback = {
            "rating": 5,
            "aspects": {"clarity": 5, "helpfulness": 4, "engagement": 5},
            "suggestions": ["More examples", "Slower pace"],
        }

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.return_value = {"session_id": "session_123"}

            result = await submit_session_feedback(
                session_id="session_123", feedback=feedback, current_user=mock_user
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_submit_feedback_exception(self, mock_user):
        """Test feedback submission with exception"""
        feedback = {"rating": 5}

        with patch(
            "app.api.tutor_modes.tutor_mode_manager.get_session_info"
        ) as mock_get_session:
            mock_get_session.side_effect = Exception("Database error")

            with pytest.raises(HTTPException) as exc_info:
                await submit_session_feedback(
                    session_id="session_123", feedback=feedback, current_user=mock_user
                )

            assert exc_info.value.status_code == 500
            assert "Failed to submit feedback" in exc_info.value.detail


# ============================================================================
# GET /categories - Get Mode Categories Tests
# ============================================================================


class TestGetModeCategories:
    """Test GET /categories endpoint"""

    @pytest.mark.asyncio
    async def test_get_categories_success(self):
        """Test successful categories retrieval"""
        result = await get_mode_categories()

        assert result["success"] is True
        assert "categories" in result
        assert "casual" in result["categories"]
        assert "professional" in result["categories"]
        assert "educational" in result["categories"]

        # Verify category structure
        casual = result["categories"]["casual"]
        assert casual["name"] == "Casual Practice"
        assert "chit_chat" in casual["modes"]
        assert "open_session" in casual["modes"]

        professional = result["categories"]["professional"]
        assert "interview_simulation" in professional["modes"]
        assert "deadline_negotiations" in professional["modes"]

        educational = result["categories"]["educational"]
        assert "teacher_mode" in educational["modes"]
        assert "vocabulary_builder" in educational["modes"]

    @pytest.mark.asyncio
    async def test_get_categories_structure_validation(self):
        """Test categories structure is valid"""
        result = await get_mode_categories()

        # Verify all expected keys exist
        assert result["success"] is True
        categories = result["categories"]

        # Verify each category has required fields
        for category_key in ["casual", "professional", "educational"]:
            assert category_key in categories
            assert "name" in categories[category_key]
            assert "description" in categories[category_key]
            assert "modes" in categories[category_key]
            assert isinstance(categories[category_key]["modes"], list)
            assert len(categories[category_key]["modes"]) > 0


# ============================================================================
# ROUTER TESTS
# ============================================================================


class TestRouter:
    """Test router configuration"""

    def test_router_prefix(self):
        """Test router has correct prefix"""
        assert router.prefix == "/api/tutor-modes"

    def test_router_tags(self):
        """Test router has correct tags"""
        assert "tutor-modes" in router.tags


# ============================================================================
# EDGE CASES AND ERROR CONDITIONS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_all_difficulty_levels_valid(self, mock_user):
        """Test all DifficultyLevel enum values are accepted"""
        for difficulty in ["beginner", "intermediate", "advanced"]:
            request = StartTutorSessionRequest(
                mode="chit_chat", language="en", difficulty=difficulty
            )

            with (
                patch(
                    "app.api.tutor_modes.tutor_mode_manager.start_tutor_session"
                ) as mock_start,
                patch(
                    "app.api.tutor_modes.tutor_mode_manager.get_conversation_starter"
                ) as mock_starter,
            ):
                mock_start.return_value = f"session_{difficulty}"
                mock_starter.return_value = "Hello!"

                result = await start_tutor_session(
                    request=request, current_user=mock_user
                )
                assert result.difficulty == difficulty

    @pytest.mark.asyncio
    async def test_all_tutor_modes_valid(self, mock_user):
        """Test all TutorMode enum values are accepted"""
        modes = [
            "chit_chat",
            "interview_simulation",
            "deadline_negotiations",
            "teacher_mode",
            "vocabulary_builder",
            "open_session",
        ]

        for mode in modes:
            request = StartTutorSessionRequest(
                mode=mode, language="en", difficulty="intermediate"
            )

            with (
                patch(
                    "app.api.tutor_modes.tutor_mode_manager.start_tutor_session"
                ) as mock_start,
                patch(
                    "app.api.tutor_modes.tutor_mode_manager.get_conversation_starter"
                ) as mock_starter,
            ):
                mock_start.return_value = f"session_{mode}"
                mock_starter.return_value = "Hello!"

                result = await start_tutor_session(
                    request=request, current_user=mock_user
                )
                assert result.mode == mode

    @pytest.mark.asyncio
    async def test_conversation_empty_context(self, mock_user, sample_tutor_response):
        """Test conversation with explicitly empty context list"""
        request = TutorConversationRequest(
            session_id="session_123", message="Hello", context_messages=[]
        )

        with (
            patch(
                "app.api.tutor_modes.tutor_mode_manager.get_session_info"
            ) as mock_get_session,
            patch(
                "app.api.tutor_modes.tutor_mode_manager.generate_tutor_response"
            ) as mock_generate,
        ):
            mock_get_session.return_value = {"session_id": "session_123"}
            mock_generate.return_value = sample_tutor_response

            result = await tutor_conversation(request=request, current_user=mock_user)

            # Should pass empty list as is
            mock_generate.assert_called_once_with(
                session_id="session_123", user_message="Hello", context_messages=[]
            )
