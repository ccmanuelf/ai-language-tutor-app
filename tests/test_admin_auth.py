"""
Comprehensive tests for app/services/admin_auth.py

Testing Strategy:
- AdminPermission class: All permission definitions
- AdminAuthService: Permission checking, role management, user operations
- FastAPI dependencies: require_admin_access, require_parent_or_admin_access, etc.
- Decorators: admin_required, parent_or_admin_required, block_guest_access
- GuestUserManager: Session creation, termination, validation
- Utility functions: initialize_admin_system, get_admin_user_info

Target: TRUE 100% coverage (214 statements, 66 branches)
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer

from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum
from app.services.admin_auth import (
    AdminAuthService,
    AdminPermission,
    GuestUserManager,
    admin_auth_service,
    admin_required,
    allow_guest_access,
    block_guest_access,
    check_admin_permission,
    get_admin_user_info,
    get_current_admin_user,
    guest_manager,
    initialize_admin_system,
    parent_or_admin_required,
    require_admin_access,
    require_admin_dashboard_access,
    require_parent_or_admin_access,
    require_permission,
)

# ===== Test Classes =====


class TestAdminPermission:
    """Test AdminPermission class definitions"""

    def test_user_management_permissions(self):
        """Test user management permission constants"""
        assert AdminPermission.MANAGE_USERS == "manage_users"
        assert AdminPermission.VIEW_USERS == "view_users"
        assert AdminPermission.CREATE_USERS == "create_users"
        assert AdminPermission.DELETE_USERS == "delete_users"

    def test_configuration_management_permissions(self):
        """Test configuration management permission constants"""
        assert AdminPermission.MANAGE_LANGUAGES == "manage_languages"
        assert AdminPermission.MANAGE_FEATURES == "manage_features"
        assert AdminPermission.MANAGE_AI_MODELS == "manage_ai_models"
        assert AdminPermission.MANAGE_SCENARIOS == "manage_scenarios"

    def test_system_administration_permissions(self):
        """Test system administration permission constants"""
        assert AdminPermission.VIEW_SYSTEM_STATUS == "view_system_status"
        assert AdminPermission.MANAGE_SYSTEM_CONFIG == "manage_system_config"
        assert AdminPermission.ACCESS_ADMIN_DASHBOARD == "access_admin_dashboard"

    def test_data_management_permissions(self):
        """Test data management permission constants"""
        assert AdminPermission.VIEW_ANALYTICS == "view_analytics"
        assert AdminPermission.EXPORT_DATA == "export_data"
        assert AdminPermission.BACKUP_SYSTEM == "backup_system"


class TestAdminAuthServiceInitialization:
    """Test AdminAuthService initialization"""

    def test_service_initialization(self):
        """Test AdminAuthService initializes correctly"""
        service = AdminAuthService()
        assert service.auth_service is not None
        assert isinstance(service.admin_permissions, dict)
        assert len(service.admin_permissions) == 3  # CHILD, PARENT, ADMIN

    def test_role_permissions_structure(self):
        """Test role permissions dictionary structure"""
        service = AdminAuthService()
        assert UserRoleEnum.CHILD in service.admin_permissions
        assert UserRoleEnum.PARENT in service.admin_permissions
        assert UserRoleEnum.ADMIN in service.admin_permissions

    def test_child_role_has_no_permissions(self):
        """Test CHILD role has no admin permissions"""
        service = AdminAuthService()
        child_permissions = service.admin_permissions[UserRoleEnum.CHILD]
        assert child_permissions == []

    def test_parent_role_permissions(self):
        """Test PARENT role has view permissions"""
        service = AdminAuthService()
        parent_permissions = service.admin_permissions[UserRoleEnum.PARENT]
        assert AdminPermission.VIEW_USERS in parent_permissions
        assert AdminPermission.VIEW_ANALYTICS in parent_permissions
        assert AdminPermission.VIEW_SYSTEM_STATUS in parent_permissions
        assert len(parent_permissions) == 3

    def test_admin_role_permissions(self):
        """Test ADMIN role has all permissions"""
        service = AdminAuthService()
        admin_permissions = service.admin_permissions[UserRoleEnum.ADMIN]

        # View permissions
        assert AdminPermission.VIEW_USERS in admin_permissions
        assert AdminPermission.VIEW_ANALYTICS in admin_permissions
        assert AdminPermission.VIEW_SYSTEM_STATUS in admin_permissions

        # Management permissions
        assert AdminPermission.MANAGE_USERS in admin_permissions
        assert AdminPermission.CREATE_USERS in admin_permissions
        assert AdminPermission.DELETE_USERS in admin_permissions
        assert AdminPermission.MANAGE_LANGUAGES in admin_permissions
        assert AdminPermission.MANAGE_FEATURES in admin_permissions
        assert AdminPermission.MANAGE_AI_MODELS in admin_permissions
        assert AdminPermission.MANAGE_SCENARIOS in admin_permissions
        assert AdminPermission.MANAGE_SYSTEM_CONFIG in admin_permissions
        assert AdminPermission.ACCESS_ADMIN_DASHBOARD in admin_permissions
        assert AdminPermission.EXPORT_DATA in admin_permissions
        assert AdminPermission.BACKUP_SYSTEM in admin_permissions

        # Total permissions
        assert len(admin_permissions) == 14


class TestAdminAuthServicePermissionChecking:
    """Test AdminAuthService permission checking methods"""

    def setup_method(self):
        """Setup test service"""
        self.service = AdminAuthService()

    def test_has_permission_child_no_permissions(self):
        """Test CHILD has no admin permissions"""
        assert not self.service.has_permission(
            UserRoleEnum.CHILD, AdminPermission.VIEW_USERS
        )
        assert not self.service.has_permission(
            UserRoleEnum.CHILD, AdminPermission.MANAGE_USERS
        )

    def test_has_permission_parent_view_permissions(self):
        """Test PARENT has view permissions"""
        assert self.service.has_permission(
            UserRoleEnum.PARENT, AdminPermission.VIEW_USERS
        )
        assert self.service.has_permission(
            UserRoleEnum.PARENT, AdminPermission.VIEW_ANALYTICS
        )

    def test_has_permission_parent_no_manage_permissions(self):
        """Test PARENT does not have management permissions"""
        assert not self.service.has_permission(
            UserRoleEnum.PARENT, AdminPermission.MANAGE_USERS
        )
        assert not self.service.has_permission(
            UserRoleEnum.PARENT, AdminPermission.DELETE_USERS
        )

    def test_has_permission_admin_all_permissions(self):
        """Test ADMIN has all permissions"""
        assert self.service.has_permission(
            UserRoleEnum.ADMIN, AdminPermission.VIEW_USERS
        )
        assert self.service.has_permission(
            UserRoleEnum.ADMIN, AdminPermission.MANAGE_USERS
        )
        assert self.service.has_permission(
            UserRoleEnum.ADMIN, AdminPermission.ACCESS_ADMIN_DASHBOARD
        )

    def test_has_permission_invalid_role(self):
        """Test has_permission with invalid role returns False"""
        # Create a mock role that doesn't exist in admin_permissions
        invalid_role = "invalid_role"
        assert not self.service.has_permission(invalid_role, AdminPermission.VIEW_USERS)

    def test_get_user_permissions_child(self):
        """Test get_user_permissions for CHILD"""
        permissions = self.service.get_user_permissions(UserRoleEnum.CHILD)
        assert permissions == []

    def test_get_user_permissions_parent(self):
        """Test get_user_permissions for PARENT"""
        permissions = self.service.get_user_permissions(UserRoleEnum.PARENT)
        assert len(permissions) == 3
        assert AdminPermission.VIEW_USERS in permissions

    def test_get_user_permissions_admin(self):
        """Test get_user_permissions for ADMIN"""
        permissions = self.service.get_user_permissions(UserRoleEnum.ADMIN)
        assert len(permissions) == 14
        assert AdminPermission.MANAGE_USERS in permissions

    def test_get_user_permissions_invalid_role(self):
        """Test get_user_permissions with invalid role"""
        permissions = self.service.get_user_permissions("invalid_role")
        assert permissions == []

    def test_enable_test_mode(self):
        """Test enabling test mode"""
        self.service.enable_test_mode()
        assert self.service._test_mode is True

    def test_disable_test_mode(self):
        """Test disabling test mode"""
        self.service.enable_test_mode()
        self.service.disable_test_mode()
        assert self.service._test_mode is False

    def test_has_permission_test_mode_admin_bypass(self):
        """Test admin users bypass permission checks in test mode"""
        self.service.enable_test_mode()

        # Admin should have access to ANY permission in test mode, even invalid ones
        assert (
            self.service.has_permission(UserRoleEnum.ADMIN, "non_existent_permission")
            is True
        )
        assert (
            self.service.has_permission(
                UserRoleEnum.ADMIN, AdminPermission.MANAGE_USERS
            )
            is True
        )

        self.service.disable_test_mode()

    def test_has_permission_test_mode_non_admin_normal(self):
        """Test non-admin users still follow normal permission checks in test mode"""
        self.service.enable_test_mode()

        # Child and Parent still follow normal permission checks in test mode
        assert (
            self.service.has_permission(
                UserRoleEnum.CHILD, AdminPermission.MANAGE_USERS
            )
            is False
        )
        assert (
            self.service.has_permission(
                UserRoleEnum.PARENT, AdminPermission.MANAGE_USERS
            )
            is False
        )

        self.service.disable_test_mode()


class TestAdminAuthServiceRequirePermissionDecorator:
    """Test require_permission decorator factory"""

    def setup_method(self):
        """Setup test service"""
        self.service = AdminAuthService()

    @pytest.mark.asyncio
    async def test_require_permission_success(self):
        """Test require_permission decorator allows access with permission"""
        decorator = self.service.require_permission(AdminPermission.VIEW_USERS)

        @decorator
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"role": UserRoleEnum.ADMIN})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_require_permission_no_user(self):
        """Test require_permission decorator raises 401 without user"""
        decorator = self.service.require_permission(AdminPermission.VIEW_USERS)

        @decorator
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user=None)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_permission_insufficient_permissions(self):
        """Test require_permission decorator raises 403 without permission"""
        decorator = self.service.require_permission(AdminPermission.MANAGE_USERS)

        @decorator
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user={"role": UserRoleEnum.CHILD})

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail


class TestAdminAuthServiceUserManagement:
    """Test user upgrade and admin creation functions"""

    def setup_method(self):
        """Setup test service"""
        self.service = AdminAuthService()

    @patch("app.services.admin_auth.get_db_session_context")
    def test_upgrade_user_to_admin_success(self, mock_context):
        """Test successful user upgrade to admin"""
        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.PARENT

        # Setup mock session
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_context.return_value.__enter__.return_value = mock_session

        result = self.service.upgrade_user_to_admin("test@example.com")

        assert result is True
        assert mock_user.role == UserRole.ADMIN
        assert hasattr(mock_user, "updated_at")

    @patch("app.services.admin_auth.get_db_session_context")
    def test_upgrade_user_to_admin_user_not_found(self, mock_context):
        """Test upgrade user when user doesn't exist"""
        # Setup mock session returning None
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session

        result = self.service.upgrade_user_to_admin("nonexistent@example.com")

        assert result is False

    @patch("app.services.admin_auth.get_db_session_context")
    def test_upgrade_user_to_admin_exception(self, mock_context):
        """Test upgrade user handles exceptions"""
        mock_context.side_effect = Exception("Database error")

        result = self.service.upgrade_user_to_admin("test@example.com")

        assert result is False

    @patch("app.services.auth.hash_password")
    @patch("app.services.admin_auth.get_db_session_context")
    def test_create_admin_user_new_user(self, mock_context, mock_hash):
        """Test creating new admin user"""
        # Setup mocks
        mock_hash.return_value = "hashed_password"
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session

        result = self.service.create_admin_user_if_not_exists(
            "admin@example.com", "Admin", "password123"
        )

        assert result is True
        mock_session.add.assert_called_once()

    @patch("app.services.admin_auth.get_db_session_context")
    def test_create_admin_user_existing_admin(self, mock_context):
        """Test creating admin when user already exists as admin"""
        # Create mock existing admin user
        mock_user = Mock(spec=User)
        mock_user.email = "admin@example.com"
        mock_user.role = UserRole.ADMIN

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_context.return_value.__enter__.return_value = mock_session

        result = self.service.create_admin_user_if_not_exists(
            "admin@example.com", "Admin", "password123"
        )

        assert result is True
        # Should not call add since user exists
        mock_session.add.assert_not_called()

    @patch("app.services.admin_auth.get_db_session_context")
    def test_create_admin_user_upgrade_existing_non_admin(self, mock_context):
        """Test creating admin upgrades existing non-admin user"""
        # Create mock existing non-admin user
        mock_user = Mock(spec=User)
        mock_user.email = "user@example.com"
        mock_user.role = UserRole.PARENT

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_context.return_value.__enter__.return_value = mock_session

        result = self.service.create_admin_user_if_not_exists(
            "user@example.com", "User", "password123"
        )

        assert result is True
        assert mock_user.role == UserRole.ADMIN
        assert hasattr(mock_user, "updated_at")

    @patch("app.services.admin_auth.get_db_session_context")
    def test_create_admin_user_exception(self, mock_context):
        """Test create admin user handles exceptions"""
        mock_context.side_effect = Exception("Database error")

        result = self.service.create_admin_user_if_not_exists(
            "admin@example.com", "Admin", "password123"
        )

        assert result is False

    def test_is_admin_user_true(self):
        """Test is_admin_user returns True for admin"""
        user_data = {"role": UserRole.ADMIN}
        assert self.service.is_admin_user(user_data) is True

    def test_is_admin_user_false(self):
        """Test is_admin_user returns False for non-admin"""
        user_data = {"role": UserRole.PARENT}
        assert self.service.is_admin_user(user_data) is False

    def test_is_parent_or_admin_parent(self):
        """Test is_parent_or_admin returns True for parent"""
        user_data = {"role": UserRole.PARENT}
        assert self.service.is_parent_or_admin(user_data) is True

    def test_is_parent_or_admin_admin(self):
        """Test is_parent_or_admin returns True for admin"""
        user_data = {"role": UserRole.ADMIN}
        assert self.service.is_parent_or_admin(user_data) is True

    def test_is_parent_or_admin_child(self):
        """Test is_parent_or_admin returns False for child"""
        user_data = {"role": UserRole.CHILD}
        assert self.service.is_parent_or_admin(user_data) is False


class TestFastAPIDependencies:
    """Test FastAPI dependency functions"""

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_admin_access_success(self, mock_get_user):
        """Test require_admin_access allows admin users"""
        mock_user = {"role": UserRole.ADMIN, "user_id": "admin123"}
        mock_get_user.return_value = mock_user

        result = await require_admin_access(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_admin_access_forbidden(self, mock_get_user):
        """Test require_admin_access denies non-admin users"""
        mock_user = {"role": UserRole.PARENT, "user_id": "parent123"}

        with pytest.raises(HTTPException) as exc_info:
            await require_admin_access(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_parent_or_admin_access_parent(self, mock_get_user):
        """Test require_parent_or_admin_access allows parent users"""
        mock_user = {"role": UserRole.PARENT, "user_id": "parent123"}

        result = await require_parent_or_admin_access(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_parent_or_admin_access_admin(self, mock_get_user):
        """Test require_parent_or_admin_access allows admin users"""
        mock_user = {"role": UserRole.ADMIN, "user_id": "admin123"}

        result = await require_parent_or_admin_access(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_parent_or_admin_access_forbidden(self, mock_get_user):
        """Test require_parent_or_admin_access denies child users"""
        mock_user = {"role": UserRole.CHILD, "user_id": "child123"}

        with pytest.raises(HTTPException) as exc_info:
            await require_parent_or_admin_access(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "Parent or Admin access required" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_admin_dashboard_access_success(self, mock_get_user):
        """Test require_admin_dashboard_access allows users with permission"""
        mock_user = {"role": UserRoleEnum.ADMIN, "user_id": "admin123"}

        result = await require_admin_dashboard_access(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_admin_dashboard_access_forbidden(self, mock_get_user):
        """Test require_admin_dashboard_access denies users without permission"""
        mock_user = {"role": UserRoleEnum.CHILD, "user_id": "child123"}

        with pytest.raises(HTTPException) as exc_info:
            await require_admin_dashboard_access(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "Admin dashboard access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_permission_dependency_success(self, mock_get_user):
        """Test require_permission dependency factory allows access with permission"""
        mock_user = {"role": UserRoleEnum.ADMIN, "user_id": "admin123"}

        permission_checker = require_permission(AdminPermission.MANAGE_USERS)
        result = await permission_checker(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_require_permission_dependency_forbidden(self, mock_get_user):
        """Test require_permission dependency factory denies access without permission"""
        mock_user = {"role": UserRoleEnum.CHILD, "user_id": "child123"}

        permission_checker = require_permission(AdminPermission.MANAGE_USERS)

        with pytest.raises(HTTPException) as exc_info:
            await permission_checker(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "Permission required" in exc_info.value.detail


class TestRouteProtectionDecorators:
    """Test route protection decorators"""

    @pytest.mark.asyncio
    async def test_admin_required_success(self):
        """Test admin_required decorator allows admin users"""

        @admin_required
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"role": UserRole.ADMIN})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_admin_required_no_user(self):
        """Test admin_required decorator denies without user"""

        @admin_required
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user=None)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_admin_required_non_admin(self):
        """Test admin_required decorator denies non-admin users"""

        @admin_required
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user={"role": UserRole.PARENT})

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_parent_or_admin_required_parent(self):
        """Test parent_or_admin_required allows parent users"""

        @parent_or_admin_required
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"role": UserRole.PARENT})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_parent_or_admin_required_admin(self):
        """Test parent_or_admin_required allows admin users"""

        @parent_or_admin_required
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"role": UserRole.ADMIN})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_parent_or_admin_required_no_user(self):
        """Test parent_or_admin_required denies without user"""

        @parent_or_admin_required
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user=None)

        assert exc_info.value.status_code == 403
        assert "Parent or Admin access required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_parent_or_admin_required_child(self):
        """Test parent_or_admin_required denies child users"""

        @parent_or_admin_required
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user={"role": UserRole.CHILD})

        assert exc_info.value.status_code == 403


class TestGuestUserManager:
    """Test GuestUserManager functionality"""

    def setup_method(self):
        """Setup fresh GuestUserManager for each test"""
        self.manager = GuestUserManager()

    def test_manager_initialization(self):
        """Test GuestUserManager initializes correctly"""
        assert self.manager.active_guest_session is None
        assert self.manager.guest_session_data == {}

    def test_create_guest_session_success(self):
        """Test creating guest session successfully"""
        result = self.manager.create_guest_session("session_123", {"device": "mobile"})

        assert result is True
        assert self.manager.active_guest_session == "session_123"
        assert self.manager.guest_session_data["session_id"] == "session_123"
        assert self.manager.guest_session_data["device_info"] == {"device": "mobile"}
        assert self.manager.guest_session_data["is_active"] is True

    def test_create_guest_session_without_device_info(self):
        """Test creating guest session without device info"""
        result = self.manager.create_guest_session("session_456")

        assert result is True
        assert self.manager.guest_session_data["device_info"] == {}

    def test_create_guest_session_already_active(self):
        """Test creating guest session when one already exists"""
        self.manager.create_guest_session("session_123")
        result = self.manager.create_guest_session("session_456")

        assert result is False
        assert self.manager.active_guest_session == "session_123"  # Unchanged

    def test_terminate_guest_session_success(self):
        """Test terminating active guest session"""
        self.manager.create_guest_session("session_123")
        result = self.manager.terminate_guest_session("session_123")

        assert result is True
        assert self.manager.active_guest_session is None
        assert self.manager.guest_session_data == {}

    def test_terminate_guest_session_without_id(self):
        """Test terminating guest session without providing session_id"""
        self.manager.create_guest_session("session_123")
        result = self.manager.terminate_guest_session()

        assert result is True
        assert self.manager.active_guest_session is None

    def test_terminate_guest_session_wrong_id(self):
        """Test terminating guest session with wrong session_id"""
        self.manager.create_guest_session("session_123")
        result = self.manager.terminate_guest_session("wrong_session")

        assert result is False
        assert self.manager.active_guest_session == "session_123"  # Unchanged

    def test_terminate_guest_session_no_active_session(self):
        """Test terminating when no session is active"""
        result = self.manager.terminate_guest_session("session_123")

        assert result is False

    def test_terminate_guest_session_no_active_session_no_id(self):
        """Test terminating without session_id when no session is active"""
        result = self.manager.terminate_guest_session()

        assert result is False

    def test_is_guest_session_active_true(self):
        """Test is_guest_session_active returns True when active"""
        self.manager.create_guest_session("session_123")
        assert self.manager.is_guest_session_active() is True

    def test_is_guest_session_active_false(self):
        """Test is_guest_session_active returns False when not active"""
        assert self.manager.is_guest_session_active() is False

    def test_get_guest_session_info_active(self):
        """Test get_guest_session_info returns data when active"""
        self.manager.create_guest_session("session_123", {"device": "tablet"})
        info = self.manager.get_guest_session_info()

        assert info is not None
        assert info["session_id"] == "session_123"
        assert info["device_info"] == {"device": "tablet"}
        assert "created_at" in info

    def test_get_guest_session_info_not_active(self):
        """Test get_guest_session_info returns None when not active"""
        info = self.manager.get_guest_session_info()
        assert info is None


class TestGuestAccessDependency:
    """Test allow_guest_access dependency"""

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.auth_service")
    async def test_allow_guest_access_authenticated_user(self, mock_auth_service):
        """Test allow_guest_access with authenticated user"""
        mock_request = Mock(spec=Request)
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_token"

        mock_user = {"user_id": "user123", "username": "testuser", "role": "parent"}
        mock_auth_service.get_current_user_from_token.return_value = mock_user

        with patch("fastapi.security.HTTPBearer") as mock_bearer:
            mock_bearer_instance = AsyncMock()
            mock_bearer_instance.return_value = mock_credentials
            mock_bearer.return_value = mock_bearer_instance

            result = await allow_guest_access(mock_request)

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_allow_guest_access_guest_session(self):
        """Test allow_guest_access with active guest session"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "guest_session_123"

        # Setup guest manager with active session
        guest_manager.create_guest_session("guest_session_123")

        with patch("fastapi.security.HTTPBearer") as mock_bearer:
            mock_bearer_instance = AsyncMock()
            mock_bearer_instance.return_value = None  # No credentials
            mock_bearer.return_value = mock_bearer_instance

            result = await allow_guest_access(mock_request)

            assert result["user_id"] == "guest"
            assert result["username"] == "Guest User"
            assert result["role"] == "guest"
            assert result["is_guest"] is True

        # Cleanup
        guest_manager.terminate_guest_session()

    @pytest.mark.asyncio
    async def test_allow_guest_access_no_auth(self):
        """Test allow_guest_access without authentication or guest session"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = None

        with patch("fastapi.security.HTTPBearer") as mock_bearer:
            mock_bearer_instance = AsyncMock()
            mock_bearer_instance.return_value = None
            mock_bearer.return_value = mock_bearer_instance

            with pytest.raises(HTTPException) as exc_info:
                await allow_guest_access(mock_request)

            assert exc_info.value.status_code == 401
            assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_allow_guest_access_wrong_guest_session(self):
        """Test allow_guest_access with wrong guest session ID"""
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "wrong_session"

        # Setup guest manager with different session
        guest_manager.create_guest_session("correct_session_123")

        with patch("fastapi.security.HTTPBearer") as mock_bearer:
            mock_bearer_instance = AsyncMock()
            mock_bearer_instance.return_value = None
            mock_bearer.return_value = mock_bearer_instance

            with pytest.raises(HTTPException) as exc_info:
                await allow_guest_access(mock_request)

            assert exc_info.value.status_code == 401

        # Cleanup
        guest_manager.terminate_guest_session()

    @pytest.mark.asyncio
    async def test_allow_guest_access_exception_handling(self):
        """Test allow_guest_access handles exceptions"""
        mock_request = Mock(spec=Request)

        with patch("fastapi.security.HTTPBearer") as mock_bearer:
            mock_bearer.side_effect = Exception("Unexpected error")

            with pytest.raises(HTTPException) as exc_info:
                await allow_guest_access(mock_request)

            assert exc_info.value.status_code == 401
            assert "Authentication failed" in exc_info.value.detail


class TestBlockGuestAccessDecorator:
    """Test block_guest_access decorator"""

    @pytest.mark.asyncio
    async def test_block_guest_access_allows_regular_user(self):
        """Test block_guest_access allows regular users"""

        @block_guest_access
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"user_id": "user123", "is_guest": False})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_block_guest_access_allows_user_without_is_guest(self):
        """Test block_guest_access allows users without is_guest flag"""

        @block_guest_access
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"user_id": "user123"})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_block_guest_access_blocks_guest_user(self):
        """Test block_guest_access blocks guest users"""

        @block_guest_access
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user={"user_id": "guest", "is_guest": True})

        assert exc_info.value.status_code == 403
        assert (
            "Guest users cannot access configuration features" in exc_info.value.detail
        )


class TestUtilityFunctions:
    """Test utility functions"""

    @patch("app.services.admin_auth.admin_auth_service.create_admin_user_if_not_exists")
    def test_initialize_admin_system_success(self, mock_create_admin):
        """Test initialize_admin_system succeeds"""
        mock_create_admin.return_value = True

        result = initialize_admin_system()

        assert result is True
        mock_create_admin.assert_called_once_with(
            "mcampos.cerda@tutanota.com", "Admin User", "admin123"
        )

    @patch("app.services.admin_auth.admin_auth_service.create_admin_user_if_not_exists")
    def test_initialize_admin_system_failure(self, mock_create_admin):
        """Test initialize_admin_system handles failure"""
        mock_create_admin.return_value = False

        result = initialize_admin_system()

        assert result is False

    @patch("app.services.admin_auth.get_db_session_context")
    def test_get_admin_user_info_success(self, mock_context):
        """Test get_admin_user_info returns admin info"""
        mock_user = Mock(spec=User)
        mock_user.user_id = "admin123"
        mock_user.username = "Admin User"
        mock_user.email = "mcampos.cerda@tutanota.com"
        mock_user.role = UserRole.ADMIN
        mock_user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_user.last_login = datetime(2024, 1, 15, tzinfo=timezone.utc)

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_context.return_value.__enter__.return_value = mock_session

        result = get_admin_user_info()

        assert result is not None
        assert result["user_id"] == "admin123"
        assert result["username"] == "Admin User"
        assert result["email"] == "mcampos.cerda@tutanota.com"
        assert result["role"] == UserRole.ADMIN
        assert result["is_admin"] is True

    @patch("app.services.admin_auth.get_db_session_context")
    def test_get_admin_user_info_user_not_found(self, mock_context):
        """Test get_admin_user_info returns None when user not found"""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session

        result = get_admin_user_info()

        assert result is None

    @patch("app.services.admin_auth.get_db_session_context")
    def test_get_admin_user_info_no_last_login(self, mock_context):
        """Test get_admin_user_info when last_login attribute doesn't exist"""
        # Create a mock user without last_login attribute
        mock_user = MagicMock(
            spec=["user_id", "username", "email", "role", "created_at"]
        )
        mock_user.user_id = "admin123"
        mock_user.username = "Admin User"
        mock_user.email = "mcampos.cerda@tutanota.com"
        mock_user.role = UserRole.ADMIN
        mock_user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_context.return_value.__enter__.return_value = mock_session

        result = get_admin_user_info()

        assert result is not None
        assert result["last_login"] is None

    @patch("app.services.admin_auth.get_db_session_context")
    def test_get_admin_user_info_exception(self, mock_context):
        """Test get_admin_user_info handles exceptions"""
        mock_context.side_effect = Exception("Database error")

        result = get_admin_user_info()

        assert result is None

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_get_current_admin_user_admin(self, mock_get_user):
        """Test get_current_admin_user returns admin user"""
        mock_user = {"user_id": "admin123", "role": UserRoleEnum.ADMIN}

        result = await get_current_admin_user(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_get_current_admin_user_parent(self, mock_get_user):
        """Test get_current_admin_user returns parent user"""
        mock_user = {"user_id": "parent123", "role": UserRoleEnum.PARENT}

        result = await get_current_admin_user(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_get_current_admin_user_no_user(self, mock_get_user):
        """Test get_current_admin_user raises 401 without user"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(current_user=None)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.get_current_user")
    async def test_get_current_admin_user_child(self, mock_get_user):
        """Test get_current_admin_user raises 403 for child users"""
        mock_user = {"user_id": "child123", "role": UserRoleEnum.CHILD}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "Admin or Parent access required" in exc_info.value.detail


class TestCheckAdminPermissionDecorator:
    """Test check_admin_permission decorator"""

    @pytest.mark.asyncio
    async def test_check_admin_permission_success(self):
        """Test check_admin_permission allows access with permission"""

        @check_admin_permission(AdminPermission.MANAGE_USERS)
        async def test_func(current_user=None):
            return "Success"

        result = await test_func(current_user={"role": UserRoleEnum.ADMIN})
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_check_admin_permission_no_user(self):
        """Test check_admin_permission raises 401 without user"""

        @check_admin_permission(AdminPermission.MANAGE_USERS)
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user=None)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_check_admin_permission_insufficient_permissions(self):
        """Test check_admin_permission raises 403 without permission"""

        @check_admin_permission(AdminPermission.MANAGE_USERS)
        async def test_func(current_user=None):
            return "Success"

        with pytest.raises(HTTPException) as exc_info:
            await test_func(current_user={"role": UserRoleEnum.CHILD})

        assert exc_info.value.status_code == 403
        assert "Permission denied" in exc_info.value.detail


class TestGlobalInstances:
    """Test global instance singletons"""

    def test_admin_auth_service_singleton(self):
        """Test admin_auth_service is AdminAuthService instance"""
        assert isinstance(admin_auth_service, AdminAuthService)

    def test_guest_manager_singleton(self):
        """Test guest_manager is GuestUserManager instance"""
        assert isinstance(guest_manager, GuestUserManager)


# ===== Summary =====
# Total Test Classes: 14
# Estimated Tests: ~100+ comprehensive tests
# Coverage Target: TRUE 100% (214 statements, 66 branches)
# Focus Areas:
# - AdminPermission definitions ✅
# - AdminAuthService permission system ✅
# - User management (upgrade, create admin) ✅
# - FastAPI dependencies ✅
# - Route protection decorators ✅
# - GuestUserManager session handling ✅
# - Guest access control ✅
# - Utility functions ✅
# - Global instances ✅
