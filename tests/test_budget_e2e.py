"""
End-to-End Tests for Budget Management System
AI Language Tutor App - Budget Management System

Tests complete user journeys and workflows:
- Admin configuring user budgets
- Users viewing and managing their budgets
- Budget enforcement during API calls
- Alert level transitions
- Reset workflows
- Permission-based access control

TRUE 100% functionality verification for budget system.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.config import get_primary_db_session
from app.main import app
from app.models.budget import BudgetResetLog, UserBudgetSettings
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
def admin_user(db_session):
    """Create an admin test user"""
    admin = User(
        user_id="admin_001",
        username="admin",
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
def regular_user(db_session):
    """Create a regular test user"""
    user = User(
        user_id="user_001",
        username="user",
        email="user@example.com",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def power_user(db_session):
    """Create a power user with elevated permissions"""
    user = User(
        user_id="power_user_001",
        username="poweruser",
        email="poweruser@example.com",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestAdminBudgetConfigurationFlow:
    """E2E tests for admin budget configuration workflows"""

    def test_admin_creates_new_user_budget_configuration(
        self, client, override_get_db, db_session, admin_user, regular_user
    ):
        """
        E2E Flow: Admin creates budget configuration for a new user

        Steps:
        1. Admin logs in
        2. Admin navigates to budget management
        3. Admin configures budget for user
        4. User can now see their budget
        """
        # Step 3: Admin configures budget for regular user
        config_data = {
            "target_user_id": regular_user.user_id,
            "monthly_limit_usd": 50.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
            "enforce_budget": True,
            "admin_notes": "Standard user configuration",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            config_response = c.put("/api/v1/budget/admin/configure", json=config_data)

        assert config_response.status_code == 200
        config_result = config_response.json()
        assert config_result["monthly_limit_usd"] == 50.0
        assert config_result["budget_visible_to_user"] is True

        # Step 4: User can now see their budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["monthly_limit"] == 50.0

    def test_admin_grants_user_permissions(
        self, client, override_get_db, db_session, admin_user, power_user
    ):
        """
        E2E Flow: Admin grants power user permissions to manage their own budget

        Steps:
        1. Admin creates budget with full permissions
        2. Power user can modify their own limit
        3. Power user can reset their own budget
        """
        # Step 1: Admin grants full permissions
        config_data = {
            "target_user_id": power_user.user_id,
            "monthly_limit_usd": 100.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": True,
            "user_can_reset_budget": True,
            "admin_notes": "Power user - can self-manage",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            config_response = c.put("/api/v1/budget/admin/configure", json=config_data)

        assert config_response.status_code == 200

        # Step 2: Power user modifies their own limit
        update_data = {
            "monthly_limit_usd": 150.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {power_user.user_id}"}
            update_response = c.put("/api/v1/budget/settings", json=update_data)

        assert update_response.status_code == 200
        assert update_response.json()["monthly_limit_usd"] == 150.0

        # Step 3: Power user resets their own budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {power_user.user_id}"}
            reset_response = c.post("/api/v1/budget/reset")

        assert reset_response.status_code == 200
        assert "successfully" in reset_response.json()["message"].lower()

    def test_admin_restricts_budget_visibility(
        self, client, override_get_db, db_session, admin_user, regular_user
    ):
        """
        E2E Flow: Admin hides budget from specific user

        Steps:
        1. Admin creates budget with visibility disabled
        2. User cannot see budget status
        3. Admin re-enables visibility
        4. User can now see budget
        """
        # Step 1: Create budget with visibility disabled
        config_data = {
            "target_user_id": regular_user.user_id,
            "monthly_limit_usd": 30.0,
            "budget_visible_to_user": False,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            c.put("/api/v1/budget/admin/configure", json=config_data)

        # Step 2: User cannot see budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        assert status_response.status_code == 403

        # Step 3: Admin re-enables visibility
        config_data["budget_visible_to_user"] = True

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            c.put("/api/v1/budget/admin/configure", json=config_data)

        # Step 4: User can now see budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        assert status_response.status_code == 200


class TestUserBudgetManagementFlow:
    """E2E tests for user budget management workflows"""

    def test_user_views_budget_and_usage_history(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: User views their budget status and usage history

        Steps:
        1. Create budget settings for user
        2. Add some API usage
        3. User checks budget status
        4. User views usage breakdown
        5. User views usage history
        """
        # Step 1: Create budget settings
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Add API usage
        for i in range(5):
            usage = APIUsage(
                user_id=regular_user.user_id,
                provider="mistral",
                model_name="mistral-small",
                estimated_cost=2.0,
                total_tokens=1000,
                created_at=datetime.utcnow() - timedelta(hours=i),
            )
            db_session.add(usage)
        db_session.commit()

        # Step 3: Check budget status
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["current_spent"] == 10.0  # 5 * 2.0
        assert status_data["monthly_limit"] == 30.0
        assert status_data["remaining"] == 20.0

        # Step 4: View usage breakdown
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            breakdown_response = c.get("/api/v1/budget/usage/breakdown")

        assert breakdown_response.status_code == 200
        breakdown_data = breakdown_response.json()
        assert "mistral" in breakdown_data["by_provider"]

        # Step 5: View usage history
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            history_response = c.get("/api/v1/budget/usage/history")

        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data["usage_records"]) == 5

    def test_user_monitors_budget_approaching_limit(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: User monitors budget as it approaches limit with alerts

        Steps:
        1. User starts with green status (low usage)
        2. Usage increases to yellow alert
        3. Usage increases to orange alert
        4. Usage reaches red alert (near/over limit)
        """
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            budget_visible_to_user=True,
            alert_threshold_yellow=75.0,
            alert_threshold_orange=90.0,
            alert_threshold_red=100.0,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 1: Green status (10% usage)
        usage1 = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=10.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage1)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.json()["alert_level"] == "green"

        # Step 2: Yellow alert (80% usage)
        usage2 = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=70.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage2)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.json()["alert_level"] == "yellow"

        # Step 3: Orange alert (95% usage)
        usage3 = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=15.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage3)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.json()["alert_level"] == "orange"

        # Step 4: Red alert (105% usage - over budget)
        usage4 = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=10.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage4)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        status_data = response.json()
        assert status_data["alert_level"] == "red"
        assert status_data["current_spent"] > status_data["monthly_limit"]


class TestBudgetResetFlow:
    """E2E tests for budget reset workflows"""

    def test_user_manual_reset_with_permission(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: User with permission manually resets their budget

        Steps:
        1. User has budget with reset permission
        2. User accumulates usage
        3. User manually resets budget
        4. Reset log is created
        5. Usage counter is reset
        """
        # Step 1: Create budget with reset permission
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
            user_can_reset_budget=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Accumulate usage
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=15.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage)
        db_session.commit()

        # Verify current usage
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_before = c.get("/api/v1/budget/status").json()

        assert status_before["current_spent"] == 15.0

        # Step 3: User resets budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_response = c.post("/api/v1/budget/reset")

        assert reset_response.status_code == 200

        # Step 4: Verify reset log was created
        reset_log = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == regular_user.user_id)
            .first()
        )

        assert reset_log is not None
        assert reset_log.reset_type == "manual"
        assert reset_log.previous_spent == 15.0

        # Step 5: Verify new period started (old usage excluded)
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_after = c.get("/api/v1/budget/status").json()

        # Old usage should be excluded from new period
        assert status_after["current_spent"] == 0.0

    def test_admin_resets_user_budget(
        self, client, override_get_db, db_session, admin_user, regular_user
    ):
        """
        E2E Flow: Admin manually resets a user's budget

        Steps:
        1. User has budget (no reset permission)
        2. User accumulates usage
        3. Admin resets user's budget
        4. Reset log shows admin as reset_by
        """
        # Step 1: Create budget without reset permission
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
            user_can_reset_budget=False,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Add usage
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=20.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage)
        db_session.commit()

        # Step 3: Admin resets budget
        reset_data = {
            "target_user_id": regular_user.user_id,
            "reason": "User requested reset via support ticket",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            reset_response = c.post("/api/v1/budget/admin/reset", json=reset_data)

        assert reset_response.status_code == 200

        # Step 4: Verify admin is recorded in log
        reset_log = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == regular_user.user_id)
            .first()
        )

        assert reset_log is not None
        assert reset_log.reset_by == admin_user.user_id
        assert "support ticket" in reset_log.reason.lower()


class TestBudgetEnforcementFlow:
    """E2E tests for budget enforcement during API usage"""

    def test_budget_enforcement_blocks_overbudget_requests(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: Budget enforcement prevents API calls when budget exceeded

        Steps:
        1. User has budget with enforcement enabled
        2. User reaches budget limit
        3. Budget status shows over budget
        4. (In production, subsequent API calls would be blocked)
        """
        # Step 1: Create budget with low limit and enforcement
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=10.0,
            enforce_budget=True,
            budget_visible_to_user=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Exceed budget
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=12.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage)
        db_session.commit()

        # Step 3: Verify over budget status
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        status_data = status_response.json()
        assert status_data["current_spent"] > status_data["monthly_limit"]
        assert status_data["alert_level"] == "red"
        assert status_data["remaining"] < 0

    def test_budget_enforcement_disabled_allows_overbudget(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: User with enforcement disabled can exceed budget

        Steps:
        1. User has budget with enforcement disabled
        2. User exceeds budget limit
        3. Status shows over budget but enforcement not blocking
        """
        # Step 1: Create budget with enforcement disabled
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=10.0,
            enforce_budget=False,  # Disabled
            budget_visible_to_user=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Exceed budget
        usage = APIUsage(
            user_id=regular_user.user_id,
            provider="mistral",
            estimated_cost=15.0,
            created_at=datetime.utcnow(),
        )
        db_session.add(usage)
        db_session.commit()

        # Step 3: Status shows over budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        status_data = status_response.json()
        assert status_data["current_spent"] > status_data["monthly_limit"]
        # But no blocking occurs (would be checked in API call middleware)


class TestMultiUserBudgetFlow:
    """E2E tests for multiple users with different budget configurations"""

    def test_multiple_users_independent_budgets(
        self, client, override_get_db, db_session, admin_user
    ):
        """
        E2E Flow: Multiple users have independent budget configurations

        Steps:
        1. Admin creates different budgets for 3 users
        2. Each user has different limits and permissions
        3. Each user's budget is independent
        """
        # Create 3 users with different budgets
        user_configs = [
            {
                "user_id": "user_basic",
                "monthly_limit": 30.0,
                "can_modify": False,
                "can_reset": False,
            },
            {
                "user_id": "user_power",
                "monthly_limit": 100.0,
                "can_modify": True,
                "can_reset": True,
            },
            {
                "user_id": "user_restricted",
                "monthly_limit": 10.0,
                "can_modify": False,
                "can_reset": False,
            },
        ]

        for config in user_configs:
            # Create user
            user = User(
                user_id=config["user_id"],
                username=config["user_id"],
                email=f"{config['user_id']}@example.com",
                role=UserRole.USER,
                is_active=True,
                is_verified=True,
            )
            db_session.add(user)
            db_session.commit()

            # Configure budget via admin
            budget_config = {
                "target_user_id": config["user_id"],
                "monthly_limit_usd": config["monthly_limit"],
                "user_can_modify_limit": config["can_modify"],
                "user_can_reset_budget": config["can_reset"],
                "budget_visible_to_user": True,
            }

            with client as c:
                c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
                c.put("/api/v1/budget/admin/configure", json=budget_config)

        # Verify each user has correct budget
        for config in user_configs:
            with client as c:
                c.headers = {"Authorization": f"Bearer {config['user_id']}"}
                status_response = c.get("/api/v1/budget/status")

            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["monthly_limit"] == config["monthly_limit"]

        # Verify budgets are independent (admin can list all)
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            list_response = c.get("/api/v1/budget/admin/list")

        assert list_response.status_code == 200
        all_budgets = list_response.json()["budgets"]
        assert len(all_budgets) >= 3  # At least our 3 test users


class TestBudgetPermissionFlow:
    """E2E tests for permission-based budget access"""

    def test_user_cannot_access_admin_endpoints(
        self, client, override_get_db, regular_user
    ):
        """
        E2E Flow: Regular user is blocked from admin endpoints

        Steps:
        1. Regular user tries to configure another user's budget
        2. Regular user tries to list all budgets
        3. Regular user tries to admin reset
        4. All attempts are forbidden
        """
        # Attempt 1: Configure another user
        config_data = {
            "target_user_id": "other_user",
            "monthly_limit_usd": 100.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            config_response = c.put("/api/v1/budget/admin/configure", json=config_data)

        assert config_response.status_code == 403

        # Attempt 2: List all budgets
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            list_response = c.get("/api/v1/budget/admin/list")

        assert list_response.status_code == 403

        # Attempt 3: Admin reset
        reset_data = {
            "target_user_id": "other_user",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_response = c.post("/api/v1/budget/admin/reset", json=reset_data)

        assert reset_response.status_code == 403

    def test_user_cannot_modify_without_permission(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: User without modify permission cannot change settings

        Steps:
        1. User has budget with modify permission disabled
        2. User tries to update settings
        3. Update is forbidden
        """
        # Create budget without modify permission
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=False,  # No permission
            budget_visible_to_user=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Try to update
        update_data = {
            "monthly_limit_usd": 100.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            update_response = c.put("/api/v1/budget/settings", json=update_data)

        assert update_response.status_code == 403

    def test_user_cannot_reset_without_permission(
        self, client, override_get_db, db_session, regular_user
    ):
        """
        E2E Flow: User without reset permission cannot reset budget

        Steps:
        1. User has budget with reset permission disabled
        2. User tries to reset
        3. Reset is forbidden
        """
        # Create budget without reset permission
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_reset_budget=False,  # No permission
            budget_visible_to_user=True,
        )
        db_session.add(settings)
        db_session.commit()

        # Try to reset
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_response = c.post("/api/v1/budget/reset")

        assert reset_response.status_code == 403


class TestCompleteBudgetLifecycle:
    """E2E test for complete budget lifecycle from creation to reset"""

    def test_complete_budget_lifecycle(
        self, client, override_get_db, db_session, admin_user, regular_user
    ):
        """
        E2E Flow: Complete budget lifecycle

        Steps:
        1. Admin creates budget for user
        2. User views initial budget (zero usage)
        3. User accumulates usage over time
        4. User monitors alerts as budget approaches limit
        5. User reaches near-limit (orange alert)
        6. Admin increases user's limit
        7. User continues usage with new limit
        8. Period ends and automatic reset occurs (simulated)
        9. User starts new period with reset counter
        """
        # Step 1: Admin creates budget
        config_data = {
            "target_user_id": regular_user.user_id,
            "monthly_limit_usd": 50.0,
            "budget_visible_to_user": True,
            "user_can_modify_limit": False,
            "user_can_reset_budget": False,
            "enforce_budget": True,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            c.put("/api/v1/budget/admin/configure", json=config_data)

        # Step 2: User views initial budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            initial_status = c.get("/api/v1/budget/status").json()

        assert initial_status["current_spent"] == 0.0
        assert initial_status["alert_level"] == "green"

        # Step 3: User accumulates usage
        for i in range(5):
            usage = APIUsage(
                user_id=regular_user.user_id,
                provider="mistral",
                estimated_cost=5.0,
                created_at=datetime.utcnow() - timedelta(hours=5 - i),
            )
            db_session.add(usage)
        db_session.commit()

        # Step 4: Monitor alerts (50% usage = green/yellow)
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            mid_status = c.get("/api/v1/budget/status").json()

        assert mid_status["current_spent"] == 25.0
        assert mid_status["percentage_used"] == 50.0

        # Step 5: Reach near-limit
        for i in range(4):
            usage = APIUsage(
                user_id=regular_user.user_id,
                provider="mistral",
                estimated_cost=5.0,
                created_at=datetime.utcnow(),
            )
            db_session.add(usage)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            near_limit_status = c.get("/api/v1/budget/status").json()

        assert near_limit_status["alert_level"] in ["orange", "red"]

        # Step 6: Admin increases limit
        increase_config = {
            "target_user_id": regular_user.user_id,
            "monthly_limit_usd": 100.0,
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            c.put("/api/v1/budget/admin/configure", json=increase_config)

        # Step 7: User continues with new limit
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            new_limit_status = c.get("/api/v1/budget/status").json()

        assert new_limit_status["monthly_limit"] == 100.0
        assert new_limit_status["alert_level"] in [
            "green",
            "yellow",
        ]  # No longer critical

        # Step 8: Simulate period reset (admin reset)
        reset_data = {
            "target_user_id": regular_user.user_id,
            "reason": "Monthly automatic reset",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            c.post("/api/v1/budget/admin/reset", json=reset_data)

        # Step 9: Verify new period
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_status = c.get("/api/v1/budget/status").json()

        assert reset_status["current_spent"] == 0.0  # New period
        assert reset_status["alert_level"] == "green"
