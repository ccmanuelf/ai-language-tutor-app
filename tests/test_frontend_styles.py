"""
Tests for app/frontend/styles.py
Target: 100% coverage (9 statements, 0 branches)
"""

import pytest
from fasthtml.common import Style


class TestLoadStyles:
    """Test load_styles function"""

    def test_load_styles_returns_style_object(self):
        """Test that load_styles returns a Style object"""
        from app.frontend.styles import load_styles

        result = load_styles()

        assert isinstance(result, type(Style("")))

    def test_load_styles_contains_css_content(self):
        """Test that load_styles returns non-empty CSS content"""
        from app.frontend.styles import load_styles

        result = load_styles()

        # Convert to string to check content
        result_str = str(result)
        assert len(result_str) > 0
        assert "body" in result_str or "root" in result_str or "container" in result_str

    def test_load_styles_contains_color_variables(self):
        """Test that styles include CSS custom properties"""
        from app.frontend.styles import load_styles

        result = load_styles()
        result_str = str(result)

        # Check for CSS variables
        assert "--primary-color" in result_str or "var(--" in result_str

    def test_load_styles_contains_responsive_design(self):
        """Test that styles include responsive design media queries"""
        from app.frontend.styles import load_styles

        result = load_styles()
        result_str = str(result)

        # Check for media queries
        assert "@media" in result_str


class TestGetStatusClass:
    """Test get_status_class utility function"""

    def test_get_status_class_success(self):
        """Test get_status_class with 'success' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("success")
        assert result == "status-success"

    def test_get_status_class_warning(self):
        """Test get_status_class with 'warning' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("warning")
        assert result == "status-warning"

    def test_get_status_class_error(self):
        """Test get_status_class with 'error' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("error")
        assert result == "status-error"

    def test_get_status_class_connected(self):
        """Test get_status_class with 'connected' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("connected")
        assert result == "status-success"

    def test_get_status_class_disconnected(self):
        """Test get_status_class with 'disconnected' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("disconnected")
        assert result == "status-error"

    def test_get_status_class_ready(self):
        """Test get_status_class with 'ready' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("ready")
        assert result == "status-success"

    def test_get_status_class_loading(self):
        """Test get_status_class with 'loading' status"""
        from app.frontend.styles import get_status_class

        result = get_status_class("loading")
        assert result == "status-warning"

    def test_get_status_class_unknown(self):
        """Test get_status_class with unknown status (default)"""
        from app.frontend.styles import get_status_class

        result = get_status_class("unknown_status")
        assert result == "status-warning"

    def test_get_status_class_case_insensitive(self):
        """Test get_status_class is case insensitive"""
        from app.frontend.styles import get_status_class

        result_upper = get_status_class("SUCCESS")
        result_lower = get_status_class("success")
        result_mixed = get_status_class("SuCcEsS")

        assert result_upper == result_lower == result_mixed == "status-success"


class TestGetAlertClass:
    """Test get_alert_class utility function"""

    def test_get_alert_class_success(self):
        """Test get_alert_class with 'success' type"""
        from app.frontend.styles import get_alert_class

        result = get_alert_class("success")
        assert result == "alert-success"

    def test_get_alert_class_warning(self):
        """Test get_alert_class with 'warning' type"""
        from app.frontend.styles import get_alert_class

        result = get_alert_class("warning")
        assert result == "alert-warning"

    def test_get_alert_class_error(self):
        """Test get_alert_class with 'error' type"""
        from app.frontend.styles import get_alert_class

        result = get_alert_class("error")
        assert result == "alert-error"

    def test_get_alert_class_info(self):
        """Test get_alert_class with 'info' type"""
        from app.frontend.styles import get_alert_class

        result = get_alert_class("info")
        assert result == "alert-warning"

    def test_get_alert_class_unknown(self):
        """Test get_alert_class with unknown type (default)"""
        from app.frontend.styles import get_alert_class

        result = get_alert_class("unknown_type")
        assert result == "alert-warning"

    def test_get_alert_class_case_insensitive(self):
        """Test get_alert_class is case insensitive"""
        from app.frontend.styles import get_alert_class

        result_upper = get_alert_class("ERROR")
        result_lower = get_alert_class("error")
        result_mixed = get_alert_class("ErRoR")

        assert result_upper == result_lower == result_mixed == "alert-error"
