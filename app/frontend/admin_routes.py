"""
Admin Dashboard Route Handlers
AI Language Tutor App - Personal Family Educational Tool

This module provides FastHTML route handlers for the admin dashboard,
integrating with the admin authentication system and dashboard frontend.
"""

from fasthtml.common import *
from fastapi import HTTPException, Depends, status
from typing import Dict, List, Any, Optional
import logging
import json

from app.services.admin_auth import (
    admin_auth_service,
    require_admin_access,
    require_permission,
    AdminPermission,
)
from app.services.auth import get_current_user
from app.models.database import User, UserRole
from app.database.config import get_db_session_context
from app.frontend.admin_dashboard import create_user_management_page

logger = logging.getLogger(__name__)


def create_admin_routes(app):
    """Create admin dashboard routes for the FastHTML app"""

    @app.get("/dashboard/admin")
    async def admin_dashboard_redirect(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Redirect to user management (main admin page)"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            return RedirectResponse("/dashboard/admin/users", status_code=302)

        except Exception as e:
            logger.error(f"Error in admin dashboard redirect: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to access admin dashboard",
            )

    @app.get("/dashboard/admin/users")
    async def admin_users_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin user management page"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Get all users from database
            with get_db_session_context() as session:
                users = session.query(User).all()

                user_list = []
                for user in users:
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

            # Check for active guest session
            from app.services.admin_auth import GuestUserManager

            guest_manager = GuestUserManager()

            guest_info = None
            if guest_manager.active_guest_session:
                guest_info = {
                    "user_id": guest_manager.active_guest_session,
                    "created_at": guest_manager.guest_session_data.get(
                        "created_at", "Unknown"
                    ),
                    "status": "active",
                }

            # Create and return the page
            return create_user_management_page(user_list, current_user, guest_info)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin users page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load user management page",
            )

    @app.get("/dashboard/admin/languages")
    async def admin_languages_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin language configuration page (placeholder)"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # TODO: Implement language configuration page
            return Html(
                Head(
                    Title("Admin Dashboard - Language Configuration"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                ),
                Body(
                    H1("Language Configuration"),
                    P("Language configuration interface coming soon..."),
                    A(
                        "Back to Users",
                        href="/dashboard/admin/users",
                        style="color: #3b82f6; text-decoration: none;",
                    ),
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin languages page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load language configuration page",
            )

    @app.get("/dashboard/admin/features")
    async def admin_features_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin feature toggle page (placeholder)"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # TODO: Implement feature toggle page
            return Html(
                Head(
                    Title("Admin Dashboard - Feature Management"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                ),
                Body(
                    H1("Feature Management"),
                    P("Feature toggle interface coming soon..."),
                    A(
                        "Back to Users",
                        href="/dashboard/admin/users",
                        style="color: #3b82f6; text-decoration: none;",
                    ),
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin features page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load feature management page",
            )

    @app.get("/dashboard/admin/system")
    async def admin_system_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin system status page (placeholder)"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # TODO: Implement system status page
            return Html(
                Head(
                    Title("Admin Dashboard - System Status"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                ),
                Body(
                    H1("System Status"),
                    P("System monitoring interface coming soon..."),
                    A(
                        "Back to Users",
                        href="/dashboard/admin/users",
                        style="color: #3b82f6; text-decoration: none;",
                    ),
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin system page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load system status page",
            )


def register_admin_routes(app, admin_api_router):
    """Register admin routes and API endpoints with the FastHTML app"""

    # Register dashboard routes
    create_admin_routes(app)

    # Note: FastHTML apps don't use include_router like FastAPI
    # The admin API endpoints will be registered separately via the backend API

    logger.info("Admin dashboard routes registered successfully")
