"""
Integration Tests for Scenario Management API
app/api/scenario_management.py

Session 84 - Target: TRUE 100% coverage with FastAPI TestClient
Following the proven pattern from test_api_conversations.py
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.database.config import get_primary_db_session
from app.main import app
from app.models.simple_user import SimpleUser, UserRole
from app.services.admin_auth import AdminPermission, require_admin_access
from app.services.auth import get_current_user
from app.services.scenario_manager import (
    ConversationRole,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioManager,
    ScenarioPhase,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(autouse=True, scope="function")
def enable_admin_test_mode():
    """Enable test mode for admin auth service - runs automatically for all tests in this module"""
    from app.services.admin_auth import admin_auth_service

    # Only enable if not already enabled
    was_enabled = admin_auth_service._test_mode
    if not was_enabled:
        admin_auth_service.enable_test_mode()

    yield

    # Only disable if we enabled it
    if not was_enabled:
        admin_auth_service.disable_test_mode()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def admin_user():
    """Create a sample admin user"""
    user = SimpleUser(
        id=1,
        user_id="admin123",
        username="admin_test",
        email="admin@test.com",
        role=UserRole.ADMIN,
    )
    return user


@pytest.fixture
def admin_user_dict():
    """Create admin user dict for get_current_user override"""
    return {
        "user_id": "admin123",
        "username": "admin_test",
        "email": "admin@test.com",
        "role": "admin",
    }


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
def mock_scenario_manager():
    """Create mock scenario manager"""
    manager = AsyncMock(spec=ScenarioManager)
    return manager


@pytest.fixture
def sample_scenario():
    """Create a sample conversation scenario"""
    phases = [
        ScenarioPhase(
            phase_id="phase1",
            name="Greeting Phase",
            description="Initial greeting and seating",
            expected_duration_minutes=3,
            key_vocabulary=["hello", "welcome", "table", "menu"],
            essential_phrases=["Buongiorno", "Una tavola per due"],
            learning_objectives=["Greet the staff", "Request a table"],
            cultural_notes="In Italy, greetings are important",
            success_criteria=["Successfully greet", "Get seated"],
        )
    ]
    scenario = ConversationScenario(
        scenario_id="test_scenario_1",
        name="Test Restaurant Scenario",
        category=ScenarioCategory.RESTAURANT,
        difficulty=ScenarioDifficulty.BEGINNER,
        description="Ordering food at an Italian restaurant in Rome",
        user_role=ConversationRole.CUSTOMER,
        ai_role=ConversationRole.SERVICE_PROVIDER,
        setting="A busy Italian restaurant in Rome",
        duration_minutes=15,
        phases=phases,
        vocabulary_focus=["menu", "pasta", "wine", "bill"],
        cultural_context='{"customs": "Italian dining etiquette", "formality": "casual"}',
        learning_goals=["Order food", "Ask questions", "Request the bill"],
    )
    scenario.is_active = True
    scenario.created_at = datetime(2024, 1, 1, 12, 0, 0)
    scenario.updated_at = datetime(2024, 1, 2, 12, 0, 0)
    return scenario


@pytest.fixture
def sample_scenarios_list(sample_scenario):
    """Create a list of sample scenarios"""
    # Active scenario
    scenario1 = sample_scenario

    # Inactive scenario
    scenario2 = ConversationScenario(
        scenario_id="test_scenario_2",
        name="Hotel Check-in",
        category=ScenarioCategory.TRAVEL,
        difficulty=ScenarioDifficulty.INTERMEDIATE,
        description="Checking in at a hotel reception in Paris",
        user_role=ConversationRole.CUSTOMER,
        ai_role=ConversationRole.SERVICE_PROVIDER,
        setting="Hotel reception in Paris",
        duration_minutes=10,
        phases=[],
        vocabulary_focus=["reservation", "room", "key"],
        cultural_context="{}",
        learning_goals=["Check in", "Ask about facilities"],
    )
    scenario2.is_active = False
    scenario2.created_at = datetime(2024, 1, 3, 12, 0, 0)
    scenario2.updated_at = datetime(2024, 1, 4, 12, 0, 0)

    # Different category scenario
    scenario3 = ConversationScenario(
        scenario_id="test_scenario_3",
        name="Shopping at Market",
        category=ScenarioCategory.SHOPPING,
        difficulty=ScenarioDifficulty.BEGINNER,
        description="Buying groceries at a local market in Barcelona",
        user_role=ConversationRole.CUSTOMER,
        ai_role=ConversationRole.SERVICE_PROVIDER,
        setting="Local market in Barcelona",
        duration_minutes=12,
        phases=[],
        vocabulary_focus=["vegetables", "fruit", "price"],
        cultural_context='{"market_culture": "Spanish bargaining customs"}',
        learning_goals=["Buy groceries", "Negotiate prices"],
    )
    scenario3.is_active = True
    scenario3.created_at = datetime(2024, 1, 5, 12, 0, 0)
    scenario3.updated_at = datetime(2024, 1, 6, 12, 0, 0)

    return [scenario1, scenario2, scenario3]


@pytest.fixture
def content_config():
    """Create a sample content processing config as dict"""
    return {
        "max_video_length_minutes": 60,
        "ai_provider_preference": "mistral",
        "enable_auto_flashcards": True,
        "enable_auto_quizzes": True,
        "enable_auto_summaries": True,
        "max_flashcards_per_content": 20,
        "max_quiz_questions": 10,
        "summary_length_preference": "medium",
        "language_detection_enabled": True,
        "content_quality_threshold": 0.7,
        "enable_content_moderation": True,
    }


# ============================================================================
# Helper function to override dependencies
# ============================================================================


def override_deps(client, mock_db, admin_user, mock_scenario_manager):
    """Override FastAPI dependencies for testing"""
    app.dependency_overrides[get_primary_db_session] = lambda: mock_db
    app.dependency_overrides[require_admin_access] = lambda: admin_user

    # Patch the scenario_manager service
    with patch("app.api.scenario_management.scenario_manager", mock_scenario_manager):
        yield

    # Clear overrides after test
    app.dependency_overrides.clear()


# ============================================================================
# TEST CLASS 1: List Scenarios Endpoint
# ============================================================================


class TestListScenariosEndpoint:
    """Test GET /api/admin/scenario-management/scenarios"""

    def test_list_all_scenarios(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenarios_list
    ):
        """Test listing all scenarios without filters"""
        mock_scenario_manager.get_all_scenarios.return_value = sample_scenarios_list

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get("/api/admin/scenario-management/scenarios")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Only active scenarios returned by default
        assert data[0]["scenario_id"] == "test_scenario_1"
        assert data[0]["name"] == "Test Restaurant Scenario"

        mock_scenario_manager.get_all_scenarios.assert_called_once()

    def test_list_scenarios_filter_by_category(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenarios_list
    ):
        """Test filtering scenarios by category"""
        mock_scenario_manager.get_all_scenarios.return_value = sample_scenarios_list

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/scenarios?category=restaurant"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Only restaurant scenario should be returned after filtering
        assert len(data) == 1
        assert data[0]["category"] == "restaurant"

    def test_list_scenarios_filter_by_difficulty(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenarios_list
    ):
        """Test filtering scenarios by difficulty"""
        mock_scenario_manager.get_all_scenarios.return_value = sample_scenarios_list

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/scenarios?difficulty=beginner"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Two beginner scenarios should be returned
        assert len(data) == 2
        for scenario in data:
            assert scenario["difficulty"] == "beginner"

    def test_list_scenarios_filter_active_only(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenarios_list
    ):
        """Test filtering for active scenarios only"""
        mock_scenario_manager.get_all_scenarios.return_value = sample_scenarios_list

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/scenarios?active_only=true"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Two active scenarios
        assert len(data) == 2
        for scenario in data:
            assert scenario["is_active"] is True

    def test_list_scenarios_combined_filters(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenarios_list
    ):
        """Test combining multiple filters"""
        mock_scenario_manager.get_all_scenarios.return_value = sample_scenarios_list

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/scenarios"
                "?category=restaurant&difficulty=beginner&active_only=true"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "restaurant"
        assert data[0]["difficulty"] == "beginner"
        assert data[0]["is_active"] is True


# ============================================================================
# TEST CLASS 2: Get Single Scenario Endpoint
# ============================================================================


class TestGetScenarioEndpoint:
    """Test GET /api/admin/scenario-management/scenarios/{scenario_id}"""

    def test_get_scenario_success(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenario
    ):
        """Test getting a scenario by ID"""
        mock_scenario_manager.get_scenario_by_id.return_value = sample_scenario

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/scenarios/test_scenario_1"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "test_scenario_1"
        assert data["name"] == "Test Restaurant Scenario"
        assert len(data["phases"]) == 1

    def test_get_scenario_not_found(
        self, client, mock_db, admin_user, mock_scenario_manager
    ):
        """Test getting a non-existent scenario"""
        mock_scenario_manager.get_scenario_by_id.return_value = None

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/scenarios/nonexistent"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============================================================================
# TEST CLASS 3: Create Scenario Endpoint
# ============================================================================


class TestCreateScenarioEndpoint:
    """Test POST /api/admin/scenario-management/scenarios"""

    def test_create_scenario_success(
        self,
        client,
        mock_db,
        admin_user,
        admin_user_dict,
        mock_scenario_manager,
        sample_scenario,
    ):
        """Test creating a new scenario"""
        mock_scenario_manager.save_scenario.return_value = sample_scenario

        create_data = {
            "name": "Test Restaurant Scenario",
            "category": "restaurant",
            "difficulty": "beginner",
            "description": "Practice ordering food at an Italian restaurant",
            "user_role": "customer",
            "ai_role": "service_provider",
            "setting": "A busy Italian restaurant in Rome",
            "duration_minutes": 15,
            "vocabulary_focus": ["menu", "pasta"],
            "cultural_context": "Italian dining customs",
            "phases": [
                {
                    "phase_id": "phase1",
                    "name": "Greeting Phase",
                    "description": "Initial greeting and seating",
                    "expected_duration_minutes": 3,
                    "key_vocabulary": ["hello", "welcome"],
                    "essential_phrases": ["Buongiorno"],
                    "learning_objectives": ["Greet the staff"],
                }
            ],
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        # Patch has_permission in the module where require_permission will call it
        with patch(
            "app.services.admin_auth.AdminAuthService.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.post(
                    "/api/admin/scenario-management/scenarios",
                    json=create_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200  # Endpoint returns 200, not 201
        data = response.json()
        assert "scenario_id" in data
        assert data["name"] == "Test Restaurant Scenario"

        mock_scenario_manager.save_scenario.assert_called_once()

    def test_create_scenario_validation_error(
        self, client, mock_db, admin_user, admin_user_dict, mock_scenario_manager
    ):
        """Test creating a scenario with invalid data"""
        invalid_data = {
            "name": "Test",
            # Missing required fields
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.post(
                    "/api/admin/scenario-management/scenarios",
                    json=invalid_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 422  # Validation error


# ============================================================================
# TEST CLASS 4: Update Scenario Endpoint
# ============================================================================


class TestUpdateScenarioEndpoint:
    """Test PUT /api/admin/scenario-management/scenarios/{scenario_id}"""

    def test_update_scenario_success(
        self,
        client,
        mock_db,
        admin_user,
        admin_user_dict,
        mock_scenario_manager,
        sample_scenario,
    ):
        """Test updating an existing scenario"""
        mock_scenario_manager.get_scenario_by_id.return_value = sample_scenario
        mock_scenario_manager.save_scenario.return_value = sample_scenario

        update_data = {
            "name": "Updated Restaurant Scenario",
            "difficulty": "intermediate",
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.put(
                    "/api/admin/scenario-management/scenarios/test_scenario_1",
                    json=update_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        mock_scenario_manager.save_scenario.assert_called_once()

    def test_update_scenario_not_found(
        self, client, mock_db, admin_user, admin_user_dict, mock_scenario_manager
    ):
        """Test updating a non-existent scenario"""
        mock_scenario_manager.get_scenario_by_id.return_value = None

        update_data = {"name": "Updated Name"}

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.put(
                    "/api/admin/scenario-management/scenarios/nonexistent",
                    json=update_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 404

    def test_update_scenario_with_phases(
        self,
        client,
        mock_db,
        admin_user,
        admin_user_dict,
        mock_scenario_manager,
        sample_scenario,
    ):
        """Test updating scenario phases"""
        mock_scenario_manager.get_scenario_by_id.return_value = sample_scenario
        mock_scenario_manager.save_scenario.return_value = sample_scenario

        update_data = {
            "phases": [
                {
                    "phase_id": "phase1",
                    "name": "Updated Phase",
                    "description": "Updated greeting phase",
                    "expected_duration_minutes": 5,
                    "key_vocabulary": ["new", "words"],
                    "essential_phrases": ["Ciao"],
                    "learning_objectives": ["New objective"],
                }
            ]
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.put(
                    "/api/admin/scenario-management/scenarios/test_scenario_1",
                    json=update_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200


# ============================================================================
# TEST CLASS 5: Delete Scenario Endpoint
# ============================================================================


class TestDeleteScenarioEndpoint:
    """Test DELETE /api/admin/scenario-management/scenarios/{scenario_id}"""

    def test_delete_scenario_success(
        self,
        client,
        mock_db,
        admin_user,
        admin_user_dict,
        mock_scenario_manager,
        sample_scenario,
    ):
        """Test deleting a scenario"""
        mock_scenario_manager.get_scenario_by_id.return_value = sample_scenario
        mock_scenario_manager.delete_scenario.return_value = True

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.delete(
                    "/api/admin/scenario-management/scenarios/test_scenario_1"
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_delete_scenario_not_found(
        self, client, mock_db, admin_user, admin_user_dict, mock_scenario_manager
    ):
        """Test deleting a non-existent scenario"""
        mock_scenario_manager.get_scenario_by_id.return_value = None

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.delete(
                    "/api/admin/scenario-management/scenarios/nonexistent"
                )

        app.dependency_overrides.clear()

        assert response.status_code == 404


# ============================================================================
# TEST CLASS 6: Content Config Endpoints
# ============================================================================


class TestContentConfigEndpoints:
    """Test content processing configuration endpoints"""

    def test_get_content_config(self, client, mock_db, admin_user):
        """Test GET /api/admin/scenario-management/content-config"""
        # Endpoint returns default config, doesn't use scenario_manager
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        response = client.get("/api/admin/scenario-management/content-config")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Check for expected fields in default config
        assert "enable_auto_flashcards" in data
        assert "enable_auto_quizzes" in data
        assert "max_video_length_minutes" in data

    def test_update_content_config(
        self,
        client,
        mock_db,
        admin_user,
        admin_user_dict,
    ):
        """Test PUT /api/admin/scenario-management/content-config"""
        # Endpoint just validates and returns the provided config
        update_data = {
            "max_video_length_minutes": 120,
            "enable_auto_flashcards": False,
            "enable_auto_quizzes": True,
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            response = client.put(
                "/api/admin/scenario-management/content-config",
                json=update_data,
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["max_video_length_minutes"] == 120
        assert data["enable_auto_flashcards"] is False


# ============================================================================
# TEST CLASS 7: Bulk Operations Endpoint
# ============================================================================


class TestBulkOperationsEndpoint:
    """Test POST /api/admin/scenario-management/scenarios/bulk"""

    def test_bulk_activate(
        self, client, mock_db, admin_user, admin_user_dict, mock_scenario_manager
    ):
        """Test bulk activating scenarios"""
        # Mock the actual method used by the endpoint
        mock_scenario_manager.set_scenario_active = AsyncMock()

        bulk_data = {
            "scenario_ids": ["id1", "id2", "id3"],
            "operation": "activate",
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.post(
                    "/api/admin/scenario-management/scenarios/bulk",
                    json=bulk_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "activate"
        assert len(data["results"]) == 3
        assert all(r["status"] == "activated" for r in data["results"])

    def test_bulk_deactivate(
        self, client, mock_db, admin_user, admin_user_dict, mock_scenario_manager
    ):
        """Test bulk deactivating scenarios"""
        # Mock the actual method used by the endpoint
        mock_scenario_manager.set_scenario_active = AsyncMock()

        bulk_data = {
            "scenario_ids": ["id1", "id2", "id3"],
            "operation": "deactivate",
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.post(
                    "/api/admin/scenario-management/scenarios/bulk",
                    json=bulk_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "deactivate"
        assert len(data["results"]) == 3

    def test_bulk_delete(
        self, client, mock_db, admin_user, admin_user_dict, mock_scenario_manager
    ):
        """Test bulk deleting scenarios"""
        # Mock the actual method used by the endpoint
        mock_scenario_manager.delete_scenario = AsyncMock()

        bulk_data = {
            "scenario_ids": ["id1", "id2"],
            "operation": "delete",
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.post(
                    "/api/admin/scenario-management/scenarios/bulk",
                    json=bulk_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "delete"
        assert len(data["results"]) == 2

    def test_bulk_export(
        self,
        client,
        mock_db,
        admin_user,
        admin_user_dict,
        mock_scenario_manager,
    ):
        """Test bulk exporting scenarios"""
        # Export operation doesn't use scenario_manager methods currently
        bulk_data = {
            "scenario_ids": ["id1", "id2", "id3"],
            "operation": "export",
        }

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user
        app.dependency_overrides[get_current_user] = lambda: admin_user_dict

        with patch(
            "app.services.admin_auth.admin_auth_service.has_permission",
            return_value=True,
        ):
            with patch(
                "app.api.scenario_management.scenario_manager", mock_scenario_manager
            ):
                response = client.post(
                    "/api/admin/scenario-management/scenarios/bulk",
                    json=bulk_data,
                )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "export"
        assert len(data["results"]) == 3


# ============================================================================
# TEST CLASS 8: Templates Endpoint
# ============================================================================


class TestTemplatesEndpoint:
    """Test GET /api/admin/scenario-management/templates"""

    def test_get_templates_all(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenarios_list
    ):
        """Test getting all templates"""
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get("/api/admin/scenario-management/templates")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Response contains 4 keys: categories, difficulties, roles, phase_templates
        assert len(data) == 4
        assert "categories" in data
        assert "difficulties" in data
        assert "roles" in data
        assert "phase_templates" in data
        assert len(data["phase_templates"]) == 3

    def test_get_templates_by_category(
        self, client, mock_db, admin_user, mock_scenario_manager, sample_scenario
    ):
        """Test getting templates - category filter doesn't affect template structure"""

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get(
                "/api/admin/scenario-management/templates?category=restaurant"
            )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Templates endpoint ignores category parameter and returns all templates
        assert len(data) == 4
        assert "categories" in data


# ============================================================================
# TEST CLASS 9: Statistics Endpoint
# ============================================================================


class TestStatisticsEndpoint:
    """Test GET /api/admin/scenario-management/statistics"""

    def test_get_statistics(self, client, mock_db, admin_user, mock_scenario_manager):
        """Test getting scenario statistics"""

        app.dependency_overrides[get_primary_db_session] = lambda: mock_db
        app.dependency_overrides[require_admin_access] = lambda: admin_user

        with patch(
            "app.api.scenario_management.scenario_manager", mock_scenario_manager
        ):
            response = client.get("/api/admin/scenario-management/statistics")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        # Endpoint returns hardcoded statistics
        assert data["total_scenarios"] == 15
        assert data["active_scenarios"] == 12
        assert "scenarios_by_category" in data
        assert "scenarios_by_difficulty" in data
        assert data["scenarios_by_category"]["restaurant"] == 4
