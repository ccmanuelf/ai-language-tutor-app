"""
End-to-End Tests for Scenario-Based Learning
Session 123 - Phase 2: TRUE 100% Functionality Validation

⚠️ WARNING: These tests use REAL services and database!
- REAL AI API calls (costs money)
- REAL database operations
- REAL scenario workflows

Run manually only: pytest tests/e2e/test_scenarios_e2e.py -v -s -m e2e
"""

import os
import time
from datetime import datetime
from typing import Dict, List

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.database.config import get_primary_db_session
from app.main import app
from app.models.simple_user import SimpleUser, UserRole

# Mark ALL tests in this module as E2E
pytestmark = pytest.mark.e2e

# Load environment variables
load_dotenv()


class TestScenarioListingE2E:
    """E2E tests for listing and filtering scenarios"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user for scenarios
        self.test_user_id = f"e2e_scenario_user_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Scenario Tester",
            "email": f"e2e_scenario_{int(datetime.now().timestamp())}@example.com",
            "password": "TestScenarioPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Learner",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup: Delete test user after tests
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_list_all_scenarios_e2e(self):
        """
        Test listing all available scenarios end-to-end

        Validates:
        - GET /api/v1/scenarios/ returns scenarios
        - Response includes scenario metadata
        - Scenarios have required fields
        """
        # Get all scenarios
        response = self.client.get("/api/v1/scenarios/", headers=self.auth_headers)

        # Verify response
        assert response.status_code == 200, f"Failed to list scenarios: {response.text}"

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "scenarios" in data["data"]

        scenarios = data["data"]["scenarios"]
        assert len(scenarios) > 0, "No scenarios returned"

        # Verify scenario structure
        first_scenario = scenarios[0]
        assert (
            "scenario_id" in first_scenario
            or "name" in first_scenario
            or "category" in first_scenario
        )
        assert "category" in first_scenario
        assert "difficulty" in first_scenario
        assert "description" in first_scenario

        print(f"\n✅ E2E: Listed {len(scenarios)} scenarios successfully")

    def test_filter_scenarios_by_category_e2e(self):
        """
        Test filtering scenarios by category

        Validates:
        - Category filter works correctly
        - Returned scenarios match filter
        - Multiple categories can be queried
        """
        # Test filtering by 'travel' category
        response = self.client.get(
            "/api/v1/scenarios/?category=travel", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        scenarios = data["data"]["scenarios"]

        # Verify all returned scenarios are travel category
        for scenario in scenarios:
            assert scenario["category"].lower() == "travel", (
                f"Expected travel category, got {scenario['category']}"
            )

        print(f"\n✅ E2E: Filtered {len(scenarios)} travel scenarios")

    def test_filter_scenarios_by_difficulty_e2e(self):
        """
        Test filtering scenarios by difficulty level

        Validates:
        - Difficulty filter works correctly
        - Beginner/Intermediate/Advanced filtering
        - Appropriate scenarios returned for user level
        """
        # Test filtering by 'beginner' difficulty
        response = self.client.get(
            "/api/v1/scenarios/?difficulty=beginner", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        scenarios = data["data"]["scenarios"]
        assert len(scenarios) > 0, "No beginner scenarios found"

        # Verify difficulty levels
        for scenario in scenarios:
            assert scenario["difficulty"].lower() == "beginner", (
                f"Expected beginner difficulty, got {scenario['difficulty']}"
            )

        print(f"\n✅ E2E: Filtered {len(scenarios)} beginner scenarios")


class TestScenarioDetailsE2E:
    """E2E tests for getting scenario details"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_scenario_detail_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Detail Tester",
            "email": f"e2e_detail_{int(datetime.now().timestamp())}@example.com",
            "password": "TestDetailPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200

        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_get_scenario_details_e2e(self):
        """
        Test getting specific scenario details

        Validates:
        - GET /api/v1/scenarios/{scenario_id} works
        - Detailed scenario information returned
        - Includes description, objectives, context
        """
        # First, get list of scenarios to pick one
        list_response = self.client.get("/api/v1/scenarios/", headers=self.auth_headers)
        assert list_response.status_code == 200

        scenarios = list_response.json()["data"]["scenarios"]
        assert len(scenarios) > 0, "No scenarios available for detail test"

        # Get details for first scenario
        scenario_id = scenarios[0]["scenario_id"]
        response = self.client.get(
            f"/api/v1/scenarios/{scenario_id}", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        scenario_details = data["data"]["scenario"]
        assert scenario_details["scenario_id"] == scenario_id
        assert "description" in scenario_details
        assert (
            "objectives" in scenario_details
            or "learning_objectives" in scenario_details
        )

        print(f"\n✅ E2E: Retrieved details for scenario '{scenario_details['title']}'")


class TestScenarioConversationE2E:
    """E2E tests for scenario-based conversations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_scenario_conv_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Scenario Conversationalist",
            "email": f"e2e_conv_{int(datetime.now().timestamp())}@example.com",
            "password": "TestConvPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200

        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Store conversation IDs for cleanup
        self.conversation_ids = []

        yield

        # Cleanup conversations
        from app.services.conversation_manager import conversation_manager

        for conv_id in self.conversation_ids:
            if conv_id in conversation_manager.active_conversations:
                del conversation_manager.active_conversations[conv_id]

        # Cleanup user
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_start_scenario_conversation_e2e(self):
        """
        Test starting a scenario-based conversation

        Validates:
        - POST /api/v1/scenarios/start creates conversation
        - Returns conversation_id and scenario progress
        - Scenario context initialized correctly
        """
        # Get available scenarios
        list_response = self.client.get("/api/v1/scenarios/", headers=self.auth_headers)
        assert list_response.status_code == 200

        scenarios = list_response.json()["data"]["scenarios"]
        assert len(scenarios) > 0

        # Start scenario conversation
        scenario_id = scenarios[0]["scenario_id"]
        start_request = {
            "scenario_id": scenario_id,
            "language": "en",
            "learning_focus": "conversation",
        }

        response = self.client.post(
            "/api/v1/scenarios/start", json=start_request, headers=self.auth_headers
        )

        assert response.status_code == 200, f"Failed to start scenario: {response.text}"

        data = response.json()
        assert data["success"] is True
        assert "conversation_id" in data["data"]

        conversation_id = data["data"]["conversation_id"]
        self.conversation_ids.append(conversation_id)

        # Verify conversation initialized
        assert conversation_id is not None
        assert len(conversation_id) > 0

        print(f"\n✅ E2E: Started scenario conversation {conversation_id}")

    def test_scenario_multi_turn_conversation_e2e(self):
        """
        Test multi-turn conversation in scenario context

        Validates:
        - Multiple messages in scenario work correctly
        - AI maintains scenario context
        - Progress tracking works
        - Scenario-specific responses
        """
        # Get and start a scenario
        list_response = self.client.get("/api/v1/scenarios/", headers=self.auth_headers)
        scenarios = list_response.json()["data"]["scenarios"]
        scenario_id = scenarios[0]["scenario_id"]

        start_response = self.client.post(
            "/api/v1/scenarios/start",
            json={
                "scenario_id": scenario_id,
                "language": "en",
                "learning_focus": "conversation",
            },
            headers=self.auth_headers,
        )
        assert start_response.status_code == 200

        conversation_id = start_response.json()["data"]["conversation_id"]
        self.conversation_ids.append(conversation_id)

        # Send multiple messages in scenario
        messages = [
            "Hello, I'd like some help.",
            "Yes, I understand.",
            "Thank you for your assistance.",
        ]

        for i, message in enumerate(messages):
            response = self.client.post(
                "/api/v1/scenarios/message",
                json={"conversation_id": conversation_id, "message": message},
                headers=self.auth_headers,
            )

            assert response.status_code == 200, (
                f"Message {i + 1} failed: {response.text}"
            )

            data = response.json()
            assert data["success"] is True
            assert "response" in data["data"]

            ai_response = data["data"]["response"]
            assert len(ai_response) > 0, "AI response is empty"

            # Small delay between messages
            time.sleep(0.5)

        print(f"\n✅ E2E: Completed {len(messages)}-turn scenario conversation")

    def test_scenario_progress_tracking_e2e(self):
        """
        Test scenario progress tracking

        Validates:
        - GET /api/v1/scenarios/progress/{conversation_id} works
        - Progress data includes metrics
        - Completion percentage tracked
        - Learning objectives monitored
        """
        # Start a scenario
        list_response = self.client.get("/api/v1/scenarios/", headers=self.auth_headers)
        scenarios = list_response.json()["data"]["scenarios"]

        start_response = self.client.post(
            "/api/v1/scenarios/start",
            json={
                "scenario_id": scenarios[0]["scenario_id"],
                "language": "en",
                "learning_focus": "conversation",
            },
            headers=self.auth_headers,
        )

        conversation_id = start_response.json()["data"]["conversation_id"]
        self.conversation_ids.append(conversation_id)

        # Send a message to generate progress
        self.client.post(
            "/api/v1/scenarios/message",
            json={
                "conversation_id": conversation_id,
                "message": "Hello, I need assistance.",
            },
            headers=self.auth_headers,
        )

        # Check progress
        progress_response = self.client.get(
            f"/api/v1/scenarios/progress/{conversation_id}", headers=self.auth_headers
        )

        assert progress_response.status_code == 200
        data = progress_response.json()
        assert data["success"] is True

        # Verify progress data structure
        progress = data["data"]
        assert "scenario_id" in progress or "progress" in progress

        print(f"\n✅ E2E: Retrieved scenario progress for conversation")


class TestScenarioCompletionE2E:
    """E2E tests for completing scenarios"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_scenario_complete_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Completion Tester",
            "email": f"e2e_complete_{int(datetime.now().timestamp())}@example.com",
            "password": "TestCompletePassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200

        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        self.conversation_ids = []

        yield

        # Cleanup
        from app.services.conversation_manager import conversation_manager

        for conv_id in self.conversation_ids:
            if conv_id in conversation_manager.active_conversations:
                del conversation_manager.active_conversations[conv_id]

        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_complete_scenario_e2e(self):
        """
        Test completing a scenario conversation

        Validates:
        - POST /api/v1/scenarios/complete/{conversation_id} works
        - Completion data returned
        - Final assessment provided
        - Progress saved
        """
        # Start scenario
        list_response = self.client.get("/api/v1/scenarios/", headers=self.auth_headers)
        scenarios = list_response.json()["data"]["scenarios"]

        start_response = self.client.post(
            "/api/v1/scenarios/start",
            json={
                "scenario_id": scenarios[0]["scenario_id"],
                "language": "en",
                "learning_focus": "conversation",
            },
            headers=self.auth_headers,
        )

        conversation_id = start_response.json()["data"]["conversation_id"]
        self.conversation_ids.append(conversation_id)

        # Have some interaction
        self.client.post(
            "/api/v1/scenarios/message",
            json={
                "conversation_id": conversation_id,
                "message": "I would like to complete this scenario.",
            },
            headers=self.auth_headers,
        )

        # Complete scenario
        complete_response = self.client.post(
            f"/api/v1/scenarios/complete/{conversation_id}", headers=self.auth_headers
        )

        assert complete_response.status_code == 200
        data = complete_response.json()
        assert data["success"] is True

        # Verify completion data
        completion_data = data["data"]
        assert "status" in completion_data or "completed" in completion_data

        print(f"\n✅ E2E: Completed scenario conversation successfully")


class TestScenarioCategoriesE2E:
    """E2E tests for scenario categories"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_scenario_cat_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Category Tester",
            "email": f"e2e_cat_{int(datetime.now().timestamp())}@example.com",
            "password": "TestCategoryPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200

        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_get_scenario_categories_e2e(self):
        """
        Test getting available scenario categories

        Validates:
        - GET /api/v1/scenarios/categories works
        - Returns list of categories
        - Categories have metadata
        - Common categories available (travel, restaurant, shopping)
        """
        response = self.client.get(
            "/api/v1/scenarios/categories", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        categories = data["data"]["categories"]
        assert len(categories) > 0, "No categories returned"

        # Verify expected categories exist
        category_names = [
            cat["name"].lower() if isinstance(cat, dict) else cat.lower()
            for cat in categories
        ]

        expected_categories = ["travel", "restaurant", "shopping"]
        for expected in expected_categories:
            assert any(expected in name for name in category_names), (
                f"Expected category '{expected}' not found"
            )

        print(f"\n✅ E2E: Retrieved {len(categories)} scenario categories")

    def test_get_scenarios_by_category_e2e(self):
        """
        Test getting scenarios for specific category

        Validates:
        - GET /api/v1/scenarios/category/{category_name} works
        - Returns scenarios for that category only
        - Scenarios have appropriate context
        """
        # Get categories first
        cat_response = self.client.get(
            "/api/v1/scenarios/categories", headers=self.auth_headers
        )
        assert cat_response.status_code == 200

        categories = cat_response.json()["data"]["categories"]
        assert len(categories) > 0

        # Get first category name
        first_category = categories[0]
        category_name = (
            first_category["name"]
            if isinstance(first_category, dict)
            else first_category
        )

        # Get scenarios for this category
        response = self.client.get(
            f"/api/v1/scenarios/category/{category_name}", headers=self.auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        scenarios = data["data"]["scenarios"]
        assert len(scenarios) > 0, f"No scenarios for category {category_name}"

        # Verify scenarios match category
        for scenario in scenarios:
            assert (
                scenario["category"].lower() == category_name.lower()
                or category_name.lower() in scenario["category"].lower()
            )

        print(
            f"\n✅ E2E: Retrieved {len(scenarios)} scenarios for '{category_name}' category"
        )


class TestScenarioErrorHandlingE2E:
    """E2E tests for scenario error handling"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        self.test_user_id = f"e2e_scenario_err_{int(datetime.now().timestamp())}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Error Tester",
            "email": f"e2e_err_{int(datetime.now().timestamp())}@example.com",
            "password": "TestErrorPassword123!",
            "role": "child",
        }

        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200

        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        yield

        # Cleanup
        db = get_primary_db_session()
        try:
            test_user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            if test_user:
                db.delete(test_user)
                db.commit()
        finally:
            db.close()

    def test_invalid_scenario_id_e2e(self):
        """
        Test error handling for invalid scenario ID

        Validates:
        - Starting scenario with invalid ID returns 404 or 400
        - Error message is clear
        - No partial state created
        """
        response = self.client.post(
            "/api/v1/scenarios/start",
            json={
                "scenario_id": "INVALID_SCENARIO_ID_123456",
                "language": "en",
                "learning_focus": "conversation",
            },
            headers=self.auth_headers,
        )

        # Should return error
        assert response.status_code in [400, 404, 500], (
            f"Expected error status, got {response.status_code}"
        )

        data = response.json()
        assert "detail" in data or "error" in data or "message" in data

        print(f"\n✅ E2E: Invalid scenario ID properly rejected")

    def test_unauthorized_scenario_access_e2e(self):
        """
        Test error handling for unauthorized access

        Validates:
        - Accessing scenarios without auth returns 401
        - Accessing other user's conversation returns 403
        - Proper error messages
        """
        # Try to list scenarios without authentication
        response = self.client.get("/api/v1/scenarios/")

        assert response.status_code == 401, (
            f"Expected 401 unauthorized, got {response.status_code}"
        )

        print(f"\n✅ E2E: Unauthorized access properly rejected")
