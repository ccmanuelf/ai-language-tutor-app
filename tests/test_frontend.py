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
        assert "Personal Family Educational Tool" in content
        assert "FastHTML Frontend is running successfully!" in content
        assert "🎯" in content  # Check for the emoji

        # Check for proper HTML structure
        assert "<html>" in content
        assert "<head>" in content
        assert "<title>AI Language Tutor</title>" in content
        assert "<body>" in content
        assert 'charset="utf-8"' in content
        assert 'name="viewport"' in content

    def test_home_route_css_link(self):
        """Test that home page includes CSS link"""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.text
        assert 'href="/static/css/style.css"' in content
        assert 'type="text/css"' in content

    def test_home_route_javascript(self):
        """Test that home page includes JavaScript"""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.text
        assert 'src="/static/js/app.js"' in content

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
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 2  # Should have exactly 2 keys
        assert "status" in data
        assert "service" in data

    def test_home_route_html_structure(self):
        """Test detailed HTML structure of home page"""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.text

        # Check for specific HTML elements
        assert 'class="title"' in content
        assert 'class="subtitle"' in content
        assert 'class="status"' in content
        assert 'class="container"' in content

        # Check that title, subtitle, and status are in the right order
        title_pos = content.find("🎯 AI Language Tutor")
        subtitle_pos = content.find("Personal Family Educational Tool")
        status_pos = content.find("FastHTML Frontend is running successfully!")

        assert title_pos < subtitle_pos < status_pos

    def test_nonexistent_route(self):
        """Test that non-existent routes return 404"""
        response = self.client.get("/nonexistent")
        assert response.status_code == 404
