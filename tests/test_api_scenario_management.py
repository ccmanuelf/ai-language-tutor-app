"""
Tests for Scenario Management API
app/api/scenario_management.py

Testing TRUE 100% coverage with actual behavior validation.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.scenario_management import (
    BulkScenarioOperation,
    ContentProcessingConfigModel,
    ScenarioCreateRequest,
    ScenarioModel,
    ScenarioPhaseModel,
    ScenarioUpdateRequest,
    _apply_scenario_filters,
    _apply_scenario_updates,
    _build_scenario_dict,
    _convert_phase_data_to_objects,
    _convert_scenarios_to_models,
    _get_scenario_or_404,
    _update_enum_field,
    router,
)
from app.services.admin_auth import AdminPermission
from app.services.scenario_manager import (
    ConversationRole,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioPhase,
)

# ===========================
# Test Fixtures
# ===========================


@pytest.fixture
def mock_scenario():
    """Create a mock conversation scenario"""
    phases = [
        ScenarioPhase(
            phase_id="phase1",
            name="Introduction",
            description="Initial greeting",
            expected_duration_minutes=5,
            key_vocabulary=["hello", "goodbye"],
            essential_phrases=["How are you?"],
            learning_objectives=["Greetings"],
            cultural_notes="Be polite",
            success_criteria=["Complete greeting"],
        )
    ]

    scenario = ConversationScenario(
        scenario_id="test_scenario_1",
        name="Test Restaurant",
        category=ScenarioCategory.RESTAURANT,
        difficulty=ScenarioDifficulty.BEGINNER,
        description="A test restaurant scenario",
        user_role=ConversationRole.CUSTOMER,
        ai_role=ConversationRole.SERVICE_PROVIDER,
        setting="A busy Italian restaurant",
        duration_minutes=30,
        phases=phases,
        prerequisites=["basic_greetings"],
        learning_outcomes=["Order food", "Pay bill"],
        vocabulary_focus=["menu", "waiter", "food"],
        cultural_context="Italian dining customs",
    )

    # Add timestamp attributes
    scenario.is_active = True
    scenario.created_at = datetime(2024, 1, 1, 12, 0, 0)
    scenario.updated_at = datetime(2024, 1, 2, 12, 0, 0)

    return scenario


@pytest.fixture
def mock_scenario_manager():
    """Create a mock scenario manager"""
    manager = AsyncMock()
    manager.initialize = AsyncMock()
    manager.get_all_scenarios = AsyncMock()
    manager.get_scenario_by_id = AsyncMock()
    manager.save_scenario = AsyncMock()
    manager.delete_scenario = AsyncMock()
    manager.set_scenario_active = AsyncMock()
    return manager


@pytest.fixture
def admin_user():
    """Create a mock admin user"""
    user = MagicMock()
    user.id = "admin_123"
    user.username = "admin"
    user.is_admin = True
    return user


@pytest.fixture
def scenario_create_request():
    """Create a valid scenario creation request"""
    return ScenarioCreateRequest(
        name="New Restaurant Scenario",
        category="restaurant",
        difficulty="intermediate",
        description="A comprehensive restaurant ordering scenario",
        user_role="customer",
        ai_role="service_provider",
        setting="Upscale French restaurant",
        duration_minutes=45,
        phases=[
            ScenarioPhaseModel(
                phase_id="phase1",
                name="Arrival",
                description="Enter and be seated",
                expected_duration_minutes=5,
                key_vocabulary=["reservation", "table"],
                essential_phrases=["Table for two please"],
                learning_objectives=["Making reservations"],
                cultural_notes="Wait to be seated",
                success_criteria=["Successfully seated"],
            )
        ],
        prerequisites=["basic_french"],
        learning_outcomes=["Order in French", "Understand menu"],
        vocabulary_focus=["cuisine", "wine", "dessert"],
        cultural_context="French dining etiquette",
    )


# ===========================
# Helper Function Tests
# ===========================


class TestApplyScenarioFilters:
    """Test _apply_scenario_filters function"""

    def test_filter_by_category(self, mock_scenario):
        """Test filtering scenarios by category"""
        scenarios = [mock_scenario]

        # Should include the scenario
        result = _apply_scenario_filters(scenarios, "restaurant", None, True)
        assert len(result) == 1

        # Should exclude the scenario
        result = _apply_scenario_filters(scenarios, "travel", None, True)
        assert len(result) == 0

    def test_filter_by_difficulty(self, mock_scenario):
        """Test filtering scenarios by difficulty"""
        scenarios = [mock_scenario]

        # Should include the scenario
        result = _apply_scenario_filters(scenarios, None, "beginner", True)
        assert len(result) == 1

        # Should exclude the scenario
        result = _apply_scenario_filters(scenarios, None, "advanced", True)
        assert len(result) == 0

    def test_filter_by_active_status(self, mock_scenario):
        """Test filtering by active status"""
        active_scenario = mock_scenario
        active_scenario.is_active = True

        inactive_scenario = ConversationScenario(
            scenario_id="inactive",
            name="Inactive",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Inactive scenario",
            user_role=ConversationRole.TOURIST,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Hotel",
            duration_minutes=20,
            phases=[],
            vocabulary_focus=[],
            cultural_context=None,
        )
        inactive_scenario.is_active = False

        scenarios = [active_scenario, inactive_scenario]

        # Filter active only
        result = _apply_scenario_filters(scenarios, None, None, True)
        assert len(result) == 1
        assert result[0].scenario_id == "test_scenario_1"

        # Don't filter by active status
        result = _apply_scenario_filters(scenarios, None, None, False)
        assert len(result) == 2

    def test_combined_filters(self, mock_scenario):
        """Test applying multiple filters together"""
        scenarios = [mock_scenario]

        # All filters match
        result = _apply_scenario_filters(scenarios, "restaurant", "beginner", True)
        assert len(result) == 1

        # Category matches but difficulty doesn't
        result = _apply_scenario_filters(scenarios, "restaurant", "advanced", True)
        assert len(result) == 0


class TestConvertScenarios:
    """Test scenario conversion functions"""

    def test_build_scenario_dict(self, mock_scenario):
        """Test building scenario dictionary from object"""
        result = _build_scenario_dict(mock_scenario)

        assert result["scenario_id"] == "test_scenario_1"
        assert result["name"] == "Test Restaurant"
        assert result["category"] == "restaurant"
        assert result["difficulty"] == "beginner"
        assert result["user_role"] == "customer"
        assert result["ai_role"] == "service_provider"
        assert result["duration_minutes"] == 30
        assert len(result["phases"]) == 1
        assert result["phases"][0]["phase_id"] == "phase1"
        assert result["phases"][0]["name"] == "Introduction"
        assert result["prerequisites"] == ["basic_greetings"]
        assert result["learning_outcomes"] == ["Order food", "Pay bill"]
        assert result["vocabulary_focus"] == ["menu", "waiter", "food"]
        assert result["cultural_context"] == "Italian dining customs"
        assert result["is_active"] is True
        assert result["created_at"] == datetime(2024, 1, 1, 12, 0, 0)
        assert result["updated_at"] == datetime(2024, 1, 2, 12, 0, 0)

    def test_build_scenario_dict_missing_optional_fields(self):
        """Test building dict from scenario with missing optional fields"""
        minimal_scenario = ConversationScenario(
            scenario_id="minimal",
            name="Minimal",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Minimal scenario",
            user_role=ConversationRole.TOURIST,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Hotel lobby",
            duration_minutes=15,
            phases=[],
            vocabulary_focus=[],
            cultural_context=None,
        )

        result = _build_scenario_dict(minimal_scenario)

        assert result["prerequisites"] == []
        assert result["learning_outcomes"] == []
        assert result["vocabulary_focus"] == []
        assert result["cultural_context"] is None
        assert result["is_active"] is True
        assert result["created_at"] is None
        assert result["updated_at"] is None

    def test_convert_scenarios_to_models(self, mock_scenario):
        """Test converting list of scenarios to models"""
        scenarios = [mock_scenario]

        result = _convert_scenarios_to_models(scenarios)

        assert len(result) == 1
        assert isinstance(result[0], ScenarioModel)
        assert result[0].scenario_id == "test_scenario_1"
        assert result[0].name == "Test Restaurant"


class TestScenarioUpdates:
    """Test scenario update helper functions"""

    def test_convert_phase_data_to_objects(self):
        """Test converting phase data to ScenarioPhase objects"""
        phase_data = [
            ScenarioPhaseModel(
                phase_id="p1",
                name="Phase 1",
                description="First phase",
                expected_duration_minutes=10,
                key_vocabulary=["word1", "word2"],
                essential_phrases=["phrase1"],
                learning_objectives=["objective1"],
                cultural_notes="Note",
                success_criteria=["criteria1"],
            )
        ]

        result = _convert_phase_data_to_objects(phase_data)

        assert len(result) == 1
        assert isinstance(result[0], ScenarioPhase)
        assert result[0].phase_id == "p1"
        assert result[0].name == "Phase 1"
        assert result[0].key_vocabulary == ["word1", "word2"]

    def test_update_enum_field_category(self, mock_scenario):
        """Test updating category enum field"""
        _update_enum_field(mock_scenario, "category", "travel")
        assert mock_scenario.category == ScenarioCategory.TRAVEL

    def test_update_enum_field_difficulty(self, mock_scenario):
        """Test updating difficulty enum field"""
        _update_enum_field(mock_scenario, "difficulty", "advanced")
        assert mock_scenario.difficulty == ScenarioDifficulty.ADVANCED

    def test_update_enum_field_user_role(self, mock_scenario):
        """Test updating user_role enum field"""
        _update_enum_field(mock_scenario, "user_role", "tourist")
        assert mock_scenario.user_role == ConversationRole.TOURIST

    def test_update_enum_field_ai_role(self, mock_scenario):
        """Test updating ai_role enum field"""
        _update_enum_field(mock_scenario, "ai_role", "service_provider")
        assert mock_scenario.ai_role == ConversationRole.SERVICE_PROVIDER

    def test_update_enum_field_unknown_field(self, mock_scenario):
        """Test updating enum field with unknown field name - should do nothing"""
        original_category = mock_scenario.category
        original_difficulty = mock_scenario.difficulty

        # Call with an unknown field name - should not raise error, just do nothing
        _update_enum_field(mock_scenario, "unknown_field", "some_value")

        # Verify nothing changed
        assert mock_scenario.category == original_category
        assert mock_scenario.difficulty == original_difficulty

    def test_apply_scenario_updates_simple_fields(self, mock_scenario):
        """Test applying simple field updates"""
        updates = {
            "name": "Updated Name",
            "description": "Updated description",
            "duration_minutes": 60,
            "is_active": False,
        }

        _apply_scenario_updates(mock_scenario, updates)

        assert mock_scenario.name == "Updated Name"
        assert mock_scenario.description == "Updated description"
        assert mock_scenario.duration_minutes == 60
        assert mock_scenario.is_active is False

    def test_apply_scenario_updates_enum_fields(self, mock_scenario):
        """Test applying enum field updates"""
        updates = {
            "category": "travel",
            "difficulty": "intermediate",
            "user_role": "tourist",
            "ai_role": "local",
        }

        _apply_scenario_updates(mock_scenario, updates)

        assert mock_scenario.category == ScenarioCategory.TRAVEL
        assert mock_scenario.difficulty == ScenarioDifficulty.INTERMEDIATE
        assert mock_scenario.user_role == ConversationRole.TOURIST
        assert mock_scenario.ai_role == ConversationRole.LOCAL

    def test_apply_scenario_updates_phases(self, mock_scenario):
        """Test applying phases update"""
        new_phases = [
            ScenarioPhaseModel(
                phase_id="new_phase",
                name="New Phase",
                description="A new phase",
                expected_duration_minutes=15,
                key_vocabulary=["new_word"],
                essential_phrases=["new phrase"],
                learning_objectives=["new objective"],
                cultural_notes="New note",
                success_criteria=["new criteria"],
            )
        ]

        updates = {"phases": new_phases}

        _apply_scenario_updates(mock_scenario, updates)

        assert len(mock_scenario.phases) == 1
        assert mock_scenario.phases[0].phase_id == "new_phase"
        assert mock_scenario.phases[0].name == "New Phase"

    def test_apply_scenario_updates_phases_none(self, mock_scenario):
        """Test applying None phases doesn't crash"""
        original_phases = mock_scenario.phases
        updates = {"phases": None}

        _apply_scenario_updates(mock_scenario, updates)

        # When phases is None, the update sets it to None (as per the code logic)
        # This is the actual behavior - it doesn't skip None values
        assert mock_scenario.phases is None


class TestGetScenarioOr404:
    """Test _get_scenario_or_404 helper function"""

    @pytest.mark.asyncio
    async def test_get_scenario_success(self, mock_scenario_manager, mock_scenario):
        """Test successfully getting a scenario"""
        mock_scenario_manager.get_scenario_by_id.return_value = mock_scenario

        result = await _get_scenario_or_404(mock_scenario_manager, "test_scenario_1")

        assert result == mock_scenario
        mock_scenario_manager.get_scenario_by_id.assert_called_once_with(
            "test_scenario_1"
        )

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(self, mock_scenario_manager):
        """Test getting non-existent scenario raises 404"""
        mock_scenario_manager.get_scenario_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await _get_scenario_or_404(mock_scenario_manager, "nonexistent")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail


# ===========================
# Endpoint Tests
# ===========================


class TestListScenariosEndpoint:
    """Test GET /scenarios endpoint - already has some coverage"""

    @pytest.mark.asyncio
    async def test_list_scenarios_success(self, admin_user, mock_scenario):
        """Test successfully listing scenarios"""
        scenarios = [mock_scenario]

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_all_scenarios.return_value = scenarios
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import list_scenarios

            result = await list_scenarios(
                category=None,
                difficulty=None,
                active_only=False,
                limit=50,
                offset=0,
                user=admin_user,
            )

            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].scenario_id == "test_scenario_1"

    @pytest.mark.asyncio
    async def test_list_scenarios_error_handling(self, admin_user):
        """Test error handling in list_scenarios endpoint"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_ensure.side_effect = Exception("Database error")

            from app.api.scenario_management import list_scenarios

            with pytest.raises(HTTPException) as exc_info:
                await list_scenarios(
                    category=None,
                    difficulty=None,
                    active_only=True,
                    limit=50,
                    offset=0,
                    user=admin_user,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to list scenarios" in exc_info.value.detail


class TestGetScenarioEndpoint:
    """Test GET /scenarios/{scenario_id} endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenario_success(self, admin_user, mock_scenario):
        """Test successfully getting a scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = mock_scenario
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import get_scenario

            result = await get_scenario("test_scenario_1", user=admin_user)

            assert isinstance(result, ScenarioModel)
            assert result.scenario_id == "test_scenario_1"
            assert result.name == "Test Restaurant"
            assert len(result.phases) == 1

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(self, admin_user):
        """Test getting non-existent scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = None
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import get_scenario

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario("nonexistent", user=admin_user)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_scenario_error_handling(self, admin_user):
        """Test error handling in get_scenario endpoint"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_ensure.side_effect = Exception("Database connection failed")

            from app.api.scenario_management import get_scenario

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario("test_id", user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to get scenario" in exc_info.value.detail


class TestCreateScenarioEndpoint:
    """Test POST /scenarios endpoint"""

    @pytest.mark.asyncio
    async def test_create_scenario_success(self, admin_user, scenario_create_request):
        """Test successfully creating a scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.save_scenario = AsyncMock()
            mock_ensure.return_value = mock_manager

            with patch("app.api.scenario_management.uuid4") as mock_uuid:
                mock_uuid.return_value = "generated-uuid-123"

                from app.api.scenario_management import create_scenario

                result = await create_scenario(scenario_create_request, user=admin_user)

                assert isinstance(result, ScenarioModel)
                assert result.name == "New Restaurant Scenario"
                assert result.category == "restaurant"
                assert result.difficulty == "intermediate"
                assert result.user_role == "customer"
                assert result.ai_role == "service_provider"
                assert result.is_active is True
                assert result.created_at is not None
                assert result.updated_at is not None
                assert len(result.phases) == 1

                # Verify save was called
                mock_manager.save_scenario.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_scenario_error_handling(
        self, admin_user, scenario_create_request
    ):
        """Test error handling when creating scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_ensure.side_effect = Exception("Failed to save scenario")

            from app.api.scenario_management import create_scenario

            with pytest.raises(HTTPException) as exc_info:
                await create_scenario(scenario_create_request, user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to create scenario" in exc_info.value.detail


class TestUpdateScenarioEndpoint:
    """Test PUT /scenarios/{scenario_id} endpoint"""

    @pytest.mark.asyncio
    async def test_update_scenario_success(self, admin_user, mock_scenario):
        """Test successfully updating a scenario"""
        update_request = ScenarioUpdateRequest(
            name="Updated Restaurant Name",
            difficulty="advanced",
            duration_minutes=60,
        )

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = mock_scenario
            mock_manager.save_scenario = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import update_scenario

            result = await update_scenario(
                "test_scenario_1", update_request, user=admin_user
            )

            assert isinstance(result, ScenarioModel)
            assert result.name == "Updated Restaurant Name"
            assert result.difficulty == "advanced"
            assert result.duration_minutes == 60

            # Verify save was called
            mock_manager.save_scenario.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_scenario_not_found(self, admin_user):
        """Test updating non-existent scenario"""
        update_request = ScenarioUpdateRequest(name="Updated Name")

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = None
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import update_scenario

            with pytest.raises(HTTPException) as exc_info:
                await update_scenario("nonexistent", update_request, user=admin_user)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_scenario_error_handling(self, admin_user, mock_scenario):
        """Test error handling when updating scenario"""
        update_request = ScenarioUpdateRequest(name="Updated Name")

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = mock_scenario
            mock_manager.save_scenario.side_effect = Exception("Save failed")
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import update_scenario

            with pytest.raises(HTTPException) as exc_info:
                await update_scenario(
                    "test_scenario_1", update_request, user=admin_user
                )

            assert exc_info.value.status_code == 500
            assert "Failed to update scenario" in exc_info.value.detail


class TestDeleteScenarioEndpoint:
    """Test DELETE /scenarios/{scenario_id} endpoint"""

    @pytest.mark.asyncio
    async def test_delete_scenario_success(self, admin_user, mock_scenario):
        """Test successfully deleting a scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = mock_scenario
            mock_manager.delete_scenario = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import delete_scenario

            result = await delete_scenario("test_scenario_1", user=admin_user)

            assert result.status_code == 200
            assert "deleted successfully" in result.body.decode()

            # Verify delete was called
            mock_manager.delete_scenario.assert_called_once_with("test_scenario_1")

    @pytest.mark.asyncio
    async def test_delete_scenario_not_found(self, admin_user):
        """Test deleting non-existent scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = None
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import delete_scenario

            with pytest.raises(HTTPException) as exc_info:
                await delete_scenario("nonexistent", user=admin_user)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_scenario_error_handling(self, admin_user, mock_scenario):
        """Test error handling when deleting scenario"""
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.get_scenario_by_id.return_value = mock_scenario
            mock_manager.delete_scenario.side_effect = Exception("Delete failed")
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import delete_scenario

            with pytest.raises(HTTPException) as exc_info:
                await delete_scenario("test_scenario_1", user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to delete scenario" in exc_info.value.detail


class TestContentConfigEndpoints:
    """Test content configuration endpoints"""

    @pytest.mark.asyncio
    async def test_get_content_config_success(self, admin_user):
        """Test successfully getting content config"""
        from app.api.scenario_management import get_content_config

        result = await get_content_config(user=admin_user)

        assert isinstance(result, ContentProcessingConfigModel)
        assert result.max_video_length_minutes == 60
        assert result.ai_provider_preference == "mistral"
        assert result.enable_auto_flashcards is True

    @pytest.mark.asyncio
    async def test_get_content_config_error_handling(self, admin_user):
        """Test error handling in get_content_config"""
        with patch(
            "app.api.scenario_management.ContentProcessingConfigModel"
        ) as mock_model:
            mock_model.side_effect = Exception("Config load failed")

            from app.api.scenario_management import get_content_config

            with pytest.raises(HTTPException) as exc_info:
                await get_content_config(user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to get content configuration" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_content_config_success(self, admin_user):
        """Test successfully updating content config"""
        config_data = ContentProcessingConfigModel(
            max_video_length_minutes=120,
            ai_provider_preference="openai",
            enable_auto_flashcards=False,
        )

        from app.api.scenario_management import update_content_config

        result = await update_content_config(config_data, user=admin_user)

        assert isinstance(result, ContentProcessingConfigModel)
        assert result.max_video_length_minutes == 120
        assert result.ai_provider_preference == "openai"
        assert result.enable_auto_flashcards is False

    @pytest.mark.asyncio
    async def test_update_content_config_error_handling(self, admin_user):
        """Test error handling in update_content_config"""
        config_data = ContentProcessingConfigModel()

        # Force an exception by patching the logger
        with patch("app.api.scenario_management.logger") as mock_logger:
            mock_logger.info.side_effect = Exception("Logging failed")

            from app.api.scenario_management import update_content_config

            with pytest.raises(HTTPException) as exc_info:
                await update_content_config(config_data, user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to update content configuration" in exc_info.value.detail


class TestBulkOperationsEndpoint:
    """Test POST /scenarios/bulk endpoint"""

    @pytest.mark.asyncio
    async def test_bulk_activate_scenarios(self, admin_user):
        """Test bulk activate operation"""
        bulk_op = BulkScenarioOperation(
            operation="activate", scenario_ids=["scenario1", "scenario2"]
        )

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.set_scenario_active = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import bulk_scenario_operations

            result = await bulk_scenario_operations(bulk_op, user=admin_user)

            assert result.status_code == 200
            response_data = eval(result.body.decode())
            assert response_data["operation"] == "activate"
            assert len(response_data["results"]) == 2
            assert response_data["results"][0]["status"] == "activated"
            assert response_data["results"][1]["status"] == "activated"

            # Verify set_scenario_active was called for each scenario
            assert mock_manager.set_scenario_active.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_deactivate_scenarios(self, admin_user):
        """Test bulk deactivate operation"""
        bulk_op = BulkScenarioOperation(
            operation="deactivate", scenario_ids=["scenario1", "scenario2"]
        )

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.set_scenario_active = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import bulk_scenario_operations

            result = await bulk_scenario_operations(bulk_op, user=admin_user)

            assert result.status_code == 200
            response_data = eval(result.body.decode())
            assert response_data["operation"] == "deactivate"
            assert response_data["results"][0]["status"] == "deactivated"

    @pytest.mark.asyncio
    async def test_bulk_delete_scenarios(self, admin_user):
        """Test bulk delete operation"""
        bulk_op = BulkScenarioOperation(
            operation="delete", scenario_ids=["scenario1", "scenario2"]
        )

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_manager.delete_scenario = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import bulk_scenario_operations

            result = await bulk_scenario_operations(bulk_op, user=admin_user)

            assert result.status_code == 200
            response_data = eval(result.body.decode())
            assert response_data["operation"] == "delete"
            assert response_data["results"][0]["status"] == "deleted"

            # Verify delete_scenario was called for each scenario
            assert mock_manager.delete_scenario.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_export_scenarios(self, admin_user):
        """Test bulk export operation"""
        bulk_op = BulkScenarioOperation(operation="export", scenario_ids=["scenario1"])

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import bulk_scenario_operations

            result = await bulk_scenario_operations(bulk_op, user=admin_user)

            assert result.status_code == 200
            response_data = eval(result.body.decode())
            assert response_data["operation"] == "export"
            assert response_data["results"][0]["status"] == "exported"

    @pytest.mark.asyncio
    async def test_bulk_operations_partial_failure(self, admin_user):
        """Test bulk operation with some failures"""
        bulk_op = BulkScenarioOperation(
            operation="activate", scenario_ids=["good_scenario", "bad_scenario"]
        )

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()

            # First call succeeds, second fails
            def side_effect(scenario_id, active):
                if scenario_id == "bad_scenario":
                    raise Exception("Scenario not found")

            mock_manager.set_scenario_active = AsyncMock(side_effect=side_effect)
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import bulk_scenario_operations

            result = await bulk_scenario_operations(bulk_op, user=admin_user)

            assert result.status_code == 200
            response_data = eval(result.body.decode())
            assert response_data["results"][0]["status"] == "activated"
            assert response_data["results"][1]["status"] == "error"
            assert "error" in response_data["results"][1]

    @pytest.mark.asyncio
    async def test_bulk_operations_error_handling(self, admin_user):
        """Test error handling in bulk operations"""
        bulk_op = BulkScenarioOperation(
            operation="activate", scenario_ids=["scenario1"]
        )

        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_ensure.side_effect = Exception("Manager initialization failed")

            from app.api.scenario_management import bulk_scenario_operations

            with pytest.raises(HTTPException) as exc_info:
                await bulk_scenario_operations(bulk_op, user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to perform bulk operation" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_bulk_operations_invalid_operation(self, admin_user):
        """Test bulk operation with invalid operation type (defensive else branch)"""
        # We need to bypass Pydantic validation to test the else branch
        # Create a mock BulkScenarioOperation with an invalid operation
        with patch(
            "app.api.scenario_management.ensure_scenario_manager_initialized"
        ) as mock_ensure:
            mock_manager = AsyncMock()
            mock_ensure.return_value = mock_manager

            from app.api.scenario_management import bulk_scenario_operations

            # Create a mock object that bypasses Pydantic validation
            mock_bulk_op = Mock()
            mock_bulk_op.operation = "invalid_operation"  # Not in the allowed set
            mock_bulk_op.scenario_ids = ["scenario1"]

            response = await bulk_scenario_operations(mock_bulk_op, user=admin_user)
            response_data = response.body.decode("utf-8")
            import json

            response_data = json.loads(response_data)

            # The else branch should log an error and return error status
            assert response_data["results"][0]["status"] == "error"
            assert response_data["results"][0]["error"] == "Invalid operation"


class TestTemplatesEndpoint:
    """Test GET /templates endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenario_templates_success(self, admin_user):
        """Test successfully getting scenario templates"""
        from app.api.scenario_management import get_scenario_templates

        result = await get_scenario_templates(user=admin_user)

        assert result.status_code == 200
        response_data = eval(result.body.decode())

        # Verify structure
        assert "categories" in response_data
        assert "difficulties" in response_data
        assert "roles" in response_data
        assert "phase_templates" in response_data

        # Verify categories
        assert len(response_data["categories"]) > 0
        assert any(cat["value"] == "restaurant" for cat in response_data["categories"])

        # Verify difficulties
        assert len(response_data["difficulties"]) > 0
        assert any(
            diff["value"] == "beginner" for diff in response_data["difficulties"]
        )

        # Verify roles
        assert len(response_data["roles"]) > 0
        assert any(role["value"] == "customer" for role in response_data["roles"])

        # Verify phase templates
        assert len(response_data["phase_templates"]) == 3
        assert response_data["phase_templates"][0]["name"] == "Introduction"
        assert response_data["phase_templates"][1]["name"] == "Main Interaction"
        assert response_data["phase_templates"][2]["name"] == "Conclusion"

    @pytest.mark.asyncio
    async def test_get_scenario_templates_error_handling(self, admin_user):
        """Test error handling in get_scenario_templates"""
        with patch("app.api.scenario_management.ScenarioCategory") as mock_category:
            mock_category.__iter__.side_effect = Exception("Enum error")

            from app.api.scenario_management import get_scenario_templates

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_templates(user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to get scenario templates" in exc_info.value.detail


class TestStatisticsEndpoint:
    """Test GET /statistics endpoint"""

    @pytest.mark.asyncio
    async def test_get_scenario_statistics_success(self, admin_user):
        """Test successfully getting scenario statistics"""
        from app.api.scenario_management import get_scenario_statistics

        result = await get_scenario_statistics(user=admin_user)

        assert result.status_code == 200
        response_data = eval(result.body.decode())

        # Verify structure
        assert "total_scenarios" in response_data
        assert "active_scenarios" in response_data
        assert "scenarios_by_category" in response_data
        assert "scenarios_by_difficulty" in response_data
        assert "most_popular_scenarios" in response_data
        assert "average_completion_rate" in response_data
        assert "total_sessions" in response_data

        # Verify data types
        assert isinstance(response_data["total_scenarios"], int)
        assert isinstance(response_data["scenarios_by_category"], dict)
        assert isinstance(response_data["most_popular_scenarios"], list)
        assert isinstance(response_data["average_completion_rate"], float)

    @pytest.mark.asyncio
    async def test_get_scenario_statistics_error_handling(self, admin_user):
        """Test error handling in get_scenario_statistics"""
        with patch("app.api.scenario_management.logger") as mock_logger:
            mock_logger.info.side_effect = Exception("Logging failed")

            from app.api.scenario_management import get_scenario_statistics

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario_statistics(user=admin_user)

            assert exc_info.value.status_code == 500
            assert "Failed to get scenario statistics" in exc_info.value.detail


# ===========================
# Helper Function Tests
# ===========================


class TestEnsureScenarioManagerInitialized:
    """Test ensure_scenario_manager_initialized helper"""

    @pytest.mark.asyncio
    async def test_ensure_scenario_manager_initialized(self):
        """Test that scenario manager gets initialized and returned"""
        with patch("app.api.scenario_management.scenario_manager") as mock_sm:
            mock_sm.initialize = AsyncMock()

            from app.api.scenario_management import ensure_scenario_manager_initialized

            result = await ensure_scenario_manager_initialized()

            # Verify initialize was called
            mock_sm.initialize.assert_called_once()
            # Verify the manager itself is returned
            assert result == mock_sm


# ===========================
# Pydantic Model Validation Tests
# ===========================


class TestPydanticModels:
    """Test Pydantic model validations"""

    def test_scenario_model_category_validation(self):
        """Test category validation in ScenarioModel"""
        with pytest.raises(ValueError) as exc_info:
            ScenarioModel(
                scenario_id="test",
                name="Test",
                category="invalid_category",  # Invalid
                difficulty="beginner",
                description="Test",
                user_role="customer",
                ai_role="service_provider",
                setting="Test",
                duration_minutes=30,
                phases=[],
            )

        assert "Category must be one of" in str(exc_info.value)

    def test_scenario_model_difficulty_validation(self):
        """Test difficulty validation in ScenarioModel"""
        with pytest.raises(ValueError) as exc_info:
            ScenarioModel(
                scenario_id="test",
                name="Test",
                category="restaurant",
                difficulty="invalid_difficulty",  # Invalid
                description="Test",
                user_role="customer",
                ai_role="service_provider",
                setting="Test",
                duration_minutes=30,
                phases=[],
            )

        assert "Difficulty must be one of" in str(exc_info.value)

    def test_scenario_model_role_validation(self):
        """Test role validation in ScenarioModel"""
        with pytest.raises(ValueError) as exc_info:
            ScenarioModel(
                scenario_id="test",
                name="Test",
                category="restaurant",
                difficulty="beginner",
                description="Test",
                user_role="invalid_role",  # Invalid
                ai_role="service_provider",
                setting="Test",
                duration_minutes=30,
                phases=[],
            )

        assert "Role must be one of" in str(exc_info.value)
