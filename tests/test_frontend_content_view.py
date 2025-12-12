"""
Tests for Content View Frontend Module
Complete coverage for app/frontend/content_view.py
"""

import pytest
from fastapi.testclient import TestClient

from app.frontend_main import frontend_app


class TestContentViewRoute:
    """Test suite for content view frontend route"""

    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(frontend_app)

    def test_content_view_route_accessible(self):
        """Test that content view route is accessible"""
        content_id = "test-content-123"
        response = self.client.get(f"/content/{content_id}")
        assert response.status_code == 200

    def test_content_view_returns_html(self):
        """Test that content_view returns valid HTML structure"""
        content_id = "test-content-123"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Validate HTML structure
        assert "<html" in content.lower()
        assert "Content Viewer" in content
        assert content_id in content

    def test_content_view_includes_title(self):
        """Test that content view includes proper title"""
        content_id = "article-456"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check title includes content_id
        assert f"Content Viewer - {content_id}" in content

    def test_content_view_includes_back_link(self):
        """Test that content view includes back to home link"""
        content_id = "doc-789"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for back link
        assert "Back to Home" in content
        assert 'href="/"' in content

    def test_content_view_includes_loading_state(self):
        """Test that content view includes loading state"""
        content_id = "content-001"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for loading state elements
        assert "Loading Content" in content
        assert "loadingState" in content

    def test_content_view_includes_error_state(self):
        """Test that content view includes error state"""
        content_id = "content-002"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for error state elements
        assert "Content Not Found" in content
        assert "errorState" in content

    def test_content_view_includes_content_display(self):
        """Test that content view includes content display area"""
        content_id = "content-003"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for content display elements
        assert "contentDisplay" in content
        assert "Content Details" in content

    def test_content_view_includes_materials_grid(self):
        """Test that content view includes materials grid"""
        content_id = "content-004"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for materials grid
        assert "Learning Materials" in content
        assert "materialsGrid" in content

    def test_content_view_includes_javascript(self):
        """Test that content view includes JavaScript for loading content"""
        content_id = "content-005"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for JavaScript functions
        assert "loadContent" in content
        assert "displayContent" in content
        assert "createMaterialCard" in content
        assert "showError" in content

    def test_content_view_includes_styles(self):
        """Test that content view includes CSS styles"""
        content_id = "content-006"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for CSS styles
        assert "--primary-color" in content
        assert ".container" in content
        assert ".content-card" in content
        assert ".material-grid" in content

    def test_content_view_with_different_content_ids(self):
        """Test content view with various content IDs"""
        content_ids = ["test-1", "article-abc", "content-xyz-123", "doc_001"]

        for content_id in content_ids:
            response = self.client.get(f"/content/{content_id}")
            assert response.status_code == 200
            content = response.text

            # Each should include the content_id
            assert content_id in content

    def test_content_view_api_endpoint_reference(self):
        """Test that content view references correct API endpoint"""
        content_id = "content-007"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for API endpoint reference
        assert "/api/content/content/" in content
        assert f"/api/content/content/{content_id}" in content

    def test_content_view_metadata_fields(self):
        """Test that content view includes all metadata fields"""
        content_id = "content-008"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for metadata field labels
        assert "Type:" in content
        assert "Topics:" in content
        assert "Difficulty:" in content
        assert "Word Count:" in content
        assert "Created:" in content

    def test_content_view_includes_content_preview(self):
        """Test that content view includes content preview section"""
        content_id = "content-009"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for content preview section
        assert "Content Preview" in content
        assert "contentPreview" in content

    def test_content_view_includes_material_type_icons(self):
        """Test that content view JavaScript includes material type icons"""
        content_id = "content-010"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for material type icons in JavaScript
        assert "typeIcons" in content
        assert "'summary'" in content
        assert "'flashcards'" in content
        assert "'quiz'" in content
        assert "'key_concepts'" in content

    def test_content_view_includes_view_material_function(self):
        """Test that content view includes viewMaterial function"""
        content_id = "content-011"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for viewMaterial function
        assert "viewMaterial" in content
        assert "material_id" in content.lower()

    def test_content_view_includes_dom_content_loaded_listener(self):
        """Test that content view includes DOMContentLoaded event listener"""
        content_id = "content-012"
        response = self.client.get(f"/content/{content_id}")

        assert response.status_code == 200
        content = response.text

        # Check for DOMContentLoaded listener
        assert "DOMContentLoaded" in content
        assert "addEventListener" in content
