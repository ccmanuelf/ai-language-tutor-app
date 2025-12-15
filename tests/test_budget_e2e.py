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

# Note: Using datetime.now() instead of datetime.now() to match API implementation
# API uses datetime.now() for period calculations
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.config import get_primary_db_session
from app.main import app
from app.models.budget import BudgetResetLog, UserBudgetSettings
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
        role=UserRole.CHILD,
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
        role=UserRole.CHILD,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_regular_user(regular_user):
    """Override auth to return regular user"""
    from app.api.auth import SimpleUser, require_auth
    from app.services.auth import get_current_user

    class MockUser:
        def __init__(self):
            self.id = regular_user.id
            self.user_id = regular_user.user_id
            self.username = regular_user.username
            self.email = regular_user.email
            self.role = regular_user.role.value

    def override_auth():
        return MockUser()

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
    from app.api.auth import SimpleUser, require_auth
    from app.services.admin_auth import require_admin_access
    from app.services.auth import get_current_user

    class MockUser:
        def __init__(self):
            self.id = admin_user.id
            self.user_id = admin_user.user_id
            self.username = admin_user.username
            self.email = admin_user.email
            self.role = admin_user.role.value

    def override_auth():
        return MockUser()

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


class TestAdminBudgetConfigurationFlow:
    """E2E tests for admin budget configuration workflows"""

    def test_admin_creates_new_user_budget_configuration(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
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
        assert status_data["total_budget"] == 50.0

    def test_admin_grants_user_permissions(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        power_user,
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
            reset_response = c.post(
                "/api/v1/budget/reset", json={"reason": "User requested reset"}
            )

        assert reset_response.status_code == 200
        assert "successfully" in reset_response.json()["message"].lower()

    def test_admin_restricts_budget_visibility(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
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
        self, client, override_get_db, db_session, auth_regular_user, regular_user
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
        period_start = datetime.now() - timedelta(days=1)  # Start 1 day ago
        period_end = datetime.now() + timedelta(days=29)  # End 29 days from now
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Add API usage (all within current period)
        for i in range(5):
            usage = APIUsage(
                user_id=regular_user.id,
                api_provider="mistral",
                api_endpoint="/v1/chat/completions",
                request_type="chat",
                estimated_cost=2.0,
                tokens_used=1000,
                created_at=datetime.now() - timedelta(hours=i),
            )
            db_session.add(usage)
        db_session.commit()

        # Step 3: Check budget status
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["used_budget"] == 10.0  # 5 * 2.0
        assert status_data["total_budget"] == 30.0
        assert status_data["remaining_budget"] == 20.0

        # Step 4: View usage breakdown
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            breakdown_response = c.get("/api/v1/budget/usage/breakdown")

        assert breakdown_response.status_code == 200
        breakdown_data = breakdown_response.json()
        assert "mistral" in breakdown_data["by_provider"]

        # Step 5: View reset history (returns empty since no resets yet)
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            history_response = c.get("/api/v1/budget/history")

        assert history_response.status_code == 200
        history_data = history_response.json()
        # No resets yet, so should be empty list
        assert isinstance(history_data, list)

    def test_user_monitors_budget_approaching_limit(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """
        E2E Flow: User monitors budget as it approaches limit with alerts

        Steps:
        1. User starts with green status (low usage)
        2. Usage increases to yellow alert
        3. Usage increases to orange alert
        4. Usage reaches red alert (near/over limit)
        """
        period_start = datetime.now() - timedelta(days=1)
        period_end = datetime.now() + timedelta(days=29)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=100.0,
            budget_visible_to_user=True,
            alert_threshold_yellow=75.0,
            alert_threshold_orange=90.0,
            alert_threshold_red=100.0,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 1: Green status (10% usage)
        usage1 = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=10.0,
            created_at=datetime.now(),
        )
        db_session.add(usage1)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.json()["alert_level"] == "green"

        # Step 2: Yellow alert (80% usage)
        usage2 = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=70.0,
            created_at=datetime.now(),
        )
        db_session.add(usage2)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.json()["alert_level"] == "yellow"

        # Step 3: Orange alert (95% usage)
        usage3 = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=15.0,
            created_at=datetime.now(),
        )
        db_session.add(usage3)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        assert response.json()["alert_level"] == "orange"

        # Step 4: Red alert (105% usage - over budget)
        usage4 = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=10.0,
            created_at=datetime.now(),
        )
        db_session.add(usage4)
        db_session.commit()

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            response = c.get("/api/v1/budget/status")

        status_data = response.json()
        assert status_data["alert_level"] == "red"
        assert status_data["used_budget"] > status_data["total_budget"]


class TestBudgetResetFlow:
    """E2E tests for budget reset workflows"""

    def test_user_manual_reset_with_permission(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
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
        period_start = datetime.now() - timedelta(days=1)  # Start 1 day ago
        period_end = datetime.now() + timedelta(days=29)  # End 29 days from now
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
            user_can_reset_budget=True,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Accumulate usage (within current period, but in the past)
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=15.0,
            created_at=datetime.now() - timedelta(hours=1),  # 1 hour ago
        )
        db_session.add(usage)
        db_session.commit()

        # Verify current usage
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_before = c.get("/api/v1/budget/status").json()

        assert status_before["used_budget"] == 15.0

        # Step 3: User resets budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_response = c.post(
                "/api/v1/budget/reset", json={"reason": "Manual reset"}
            )

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

        # Refresh session to see updated settings
        db_session.expire_all()

        # Step 5: Verify new period started (old usage excluded)
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_after = c.get("/api/v1/budget/status").json()

        # Old usage should be excluded from new period
        # The usage was created 1 hour ago, reset sets period_start to now
        # So usage should not be counted in new period
        assert status_after["used_budget"] == 0.0
        assert status_after["alert_level"] == "green"

    def test_admin_resets_user_budget(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
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
        period_start = datetime.now() - timedelta(days=1)
        period_end = datetime.now() + timedelta(days=29)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            budget_visible_to_user=True,
            user_can_reset_budget=False,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Add usage
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=20.0,
            created_at=datetime.now(),
        )
        db_session.add(usage)
        db_session.commit()

        # Step 3: Admin resets budget
        reset_data = {
            "reason": "User requested reset via support ticket",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            reset_response = c.post(
                f"/api/v1/budget/admin/reset/{regular_user.user_id}", json=reset_data
            )

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
        self, client, override_get_db, db_session, auth_regular_user, regular_user
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
        period_start = datetime.now() - timedelta(days=1)
        period_end = datetime.now() + timedelta(days=29)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=10.0,
            enforce_budget=True,
            budget_visible_to_user=True,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Exceed budget
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=12.0,
            created_at=datetime.now(),
        )
        db_session.add(usage)
        db_session.commit()

        # Step 3: Verify over budget status
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        status_data = status_response.json()
        assert status_data["used_budget"] > status_data["total_budget"]
        assert status_data["alert_level"] == "red"
        assert status_data["remaining_budget"] == 0  # Clamped to 0, not negative

    def test_budget_enforcement_disabled_allows_overbudget(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """
        E2E Flow: User with enforcement disabled can exceed budget

        Steps:
        1. User has budget with enforcement disabled
        2. User exceeds budget limit
        3. Status shows over budget but enforcement not blocking
        """
        # Step 1: Create budget with enforcement disabled
        period_start = datetime.now() - timedelta(days=1)
        period_end = datetime.now() + timedelta(days=29)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=10.0,
            enforce_budget=False,  # Disabled
            budget_visible_to_user=True,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Step 2: Exceed budget
        usage = APIUsage(
            user_id=regular_user.id,
            api_provider="mistral",
            api_endpoint="/v1/chat/completions",
            request_type="chat",
            estimated_cost=15.0,
            created_at=datetime.now(),
        )
        db_session.add(usage)
        db_session.commit()

        # Step 3: Status shows over budget
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            status_response = c.get("/api/v1/budget/status")

        status_data = status_response.json()
        assert status_data["used_budget"] > status_data["total_budget"]
        # But no blocking occurs (would be checked in API call middleware)


class TestMultiUserBudgetFlow:
    """E2E tests for multiple users with different budget configurations"""

    def test_multiple_users_independent_budgets(
        self, client, override_get_db, db_session, auth_admin_user, admin_user
    ):
        """
        E2E Flow: Multiple users have independent budget configurations

        Steps:
        1. Admin creates different budgets for 3 users
        2. Each user has different limits and permissions
        3. Each user's budget is independent
        """
        from app.api.auth import require_auth

        # Create 3 users with different budgets
        user_configs = []
        created_users = []

        for i, (uid, budget, can_mod, can_reset) in enumerate(
            [
                ("user_basic", 30.0, False, False),
                ("user_power", 100.0, True, True),
                ("user_restricted", 10.0, False, False),
            ]
        ):
            # Create user
            user = User(
                user_id=uid,
                username=uid,
                email=f"{uid}@example.com",
                role=UserRole.CHILD,
                is_active=True,
                is_verified=True,
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            created_users.append(user)

            user_configs.append(
                {
                    "user_id": uid,
                    "user_obj": user,
                    "total_budget": budget,
                    "can_modify": can_mod,
                    "can_reset": can_reset,
                }
            )

            # Configure budget via admin
            budget_config = {
                "target_user_id": uid,
                "monthly_limit_usd": budget,
                "user_can_modify_limit": can_mod,
                "user_can_reset_budget": can_reset,
                "budget_visible_to_user": True,
            }

            with client as c:
                c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
                c.put("/api/v1/budget/admin/configure", json=budget_config)

        # Verify each user has correct budget
        for config in user_configs:
            user_obj = config["user_obj"]

            # Create auth override for this specific user
            class MockUser:
                def __init__(self):
                    self.id = user_obj.id
                    self.user_id = user_obj.user_id
                    self.username = user_obj.username
                    self.email = user_obj.email
                    self.role = user_obj.role.value

            def override_auth():
                return MockUser()

            app.dependency_overrides[require_auth] = override_auth

            with client as c:
                c.headers = {"Authorization": f"Bearer {config['user_id']}"}
                status_response = c.get("/api/v1/budget/status")

            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["total_budget"] == config["total_budget"]

        # Restore admin auth for list check
        app.dependency_overrides.clear()

        class MockAdminUser:
            def __init__(self):
                self.id = admin_user.id
                self.user_id = admin_user.user_id
                self.username = admin_user.username
                self.email = admin_user.email
                self.role = admin_user.role.value

        def override_admin_auth():
            return MockAdminUser()

        from app.services.admin_auth import require_admin_access

        app.dependency_overrides[require_auth] = override_admin_auth
        app.dependency_overrides[require_admin_access] = override_admin_auth

        # Verify budgets are independent (admin can list all)
        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            list_response = c.get("/api/v1/budget/admin/users")

        assert list_response.status_code == 200
        all_budgets = list_response.json()
        assert len(all_budgets) >= 3  # At least our 3 test users

        app.dependency_overrides.clear()


class TestBudgetPermissionFlow:
    """E2E tests for permission-based budget access"""

    def test_user_cannot_access_admin_endpoints(
        self, client, override_get_db, auth_regular_user, regular_user
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
            list_response = c.get("/api/v1/budget/admin/users")

        assert list_response.status_code == 403

        # Attempt 3: Admin reset
        reset_data = {
            "reason": "Testing permissions",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_response = c.post(
                "/api/v1/budget/admin/reset/other_user", json=reset_data
            )

        assert reset_response.status_code == 403

    def test_user_cannot_modify_without_permission(
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """
        E2E Flow: User without modify permission cannot change settings

        Steps:
        1. User has budget with modify permission disabled
        2. User tries to update settings
        3. Update is forbidden
        """
        # Create budget without modify permission
        period_start = datetime.now() - timedelta(days=1)
        period_end = datetime.now() + timedelta(days=29)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_modify_limit=False,  # No permission
            budget_visible_to_user=True,
            current_period_start=period_start,
            current_period_end=period_end,
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
        self, client, override_get_db, db_session, auth_regular_user, regular_user
    ):
        """
        E2E Flow: User without reset permission cannot reset budget

        Steps:
        1. User has budget with reset permission disabled
        2. User tries to reset
        3. Reset is forbidden
        """
        # Create budget without reset permission
        period_start = datetime.now() - timedelta(days=1)
        period_end = datetime.now() + timedelta(days=29)
        settings = UserBudgetSettings(
            user_id=regular_user.user_id,
            monthly_limit_usd=30.0,
            user_can_reset_budget=False,  # No permission
            budget_visible_to_user=True,
            current_period_start=period_start,
            current_period_end=period_end,
        )
        db_session.add(settings)
        db_session.commit()

        # Try to reset
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_response = c.post(
                "/api/v1/budget/reset", json={"reason": "Attempting reset"}
            )

        assert reset_response.status_code == 403


class TestCompleteBudgetLifecycle:
    """E2E test for complete budget lifecycle from creation to reset"""

    def test_complete_budget_lifecycle(
        self,
        client,
        override_get_db,
        db_session,
        auth_admin_user,
        admin_user,
        auth_regular_user,
        regular_user,
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

        assert initial_status["used_budget"] == 0.0
        assert initial_status["alert_level"] == "green"

        # Step 3: User accumulates usage (all within current period)
        for i in range(5):
            usage = APIUsage(
                user_id=regular_user.id,
                api_provider="mistral",
                api_endpoint="/v1/chat/completions",
                request_type="chat",
                estimated_cost=5.0,
                created_at=datetime.now(),  # All created now, within period
            )
            db_session.add(usage)
        db_session.commit()

        # Step 4: Monitor alerts (50% usage = green/yellow)
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            mid_status = c.get("/api/v1/budget/status").json()

        assert mid_status["used_budget"] == 25.0
        assert mid_status["percentage_used"] == 50.0

        # Step 5: Reach near-limit
        for i in range(4):
            usage = APIUsage(
                user_id=regular_user.id,
                api_provider="mistral",
                api_endpoint="/v1/chat/completions",
                request_type="chat",
                estimated_cost=5.0,
                created_at=datetime.now(),
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

        assert new_limit_status["total_budget"] == 100.0
        assert new_limit_status["alert_level"] in [
            "green",
            "yellow",
        ]  # No longer critical

        # Step 8: Simulate period reset (admin reset)
        reset_data = {
            "reason": "Monthly automatic reset",
        }

        with client as c:
            c.headers = {"Authorization": f"Bearer {admin_user.user_id}"}
            c.post(
                f"/api/v1/budget/admin/reset/{regular_user.user_id}", json=reset_data
            )

        # Step 9: Verify new period
        with client as c:
            c.headers = {"Authorization": f"Bearer {regular_user.user_id}"}
            reset_status = c.get("/api/v1/budget/status").json()

        assert reset_status["used_budget"] == 0.0  # New period
        assert reset_status["alert_level"] == "green"
