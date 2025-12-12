"""
Test module for Admin Learning Analytics Frontend
AI Language Tutor App - Session 106

Tests for app/frontend/admin_learning_analytics.py module
Target: 100% coverage with comprehensive test scenarios
"""

import pytest
from fasthtml.common import *

from app.frontend.admin_learning_analytics import (
    admin_analytics_scripts,
    admin_learning_analytics_page,
    admin_learning_analytics_page_with_scripts,
    admin_learning_analytics_styles,
    create_advanced_settings_section,
    create_algorithm_config_section,
    create_gamification_config_section,
    create_system_analytics_section,
    create_thresholds_config_section,
)


class TestAdminLearningAnalyticsStyles:
    """Test admin learning analytics CSS styles"""

    def test_admin_learning_analytics_styles_returns_style(self):
        """Test that styles function returns a Style element"""
        result = admin_learning_analytics_styles()
        result_str = str(result)
        assert "<style>" in result_str.lower()

    def test_admin_learning_analytics_styles_contains_css_classes(self):
        """Test that CSS contains expected class definitions"""
        result = admin_learning_analytics_styles()
        css_content = str(result)

        # Check for main container classes
        assert ".admin-analytics-page" in css_content
        assert ".admin-analytics-container" in css_content
        assert ".admin-header" in css_content

        # Check for configuration section classes
        assert ".config-sections" in css_content
        assert ".config-section" in css_content
        assert ".section-header" in css_content

        # Check for form classes
        assert ".config-form" in css_content
        assert ".form-grid" in css_content
        assert ".form-group" in css_content

        # Check for algorithm-specific classes
        assert ".algorithm-grid" in css_content
        assert ".algorithm-param" in css_content

        # Check for button classes
        assert ".btn-primary" in css_content
        assert ".btn-secondary" in css_content
        assert ".btn-danger" in css_content

    def test_admin_learning_analytics_styles_contains_responsive_design(self):
        """Test that CSS includes responsive design media queries"""
        result = admin_learning_analytics_styles()
        css_content = str(result)

        assert "@media (max-width: 768px)" in css_content

    def test_admin_learning_analytics_styles_contains_animations(self):
        """Test that CSS includes animation definitions"""
        result = admin_learning_analytics_styles()
        css_content = str(result)

        assert ".fade-in" in css_content
        assert "@keyframes fadeIn" in css_content


class TestSystemAnalyticsSection:
    """Test system analytics section component"""

    def test_create_system_analytics_section_with_default_data(self):
        """Test creating system analytics section with default stats"""
        system_stats = {
            "total_users": 45,
            "total_sessions": 1250,
            "total_study_time": 34500,
            "avg_accuracy": 76.8,
            "total_items": 15800,
            "avg_mastery": 0.68,
        }

        result = create_system_analytics_section(system_stats)
        result_str = str(result)

        # Check section title
        assert "System Analytics Overview" in result_str

        # Check for stat values
        assert "45" in result_str  # total_users
        assert "1,250" in result_str  # total_sessions formatted
        assert "34,500" in result_str  # total_study_time formatted
        assert "76.8%" in result_str  # avg_accuracy
        assert "15,800" in result_str  # total_items formatted

    def test_create_system_analytics_section_with_missing_values(self):
        """Test section handles missing stat values gracefully"""
        system_stats = {}

        result = create_system_analytics_section(system_stats)
        result_str = str(result)

        # Should still render without errors
        assert "System Analytics Overview" in result_str
        assert "Active Users" in result_str

    def test_create_system_analytics_section_contains_all_metrics(self):
        """Test section includes all expected metrics"""
        system_stats = {
            "total_users": 100,
            "total_sessions": 5000,
            "total_study_time": 50000,
            "avg_accuracy": 85.5,
            "total_items": 20000,
            "avg_mastery": 0.75,
            "mastered_items": 15000,
        }

        result = create_system_analytics_section(system_stats)
        result_str = str(result)

        assert "Active Users" in result_str
        assert "Learning Sessions" in result_str
        assert "Study Minutes" in result_str
        assert "Average Accuracy" in result_str
        assert "Learning Items" in result_str
        assert "Average Mastery" in result_str


class TestAlgorithmConfigSection:
    """Test spaced repetition algorithm configuration section"""

    def test_create_algorithm_config_section_with_default_config(self):
        """Test algorithm config section with default configuration"""
        config = {
            "initial_ease_factor": 2.5,
            "minimum_ease_factor": 1.3,
            "maximum_ease_factor": 3.0,
            "ease_factor_change": 0.15,
            "initial_interval_days": 1,
            "graduation_interval_days": 4,
            "easy_interval_days": 7,
            "maximum_interval_days": 365,
        }

        result = create_algorithm_config_section(config)
        result_str = str(result)

        # Check section title
        assert "Spaced Repetition Algorithm" in result_str

        # Check for config parameters
        assert "Initial Ease Factor" in result_str
        assert "Initial Interval (Days)" in result_str
        assert "Graduation Interval (Days)" in result_str
        assert "Easy Interval (Days)" in result_str
        assert "Maximum Interval (Days)" in result_str

        # Check for config values
        assert "2.5" in result_str
        assert "365" in result_str

    def test_create_algorithm_config_section_contains_form(self):
        """Test that section contains a form element"""
        config = {"initial_ease_factor": 2.5}

        result = create_algorithm_config_section(config)
        result_str = str(result)

        # Check for form elements
        assert "<form" in result_str.lower()
        assert 'method="post"' in result_str.lower()
        assert "/api/admin/learning-analytics/algorithm-config" in result_str

    def test_create_algorithm_config_section_has_input_fields(self):
        """Test that section has input fields for each parameter"""
        config = {
            "initial_ease_factor": 2.5,
            "initial_interval_days": 1,
            "ease_factor_change": 0.15,
        }

        result = create_algorithm_config_section(config)
        result_str = str(result)

        # Check for input fields
        assert 'name="initial_ease_factor"' in result_str
        assert 'name="initial_interval_days"' in result_str
        assert 'name="ease_factor_change"' in result_str

    def test_create_algorithm_config_section_has_buttons(self):
        """Test that section has action buttons"""
        config = {}

        result = create_algorithm_config_section(config)
        result_str = str(result)

        assert "Reset to Defaults" in result_str
        assert "Save Algorithm Settings" in result_str


class TestGamificationConfigSection:
    """Test gamification settings configuration section"""

    def test_create_gamification_config_section_with_default_config(self):
        """Test gamification config section with default settings"""
        config = {
            "points_per_correct": 10,
            "points_per_streak_day": 5,
            "points_per_goal_achieved": 100,
            "daily_goal_default": 30,
        }

        result = create_gamification_config_section(config)
        result_str = str(result)

        # Check section title
        assert "Gamification Settings" in result_str

        # Check for config parameters
        assert "Points per Correct Answer" in result_str
        assert "Points per Streak Day" in result_str
        assert "Points per Goal Achievement" in result_str
        assert "Default Daily Goal (minutes)" in result_str

    def test_create_gamification_config_section_has_achievement_toggles(self):
        """Test that section includes achievement toggle checkboxes"""
        config = {}

        result = create_gamification_config_section(config)
        result_str = str(result)

        # Check for achievement settings
        assert "Achievement Settings" in result_str
        assert "Enable streak achievements" in result_str
        assert "Enable vocabulary achievements" in result_str
        assert "Enable mastery achievements" in result_str
        assert "Enable goal achievements" in result_str

    def test_create_gamification_config_section_contains_form(self):
        """Test that section contains form with correct action"""
        config = {}

        result = create_gamification_config_section(config)
        result_str = str(result)

        assert "<form" in result_str.lower()
        assert "/api/admin/learning-analytics/gamification-config" in result_str

    def test_create_gamification_config_section_has_action_buttons(self):
        """Test that section has preview and save buttons"""
        config = {}

        result = create_gamification_config_section(config)
        result_str = str(result)

        assert "Preview Changes" in result_str
        assert "Save Gamification Settings" in result_str


class TestThresholdsConfigSection:
    """Test performance thresholds configuration section"""

    def test_create_thresholds_config_section_with_default_config(self):
        """Test thresholds config section with default settings"""
        config = {
            "mastery_threshold": 0.85,
            "review_threshold": 0.7,
            "difficulty_threshold": 0.5,
            "retention_threshold": 0.8,
        }

        result = create_thresholds_config_section(config)
        result_str = str(result)

        # Check section title
        assert "Performance Thresholds" in result_str

        # Check for threshold parameters
        assert "Mastery Threshold" in result_str
        assert "Review Threshold" in result_str
        assert "Difficulty Threshold" in result_str
        assert "Retention Threshold" in result_str

    def test_create_thresholds_config_section_has_input_fields(self):
        """Test that section has input fields with proper ranges"""
        config = {
            "mastery_threshold": 0.85,
            "review_threshold": 0.7,
        }

        result = create_thresholds_config_section(config)
        result_str = str(result)

        # Check for input fields with names
        assert 'name="mastery_threshold"' in result_str
        assert 'name="review_threshold"' in result_str
        assert 'name="difficulty_threshold"' in result_str
        assert 'name="retention_threshold"' in result_str

    def test_create_thresholds_config_section_contains_form(self):
        """Test that section contains form with correct action"""
        config = {}

        result = create_thresholds_config_section(config)
        result_str = str(result)

        assert "<form" in result_str.lower()
        assert "/api/admin/learning-analytics/thresholds-config" in result_str

    def test_create_thresholds_config_section_has_buttons(self):
        """Test that section has action buttons"""
        config = {}

        result = create_thresholds_config_section(config)
        result_str = str(result)

        assert "Run Threshold Analysis" in result_str
        assert "Save Threshold Settings" in result_str


class TestAdvancedSettingsSection:
    """Test advanced settings configuration section"""

    def test_create_advanced_settings_section_structure(self):
        """Test advanced settings section basic structure"""
        result = create_advanced_settings_section()
        result_str = str(result)

        # Check section title
        assert "Advanced Settings" in result_str

        # Check for warning message
        assert "⚠️" in result_str or "Advanced configuration options" in result_str

    def test_create_advanced_settings_section_has_data_retention_options(self):
        """Test that section includes data retention settings"""
        result = create_advanced_settings_section()
        result_str = str(result)

        assert "Analytics Data Retention (days)" in result_str
        assert "30 days" in result_str
        assert "90 days" in result_str
        assert "365 days" in result_str

    def test_create_advanced_settings_section_has_performance_method(self):
        """Test that section includes performance calculation method"""
        result = create_advanced_settings_section()
        result_str = str(result)

        assert "Performance Calculation Method" in result_str
        assert "Weighted Average" in result_str
        assert "Simple Average" in result_str
        assert "Exponential Smoothing" in result_str

    def test_create_advanced_settings_section_has_archive_option(self):
        """Test that section includes auto-archive option"""
        result = create_advanced_settings_section()
        result_str = str(result)

        assert "Auto-Archive Inactive Items" in result_str

    def test_create_advanced_settings_section_has_debug_logging(self):
        """Test that section includes debug logging option"""
        result = create_advanced_settings_section()
        result_str = str(result)

        assert "Enable Debug Logging" in result_str

    def test_create_advanced_settings_section_has_system_actions(self):
        """Test that section includes system action buttons"""
        result = create_advanced_settings_section()
        result_str = str(result)

        assert "System Actions" in result_str
        assert "Export Configuration" in result_str
        assert "Import Configuration" in result_str
        assert "Reset All Settings" in result_str
        assert "Save Advanced Settings" in result_str


class TestAdminAnalyticsScripts:
    """Test JavaScript functions for admin analytics"""

    def test_admin_analytics_scripts_returns_script(self):
        """Test that scripts function returns a Script element"""
        result = admin_analytics_scripts()
        result_str = str(result)
        assert "<script>" in result_str.lower()

    def test_admin_analytics_scripts_contains_reset_function(self):
        """Test that scripts include resetAlgorithmDefaults function"""
        result = admin_analytics_scripts()
        script_content = str(result)

        assert "function resetAlgorithmDefaults()" in script_content

    def test_admin_analytics_scripts_contains_confirm_reset_function(self):
        """Test that scripts include confirmResetAll function"""
        result = admin_analytics_scripts()
        script_content = str(result)

        assert "function confirmResetAll()" in script_content

    def test_admin_analytics_scripts_contains_export_function(self):
        """Test that scripts include exportConfiguration function"""
        result = admin_analytics_scripts()
        script_content = str(result)

        assert "function exportConfiguration()" in script_content

    def test_admin_analytics_scripts_contains_form_handling(self):
        """Test that scripts include form submission handling"""
        result = admin_analytics_scripts()
        script_content = str(result)

        assert "addEventListener('submit'" in script_content
        assert "querySelectorAll('form')" in script_content

    def test_admin_analytics_scripts_contains_default_values(self):
        """Test that scripts include default configuration values"""
        result = admin_analytics_scripts()
        script_content = str(result)

        assert "initial_ease_factor: 2.5" in script_content
        assert "initial_interval_days: 1" in script_content
        assert "maximum_interval_days: 365" in script_content


class TestAdminLearningAnalyticsPage:
    """Test main admin learning analytics page"""

    def test_admin_learning_analytics_page_with_defaults(self):
        """Test page renders with default configuration"""
        result = admin_learning_analytics_page()
        result_str = str(result)

        # Check page structure
        assert "Learning Analytics Configuration" in result_str
        assert "Configure spaced repetition algorithms" in result_str

    def test_admin_learning_analytics_page_with_custom_config(self):
        """Test page renders with custom configuration"""
        custom_config = {
            "initial_ease_factor": 3.0,
            "initial_interval_days": 2,
            "maximum_interval_days": 500,
            "points_per_correct": 20,
        }

        custom_stats = {
            "total_users": 100,
            "total_sessions": 5000,
        }

        result = admin_learning_analytics_page(custom_config, custom_stats)
        result_str = str(result)

        # Check that custom values appear
        assert "100" in result_str  # total_users
        assert "5,000" in result_str  # total_sessions

    def test_admin_learning_analytics_page_contains_all_sections(self):
        """Test page includes all configuration sections"""
        result = admin_learning_analytics_page()
        result_str = str(result)

        # Check for all major sections
        assert "System Analytics Overview" in result_str
        assert "Spaced Repetition Algorithm" in result_str
        assert "Gamification Settings" in result_str
        assert "Performance Thresholds" in result_str
        assert "Advanced Settings" in result_str

    def test_admin_learning_analytics_page_has_header(self):
        """Test page has proper header structure"""
        result = admin_learning_analytics_page()
        result_str = str(result)

        assert "Learning Analytics Configuration" in result_str
        # Check for breadcrumb (flexible to handle different formatting)
        assert (
            "Dashboard" in result_str
            and "Admin" in result_str
            and "Learning Analytics" in result_str
        )

    def test_admin_learning_analytics_page_has_styles(self):
        """Test page includes CSS styles"""
        result = admin_learning_analytics_page()
        result_str = str(result)

        # The styles should be included via admin_learning_analytics_styles()
        assert (
            ".admin-analytics-page" in result_str
            or "admin-analytics-page" in result_str
        )


class TestAdminLearningAnalyticsPageWithScripts:
    """Test admin learning analytics page with JavaScript"""

    def test_page_with_scripts_includes_styles(self):
        """Test page with scripts includes CSS styles"""
        result = admin_learning_analytics_page_with_scripts()
        result_str = str(result)

        assert (
            ".admin-analytics-page" in result_str
            or "admin-analytics-page" in result_str
        )

    def test_page_with_scripts_includes_javascript(self):
        """Test page with scripts includes JavaScript functions"""
        result = admin_learning_analytics_page_with_scripts()
        result_str = str(result)

        assert "<script" in result_str.lower()
        assert "function resetAlgorithmDefaults()" in result_str

    def test_page_with_scripts_accepts_custom_config(self):
        """Test page with scripts accepts custom config and stats"""
        custom_config = {
            "initial_ease_factor": 2.8,
            "points_per_correct": 15,
        }

        custom_stats = {
            "total_users": 75,
            "total_sessions": 3000,
        }

        result = admin_learning_analytics_page_with_scripts(custom_config, custom_stats)
        result_str = str(result)

        # Check custom values appear
        assert "75" in result_str
        assert "3,000" in result_str

    def test_page_with_scripts_contains_all_content(self):
        """Test page with scripts has all configuration sections"""
        result = admin_learning_analytics_page_with_scripts()
        result_str = str(result)

        assert "Learning Analytics Configuration" in result_str
        assert "System Analytics Overview" in result_str
        assert "Spaced Repetition Algorithm" in result_str
        assert "Gamification Settings" in result_str


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_system_analytics_with_zero_values(self):
        """Test system analytics handles zero values"""
        system_stats = {
            "total_users": 0,
            "total_sessions": 0,
            "total_study_time": 0,
            "avg_accuracy": 0,
        }

        result = create_system_analytics_section(system_stats)
        result_str = str(result)

        # Should render without errors
        assert "System Analytics Overview" in result_str

    def test_algorithm_config_with_empty_dict(self):
        """Test algorithm config handles empty configuration"""
        config = {}

        result = create_algorithm_config_section(config)
        result_str = str(result)

        # Should use default values
        assert "Spaced Repetition Algorithm" in result_str
        assert "Initial Ease Factor" in result_str

    def test_gamification_config_with_none_values(self):
        """Test gamification config handles None values"""
        config = {
            "points_per_correct": None,
            "points_per_streak_day": None,
        }

        result = create_gamification_config_section(config)
        result_str = str(result)

        # Should render without errors
        assert "Gamification Settings" in result_str

    def test_page_renders_without_config_or_stats(self):
        """Test page renders when both config and stats are None"""
        result = admin_learning_analytics_page(None, None)
        result_str = str(result)

        # Should use defaults and render successfully
        assert "Learning Analytics Configuration" in result_str
        assert "System Analytics Overview" in result_str
