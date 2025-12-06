"""
Comprehensive Test Suite for app/api/scenarios.py
AI Language Tutor App - Scenario-Based Conversation API Endpoints

This test suite achieves TRUE 100% coverage (statements + branches + zero warnings)
for the scenarios API module, following the proven methodology from Sessions 84-88.

Test Coverage:
- Pydantic Models (4 models): Validation and field tests
- Helper Functions (4 functions): All paths and edge cases
- API Endpoints (11 endpoints): Success, error, and edge cases
- Integration Tests: Multi-endpoint workflows
- Module-level Tests: Router and utility functions

Quality Standards:
- Read actual code definitions first ✅
- Direct function imports for coverage ✅
- Comprehensive test coverage (happy + error + edge) ✅
- HTTPException re-raising patterns ✅
- AsyncMock for async operations ✅
- Zero warnings ✅
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException

# Direct imports for coverage measurement
from app.api.scenarios import (
    CreateFromTemplateRequest,
    # Pydantic models
    ScenarioListRequest,
    ScenarioMessageRequest,
    ScenarioResponse,
    StartScenarioRequest,
    _add_user_recommendations,
    _build_scenarios_response,
    _get_category_description,
    # Helper functions
    _validate_scenario_filters,
    complete_scenario_conversation,
    create_scenario_from_template,
    get_scenario_categories,
    get_scenario_details,
    get_scenario_progress,
    get_scenarios_by_category,
    # Utility function
    get_scenarios_router,
    get_tier1_scenarios,
    get_universal_templates,
    # API endpoints
    list_scenarios,
    send_scenario_message,
    start_scenario_conversation,
)
from app.services.conversation_models import LearningFocus

# Import enums and models
from app.services.scenario_manager import (
    ConversationRole,
    ScenarioCategory,
    ScenarioDifficulty,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = Mock()
    user.id = 123
    return user


@pytest.fixture
def sample_scenarios():
    """Sample scenario data"""
    return [
        {
            "id": "restaurant_001",
            "name": "Restaurant Ordering",
            "category": "restaurant",
            "difficulty": "beginner",
            "description": "Practice ordering food",
        },
        {
            "id": "travel_001",
            "name": "Hotel Check-in",
            "category": "travel",
            "difficulty": "intermediate",
            "description": "Check into a hotel",
        },
        {
            "id": "shopping_001",
            "name": "Buying Clothes",
            "category": "shopping",
            "difficulty": "advanced",
            "description": "Shopping for clothing",
        },
    ]


@pytest.fixture
def sample_scenario_details():
    """Sample detailed scenario data"""
    return {
        "scenario_id": "restaurant_001",
        "name": "Restaurant Ordering",
        "category": "restaurant",
        "difficulty": "beginner",
        "description": "Practice ordering food at a restaurant",
        "phases": ["arrival", "ordering", "dining", "payment"],
        "objectives": ["Order food", "Ask questions", "Pay the bill"],
        "vocabulary": ["menu", "waiter", "order", "bill"],
    }


@pytest.fixture
def sample_conversation_context():
    """Sample conversation context"""
    context = Mock()
    context.user_id = "123"
    context.scenario_progress_id = "progress_001"
    context.is_scenario_based = True
    return context


@pytest.fixture
def sample_scenario_progress():
    """Sample scenario progress data"""
    return {
        "progress_id": "progress_001",
        "scenario_id": "restaurant_001",
        "current_phase": "ordering",
        "completed_phases": ["arrival"],
        "score": 85,
        "objectives_completed": 2,
        "total_objectives": 5,
    }


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================


class TestPydanticModels:
    """Test Pydantic model validation and field defaults"""

    def test_scenario_list_request_all_fields(self):
        """Test ScenarioListRequest with all fields"""
        request = ScenarioListRequest(
            category="restaurant", difficulty="beginner", user_level="advanced"
        )
        assert request.category == "restaurant"
        assert request.difficulty == "beginner"
        assert request.user_level == "advanced"

    def test_scenario_list_request_defaults(self):
        """Test ScenarioListRequest with default values"""
        request = ScenarioListRequest()
        assert request.category is None
        assert request.difficulty is None
        assert request.user_level == "intermediate"

    def test_start_scenario_request_all_fields(self):
        """Test StartScenarioRequest with all fields"""
        request = StartScenarioRequest(
            scenario_id="restaurant_001",
            language="es",
            learning_focus="pronunciation",
        )
        assert request.scenario_id == "restaurant_001"
        assert request.language == "es"
        assert request.learning_focus == "pronunciation"

    def test_start_scenario_request_defaults(self):
        """Test StartScenarioRequest with default values"""
        request = StartScenarioRequest(scenario_id="test_001")
        assert request.scenario_id == "test_001"
        assert request.language == "en"
        assert request.learning_focus == "conversation"

    def test_scenario_message_request_all_fields(self):
        """Test ScenarioMessageRequest with all fields"""
        request = ScenarioMessageRequest(
            conversation_id="conv_123", message="Hello", include_speech=True
        )
        assert request.conversation_id == "conv_123"
        assert request.message == "Hello"
        assert request.include_speech is True

    def test_scenario_message_request_defaults(self):
        """Test ScenarioMessageRequest with default values"""
        request = ScenarioMessageRequest(conversation_id="conv_123", message="Hi")
        assert request.conversation_id == "conv_123"
        assert request.message == "Hi"
        assert request.include_speech is False

    def test_create_from_template_request_all_fields(self):
        """Test CreateFromTemplateRequest with all fields"""
        request = CreateFromTemplateRequest(
            template_id="template_001",
            difficulty="advanced",
            variation_id="var_001",
            user_role="customer",
            ai_role="service_provider",
        )
        assert request.template_id == "template_001"
        assert request.difficulty == "advanced"
        assert request.variation_id == "var_001"
        assert request.user_role == "customer"
        assert request.ai_role == "service_provider"

    def test_create_from_template_request_defaults(self):
        """Test CreateFromTemplateRequest with default values"""
        request = CreateFromTemplateRequest(
            template_id="template_001", difficulty="beginner"
        )
        assert request.template_id == "template_001"
        assert request.difficulty == "beginner"
        assert request.variation_id is None
        assert request.user_role == "student"
        assert request.ai_role == "teacher"

    def test_scenario_response_success(self):
        """Test ScenarioResponse success case"""
        response = ScenarioResponse(
            success=True, data={"test": "data"}, message="Success"
        )
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.message == "Success"
        assert response.error is None

    def test_scenario_response_error(self):
        """Test ScenarioResponse error case"""
        response = ScenarioResponse(success=False, error="Test error", message="Failed")
        assert response.success is False
        assert response.error == "Test error"
        assert response.message == "Failed"
        assert response.data is None

    def test_scenario_response_minimal(self):
        """Test ScenarioResponse with minimal fields"""
        response = ScenarioResponse(success=True)
        assert response.success is True
        assert response.data is None
        assert response.message is None
        assert response.error is None


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestHelperFunctions:
    """Test helper functions for scenarios API"""

    def test_validate_scenario_filters_valid_category(self):
        """Test _validate_scenario_filters with valid category"""
        # Should not raise exception
        _validate_scenario_filters("restaurant", None)

    def test_validate_scenario_filters_valid_difficulty(self):
        """Test _validate_scenario_filters with valid difficulty"""
        # Should not raise exception
        _validate_scenario_filters(None, "beginner")

    def test_validate_scenario_filters_both_valid(self):
        """Test _validate_scenario_filters with both valid"""
        # Should not raise exception
        _validate_scenario_filters("travel", "intermediate")

    def test_validate_scenario_filters_both_none(self):
        """Test _validate_scenario_filters with both None"""
        # Should not raise exception
        _validate_scenario_filters(None, None)

    def test_validate_scenario_filters_invalid_category(self):
        """Test _validate_scenario_filters with invalid category"""
        with pytest.raises(HTTPException) as exc_info:
            _validate_scenario_filters("invalid_category", None)
        assert exc_info.value.status_code == 400
        assert "Invalid category" in exc_info.value.detail

    def test_validate_scenario_filters_invalid_difficulty(self):
        """Test _validate_scenario_filters with invalid difficulty"""
        with pytest.raises(HTTPException) as exc_info:
            _validate_scenario_filters(None, "invalid_difficulty")
        assert exc_info.value.status_code == 400
        assert "Invalid difficulty" in exc_info.value.detail

    def test_add_user_recommendations_exact_match(self):
        """Test _add_user_recommendations with exact difficulty match"""
        scenarios = [
            {"id": "1", "difficulty": "beginner"},
            {"id": "2", "difficulty": "intermediate"},
        ]
        result = _add_user_recommendations(scenarios, "beginner")
        assert result[0]["recommended"] is True
        # Beginner also recommends intermediate
        assert result[1]["recommended"] is True

    def test_add_user_recommendations_beginner_intermediate(self):
        """Test _add_user_recommendations beginner recommends intermediate"""
        scenarios = [
            {"id": "1", "difficulty": "beginner"},
            {"id": "2", "difficulty": "intermediate"},
            {"id": "3", "difficulty": "advanced"},
        ]
        result = _add_user_recommendations(scenarios, "beginner")
        assert result[0]["recommended"] is True  # beginner matches
        assert result[1]["recommended"] is True  # intermediate recommended for beginner
        assert result[2]["recommended"] is False  # advanced not recommended

    def test_add_user_recommendations_intermediate_no_extra(self):
        """Test _add_user_recommendations intermediate doesn't recommend beginner"""
        scenarios = [
            {"id": "1", "difficulty": "beginner"},
            {"id": "2", "difficulty": "intermediate"},
        ]
        result = _add_user_recommendations(scenarios, "intermediate")
        assert result[0]["recommended"] is False
        assert result[1]["recommended"] is True

    def test_add_user_recommendations_advanced(self):
        """Test _add_user_recommendations with advanced level"""
        scenarios = [
            {"id": "1", "difficulty": "beginner"},
            {"id": "2", "difficulty": "advanced"},
        ]
        result = _add_user_recommendations(scenarios, "advanced")
        assert result[0]["recommended"] is False
        assert result[1]["recommended"] is True

    def test_build_scenarios_response_empty_list(self):
        """Test _build_scenarios_response with empty scenario list"""
        result = _build_scenarios_response([])
        assert result.success is True
        assert result.data["scenarios"] == []
        assert result.data["total_count"] == 0
        assert len(result.data["categories"]) > 0
        assert len(result.data["difficulties"]) > 0
        assert "Found 0" in result.message

    def test_build_scenarios_response_multiple_scenarios(self):
        """Test _build_scenarios_response with multiple scenarios"""
        scenarios = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        result = _build_scenarios_response(scenarios)
        assert result.success is True
        assert result.data["scenarios"] == scenarios
        assert result.data["total_count"] == 3
        assert "Found 3" in result.message

    def test_get_category_description_all_categories(self):
        """Test _get_category_description for all known categories"""
        categories_to_test = [
            ScenarioCategory.TRAVEL,
            ScenarioCategory.RESTAURANT,
            ScenarioCategory.SHOPPING,
            ScenarioCategory.BUSINESS,
            ScenarioCategory.HEALTHCARE,
            ScenarioCategory.SOCIAL,
            ScenarioCategory.EMERGENCY,
            ScenarioCategory.EDUCATION,
            ScenarioCategory.DAILY_LIFE,
            ScenarioCategory.HOBBIES,
        ]
        for category in categories_to_test:
            description = _get_category_description(category)
            assert isinstance(description, str)
            assert len(description) > 0

    def test_get_category_description_unknown_category(self):
        """Test _get_category_description with unknown category returns default"""
        # Create a mock category that's not in the descriptions dict
        mock_category = Mock()
        mock_category.value = "unknown_category"
        description = _get_category_description(mock_category)
        assert description == "Practice structured conversations in this context"


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================


class TestListScenariosEndpoint:
    """Test list_scenarios endpoint"""

    @pytest.mark.asyncio
    async def test_list_scenarios_success_no_filters(self, mock_user, sample_scenarios):
        """Test listing scenarios without filters"""
        with patch("app.api.scenarios.get_available_scenarios") as mock_get_scenarios:
            mock_get_scenarios.return_value = sample_scenarios

            result = await list_scenarios(current_user=mock_user)

            assert result.success is True
            assert len(result.data["scenarios"]) == 3
            assert result.data["total_count"] == 3
            # Check that recommendations were added
            assert "recommended" in result.data["scenarios"][0]

    @pytest.mark.asyncio
    async def test_list_scenarios_with_category_filter(
        self, mock_user, sample_scenarios
    ):
        """Test listing scenarios with category filter"""
        filtered_scenarios = [
            s for s in sample_scenarios if s["category"] == "restaurant"
        ]
        with patch("app.api.scenarios.get_available_scenarios") as mock_get_scenarios:
            mock_get_scenarios.return_value = filtered_scenarios

            result = await list_scenarios(category="restaurant", current_user=mock_user)

            assert result.success is True
            assert len(result.data["scenarios"]) == 1
            assert result.data["scenarios"][0]["category"] == "restaurant"

    @pytest.mark.asyncio
    async def test_list_scenarios_with_difficulty_filter(
        self, mock_user, sample_scenarios
    ):
        """Test listing scenarios with difficulty filter"""
        filtered_scenarios = [
            s for s in sample_scenarios if s["difficulty"] == "beginner"
        ]
        with patch("app.api.scenarios.get_available_scenarios") as mock_get_scenarios:
            mock_get_scenarios.return_value = filtered_scenarios

            result = await list_scenarios(difficulty="beginner", current_user=mock_user)

            assert result.success is True
            assert len(result.data["scenarios"]) == 1
            assert result.data["scenarios"][0]["difficulty"] == "beginner"

    @pytest.mark.asyncio
    async def test_list_scenarios_with_user_level(self, mock_user, sample_scenarios):
        """Test listing scenarios with custom user level"""
        with patch("app.api.scenarios.get_available_scenarios") as mock_get_scenarios:
            mock_get_scenarios.return_value = sample_scenarios

            result = await list_scenarios(user_level="advanced", current_user=mock_user)

            assert result.success is True
            # Verify recommendations based on advanced level
            for scenario in result.data["scenarios"]:
                if scenario["difficulty"] == "advanced":
                    assert scenario["recommended"] is True

    @pytest.mark.asyncio
    async def test_list_scenarios_invalid_category(self, mock_user):
        """Test listing scenarios with invalid category raises 400"""
        with pytest.raises(HTTPException) as exc_info:
            await list_scenarios(category="invalid_cat", current_user=mock_user)
        assert exc_info.value.status_code == 400
        assert "Invalid category" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_list_scenarios_invalid_difficulty(self, mock_user):
        """Test listing scenarios with invalid difficulty raises 400"""
        with pytest.raises(HTTPException) as exc_info:
            await list_scenarios(difficulty="invalid_diff", current_user=mock_user)
        assert exc_info.value.status_code == 400
        assert "Invalid difficulty" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_list_scenarios_service_exception(self, mock_user):
        """Test listing scenarios when service raises exception"""
        with patch("app.api.scenarios.get_available_scenarios") as mock_get_scenarios:
            mock_get_scenarios.side_effect = Exception("Service error")

            with pytest.raises(HTTPException) as exc_info:
                await list_scenarios(current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve scenarios" in exc_info.value.detail


class TestGetScenarioDetailsEndpoint:
    """Test get_scenario_details endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenario_details_success(
        self, mock_user, sample_scenario_details
    ):
        """Test getting scenario details successfully"""
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_scenario_details.return_value = sample_scenario_details

            result = await get_scenario_details("restaurant_001", mock_user)

            assert result.success is True
            assert result.data == sample_scenario_details
            assert "successfully" in result.message

    @pytest.mark.asyncio
    async def test_get_scenario_details_not_found(self, mock_user):
        """Test getting details for non-existent scenario"""
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_scenario_details.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_details("nonexistent_001", mock_user)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_scenario_details_service_exception(self, mock_user):
        """Test getting scenario details when service raises exception"""
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_scenario_details.side_effect = Exception("Service error")

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_details("restaurant_001", mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve scenario details" in exc_info.value.detail


class TestStartScenarioConversationEndpoint:
    """Test start_scenario_conversation endpoint"""

    @pytest.mark.asyncio
    async def test_start_scenario_conversation_success(
        self, mock_user, sample_scenario_progress
    ):
        """Test starting scenario conversation successfully"""
        request = StartScenarioRequest(
            scenario_id="restaurant_001",
            language="es",
            learning_focus="conversation",
        )

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.start_conversation = AsyncMock(return_value="conv_123")
            mock_context = Mock()
            mock_context.scenario_progress_id = "progress_001"
            mock_conv_manager.active_conversations = {"conv_123": mock_context}

            with patch("app.api.scenarios.get_scenario_status") as mock_get_status:
                mock_get_status.return_value = sample_scenario_progress

                result = await start_scenario_conversation(request, mock_user)

                assert result.success is True
                assert result.data["conversation_id"] == "conv_123"
                assert result.data["scenario_progress"] == sample_scenario_progress
                assert result.data["language"] == "es"

    @pytest.mark.asyncio
    async def test_start_scenario_conversation_no_progress_id(self, mock_user):
        """Test starting scenario conversation without progress ID"""
        request = StartScenarioRequest(scenario_id="restaurant_001")

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.start_conversation = AsyncMock(return_value="conv_123")
            mock_context = Mock()
            mock_context.scenario_progress_id = None
            mock_conv_manager.active_conversations = {"conv_123": mock_context}

            result = await start_scenario_conversation(request, mock_user)

            assert result.success is True
            assert result.data["conversation_id"] == "conv_123"
            assert result.data["scenario_progress"] is None

    @pytest.mark.asyncio
    async def test_start_scenario_conversation_invalid_learning_focus(self, mock_user):
        """Test starting scenario with invalid learning focus"""
        request = StartScenarioRequest(
            scenario_id="restaurant_001", learning_focus="invalid_focus"
        )

        with pytest.raises(HTTPException) as exc_info:
            await start_scenario_conversation(request, mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid learning focus" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_scenario_conversation_service_exception(self, mock_user):
        """Test starting scenario when service raises exception"""
        request = StartScenarioRequest(scenario_id="restaurant_001")

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.start_conversation = AsyncMock(
                side_effect=Exception("Service error")
            )

            with pytest.raises(HTTPException) as exc_info:
                await start_scenario_conversation(request, mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to start scenario conversation" in exc_info.value.detail


class TestSendScenarioMessageEndpoint:
    """Test send_scenario_message endpoint"""

    @pytest.mark.asyncio
    async def test_send_scenario_message_success(
        self, mock_user, sample_conversation_context
    ):
        """Test sending message in scenario conversation"""
        request = ScenarioMessageRequest(
            conversation_id="conv_123", message="I would like to order"
        )

        response_data = {
            "ai_response": "What would you like to order?",
            "analysis": {"confidence": 0.9},
        }

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.send_message = AsyncMock(return_value=response_data)

            result = await send_scenario_message(request, mock_user)

            assert result.success is True
            assert result.data == response_data
            assert "successfully" in result.message

    @pytest.mark.asyncio
    async def test_send_scenario_message_conversation_not_found(self, mock_user):
        """Test sending message to non-existent conversation"""
        request = ScenarioMessageRequest(conversation_id="nonexistent", message="Hello")

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {}

            with pytest.raises(HTTPException) as exc_info:
                await send_scenario_message(request, mock_user)

            assert exc_info.value.status_code == 404
            assert "not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_send_scenario_message_access_denied(
        self, mock_user, sample_conversation_context
    ):
        """Test sending message to another user's conversation"""
        request = ScenarioMessageRequest(conversation_id="conv_123", message="Hello")

        wrong_user_context = Mock()
        wrong_user_context.user_id = "999"  # Different user

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {"conv_123": wrong_user_context}

            with pytest.raises(HTTPException) as exc_info:
                await send_scenario_message(request, mock_user)

            assert exc_info.value.status_code == 403
            assert "Access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_send_scenario_message_service_exception(
        self, mock_user, sample_conversation_context
    ):
        """Test sending message when service raises exception"""
        request = ScenarioMessageRequest(conversation_id="conv_123", message="Hello")

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.send_message = AsyncMock(
                side_effect=Exception("Service error")
            )

            with pytest.raises(HTTPException) as exc_info:
                await send_scenario_message(request, mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to process message" in exc_info.value.detail


class TestGetScenarioProgressEndpoint:
    """Test get_scenario_progress endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenario_progress_success_with_scenario(
        self, mock_user, sample_conversation_context, sample_scenario_progress
    ):
        """Test getting progress for scenario-based conversation"""
        conversation_summary = {"total_messages": 10, "duration": 300}

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.get_conversation_summary = AsyncMock(
                return_value=conversation_summary
            )

            with patch("app.api.scenarios.get_scenario_status") as mock_get_status:
                mock_get_status.return_value = sample_scenario_progress

                result = await get_scenario_progress("conv_123", mock_user)

                assert result.success is True
                assert result.data["conversation_summary"] == conversation_summary
                assert result.data["scenario_progress"] == sample_scenario_progress
                assert result.data["is_scenario_based"] is True

    @pytest.mark.asyncio
    async def test_get_scenario_progress_non_scenario_conversation(self, mock_user):
        """Test getting progress for non-scenario conversation"""
        context = Mock()
        context.user_id = "123"
        context.is_scenario_based = False
        context.scenario_progress_id = None

        conversation_summary = {"total_messages": 5, "duration": 150}

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {"conv_123": context}
            mock_conv_manager.get_conversation_summary = AsyncMock(
                return_value=conversation_summary
            )

            result = await get_scenario_progress("conv_123", mock_user)

            assert result.success is True
            assert result.data["scenario_progress"] is None
            assert result.data["is_scenario_based"] is False

    @pytest.mark.asyncio
    async def test_get_scenario_progress_conversation_not_found(self, mock_user):
        """Test getting progress for non-existent conversation"""
        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {}

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_progress("nonexistent", mock_user)

            assert exc_info.value.status_code == 404
            assert "not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_scenario_progress_access_denied(self, mock_user):
        """Test getting progress for another user's conversation"""
        context = Mock()
        context.user_id = "999"  # Different user

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {"conv_123": context}

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_progress("conv_123", mock_user)

            assert exc_info.value.status_code == 403
            assert "Access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_scenario_progress_service_exception(
        self, mock_user, sample_conversation_context
    ):
        """Test getting progress when service raises exception"""
        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.get_conversation_summary = AsyncMock(
                side_effect=Exception("Service error")
            )

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_progress("conv_123", mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve progress" in exc_info.value.detail


class TestCompleteScenarioConversationEndpoint:
    """Test complete_scenario_conversation endpoint"""

    @pytest.mark.asyncio
    async def test_complete_scenario_conversation_success_with_scenario(
        self, mock_user, sample_conversation_context
    ):
        """Test completing scenario-based conversation"""
        conversation_summary = {"total_messages": 20, "duration": 600}
        scenario_summary = {"score": 90, "completion_time": 600}

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.end_conversation = AsyncMock(
                return_value=conversation_summary
            )

            with patch("app.api.scenarios.finish_scenario") as mock_finish:
                mock_finish.return_value = scenario_summary

                result = await complete_scenario_conversation("conv_123", mock_user)

                assert result.success is True
                assert result.data["conversation_summary"] == conversation_summary
                assert result.data["scenario_summary"] == scenario_summary
                assert "completion_time" in result.data

    @pytest.mark.asyncio
    async def test_complete_scenario_conversation_non_scenario(self, mock_user):
        """Test completing non-scenario conversation"""
        context = Mock()
        context.user_id = "123"
        context.is_scenario_based = False
        context.scenario_progress_id = None

        conversation_summary = {"total_messages": 10, "duration": 300}

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {"conv_123": context}
            mock_conv_manager.end_conversation = AsyncMock(
                return_value=conversation_summary
            )

            result = await complete_scenario_conversation("conv_123", mock_user)

            assert result.success is True
            assert result.data["conversation_summary"] == conversation_summary
            assert result.data["scenario_summary"] is None

    @pytest.mark.asyncio
    async def test_complete_scenario_conversation_scenario_finish_fails(
        self, mock_user, sample_conversation_context
    ):
        """Test completing scenario when finish_scenario fails"""
        conversation_summary = {"total_messages": 20, "duration": 600}

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.end_conversation = AsyncMock(
                return_value=conversation_summary
            )

            with patch("app.api.scenarios.finish_scenario") as mock_finish:
                mock_finish.side_effect = Exception("Scenario finish error")

                result = await complete_scenario_conversation("conv_123", mock_user)

                # Should still succeed even if scenario finish fails
                assert result.success is True
                assert result.data["scenario_summary"] is None

    @pytest.mark.asyncio
    async def test_complete_scenario_conversation_not_found(self, mock_user):
        """Test completing non-existent conversation"""
        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {}

            with pytest.raises(HTTPException) as exc_info:
                await complete_scenario_conversation("nonexistent", mock_user)

            assert exc_info.value.status_code == 404
            assert "not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_scenario_conversation_access_denied(self, mock_user):
        """Test completing another user's conversation"""
        context = Mock()
        context.user_id = "999"  # Different user

        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {"conv_123": context}

            with pytest.raises(HTTPException) as exc_info:
                await complete_scenario_conversation("conv_123", mock_user)

            assert exc_info.value.status_code == 403
            assert "Access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_scenario_conversation_service_exception(
        self, mock_user, sample_conversation_context
    ):
        """Test completing conversation when service raises exception"""
        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.active_conversations = {
                "conv_123": sample_conversation_context
            }
            mock_conv_manager.end_conversation = AsyncMock(
                side_effect=Exception("Service error")
            )

            with pytest.raises(HTTPException) as exc_info:
                await complete_scenario_conversation("conv_123", mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to complete conversation" in exc_info.value.detail


class TestGetScenarioCategoriesEndpoint:
    """Test get_scenario_categories endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenario_categories_success(self):
        """Test getting scenario categories successfully"""
        result = await get_scenario_categories()

        assert result.success is True
        assert "categories" in result.data
        assert len(result.data["categories"]) == len(ScenarioCategory)

        # Verify structure of each category
        for category in result.data["categories"]:
            assert "id" in category
            assert "name" in category
            assert "description" in category

    @pytest.mark.asyncio
    async def test_get_scenario_categories_exception(self):
        """Test getting categories when exception occurs"""
        with patch("app.api.scenarios._get_category_description") as mock_get_desc:
            mock_get_desc.side_effect = Exception("Description error")

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_categories()

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve categories" in exc_info.value.detail


class TestGetUniversalTemplatesEndpoint:
    """Test get_universal_templates endpoint"""

    @pytest.mark.asyncio
    async def test_get_universal_templates_no_filter(self, mock_user):
        """Test getting all universal templates"""
        templates = [{"id": "template_001"}, {"id": "template_002"}]

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_universal_templates.return_value = templates

            result = await get_universal_templates(current_user=mock_user)

            assert result.success is True
            assert result.data["templates"] == templates
            assert result.data["total_count"] == 2
            assert result.data["tier_filter"] is None

    @pytest.mark.asyncio
    async def test_get_universal_templates_with_tier_filter(self, mock_user):
        """Test getting templates filtered by tier"""
        templates = [{"id": "template_001", "tier": 1}]

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_universal_templates.return_value = templates

            result = await get_universal_templates(tier=1, current_user=mock_user)

            assert result.success is True
            assert result.data["templates"] == templates
            assert result.data["tier_filter"] == 1
            assert "tier 1" in result.message

    @pytest.mark.asyncio
    async def test_get_universal_templates_exception(self, mock_user):
        """Test getting templates when exception occurs"""
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_universal_templates.side_effect = Exception(
                "Template error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await get_universal_templates(current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve templates" in exc_info.value.detail


class TestGetTier1ScenariosEndpoint:
    """Test get_tier1_scenarios endpoint"""

    @pytest.mark.asyncio
    async def test_get_tier1_scenarios_success(self, mock_user):
        """Test getting Tier 1 scenarios successfully"""
        tier1_scenarios = [
            {"id": "tier1_001", "tier": 1},
            {"id": "tier1_002", "tier": 1},
        ]

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_tier1_scenarios.return_value = tier1_scenarios

            result = await get_tier1_scenarios(current_user=mock_user)

            assert result.success is True
            assert result.data["tier1_scenarios"] == tier1_scenarios
            assert result.data["total_count"] == 2
            assert result.data["tier"] == 1
            assert "Essential" in result.data["description"]

    @pytest.mark.asyncio
    async def test_get_tier1_scenarios_exception(self, mock_user):
        """Test getting Tier 1 scenarios when exception occurs"""
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_tier1_scenarios.side_effect = Exception("Tier1 error")

            with pytest.raises(HTTPException) as exc_info:
                await get_tier1_scenarios(current_user=mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve Tier 1 scenarios" in exc_info.value.detail


class TestCreateScenarioFromTemplateEndpoint:
    """Test create_scenario_from_template endpoint"""

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_success(self, mock_user):
        """Test creating scenario from template successfully"""
        request = CreateFromTemplateRequest(
            template_id="template_001",
            difficulty="intermediate",
            user_role="customer",
            ai_role="service_provider",
        )

        mock_scenario = Mock()
        mock_scenario.scenario_id = "scenario_123"
        mock_scenario.name = "Test Scenario"

        scenario_details = {
            "scenario_id": "scenario_123",
            "name": "Test Scenario",
            "difficulty": "intermediate",
        }

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.create_scenario_from_template.return_value = mock_scenario
            mock_manager.get_scenario_details.return_value = scenario_details

            result = await create_scenario_from_template(request, mock_user)

            assert result.success is True
            assert result.data["scenario"] == scenario_details
            assert result.data["template_id"] == "template_001"

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_with_variation(self, mock_user):
        """Test creating scenario with specific variation"""
        request = CreateFromTemplateRequest(
            template_id="template_001",
            difficulty="beginner",
            variation_id="var_001",
        )

        mock_scenario = Mock()
        mock_scenario.scenario_id = "scenario_123"
        mock_scenario.name = "Test Scenario"

        scenario_details = {"scenario_id": "scenario_123"}

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.create_scenario_from_template.return_value = mock_scenario
            mock_manager.get_scenario_details.return_value = scenario_details

            result = await create_scenario_from_template(request, mock_user)

            assert result.success is True
            assert result.data["variation_id"] == "var_001"

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_invalid_difficulty(self, mock_user):
        """Test creating scenario with invalid difficulty"""
        request = CreateFromTemplateRequest(
            template_id="template_001", difficulty="invalid_diff"
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_scenario_from_template(request, mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid difficulty level" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_invalid_user_role(self, mock_user):
        """Test creating scenario with invalid user role"""
        request = CreateFromTemplateRequest(
            template_id="template_001",
            difficulty="beginner",
            user_role="invalid_role",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_scenario_from_template(request, mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid role" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_invalid_ai_role(self, mock_user):
        """Test creating scenario with invalid AI role"""
        request = CreateFromTemplateRequest(
            template_id="template_001",
            difficulty="beginner",
            ai_role="invalid_role",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_scenario_from_template(request, mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid role" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_not_found(self, mock_user):
        """Test creating scenario from non-existent template"""
        request = CreateFromTemplateRequest(
            template_id="nonexistent", difficulty="beginner"
        )

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.create_scenario_from_template.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await create_scenario_from_template(request, mock_user)

            assert exc_info.value.status_code == 404
            assert "Template not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_scenario_from_template_exception(self, mock_user):
        """Test creating scenario when exception occurs"""
        request = CreateFromTemplateRequest(
            template_id="template_001", difficulty="beginner"
        )

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.create_scenario_from_template.side_effect = Exception(
                "Creation error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await create_scenario_from_template(request, mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to create scenario" in exc_info.value.detail


class TestGetScenariosByCategoryEndpoint:
    """Test get_scenarios_by_category endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenarios_by_category_success(self, mock_user):
        """Test getting scenarios by valid category"""
        category_data = {
            "category": "restaurant",
            "scenarios": [{"id": "restaurant_001"}],
            "templates": [{"id": "template_001"}],
        }

        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_scenarios_by_category.return_value = category_data

            result = await get_scenarios_by_category("restaurant", mock_user)

            assert result.success is True
            assert result.data == category_data
            assert "restaurant" in result.message

    @pytest.mark.asyncio
    async def test_get_scenarios_by_category_invalid_category(self, mock_user):
        """Test getting scenarios with invalid category"""
        with pytest.raises(HTTPException) as exc_info:
            await get_scenarios_by_category("invalid_category", mock_user)

        assert exc_info.value.status_code == 400
        assert "Invalid category" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_scenarios_by_category_exception(self, mock_user):
        """Test getting scenarios when exception occurs"""
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_scenarios_by_category.side_effect = Exception(
                "Category error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await get_scenarios_by_category("restaurant", mock_user)

            assert exc_info.value.status_code == 500
            assert "Failed to retrieve category scenarios" in exc_info.value.detail


# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================


class TestGetScenariosRouter:
    """Test get_scenarios_router utility function"""

    def test_get_scenarios_router_returns_router(self):
        """Test that get_scenarios_router returns the router instance"""
        router = get_scenarios_router()
        assert router is not None
        assert hasattr(router, "routes")
        assert router.prefix == "/api/v1/scenarios"


# ============================================================================
# INTEGRATION WORKFLOW TESTS
# ============================================================================


class TestScenarioWorkflows:
    """Test end-to-end scenario workflows"""

    @pytest.mark.asyncio
    async def test_complete_scenario_workflow(
        self, mock_user, sample_scenarios, sample_scenario_progress
    ):
        """Test complete workflow: list -> start -> message -> progress -> complete"""
        # 1. List scenarios
        with patch("app.api.scenarios.get_available_scenarios") as mock_get_scenarios:
            mock_get_scenarios.return_value = sample_scenarios
            scenarios_result = await list_scenarios(current_user=mock_user)
            assert scenarios_result.success is True

        # 2. Start scenario conversation
        start_request = StartScenarioRequest(scenario_id="restaurant_001")
        with patch("app.api.scenarios.conversation_manager") as mock_conv_manager:
            mock_conv_manager.start_conversation = AsyncMock(return_value="conv_123")
            mock_context = Mock()
            mock_context.user_id = "123"
            mock_context.scenario_progress_id = "progress_001"
            mock_context.is_scenario_based = True
            mock_conv_manager.active_conversations = {"conv_123": mock_context}

            with patch("app.api.scenarios.get_scenario_status") as mock_get_status:
                mock_get_status.return_value = sample_scenario_progress
                start_result = await start_scenario_conversation(
                    start_request, mock_user
                )
                assert start_result.success is True
                conversation_id = start_result.data["conversation_id"]

            # 3. Send message
            message_request = ScenarioMessageRequest(
                conversation_id=conversation_id, message="Hello"
            )
            mock_conv_manager.send_message = AsyncMock(
                return_value={"ai_response": "Hi"}
            )
            message_result = await send_scenario_message(message_request, mock_user)
            assert message_result.success is True

            # 4. Check progress
            mock_conv_manager.get_conversation_summary = AsyncMock(
                return_value={"total_messages": 2}
            )
            progress_result = await get_scenario_progress(conversation_id, mock_user)
            assert progress_result.success is True

            # 5. Complete scenario
            mock_conv_manager.end_conversation = AsyncMock(
                return_value={"total_messages": 10}
            )
            with patch("app.api.scenarios.finish_scenario") as mock_finish:
                mock_finish.return_value = {"score": 90}
                complete_result = await complete_scenario_conversation(
                    conversation_id, mock_user
                )
                assert complete_result.success is True

    @pytest.mark.asyncio
    async def test_template_creation_workflow(self, mock_user):
        """Test workflow: get templates -> create from template -> get details"""
        # 1. Get templates
        templates = [{"id": "template_001"}]
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_universal_templates.return_value = templates
            templates_result = await get_universal_templates(current_user=mock_user)
            assert templates_result.success is True

            # 2. Create scenario from template
            create_request = CreateFromTemplateRequest(
                template_id="template_001", difficulty="beginner"
            )
            mock_scenario = Mock()
            mock_scenario.scenario_id = "scenario_123"
            mock_scenario.name = "Created Scenario"
            scenario_details = {"scenario_id": "scenario_123"}

            mock_manager.create_scenario_from_template.return_value = mock_scenario
            mock_manager.get_scenario_details.return_value = scenario_details

            create_result = await create_scenario_from_template(
                create_request, mock_user
            )
            assert create_result.success is True

            # 3. Get scenario details
            details_result = await get_scenario_details("scenario_123", mock_user)
            assert details_result.success is True

    @pytest.mark.asyncio
    async def test_category_browsing_workflow(self, mock_user):
        """Test workflow: get categories -> browse category -> get scenario details"""
        # 1. Get all categories
        categories_result = await get_scenario_categories()
        assert categories_result.success is True

        # 2. Browse specific category
        category_data = {
            "scenarios": [{"id": "restaurant_001"}],
            "templates": [{"id": "template_001"}],
        }
        with patch("app.api.scenarios.scenario_manager") as mock_manager:
            mock_manager.get_scenarios_by_category.return_value = category_data
            category_result = await get_scenarios_by_category("restaurant", mock_user)
            assert category_result.success is True

            # 3. Get scenario details
            scenario_details = {"scenario_id": "restaurant_001"}
            mock_manager.get_scenario_details.return_value = scenario_details
            details_result = await get_scenario_details("restaurant_001", mock_user)
            assert details_result.success is True
