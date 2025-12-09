"""
Unit tests for Budget Manager User Control functionality

Tests the new AI provider selection with user preferences and budget control:
- AIProviderSettings model
- BudgetExceededWarning creation
- BudgetThresholdAlert creation
- Budget manager threshold monitoring
- AI router preferred provider selection
- User model AI settings methods
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.models.schemas import (
    AIProviderSettings,
    BudgetAlertSeverity,
    BudgetExceededWarning,
    BudgetThresholdAlert,
    ProviderSelectionMode,
)
from app.services.budget_manager import BudgetAlert, BudgetStatus, budget_manager


class TestAIProviderSettings:
    """Test AIProviderSettings Pydantic model"""

    def test_default_settings(self):
        """Test default AI provider settings"""
        settings = AIProviderSettings()

        assert settings.provider_selection_mode == ProviderSelectionMode.BALANCED
        assert settings.default_provider == "claude"
        assert settings.enforce_budget_limits is True
        assert settings.budget_override_allowed is True
        assert settings.alert_on_budget_threshold == 0.80
        assert settings.notify_on_provider_change is True
        assert settings.notify_on_budget_alert is True
        assert settings.auto_fallback_to_ollama is False
        assert settings.prefer_local_when_available is False

    def test_custom_settings(self):
        """Test custom AI provider settings"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.USER_CHOICE,
            default_provider="mistral",
            enforce_budget_limits=False,
            budget_override_allowed=False,
            alert_on_budget_threshold=0.75,
            auto_fallback_to_ollama=True,
        )

        assert settings.provider_selection_mode == ProviderSelectionMode.USER_CHOICE
        assert settings.default_provider == "mistral"
        assert settings.enforce_budget_limits is False
        assert settings.budget_override_allowed is False
        assert settings.alert_on_budget_threshold == 0.75
        assert settings.auto_fallback_to_ollama is True

    def test_threshold_validation(self):
        with pytest.raises(
            ValueError, match="Budget alert threshold should be at least 50%"
        ):
            AIProviderSettings(alert_on_budget_threshold=0.4)

    def test_threshold_boundary_values(self):
        """Test threshold boundary values"""
        # Valid: 50%
        settings = AIProviderSettings(alert_on_budget_threshold=0.5)
        assert settings.alert_on_budget_threshold == 0.5

        # Valid: 100%
        settings = AIProviderSettings(alert_on_budget_threshold=1.0)
        assert settings.alert_on_budget_threshold == 1.0


class TestBudgetExceededWarning:
    """Test BudgetExceededWarning model"""

    def test_create_warning(self):
        """Test creating budget exceeded warning from budget status"""
        # Mock budget status
        budget_status = Mock()
        budget_status.used_budget = 32.50
        budget_status.total_budget = 30.0
        budget_status.percentage_used = 108.33

        warning = BudgetExceededWarning.create(
            budget_status=budget_status,
            requested_provider="claude",
            estimated_cost=0.05,
        )

        assert warning.current_usage == 32.50
        assert warning.budget_limit == 30.0
        assert warning.percentage_used == 108.33
        assert warning.requested_provider == "claude"
        assert warning.estimated_cost == 0.05
        assert warning.alternative_provider == "ollama"
        assert warning.alternative_cost == 0.0
        assert warning.allow_override is True
        assert "Budget exceeded" in warning.message
        assert "claude" in warning.message

    def test_warning_message_format(self):
        """Test warning message is user-friendly"""
        budget_status = Mock()
        budget_status.used_budget = 28.0
        budget_status.total_budget = 30.0
        budget_status.percentage_used = 93.33

        warning = BudgetExceededWarning.create(
            budget_status=budget_status,
            requested_provider="claude",
            estimated_cost=0.05,
        )

        # Check message contains key information
        assert "93.3%" in warning.message or "93%" in warning.message
        assert "claude" in warning.message.lower()
        assert "$" in warning.message
        assert "ollama" in warning.message.lower()


class TestBudgetThresholdAlert:
    """Test BudgetThresholdAlert model"""

    def test_create_info_alert(self):
        """Test creating info-level threshold alert (75%)"""
        budget_status = Mock()
        budget_status.used_budget = 22.5
        budget_status.total_budget = 30.0
        budget_status.remaining_budget = 7.5
        budget_status.days_remaining = 15
        budget_status.projected_monthly_cost = 30.0

        alert = BudgetThresholdAlert.create(
            budget_status=budget_status,
            threshold=75.0,
            severity=BudgetAlertSeverity.INFO,
        )

        assert alert.threshold_percentage == 75.0
        assert alert.current_usage == 22.5
        assert alert.budget_limit == 30.0
        assert alert.remaining_budget == 7.5
        assert alert.severity == BudgetAlertSeverity.INFO
        assert "Budget update" in alert.message
        assert "75%" in alert.message

    def test_create_warning_alert(self):
        """Test creating warning-level threshold alert (80%)"""
        budget_status = Mock()
        budget_status.used_budget = 24.0
        budget_status.total_budget = 30.0
        budget_status.remaining_budget = 6.0
        budget_status.days_remaining = 10
        budget_status.projected_monthly_cost = 36.0

        alert = BudgetThresholdAlert.create(
            budget_status=budget_status,
            threshold=80.0,
            severity=BudgetAlertSeverity.WARNING,
        )

        assert alert.threshold_percentage == 80.0
        assert alert.severity == BudgetAlertSeverity.WARNING
        assert "Budget warning" in alert.message
        assert "$6.00" in alert.message

    def test_create_critical_alert(self):
        """Test creating critical-level threshold alert (90%+)"""
        budget_status = Mock()
        budget_status.used_budget = 27.0
        budget_status.total_budget = 30.0
        budget_status.remaining_budget = 3.0
        budget_status.days_remaining = 5
        budget_status.projected_monthly_cost = 54.0

        alert = BudgetThresholdAlert.create(
            budget_status=budget_status,
            threshold=90.0,
            severity=BudgetAlertSeverity.CRITICAL,
        )

        assert alert.threshold_percentage == 90.0
        assert alert.severity == BudgetAlertSeverity.CRITICAL
        assert "Budget critical" in alert.message
        assert "Ollama" in alert.message  # Should suggest free alternative


class TestBudgetManagerThresholds:
    """Test budget manager threshold monitoring"""

    def test_check_threshold_alerts_below_75(self):
        """Test no alerts when usage < 75%"""
        with patch.object(
            budget_manager, "get_current_budget_status"
        ) as mock_get_status:
            mock_status = BudgetStatus(
                total_budget=30.0,
                used_budget=20.0,
                remaining_budget=10.0,
                percentage_used=66.67,
                alert_level=BudgetAlert.YELLOW,
                days_remaining=15,
                projected_monthly_cost=26.67,
                is_over_budget=False,
            )
            mock_get_status.return_value = mock_status

            alerts = budget_manager.check_budget_threshold_alerts()

            assert len(alerts) == 0

    def test_check_threshold_alerts_75_to_80(self):
        """Test info alert at 75-79% usage"""
        with patch.object(
            budget_manager, "get_current_budget_status"
        ) as mock_get_status:
            mock_status = BudgetStatus(
                total_budget=30.0,
                used_budget=23.0,
                remaining_budget=7.0,
                percentage_used=76.67,
                alert_level=BudgetAlert.ORANGE,
                days_remaining=12,
                projected_monthly_cost=31.0,
                is_over_budget=False,
            )
            mock_get_status.return_value = mock_status

            alerts = budget_manager.check_budget_threshold_alerts()

            assert len(alerts) == 1
            assert alerts[0].threshold_percentage == 75.0
            assert alerts[0].severity == BudgetAlertSeverity.INFO

    def test_check_threshold_alerts_80_to_90(self):
        """Test warning alert at 80-89% usage"""
        with patch.object(
            budget_manager, "get_current_budget_status"
        ) as mock_get_status:
            mock_status = BudgetStatus(
                total_budget=30.0,
                used_budget=25.0,
                remaining_budget=5.0,
                percentage_used=83.33,
                alert_level=BudgetAlert.ORANGE,
                days_remaining=10,
                projected_monthly_cost=37.5,
                is_over_budget=False,
            )
            mock_get_status.return_value = mock_status

            alerts = budget_manager.check_budget_threshold_alerts()

            assert len(alerts) == 1
            assert alerts[0].threshold_percentage == 80.0
            assert alerts[0].severity == BudgetAlertSeverity.WARNING

    def test_check_threshold_alerts_90_to_100(self):
        """Test critical alert at 90-99% usage"""
        with patch.object(
            budget_manager, "get_current_budget_status"
        ) as mock_get_status:
            mock_status = BudgetStatus(
                total_budget=30.0,
                used_budget=28.0,
                remaining_budget=2.0,
                percentage_used=93.33,
                alert_level=BudgetAlert.RED,
                days_remaining=8,
                projected_monthly_cost=45.0,
                is_over_budget=False,
            )
            mock_get_status.return_value = mock_status

            alerts = budget_manager.check_budget_threshold_alerts()

            assert len(alerts) == 1
            assert alerts[0].threshold_percentage == 90.0
            assert alerts[0].severity == BudgetAlertSeverity.CRITICAL

    def test_check_threshold_alerts_over_100(self):
        """Test critical alert when budget exceeded"""
        with patch.object(
            budget_manager, "get_current_budget_status"
        ) as mock_get_status:
            mock_status = BudgetStatus(
                total_budget=30.0,
                used_budget=32.0,
                remaining_budget=-2.0,
                percentage_used=106.67,
                alert_level=BudgetAlert.CRITICAL,
                days_remaining=5,
                projected_monthly_cost=64.0,
                is_over_budget=True,
            )
            mock_get_status.return_value = mock_status

            alerts = budget_manager.check_budget_threshold_alerts()

            assert len(alerts) == 1
            assert alerts[0].threshold_percentage == 100.0
            assert alerts[0].severity == BudgetAlertSeverity.CRITICAL

    def test_should_enforce_budget_default(self):
        """Test budget enforcement default (True)"""
        enforce = budget_manager.should_enforce_budget(None)
        assert enforce is True

    def test_should_enforce_budget_from_preferences(self):
        """Test budget enforcement from user preferences"""
        # Enabled
        prefs = {"ai_provider_settings": {"enforce_budget_limits": True}}
        enforce = budget_manager.should_enforce_budget(prefs)
        assert enforce is True

        # Disabled
        prefs = {"ai_provider_settings": {"enforce_budget_limits": False}}
        enforce = budget_manager.should_enforce_budget(prefs)
        assert enforce is False

    def test_can_override_budget_default(self):
        """Test budget override default (True)"""
        can_override = budget_manager.can_override_budget(None)
        assert can_override is True

    def test_can_override_budget_from_preferences(self):
        """Test budget override from user preferences"""
        # Allowed
        prefs = {"ai_provider_settings": {"budget_override_allowed": True}}
        can_override = budget_manager.can_override_budget(prefs)
        assert can_override is True

        # Not allowed
        prefs = {"ai_provider_settings": {"budget_override_allowed": False}}
        can_override = budget_manager.can_override_budget(prefs)
        assert can_override is False


class TestUserModelAISettings:
    """Test User model AI provider settings methods"""

    def test_get_ai_provider_settings_defaults(self):
        """Test getting AI settings with defaults when none set"""
        from app.models.database import User

        user = User(
            user_id="test_user",
            username="Test User",
            preferences={},  # No AI settings
        )

        settings = user.get_ai_provider_settings()

        # Check all defaults are present
        assert settings["provider_selection_mode"] == "balanced"
        assert settings["default_provider"] == "claude"
        assert settings["enforce_budget_limits"] is True
        assert settings["budget_override_allowed"] is True
        assert settings["alert_on_budget_threshold"] == 0.80
        assert settings["notify_on_provider_change"] is True
        assert settings["notify_on_budget_alert"] is True
        assert settings["auto_fallback_to_ollama"] is False
        assert settings["prefer_local_when_available"] is False

    def test_get_ai_provider_settings_with_custom(self):
        """Test getting AI settings with custom values"""
        from app.models.database import User

        user = User(
            user_id="test_user",
            username="Test User",
            preferences={
                "ai_provider_settings": {
                    "provider_selection_mode": "user_choice",
                    "enforce_budget_limits": False,
                    "auto_fallback_to_ollama": True,
                }
            },
        )

        settings = user.get_ai_provider_settings()

        # Custom values override defaults
        assert settings["provider_selection_mode"] == "user_choice"
        assert settings["enforce_budget_limits"] is False
        assert settings["auto_fallback_to_ollama"] is True

        # Defaults for unset values
        assert settings["default_provider"] == "claude"
        assert settings["budget_override_allowed"] is True

    def test_set_ai_provider_settings(self):
        """Test setting AI provider settings"""
        from app.models.database import User

        user = User(
            user_id="test_user",
            username="Test User",
            preferences={},
        )

        # Set new settings
        user.set_ai_provider_settings(
            {
                "provider_selection_mode": "cost_optimized",
                "enforce_budget_limits": False,
            }
        )

        # Verify settings were saved
        assert "ai_provider_settings" in user.preferences
        assert (
            user.preferences["ai_provider_settings"]["provider_selection_mode"]
            == "cost_optimized"
        )
        assert (
            user.preferences["ai_provider_settings"]["enforce_budget_limits"] is False
        )

    def test_set_ai_provider_settings_merges(self):
        """Test that setting AI settings merges with existing"""
        from app.models.database import User

        user = User(
            user_id="test_user",
            username="Test User",
            preferences={
                "ai_provider_settings": {
                    "provider_selection_mode": "balanced",
                    "default_provider": "claude",
                }
            },
        )

        # Update only one setting
        user.set_ai_provider_settings({"enforce_budget_limits": False})

        settings = user.preferences["ai_provider_settings"]
        # Old settings preserved
        assert settings["provider_selection_mode"] == "balanced"
        assert settings["default_provider"] == "claude"
        # New setting added
        assert settings["enforce_budget_limits"] is False

    def test_set_ai_provider_settings_null_preferences(self):
        """Test setting AI settings when preferences is None"""
        from app.models.database import User

        user = User(user_id="test_user", username="Test User", preferences=None)

        user.set_ai_provider_settings({"enforce_budget_limits": False})

        # Preferences should be initialized
        assert user.preferences is not None
        assert "ai_provider_settings" in user.preferences
        assert (
            user.preferences["ai_provider_settings"]["enforce_budget_limits"] is False
        )
        assert user.preferences["ai_provider_settings"]["enforce_budget_limits"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
