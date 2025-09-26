#!/usr/bin/env python3
"""
Simple Admin Authentication Test for Task 3.1.1 Validation
Tests the core functionality that was actually implemented.
"""

import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.services.admin_auth import AdminAuthService, admin_auth_service
from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum
from app.database.config import get_db_session_context


def test_admin_user_database():
    """Test that admin user exists in database with correct role"""
    print("🔑 TEST 1: Admin User Database Record")
    try:
        with get_db_session_context() as session:
            admin_user = (
                session.query(User)
                .filter_by(email="mcampos.cerda@tutanota.com")
                .first()
            )

            if not admin_user:
                return False, "Admin user not found"

            if admin_user.role != UserRole.ADMIN:
                return False, f"Wrong role: {admin_user.role}"

            print(f"   ✅ Email: {admin_user.email}")
            print(f"   ✅ User ID: {admin_user.user_id}")
            print(f"   ✅ Role: {admin_user.role}")
            print(f"   ✅ Active: {admin_user.is_active}")

            return True, "Admin user correctly configured"
    except Exception as e:
        return False, f"Database error: {str(e)}"


def test_permission_system():
    """Test the role-based permission system"""
    print("\n🛡️ TEST 2: Permission System")
    try:
        auth_service = AdminAuthService()

        # Test admin permissions
        admin_perms = auth_service.get_user_permissions(UserRoleEnum.ADMIN)
        expected_admin_perms = [
            "manage_users",
            "view_users",
            "create_users",
            "delete_users",
            "manage_languages",
            "manage_features",
            "manage_ai_models",
            "manage_scenarios",
            "view_system_status",
            "manage_system_config",
            "access_admin_dashboard",
            "view_analytics",
            "export_data",
            "backup_system",
        ]

        for perm in expected_admin_perms:
            if perm not in admin_perms:
                return False, f"Missing admin permission: {perm}"

        print(f"   ✅ Admin permissions: {len(admin_perms)} permissions")

        # Test parent permissions
        parent_perms = auth_service.get_user_permissions(UserRoleEnum.PARENT)
        expected_parent_perms = ["view_users", "view_analytics", "view_system_status"]

        for perm in expected_parent_perms:
            if perm not in parent_perms:
                return False, f"Missing parent permission: {perm}"

        print(f"   ✅ Parent permissions: {len(parent_perms)} permissions")

        # Test child permissions (should be empty)
        child_perms = auth_service.get_user_permissions(UserRoleEnum.CHILD)
        if child_perms:
            return (
                False,
                f"Child should have no admin permissions, but has: {child_perms}",
            )

        print("   ✅ Child permissions: 0 permissions (correct)")

        return True, "Permission system working correctly"

    except Exception as e:
        return False, f"Permission system error: {str(e)}"


def test_permission_checking():
    """Test has_permission method"""
    print("\n✅ TEST 3: Permission Checking")
    try:
        auth_service = AdminAuthService()

        # Test admin has admin permissions
        if not auth_service.has_permission(
            UserRoleEnum.ADMIN, "access_admin_dashboard"
        ):
            return False, "Admin should have dashboard access"

        if not auth_service.has_permission(UserRoleEnum.ADMIN, "manage_users"):
            return False, "Admin should have user management"

        print("   ✅ Admin has required permissions")

        # Test parent has limited permissions
        if not auth_service.has_permission(UserRoleEnum.PARENT, "view_analytics"):
            return False, "Parent should have analytics view"

        if auth_service.has_permission(UserRoleEnum.PARENT, "manage_users"):
            return False, "Parent should NOT have user management"

        print("   ✅ Parent has correct limited permissions")

        # Test child has no admin permissions
        if auth_service.has_permission(UserRoleEnum.CHILD, "access_admin_dashboard"):
            return False, "Child should NOT have dashboard access"

        print("   ✅ Child correctly blocked from admin features")

        return True, "Permission checking working correctly"

    except Exception as e:
        return False, f"Permission checking error: {str(e)}"


def test_admin_user_methods():
    """Test admin user detection methods"""
    print("\n👑 TEST 4: Admin User Detection")
    try:
        auth_service = AdminAuthService()

        # Test is_admin_user with admin data
        admin_data = {"role": UserRole.ADMIN, "email": "mcampos.cerda@tutanota.com"}
        if not auth_service.is_admin_user(admin_data):
            return False, "is_admin_user should return True for admin"

        print("   ✅ is_admin_user correctly identifies admin")

        # Test is_admin_user with non-admin data
        parent_data = {"role": UserRole.PARENT, "email": "parent@example.com"}
        if auth_service.is_admin_user(parent_data):
            return False, "is_admin_user should return False for parent"

        print("   ✅ is_admin_user correctly rejects non-admin")

        # Test is_parent_or_admin
        if not auth_service.is_parent_or_admin(admin_data):
            return False, "is_parent_or_admin should return True for admin"

        if not auth_service.is_parent_or_admin(parent_data):
            return False, "is_parent_or_admin should return True for parent"

        child_data = {"role": UserRole.CHILD, "email": "child@example.com"}
        if auth_service.is_parent_or_admin(child_data):
            return False, "is_parent_or_admin should return False for child"

        print("   ✅ is_parent_or_admin works correctly")

        return True, "Admin user detection working correctly"

    except Exception as e:
        return False, f"Admin user detection error: {str(e)}"


def test_upgrade_functionality():
    """Test admin upgrade functionality"""
    print("\n🔧 TEST 5: Admin Upgrade Functionality")
    try:
        auth_service = AdminAuthService()

        # Test that upgrade to existing admin returns True
        result = auth_service.upgrade_user_to_admin("mcampos.cerda@tutanota.com")
        if not result:
            return False, "upgrade_user_to_admin failed for existing admin"

        print("   ✅ upgrade_user_to_admin handles existing admin correctly")

        # Verify the user is still admin after "upgrade"
        with get_db_session_context() as session:
            admin_user = (
                session.query(User)
                .filter_by(email="mcampos.cerda@tutanota.com")
                .first()
            )
            if admin_user.role != UserRole.ADMIN:
                return False, f"User role changed unexpectedly: {admin_user.role}"

        print("   ✅ Admin user role preserved after upgrade operation")

        return True, "Admin upgrade functionality working"

    except Exception as e:
        return False, f"Admin upgrade error: {str(e)}"


def run_focused_test():
    """Run focused admin authentication tests"""
    print("🧪 ADMIN AUTHENTICATION FOCUSED TEST SUITE")
    print("=" * 55)

    tests = [
        ("Admin User Database", test_admin_user_database),
        ("Permission System", test_permission_system),
        ("Permission Checking", test_permission_checking),
        ("Admin User Detection", test_admin_user_methods),
        ("Admin Upgrade Functionality", test_upgrade_functionality),
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(tests),
        "passed": 0,
        "failed": 0,
        "test_results": [],
        "overall_status": "UNKNOWN",
    }

    for test_name, test_func in tests:
        try:
            success, message = test_func()
            status = "PASSED" if success else "FAILED"

            results["test_results"].append(
                {
                    "test_name": test_name,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            if success:
                results["passed"] += 1
                print(f"✅ {test_name}: PASSED")
            else:
                results["failed"] += 1
                print(f"❌ {test_name}: FAILED - {message}")

        except Exception as e:
            results["failed"] += 1
            error_msg = f"Test exception: {str(e)}"
            results["test_results"].append(
                {
                    "test_name": test_name,
                    "status": "ERROR",
                    "message": error_msg,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            print(f"💥 {test_name}: ERROR - {error_msg}")

    # Determine overall status
    if results["failed"] == 0:
        results["overall_status"] = "PASSED"
        print(f"\n🎉 ALL TESTS PASSED ({results['passed']}/{results['total_tests']})")
    else:
        results["overall_status"] = "FAILED"
        print(
            f"\n🚨 TESTS FAILED ({results['failed']}/{results['total_tests']} failed)"
        )

    return results


if __name__ == "__main__":
    results = run_focused_test()

    # Save results to validation artifacts
    os.makedirs("validation_artifacts/3.1.1", exist_ok=True)
    with open("validation_artifacts/3.1.1/admin_auth_tests.json", "w") as f:
        json.dump(results, f, indent=2)

    print(
        f"\n📁 Test results saved to: validation_artifacts/3.1.1/admin_auth_tests.json"
    )

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)
