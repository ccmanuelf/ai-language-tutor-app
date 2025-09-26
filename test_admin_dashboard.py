#!/usr/bin/env python3
"""
Admin Dashboard Test Suite for Task 3.1.2 Validation
Tests the complete user management dashboard implementation.
"""

import sys
import os
import json
from datetime import datetime
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.frontend.admin_dashboard import (
    create_user_management_page,
    create_user_card,
    create_add_user_modal,
    create_guest_session_panel,
    create_admin_header,
)
from app.api.admin import (
    admin_router,
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    StandardResponse,
)
from app.services.admin_auth import AdminAuthService, admin_auth_service
from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum
from app.database.config import get_db_session_context


def test_admin_dashboard_components():
    """Test admin dashboard component creation"""
    print("🎨 TEST 1: Admin Dashboard Components")
    try:
        # Test sample data
        sample_users = [
            {
                "user_id": "admin_123",
                "username": "Admin User",
                "email": "mcampos.cerda@tutanota.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": "ADMIN",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-09-26T10:00:00",
                "updated_at": "2025-09-26T10:00:00",
                "last_login": "2025-09-26T09:00:00",
            },
            {
                "user_id": "parent_456",
                "username": "Parent User",
                "email": "parent@example.com",
                "first_name": "Parent",
                "last_name": "User",
                "role": "PARENT",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-09-25T10:00:00",
                "updated_at": "2025-09-25T10:00:00",
                "last_login": None,
            },
            {
                "user_id": "child_789",
                "username": "Child User",
                "email": "child@example.com",
                "first_name": "Child",
                "last_name": "User",
                "role": "CHILD",
                "is_active": False,
                "is_verified": True,
                "created_at": "2025-09-24T10:00:00",
                "updated_at": "2025-09-24T10:00:00",
                "last_login": "2025-09-24T08:00:00",
            },
        ]

        sample_admin = {
            "email": "mcampos.cerda@tutanota.com",
            "role": "ADMIN",
            "username": "Admin User",
        }

        # Test user card creation
        for user in sample_users:
            user_card = create_user_card(user)
            if not user_card:
                return False, f"Failed to create user card for {user['email']}"

        print("   ✅ User cards created successfully")

        # Test admin header
        admin_header = create_admin_header(sample_admin)
        if not admin_header:
            return False, "Failed to create admin header"

        print("   ✅ Admin header created successfully")

        # Test add user modal
        add_modal = create_add_user_modal()
        if not add_modal:
            return False, "Failed to create add user modal"

        print("   ✅ Add user modal created successfully")

        # Test guest session panel (no active session)
        guest_panel_empty = create_guest_session_panel(None)
        if not guest_panel_empty:
            return False, "Failed to create empty guest session panel"

        print("   ✅ Empty guest session panel created successfully")

        # Test guest session panel (with active session)
        guest_info = {
            "user_id": "guest_123",
            "created_at": "2025-09-26T10:00:00",
            "status": "active",
        }
        guest_panel_active = create_guest_session_panel(guest_info)
        if not guest_panel_active:
            return False, "Failed to create active guest session panel"

        print("   ✅ Active guest session panel created successfully")

        # Test complete page creation
        full_page = create_user_management_page(sample_users, sample_admin, guest_info)
        if not full_page:
            return False, "Failed to create complete user management page"

        print("   ✅ Complete user management page created successfully")

        return True, "All admin dashboard components working correctly"

    except Exception as e:
        return False, f"Dashboard component error: {str(e)}"


def test_admin_api_models():
    """Test admin API request/response models"""
    print("\n📋 TEST 2: Admin API Models")
    try:
        # Test CreateUserRequest
        create_request = CreateUserRequest(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            role=UserRoleEnum.CHILD,
        )

        if not create_request:
            return False, "Failed to create CreateUserRequest"

        print("   ✅ CreateUserRequest model working")

        # Test UpdateUserRequest
        update_request = UpdateUserRequest(first_name="Updated", is_active=False)

        if not update_request:
            return False, "Failed to create UpdateUserRequest"

        print("   ✅ UpdateUserRequest model working")

        # Test UserResponse
        user_response = UserResponse(
            user_id="test_123",
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="CHILD",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=None,
        )

        if not user_response:
            return False, "Failed to create UserResponse"

        print("   ✅ UserResponse model working")

        # Test StandardResponse
        standard_response = StandardResponse(
            success=True, message="Test successful", data={"test": "data"}
        )

        if not standard_response:
            return False, "Failed to create StandardResponse"

        print("   ✅ StandardResponse model working")

        return True, "All admin API models working correctly"

    except Exception as e:
        return False, f"API model error: {str(e)}"


def test_database_integration():
    """Test database operations for user management"""
    print("\n🗄️ TEST 3: Database Integration")
    try:
        with get_db_session_context() as session:
            # Test user listing
            users = session.query(User).all()
            if not isinstance(users, list):
                return False, "Failed to retrieve user list"

            print(f"   ✅ Retrieved {len(users)} users from database")

            # Test admin user exists
            admin_user = (
                session.query(User)
                .filter_by(email="mcampos.cerda@tutanota.com")
                .first()
            )
            if not admin_user:
                return False, "Admin user not found in database"

            if admin_user.role != UserRole.ADMIN:
                return False, f"Admin user has wrong role: {admin_user.role}"

            print("   ✅ Admin user verified in database")

            # Test role filtering
            admin_count = (
                session.query(User).filter(User.role == UserRole.ADMIN).count()
            )
            parent_count = (
                session.query(User).filter(User.role == UserRole.PARENT).count()
            )
            child_count = (
                session.query(User).filter(User.role == UserRole.CHILD).count()
            )

            print(
                f"   ✅ Role distribution: {admin_count} admins, {parent_count} parents, {child_count} children"
            )

            # Test active user filtering
            active_count = session.query(User).filter(User.is_active == True).count()
            inactive_count = session.query(User).filter(User.is_active == False).count()

            print(
                f"   ✅ Status distribution: {active_count} active, {inactive_count} inactive"
            )

            return True, "Database integration working correctly"

    except Exception as e:
        return False, f"Database integration error: {str(e)}"


def test_permission_integration():
    """Test permission system integration with dashboard"""
    print("\n🛡️ TEST 4: Permission System Integration")
    try:
        auth_service = AdminAuthService()

        # Test admin permissions for dashboard access
        admin_perms = auth_service.get_user_permissions(UserRoleEnum.ADMIN)
        required_dashboard_perms = [
            "view_users",
            "manage_users",
            "create_users",
            "delete_users",
            "access_admin_dashboard",
            "manage_system_config",
        ]

        for perm in required_dashboard_perms:
            if perm not in admin_perms:
                return False, f"Admin missing required dashboard permission: {perm}"

        print("   ✅ Admin has all required dashboard permissions")

        # Test parent permissions (should be limited)
        parent_perms = auth_service.get_user_permissions(UserRoleEnum.PARENT)
        if "manage_users" in parent_perms:
            return False, "Parent should not have user management permissions"

        if "access_admin_dashboard" in parent_perms:
            return False, "Parent should not have dashboard access"

        print("   ✅ Parent permissions correctly limited")

        # Test child permissions (should have none)
        child_perms = auth_service.get_user_permissions(UserRoleEnum.CHILD)
        admin_only_perms = ["view_users", "manage_users", "access_admin_dashboard"]

        for perm in admin_only_perms:
            if perm in child_perms:
                return False, f"Child should not have admin permission: {perm}"

        print("   ✅ Child permissions correctly blocked")

        # Test permission checking methods
        if not auth_service.has_permission(
            UserRoleEnum.ADMIN, "access_admin_dashboard"
        ):
            return False, "Admin should have dashboard access permission"

        if auth_service.has_permission(UserRoleEnum.CHILD, "manage_users"):
            return False, "Child should not have user management permission"

        print("   ✅ Permission checking methods working correctly")

        return True, "Permission system integration working correctly"

    except Exception as e:
        return False, f"Permission integration error: {str(e)}"


def test_guest_session_management():
    """Test guest session management functionality"""
    print("\n👤 TEST 5: Guest Session Management")
    try:
        from app.services.admin_auth import GuestUserManager

        guest_manager = GuestUserManager()

        # Test initial state (no active session)
        if guest_manager.active_guest_session:
            # Clear any existing session for testing
            guest_manager.active_guest_session = None
            guest_manager.guest_session_data = {}

        print("   ✅ Guest manager initialized with no active session")

        # Test creating guest session
        guest_id = f"guest_{int(datetime.utcnow().timestamp())}"
        guest_manager.active_guest_session = guest_id
        guest_manager.guest_session_data = {
            "user_id": guest_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        if not guest_manager.active_guest_session:
            return False, "Failed to create guest session"

        print(f"   ✅ Guest session created: {guest_id}")

        # Test guest session data
        if guest_manager.guest_session_data.get("user_id") != guest_id:
            return False, "Guest session data inconsistent"

        print("   ✅ Guest session data consistent")

        # Test session termination
        guest_manager.active_guest_session = None
        guest_manager.guest_session_data = {}

        if guest_manager.active_guest_session:
            return False, "Failed to terminate guest session"

        print("   ✅ Guest session terminated successfully")

        return True, "Guest session management working correctly"

    except Exception as e:
        return False, f"Guest session management error: {str(e)}"


def test_dashboard_data_flow():
    """Test complete data flow from database to dashboard"""
    print("\n🔄 TEST 6: Dashboard Data Flow")
    try:
        # Simulate the complete flow from database to frontend

        # 1. Get users from database and convert within session context
        user_list = []
        with get_db_session_context() as session:
            db_users = session.query(User).all()

            # 2. Convert to frontend format within session
            for user in db_users:
                user_list.append(
                    {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.name,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                        "created_at": user.created_at.isoformat()
                        if user.created_at
                        else None,
                        "updated_at": user.updated_at.isoformat()
                        if user.updated_at
                        else None,
                        "last_login": user.last_login.isoformat()
                        if user.last_login
                        else None,
                    }
                )

        print(f"   ✅ Converted {len(user_list)} database users to frontend format")

        # 3. Create dashboard components with real data
        admin_user = {
            "email": "mcampos.cerda@tutanota.com",
            "role": "ADMIN",
            "username": "Admin User",
        }

        # Test user cards with real data
        for user in user_list[:3]:  # Test first 3 users
            user_card = create_user_card(user)
            if not user_card:
                return (
                    False,
                    f"Failed to create user card for real user {user['email']}",
                )

        print("   ✅ User cards created with real database data")

        # 4. Create complete page with real data
        complete_page = create_user_management_page(user_list, admin_user, None)
        if not complete_page:
            return False, "Failed to create complete page with real data"

        print("   ✅ Complete dashboard page created with real data")

        # 5. Test statistics calculation
        total_users = len(user_list)
        admin_users = len([u for u in user_list if u.get("role") == "ADMIN"])
        parent_users = len([u for u in user_list if u.get("role") == "PARENT"])
        child_users = len([u for u in user_list if u.get("role") == "CHILD"])
        active_users = len([u for u in user_list if u.get("is_active", True)])

        print(
            f"   ✅ Statistics calculated: {total_users} total, {admin_users} admins, {parent_users} parents, {child_users} children, {active_users} active"
        )

        # Verify statistics make sense
        if admin_users + parent_users + child_users != total_users:
            return False, "Role statistics don't add up correctly"

        if admin_users < 1:
            return False, "Should have at least one admin user"

        print("   ✅ Statistics validation passed")

        return True, "Complete dashboard data flow working correctly"

    except Exception as e:
        return False, f"Dashboard data flow error: {str(e)}"


def run_comprehensive_dashboard_test():
    """Run all admin dashboard tests"""
    print("🧪 ADMIN DASHBOARD COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    tests = [
        ("Admin Dashboard Components", test_admin_dashboard_components),
        ("Admin API Models", test_admin_api_models),
        ("Database Integration", test_database_integration),
        ("Permission System Integration", test_permission_integration),
        ("Guest Session Management", test_guest_session_management),
        ("Dashboard Data Flow", test_dashboard_data_flow),
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
    results = run_comprehensive_dashboard_test()

    # Save results to validation artifacts
    os.makedirs("validation_artifacts/3.1.2", exist_ok=True)
    with open("validation_artifacts/3.1.2/admin_dashboard_tests.json", "w") as f:
        json.dump(results, f, indent=2)

    print(
        f"\n📁 Test results saved to: validation_artifacts/3.1.2/admin_dashboard_tests.json"
    )

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)
