"""
Comprehensive Test Suite for Learning Analytics API
Session 88 - TRUE 100% Coverage Campaign

Following proven patterns from Sessions 84-87:
- Read actual code first ✅
- Direct function imports ✅
- Comprehensive test coverage ✅
- No compromises on quality ✅
- Quality over speed ✅
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Direct imports from the module for coverage measurement
from app.api.learning_analytics import (
    CreateGoalRequest,
    # Pydantic Models
    CreateLearningItemRequest,
    EndSessionRequest,
    # Pydantic Enums
    ItemTypeEnum,
    ReviewItemRequest,
    ReviewResultEnum,
    SessionTypeEnum,
    StartSessionRequest,
    UpdateConfigRequest,
    create_learning_goal,
    # API Endpoints
    create_learning_item,
    end_learning_session,
    get_algorithm_config,
    get_api_stats,
    get_due_items,
    get_system_analytics,
    get_user_achievements,
    get_user_analytics,
    get_user_goals,
    health_check,
    review_item,
    # Router
    router,
    # Manager
    sr_manager,
    start_learning_session,
    update_algorithm_config,
)
from app.models.database import User
from app.services.spaced_repetition_manager import ItemType, ReviewResult, SessionType

# ============= PYDANTIC ENUM TESTS =============


class TestPydanticEnums:
    """Test Pydantic enum definitions"""

    def test_item_type_enum_values(self):
        """Test ItemTypeEnum has correct values"""
        assert ItemTypeEnum.VOCABULARY.value == "vocabulary"
        assert ItemTypeEnum.PHRASE.value == "phrase"
        assert ItemTypeEnum.GRAMMAR.value == "grammar"
        assert ItemTypeEnum.PRONUNCIATION.value == "pronunciation"

    def test_session_type_enum_values(self):
        """Test SessionTypeEnum has correct values"""
        assert SessionTypeEnum.VOCABULARY.value == "vocabulary"
        assert SessionTypeEnum.CONVERSATION.value == "conversation"
        assert SessionTypeEnum.TUTOR_MODE.value == "tutor_mode"
        assert SessionTypeEnum.SCENARIO.value == "scenario"
        assert SessionTypeEnum.CONTENT_REVIEW.value == "content_review"

    def test_review_result_enum_values(self):
        """Test ReviewResultEnum has correct values"""
        assert ReviewResultEnum.AGAIN.value == "again"
        assert ReviewResultEnum.HARD.value == "hard"
        assert ReviewResultEnum.GOOD.value == "good"
        assert ReviewResultEnum.EASY.value == "easy"


# ============= PYDANTIC MODEL TESTS =============


class TestPydanticModels:
    """Test Pydantic model validation"""

    def test_create_learning_item_request_valid(self):
        """Test CreateLearningItemRequest with valid data"""
        request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="hola",
            item_type=ItemTypeEnum.VOCABULARY,
            translation="hello",
            definition="A greeting",
            pronunciation_guide="OH-lah",
            example_usage="Hola, ¿cómo estás?",
            context_tags=["greetings", "basic"],
            source_session_id="session_123",
            source_content="conversation",
            metadata={"difficulty": "easy"},
        )
        assert request.user_id == 123
        assert request.language_code == "es"
        assert request.content == "hola"
        assert request.item_type == ItemTypeEnum.VOCABULARY

    def test_create_learning_item_request_defaults(self):
        """Test CreateLearningItemRequest with default values"""
        request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="hola",
            item_type=ItemTypeEnum.VOCABULARY,
        )
        assert request.translation == ""
        assert request.definition == ""
        assert request.pronunciation_guide == ""
        assert request.example_usage == ""
        assert request.context_tags == []
        assert request.source_session_id == ""
        assert request.source_content == ""
        assert request.metadata == {}

    def test_review_item_request_valid(self):
        """Test ReviewItemRequest with valid data"""
        request = ReviewItemRequest(
            item_id="item_123",
            review_result=ReviewResultEnum.GOOD,
            response_time_ms=1500,
            confidence_score=0.85,
        )
        assert request.item_id == "item_123"
        assert request.review_result == ReviewResultEnum.GOOD
        assert request.response_time_ms == 1500
        assert request.confidence_score == 0.85

    def test_review_item_request_defaults(self):
        """Test ReviewItemRequest with default values"""
        request = ReviewItemRequest(
            item_id="item_123", review_result=ReviewResultEnum.GOOD
        )
        assert request.response_time_ms == 0
        assert request.confidence_score == 0.0

    def test_start_session_request_valid(self):
        """Test StartSessionRequest with valid data"""
        request = StartSessionRequest(
            user_id=123,
            language_code="es",
            session_type=SessionTypeEnum.VOCABULARY,
            mode_specific_data={"mode": "flashcards"},
            content_source="app",
            ai_model_used="gpt-4",
            tutor_mode="socratic",
            scenario_id="scenario_123",
        )
        assert request.user_id == 123
        assert request.session_type == SessionTypeEnum.VOCABULARY

    def test_start_session_request_defaults(self):
        """Test StartSessionRequest with default values"""
        request = StartSessionRequest(
            user_id=123, language_code="es", session_type=SessionTypeEnum.VOCABULARY
        )
        assert request.mode_specific_data == {}
        assert request.content_source == ""
        assert request.ai_model_used == ""
        assert request.tutor_mode == ""
        assert request.scenario_id == ""

    def test_end_session_request_valid(self):
        """Test EndSessionRequest with valid data"""
        request = EndSessionRequest(
            session_id="session_123",
            items_studied=20,
            items_correct=18,
            items_incorrect=2,
            average_response_time_ms=2000,
            confidence_score=0.9,
            engagement_score=0.85,
            new_items_learned=5,
        )
        assert request.session_id == "session_123"
        assert request.items_studied == 20

    def test_end_session_request_defaults(self):
        """Test EndSessionRequest with default values"""
        request = EndSessionRequest(session_id="session_123")
        assert request.items_studied == 0
        assert request.items_correct == 0
        assert request.items_incorrect == 0
        assert request.average_response_time_ms == 0
        assert request.confidence_score == 0.0
        assert request.engagement_score == 0.0
        assert request.new_items_learned == 0

    def test_create_goal_request_valid(self):
        """Test CreateGoalRequest with valid data"""
        request = CreateGoalRequest(
            user_id=123,
            language_code="es",
            goal_type="vocabulary_mastery",
            title="Master 100 words",
            description="Learn 100 new vocabulary words",
            target_value=100.0,
            unit="words",
            difficulty_level=2,
            priority=1,
            is_daily=False,
            is_weekly=False,
            is_monthly=True,
            target_days=30,
        )
        assert request.user_id == 123
        assert request.target_value == 100.0

    def test_create_goal_request_defaults(self):
        """Test CreateGoalRequest with default values"""
        request = CreateGoalRequest(
            user_id=123,
            language_code="es",
            goal_type="vocabulary",
            title="Learn words",
            target_value=50.0,
            unit="words",
        )
        assert request.description == ""
        assert request.difficulty_level == 2
        assert request.priority == 2
        assert request.is_daily is False
        assert request.is_weekly is False
        assert request.is_monthly is False
        assert request.target_days == 30

    def test_update_config_request_all_fields(self):
        """Test UpdateConfigRequest with all fields"""
        request = UpdateConfigRequest(
            initial_ease_factor=2.5,
            minimum_ease_factor=1.3,
            maximum_ease_factor=3.0,
            ease_factor_change=0.15,
            initial_interval_days=1,
            graduation_interval_days=3,
            easy_interval_days=4,
            maximum_interval_days=365,
            mastery_threshold=0.8,
            review_threshold=0.6,
            difficulty_threshold=0.4,
            retention_threshold=0.7,
            points_per_correct=10.0,
            points_per_streak_day=5.0,
            points_per_goal_achieved=100.0,
            daily_goal_default=20,
        )
        assert request.initial_ease_factor == 2.5
        assert request.daily_goal_default == 20

    def test_update_config_request_none_values(self):
        """Test UpdateConfigRequest with None values (all optional)"""
        request = UpdateConfigRequest()
        assert request.initial_ease_factor is None
        assert request.minimum_ease_factor is None
        assert request.maximum_ease_factor is None


# ============= SPACED REPETITION ENDPOINT TESTS =============


class TestSpacedRepetitionEndpoints:
    """Test spaced repetition API endpoints"""

    @pytest.mark.asyncio
    async def test_create_learning_item_success(self):
        """Test successful learning item creation"""
        request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="hola",
            item_type=ItemTypeEnum.VOCABULARY,
            translation="hello",
        )

        with patch.object(sr_manager, "add_learning_item", return_value="item_123"):
            response = await create_learning_item(request)

            assert response.status_code == 201
            content = response.body.decode()
            assert "item_123" in content
            assert "success" in content

    @pytest.mark.asyncio
    async def test_create_learning_item_exception(self):
        """Test learning item creation with exception"""
        request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="hola",
            item_type=ItemTypeEnum.VOCABULARY,
        )

        with patch.object(
            sr_manager, "add_learning_item", side_effect=Exception("Database error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await create_learning_item(request)

            assert exc_info.value.status_code == 500
            assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_review_item_success(self):
        """Test successful item review"""
        request = ReviewItemRequest(
            item_id="item_123",
            review_result=ReviewResultEnum.GOOD,
            response_time_ms=1500,
            confidence_score=0.85,
        )

        with patch.object(sr_manager, "review_item", return_value=True):
            response = await review_item(request)

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "item_123" in content

    @pytest.mark.asyncio
    async def test_review_item_not_found(self):
        """Test item review with item not found"""
        request = ReviewItemRequest(
            item_id="item_999", review_result=ReviewResultEnum.GOOD
        )

        with patch.object(sr_manager, "review_item", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await review_item(request)

            assert exc_info.value.status_code == 404
            assert "Item not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_review_item_exception(self):
        """Test item review with exception"""
        request = ReviewItemRequest(
            item_id="item_123", review_result=ReviewResultEnum.GOOD
        )

        with patch.object(
            sr_manager, "review_item", side_effect=Exception("Review error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await review_item(request)

            assert exc_info.value.status_code == 500
            assert "Review error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_due_items_success(self):
        """Test successful retrieval of due items"""
        mock_items = [
            {"item_id": "item_1", "content": "hola"},
            {"item_id": "item_2", "content": "adiós"},
        ]

        with patch.object(sr_manager, "get_due_items", return_value=mock_items):
            response = await get_due_items(user_id=123, language_code="es", limit=20)

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "2" in content  # count

    @pytest.mark.asyncio
    async def test_get_due_items_empty(self):
        """Test retrieval of due items with no items"""
        with patch.object(sr_manager, "get_due_items", return_value=[]):
            response = await get_due_items(user_id=123, language_code="es", limit=20)

            assert response.status_code == 200
            content = response.body.decode()
            assert "0" in content  # count

    @pytest.mark.asyncio
    async def test_get_due_items_exception(self):
        """Test get due items with exception"""
        with patch.object(
            sr_manager, "get_due_items", side_effect=Exception("Database error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_due_items(user_id=123, language_code="es", limit=20)

            assert exc_info.value.status_code == 500
            assert "Database error" in str(exc_info.value.detail)


# ============= LEARNING SESSION ENDPOINT TESTS =============


class TestLearningSessionEndpoints:
    """Test learning session API endpoints"""

    @pytest.mark.asyncio
    async def test_start_learning_session_success(self):
        """Test successful session start"""
        request = StartSessionRequest(
            user_id=123,
            language_code="es",
            session_type=SessionTypeEnum.VOCABULARY,
            mode_specific_data={"mode": "flashcards"},
        )

        with patch.object(
            sr_manager, "start_learning_session", return_value="session_123"
        ):
            response = await start_learning_session(request)

            assert response.status_code == 201
            content = response.body.decode()
            assert "session_123" in content
            assert "success" in content

    @pytest.mark.asyncio
    async def test_start_learning_session_exception(self):
        """Test session start with exception"""
        request = StartSessionRequest(
            user_id=123, language_code="es", session_type=SessionTypeEnum.VOCABULARY
        )

        with patch.object(
            sr_manager, "start_learning_session", side_effect=Exception("Session error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await start_learning_session(request)

            assert exc_info.value.status_code == 500
            assert "Session error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_end_learning_session_success(self):
        """Test successful session end"""
        request = EndSessionRequest(
            session_id="session_123",
            items_studied=20,
            items_correct=18,
            items_incorrect=2,
        )

        with patch.object(sr_manager, "end_learning_session", return_value=True):
            response = await end_learning_session(request)

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "session_123" in content

    @pytest.mark.asyncio
    async def test_end_learning_session_not_found(self):
        """Test session end with session not found"""
        request = EndSessionRequest(session_id="session_999")

        with patch.object(sr_manager, "end_learning_session", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await end_learning_session(request)

            assert exc_info.value.status_code == 404
            assert "Session not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_end_learning_session_exception(self):
        """Test session end with exception"""
        request = EndSessionRequest(session_id="session_123")

        with patch.object(
            sr_manager,
            "end_learning_session",
            side_effect=Exception("End session error"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await end_learning_session(request)

            assert exc_info.value.status_code == 500
            assert "End session error" in str(exc_info.value.detail)


# ============= ANALYTICS ENDPOINT TESTS =============


class TestAnalyticsEndpoints:
    """Test analytics API endpoints"""

    @pytest.mark.asyncio
    async def test_get_user_analytics_success(self):
        """Test successful user analytics retrieval"""
        mock_analytics = {
            "total_items": 100,
            "mastered_items": 50,
            "retention_rate": 0.85,
        }

        with patch.object(
            sr_manager, "get_user_analytics", return_value=mock_analytics
        ):
            response = await get_user_analytics(
                user_id=123, language_code="es", period="daily"
            )

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "total_items" in content

    @pytest.mark.asyncio
    async def test_get_user_analytics_exception(self):
        """Test user analytics with exception"""
        with patch.object(
            sr_manager, "get_user_analytics", side_effect=Exception("Analytics error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_user_analytics(
                    user_id=123, language_code="es", period="weekly"
                )

            assert exc_info.value.status_code == 500
            assert "Analytics error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_system_analytics_success(self):
        """Test successful system analytics retrieval"""
        mock_analytics = {
            "total_users": 1000,
            "total_items": 50000,
            "average_retention": 0.75,
        }

        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(
            sr_manager, "get_system_analytics", return_value=mock_analytics
        ):
            response = await get_system_analytics(admin_user=mock_admin)

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "total_users" in content

    @pytest.mark.asyncio
    async def test_get_system_analytics_exception(self):
        """Test system analytics with exception"""
        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(
            sr_manager, "get_system_analytics", side_effect=Exception("System error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_system_analytics(admin_user=mock_admin)

            assert exc_info.value.status_code == 500
            assert "System error" in str(exc_info.value.detail)


# ============= GOALS MANAGEMENT ENDPOINT TESTS =============


class TestGoalsManagementEndpoints:
    """Test goals management API endpoints"""

    @pytest.mark.asyncio
    async def test_create_learning_goal_success(self):
        """Test successful goal creation"""
        request = CreateGoalRequest(
            user_id=123,
            language_code="es",
            goal_type="vocabulary",
            title="Master 100 words",
            target_value=100.0,
            unit="words",
            target_days=30,
        )

        response = await create_learning_goal(request)

        assert response.status_code == 201
        content = response.body.decode()
        assert "success" in content
        assert "goal_" in content
        assert "target_date" in content

    @pytest.mark.asyncio
    async def test_create_learning_goal_exception(self):
        """Test goal creation with exception"""
        request = CreateGoalRequest(
            user_id=123,
            language_code="es",
            goal_type="vocabulary",
            title="Master words",
            target_value=100.0,
            unit="words",
        )

        with patch("app.api.learning_analytics.datetime") as mock_datetime:
            mock_datetime.now.side_effect = Exception("Date error")

            with pytest.raises(HTTPException) as exc_info:
                await create_learning_goal(request)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_user_goals_success(self):
        """Test successful user goals retrieval"""
        response = await get_user_goals(
            user_id=123, language_code="es", status="active"
        )

        assert response.status_code == 200
        content = response.body.decode()
        assert "success" in content
        assert "goals" in content
        assert "count" in content

    @pytest.mark.asyncio
    async def test_get_user_goals_exception(self):
        """Test user goals with exception"""
        # Trigger exception by mocking JSONResponse to raise
        with patch("app.api.learning_analytics.JSONResponse") as mock_response:
            mock_response.side_effect = Exception("Response error")

            with pytest.raises(HTTPException) as exc_info:
                await get_user_goals(user_id=123, language_code="es", status="active")

            assert exc_info.value.status_code == 500
            assert "Response error" in str(exc_info.value.detail)


# ============= ACHIEVEMENTS ENDPOINT TESTS =============


class TestAchievementsEndpoints:
    """Test achievements API endpoints"""

    @pytest.mark.asyncio
    async def test_get_user_achievements_with_language(self):
        """Test user achievements with language code"""
        response = await get_user_achievements(
            user_id=123, language_code="es", limit=50
        )

        assert response.status_code == 200
        content = response.body.decode()
        assert "success" in content
        assert "achievements" in content
        assert "total_points" in content

    @pytest.mark.asyncio
    async def test_get_user_achievements_without_language(self):
        """Test user achievements without language code"""
        response = await get_user_achievements(
            user_id=123, language_code=None, limit=50
        )

        assert response.status_code == 200
        content = response.body.decode()
        assert "success" in content

    @pytest.mark.asyncio
    async def test_get_user_achievements_exception(self):
        """Test user achievements with exception"""
        with patch("app.api.learning_analytics.JSONResponse") as mock_response:
            mock_response.side_effect = Exception("Response error")

            with pytest.raises(HTTPException) as exc_info:
                await get_user_achievements(user_id=123, language_code="es", limit=50)

            assert exc_info.value.status_code == 500


# ============= ADMIN CONFIGURATION ENDPOINT TESTS =============


class TestAdminConfigurationEndpoints:
    """Test admin configuration API endpoints"""

    @pytest.mark.asyncio
    async def test_get_algorithm_config_success(self):
        """Test successful algorithm config retrieval"""
        mock_config = {
            "initial_ease_factor": 2.5,
            "minimum_ease_factor": 1.3,
            "maximum_ease_factor": 3.0,
        }

        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(sr_manager, "config", mock_config):
            response = await get_algorithm_config(admin_user=mock_admin)

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "initial_ease_factor" in content

    @pytest.mark.asyncio
    async def test_get_algorithm_config_exception(self):
        """Test algorithm config with exception"""
        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(sr_manager, "config", side_effect=Exception("Config error")):
            with pytest.raises(HTTPException) as exc_info:
                await get_algorithm_config(admin_user=mock_admin)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_update_algorithm_config_success(self):
        """Test successful algorithm config update"""
        request = UpdateConfigRequest(
            initial_ease_factor=2.5,
            minimum_ease_factor=1.3,
            daily_goal_default=25,
        )

        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(sr_manager, "update_algorithm_config", return_value=True):
            response = await update_algorithm_config(request, admin_user=mock_admin)

            assert response.status_code == 200
            content = response.body.decode()
            assert "success" in content
            assert "updated_fields" in content

    @pytest.mark.asyncio
    async def test_update_algorithm_config_no_updates(self):
        """Test algorithm config update with no fields provided"""
        request = UpdateConfigRequest()  # All None values

        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with pytest.raises(HTTPException) as exc_info:
            await update_algorithm_config(request, admin_user=mock_admin)

        assert exc_info.value.status_code == 400
        assert "No configuration updates provided" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_algorithm_config_failed(self):
        """Test algorithm config update failure"""
        request = UpdateConfigRequest(initial_ease_factor=2.5)

        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(sr_manager, "update_algorithm_config", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await update_algorithm_config(request, admin_user=mock_admin)

            assert exc_info.value.status_code == 500
            assert "Failed to update configuration" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_algorithm_config_exception(self):
        """Test algorithm config update with exception"""
        request = UpdateConfigRequest(initial_ease_factor=2.5)

        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        with patch.object(
            sr_manager, "update_algorithm_config", side_effect=Exception("Update error")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await update_algorithm_config(request, admin_user=mock_admin)

            assert exc_info.value.status_code == 500


# ============= UTILITY ENDPOINT TESTS =============


class TestUtilityEndpoints:
    """Test utility API endpoints"""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test health check endpoint"""
        response = await health_check()

        assert response.status_code == 200
        content = response.body.decode()
        assert "success" in content
        assert "learning_analytics" in content
        assert "operational" in content
        assert "timestamp" in content

    @pytest.mark.asyncio
    async def test_get_api_stats_success(self):
        """Test API stats endpoint"""
        response = await get_api_stats()

        assert response.status_code == 200
        content = response.body.decode()
        assert "success" in content
        assert "endpoints_available" in content
        assert "13" in content  # 13 endpoints

    @pytest.mark.asyncio
    async def test_get_api_stats_exception(self):
        """Test API stats with exception"""
        with patch("app.api.learning_analytics.JSONResponse") as mock_response:
            mock_response.side_effect = Exception("Stats error")

            with pytest.raises(HTTPException) as exc_info:
                await get_api_stats()

            assert exc_info.value.status_code == 500


# ============= ROUTER TESTS =============


class TestRouter:
    """Test router configuration"""

    def test_router_prefix(self):
        """Test router has correct prefix"""
        assert router.prefix == "/api/learning-analytics"

    def test_router_tags(self):
        """Test router has correct tags"""
        assert "Learning Analytics" in router.tags


# ============= MODULE-LEVEL TESTS =============


class TestModuleLevel:
    """Test module-level functionality"""

    def test_sr_manager_exists(self):
        """Test SpacedRepetitionManager is initialized"""
        assert sr_manager is not None
        assert hasattr(sr_manager, "add_learning_item")
        assert hasattr(sr_manager, "review_item")
        assert hasattr(sr_manager, "get_due_items")

    def test_all_exports(self):
        """Test __all__ exports"""
        from app.api.learning_analytics import __all__

        assert "router" in __all__


# ============= ENUM CONVERSION TESTS =============


class TestEnumConversion:
    """Test enum conversion in endpoints"""

    @pytest.mark.asyncio
    async def test_create_item_enum_conversion_vocabulary(self):
        """Test ItemType enum conversion for VOCABULARY"""
        request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="test",
            item_type=ItemTypeEnum.VOCABULARY,
        )

        with patch.object(
            sr_manager, "add_learning_item", return_value="item_123"
        ) as mock_add:
            await create_learning_item(request)
            # Verify ItemType.VOCABULARY was passed (not ItemTypeEnum)
            mock_add.assert_called_once()
            call_kwargs = mock_add.call_args.kwargs
            assert call_kwargs["item_type"] == ItemType.VOCABULARY

    @pytest.mark.asyncio
    async def test_create_item_enum_conversion_phrase(self):
        """Test ItemType enum conversion for PHRASE"""
        request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="test",
            item_type=ItemTypeEnum.PHRASE,
        )

        with patch.object(
            sr_manager, "add_learning_item", return_value="item_123"
        ) as mock_add:
            await create_learning_item(request)
            call_kwargs = mock_add.call_args.kwargs
            assert call_kwargs["item_type"] == ItemType.PHRASE

    @pytest.mark.asyncio
    async def test_review_item_enum_conversion_again(self):
        """Test ReviewResult enum conversion for AGAIN"""
        request = ReviewItemRequest(
            item_id="item_123", review_result=ReviewResultEnum.AGAIN
        )

        with patch.object(sr_manager, "review_item", return_value=True) as mock_review:
            await review_item(request)
            call_kwargs = mock_review.call_args.kwargs
            assert call_kwargs["review_result"] == ReviewResult.AGAIN

    @pytest.mark.asyncio
    async def test_review_item_enum_conversion_hard(self):
        """Test ReviewResult enum conversion for HARD"""
        request = ReviewItemRequest(
            item_id="item_123", review_result=ReviewResultEnum.HARD
        )

        with patch.object(sr_manager, "review_item", return_value=True) as mock_review:
            await review_item(request)
            call_kwargs = mock_review.call_args.kwargs
            assert call_kwargs["review_result"] == ReviewResult.HARD

    @pytest.mark.asyncio
    async def test_review_item_enum_conversion_easy(self):
        """Test ReviewResult enum conversion for EASY"""
        request = ReviewItemRequest(
            item_id="item_123", review_result=ReviewResultEnum.EASY
        )

        with patch.object(sr_manager, "review_item", return_value=True) as mock_review:
            await review_item(request)
            call_kwargs = mock_review.call_args.kwargs
            assert call_kwargs["review_result"] == ReviewResult.EASY

    @pytest.mark.asyncio
    async def test_start_session_enum_conversion_conversation(self):
        """Test SessionType enum conversion for CONVERSATION"""
        request = StartSessionRequest(
            user_id=123, language_code="es", session_type=SessionTypeEnum.CONVERSATION
        )

        with patch.object(
            sr_manager, "start_learning_session", return_value="session_123"
        ) as mock_start:
            await start_learning_session(request)
            call_kwargs = mock_start.call_args.kwargs
            assert call_kwargs["session_type"] == SessionType.CONVERSATION

    @pytest.mark.asyncio
    async def test_start_session_enum_conversion_scenario(self):
        """Test SessionType enum conversion for SCENARIO"""
        request = StartSessionRequest(
            user_id=123, language_code="es", session_type=SessionTypeEnum.SCENARIO
        )

        with patch.object(
            sr_manager, "start_learning_session", return_value="session_123"
        ) as mock_start:
            await start_learning_session(request)
            call_kwargs = mock_start.call_args.kwargs
            assert call_kwargs["session_type"] == SessionType.SCENARIO


# ============= INTEGRATION WORKFLOW TESTS =============


class TestIntegrationWorkflows:
    """Test complete workflows across multiple endpoints"""

    @pytest.mark.asyncio
    async def test_complete_learning_workflow(self):
        """Test complete workflow: create item -> get due -> review"""
        # Step 1: Create learning item
        create_request = CreateLearningItemRequest(
            user_id=123,
            language_code="es",
            content="hola",
            item_type=ItemTypeEnum.VOCABULARY,
            translation="hello",
        )

        with patch.object(sr_manager, "add_learning_item", return_value="item_123"):
            create_response = await create_learning_item(create_request)
            assert create_response.status_code == 201

        # Step 2: Get due items
        with patch.object(
            sr_manager,
            "get_due_items",
            return_value=[{"item_id": "item_123", "content": "hola"}],
        ):
            due_response = await get_due_items(
                user_id=123, language_code="es", limit=20
            )
            assert due_response.status_code == 200

        # Step 3: Review item
        review_request = ReviewItemRequest(
            item_id="item_123", review_result=ReviewResultEnum.GOOD
        )

        with patch.object(sr_manager, "review_item", return_value=True):
            review_response = await review_item(review_request)
            assert review_response.status_code == 200

    @pytest.mark.asyncio
    async def test_complete_session_workflow(self):
        """Test complete workflow: start session -> end session -> get analytics"""
        # Step 1: Start session
        start_request = StartSessionRequest(
            user_id=123, language_code="es", session_type=SessionTypeEnum.VOCABULARY
        )

        with patch.object(
            sr_manager, "start_learning_session", return_value="session_123"
        ):
            start_response = await start_learning_session(start_request)
            assert start_response.status_code == 201

        # Step 2: End session
        end_request = EndSessionRequest(session_id="session_123", items_studied=10)

        with patch.object(sr_manager, "end_learning_session", return_value=True):
            end_response = await end_learning_session(end_request)
            assert end_response.status_code == 200

        # Step 3: Get analytics
        with patch.object(
            sr_manager, "get_user_analytics", return_value={"total_sessions": 1}
        ):
            analytics_response = await get_user_analytics(
                user_id=123, language_code="es", period="daily"
            )
            assert analytics_response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_config_workflow(self):
        """Test admin workflow: get config -> update config -> verify"""
        mock_admin = User(user_id="admin_1", username="admin", email="admin@test.com")

        # Step 1: Get current config
        mock_config = {"initial_ease_factor": 2.5}
        with patch.object(sr_manager, "config", mock_config):
            get_response = await get_algorithm_config(admin_user=mock_admin)
            assert get_response.status_code == 200

        # Step 2: Update config
        update_request = UpdateConfigRequest(initial_ease_factor=2.8)

        with patch.object(sr_manager, "update_algorithm_config", return_value=True):
            update_response = await update_algorithm_config(
                update_request, admin_user=mock_admin
            )
            assert update_response.status_code == 200

        # Step 3: Verify update
        updated_config = {"initial_ease_factor": 2.8}
        with patch.object(sr_manager, "config", updated_config):
            verify_response = await get_algorithm_config(admin_user=mock_admin)
            assert verify_response.status_code == 200
