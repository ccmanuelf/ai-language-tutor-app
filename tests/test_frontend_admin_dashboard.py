"""
Test module for Admin Dashboard Frontend
AI Language Tutor App - Session 107

Tests for app/frontend/admin_dashboard.py module
Target: 100% coverage - completing the final 4% gap (lines 127-128)
"""

from datetime import datetime
from typing import Any, Dict

import pytest
from fasthtml.common import to_xml

from app.frontend.admin_dashboard import (
    _create_action_buttons,
    _create_user_details,
    _create_user_header,
    _format_datetime,
    _get_role_styling,
    _get_status_styling,
    create_add_user_modal,
    create_admin_header,
    create_guest_session_panel,
    create_user_card,
    create_user_management_page,
)


class TestFormatDatetime:
    """Test suite for _format_datetime helper function"""

    def test_format_datetime_with_valid_iso_string(self):
        """Test formatting a valid ISO datetime string"""
        dt_string = "2024-12-12T10:30:00Z"
        result = _format_datetime(dt_string)
        assert result == "2024-12-12 10:30"

    def test_format_datetime_with_none(self):
        """Test formatting when dt_string is None"""
        result = _format_datetime(None)
        assert result == "Unknown"

    def test_format_datetime_with_empty_string(self):
        """Test formatting when dt_string is empty"""
        result = _format_datetime("")
        assert result == "Unknown"

    def test_format_datetime_with_invalid_format(self):
        """Test formatting with invalid datetime format (triggers ValueError)"""
        dt_string = "not-a-valid-datetime"
        result = _format_datetime(dt_string)
        assert result == "Unknown"

    def test_format_datetime_with_non_string_triggers_attribute_error(self):
        """Test formatting with non-string input (triggers AttributeError)"""
        # Pass an integer which will cause AttributeError when calling .replace()
        result = _format_datetime(12345)  # type: ignore
        assert result == "Unknown"

    def test_format_datetime_with_valid_iso_no_z(self):
        """Test formatting valid ISO string without Z suffix"""
        dt_string = "2024-12-12T10:30:00"
        result = _format_datetime(dt_string)
        assert result == "2024-12-12 10:30"


class TestGetRoleStyling:
    """Test suite for _get_role_styling helper function"""

    def test_get_role_styling_admin(self):
        """Test role styling for ADMIN role"""
        user = {"role": "ADMIN"}
        role, color = _get_role_styling(user)
        assert role == "ADMIN"
        assert color == "#dc2626"

    def test_get_role_styling_parent(self):
        """Test role styling for PARENT role"""
        user = {"role": "PARENT"}
        role, color = _get_role_styling(user)
        assert role == "PARENT"
        assert color == "#2563eb"

    def test_get_role_styling_child(self):
        """Test role styling for CHILD role"""
        user = {"role": "CHILD"}
        role, color = _get_role_styling(user)
        assert role == "CHILD"
        assert color == "#16a34a"

    def test_get_role_styling_guest(self):
        """Test role styling for GUEST role"""
        user = {"role": "GUEST"}
        role, color = _get_role_styling(user)
        assert role == "GUEST"
        assert color == "#6b7280"

    def test_get_role_styling_default(self):
        """Test role styling with no role specified (defaults to CHILD)"""
        user = {}
        role, color = _get_role_styling(user)
        assert role == "CHILD"
        assert color == "#16a34a"

    def test_get_role_styling_unknown_role(self):
        """Test role styling with unknown role"""
        user = {"role": "UNKNOWN"}
        role, color = _get_role_styling(user)
        assert role == "UNKNOWN"
        assert color == "#6b7280"


class TestGetStatusStyling:
    """Test suite for _get_status_styling helper function"""

    def test_get_status_styling_active(self):
        """Test status styling for active user"""
        user = {"is_active": True}
        color, text = _get_status_styling(user)
        assert color == "#16a34a"
        assert text == "Active"

    def test_get_status_styling_inactive(self):
        """Test status styling for inactive user"""
        user = {"is_active": False}
        color, text = _get_status_styling(user)
        assert color == "#dc2626"
        assert text == "Inactive"

    def test_get_status_styling_default_active(self):
        """Test status styling defaults to active when not specified"""
        user = {}
        color, text = _get_status_styling(user)
        assert color == "#16a34a"
        assert text == "Active"


class TestCreateUserHeader:
    """Test suite for _create_user_header helper function"""

    def test_create_user_header_with_full_name(self):
        """Test user header with first and last name"""
        user = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe",
        }
        result = _create_user_header(user, "ADMIN", "#dc2626", "#16a34a", "Active")
        result_str = to_xml(result)

        assert "John Doe" in result_str
        assert "john@example.com" in result_str
        assert "ADMIN" in result_str
        assert "Active" in result_str

    def test_create_user_header_username_only(self):
        """Test user header when only username is available"""
        user = {"email": "user@example.com", "username": "testuser"}
        result = _create_user_header(user, "CHILD", "#16a34a", "#16a34a", "Active")
        result_str = to_xml(result)

        assert "testuser" in result_str
        assert "user@example.com" in result_str

    def test_create_user_header_no_email(self):
        """Test user header with missing email"""
        user = {"first_name": "Jane", "last_name": "Smith", "username": "janesmith"}
        result = _create_user_header(user, "PARENT", "#2563eb", "#16a34a", "Active")
        result_str = to_xml(result)

        assert "Jane Smith" in result_str
        assert "No email" in result_str


class TestCreateUserDetails:
    """Test suite for _create_user_details helper function"""

    def test_create_user_details_with_all_fields(self):
        """Test user details with all fields present"""
        user = {
            "user_id": "user123",
            "created_at": "2024-12-01T10:00:00Z",
            "last_login": "2024-12-12T15:30:00Z",
        }
        result = _create_user_details(user)
        result_str = to_xml(result)

        assert "user123" in result_str
        assert "User ID:" in result_str
        assert "Created:" in result_str
        assert "Last Login:" in result_str
        assert "2024-12-01" in result_str
        assert "2024-12-12" in result_str

    def test_create_user_details_without_last_login(self):
        """Test user details when last_login is None"""
        user = {
            "user_id": "user456",
            "created_at": "2024-12-01T10:00:00Z",
            "last_login": None,
        }
        result = _create_user_details(user)
        result_str = to_xml(result)

        assert "user456" in result_str
        # Should not include Last Login section
        assert "Last Login:" not in result_str

    def test_create_user_details_missing_fields(self):
        """Test user details with missing fields"""
        user = {}
        result = _create_user_details(user)
        result_str = to_xml(result)

        assert "N/A" in result_str
        assert "Unknown" in result_str


class TestCreateActionButtons:
    """Test suite for _create_action_buttons helper function"""

    def test_create_action_buttons_admin_user(self):
        """Test action buttons for admin user (delete protected)"""
        user = {"user_id": "admin123"}
        result = _create_action_buttons(user, "ADMIN")
        result_str = to_xml(result)

        assert "Edit" in result_str
        assert "Toggle Status" in result_str
        assert "Protected" in result_str
        assert "disabled" in result_str
        assert "editUser('admin123')" in result_str

    def test_create_action_buttons_regular_user(self):
        """Test action buttons for non-admin user (delete enabled)"""
        user = {"user_id": "user123"}
        result = _create_action_buttons(user, "CHILD")
        result_str = to_xml(result)

        assert "Edit" in result_str
        assert "Toggle Status" in result_str
        assert "Delete" in result_str
        assert "disabled" not in result_str
        assert "deleteUser('user123')" in result_str


class TestCreateUserCard:
    """Test suite for create_user_card function"""

    def test_create_user_card_complete(self):
        """Test creating a complete user card"""
        user = {
            "user_id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "PARENT",
            "is_active": True,
            "created_at": "2024-12-01T10:00:00Z",
            "last_login": "2024-12-12T15:30:00Z",
        }
        result = create_user_card(user)
        result_str = to_xml(result)

        assert "Test User" in result_str
        assert "test@example.com" in result_str
        assert "PARENT" in result_str
        assert "Active" in result_str
        assert "user123" in result_str


class TestCreateAdminHeader:
    """Test suite for create_admin_header function"""

    def test_create_admin_header(self):
        """Test creating admin header"""
        current_user = {
            "user_id": "admin123",
            "username": "admin",
            "email": "admin@example.com",
            "role": "ADMIN",
        }
        result = create_admin_header(current_user)
        result_str = to_xml(result)

        assert "Admin Dashboard" in result_str
        assert "Users" in result_str
        assert "Languages" in result_str
        assert "Features" in result_str
        assert "System" in result_str
        assert "/dashboard/admin/users" in result_str


class TestCreateAddUserModal:
    """Test suite for create_add_user_modal function"""

    def test_create_add_user_modal(self):
        """Test creating add user modal"""
        result = create_add_user_modal()
        result_str = to_xml(result)

        assert "Add New User" in result_str
        assert "First Name:" in result_str
        assert "Last Name:" in result_str
        assert "Email:" in result_str
        assert "Username:" in result_str
        assert "Role:" in result_str
        assert "Password:" in result_str
        assert "Create User" in result_str
        assert "Cancel" in result_str
        assert "addUserModal" in result_str
        assert "newUserFirstName" in result_str


class TestCreateGuestSessionPanel:
    """Test suite for create_guest_session_panel function"""

    def test_create_guest_session_panel_with_active_session(self):
        """Test guest session panel with active guest"""
        guest_info = {"user_id": "guest123", "created_at": "2024-12-12T10:00:00"}
        result = create_guest_session_panel(guest_info)
        result_str = to_xml(result)

        assert "Current Guest Session" in result_str
        assert "guest123" in result_str
        assert "Session Started:" in result_str
        assert "Status: Active" in result_str
        assert "Terminate Session" in result_str

    def test_create_guest_session_panel_without_active_session(self):
        """Test guest session panel without active guest"""
        result = create_guest_session_panel(None)
        result_str = to_xml(result)

        assert "Guest Session Management" in result_str
        assert "No active guest sessions" in result_str
        assert "Create Guest Session" in result_str


class TestCreateUserManagementPage:
    """Test suite for create_user_management_page function"""

    def test_create_user_management_page_with_users(self):
        """Test creating user management page with users"""
        users = [
            {
                "user_id": "admin1",
                "username": "admin",
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": "ADMIN",
                "is_active": True,
                "created_at": "2024-12-01T10:00:00Z",
            },
            {
                "user_id": "parent1",
                "username": "parent",
                "email": "parent@example.com",
                "first_name": "Parent",
                "last_name": "User",
                "role": "PARENT",
                "is_active": True,
                "created_at": "2024-12-01T10:00:00Z",
            },
            {
                "user_id": "child1",
                "username": "child",
                "email": "child@example.com",
                "first_name": "Child",
                "last_name": "User",
                "role": "CHILD",
                "is_active": False,
                "created_at": "2024-12-01T10:00:00Z",
            },
        ]
        current_user = {"user_id": "admin1", "username": "admin", "role": "ADMIN"}

        result = create_user_management_page(users, current_user, guest_info=None)
        result_str = to_xml(result)

        # Check page structure
        assert "Admin Dashboard - User Management" in result_str
        assert "User Management" in result_str

        # Check statistics
        assert "3" in result_str  # Total users
        assert "1" in result_str  # Admin count
        assert "2" in result_str  # Active users (admin + parent)

        # Check user cards
        assert "Admin User" in result_str
        assert "Parent User" in result_str
        assert "Child User" in result_str

        # Check search functionality
        assert "Search users" in result_str
        assert "Add New User" in result_str

    def test_create_user_management_page_empty_users(self):
        """Test creating user management page with no users"""
        users = []
        current_user = {"user_id": "admin1", "username": "admin", "role": "ADMIN"}

        result = create_user_management_page(users, current_user)
        result_str = to_xml(result)

        assert "Admin Dashboard - User Management" in result_str
        assert "0" in result_str  # All counts should be 0

    def test_create_user_management_page_with_guest(self):
        """Test creating user management page with active guest"""
        users = [
            {
                "user_id": "admin1",
                "username": "admin",
                "email": "admin@example.com",
                "role": "ADMIN",
                "is_active": True,
                "created_at": "2024-12-01T10:00:00Z",
            }
        ]
        current_user = {"user_id": "admin1", "username": "admin", "role": "ADMIN"}
        guest_info = {"user_id": "guest123", "created_at": "2024-12-12T10:00:00"}

        result = create_user_management_page(users, current_user, guest_info)
        result_str = to_xml(result)

        assert "Current Guest Session" in result_str
        assert "guest123" in result_str
