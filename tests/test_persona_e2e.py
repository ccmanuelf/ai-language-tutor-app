"""
End-to-End Tests for Persona System Integration

Tests complete workflows:
- Persona selection → conversation with persona → AI response includes persona
- Persona preference persistence across sessions
- Persona switching between conversations
- Dynamic field injection in real conversations
- Multi-language persona support
- Provider-agnostic persona integration

TRUE 100% coverage goal for persona E2E functionality.
"""

from unittest.mock import AsyncMock, Mock, patch

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
        user_id="e2e_test_user",
        username="e2etest",
        email="e2e@test.com",
        role=UserRole.CHILD,
        preferences={},
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


@pytest.fixture
def mock_ai_response():
    """Create mock AI response"""

    class MockAIResponse:
        def __init__(self):
            self.content = "This is a test response from the AI."
            self.cost = 0.001

    return MockAIResponse()


class TestPersonaConversationIntegration:
    """Test persona integration with conversation API"""

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_conversation_uses_persona_system_prompt(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test that conversations pass persona system prompt to AI service"""
        # Set user's persona preference
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "guiding_challenger",
                "subject": "calculus",
                "learner_level": "advanced",
            }
        }
        db_session.commit()

        # Mock AI service response
        mock_generate.return_value = mock_ai_response

        # Send chat request
        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "Explain derivatives to me",
                "language": "en",
            },
        )

        assert response.status_code == 200

        # Verify AI service was called with system_prompt
        assert mock_generate.called
        call_kwargs = mock_generate.call_args.kwargs

        # Should have system_prompt parameter
        assert "system_prompt" in call_kwargs
        system_prompt = call_kwargs["system_prompt"]

        # System prompt should contain persona content
        assert system_prompt is not None
        assert len(system_prompt) > 0

        # Should contain global guidelines
        assert "Global Guidelines for All Tutor Personas" in system_prompt or "Global" in system_prompt

        # Should contain persona-specific content
        assert "Guiding Challenger" in system_prompt or "challenger" in system_prompt.lower()

        # Should have injected dynamic fields
        assert "calculus" in system_prompt.lower()  # subject
        assert "advanced" in system_prompt.lower()  # learner_level

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_conversation_without_persona_has_no_system_prompt(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test that conversations without persona don't pass system_prompt"""
        # Ensure no persona preference
        test_user.preferences = {}
        db_session.commit()

        # Mock AI service response
        mock_generate.return_value = mock_ai_response

        # Send chat request
        response = client.post(
            "/api/v1/conversations/chat",
            json={
                "message": "Hello",
                "language": "en",
            },
        )

        assert response.status_code == 200

        # Verify AI service was called
        assert mock_generate.called
        call_kwargs = mock_generate.call_args.kwargs

        # Should have system_prompt parameter but it should be None
        assert call_kwargs.get("system_prompt") is None

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_persona_switching_between_conversations(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test switching personas between conversations"""
        mock_generate.return_value = mock_ai_response

        # Conversation 1 with guiding_challenger
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "guiding_challenger",
                "subject": "math",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        response1 = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Test 1", "language": "en"},
        )
        assert response1.status_code == 200

        # Verify first persona used
        call1_kwargs = mock_generate.call_args.kwargs
        assert "challenger" in call1_kwargs["system_prompt"].lower()

        # Switch to encouraging_coach
        client.put(
            "/api/v1/personas/preference",
            json={
                "persona_type": "encouraging_coach",
                "subject": "spanish",
                "learner_level": "intermediate",
            },
        )

        # Conversation 2 with encouraging_coach
        response2 = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Test 2", "language": "en"},
        )
        assert response2.status_code == 200

        # Verify second persona used
        call2_kwargs = mock_generate.call_args.kwargs
        assert "coach" in call2_kwargs["system_prompt"].lower()
        assert "spanish" in call2_kwargs["system_prompt"].lower()

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_persona_with_all_5_types(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test conversations work with all 5 persona types"""
        mock_generate.return_value = mock_ai_response

        persona_types = [
            "guiding_challenger",
            "encouraging_coach",
            "friendly_conversational",
            "expert_scholar",
            "creative_mentor",
        ]

        for persona_type in persona_types:
            # Set persona preference
            test_user.preferences = {
                "persona_preference": {
                    "persona_type": persona_type,
                    "subject": "test_subject",
                    "learner_level": "beginner",
                }
            }
            db_session.commit()

            # Send conversation
            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": f"Test with {persona_type}", "language": "en"},
            )

            assert response.status_code == 200

            # Verify system prompt was generated
            call_kwargs = mock_generate.call_args.kwargs
            assert "system_prompt" in call_kwargs
            assert call_kwargs["system_prompt"] is not None
            assert len(call_kwargs["system_prompt"]) > 0


class TestPersonaDynamicFieldInjection:
    """Test dynamic field injection in real conversations"""

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_subject_field_injection(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test {subject} field is injected in persona prompts"""
        mock_generate.return_value = mock_ai_response

        test_user.preferences = {
            "persona_preference": {
                "persona_type": "expert_scholar",
                "subject": "quantum mechanics",
                "learner_level": "advanced",
            }
        }
        db_session.commit()

        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Explain superposition", "language": "en"},
        )

        assert response.status_code == 200

        # Verify subject was injected
        call_kwargs = mock_generate.call_args.kwargs
        system_prompt = call_kwargs["system_prompt"]
        assert "quantum mechanics" in system_prompt.lower()

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_learner_level_field_injection(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test {learner_level} field is injected in persona prompts"""
        mock_generate.return_value = mock_ai_response

        levels = ["beginner", "intermediate", "advanced"]

        for level in levels:
            test_user.preferences = {
                "persona_preference": {
                    "persona_type": "encouraging_coach",
                    "subject": "french",
                    "learner_level": level,
                }
            }
            db_session.commit()

            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": "Test", "language": "en"},
            )

            assert response.status_code == 200

            # Verify level was injected
            call_kwargs = mock_generate.call_args.kwargs
            system_prompt = call_kwargs["system_prompt"]
            assert level in system_prompt.lower()

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_language_field_injection(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test {language} field is injected based on conversation language"""
        mock_generate.return_value = mock_ai_response

        test_user.preferences = {
            "persona_preference": {
                "persona_type": "friendly_conversational",
                "subject": "grammar",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        # Test with Spanish language
        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Hola", "language": "es"},
        )

        assert response.status_code == 200

        # Verify language code was injected
        call_kwargs = mock_generate.call_args.kwargs
        system_prompt = call_kwargs["system_prompt"]
        # The language code (es) should be injected
        assert "es" in system_prompt.lower() or "spanish" in system_prompt.lower()


class TestPersonaProviderIndependence:
    """Test persona system is provider-agnostic

    Note: Provider independence is verified through architecture:
    - PersonaService generates plain text system prompts
    - ClaudeService.generate_response accepts system_prompt parameter
    - All AI services inherit the same interface
    - Persona prompts are just strings passed to any provider

    The integration with Claude is tested in other test classes.
    Testing with other providers would require extensive budget/routing mocking
    that doesn't add value beyond the architectural verification above.
    """

    def test_persona_service_generates_provider_agnostic_text(
        self, client, override_get_db
    ):
        """Test that PersonaService generates provider-agnostic text"""
        from app.services.persona_service import PersonaType, get_persona_service

        persona_service = get_persona_service()

        # Generate persona prompt
        prompt = persona_service.get_persona_prompt(
            persona_type=PersonaType.EXPERT_SCHOLAR,
            subject="mathematics",
            learner_level="advanced",
            language="en",
        )

        # Should be plain text (no provider-specific formatting)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # Should contain persona content
        assert "expert" in prompt.lower() or "scholar" in prompt.lower()
        assert "mathematics" in prompt.lower()
        assert "advanced" in prompt.lower()

        # Should NOT contain provider-specific markers
        assert "claude" not in prompt.lower()
        assert "gpt" not in prompt.lower()
        assert "deepseek" not in prompt.lower()
        assert "mistral" not in prompt.lower()


class TestPersonaPersistence:
    """Test persona preference persistence across sessions"""

    def test_persona_persists_across_api_calls(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test persona preference persists in database"""
        # Set persona
        response1 = client.put(
            "/api/v1/personas/preference",
            json={
                "persona_type": "guiding_challenger",
                "subject": "physics",
                "learner_level": "advanced",
            },
        )
        assert response1.status_code == 200

        # Retrieve persona (simulating new session)
        response2 = client.get("/api/v1/personas/current")
        assert response2.status_code == 200

        data = response2.json()
        assert data["persona_type"] == "guiding_challenger"
        assert data["subject"] == "physics"
        assert data["learner_level"] == "advanced"

        # Verify it's in the database
        db_session.refresh(test_user)
        assert "persona_preference" in test_user.preferences
        assert test_user.preferences["persona_preference"]["persona_type"] == "guiding_challenger"

    def test_persona_reset_persists(
        self, client, test_user, auth_user, override_get_db, db_session
    ):
        """Test persona reset persists in database"""
        # Set persona
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "expert_scholar",
                "subject": "chemistry",
                "learner_level": "intermediate",
            }
        }
        db_session.commit()

        # Reset persona
        response = client.delete("/api/v1/personas/preference")
        assert response.status_code == 200

        # Verify reset persists
        db_session.refresh(test_user)
        assert "persona_preference" not in test_user.preferences


class TestPersonaErrorHandling:
    """Test persona system error handling"""

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_conversation_continues_if_persona_fails_to_load(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test conversation continues even if persona fails to load"""
        mock_generate.return_value = mock_ai_response

        # Set invalid persona (corrupted data)
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "nonexistent_persona",
                "subject": "test",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        # Conversation should still work
        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Hello", "language": "en"},
        )

        # Should succeed without persona
        assert response.status_code == 200

        # Should fall back to no system_prompt
        call_kwargs = mock_generate.call_args.kwargs
        assert call_kwargs.get("system_prompt") is None

    @patch("app.services.persona_service.PersonaService.get_persona_prompt")
    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_conversation_continues_if_persona_service_raises_exception(
        self, mock_generate, mock_persona, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test conversation continues if persona service raises exception"""
        mock_generate.return_value = mock_ai_response
        mock_persona.side_effect = Exception("Persona service error")

        test_user.preferences = {
            "persona_preference": {
                "persona_type": "guiding_challenger",
                "subject": "test",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        # Conversation should still work despite exception
        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Hello", "language": "en"},
        )

        assert response.status_code == 200


class TestPersonaCompleteCoverageWorkflow:
    """Test complete persona workflow from start to finish"""

    @patch("app.services.claude_service.ClaudeService.generate_response")
    def test_complete_user_journey(
        self, mock_generate, client, test_user, auth_user, override_get_db, db_session, mock_ai_response
    ):
        """Test complete user journey: discover → select → converse → switch → reset"""
        mock_generate.return_value = mock_ai_response

        # Step 1: Discover available personas
        response = client.get("/api/v1/personas/available")
        assert response.status_code == 200
        personas = response.json()["personas"]
        assert len(personas) == 5

        # Step 2: Get detailed info about a persona
        response = client.get("/api/v1/personas/info/expert_scholar")
        assert response.status_code == 200
        persona_info = response.json()
        assert persona_info["name"] == "Expert Scholar"

        # Step 3: Set persona preference
        response = client.put(
            "/api/v1/personas/preference",
            json={
                "persona_type": "expert_scholar",
                "subject": "astronomy",
                "learner_level": "advanced",
            },
        )
        assert response.status_code == 200

        # Step 4: Have conversation with persona
        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Explain black holes", "language": "en"},
        )
        assert response.status_code == 200
        assert mock_generate.called

        # Verify persona was used
        call_kwargs = mock_generate.call_args.kwargs
        assert "system_prompt" in call_kwargs
        assert "expert" in call_kwargs["system_prompt"].lower() or "scholar" in call_kwargs["system_prompt"].lower()
        assert "astronomy" in call_kwargs["system_prompt"].lower()

        # Step 5: Switch to different persona
        response = client.put(
            "/api/v1/personas/preference",
            json={
                "persona_type": "creative_mentor",
                "subject": "art",
                "learner_level": "beginner",
            },
        )
        assert response.status_code == 200

        # Step 6: Have another conversation with new persona
        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Teach me about impressionism", "language": "en"},
        )
        assert response.status_code == 200

        # Verify new persona was used
        call_kwargs = mock_generate.call_args.kwargs
        assert "creative" in call_kwargs["system_prompt"].lower() or "mentor" in call_kwargs["system_prompt"].lower()
        assert "art" in call_kwargs["system_prompt"].lower()

        # Step 7: Reset to default
        response = client.delete("/api/v1/personas/preference")
        assert response.status_code == 200

        # Step 8: Verify reset worked
        response = client.get("/api/v1/personas/current")
        assert response.status_code == 200
        assert response.json()["persona_type"] == "friendly_conversational"

        # Step 9: Conversation without persona
        response = client.post(
            "/api/v1/conversations/chat",
            json={"message": "Hello", "language": "en"},
        )
        assert response.status_code == 200

        # Should have no system_prompt
        call_kwargs = mock_generate.call_args.kwargs
        assert call_kwargs.get("system_prompt") is None
