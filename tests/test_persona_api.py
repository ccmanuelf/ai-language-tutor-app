"""
Comprehensive Tests for Persona API Endpoints

Tests cover:
- GET /api/v1/personas/available
- GET /api/v1/personas/current
- PUT /api/v1/personas/preference
- GET /api/v1/personas/info/{persona_type}
- DELETE /api/v1/personas/preference

TRUE 100% coverage goal for persona API functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.config import get_primary_db_session
from app.main import app
from app.models.database import Base, User, UserRole
from app.services.persona_service import PersonaType

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the database dependency"""

    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_primary_db_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create test user with clean preferences"""
    user = User(
        user_id="test_persona_user",
        username="personatest",
        email="persona@test.com",
        role=UserRole.CHILD,
        preferences={},  # Start with empty preferences
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_user(test_user):
    """Override auth to return test user"""
    from app.api.auth import require_auth
    from app.services.auth import get_current_user

    class MockUser:
        def __init__(self):
            self.id = test_user.id
            self.user_id = test_user.user_id
            self.username = test_user.username
            self.email = test_user.email
            self.role = test_user.role.value

    def override_auth():
        return MockUser()

    def override_get_current_user():
        return {
            "id": test_user.id,
            "user_id": test_user.user_id,
            "username": test_user.username,
            "email": test_user.email,
            "role": test_user.role.value,
        }

    app.dependency_overrides[require_auth] = override_auth
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.pop(require_auth, None)
    app.dependency_overrides.pop(get_current_user, None)


class TestGetAvailablePersonas:
    """Test GET /api/v1/personas/available endpoint"""

    def test_returns_all_personas(self, client, override_get_db):
        """Test returns all 5 available personas"""
        response = client.get("/api/v1/personas/available")

        assert response.status_code == 200
        data = response.json()

        assert "personas" in data
        assert "default_persona" in data
        assert "total_count" in data
        assert len(data["personas"]) == 5
        assert data["total_count"] == 5

    def test_persona_structure(self, client, override_get_db):
        """Test each persona has required fields"""
        response = client.get("/api/v1/personas/available")
        data = response.json()

        for persona in data["personas"]:
            assert "persona_type" in persona
            assert "name" in persona
            assert "description" in persona
            assert "key_traits" in persona
            assert "best_for" in persona
            assert isinstance(persona["key_traits"], list)

    def test_default_persona_is_valid(self, client, override_get_db):
        """Test default persona is one of the available types"""
        response = client.get("/api/v1/personas/available")
        data = response.json()

        persona_types = {p["persona_type"] for p in data["personas"]}
        assert data["default_persona"] in persona_types

    def test_does_not_require_authentication(self, client, override_get_db):
        """Test endpoint is public (no auth required)"""
        # Should work without auth headers
        response = client.get("/api/v1/personas/available")
        assert response.status_code == 200


class TestGetCurrentPersona:
    """Test GET /api/v1/personas/current endpoint"""

    def test_returns_default_when_no_preference_set(
        self, client, test_user, auth_user, override_get_db
    ):
        """Test returns default persona when user has no preference"""
        response = client.get("/api/v1/personas/current")

        assert response.status_code == 200
        data = response.json()

        assert "persona_type" in data
        assert "subject" in data
        assert "learner_level" in data
        assert "persona_info" in data

        # Should be default (friendly_conversational)
        assert data["persona_type"] == "friendly_conversational"
        assert data["learner_level"] == "beginner"

    def test_returns_user_preference_when_set(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test returns user's persona preference when set"""
        # Set user preference
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "guiding_challenger",
                "subject": "calculus",
                "learner_level": "advanced",
            }
        }
        db_session.commit()

        response = client.get("/api/v1/personas/current")

        assert response.status_code == 200
        data = response.json()

        assert data["persona_type"] == "guiding_challenger"
        assert data["subject"] == "calculus"
        assert data["learner_level"] == "advanced"

    def test_requires_authentication(self, client, override_get_db):
        """Test endpoint requires authentication"""
        response = client.get("/api/v1/personas/current")

        # Should return 401 without auth
        assert response.status_code == 401

    def test_handles_invalid_persona_in_preferences(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test handles invalid persona type gracefully"""
        # Set invalid persona in preferences
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "invalid_persona",
                "subject": "math",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        response = client.get("/api/v1/personas/current")

        assert response.status_code == 200
        data = response.json()

        # Should fall back to default
        assert data["persona_type"] == "friendly_conversational"


class TestSetPersonaPreference:
    """Test PUT /api/v1/personas/preference endpoint"""

    def test_sets_persona_preference_successfully(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test successfully sets user's persona preference"""
        request_data = {
            "persona_type": "expert_scholar",
            "subject": "quantum physics",
            "learner_level": "advanced",
        }

        response = client.put("/api/v1/personas/preference", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["persona_type"] == "expert_scholar"
        assert data["subject"] == "quantum physics"
        assert data["learner_level"] == "advanced"

        # Verify saved in database
        db_session.refresh(test_user)
        assert test_user.preferences["persona_preference"]["persona_type"] == "expert_scholar"

    def test_updates_existing_preference(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test updates existing persona preference"""
        # Set initial preference
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "encouraging_coach",
                "subject": "spanish",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        # Update preference
        request_data = {
            "persona_type": "creative_mentor",
            "subject": "art history",
            "learner_level": "intermediate",
        }

        response = client.put("/api/v1/personas/preference", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["persona_type"] == "creative_mentor"
        assert data["subject"] == "art history"

    def test_rejects_invalid_persona_type(
        self, client, test_user, auth_user, override_get_db
    ):
        """Test rejects invalid persona type"""
        request_data = {
            "persona_type": "invalid_persona",
            "subject": "math",
            "learner_level": "beginner",
        }

        response = client.put("/api/v1/personas/preference", json=request_data)

        assert response.status_code == 400
        assert "Invalid persona type" in response.json()["detail"]

    def test_rejects_invalid_learner_level(
        self, client, test_user, auth_user, override_get_db
    ):
        """Test rejects invalid learner level"""
        request_data = {
            "persona_type": "guiding_challenger",
            "subject": "math",
            "learner_level": "expert",  # Invalid - should be beginner/intermediate/advanced
        }

        response = client.put("/api/v1/personas/preference", json=request_data)

        assert response.status_code == 400
        assert "Invalid learner level" in response.json()["detail"]

    def test_accepts_all_valid_learner_levels(
        self, client, test_user, auth_user, override_get_db
    ):
        """Test accepts all valid learner levels"""
        valid_levels = ["beginner", "intermediate", "advanced"]

        for level in valid_levels:
            request_data = {
                "persona_type": "friendly_conversational",
                "subject": "test",
                "learner_level": level,
            }

            response = client.put("/api/v1/personas/preference", json=request_data)
            assert response.status_code == 200

    def test_handles_empty_subject(self, client, test_user, auth_user, override_get_db):
        """Test handles empty subject field"""
        request_data = {
            "persona_type": "encouraging_coach",
            "subject": "",
            "learner_level": "beginner",
        }

        response = client.put("/api/v1/personas/preference", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == ""

    def test_requires_authentication(self, client, override_get_db):
        """Test endpoint requires authentication"""
        request_data = {
            "persona_type": "guiding_challenger",
            "learner_level": "beginner",
        }

        response = client.put("/api/v1/personas/preference", json=request_data)
        assert response.status_code == 401

    def test_preserves_other_preferences(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test doesn't overwrite other user preferences"""
        # Set some other preferences
        test_user.preferences = {
            "theme": "dark",
            "language": "en",
        }
        db_session.commit()

        request_data = {
            "persona_type": "expert_scholar",
            "learner_level": "advanced",
        }

        response = client.put("/api/v1/personas/preference", json=request_data)
        assert response.status_code == 200

        # Verify other preferences preserved
        db_session.refresh(test_user)
        assert test_user.preferences["theme"] == "dark"
        assert test_user.preferences["language"] == "en"
        assert "persona_preference" in test_user.preferences


class TestGetPersonaInfo:
    """Test GET /api/v1/personas/info/{persona_type} endpoint"""

    def test_returns_persona_info(self, client, override_get_db):
        """Test returns detailed persona information"""
        response = client.get("/api/v1/personas/info/guiding_challenger")

        assert response.status_code == 200
        data = response.json()

        assert data["persona_type"] == "guiding_challenger"
        assert data["name"] == "Guiding Challenger"
        assert "description" in data
        assert "key_traits" in data
        assert "best_for" in data

    def test_returns_all_persona_types(self, client, override_get_db):
        """Test can retrieve info for all persona types"""
        persona_types = [
            "guiding_challenger",
            "encouraging_coach",
            "friendly_conversational",
            "expert_scholar",
            "creative_mentor",
        ]

        for persona_type in persona_types:
            response = client.get(f"/api/v1/personas/info/{persona_type}")
            assert response.status_code == 200
            assert response.json()["persona_type"] == persona_type

    def test_returns_404_for_invalid_persona(self, client, override_get_db):
        """Test returns 404 for invalid persona type"""
        response = client.get("/api/v1/personas/info/invalid_persona")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_does_not_require_authentication(self, client, override_get_db):
        """Test endpoint is public (no auth required)"""
        response = client.get("/api/v1/personas/info/expert_scholar")
        assert response.status_code == 200


class TestResetPersonaPreference:
    """Test DELETE /api/v1/personas/preference endpoint"""

    def test_resets_persona_to_default(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test resets user's persona preference to default"""
        # Set custom preference
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "expert_scholar",
                "subject": "math",
                "learner_level": "advanced",
            }
        }
        db_session.commit()

        response = client.delete("/api/v1/personas/preference")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["default_persona"] == "friendly_conversational"

        # Verify removed from database
        db_session.refresh(test_user)
        assert "persona_preference" not in test_user.preferences

    def test_handles_no_existing_preference(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test handles case when user has no persona preference"""
        # Ensure no preference set
        test_user.preferences = {}
        db_session.commit()

        response = client.delete("/api/v1/personas/preference")

        assert response.status_code == 200

    def test_preserves_other_preferences(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test doesn't remove other user preferences"""
        # Set preferences including persona
        test_user.preferences = {
            "theme": "dark",
            "language": "es",
            "persona_preference": {
                "persona_type": "guiding_challenger",
            }
        }
        db_session.commit()

        response = client.delete("/api/v1/personas/preference")
        assert response.status_code == 200

        # Verify other preferences preserved
        db_session.refresh(test_user)
        assert test_user.preferences["theme"] == "dark"
        assert test_user.preferences["language"] == "es"
        assert "persona_preference" not in test_user.preferences

    def test_requires_authentication(self, client, override_get_db):
        """Test endpoint requires authentication"""
        response = client.delete("/api/v1/personas/preference")
        assert response.status_code == 401


class TestEndToEndWorkflow:
    """Test complete persona management workflow"""

    def test_complete_persona_workflow(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test complete workflow: list → get current → set → get current → reset"""
        # Step 1: Get available personas
        response = client.get("/api/v1/personas/available")
        assert response.status_code == 200
        personas = response.json()["personas"]
        assert len(personas) == 5

        # Step 2: Get current (should be default)
        response = client.get("/api/v1/personas/current")
        assert response.status_code == 200
        assert response.json()["persona_type"] == "friendly_conversational"

        # Step 3: Set new preference
        response = client.put(
            "/api/v1/personas/preference",
            json={
                "persona_type": "expert_scholar",
                "subject": "mathematics",
                "learner_level": "advanced",
            },
        )
        assert response.status_code == 200

        # Step 4: Verify preference was saved
        response = client.get("/api/v1/personas/current")
        assert response.status_code == 200
        data = response.json()
        assert data["persona_type"] == "expert_scholar"
        assert data["subject"] == "mathematics"

        # Step 5: Get info about the persona
        response = client.get("/api/v1/personas/info/expert_scholar")
        assert response.status_code == 200
        assert response.json()["name"] == "Expert Scholar"

        # Step 6: Reset to default
        response = client.delete("/api/v1/personas/preference")
        assert response.status_code == 200

        # Step 7: Verify reset
        response = client.get("/api/v1/personas/current")
        assert response.status_code == 200
        assert response.json()["persona_type"] == "friendly_conversational"
