"""
Tests for app/frontend/layout.py
Coverage target: 41.67% → 100.00%
"""

import pytest
from fasthtml.common import to_xml

from app.frontend.layout import (
    create_admin_header,
    create_admin_sidebar,
    create_alert,
    create_button,
    create_card,
    create_footer,
    create_form_group,
    create_grid,
    create_header,
    create_layout,
    create_status_indicator,
)


class TestCreateHeader:
    """Test create_header function"""

    def test_create_header_home_active(self):
        """Test header with home page active"""
        result = create_header("home")
        result_str = to_xml(result)
        assert "Home" in result_str
        assert "Profile" in result_str
        assert "Conversation" in result_str
        assert "Progress" in result_str


class TestCreateFooter:
    """Test create_footer function"""

    def test_create_footer(self):
        """Test footer creation"""
        result = create_footer()
        result_str = to_xml(result)
        assert "AI Language Tutor" in result_str
        assert "Personal Family Educational Tool" in result_str


class TestCreateLayout:
    """Test create_layout function"""

    def test_create_layout(self):
        """Test complete page layout"""
        from fasthtml.common import Div

        content = Div("Test content")
        result = create_layout(content, current_page="home", title="Test Page")
        result_str = to_xml(result)
        assert "Test Page" in result_str
        assert "Test content" in result_str


class TestCreateCard:
    """Test create_card function"""

    def test_create_card_with_title(self):
        """Test card creation with title"""
        from fasthtml.common import P

        content = P("Card content")
        result = create_card(content, title="Test Card")
        result_str = to_xml(result)
        assert "Test Card" in result_str
        assert "Card content" in result_str

    def test_create_card_without_title(self):
        """Test card creation without title"""
        from fasthtml.common import P

        content = P("Card content")
        result = create_card(content)
        result_str = to_xml(result)
        assert "Card content" in result_str

    def test_create_card_with_list_content(self):
        """Test card creation with list of content items (covers line 87)"""
        from fasthtml.common import Div, P

        content = [P("Item 1"), P("Item 2"), Div("Item 3")]
        result = create_card(content, title="Multi-item Card")
        result_str = to_xml(result)
        assert "Multi-item Card" in result_str
        assert "Item 1" in result_str
        assert "Item 2" in result_str
        assert "Item 3" in result_str


class TestCreateGrid:
    """Test create_grid function (covers lines 148-155)"""

    def test_create_grid_2_columns(self):
        """Test grid creation with 2 columns"""
        from fasthtml.common import Div

        items = [Div("Item 1"), Div("Item 2")]
        result = create_grid(items, columns=2)
        result_str = to_xml(result)
        assert "Item 1" in result_str
        assert "Item 2" in result_str
        assert "grid-2" in result_str

    def test_create_grid_3_columns(self):
        """Test grid creation with 3 columns"""
        from fasthtml.common import Div

        items = [Div("Item 1"), Div("Item 2"), Div("Item 3")]
        result = create_grid(items, columns=3)
        result_str = to_xml(result)
        assert "grid-3" in result_str


class TestCreateStatusIndicator:
    """Test create_status_indicator function (covers lines 84, 89)"""

    def test_create_status_indicator_success(self):
        """Test status indicator with success status"""
        result = create_status_indicator("Ready", status="success")
        result_str = to_xml(result)
        assert "Ready" in result_str
        assert "✅" in result_str

    def test_create_status_indicator_warning(self):
        """Test status indicator with warning status"""
        result = create_status_indicator("Warning", status="warning")
        result_str = to_xml(result)
        assert "Warning" in result_str
        assert "⚠️" in result_str

    def test_create_status_indicator_error(self):
        """Test status indicator with error status"""
        result = create_status_indicator("Error", status="error")
        result_str = to_xml(result)
        assert "Error" in result_str
        assert "❌" in result_str

    def test_create_status_indicator_connected(self):
        """Test status indicator with connected status"""
        result = create_status_indicator("Connected", status="connected")
        result_str = to_xml(result)
        assert "Connected" in result_str
        assert "🟢" in result_str

    def test_create_status_indicator_unknown(self):
        """Test status indicator with unknown status (covers default case)"""
        result = create_status_indicator("Unknown", status="unknown_status")
        result_str = to_xml(result)
        assert "Unknown" in result_str
        assert "⚠️" in result_str  # Default icon


class TestCreateAlert:
    """Test create_alert function (covers lines 102-117)"""

    def test_create_alert_success(self):
        """Test alert with success type"""
        result = create_alert("Success message", alert_type="success")
        result_str = to_xml(result)
        assert "Success message" in result_str
        assert "✅" in result_str

    def test_create_alert_warning(self):
        """Test alert with warning type"""
        result = create_alert("Warning message", alert_type="warning")
        result_str = to_xml(result)
        assert "Warning message" in result_str
        assert "⚠️" in result_str

    def test_create_alert_error(self):
        """Test alert with error type"""
        result = create_alert("Error message", alert_type="error")
        result_str = to_xml(result)
        assert "Error message" in result_str
        assert "❌" in result_str

    def test_create_alert_info(self):
        """Test alert with info type"""
        result = create_alert("Info message", alert_type="info")
        result_str = to_xml(result)
        assert "Info message" in result_str
        assert "ℹ️" in result_str

    def test_create_alert_unknown(self):
        """Test alert with unknown type (covers default case)"""
        result = create_alert("Message", alert_type="unknown")
        result_str = to_xml(result)
        assert "Message" in result_str
        assert "ℹ️" in result_str  # Default icon


class TestCreateFormGroup:
    """Test create_form_group function (covers lines 122-129)"""

    def test_create_form_group_with_help_text(self):
        """Test form group with help text"""
        from fasthtml.common import Input

        input_elem = Input(type="text", name="test")
        result = create_form_group("Test Label", input_elem, help_text="Help text here")
        result_str = to_xml(result)
        assert "Test Label" in result_str
        assert "Help text here" in result_str

    def test_create_form_group_without_help_text(self):
        """Test form group without help text"""
        from fasthtml.common import Input

        input_elem = Input(type="text", name="test")
        result = create_form_group("Test Label", input_elem)
        result_str = to_xml(result)
        assert "Test Label" in result_str


class TestCreateButton:
    """Test create_button function (covers lines 134-141)"""

    def test_create_button_primary(self):
        """Test primary button"""
        result = create_button("Click Me", button_type="primary")
        result_str = to_xml(result)
        assert "Click Me" in result_str
        assert "btn-primary" in result_str

    def test_create_button_with_onclick(self):
        """Test button with onclick handler"""
        result = create_button(
            "Click Me", button_type="primary", onclick="alert('test')"
        )
        result_str = to_xml(result)
        assert "Click Me" in result_str
        assert "alert('test')" in result_str

    def test_create_button_secondary(self):
        """Test secondary button"""
        result = create_button("Cancel", button_type="secondary")
        result_str = to_xml(result)
        assert "Cancel" in result_str
        assert "btn-secondary" in result_str


class TestCreateAdminSidebar:
    """Test create_admin_sidebar function (covers lines 162-214)"""

    def test_create_admin_sidebar_users_active(self):
        """Test admin sidebar with users page active"""
        result = create_admin_sidebar(current_page="users")
        result_str = to_xml(result)
        assert "Admin Panel" in result_str
        assert "User Management" in result_str
        assert "Language Config" in result_str
        assert "Feature Toggles" in result_str
        assert "AI Models" in result_str
        assert "Scenarios" in result_str  # Label is "Scenarios & Content"
        assert "content processing" in result_str  # From description
        assert "System Status" in result_str
        assert "Analytics" in result_str

    def test_create_admin_sidebar_languages_active(self):
        """Test admin sidebar with languages page active"""
        result = create_admin_sidebar(current_page="languages")
        result_str = to_xml(result)
        assert "Language Config" in result_str

    def test_create_admin_sidebar_features_active(self):
        """Test admin sidebar with features page active"""
        result = create_admin_sidebar(current_page="features")
        result_str = to_xml(result)
        assert "Feature Toggles" in result_str

    def test_create_admin_sidebar_ai_models_active(self):
        """Test admin sidebar with AI models page active"""
        result = create_admin_sidebar(current_page="ai_models")
        result_str = to_xml(result)
        assert "AI Models" in result_str

    def test_create_admin_sidebar_scenarios_active(self):
        """Test admin sidebar with scenarios page active"""
        result = create_admin_sidebar(current_page="scenarios")
        result_str = to_xml(result)
        assert "Scenarios" in result_str  # Label is "Scenarios & Content"
        assert "content processing" in result_str  # From description

    def test_create_admin_sidebar_system_active(self):
        """Test admin sidebar with system page active"""
        result = create_admin_sidebar(current_page="system")
        result_str = to_xml(result)
        assert "System Status" in result_str

    def test_create_admin_sidebar_analytics_active(self):
        """Test admin sidebar with analytics page active"""
        result = create_admin_sidebar(current_page="analytics")
        result_str = to_xml(result)
        assert "Analytics" in result_str


class TestCreateAdminHeader:
    """Test create_admin_header function (covers lines 268-274)"""

    def test_create_admin_header_with_full_name(self):
        """Test admin header with user's full name"""
        user = {"first_name": "John", "last_name": "Doe", "username": "johndoe"}
        result = create_admin_header(user, page_title="Dashboard")
        result_str = to_xml(result)
        assert "Dashboard" in result_str
        assert "John Doe" in result_str

    def test_create_admin_header_with_username_only(self):
        """Test admin header when first/last name missing (uses username)"""
        user = {"first_name": "", "last_name": "", "username": "johndoe"}
        result = create_admin_header(user, page_title="Dashboard")
        result_str = to_xml(result)
        assert "johndoe" in result_str

    def test_create_admin_header_no_name_fields(self):
        """Test admin header with missing name fields (uses default)"""
        user = {"username": "admin"}
        result = create_admin_header(user, page_title="Settings")
        result_str = to_xml(result)
        assert "Settings" in result_str
        assert "admin" in result_str

    def test_create_admin_header_includes_dropdown_script(self):
        """Test that admin header includes dropdown JavaScript"""
        user = {"username": "admin", "first_name": "Admin", "last_name": "User"}
        result = create_admin_header(user, page_title="Dashboard")
        result_str = to_xml(result)
        assert "toggleUserMenu" in result_str
        assert "Profile" in result_str
        assert "Return to App" in result_str
        assert "Logout" in result_str
