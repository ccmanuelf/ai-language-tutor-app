"""
Comprehensive Test Suite for Real-Time Analysis API

This test suite achieves TRUE 100% coverage (statements + branches + zero warnings)
for app/api/realtime_analysis.py module.

Test Coverage:
- Pydantic Models (6 models with validation)
- WebSocketManager class methods
- Helper functions (all branches)
- API endpoints (success + error paths)
- Integration workflows
"""

import base64
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, WebSocket, WebSocketDisconnect

# Import directly from module for coverage measurement
from app.api.realtime_analysis import (
    AnalyticsResponse,
    AnalyzeAudioRequest,
    FeedbackResponse,
    # Pydantic Models
    StartAnalysisRequest,
    StartAnalysisResponse,
    # WebSocketManager
    WebSocketManager,
    _add_specific_feedback_data,
    _convert_feedback_to_responses,
    _create_base_feedback_response,
    # Helper functions
    _decode_audio_data,
    _get_session_data,
    _send_websocket_feedback,
    analyze_audio_segment,
    end_analysis_session,
    get_recent_feedback,
    get_session_analytics,
    health_check,
    # Router
    router,
    # API endpoints
    start_analysis_session,
    websocket_endpoint,
    websocket_manager,
)
from app.models.database import User
from app.services.realtime_analyzer import (
    AnalysisType,
    FeedbackPriority,
    FluencyMetrics,
    GrammarIssue,
    PronunciationAnalysis,
    RealTimeFeedback,
)

# ============================================================================
# SECTION 1: PYDANTIC MODEL TESTS
# ============================================================================


class TestPydanticModels:
    """Test all Pydantic models with validation scenarios"""

    def test_start_analysis_request_minimal(self):
        """Test StartAnalysisRequest with minimal required fields"""
        request = StartAnalysisRequest(language="en")
        assert request.language == "en"
        assert request.analysis_types == ["comprehensive"]
        assert request.user_preferences == {}

    def test_start_analysis_request_full(self):
        """Test StartAnalysisRequest with all fields"""
        request = StartAnalysisRequest(
            language="es",
            analysis_types=["pronunciation", "grammar"],
            user_preferences={"strict": True, "level": "intermediate"},
        )
        assert request.language == "es"
        assert request.analysis_types == ["pronunciation", "grammar"]
        assert request.user_preferences == {"strict": True, "level": "intermediate"}

    def test_start_analysis_response_creation(self):
        """Test StartAnalysisResponse model creation"""
        now = datetime.now()
        response = StartAnalysisResponse(
            session_id="test_session_123",
            user_id="user_456",
            language="fr",
            analysis_types=["fluency"],
            started_at=now,
            status="active",
        )
        assert response.session_id == "test_session_123"
        assert response.user_id == "user_456"
        assert response.language == "fr"
        assert response.analysis_types == ["fluency"]
        assert response.started_at == now
        assert response.status == "active"

    def test_start_analysis_response_default_status(self):
        """Test StartAnalysisResponse default status value"""
        response = StartAnalysisResponse(
            session_id="test_session",
            user_id="user_id",
            language="de",
            analysis_types=["comprehensive"],
            started_at=datetime.now(),
        )
        assert response.status == "active"

    def test_analyze_audio_request_minimal(self):
        """Test AnalyzeAudioRequest with minimal fields"""
        now = datetime.now()
        request = AnalyzeAudioRequest(
            session_id="session_123",
            audio_data="YXVkaW9kYXRh",  # base64 encoded "audiodata"
            text="Hello world",
            confidence=0.95,
        )
        assert request.session_id == "session_123"
        assert request.audio_data == "YXVkaW9kYXRh"
        assert request.text == "Hello world"
        assert request.confidence == 0.95
        assert isinstance(request.timestamp, datetime)

    def test_analyze_audio_request_with_timestamp(self):
        """Test AnalyzeAudioRequest with explicit timestamp"""
        specific_time = datetime(2024, 1, 1, 12, 0, 0)
        request = AnalyzeAudioRequest(
            session_id="session_123",
            audio_data="YXVkaW9kYXRh",
            text="Bonjour",
            confidence=0.87,
            timestamp=specific_time,
        )
        assert request.timestamp == specific_time

    def test_analyze_audio_request_confidence_validation_min(self):
        """Test AnalyzeAudioRequest confidence minimum validation"""
        request = AnalyzeAudioRequest(
            session_id="session_123",
            audio_data="YXVkaW9kYXRh",
            text="Test",
            confidence=0.0,  # Minimum valid value
        )
        assert request.confidence == 0.0

    def test_analyze_audio_request_confidence_validation_max(self):
        """Test AnalyzeAudioRequest confidence maximum validation"""
        request = AnalyzeAudioRequest(
            session_id="session_123",
            audio_data="YXVkaW9kYXRh",
            text="Test",
            confidence=1.0,  # Maximum valid value
        )
        assert request.confidence == 1.0

    def test_feedback_response_minimal(self):
        """Test FeedbackResponse with minimal required fields"""
        now = datetime.now()
        response = FeedbackResponse(
            feedback_id="fb_123",
            timestamp=now,
            analysis_type="pronunciation",
            priority="important",
            message="Good pronunciation",
            correction=None,
            explanation="Keep practicing",
            confidence=0.85,
            actionable=True,
        )
        assert response.feedback_id == "fb_123"
        assert response.timestamp == now
        assert response.analysis_type == "pronunciation"
        assert response.priority == "important"
        assert response.message == "Good pronunciation"
        assert response.correction is None
        assert response.explanation == "Keep practicing"
        assert response.confidence == 0.85
        assert response.actionable is True
        assert response.pronunciation_score is None
        assert response.grammar_errors is None
        assert response.fluency_metrics is None

    def test_feedback_response_with_pronunciation(self):
        """Test FeedbackResponse with pronunciation data"""
        response = FeedbackResponse(
            feedback_id="fb_pron",
            timestamp=datetime.now(),
            analysis_type="pronunciation",
            priority="minor",
            message="Excellent!",
            correction=None,
            explanation="Great work",
            confidence=0.92,
            actionable=False,
            pronunciation_score=88.5,
        )
        assert response.pronunciation_score == 88.5

    def test_feedback_response_with_grammar_errors(self):
        """Test FeedbackResponse with grammar error data"""
        grammar_errors = [
            {
                "error_type": "subject_verb_agreement",
                "correction": "is",
                "explanation": "Subject is singular",
                "confidence": 0.9,
            }
        ]
        response = FeedbackResponse(
            feedback_id="fb_gram",
            timestamp=datetime.now(),
            analysis_type="grammar",
            priority="critical",
            message="Grammar error detected",
            correction="The cat is sleeping",
            explanation="Subject-verb agreement",
            confidence=0.9,
            actionable=True,
            grammar_errors=grammar_errors,
        )
        assert response.grammar_errors == grammar_errors
        assert len(response.grammar_errors) == 1

    def test_feedback_response_with_fluency_metrics(self):
        """Test FeedbackResponse with fluency metrics"""
        fluency_metrics = {
            "speech_rate": 145.2,
            "confidence_score": 0.78,
            "hesitation_count": 3,
        }
        response = FeedbackResponse(
            feedback_id="fb_flu",
            timestamp=datetime.now(),
            analysis_type="fluency",
            priority="suggestion",
            message="Good fluency",
            correction=None,
            explanation="Consider reducing filler words",
            confidence=0.82,
            actionable=True,
            fluency_metrics=fluency_metrics,
        )
        assert response.fluency_metrics == fluency_metrics
        assert response.fluency_metrics["speech_rate"] == 145.2

    def test_analytics_response_creation(self):
        """Test AnalyticsResponse model creation"""
        session_info = {"session_id": "s123", "user_id": "u456"}
        performance_metrics = {"pronunciation": {"average_score": 85.0}}
        feedback_summary = {"total_feedback": 10, "critical_issues": 2}
        improvement_areas = ["pronunciation", "grammar"]

        response = AnalyticsResponse(
            session_info=session_info,
            performance_metrics=performance_metrics,
            feedback_summary=feedback_summary,
            improvement_areas=improvement_areas,
            overall_score=82.5,
        )
        assert response.session_info == session_info
        assert response.performance_metrics == performance_metrics
        assert response.feedback_summary == feedback_summary
        assert response.improvement_areas == improvement_areas
        assert response.overall_score == 82.5


# ============================================================================
# SECTION 2: WEBSOCKET MANAGER TESTS
# ============================================================================


class TestWebSocketManager:
    """Test WebSocketManager class methods"""

    @pytest.fixture
    def manager(self):
        """Create fresh WebSocketManager instance"""
        return WebSocketManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_new_session(self, manager, mock_websocket):
        """Test connecting WebSocket for new session"""
        connection_id = await manager.connect(mock_websocket, "session_123", "user_456")

        # Verify connection was accepted
        mock_websocket.accept.assert_called_once()

        # Verify connection stored
        assert connection_id in manager.active_connections
        assert manager.active_connections[connection_id] == mock_websocket

        # Verify session tracking
        assert "session_123" in manager.session_connections
        assert connection_id in manager.session_connections["session_123"]

    @pytest.mark.asyncio
    async def test_connect_existing_session(self, manager, mock_websocket):
        """Test connecting additional WebSocket to existing session"""
        # First connection
        connection_id_1 = await manager.connect(
            mock_websocket, "session_123", "user_456"
        )

        # Second connection to same session
        mock_websocket_2 = AsyncMock(spec=WebSocket)
        mock_websocket_2.accept = AsyncMock()
        connection_id_2 = await manager.connect(
            mock_websocket_2, "session_123", "user_789"
        )

        # Both connections should be tracked
        assert connection_id_1 in manager.active_connections
        assert connection_id_2 in manager.active_connections
        assert len(manager.session_connections["session_123"]) == 2

    def test_disconnect_removes_connection(self, manager, mock_websocket):
        """Test disconnecting removes connection"""
        # Manually add connection
        connection_id = "user_456_session_123_1234567890.0"
        manager.active_connections[connection_id] = mock_websocket
        manager.session_connections["session_123"] = [connection_id]

        # Disconnect
        manager.disconnect(connection_id, "session_123")

        # Verify removal
        assert connection_id not in manager.active_connections
        assert connection_id not in manager.session_connections.get("session_123", [])

    def test_disconnect_removes_session_when_empty(self, manager, mock_websocket):
        """Test disconnecting last connection removes session"""
        connection_id = "user_456_session_123_1234567890.0"
        manager.active_connections[connection_id] = mock_websocket
        manager.session_connections["session_123"] = [connection_id]

        manager.disconnect(connection_id, "session_123")

        # Session should be removed when empty
        assert "session_123" not in manager.session_connections

    def test_disconnect_keeps_other_connections(self, manager):
        """Test disconnecting one connection keeps others"""
        connection_id_1 = "conn_1"
        connection_id_2 = "conn_2"
        mock_ws_1 = AsyncMock(spec=WebSocket)
        mock_ws_2 = AsyncMock(spec=WebSocket)

        manager.active_connections[connection_id_1] = mock_ws_1
        manager.active_connections[connection_id_2] = mock_ws_2
        manager.session_connections["session_123"] = [connection_id_1, connection_id_2]

        manager.disconnect(connection_id_1, "session_123")

        # Second connection should remain
        assert connection_id_2 in manager.active_connections
        assert connection_id_2 in manager.session_connections["session_123"]

    def test_disconnect_nonexistent_connection(self, manager):
        """Test disconnecting non-existent connection doesn't error"""
        # Should not raise exception
        manager.disconnect("nonexistent_id", "session_123")

    @pytest.mark.asyncio
    async def test_send_feedback_success(self, manager, mock_websocket):
        """Test sending feedback to connected WebSocket"""
        connection_id = "conn_123"
        manager.active_connections[connection_id] = mock_websocket
        manager.session_connections["session_123"] = [connection_id]

        feedback_data = {"type": "feedback", "message": "Good work"}

        await manager.send_feedback("session_123", feedback_data)

        mock_websocket.send_json.assert_called_once_with(feedback_data)

    @pytest.mark.asyncio
    async def test_send_feedback_multiple_connections(self, manager):
        """Test sending feedback to multiple connections"""
        mock_ws_1 = AsyncMock(spec=WebSocket)
        mock_ws_2 = AsyncMock(spec=WebSocket)

        manager.active_connections["conn_1"] = mock_ws_1
        manager.active_connections["conn_2"] = mock_ws_2
        manager.session_connections["session_123"] = ["conn_1", "conn_2"]

        feedback_data = {"type": "feedback", "score": 85}

        await manager.send_feedback("session_123", feedback_data)

        # Both connections should receive feedback
        mock_ws_1.send_json.assert_called_once_with(feedback_data)
        mock_ws_2.send_json.assert_called_once_with(feedback_data)

    @pytest.mark.asyncio
    async def test_send_feedback_handles_errors(self, manager):
        """Test sending feedback handles WebSocket errors"""
        mock_ws_failing = AsyncMock(spec=WebSocket)
        mock_ws_failing.send_json = AsyncMock(side_effect=Exception("Connection lost"))

        connection_id = "conn_failing"
        manager.active_connections[connection_id] = mock_ws_failing
        manager.session_connections["session_123"] = [connection_id]

        feedback_data = {"type": "feedback"}

        # Should not raise exception, just log warning
        await manager.send_feedback("session_123", feedback_data)

        # Connection should be cleaned up
        assert connection_id not in manager.active_connections

    @pytest.mark.asyncio
    async def test_send_feedback_no_session(self, manager):
        """Test sending feedback to non-existent session"""
        feedback_data = {"type": "feedback"}

        # Should not raise exception
        await manager.send_feedback("nonexistent_session", feedback_data)

    @pytest.mark.asyncio
    async def test_send_feedback_connection_not_in_active(self, manager):
        """Test sending feedback when connection_id is in session but not in active_connections"""
        # Setup: connection_id in session_connections but NOT in active_connections
        manager.session_connections["session_123"] = ["orphaned_conn"]
        # Don't add to active_connections

        feedback_data = {"type": "feedback"}

        # Should not raise exception, just skip the orphaned connection
        await manager.send_feedback("session_123", feedback_data)


# ============================================================================
# SECTION 3: HELPER FUNCTION TESTS
# ============================================================================


class TestHelperFunctions:
    """Test all helper functions with all branches"""

    def test_decode_audio_data_success(self):
        """Test successful base64 audio decoding"""
        audio_data = base64.b64encode(b"test audio data").decode()
        result = _decode_audio_data(audio_data)
        assert result == b"test audio data"

    def test_decode_audio_data_invalid_base64(self):
        """Test decoding invalid base64 raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            _decode_audio_data("invalid!!!base64")

        assert exc_info.value.status_code == 400
        assert "Invalid audio data" in str(exc_info.value.detail)

    @patch("app.api.realtime_analysis.realtime_analyzer")
    def test_get_session_data_success(self, mock_analyzer):
        """Test getting session data for existing session"""
        mock_session = Mock()
        mock_session.language = "en"
        mock_analyzer.active_sessions = {"session_123": mock_session}

        result = _get_session_data("session_123")

        assert result == mock_session
        assert result.language == "en"

    @patch("app.api.realtime_analysis.realtime_analyzer")
    def test_get_session_data_not_found(self, mock_analyzer):
        """Test getting session data for non-existent session"""
        mock_analyzer.active_sessions = {}

        with pytest.raises(HTTPException) as exc_info:
            _get_session_data("nonexistent_session")

        assert exc_info.value.status_code == 404
        assert "Analysis session not found" in exc_info.value.detail

    def test_create_base_feedback_response(self):
        """Test creating base feedback response object"""
        mock_feedback = Mock()
        mock_feedback.feedback_id = "fb_123"
        mock_feedback.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        mock_feedback.analysis_type = AnalysisType.PRONUNCIATION
        mock_feedback.priority = FeedbackPriority.IMPORTANT
        mock_feedback.message = "Test message"
        mock_feedback.correction = "Test correction"
        mock_feedback.explanation = "Test explanation"
        mock_feedback.confidence = 0.85
        mock_feedback.actionable = True

        result = _create_base_feedback_response(mock_feedback)

        assert isinstance(result, FeedbackResponse)
        assert result.feedback_id == "fb_123"
        assert result.timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert result.analysis_type == "pronunciation"
        assert result.priority == "important"
        assert result.message == "Test message"
        assert result.correction == "Test correction"
        assert result.explanation == "Test explanation"
        assert result.confidence == 0.85
        assert result.actionable is True

    def test_add_specific_feedback_data_with_pronunciation(self):
        """Test adding pronunciation data to feedback response"""
        feedback_response = FeedbackResponse(
            feedback_id="fb_123",
            timestamp=datetime.now(),
            analysis_type="pronunciation",
            priority="minor",
            message="Test",
            correction=None,
            explanation="Test",
            confidence=0.8,
            actionable=True,
        )

        mock_feedback = Mock()
        mock_feedback.pronunciation_data = Mock()
        mock_feedback.pronunciation_data.score = 92.5
        mock_feedback.grammar_data = None
        mock_feedback.fluency_data = None

        _add_specific_feedback_data(feedback_response, mock_feedback)

        assert feedback_response.pronunciation_score == 92.5

    def test_add_specific_feedback_data_with_grammar(self):
        """Test adding grammar data to feedback response"""
        feedback_response = FeedbackResponse(
            feedback_id="fb_123",
            timestamp=datetime.now(),
            analysis_type="grammar",
            priority="critical",
            message="Test",
            correction=None,
            explanation="Test",
            confidence=0.8,
            actionable=True,
        )

        mock_feedback = Mock()
        mock_feedback.pronunciation_data = None
        mock_feedback.grammar_data = Mock()
        mock_feedback.grammar_data.error_type = "subject_verb"
        mock_feedback.grammar_data.correction = "are"
        mock_feedback.grammar_data.explanation = "Plural subject"
        mock_feedback.grammar_data.confidence = 0.9
        mock_feedback.fluency_data = None

        _add_specific_feedback_data(feedback_response, mock_feedback)

        assert feedback_response.grammar_errors == [
            {
                "error_type": "subject_verb",
                "correction": "are",
                "explanation": "Plural subject",
                "confidence": 0.9,
            }
        ]

    def test_add_specific_feedback_data_with_fluency(self):
        """Test adding fluency data to feedback response"""
        feedback_response = FeedbackResponse(
            feedback_id="fb_123",
            timestamp=datetime.now(),
            analysis_type="fluency",
            priority="suggestion",
            message="Test",
            correction=None,
            explanation="Test",
            confidence=0.8,
            actionable=True,
        )

        mock_feedback = Mock()
        mock_feedback.pronunciation_data = None
        mock_feedback.grammar_data = None
        mock_feedback.fluency_data = Mock()
        mock_feedback.fluency_data.speech_rate = 150.5
        mock_feedback.fluency_data.confidence_score = 0.82
        mock_feedback.fluency_data.hesitation_count = 3

        _add_specific_feedback_data(feedback_response, mock_feedback)

        assert feedback_response.fluency_metrics == {
            "speech_rate": 150.5,
            "confidence_score": 0.82,
            "hesitation_count": 3,
        }

    def test_add_specific_feedback_data_no_data(self):
        """Test adding feedback data when no specific data exists"""
        feedback_response = FeedbackResponse(
            feedback_id="fb_123",
            timestamp=datetime.now(),
            analysis_type="comprehensive",
            priority="minor",
            message="Test",
            correction=None,
            explanation="Test",
            confidence=0.8,
            actionable=True,
        )

        mock_feedback = Mock()
        mock_feedback.pronunciation_data = None
        mock_feedback.grammar_data = None
        mock_feedback.fluency_data = None

        _add_specific_feedback_data(feedback_response, mock_feedback)

        # Should not crash, fields remain None
        assert feedback_response.pronunciation_score is None
        assert feedback_response.grammar_errors is None
        assert feedback_response.fluency_metrics is None

    def test_convert_feedback_to_responses_empty_list(self):
        """Test converting empty feedback list"""
        result = _convert_feedback_to_responses([])
        assert result == []

    def test_convert_feedback_to_responses_single_item(self):
        """Test converting single feedback item"""
        mock_feedback = Mock()
        mock_feedback.feedback_id = "fb_1"
        mock_feedback.timestamp = datetime.now()
        mock_feedback.analysis_type = AnalysisType.GRAMMAR
        mock_feedback.priority = FeedbackPriority.CRITICAL
        mock_feedback.message = "Error"
        mock_feedback.correction = "Fixed"
        mock_feedback.explanation = "Explanation"
        mock_feedback.confidence = 0.9
        mock_feedback.actionable = True
        mock_feedback.pronunciation_data = None
        mock_feedback.grammar_data = None
        mock_feedback.fluency_data = None

        result = _convert_feedback_to_responses([mock_feedback])

        assert len(result) == 1
        assert isinstance(result[0], FeedbackResponse)
        assert result[0].feedback_id == "fb_1"

    def test_convert_feedback_to_responses_multiple_items(self):
        """Test converting multiple feedback items"""
        mock_feedback_1 = Mock()
        mock_feedback_1.feedback_id = "fb_1"
        mock_feedback_1.timestamp = datetime.now()
        mock_feedback_1.analysis_type = AnalysisType.PRONUNCIATION
        mock_feedback_1.priority = FeedbackPriority.MINOR
        mock_feedback_1.message = "Good"
        mock_feedback_1.correction = None
        mock_feedback_1.explanation = "Explanation 1"
        mock_feedback_1.confidence = 0.85
        mock_feedback_1.actionable = False
        mock_feedback_1.pronunciation_data = Mock()
        mock_feedback_1.pronunciation_data.score = 88.0
        mock_feedback_1.grammar_data = None
        mock_feedback_1.fluency_data = None

        mock_feedback_2 = Mock()
        mock_feedback_2.feedback_id = "fb_2"
        mock_feedback_2.timestamp = datetime.now()
        mock_feedback_2.analysis_type = AnalysisType.FLUENCY
        mock_feedback_2.priority = FeedbackPriority.SUGGESTION
        mock_feedback_2.message = "Consider"
        mock_feedback_2.correction = None
        mock_feedback_2.explanation = "Explanation 2"
        mock_feedback_2.confidence = 0.75
        mock_feedback_2.actionable = True
        mock_feedback_2.pronunciation_data = None
        mock_feedback_2.grammar_data = None
        mock_feedback_2.fluency_data = Mock()
        mock_feedback_2.fluency_data.speech_rate = 145.0
        mock_feedback_2.fluency_data.confidence_score = 0.75
        mock_feedback_2.fluency_data.hesitation_count = 2

        result = _convert_feedback_to_responses([mock_feedback_1, mock_feedback_2])

        assert len(result) == 2
        assert result[0].feedback_id == "fb_1"
        assert result[0].pronunciation_score == 88.0
        assert result[1].feedback_id == "fb_2"
        assert result[1].fluency_metrics["speech_rate"] == 145.0

    @pytest.mark.asyncio
    async def test_send_websocket_feedback_with_feedback(self):
        """Test sending feedback via WebSocket when feedback exists"""
        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.send_feedback = AsyncMock()

            feedback_response = FeedbackResponse(
                feedback_id="fb_1",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                analysis_type="pronunciation",
                priority="important",
                message="Test",
                correction=None,
                explanation="Test explanation",
                confidence=0.85,
                actionable=True,
            )

            await _send_websocket_feedback("session_123", [feedback_response])

            # Verify send_feedback was called
            mock_manager.send_feedback.assert_called_once()
            call_args = mock_manager.send_feedback.call_args
            assert call_args[0][0] == "session_123"

            websocket_data = call_args[0][1]
            assert websocket_data["type"] == "realtime_feedback"
            assert websocket_data["session_id"] == "session_123"
            assert len(websocket_data["feedback"]) == 1

    @pytest.mark.asyncio
    async def test_send_websocket_feedback_empty_list(self):
        """Test sending feedback via WebSocket with empty list"""
        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.send_feedback = AsyncMock()

            await _send_websocket_feedback("session_123", [])

            # Should not call send_feedback for empty list
            mock_manager.send_feedback.assert_not_called()


# ============================================================================
# SECTION 4: API ENDPOINT TESTS
# ============================================================================


class TestAPIEndpoints:
    """Test all API endpoints with success and error paths"""

    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        user = Mock(spec=User)
        user.id = 123
        user.username = "test_user"
        return user

    @pytest.mark.asyncio
    async def test_start_analysis_session_success(self, mock_user):
        """Test starting analysis session successfully"""
        with patch("app.api.realtime_analysis.start_realtime_analysis") as mock_start:
            mock_start.return_value = "session_abc123"

            request = StartAnalysisRequest(
                language="en", analysis_types=["pronunciation", "grammar"]
            )

            response = await start_analysis_session(request, mock_user)

            assert isinstance(response, StartAnalysisResponse)
            assert response.session_id == "session_abc123"
            assert response.user_id == "123"
            assert response.language == "en"
            assert response.analysis_types == ["pronunciation", "grammar"]
            assert response.status == "active"

            # Verify service was called with correct parameters
            mock_start.assert_called_once()
            call_args = mock_start.call_args
            assert call_args[1]["user_id"] == "123"
            assert call_args[1]["language"] == "en"

    @pytest.mark.asyncio
    async def test_start_analysis_session_invalid_analysis_type(self, mock_user):
        """Test starting session with invalid analysis type"""
        with patch("app.api.realtime_analysis.start_realtime_analysis") as mock_start:
            request = StartAnalysisRequest(
                language="en", analysis_types=["invalid_type"]
            )

            with pytest.raises(HTTPException) as exc_info:
                await start_analysis_session(request, mock_user)

            assert exc_info.value.status_code == 400
            assert "Invalid analysis type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_analysis_session_service_error(self, mock_user):
        """Test starting session when service raises error"""
        with patch("app.api.realtime_analysis.start_realtime_analysis") as mock_start:
            mock_start.side_effect = Exception("Service unavailable")

            request = StartAnalysisRequest(language="en")

            with pytest.raises(HTTPException) as exc_info:
                await start_analysis_session(request, mock_user)

            assert exc_info.value.status_code == 500
            assert "Service unavailable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_analyze_audio_segment_success(self, mock_user):
        """Test analyzing audio segment successfully"""
        with (
            patch("app.api.realtime_analysis.analyze_speech_realtime") as mock_analyze,
            patch("app.api.realtime_analysis._get_session_data") as mock_get_session,
            patch("app.api.realtime_analysis._send_websocket_feedback") as mock_ws,
        ):
            # Setup mocks
            mock_session = Mock()
            mock_session.language = "en"
            mock_get_session.return_value = mock_session

            mock_feedback = Mock()
            mock_feedback.feedback_id = "fb_1"
            mock_feedback.timestamp = datetime.now()
            mock_feedback.analysis_type = AnalysisType.PRONUNCIATION
            mock_feedback.priority = FeedbackPriority.MINOR
            mock_feedback.message = "Good"
            mock_feedback.correction = None
            mock_feedback.explanation = "Explanation"
            mock_feedback.confidence = 0.85
            mock_feedback.actionable = True
            mock_feedback.pronunciation_data = None
            mock_feedback.grammar_data = None
            mock_feedback.fluency_data = None

            mock_analyze.return_value = [mock_feedback]
            mock_ws.return_value = None

            request = AnalyzeAudioRequest(
                session_id="session_123",
                audio_data=base64.b64encode(b"audio data").decode(),
                text="Hello world",
                confidence=0.95,
            )

            response = await analyze_audio_segment(request, mock_user)

            assert isinstance(response, list)
            assert len(response) == 1
            assert isinstance(response[0], FeedbackResponse)
            assert response[0].feedback_id == "fb_1"

    @pytest.mark.asyncio
    async def test_analyze_audio_segment_invalid_audio(self, mock_user):
        """Test analyzing with invalid audio data"""
        request = AnalyzeAudioRequest(
            session_id="session_123",
            audio_data="invalid!!!base64",
            text="Hello",
            confidence=0.9,
        )

        with pytest.raises(HTTPException) as exc_info:
            await analyze_audio_segment(request, mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid audio data" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_analyze_audio_segment_session_not_found(self, mock_user):
        """Test analyzing with non-existent session"""
        with patch("app.api.realtime_analysis._get_session_data") as mock_get_session:
            mock_get_session.side_effect = HTTPException(
                status_code=404, detail="Session not found"
            )

            request = AnalyzeAudioRequest(
                session_id="nonexistent",
                audio_data=base64.b64encode(b"audio").decode(),
                text="Hello",
                confidence=0.9,
            )

            with pytest.raises(HTTPException) as exc_info:
                await analyze_audio_segment(request, mock_user)

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_analyze_audio_segment_service_error(self, mock_user):
        """Test analyzing when service raises error"""
        with (
            patch("app.api.realtime_analysis._get_session_data") as mock_get_session,
            patch("app.api.realtime_analysis.analyze_speech_realtime") as mock_analyze,
        ):
            mock_session = Mock()
            mock_session.language = "en"
            mock_get_session.return_value = mock_session
            mock_analyze.side_effect = Exception("Analysis failed")

            request = AnalyzeAudioRequest(
                session_id="session_123",
                audio_data=base64.b64encode(b"audio").decode(),
                text="Hello",
                confidence=0.9,
            )

            with pytest.raises(HTTPException) as exc_info:
                await analyze_audio_segment(request, mock_user)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_session_analytics_success(self, mock_user):
        """Test getting session analytics successfully"""
        with patch(
            "app.api.realtime_analysis.get_realtime_analytics"
        ) as mock_get_analytics:
            mock_analytics = {
                "session_info": {
                    "session_id": "session_123",
                    "user_id": "123",
                    "language": "en",
                    "duration": 300.0,
                    "total_words": 100,
                    "total_errors": 5,
                },
                "performance_metrics": {"pronunciation": {"average_score": 85.0}},
                "feedback_summary": {"total_feedback": 10, "critical_issues": 1},
                "improvement_areas": ["pronunciation"],
                "overall_score": 82.5,
            }
            mock_get_analytics.return_value = mock_analytics

            response = await get_session_analytics("session_123", mock_user)

            assert isinstance(response, AnalyticsResponse)
            assert response.session_info["session_id"] == "session_123"
            assert response.overall_score == 82.5

    @pytest.mark.asyncio
    async def test_get_session_analytics_access_denied(self, mock_user):
        """Test getting analytics for session owned by different user"""
        with patch(
            "app.api.realtime_analysis.get_realtime_analytics"
        ) as mock_get_analytics:
            mock_analytics = {
                "session_info": {
                    "user_id": "999",  # Different user
                    "session_id": "session_123",
                },
                "performance_metrics": {},
                "feedback_summary": {},
                "improvement_areas": [],
                "overall_score": 0.0,
            }
            mock_get_analytics.return_value = mock_analytics

            with pytest.raises(HTTPException) as exc_info:
                await get_session_analytics("session_123", mock_user)

            assert exc_info.value.status_code == 403
            assert "Access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_session_analytics_service_error(self, mock_user):
        """Test getting analytics when service raises error"""
        with patch(
            "app.api.realtime_analysis.get_realtime_analytics"
        ) as mock_get_analytics:
            mock_get_analytics.side_effect = Exception("Analytics unavailable")

            with pytest.raises(HTTPException) as exc_info:
                await get_session_analytics("session_123", mock_user)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_end_analysis_session_success(self, mock_user):
        """Test ending analysis session successfully"""
        with (
            patch("app.api.realtime_analysis.end_realtime_session") as mock_end,
            patch(
                "app.api.realtime_analysis.websocket_manager.send_feedback"
            ) as mock_ws,
        ):
            final_analytics = {
                "session_info": {"user_id": "123", "session_id": "session_123"},
                "performance_metrics": {},
                "feedback_summary": {},
                "improvement_areas": [],
                "overall_score": 85.0,
            }
            mock_end.return_value = final_analytics
            mock_ws.return_value = None

            response = await end_analysis_session("session_123", mock_user)

            assert response["status"] == "ended"
            assert response["session_id"] == "session_123"
            assert "final_analytics" in response

    @pytest.mark.asyncio
    async def test_end_analysis_session_access_denied(self, mock_user):
        """Test ending session owned by different user"""
        with patch("app.api.realtime_analysis.end_realtime_session") as mock_end:
            final_analytics = {
                "session_info": {
                    "user_id": "999",  # Different user
                    "session_id": "session_123",
                },
                "performance_metrics": {},
                "feedback_summary": {},
                "improvement_areas": [],
                "overall_score": 0.0,
            }
            mock_end.return_value = final_analytics

            with pytest.raises(HTTPException) as exc_info:
                await end_analysis_session("session_123", mock_user)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_end_analysis_session_service_error(self, mock_user):
        """Test ending session when service raises error"""
        with patch("app.api.realtime_analysis.end_realtime_session") as mock_end:
            mock_end.side_effect = Exception("Failed to end session")

            with pytest.raises(HTTPException) as exc_info:
                await end_analysis_session("session_123", mock_user)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_recent_feedback_success(self, mock_user):
        """Test getting recent feedback successfully"""
        with patch("app.api.realtime_analysis.realtime_analyzer") as mock_analyzer:
            mock_session = Mock()
            mock_session.user_id = "123"
            mock_analyzer.active_sessions = {"session_123": mock_session}

            mock_feedback = Mock()
            mock_feedback.feedback_id = "fb_1"
            mock_feedback.timestamp = datetime.now()
            mock_feedback.analysis_type = AnalysisType.GRAMMAR
            mock_feedback.priority = FeedbackPriority.IMPORTANT
            mock_feedback.message = "Error found"
            mock_feedback.correction = "Corrected"
            mock_feedback.explanation = "Explanation"
            mock_feedback.confidence = 0.9
            mock_feedback.actionable = True

            mock_analyzer.get_live_feedback = AsyncMock(return_value=[mock_feedback])

            response = await get_recent_feedback("session_123", 10, mock_user)

            assert isinstance(response, list)
            assert len(response) == 1
            assert response[0].feedback_id == "fb_1"

    @pytest.mark.asyncio
    async def test_get_recent_feedback_session_not_found(self, mock_user):
        """Test getting feedback for non-existent session"""
        with patch("app.api.realtime_analysis.realtime_analyzer") as mock_analyzer:
            mock_analyzer.active_sessions = {}

            with pytest.raises(HTTPException) as exc_info:
                await get_recent_feedback("nonexistent", 10, mock_user)

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_recent_feedback_access_denied(self, mock_user):
        """Test getting feedback for session owned by different user"""
        with patch("app.api.realtime_analysis.realtime_analyzer") as mock_analyzer:
            mock_session = Mock()
            mock_session.user_id = "999"  # Different user
            mock_analyzer.active_sessions = {"session_123": mock_session}

            with pytest.raises(HTTPException) as exc_info:
                await get_recent_feedback("session_123", 10, mock_user)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_recent_feedback_service_error(self, mock_user):
        """Test getting feedback when service raises error"""
        with patch("app.api.realtime_analysis.realtime_analyzer") as mock_analyzer:
            mock_session = Mock()
            mock_session.user_id = "123"
            mock_analyzer.active_sessions = {"session_123": mock_session}
            mock_analyzer.get_live_feedback = AsyncMock(side_effect=Exception("Failed"))

            with pytest.raises(HTTPException) as exc_info:
                await get_recent_feedback("session_123", 10, mock_user)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_websocket_endpoint_connect_success(self):
        """Test WebSocket connection success"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.receive_json = AsyncMock(side_effect=WebSocketDisconnect())

        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            await websocket_endpoint(mock_websocket, "session_123")

            # Verify connection flow
            mock_manager.connect.assert_called_once_with(
                mock_websocket, "session_123", "user"
            )
            mock_websocket.send_json.assert_called_once()
            mock_manager.disconnect.assert_called_once_with("conn_123", "session_123")

    @pytest.mark.asyncio
    async def test_websocket_endpoint_ping_pong(self):
        """Test WebSocket ping-pong message handling"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        # Return ping message then disconnect
        mock_websocket.receive_json = AsyncMock(
            side_effect=[{"type": "ping"}, WebSocketDisconnect()]
        )

        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            await websocket_endpoint(mock_websocket, "session_123")

            # Verify pong was sent (after initial connection message)
            assert mock_websocket.send_json.call_count == 2
            pong_call = mock_websocket.send_json.call_args_list[1]
            assert pong_call[0][0]["type"] == "pong"

    @pytest.mark.asyncio
    async def test_websocket_endpoint_request_analytics_success(self):
        """Test WebSocket analytics request handling"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        # Request analytics then disconnect
        mock_websocket.receive_json = AsyncMock(
            side_effect=[{"type": "request_analytics"}, WebSocketDisconnect()]
        )

        with (
            patch("app.api.realtime_analysis.websocket_manager") as mock_manager,
            patch("app.api.realtime_analysis.get_realtime_analytics") as mock_analytics,
        ):
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            mock_analytics.return_value = {"overall_score": 85.0}

            await websocket_endpoint(mock_websocket, "session_123")

            # Verify analytics response was sent
            assert mock_websocket.send_json.call_count >= 2
            analytics_call = mock_websocket.send_json.call_args_list[1]
            assert analytics_call[0][0]["type"] == "analytics_update"

    @pytest.mark.asyncio
    async def test_websocket_endpoint_request_analytics_error(self):
        """Test WebSocket analytics request error handling"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        mock_websocket.receive_json = AsyncMock(
            side_effect=[{"type": "request_analytics"}, WebSocketDisconnect()]
        )

        with (
            patch("app.api.realtime_analysis.websocket_manager") as mock_manager,
            patch("app.api.realtime_analysis.get_realtime_analytics") as mock_analytics,
        ):
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            mock_analytics.side_effect = Exception("Analytics failed")

            await websocket_endpoint(mock_websocket, "session_123")

            # Verify error response was sent
            error_sent = any(
                call[0][0].get("type") == "error"
                for call in mock_websocket.send_json.call_args_list
            )
            assert error_sent

    @pytest.mark.asyncio
    async def test_websocket_endpoint_message_error_handling(self):
        """Test WebSocket message processing error handling"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        # Raise exception then disconnect
        mock_websocket.receive_json = AsyncMock(
            side_effect=[Exception("Message processing error"), WebSocketDisconnect()]
        )

        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            await websocket_endpoint(mock_websocket, "session_123")

            # Verify error was sent
            error_sent = any(
                call[0][0].get("type") == "error"
                for call in mock_websocket.send_json.call_args_list
            )
            assert error_sent

    @pytest.mark.asyncio
    async def test_websocket_endpoint_connection_error(self):
        """Test WebSocket connection error handling"""
        mock_websocket = AsyncMock(spec=WebSocket)

        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.connect = AsyncMock(side_effect=Exception("Connection failed"))
            mock_manager.disconnect = Mock()

            # Should not raise exception
            await websocket_endpoint(mock_websocket, "session_123")

            # disconnect should not be called if connect failed
            mock_manager.disconnect.assert_not_called()

    @pytest.mark.asyncio
    async def test_websocket_endpoint_unknown_message_type(self):
        """Test WebSocket handling of unknown message types"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        # Send unknown message type then disconnect
        mock_websocket.receive_json = AsyncMock(
            side_effect=[
                {"type": "unknown_type", "data": "test"},
                WebSocketDisconnect(),
            ]
        )

        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            await websocket_endpoint(mock_websocket, "session_123")

            # Verify connection established and cleanup occurred
            mock_manager.connect.assert_called_once()
            mock_manager.disconnect.assert_called_once_with("conn_123", "session_123")

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        with (
            patch("app.api.realtime_analysis.realtime_analyzer") as mock_analyzer,
            patch("app.api.realtime_analysis.websocket_manager") as mock_ws_manager,
        ):
            mock_analyzer.active_sessions = {"s1": Mock(), "s2": Mock()}
            mock_ws_manager.active_connections = {
                "c1": Mock(),
                "c2": Mock(),
                "c3": Mock(),
            }

            response = await health_check()

            assert response["status"] == "healthy"
            assert response["service"] == "realtime_analysis"
            assert response["active_sessions"] == 2
            assert response["active_websockets"] == 3
            assert "timestamp" in response


# ============================================================================
# SECTION 5: INTEGRATION TESTS
# ============================================================================


class TestIntegrationWorkflows:
    """Test complete workflows integrating multiple components"""

    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        user = Mock(spec=User)
        user.id = 123
        user.username = "test_user"
        return user

    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, mock_user):
        """Test complete workflow: start -> analyze -> get analytics -> end"""
        with (
            patch("app.api.realtime_analysis.start_realtime_analysis") as mock_start,
            patch("app.api.realtime_analysis.analyze_speech_realtime") as mock_analyze,
            patch(
                "app.api.realtime_analysis.get_realtime_analytics"
            ) as mock_get_analytics,
            patch("app.api.realtime_analysis.end_realtime_session") as mock_end,
            patch("app.api.realtime_analysis._get_session_data") as mock_get_session,
            patch("app.api.realtime_analysis._send_websocket_feedback") as mock_ws,
        ):
            # Step 1: Start session
            mock_start.return_value = "session_123"
            start_request = StartAnalysisRequest(language="en")
            start_response = await start_analysis_session(start_request, mock_user)

            assert start_response.session_id == "session_123"

            # Step 2: Analyze audio
            mock_session = Mock()
            mock_session.language = "en"
            mock_get_session.return_value = mock_session

            mock_feedback = Mock()
            mock_feedback.feedback_id = "fb_1"
            mock_feedback.timestamp = datetime.now()
            mock_feedback.analysis_type = AnalysisType.PRONUNCIATION
            mock_feedback.priority = FeedbackPriority.MINOR
            mock_feedback.message = "Good"
            mock_feedback.correction = None
            mock_feedback.explanation = "Keep it up"
            mock_feedback.confidence = 0.85
            mock_feedback.actionable = True
            mock_feedback.pronunciation_data = None
            mock_feedback.grammar_data = None
            mock_feedback.fluency_data = None

            mock_analyze.return_value = [mock_feedback]

            analyze_request = AnalyzeAudioRequest(
                session_id="session_123",
                audio_data=base64.b64encode(b"audio").decode(),
                text="Hello",
                confidence=0.9,
            )
            analyze_response = await analyze_audio_segment(analyze_request, mock_user)

            assert len(analyze_response) == 1

            # Step 3: Get analytics
            mock_analytics = {
                "session_info": {"user_id": "123", "session_id": "session_123"},
                "performance_metrics": {},
                "feedback_summary": {},
                "improvement_areas": [],
                "overall_score": 85.0,
            }
            mock_get_analytics.return_value = mock_analytics

            analytics_response = await get_session_analytics("session_123", mock_user)
            assert analytics_response.overall_score == 85.0

            # Step 4: End session
            mock_end.return_value = mock_analytics
            end_response = await end_analysis_session("session_123", mock_user)

            assert end_response["status"] == "ended"
            assert end_response["session_id"] == "session_123"

    @pytest.mark.asyncio
    async def test_websocket_with_realtime_feedback(self, mock_user):
        """Test WebSocket integration with real-time feedback delivery"""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.receive_json = AsyncMock(side_effect=WebSocketDisconnect())

        with patch("app.api.realtime_analysis.websocket_manager") as mock_manager:
            mock_manager.connect = AsyncMock(return_value="conn_123")
            mock_manager.disconnect = Mock()

            # Test WebSocket connection
            await websocket_endpoint(mock_websocket, "session_123")

            # Verify connection established
            mock_manager.connect.assert_called_once()

            # Verify connection message sent
            assert mock_websocket.send_json.call_count >= 1
            connection_msg = mock_websocket.send_json.call_args_list[0][0][0]
            assert connection_msg["type"] == "connected"

    @pytest.mark.asyncio
    async def test_multiple_analyses_same_session(self, mock_user):
        """Test multiple audio analyses in same session"""
        with (
            patch("app.api.realtime_analysis.analyze_speech_realtime") as mock_analyze,
            patch("app.api.realtime_analysis._get_session_data") as mock_get_session,
            patch("app.api.realtime_analysis._send_websocket_feedback") as mock_ws,
        ):
            mock_session = Mock()
            mock_session.language = "en"
            mock_get_session.return_value = mock_session

            # First analysis
            mock_feedback_1 = Mock()
            mock_feedback_1.feedback_id = "fb_1"
            mock_feedback_1.timestamp = datetime.now()
            mock_feedback_1.analysis_type = AnalysisType.PRONUNCIATION
            mock_feedback_1.priority = FeedbackPriority.MINOR
            mock_feedback_1.message = "First"
            mock_feedback_1.correction = None
            mock_feedback_1.explanation = "Explanation 1"
            mock_feedback_1.confidence = 0.85
            mock_feedback_1.actionable = True
            mock_feedback_1.pronunciation_data = None
            mock_feedback_1.grammar_data = None
            mock_feedback_1.fluency_data = None

            mock_analyze.return_value = [mock_feedback_1]

            request_1 = AnalyzeAudioRequest(
                session_id="session_123",
                audio_data=base64.b64encode(b"audio1").decode(),
                text="Hello",
                confidence=0.9,
            )
            response_1 = await analyze_audio_segment(request_1, mock_user)
            assert len(response_1) == 1

            # Second analysis
            mock_feedback_2 = Mock()
            mock_feedback_2.feedback_id = "fb_2"
            mock_feedback_2.timestamp = datetime.now()
            mock_feedback_2.analysis_type = AnalysisType.GRAMMAR
            mock_feedback_2.priority = FeedbackPriority.IMPORTANT
            mock_feedback_2.message = "Second"
            mock_feedback_2.correction = "Corrected"
            mock_feedback_2.explanation = "Explanation 2"
            mock_feedback_2.confidence = 0.9
            mock_feedback_2.actionable = True
            mock_feedback_2.pronunciation_data = None
            mock_feedback_2.grammar_data = None
            mock_feedback_2.fluency_data = None

            mock_analyze.return_value = [mock_feedback_2]

            request_2 = AnalyzeAudioRequest(
                session_id="session_123",
                audio_data=base64.b64encode(b"audio2").decode(),
                text="World",
                confidence=0.88,
            )
            response_2 = await analyze_audio_segment(request_2, mock_user)
            assert len(response_2) == 1

            # Both analyses should use same session
            assert mock_get_session.call_count == 2
            assert all(
                call[0][0] == "session_123" for call in mock_get_session.call_args_list
            )


# ============================================================================
# SECTION 6: MODULE-LEVEL TESTS
# ============================================================================


class TestModuleLevel:
    """Test module-level components"""

    def test_global_websocket_manager_exists(self):
        """Test global websocket_manager instance exists"""
        assert websocket_manager is not None
        assert isinstance(websocket_manager, WebSocketManager)

    def test_router_configuration(self):
        """Test router is configured correctly"""
        assert router.prefix == "/api/realtime"
        assert "Real-Time Analysis" in router.tags

    def test_router_has_all_endpoints(self):
        """Test router includes all expected endpoints"""
        route_paths = [route.path for route in router.routes]

        # REST endpoints (paths include prefix)
        assert "/api/realtime/start" in route_paths
        assert "/api/realtime/analyze" in route_paths
        assert "/api/realtime/analytics/{session_id}" in route_paths
        assert "/api/realtime/end/{session_id}" in route_paths
        assert "/api/realtime/feedback/{session_id}" in route_paths
        assert "/api/realtime/health" in route_paths

        # WebSocket endpoint
        assert "/api/realtime/ws/{session_id}" in route_paths
