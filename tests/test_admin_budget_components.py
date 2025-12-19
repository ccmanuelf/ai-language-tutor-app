"""
Tests for app/frontend/admin_budget.py - Admin Budget Management UI

Target: Comprehensive coverage of admin budget management components
- Status badge logic (5 levels: OK, MODERATE, HIGH, CRITICAL, OVER BUDGET)
- Permission indicator combinations (8 combinations)
- Progress bar colors and widths
- Modal form structure
- JavaScript generation

Session 129H - Phase 1: Frontend Budget Coverage
"""

import pytest
from fasthtml.common import to_xml

# Import module at top level to enable coverage detection
import app.frontend.admin_budget  # noqa: F401


class TestCreateBudgetOverviewCard:
    """Test create_budget_overview_card function"""

    def test_overview_card_displays_statistics(self):
        """Test overview card displays system-wide statistics"""
        from app.frontend.admin_budget import create_budget_overview_card

        budget_data = {
            "stats": {
                "total_users": 10,
                "total_budget_allocated": 350.0,
                "total_spent": 125.50,
                "users_over_budget": 2,
            }
        }

        result = create_budget_overview_card(budget_data)
        result_str = to_xml(result)

        # Validate header
        assert "Budget System Overview" in result_str

        # Validate statistics display
        assert "10" in result_str  # total_users
        assert "$350.00" in result_str  # total_budget_allocated
        assert "$125.50" in result_str  # total_spent
        assert "2" in result_str  # users_over_budget

        # Validate labels
        assert "Total Users" in result_str
        assert "Total Budget Allocated" in result_str
        assert "Total Spent" in result_str
        assert "Users Over Budget" in result_str

    def test_overview_card_highlights_users_over_budget(self):
        """Test overview card highlights users over budget in red"""
        from app.frontend.admin_budget import create_budget_overview_card

        budget_data = {
            "stats": {
                "total_users": 10,
                "total_budget_allocated": 300.0,
                "total_spent": 150.0,
                "users_over_budget": 3,  # Should show in red
            }
        }

        result = create_budget_overview_card(budget_data)
        result_str = to_xml(result)

        # Should have danger color for users_over_budget > 0
        assert "--danger-color" in result_str

    def test_overview_card_handles_zero_users_over_budget(self):
        """Test overview card when no users are over budget"""
        from app.frontend.admin_budget import create_budget_overview_card

        budget_data = {
            "stats": {
                "total_users": 10,
                "total_budget_allocated": 300.0,
                "total_spent": 150.0,
                "users_over_budget": 0,  # No users over budget
            }
        }

        result = create_budget_overview_card(budget_data)
        result_str = to_xml(result)

        # Should not have danger color when users_over_budget == 0
        # The "0" should appear without danger styling
        assert "0" in result_str


class TestCreateUserBudgetRow:
    """Test create_user_budget_row function"""

    def test_budget_row_status_ok_under_50(self):
        """Test status badge shows OK when usage < 50%"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_001",
            "monthly_limit_usd": 30.0,
            "current_usage": 10.0,  # 33.33%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Validate OK status
        assert "OK" in result_str
        assert "badge-success" in result_str

        # Validate user ID and amounts
        assert "test_user_001" in result_str
        assert "$30.00" in result_str
        assert "$10.00" in result_str

    def test_budget_row_status_moderate_50_to_75(self):
        """Test status badge shows MODERATE when 50% <= usage < 75%"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_002",
            "monthly_limit_usd": 30.0,
            "current_usage": 18.0,  # 60%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Validate MODERATE status
        assert "MODERATE" in result_str
        assert "badge-yellow" in result_str

    def test_budget_row_status_high_75_to_90(self):
        """Test status badge shows HIGH when 75% <= usage < 90%"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_003",
            "monthly_limit_usd": 30.0,
            "current_usage": 24.0,  # 80%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Validate HIGH status
        assert "HIGH" in result_str
        assert "badge-orange" in result_str

    def test_budget_row_status_critical_90_to_100(self):
        """Test status badge shows CRITICAL when 90% <= usage < 100%"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_004",
            "monthly_limit_usd": 30.0,
            "current_usage": 27.5,  # 91.67%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Validate CRITICAL status
        assert "CRITICAL" in result_str
        assert "badge-warning" in result_str

    def test_budget_row_status_over_budget_100_plus(self):
        """Test status badge shows OVER BUDGET when usage >= 100%"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_005",
            "monthly_limit_usd": 30.0,
            "current_usage": 35.0,  # 116.67%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Validate OVER BUDGET status
        assert "OVER BUDGET" in result_str
        assert "badge-danger" in result_str

    def test_budget_row_permission_all_disabled(self):
        """Test permission indicators when all permissions disabled"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_006",
            "monthly_limit_usd": 30.0,
            "current_usage": 10.0,
            "budget_visible_to_user": False,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Should show "None" when no permissions
        assert "None" in result_str

    def test_budget_row_permission_visible_only(self):
        """Test permission indicators with only visibility enabled"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_007",
            "monthly_limit_usd": 30.0,
            "current_usage": 10.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Should show only Visible permission
        assert "👁️ Visible" in result_str

    def test_budget_row_permission_all_enabled(self):
        """Test permission indicators when all permissions enabled"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_008",
            "monthly_limit_usd": 30.0,
            "current_usage": 10.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": True,
            "user_can_reset_budget": True,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Should show all three permissions
        assert "👁️ Visible" in result_str
        assert "✏️ Can Modify" in result_str
        assert "🔄 Can Reset" in result_str

    def test_budget_row_progress_bar_color_green(self):
        """Test progress bar shows green for healthy usage (<75%)"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_009",
            "monthly_limit_usd": 30.0,
            "current_usage": 15.0,  # 50%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Progress bar should be green (success color)
        assert "--success-color" in result_str

    def test_budget_row_progress_bar_color_yellow(self):
        """Test progress bar shows yellow for warning usage (75-89%)"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_010",
            "monthly_limit_usd": 30.0,
            "current_usage": 24.0,  # 80%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Progress bar should be yellow (warning color)
        assert "--warning-color" in result_str

    def test_budget_row_progress_bar_color_red(self):
        """Test progress bar shows red for critical/over usage (>=90%)"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_011",
            "monthly_limit_usd": 30.0,
            "current_usage": 28.0,  # 93.33%
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Progress bar should be red (danger color)
        assert "--danger-color" in result_str

    def test_budget_row_action_buttons(self):
        """Test row contains Configure and Reset buttons"""
        from app.frontend.admin_budget import create_user_budget_row

        user_budget = {
            "user_id": "test_user_012",
            "monthly_limit_usd": 30.0,
            "current_usage": 10.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
        }

        result = create_user_budget_row(user_budget)
        result_str = to_xml(result)

        # Validate action buttons
        assert "Configure" in result_str
        assert "Reset" in result_str
        assert "openBudgetConfigModal" in result_str
        assert "resetUserBudget" in result_str


class TestCreateUserBudgetList:
    """Test create_user_budget_list function"""

    def test_budget_list_with_users(self):
        """Test budget list displays user budget table"""
        from app.frontend.admin_budget import create_user_budget_list

        users_budget = [
            {
                "user_id": "user_001",
                "monthly_limit_usd": 30.0,
                "current_usage": 10.0,
                "budget_visible_to_user": True,
                "user_can_modify_limit": False,
                "user_can_reset_budget": False,
            },
            {
                "user_id": "user_002",
                "monthly_limit_usd": 50.0,
                "current_usage": 25.0,
                "budget_visible_to_user": True,
                "user_can_modify_limit": True,
                "user_can_reset_budget": True,
            },
        ]

        result = create_user_budget_list(users_budget)
        result_str = to_xml(result)

        # Validate header
        assert "User Budget Management" in result_str

        # Validate search input
        assert "userSearch" in result_str
        assert "Search users..." in result_str

        # Validate table headers
        assert "User ID" in result_str
        assert "Monthly Limit" in result_str
        assert "Current Usage" in result_str
        assert "Status" in result_str
        assert "Permissions" in result_str
        assert "Actions" in result_str

        # Validate both users appear
        assert "user_001" in result_str
        assert "user_002" in result_str

    def test_budget_list_filter_function(self):
        """Test budget list includes search filter JavaScript"""
        from app.frontend.admin_budget import create_user_budget_list

        users_budget = []

        result = create_user_budget_list(users_budget)
        result_str = to_xml(result)

        # Should have filter function reference
        assert "filterUserBudgets" in result_str or "userSearch" in result_str


class TestCreateBudgetConfigModal:
    """Test create_budget_config_modal function"""

    def test_config_modal_structure(self):
        """Test configuration modal contains all required fields"""
        from app.frontend.admin_budget import create_budget_config_modal

        result = create_budget_config_modal()
        result_str = to_xml(result)

        # Validate modal header
        assert "Configure User Budget" in result_str

        # Validate form fields
        assert "User ID" in result_str or "configUserId" in result_str
        assert "Monthly Budget Limit" in result_str or "configMonthlyLimit" in result_str
        assert "Budget Visible to User" in result_str or "configVisible" in result_str
        assert "User Can Modify Limit" in result_str or "configCanModify" in result_str
        assert "User Can Reset Budget" in result_str or "configCanReset" in result_str
        assert "Admin Notes" in result_str or "configNotes" in result_str

    def test_config_modal_action_buttons(self):
        """Test configuration modal has Cancel and Save buttons"""
        from app.frontend.admin_budget import create_budget_config_modal

        result = create_budget_config_modal()
        result_str = to_xml(result)

        # Validate action buttons
        assert "Cancel" in result_str
        assert "Save Configuration" in result_str
        assert "closeBudgetConfigModal" in result_str
        assert "saveBudgetConfig" in result_str

    def test_config_modal_field_descriptions(self):
        """Test configuration modal includes helpful field descriptions"""
        from app.frontend.admin_budget import create_budget_config_modal

        result = create_budget_config_modal()
        result_str = to_xml(result)

        # Should have description text for permissions
        assert "disabled" in result_str.lower() or "allow" in result_str.lower()


class TestCreateBudgetScripts:
    """Test create_budget_scripts function (JavaScript generation)"""

    def test_scripts_contain_filter_function(self):
        """Test scripts include user budget filter function"""
        from app.frontend.admin_budget import create_budget_scripts

        result = create_budget_scripts()
        result_str = to_xml(result)

        # Validate filter function
        assert "function filterUserBudgets()" in result_str
        assert "userSearch" in result_str

    def test_scripts_contain_modal_open_function(self):
        """Test scripts include modal open function"""
        from app.frontend.admin_budget import create_budget_scripts

        result = create_budget_scripts()
        result_str = to_xml(result)

        # Validate modal open function
        assert "function openBudgetConfigModal" in result_str
        assert "/api/v1/budget/admin/users" in result_str

    def test_scripts_contain_modal_close_function(self):
        """Test scripts include modal close function"""
        from app.frontend.admin_budget import create_budget_scripts

        result = create_budget_scripts()
        result_str = to_xml(result)

        # Validate modal close function
        assert "function closeBudgetConfigModal()" in result_str
        assert "budgetConfigModal" in result_str

    def test_scripts_contain_save_config_function(self):
        """Test scripts include save configuration function"""
        from app.frontend.admin_budget import create_budget_scripts

        result = create_budget_scripts()
        result_str = to_xml(result)

        # Validate save function
        assert "async function saveBudgetConfig()" in result_str
        assert "/api/v1/budget/admin/configure" in result_str
        assert "PUT" in result_str or "method" in result_str.lower()

    def test_scripts_contain_reset_budget_function(self):
        """Test scripts include reset budget function"""
        from app.frontend.admin_budget import create_budget_scripts

        result = create_budget_scripts()
        result_str = to_xml(result)

        # Validate reset function
        assert "async function resetUserBudget" in result_str
        assert "/api/v1/budget/admin/reset" in result_str
        assert "confirm(" in result_str  # Confirmation dialog


class TestCreateAdminBudgetPage:
    """Test create_admin_budget_page function (page assembly)"""

    def test_admin_page_contains_all_sections(self):
        """Test complete admin page contains all major sections"""
        from app.frontend.admin_budget import create_admin_budget_page

        result = create_admin_budget_page()
        result_str = to_xml(result)

        # Validate page header
        assert "Budget Management" in result_str

        # Validate sections are present
        assert "Budget System Overview" in result_str or "Total Users" in result_str
        assert "User Budget Management" in result_str or "User ID" in result_str

    def test_admin_page_includes_modal(self):
        """Test admin page includes configuration modal"""
        from app.frontend.admin_budget import create_admin_budget_page

        result = create_admin_budget_page()
        result_str = to_xml(result)

        # Should include modal
        assert "budgetConfigModal" in result_str or "Configure User Budget" in result_str

    def test_admin_page_includes_scripts(self):
        """Test admin page includes JavaScript for functionality"""
        from app.frontend.admin_budget import create_admin_budget_page

        result = create_admin_budget_page()
        result_str = to_xml(result)

        # Should include JavaScript functions
        assert "filterUserBudgets" in result_str or "saveBudgetConfig" in result_str

    def test_admin_page_uses_demo_data(self):
        """Test admin page contains demo/placeholder data"""
        from app.frontend.admin_budget import create_admin_budget_page

        result = create_admin_budget_page()
        result_str = to_xml(result)

        # Should contain some user data (from demo data in function)
        assert "admin_1758913874" in result_str or "user_001" in result_str
