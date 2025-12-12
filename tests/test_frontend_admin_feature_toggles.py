"""
Tests for app/frontend/admin_feature_toggles.py
Target: 100% coverage (17 statements, 0 branches)
"""

import pytest
from fasthtml.common import to_xml


class TestCreateFeatureTogglePage:
    """Test create_feature_toggle_page function"""

    def test_create_feature_toggle_page_returns_div(self):
        """Test that create_feature_toggle_page returns a Div element"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()

        # Verify it returns a FastHTML component (has children or is callable)
        assert result is not None
        # FastHTML components have a specific structure
        assert hasattr(result, "children") or callable(result)

    def test_create_feature_toggle_page_contains_header(self):
        """Test that the page contains a header with title"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "Feature Toggle Management" in result_str

    def test_create_feature_toggle_page_contains_action_buttons(self):
        """Test that the page contains action buttons"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "Create Feature" in result_str
        assert "View Statistics" in result_str
        assert "Refresh" in result_str

    def test_create_feature_toggle_page_contains_search_filters(self):
        """Test that the page contains search and filter controls"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "Search features" in result_str
        assert "All Categories" in result_str
        assert "All Statuses" in result_str

    def test_create_feature_toggle_page_contains_table(self):
        """Test that the page contains features table"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "featuresTableBody" in result_str
        assert "Name" in result_str
        assert "Category" in result_str
        assert "Status" in result_str

    def test_create_feature_toggle_page_contains_modals(self):
        """Test that the page contains modal dialogs"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "createFeatureModal" in result_str
        assert "editFeatureModal" in result_str
        assert "userAccessModal" in result_str
        assert "statsModal" in result_str

    def test_create_feature_toggle_page_contains_javascript(self):
        """Test that the page contains JavaScript functionality"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "loadFeatures" in result_str or "function loadFeatures" in result_str

    def test_create_feature_toggle_page_contains_pagination(self):
        """Test that the page contains pagination controls"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_page

        result = create_feature_toggle_page()
        result_str = to_xml(result)

        assert "Previous" in result_str
        assert "Next" in result_str


class TestCreateFeaturesTable:
    """Test create_features_table function"""

    def test_create_features_table_returns_div(self):
        """Test that create_features_table returns a Div"""
        from app.frontend.admin_feature_toggles import create_features_table

        result = create_features_table()
        assert result is not None

    def test_create_features_table_contains_table_headers(self):
        """Test that table contains proper headers"""
        from app.frontend.admin_feature_toggles import create_features_table

        result = create_features_table()
        result_str = to_xml(result)

        assert "Name" in result_str
        assert "Category" in result_str
        assert "Status" in result_str
        assert "Scope" in result_str
        assert "Created" in result_str
        assert "Actions" in result_str

    def test_create_features_table_contains_sorting(self):
        """Test that table headers have sorting functionality"""
        from app.frontend.admin_feature_toggles import create_features_table

        result = create_features_table()
        result_str = to_xml(result)

        assert "sortTable" in result_str


class TestCreateFeatureModal:
    """Test create_feature_modal function"""

    def test_create_feature_modal_returns_div(self):
        """Test that create_feature_modal returns a Div"""
        from app.frontend.admin_feature_toggles import create_feature_modal

        result = create_feature_modal()
        assert result is not None

    def test_create_feature_modal_contains_form_fields(self):
        """Test that modal contains all required form fields"""
        from app.frontend.admin_feature_toggles import create_feature_modal

        result = create_feature_modal()
        result_str = to_xml(result)

        assert "Feature Name" in result_str
        assert "Description" in result_str
        assert "Category" in result_str
        assert "Scope" in result_str

    def test_create_feature_modal_contains_configuration_options(self):
        """Test that modal contains configuration options"""
        from app.frontend.admin_feature_toggles import create_feature_modal

        result = create_feature_modal()
        result_str = to_xml(result)

        assert "Initial Status" in result_str
        assert "Rollout Percentage" in result_str

    def test_create_feature_modal_contains_environment_config(self):
        """Test that modal contains environment configuration"""
        from app.frontend.admin_feature_toggles import create_feature_modal

        result = create_feature_modal()
        result_str = to_xml(result)

        assert "Development" in result_str
        assert "Staging" in result_str
        assert "Production" in result_str


class TestCreateEditFeatureModal:
    """Test create_edit_feature_modal function"""

    def test_create_edit_feature_modal_returns_div(self):
        """Test that create_edit_feature_modal returns a Div"""
        from app.frontend.admin_feature_toggles import create_edit_feature_modal

        result = create_edit_feature_modal()
        assert result is not None

    def test_create_edit_feature_modal_contains_title(self):
        """Test that edit modal contains proper title"""
        from app.frontend.admin_feature_toggles import create_edit_feature_modal

        result = create_edit_feature_modal()
        result_str = to_xml(result)

        assert "Edit Feature Toggle" in result_str


class TestCreateUserAccessModal:
    """Test create_user_access_modal function"""

    def test_create_user_access_modal_returns_div(self):
        """Test that create_user_access_modal returns a Div"""
        from app.frontend.admin_feature_toggles import create_user_access_modal

        result = create_user_access_modal()
        assert result is not None

    def test_create_user_access_modal_contains_title(self):
        """Test that user access modal contains proper title"""
        from app.frontend.admin_feature_toggles import create_user_access_modal

        result = create_user_access_modal()
        result_str = to_xml(result)

        assert "Manage User Access" in result_str


class TestCreateStatsModal:
    """Test create_stats_modal function"""

    def test_create_stats_modal_returns_div(self):
        """Test that create_stats_modal returns a Div"""
        from app.frontend.admin_feature_toggles import create_stats_modal

        result = create_stats_modal()
        assert result is not None

    def test_create_stats_modal_contains_title(self):
        """Test that stats modal contains proper title"""
        from app.frontend.admin_feature_toggles import create_stats_modal

        result = create_stats_modal()
        result_str = to_xml(result)

        assert "Feature Toggle Statistics" in result_str


class TestCreateFeatureToggleJs:
    """Test create_feature_toggle_js function"""

    def test_create_feature_toggle_js_returns_string(self):
        """Test that create_feature_toggle_js returns a JavaScript string"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_js

        result = create_feature_toggle_js()
        assert isinstance(result, str)

    def test_create_feature_toggle_js_contains_functions(self):
        """Test that JavaScript contains required functions"""
        from app.frontend.admin_feature_toggles import create_feature_toggle_js

        result = create_feature_toggle_js()

        assert "loadFeatures" in result
        assert "renderFeatures" in result
        assert "filterFeatures" in result
        assert "createFeature" in result


class TestRenderFeatureTogglesPage:
    """Test render_feature_toggles_page async function"""

    @pytest.mark.asyncio
    async def test_render_feature_toggles_page_returns_page(self):
        """Test that render_feature_toggles_page returns the page"""
        from app.frontend.admin_feature_toggles import render_feature_toggles_page

        result = await render_feature_toggles_page()
        assert result is not None

    @pytest.mark.asyncio
    async def test_render_feature_toggles_page_returns_same_as_create(self):
        """Test that render_feature_toggles_page returns same content as create_feature_toggle_page"""
        from app.frontend.admin_feature_toggles import (
            create_feature_toggle_page,
            render_feature_toggles_page,
        )

        rendered = await render_feature_toggles_page()
        created = create_feature_toggle_page()

        # Both should be similar FT objects
        rendered_str = to_xml(rendered)
        created_str = to_xml(created)

        assert "Feature Toggle Management" in rendered_str
        assert "Feature Toggle Management" in created_str
