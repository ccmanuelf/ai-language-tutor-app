"""
Admin Authentication and Permission System for AI Language Tutor App

This module extends the base authentication system with admin-specific
functionality including:
- Enhanced role-based permission system
- Admin-only route protection
- Configuration access control
- Admin user management
"""

import logging
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, Request, status

from app.database.config import get_db_session_context
from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum
from app.services.auth import auth_service, get_current_user

logger = logging.getLogger(__name__)


class AdminPermission:
    """Admin permission definitions"""

    # User Management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    DELETE_USERS = "delete_users"

    # Configuration Management
    MANAGE_LANGUAGES = "manage_languages"
    MANAGE_FEATURES = "manage_features"
    MANAGE_AI_MODELS = "manage_ai_models"
    MANAGE_SCENARIOS = "manage_scenarios"

    # System Administration
    VIEW_SYSTEM_STATUS = "view_system_status"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    ACCESS_ADMIN_DASHBOARD = "access_admin_dashboard"

    # Data Management
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    BACKUP_SYSTEM = "backup_system"


class AdminAuthService:
    """Extended authentication service for admin operations"""

    def __init__(self):
        self.auth_service = auth_service
        self.admin_permissions = self._define_role_permissions()
        self._test_mode = False

    def _define_role_permissions(self) -> Dict[UserRoleEnum, List[str]]:
        """Define permissions for each role"""
        return {
            UserRoleEnum.CHILD: [
                # Children have no admin permissions
            ],
            UserRoleEnum.PARENT: [
                AdminPermission.VIEW_USERS,
                AdminPermission.VIEW_ANALYTICS,
                AdminPermission.VIEW_SYSTEM_STATUS,
            ],
            UserRoleEnum.ADMIN: [
                # ADMIN has all PARENT permissions plus configuration access
                AdminPermission.VIEW_USERS,
                AdminPermission.VIEW_ANALYTICS,
                AdminPermission.VIEW_SYSTEM_STATUS,
                # Plus admin-only permissions
                AdminPermission.MANAGE_USERS,
                AdminPermission.CREATE_USERS,
                AdminPermission.DELETE_USERS,
                AdminPermission.MANAGE_LANGUAGES,
                AdminPermission.MANAGE_FEATURES,
                AdminPermission.MANAGE_AI_MODELS,
                AdminPermission.MANAGE_SCENARIOS,
                AdminPermission.MANAGE_SYSTEM_CONFIG,
                AdminPermission.ACCESS_ADMIN_DASHBOARD,
                AdminPermission.EXPORT_DATA,
                AdminPermission.BACKUP_SYSTEM,
            ],
        }

    def has_permission(self, user_role: UserRoleEnum, permission: str) -> bool:
        """Check if user role has specific permission"""
        # In test mode, admin role has all permissions
        if self._test_mode and user_role == UserRoleEnum.ADMIN:
            return True

        role_permissions = self.admin_permissions.get(user_role, [])
        return permission in role_permissions

    def enable_test_mode(self):
        """Enable test mode - admin users bypass permission checks"""
        self._test_mode = True
        logger.debug("Admin auth test mode enabled")

    def disable_test_mode(self):
        """Disable test mode - normal permission checks"""
        self._test_mode = False
        logger.debug("Admin auth test mode disabled")

    def get_user_permissions(self, user_role: UserRoleEnum) -> List[str]:
        """Get all permissions for a user role"""
        return self.admin_permissions.get(user_role, [])

    def require_permission(self, permission: str):
        """Decorator factory to require specific permission"""

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract current user from dependencies
                current_user = kwargs.get("current_user")
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                    )

                user_role = UserRoleEnum(current_user.get("role"))
                if not self.has_permission(user_role, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required: {permission}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def upgrade_user_to_admin(self, user_email: str) -> bool:
        """Upgrade a user to admin role"""
        try:
            with get_db_session_context() as session:
                user = session.query(User).filter(User.email == user_email).first()
                if not user:
                    logger.error(f"User not found: {user_email}")
                    return False

                user.role = UserRole.ADMIN
                user.updated_at = datetime.now(timezone.utc)
                # Context manager handles commit/rollback automatically

                logger.info(f"Successfully upgraded user {user_email} to ADMIN role")
                return True

        except Exception as e:
            logger.error(f"Failed to upgrade user {user_email} to admin: {e}")
            return False

    def create_admin_user_if_not_exists(
        self, email: str, username: str, password: str
    ) -> bool:
        """Create admin user if it doesn't exist"""
        try:
            with get_db_session_context() as session:
                # Check if user already exists
                existing_user = session.query(User).filter(User.email == email).first()
                if existing_user:
                    # User exists, upgrade to admin if not already
                    if existing_user.role != UserRole.ADMIN:
                        existing_user.role = UserRole.ADMIN
                        existing_user.updated_at = datetime.now(timezone.utc)
                        # Context manager handles commit automatically
                        logger.info(f"Upgraded existing user {email} to ADMIN role")
                    return True

                # Create new admin user directly
                from app.services.auth import hash_password

                new_admin = User(
                    user_id=f"admin_{int(datetime.now(timezone.utc).timestamp())}",
                    username=username,
                    email=email,
                    password_hash=hash_password(password),
                    role=UserRole.ADMIN,
                    first_name="System",
                    last_name="Administrator",
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )

                session.add(new_admin)
                # Context manager will handle commit
                logger.info(f"Created new admin user: {email}")
                return True

        except Exception as e:
            logger.error(f"Failed to create/upgrade admin user {email}: {e}")
            return False

    def is_admin_user(self, user_data: Dict[str, Any]) -> bool:
        """Check if user has admin role"""
        user_role = user_data.get("role")
        return user_role == UserRole.ADMIN

    def is_parent_or_admin(self, user_data: Dict[str, Any]) -> bool:
        """Check if user has parent or admin role"""
        user_role = user_data.get("role")
        return user_role in [UserRole.PARENT, UserRole.ADMIN]


# Global admin authentication service
admin_auth_service = AdminAuthService()


# FastAPI Dependencies for Admin Authentication
async def require_admin_access(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """FastAPI dependency to require admin access"""
    if not admin_auth_service.is_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def require_parent_or_admin_access(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """FastAPI dependency to require parent or admin access"""
    if not admin_auth_service.is_parent_or_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent or Admin access required",
        )
    return current_user


async def require_admin_dashboard_access(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """FastAPI dependency for admin dashboard access"""
    user_role = UserRoleEnum(current_user.get("role"))
    if not admin_auth_service.has_permission(
        user_role, AdminPermission.ACCESS_ADMIN_DASHBOARD
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin dashboard access denied",
        )
    return current_user


def require_permission(permission: str):
    """FastAPI dependency factory for specific permissions"""

    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        user_role = UserRoleEnum(current_user.get("role"))
        if not admin_auth_service.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}",
            )
        return current_user

    return permission_checker


# Route Protection Decorators
def admin_required(func):
    """Decorator to require admin access for route functions"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This decorator assumes current_user is passed as kwarg
        current_user = kwargs.get("current_user")
        if not current_user or not admin_auth_service.is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )
        return await func(*args, **kwargs)

    return wrapper


def parent_or_admin_required(func):
    """Decorator to require parent or admin access for route functions"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if not current_user or not admin_auth_service.is_parent_or_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Parent or Admin access required",
            )
        return await func(*args, **kwargs)

    return wrapper


# Guest User Management
class GuestUserManager:
    """Manager for guest user sessions"""

    def __init__(self):
        self.active_guest_session: Optional[str] = None
        self.guest_session_data: Dict[str, Any] = {}

    def create_guest_session(
        self, session_id: str, device_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a guest session (only one allowed concurrently)"""
        if self.active_guest_session:
            logger.warning(f"Guest session already active: {self.active_guest_session}")
            return False

        self.active_guest_session = session_id
        self.guest_session_data = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc),
            "device_info": device_info or {},
            "is_active": True,
        }

        logger.info(f"Created guest session: {session_id}")
        return True

    def terminate_guest_session(self, session_id: Optional[str] = None) -> bool:
        """Terminate guest session"""
        if session_id and session_id != self.active_guest_session:
            return False

        if self.active_guest_session:
            logger.info(f"Terminated guest session: {self.active_guest_session}")
            self.active_guest_session = None
            self.guest_session_data = {}
            return True

        return False

    def is_guest_session_active(self) -> bool:
        """Check if guest session is active"""
        return self.active_guest_session is not None

    def get_guest_session_info(self) -> Optional[Dict[str, Any]]:
        """Get guest session information"""
        if self.active_guest_session:
            return self.guest_session_data.copy()
        return None


# Global guest user manager
guest_manager = GuestUserManager()


# Guest User Dependencies
async def allow_guest_access(request: Request) -> Dict[str, Any]:
    """Allow access for authenticated users or active guest session"""
    try:
        # Try to get authenticated user first
        from fastapi.security import HTTPBearer

        bearer = HTTPBearer(auto_error=False)
        credentials = await bearer(request)

        if credentials:
            # Regular authenticated user
            return auth_service.get_current_user_from_token(credentials.credentials)

        # Check for active guest session
        session_id = request.headers.get("X-Guest-Session-ID")
        if session_id and session_id == guest_manager.active_guest_session:
            return {
                "user_id": "guest",
                "username": "Guest User",
                "role": "guest",
                "session_id": session_id,
                "is_guest": True,
            }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required or guest session not found",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )


def block_guest_access(func):
    """Decorator to block guest users from accessing admin/config features"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if current_user and current_user.get("is_guest"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guest users cannot access configuration features",
            )
        return await func(*args, **kwargs)

    return wrapper


# Utility Functions
def initialize_admin_system():
    """Initialize admin system with default admin user"""
    admin_email = "mcampos.cerda@tutanota.com"
    admin_username = "Admin User"
    admin_password = "admin123"  # Should be changed on first login

    success = admin_auth_service.create_admin_user_if_not_exists(
        admin_email, admin_username, admin_password
    )

    if success:
        logger.info("Admin system initialized successfully")
    else:
        logger.error("Failed to initialize admin system")

    return success


def get_admin_user_info() -> Optional[Dict[str, Any]]:
    """Get admin user information"""
    try:
        with get_db_session_context() as session:
            admin_user = (
                session.query(User)
                .filter(User.email == "mcampos.cerda@tutanota.com")
                .first()
            )

            if admin_user:
                return {
                    "user_id": admin_user.user_id,
                    "username": admin_user.username,
                    "email": admin_user.email,
                    "role": admin_user.role,
                    "is_admin": admin_user.role == UserRole.ADMIN,
                    "created_at": admin_user.created_at,
                    "last_login": getattr(admin_user, "last_login", None),
                }
            return None

    except Exception as e:
        logger.error(f"Failed to get admin user info: {e}")
        return None


# FastAPI Dependencies
async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> User:
    """FastAPI dependency to get current admin user"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user_role = current_user.get("role")
    if user_role not in [UserRoleEnum.ADMIN, UserRoleEnum.PARENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Parent access required",
        )

    # Return user-like dict compatible with User model
    return current_user


def check_admin_permission(permission: str):
    """Decorator to check specific admin permission"""

    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args, current_user: Optional[Dict[str, Any]] = None, **kwargs
        ):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
                )

            user_role = current_user.get("role")
            if not admin_auth_service.has_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}",
                )

            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
