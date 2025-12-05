"""
Comprehensive tests for app/api/progress_analytics.py
Session 86: Achieving TRUE 100% coverage (statements + branches + zero warnings)

Test Coverage:
- Pydantic model validations (7 models)
- Enum classes (3 enums)
- Conversation tracking endpoints (2)
- Multi-skill progress endpoints (3)
- Learning path recommendation endpoints (2)
- Memory retention analytics endpoints (2)
- Enhanced dashboard endpoints (1)
- Admin endpoints (1)
- Utility endpoints (2)

Total: 23 endpoint/function groups to test comprehensively
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Direct imports for coverage measurement (Session 84-85 pattern)
from app.api.progress_analytics import (
    ConfidenceLevelEnum,
    # Pydantic Models
    ConversationTrackingRequest,
    LearningPathGenerationRequest,
    LearningPathTypeEnum,
    MemoryRetentionAnalysisRequest,
    SkillProgressUpdateRequest,
    # Enums
    SkillTypeEnum,
    analyze_memory_retention,
    generate_learning_path,
    get_api_stats,
    get_comprehensive_dashboard,
    get_conversation_analytics,
    get_learning_path_recommendations,
    get_memory_retention_trends,
    get_multi_skill_analytics,
    get_skill_comparison,
    get_system_progress_analytics,
    health_check,
    progress_service,
    # Module-level objects
    router,
    # Endpoints
    track_conversation_session,
    update_skill_progress,
)
from app.models.database import User
from app.services.progress_analytics_service import (
    ConversationMetrics,
    LearningPathRecommendation,
    LearningPathType,
    MemoryRetentionAnalysis,
    SkillProgressMetrics,
)

# ============= TEST FIXTURES =============


@pytest.fixture
def sample_conversation_request() -> ConversationTrackingRequest:
    """Sample conversation tracking request"""
    return ConversationTrackingRequest(
        session_id="test_session_123",
        user_id=1,
        language_code="es",
        conversation_type="scenario",
        scenario_id="restaurant_basic",
        tutor_mode=None,
        duration_minutes=15.5,
        total_exchanges=20,
        user_turns=10,
        ai_turns=10,
        words_spoken=150,
        unique_words_used=75,
        vocabulary_complexity_score=0.65,
        grammar_accuracy_score=0.78,
        pronunciation_clarity_score=0.72,
        fluency_score=0.68,
        average_confidence_score=0.75,
        confidence_distribution={"high": 6, "moderate": 3, "low": 1},
        engagement_score=0.82,
        hesitation_count=3,
        self_correction_count=2,
        new_vocabulary_encountered=12,
        grammar_patterns_practiced=5,
        cultural_context_learned=2,
        learning_objectives_met=["order food", "ask questions"],
        improvement_from_last_session=0.05,
        peer_comparison_percentile=65.0,
        started_at=datetime.now(),
        ended_at=datetime.now() + timedelta(minutes=15),
    )


@pytest.fixture
def sample_skill_update_request() -> SkillProgressUpdateRequest:
    """Sample skill progress update request"""
    return SkillProgressUpdateRequest(
        user_id=1,
        language_code="es",
        skill_type=SkillTypeEnum.VOCABULARY,
        current_level=65.0,
        mastery_percentage=70.0,
        confidence_level=ConfidenceLevelEnum.HIGH,
        initial_assessment_score=45.0,
        latest_assessment_score=65.0,
        total_practice_sessions=25,
        total_practice_time_minutes=750,
        average_session_performance=0.72,
        consistency_score=0.85,
        easy_items_percentage=60.0,
        moderate_items_percentage=30.0,
        hard_items_percentage=10.0,
        challenge_comfort_level=0.65,
        retention_rate=0.78,
        forgetting_curve_analysis={"day_1": 0.95, "day_7": 0.75, "day_30": 0.60},
        optimal_review_intervals={"easy": 7, "moderate": 3, "hard": 1},
        recommended_focus_areas=["idioms", "phrasal_verbs"],
        suggested_exercises=["flashcards", "context_practice"],
        next_milestone_target="Reach 75% mastery",
    )


@pytest.fixture
def sample_learning_path_request() -> LearningPathGenerationRequest:
    """Sample learning path generation request"""
    return LearningPathGenerationRequest(
        user_id=1,
        language_code="es",
        time_commitment_hours_per_week=5.0,
        preferred_session_length_minutes=30,
        difficulty_preference=2,
        primary_goals=["Improve fluency", "Build vocabulary"],
        target_skills=[SkillTypeEnum.SPEAKING, SkillTypeEnum.VOCABULARY],
        learning_style_preferences=["interactive", "visual"],
        preferred_content_types=["conversations", "exercises"],
        target_duration_weeks=12,
        current_proficiency_level="intermediate",
        specific_challenges=["pronunciation", "verb_conjugation"],
    )


@pytest.fixture
def sample_memory_retention_request() -> MemoryRetentionAnalysisRequest:
    """Sample memory retention analysis request"""
    return MemoryRetentionAnalysisRequest(
        user_id=1,
        language_code="es",
        analysis_period_days=30,
        include_item_analysis=True,
        include_timing_optimization=True,
        include_peer_comparison=False,
    )


@pytest.fixture
def mock_admin_user() -> User:
    """Mock admin user for testing"""
    user = MagicMock(spec=User)
    user.id = 999
    user.username = "admin"
    user.role = "admin"
    user.is_guest = False
    return user


# ============= ENUM TESTS =============


class TestEnums:
    """Test enum classes"""

    def test_skill_type_enum_values(self):
        """Test SkillTypeEnum has all expected values"""
        assert SkillTypeEnum.VOCABULARY.value == "vocabulary"
        assert SkillTypeEnum.GRAMMAR.value == "grammar"
        assert SkillTypeEnum.LISTENING.value == "listening"
        assert SkillTypeEnum.SPEAKING.value == "speaking"
        assert SkillTypeEnum.PRONUNCIATION.value == "pronunciation"
        assert SkillTypeEnum.CONVERSATION.value == "conversation"
        assert SkillTypeEnum.COMPREHENSION.value == "comprehension"
        assert SkillTypeEnum.WRITING.value == "writing"

    def test_learning_path_type_enum_values(self):
        """Test LearningPathTypeEnum has all expected values"""
        assert LearningPathTypeEnum.BEGINNER_FOUNDATION.value == "beginner_foundation"
        assert LearningPathTypeEnum.CONVERSATION_FOCUSED.value == "conversation_focused"
        assert LearningPathTypeEnum.VOCABULARY_INTENSIVE.value == "vocabulary_intensive"
        assert LearningPathTypeEnum.GRAMMAR_MASTERY.value == "grammar_mastery"
        assert (
            LearningPathTypeEnum.PRONUNCIATION_PERFECTION.value
            == "pronunciation_perfection"
        )
        assert (
            LearningPathTypeEnum.COMPREHENSIVE_BALANCED.value
            == "comprehensive_balanced"
        )
        assert LearningPathTypeEnum.RAPID_PROGRESS.value == "rapid_progress"
        assert LearningPathTypeEnum.RETENTION_FOCUSED.value == "retention_focused"

    def test_confidence_level_enum_values(self):
        """Test ConfidenceLevelEnum has all expected values"""
        assert ConfidenceLevelEnum.VERY_LOW.value == "very_low"
        assert ConfidenceLevelEnum.LOW.value == "low"
        assert ConfidenceLevelEnum.MODERATE.value == "moderate"
        assert ConfidenceLevelEnum.HIGH.value == "high"
        assert ConfidenceLevelEnum.VERY_HIGH.value == "very_high"


# ============= PYDANTIC MODEL VALIDATION TESTS =============


class TestPydanticModels:
    """Test Pydantic model validations"""

    def test_conversation_tracking_request_valid(self, sample_conversation_request):
        """Test valid conversation tracking request"""
        assert sample_conversation_request.session_id == "test_session_123"
        assert sample_conversation_request.user_id == 1
        assert sample_conversation_request.language_code == "es"
        assert sample_conversation_request.duration_minutes == 15.5

    def test_conversation_tracking_request_minimal(self):
        """Test conversation tracking request with minimal fields"""
        request = ConversationTrackingRequest(
            session_id="minimal_123",
            user_id=1,
            language_code="es",
            conversation_type="free_form",
        )
        assert request.duration_minutes == 0.0
        assert request.total_exchanges == 0
        assert request.confidence_distribution == {}

    def test_conversation_tracking_request_validation_language_code_too_short(
        self,
    ):
        """Test language code validation - too short"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            ConversationTrackingRequest(
                session_id="test",
                user_id=1,
                language_code="e",
                conversation_type="scenario",
            )

    def test_conversation_tracking_request_validation_negative_duration(self):
        """Test duration validation - negative value"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            ConversationTrackingRequest(
                session_id="test",
                user_id=1,
                language_code="es",
                conversation_type="scenario",
                duration_minutes=-5.0,
            )

    def test_conversation_tracking_request_validation_score_out_of_range(self):
        """Test score validation - value > 1.0"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            ConversationTrackingRequest(
                session_id="test",
                user_id=1,
                language_code="es",
                conversation_type="scenario",
                fluency_score=1.5,
            )

    def test_skill_progress_update_request_valid(self, sample_skill_update_request):
        """Test valid skill progress update request"""
        assert sample_skill_update_request.user_id == 1
        assert sample_skill_update_request.skill_type == SkillTypeEnum.VOCABULARY
        assert sample_skill_update_request.current_level == 65.0
        assert sample_skill_update_request.confidence_level == ConfidenceLevelEnum.HIGH

    def test_skill_progress_update_request_minimal(self):
        """Test skill progress update request with minimal fields"""
        request = SkillProgressUpdateRequest(
            user_id=1,
            language_code="es",
            skill_type=SkillTypeEnum.GRAMMAR,
            current_level=50.0,
            mastery_percentage=55.0,
            confidence_level=ConfidenceLevelEnum.MODERATE,
        )
        assert request.total_practice_sessions == 0
        assert request.forgetting_curve_analysis == {}

    def test_skill_progress_update_request_validation_level_out_of_range(self):
        """Test level validation - value > 100"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SkillProgressUpdateRequest(
                user_id=1,
                language_code="es",
                skill_type=SkillTypeEnum.GRAMMAR,
                current_level=150.0,
                mastery_percentage=55.0,
                confidence_level=ConfidenceLevelEnum.MODERATE,
            )

    def test_skill_progress_update_request_field_validator(
        self, sample_skill_update_request
    ):
        """Test difficulty percentage field validator"""
        # Validator should accept valid percentages
        assert sample_skill_update_request.easy_items_percentage == 60.0
        assert sample_skill_update_request.moderate_items_percentage == 30.0
        assert sample_skill_update_request.hard_items_percentage == 10.0

    def test_learning_path_generation_request_valid(self, sample_learning_path_request):
        """Test valid learning path generation request"""
        assert sample_learning_path_request.user_id == 1
        assert sample_learning_path_request.time_commitment_hours_per_week == 5.0
        assert sample_learning_path_request.difficulty_preference == 2
        assert len(sample_learning_path_request.target_skills) == 2

    def test_learning_path_generation_request_defaults(self):
        """Test learning path request with default values"""
        request = LearningPathGenerationRequest(user_id=1, language_code="es")
        assert request.time_commitment_hours_per_week == 5.0
        assert request.preferred_session_length_minutes == 30
        assert request.difficulty_preference == 2
        assert request.target_duration_weeks == 12

    def test_learning_path_generation_request_validation_time_commitment(self):
        """Test time commitment validation - value too low"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            LearningPathGenerationRequest(
                user_id=1, language_code="es", time_commitment_hours_per_week=0.5
            )

    def test_learning_path_generation_request_validation_duration_weeks(self):
        """Test duration weeks validation - value too high"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            LearningPathGenerationRequest(
                user_id=1, language_code="es", target_duration_weeks=100
            )

    def test_memory_retention_analysis_request_valid(
        self, sample_memory_retention_request
    ):
        """Test valid memory retention analysis request"""
        assert sample_memory_retention_request.user_id == 1
        assert sample_memory_retention_request.analysis_period_days == 30
        assert sample_memory_retention_request.include_item_analysis is True

    def test_memory_retention_analysis_request_defaults(self):
        """Test memory retention request with default values"""
        request = MemoryRetentionAnalysisRequest(user_id=1, language_code="es")
        assert request.analysis_period_days == 30
        assert request.include_item_analysis is True
        assert request.include_timing_optimization is True
        assert request.include_peer_comparison is False

    def test_memory_retention_analysis_request_validation_period_days(self):
        """Test period days validation - value too low"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            MemoryRetentionAnalysisRequest(
                user_id=1, language_code="es", analysis_period_days=5
            )


# ============= CONVERSATION TRACKING ENDPOINT TESTS =============


class TestConversationTrackingEndpoints:
    """Test conversation tracking endpoints"""

    @pytest.mark.asyncio
    async def test_track_conversation_session_success(
        self, sample_conversation_request
    ):
        """Test successful conversation session tracking"""
        with patch.object(
            progress_service, "track_conversation_session", return_value=True
        ) as mock_track:
            response = await track_conversation_session(sample_conversation_request)

            assert isinstance(response, JSONResponse)
            content = json.loads(response.body.decode())
            assert content["success"] is True
            assert content["message"] == "Conversation session tracked successfully"
            assert content["data"]["session_id"] == "test_session_123"
            assert response.status_code == 201

            # Verify service was called with correct metrics
            mock_track.assert_called_once()
            call_args = mock_track.call_args[0][0]
            assert isinstance(call_args, ConversationMetrics)
            assert call_args.session_id == "test_session_123"

    @pytest.mark.asyncio
    async def test_track_conversation_session_failure(
        self, sample_conversation_request
    ):
        """Test conversation session tracking failure"""
        with patch.object(
            progress_service, "track_conversation_session", return_value=False
        ):
            with pytest.raises(HTTPException) as exc_info:
                await track_conversation_session(sample_conversation_request)

            assert exc_info.value.status_code == 500
            assert "Failed to track conversation session" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_track_conversation_session_exception(
        self, sample_conversation_request
    ):
        """Test conversation session tracking with exception"""
        with patch.object(
            progress_service,
            "track_conversation_session",
            side_effect=Exception("Database error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await track_conversation_session(sample_conversation_request)

            assert exc_info.value.status_code == 500
            assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_conversation_analytics_success(self):
        """Test successful conversation analytics retrieval"""
        mock_analytics = {
            "overview": {"total_conversations": 10},
            "performance_metrics": {"average_fluency_score": 0.75},
        }

        with patch.object(
            progress_service, "get_conversation_analytics", return_value=mock_analytics
        ) as mock_get:
            response = await get_conversation_analytics(
                user_id=1, language_code="es", period_days=30
            )

            assert isinstance(response, JSONResponse)
            content = json.loads(response.body.decode())
            assert content["success"] is True
            assert content["data"]["overview"]["total_conversations"] == 10
            assert response.status_code == 200

            mock_get.assert_called_once_with(1, "es", 30)

    @pytest.mark.asyncio
    async def test_get_conversation_analytics_exception(self):
        """Test conversation analytics retrieval with exception"""
        with patch.object(
            progress_service,
            "get_conversation_analytics",
            side_effect=Exception("Query error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_conversation_analytics(
                    user_id=1, language_code="es", period_days=30
                )

            assert exc_info.value.status_code == 500
            assert "Query error" in str(exc_info.value.detail)


# ============= MULTI-SKILL PROGRESS ENDPOINT TESTS =============


class TestMultiSkillProgressEndpoints:
    """Test multi-skill progress endpoints"""

    @pytest.mark.asyncio
    async def test_update_skill_progress_success(self, sample_skill_update_request):
        """Test successful skill progress update"""
        with patch.object(
            progress_service, "update_skill_progress", return_value=True
        ) as mock_update:
            response = await update_skill_progress(sample_skill_update_request)

            assert isinstance(response, JSONResponse)
            content = json.loads(response.body.decode())
            assert content["success"] is True
            assert content["message"] == "Skill progress updated successfully"
            assert content["data"]["user_id"] == 1
            assert content["data"]["skill_type"] == "vocabulary"
            assert response.status_code == 200

            # Verify service was called
            mock_update.assert_called_once()
            call_args = mock_update.call_args[0][0]
            assert isinstance(call_args, SkillProgressMetrics)

    @pytest.mark.asyncio
    async def test_update_skill_progress_with_no_initial_assessment(self):
        """Test skill progress update without initial assessment score"""
        request = SkillProgressUpdateRequest(
            user_id=1,
            language_code="es",
            skill_type=SkillTypeEnum.GRAMMAR,
            current_level=60.0,
            mastery_percentage=65.0,
            confidence_level=ConfidenceLevelEnum.MODERATE,
            initial_assessment_score=None,
            latest_assessment_score=None,
        )

        with patch.object(progress_service, "update_skill_progress", return_value=True):
            response = await update_skill_progress(request)

            content = json.loads(response.body.decode())
            assert content["success"] is True

    @pytest.mark.asyncio
    async def test_update_skill_progress_failure(self, sample_skill_update_request):
        """Test skill progress update failure"""
        with patch.object(
            progress_service, "update_skill_progress", return_value=False
        ):
            with pytest.raises(HTTPException) as exc_info:
                await update_skill_progress(sample_skill_update_request)

            assert exc_info.value.status_code == 500
            assert "Failed to update skill progress" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_skill_progress_exception(self, sample_skill_update_request):
        """Test skill progress update with exception"""
        with patch.object(
            progress_service,
            "update_skill_progress",
            side_effect=Exception("Update error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await update_skill_progress(sample_skill_update_request)

            assert exc_info.value.status_code == 500
            assert "Update error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_multi_skill_analytics_success(self):
        """Test successful multi-skill analytics retrieval"""
        mock_analytics = {
            "skill_overview": {"total_skills_tracked": 5},
            "individual_skills": [],
        }

        with patch.object(
            progress_service, "get_multi_skill_analytics", return_value=mock_analytics
        ) as mock_get:
            response = await get_multi_skill_analytics(user_id=1, language_code="es")

            assert isinstance(response, JSONResponse)
            content = json.loads(response.body.decode())
            assert content["success"] is True
            assert content["data"]["skill_overview"]["total_skills_tracked"] == 5
            assert response.status_code == 200

            mock_get.assert_called_once_with(1, "es")

    @pytest.mark.asyncio
    async def test_get_multi_skill_analytics_exception(self):
        """Test multi-skill analytics retrieval with exception"""
        with patch.object(
            progress_service,
            "get_multi_skill_analytics",
            side_effect=Exception("Analytics error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_multi_skill_analytics(user_id=1, language_code="es")

            assert exc_info.value.status_code == 500
            assert "Analytics error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_skill_comparison_success(self):
        """Test successful skill comparison retrieval"""
        response = await get_skill_comparison(
            user_id=1, language_code="es", comparison_period_days=30
        )

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["data"]["user_id"] == 1
        assert content["data"]["language_code"] == "es"
        assert content["data"]["comparison_period_days"] == 30
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_skill_comparison_exception(self):
        """Test skill comparison with exception (simulated)"""
        # This endpoint doesn't raise exceptions in current implementation,
        # but we test the exception handling path
        with patch(
            "app.api.progress_analytics.JSONResponse",
            side_effect=Exception("Response error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await get_skill_comparison(user_id=1, language_code="es")

            assert "Response error" in str(exc_info.value)


# ============= LEARNING PATH RECOMMENDATION ENDPOINT TESTS =============


class TestLearningPathRecommendationEndpoints:
    """Test learning path recommendation endpoints"""

    @pytest.mark.asyncio
    async def test_generate_learning_path_success(self, sample_learning_path_request):
        """Test successful learning path generation"""
        response = await generate_learning_path(sample_learning_path_request)

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["message"] == "Learning path generated successfully"
        assert "recommendation_id" in content["data"]
        assert (
            content["data"]["path_type"]
            == LearningPathType.COMPREHENSIVE_BALANCED.value
        )
        assert content["data"]["duration_weeks"] == 12
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_generate_learning_path_with_minimal_request(self):
        """Test learning path generation with minimal request"""
        request = LearningPathGenerationRequest(user_id=1, language_code="es")

        response = await generate_learning_path(request)

        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["data"]["duration_weeks"] == 12  # default value

    @pytest.mark.asyncio
    async def test_generate_learning_path_exception(self, sample_learning_path_request):
        """Test learning path generation with exception"""
        with patch(
            "app.api.progress_analytics.LearningPathRecommendation",
            side_effect=Exception("Generation error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await generate_learning_path(sample_learning_path_request)

            assert exc_info.value.status_code == 500
            assert "Generation error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_learning_path_recommendations_success(self):
        """Test successful learning path recommendations retrieval"""
        response = await get_learning_path_recommendations(
            user_id=1, language_code="es", active_only=True
        )

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert (
            content["message"] == "Learning path recommendations retrieved successfully"
        )
        assert content["data"]["user_id"] == 1
        assert content["data"]["language_code"] == "es"
        assert content["data"]["count"] == 0
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_learning_path_recommendations_exception(self):
        """Test learning path recommendations retrieval with exception"""
        with patch(
            "app.api.progress_analytics.JSONResponse",
            side_effect=Exception("Query error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await get_learning_path_recommendations(user_id=1, language_code="es")

            assert "Query error" in str(exc_info.value)


# ============= MEMORY RETENTION ANALYTICS ENDPOINT TESTS =============


class TestMemoryRetentionAnalyticsEndpoints:
    """Test memory retention analytics endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_memory_retention_success(
        self, sample_memory_retention_request
    ):
        """Test successful memory retention analysis"""
        response = await analyze_memory_retention(sample_memory_retention_request)

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["message"] == "Memory retention analysis completed successfully"
        assert content["data"]["user_id"] == 1
        assert "retention_rates" in content["data"]
        assert "recall_analysis" in content["data"]
        assert "learning_efficiency" in content["data"]
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_analyze_memory_retention_with_all_options(self):
        """Test memory retention analysis with all options enabled"""
        request = MemoryRetentionAnalysisRequest(
            user_id=1,
            language_code="es",
            analysis_period_days=60,
            include_item_analysis=True,
            include_timing_optimization=True,
            include_peer_comparison=True,
        )

        response = await analyze_memory_retention(request)

        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["data"]["analysis_period_days"] == 60

    @pytest.mark.asyncio
    async def test_analyze_memory_retention_exception(
        self, sample_memory_retention_request
    ):
        """Test memory retention analysis with exception"""
        with patch(
            "app.api.progress_analytics.MemoryRetentionAnalysis",
            side_effect=Exception("Analysis error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_memory_retention(sample_memory_retention_request)

            assert exc_info.value.status_code == 500
            assert "Analysis error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_memory_retention_trends_success(self):
        """Test successful memory retention trends retrieval"""
        response = await get_memory_retention_trends(
            user_id=1, language_code="es", period_days=90
        )

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["message"] == "Memory retention trends retrieved successfully"
        assert content["data"]["user_id"] == 1
        assert content["data"]["period_days"] == 90
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_memory_retention_trends_exception(self):
        """Test memory retention trends retrieval with exception"""
        with patch(
            "app.api.progress_analytics.JSONResponse",
            side_effect=Exception("Trends error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await get_memory_retention_trends(user_id=1, language_code="es")

            assert "Trends error" in str(exc_info.value)


# ============= ENHANCED DASHBOARD ENDPOINT TESTS =============


class TestEnhancedDashboardEndpoints:
    """Test enhanced dashboard endpoints"""

    @pytest.mark.asyncio
    async def test_get_comprehensive_dashboard_success(self):
        """Test successful comprehensive dashboard retrieval"""
        mock_conversation_analytics = {"overview": {"total_conversations": 5}}
        mock_skill_analytics = {"skill_overview": {"total_skills_tracked": 3}}

        with (
            patch.object(
                progress_service,
                "get_conversation_analytics",
                return_value=mock_conversation_analytics,
            ),
            patch.object(
                progress_service,
                "get_multi_skill_analytics",
                return_value=mock_skill_analytics,
            ),
        ):
            response = await get_comprehensive_dashboard(
                user_id=1, language_code="es", period_days=30
            )

            assert isinstance(response, JSONResponse)
            content = json.loads(response.body.decode())
            assert content["success"] is True
            assert (
                content["message"]
                == "Comprehensive dashboard data retrieved successfully"
            )
            assert "conversation_analytics" in content["data"]
            assert "skill_analytics" in content["data"]
            assert "learning_path_status" in content["data"]
            assert "memory_retention_summary" in content["data"]
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_comprehensive_dashboard_exception(self):
        """Test comprehensive dashboard retrieval with exception"""
        with patch.object(
            progress_service,
            "get_conversation_analytics",
            side_effect=Exception("Dashboard error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_comprehensive_dashboard(user_id=1, language_code="es")

            assert exc_info.value.status_code == 500
            assert "Dashboard error" in str(exc_info.value.detail)


# ============= ADMIN ENDPOINT TESTS =============


class TestAdminEndpoints:
    """Test admin endpoints"""

    @pytest.mark.asyncio
    async def test_get_system_progress_analytics_success(self, mock_admin_user):
        """Test successful system progress analytics retrieval"""
        response = await get_system_progress_analytics(
            admin_user=mock_admin_user, period_days=30
        )

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["message"] == "System progress analytics retrieved successfully"
        assert content["data"]["period_days"] == 30
        assert "total_users" in content["data"]
        assert "total_conversations" in content["data"]
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_system_progress_analytics_exception(self, mock_admin_user):
        """Test system progress analytics retrieval with exception"""
        with patch(
            "app.api.progress_analytics.JSONResponse",
            side_effect=Exception("System analytics error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await get_system_progress_analytics(admin_user=mock_admin_user)

            assert "System analytics error" in str(exc_info.value)


# ============= UTILITY ENDPOINT TESTS =============


class TestUtilityEndpoints:
    """Test utility endpoints"""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        response = await health_check()

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert content["message"] == "Progress Analytics API is healthy"
        assert content["data"]["service"] == "progress_analytics"
        assert content["data"]["status"] == "operational"
        assert "features" in content["data"]
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_api_stats_success(self):
        """Test successful API stats retrieval"""
        response = await get_api_stats()

        assert isinstance(response, JSONResponse)
        content = json.loads(response.body.decode())
        assert content["success"] is True
        assert (
            content["message"]
            == "Progress Analytics API statistics retrieved successfully"
        )
        assert content["data"]["endpoints_available"] == 14
        assert content["data"]["conversation_tracking_active"] is True
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_api_stats_exception(self):
        """Test API stats retrieval with exception"""
        with patch(
            "app.api.progress_analytics.JSONResponse",
            side_effect=Exception("Stats error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await get_api_stats()

            assert "Stats error" in str(exc_info.value)


# ============= MODULE-LEVEL TESTS =============


class TestModuleLevel:
    """Test module-level objects and initialization"""

    def test_router_initialization(self):
        """Test router is properly initialized"""
        assert router is not None
        assert router.prefix == "/api/progress-analytics"
        assert "Progress Analytics" in router.tags

    def test_progress_service_initialization(self):
        """Test progress service is initialized"""
        assert progress_service is not None
        from app.services.progress_analytics_service import ProgressAnalyticsService

        assert isinstance(progress_service, ProgressAnalyticsService)


# ============= INTEGRATION TESTS =============


class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_conversation_to_dashboard_workflow(
        self, sample_conversation_request
    ):
        """Test complete workflow from tracking conversation to dashboard"""
        # Track conversation
        with patch.object(
            progress_service, "track_conversation_session", return_value=True
        ):
            track_response = await track_conversation_session(
                sample_conversation_request
            )
            track_content = json.loads(track_response.body.decode())
            assert track_content["success"] is True

        # Get analytics
        mock_analytics = {"overview": {"total_conversations": 1}}
        with patch.object(
            progress_service, "get_conversation_analytics", return_value=mock_analytics
        ):
            analytics_response = await get_conversation_analytics(
                user_id=1, language_code="es"
            )
            analytics_content = json.loads(analytics_response.body.decode())
            assert analytics_content["success"] is True

    @pytest.mark.asyncio
    async def test_skill_update_to_analytics_workflow(
        self, sample_skill_update_request
    ):
        """Test complete workflow from skill update to analytics"""
        # Update skill
        with patch.object(progress_service, "update_skill_progress", return_value=True):
            update_response = await update_skill_progress(sample_skill_update_request)
            update_content = json.loads(update_response.body.decode())
            assert update_content["success"] is True

        # Get skill analytics
        mock_analytics = {"skill_overview": {"total_skills_tracked": 1}}
        with patch.object(
            progress_service, "get_multi_skill_analytics", return_value=mock_analytics
        ):
            analytics_response = await get_multi_skill_analytics(
                user_id=1, language_code="es"
            )
            analytics_content = json.loads(analytics_response.body.decode())
            assert analytics_content["success"] is True

    @pytest.mark.asyncio
    async def test_learning_path_generation_workflow(
        self, sample_learning_path_request
    ):
        """Test learning path generation and retrieval workflow"""
        # Generate learning path
        generate_response = await generate_learning_path(sample_learning_path_request)
        generate_content = json.loads(generate_response.body.decode())
        assert generate_content["success"] is True

        # Get recommendations
        recommendations_response = await get_learning_path_recommendations(
            user_id=1, language_code="es"
        )
        recommendations_content = json.loads(recommendations_response.body.decode())
        assert recommendations_content["success"] is True
