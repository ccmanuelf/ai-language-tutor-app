"""
Comprehensive tests for app/services/auth.py

Tests cover:
- Password management (hashing, verification, validation, generation)
- PIN management (generation, hashing, verification)
- JWT token management (creation, verification, refresh, revocation)
- Session management (creation, retrieval, updates, revocation)
- Authentication methods (user auth, child auth)
- FastAPI dependencies
- Convenience functions
- Security utilities (API keys, rate limiting)

Target: TRUE 100% coverage
"""

import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import jwt
import pytest
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials

from app.models.schemas import UserRoleEnum
from app.services.auth import (
    AuthConfig,
    AuthenticationService,
    RateLimiter,
    SessionData,
    TokenData,
    auth_config,
    auth_service,
    check_rate_limit,
    create_access_token,
    generate_api_key,
    generate_secure_token,
    get_current_active_user,
    get_current_user,
    hash_api_key,
    hash_password,
    rate_limiter,
    require_role,
    security,
    verify_api_key,
    verify_password,
    verify_token,
)

# ============================================================================
# TEST CLASS 1: AuthConfig
# ============================================================================


class TestAuthConfig:
    """Test AuthConfig initialization and attributes"""

    def test_auth_config_initialization(self):
        """Test AuthConfig initializes with correct defaults"""
        config = AuthConfig()

        assert config.ALGORITHM == "HS256"
        assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24
        assert config.REFRESH_TOKEN_EXPIRE_DAYS == 30
        assert config.PASSWORD_MIN_LENGTH == 8
        assert config.PASSWORD_MAX_LENGTH == 128
        assert config.SESSION_EXPIRE_HOURS == 12
        assert config.MAX_SESSIONS_PER_USER == 5
        assert config.CHILD_PIN_LENGTH == 4
        assert config.CHILD_SESSION_EXPIRE_HOURS == 8

    def test_auth_config_has_secret_key(self):
        """Test AuthConfig loads secret key from settings"""
        config = AuthConfig()
        assert hasattr(config, "SECRET_KEY")
        assert config.SECRET_KEY is not None


# ============================================================================
# TEST CLASS 2: Pydantic Models
# ============================================================================


class TestPydanticModels:
    """Test TokenData and SessionData Pydantic models"""

    def test_token_data_creation(self):
        """Test TokenData model creation"""
        now = datetime.now(timezone.utc)
        token_data = TokenData(
            user_id="user123",
            username="testuser",
            role=UserRoleEnum.CHILD,
            session_id="session123",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
        )

        assert token_data.user_id == "user123"
        assert token_data.username == "testuser"
        assert token_data.role == UserRoleEnum.CHILD
        assert token_data.session_id == "session123"

    def test_session_data_creation(self):
        """Test SessionData model creation"""
        now = datetime.now(timezone.utc)
        session_data = SessionData(
            session_id="session123",
            user_id="user123",
            device_info={"browser": "Chrome"},
            ip_address="127.0.0.1",
            created_at=now,
            last_activity=now,
            is_active=True,
        )

        assert session_data.session_id == "session123"
        assert session_data.user_id == "user123"
        assert session_data.device_info == {"browser": "Chrome"}
        assert session_data.ip_address == "127.0.0.1"
        assert session_data.is_active is True

    def test_session_data_default_values(self):
        """Test SessionData model with default values"""
        now = datetime.now(timezone.utc)
        session_data = SessionData(
            session_id="session123",
            user_id="user123",
            created_at=now,
            last_activity=now,
        )

        assert session_data.device_info == {}
        assert session_data.ip_address is None
        assert session_data.is_active is True


# ============================================================================
# TEST CLASS 3: Password Management
# ============================================================================


class TestPasswordManagement:
    """Test password hashing, verification, and validation"""

    def test_validate_password_strength_valid(self):
        """Test password validation with valid password"""
        service = AuthenticationService()
        assert service.validate_password_strength("Password123") is True

    def test_validate_password_strength_too_short(self):
        """Test password validation fails for short password"""
        service = AuthenticationService()
        assert service.validate_password_strength("Pass1") is False

    def test_validate_password_strength_too_long(self):
        """Test password validation fails for too long password"""
        service = AuthenticationService()
        long_password = "a" * 129
        assert service.validate_password_strength(long_password) is False

    def test_validate_password_strength_no_letter(self):
        """Test password validation fails without letters"""
        service = AuthenticationService()
        assert service.validate_password_strength("12345678") is False

    def test_validate_password_strength_no_number(self):
        """Test password validation fails without numbers"""
        service = AuthenticationService()
        assert service.validate_password_strength("PasswordOnly") is False

    def test_validate_password_strength_empty(self):
        """Test password validation fails for empty password"""
        service = AuthenticationService()
        assert service.validate_password_strength("") is False

    def test_hash_password_success(self):
        """Test password hashing with valid password"""
        service = AuthenticationService()
        password = "ValidPass123"
        hashed = service.hash_password(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_invalid_raises_error(self):
        """Test password hashing raises error for invalid password"""
        service = AuthenticationService()
        with pytest.raises(ValueError, match="does not meet security requirements"):
            service.hash_password("weak")

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        service = AuthenticationService()
        password = "CorrectPass123"
        hashed = service.hash_password(password)

        assert service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        service = AuthenticationService()
        password = "CorrectPass123"
        hashed = service.hash_password(password)

        assert service.verify_password("WrongPass123", hashed) is False

    @patch("app.services.auth.bcrypt.checkpw")
    def test_verify_password_exception_handling(self, mock_checkpw):
        """Test password verification handles exceptions gracefully"""
        mock_checkpw.side_effect = Exception("Bcrypt error")

        service = AuthenticationService()
        result = service.verify_password("any", "hash")

        assert result is False

    def test_generate_secure_password_default_length(self):
        """Test secure password generation with default length"""
        service = AuthenticationService()
        password = service.generate_secure_password()

        assert len(password) == 12
        # Password should contain characters from the allowed set
        allowed_chars = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        )
        assert all(c in allowed_chars for c in password)

    def test_generate_secure_password_custom_length(self):
        """Test secure password generation with custom length"""
        service = AuthenticationService()
        password = service.generate_secure_password(length=20)

        assert len(password) == 20


# ============================================================================
# TEST CLASS 4: PIN Management
# ============================================================================


class TestPINManagement:
    """Test PIN generation, hashing, and verification for child accounts"""

    def test_generate_child_pin(self):
        """Test child PIN generation"""
        service = AuthenticationService()
        pin = service.generate_child_pin()

        assert len(pin) == 4
        assert pin.isdigit()

    def test_hash_pin(self):
        """Test PIN hashing"""
        service = AuthenticationService()
        pin = "1234"
        hashed = service.hash_pin(pin)

        assert isinstance(hashed, str)
        assert hashed != pin
        assert len(hashed) == 64  # SHA256 hex digest length

    def test_verify_pin_correct(self):
        """Test PIN verification with correct PIN"""
        service = AuthenticationService()
        pin = "1234"
        hashed = service.hash_pin(pin)

        assert service.verify_pin(pin, hashed) is True

    def test_verify_pin_incorrect(self):
        """Test PIN verification with incorrect PIN"""
        service = AuthenticationService()
        pin = "1234"
        hashed = service.hash_pin(pin)

        assert service.verify_pin("9999", hashed) is False


# ============================================================================
# TEST CLASS 5: JWT Token Creation
# ============================================================================


class TestJWTTokenCreation:
    """Test JWT access and refresh token creation"""

    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry"""
        service = AuthenticationService()
        user_data = {"user_id": "user123", "username": "testuser"}
        token = service.create_access_token(user_data)

        assert isinstance(token, str)

        # Decode and verify (disable expiry check for testing)
        payload = jwt.decode(
            token,
            service.config.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        assert payload["user_id"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_custom_expiry(self):
        """Test access token creation with custom expiry"""
        service = AuthenticationService()
        user_data = {"user_id": "user123"}
        custom_delta = timedelta(hours=2)

        before_time = datetime.now(timezone.utc)
        token = service.create_access_token(user_data, expires_delta=custom_delta)
        after_time = datetime.now(timezone.utc)

        payload = jwt.decode(
            token,
            service.config.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Verify exp is approximately now + custom_delta (within 10 seconds for test execution)
        expected_min = before_time + custom_delta - timedelta(seconds=1)
        expected_max = after_time + custom_delta + timedelta(seconds=1)
        assert expected_min <= exp_time <= expected_max

    @patch("app.services.auth.jwt.encode")
    def test_create_access_token_encoding_error(self, mock_encode):
        """Test access token creation handles encoding errors"""
        mock_encode.side_effect = Exception("Encoding error")

        service = AuthenticationService()
        user_data = {"user_id": "user123"}

        with pytest.raises(HTTPException) as exc_info:
            service.create_access_token(user_data)

        assert exc_info.value.status_code == 500
        assert "Could not create access token" in str(exc_info.value.detail)

    @patch("app.services.auth.datetime")
    @patch("app.services.auth.secrets.token_urlsafe")
    def test_create_refresh_token(self, mock_token, mock_datetime):
        """Test refresh token creation"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now
        mock_token.return_value = "unique_jti_token"

        service = AuthenticationService()
        token = service.create_refresh_token("user123")

        assert isinstance(token, str)

        # Verify token is stored
        assert "unique_jti_token" in service.refresh_tokens
        assert service.refresh_tokens["unique_jti_token"]["user_id"] == "user123"
        assert service.refresh_tokens["unique_jti_token"]["is_active"] is True

    @patch("app.services.auth.jwt.encode")
    def test_create_refresh_token_encoding_error(self, mock_encode):
        """Test refresh token creation handles encoding errors"""
        mock_encode.side_effect = Exception("Encoding error")

        service = AuthenticationService()

        with pytest.raises(HTTPException) as exc_info:
            service.create_refresh_token("user123")

        assert exc_info.value.status_code == 500
        assert "Could not create refresh token" in str(exc_info.value.detail)


# ============================================================================
# TEST CLASS 6: JWT Token Verification
# ============================================================================


class TestJWTTokenVerification:
    """Test JWT token verification and validation"""

    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        service = AuthenticationService()
        user_data = {"user_id": "user123", "role": "parent"}
        token = service.create_access_token(user_data)

        payload = service.verify_token(token)

        assert payload["user_id"] == "user123"
        assert payload["role"] == "parent"
        assert payload["type"] == "access"

    def test_verify_token_expired(self):
        """Test token verification with expired token"""
        service = AuthenticationService()
        user_data = {"user_id": "user123"}

        # Create token that expired 1 hour ago
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        expired_token = jwt.encode(
            {"user_id": "user123", "exp": past_time},
            service.config.SECRET_KEY,
            algorithm="HS256",
        )

        with pytest.raises(HTTPException) as exc_info:
            service.verify_token(expired_token)

        assert exc_info.value.status_code == 401
        assert "Token has expired" in str(exc_info.value.detail)

    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        service = AuthenticationService()

        with pytest.raises(HTTPException) as exc_info:
            service.verify_token("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)


# ============================================================================
# TEST CLASS 7: Token Refresh and Revocation
# ============================================================================


class TestTokenRefreshAndRevocation:
    """Test refresh token operations and revocation"""

    @patch("app.services.auth.secrets.token_urlsafe")
    def test_refresh_access_token_success(self, mock_token):
        """Test refreshing access token with valid refresh token"""
        mock_token.side_effect = ["old_jti", "new_jti"]

        service = AuthenticationService()
        refresh_token = service.create_refresh_token("user123")

        new_access, new_refresh = service.refresh_access_token(refresh_token)

        assert isinstance(new_access, str)
        assert isinstance(new_refresh, str)

        # Verify old token was revoked
        assert service.refresh_tokens["old_jti"]["is_active"] is False

        # Verify new token is active
        assert service.refresh_tokens["new_jti"]["is_active"] is True

    def test_refresh_access_token_invalid_type(self):
        """Test refresh fails with access token instead of refresh token"""
        service = AuthenticationService()
        access_token = service.create_access_token({"user_id": "user123"})

        with pytest.raises(HTTPException) as exc_info:
            service.refresh_access_token(access_token)

        assert exc_info.value.status_code == 401
        assert "Invalid refresh token" in str(exc_info.value.detail)

    @patch("app.services.auth.secrets.token_urlsafe")
    def test_refresh_access_token_revoked(self, mock_token):
        """Test refresh fails with revoked refresh token"""
        mock_token.return_value = "jti123"

        service = AuthenticationService()
        refresh_token = service.create_refresh_token("user123")

        # Revoke the token
        service.refresh_tokens["jti123"]["is_active"] = False

        with pytest.raises(HTTPException) as exc_info:
            service.refresh_access_token(refresh_token)

        assert exc_info.value.status_code == 401
        assert "has been revoked" in str(exc_info.value.detail)

    def test_refresh_access_token_missing_jti(self):
        """Test refresh fails when JTI not found"""
        service = AuthenticationService()

        # Create a token without JTI in storage
        token_data = {
            "user_id": "user123",
            "type": "refresh",
            "jti": "nonexistent_jti",
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
            "iat": datetime.now(timezone.utc),
        }
        refresh_token = jwt.encode(
            token_data, service.config.SECRET_KEY, algorithm="HS256"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.refresh_access_token(refresh_token)

        assert exc_info.value.status_code == 401

    def test_refresh_access_token_expired(self):
        """Test refresh fails with expired refresh token"""
        service = AuthenticationService()

        past_time = datetime.now(timezone.utc) - timedelta(days=31)
        expired_refresh = jwt.encode(
            {"user_id": "user123", "type": "refresh", "exp": past_time},
            service.config.SECRET_KEY,
            algorithm="HS256",
        )

        with pytest.raises(HTTPException) as exc_info:
            service.refresh_access_token(expired_refresh)

        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()

    @patch("app.services.auth.secrets.token_urlsafe")
    def test_revoke_refresh_token_success(self, mock_token):
        """Test refresh token revocation"""
        mock_token.return_value = "jti123"

        service = AuthenticationService()
        refresh_token = service.create_refresh_token("user123")

        result = service.revoke_refresh_token(refresh_token)

        assert result is True
        assert service.refresh_tokens["jti123"]["is_active"] is False

    def test_revoke_refresh_token_nonexistent(self):
        """Test revoking nonexistent refresh token returns False"""
        service = AuthenticationService()

        token_data = {
            "jti": "nonexistent",
            "user_id": "user123",
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        }
        fake_token = jwt.encode(
            token_data, service.config.SECRET_KEY, algorithm="HS256"
        )

        result = service.revoke_refresh_token(fake_token)

        assert result is False

    @patch("app.services.auth.jwt.decode")
    def test_revoke_refresh_token_exception(self, mock_decode):
        """Test refresh token revocation handles exceptions"""
        mock_decode.side_effect = Exception("Decode error")

        service = AuthenticationService()
        result = service.revoke_refresh_token("invalid_token")

        assert result is False


# ============================================================================
# TEST CLASS 8: Session Management
# ============================================================================


class TestSessionManagement:
    """Test session creation, retrieval, and management"""

    @patch("app.services.auth.secrets.token_urlsafe")
    @patch("app.services.auth.datetime")
    def test_create_session_basic(self, mock_datetime, mock_token):
        """Test basic session creation"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now
        mock_token.return_value = "session123"

        service = AuthenticationService()
        session_id = service.create_session("user123")

        assert session_id == "session123"
        assert "session123" in service.active_sessions

        session = service.active_sessions["session123"]
        assert session.user_id == "user123"
        assert session.is_active is True
        assert session.device_info == {}

    @patch("app.services.auth.secrets.token_urlsafe")
    @patch("app.services.auth.datetime")
    def test_create_session_with_details(self, mock_datetime, mock_token):
        """Test session creation with device info and IP"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now
        mock_token.return_value = "session123"

        service = AuthenticationService()
        device_info = {"browser": "Chrome", "os": "Linux"}
        session_id = service.create_session(
            "user123", device_info=device_info, ip_address="192.168.1.1"
        )

        session = service.active_sessions[session_id]
        assert session.device_info == device_info
        assert session.ip_address == "192.168.1.1"

    @patch("app.services.auth.secrets.token_urlsafe")
    @patch("app.services.auth.datetime")
    def test_create_session_max_sessions_limit(self, mock_datetime, mock_token):
        """Test session creation enforces max sessions per user"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        # Create session IDs
        session_ids = [f"session{i}" for i in range(6)]
        mock_token.side_effect = session_ids

        service = AuthenticationService()

        # Create MAX_SESSIONS_PER_USER sessions
        for i in range(service.config.MAX_SESSIONS_PER_USER):
            service.create_session("user123")

        # All sessions should be active
        active_count = sum(
            1
            for s in service.active_sessions.values()
            if s.user_id == "user123" and s.is_active
        )
        assert active_count == service.config.MAX_SESSIONS_PER_USER

        # Create one more session - should deactivate oldest
        service.create_session("user123")

        # Still only MAX_SESSIONS_PER_USER active
        active_count = sum(
            1
            for s in service.active_sessions.values()
            if s.user_id == "user123" and s.is_active
        )
        assert active_count == service.config.MAX_SESSIONS_PER_USER

    @patch("app.services.auth.datetime")
    def test_get_session_active(self, mock_datetime):
        """Test retrieving an active session"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()
        session_id = service.create_session("user123")

        session = service.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id
        assert session.is_active is True

    def test_get_session_nonexistent(self):
        """Test retrieving nonexistent session returns None"""
        service = AuthenticationService()
        session = service.get_session("nonexistent")

        assert session is None

    @patch("app.services.auth.datetime")
    def test_get_session_inactive(self, mock_datetime):
        """Test retrieving inactive session returns None"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()
        session_id = service.create_session("user123")

        # Deactivate session
        service.active_sessions[session_id].is_active = False

        session = service.get_session(session_id)

        assert session is None

    @patch("app.services.auth.datetime")
    def test_get_session_expired(self, mock_datetime):
        """Test retrieving expired session returns None and deactivates it"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()
        session_id = service.create_session("user123")

        # Move time forward past expiration
        future = now + timedelta(hours=service.config.SESSION_EXPIRE_HOURS + 1)
        mock_datetime.now.return_value = future

        session = service.get_session(session_id)

        assert session is None
        assert service.active_sessions[session_id].is_active is False

    @patch("app.services.auth.datetime")
    def test_update_session_activity_success(self, mock_datetime):
        """Test updating session activity timestamp"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()
        session_id = service.create_session("user123")

        # Move time forward
        later = now + timedelta(hours=1)
        mock_datetime.now.return_value = later

        result = service.update_session_activity(session_id)

        assert result is True
        assert service.active_sessions[session_id].last_activity == later

    def test_update_session_activity_nonexistent(self):
        """Test updating nonexistent session returns False"""
        service = AuthenticationService()
        result = service.update_session_activity("nonexistent")

        assert result is False

    @patch("app.services.auth.datetime")
    def test_update_session_activity_inactive(self, mock_datetime):
        """Test updating inactive session returns False"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()
        session_id = service.create_session("user123")
        service.active_sessions[session_id].is_active = False

        result = service.update_session_activity(session_id)

        assert result is False

    @patch("app.services.auth.datetime")
    def test_revoke_session_success(self, mock_datetime):
        """Test session revocation"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()
        session_id = service.create_session("user123")

        result = service.revoke_session(session_id)

        assert result is True
        assert service.active_sessions[session_id].is_active is False

    def test_revoke_session_nonexistent(self):
        """Test revoking nonexistent session returns False"""
        service = AuthenticationService()
        result = service.revoke_session("nonexistent")

        assert result is False

    @patch("app.services.auth.datetime")
    def test_revoke_all_user_sessions(self, mock_datetime):
        """Test revoking all sessions for a user"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()

        # Create multiple sessions for user123
        service.create_session("user123")
        service.create_session("user123")
        service.create_session("user456")  # Different user

        count = service.revoke_all_user_sessions("user123")

        assert count == 2

        # Verify user123 sessions are inactive
        for session in service.active_sessions.values():
            if session.user_id == "user123":
                assert session.is_active is False
            elif session.user_id == "user456":
                assert session.is_active is True

    @patch("app.services.auth.datetime")
    def test_cleanup_expired_sessions(self, mock_datetime):
        """Test cleaning up expired sessions and refresh tokens"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()

        # Create sessions
        session1 = service.create_session("user123")
        session2 = service.create_session("user456")

        # Create refresh token
        service.refresh_tokens["old_token"] = {
            "user_id": "user123",
            "created_at": now,
            "is_active": True,
        }

        # Move time forward past expiration
        future = now + timedelta(days=service.config.REFRESH_TOKEN_EXPIRE_DAYS + 1)
        mock_datetime.now.return_value = future

        count = service.cleanup_expired_sessions()

        # Sessions should be deactivated
        assert service.active_sessions[session1].is_active is False
        assert service.active_sessions[session2].is_active is False

        # Old refresh token should be deleted
        assert "old_token" not in service.refresh_tokens


# ============================================================================
# TEST CLASS 9: Authentication Methods
# ============================================================================


class TestAuthenticationMethods:
    """Test user authentication and child PIN authentication"""

    @patch("app.services.auth.secrets.token_urlsafe")
    @patch("app.services.auth.datetime")
    def test_authenticate_user_success(self, mock_datetime, mock_token):
        """Test successful user authentication"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now
        mock_token.side_effect = ["session123", "jti123"]

        service = AuthenticationService()
        password = "ValidPass123"
        hashed = service.hash_password(password)

        user_data = {
            "password_hash": hashed,
            "username": "testuser",
            "role": "parent",
        }

        result = service.authenticate_user("user123", password, user_data)

        assert result["access_token"] is not None
        assert result["refresh_token"] is not None
        assert result["token_type"] == "bearer"
        assert result["session_id"] == "session123"
        assert result["expires_in"] == service.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def test_authenticate_user_wrong_password(self):
        """Test user authentication with wrong password raises error"""
        service = AuthenticationService()
        password = "ValidPass123"
        hashed = service.hash_password(password)

        user_data = {
            "password_hash": hashed,
            "username": "testuser",
            "role": "parent",
        }

        with pytest.raises(HTTPException) as exc_info:
            service.authenticate_user("user123", "WrongPass123", user_data)

        assert exc_info.value.status_code == 401
        assert "Incorrect username or password" in str(exc_info.value.detail)

    @patch("app.services.auth.secrets.token_urlsafe")
    @patch("app.services.auth.datetime")
    def test_authenticate_child_pin_success(self, mock_datetime, mock_token):
        """Test successful child PIN authentication"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now
        mock_token.return_value = "session123"

        service = AuthenticationService()
        pin = "1234"
        hashed_pin = service.hash_pin(pin)

        user_data = {
            "pin_hash": hashed_pin,
            "username": "childuser",
            "role": "child",
        }

        result = service.authenticate_child_pin("user456", pin, user_data)

        assert result["access_token"] is not None
        assert result["token_type"] == "bearer"
        assert result["session_id"] == "session123"
        assert result["expires_in"] == service.config.CHILD_SESSION_EXPIRE_HOURS * 3600
        assert "refresh_token" not in result  # Children don't get refresh tokens

    def test_authenticate_child_pin_wrong_pin(self):
        """Test child authentication with wrong PIN raises error"""
        service = AuthenticationService()
        pin = "1234"
        hashed_pin = service.hash_pin(pin)

        user_data = {
            "pin_hash": hashed_pin,
            "username": "childuser",
            "role": "child",
        }

        with pytest.raises(HTTPException) as exc_info:
            service.authenticate_child_pin("user456", "9999", user_data)

        assert exc_info.value.status_code == 401
        assert "Incorrect PIN" in str(exc_info.value.detail)

    def test_authenticate_child_pin_no_pin_hash(self):
        """Test child authentication without PIN hash raises error"""
        service = AuthenticationService()

        user_data = {
            "username": "childuser",
            "role": "child",
        }

        with pytest.raises(HTTPException) as exc_info:
            service.authenticate_child_pin("user456", "1234", user_data)

        assert exc_info.value.status_code == 401

    @patch("app.services.auth.secrets.token_urlsafe")
    def test_get_current_user_from_token_success(self, mock_token):
        """Test getting current user from valid token"""
        mock_token.return_value = "session123"

        service = AuthenticationService()
        session_id = service.create_session("user123")

        token_data = {
            "user_id": "user123",
            "username": "testuser",
            "session_id": session_id,
        }
        token = service.create_access_token(token_data)

        user_data = service.get_current_user_from_token(token)

        assert user_data["user_id"] == "user123"
        assert user_data["username"] == "testuser"
        assert user_data["session_id"] == session_id

    def test_get_current_user_from_token_refresh_type(self):
        """Test getting user from refresh token raises error"""
        service = AuthenticationService()
        refresh_token = service.create_refresh_token("user123")

        with pytest.raises(HTTPException) as exc_info:
            service.get_current_user_from_token(refresh_token)

        assert exc_info.value.status_code == 401
        assert "Invalid token type" in str(exc_info.value.detail)

    def test_get_current_user_from_token_expired_session(self):
        """Test getting user with expired session raises error"""
        service = AuthenticationService()
        session_id = service.create_session("user123")

        token_data = {
            "user_id": "user123",
            "session_id": session_id,
        }
        token = service.create_access_token(token_data)

        # Manually expire the session by setting last_activity in the past
        service.active_sessions[session_id].last_activity = datetime.now(
            timezone.utc
        ) - timedelta(hours=service.config.SESSION_EXPIRE_HOURS + 1)

        with pytest.raises(HTTPException) as exc_info:
            service.get_current_user_from_token(token)

        assert exc_info.value.status_code == 401
        assert "Session has expired" in str(exc_info.value.detail)

    def test_get_current_user_from_token_no_session_id(self):
        """Test getting user from token without session_id"""
        service = AuthenticationService()

        token_data = {"user_id": "user123"}
        token = service.create_access_token(token_data)

        user_data = service.get_current_user_from_token(token)

        assert user_data["user_id"] == "user123"


# ============================================================================
# TEST CLASS 10: FastAPI Dependencies
# ============================================================================


class TestFastAPIDependencies:
    """Test FastAPI dependency functions for authentication"""

    @pytest.mark.asyncio
    async def test_get_current_user_with_credentials(self):
        """Test get_current_user dependency with valid credentials"""
        service = AuthenticationService()
        token = service.create_access_token(
            {"user_id": "user123", "username": "testuser"}
        )

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user(credentials)

        assert user["user_id"] == "user123"
        assert user["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test get_current_user dependency without credentials raises error"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_active_user(self):
        """Test get_current_active_user dependency"""
        current_user = {"user_id": "user123", "username": "testuser"}

        active_user = await get_current_active_user(current_user)

        assert active_user == current_user

    @pytest.mark.asyncio
    async def test_require_role_success(self):
        """Test require_role dependency with correct role"""
        current_user = {"user_id": "user123", "role": "parent"}

        role_checker = await require_role(UserRoleEnum.PARENT)
        user = role_checker(current_user)

        assert user == current_user

    @pytest.mark.asyncio
    async def test_require_role_wrong_role(self):
        """Test require_role dependency with wrong role raises error"""
        current_user = {"user_id": "user123", "role": "child"}

        role_checker = await require_role(UserRoleEnum.PARENT)

        with pytest.raises(HTTPException) as exc_info:
            role_checker(current_user)

        assert exc_info.value.status_code == 403
        assert "requires parent role" in str(exc_info.value.detail)


# ============================================================================
# TEST CLASS 11: Convenience Functions
# ============================================================================


class TestConvenienceFunctions:
    """Test module-level convenience functions"""

    def test_hash_password_convenience(self):
        """Test convenience hash_password function"""
        password = "ValidPass123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert hashed != password

    def test_verify_password_convenience(self):
        """Test convenience verify_password function"""
        password = "ValidPass123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("WrongPass123", hashed) is False

    def test_create_access_token_convenience(self):
        """Test convenience create_access_token function"""
        user_data = {"user_id": "user123"}
        token = create_access_token(user_data)

        assert isinstance(token, str)

    def test_verify_token_convenience(self):
        """Test convenience verify_token function"""
        user_data = {"user_id": "user123", "role": "parent"}
        token = create_access_token(user_data)

        payload = verify_token(token)

        assert payload["user_id"] == "user123"
        assert payload["role"] == "parent"


# ============================================================================
# TEST CLASS 12: Security Utilities
# ============================================================================


class TestSecurityUtilities:
    """Test security utility functions"""

    def test_generate_secure_token_default_length(self):
        """Test secure token generation with default length"""
        token = generate_secure_token()

        # URL-safe base64 encoding of 32 bytes
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_secure_token_custom_length(self):
        """Test secure token generation with custom length"""
        token = generate_secure_token(length=16)

        assert isinstance(token, str)

    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = generate_api_key()

        assert isinstance(api_key, str)
        assert api_key.startswith("ak_")

    def test_hash_api_key(self):
        """Test API key hashing"""
        api_key = "ak_testkey123"
        hashed = hash_api_key(api_key)

        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA256 hex digest

    def test_verify_api_key_correct(self):
        """Test API key verification with correct key"""
        api_key = "ak_testkey123"
        hashed = hash_api_key(api_key)

        assert verify_api_key(api_key, hashed) is True

    def test_verify_api_key_incorrect(self):
        """Test API key verification with incorrect key"""
        api_key = "ak_testkey123"
        hashed = hash_api_key(api_key)

        assert verify_api_key("ak_wrongkey", hashed) is False


# ============================================================================
# TEST CLASS 13: Rate Limiting
# ============================================================================


class TestRateLimiting:
    """Test RateLimiter class and rate limiting functionality"""

    @patch("app.services.auth.datetime")
    def test_rate_limiter_allows_within_limit(self, mock_datetime):
        """Test rate limiter allows requests within limit"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        limiter = RateLimiter()

        # Make requests within limit
        for i in range(10):
            result = limiter.is_allowed("test_key", max_requests=10, window_seconds=60)
            assert result is True

    @patch("app.services.auth.datetime")
    def test_rate_limiter_blocks_over_limit(self, mock_datetime):
        """Test rate limiter blocks requests over limit"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        limiter = RateLimiter()

        # Make requests up to limit
        for i in range(5):
            limiter.is_allowed("test_key", max_requests=5, window_seconds=60)

        # Next request should be blocked
        result = limiter.is_allowed("test_key", max_requests=5, window_seconds=60)
        assert result is False

    @patch("app.services.auth.datetime")
    def test_rate_limiter_resets_after_window(self, mock_datetime):
        """Test rate limiter resets after time window"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        limiter = RateLimiter()

        # Make requests up to limit
        for i in range(5):
            limiter.is_allowed("test_key", max_requests=5, window_seconds=60)

        # Should be blocked
        result = limiter.is_allowed("test_key", max_requests=5, window_seconds=60)
        assert result is False

        # Move time forward past window
        future = now + timedelta(seconds=61)
        mock_datetime.now.return_value = future

        # Should be allowed again
        result = limiter.is_allowed("test_key", max_requests=5, window_seconds=60)
        assert result is True

    @patch("app.services.auth.datetime")
    def test_rate_limiter_different_keys_independent(self, mock_datetime):
        """Test rate limiter treats different keys independently"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        limiter = RateLimiter()

        # Max out key1
        for i in range(5):
            limiter.is_allowed("key1", max_requests=5, window_seconds=60)

        # key1 should be blocked
        assert limiter.is_allowed("key1", max_requests=5, window_seconds=60) is False

        # key2 should still be allowed
        assert limiter.is_allowed("key2", max_requests=5, window_seconds=60) is True

    def test_check_rate_limit_within_limit(self):
        """Test check_rate_limit allows request within limit"""
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"

        # Reset rate limiter
        rate_limiter.requests.clear()

        # Should not raise
        check_rate_limit(request, max_requests=100, window_seconds=3600)

    @patch("app.services.auth.rate_limiter.is_allowed")
    def test_check_rate_limit_over_limit(self, mock_is_allowed):
        """Test check_rate_limit raises exception over limit"""
        mock_is_allowed.return_value = False

        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"

        with pytest.raises(HTTPException) as exc_info:
            check_rate_limit(request, max_requests=100, window_seconds=3600)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail)


# ============================================================================
# TEST CLASS 14: Global Instances
# ============================================================================


class TestGlobalInstances:
    """Test global service instances and singletons"""

    def test_global_auth_config_exists(self):
        """Test global auth_config instance exists"""
        assert auth_config is not None
        assert isinstance(auth_config, AuthConfig)

    def test_global_auth_service_exists(self):
        """Test global auth_service instance exists"""
        assert auth_service is not None
        assert isinstance(auth_service, AuthenticationService)

    def test_global_security_bearer_exists(self):
        """Test global security HTTPBearer instance exists"""
        from fastapi.security import HTTPBearer

        assert security is not None
        assert isinstance(security, HTTPBearer)

    def test_global_rate_limiter_exists(self):
        """Test global rate_limiter instance exists"""
        assert rate_limiter is not None
        assert isinstance(rate_limiter, RateLimiter)


# ============================================================================
# TEST CLASS 15: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and comprehensive error handling"""

    def test_validate_password_strength_boundary_min_length(self):
        """Test password at exact minimum length boundary"""
        service = AuthenticationService()
        # Exactly 8 chars with letter and number
        assert service.validate_password_strength("Pass123!") is True

    def test_validate_password_strength_boundary_max_length(self):
        """Test password at exact maximum length boundary"""
        service = AuthenticationService()
        # Exactly 128 chars
        password = "a" * 127 + "1"
        assert service.validate_password_strength(password) is True

    def test_session_data_model_empty_device_info(self):
        """Test SessionData with explicitly empty device_info"""
        now = datetime.now(timezone.utc)
        session = SessionData(
            session_id="test",
            user_id="user123",
            device_info={},
            created_at=now,
            last_activity=now,
        )
        assert session.device_info == {}

    @patch("app.services.auth.datetime")
    def test_cleanup_no_expired_items(self, mock_datetime):
        """Test cleanup with no expired items returns 0"""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = now

        service = AuthenticationService()

        # Create fresh session
        service.create_session("user123")

        # No time has passed
        count = service.cleanup_expired_sessions()

        assert count == 0

    def test_token_data_model_with_all_fields(self):
        """Test TokenData model with all fields populated"""
        now = datetime.now(timezone.utc)
        token = TokenData(
            user_id="user123",
            username="testuser",
            role=UserRoleEnum.PARENT,
            session_id="session123",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
        )

        assert token.user_id == "user123"
        assert token.username == "testuser"
        assert token.role == UserRoleEnum.PARENT

    def test_multiple_cleanup_calls_idempotent(self):
        """Test multiple cleanup calls count expired sessions each time"""
        service = AuthenticationService()
        session_id = service.create_session("user123")

        # Manually expire session by setting last_activity to the past
        service.active_sessions[session_id].last_activity = datetime.now(
            timezone.utc
        ) - timedelta(hours=service.config.SESSION_EXPIRE_HOURS + 1)

        count1 = service.cleanup_expired_sessions()
        count2 = service.cleanup_expired_sessions()

        # Both calls find the expired session (implementation doesn't skip already inactive)
        assert count1 == 1
        assert count2 == 1

        # But session is marked inactive
        assert service.active_sessions[session_id].is_active is False


# ============================================================================
# TEST CLASS 16: Additional Coverage for Missing Lines
# ============================================================================


class TestMissingCoverageLines:
    """Tests to achieve TRUE 100% coverage"""

    def test_refresh_access_token_invalid_token_error(self):
        """Test refresh_access_token handles jwt.InvalidTokenError"""
        service = AuthenticationService()

        # Create a malformed token that will raise InvalidTokenError
        with pytest.raises(HTTPException) as exc_info:
            service.refresh_access_token("completely.invalid.token")

        assert exc_info.value.status_code == 401
        assert "Invalid refresh token" in str(exc_info.value.detail)

    @patch("app.services.auth.secrets.token_urlsafe")
    def test_cleanup_expired_refresh_tokens(self, mock_token):
        """Test cleanup_expired_sessions removes old refresh tokens"""
        mock_token.return_value = "test_jti"

        service = AuthenticationService()

        # Create a refresh token
        service.create_refresh_token("user123")

        # Manually set created_at to past expiry
        service.refresh_tokens["test_jti"]["created_at"] = datetime.now(
            timezone.utc
        ) - timedelta(days=service.config.REFRESH_TOKEN_EXPIRE_DAYS + 1)

        # Cleanup should delete the token
        count = service.cleanup_expired_sessions()

        assert count == 1
        assert "test_jti" not in service.refresh_tokens

    def test_cleanup_no_refresh_tokens_to_clean(self):
        """Test cleanup when there are no expired refresh tokens"""
        service = AuthenticationService()

        # Don't create any refresh tokens, just a session
        session_id = service.create_session("user123")

        # Don't expire anything
        count = service.cleanup_expired_sessions()

        # Should be 0 since nothing is expired
        assert count == 0
