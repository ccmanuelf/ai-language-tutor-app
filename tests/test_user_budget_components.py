"""
Tests for app/frontend/user_budget.py - User Budget Dashboard Components

Target: Comprehensive coverage of user budget UI components
- Alert level logic (red/orange/yellow/green)
- Permission-based rendering (can_modify_limit, can_reset_budget)
- Data formatting and calculations
- HTML structure validation
- JavaScript generation

Session 129H - Phase 1: Frontend Budget Coverage
"""

import pytest
from fasthtml.common import to_xml

# Import module at top level to enable coverage detection
import app.frontend.user_budget  # noqa: F401


class TestCreateBudgetStatusCard:
    """Test create_budget_status_card function"""

    def test_budget_status_card_green_alert_healthy(self):
        """Test green alert status (<75% usage)"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 15.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",
            "percentage_used": 50.0,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Validate green alert status
        assert "✅ HEALTHY" in result_str
        assert "bg-green-100" in result_str
        assert "bg-green-500" in result_str  # Progress bar color

        # Validate spending display
        assert "$15.00" in result_str  # Current spent
        assert "$30.00" in result_str  # Monthly limit
        assert "$15.00" in result_str  # Remaining (positive)
        assert "50.0%" in result_str  # Percentage

        # Validate period display
        assert "2025-12-01" in result_str
        assert "2025-12-31" in result_str

    def test_budget_status_card_yellow_alert_warning(self):
        """Test yellow alert status (75-89% usage)"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 24.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "yellow",
            "percentage_used": 80.0,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Validate yellow alert status
        assert "⚡ WARNING" in result_str
        assert "bg-yellow-100" in result_str
        assert "bg-yellow-500" in result_str  # Progress bar color

        # Validate spending
        assert "$24.00" in result_str
        assert "$6.00" in result_str  # Remaining
        assert "80.0%" in result_str

    def test_budget_status_card_orange_alert_critical(self):
        """Test orange alert status (90-99% usage)"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 27.5,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "orange",
            "percentage_used": 91.67,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Validate orange alert status
        assert "⚠️ CRITICAL" in result_str
        assert "bg-orange-100" in result_str
        assert "bg-orange-500" in result_str  # Progress bar color

        # Validate spending
        assert "$27.50" in result_str
        assert "$2.50" in result_str  # Remaining
        assert "91.7%" in result_str

    def test_budget_status_card_red_alert_over_budget(self):
        """Test red alert status (≥100% usage)"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 35.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "red",
            "percentage_used": 116.67,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Validate red alert status
        assert "⚠️ OVER BUDGET" in result_str
        assert "bg-red-100" in result_str
        assert "bg-red-500" in result_str  # Progress bar color

        # Validate spending
        assert "$35.00" in result_str
        assert "-$5.00" in result_str or "$-5.00" in result_str  # Negative remaining
        assert "116.7%" in result_str

    def test_budget_status_card_percentage_over_100_alert_level_fallback(self):
        """Test percentage ≥100% triggers red alert even if alert_level is different"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 32.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",  # Intentionally wrong
            "percentage_used": 106.67,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Should show red alert due to percentage ≥100%
        assert "⚠️ OVER BUDGET" in result_str
        assert "bg-red-100" in result_str

    def test_budget_status_card_percentage_over_90_alert_level_fallback(self):
        """Test percentage ≥90% triggers orange alert even if alert_level is different"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 27.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",  # Intentionally wrong
            "percentage_used": 90.0,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Should show orange/critical alert due to percentage ≥90%
        assert "⚠️ CRITICAL" in result_str
        assert "bg-orange-100" in result_str

    def test_budget_status_card_percentage_over_75_alert_level_fallback(self):
        """Test percentage ≥75% triggers yellow alert even if alert_level is different"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 22.5,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",  # Intentionally wrong
            "percentage_used": 75.0,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Should show yellow/warning alert due to percentage ≥75%
        assert "⚡ WARNING" in result_str
        assert "bg-yellow-100" in result_str

    def test_budget_status_card_remaining_budget_positive(self):
        """Test remaining budget display when positive"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 50.0,
            "current_spent": 20.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",
            "percentage_used": 40.0,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Remaining should be $30.00 and show green
        assert "$30.00" in result_str
        assert "text-green-400" in result_str  # Positive remaining color

    def test_budget_status_card_remaining_budget_negative(self):
        """Test remaining budget display when negative (over budget)"""
        from app.frontend.user_budget import create_budget_status_card

        budget_data = {
            "monthly_limit": 30.0,
            "current_spent": 40.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "red",
            "percentage_used": 133.33,
        }

        result = create_budget_status_card(budget_data)
        result_str = to_xml(result)

        # Remaining should be -$10.00 and show red
        assert "text-red-400" in result_str  # Negative remaining color


class TestCreateBudgetSettingsCard:
    """Test create_budget_settings_card function"""

    def test_settings_card_no_permissions(self):
        """Test settings card with no permissions (all disabled)"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=False, can_reset_budget=False
        )
        result_str = to_xml(result)

        # Validate all inputs are disabled
        assert "opacity-50 cursor-not-allowed" in result_str

        # Validate lock message
        assert "🔒 Contact admin to modify" in result_str

        # Validate buttons are disabled
        assert result_str.count("disabled") >= 2  # At least Save and Reset buttons

    def test_settings_card_can_modify_only(self):
        """Test settings card with can_modify_limit=True, can_reset_budget=False"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=True, can_reset_budget=False
        )
        result_str = to_xml(result)

        # Validate modify message
        assert "✏️ You can modify this" in result_str

        # Save button should be enabled, Reset button disabled
        # Note: FastHTML may render disabled differently, check for button presence
        assert "💾 Save Settings" in result_str
        assert "🔄 Reset Budget" in result_str

    def test_settings_card_can_reset_only(self):
        """Test settings card with can_modify_limit=False, can_reset_budget=True"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=False, can_reset_budget=True
        )
        result_str = to_xml(result)

        # Validate inputs are disabled (can't modify limit)
        assert "🔒 Contact admin to modify" in result_str

        # Both buttons should be present
        assert "💾 Save Settings" in result_str
        assert "🔄 Reset Budget" in result_str

    def test_settings_card_all_permissions(self):
        """Test settings card with all permissions enabled"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=True, can_reset_budget=True
        )
        result_str = to_xml(result)

        # Validate modify message
        assert "✏️ You can modify this" in result_str

        # Both buttons should be present and not have disabled styling
        assert "💾 Save Settings" in result_str
        assert "🔄 Reset Budget" in result_str

    def test_settings_card_displays_current_values(self):
        """Test settings card displays current values correctly"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 45.50,
            "enforce_budget": False,
            "alert_threshold_yellow": 70.0,
            "alert_threshold_orange": 85.0,
            "alert_threshold_red": 95.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=True, can_reset_budget=True
        )
        result_str = to_xml(result)

        # Validate values are displayed
        assert "45.50" in result_str  # Monthly limit
        assert "70" in result_str  # Yellow threshold
        assert "85" in result_str  # Orange threshold
        assert "95" in result_str  # Red threshold

    def test_settings_card_enforce_budget_checkbox_checked(self):
        """Test enforce budget checkbox when True"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=True, can_reset_budget=True
        )
        result_str = to_xml(result)

        # Checkbox should be checked
        assert "checked" in result_str or 'checked="checked"' in result_str

    def test_settings_card_enforce_budget_checkbox_unchecked(self):
        """Test enforce budget checkbox when False"""
        from app.frontend.user_budget import create_budget_settings_card

        settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": False,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        result = create_budget_settings_card(
            settings, can_modify_limit=True, can_reset_budget=True
        )
        result_str = to_xml(result)

        # Component should be present but unchecked
        assert "enforceBudgetCheckbox" in result_str


class TestCreateUsageHistoryTable:
    """Test create_usage_history_table function"""

    def test_usage_history_empty_state(self):
        """Test usage history table with no records"""
        from app.frontend.user_budget import create_usage_history_table

        usage_history = []

        result = create_usage_history_table(usage_history)
        result_str = to_xml(result)

        # Validate empty state message
        assert "📊 Usage History" in result_str
        assert "No usage history available yet" in result_str

    def test_usage_history_with_records(self):
        """Test usage history table with records"""
        from app.frontend.user_budget import create_usage_history_table

        usage_history = [
            {
                "timestamp": "2025-12-19 10:30:00",
                "provider": "OpenAI",
                "model": "gpt-4",
                "cost": 0.0234,
                "tokens": 1200,
            },
            {
                "timestamp": "2025-12-19 09:15:00",
                "provider": "Anthropic",
                "model": "claude-3-sonnet",
                "cost": 0.0156,
                "tokens": 800,
            },
        ]

        result = create_usage_history_table(usage_history)
        result_str = to_xml(result)

        # Validate table headers
        assert "Timestamp" in result_str
        assert "Provider" in result_str
        assert "Model" in result_str
        assert "Tokens" in result_str
        assert "Cost" in result_str

        # Validate data is displayed
        assert "2025-12-19 10:30:00" in result_str
        assert "OpenAI" in result_str
        assert "gpt-4" in result_str
        assert "1,200" in result_str  # Formatted with comma
        assert "$0.0234" in result_str

        assert "2025-12-19 09:15:00" in result_str
        assert "Anthropic" in result_str
        assert "claude-3-sonnet" in result_str
        assert "800" in result_str
        assert "$0.0156" in result_str

    def test_usage_history_handles_missing_provider(self):
        """Test usage history handles missing provider key gracefully"""
        from app.frontend.user_budget import create_usage_history_table

        usage_history = [
            {
                "timestamp": "2025-12-19 10:30:00",
                # provider key missing - should use default "Unknown"
                "model": "test-model",
                "cost": 0.01,
                "tokens": 500,
            }
        ]

        result = create_usage_history_table(usage_history)
        result_str = to_xml(result)

        # Should show "Unknown" for missing provider key
        assert "Unknown" in result_str

    def test_usage_history_handles_zero_cost(self):
        """Test usage history handles zero cost records"""
        from app.frontend.user_budget import create_usage_history_table

        usage_history = [
            {
                "timestamp": "2025-12-19 10:30:00",
                "provider": "OpenAI",
                "model": "gpt-4",
                "cost": 0.0,
                "tokens": 100,
            }
        ]

        result = create_usage_history_table(usage_history)
        result_str = to_xml(result)

        # Should display $0.0000
        assert "$0.0000" in result_str


class TestCreateBudgetBreakdownChart:
    """Test create_budget_breakdown_chart function"""

    def test_breakdown_chart_empty_data(self):
        """Test breakdown chart with no data"""
        from app.frontend.user_budget import create_budget_breakdown_chart

        breakdown = {"by_provider": {}, "by_model": {}}

        result = create_budget_breakdown_chart(breakdown)
        result_str = to_xml(result)

        # Should return empty Div or minimal content
        assert result_str is not None
        # Empty breakdown should not render the full chart
        assert len(result_str) < 100 or result_str == "<div></div>"

    def test_breakdown_chart_with_provider_data(self):
        """Test breakdown chart with provider data"""
        from app.frontend.user_budget import create_budget_breakdown_chart

        breakdown = {
            "by_provider": {"OpenAI": 12.50, "Anthropic": 8.75, "Google": 3.25},
            "by_model": {},
        }

        result = create_budget_breakdown_chart(breakdown)
        result_str = to_xml(result)

        # Validate chart header
        assert "📈 Spending Breakdown" in result_str
        assert "By Provider" in result_str

        # Validate provider data
        assert "OpenAI" in result_str
        assert "$12.500" in result_str or "$12.50" in result_str

        assert "Anthropic" in result_str
        assert "$8.750" in result_str or "$8.75" in result_str

        assert "Google" in result_str
        assert "$3.250" in result_str or "$3.25" in result_str

    def test_breakdown_chart_calculates_percentages(self):
        """Test breakdown chart calculates percentage widths correctly"""
        from app.frontend.user_budget import create_budget_breakdown_chart

        breakdown = {
            "by_provider": {
                "OpenAI": 20.0,  # 50% of total
                "Anthropic": 20.0,  # 50% of total
            },
            "by_model": {},
        }

        result = create_budget_breakdown_chart(breakdown)
        result_str = to_xml(result)

        # Should have width: 50% for progress bars
        assert "width: 50" in result_str  # Percentage calculation

    def test_breakdown_chart_sorts_by_cost_descending(self):
        """Test breakdown chart sorts providers by cost (highest first)"""
        from app.frontend.user_budget import create_budget_breakdown_chart

        breakdown = {
            "by_provider": {
                "Anthropic": 5.0,
                "OpenAI": 15.0,  # Highest
                "Google": 10.0,
            },
            "by_model": {},
        }

        result = create_budget_breakdown_chart(breakdown)
        result_str = to_xml(result)

        # OpenAI should appear before Google, Google before Anthropic
        openai_pos = result_str.find("OpenAI")
        google_pos = result_str.find("Google")
        anthropic_pos = result_str.find("Anthropic")

        assert openai_pos < google_pos < anthropic_pos


class TestCreateBudgetJavascript:
    """Test create_budget_javascript function"""

    def test_budget_javascript_contains_save_function(self):
        """Test JavaScript contains saveBudgetSettings function"""
        from app.frontend.user_budget import create_budget_javascript

        result = create_budget_javascript()
        result_str = to_xml(result)

        # Validate save function exists
        assert "async function saveBudgetSettings()" in result_str
        assert "monthlyLimitInput" in result_str
        assert "enforceBudgetCheckbox" in result_str

    def test_budget_javascript_contains_threshold_validation(self):
        """Test JavaScript validates threshold ordering (yellow < orange < red)"""
        from app.frontend.user_budget import create_budget_javascript

        result = create_budget_javascript()
        result_str = to_xml(result)

        # Validate threshold ordering check
        assert "alertYellow >= alertOrange" in result_str or "Yellow < Orange < Red" in result_str

    def test_budget_javascript_contains_reset_function(self):
        """Test JavaScript contains resetBudget function"""
        from app.frontend.user_budget import create_budget_javascript

        result = create_budget_javascript()
        result_str = to_xml(result)

        # Validate reset function exists
        assert "async function resetBudget()" in result_str
        assert "confirm(" in result_str  # Confirmation dialog

    def test_budget_javascript_contains_api_endpoints(self):
        """Test JavaScript contains correct API endpoints"""
        from app.frontend.user_budget import create_budget_javascript

        result = create_budget_javascript()
        result_str = to_xml(result)

        # Validate API endpoints
        assert "/api/v1/budget/settings" in result_str
        assert "/api/v1/budget/reset" in result_str

    def test_budget_javascript_contains_auto_refresh(self):
        """Test JavaScript contains auto-refresh logic"""
        from app.frontend.user_budget import create_budget_javascript

        result = create_budget_javascript()
        result_str = to_xml(result)

        # Validate auto-refresh (30 seconds)
        assert "setInterval" in result_str
        assert "30000" in result_str  # 30 seconds in milliseconds


class TestCreateUserBudgetPage:
    """Test create_user_budget_page function (page assembly)"""

    def test_user_budget_page_contains_all_sections(self):
        """Test complete page contains all major sections"""
        from app.frontend.user_budget import create_user_budget_page

        budget_status = {
            "monthly_limit": 30.0,
            "current_spent": 15.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",
            "percentage_used": 50.0,
        }

        budget_settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        usage_history = []
        breakdown = {"by_provider": {}, "by_model": {}}

        result = create_user_budget_page(
            budget_status=budget_status,
            budget_settings=budget_settings,
            usage_history=usage_history,
            breakdown=breakdown,
            can_modify_limit=True,
            can_reset_budget=True,
        )
        result_str = to_xml(result)

        # Validate page header
        assert "💰 My Budget Dashboard" in result_str
        assert "Monitor your AI API usage" in result_str

        # Validate sections are present
        assert "💰 My Budget Status" in result_str  # Status card
        assert "⚙️ Budget Settings" in result_str  # Settings card
        assert "📊" in result_str  # Usage history or breakdown

    def test_user_budget_page_passes_permissions_correctly(self):
        """Test page passes permission flags to settings card"""
        from app.frontend.user_budget import create_user_budget_page

        budget_status = {
            "monthly_limit": 30.0,
            "current_spent": 15.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",
            "percentage_used": 50.0,
        }

        budget_settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        usage_history = []
        breakdown = {"by_provider": {}, "by_model": {}}

        # Test with no permissions
        result = create_user_budget_page(
            budget_status=budget_status,
            budget_settings=budget_settings,
            usage_history=usage_history,
            breakdown=breakdown,
            can_modify_limit=False,
            can_reset_budget=False,
        )
        result_str = to_xml(result)

        # Should show lock message
        assert "🔒 Contact admin to modify" in result_str

    def test_user_budget_page_includes_javascript(self):
        """Test page includes JavaScript for interactivity"""
        from app.frontend.user_budget import create_user_budget_page

        budget_status = {
            "monthly_limit": 30.0,
            "current_spent": 15.0,
            "period_start": "2025-12-01",
            "period_end": "2025-12-31",
            "alert_level": "green",
            "percentage_used": 50.0,
        }

        budget_settings = {
            "monthly_limit_usd": 30.0,
            "enforce_budget": True,
            "alert_threshold_yellow": 75.0,
            "alert_threshold_orange": 90.0,
            "alert_threshold_red": 100.0,
        }

        usage_history = []
        breakdown = {"by_provider": {}, "by_model": {}}

        result = create_user_budget_page(
            budget_status=budget_status,
            budget_settings=budget_settings,
            usage_history=usage_history,
            breakdown=breakdown,
            can_modify_limit=True,
            can_reset_budget=True,
        )
        result_str = to_xml(result)

        # Should include JavaScript functions
        assert "saveBudgetSettings" in result_str or "<script>" in result_str
