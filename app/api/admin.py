"""
Admin API Endpoints for User Management Dashboard
AI Language Tutor App - Personal Family Educational Tool

This module provides RESTful API endpoints for admin operations including:
- User management (CRUD operations)
- Guest session management
- System configuration
- Analytics and reporting
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from app.services.admin_auth import (
    admin_auth_service,
    require_admin_access,
    require_permission,
    AdminPermission,
)
from app.services.auth import auth_service, hash_password
from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum
from app.database.config import get_db_session_context

logger = logging.getLogger(__name__)

# Initialize router
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


# Pydantic models for request/response
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: UserRoleEnum = UserRoleEnum.CHILD


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]


class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# User Management Endpoints
@admin_router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.VIEW_USERS)
    ),
):
    """Get list of all users (admin permission required)"""
    try:
        with get_db_session_context() as session:
            users = session.query(User).all()

            user_list = []
            for user in users:
                user_list.append(
                    UserResponse(
                        user_id=user.user_id,
                        username=user.username,
                        email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        role=user.role.name,
                        is_active=user.is_active,
                        is_verified=user.is_verified,
                        created_at=user.created_at,
                        updated_at=user.updated_at,
                        last_login=user.last_login,
                    )
                )

            return user_list

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        )


@admin_router.post("/users", response_model=StandardResponse)
async def create_user(
    user_data: CreateUserRequest,
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.CREATE_USERS)
    ),
):
    """Create a new user (admin permission required)"""
    try:
        with get_db_session_context() as session:
            # Check if user already exists
            existing_user = (
                session.query(User)
                .filter(
                    (User.email == user_data.email)
                    | (User.username == user_data.username)
                )
                .first()
            )

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email or username already exists",
                )

            # Convert role enum to database enum
            role_mapping = {
                UserRoleEnum.ADMIN: UserRole.ADMIN,
                UserRoleEnum.PARENT: UserRole.PARENT,
                UserRoleEnum.CHILD: UserRole.CHILD,
            }

            # Create new user
            new_user = User(
                user_id=f"user_{int(datetime.utcnow().timestamp())}",
                username=user_data.username,
                email=user_data.email,
                password_hash=hash_password(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=role_mapping[user_data.role],
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(new_user)
            # Context manager handles commit

            logger.info(
                f"Admin {current_user.get('email')} created user {user_data.email}"
            )

            return StandardResponse(
                success=True,
                message="User created successfully",
                data={"user_id": new_user.user_id},
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@admin_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.VIEW_USERS)
    ),
):
    """Get specific user details (admin permission required)"""
    try:
        with get_db_session_context() as session:
            user = session.query(User).filter(User.user_id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            return UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


@admin_router.put("/users/{user_id}", response_model=StandardResponse)
async def update_user(
    user_id: str,
    user_data: UpdateUserRequest,
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.MANAGE_USERS)
    ),
):
    """Update user details (admin permission required)"""
    try:
        with get_db_session_context() as session:
            user = session.query(User).filter(User.user_id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # Prevent admins from demoting themselves
            if (
                user.email == current_user.get("email")
                and user_data.role
                and user_data.role != UserRoleEnum.ADMIN
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot change your own admin role",
                )

            # Update fields if provided
            if user_data.username:
                # Check username uniqueness
                existing = (
                    session.query(User)
                    .filter(
                        User.username == user_data.username, User.user_id != user_id
                    )
                    .first()
                )
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already exists",
                    )
                user.username = user_data.username

            if user_data.email:
                # Check email uniqueness
                existing = (
                    session.query(User)
                    .filter(User.email == user_data.email, User.user_id != user_id)
                    .first()
                )
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists",
                    )
                user.email = user_data.email

            if user_data.first_name is not None:
                user.first_name = user_data.first_name

            if user_data.last_name is not None:
                user.last_name = user_data.last_name

            if user_data.role:
                role_mapping = {
                    UserRoleEnum.ADMIN: UserRole.ADMIN,
                    UserRoleEnum.PARENT: UserRole.PARENT,
                    UserRoleEnum.CHILD: UserRole.CHILD,
                }
                user.role = role_mapping[user_data.role]

            if user_data.is_active is not None:
                # Prevent admins from deactivating themselves
                if user.email == current_user.get("email") and not user_data.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot deactivate your own account",
                    )
                user.is_active = user_data.is_active

            user.updated_at = datetime.utcnow()
            # Context manager handles commit

            logger.info(f"Admin {current_user.get('email')} updated user {user.email}")

            return StandardResponse(success=True, message="User updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@admin_router.post("/users/{user_id}/toggle-status", response_model=StandardResponse)
async def toggle_user_status(
    user_id: str,
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.MANAGE_USERS)
    ),
):
    """Toggle user active/inactive status (admin permission required)"""
    try:
        with get_db_session_context() as session:
            user = session.query(User).filter(User.user_id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # Prevent admins from deactivating themselves
            if user.email == current_user.get("email") and user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate your own account",
                )

            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            # Context manager handles commit

            action = "activated" if user.is_active else "deactivated"
            logger.info(f"Admin {current_user.get('email')} {action} user {user.email}")

            return StandardResponse(success=True, message=f"User {action} successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling user status {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle user status",
        )


@admin_router.delete("/users/{user_id}", response_model=StandardResponse)
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.DELETE_USERS)
    ),
):
    """Delete user (admin permission required)"""
    try:
        with get_db_session_context() as session:
            user = session.query(User).filter(User.user_id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # Prevent admins from deleting themselves
            if user.email == current_user.get("email"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete your own account",
                )

            # Prevent deletion of admin users (extra safety)
            if user.role == UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete admin users",
                )

            session.delete(user)
            # Context manager handles commit

            logger.info(f"Admin {current_user.get('email')} deleted user {user.email}")

            return StandardResponse(success=True, message="User deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )


# Guest Session Management Endpoints
@admin_router.get("/guest-session", response_model=StandardResponse)
async def get_guest_session(
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.VIEW_SYSTEM_STATUS)
    ),
):
    """Get current guest session information"""
    try:
        # Check if there's an active guest session
        # This would integrate with the GuestUserManager
        from app.services.admin_auth import GuestUserManager

        guest_manager = GuestUserManager()

        if guest_manager.active_guest_session:
            return StandardResponse(
                success=True,
                message="Active guest session found",
                data={
                    "user_id": guest_manager.active_guest_session,
                    "session_data": guest_manager.guest_session_data,
                    "created_at": guest_manager.guest_session_data.get("created_at"),
                    "status": "active",
                },
            )
        else:
            return StandardResponse(
                success=True, message="No active guest session", data=None
            )

    except Exception as e:
        logger.error(f"Error getting guest session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve guest session information",
        )


@admin_router.post("/guest-session", response_model=StandardResponse)
async def create_guest_session(
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.MANAGE_SYSTEM_CONFIG)
    ),
):
    """Create a new guest session"""
    try:
        from app.services.admin_auth import GuestUserManager

        guest_manager = GuestUserManager()

        # Check if there's already an active session
        if guest_manager.active_guest_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Guest session already active. Terminate existing session first.",
            )

        # Create new guest session
        guest_id = f"guest_{int(datetime.utcnow().timestamp())}"
        guest_manager.active_guest_session = guest_id
        guest_manager.guest_session_data = {
            "user_id": guest_id,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": current_user.get("email"),
            "status": "active",
        }

        logger.info(
            f"Admin {current_user.get('email')} created guest session {guest_id}"
        )

        return StandardResponse(
            success=True,
            message="Guest session created successfully",
            data={"guest_id": guest_id},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating guest session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create guest session",
        )


@admin_router.delete("/guest-session", response_model=StandardResponse)
async def terminate_guest_session(
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.MANAGE_SYSTEM_CONFIG)
    ),
):
    """Terminate the current guest session"""
    try:
        from app.services.admin_auth import GuestUserManager

        guest_manager = GuestUserManager()

        if not guest_manager.active_guest_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active guest session to terminate",
            )

        guest_id = guest_manager.active_guest_session
        guest_manager.active_guest_session = None
        guest_manager.guest_session_data = {}

        logger.info(
            f"Admin {current_user.get('email')} terminated guest session {guest_id}"
        )

        return StandardResponse(
            success=True, message="Guest session terminated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating guest session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate guest session",
        )


# System Statistics Endpoint
@admin_router.get("/stats", response_model=StandardResponse)
async def get_system_stats(
    current_user: Dict[str, Any] = Depends(
        require_permission(AdminPermission.VIEW_ANALYTICS)
    ),
):
    """Get system statistics for admin dashboard"""
    try:
        with get_db_session_context() as session:
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.is_active == True).count()
            admin_users = (
                session.query(User).filter(User.role == UserRole.ADMIN).count()
            )
            parent_users = (
                session.query(User).filter(User.role == UserRole.PARENT).count()
            )
            child_users = (
                session.query(User).filter(User.role == UserRole.CHILD).count()
            )

            # Get recent users (last 7 days)
            from datetime import timedelta

            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_users = (
                session.query(User).filter(User.created_at >= seven_days_ago).count()
            )

            return StandardResponse(
                success=True,
                message="System statistics retrieved successfully",
                data={
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": total_users - active_users,
                    "admin_users": admin_users,
                    "parent_users": parent_users,
                    "child_users": child_users,
                    "recent_users": recent_users,
                    "last_updated": datetime.utcnow().isoformat(),
                },
            )

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics",
        )


# Include language configuration router
from app.api.language_config import router as language_config_router

admin_router.include_router(language_config_router)
