"""
Admin Route Protection Middleware for AI Language Tutor App

This module provides comprehensive middleware for protecting admin routes
and enforcing permission-based access control.
"""

import logging
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.admin_auth import admin_auth_service, AdminPermission
from app.services.auth import auth_service
from app.models.database import UserRole

logger = logging.getLogger(__name__)


class AdminRouteMiddleware(BaseHTTPMiddleware):
    """Middleware for protecting admin routes"""

    def __init__(self, app, admin_routes_prefix: str = "/dashboard/admin"):
        super().__init__(app)
        self.admin_routes_prefix = admin_routes_prefix
        self.excluded_paths = [
            "/auth/login",
            "/auth/logout",
            "/auth/register",
            "/static",
            "/favicon.ico",
            "/health",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce admin access control"""

        # Skip middleware for non-admin routes
        if not self._is_admin_route(request.url.path):
            return await call_next(request)

        # Skip middleware for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        try:
            # Get current user from request
            current_user = await self._get_current_user(request)

            if not current_user:
                logger.warning(
                    f"Unauthorized access attempt to admin route: {request.url.path}"
                )
                return self._redirect_to_login(request)

            # Check if user has admin access
            if not admin_auth_service.is_admin_user(current_user):
                logger.warning(
                    f"Non-admin user {current_user.get('email')} attempted to access: {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check specific permission if required
            required_permission = self._get_required_permission(request.url.path)
            if required_permission:
                user_role = current_user.get("role")
                if isinstance(user_role, str):
                    # Convert string role to UserRole enum for permission check
                    user_role = UserRole(user_role)

                if not admin_auth_service.has_permission(
                    user_role, required_permission
                ):
                    logger.warning(
                        f"User {current_user.get('email')} lacks permission {required_permission} for: {request.url.path}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission required: {required_permission}",
                    )

            # Add current user to request state for route handlers
            request.state.current_user = current_user
            request.state.is_admin = True

            logger.debug(
                f"Admin access granted to {current_user.get('email')} for: {request.url.path}"
            )

            return await call_next(request)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Admin middleware error for {request.url.path}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error in admin access control",
            )

    def _is_admin_route(self, path: str) -> bool:
        """Check if the path is an admin route"""
        return path.startswith(self.admin_routes_prefix)

    def _is_excluded_path(self, path: str) -> bool:
        """Check if the path should be excluded from admin checks"""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    async def _get_current_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract current user from request"""
        try:
            # Try to get user from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                return auth_service.get_current_user_from_token(token)

            # Try to get user from session/cookies
            # This would need to be implemented based on your session management
            session_token = request.cookies.get("session_token")
            if session_token:
                return auth_service.get_current_user_from_token(session_token)

            return None

        except Exception as e:
            logger.error(f"Error extracting user from request: {e}")
            return None

    def _redirect_to_login(self, request: Request) -> RedirectResponse:
        """Redirect to login page with return URL"""
        login_url = "/auth/login"
        return_url = str(request.url)
        return RedirectResponse(
            url=f"{login_url}?next={return_url}", status_code=status.HTTP_302_FOUND
        )

    def _get_required_permission(self, path: str) -> Optional[str]:
        """Get required permission for specific admin routes"""
        permission_map = {
            "/dashboard/admin/users": AdminPermission.MANAGE_USERS,
            "/dashboard/admin/users/create": AdminPermission.CREATE_USERS,
            "/dashboard/admin/users/delete": AdminPermission.DELETE_USERS,
            "/dashboard/admin/languages": AdminPermission.MANAGE_LANGUAGES,
            "/dashboard/admin/features": AdminPermission.MANAGE_FEATURES,
            "/dashboard/admin/models": AdminPermission.MANAGE_AI_MODELS,
            "/dashboard/admin/scenarios": AdminPermission.MANAGE_SCENARIOS,
            "/dashboard/admin/system": AdminPermission.MANAGE_SYSTEM_CONFIG,
            "/dashboard/admin/analytics": AdminPermission.VIEW_ANALYTICS,
            "/dashboard/admin/backup": AdminPermission.BACKUP_SYSTEM,
            "/dashboard/admin/export": AdminPermission.EXPORT_DATA,
        }

        # Check for exact matches first
        if path in permission_map:
            return permission_map[path]

        # Check for prefix matches
        for route_prefix, permission in permission_map.items():
            if path.startswith(route_prefix):
                return permission

        # Default admin dashboard access
        return AdminPermission.ACCESS_ADMIN_DASHBOARD


class AdminPermissionChecker:
    """Utility class for checking admin permissions in route handlers"""

    @staticmethod
    def require_admin_permission(permission: str):
        """Decorator to require specific admin permission"""

        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract request from args (FastAPI dependency injection pattern)
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

                if not request:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Request object not found",
                    )

                current_user = getattr(request.state, "current_user", None)
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                    )

                user_role = current_user.get("role")
                if isinstance(user_role, str):
                    user_role = UserRole(user_role)

                if not admin_auth_service.has_permission(user_role, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission required: {permission}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def get_current_admin_user(request: Request) -> Dict[str, Any]:
        """Get current admin user from request state"""
        current_user = getattr(request.state, "current_user", None)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if not admin_auth_service.is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        return current_user


# Utility functions for FastHTML integration
def protect_admin_route(permission: str = None):
    """FastHTML route protection decorator"""

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            try:
                # Get current user
                current_user = await AdminRouteMiddleware(None)._get_current_user(
                    request
                )

                if not current_user:
                    return RedirectResponse(url="/auth/login", status_code=302)

                # Check admin access
                if not admin_auth_service.is_admin_user(current_user):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin access required",
                    )

                # Check specific permission
                if permission:
                    user_role = current_user.get("role")
                    if isinstance(user_role, str):
                        user_role = UserRole(user_role)

                    if not admin_auth_service.has_permission(user_role, permission):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Permission required: {permission}",
                        )

                # Add user to request
                request.state.current_user = current_user
                return await func(request, *args, **kwargs)

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Admin route protection error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error",
                )

        return wrapper

    return decorator


# Pre-configured decorators for common permissions
require_user_management = protect_admin_route(AdminPermission.MANAGE_USERS)
require_system_config = protect_admin_route(AdminPermission.MANAGE_SYSTEM_CONFIG)
require_analytics_access = protect_admin_route(AdminPermission.VIEW_ANALYTICS)
require_admin_dashboard = protect_admin_route(AdminPermission.ACCESS_ADMIN_DASHBOARD)
