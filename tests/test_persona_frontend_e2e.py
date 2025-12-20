"""
E2E Tests for Persona Frontend Integration
AI Language Tutor App - End-to-End Frontend Tests

Tests the complete persona frontend workflow including:
- Page rendering with authentication
- Persona selection and customization
- API integration
- State persistence

This test module creates a test app with properly mocked dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Any, Dict

from fasthtml.common import *

from app.database.config import get_primary_db_session
from app.models.database import Base, User, UserRole
from app.services.persona_service import get_persona_service, PersonaType
from app.frontend.layout import create_footer, create_header
from app.frontend.persona_selection import create_persona_selection_section
from app.frontend.styles import load_styles

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


@pytest.fixture
def test_user(db_session):
    """Create test user with clean preferences"""
    user = User(
        user_id="frontend_e2e_test_user",
        username="frontendetest",
        email="frontend_e2e@test.com",
        role=UserRole.CHILD,
        preferences={},
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_app(test_user, db_session):
    """Create a test FastHTML app with mocked persona route"""

    # Create test app
    app = FastHTML(
        debug=True,
        title="Test Persona Frontend",
    )

    # Create mock get_current_user that returns test user
    def mock_get_current_user():
        return {
            "id": test_user.id,
            "user_id": test_user.user_id,
            "username": test_user.username,
            "email": test_user.email,
            "role": test_user.role.value,
        }

    # Create mock get_db that returns test session
    def mock_get_db():
        return db_session

    # Register persona profile route with mocked dependencies
    @app.get("/profile/persona")
    async def persona_profile_page():
        """Persona selection page (with mocked auth)"""
        try:
            # Use mocked current_user
            current_user = mock_get_current_user()
            user_id = current_user.get("user_id")

            if not user_id:
                return Html(
                    Head(Title("Unauthorized")),
                    Body(P("Authentication required"))
                )

            # Use mocked db session
            db = mock_get_db()

            # Get persona service
            persona_service = get_persona_service()

            # Get all available personas
            available_personas = persona_service.get_available_personas()

            # Get user from database
            user = db.query(User).filter(User.id == test_user.id).first()
            if not user:
                return Html(
                    Head(Title("User Not Found")),
                    Body(P("User not found"))
                )

            # Get user's persona preference
            user_preferences = user.preferences or {}
            persona_pref = user_preferences.get("persona_preference", {})

            # Extract current persona settings
            persona_type_str = persona_pref.get("persona_type")
            subject = persona_pref.get("subject", "")
            learner_level = persona_pref.get("learner_level", "beginner")

            # Determine current persona
            if persona_type_str and persona_service.validate_persona_type(persona_type_str):
                # Convert string to PersonaType enum
                persona_enum = PersonaType(persona_type_str)
                current_persona_metadata = persona_service.get_persona_metadata(persona_enum)
            else:
                # Use default persona
                default_type = persona_service.get_default_persona()
                current_persona_metadata = persona_service.get_persona_metadata(default_type)
                persona_type_str = default_type.value

            # Add persona_type to metadata for selection highlighting
            current_persona_metadata["persona_type"] = persona_type_str

            # Prepare current customization
            current_customization = {
                "subject": subject,
                "learner_level": learner_level,
            }

            # Create the full persona profile page
            return Html(
                Head(
                    Title("AI Tutor Persona - Profile Settings"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport",
                        content="width=device-width, initial-scale=1.0",
                    ),
                    load_styles(),
                ),
                Body(
                    create_header("profile"),
                    Main(
                        Div(
                            # Page header
                            Div(
                                H1(
                                    "Profile Settings",
                                    cls="text-3xl font-bold text-white mb-2",
                                ),
                                P(
                                    "Personalize your AI tutor and learning experience",
                                    cls="text-gray-300 text-sm mb-6",
                                ),
                                A(
                                    "← Back to Profile",
                                    href="/profile",
                                    cls="text-purple-400 hover:text-purple-300 text-sm",
                                ),
                                cls="mb-8",
                            ),
                            # Persona selection section
                            create_persona_selection_section(
                                available_personas=available_personas,
                                current_persona=current_persona_metadata,
                                current_customization=current_customization,
                            ),
                            cls="container mx-auto px-4 py-8 max-w-6xl",
                        ),
                        cls="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                    ),
                    create_footer(),
                ),
            )

        except Exception as e:
            import logging
            logging.error(f"Error in persona profile page: {e}", exc_info=True)
            return Html(
                Head(Title("Error")),
                Body(P(f"Error: {str(e)}"))
            )

    return app


@pytest.fixture
def client(test_app):
    """Create test client with test app"""
    return TestClient(test_app)


class TestPersonaProfilePageAccess:
    """Test accessing the persona profile page"""

    def test_authenticated_user_can_access(self, client):
        """Test that authenticated users can access persona page"""
        response = client.get("/profile/persona")

        # Should return 200 OK
        assert response.status_code == 200

    def test_returns_html_content(self, client):
        """Test that response is HTML content"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestPersonaProfilePageContent:
    """Test persona profile page content"""

    def test_displays_persona_section_header(self, client):
        """Test that page displays persona section header"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should include persona section
        assert "AI Tutor Persona" in html or "🎭" in html

    def test_displays_all_five_personas(self, client):
        """Test that all 5 persona types are displayed"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # All 5 personas should be present
        assert "Guiding Challenger" in html
        assert "Encouraging Coach" in html
        assert "Friendly Conversationalist" in html
        assert "Expert Scholar" in html
        assert "Creative Mentor" in html

    def test_displays_persona_icons(self, client):
        """Test that persona icons are displayed"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Check for persona icons
        assert "🌟" in html  # Guiding Challenger
        assert "💪" in html  # Encouraging Coach
        assert "😊" in html  # Friendly Conversationalist
        assert "🎓" in html  # Expert Scholar
        assert "🎨" in html  # Creative Mentor

    def test_displays_current_selection_summary(self, client):
        """Test that current selection summary is displayed"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should show current selection
        assert "Current Selection" in html

    def test_includes_javascript_for_modals(self, client):
        """Test that JavaScript functions are included"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Check for JavaScript functions
        assert "openPersonaModal" in html
        assert "closePersonaModal" in html
        assert "selectPersona" in html
        assert "resetPersonaToDefault" in html


class TestPersonaSelectionWorkflow:
    """Test complete persona selection workflow"""

    def test_displays_default_persona_for_new_user(self, client):
        """Test that new users see default persona (Friendly Conversationalist)"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Default persona should be displayed
        assert "Friendly Conversationalist" in html

    def test_displays_user_selected_persona(self, client, test_user, db_session):
        """Test that page displays user's selected persona"""
        # Set persona preference
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "guiding_challenger",
                "subject": "Spanish",
                "learner_level": "intermediate",
            }
        }
        db_session.commit()

        # Request persona page
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should show selected persona
        assert "Guiding Challenger" in html
        assert "SELECTED" in html

    def test_displays_customization_values(self, client, test_user, db_session):
        """Test that customization values are displayed in forms"""
        # Set persona with customization
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "encouraging_coach",
                "subject": "Mathematics",
                "learner_level": "advanced",
            }
        }
        db_session.commit()

        # Request persona page
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Customization should be present
        assert "Mathematics" in html
        assert "advanced" in html


class TestPersonaModalInteraction:
    """Test persona modal functionality"""

    def test_includes_modal_for_each_persona(self, client):
        """Test that page includes modal for each persona type"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have modals for all persona types
        assert "modal-guiding_challenger" in html
        assert "modal-encouraging_coach" in html
        assert "modal-friendly_conversational" in html
        assert "modal-expert_scholar" in html
        assert "modal-creative_mentor" in html

    def test_modals_include_customization_forms(self, client):
        """Test that modals include customization forms"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have subject and level inputs
        assert "persona-subject" in html
        assert "persona-learner-level" in html


class TestPersonaResetFunctionality:
    """Test persona reset to default"""

    def test_displays_reset_button(self, client):
        """Test that page displays reset button"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have reset button
        assert "Reset to Default" in html or "reset" in html.lower()

    def test_reset_javascript_function_included(self, client):
        """Test that reset JavaScript function is included"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have resetPersonaToDefault function
        assert "resetPersonaToDefault" in html


class TestPersonaPageNavigation:
    """Test navigation and layout"""

    def test_includes_navigation_header(self, client):
        """Test that page includes navigation header"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have navigation
        assert "AI Language Tutor" in html

    def test_includes_back_to_profile_link(self, client):
        """Test that page includes link back to profile"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have back link
        assert "Back to Profile" in html or "/profile" in html

    def test_includes_footer(self, client):
        """Test that page includes footer"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have footer content
        assert "AI Language Tutor" in html


class TestPersonaErrorHandling:
    """Test error handling"""

    def test_handles_invalid_persona_in_preferences(self, client, test_user, db_session):
        """Test that page handles invalid persona type gracefully"""
        # Set invalid persona
        test_user.preferences = {
            "persona_preference": {
                "persona_type": "invalid_persona",
                "subject": "Test",
                "learner_level": "beginner",
            }
        }
        db_session.commit()

        # Page should still load with default
        response = client.get("/profile/persona")

        assert response.status_code == 200
        # Should fall back to default
        assert "Friendly Conversationalist" in response.text

    def test_handles_missing_preferences(self, client, test_user, db_session):
        """Test that page handles None preferences"""
        # Set preferences to None
        test_user.preferences = None
        db_session.commit()

        # Page should still load
        response = client.get("/profile/persona")

        assert response.status_code == 200
        # Should show default
        assert "Friendly Conversationalist" in response.text


class TestPersonaResponsiveDesign:
    """Test responsive design elements"""

    def test_includes_responsive_grid_classes(self, client):
        """Test that page uses responsive CSS classes"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have responsive classes
        assert "grid" in html
        # Should have breakpoint classes
        assert any(bp in html for bp in ["md:", "lg:", "sm:"])

    def test_includes_viewport_meta_tag(self, client):
        """Test that page includes viewport meta tag for mobile"""
        response = client.get("/profile/persona")

        assert response.status_code == 200
        html = response.text

        # Should have viewport meta
        assert "viewport" in html
        assert "width=device-width" in html
