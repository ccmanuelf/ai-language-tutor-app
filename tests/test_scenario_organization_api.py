"""
Comprehensive API Tests for Scenario Organization Endpoints
AI Language Tutor App - Session 133

Tests cover all 27 API endpoints:
- Collections (8 endpoints)
- Tags (4 endpoints)
- Bookmarks (5 endpoints)
- Ratings (5 endpoints)
- Discovery (5 endpoints)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.database import User
from app.models.scenario_db_models import Scenario


@pytest.fixture
def db_session_api():
    """
    Database session specifically for API tests.
    Uses a file-based SQLite database instead of in-memory to ensure
    TestClient can share the same database across requests.
    """
    import os
    import tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.database import Base

    # Create temporary file for database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    database_url = f"sqlite:///{db_path}"

    # Create engine and session
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(db_session_api):
    """FastAPI test client with database override"""
    from app.database.config import (
        get_db_session,  # CRITICAL: Must match the import used by API endpoints!
    )

    app = create_app()

    # Override database dependency to use test db_session_api
    # CRITICAL: Must be a generator that yields the session (FastAPI expects this)
    def override_get_db():
        try:
            yield db_session_api
        finally:
            pass  # Don't close the session - let the fixture handle cleanup

    app.dependency_overrides[get_db_session] = override_get_db

    return TestClient(app)


@pytest.fixture
def auth_headers(client, test_user):
    """Authentication headers using dependency override"""
    from app.core.security import require_auth

    app = client.app

    # Create mock user for auth
    class MockUser:
        def __init__(self):
            self.id = test_user.id
            self.user_id = test_user.user_id
            self.username = test_user.username
            self.email = test_user.email
            self.role = "CHILD"

    def override_auth():
        return MockUser()

    app.dependency_overrides[require_auth] = override_auth
    yield {}
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def test_user(db_session_api):
    """Create test user"""
    user = User(
        user_id="test_api_user",
        username="apitest",
        email="api@test.com",
        password_hash="not_used_in_tests",
    )
    db_session_api.add(user)
    db_session_api.commit()
    db_session_api.refresh(user)  # Refresh to load from DB
    return user


@pytest.fixture
def test_scenario(db_session_api, test_user):
    """Create test scenario"""
    scenario = Scenario(
        scenario_id="api_test_scenario",
        title="API Test Scenario",
        description="For testing API endpoints",
        category="restaurant",
        difficulty="beginner",
        estimated_duration=15,
        created_by=test_user.id,
        is_public=True,
    )
    db_session_api.add(scenario)
    db_session_api.commit()
    db_session_api.refresh(scenario)  # Refresh to load from DB
    return scenario


# ==================== COLLECTION ENDPOINTS ====================


def test_create_collection(client, auth_headers):
    """POST /api/v1/scenario-organization/collections"""
    response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={
            "name": "My Test Collection",
            "description": "Test description",
            "is_public": False,
            "is_learning_path": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "collection" in data
    assert "collection_id" in data["collection"]


def test_create_collection_unauthorized(client):
    """Test creating collection without auth"""
    response = client.post(
        "/api/v1/scenario-organization/collections",
        params={"name": "Unauthorized"},
    )

    assert response.status_code == 401


def test_get_collection(client, auth_headers, test_user):
    """GET /api/v1/scenario-organization/collections/{collection_id}"""
    # First create a collection
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Get Test"},
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    # Then retrieve it
    response = client.get(
        f"/api/v1/scenario-organization/collections/{collection_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["collection"]["name"] == "Get Test"


def test_get_user_collections(client, auth_headers):
    """GET /api/v1/scenario-organization/collections"""
    # Create some collections
    client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Collection 1"},
    )
    client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Collection 2"},
    )

    # Get all collections
    response = client.get(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["collections"]) >= 2


def test_add_scenario_to_collection(client, auth_headers, test_scenario):
    """POST /api/v1/scenario-organization/collections/{id}/scenarios"""
    # Create collection
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Add Scenario Test"},
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    # Add scenario
    response = client.post(
        f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "notes": "Test note",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_remove_scenario_from_collection(client, auth_headers, test_scenario):
    """DELETE /api/v1/scenario-organization/collections/{id}/scenarios/{scenario_id}"""
    # Create collection and add scenario
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Remove Test"},
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    client.post(
        f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
        headers=auth_headers,
        params={"scenario_id": test_scenario.scenario_id},
    )

    # Remove scenario
    response = client.delete(
        f"/api/v1/scenario-organization/collections/{collection_id}/scenarios/{test_scenario.scenario_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_reorder_collection(client, auth_headers, db_session_api, test_user):
    """PUT /api/v1/scenario-organization/collections/{id}/reorder"""
    # Create collection with multiple scenarios
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Reorder Test"},
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    # Create and add 3 scenarios
    scenario_ids = []
    for i in range(3):
        scenario = Scenario(
            scenario_id=f"reorder_{i}",
            title=f"Reorder {i}",
            description="Test",
            category="restaurant",
            difficulty="beginner",
            estimated_duration=15,
            created_by=test_user.id,
        )
        db_session_api.add(scenario)
        db_session_api.commit()
        scenario_ids.append(scenario.scenario_id)

        client.post(
            f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
            headers=auth_headers,
            params={"scenario_id": scenario.scenario_id},
        )

    # Reorder
    response = client.put(
        f"/api/v1/scenario-organization/collections/{collection_id}/reorder",
        headers=auth_headers,
        json={"scenario_order": list(reversed(scenario_ids))},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_delete_collection(client, auth_headers):
    """DELETE /api/v1/scenario-organization/collections/{id}"""
    # Create collection
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "To Delete"},
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    # Delete it
    response = client.delete(
        f"/api/v1/scenario-organization/collections/{collection_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_public_collections(client, auth_headers):
    """GET /api/v1/scenario-organization/public-collections"""
    # Create a public collection
    client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={
            "name": "Public Collection",
            "is_public": True,
        },
    )

    # Get public collections
    response = client.get(
        "/api/v1/scenario-organization/public-collections",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "collections" in data


# ==================== TAG ENDPOINTS ====================


def test_add_user_tag(client, auth_headers, test_scenario):
    """POST /api/v1/scenario-organization/scenarios/{id}/tags"""
    response = client.post(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/tags",
        headers=auth_headers,
        params={"tag": "helpful"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_add_ai_tags(client, auth_headers, test_scenario):
    """POST /api/v1/scenario-organization/scenarios/{id}/ai-tags"""
    response = client.post(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/ai-tags",
        headers=auth_headers,
        json={"tags": ["restaurant", "conversation", "beginner"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_scenario_tags(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/scenarios/{id}/tags"""
    # Add some tags first
    client.post(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/tags",
        headers=auth_headers,
        params={"tag": "useful"},
    )

    # Get tags
    response = client.get(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/tags",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "tags" in data


def test_search_by_tag(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/tags/search"""
    # Add a tag
    client.post(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/tags",
        headers=auth_headers,
        params={"tag": "searchable"},
    )

    # Search for it
    response = client.get(
        "/api/v1/scenario-organization/tags/search",
        headers=auth_headers,
        params={"tag": "searchable"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data


# ==================== BOOKMARK ENDPOINTS ====================


def test_add_bookmark(client, auth_headers, test_scenario):
    """POST /api/v1/scenario-organization/bookmarks"""
    response = client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "folder": "favorites",
            "notes": "Great scenario",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_remove_bookmark(client, auth_headers, test_scenario):
    """DELETE /api/v1/scenario-organization/bookmarks/{scenario_id}"""
    # Add bookmark first
    client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"scenario_id": test_scenario.scenario_id},
    )

    # Remove it
    response = client.delete(
        f"/api/v1/scenario-organization/bookmarks/{test_scenario.scenario_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_user_bookmarks(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/bookmarks"""
    # Add bookmark
    client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"scenario_id": test_scenario.scenario_id},
    )

    # Get bookmarks
    response = client.get(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "bookmarks" in data


def test_get_bookmark_folders(client, auth_headers, db_session_api, test_user):
    """GET /api/v1/scenario-organization/bookmarks/folders"""
    # Create scenarios with different folders
    for i, folder in enumerate(["work", "personal", "work"]):
        scenario = Scenario(
            scenario_id=f"folder_test_{i}",
            title=f"Folder Test {i}",
            description="Test",
            category="restaurant",
            difficulty="beginner",
            estimated_duration=15,
            created_by=test_user.id,
        )
        db_session_api.add(scenario)
        db_session_api.commit()

        client.post(
            "/api/v1/scenario-organization/bookmarks",
            headers=auth_headers,
            params={"scenario_id": scenario.scenario_id, "folder": folder},
        )

    # Get folders
    response = client.get(
        "/api/v1/scenario-organization/bookmarks/folders",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "folders" in data
    assert len(data["folders"]) == 2  # work and personal


def test_check_bookmark_status(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/bookmarks/{scenario_id}/check"""
    # Check when not bookmarked
    response = client.get(
        f"/api/v1/scenario-organization/bookmarks/{test_scenario.scenario_id}/check",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_bookmarked"] is False

    # Add bookmark
    client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"scenario_id": test_scenario.scenario_id},
    )

    # Check again
    response = client.get(
        f"/api/v1/scenario-organization/bookmarks/{test_scenario.scenario_id}/check",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_bookmarked"] is True


# ==================== RATING ENDPOINTS ====================


def test_add_rating(client, auth_headers, test_scenario):
    """POST /api/v1/scenario-organization/ratings"""
    response = client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "rating": 5,
            "review": "Excellent!",
            "difficulty_rating": 4,
            "usefulness_rating": 5,
            "cultural_accuracy_rating": 5,
            "is_public": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_add_rating_invalid_value(client, auth_headers, test_scenario):
    """Test adding rating with invalid value (out of range)"""
    response = client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "rating": 6,  # Invalid: must be 1-5
        },
    )

    assert response.status_code == 422  # Validation error


def test_get_scenario_ratings(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/scenarios/{id}/ratings"""
    # Add a rating
    client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "rating": 4,
            "review": "Good scenario",
        },
    )

    # Get ratings
    response = client.get(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/ratings",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "ratings" in data


def test_get_rating_summary(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/scenarios/{id}/ratings/summary"""
    # Add rating
    client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "rating": 5,
        },
    )

    # Get summary
    response = client.get(
        f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/ratings/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "average_rating" in data["summary"]
    assert "rating_count" in data["summary"]


def test_get_my_rating(client, auth_headers, test_scenario):
    """GET /api/v1/scenario-organization/ratings/my-rating/{scenario_id}"""
    # Add rating
    client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "rating": 4,
        },
    )

    # Get own rating
    response = client.get(
        f"/api/v1/scenario-organization/ratings/my-rating/{test_scenario.scenario_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rating"]["rating"] == 4


def test_delete_rating(client, auth_headers, test_scenario):
    """DELETE /api/v1/scenario-organization/ratings/{scenario_id}"""
    # Add rating
    client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": test_scenario.scenario_id,
            "rating": 3,
        },
    )

    # Delete it
    response = client.delete(
        f"/api/v1/scenario-organization/ratings/{test_scenario.scenario_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


# ==================== DISCOVERY ENDPOINTS ====================


def test_search_scenarios(client, auth_headers):
    """GET /api/v1/scenario-organization/search"""
    response = client.get(
        "/api/v1/scenario-organization/search",
        headers=auth_headers,
        params={"q": "restaurant"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data


def test_search_scenarios_with_filters(client, auth_headers):
    """Test search with category and difficulty filters"""
    response = client.get(
        "/api/v1/scenario-organization/search",
        headers=auth_headers,
        params={
            "q": "test",
            "category": "restaurant",
            "difficulty": "beginner",
        },
    )

    assert response.status_code == 200


def test_get_trending_scenarios(client, auth_headers):
    """GET /api/v1/scenario-organization/trending"""
    response = client.get(
        "/api/v1/scenario-organization/trending",
        headers=auth_headers,
        params={"limit": 10},
    )

    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data


def test_get_popular_scenarios(client, auth_headers):
    """GET /api/v1/scenario-organization/popular"""
    response = client.get(
        "/api/v1/scenario-organization/popular",
        headers=auth_headers,
        params={"limit": 10},
    )

    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data


def test_get_recommended_scenarios(client, auth_headers):
    """GET /api/v1/scenario-organization/recommended"""
    response = client.get(
        "/api/v1/scenario-organization/recommended",
        headers=auth_headers,
        params={"limit": 10},
    )

    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data


def test_get_discovery_hub(client, auth_headers):
    """GET /api/v1/scenario-organization/discovery-hub"""
    response = client.get(
        "/api/v1/scenario-organization/discovery-hub",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "hub" in data
    hub = data["hub"]
    assert "popular" in hub
    assert "top_rated" in hub
    assert "recommended" in hub


# ==================== AUTHORIZATION TESTS ====================


def test_endpoints_require_auth(client, test_scenario):
    """Test that all endpoints require authentication"""
    endpoints = [
        ("POST", "/api/v1/scenario-organization/collections", {}),
        ("GET", "/api/v1/scenario-organization/collections", {}),
        (
            "POST",
            f"/api/v1/scenario-organization/scenarios/{test_scenario.scenario_id}/tags",
            {},
        ),
        ("POST", "/api/v1/scenario-organization/bookmarks", {}),
        ("POST", "/api/v1/scenario-organization/ratings", {}),
        ("GET", "/api/v1/scenario-organization/search", {"query": "test"}),
    ]

    for method, url, params in endpoints:
        if method == "GET":
            response = client.get(url, params=params)
        else:
            response = client.post(url, params=params)

        assert response.status_code == 401, f"{method} {url} should require auth"


# ==================== VALIDATION TESTS ====================


def test_create_collection_validation(client, auth_headers):
    """Test collection creation validation"""
    # Missing name
    response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        json={"description": "No name"},
    )

    assert response.status_code == 422  # Validation error


def test_add_rating_validation(client, auth_headers, test_scenario):
    """Test rating validation"""
    # Missing scenario_id
    response = client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        json={"rating": 5},
    )

    assert response.status_code == 422
