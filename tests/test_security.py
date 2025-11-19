"""
Test module for core/security.py
AI Language Tutor App - Security utilities testing

Tests JWT authentication, password hashing, and user session management.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    require_auth,
    verify_password,
    verify_token,
)
from app.models.simple_user import SimpleUser


class TestJWTTokens:
    """Test JWT token creation and verification"""

    def test_create_access_token_with_default_expiry(self):
        """Test creating JWT token with default expiration"""
        data = {"sub": "test_user", "role": "admin"}
        token = create_access_token(data)

        # Verify token can be decoded
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test_user"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_create_access_token_with_custom_expiry(self):
        """Test creating JWT token with custom expiration"""
        data = {"sub": "test_user"}
        custom_delta = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_delta)

        # Verify token can be decoded
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test_user"
        assert "exp" in payload

        # Verify expiration is approximately 2 hours from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = (exp_time - now).total_seconds()
        # Allow 5 second tolerance for test execution time
        assert 7195 <= time_diff <= 7205  # ~2 hours

    def test_verify_token_valid(self):
        """Test verifying valid JWT token"""
        data = {"sub": "test_user", "role": "admin"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user"
        assert payload["role"] == "admin"

    def test_verify_token_invalid(self):
        """Test verifying invalid JWT token"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None

    def test_verify_token_expired(self):
        """Test verifying expired JWT token"""
        data = {"sub": "test_user"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = verify_token(token)
        assert payload is None


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_get_password_hash(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        # Verify hash is generated
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0

        # Verify hash is different from password
        assert hashed != password

    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        result = verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        result = verify_password(wrong_password, hashed)
        assert result is False

    def test_verify_password_exception_handling(self):
        """Test password verification with invalid hash (exception handling)"""
        password = "test_password"
        invalid_hash = "not_a_valid_hash"

        # Should return False when exception occurs
        result = verify_password(password, invalid_hash)
        assert result is False


class TestUserAuthentication:
    """Test user authentication functions"""

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Create mock user with password
        mock_user = SimpleUser(
            user_id="test_user",
            email="test@example.com",
            password_hash=get_password_hash("correct_password"),
        )

        # Create mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Test authentication
        result = authenticate_user(mock_db, "test_user", "correct_password")
        assert result is not None
        assert result.user_id == "test_user"

    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user"""
        # Create mock database session with no user
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Test authentication
        result = authenticate_user(mock_db, "nonexistent_user", "password")
        assert result is None

    def test_authenticate_user_no_password_hash(self):
        """Test authentication with user that has no password (development mode)"""
        # Create mock user without password
        mock_user = SimpleUser(
            user_id="dev_user", email="dev@example.com", password_hash=None
        )

        # Create mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Test authentication - should succeed in development mode
        result = authenticate_user(mock_db, "dev_user", "any_password")
        assert result is not None
        assert result.user_id == "dev_user"

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        # Create mock user with password
        mock_user = SimpleUser(
            user_id="test_user",
            email="test@example.com",
            password_hash=get_password_hash("correct_password"),
        )

        # Create mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Test authentication with wrong password
        result = authenticate_user(mock_db, "test_user", "wrong_password")
        assert result is None


class TestGetCurrentUser:
    """Test get_current_user function"""

    def test_get_current_user_no_credentials(self):
        """Test get_current_user with no credentials"""
        mock_db = Mock(spec=Session)

        result = get_current_user(credentials=None, db=mock_db)
        assert result is None

    def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token.here"
        )
        mock_db = Mock(spec=Session)

        result = get_current_user(credentials=mock_credentials, db=mock_db)
        assert result is None

    def test_get_current_user_no_user_id_in_payload(self):
        """Test get_current_user with token missing user_id"""
        # Create token without 'sub' claim
        data = {"role": "admin"}  # Missing 'sub'
        token = create_access_token(data)

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )
        mock_db = Mock(spec=Session)

        result = get_current_user(credentials=mock_credentials, db=mock_db)
        assert result is None

    def test_get_current_user_user_not_found(self):
        """Test get_current_user with valid token but user not in database"""
        data = {"sub": "nonexistent_user"}
        token = create_access_token(data)

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        # Create mock database session with no user
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = get_current_user(credentials=mock_credentials, db=mock_db)
        assert result is None

    def test_get_current_user_success(self):
        """Test successful get_current_user"""
        # Create mock user
        mock_user = SimpleUser(user_id="test_user", email="test@example.com")

        # Create valid token
        data = {"sub": "test_user"}
        token = create_access_token(data)

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        # Create mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = get_current_user(credentials=mock_credentials, db=mock_db)
        assert result is not None
        assert result.user_id == "test_user"


class TestRequireAuth:
    """Test require_auth function"""

    def test_require_auth_no_user(self):
        """Test require_auth raises exception when not authenticated"""
        mock_credentials = None
        mock_db = Mock(spec=Session)

        with pytest.raises(HTTPException) as exc_info:
            require_auth(credentials=mock_credentials, db=mock_db)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail

    def test_require_auth_invalid_token(self):
        """Test require_auth raises exception with invalid token"""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token.here"
        )
        mock_db = Mock(spec=Session)

        with pytest.raises(HTTPException) as exc_info:
            require_auth(credentials=mock_credentials, db=mock_db)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail

    def test_require_auth_success(self):
        """Test successful require_auth"""
        # Create mock user
        mock_user = SimpleUser(user_id="test_user", email="test@example.com")

        # Create valid token
        data = {"sub": "test_user"}
        token = create_access_token(data)

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        # Create mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = require_auth(credentials=mock_credentials, db=mock_db)
        assert result is not None
        assert result.user_id == "test_user"
