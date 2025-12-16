"""
End-to-End Tests for Visual Learning
Session 125 - Phase 2: TRUE 100% Functionality Validation

⚠️ WARNING: These tests use REAL services and database!
- REAL visual learning services
- REAL database operations
- REAL file storage

Complete end-to-end validation of visual learning features:
- Grammar flowcharts
- Progress visualizations
- Visual vocabulary tools
- Pronunciation guides

Run manually only: pytest tests/e2e/test_visual_e2e.py -v -s -m e2e
"""

import os
import random
import time
from datetime import datetime
from typing import Dict

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.database.config import get_primary_db_session
from app.main import app
from app.models.simple_user import SimpleUser

# Mark ALL tests in this module as E2E
pytestmark = pytest.mark.e2e

# Load environment variables
load_dotenv()


# ==================== Grammar Flowchart Tests ====================


class TestGrammarFlowchartsE2E:
    """
    E2E tests for grammar flowchart functionality

    Tests the complete workflow:
    1. Create flowchart
    2. Add nodes
    3. Connect nodes
    4. Retrieve and validate structure
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_visual_user_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Visual Tester",
            "email": f"e2e_visual_{int(datetime.now().timestamp())}@example.com",
            "password": "TestVisualPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Tester",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
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

    def test_complete_flowchart_creation_workflow_e2e(self):
        """
        E2E Test: Complete grammar flowchart creation and retrieval workflow

        Validates:
        - Flowchart creation with valid data
        - Node addition with examples
        - Node connection logic
        - Complete flowchart retrieval
        - Data integrity throughout workflow
        """
        # Step 1: Create a grammar flowchart
        flowchart_data = {
            "concept": "verb_conjugation",
            "title": "Spanish Present Tense Conjugation",
            "description": "Learn how to conjugate regular verbs in Spanish present tense",
            "language": "es",
            "difficulty_level": 2,
            "learning_outcomes": [
                "Conjugate -ar verbs",
                "Conjugate -er verbs",
                "Conjugate -ir verbs",
            ],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts",
            json=flowchart_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Flowchart creation failed: {response.text}"
        )
        create_result = response.json()
        assert create_result["status"] == "success"
        assert "flowchart_id" in create_result
        flowchart_id = create_result["flowchart_id"]

        # Step 2: Add start node
        start_node_data = {
            "flowchart_id": flowchart_id,
            "title": "Start: Verb Conjugation",
            "description": "Begin learning verb conjugation",
            "node_type": "start",
            "content": "Welcome to Spanish verb conjugation",
            "examples": [],
            "position": [0, 0],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts/nodes",
            json=start_node_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Start node creation failed: {response.text}"
        )
        start_result = response.json()
        assert start_result["status"] == "success"
        assert "node_id" in start_result
        start_node_id = start_result["node_id"]

        # Step 3: Add decision node
        decision_node_data = {
            "flowchart_id": flowchart_id,
            "title": "Choose Verb Type",
            "description": "Select the verb ending type",
            "node_type": "decision",
            "content": "What type of verb are you conjugating?",
            "examples": ["-ar verbs", "-er verbs", "-ir verbs"],
            "position": [1, 0],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts/nodes",
            json=decision_node_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Decision node creation failed: {response.text}"
        )
        decision_result = response.json()
        assert decision_result["status"] == "success"
        decision_node_id = decision_result["node_id"]

        # Step 4: Add process node for -ar verbs
        process_node_data = {
            "flowchart_id": flowchart_id,
            "title": "-ar Verb Conjugation",
            "description": "Conjugate -ar verbs in present tense",
            "node_type": "process",
            "content": "Remove -ar and add: o, as, a, amos, áis, an",
            "examples": [
                "hablar → hablo, hablas, habla",
                "cantar → canto, cantas, canta",
            ],
            "position": [2, 0],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts/nodes",
            json=process_node_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Process node creation failed: {response.text}"
        )
        process_result = response.json()
        assert process_result["status"] == "success"
        process_node_id = process_result["node_id"]

        # Step 5: Connect nodes
        connection1_data = {
            "flowchart_id": flowchart_id,
            "from_node_id": start_node_id,
            "to_node_id": decision_node_id,
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts/connections",
            json=connection1_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, f"Connection 1 failed: {response.text}"
        assert response.json()["status"] == "success"

        connection2_data = {
            "flowchart_id": flowchart_id,
            "from_node_id": decision_node_id,
            "to_node_id": process_node_id,
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts/connections",
            json=connection2_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, f"Connection 2 failed: {response.text}"
        assert response.json()["status"] == "success"

        # Step 6: Retrieve complete flowchart and validate
        response = self.client.get(f"/api/visual-learning/flowcharts/{flowchart_id}")
        assert response.status_code == 200, (
            f"Flowchart retrieval failed: {response.text}"
        )
        flowchart = response.json()

        # Validate flowchart structure
        assert flowchart["flowchart_id"] == flowchart_id
        assert flowchart["concept"] == "verb_conjugation"
        assert flowchart["title"] == "Spanish Present Tense Conjugation"
        assert flowchart["language"] == "es"
        assert flowchart["difficulty_level"] == 2
        assert len(flowchart["nodes"]) == 3
        assert len(flowchart["connections"]) == 2
        assert len(flowchart["learning_outcomes"]) == 3

        # Validate nodes
        nodes_by_id = {node["node_id"]: node for node in flowchart["nodes"]}
        assert start_node_id in nodes_by_id
        assert decision_node_id in nodes_by_id
        assert process_node_id in nodes_by_id

        # Validate start node
        start_node = nodes_by_id[start_node_id]
        assert start_node["node_type"] == "start"
        assert start_node["title"] == "Start: Verb Conjugation"
        assert decision_node_id in start_node["next_nodes"]

        # Validate decision node
        decision_node = nodes_by_id[decision_node_id]
        assert decision_node["node_type"] == "decision"
        assert len(decision_node["examples"]) == 3
        assert process_node_id in decision_node["next_nodes"]

        # Validate process node
        process_node = nodes_by_id[process_node_id]
        assert process_node["node_type"] == "process"
        assert len(process_node["examples"]) == 2
        assert "hablar" in process_node["examples"][0]

        # Validate connections
        assert [start_node_id, decision_node_id] in flowchart["connections"]
        assert [decision_node_id, process_node_id] in flowchart["connections"]

    def test_list_flowcharts_with_filtering_e2e(self):
        """
        E2E Test: List flowcharts with language and concept filtering

        Validates:
        - Creating multiple flowcharts
        - Listing all flowcharts
        - Filtering by language
        - Filtering by concept
        - Response structure
        """
        # Create flowchart 1: Spanish verb conjugation
        flowchart1_data = {
            "concept": "verb_conjugation",
            "title": "Spanish Verb Conjugation",
            "description": "Spanish verb conjugation guide",
            "language": "es",
            "difficulty_level": 2,
            "learning_outcomes": ["Conjugate Spanish verbs"],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts",
            json=flowchart1_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Flowchart 1 creation failed: {response.text}"
        )

        # Create flowchart 2: French sentence structure
        flowchart2_data = {
            "concept": "sentence_structure",
            "title": "French Sentence Structure",
            "description": "Learn French sentence structure",
            "language": "fr",
            "difficulty_level": 3,
            "learning_outcomes": ["Build French sentences"],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts",
            json=flowchart2_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Flowchart 2 creation failed: {response.text}"
        )

        # List all flowcharts
        response = self.client.get("/api/visual-learning/flowcharts")
        assert response.status_code == 200, f"Flowchart listing failed: {response.text}"
        result = response.json()
        assert result["status"] == "success"
        assert result["count"] >= 2  # At least our 2 test flowcharts
        assert len(result["flowcharts"]) >= 2

        # Filter by language (Spanish)
        response = self.client.get("/api/visual-learning/flowcharts?language=es")
        assert response.status_code == 200, f"Spanish filter failed: {response.text}"
        result = response.json()
        assert result["status"] == "success"
        spanish_flowcharts = [f for f in result["flowcharts"] if f["language"] == "es"]
        assert len(spanish_flowcharts) >= 1

        # Filter by concept (verb_conjugation)
        response = self.client.get(
            "/api/visual-learning/flowcharts?concept=verb_conjugation"
        )
        assert response.status_code == 200, f"Concept filter failed: {response.text}"
        result = response.json()
        assert result["status"] == "success"
        verb_flowcharts = [
            f for f in result["flowcharts"] if f["concept"] == "verb_conjugation"
        ]
        assert len(verb_flowcharts) >= 1

    def test_flowchart_error_handling_e2e(self):
        """
        E2E Test: Error handling for invalid flowchart operations

        Validates:
        - Invalid concept type rejection
        - Missing flowchart handling
        - Invalid node data handling
        """
        # Test 1: Invalid concept type
        invalid_concept_data = {
            "concept": "invalid_concept_type",
            "title": "Test Flowchart",
            "description": "Test description",
            "language": "en",
            "difficulty_level": 1,
            "learning_outcomes": [],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts",
            json=invalid_concept_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 400
        assert "Invalid concept type" in response.json()["detail"]

        # Test 2: Add node to non-existent flowchart
        node_data = {
            "flowchart_id": "non_existent_flowchart_id",
            "title": "Test Node",
            "description": "Test description",
            "node_type": "start",
            "content": "Test content",
            "examples": [],
            "position": [0, 0],
        }

        response = self.client.post(
            "/api/visual-learning/flowcharts/nodes",
            json=node_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Test 3: Get non-existent flowchart
        response = self.client.get("/api/visual-learning/flowcharts/non_existent_id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ==================== Progress Visualization Tests ====================


class TestProgressVisualizationsE2E:
    """
    E2E tests for progress visualization functionality

    Tests complete visualization workflow:
    1. Create visualizations
    2. Retrieve by user
    3. Filter by type
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_viz_user_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Viz Tester",
            "email": f"e2e_viz_{int(datetime.now().timestamp())}@example.com",
            "password": "TestVizPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Viz",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
        auth_data = response.json()
        self.auth_token = auth_data["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Get actual user ID from database
        db = get_primary_db_session()
        try:
            user = (
                db.query(SimpleUser)
                .filter(SimpleUser.user_id == self.test_user_id)
                .first()
            )
            assert user is not None, "User not found after registration"
            self.user_id = str(user.id)
        finally:
            db.close()

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

    def test_create_and_retrieve_visualizations_e2e(self):
        """
        E2E Test: Create and retrieve progress visualizations

        Validates:
        - Creating visualization with data points
        - Retrieving user visualizations
        - Data integrity
        - Multiple visualization types
        """
        # Create bar chart visualization
        bar_chart_data = {
            "user_id": self.user_id,
            "visualization_type": "bar_chart",
            "title": "Weekly Progress",
            "description": "Words learned per week",
            "data_points": [
                {"week": "Week 1", "words": 50},
                {"week": "Week 2", "words": 75},
                {"week": "Week 3", "words": 100},
                {"week": "Week 4", "words": 90},
            ],
            "x_axis_label": "Week",
            "y_axis_label": "Words Learned",
            "color_scheme": ["#6366f1", "#0891b2", "#f59e0b"],
        }

        response = self.client.post(
            "/api/visual-learning/visualizations",
            json=bar_chart_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Bar chart creation failed: {response.text}"
        )
        result = response.json()
        assert result["status"] == "success"
        assert "visualization_id" in result
        bar_chart_id = result["visualization_id"]

        # Create line chart visualization
        line_chart_data = {
            "user_id": self.user_id,
            "visualization_type": "line_chart",
            "title": "Fluency Score Over Time",
            "description": "Track your fluency improvement",
            "data_points": [
                {"month": "Jan", "score": 60},
                {"month": "Feb", "score": 65},
                {"month": "Mar", "score": 72},
                {"month": "Apr", "score": 78},
            ],
            "x_axis_label": "Month",
            "y_axis_label": "Fluency Score",
        }

        response = self.client.post(
            "/api/visual-learning/visualizations",
            json=line_chart_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Line chart creation failed: {response.text}"
        )
        assert response.json()["status"] == "success"

        # Retrieve all user visualizations
        response = self.client.get(
            f"/api/visual-learning/visualizations/user/{self.user_id}",
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Visualization retrieval failed: {response.text}"
        )
        result = response.json()
        assert result["status"] == "success"
        assert result["count"] >= 2
        assert len(result["visualizations"]) >= 2

        # Validate bar chart data
        bar_charts = [
            v
            for v in result["visualizations"]
            if v["visualization_type"] == "bar_chart"
        ]
        assert len(bar_charts) >= 1
        bar_chart = next(
            (v for v in bar_charts if v["visualization_id"] == bar_chart_id), None
        )
        assert bar_chart is not None
        assert bar_chart["title"] == "Weekly Progress"
        assert len(bar_chart["data_points"]) == 4
        assert bar_chart["x_axis_label"] == "Week"
        assert bar_chart["y_axis_label"] == "Words Learned"
        assert len(bar_chart["color_scheme"]) == 3

    def test_multi_type_visualizations_e2e(self):
        """
        E2E Test: Multiple visualization types support

        Validates:
        - Creating different visualization types
        - Type-specific filtering
        - Correct type handling
        """
        # Create pie chart
        pie_chart_data = {
            "user_id": self.user_id,
            "visualization_type": "pie_chart",
            "title": "Learning Time Distribution",
            "description": "How you spend your learning time",
            "data_points": [
                {"category": "Vocabulary", "percentage": 40},
                {"category": "Grammar", "percentage": 30},
                {"category": "Conversation", "percentage": 20},
                {"category": "Pronunciation", "percentage": 10},
            ],
        }

        response = self.client.post(
            "/api/visual-learning/visualizations",
            json=pie_chart_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Pie chart creation failed: {response.text}"
        )

        # Create progress bar
        progress_bar_data = {
            "user_id": self.user_id,
            "visualization_type": "progress_bar",
            "title": "Course Completion",
            "description": "Your progress through the course",
            "data_points": [{"module": "Spanish Basics", "completion": 85}],
        }

        response = self.client.post(
            "/api/visual-learning/visualizations",
            json=progress_bar_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Progress bar creation failed: {response.text}"
        )

        # Filter by visualization type (pie_chart)
        response = self.client.get(
            f"/api/visual-learning/visualizations/user/{self.user_id}?visualization_type=pie_chart",
            headers=self.auth_headers,
        )
        assert response.status_code == 200, f"Pie chart filter failed: {response.text}"
        result = response.json()
        assert result["status"] == "success"
        # All returned visualizations should be pie charts
        for viz in result["visualizations"]:
            assert viz["visualization_type"] == "pie_chart"

    def test_visualization_error_handling_e2e(self):
        """
        E2E Test: Error handling for visualizations

        Validates:
        - Invalid visualization type rejection
        - Invalid filter type handling
        """
        # Test invalid visualization type
        invalid_viz_data = {
            "user_id": self.user_id,
            "visualization_type": "invalid_type",
            "title": "Test",
            "description": "Test",
            "data_points": [{"x": 1, "y": 2}],
        }

        response = self.client.post(
            "/api/visual-learning/visualizations",
            json=invalid_viz_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 400
        assert "Invalid visualization type" in response.json()["detail"]

        # Test invalid filter type
        response = self.client.get(
            f"/api/visual-learning/visualizations/user/{self.user_id}?visualization_type=invalid_type",
            headers=self.auth_headers,
        )
        assert response.status_code == 400
        assert "Invalid type" in response.json()["detail"]


# ==================== Visual Vocabulary Tests ====================


class TestVisualVocabularyE2E:
    """
    E2E tests for visual vocabulary functionality

    Tests vocabulary visual creation and retrieval
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_vocab_user_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Vocab Tester",
            "email": f"e2e_vocab_{int(datetime.now().timestamp())}@example.com",
            "password": "TestVocabPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Vocab",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
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

    def test_create_and_list_vocabulary_visuals_e2e(self):
        """
        E2E Test: Create and list vocabulary visuals

        Validates:
        - Creating vocabulary visual with examples
        - Listing by language
        - Complete data structure
        """
        # Create Spanish vocabulary visual
        vocab_data = {
            "word": "hablar",
            "language": "es",
            "translation": "to speak",
            "visualization_type": "semantic_map",
            "phonetic": "a-BLAR",
            "example_sentences": [
                {"spanish": "Yo hablo español", "english": "I speak Spanish"},
                {"spanish": "¿Hablas inglés?", "english": "Do you speak English?"},
            ],
            "related_words": ["decir", "conversar", "comunicar"],
            "difficulty_level": 1,
        }

        response = self.client.post(
            "/api/visual-learning/vocabulary",
            json=vocab_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Vocabulary creation failed: {response.text}"
        )
        result = response.json()
        assert result["status"] == "success"
        assert "visual_id" in result

        # List vocabulary visuals (Spanish)
        response = self.client.get("/api/visual-learning/vocabulary?language=es")
        assert response.status_code == 200, (
            f"Vocabulary listing failed: {response.text}"
        )
        result = response.json()
        assert result["status"] == "success"
        assert result["count"] >= 1
        assert len(result["visuals"]) >= 1

        # Validate vocabulary visual structure
        spanish_visuals = [v for v in result["visuals"] if v["word"] == "hablar"]
        assert len(spanish_visuals) >= 1
        vocab = spanish_visuals[0]
        assert vocab["language"] == "es"
        assert vocab["translation"] == "to speak"
        assert vocab["visualization_type"] == "semantic_map"
        assert vocab["phonetic"] == "a-BLAR"
        assert len(vocab["example_sentences"]) == 2
        assert len(vocab["related_words"]) == 3
        assert vocab["difficulty_level"] == 1

    def test_multi_language_vocabulary_support_e2e(self):
        """
        E2E Test: Multi-language vocabulary visual support

        Validates:
        - Creating visuals in multiple languages
        - Language-specific filtering
        - Different visualization types
        """
        # Create French vocabulary visual
        french_vocab_data = {
            "word": "parler",
            "language": "fr",
            "translation": "to speak",
            "visualization_type": "context_examples",
            "phonetic": "par-LAY",
            "example_sentences": [
                {"french": "Je parle français", "english": "I speak French"},
            ],
            "related_words": ["dire", "discuter"],
            "difficulty_level": 1,
        }

        response = self.client.post(
            "/api/visual-learning/vocabulary",
            json=french_vocab_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"French vocab creation failed: {response.text}"
        )

        # Create German vocabulary visual
        german_vocab_data = {
            "word": "sprechen",
            "language": "de",
            "translation": "to speak",
            "visualization_type": "word_cloud",
            "phonetic": "SHPREH-khen",
            "example_sentences": [
                {"german": "Ich spreche Deutsch", "english": "I speak German"},
            ],
            "related_words": ["sagen", "reden"],
            "difficulty_level": 2,
        }

        response = self.client.post(
            "/api/visual-learning/vocabulary",
            json=german_vocab_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"German vocab creation failed: {response.text}"
        )

        # List French vocabulary
        response = self.client.get("/api/visual-learning/vocabulary?language=fr")
        assert response.status_code == 200, f"French listing failed: {response.text}"
        result = response.json()
        french_visuals = [v for v in result["visuals"] if v["language"] == "fr"]
        assert len(french_visuals) >= 1

        # List German vocabulary
        response = self.client.get("/api/visual-learning/vocabulary?language=de")
        assert response.status_code == 200, f"German listing failed: {response.text}"
        result = response.json()
        german_visuals = [v for v in result["visuals"] if v["language"] == "de"]
        assert len(german_visuals) >= 1

    def test_vocabulary_visualization_types_e2e(self):
        """
        E2E Test: Different vocabulary visualization types

        Validates:
        - Word cloud visualization
        - Semantic map visualization
        - Etymology tree visualization
        - Type-specific filtering
        """
        # Create word cloud
        word_cloud_data = {
            "word": "libro",
            "language": "es",
            "translation": "book",
            "visualization_type": "word_cloud",
            "related_words": ["leer", "página", "capítulo", "biblioteca"],
            "difficulty_level": 1,
        }

        response = self.client.post(
            "/api/visual-learning/vocabulary",
            json=word_cloud_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Word cloud creation failed: {response.text}"
        )

        # Create etymology tree
        etymology_data = {
            "word": "teléfono",
            "language": "es",
            "translation": "telephone",
            "visualization_type": "etymology_tree",
            "related_words": ["tele", "phone", "telefonear"],
            "difficulty_level": 2,
        }

        response = self.client.post(
            "/api/visual-learning/vocabulary",
            json=etymology_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Etymology tree creation failed: {response.text}"
        )

        # Filter by visualization type (word_cloud)
        response = self.client.get(
            "/api/visual-learning/vocabulary?visualization_type=word_cloud"
        )
        assert response.status_code == 200, f"Word cloud filter failed: {response.text}"
        result = response.json()
        word_cloud_visuals = [
            v for v in result["visuals"] if v["visualization_type"] == "word_cloud"
        ]
        assert len(word_cloud_visuals) >= 1


# ==================== Pronunciation Guide Tests ====================


class TestPronunciationGuidesE2E:
    """
    E2E tests for pronunciation guide functionality

    Tests guide creation and retrieval
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and authentication"""
        self.client = TestClient(app)

        # Create test user
        self.test_user_id = f"e2e_pron_user_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        self.test_user_data = {
            "user_id": self.test_user_id,
            "username": "E2E Pron Tester",
            "email": f"e2e_pron_{int(datetime.now().timestamp())}@example.com",
            "password": "TestPronPassword123!",
            "role": "child",
            "first_name": "E2E",
            "last_name": "Pron",
        }

        # Register test user
        response = self.client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"

        # Store auth token
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

    def test_create_and_retrieve_pronunciation_guide_e2e(self):
        """
        E2E Test: Create and retrieve pronunciation guide

        Validates:
        - Creating guide with complete data
        - Retrieving by ID
        - Breakdown and tips structure
        """
        # Create pronunciation guide
        guide_data = {
            "word_or_phrase": "hola",
            "language": "es",
            "phonetic_spelling": "OH-lah",
            "ipa_notation": "/ˈola/",
            "breakdown": [
                {"syllable": "ho", "sound": "OH", "tips": "Like 'oh' in English"},
                {"syllable": "la", "sound": "lah", "tips": "Like 'la' in 'lava'"},
            ],
            "common_mistakes": [
                "Don't pronounce the 'h'",
                "Avoid adding an 'r' sound",
            ],
            "practice_tips": [
                "Practice saying 'OH-lah' slowly",
                "Listen to native speakers",
            ],
            "difficulty_level": 1,
        }

        response = self.client.post(
            "/api/visual-learning/pronunciation",
            json=guide_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, f"Guide creation failed: {response.text}"
        result = response.json()
        assert result["status"] == "success"
        assert "guide_id" in result
        guide_id = result["guide_id"]

        # Retrieve pronunciation guide
        response = self.client.get(f"/api/visual-learning/pronunciation/{guide_id}")
        assert response.status_code == 200, f"Guide retrieval failed: {response.text}"
        guide = response.json()

        # Validate guide structure
        assert guide["guide_id"] == guide_id
        assert guide["word_or_phrase"] == "hola"
        assert guide["language"] == "es"
        assert guide["phonetic_spelling"] == "OH-lah"
        assert guide["ipa_notation"] == "/ˈola/"
        assert len(guide["breakdown"]) == 2
        assert len(guide["common_mistakes"]) == 2
        assert len(guide["practice_tips"]) == 2
        assert guide["difficulty_level"] == 1

        # Validate breakdown structure
        assert guide["breakdown"][0]["syllable"] == "ho"
        assert guide["breakdown"][0]["sound"] == "OH"
        assert "tips" in guide["breakdown"][0]

    def test_list_pronunciation_guides_with_filtering_e2e(self):
        """
        E2E Test: List pronunciation guides with filtering

        Validates:
        - Creating multiple guides
        - Filtering by language
        - Filtering by difficulty level
        """
        # Create Spanish guide (difficulty 1)
        spanish_guide_data = {
            "word_or_phrase": "gracias",
            "language": "es",
            "phonetic_spelling": "GRAH-see-ahs",
            "ipa_notation": "/ˈɡɾasjas/",
            "breakdown": [],
            "common_mistakes": [],
            "practice_tips": [],
            "difficulty_level": 1,
        }

        response = self.client.post(
            "/api/visual-learning/pronunciation",
            json=spanish_guide_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"Spanish guide creation failed: {response.text}"
        )

        # Create French guide (difficulty 2)
        french_guide_data = {
            "word_or_phrase": "bonjour",
            "language": "fr",
            "phonetic_spelling": "bon-ZHOOR",
            "ipa_notation": "/bɔ̃ʒuʁ/",
            "breakdown": [],
            "common_mistakes": [],
            "practice_tips": [],
            "difficulty_level": 2,
        }

        response = self.client.post(
            "/api/visual-learning/pronunciation",
            json=french_guide_data,
            headers=self.auth_headers,
        )
        assert response.status_code == 200, (
            f"French guide creation failed: {response.text}"
        )

        # List all guides
        response = self.client.get("/api/visual-learning/pronunciation")
        assert response.status_code == 200, f"Guide listing failed: {response.text}"
        result = response.json()
        assert result["status"] == "success"
        assert result["count"] >= 2

        # Filter by language (Spanish)
        response = self.client.get("/api/visual-learning/pronunciation?language=es")
        assert response.status_code == 200, f"Spanish filter failed: {response.text}"
        result = response.json()
        spanish_guides = [g for g in result["guides"] if g["language"] == "es"]
        assert len(spanish_guides) >= 1

        # Filter by difficulty level (1)
        response = self.client.get(
            "/api/visual-learning/pronunciation?difficulty_level=1"
        )
        assert response.status_code == 200, f"Difficulty filter failed: {response.text}"
        result = response.json()
        level1_guides = [g for g in result["guides"] if g["difficulty_level"] == 1]
        assert len(level1_guides) >= 1

    def test_pronunciation_guide_error_handling_e2e(self):
        """
        E2E Test: Error handling for pronunciation guides

        Validates:
        - Non-existent guide handling
        """
        # Test non-existent guide
        response = self.client.get(
            "/api/visual-learning/pronunciation/non_existent_guide_id"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
