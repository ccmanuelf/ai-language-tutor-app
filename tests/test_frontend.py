"""
Test module for FastHTML frontend
AI Language Tutor App - Personal Family Educational Tool
"""

import pytest
from fastapi.testclient import TestClient
from app.frontend_main import frontend_app, create_frontend_app


class TestFastHTMLFrontend:
    """Test suite for FastHTML frontend application"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_create_frontend_app(self):
        """Test frontend app creation"""
        app = create_frontend_app()
        assert app is not None
        # Test that the app has the expected configuration
        assert hasattr(app, "route")

    def test_home_route(self):
        """Test the home page route"""
        response = self.client.get("/")
        assert response.status_code == 200

        # Check that the response contains HTML
        content = response.text
        assert "AI Language Tutor" in content

        # Check for proper HTML structure (case insensitive)
        content_lower = content.lower()
        assert "<html>" in content_lower
        assert "<head>" in content_lower
        assert "<title>" in content_lower
        # Check for body tag as an element, not in CSS
        assert "</body>" in content_lower  # Closing tag is more reliable
        assert 'charset="utf-8"' in content_lower
        assert 'name="viewport"' in content_lower

    def test_home_route_css_link(self):
        """Test that home page includes CSS styling"""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.text
        # Check for inline styles or style tags
        assert "<style>" in content or 'href="/static/css/' in content

    def test_home_route_javascript(self):
        """Test that home page includes JavaScript"""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.text
        # Check for inline scripts or script tags
        assert "<script>" in content or 'src="/static/js/' in content

    def test_frontend_health_check(self):
        """Test frontend health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-language-tutor-frontend"

    def test_frontend_health_response_format(self):
        """Test health check response format"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data

    def test_home_route_html_structure(self):
        """Test detailed HTML structure of home page"""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.text.strip()

        # Check for common HTML structure elements (case insensitive)
        content_lower = content.lower()
        assert (
            content_lower.startswith("<!doctype html>")
            or "<!doctype html>" in content_lower
        )
        assert "</html>" in content_lower
        assert "</head>" in content_lower
        assert "</body>" in content_lower

    def test_nonexistent_route(self):
        """Test that non-existent routes return 404"""
        response = self.client.get("/nonexistent")
        assert response.status_code == 404
