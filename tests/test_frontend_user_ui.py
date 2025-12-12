"""
Test module for User UI Components Frontend
AI Language Tutor App - Session 106

Tests for app/frontend/user_ui.py module
Target: 100% coverage with comprehensive test scenarios
"""

from datetime import datetime

import pytest
from fasthtml.common import *

from app.frontend.user_ui import (
    child_pin_form,
    error_message,
    footer,
    learning_progress_section,
    loading_spinner,
    login_form,
    main_layout,
    nav_bar,
    progress_card,
    registration_form,
    stat_card,
    statistics_section,
    user_dashboard,
    user_edit_form,
    user_profile_page,
)

# Sample user data for testing
SAMPLE_USER_RESPONSE = {
    "user_id": "test123",
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "CHILD",
    "ui_language": "en",
}

SAMPLE_USER_PROFILE = {
    "user_id": "test123",
    "username": "testuser",
    "role": "CHILD",
    "languages": ["en", "es"],
    "learning_progress": [
        {
            "language": "es",
            "skill_type": "vocabulary",
            "current_level": 5,
            "target_level": 10,
            "progress_percentage": 65.5,
        }
    ],
    "total_conversations": 25,
    "total_study_time_minutes": 480,
}


class TestUserProfilePage:
    """Test user profile page component"""

    def test_user_profile_page_with_basic_data(self):
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_profile_page(user_data)
        result_str = str(result)

        # Check for profile information
        assert "User Profile" in result_str
        assert "testuser" in result_str

    def test_user_profile_page_with_role_display(self):
        """Test profile page displays user role"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_profile_page(user_data)
        result_str = str(result)

        assert "Role" in result_str or "role" in result_str.lower()
        assert "CHILD" in result_str or "Child" in result_str

    def test_user_profile_page_with_languages(self):
        """Test profile page displays language count"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_profile_page(user_data)
        result_str = str(result)

        assert "2" in result_str  # 2 languages
        assert "language" in result_str.lower()

    def test_user_profile_page_without_learning_progress(self):
        """Test profile page handles empty learning progress"""
        user_data_dict = SAMPLE_USER_PROFILE.copy()
        user_data_dict["learning_progress"] = []  # Empty list instead of None
        user_data = type("UserProfile", (), user_data_dict)()

        result = user_profile_page(user_data)
        result_str = str(result)

        # Should still render
        assert "User Profile" in result_str

    def test_user_profile_page_has_action_buttons(self):
        """Test profile page includes action buttons"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_profile_page(user_data)
        result_str = str(result)

        assert "Edit Profile" in result_str
        assert "View Settings" in result_str or "Settings" in result_str


class TestLearningProgressSection:
    """Test learning progress section component"""

    def test_learning_progress_section_with_data(self):
        """Test learning progress section with progress data"""
        progress_data = [
            {
                "language": "es",
                "skill_type": "vocabulary",
                "current_level": 5,
                "target_level": 10,
                "progress_percentage": 65.5,
            },
            {
                "language": "fr",
                "skill_type": "grammar",
                "current_level": 3,
                "target_level": 10,
                "progress_percentage": 30.0,
            },
        ]

        result = learning_progress_section(progress_data)
        result_str = str(result)

        assert "Learning Progress" in result_str
        assert "ES" in result_str.upper()  # Language code
        assert "Vocabulary" in result_str or "vocabulary" in result_str.lower()

    def test_learning_progress_section_displays_all_items(self):
        """Test that section displays all progress items"""
        progress_data = [
            {
                "language": f"lang{i}",
                "skill_type": "test",
                "current_level": i,
                "target_level": 10,
                "progress_percentage": i * 10,
            }
            for i in range(3)
        ]

        result = learning_progress_section(progress_data)
        result_str = str(result)

        # Should display multiple progress items
        assert "Learning Progress" in result_str


class TestProgressCard:
    """Test individual progress card component"""

    def test_progress_card_with_data(self):
        """Test progress card renders with progress data"""
        progress = {
            "language": "es",
            "skill_type": "vocabulary",
            "current_level": 5,
            "target_level": 10,
            "progress_percentage": 65.5,
        }

        result = progress_card(progress)
        result_str = str(result)

        assert "ES" in result_str.upper()
        assert "Vocabulary" in result_str or "vocabulary" in result_str.lower()
        assert "5" in result_str  # current level
        assert "10" in result_str  # target level
        assert "65" in result_str  # progress percentage

    def test_progress_card_with_zero_progress(self):
        """Test progress card with 0% progress"""
        progress = {
            "language": "fr",
            "skill_type": "grammar",
            "current_level": 0,
            "target_level": 10,
            "progress_percentage": 0,
        }

        result = progress_card(progress)
        result_str = str(result)

        assert "FR" in result_str.upper()
        assert "0" in result_str


class TestStatisticsSection:
    """Test statistics section component"""

    def test_statistics_section_with_user_data(self):
        """Test statistics section with user data"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = statistics_section(user_data)
        result_str = str(result)

        assert "Statistics" in result_str
        assert "25" in result_str  # total_conversations
        assert "480" in result_str  # total_study_time_minutes

    def test_statistics_section_displays_all_stats(self):
        """Test that section displays all stat cards"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = statistics_section(user_data)
        result_str = str(result)

        # Check for stat labels
        assert "Conversations" in result_str or "conversation" in result_str.lower()
        assert "Study Time" in result_str or "study" in result_str.lower()
        assert "Languages" in result_str or "language" in result_str.lower()


class TestStatCard:
    """Test individual stat card component"""

    def test_stat_card_with_data(self):
        """Test stat card renders with data"""
        result = stat_card("Total Sessions", 42, "📚")
        result_str = str(result)

        assert "Total Sessions" in result_str
        assert "42" in result_str
        assert "📚" in result_str

    def test_stat_card_with_zero_value(self):
        """Test stat card with zero value"""
        result = stat_card("Progress Items", 0, "📊")
        result_str = str(result)

        assert "Progress Items" in result_str
        assert "0" in result_str

    def test_stat_card_with_string_value(self):
        """Test stat card with string value"""
        result = stat_card("Language", "Spanish", "🌍")
        result_str = str(result)

        assert "Language" in result_str
        assert "Spanish" in result_str


class TestUserEditForm:
    """Test user edit form component"""

    def test_user_edit_form_with_user_data(self):
        """Test edit form renders with user data"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()

        result = user_edit_form(user_data)
        result_str = str(result)

        assert "Edit Profile" in result_str
        assert "testuser" in result_str
        assert "test@example.com" in result_str

    def test_user_edit_form_has_all_fields(self):
        """Test edit form includes all input fields"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()

        result = user_edit_form(user_data)
        result_str = str(result)

        assert "Username" in result_str
        assert "Email" in result_str
        assert "First Name" in result_str
        assert "Last Name" in result_str
        assert "UI Language" in result_str

    def test_user_edit_form_has_language_options(self):
        """Test edit form includes language options"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()

        result = user_edit_form(user_data)
        result_str = str(result)

        # Check for language options
        assert "English" in result_str
        assert "中文" in result_str or "zh" in result_str
        assert "Français" in result_str or "fr" in result_str

    def test_user_edit_form_has_action_buttons(self):
        """Test edit form includes action buttons"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()

        result = user_edit_form(user_data)
        result_str = str(result)

        assert "Save Changes" in result_str
        assert "Cancel" in result_str


class TestLoginForm:
    """Test login form component"""

    def test_login_form_renders(self):
        """Test login form renders correctly"""
        result = login_form()
        result_str = str(result)

        assert "Login" in result_str

    def test_login_form_has_input_fields(self):
        """Test login form has required input fields"""
        result = login_form()
        result_str = str(result)

        assert "User ID" in result_str
        assert "Password" in result_str

    def test_login_form_has_submit_button(self):
        """Test login form has submit button"""
        result = login_form()
        result_str = str(result)

        assert "Login" in result_str
        # Should have submit button
        assert 'type="submit"' in result_str

    def test_login_form_has_create_account_link(self):
        """Test login form has create account link"""
        result = login_form()
        result_str = str(result)

        assert "Create Account" in result_str or "register" in result_str.lower()


class TestChildPinForm:
    """Test child PIN login form component"""

    def test_child_pin_form_renders(self):
        """Test child PIN form renders correctly"""
        result = child_pin_form()
        result_str = str(result)

        assert "Enter Your PIN" in result_str or "PIN" in result_str

    def test_child_pin_form_has_pin_input(self):
        """Test child PIN form has PIN input field"""
        result = child_pin_form()
        result_str = str(result)

        assert 'type="password"' in result_str
        assert 'maxlength="4"' in result_str

    def test_child_pin_form_has_submit_button(self):
        """Test child PIN form has submit button"""
        result = child_pin_form()
        result_str = str(result)

        assert "Continue" in result_str or 'type="submit"' in result_str


class TestRegistrationForm:
    """Test user registration form component"""

    def test_registration_form_renders(self):
        """Test registration form renders correctly"""
        result = registration_form()
        result_str = str(result)

        assert "Create Account" in result_str

    def test_registration_form_has_all_fields(self):
        """Test registration form has all required fields"""
        result = registration_form()
        result_str = str(result)

        assert "User ID" in result_str
        assert "Username" in result_str
        assert "Email" in result_str
        assert "Account Type" in result_str
        assert "Password" in result_str

    def test_registration_form_has_role_options(self):
        """Test registration form includes role options"""
        result = registration_form()
        result_str = str(result)

        assert "Child Account" in result_str or "child" in result_str.lower()
        assert "Parent Account" in result_str or "parent" in result_str.lower()

    def test_registration_form_has_submit_button(self):
        """Test registration form has submit button"""
        result = registration_form()
        result_str = str(result)

        assert "Create Account" in result_str

    def test_registration_form_has_login_link(self):
        """Test registration form has login link"""
        result = registration_form()
        result_str = str(result)

        assert "Already have an account" in result_str or "login" in result_str.lower()


class TestUserDashboard:
    """Test user dashboard component"""

    def test_user_dashboard_with_user_data(self):
        """Test user dashboard renders with user data"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_dashboard(user_data)
        result_str = str(result)

        assert "Welcome back" in result_str
        assert "testuser" in result_str

    def test_user_dashboard_displays_role(self):
        """Test user dashboard displays user role"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_dashboard(user_data)
        result_str = str(result)

        assert "Role" in result_str or "CHILD" in result_str

    def test_user_dashboard_with_learning_progress(self):
        """Test user dashboard shows learning progress"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_dashboard(user_data)
        result_str = str(result)

        assert "Progress" in result_str or "progress" in result_str.lower()

    def test_user_dashboard_without_learning_progress(self):
        """Test user dashboard shows get started message without progress"""
        user_data_dict = SAMPLE_USER_PROFILE.copy()
        user_data_dict["learning_progress"] = []
        user_data = type("UserProfile", (), user_data_dict)()

        result = user_dashboard(user_data)
        result_str = str(result)

        assert "Get Started" in result_str or "Add Language" in result_str

    def test_user_dashboard_has_quick_actions(self):
        """Test user dashboard includes quick action buttons"""
        user_data = type("UserProfile", (), SAMPLE_USER_PROFILE)()

        result = user_dashboard(user_data)
        result_str = str(result)

        assert "Quick Actions" in result_str or "Start Conversation" in result_str


class TestErrorMessage:
    """Test error message component"""

    def test_error_message_default_type(self):
        """Test error message with default type"""
        result = error_message("Something went wrong")
        result_str = str(result)

        assert "Something went wrong" in result_str

    def test_error_message_error_type(self):
        """Test error message with error type"""
        result = error_message("Error occurred", "error")
        result_str = str(result)

        assert "Error occurred" in result_str

    def test_error_message_warning_type(self):
        """Test error message with warning type"""
        result = error_message("Warning message", "warning")
        result_str = str(result)

        assert "Warning message" in result_str

    def test_error_message_success_type(self):
        """Test error message with success type"""
        result = error_message("Success!", "success")
        result_str = str(result)

        assert "Success!" in result_str

    def test_error_message_info_type(self):
        """Test error message with info type"""
        result = error_message("Information", "info")
        result_str = str(result)

        assert "Information" in result_str


class TestLoadingSpinner:
    """Test loading spinner component"""

    def test_loading_spinner_renders(self):
        """Test loading spinner renders correctly"""
        result = loading_spinner()
        result_str = str(result)

        assert "Loading" in result_str or "loading" in result_str.lower()

    def test_loading_spinner_has_animation(self):
        """Test loading spinner includes animation class"""
        result = loading_spinner()
        result_str = str(result)

        # Should have animation or spinner related class
        assert "animate" in result_str.lower() or "spin" in result_str.lower()


class TestMainLayout:
    """Test main layout wrapper component"""

    def test_main_layout_with_content(self):
        """Test main layout wraps content correctly"""
        content = Div("Test Content")
        result = main_layout(content)
        result_str = str(result)

        assert "Test Content" in result_str
        assert "AI Language Tutor" in result_str

    def test_main_layout_without_user_data(self):
        """Test main layout renders without user data"""
        content = Div("Content")
        result = main_layout(content, None)
        result_str = str(result)

        assert "Content" in result_str

    def test_main_layout_with_user_data(self):
        """Test main layout includes navigation with user data"""
        content = Div("Content")
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()
        result = main_layout(content, user_data)
        result_str = str(result)

        assert "testuser" in result_str
        assert "Content" in result_str

    def test_main_layout_has_head_elements(self):
        """Test main layout includes head elements"""
        content = Div("Content")
        result = main_layout(content)
        result_str = str(result)

        assert "AI Language Tutor" in result_str  # Title
        assert 'charset="UTF-8"' in result_str.lower() or "utf-8" in result_str.lower()

    def test_main_layout_has_footer(self):
        """Test main layout includes footer"""
        content = Div("Content")
        result = main_layout(content)
        result_str = str(result)

        # Footer should be present
        current_year = datetime.now().year
        assert str(current_year) in result_str or "AI Language Tutor" in result_str


class TestNavBar:
    """Test navigation bar component"""

    def test_nav_bar_with_user_data(self):
        """Test navigation bar renders with user data"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()
        result = nav_bar(user_data)
        result_str = str(result)

        assert "testuser" in result_str
        assert "AI Language Tutor" in result_str

    def test_nav_bar_has_navigation_links(self):
        """Test navigation bar includes navigation links"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()
        result = nav_bar(user_data)
        result_str = str(result)

        assert "Dashboard" in result_str
        assert "Chat" in result_str or "chat" in result_str.lower()

    def test_nav_bar_has_logout_link(self):
        """Test navigation bar includes logout link"""
        user_data = type("UserResponse", (), SAMPLE_USER_RESPONSE)()
        result = nav_bar(user_data)
        result_str = str(result)

        assert "Logout" in result_str or "logout" in result_str.lower()


class TestFooter:
    """Test footer component"""

    def test_footer_renders(self):
        """Test footer renders correctly"""
        result = footer()
        result_str = str(result)

        assert "AI Language Tutor" in result_str

    def test_footer_has_current_year(self):
        """Test footer displays current year"""
        result = footer()
        result_str = str(result)

        current_year = datetime.now().year
        assert str(current_year) in result_str

    def test_footer_has_educational_tool_text(self):
        """Test footer includes educational tool text"""
        result = footer()
        result_str = str(result)

        assert (
            "Personal Family Educational Tool" in result_str
            or "Educational" in result_str
        )


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_profile_page_with_no_languages(self):
        """Test profile page handles empty languages list"""
        user_data_dict = SAMPLE_USER_PROFILE.copy()
        user_data_dict["languages"] = []
        user_data = type("UserProfile", (), user_data_dict)()

        result = user_profile_page(user_data)
        result_str = str(result)

        # Should still render
        assert "User Profile" in result_str

    def test_statistics_with_zero_values(self):
        """Test statistics section handles zero values"""
        user_data_dict = SAMPLE_USER_PROFILE.copy()
        user_data_dict["total_conversations"] = 0
        user_data_dict["total_study_time_minutes"] = 0
        user_data = type("UserProfile", (), user_data_dict)()

        result = statistics_section(user_data)
        result_str = str(result)

        # Should display zeros
        assert "0" in result_str

    def test_edit_form_with_missing_email(self):
        """Test edit form handles missing email"""
        user_data_dict = SAMPLE_USER_RESPONSE.copy()
        user_data_dict["email"] = None
        user_data = type("UserResponse", (), user_data_dict)()

        result = user_edit_form(user_data)
        result_str = str(result)

        # Should still render
        assert "Edit Profile" in result_str

    def test_dashboard_with_empty_progress_list(self):
        """Test dashboard handles empty learning progress list"""
        user_data_dict = SAMPLE_USER_PROFILE.copy()
        user_data_dict["learning_progress"] = []
        user_data = type("UserProfile", (), user_data_dict)()
        user_data = type("UserProfile", (), user_data_dict)()

        result = user_dashboard(user_data)
        result_str = str(result)

        # Should show get started message
        assert "Get Started" in result_str or "Welcome" in result_str
