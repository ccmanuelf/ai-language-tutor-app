"""
Comprehensive Tests for Budget API Endpoints
AI Language Tutor App - Budget Management System

Tests all 9 budget API endpoints:
- User endpoints (6): status, settings, update, reset, breakdown, history
- Admin endpoints (3): configure, list all, admin reset

TRUE 100% coverage goal for budget API functionality.
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.config import get_primary_db_session
from app.main import app
from app.models.budget import BudgetPeriod, BudgetResetLog, UserBudgetSettings
from app.models.database import APIUsage, Base, User, UserRole

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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
def regular_user(db_session):
    """Create a regular test user"""
    user = User(
        user_id="test_user_123",
        username="testuser",
        email="test@example.com",
        role=UserRole.USER,
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
    settings = UserBudgetSettings(
        user_id=regular_user.user_id,
        monthly_limit_usd=30.0,
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
    base_time = datetime.utcnow() - timedelta(days=5)

    for i in range(10):
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            model_name="mistral-small",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
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

        assert "monthly_limit" in data
        assert "current_spent" in data
        assert "remaining" in data
        assert "percentage_used" in data
        assert "alert_level" in data
        assert "period_start" in data
        assert "period_end" in data

        assert data["monthly_limit"] == 30.0
        assert data["current_spent"] == 1.5  # 10 records * 0.15
        assert data["remaining"] == 28.5

    def test_get_budget_status_unauthorized(self, client, override_get_db):
        """Test budget status without authentication"""
        response = client.get("/api/v1/budget/status")
        assert response.status_code == 401

    def test_get_budget_status_hidden(
        self, client, override_get_db, db_session, regular_user
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

    def test_get_budget_status_creates_default_settings(
        self, client, override_get_db, regular_user
    ):
        """Test that default settings are created if none exist"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        # Should have default values
        assert data["monthly_limit"] == 30.0  # Default limit


class TestBudgetSettingsEndpoint:
    """Tests for GET /api/v1/budget/settings endpoint"""

    def test_get_budget_settings_success(
        self, client, override_get_db, regular_user, user_budget_settings
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
        self, client, override_get_db, db_session, regular_user
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
            "alert_threshold_yellow": 80.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.put("/api/v1/budget/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["monthly_limit_usd"] == 50.0
        assert data["enforce_budget"] is False
        assert data["alert_threshold_yellow"] == 80.0

    def test_update_settings_without_permission(
        self, client, override_get_db, regular_user, user_budget_settings
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
        self, client, override_get_db, db_session, regular_user
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
        self, client, override_get_db, db_session, regular_user, api_usage_records
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
            response = c.post("/api/v1/budget/reset")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Budget reset successfully"
        assert "new_period_start" in data
        assert "new_period_end" in data

    def test_reset_budget_without_permission(
        self, client, override_get_db, regular_user, user_budget_settings
    ):
        """Test resetting budget without permission"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.post("/api/v1/budget/reset")

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_reset_budget_creates_log(
        self, client, override_get_db, db_session, regular_user
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
            response = c.post("/api/v1/budget/reset")

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
        assert "by_model" in data
        assert "by_day" in data

        # Should have breakdown for mistral provider
        assert "mistral" in data["by_provider"]
        assert data["by_provider"]["mistral"] == 1.5  # 10 * 0.15


class TestUsageHistoryEndpoint:
    """Tests for GET /api/v1/budget/usage/history endpoint"""

    def test_get_usage_history_success(
        self,
        client,
        override_get_db,
        regular_user,
        user_budget_settings,
        api_usage_records,
    ):
        """Test successfully retrieving usage history"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/usage/history")

        assert response.status_code == 200
        data = response.json()

        assert "usage_records" in data
        assert len(data["usage_records"]) == 10

        # Verify record structure
        record = data["usage_records"][0]
        assert "timestamp" in record
        assert "provider" in record
        assert "model" in record
        assert "cost" in record
        assert "tokens" in record

    def test_get_usage_history_pagination(
        self,
        client,
        override_get_db,
        regular_user,
        user_budget_settings,
        api_usage_records,
    ):
        """Test usage history with pagination"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/usage/history?limit=5&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data["usage_records"]) == 5


class TestAdminConfigureEndpoint:
    """Tests for PUT /api/v1/budget/admin/configure endpoint"""

    def test_admin_configure_user_budget(
        self, client, override_get_db, admin_user, regular_user, user_budget_settings
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
        self, client, override_get_db, regular_user
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
        self, client, override_get_db, db_session, admin_user, regular_user
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
            response = c.get("/api/v1/budget/admin/list")

        assert response.status_code == 200
        data = response.json()

        assert "budgets" in data
        assert len(data["budgets"]) == 2

    def test_admin_list_requires_admin(self, client, override_get_db, regular_user):
        """Test that non-admin cannot list all budgets"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/admin/list")

        assert response.status_code == 403


class TestAdminResetEndpoint:
    """Tests for POST /api/v1/budget/admin/reset endpoint"""

    def test_admin_reset_user_budget(
        self, client, override_get_db, admin_user, regular_user, user_budget_settings
    ):
        """Test admin resetting a user's budget"""
        reset_data = {
            "target_user_id": regular_user.user_id,
            "reason": "Monthly reset requested by user",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.post("/api/v1/budget/admin/reset", json=reset_data)

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Budget reset successfully"
        assert "new_period_start" in data
        assert "new_period_end" in data

    def test_admin_reset_requires_admin(self, client, override_get_db, regular_user):
        """Test that non-admin cannot reset user budgets"""
        reset_data = {
            "target_user_id": "other_user",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.post("/api/v1/budget/admin/reset", json=reset_data)

        assert response.status_code == 403

    def test_admin_reset_creates_log(
        self,
        client,
        override_get_db,
        db_session,
        admin_user,
        regular_user,
        user_budget_settings,
    ):
        """Test that admin reset creates audit log"""
        reset_data = {
            "target_user_id": regular_user.user_id,
            "reason": "Admin reset test",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            response = c.post("/api/v1/budget/admin/reset", json=reset_data)

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
        self, client, override_get_db, db_session, regular_user
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
                user_id=regular_user.user_id,
                provider="mistral",
                model_name="mistral-small",
                estimated_cost=0.15,
                created_at=datetime.utcnow(),
            )
            db_session.add(usage)

        db_session.commit()

        # Status should show over budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["current_spent"] > data["monthly_limit"]
        assert data["alert_level"] == "red"

    def test_budget_allows_when_not_exceeded(
        self, client, override_get_db, regular_user, user_budget_settings
    ):
        """Test that budget allows requests when not exceeded"""
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["current_spent"] <= data["monthly_limit"]


class TestBudgetAlertLevels:
    """Tests for budget alert threshold logic"""

    def test_green_alert_level(self, client, override_get_db, db_session, regular_user):
        """Test green alert when usage is low"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            alert_threshold_yellow=75.0,
        )
        db_session.add(settings)

        # Add small usage (10% of budget)
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=10.0,
            created_at=datetime.utcnow(),
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
        self, client, override_get_db, db_session, regular_user
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
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=80.0,
            created_at=datetime.utcnow(),
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
        self, client, override_get_db, db_session, regular_user
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
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=95.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["alert_level"] == "orange"

    def test_red_alert_level(self, client, override_get_db, db_session, regular_user):
        """Test red alert when over budget"""
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            alert_threshold_red=100.0,
        )
        db_session.add(settings)

        # Add usage over budget (105%)
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=105.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.status_code == 200
        data = response.json()

        assert data["alert_level"] == "red"
        assert data["percentage_used"] > 100.0
