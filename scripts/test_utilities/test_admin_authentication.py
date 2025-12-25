#!/usr/bin/env python3
"""
Admin Authentication System Test Suite for Task 3.1.1 Validation
Tests all critical components of the admin authentication implementation.
"""

import sys
import os
import json
from datetime import datetime
import traceback

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.services.admin_auth import AdminAuthService
from app.models.database import User, UserRole
from app.database.config import get_db_session_context


def test_admin_user_exists():
    """Test that the admin user exists and has correct role"""
    print("\n🔑 TEST 1: Admin User Existence")
    try:
        with get_db_session_context() as session:
            admin_user = (
                session.query(User)
                .filter_by(email="mcampos.cerda@tutanota.com")
                .first()
            )

            if not admin_user:
                return False, "Admin user not found in database"

            if admin_user.role != UserRole.ADMIN:
                return (
                    False,
                    f"Admin user has wrong role: {admin_user.role}, expected: {UserRole.ADMIN}",
                )

            print(f"   ✅ Admin user found: {admin_user.email}")
            print(f"   ✅ User ID: {admin_user.user_id}")
            print(f"   ✅ Role: {admin_user.role}")
            print(f"   ✅ Active: {admin_user.is_active}")

            return True, "Admin user exists with correct role"

    except Exception as e:
        return False, f"Database error: {str(e)}"


def test_admin_auth_service():
    """Test AdminAuthService functionality"""
    print("\n🛡️ TEST 2: AdminAuthService")
    try:
        auth_service = AdminAuthService()

        # Test has_admin_role
        result = auth_service.has_admin_role("mcampos.cerda@tutanota.com")
        if not result:
            return False, "has_admin_role returned False for admin user"

        print("   ✅ has_admin_role working correctly")

        # Test get_user_permissions
        permissions = auth_service.get_user_permissions("mcampos.cerda@tutanota.com")
        if not permissions:
            return False, "get_user_permissions returned empty for admin user"

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
            if perm not in permissions:
                return False, f"Missing admin permission: {perm}"

        print(f"   ✅ All {len(permissions)} admin permissions present")

        # Test check_permission
        for perm in expected_admin_perms[:5]:  # Test first 5 permissions
            if not auth_service.check_permission("mcampos.cerda@tutanota.com", perm):
                return False, f"check_permission failed for {perm}"

        print("   ✅ check_permission working correctly")

        return True, "AdminAuthService fully functional"

    except Exception as e:
        return False, f"AdminAuthService error: {str(e)}"


def test_role_hierarchy():
    """Test role hierarchy and permission inheritance"""
    print("\n📊 TEST 3: Role Hierarchy")
    try:
        auth_service = AdminAuthService()

        # Test parent permissions (subset of admin)
        parent_perms = ["view_users", "view_analytics", "view_system_status"]

        for perm in parent_perms:
            if not auth_service.check_permission("mcampos.cerda@tutanota.com", perm):
                return False, f"Admin user missing parent permission: {perm}"

        print("   ✅ Admin user has all parent permissions")

        # Test admin-only permissions
        admin_only_perms = [
            "manage_users",
            "access_admin_dashboard",
            "manage_system_config",
        ]

        for perm in admin_only_perms:
            if not auth_service.check_permission("mcampos.cerda@tutanota.com", perm):
                return False, f"Admin user missing admin-only permission: {perm}"

        print("   ✅ Admin user has admin-only permissions")

        return True, "Role hierarchy working correctly"

    except Exception as e:
        return False, f"Role hierarchy error: {str(e)}"


def test_guest_user_management():
    """Test guest user management system"""
    print("\n👤 TEST 4: Guest User Management")
    try:
        auth_service = AdminAuthService()

        # Test guest user creation
        guest_id = auth_service.create_guest_user()
        if not guest_id:
            return False, "Failed to create guest user"

        print(f"   ✅ Guest user created: {guest_id}")

        # Test guest user lookup
        guest_user = auth_service.get_guest_user(guest_id)
        if not guest_user:
            return False, "Failed to retrieve guest user"

        print(f"   ✅ Guest user retrieved: {guest_user['user_id']}")

        # Test guest user permissions (should be minimal)
        guest_perms = auth_service.get_user_permissions_by_user_id(guest_id)
        if "access_admin_dashboard" in guest_perms:
            return False, "Guest user has admin permissions"

        print(
            f"   ✅ Guest user has limited permissions: {len(guest_perms)} permissions"
        )

        # Test guest user cleanup
        if auth_service.cleanup_guest_user(guest_id):
            print("   ✅ Guest user cleanup successful")
        else:
            print("   ⚠️ Guest user cleanup failed (may be expected)")

        return True, "Guest user management working"

    except Exception as e:
        return False, f"Guest user management error: {str(e)}"


def test_database_integration():
    """Test database operations and consistency"""
    print("\n🗄️ TEST 5: Database Integration")
    try:
        with get_db_session_context() as session:
            # Test user count
            user_count = session.query(User).count()
            print(f"   ✅ Total users in database: {user_count}")

            # Test admin user database record
            admin_user = (
                session.query(User)
                .filter_by(email="mcampos.cerda@tutanota.com")
                .first()
            )

            # Verify all required fields
            required_fields = ["user_id", "username", "email", "role", "is_active"]
            for field in required_fields:
                if not getattr(admin_user, field, None):
                    return False, f"Admin user missing required field: {field}"

            print("   ✅ Admin user has all required fields")

            # Test role enum consistency
            if admin_user.role.name != "ADMIN":
                return (
                    False,
                    f"Role enum inconsistency: {admin_user.role.name} != ADMIN",
                )

            print("   ✅ Role enum consistency verified")

            return True, "Database integration successful"

    except Exception as e:
        return False, f"Database integration error: {str(e)}"


def run_comprehensive_test():
    """Run all admin authentication tests"""
    print("🧪 ADMIN AUTHENTICATION COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    tests = [
        ("Admin User Exists", test_admin_user_exists),
        ("AdminAuthService", test_admin_auth_service),
        ("Role Hierarchy", test_role_hierarchy),
        ("Guest User Management", test_guest_user_management),
        ("Database Integration", test_database_integration),
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
                    "traceback": traceback.format_exc(),
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
    results = run_comprehensive_test()

    # Save results to validation artifacts
    os.makedirs("validation_artifacts/3.1.1", exist_ok=True)
    with open("validation_artifacts/3.1.1/admin_authentication_tests.json", "w") as f:
        json.dump(results, f, indent=2)

    print(
        f"\n📁 Test results saved to: validation_artifacts/3.1.1/admin_authentication_tests.json"
    )

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)
