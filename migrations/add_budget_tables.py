"""
Database Migration: Add Budget Management Tables

Creates user_budget_settings and budget_reset_log tables for
comprehensive per-user budget management system.

Run with: python migrations/add_budget_tables.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.config import get_primary_db_session
from app.models.budget import Base, BudgetPeriod, BudgetResetLog, UserBudgetSettings
from app.models.database import User, UserRole


def check_tables_exist(engine) -> dict:
    """Check which budget tables already exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    return {
        "user_budget_settings": "user_budget_settings" in existing_tables,
        "budget_reset_log": "budget_reset_log" in existing_tables,
    }


def create_budget_tables(engine):
    """Create budget management tables"""
    print("Creating budget management tables...")

    # Check what exists
    status = check_tables_exist(engine)

    if status["user_budget_settings"] and status["budget_reset_log"]:
        print("✅ Budget tables already exist. No migration needed.")
        return

    # Create tables
    Base.metadata.create_all(
        engine,
        tables=[
            UserBudgetSettings.__table__,
            BudgetResetLog.__table__,
        ],
    )

    print("✅ Budget tables created successfully!")
    print("   - user_budget_settings")
    print("   - budget_reset_log")


def create_default_admin_budget_settings(db: Session):
    """Create default budget settings for admin users"""
    print("\nCreating default budget settings for admin users...")

    # Get all admin users
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()

    if not admins:
        print("⚠️  No admin users found. Skipping admin budget setup.")
        return

    created_count = 0
    for admin in admins:
        # Check if admin already has budget settings
        existing = (
            db.query(UserBudgetSettings)
            .filter(UserBudgetSettings.user_id == admin.user_id)
            .first()
        )

        if existing:
            print(f"   Admin {admin.user_id} already has budget settings. Skipping.")
            continue

        # Create admin budget settings with full permissions
        admin_settings = UserBudgetSettings(
            user_id=admin.user_id,
            monthly_limit_usd=100.0,  # Higher limit for admins
            budget_period=BudgetPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=None,  # Will be calculated
            last_reset_date=datetime.now(),
            enforce_budget=False,  # Admins not restricted by default
            allow_budget_override=True,
            auto_fallback_to_ollama=False,
            alert_threshold_yellow=50.0,
            alert_threshold_orange=75.0,
            alert_threshold_red=90.0,
            budget_visible_to_user=True,  # Admins can see their budget
            user_can_modify_limit=True,  # Admins can modify their own limit
            user_can_reset_budget=True,  # Admins can reset their own budget
            admin_notes="Admin user - full budget access",
            configured_by="system_migration",
        )

        # Calculate period end
        admin_settings.current_period_end = admin_settings.calculate_next_reset_date()

        db.add(admin_settings)
        created_count += 1
        print(f"   ✅ Created budget settings for admin: {admin.user_id}")

    if created_count > 0:
        db.commit()
        print(f"\n✅ Created budget settings for {created_count} admin user(s)")
    else:
        print("\n✅ All admins already have budget settings")


def create_default_user_budget_settings(db: Session):
    """Create default budget settings for non-admin users"""
    print("\nCreating default budget settings for regular users...")

    # Get all non-admin users
    users = db.query(User).filter(User.role != UserRole.ADMIN).all()

    if not users:
        print("⚠️  No regular users found. Skipping user budget setup.")
        return

    created_count = 0
    for user in users:
        # Check if user already has budget settings
        existing = (
            db.query(UserBudgetSettings)
            .filter(UserBudgetSettings.user_id == user.user_id)
            .first()
        )

        if existing:
            continue

        # Create user budget settings with default permissions
        user_settings = UserBudgetSettings(
            user_id=user.user_id,
            monthly_limit_usd=30.0,  # Standard limit for users
            budget_period=BudgetPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=None,  # Will be calculated
            last_reset_date=datetime.now(),
            enforce_budget=True,  # Users are budget-restricted
            allow_budget_override=True,
            auto_fallback_to_ollama=False,
            alert_threshold_yellow=50.0,
            alert_threshold_orange=75.0,
            alert_threshold_red=90.0,
            budget_visible_to_user=True,  # Users can see their budget
            user_can_modify_limit=False,  # Users cannot modify limit (admin only)
            user_can_reset_budget=False,  # Users cannot reset (admin only)
            admin_notes="Default user settings",
            configured_by="system_migration",
        )

        # Calculate period end
        user_settings.current_period_end = user_settings.calculate_next_reset_date()

        db.add(user_settings)
        created_count += 1

    if created_count > 0:
        db.commit()
        print(f"✅ Created budget settings for {created_count} regular user(s)")
    else:
        print("✅ All regular users already have budget settings")


def verify_migration(engine, db: Session):
    """Verify migration was successful"""
    print("\n" + "=" * 60)
    print("MIGRATION VERIFICATION")
    print("=" * 60)

    # Check tables exist
    status = check_tables_exist(engine)

    print("\nTable Status:")
    print(
        f"   user_budget_settings: {'✅ EXISTS' if status['user_budget_settings'] else '❌ MISSING'}"
    )
    print(
        f"   budget_reset_log: {'✅ EXISTS' if status['budget_reset_log'] else '❌ MISSING'}"
    )

    # Count settings created
    budget_settings_count = db.query(UserBudgetSettings).count()
    reset_log_count = db.query(BudgetResetLog).count()

    print(f"\nData Status:")
    print(f"   User budget settings: {budget_settings_count} records")
    print(f"   Budget reset logs: {reset_log_count} records")

    # Check admin settings
    admin_count = (
        db.query(UserBudgetSettings)
        .filter(UserBudgetSettings.user_can_modify_limit == True)
        .count()
    )

    print(f"\nAdmin Configuration:")
    print(f"   Users with full budget access: {admin_count}")

    # Summary
    print("\n" + "=" * 60)
    if status["user_budget_settings"] and status["budget_reset_log"]:
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 60)
        print("\nBudget management system is now available!")
        print("\nAPI Endpoints:")
        print("   GET  /api/v1/budget/status")
        print("   GET  /api/v1/budget/settings")
        print("   PUT  /api/v1/budget/settings")
        print("   POST /api/v1/budget/reset")
        print("   GET  /api/v1/budget/usage/breakdown")
        print("   GET  /api/v1/budget/history")
        print("\nAdmin Endpoints:")
        print("   PUT  /api/v1/budget/admin/configure")
        print("   GET  /api/v1/budget/admin/users")
        print("   POST /api/v1/budget/admin/reset/{user_id}")
    else:
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        print("\nSome tables are missing. Please check errors above.")


def main():
    """Run the migration"""
    print("=" * 60)
    print("BUDGET MANAGEMENT SYSTEM MIGRATION")
    print("=" * 60)
    print("\nThis migration will:")
    print("1. Create user_budget_settings table")
    print("2. Create budget_reset_log table")
    print("3. Set up default budget settings for all users")
    print("4. Give admins full budget access")
    print("5. Give regular users view-only access\n")

    # Get database connection
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    db = get_primary_db_session()

    try:
        # Step 1: Create tables
        create_budget_tables(engine)

        # Step 2: Create default settings for admins
        create_default_admin_budget_settings(db)

        # Step 3: Create default settings for users
        create_default_user_budget_settings(db)

        # Step 4: Verify migration
        verify_migration(engine, db)

    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
