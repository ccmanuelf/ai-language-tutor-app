#!/usr/bin/env python3
"""
Admin User Upgrade Script for AI Language Tutor App

This script upgrades mcampos.cerda@tutanota.com to ADMIN role
and initializes the admin system.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.admin_auth import (
    admin_auth_service,
    initialize_admin_system,
    get_admin_user_info,
)
from app.database.config import get_db_session_context
from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_current_admin_status():
    """Check current admin user status"""
    logger.info("Checking current admin user status...")

    admin_info = get_admin_user_info()
    if admin_info:
        logger.info("Admin user found:")
        logger.info(f"  User ID: {admin_info['user_id']}")
        logger.info(f"  Username: {admin_info['username']}")
        logger.info(f"  Email: {admin_info['email']}")
        logger.info(f"  Role: {admin_info['role']}")
        logger.info(f"  Is Admin: {admin_info['is_admin']}")
        return admin_info
    else:
        logger.info("Admin user not found")
        return None


def upgrade_admin_user():
    """Upgrade mcampos.cerda@tutanota.com to admin role"""
    admin_email = "mcampos.cerda@tutanota.com"

    logger.info(f"Upgrading user {admin_email} to ADMIN role...")

    # First check if user exists
    try:
        with get_db_session_context() as session:
            user = session.query(User).filter(User.email == admin_email).first()

            if not user:
                logger.error(f"User {admin_email} not found in database")
                logger.info("Creating admin user...")

                # Create admin user using the service
                success = initialize_admin_system()
                if success:
                    logger.info("✅ Admin user created successfully")
                    return True
                else:
                    logger.error("❌ Failed to create admin user")
                    return False

            # User exists, check current role
            current_role = user.role
            logger.info(f"Current role: {current_role}")

            if current_role == UserRole.ADMIN:
                logger.info("✅ User is already an admin")
                return True

            # Upgrade to admin
            success = admin_auth_service.upgrade_user_to_admin(admin_email)
            if success:
                logger.info("✅ User successfully upgraded to ADMIN role")
                return True
            else:
                logger.error("❌ Failed to upgrade user to admin")
                return False

    except Exception as e:
        logger.error(f"❌ Error during admin upgrade: {e}")
        return False


def test_admin_permissions():
    """Test admin permission system"""
    logger.info("Testing admin permission system...")

    try:
        from app.services.admin_auth import AdminPermission

        # Test permission definitions
        admin_permissions = admin_auth_service.get_user_permissions(UserRoleEnum.ADMIN)
        parent_permissions = admin_auth_service.get_user_permissions(
            UserRoleEnum.PARENT
        )
        child_permissions = admin_auth_service.get_user_permissions(UserRoleEnum.CHILD)

        logger.info(
            f"ADMIN permissions ({len(admin_permissions)}): {admin_permissions[:5]}..."
        )
        logger.info(
            f"PARENT permissions ({len(parent_permissions)}): {parent_permissions}"
        )
        logger.info(
            f"CHILD permissions ({len(child_permissions)}): {child_permissions}"
        )

        # Test specific permission checks
        test_cases = [
            (UserRoleEnum.ADMIN, AdminPermission.ACCESS_ADMIN_DASHBOARD, True),
            (UserRoleEnum.ADMIN, AdminPermission.MANAGE_USERS, True),
            (UserRoleEnum.PARENT, AdminPermission.VIEW_ANALYTICS, True),
            (UserRoleEnum.PARENT, AdminPermission.MANAGE_USERS, False),
            (UserRoleEnum.CHILD, AdminPermission.ACCESS_ADMIN_DASHBOARD, False),
        ]

        for role, permission, expected in test_cases:
            result = admin_auth_service.has_permission(role, permission)
            status = "✅" if result == expected else "❌"
            logger.info(
                f"{status} {role.value} + {permission} = {result} (expected: {expected})"
            )

        logger.info("✅ Permission system tests completed")
        return True

    except Exception as e:
        logger.error(f"❌ Permission system test failed: {e}")
        return False


def main():
    """Main upgrade process"""
    logger.info("🚀 Starting Admin User Upgrade Process")
    logger.info("=" * 50)

    # Step 1: Check current status
    logger.info("STEP 1: Checking current admin status")
    check_current_admin_status()

    # Step 2: Upgrade user if needed
    logger.info("\nSTEP 2: Upgrading admin user")
    upgrade_success = upgrade_admin_user()

    if not upgrade_success:
        logger.error("❌ Admin upgrade failed. Exiting.")
        return False

    # Step 3: Verify upgrade
    logger.info("\nSTEP 3: Verifying admin upgrade")
    new_status = check_current_admin_status()

    if new_status and new_status["is_admin"]:
        logger.info("✅ Admin user upgrade verified successfully")
    else:
        logger.error("❌ Admin user upgrade verification failed")
        return False

    # Step 4: Test permission system
    logger.info("\nSTEP 4: Testing permission system")
    permission_test = test_admin_permissions()

    if not permission_test:
        logger.error("❌ Permission system test failed")
        return False

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("🎉 ADMIN USER UPGRADE COMPLETED SUCCESSFULLY")
    logger.info("=" * 50)
    logger.info(f"✅ Admin user: {new_status['email']}")
    logger.info(f"✅ User ID: {new_status['user_id']}")
    logger.info(f"✅ Role: {new_status['role']}")
    logger.info(f"✅ Admin access: {new_status['is_admin']}")
    logger.info("✅ Permission system: Working")
    logger.info("\n🔑 Next steps:")
    logger.info("  1. Test admin login")
    logger.info("  2. Access admin dashboard")
    logger.info("  3. Verify configuration access")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
