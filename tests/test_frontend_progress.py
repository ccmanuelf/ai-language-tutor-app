"""
Tests for Progress Frontend Module
Complete coverage for app/frontend/progress.py
"""

import pytest
from fastapi.testclient import TestClient

from app.frontend_main import frontend_app


class TestProgressRoute:
    """Test suite for progress frontend route"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_progress_route_accessible(self):
        """Test that progress route is accessible"""
        response = self.client.get("/progress")
        assert response.status_code == 200

    def test_progress_returns_html(self):
        """Test that progress returns valid HTML structure"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Validate HTML structure
        assert "<html" in content.lower()
        assert "Learning Progress" in content

    def test_progress_includes_overview_section(self):
        """Test that progress page includes overview section"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for overview section
        assert "Overview" in content

    def test_progress_includes_current_streak(self):
        """Test that progress page includes current streak"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for current streak
        assert "Current Streak" in content
        assert "days" in content

    def test_progress_includes_total_conversations(self):
        """Test that progress page includes total conversations"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for total conversations
        assert "Total Conversations" in content

    def test_progress_includes_words_learned(self):
        """Test that progress page includes words learned"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for words learned
        assert "Words Learned" in content

    def test_progress_includes_language_progress_section(self):
        """Test that progress page includes language progress section"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for language progress section
        assert "Language Progress" in content

    def test_progress_includes_spanish_progress(self):
        """Test that progress page includes Spanish progress"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for Spanish progress
        assert "Spanish" in content
        assert "Intermediate" in content
        assert "67%" in content

    def test_progress_includes_french_progress(self):
        """Test that progress page includes French progress"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for French progress
        assert "French" in content
        assert "Beginner" in content
        assert "34%" in content

    def test_progress_includes_progress_bars(self):
        """Test that progress page includes progress bars"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for progress bar styling (height and border-radius indicate progress bars)
        assert "height: 8px" in content
        assert "border-radius: 4px" in content

    def test_progress_uses_layout(self):
        """Test that progress page uses the layout component"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Progress page should have title set through layout
        assert "Progress Tracking - AI Language Tutor" in content

    def test_progress_grid_layout(self):
        """Test that progress page uses grid layout for overview cards"""
        response = self.client.get("/progress")

        assert response.status_code == 200
        content = response.text

        # Check for grid classes
        assert "grid" in content
