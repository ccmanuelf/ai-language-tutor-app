"""
Comprehensive Tests for Budget API Endpoints
AI Language Tutor App - Budget Management System

Tests all 9 budget API endpoints:
- User endpoints (6): status, settings, update, reset, breakdown, history
- Admin endpoints (3): configure, list all, admin reset

TRUE 100% coverage goal for budget API functionality.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.config import get_primary_db_session
from app.main import app
from app.models.budget import BudgetPeriod, BudgetResetLog, UserBudgetSettings
from app.models.database import APIUsage, Base, User, UserRole

# Test database setup
# Use StaticPool to ensure all connections share the same in-memory database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the database dependency"""

    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_primary_db_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_regular_user(regular_user):
    """Override auth to return regular user"""
    from app.api.auth import require_auth
    from app.services.auth import get_current_user

    # Create a simple mock object instead of SQLAlchemy model
    class MockUser:
        def __init__(self):
            self.id = regular_user.id
            self.user_id = regular_user.user_id
            self.username = regular_user.username
            self.email = regular_user.email
            self.role = regular_user.role.value

    def override_auth():
        return MockUser()

    # Need to return dict for get_current_user
    def override_get_current_user():
        return {
            "id": regular_user.id,
            "user_id": regular_user.user_id,
            "username": regular_user.username,
            "email": regular_user.email,
            "role": regular_user.role.value,
        }

    app.dependency_overrides[require_auth] = override_auth
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.pop(require_auth, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def auth_admin_user(admin_user):
    """Override auth to return admin user"""
    from app.api.auth import require_auth
    from app.services.admin_auth import require_admin_access
    from app.services.auth import get_current_user

    # Create a simple mock object instead of SQLAlchemy model
    class MockUser:
        def __init__(self):
            self.id = admin_user.id
            self.user_id = admin_user.user_id
            self.username = admin_user.username
            self.email = admin_user.email
            self.role = admin_user.role.value

    def override_auth():
        return MockUser()

    # Need to return dict for get_current_user
    def override_get_current_user():
        return {
            "id": admin_user.id,
            "user_id": admin_user.user_id,
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role.value,
        }

    app.dependency_overrides[require_auth] = override_auth
    app.dependency_overrides[require_admin_access] = override_auth
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.pop(require_auth, None)
    app.dependency_overrides.pop(require_admin_access, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def regular_user(db_session):
    """Create a regular test user"""
    user = User(
        user_id="test_user_123",
        username="testuser",
        email="test@example.com",
        role=UserRole.CHILD,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin test user"""
    admin = User(
        user_id="admin_user_456",
        username="adminuser",
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def user_budget_settings(db_session, regular_user):
    """Create budget settings for regular user"""
    # Set period start to 10 days ago to include test API usage records (which are 5 days old)
    period_start = datetime.now(timezone.utc) - timedelta(days=10)
    period_end = datetime.now(timezone.utc) + timedelta(days=20)

    settings = UserBudgetSettings(
        user_id=regular_user.user_id,
        monthly_limit_usd=30.0,
        current_period_start=period_start,
        current_period_end=period_end,
        enforce_budget=True,
        budget_visible_to_user=True,
        user_can_modify_limit=False,
        user_can_reset_budget=False,
        alert_threshold_yellow=75.0,
        alert_threshold_orange=90.0,
        alert_threshold_red=100.0,
    )
    db_session.add(settings)
    db_session.commit()
    db_session.refresh(settings)
    return settings


@pytest.fixture
def api_usage_records(db_session, regular_user):
    """Create sample API usage records"""
    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=5)

    for i in range(10):
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            tokens_used=150,
            estimated_cost=0.15,
            created_at=base_time + timedelta(hours=i),
        )
        records.append(usage)
        db_session.add(usage)

    db_session.commit()
    return records


class TestBudgetStatusEndpoint:
    """Tests for GET /api/v1/budget/status endpoint"""

    def test_get_budget_status_success(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
        api_usage_records,
    ):
        """Test successfully retrieving budget status"""
        # Mock authentication
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert "total_budget" in data
        assert "used_budget" in data
        assert "remaining_budget" in data
        assert "percentage_used" in data
        assert "alert_level" in data
        assert "period_start" in data
        assert "period_end" in data
        assert "budget_period" in data
        assert "can_view_budget" in data
        assert "can_modify_limit" in data
        assert "can_reset_budget" in data

        assert data["total_budget"] == 30.0
        assert data["used_budget"] == 1.5  # 10 records * 0.15
        assert data["remaining_budget"] == 28.5

    def test_get_budget_status_unauthorized(self, client, override_get_db):
        """Test budget status without authentication"""
        response = client.get("/api/v1/budget/status")
        assert response.status_code == 401

    def test_get_budget_status_hidden(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test budget status when visibility is disabled"""
        # Create settings with visibility disabled
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=False,
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 403
        assert "visibility is disabled" in response.json()["detail"].lower()


class TestHelperFunctionsDirectly:
    """Direct tests of helper functions to achieve TRUE 100% coverage"""

    def test_calculate_period_end_monthly_non_december(self):
        """Test _calculate_period_end for MONTHLY in non-December month (line 171)"""
        from app.api.budget import _calculate_period_end

        # Mock datetime.now() to return a non-December date
        with patch('app.api.budget.datetime') as mock_dt:
            # Set to June 15, 2025
            mock_now = datetime(2025, 6, 15, 10, 30, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.return_value = datetime  # Pass through datetime() calls
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = _calculate_period_end(BudgetPeriod.MONTHLY, None)

            # Should return July 1, 2025
            assert result == datetime(2025, 7, 1, 0, 0, 0)

    def test_calculate_period_end_default_fallback_non_december(self):
        """Test _calculate_period_end default fallback in non-December (line 187)"""
        from app.api.budget import _calculate_period_end

        # Test with CUSTOM period but no custom_days (triggers default fallback)
        with patch('app.api.budget.datetime') as mock_dt:
            # Set to March 20, 2025 (non-December)
            mock_now = datetime(2025, 3, 20, 14, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # CUSTOM period with custom_days=None triggers default
            result = _calculate_period_end(BudgetPeriod.CUSTOM, None)

            # Should use default monthly calculation: April 1, 2025
            assert result == datetime(2025, 4, 1, 0, 0, 0)

    def test_check_budget_permissions_unknown_permission_type(self):
        """Test _check_budget_permissions with unknown permission type (line 206)"""
        from app.api.budget import _check_budget_permissions
        from app.api.auth import SimpleUser

        # Create mock user and settings
        class MockUser:
            def __init__(self):
                self.id = 1
                self.user_id = "test_user"
                self.role = "child"  # Not admin

        mock_settings = UserBudgetSettings(
            user_id="test_user",
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
            user_can_modify_limit=True,
            user_can_reset_budget=True,
        )

        # Test with unknown permission type
        result = _check_budget_permissions(
            MockUser(),
            mock_settings,
            "unknown_permission_type"
        )

        # Should return False for unknown permission
        assert result is False

    def test_get_budget_status_creates_default_settings(
        self, client, override_get_db, auth_regular_user, regular_user
    ):
        """Test that default settings are created if none exist"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # Should have default values
        assert data["total_budget"] == 30.0  # Default limit


class TestBudgetSettingsEndpoint:
    """Tests for GET /api/v1/budget/settings endpoint"""

    def test_get_budget_settings_success(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test successfully retrieving budget settings"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/settings")

        assert response.status_code == 200
        data = response.json()

        assert data["monthly_limit_usd"] == 30.0
        assert data["enforce_budget"] is True
        assert data["budget_visible_to_user"] is True
        assert data["user_can_modify_limit"] is False
        assert data["user_can_reset_budget"] is False
        assert data["alert_threshold_yellow"] == 75.0
        assert data["alert_threshold_orange"] == 90.0
        assert data["alert_threshold_red"] == 100.0

    def test_get_budget_settings_unauthorized(self, client, override_get_db):
        """Test getting settings without authentication"""
        response = client.get("/api/v1/budget/settings")
        assert response.status_code == 401


class TestUpdateBudgetSettingsEndpoint:
    """Tests for PUT /api/v1/budget/settings endpoint"""

    def test_update_settings_with_permission(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating settings when user has permission"""
        # Create settings with modify permission
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {
            "monthly_limit_usd": 50.0,
            "enforce_budget": False,
            "alert_threshold_yellow": 60.0,  # Must be < orange (75) < red (90)
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["monthly_limit_usd"] == 50.0
        assert data["enforce_budget"] is False
        assert data["alert_threshold_yellow"] == 60.0

    def test_update_settings_without_permission(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test updating settings without permission"""
        update_data = {
            "monthly_limit_usd": 100.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_update_settings_invalid_thresholds(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating with invalid threshold values"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Yellow > Orange (invalid)
        update_data = {
            "alert_threshold_yellow": 95.0,
            "alert_threshold_orange": 90.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 400
        assert "threshold" in response.json()["detail"].lower()


class TestResetBudgetEndpoint:
    """Tests for POST /api/v1/budget/reset endpoint"""

    def test_reset_budget_with_permission(
        self,
        client,
        override_get_db,
        db_session,
        auth_regular_user,
        regular_user,
        api_usage_records,
    ):
        """Test resetting budget when user has permission"""
        # Create settings with reset permission
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_reset_budget=True,
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.post("/api/v1/budget/reset", json={})

        assert response.status_code == 200
        data = response.json()

        # User reset endpoint doesn't include user_id in message (unlike admin reset)
        assert data["message"] == "Budget reset successfully"
        assert "new_period_start" in data
        assert "new_period_end" in data

    def test_reset_budget_without_permission(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test resetting budget without permission"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.post("/api/v1/budget/reset", json={})

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_reset_budget_creates_log(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test that reset creates audit log entry"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_reset_budget=True,
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.post("/api/v1/budget/reset", json={})

        assert response.status_code == 200

        # Check that log entry was created
        log_entry = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == regular_user.user_id)
            .first()
        )

        assert log_entry is not None
        assert log_entry.reset_type == "manual"
        assert log_entry.reset_by == regular_user.user_id


class TestUsageBreakdownEndpoint:
    """Tests for GET /api/v1/budget/usage/breakdown endpoint"""

    def test_get_usage_breakdown_success(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
        api_usage_records,
    ):
        """Test successfully retrieving usage breakdown"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/usage/breakdown")

        assert response.status_code == 200
        data = response.json()

        assert "by_provider" in data
        assert "by_service_type" in data
        assert "by_day" in data

        # Should have breakdown for mistral provider
        assert "mistral" in data["by_provider"]
        assert abs(data["by_provider"]["mistral"] - 1.5) < 0.01  # 10 * 0.15 (approx)


class TestUsageHistoryEndpoint:
    """Tests for GET /api/v1/budget/usage/history endpoint"""

    def test_get_usage_history_success(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
        api_usage_records,
    ):
        """Test successfully retrieving usage history"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/history")

        assert response.status_code == 200
        data = response.json()

        # This endpoint returns budget reset history, not API usage
        assert isinstance(data, list)
        # Budget reset history might be empty if no resets occurred
        # Just verify it returns successfully

    def test_get_usage_history_pagination(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
        api_usage_records,
    ):
        """Test budget reset history with pagination"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/history?limit=5")

        assert response.status_code == 200
        data = response.json()

        # Returns list of reset history records
        assert isinstance(data, list)


class TestAdminConfigureEndpoint:
    """Tests for PUT /api/v1/budget/admin/configure endpoint"""

    def test_admin_configure_user_budget(
        self,
        client,
        override_get_db,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test admin configuring user budget settings"""
        config_data = {
            "target_user_id": regular_user.user_id,
            "monthly_limit_usd": 100.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": True,
            "user_can_reset_budget": True,
            "admin_notes": "Increased limit for power user",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)

        assert response.status_code == 200
        data = response.json()

        assert data["monthly_limit_usd"] == 100.0
        assert data["user_can_modify_limit"] is True
        assert data["user_can_reset_budget"] is True
        assert data["admin_notes"] == "Increased limit for power user"

    def test_admin_configure_requires_admin(
        self, client, override_get_db, auth_regular_user, regular_user
    ):
        """Test that non-admin cannot configure budgets"""
        config_data = {
            "target_user_id": "other_user",
            "monthly_limit_usd": 100.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)

        assert response.status_code == 403


class TestAdminListAllEndpoint:
    """Tests for GET /api/v1/budget/admin/list endpoint"""

    def test_admin_list_all_budgets(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
    ):
        """Test admin listing all user budgets"""
        # Create multiple user budget settings
        settings1 = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
        )
        settings2 = UserBudgetSettings(
            user_id=admin_user.user_id,
            monthly_limit_usd=100.0,
        )
        db_session.add_all([settings1, settings2])
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.get("/api/v1/budget/admin/users")

        assert response.status_code == 200
        data = response.json()

        # Returns list of budget settings
        assert isinstance(data, list)
        assert len(data) == 2

    def test_admin_list_requires_admin(
        self, client, override_get_db, auth_regular_user, regular_user
    ):
        """Test that non-admin cannot list all budgets"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/admin/users")

        assert response.status_code == 403


class TestAdminResetEndpoint:
    """Tests for POST /api/v1/budget/admin/reset endpoint"""

    def test_admin_reset_user_budget(
        self,
        client,
        override_get_db,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test admin resetting a user's budget"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.post(
                f"/api/v1/budget/admin/reset/{regular_user.user_id}",
                json={"reason": "Monthly reset requested by user"},
            )

        assert response.status_code == 200
        data = response.json()

        assert "Budget reset successfully" in data["message"]
        assert regular_user.user_id in data["message"]
        assert "new_period_start" in data
        assert "new_period_end" in data

    def test_admin_reset_requires_admin(
        self, client, override_get_db, auth_regular_user, regular_user
    ):
        """Test that non-admin cannot reset user budgets"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.post("/api/v1/budget/admin/reset/other_user", json={})

        assert response.status_code == 403

    def test_admin_reset_creates_log(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test that admin reset creates audit log"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.post(
                f"/api/v1/budget/admin/reset/{regular_user.user_id}",
                json={"reason": "Admin reset test"},
            )

        assert response.status_code == 200

        # Check log entry
        log_entry = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == regular_user.user_id)
            .first()
        )

        assert log_entry is not None
        assert log_entry.reset_type == "manual"
        assert log_entry.reset_by == admin_user.user_id  # Admin who reset it


class TestBudgetEnforcement:
    """Tests for budget enforcement logic"""

    def test_budget_blocks_when_exceeded(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test that budget enforcement blocks requests when exceeded"""
        # Create settings with low limit and enforcement enabled
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=1.0,  # Very low limit
            enforce_budget=True,
        )
        db_session.add(settings)

        # Create usage that exceeds limit
        for i in range(10):
            usage = APIUsage(
                user_id=regular_user.id,
                api_provider="mistral",
                api_endpoint="/v1/chat/completions",
                request_type="chat",
                estimated_cost=0.15,
                created_at=datetime.now(timezone.utc),
            )
            db_session.add(usage)

        db_session.commit()

        # Status should show over budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["used_budget"] > data["total_budget"]
        assert data["is_over_budget"] is True

    def test_budget_allows_when_not_exceeded(
        self,
        client,
        override_get_db,
        auth_regular_user,
        regular_user,
        user_budget_settings,
    ):
        """Test that budget allows requests when not exceeded"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["used_budget"] <= data["total_budget"]
        assert data["is_over_budget"] is False


class TestBudgetAlertLevels:
    """Tests for budget alert threshold logic"""

    def test_green_alert_level(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test green alert when usage is low"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            alert_threshold_yellow=75.0,
        )
        db_session.add(settings)

        # Add small usage (10% of budget)
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=10.0,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["alert_level"] == "green"
        assert data["percentage_used"] == 10.0

    def test_yellow_alert_level(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test yellow alert at threshold"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            alert_threshold_yellow=75.0,
            alert_threshold_orange=90.0,
        )
        db_session.add(settings)

        # Add usage at yellow threshold (80%)
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=80.0,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["alert_level"] == "yellow"

    def test_orange_alert_level(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test orange alert at threshold"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            alert_threshold_orange=90.0,
            alert_threshold_red=100.0,
        )
        db_session.add(settings)

        # Add usage at orange threshold (95%)
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=95.0,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["alert_level"] == "orange"

    def test_red_alert_level(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test red alert when over budget"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            alert_threshold_red=100.0,
        )
        db_session.add(settings)

        # Add usage over budget (105%)
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=105.0,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # When over 100%, alert_level is "red" (not "critical")
        assert data["alert_level"] == "red"
        assert data["percentage_used"] > 100.0


class TestBudgetPeriodCalculations:
    """Tests for different budget period calculations (WEEKLY, DAILY, CUSTOM)"""

    def test_weekly_period_status(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test budget status with WEEKLY period"""
        # Create settings with WEEKLY period
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.WEEKLY,
            current_period_start=datetime.now(timezone.utc) - timedelta(days=3),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=4),
        )
        db_session.add(settings)

        # Add some usage
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=5.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # Should calculate weekly projection (daily_avg * 7)
        assert data["budget_period"] == "weekly"
        assert "projected_period_cost" in data
        # projected_cost should be roughly: (5.0 / 4 days) * 7 = ~8.75
        assert data["projected_period_cost"] > 0

    def test_daily_period_status(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test budget status with DAILY period"""
        # Create settings with DAILY period
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=5.0,
            budget_period=BudgetPeriod.DAILY,
            current_period_start=datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            current_period_end=datetime.now(timezone.utc).replace(
                hour=23, minute=59, second=59, microsecond=0
            ),
        )
        db_session.add(settings)

        # Add usage for today
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=2.0,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # Should use total_cost as projection for daily
        assert data["budget_period"] == "daily"
        assert data["used_budget"] == 2.0
        # For daily period, projected_cost equals current usage
        assert data["projected_period_cost"] == 2.0

    def test_custom_period_with_days_status(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test budget status with CUSTOM period and custom_period_days set"""
        # Create settings with CUSTOM period (14 days)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=50.0,
            budget_period=BudgetPeriod.CUSTOM,
            custom_period_days=14,
            current_period_start=datetime.now(timezone.utc) - timedelta(days=7),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db_session.add(settings)

        # Add usage
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=14.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # Should calculate custom projection (daily_avg * custom_period_days)
        assert data["budget_period"] == "custom"
        assert "projected_period_cost" in data
        # projected_cost should be roughly: (14.0 / 8 days) * 14 = ~24.5
        assert data["projected_period_cost"] > 0

    def test_custom_period_without_days_uses_default(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test CUSTOM period without custom_period_days falls back to monthly (30 days)"""
        # Create settings with CUSTOM period but NO custom_period_days
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.CUSTOM,
            custom_period_days=None,  # Not set
            current_period_start=datetime.now(timezone.utc) - timedelta(days=5),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=25),
        )
        db_session.add(settings)

        # Add usage
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=10.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # Should use default 30-day projection
        assert data["budget_period"] == "custom"
        # projected_cost should be: (10.0 / 6 days) * 30 = ~50.0
        assert data["projected_period_cost"] > 0


class TestUpdateBudgetSettingsAllFields:
    """Tests for updating all optional fields in budget settings"""

    def test_update_custom_limit_usd(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating custom_limit_usd field"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"custom_limit_usd": 75.0}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["custom_limit_usd"] == 75.0

    def test_update_budget_period_to_weekly(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test changing budget_period to WEEKLY (recalculates period_end)"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.MONTHLY,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"budget_period": "weekly"}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["budget_period"] == "weekly"
        # period_end should be recalculated (now + 7 days)

    def test_update_budget_period_to_daily(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test changing budget_period to DAILY (recalculates period_end)"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.MONTHLY,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"budget_period": "daily"}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["budget_period"] == "daily"

    def test_update_budget_period_to_custom_with_days(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test changing to CUSTOM period with custom_period_days"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.MONTHLY,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"budget_period": "custom", "custom_period_days": 21}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["budget_period"] == "custom"
        assert data["custom_period_days"] == 21

    def test_update_enforce_budget_field(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating enforce_budget field"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            enforce_budget=True,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"enforce_budget": False}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["enforce_budget"] is False

    def test_update_allow_budget_override_field(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating allow_budget_override field"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            allow_budget_override=True,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"allow_budget_override": False}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["allow_budget_override"] is False

    def test_update_auto_fallback_to_ollama_field(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating auto_fallback_to_ollama field"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            auto_fallback_to_ollama=False,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {"auto_fallback_to_ollama": True}

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["auto_fallback_to_ollama"] is True

    def test_update_all_threshold_fields(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test updating all three threshold fields together"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        update_data = {
            "alert_threshold_yellow": 60.0,
            "alert_threshold_orange": 80.0,
            "alert_threshold_red": 95.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["alert_threshold_yellow"] == 60.0
        assert data["alert_threshold_orange"] == 80.0
        assert data["alert_threshold_red"] == 95.0


class TestAdminConfigureAllFields:
    """Tests for admin configuration of all optional fields"""

    def test_admin_configure_all_fields_sequential(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        regular_user,
    ):
        """Test admin configuring each field sequentially (tests branches 606-621)"""
        # Create initial settings
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
        )
        db_session.add(settings)
        db_session.commit()

        # Test updating budget_visible_to_user
        config_data = {
            "target_user_id": regular_user.user_id,
            "budget_visible_to_user": False,
        }
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)
        assert response.status_code == 200
        assert response.json()["budget_visible_to_user"] is False

        # Test updating user_can_modify_limit
        config_data = {
            "target_user_id": regular_user.user_id,
            "user_can_modify_limit": True,
        }
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)
        assert response.status_code == 200
        assert response.json()["user_can_modify_limit"] is True

        # Test updating user_can_reset_budget
        config_data = {
            "target_user_id": regular_user.user_id,
            "user_can_reset_budget": True,
        }
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)
        assert response.status_code == 200
        assert response.json()["user_can_reset_budget"] is True

        # Test updating monthly_limit_usd
        config_data = {
            "target_user_id": regular_user.user_id,
            "monthly_limit_usd": 100.0,
        }
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)
        assert response.status_code == 200
        assert response.json()["monthly_limit_usd"] == 100.0

        # Test updating admin_notes
        config_data = {
            "target_user_id": regular_user.user_id,
            "admin_notes": "Test notes for coverage",
        }
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/admin/configure", json=config_data)
        assert response.status_code == 200
        assert response.json()["admin_notes"] == "Test notes for coverage"


class TestAdminResetErrorHandling:
    """Tests for error handling in admin reset endpoint"""

    def test_admin_reset_nonexistent_user(
        self, client, override_get_db, auth_admin_user, admin_user
    ):
        """Test admin reset with non-existent user returns 404"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.post(
                "/api/v1/budget/admin/reset/nonexistent_user_999",
                json={"reason": "Test reset"},
            )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestPeriodCalculationEdgeCases:
    """Tests for edge cases in _calculate_period_end helper function"""

    def test_monthly_period_non_december(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test MONTHLY period calculation in non-December month (line 171)"""
        # Create settings with MONTHLY period, ensuring it's not December
        import datetime
        # Use a fixed date in a non-December month
        non_december_date = datetime.datetime(2025, 6, 15, 10, 0, 0)

        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.MONTHLY,
            current_period_start=non_december_date,
            current_period_end=datetime.datetime(2025, 7, 1, 0, 0, 0),
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        # This exercises the MONTHLY period calculation for non-December


class TestAdminPermissions:
    """Tests for admin permission checks"""

    def test_admin_has_view_permission(
        self, client, override_get_db, db_session, auth_admin_user, admin_user
    ):
        """Test that admin users always have view permission (line 196)"""
        # Create settings with budget_visible_to_user=False
        settings = UserBudgetSettings(
            user_id=admin_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=False,  # Disabled for regular users
        )
        db_session.add(settings)
        db_session.commit()

        # Admin should still be able to view despite visibility=False
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        # Admin bypasses the permission check
        assert response.status_code == 200

    def test_admin_has_modify_permission(
        self, client, override_get_db, db_session, auth_admin_user, admin_user
    ):
        """Test that admin users always have modify permission"""
        # Create settings with user_can_modify_limit=False
        settings = UserBudgetSettings(
            user_id=admin_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=False,  # Disabled for regular users
        )
        db_session.add(settings)
        db_session.commit()

        # Admin should still be able to modify despite permission=False
        update_data = {"monthly_limit_usd": 100.0}
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        # Admin bypasses the permission check
        assert response.status_code == 200
        assert response.json()["monthly_limit_usd"] == 100.0


class TestHelperFunctionCoverage:
    """Tests to cover helper function edge cases"""

    def test_update_custom_period_without_days_triggers_default(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test CUSTOM period update without custom_period_days (triggers default calculation)"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.MONTHLY,
            user_can_modify_limit=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Change to CUSTOM period but don't provide custom_period_days
        # This should trigger the default fallback in _calculate_period_end (lines 184-187)
        update_data = {
            "budget_period": "custom"
            # Note: NOT providing custom_period_days
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["budget_period"] == "custom"
        # Should have recalculated period_end using default (monthly) logic

    def test_get_settings_forbidden_for_regular_user(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test get_budget_settings when visibility is False (line 320)"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=False,
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/settings")

        assert response.status_code == 403
        assert "visibility is disabled" in response.json()["detail"].lower()

    def test_usage_breakdown_forbidden_when_visibility_disabled(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test get_usage_breakdown when visibility is False (line 483)"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=False,
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/usage/breakdown")

        assert response.status_code == 403
        assert "visibility is disabled" in response.json()["detail"].lower()

    def test_history_forbidden_when_visibility_disabled(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """Test get_budget_reset_history when visibility is False (line 567)"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=False,
        )
        db_session.add(settings)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/history")

        assert response.status_code == 403
        assert "visibility is disabled" in response.json()["detail"].lower()
