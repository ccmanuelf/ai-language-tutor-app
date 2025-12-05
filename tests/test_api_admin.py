"""
Comprehensive Test Suite for Admin API Endpoints
app/api/admin.py

Target: TRUE 100% coverage (statements + branches + zero warnings)
Session: 85
Module: app/api/admin.py (238 statements, 92 branches)

Test Coverage:
- Helper Functions (6 functions)
- API Endpoints (9 endpoints)
- Pydantic Models (4 models)
- Error Handling (all exception paths)
- Edge Cases (defensive code paths)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, status
from pydantic import ValidationError

# Import module functions directly for coverage measurement
from app.api.admin import (
    CreateUserRequest,
    StandardResponse,
    UpdateUserRequest,
    UserResponse,
    _check_email_uniqueness,
    _check_username_uniqueness,
    _get_user_or_404,
    _update_user_fields,
    _update_user_role,
    _validate_self_deactivation,
    _validate_self_modification,
    admin_router,
    create_guest_session,
    create_user,
    delete_user,
    get_guest_session,
    get_system_stats,
    get_user,
    list_users,
    terminate_guest_session,
    toggle_user_status,
    update_user,
)
from app.models.database import User, UserRole
from app.models.schemas import UserRoleEnum

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_session():
    """Create a mock database session"""
    session = MagicMock()
    return session


@pytest.fixture
def sample_user():
    """Create a sample user object"""
    user = User(
        user_id="user_123",
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role=UserRole.CHILD,
        is_active=True,
        is_verified=True,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_login=datetime(2024, 1, 15, tzinfo=timezone.utc),
    )
    return user


@pytest.fixture
def sample_admin_user():
    """Create a sample admin user object"""
    user = User(
        user_id="admin_123",
        username="adminuser",
        email="admin@example.com",
        password_hash="hashed_password",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_login=datetime(2024, 1, 15, tzinfo=timezone.utc),
    )
    return user


@pytest.fixture
def current_user_dict():
    """Create a current user dictionary for permission checks"""
    return {
        "user_id": "admin_123",
        "email": "admin@example.com",
        "role": "ADMIN",
    }


@pytest.fixture
def create_user_request_data():
    """Sample CreateUserRequest data"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "securepassword123",
        "role": UserRoleEnum.CHILD,
    }


@pytest.fixture
def update_user_request_data():
    """Sample UpdateUserRequest data"""
    return {
        "username": "updateduser",
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "Name",
        "role": UserRoleEnum.PARENT,
        "is_active": True,
    }


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================


class TestPydanticModels:
    """Test Pydantic model validation"""

    def test_create_user_request_valid(self, create_user_request_data):
        """Test CreateUserRequest with valid data"""
        request = CreateUserRequest(**create_user_request_data)
        assert request.username == "newuser"
        assert request.email == "newuser@example.com"
        assert request.first_name == "New"
        assert request.last_name == "User"
        assert request.password == "securepassword123"
        assert request.role == UserRoleEnum.CHILD

    def test_create_user_request_default_role(self):
        """Test CreateUserRequest default role is CHILD"""
        request = CreateUserRequest(
            username="user",
            email="user@example.com",
            first_name="First",
            last_name="Last",
            password="password123",
        )
        assert request.role == UserRoleEnum.CHILD

    def test_create_user_request_invalid_email(self):
        """Test CreateUserRequest with invalid email"""
        with pytest.raises(ValidationError):
            CreateUserRequest(
                username="user",
                email="invalid-email",
                first_name="First",
                last_name="Last",
                password="password123",
            )

    def test_update_user_request_all_optional(self):
        """Test UpdateUserRequest with all fields optional"""
        request = UpdateUserRequest()
        assert request.username is None
        assert request.email is None
        assert request.first_name is None
        assert request.last_name is None
        assert request.role is None
        assert request.is_active is None

    def test_update_user_request_partial(self):
        """Test UpdateUserRequest with partial data"""
        request = UpdateUserRequest(username="newname", email="new@example.com")
        assert request.username == "newname"
        assert request.email == "new@example.com"
        assert request.first_name is None

    def test_user_response_model(self):
        """Test UserResponse model"""
        now = datetime.now(timezone.utc)
        response = UserResponse(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="CHILD",
            is_active=True,
            is_verified=True,
            created_at=now,
            updated_at=now,
            last_login=now,
        )
        assert response.user_id == "user_123"
        assert response.role == "CHILD"

    def test_standard_response_success(self):
        """Test StandardResponse for success case"""
        response = StandardResponse(
            success=True, message="Operation successful", data={"id": "123"}
        )
        assert response.success is True
        assert response.message == "Operation successful"
        assert response.data == {"id": "123"}

    def test_standard_response_no_data(self):
        """Test StandardResponse without data"""
        response = StandardResponse(success=False, message="Operation failed")
        assert response.success is False
        assert response.data is None


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestHelperFunctions:
    """Test helper functions"""

    def test_get_user_or_404_success(self, mock_session, sample_user):
        """Test _get_user_or_404 when user exists"""
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = _get_user_or_404(mock_session, "user_123")

        assert result == sample_user
        mock_session.query.assert_called_once()

    def test_get_user_or_404_not_found(self, mock_session):
        """Test _get_user_or_404 when user doesn't exist"""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            _get_user_or_404(mock_session, "nonexistent")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    def test_validate_self_modification_not_self(self, sample_user, current_user_dict):
        """Test _validate_self_modification when not modifying self"""
        user_data = UpdateUserRequest(role=UserRoleEnum.CHILD)

        # Should not raise exception
        _validate_self_modification(sample_user, user_data, current_user_dict)

    def test_validate_self_modification_self_same_role(
        self, sample_admin_user, current_user_dict
    ):
        """Test _validate_self_modification when admin keeps admin role"""
        user_data = UpdateUserRequest(role=UserRoleEnum.ADMIN)
        sample_admin_user.email = current_user_dict["email"]

        # Should not raise exception
        _validate_self_modification(sample_admin_user, user_data, current_user_dict)

    def test_validate_self_modification_self_demotion(
        self, sample_admin_user, current_user_dict
    ):
        """Test _validate_self_modification when admin tries to demote themselves"""
        user_data = UpdateUserRequest(role=UserRoleEnum.CHILD)
        sample_admin_user.email = current_user_dict["email"]

        with pytest.raises(HTTPException) as exc_info:
            _validate_self_modification(sample_admin_user, user_data, current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Cannot change your own admin role"

    def test_validate_self_modification_no_role_change(
        self, sample_admin_user, current_user_dict
    ):
        """Test _validate_self_modification when no role change requested"""
        user_data = UpdateUserRequest(username="newname")
        sample_admin_user.email = current_user_dict["email"]

        # Should not raise exception
        _validate_self_modification(sample_admin_user, user_data, current_user_dict)

    def test_check_username_uniqueness_unique(self, mock_session):
        """Test _check_username_uniqueness when username is unique"""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Should not raise exception
        _check_username_uniqueness(mock_session, "newusername", "user_123")

    def test_check_username_uniqueness_conflict(self, mock_session, sample_user):
        """Test _check_username_uniqueness when username exists"""
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        with pytest.raises(HTTPException) as exc_info:
            _check_username_uniqueness(mock_session, "testuser", "different_id")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Username already exists"

    def test_check_email_uniqueness_unique(self, mock_session):
        """Test _check_email_uniqueness when email is unique"""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Should not raise exception
        _check_email_uniqueness(mock_session, "new@example.com", "user_123")

    def test_check_email_uniqueness_conflict(self, mock_session, sample_user):
        """Test _check_email_uniqueness when email exists"""
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        with pytest.raises(HTTPException) as exc_info:
            _check_email_uniqueness(mock_session, "test@example.com", "different_id")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Email already exists"

    def test_update_user_role_admin(self, sample_user):
        """Test _update_user_role with ADMIN role"""
        _update_user_role(sample_user, UserRoleEnum.ADMIN)
        assert sample_user.role == UserRole.ADMIN

    def test_update_user_role_parent(self, sample_user):
        """Test _update_user_role with PARENT role"""
        _update_user_role(sample_user, UserRoleEnum.PARENT)
        assert sample_user.role == UserRole.PARENT

    def test_update_user_role_child(self, sample_admin_user):
        """Test _update_user_role with CHILD role"""
        _update_user_role(sample_admin_user, UserRoleEnum.CHILD)
        assert sample_admin_user.role == UserRole.CHILD

    def test_validate_self_deactivation_not_self(self, sample_user, current_user_dict):
        """Test _validate_self_deactivation when not deactivating self"""
        # Should not raise exception
        _validate_self_deactivation(sample_user, False, current_user_dict)

    def test_validate_self_deactivation_activating_self(
        self, sample_admin_user, current_user_dict
    ):
        """Test _validate_self_deactivation when activating self"""
        sample_admin_user.email = current_user_dict["email"]

        # Should not raise exception (activating is OK)
        _validate_self_deactivation(sample_admin_user, True, current_user_dict)

    def test_validate_self_deactivation_self_deactivation(
        self, sample_admin_user, current_user_dict
    ):
        """Test _validate_self_deactivation when deactivating self"""
        sample_admin_user.email = current_user_dict["email"]

        with pytest.raises(HTTPException) as exc_info:
            _validate_self_deactivation(sample_admin_user, False, current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Cannot deactivate your own account"

    @patch("app.api.admin.get_db_session_context")
    def test_update_user_fields_username_only(
        self, mock_context, mock_session, sample_user, current_user_dict
    ):
        """Test _update_user_fields with username update"""
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        user_data = UpdateUserRequest(username="newusername")
        _update_user_fields(
            mock_session, sample_user, user_data, "user_123", current_user_dict
        )

        assert sample_user.username == "newusername"

    @patch("app.api.admin.get_db_session_context")
    def test_update_user_fields_email_only(
        self, mock_context, mock_session, sample_user, current_user_dict
    ):
        """Test _update_user_fields with email update"""
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        user_data = UpdateUserRequest(email="newemail@example.com")
        _update_user_fields(
            mock_session, sample_user, user_data, "user_123", current_user_dict
        )

        assert sample_user.email == "newemail@example.com"

    def test_update_user_fields_first_name(
        self, mock_session, sample_user, current_user_dict
    ):
        """Test _update_user_fields with first_name update"""
        user_data = UpdateUserRequest(first_name="NewFirst")
        _update_user_fields(
            mock_session, sample_user, user_data, "user_123", current_user_dict
        )

        assert sample_user.first_name == "NewFirst"

    def test_update_user_fields_last_name(
        self, mock_session, sample_user, current_user_dict
    ):
        """Test _update_user_fields with last_name update"""
        user_data = UpdateUserRequest(last_name="NewLast")
        _update_user_fields(
            mock_session, sample_user, user_data, "user_123", current_user_dict
        )

        assert sample_user.last_name == "NewLast"

    def test_update_user_fields_role(
        self, mock_session, sample_user, current_user_dict
    ):
        """Test _update_user_fields with role update"""
        user_data = UpdateUserRequest(role=UserRoleEnum.PARENT)
        _update_user_fields(
            mock_session, sample_user, user_data, "user_123", current_user_dict
        )

        assert sample_user.role == UserRole.PARENT

    def test_update_user_fields_is_active(
        self, mock_session, sample_user, current_user_dict
    ):
        """Test _update_user_fields with is_active update"""
        user_data = UpdateUserRequest(is_active=False)
        _update_user_fields(
            mock_session, sample_user, user_data, "user_123", current_user_dict
        )

        assert sample_user.is_active is False


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================


class TestListUsersEndpoint:
    """Test GET /api/admin/users endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_list_users_success(self, mock_context, current_user_dict):
        """Test listing users successfully"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session

        user1 = User(
            user_id="user_1",
            username="user1",
            email="user1@example.com",
            password_hash="hash",
            first_name="User",
            last_name="One",
            role=UserRole.CHILD,
            is_active=True,
            is_verified=True,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            last_login=None,
        )

        user2 = User(
            user_id="user_2",
            username="user2",
            email="user2@example.com",
            password_hash="hash",
            first_name="User",
            last_name="Two",
            role=UserRole.PARENT,
            is_active=True,
            is_verified=False,
            created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            last_login=datetime(2024, 1, 5, tzinfo=timezone.utc),
        )

        mock_session.query.return_value.all.return_value = [user1, user2]

        result = await list_users(current_user=current_user_dict)

        assert len(result) == 2
        assert result[0].user_id == "user_1"
        assert result[0].role == "CHILD"
        assert result[0].last_login is None
        assert result[1].user_id == "user_2"
        assert result[1].role == "PARENT"
        assert result[1].last_login is not None

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_list_users_empty(self, mock_context, current_user_dict):
        """Test listing users when none exist"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = []

        result = await list_users(current_user=current_user_dict)

        assert result == []

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_list_users_database_error(self, mock_context, current_user_dict):
        """Test listing users with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await list_users(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to retrieve users"


class TestCreateUserEndpoint:
    """Test POST /api/admin/users endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.hash_password")
    @patch("app.api.admin.get_db_session_context")
    async def test_create_user_success(
        self, mock_context, mock_hash, create_user_request_data, current_user_dict
    ):
        """Test creating user successfully"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_hash.return_value = "hashed_password"

        user_data = CreateUserRequest(**create_user_request_data)
        result = await create_user(user_data=user_data, current_user=current_user_dict)

        assert result.success is True
        assert result.message == "User created successfully"
        assert "user_id" in result.data
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_create_user_duplicate_email(
        self, mock_context, create_user_request_data, current_user_dict, sample_user
    ):
        """Test creating user with duplicate email"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        user_data = CreateUserRequest(**create_user_request_data)

        with pytest.raises(HTTPException) as exc_info:
            await create_user(user_data=user_data, current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.admin.hash_password")
    @patch("app.api.admin.get_db_session_context")
    async def test_create_user_with_admin_role(
        self, mock_context, mock_hash, current_user_dict
    ):
        """Test creating user with ADMIN role"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_hash.return_value = "hashed_password"

        user_data = CreateUserRequest(
            username="admin2",
            email="admin2@example.com",
            first_name="Admin",
            last_name="Two",
            password="password",
            role=UserRoleEnum.ADMIN,
        )

        result = await create_user(user_data=user_data, current_user=current_user_dict)

        assert result.success is True
        # Verify the user added has ADMIN role
        call_args = mock_session.add.call_args[0][0]
        assert call_args.role == UserRole.ADMIN

    @pytest.mark.asyncio
    @patch("app.api.admin.hash_password")
    @patch("app.api.admin.get_db_session_context")
    async def test_create_user_with_parent_role(
        self, mock_context, mock_hash, current_user_dict
    ):
        """Test creating user with PARENT role"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_hash.return_value = "hashed_password"

        user_data = CreateUserRequest(
            username="parent1",
            email="parent1@example.com",
            first_name="Parent",
            last_name="One",
            password="password",
            role=UserRoleEnum.PARENT,
        )

        result = await create_user(user_data=user_data, current_user=current_user_dict)

        assert result.success is True
        call_args = mock_session.add.call_args[0][0]
        assert call_args.role == UserRole.PARENT

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_create_user_database_error(
        self, mock_context, create_user_request_data, current_user_dict
    ):
        """Test creating user with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        user_data = CreateUserRequest(**create_user_request_data)

        with pytest.raises(HTTPException) as exc_info:
            await create_user(user_data=user_data, current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to create user"


class TestGetUserEndpoint:
    """Test GET /api/admin/users/{user_id} endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_get_user_success(self, mock_context, sample_user, current_user_dict):
        """Test getting user successfully"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = await get_user(user_id="user_123", current_user=current_user_dict)

        assert result.user_id == "user_123"
        assert result.email == "test@example.com"
        assert result.role == "CHILD"

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_get_user_not_found(self, mock_context, current_user_dict):
        """Test getting non-existent user"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_user(user_id="nonexistent", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_get_user_database_error(self, mock_context, current_user_dict):
        """Test getting user with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await get_user(user_id="user_123", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to retrieve user"


class TestUpdateUserEndpoint:
    """Test PUT /api/admin/users/{user_id} endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_update_user_success(
        self, mock_context, sample_user, current_user_dict
    ):
        """Test updating user successfully"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session

        # Setup query mock to return user for get_user_or_404, then None for uniqueness checks
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            sample_user,  # First call: get_user_or_404
            None,  # Second call: username uniqueness check
        ]

        user_data = UpdateUserRequest(username="updated_username")
        result = await update_user(
            user_id="user_123", user_data=user_data, current_user=current_user_dict
        )

        assert result.success is True
        assert result.message == "User updated successfully"
        assert sample_user.username == "updated_username"

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_update_user_not_found(self, mock_context, current_user_dict):
        """Test updating non-existent user"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        user_data = UpdateUserRequest(username="new_name")

        with pytest.raises(HTTPException) as exc_info:
            await update_user(
                user_id="nonexistent",
                user_data=user_data,
                current_user=current_user_dict,
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_update_user_self_demotion(
        self, mock_context, sample_admin_user, current_user_dict
    ):
        """Test admin trying to demote themselves"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        sample_admin_user.email = current_user_dict["email"]
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_admin_user
        )

        user_data = UpdateUserRequest(role=UserRoleEnum.CHILD)

        with pytest.raises(HTTPException) as exc_info:
            await update_user(
                user_id="admin_123", user_data=user_data, current_user=current_user_dict
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "own admin role" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_update_user_database_error(self, mock_context, current_user_dict):
        """Test updating user with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        user_data = UpdateUserRequest(username="new_name")

        with pytest.raises(HTTPException) as exc_info:
            await update_user(
                user_id="user_123", user_data=user_data, current_user=current_user_dict
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to update user"


class TestToggleUserStatusEndpoint:
    """Test POST /api/admin/users/{user_id}/toggle-status endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_toggle_user_status_activate(
        self, mock_context, sample_user, current_user_dict
    ):
        """Test activating inactive user"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        sample_user.is_active = False
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = await toggle_user_status(
            user_id="user_123", current_user=current_user_dict
        )

        assert result.success is True
        assert "activated" in result.message
        assert sample_user.is_active is True

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_toggle_user_status_deactivate(
        self, mock_context, sample_user, current_user_dict
    ):
        """Test deactivating active user"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        sample_user.is_active = True
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = await toggle_user_status(
            user_id="user_123", current_user=current_user_dict
        )

        assert result.success is True
        assert "deactivated" in result.message
        assert sample_user.is_active is False

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_toggle_user_status_not_found(self, mock_context, current_user_dict):
        """Test toggling status of non-existent user"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await toggle_user_status(
                user_id="nonexistent", current_user=current_user_dict
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_toggle_user_status_self_deactivation(
        self, mock_context, sample_admin_user, current_user_dict
    ):
        """Test admin trying to deactivate themselves"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        sample_admin_user.email = current_user_dict["email"]
        sample_admin_user.is_active = True
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_admin_user
        )

        with pytest.raises(HTTPException) as exc_info:
            await toggle_user_status(
                user_id="admin_123", current_user=current_user_dict
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "own account" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_toggle_user_status_database_error(
        self, mock_context, current_user_dict
    ):
        """Test toggling status with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await toggle_user_status(user_id="user_123", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to toggle user status"


class TestDeleteUserEndpoint:
    """Test DELETE /api/admin/users/{user_id} endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_delete_user_success(
        self, mock_context, sample_user, current_user_dict
    ):
        """Test deleting user successfully"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = await delete_user(user_id="user_123", current_user=current_user_dict)

        assert result.success is True
        assert result.message == "User deleted successfully"
        mock_session.delete.assert_called_once_with(sample_user)

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_delete_user_not_found(self, mock_context, current_user_dict):
        """Test deleting non-existent user"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await delete_user(user_id="nonexistent", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_delete_user_self_deletion(
        self, mock_context, sample_admin_user, current_user_dict
    ):
        """Test admin trying to delete themselves"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        sample_admin_user.email = current_user_dict["email"]
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_admin_user
        )

        with pytest.raises(HTTPException) as exc_info:
            await delete_user(user_id="admin_123", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "own account" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_delete_user_admin_protection(
        self, mock_context, sample_admin_user, current_user_dict
    ):
        """Test preventing deletion of admin users"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        # Different admin user
        sample_admin_user.email = "different@example.com"
        mock_session.query.return_value.filter.return_value.first.return_value = (
            sample_admin_user
        )

        with pytest.raises(HTTPException) as exc_info:
            await delete_user(user_id="admin_123", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete admin users" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_delete_user_database_error(self, mock_context, current_user_dict):
        """Test deleting user with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await delete_user(user_id="user_123", current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to delete user"


class TestGuestSessionEndpoints:
    """Test guest session management endpoints"""

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_get_guest_session_active(
        self, mock_manager_class, current_user_dict
    ):
        """Test getting active guest session"""
        mock_manager = MagicMock()
        mock_manager.active_guest_session = "guest_123"
        mock_manager.guest_session_data = {
            "user_id": "guest_123",
            "created_at": "2024-01-01T00:00:00",
            "status": "active",
        }
        mock_manager_class.return_value = mock_manager

        result = await get_guest_session(current_user=current_user_dict)

        assert result.success is True
        assert "Active guest session found" in result.message
        assert result.data["user_id"] == "guest_123"
        assert result.data["status"] == "active"

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_get_guest_session_inactive(
        self, mock_manager_class, current_user_dict
    ):
        """Test getting guest session when none active"""
        mock_manager = MagicMock()
        mock_manager.active_guest_session = None
        mock_manager.guest_session_data = {}
        mock_manager_class.return_value = mock_manager

        result = await get_guest_session(current_user=current_user_dict)

        assert result.success is True
        assert "No active guest session" in result.message
        assert result.data is None

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_get_guest_session_error(self, mock_manager_class, current_user_dict):
        """Test getting guest session with error"""
        mock_manager_class.side_effect = Exception("Manager error")

        with pytest.raises(HTTPException) as exc_info:
            await get_guest_session(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve guest session" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_create_guest_session_success(
        self, mock_manager_class, current_user_dict
    ):
        """Test creating guest session successfully"""
        mock_manager = MagicMock()
        mock_manager.active_guest_session = None
        mock_manager_class.return_value = mock_manager

        result = await create_guest_session(current_user=current_user_dict)

        assert result.success is True
        assert "created successfully" in result.message
        assert "guest_id" in result.data
        assert mock_manager.active_guest_session is not None

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_create_guest_session_already_active(
        self, mock_manager_class, current_user_dict
    ):
        """Test creating guest session when one already exists"""
        mock_manager = MagicMock()
        mock_manager.active_guest_session = "guest_123"
        mock_manager_class.return_value = mock_manager

        with pytest.raises(HTTPException) as exc_info:
            await create_guest_session(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already active" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_create_guest_session_error(
        self, mock_manager_class, current_user_dict
    ):
        """Test creating guest session with error"""
        mock_manager_class.side_effect = Exception("Manager error")

        with pytest.raises(HTTPException) as exc_info:
            await create_guest_session(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create guest session" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_terminate_guest_session_success(
        self, mock_manager_class, current_user_dict
    ):
        """Test terminating guest session successfully"""
        mock_manager = MagicMock()
        mock_manager.active_guest_session = "guest_123"
        mock_manager_class.return_value = mock_manager

        result = await terminate_guest_session(current_user=current_user_dict)

        assert result.success is True
        assert "terminated successfully" in result.message
        assert mock_manager.active_guest_session is None
        assert mock_manager.guest_session_data == {}

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_terminate_guest_session_not_active(
        self, mock_manager_class, current_user_dict
    ):
        """Test terminating guest session when none active"""
        mock_manager = MagicMock()
        mock_manager.active_guest_session = None
        mock_manager_class.return_value = mock_manager

        with pytest.raises(HTTPException) as exc_info:
            await terminate_guest_session(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "No active guest session" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.admin_auth.GuestUserManager")
    async def test_terminate_guest_session_error(
        self, mock_manager_class, current_user_dict
    ):
        """Test terminating guest session with error"""
        mock_manager_class.side_effect = Exception("Manager error")

        with pytest.raises(HTTPException) as exc_info:
            await terminate_guest_session(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to terminate guest session" in exc_info.value.detail


class TestSystemStatsEndpoint:
    """Test GET /api/admin/stats endpoint"""

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_get_system_stats_success(self, mock_context, current_user_dict):
        """Test getting system statistics successfully"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session

        # Setup query mocks
        mock_session.query.return_value.count.return_value = 10
        mock_session.query.return_value.filter.return_value.count.side_effect = [
            8,  # active users
            2,  # admin users
            3,  # parent users
            5,  # child users
            2,  # recent users
        ]

        result = await get_system_stats(current_user=current_user_dict)

        assert result.success is True
        assert result.data["total_users"] == 10
        assert result.data["active_users"] == 8
        assert result.data["inactive_users"] == 2
        assert result.data["admin_users"] == 2
        assert result.data["parent_users"] == 3
        assert result.data["child_users"] == 5
        assert result.data["recent_users"] == 2
        assert "last_updated" in result.data

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_get_system_stats_zero_users(self, mock_context, current_user_dict):
        """Test getting system statistics with no users"""
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session

        mock_session.query.return_value.count.return_value = 0
        mock_session.query.return_value.filter.return_value.count.return_value = 0

        result = await get_system_stats(current_user=current_user_dict)

        assert result.success is True
        assert result.data["total_users"] == 0
        assert result.data["active_users"] == 0

    @pytest.mark.asyncio
    @patch("app.api.admin.get_db_session_context")
    async def test_get_system_stats_database_error(
        self, mock_context, current_user_dict
    ):
        """Test getting system statistics with database error"""
        mock_context.return_value.__enter__.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await get_system_stats(current_user=current_user_dict)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to retrieve system statistics"


# ============================================================================
# ROUTER CONFIGURATION TESTS
# ============================================================================


class TestRouterConfiguration:
    """Test admin router configuration"""

    def test_admin_router_prefix(self):
        """Test admin router has correct prefix"""
        assert admin_router.prefix == "/api/admin"

    def test_admin_router_tags(self):
        """Test admin router has correct tags"""
        assert "admin" in admin_router.tags

    def test_admin_router_includes_language_config(self):
        """Test admin router includes language_config router"""
        # The language_config router is included at the module level
        assert len(admin_router.routes) >= 9  # At least 9 admin routes
