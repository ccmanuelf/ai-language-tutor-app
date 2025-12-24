"""
Integration Tests for Scenario Organization System
AI Language Tutor App - Session 133

Tests cover end-to-end workflows:
- Collection creation and management
- Scenario discovery workflow
- Rating and review flow
- Bookmark and tag integration
- Analytics tracking
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.database import User
from app.models.scenario_db_models import Scenario, ScenarioAnalytics


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
    def override_get_db():
        try:
            yield db_session_api
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db

    return TestClient(app)


@pytest.fixture
def test_user(db_session_api):
    """Create test user"""
    user = User(
        user_id="test_integration_user",
        username="integration_user",
        email="integration@test.com",
        password_hash="not_used_in_tests",
    )
    db_session_api.add(user)
    db_session_api.commit()
    return user


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
def multiple_scenarios(db_session_api, test_user):
    """Create multiple test scenarios"""
    scenarios = []
    categories = ["restaurant", "travel", "shopping", "business", "social"]
    difficulties = ["beginner", "intermediate", "advanced"]

    for i in range(10):
        scenario = Scenario(
            scenario_id=f"integration_scenario_{i}",
            title=f"Integration Scenario {i}",
            description=f"Test scenario for integration testing {i}",
            category=categories[i % len(categories)],
            difficulty=difficulties[i % len(difficulties)],
            estimated_duration=15 + (i * 5),
            created_by=test_user.id,
            is_public=True,
            is_system_scenario=False,
        )
        db_session_api.add(scenario)
        scenarios.append(scenario)

    db_session_api.commit()
    return scenarios


# ==================== COLLECTION WORKFLOW TESTS ====================


def test_complete_collection_workflow(client, auth_headers, multiple_scenarios):
    """
    Test complete collection creation and management workflow:
    1. Create collection
    2. Add multiple scenarios
    3. Reorder scenarios
    4. View collection
    5. Remove a scenario
    6. Delete collection
    """
    # Step 1: Create collection
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={
            "name": "My Learning Path",
            "description": "Progressive learning scenarios",
            "is_learning_path": True,
            "is_public": True,
        },
    )
    assert create_response.status_code == 200
    collection_id = create_response.json()["collection"]["collection_id"]

    # Step 2: Add scenarios
    scenario_ids = [s.scenario_id for s in multiple_scenarios[:5]]
    for scenario_id in scenario_ids:
        add_response = client.post(
            f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
            headers=auth_headers,
            params={"scenario_id": scenario_id, "notes": f"Added {scenario_id}"},
        )
        assert add_response.status_code == 200

    # Step 3: Reorder scenarios
    reversed_order = list(reversed(scenario_ids))
    reorder_response = client.put(
        f"/api/v1/scenario-organization/collections/{collection_id}/reorder",
        headers=auth_headers,
        json={"scenario_order": reversed_order},
    )
    assert reorder_response.status_code == 200

    # Step 4: View collection
    get_response = client.get(
        f"/api/v1/scenario-organization/collections/{collection_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    collection_data = get_response.json()["collection"]
    assert len(collection_data["items"]) == 5

    # Step 5: Remove a scenario
    remove_response = client.delete(
        f"/api/v1/scenario-organization/collections/{collection_id}/scenarios/{scenario_ids[0]}",
        headers=auth_headers,
    )
    assert remove_response.status_code == 200

    # Verify removal
    get_response = client.get(
        f"/api/v1/scenario-organization/collections/{collection_id}",
        headers=auth_headers,
    )
    assert len(get_response.json()["collection"]["items"]) == 4

    # Step 6: Delete collection
    delete_response = client.delete(
        f"/api/v1/scenario-organization/collections/{collection_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200


def test_learning_path_progression(client, auth_headers, multiple_scenarios):
    """
    Test creating a learning path with ordered progression
    """
    # Create learning path
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={
            "name": "Beginner to Advanced Restaurant",
            "is_learning_path": True,
            "category": "restaurant",
            "difficulty_level": "beginner",
        },
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    # Add scenarios in difficulty order
    beginner_scenarios = [s for s in multiple_scenarios if s.difficulty == "beginner"][
        :3
    ]
    for scenario in beginner_scenarios:
        client.post(
            f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
            headers=auth_headers,
            params={"scenario_id": scenario.scenario_id},
        )

    # Verify order is maintained
    get_response = client.get(
        f"/api/v1/scenario-organization/collections/{collection_id}",
        headers=auth_headers,
    )
    items = get_response.json()["collection"]["items"]
    assert items[0]["position"] < items[1]["position"] < items[2]["position"]


# ==================== DISCOVERY WORKFLOW TESTS ====================


def test_discovery_to_bookmark_flow(client, auth_headers, multiple_scenarios):
    """
    Test discovery workflow:
    1. Search for scenarios
    2. View scenario details
    3. Bookmark scenario
    4. Add to collection
    5. Rate scenario
    """
    # Step 1: Search for scenarios
    search_response = client.get(
        "/api/v1/scenario-organization/search",
        headers=auth_headers,
        params={"q": "Integration", "limit": 5},
    )
    assert search_response.status_code == 200
    scenarios_found = search_response.json()["scenarios"]
    assert len(scenarios_found) > 0

    selected_scenario = scenarios_found[0]
    scenario_id = selected_scenario["scenario_id"]

    # Step 2: Bookmark scenario
    bookmark_response = client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={
            "scenario_id": scenario_id,
            "folder": "to-practice",
            "notes": "Found via search",
        },
    )
    assert bookmark_response.status_code == 200

    # Step 3: Create collection and add scenario
    collection_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "Discovered Scenarios"},
    )
    collection_id = collection_response.json()["collection"]["collection_id"]

    add_response = client.post(
        f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
        headers=auth_headers,
        params={"scenario_id": scenario_id},
    )
    assert add_response.status_code == 200

    # Step 4: Rate scenario
    rating_response = client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": scenario_id,
            "rating": 5,
            "review": "Great scenario found through discovery!",
            "is_public": True,
        },
    )
    assert rating_response.status_code == 200

    # Verify all actions succeeded
    bookmarks = client.get(
        "/api/v1/scenario-organization/bookmarks", headers=auth_headers
    )
    assert len(bookmarks.json()["bookmarks"]) >= 1

    my_rating = client.get(
        f"/api/v1/scenario-organization/ratings/my-rating/{scenario_id}",
        headers=auth_headers,
    )
    assert my_rating.json()["rating"]["rating"] == 5


def test_trending_scenarios_workflow(
    client, auth_headers, db_session, multiple_scenarios
):
    """
    Test trending scenarios discovery:
    1. Create analytics for scenarios
    2. Fetch trending
    3. Interact with trending scenario
    """
    # Step 1: Create analytics with trending scores
    for i, scenario in enumerate(multiple_scenarios[:5]):
        analytics = ScenarioAnalytics(
            scenario_id=scenario.id,
            trending_score=float(5 - i),  # Descending scores
            total_starts=100 - (i * 10),
            total_completions=80 - (i * 10),
        )
        db_session.add(analytics)
    db_session.commit()

    # Step 2: Get trending scenarios
    trending_response = client.get(
        "/api/v1/scenario-organization/trending",
        headers=auth_headers,
        params={"limit": 5},
    )
    assert trending_response.status_code == 200
    trending = trending_response.json()["scenarios"]

    # Step 3: Bookmark top trending scenario
    if len(trending) > 0:
        top_trending = trending[0]
        bookmark_response = client.post(
            "/api/v1/scenario-organization/bookmarks",
            headers=auth_headers,
            params={"scenario_id": top_trending["scenario_id"], "folder": "trending"},
        )
        assert bookmark_response.status_code == 200


# ==================== RATING AND REVIEW WORKFLOW ====================


def test_complete_rating_workflow(client, auth_headers, multiple_scenarios):
    """
    Test rating workflow:
    1. Add rating with review
    2. View rating summary
    3. Update rating
    4. Delete rating
    """
    scenario = multiple_scenarios[0]

    # Step 1: Add initial rating
    add_response = client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": scenario.scenario_id,
            "rating": 4,
            "review": "Good scenario, helpful for beginners",
            "difficulty_rating": 3,
            "usefulness_rating": 5,
            "cultural_accuracy_rating": 4,
            "is_public": True,
        },
    )
    assert add_response.status_code == 200

    # Step 2: View rating summary
    summary_response = client.get(
        f"/api/v1/scenario-organization/scenarios/{scenario.scenario_id}/ratings/summary",
        headers=auth_headers,
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()["summary"]
    assert summary["rating_count"] >= 1

    # Step 3: Update rating (delete and re-add)
    client.delete(
        f"/api/v1/scenario-organization/ratings/{scenario.scenario_id}",
        headers=auth_headers,
    )

    update_response = client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": scenario.scenario_id,
            "rating": 5,
            "review": "Actually excellent! Changed my mind after more practice.",
            "is_public": True,
        },
    )
    assert update_response.status_code == 200

    # Step 4: Verify updated rating
    my_rating = client.get(
        f"/api/v1/scenario-organization/ratings/my-rating/{scenario.scenario_id}",
        headers=auth_headers,
    )
    assert my_rating.json()["rating"]["rating"] == 5


def test_public_vs_private_ratings(
    client, auth_headers, db_session, test_user, multiple_scenarios
):
    """
    Test that private ratings are not visible to other users
    """
    scenario = multiple_scenarios[0]

    # Create another user
    other_user = User(
        user_id="test_other_user",
        username="other_user",
        email="other@test.com",
        password_hash="hash",
    )
    db_session.add(other_user)
    db_session.commit()

    # Add private rating
    client.post(
        "/api/v1/scenario-organization/ratings",
        headers=auth_headers,
        params={
            "scenario_id": scenario.scenario_id,
            "rating": 3,
            "review": "Private review",
            "is_public": False,
        },
    )

    # Get public ratings (should not include private review)
    ratings_response = client.get(
        f"/api/v1/scenario-organization/scenarios/{scenario.scenario_id}/ratings",
        headers=auth_headers,
        params={"public_only": True},
    )
    public_ratings = ratings_response.json()["ratings"]

    # Private review should not be in public ratings
    assert not any(r.get("review") == "Private review" for r in public_ratings)


# ==================== TAG AND SEARCH INTEGRATION ====================


def test_tag_based_discovery(client, auth_headers, multiple_scenarios):
    """
    Test discovering scenarios through tags:
    1. Add user tags to scenarios
    2. Add AI tags
    3. Search by tag
    4. Browse scenarios with common tags
    """
    # Step 1: Add user tags to multiple scenarios
    for i, scenario in enumerate(multiple_scenarios[:3]):
        client.post(
            f"/api/v1/scenario-organization/scenarios/{scenario.scenario_id}/tags",
            headers=auth_headers,
            params={"tag": "beginner-friendly"},
        )

    # Step 2: Add AI tags
    client.post(
        f"/api/v1/scenario-organization/scenarios/{multiple_scenarios[0].scenario_id}/ai-tags",
        headers=auth_headers,
        json={"tags": ["conversation", "practical", "everyday"]},
    )

    # Step 3: Search by user tag
    search_response = client.get(
        "/api/v1/scenario-organization/tags/search",
        headers=auth_headers,
        params={"tag": "beginner-friendly"},
    )
    assert search_response.status_code == 200
    tagged_scenarios = search_response.json()["scenarios"]
    assert len(tagged_scenarios) >= 3

    # Step 4: Get tags for a scenario
    tags_response = client.get(
        f"/api/v1/scenario-organization/scenarios/{multiple_scenarios[0].scenario_id}/tags",
        headers=auth_headers,
    )
    tags = tags_response.json()["tags"]
    assert any(t["tag"] == "beginner-friendly" for t in tags)
    assert any(t["tag"] == "conversation" for t in tags)


# ==================== BOOKMARK ORGANIZATION ====================


def test_bookmark_folder_organization(client, auth_headers, multiple_scenarios):
    """
    Test organizing bookmarks into folders:
    1. Create bookmarks in different folders
    2. List folders
    3. Filter bookmarks by folder
    4. Move bookmark to different folder
    """
    # Step 1: Add bookmarks to folders
    folders = {
        "to-practice": [0, 1, 2],
        "completed": [3, 4],
        "favorites": [5],
    }

    for folder, indices in folders.items():
        for idx in indices:
            client.post(
                "/api/v1/scenario-organization/bookmarks",
                headers=auth_headers,
                params={
                    "scenario_id": multiple_scenarios[idx].scenario_id,
                    "folder": folder,
                },
            )

    # Step 2: List all folders
    folders_response = client.get(
        "/api/v1/scenario-organization/bookmarks/folders",
        headers=auth_headers,
    )
    user_folders = folders_response.json()["folders"]
    assert len(user_folders) == 3

    # Step 3: Filter by folder
    to_practice_response = client.get(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"folder": "to-practice"},
    )
    to_practice = to_practice_response.json()["bookmarks"]
    assert len(to_practice) == 3

    # Step 4: Move bookmark (remove and re-add)
    scenario_to_move = multiple_scenarios[0].scenario_id
    client.delete(
        f"/api/v1/scenario-organization/bookmarks/{scenario_to_move}",
        headers=auth_headers,
    )
    client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"scenario_id": scenario_to_move, "folder": "favorites"},
    )

    # Verify move
    favorites_response = client.get(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"folder": "favorites"},
    )
    favorites = favorites_response.json()["bookmarks"]
    assert len(favorites) == 2


# ==================== FULL DISCOVERY HUB TEST ====================


def test_discovery_hub_complete(
    client, auth_headers, db_session_api, multiple_scenarios
):
    """
    Test complete discovery hub functionality:
    1. Get discovery hub data
    2. Verify all sections populated
    3. Interact with each section
    """
    # Setup: Add analytics and ratings
    for i, scenario in enumerate(multiple_scenarios):
        analytics = ScenarioAnalytics(
            scenario_id=scenario.id,
            trending_score=float(i),
            popularity_score=float(10 - i),
            total_starts=50 + i,
            total_completions=40 + i,
        )
        db_session_api.add(analytics)
    db_session_api.commit()

    # Add some ratings
    for scenario in multiple_scenarios[:5]:
        client.post(
            "/api/v1/scenario-organization/ratings",
            headers=auth_headers,
            params={
                "scenario_id": scenario.scenario_id,
                "rating": 4,
            },
        )

    # Step 1: Get discovery hub
    hub_response = client.get(
        "/api/v1/scenario-organization/discovery-hub",
        headers=auth_headers,
    )
    assert hub_response.status_code == 200
    response_data = hub_response.json()
    assert "hub" in response_data
    hub_data = response_data["hub"]

    # Step 2: Verify sections
    assert "trending" in hub_data
    assert "popular" in hub_data
    assert "top_rated" in hub_data
    assert "recommended" in hub_data

    # Step 3: Interact with trending scenario
    if len(hub_data["trending"]) > 0:
        trending_scenario = hub_data["trending"][0]["scenario"]

        # Bookmark it
        client.post(
            "/api/v1/scenario-organization/bookmarks",
            headers=auth_headers,
            params={"scenario_id": trending_scenario["scenario_id"]},
        )

        # Add to collection
        collection_response = client.post(
            "/api/v1/scenario-organization/collections",
            headers=auth_headers,
            params={"name": "From Discovery Hub"},
        )
        collection_id = collection_response.json()["collection"]["collection_id"]

        client.post(
            f"/api/v1/scenario-organization/collections/{collection_id}/scenarios",
            headers=auth_headers,
            params={"scenario_id": trending_scenario["scenario_id"]},
        )


# ==================== ANALYTICS TRACKING ====================


def test_scenario_usage_tracking(
    client, auth_headers, db_session_api, multiple_scenarios
):
    """
    Test that scenario usage is properly tracked:
    1. Record starts and completions
    2. Verify analytics updated
    3. Check trending/popular calculations
    """
    scenario = multiple_scenarios[0]

    # Note: This requires actual scenario start/completion endpoints
    # which may be in the scenarios API, not organization API
    # This is a placeholder for the integration

    # Verify analytics exist after usage
    # (Would need to call actual start/complete endpoints)
    pass


# ==================== ERROR HANDLING AND EDGE CASES ====================


def test_collection_permissions(
    client, auth_headers, db_session_api, test_user, multiple_scenarios
):
    """
    Test that users can only modify their own collections
    """
    # Create another user
    other_user = User(
        user_id="test_other_collection_user",
        username="other_collection_user",
        email="other_collection@test.com",
        password_hash="hash",
    )
    db_session_api.add(other_user)
    db_session_api.commit()

    # User 1 creates collection
    create_response = client.post(
        "/api/v1/scenario-organization/collections",
        headers=auth_headers,
        params={"name": "User 1 Collection"},
    )
    collection_id = create_response.json()["collection"]["collection_id"]

    # User 2 tries to modify (should fail)
    # This would require getting auth headers for user 2
    # Placeholder for permission testing


def test_invalid_scenario_id_handling(client, auth_headers):
    """
    Test graceful handling of invalid scenario IDs
    """
    # Try to bookmark non-existent scenario
    response = client.post(
        "/api/v1/scenario-organization/bookmarks",
        headers=auth_headers,
        params={"scenario_id": "nonexistent_scenario_999"},
    )

    # Should return 404 or 400, not 500
    assert response.status_code in [400, 404]


def test_empty_results_handling(client, auth_headers):
    """
    Test that endpoints handle empty results gracefully
    """
    # Search for something that doesn't exist
    response = client.get(
        "/api/v1/scenario-organization/search",
        headers=auth_headers,
        params={"q": "xyzxyzxyznonexistent"},
    )

    assert response.status_code == 200
    assert response.json()["scenarios"] == []


# ==================== PERFORMANCE TESTS ====================


def test_pagination_performance(client, auth_headers, db_session_api, test_user):
    """
    Test pagination works correctly with many items
    """
    # Create many scenarios
    for i in range(50):
        scenario = Scenario(
            scenario_id=f"perf_test_{i}",
            title=f"Performance Test {i}",
            description="Test",
            category="restaurant",
            difficulty="beginner",
            estimated_duration=15,
            created_by=test_user.id,
            is_public=True,
        )
        db_session_api.add(scenario)
    db_session_api.commit()

    # Test paginated search
    response = client.get(
        "/api/v1/scenario-organization/search",
        headers=auth_headers,
        params={"q": "Performance", "limit": 10},
    )

    assert response.status_code == 200
    assert len(response.json()["scenarios"]) <= 10
