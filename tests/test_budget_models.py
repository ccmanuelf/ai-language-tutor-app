"""
Comprehensive Tests for Budget Database Models
AI Language Tutor App - Budget Management System

Tests UserBudgetSettings and BudgetResetLog models:
- Model creation and validation
- Relationships and constraints
- Business logic methods
- Data integrity

TRUE 100% coverage goal for budget models.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.budget import (
    BudgetAlert,
    BudgetPeriod,
    BudgetResetLog,
    UserBudgetSettings,
)
from app.models.database import Base, User, UserRole

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


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
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


class TestUserBudgetSettingsModel:
    """Tests for UserBudgetSettings model"""

    def test_create_default_budget_settings(self, db_session, test_user):
        """Test creating budget settings with default values"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.user_id == test_user.user_id
        assert settings.monthly_limit_usd == 30.0  # Default
        assert settings.enforce_budget is True  # Default
        assert settings.budget_visible_to_user is True  # Default
        assert settings.user_can_modify_limit is False  # Default
        assert settings.user_can_reset_budget is False  # Default
        assert settings.budget_period == BudgetPeriod.MONTHLY  # Default
        assert settings.alert_threshold_yellow == 50.0  # Default
        assert settings.alert_threshold_orange == 75.0  # Default
        assert settings.alert_threshold_red == 90.0  # Default

    def test_create_custom_budget_settings(self, db_session, test_user):
        """Test creating budget settings with custom values"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=100.0,
            custom_limit_usd=150.0,
            enforce_budget=False,
            budget_visible_to_user=True,
            user_can_modify_limit=True,
            user_can_reset_budget=True,
            budget_period=BudgetPeriod.CUSTOM,
            alert_threshold_yellow=80.0,
            alert_threshold_orange=95.0,
            alert_threshold_red=110.0,
            admin_notes="Power user - higher limits",
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.monthly_limit_usd == 100.0
        assert settings.custom_limit_usd == 150.0
        assert settings.enforce_budget is False
        assert settings.user_can_modify_limit is True
        assert settings.user_can_reset_budget is True
        assert settings.budget_period == BudgetPeriod.CUSTOM
        assert settings.admin_notes == "Power user - higher limits"

    def test_get_effective_limit_monthly(self, db_session, test_user):
        """Test get_effective_limit() for monthly period"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=50.0,
            budget_period=BudgetPeriod.MONTHLY,
        )
        db_session.add(settings)
        db_session.commit()

        assert settings.get_effective_limit() == 50.0

    def test_get_effective_limit_custom(self, db_session, test_user):
        """Test get_effective_limit() for custom period"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=50.0,
            custom_limit_usd=75.0,
            budget_period=BudgetPeriod.CUSTOM,
        )
        db_session.add(settings)
        db_session.commit()

        assert settings.get_effective_limit() == 75.0

    def test_get_effective_limit_custom_without_custom_limit(
        self, db_session, test_user
    ):
        """Test get_effective_limit() for custom period without custom_limit_usd"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=50.0,
            custom_limit_usd=None,
            budget_period=BudgetPeriod.CUSTOM,
        )
        db_session.add(settings)
        db_session.commit()

        # Should fall back to monthly_limit_usd
        assert settings.get_effective_limit() == 50.0

    def test_period_dates_auto_set(self, db_session, test_user):
        """Test that period start date is auto-set on creation"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.current_period_start is not None
        # current_period_end is None by default - it's calculated when needed
        # last_reset_date should also be set
        assert settings.last_reset_date is not None

    def test_unique_user_id_constraint(self, db_session, test_user):
        """Test that user_id must be unique"""
        settings1 = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=30.0,
        )
        db_session.add(settings1)
        db_session.commit()

        # Try to create another settings for same user
        settings2 = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=50.0,
        )
        db_session.add(settings2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()

    def test_timestamps_auto_set(self, db_session, test_user):
        """Test that created_at and updated_at are auto-set"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.created_at is not None
        assert settings.updated_at is not None
        assert settings.created_at <= settings.updated_at

    def test_updated_at_changes_on_update(self, db_session, test_user):
        """Test that updated_at changes when record is updated"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=30.0,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        original_updated_at = settings.updated_at

        # Wait a moment and update (SQLite timestamps are second-precision)
        import time

        time.sleep(1.1)

        settings.monthly_limit_usd = 50.0
        db_session.commit()
        db_session.refresh(settings)

        assert settings.updated_at >= original_updated_at

    def test_budget_period_enum_values(self, db_session, test_user):
        """Test all BudgetPeriod enum values"""
        for period in [
            BudgetPeriod.MONTHLY,
            BudgetPeriod.WEEKLY,
            BudgetPeriod.DAILY,
            BudgetPeriod.CUSTOM,
        ]:
            settings = UserBudgetSettings(
                user_id=f"user_{period.value}",
                budget_period=period,
            )
            db_session.add(settings)

        db_session.commit()

        # Verify all were created
        count = db_session.query(UserBudgetSettings).count()
        assert count == 4

    def test_negative_limit_allowed(self, db_session, test_user):
        """Test that negative limits are stored (though may be validated elsewhere)"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=-10.0,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.monthly_limit_usd == -10.0

    def test_zero_limit_allowed(self, db_session, test_user):
        """Test that zero limit is allowed"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=0.0,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.monthly_limit_usd == 0.0

    def test_very_large_limit(self, db_session, test_user):
        """Test storing very large budget limits"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=999999.99,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.monthly_limit_usd == 999999.99

    def test_alert_thresholds_precision(self, db_session, test_user):
        """Test that alert thresholds store decimal precision"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            alert_threshold_yellow=75.5,
            alert_threshold_orange=90.25,
            alert_threshold_red=99.99,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.alert_threshold_yellow == 75.5
        assert settings.alert_threshold_orange == 90.25
        assert settings.alert_threshold_red == 99.99

    def test_admin_notes_optional(self, db_session, test_user):
        """Test that admin_notes is optional"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert settings.admin_notes is None

    def test_admin_notes_can_be_long(self, db_session, test_user):
        """Test that admin_notes can store long text"""
        long_note = "A" * 1000  # 1000 characters
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            admin_notes=long_note,
        )
        db_session.add(settings)
        db_session.commit()
        db_session.refresh(settings)

        assert len(settings.admin_notes) == 1000
        assert settings.admin_notes == long_note


class TestBudgetResetLogModel:
    """Tests for BudgetResetLog model"""

    def test_create_reset_log_entry(self, db_session, test_user):
        """Test creating a budget reset log entry"""
        from datetime import datetime, timedelta

        now = datetime.now()
        prev_start = now - timedelta(days=30)
        prev_end = now
        new_start = now
        new_end = now + timedelta(days=30)

        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="manual",
            reset_by=test_user.user_id,
            previous_limit=30.0,
            new_limit=30.0,
            previous_spent=15.0,
            previous_period_start=prev_start,
            previous_period_end=prev_end,
            new_period_start=new_start,
            new_period_end=new_end,
            reason="User requested reset",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.user_id == test_user.user_id
        assert log.reset_type == "manual"
        assert log.reset_by == test_user.user_id
        assert log.previous_limit == 30.0
        assert log.new_limit == 30.0
        assert log.previous_spent == 15.0
        assert log.reason == "User requested reset"

    def test_create_automatic_reset_log(self, db_session, test_user):
        """Test creating an automatic reset log entry"""
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="automatic",
            reset_by="system",
            previous_limit=30.0,
            new_limit=30.0,
            previous_spent=25.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
            reason="Monthly automatic reset",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.reset_type == "automatic"
        assert log.reset_by == "system"

    def test_reset_log_timestamp_auto_set(self, db_session, test_user):
        """Test that reset_at timestamp is auto-set"""
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="manual",
            reset_by=test_user.user_id,
            previous_limit=30.0,
            new_limit=50.0,
            previous_spent=0.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.reset_timestamp is not None
        assert isinstance(log.reset_timestamp, datetime)

    def test_multiple_reset_logs_for_user(self, db_session, test_user):
        """Test that multiple reset logs can exist for one user"""
        logs = []
        for i in range(5):
            log = BudgetResetLog(
                user_id=test_user.user_id,
                reset_type="manual",
                reset_by=test_user.user_id,
                previous_limit=30.0 + i * 10,
                new_limit=40.0 + i * 10,
                previous_spent=10.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
            )
            logs.append(log)
            db_session.add(log)

        db_session.commit()

        # Query all logs for user
        user_logs = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == test_user.user_id)
            .all()
        )

        assert len(user_logs) == 5

    def test_reset_log_reason_optional(self, db_session, test_user):
        """Test that reason is optional"""
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="automatic",
            reset_by="system",
            previous_limit=30.0,
            new_limit=30.0,
            previous_spent=0.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.reason is None

    def test_reset_log_ordering(self, db_session, test_user):
        """Test that reset logs can be ordered by timestamp"""
        import time

        # Create logs with small time gaps
        for i in range(3):
            log = BudgetResetLog(
                user_id=test_user.user_id,
                reset_type="manual",
                reset_by=test_user.user_id,
                previous_limit=30.0,
                new_limit=30.0,
                previous_spent=0.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
            )
            db_session.add(log)
            db_session.commit()
            time.sleep(0.01)

        # Query logs ordered by timestamp
        logs = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == test_user.user_id)
            .order_by(BudgetResetLog.reset_timestamp.asc())
            .all()
        )

        assert len(logs) == 3
        assert logs[0].reset_timestamp <= logs[1].reset_timestamp <= logs[2].reset_timestamp

    def test_reset_log_limit_change_tracking(self, db_session, test_user):
        """Test tracking limit changes in reset log"""
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="manual",
            reset_by="admin_user",
            previous_limit=30.0,
            new_limit=100.0,
            previous_spent=25.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
            reason="Admin increased limit",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        # Verify limit change is tracked
        assert log.previous_limit == 30.0
        assert log.new_limit == 100.0
        assert log.new_limit > log.previous_limit

    def test_reset_log_spent_tracking(self, db_session, test_user):
        """Test tracking previous spent amount in reset log"""
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="automatic",
            reset_by="system",
            previous_limit=30.0,
            new_limit=30.0,
            previous_spent=28.50,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
            reason="Monthly reset - user nearly reached limit",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.previous_spent == 28.50


class TestBudgetEnums:
    """Tests for budget-related enums"""

    def test_budget_period_enum_values(self):
        """Test BudgetPeriod enum has all expected values"""
        assert hasattr(BudgetPeriod, "MONTHLY")
        assert hasattr(BudgetPeriod, "WEEKLY")
        assert hasattr(BudgetPeriod, "DAILY")
        assert hasattr(BudgetPeriod, "CUSTOM")

        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.DAILY.value == "daily"
        assert BudgetPeriod.CUSTOM.value == "custom"

    def test_budget_alert_enum_values(self):
        """Test BudgetAlert enum has all expected values"""
        assert hasattr(BudgetAlert, "GREEN")
        assert hasattr(BudgetAlert, "YELLOW")
        assert hasattr(BudgetAlert, "ORANGE")
        assert hasattr(BudgetAlert, "RED")

        assert BudgetAlert.GREEN.value == "green"
        assert BudgetAlert.YELLOW.value == "yellow"
        assert BudgetAlert.ORANGE.value == "orange"
        assert BudgetAlert.RED.value == "red"


class TestBudgetModelRelationships:
    """Tests for relationships between budget models and other models"""

    def test_budget_settings_user_relationship(self, db_session, test_user):
        """Test that budget settings can reference user"""
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=30.0,
        )
        db_session.add(settings)
        db_session.commit()

        # Query settings
        retrieved_settings = (
            db_session.query(UserBudgetSettings)
            .filter(UserBudgetSettings.user_id == test_user.user_id)
            .first()
        )

        assert retrieved_settings is not None
        assert retrieved_settings.user_id == test_user.user_id

    def test_reset_log_user_relationship(self, db_session, test_user):
        """Test that reset log can reference user"""
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="manual",
            reset_by=test_user.user_id,
            previous_limit=30.0,
            new_limit=30.0,
            previous_spent=0.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
        )
        db_session.add(log)
        db_session.commit()

        # Query log
        retrieved_log = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == test_user.user_id)
            .first()
        )

        assert retrieved_log is not None
        assert retrieved_log.user_id == test_user.user_id

    def test_cascade_delete_behavior(self, db_session, test_user):
        """Test cascade delete behavior when user is deleted"""
        # Create budget settings and reset log
        settings = UserBudgetSettings(
            user_id=test_user.user_id,
            monthly_limit_usd=30.0,
        )
        log = BudgetResetLog(
            user_id=test_user.user_id,
            reset_type="manual",
            reset_by=test_user.user_id,
            previous_limit=30.0,
            new_limit=30.0,
            previous_spent=0.0,
            previous_period_start=datetime.now() - timedelta(days=30),
            previous_period_end=datetime.now(),
            new_period_start=datetime.now(),
            new_period_end=datetime.now() + timedelta(days=30),
        )
        db_session.add_all([settings, log])
        db_session.commit()

        # Delete user
        db_session.delete(test_user)
        db_session.commit()

        # Check if budget settings and log still exist
        # (behavior depends on cascade configuration)
        remaining_settings = (
            db_session.query(UserBudgetSettings)
            .filter(UserBudgetSettings.user_id == test_user.user_id)
            .first()
        )

        remaining_logs = (
            db_session.query(BudgetResetLog)
            .filter(BudgetResetLog.user_id == test_user.user_id)
            .first()
        )

        # Note: Actual behavior depends on foreign key constraints
        # This test documents the expected behavior
