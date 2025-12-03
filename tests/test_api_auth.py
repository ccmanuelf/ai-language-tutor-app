"""
Comprehensive tests for app/api/auth.py
Testing all 7 API endpoints with FastAPI TestClient

Coverage Target: TRUE 100% (95 statements, 34 branches)
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.simple_user import SimpleUser, UserRole


# Test fixtures
@pytest.fixture
def app():
    """Create FastAPI app instance for testing"""
    from app.main import create_app

    return create_app()


@pytest.fixture
def client(app):
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    user = MagicMock(spec=SimpleUser)
    user.id = 1
    user.user_id = "testuser123"
    user.username = "Test User"
    user.email = "test@example.com"
    user.role = UserRole.CHILD
    user.first_name = "Test"
    user.last_name = "User"
    user.ui_language = "en"
    user.is_active = True
    user.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    user.last_login = None
    user.updated_at = None
    user.password_hash = "hashed_password"
    return user


@pytest.fixture
def sample_parent_user():
    """Sample parent user for testing"""
    user = MagicMock(spec=SimpleUser)
    user.id = 2
    user.user_id = "parent123"
    user.username = "Parent User"
    user.email = "parent@example.com"
    user.role = UserRole.PARENT
    user.first_name = "Parent"
    user.last_name = "User"
    user.ui_language = "en"
    user.is_active = True
    user.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    user.last_login = None
    user.updated_at = None
    user.password_hash = "hashed_password"
    return user


@pytest.fixture
def sample_admin_user():
    """Sample admin user for testing"""
    user = MagicMock(spec=SimpleUser)
    user.id = 3
    user.user_id = "admin123"
    user.username = "Admin User"
    user.email = "admin@example.com"
    user.role = UserRole.ADMIN
    user.first_name = "Admin"
    user.last_name = "User"
    user.ui_language = "en"
    user.is_active = True
    user.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    user.last_login = None
    user.updated_at = None
    user.password_hash = "hashed_password"
    return user


# ============================================================================
# Test Class 1: POST /login - Successful Login
# ============================================================================


class TestLoginSuccess:
    """Test successful login scenarios"""

    def test_login_valid_credentials(self, app, client, mock_db, sample_user):
        """Test successful login with valid credentials"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with (
            patch("app.api.auth.authenticate_user") as mock_auth,
            patch("app.api.auth.create_access_token") as mock_token,
        ):
            # Setup mocks
            mock_auth.return_value = sample_user
            mock_token.return_value = "test_token_123"

            # Make request
            response = client.post(
                "/api/v1/auth/login",
                json={"user_id": "testuser123", "password": "password123"},
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test_token_123"
            assert data["token_type"] == "bearer"
            assert data["user"]["user_id"] == "testuser123"
            assert data["user"]["username"] == "Test User"
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["role"] == "child"
            assert data["user"]["is_active"] is True

            # Verify last_login was updated
            assert sample_user.last_login is not None
            mock_db.commit.assert_called_once()

        # Clean up
        app.dependency_overrides.clear()

    def test_login_no_password(self, app, client, mock_db, sample_user):
        """Test login with empty password (development mode)"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with (
            patch("app.api.auth.authenticate_user") as mock_auth,
            patch("app.api.auth.create_access_token") as mock_token,
        ):
            # Setup mocks
            mock_auth.return_value = sample_user
            mock_token.return_value = "test_token_123"

            # Make request with empty password
            response = client.post(
                "/api/v1/auth/login", json={"user_id": "testuser123", "password": ""}
            )

            # Verify response
            assert response.status_code == 200
            mock_auth.assert_called_once_with(mock_db, "testuser123", "")

        # Clean up
        app.dependency_overrides.clear()

    def test_login_user_with_null_role(self, app, client, mock_db, sample_user):
        """Test login with user that has null role"""
        from app.database.config import get_primary_db_session

        sample_user.role = None

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with (
            patch("app.api.auth.authenticate_user") as mock_auth,
            patch("app.api.auth.create_access_token") as mock_token,
        ):
            # Setup mocks
            mock_auth.return_value = sample_user
            mock_token.return_value = "test_token_123"

            # Make request
            response = client.post(
                "/api/v1/auth/login",
                json={"user_id": "testuser123", "password": "password123"},
            )

            # Verify response - should default to "child"
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["role"] == "child"

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 2: POST /login - Failed Login
# ============================================================================


class TestLoginFailure:
    """Test failed login scenarios"""

    def test_login_invalid_credentials(self, app, client, mock_db):
        """Test login with invalid credentials"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with patch("app.api.auth.authenticate_user") as mock_auth:
            # Setup mocks - authenticate_user returns None for invalid creds
            mock_auth.return_value = None

            # Make request
            response = client.post(
                "/api/v1/auth/login",
                json={"user_id": "testuser123", "password": "wrong_password"},
            )

            # Verify response
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid credentials"

        # Clean up
        app.dependency_overrides.clear()

    def test_login_nonexistent_user(self, app, client, mock_db):
        """Test login with non-existent user"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with patch("app.api.auth.authenticate_user") as mock_auth:
            # Setup mocks
            mock_auth.return_value = None

            # Make request
            response = client.post(
                "/api/v1/auth/login",
                json={"user_id": "nonexistent", "password": "password123"},
            )

            # Verify response
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid credentials"

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 3: POST /register - Successful Registration
# ============================================================================


class TestRegisterSuccess:
    """Test successful registration scenarios"""

    def test_register_with_password(self, app, client, mock_db):
        """Test registration with password"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with (
            patch("app.api.auth.get_password_hash") as mock_hash,
            patch("app.api.auth.create_access_token") as mock_token,
        ):
            # Setup mocks
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_hash.return_value = "hashed_password_123"
            mock_token.return_value = "test_token_123"

            # Track the added user
            added_user = None

            def mock_add(user):
                nonlocal added_user
                added_user = user
                user.id = 1
                user.ui_language = "en"

            mock_db.add.side_effect = mock_add

            # Make request
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "user_id": "newuser123",
                    "username": "New User",
                    "email": "new@example.com",
                    "password": "password123",
                    "role": "child",
                    "first_name": "New",
                    "last_name": "User",
                },
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test_token_123"
            assert data["token_type"] == "bearer"

            # Verify password was hashed
            mock_hash.assert_called_once_with("password123")

            # Verify user was added to database
            assert added_user is not None
            assert added_user.user_id == "newuser123"
            assert added_user.password_hash == "hashed_password_123"
            mock_db.commit.assert_called_once()

        # Clean up
        app.dependency_overrides.clear()

    def test_register_without_password(self, app, client, mock_db):
        """Test registration without password (development mode)"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with (
            patch("app.api.auth.create_access_token") as mock_token,
            patch("app.api.auth.get_password_hash") as mock_hash,
        ):
            # Setup mocks
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_token.return_value = "test_token_123"

            # Track the added user
            added_user = None

            def mock_add(user):
                nonlocal added_user
                added_user = user
                user.id = 1
                user.ui_language = "en"

            mock_db.add.side_effect = mock_add

            # Make request without password
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "user_id": "newuser123",
                    "username": "New User",
                    "role": "child",
                },
            )

            # Verify response
            assert response.status_code == 200

            # Verify password_hash was NOT called
            mock_hash.assert_not_called()

            # Verify user was created with None password_hash
            assert added_user.password_hash is None

        # Clean up
        app.dependency_overrides.clear()

    def test_register_with_parent_role(self, app, client, mock_db):
        """Test registration with parent role"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with patch("app.api.auth.create_access_token") as mock_token:
            # Setup mocks
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_token.return_value = "test_token_123"

            # Track the added user
            added_user = None

            def mock_add(user):
                nonlocal added_user
                added_user = user
                user.id = 1
                user.ui_language = "en"

            mock_db.add.side_effect = mock_add

            # Make request with parent role
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "user_id": "parent123",
                    "username": "Parent User",
                    "role": "parent",
                },
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["role"] == "parent"

            # Verify user was created with parent role
            assert added_user.role == UserRole.PARENT

        # Clean up
        app.dependency_overrides.clear()

    def test_register_with_invalid_role_defaults_to_child(self, app, client, mock_db):
        """Test registration with invalid role defaults to child"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        with patch("app.api.auth.create_access_token") as mock_token:
            # Setup mocks
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_token.return_value = "test_token_123"

            # Track the added user
            added_user = None

            def mock_add(user):
                nonlocal added_user
                added_user = user
                user.id = 1
                user.ui_language = "en"

            mock_db.add.side_effect = mock_add

            # Make request with invalid role
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "user_id": "newuser123",
                    "username": "New User",
                    "role": "invalid_role_name",
                },
            )

            # Verify response
            assert response.status_code == 200

            # Verify user was created with child role
            assert added_user.role == UserRole.CHILD

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 4: POST /register - Failed Registration
# ============================================================================


class TestRegisterFailure:
    """Test failed registration scenarios"""

    def test_register_duplicate_user_id(self, app, client, mock_db, sample_user):
        """Test registration with existing user_id"""
        from app.database.config import get_primary_db_session

        # Override database dependency
        def override_get_db():
            return mock_db

        app.dependency_overrides[get_primary_db_session] = override_get_db

        # Setup mocks - query returns existing user
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user

        # Make request
        response = client.post(
            "/api/v1/auth/register",
            json={
                "user_id": "testuser123",  # Already exists
                "username": "New User",
                "password": "password123",
            },
        )

        # Verify response
        assert response.status_code == 400
        assert response.json()["detail"] == "User ID already exists"

        # Verify database was not modified
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 5: GET /profile - Get User Profile
# ============================================================================


class TestGetProfile:
    """Test getting user profile"""

    def test_get_profile_success(self, app, client, sample_user):
        """Test getting profile for authenticated user"""
        from app.core.security import require_auth

        # Override auth dependency
        def override_require_auth():
            return sample_user

        app.dependency_overrides[require_auth] = override_require_auth

        # Make request
        response = client.get("/api/v1/auth/profile")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "testuser123"
        assert data["username"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["role"] == "child"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["ui_language"] == "en"
        assert data["is_active"] is True

        # Clean up
        app.dependency_overrides.clear()

    def test_get_profile_null_role(self, app, client, sample_user):
        """Test getting profile for user with null role"""
        from app.core.security import require_auth

        sample_user.role = None

        # Override auth dependency
        def override_require_auth():
            return sample_user

        app.dependency_overrides[require_auth] = override_require_auth

        # Make request
        response = client.get("/api/v1/auth/profile")

        # Verify response - defaults to "child"
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "child"

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 6: PUT /profile - Update User Profile
# ============================================================================


class TestUpdateProfile:
    """Test updating user profile"""

    def test_update_profile_all_fields(self, app, client, mock_db, sample_user):
        """Test updating all profile fields"""
        from app.core.security import require_auth
        from app.database.config import get_primary_db_session

        # Override dependencies
        def override_require_auth():
            return sample_user

        def override_get_db():
            return mock_db

        app.dependency_overrides[require_auth] = override_require_auth
        app.dependency_overrides[get_primary_db_session] = override_get_db

        # Make request
        response = client.put(
            "/api/v1/auth/profile",
            data={
                "username": "Updated Name",
                "email": "updated@example.com",
                "first_name": "Updated",
                "last_name": "Name",
                "ui_language": "es",
            },
        )

        # Verify response
        assert response.status_code == 200
        assert response.json()["message"] == "Profile updated successfully"

        # Verify user was updated
        assert sample_user.username == "Updated Name"
        assert sample_user.email == "updated@example.com"
        assert sample_user.first_name == "Updated"
        assert sample_user.last_name == "Name"
        assert sample_user.ui_language == "es"
        assert sample_user.updated_at is not None

        # Verify database was committed
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_user)

        # Clean up
        app.dependency_overrides.clear()

    def test_update_profile_partial_fields(self, app, client, mock_db, sample_user):
        """Test updating only some profile fields"""
        from app.core.security import require_auth
        from app.database.config import get_primary_db_session

        original_email = sample_user.email

        # Override dependencies
        def override_require_auth():
            return sample_user

        def override_get_db():
            return mock_db

        app.dependency_overrides[require_auth] = override_require_auth
        app.dependency_overrides[get_primary_db_session] = override_get_db

        # Make request - only update username
        response = client.put("/api/v1/auth/profile", data={"username": "New Username"})

        # Verify response
        assert response.status_code == 200

        # Verify only username was updated
        assert sample_user.username == "New Username"
        assert sample_user.email == original_email  # Unchanged

        # Clean up
        app.dependency_overrides.clear()

    def test_update_profile_no_fields(self, app, client, mock_db, sample_user):
        """Test updating profile with no fields (should still work)"""
        from app.core.security import require_auth
        from app.database.config import get_primary_db_session

        # Override dependencies
        def override_require_auth():
            return sample_user

        def override_get_db():
            return mock_db

        app.dependency_overrides[require_auth] = override_require_auth
        app.dependency_overrides[get_primary_db_session] = override_get_db

        # Make request with no data
        response = client.put("/api/v1/auth/profile", data={})

        # Verify response
        assert response.status_code == 200

        # Verify updated_at was still set
        assert sample_user.updated_at is not None
        mock_db.commit.assert_called_once()

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 7: GET /users - List Users
# ============================================================================


class TestListUsers:
    """Test listing users (family management)"""

    def test_list_users_as_parent(self, app, client, mock_db, sample_parent_user):
        """Test listing users as parent"""
        from app.core.security import require_auth
        from app.database.config import get_primary_db_session

        # Create sample user list
        user1 = MagicMock(spec=SimpleUser)
        user1.id = 1
        user1.user_id = "child1"
        user1.username = "Child One"
        user1.email = "child1@example.com"
        user1.role = UserRole.CHILD
        user1.first_name = "Child"
        user1.last_name = "One"
        user1.ui_language = "en"
        user1.is_active = True
        user1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        user2 = MagicMock(spec=SimpleUser)
        user2.id = 2
        user2.user_id = "child2"
        user2.username = "Child Two"
        user2.email = "child2@example.com"
        user2.role = UserRole.CHILD
        user2.first_name = "Child"
        user2.last_name = "Two"
        user2.ui_language = "en"
        user2.is_active = True
        user2.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)

        # Override dependencies
        def override_require_auth():
            return sample_parent_user

        def override_get_db():
            return mock_db

        app.dependency_overrides[require_auth] = override_require_auth
        app.dependency_overrides[get_primary_db_session] = override_get_db

        mock_db.query.return_value.filter.return_value.all.return_value = [user1, user2]

        # Make request
        response = client.get("/api/v1/auth/users")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["user_id"] == "child1"
        assert data[1]["user_id"] == "child2"

        # Clean up
        app.dependency_overrides.clear()

    def test_list_users_as_admin(self, app, client, mock_db, sample_admin_user):
        """Test listing users as admin"""
        from app.core.security import require_auth
        from app.database.config import get_primary_db_session

        # Override dependencies
        def override_require_auth():
            return sample_admin_user

        def override_get_db():
            return mock_db

        app.dependency_overrides[require_auth] = override_require_auth
        app.dependency_overrides[get_primary_db_session] = override_get_db

        mock_db.query.return_value.filter.return_value.all.return_value = []

        # Make request
        response = client.get("/api/v1/auth/users")

        # Verify response
        assert response.status_code == 200
        assert response.json() == []

        # Clean up
        app.dependency_overrides.clear()

    def test_list_users_as_child_forbidden(self, app, client, sample_user):
        """Test listing users as child (should be forbidden)"""
        from app.core.security import require_auth

        # Override auth dependency
        def override_require_auth():
            return sample_user

        app.dependency_overrides[require_auth] = override_require_auth

        # Make request
        response = client.get("/api/v1/auth/users")

        # Verify response
        assert response.status_code == 403
        assert response.json()["detail"] == "Insufficient permissions"

        # Clean up
        app.dependency_overrides.clear()

    def test_list_users_with_null_role(self, app, client, mock_db, sample_admin_user):
        """Test listing users when user has null role in database"""
        from app.core.security import require_auth
        from app.database.config import get_primary_db_session

        user_with_null_role = MagicMock(spec=SimpleUser)
        user_with_null_role.id = 1
        user_with_null_role.user_id = "user123"
        user_with_null_role.username = "User"
        user_with_null_role.email = "user@example.com"
        user_with_null_role.role = None
        user_with_null_role.first_name = "User"
        user_with_null_role.last_name = "Name"
        user_with_null_role.ui_language = "en"
        user_with_null_role.is_active = True
        user_with_null_role.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Override dependencies
        def override_require_auth():
            return sample_admin_user

        def override_get_db():
            return mock_db

        app.dependency_overrides[require_auth] = override_require_auth
        app.dependency_overrides[get_primary_db_session] = override_get_db

        mock_db.query.return_value.filter.return_value.all.return_value = [
            user_with_null_role
        ]

        # Make request
        response = client.get("/api/v1/auth/users")

        # Verify response - null role should default to "child"
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["role"] == "child"

        # Clean up
        app.dependency_overrides.clear()


# ============================================================================
# Test Class 8: POST /logout - Logout
# ============================================================================


class TestLogout:
    """Test logout endpoint"""

    def test_logout_success(self, client):
        """Test successful logout"""
        response = client.post("/api/v1/auth/logout")

        # Verify response
        assert response.status_code == 200
        assert response.json()["message"] == "Logout successful"


# ============================================================================
# Test Class 9: GET /me - Get Current User Info
# ============================================================================


class TestGetMe:
    """Test getting current user info"""

    def test_get_me_authenticated(self, app, client, sample_user):
        """Test /me endpoint with authenticated user"""
        from app.core.security import get_current_user

        # Override auth dependency
        def override_get_current_user():
            return sample_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Make request
        response = client.get("/api/v1/auth/me")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["user_id"] == "testuser123"
        assert data["user"]["username"] == "Test User"
        assert data["user"]["role"] == "child"

        # Clean up
        app.dependency_overrides.clear()

    def test_get_me_unauthenticated(self, app, client):
        """Test /me endpoint without authentication"""
        from app.core.security import get_current_user

        # Override auth dependency - no user
        def override_get_current_user():
            return None

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Make request
        response = client.get("/api/v1/auth/me")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

        # Clean up
        app.dependency_overrides.clear()

    def test_get_me_with_null_role(self, app, client, sample_user):
        """Test /me endpoint with user that has null role"""
        from app.core.security import get_current_user

        sample_user.role = None

        # Override auth dependency
        def override_get_current_user():
            return sample_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Make request
        response = client.get("/api/v1/auth/me")

        # Verify response - defaults to "child"
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "child"

        # Clean up
        app.dependency_overrides.clear()
