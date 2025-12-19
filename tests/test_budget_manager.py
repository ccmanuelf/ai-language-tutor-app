"""
Comprehensive tests for budget_manager.py

Tests cover:
- BudgetAlert enum (5 values)
- CostOptimizationStrategy enum (4 values)
- BudgetStatus dataclass
- CostEstimate dataclass
- BudgetManager class (18 methods, 68 branches)
- Module-level convenience functions (4 functions)

Target: TRUE 100% coverage (statement + branch)
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.models.budget import BudgetPeriod, UserBudgetSettings
from app.models.database import APIUsage, User
from app.services.budget_manager import (
    BudgetAlert,
    BudgetManager,
    BudgetStatus,
    CostEstimate,
    CostOptimizationStrategy,
    budget_manager,
    can_afford,
    estimate_cost,
    get_budget_status,
    record_usage,
)

# ============================================================================
# Test Enums
# ============================================================================


class TestBudgetAlert:
    """Test BudgetAlert enum"""

    def test_alert_values(self):
        """Test all alert level values"""
        assert BudgetAlert.GREEN.value == "green"
        assert BudgetAlert.YELLOW.value == "yellow"
        assert BudgetAlert.ORANGE.value == "orange"
        assert BudgetAlert.RED.value == "red"
        assert BudgetAlert.CRITICAL.value == "critical"

    def test_alert_count(self):
        """Test we have exactly 5 alert levels"""
        assert len(BudgetAlert) == 5


class TestCostOptimizationStrategy:
    """Test CostOptimizationStrategy enum"""

    def test_strategy_values(self):
        """Test all strategy values"""
        assert CostOptimizationStrategy.CHEAPEST_FIRST.value == "cheapest_first"
        assert CostOptimizationStrategy.BALANCED.value == "balanced"
        assert CostOptimizationStrategy.QUALITY_FIRST.value == "quality_first"
        assert CostOptimizationStrategy.EMERGENCY_ONLY.value == "emergency_only"

    def test_strategy_count(self):
        """Test we have exactly 4 strategies"""
        assert len(CostOptimizationStrategy) == 4


# ============================================================================
# Test Dataclasses
# ============================================================================


class TestBudgetStatus:
    """Test BudgetStatus dataclass"""

    def test_budget_status_creation(self):
        """Test BudgetStatus dataclass creation"""
        status = BudgetStatus(
            total_budget=30.0,
            used_budget=15.0,
            remaining_budget=15.0,
            percentage_used=50.0,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=15,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )

        assert status.total_budget == 30.0
        assert status.used_budget == 15.0
        assert status.remaining_budget == 15.0
        assert status.percentage_used == 50.0
        assert status.alert_level == BudgetAlert.YELLOW
        assert status.days_remaining == 15
        assert status.projected_monthly_cost == 30.0
        assert status.is_over_budget is False

    def test_budget_status_over_budget(self):
        """Test BudgetStatus when over budget"""
        status = BudgetStatus(
            total_budget=30.0,
            used_budget=35.0,
            remaining_budget=0.0,
            percentage_used=116.67,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=5,
            projected_monthly_cost=42.0,
            is_over_budget=True,
        )

        assert status.is_over_budget is True
        assert status.alert_level == BudgetAlert.CRITICAL


class TestCostEstimate:
    """Test CostEstimate dataclass"""

    def test_cost_estimate_creation(self):
        """Test CostEstimate dataclass creation"""
        estimate = CostEstimate(
            estimated_cost=0.05,
            provider="anthropic",
            service_type="llm",
            tokens_estimated=1000,
            confidence=0.9,
        )

        assert estimate.estimated_cost == 0.05
        assert estimate.provider == "anthropic"
        assert estimate.service_type == "llm"
        assert estimate.tokens_estimated == 1000
        assert estimate.confidence == 0.9

    def test_cost_estimate_zero_tokens(self):
        """Test CostEstimate with zero tokens"""
        estimate = CostEstimate(
            estimated_cost=0.02,
            provider="ibm_watson",
            service_type="stt",
            tokens_estimated=0,
            confidence=0.85,
        )

        assert estimate.tokens_estimated == 0
        assert estimate.estimated_cost == 0.02


# ============================================================================
# Test BudgetManager.__init__
# ============================================================================


class TestBudgetManagerInit:
    """Test BudgetManager initialization"""

    @patch("app.services.budget_manager.get_settings")
    def test_init_default_budget(self, mock_settings):
        """Test BudgetManager initialization with default budget"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert manager.monthly_budget == 30.0
        assert manager.alert_thresholds[BudgetAlert.YELLOW] == 0.50
        assert manager.alert_thresholds[BudgetAlert.ORANGE] == 0.75
        assert manager.alert_thresholds[BudgetAlert.RED] == 0.90
        assert manager.alert_thresholds[BudgetAlert.CRITICAL] == 1.00

    @patch("app.services.budget_manager.get_settings")
    def test_init_provider_costs_anthropic(self, mock_settings):
        """Test provider costs for Anthropic models"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert "anthropic" in manager.provider_costs
        assert "claude-3-haiku" in manager.provider_costs["anthropic"]
        assert "claude-3-sonnet" in manager.provider_costs["anthropic"]
        assert "claude-3-opus" in manager.provider_costs["anthropic"]

    @patch("app.services.budget_manager.get_settings")
    def test_init_provider_costs_mistral(self, mock_settings):
        """Test provider costs for Mistral models"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert "mistral" in manager.provider_costs
        assert "mistral-tiny" in manager.provider_costs["mistral"]

    @patch("app.services.budget_manager.get_settings")
    def test_init_provider_costs_no_watson(self, mock_settings):
        """Test that Watson is NOT in provider costs (removed in Session 100)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        # Watson was completely removed in Session 100 cleanup
        assert "ibm_watson" not in manager.provider_costs
        assert "watson" not in manager.provider_costs


# ============================================================================
# Test BudgetManager.get_current_budget_status
# ============================================================================


class TestGetCurrentBudgetStatus:
    """Test get_current_budget_status method"""

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_no_usage(self, mock_settings, mock_session):
        """Test budget status with no API usage"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock query to return 0 cost
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None  # No usage data

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        assert status.total_budget == 30.0
        assert status.used_budget == 0.0
        assert status.remaining_budget == 30.0
        assert status.percentage_used == 0.0
        assert status.alert_level == BudgetAlert.GREEN
        assert status.is_over_budget is False

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_green_alert(self, mock_settings, mock_session):
        """Test budget status in GREEN zone (0-50%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 40% usage ($12 of $30)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 12.0  # Use float, not Decimal

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        assert status.used_budget == 12.0
        assert status.percentage_used == 40.0
        assert status.alert_level == BudgetAlert.GREEN
        assert status.is_over_budget is False

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_yellow_alert(self, mock_settings, mock_session):
        """Test budget status in YELLOW zone (50-75%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 60% usage ($18 of $30)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 18.00

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        assert status.percentage_used == 60.0
        assert status.alert_level == BudgetAlert.YELLOW
        assert status.is_over_budget is False

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_orange_alert(self, mock_settings, mock_session):
        """Test budget status in ORANGE zone (75-90%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 80% usage ($24 of $30)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 24.00

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        assert status.percentage_used == 80.0
        assert status.alert_level == BudgetAlert.ORANGE
        assert status.is_over_budget is False

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_red_alert(self, mock_settings, mock_session):
        """Test budget status in RED zone (90-100%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 95% usage ($28.50 of $30)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 28.50

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        assert status.percentage_used == 95.0
        assert status.alert_level == BudgetAlert.RED
        assert status.is_over_budget is False

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_critical_alert(self, mock_settings, mock_session):
        """Test budget status in CRITICAL zone (>100%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 110% usage ($33 of $30)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 33.00

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        assert status.used_budget == 33.0
        assert status.percentage_used == pytest.approx(110.0, rel=1e-9)
        assert status.alert_level == BudgetAlert.CRITICAL
        assert status.is_over_budget is True
        assert status.remaining_budget == 0.0  # Should be max(0, ...)

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.datetime")
    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_days_remaining_december(
        self, mock_settings, mock_session, mock_datetime
    ):
        """Test days remaining calculation for December (year rollover)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock current date as December 20, 2024
        now = datetime(2024, 12, 20, 10, 0, 0)
        mock_datetime.now.return_value = now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10.00

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        # Should calculate days until January 1, 2025
        assert status.days_remaining == 12  # Dec 20 to Jan 1 (inclusive)

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.datetime")
    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_days_remaining_regular_month(
        self, mock_settings, mock_session, mock_datetime
    ):
        """Test days remaining calculation for regular month"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock current date as March 15, 2024
        now = datetime(2024, 3, 15, 10, 0, 0)
        mock_datetime.now.return_value = now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10.00

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        # Should calculate days until April 1
        assert status.days_remaining == 17  # Mar 15 to Apr 1 (inclusive)

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.datetime")
    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_projected_cost(
        self, mock_settings, mock_session, mock_datetime
    ):
        """Test projected monthly cost calculation"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock current date as March 15 (15 days elapsed)
        now = datetime(2024, 3, 15, 10, 0, 0)
        month_start = datetime(2024, 3, 1, 0, 0, 0)
        mock_datetime.now.return_value = now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock $15 spent in 15 days = $1/day average
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 15.00

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        # Daily average: $15 / 15 days = $1/day
        # Projected monthly: $1/day * 30 days = $30
        assert status.projected_monthly_cost == 30.0

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_budget_status_exception_handling(self, mock_settings, mock_session):
        """Test budget status returns fallback on exception"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock database session that raises exception
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")

        manager = BudgetManager()
        status = manager.get_current_budget_status()

        # Should return fallback status
        assert status.total_budget == 30.0
        assert status.used_budget == 0.0
        assert status.remaining_budget == 30.0
        assert status.percentage_used == 0.0
        assert status.alert_level == BudgetAlert.GREEN
        assert status.days_remaining == 30
        assert status.projected_monthly_cost == 0.0
        assert status.is_over_budget is False

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    @patch("app.services.budget_manager.datetime")
    def test_budget_status_with_user_id_monthly_period(
        self, mock_datetime, mock_settings, mock_session
    ):
        """Test budget status with user_id using monthly budget period"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock current time
        now = datetime(2025, 12, 15, 10, 30, 0)
        mock_datetime.now.return_value = now

        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Create mock user budget settings
        period_start = datetime(2025, 12, 1, 0, 0, 0)
        period_end = datetime(2026, 1, 1, 0, 0, 0)

        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.get_effective_limit.return_value = 50.0
        mock_user_settings.current_period_start = period_start
        mock_user_settings.current_period_end = period_end
        mock_user_settings.budget_period.value = "monthly"
        mock_user_settings.alert_threshold_yellow = 50.0
        mock_user_settings.alert_threshold_orange = 75.0
        mock_user_settings.alert_threshold_red = 90.0

        # Mock query to return user settings
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query

        # First call returns user settings, second returns usage cost
        mock_query.first.return_value = mock_user_settings
        mock_query.scalar.return_value = 30.0  # $30 used of $50

        manager = BudgetManager()
        status = manager.get_current_budget_status(user_id="test_user_123")

        # Verify user-specific budget was used
        assert status.total_budget == 50.0
        assert status.used_budget == 30.0
        assert status.remaining_budget == 20.0
        assert status.percentage_used == 60.0
        assert status.alert_level == BudgetAlert.YELLOW  # 60% >= 50% (yellow threshold), < 75% (orange)

        # Verify days remaining calculation (Dec 15 to Jan 1 = 16 days using .days)
        assert status.days_remaining == 16

        # Verify projected cost: 15 days elapsed (Dec 1-15), $30/15 * 30 = $60
        assert status.projected_monthly_cost == 60.0

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    @patch("app.services.budget_manager.datetime")
    def test_budget_status_with_user_id_weekly_period(
        self, mock_datetime, mock_settings, mock_session
    ):
        """Test budget status with user_id using weekly budget period"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        now = datetime(2025, 12, 15, 10, 30, 0)
        mock_datetime.now.return_value = now

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        period_start = datetime(2025, 12, 10, 0, 0, 0)
        period_end = datetime(2025, 12, 17, 0, 0, 0)

        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.get_effective_limit.return_value = 20.0
        mock_user_settings.current_period_start = period_start
        mock_user_settings.current_period_end = period_end
        mock_user_settings.budget_period.value = "weekly"
        mock_user_settings.alert_threshold_yellow = 50.0
        mock_user_settings.alert_threshold_orange = 75.0
        mock_user_settings.alert_threshold_red = 90.0

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user_settings
        mock_query.scalar.return_value = 18.0  # $18 used of $20

        manager = BudgetManager()
        status = manager.get_current_budget_status(user_id="test_user_123")

        assert status.total_budget == 20.0
        assert status.used_budget == 18.0
        assert status.percentage_used == 90.0
        assert status.alert_level == BudgetAlert.RED  # 90% >= 90% (red threshold)

        # Days remaining: Dec 15 to Dec 17 = 1 day (using .days)
        assert status.days_remaining == 1

        # Projected weekly: 6 days elapsed (Dec 10-15), $18/6 = $3/day * 7 = $21
        assert abs(status.projected_monthly_cost - 21.0) < 0.1

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    @patch("app.services.budget_manager.datetime")
    def test_budget_status_with_user_id_daily_period(
        self, mock_datetime, mock_settings, mock_session
    ):
        """Test budget status with user_id using daily budget period"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        now = datetime(2025, 12, 15, 18, 30, 0)
        mock_datetime.now.return_value = now

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        period_start = datetime(2025, 12, 15, 0, 0, 0)
        period_end = datetime(2025, 12, 16, 0, 0, 0)

        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.get_effective_limit.return_value = 5.0
        mock_user_settings.current_period_start = period_start
        mock_user_settings.current_period_end = period_end
        mock_user_settings.budget_period.value = "daily"
        mock_user_settings.alert_threshold_yellow = 50.0
        mock_user_settings.alert_threshold_orange = 75.0
        mock_user_settings.alert_threshold_red = 90.0

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user_settings
        mock_query.scalar.return_value = 5.5  # $5.50 used of $5.00

        manager = BudgetManager()
        status = manager.get_current_budget_status(user_id="test_user_123")

        assert status.total_budget == 5.0
        assert status.used_budget == 5.5
        assert abs(status.percentage_used - 110.0) < 0.01  # Floating point tolerance
        assert status.alert_level == BudgetAlert.CRITICAL  # >= 100%
        assert status.is_over_budget is True

        # Days remaining: same day, so 0
        assert status.days_remaining == 0

        # Projected daily: equals current cost for daily period
        assert status.projected_monthly_cost == 5.5

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    @patch("app.services.budget_manager.datetime")
    def test_budget_status_with_user_id_custom_period(
        self, mock_datetime, mock_settings, mock_session
    ):
        """Test budget status with user_id using custom budget period"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        now = datetime(2025, 12, 15, 10, 0, 0)
        mock_datetime.now.return_value = now

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        period_start = datetime(2025, 12, 1, 0, 0, 0)
        period_end = datetime(2025, 12, 15, 0, 0, 0)

        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.get_effective_limit.return_value = 40.0
        mock_user_settings.current_period_start = period_start
        mock_user_settings.current_period_end = period_end
        mock_user_settings.budget_period.value = "custom"
        mock_user_settings.custom_period_days = 14
        mock_user_settings.alert_threshold_yellow = 50.0
        mock_user_settings.alert_threshold_orange = 75.0
        mock_user_settings.alert_threshold_red = 90.0

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user_settings
        mock_query.scalar.return_value = 20.0  # $20 used of $40

        manager = BudgetManager()
        status = manager.get_current_budget_status(user_id="test_user_123")

        assert status.total_budget == 40.0
        assert status.used_budget == 20.0
        assert status.percentage_used == 50.0
        assert status.alert_level == BudgetAlert.YELLOW  # 50% >= 50% (yellow threshold)

        # Days remaining: Dec 15 to Dec 15 = 0
        assert status.days_remaining == 0

        # Projected: 15 days elapsed (Dec 1-15), $20/15 * 14 = ~$18.67
        assert abs(status.projected_monthly_cost - 18.67) < 0.1

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    @patch("app.services.budget_manager.datetime")
    def test_budget_status_with_user_id_custom_no_days_fallback(
        self, mock_datetime, mock_settings, mock_session
    ):
        """Test budget status with user_id custom period without custom_period_days (fallback to monthly)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        now = datetime(2025, 12, 15, 10, 0, 0)
        mock_datetime.now.return_value = now

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        period_start = datetime(2025, 12, 1, 0, 0, 0)
        period_end = datetime(2025, 12, 31, 23, 59, 59)

        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.get_effective_limit.return_value = 35.0
        mock_user_settings.current_period_start = period_start
        mock_user_settings.current_period_end = period_end
        mock_user_settings.budget_period.value = "custom"
        mock_user_settings.custom_period_days = None  # No custom days set
        mock_user_settings.alert_threshold_yellow = 50.0
        mock_user_settings.alert_threshold_orange = 75.0
        mock_user_settings.alert_threshold_red = 90.0

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user_settings
        mock_query.scalar.return_value = 10.0

        manager = BudgetManager()
        status = manager.get_current_budget_status(user_id="test_user_123")

        assert status.total_budget == 35.0
        assert status.used_budget == 10.0
        assert status.alert_level == BudgetAlert.GREEN

        # Projected should use monthly fallback (30 days)
        # 15 days elapsed (Dec 1-15), $10/15 * 30 = $20
        assert status.projected_monthly_cost == 20.0

        mock_db.close.assert_called_once()


# ============================================================================
# Test BudgetManager._determine_alert_level
# ============================================================================


class TestDetermineAlertLevel:
    """Test _determine_alert_level method"""

    @patch("app.services.budget_manager.get_settings")
    def test_determine_alert_green(self, mock_settings):
        """Test GREEN alert level (<50%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert manager._determine_alert_level(0.0) == BudgetAlert.GREEN
        assert manager._determine_alert_level(0.25) == BudgetAlert.GREEN
        assert manager._determine_alert_level(0.49) == BudgetAlert.GREEN

    @patch("app.services.budget_manager.get_settings")
    def test_determine_alert_yellow(self, mock_settings):
        """Test YELLOW alert level (50-75%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert manager._determine_alert_level(0.50) == BudgetAlert.YELLOW
        assert manager._determine_alert_level(0.60) == BudgetAlert.YELLOW
        assert manager._determine_alert_level(0.74) == BudgetAlert.YELLOW

    @patch("app.services.budget_manager.get_settings")
    def test_determine_alert_orange(self, mock_settings):
        """Test ORANGE alert level (75-90%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert manager._determine_alert_level(0.75) == BudgetAlert.ORANGE
        assert manager._determine_alert_level(0.80) == BudgetAlert.ORANGE
        assert manager._determine_alert_level(0.89) == BudgetAlert.ORANGE

    @patch("app.services.budget_manager.get_settings")
    def test_determine_alert_red(self, mock_settings):
        """Test RED alert level (90-100%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert manager._determine_alert_level(0.90) == BudgetAlert.RED
        assert manager._determine_alert_level(0.95) == BudgetAlert.RED
        assert manager._determine_alert_level(0.99) == BudgetAlert.RED

    @patch("app.services.budget_manager.get_settings")
    def test_determine_alert_critical(self, mock_settings):
        """Test CRITICAL alert level (>=100%)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        assert manager._determine_alert_level(1.0) == BudgetAlert.CRITICAL
        assert manager._determine_alert_level(1.1) == BudgetAlert.CRITICAL
        assert manager._determine_alert_level(2.0) == BudgetAlert.CRITICAL


# ============================================================================
# Test Module-Level Convenience Functions
# ============================================================================


class TestConvenienceFunctions:
    """Test module-level convenience functions"""

    @patch.object(budget_manager, "get_current_budget_status")
    def test_get_budget_status(self, mock_method):
        """Test get_budget_status convenience function"""
        mock_status = BudgetStatus(
            total_budget=30.0,
            used_budget=15.0,
            remaining_budget=15.0,
            percentage_used=50.0,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=15,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )
        mock_method.return_value = mock_status

        status = get_budget_status()

        assert status == mock_status
        mock_method.assert_called_once()

    @patch.object(budget_manager, "can_afford_operation")
    def test_can_afford(self, mock_method):
        """Test can_afford convenience function"""
        mock_method.return_value = True

        result = can_afford(0.05)

        assert result is True
        mock_method.assert_called_once_with(0.05)

    @patch.object(budget_manager, "record_api_usage")
    def test_record_usage(self, mock_method):
        """Test record_usage convenience function"""
        mock_method.return_value = True

        result = record_usage(
            user_id="user123",
            provider="anthropic",
            endpoint="claude-3-haiku",
            request_type="ai_generation",
            tokens=1000,
            cost=0.05,
        )

        assert result is True
        mock_method.assert_called_once_with(
            "user123", "anthropic", "claude-3-haiku", "ai_generation", 1000, 0.05
        )

    @patch.object(budget_manager, "estimate_cost")
    def test_estimate_cost_function(self, mock_method):
        """Test estimate_cost convenience function"""
        mock_estimate = CostEstimate(
            estimated_cost=0.05,
            provider="anthropic",
            service_type="llm",
            tokens_estimated=1000,
            confidence=0.9,
        )
        mock_method.return_value = mock_estimate

        result = estimate_cost(
            provider="anthropic",
            model="claude-3-haiku",
            service_type="llm",
            input_tokens=500,
            output_tokens=500,
        )

        assert result == mock_estimate
        mock_method.assert_called_once()


# Continue in next part...

# ============================================================================
# Test BudgetManager.estimate_cost and related methods
# ============================================================================


class TestEstimateCost:
    """Test estimate_cost and cost calculation methods"""

    @patch("app.services.budget_manager.get_settings")
    def test_estimate_cost_llm_anthropic_haiku(self, mock_settings):
        """Test cost estimation for Anthropic Claude Haiku (LLM)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        estimate = manager.estimate_cost(
            provider="anthropic",
            model="claude-3-haiku",
            service_type="llm",
            input_tokens=1000,
            output_tokens=500,
        )

        # Claude Haiku: input=$0.00025/1K, output=$0.00125/1K
        # Cost = (1000/1000 * 0.00025) + (500/1000 * 0.00125)
        # Cost = 0.00025 + 0.000625 = 0.000875
        assert estimate.estimated_cost == pytest.approx(0.000875, rel=1e-6)
        assert estimate.provider == "anthropic"
        assert estimate.service_type == "llm"
        assert estimate.tokens_estimated == 1500
        assert estimate.confidence == 0.9

    @patch("app.services.budget_manager.get_settings")
    def test_estimate_cost_llm_mistral_tiny(self, mock_settings):
        """Test cost estimation for Mistral Tiny"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        estimate = manager.estimate_cost(
            provider="mistral",
            model="mistral-tiny",
            service_type="llm",
            input_tokens=2000,
            output_tokens=1000,
        )

        # Mistral Tiny: input=$0.00014/1K, output=$0.00042/1K
        # Cost = (2000/1000 * 0.00014) + (1000/1000 * 0.00042)
        # Cost = 0.00028 + 0.00042 = 0.0007
        assert estimate.estimated_cost == pytest.approx(0.0007, rel=1e-6)
        assert estimate.confidence == 0.9

    @patch("app.services.budget_manager.get_settings")
    def test_estimate_cost_unknown_provider_fallback(self, mock_settings):
        """Test fallback pricing for unknown provider"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        estimate = manager.estimate_cost(
            provider="unknown_provider",
            model="unknown_model",
            service_type="llm",
            input_tokens=1000,
            output_tokens=500,
        )

        # Fallback: $0.002 per 1K tokens
        # Cost = (1500/1000) * 0.002 = 0.003
        assert estimate.estimated_cost == pytest.approx(0.003, rel=1e-6)
        assert estimate.confidence == 0.5

    @patch("app.services.budget_manager.get_settings")
    def test_estimate_cost_unknown_model_fallback(self, mock_settings):
        """Test fallback pricing for unknown model in known provider"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        estimate = manager.estimate_cost(
            provider="anthropic",
            model="claude-unknown",
            service_type="llm",
            input_tokens=1000,
            output_tokens=500,
        )

        # Should use fallback pricing
        assert estimate.estimated_cost == pytest.approx(0.003, rel=1e-6)
        assert estimate.confidence == 0.5

    @patch("app.services.budget_manager.get_settings")
    def test_estimate_cost_unknown_service_type(self, mock_settings):
        """Test unknown service type returns minimal cost"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        estimate = manager.estimate_cost(
            provider="anthropic",
            model="claude-3-haiku",
            service_type="unknown_service",
            input_tokens=1000,
        )

        # Unknown service type should return 0.0 with low confidence
        assert estimate.estimated_cost == 0.0
        assert estimate.confidence == 0.5

    @patch("app.services.budget_manager.get_settings")
    def test_estimate_cost_exception_handling(self, mock_settings):
        """Test exception handling returns fallback estimate"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        # Cause an exception by making _calculate_cost_from_pricing fail
        with patch.object(
            manager, "_calculate_cost_from_pricing", side_effect=Exception("Test error")
        ):
            estimate = manager.estimate_cost(
                provider="anthropic",
                model="claude-3-haiku",
                service_type="llm",
                input_tokens=1000,
                output_tokens=500,
            )

        # Should return fallback estimate
        assert estimate.estimated_cost == 0.01
        assert estimate.confidence == 0.1
        assert estimate.tokens_estimated == 1500

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_llm_cost_input_only(self, mock_settings):
        """Test LLM cost calculation with input tokens only"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"input": 0.001, "output": 0.002}

        cost, confidence = manager._calculate_llm_cost(pricing, 1000, 0)

        assert cost == 0.001
        assert confidence == 0.9

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_llm_cost_output_only(self, mock_settings):
        """Test LLM cost calculation with output tokens only"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"input": 0.001, "output": 0.002}

        cost, confidence = manager._calculate_llm_cost(pricing, 0, 1000)

        assert cost == 0.002
        assert confidence == 0.9

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_llm_cost_no_tokens(self, mock_settings):
        """Test LLM cost calculation with no tokens"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"input": 0.001, "output": 0.002}

        cost, confidence = manager._calculate_llm_cost(pricing, 0, 0)

        assert cost == 0.0
        assert confidence == 0.5  # Low confidence when no tokens

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_stt_cost(self, mock_settings):
        """Test STT cost calculation"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"per_minute": 0.02}

        cost, confidence = manager._calculate_stt_cost(pricing, 10.5)

        assert cost == 0.21
        assert confidence == 0.85

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_stt_cost_no_pricing(self, mock_settings):
        """Test STT cost calculation without per_minute pricing"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {}  # Missing per_minute

        cost, confidence = manager._calculate_stt_cost(pricing, 10.5)

        assert cost == 0.0
        assert confidence == 0.5

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_tts_cost(self, mock_settings):
        """Test TTS cost calculation"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"per_character": 0.00002}  # $0.02 per 1K chars

        cost, confidence = manager._calculate_tts_cost(pricing, 5000)

        assert cost == 0.1
        assert confidence == 0.85

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_tts_cost_no_pricing(self, mock_settings):
        """Test TTS cost calculation without per_character pricing"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {}  # Missing per_character

        cost, confidence = manager._calculate_tts_cost(pricing, 5000)

        assert cost == 0.0
        assert confidence == 0.5

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_service_cost_llm(self, mock_settings):
        """Test _calculate_service_cost for LLM service type"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"input": 0.001, "output": 0.003}

        cost, confidence = manager._calculate_service_cost(
            service_type="llm",
            pricing=pricing,
            input_tokens=1000,
            output_tokens=500,
            audio_minutes=0,
            characters=0,
        )

        # Should call _calculate_llm_cost
        expected_cost = (1000 / 1000) * 0.001 + (500 / 1000) * 0.003
        assert cost == pytest.approx(expected_cost, rel=1e-6)
        assert confidence == 0.9

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_service_cost_stt(self, mock_settings):
        """Test _calculate_service_cost for STT service type (line 267)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"per_minute": 0.025}

        cost, confidence = manager._calculate_service_cost(
            service_type="stt",
            pricing=pricing,
            input_tokens=0,
            output_tokens=0,
            audio_minutes=10.5,
            characters=0,
        )

        # Should call _calculate_stt_cost (line 267)
        assert cost == pytest.approx(0.2625, rel=1e-6)
        assert confidence == 0.85

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_service_cost_tts(self, mock_settings):
        """Test _calculate_service_cost for TTS service type (line 269)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {"per_character": 0.00001}

        cost, confidence = manager._calculate_service_cost(
            service_type="tts",
            pricing=pricing,
            input_tokens=0,
            output_tokens=0,
            audio_minutes=0,
            characters=5000,
        )

        # Should call _calculate_tts_cost (line 269)
        assert cost == pytest.approx(0.05, rel=1e-6)
        assert confidence == 0.85

    @patch("app.services.budget_manager.get_settings")
    def test_calculate_service_cost_unknown_type(self, mock_settings):
        """Test _calculate_service_cost for unknown service type"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        pricing = {}

        cost, confidence = manager._calculate_service_cost(
            service_type="unknown",
            pricing=pricing,
            input_tokens=0,
            output_tokens=0,
            audio_minutes=0,
            characters=0,
        )

        # Should return default values for unknown type
        assert cost == 0.0
        assert confidence == 0.5

    @patch("app.services.budget_manager.get_settings")
    def test_fallback_cost_estimate_llm(self, mock_settings):
        """Test fallback cost estimation for LLM"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        cost = manager._fallback_cost_estimate("llm", 1000, 500, 0, 0)

        # Conservative: $0.002 per 1K tokens
        assert cost == pytest.approx(0.003, rel=1e-6)

    @patch("app.services.budget_manager.get_settings")
    def test_fallback_cost_estimate_stt(self, mock_settings):
        """Test fallback cost estimation for STT"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        cost = manager._fallback_cost_estimate("stt", 0, 0, 5.0, 0)

        # Conservative: $0.025 per minute
        assert cost == pytest.approx(0.125, rel=1e-6)

    @patch("app.services.budget_manager.get_settings")
    def test_fallback_cost_estimate_tts(self, mock_settings):
        """Test fallback cost estimation for TTS"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        cost = manager._fallback_cost_estimate("tts", 0, 0, 0, 3000)

        # Conservative: $0.025 per 1K chars
        assert cost == pytest.approx(0.075, rel=1e-6)

    @patch("app.services.budget_manager.get_settings")
    def test_fallback_cost_estimate_unknown(self, mock_settings):
        """Test fallback cost estimation for unknown service"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        cost = manager._fallback_cost_estimate("unknown", 0, 0, 0, 0)

        # Minimal fallback
        assert cost == 0.01


# ============================================================================
# Test BudgetManager.can_afford_operation
# ============================================================================


class TestCanAffordOperation:
    """Test can_afford_operation method"""

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_green_zone(self, mock_settings, mock_session):
        """Test affordability in GREEN zone (plenty of budget)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 20% usage ($6 of $30, $24 remaining)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 6.00

        manager = BudgetManager()

        # Can afford $1 operation (with 10% buffer = $1.10 needed)
        assert manager.can_afford_operation(1.0) is True

        mock_db.close.assert_called()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_yellow_zone(self, mock_settings, mock_session):
        """Test affordability in YELLOW zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 60% usage ($18 of $30, $12 remaining)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 18.00

        manager = BudgetManager()

        # Can afford $5 operation (with 10% buffer = $5.50 needed, $12 available)
        assert manager.can_afford_operation(5.0) is True

        # Cannot afford $11 operation (with buffer = $12.10 needed, only $12 available)
        assert manager.can_afford_operation(11.0) is False

        mock_db.close.assert_called()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_red_zone_small_cost(self, mock_settings, mock_session):
        """Test affordability in RED zone with small cost"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 95% usage ($28.50 of $30, $1.50 remaining)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 28.50

        manager = BudgetManager()

        # Can afford $0.04 operation (< $0.05 limit for RED zone)
        assert manager.can_afford_operation(0.04) is True

        mock_db.close.assert_called()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_red_zone_large_cost(self, mock_settings, mock_session):
        """Test affordability in RED zone with large cost"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 95% usage ($28.50 of $30, $1.50 remaining)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 28.50

        manager = BudgetManager()

        # Cannot afford $0.06 operation (>= $0.05 limit for RED zone)
        assert manager.can_afford_operation(0.06) is False

        mock_db.close.assert_called()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_critical_zone_tiny_cost(self, mock_settings, mock_session):
        """Test affordability in CRITICAL zone with tiny cost"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 110% usage ($33 of $30, $0 remaining, over budget)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 33.00

        manager = BudgetManager()

        # Cannot afford $0.005 operation - even though < $0.01 limit,
        # remaining budget is 0 (over budget), so with buffer it's not affordable
        assert manager.can_afford_operation(0.005) is False

        mock_db.close.assert_called()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_critical_zone_small_cost(self, mock_settings, mock_session):
        """Test affordability in CRITICAL zone with small cost"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 110% usage ($33 of $30, over budget)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 33.00

        manager = BudgetManager()

        # Cannot afford $0.02 operation (>= $0.01 limit for CRITICAL zone)
        assert manager.can_afford_operation(0.02) is False

        mock_db.close.assert_called()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_can_afford_custom_buffer(self, mock_settings, mock_session):
        """Test custom buffer percentage"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock 50% usage ($15 of $30, $15 remaining)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 15.00

        manager = BudgetManager()

        # With 20% buffer: $10 * 1.20 = $12 needed, $15 available = affordable
        assert manager.can_afford_operation(10.0, buffer_percentage=0.20) is True

        # With 50% buffer: $10 * 1.50 = $15 needed, $15 available = affordable (exact)
        assert manager.can_afford_operation(10.0, buffer_percentage=0.50) is True

        # With 60% buffer: $10 * 1.60 = $16 needed, only $15 available = not affordable
        assert manager.can_afford_operation(10.0, buffer_percentage=0.60) is False

        mock_db.close.assert_called()


# Continue in next part...

# ============================================================================
# Test BudgetManager.record_api_usage
# ============================================================================


class TestRecordAPIUsage:
    """Test record_api_usage method"""

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_record_usage_without_user(self, mock_settings, mock_session):
        """Test recording API usage without user_id"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        manager = BudgetManager()
        result = manager.record_api_usage(
            user_id=None,
            provider="anthropic",
            endpoint="claude-3-haiku",
            request_type="ai_generation",
            tokens_used=1000,
            estimated_cost=0.05,
            status="success",
        )

        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_record_usage_with_user(self, mock_settings, mock_session):
        """Test recording API usage with user_id"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock user lookup
        mock_user = Mock()
        mock_user.id = 123
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        manager = BudgetManager()
        result = manager.record_api_usage(
            user_id="user123",
            provider="mistral",
            endpoint="mistral-tiny",
            request_type="llm_completion",
            tokens_used=2000,
            estimated_cost=0.07,
            actual_cost=0.065,
            status="success",
            metadata={"model": "mistral-tiny", "temperature": 0.7},
        )

        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_record_usage_user_not_found(self, mock_settings, mock_session):
        """Test recording API usage when user not found"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock user lookup returning None
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        manager = BudgetManager()
        result = manager.record_api_usage(
            user_id="nonexistent_user",
            provider="anthropic",
            endpoint="claude-3-haiku",
            request_type="ai_generation",
            tokens_used=1000,
            estimated_cost=0.05,
        )

        assert result is True
        # Should still record usage with db_user_id=None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_record_usage_exception_handling(self, mock_settings, mock_session):
        """Test exception handling in record_api_usage"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock database error
        mock_db.add.side_effect = Exception("Database error")

        manager = BudgetManager()
        result = manager.record_api_usage(
            user_id=None,
            provider="anthropic",
            endpoint="claude-3-haiku",
            request_type="ai_generation",
            tokens_used=1000,
            estimated_cost=0.05,
        )

        assert result is False
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()


# ============================================================================
# Test BudgetManager.get_cost_breakdown
# ============================================================================


class TestGetCostBreakdown:
    """Test get_cost_breakdown method"""

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_cost_breakdown_with_data(self, mock_settings, mock_session):
        """Test cost breakdown with usage data"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock provider costs query
        provider_row1 = Mock()
        provider_row1.api_provider = "anthropic"
        provider_row1.total_cost = 10.50
        provider_row1.request_count = 100
        provider_row1.total_tokens = 50000

        provider_row2 = Mock()
        provider_row2.api_provider = "mistral"
        provider_row2.total_cost = 5.25
        provider_row2.request_count = 50
        provider_row2.total_tokens = 25000

        # Mock daily costs query
        daily_row1 = Mock()
        daily_row1.date = datetime(2024, 3, 15).date()
        daily_row1.daily_cost = 5.00

        daily_row2 = Mock()
        daily_row2.date = datetime(2024, 3, 16).date()
        daily_row2.daily_cost = 7.50

        # Mock request type costs query
        request_row1 = Mock()
        request_row1.request_type = "llm_completion"
        request_row1.total_cost = 12.00
        request_row1.request_count = 120

        request_row2 = Mock()
        request_row2.request_type = "stt_transcription"
        request_row2.total_cost = 3.75
        request_row2.request_count = 30

        # Setup query mock to return different results based on grouping
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query

        # First call: provider breakdown
        # Second call: daily costs
        # Third call: request type breakdown
        mock_query.group_by.return_value.all.side_effect = [
            [provider_row1, provider_row2],
            [daily_row1, daily_row2],
            [request_row1, request_row2],
        ]

        manager = BudgetManager()
        breakdown = manager.get_cost_breakdown(days=30)

        assert breakdown["period_days"] == 30
        assert breakdown["total_cost"] == 15.75  # 10.50 + 5.25
        assert breakdown["total_requests"] == 150  # 100 + 50
        assert breakdown["total_tokens"] == 75000  # 50000 + 25000

        assert len(breakdown["provider_breakdown"]) == 2
        assert breakdown["provider_breakdown"][0]["provider"] == "anthropic"
        assert breakdown["provider_breakdown"][0]["cost"] == 10.50

        assert len(breakdown["daily_costs"]) == 2
        assert breakdown["daily_costs"][0]["date"] == "2024-03-15"
        assert breakdown["daily_costs"][0]["cost"] == 5.00

        assert len(breakdown["request_type_breakdown"]) == 2
        assert breakdown["request_type_breakdown"][0]["type"] == "llm_completion"
        assert breakdown["request_type_breakdown"][0]["cost"] == 12.00

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_cost_breakdown_no_data(self, mock_settings, mock_session):
        """Test cost breakdown with no usage data"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock empty results
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value.all.return_value = []

        manager = BudgetManager()
        breakdown = manager.get_cost_breakdown(days=7)

        assert breakdown["period_days"] == 7
        assert breakdown["total_cost"] == 0.0
        assert breakdown["total_requests"] == 0
        assert breakdown["total_tokens"] == 0
        assert breakdown["provider_breakdown"] == []
        assert breakdown["daily_costs"] == []
        assert breakdown["request_type_breakdown"] == []

        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_cost_breakdown_exception_handling(self, mock_settings, mock_session):
        """Test exception handling in cost breakdown"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock database error
        mock_db.query.side_effect = Exception("Database error")

        manager = BudgetManager()
        breakdown = manager.get_cost_breakdown(days=30)

        # Should return empty breakdown
        assert breakdown["period_days"] == 30
        assert breakdown["total_cost"] == 0.0
        assert breakdown["total_requests"] == 0
        assert breakdown["total_tokens"] == 0
        assert breakdown["provider_breakdown"] == []

        mock_db.close.assert_called_once()


# Continue in next part...

# ============================================================================
# Test BudgetManager.get_optimization_recommendations
# ============================================================================


class TestGetOptimizationRecommendations:
    """Test get_optimization_recommendations method"""

    @patch.object(BudgetManager, "get_cost_breakdown")
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_recommendations_red_alert(
        self, mock_settings, mock_status, mock_breakdown
    ):
        """Test recommendations when in RED alert zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock RED alert status
        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=28.0,
            remaining_budget=2.0,
            percentage_used=93.3,
            alert_level=BudgetAlert.RED,
            days_remaining=10,
            projected_monthly_cost=32.0,
            is_over_budget=False,
        )

        # Mock cost breakdown
        mock_breakdown.return_value = {
            "provider_breakdown": [
                {"provider": "anthropic", "cost": 20.0},
                {"provider": "mistral", "cost": 8.0},
            ]
        }

        manager = BudgetManager()
        recommendations = manager.get_optimization_recommendations()

        # Should have at least 2 recommendations (budget alert + provider optimization)
        assert len(recommendations) >= 2

        # Check for budget alert recommendation
        budget_rec = next((r for r in recommendations if r["type"] == "urgent"), None)
        assert budget_rec is not None
        assert "93.3%" in budget_rec["description"]

        # Check for provider optimization recommendation
        provider_rec = next(
            (r for r in recommendations if r["type"] == "optimization"), None
        )
        assert provider_rec is not None
        assert "anthropic" in provider_rec["description"]

    @patch.object(BudgetManager, "get_cost_breakdown")
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_recommendations_critical_alert(
        self, mock_settings, mock_status, mock_breakdown
    ):
        """Test recommendations when in CRITICAL alert zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock CRITICAL alert status
        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=35.0,
            remaining_budget=0.0,
            percentage_used=116.7,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=5,
            projected_monthly_cost=42.0,
            is_over_budget=True,
        )

        # Mock cost breakdown
        mock_breakdown.return_value = {
            "provider_breakdown": [
                {"provider": "mistral", "cost": 25.0},
                {"provider": "anthropic", "cost": 10.0},
            ]
        }

        manager = BudgetManager()
        recommendations = manager.get_optimization_recommendations()

        # Should have urgent budget alert
        budget_rec = next((r for r in recommendations if r["type"] == "urgent"), None)
        assert budget_rec is not None
        assert "116.7%" in budget_rec["description"]

    @patch.object(BudgetManager, "get_cost_breakdown")
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_recommendations_projected_overage(
        self, mock_settings, mock_status, mock_breakdown
    ):
        """Test recommendations when projected to exceed budget"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock status with high projection
        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=20.0,
            remaining_budget=10.0,
            percentage_used=66.7,
            alert_level=BudgetAlert.ORANGE,
            days_remaining=10,
            projected_monthly_cost=35.0,  # 35 > 30 * 1.1 = 33
            is_over_budget=False,
        )

        # Mock cost breakdown
        mock_breakdown.return_value = {
            "provider_breakdown": [
                {"provider": "anthropic", "cost": 15.0},
                {"provider": "mistral", "cost": 5.0},
            ]
        }

        manager = BudgetManager()
        recommendations = manager.get_optimization_recommendations()

        # Should have projection warning
        proj_rec = next((r for r in recommendations if r["type"] == "warning"), None)
        assert proj_rec is not None
        assert "$35.00" in proj_rec["description"]

    @patch.object(BudgetManager, "get_cost_breakdown")
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_recommendations_green_zone(
        self, mock_settings, mock_status, mock_breakdown
    ):
        """Test recommendations in GREEN zone (no urgent issues)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock GREEN status
        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.3,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=25.0,
            is_over_budget=False,
        )

        # Mock cost breakdown
        mock_breakdown.return_value = {
            "provider_breakdown": [
                {"provider": "anthropic", "cost": 7.0},
                {"provider": "mistral", "cost": 3.0},
            ]
        }

        manager = BudgetManager()
        recommendations = manager.get_optimization_recommendations()

        # Should still have provider optimization (always present)
        assert len(recommendations) >= 1
        provider_rec = next(
            (r for r in recommendations if r["type"] == "optimization"), None
        )
        assert provider_rec is not None


# ============================================================================
# Test BudgetManager.get_recommended_strategy
# ============================================================================


class TestGetRecommendedStrategy:
    """Test get_recommended_strategy method"""

    @patch("app.services.budget_manager.get_settings")
    def test_strategy_green_zone(self, mock_settings):
        """Test strategy for GREEN zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        status = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.3,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=25.0,
            is_over_budget=False,
        )

        strategy = manager.get_recommended_strategy(status)
        assert strategy == CostOptimizationStrategy.QUALITY_FIRST

    @patch("app.services.budget_manager.get_settings")
    def test_strategy_yellow_zone(self, mock_settings):
        """Test strategy for YELLOW zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        status = BudgetStatus(
            total_budget=30.0,
            used_budget=18.0,
            remaining_budget=12.0,
            percentage_used=60.0,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=15,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )

        strategy = manager.get_recommended_strategy(status)
        assert strategy == CostOptimizationStrategy.QUALITY_FIRST

    @patch("app.services.budget_manager.get_settings")
    def test_strategy_orange_zone(self, mock_settings):
        """Test strategy for ORANGE zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        status = BudgetStatus(
            total_budget=30.0,
            used_budget=24.0,
            remaining_budget=6.0,
            percentage_used=80.0,
            alert_level=BudgetAlert.ORANGE,
            days_remaining=10,
            projected_monthly_cost=32.0,
            is_over_budget=False,
        )

        strategy = manager.get_recommended_strategy(status)
        assert strategy == CostOptimizationStrategy.BALANCED

    @patch("app.services.budget_manager.get_settings")
    def test_strategy_red_zone(self, mock_settings):
        """Test strategy for RED zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        status = BudgetStatus(
            total_budget=30.0,
            used_budget=28.0,
            remaining_budget=2.0,
            percentage_used=93.3,
            alert_level=BudgetAlert.RED,
            days_remaining=5,
            projected_monthly_cost=35.0,
            is_over_budget=False,
        )

        strategy = manager.get_recommended_strategy(status)
        assert strategy == CostOptimizationStrategy.CHEAPEST_FIRST

    @patch("app.services.budget_manager.get_settings")
    def test_strategy_critical_zone(self, mock_settings):
        """Test strategy for CRITICAL zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()

        status = BudgetStatus(
            total_budget=30.0,
            used_budget=35.0,
            remaining_budget=0.0,
            percentage_used=116.7,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=2,
            projected_monthly_cost=42.0,
            is_over_budget=True,
        )

        strategy = manager.get_recommended_strategy(status)
        assert strategy == CostOptimizationStrategy.EMERGENCY_ONLY

    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_strategy_without_status_parameter(self, mock_settings, mock_status):
        """Test strategy when status parameter is None (fetches automatically)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.3,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=25.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        strategy = manager.get_recommended_strategy(budget_status=None)

        assert strategy == CostOptimizationStrategy.QUALITY_FIRST
        mock_status.assert_called_once()


# ============================================================================
# Test BudgetManager.check_budget_alerts
# ============================================================================


class TestCheckBudgetAlerts:
    """Test check_budget_alerts method"""

    @pytest.mark.asyncio
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    async def test_check_alerts_critical(self, mock_settings, mock_status):
        """Test alerts in CRITICAL zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=35.0,
            remaining_budget=0.0,
            percentage_used=116.7,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=2,
            projected_monthly_cost=42.0,
            is_over_budget=True,
        )

        manager = BudgetManager()
        alerts = await manager.check_budget_alerts()

        assert len(alerts) == 1
        assert alerts[0]["level"] == "critical"
        assert "Budget Exceeded" in alerts[0]["title"]
        assert "$5.00" in alerts[0]["message"]  # 35 - 30
        assert alerts[0]["action_required"] is True

    @pytest.mark.asyncio
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    async def test_check_alerts_red(self, mock_settings, mock_status):
        """Test alerts in RED zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=28.0,
            remaining_budget=2.0,
            percentage_used=93.3,
            alert_level=BudgetAlert.RED,
            days_remaining=5,
            projected_monthly_cost=35.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = await manager.check_budget_alerts()

        assert len(alerts) == 1
        assert alerts[0]["level"] == "warning"
        assert "Budget Almost Exhausted" in alerts[0]["title"]
        assert "93.3%" in alerts[0]["message"]
        assert alerts[0]["action_required"] is True

    @pytest.mark.asyncio
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    async def test_check_alerts_orange(self, mock_settings, mock_status):
        """Test alerts in ORANGE zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=24.0,
            remaining_budget=6.0,
            percentage_used=80.0,
            alert_level=BudgetAlert.ORANGE,
            days_remaining=10,
            projected_monthly_cost=32.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = await manager.check_budget_alerts()

        assert len(alerts) == 1
        assert alerts[0]["level"] == "info"
        assert "Budget Watch" in alerts[0]["title"]
        assert "80.0%" in alerts[0]["message"]
        assert alerts[0]["action_required"] is False

    @pytest.mark.asyncio
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    async def test_check_alerts_green(self, mock_settings, mock_status):
        """Test no alerts in GREEN zone"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.3,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=25.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = await manager.check_budget_alerts()

        assert len(alerts) == 0


# ============================================================================
# Test BudgetManager.check_budget_threshold_alerts
# ============================================================================


class TestCheckBudgetThresholdAlerts:
    """Test check_budget_threshold_alerts method for threshold ranges"""

    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_threshold_alerts_75_to_79_percent(self, mock_settings, mock_status):
        """Test INFO alert for 75-79% usage range"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=23.0,
            remaining_budget=7.0,
            percentage_used=76.7,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=10,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = manager.check_budget_threshold_alerts()

        assert len(alerts) == 1
        assert alerts[0].threshold_percentage == 75.0
        assert alerts[0].severity.value == "info"

    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_threshold_alerts_80_to_89_percent(self, mock_settings, mock_status):
        """Test WARNING alert for 80-89% usage range"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=25.0,
            remaining_budget=5.0,
            percentage_used=83.3,
            alert_level=BudgetAlert.ORANGE,
            days_remaining=8,
            projected_monthly_cost=32.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = manager.check_budget_threshold_alerts()

        assert len(alerts) == 1
        assert alerts[0].threshold_percentage == 80.0
        assert alerts[0].severity.value == "warning"

    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_threshold_alerts_90_to_99_percent(self, mock_settings, mock_status):
        """Test CRITICAL alert for 90-99% usage range"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=28.5,
            remaining_budget=1.5,
            percentage_used=95.0,
            alert_level=BudgetAlert.RED,
            days_remaining=3,
            projected_monthly_cost=35.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = manager.check_budget_threshold_alerts()

        assert len(alerts) == 1
        assert alerts[0].threshold_percentage == 90.0
        assert alerts[0].severity.value == "critical"

    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_threshold_alerts_100_percent_or_more(self, mock_settings, mock_status):
        """Test CRITICAL alert for 100%+ usage (over budget)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=33.0,
            remaining_budget=0.0,
            percentage_used=110.0,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=0,
            projected_monthly_cost=40.0,
            is_over_budget=True,
        )

        manager = BudgetManager()
        alerts = manager.check_budget_threshold_alerts()

        assert len(alerts) == 1
        assert alerts[0].threshold_percentage == 100.0
        assert alerts[0].severity.value == "critical"

    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_threshold_alerts_below_75_percent(self, mock_settings, mock_status):
        """Test no alerts for usage below 75%"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=20.0,
            remaining_budget=10.0,
            percentage_used=66.7,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=15,
            projected_monthly_cost=28.0,
            is_over_budget=False,
        )

        manager = BudgetManager()
        alerts = manager.check_budget_threshold_alerts()

        assert len(alerts) == 0


# ============================================================================
# Test BudgetManager.should_enforce_budget (with user_id)
# ============================================================================


class TestShouldEnforceBudgetWithUserId:
    """Test should_enforce_budget method with user_id parameter"""

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_should_enforce_with_user_id_enforce_true(self, mock_settings, mock_session):
        """Test should_enforce_budget returns True when user settings enforce_budget is True"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Create mock user budget settings with enforce_budget=True
        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.enforce_budget = True

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user_settings

        manager = BudgetManager()
        result = manager.should_enforce_budget(user_id="test_user_123")

        assert result is True
        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_should_enforce_with_user_id_enforce_false(self, mock_settings, mock_session):
        """Test should_enforce_budget returns False when user settings enforce_budget is False"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        mock_user_settings = MagicMock(spec=UserBudgetSettings)
        mock_user_settings.enforce_budget = False

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user_settings

        manager = BudgetManager()
        result = manager.should_enforce_budget(user_id="test_user_123")

        assert result is False
        mock_db.close.assert_called_once()

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_should_enforce_with_user_id_exception_fallback(self, mock_settings, mock_session):
        """Test should_enforce_budget falls back to preferences when database error occurs"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database connection error")

        manager = BudgetManager()
        # Should fallback to user_preferences (which is None, so returns True as default)
        result = manager.should_enforce_budget(user_id="test_user_123", user_preferences=None)

        assert result is True  # Default when preferences is None
        # Note: session.close() is not called when exception occurs before it

    @patch("app.services.budget_manager.get_primary_db_session")
    @patch("app.services.budget_manager.get_settings")
    def test_should_enforce_with_user_id_no_settings_found(self, mock_settings, mock_session):
        """Test should_enforce_budget falls back to preferences when user settings not found"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        mock_db = MagicMock()
        mock_session.return_value = mock_db

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # No user settings found

        # Provide user_preferences with enforce_budget_limits = False
        user_prefs = {
            "ai_provider_settings": {
                "enforce_budget_limits": False
            }
        }

        manager = BudgetManager()
        result = manager.should_enforce_budget(user_id="test_user_999", user_preferences=user_prefs)

        assert result is False  # Should use preferences fallback
        mock_db.close.assert_called_once()


# ============================================================================
# Test BudgetManager.can_override_budget
# ============================================================================


class TestCanOverrideBudget:
    """Test can_override_budget method"""

    @patch("app.services.budget_manager.get_settings")
    def test_can_override_budget_with_preferences_true(self, mock_settings):
        """Test can_override_budget returns True when preferences allow override"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        user_preferences = {
            "ai_provider_settings": {
                "budget_override_allowed": True
            }
        }

        manager = BudgetManager()
        result = manager.can_override_budget(user_preferences)

        assert result is True

    @patch("app.services.budget_manager.get_settings")
    def test_can_override_budget_with_preferences_false(self, mock_settings):
        """Test can_override_budget returns False when preferences disallow override"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        user_preferences = {
            "ai_provider_settings": {
                "budget_override_allowed": False
            }
        }

        manager = BudgetManager()
        result = manager.can_override_budget(user_preferences)

        assert result is False

    @patch("app.services.budget_manager.get_settings")
    def test_can_override_budget_no_preferences(self, mock_settings):
        """Test can_override_budget returns True (default) when no preferences provided"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        manager = BudgetManager()
        result = manager.can_override_budget(user_preferences=None)

        assert result is True  # Default: allow override


# ============================================================================
# Test BudgetManager.track_usage
# ============================================================================


class TestTrackUsage:
    """Test track_usage method"""

    @patch.object(BudgetManager, "record_api_usage")
    @patch("app.services.budget_manager.get_settings")
    def test_track_usage_success(self, mock_settings, mock_record):
        """Test successful usage tracking"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"
        mock_record.return_value = True

        manager = BudgetManager()
        result = manager.track_usage(
            provider="anthropic",
            model="claude-3-haiku",
            cost=0.05,
            tokens_used=1000,
            user_id="user123",
        )

        assert result is True
        mock_record.assert_called_once_with(
            user_id="user123",
            provider="anthropic",
            endpoint="claude-3-haiku",
            request_type="ai_generation",
            tokens_used=1000,
            estimated_cost=0.05,
            actual_cost=0.05,
            status="success",
        )

    @patch.object(BudgetManager, "record_api_usage")
    @patch("app.services.budget_manager.get_settings")
    def test_track_usage_without_user(self, mock_settings, mock_record):
        """Test usage tracking without user_id"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"
        mock_record.return_value = True

        manager = BudgetManager()
        result = manager.track_usage(
            provider="mistral",
            model="mistral-tiny",
            cost=0.03,
            tokens_used=500,
        )

        assert result is True
        mock_record.assert_called_once_with(
            user_id=None,
            provider="mistral",
            endpoint="mistral-tiny",
            request_type="ai_generation",
            tokens_used=500,
            estimated_cost=0.03,
            actual_cost=0.03,
            status="success",
        )

    @patch.object(BudgetManager, "record_api_usage")
    @patch("app.services.budget_manager.get_settings")
    def test_track_usage_exception(self, mock_settings, mock_record):
        """Test usage tracking with exception"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"
        mock_record.side_effect = Exception("Database error")

        manager = BudgetManager()
        result = manager.track_usage(
            provider="anthropic",
            model="claude-3-haiku",
            cost=0.05,
        )

        assert result is False


# ============================================================================
# Additional Tests for Missing Branch Coverage
# ============================================================================


class TestOptimizationRecommendationsEdgeCases:
    """Test edge cases for optimization recommendations"""

    @patch.object(BudgetManager, "get_cost_breakdown")
    @patch.object(BudgetManager, "get_current_budget_status")
    @patch("app.services.budget_manager.get_settings")
    def test_recommendations_no_provider_data(
        self, mock_settings, mock_status, mock_breakdown
    ):
        """Test recommendations when no provider data exists (empty provider_breakdown)"""
        mock_settings.return_value.MONTHLY_BUDGET_USD = "30.00"

        # Mock GREEN status
        mock_status.return_value = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.3,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=25.0,
            is_over_budget=False,
        )

        # Mock cost breakdown with EMPTY provider_breakdown
        mock_breakdown.return_value = {
            "provider_breakdown": []  # Empty list - no providers
        }

        manager = BudgetManager()
        recommendations = manager.get_optimization_recommendations()

        # Should not have provider optimization recommendation (no providers)
        provider_rec = next(
            (r for r in recommendations if r["type"] == "optimization"), None
        )
        assert provider_rec is None  # No provider recommendation when no data
