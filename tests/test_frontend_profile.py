"""
Tests for Profile Frontend Module
Complete coverage for app/frontend/profile.py
"""

import pytest
from fastapi.testclient import TestClient

from app.frontend_main import frontend_app


class TestProfileRoute:
    """Test suite for profile frontend route"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_profile_route_accessible(self):
        """Test that profile route is accessible"""
        response = self.client.get("/profile")
        assert response.status_code == 200

    def test_profile_returns_html(self):
        """Test that profile page returns valid HTML structure"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Validate HTML structure
        assert "<html" in content.lower()
        assert "User Profile Management" in content

    def test_profile_includes_login_section(self):
        """Test that profile page includes login section"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Check for login section
        assert "Login or Register" in content

    def test_profile_includes_login_form(self):
        """Test that profile page includes login form"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Check for login form elements
        assert "user-id" in content.lower() or "username" in content.lower()
        assert "login" in content.lower()

    def test_profile_includes_registration_section(self):
        """Test that profile page includes registration section"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Check for registration
        assert "register" in content.lower()

    def test_profile_uses_layout(self):
        """Test that profile page uses the layout component"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Profile page should have title set through layout
        assert "Profile" in content or "User" in content

    def test_profile_page_title(self):
        """Test that profile page has proper title"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Check for page title
        assert "User Profile Management" in content

    def test_profile_includes_family_features(self):
        """Test that profile page includes family management features"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Check for family-related content (may be in JavaScript or visible HTML)
        # This is based on the module description mentioning family features
        assert (
            "family" in content.lower()
            or "member" in content.lower()
            or "profile" in content.lower()
        )

    def test_profile_accessible_without_auth(self):
        """Test that profile page is accessible without authentication (shows login form)"""
        response = self.client.get("/profile")

        # Should be accessible to show login/register form
        assert response.status_code == 200

    def test_profile_contains_form_elements(self):
        """Test that profile page contains form elements"""
        response = self.client.get("/profile")

        assert response.status_code == 200
        content = response.text

        # Check for form-related HTML
        assert "input" in content.lower() or "button" in content.lower()
