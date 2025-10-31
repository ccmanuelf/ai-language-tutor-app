"""
Comprehensive tests for auth.py - Authentication Service

Focus on reaching 90%+ coverage by testing all authentication functions,
token management, session handling, and security features.

Target: 60% -> 90%+ coverage (105 uncovered lines to cover)
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from app.models.schemas import UserRoleEnum
from app.services.auth import (
    AuthConfig,
    AuthenticationService,
    SessionData,
    TokenData,
    create_access_token,
    generate_api_key,
    generate_secure_token,
    hash_password,
    verify_password,
    verify_token,
)


class TestPasswordValidation:
    """Test password validation and strength checking"""

    def setup_method(self):
        self.auth = AuthenticationService()

    def test_validate_password_strength_empty(self):
        """Test password validation with empty password"""
        assert self.auth.validate_password_strength("") is False

    def test_validate_password_strength_too_short(self):
        """Test password validation with too short password"""
        assert self.auth.validate_password_strength("Pass1") is False

    def test_validate_password_strength_too_long(self):
        """Test password validation with too long password"""
        long_pass = "A1" + "x" * 200
        assert self.auth.validate_password_strength(long_pass) is False

    def test_validate_password_strength_no_letter(self):
        """Test password validation with no letters"""
        assert self.auth.validate_password_strength("12345678") is False

    def test_validate_password_strength_no_number(self):
        """Test password validation with no numbers"""
        assert self.auth.validate_password_strength("password") is False

    def test_validate_password_strength_valid(self):
        """Test password validation with valid password"""
        assert self.auth.validate_password_strength("Password123") is True
        assert self.auth.validate_password_strength("Test1234") is True

    def test_hash_password_weak_raises_error(self):
        """Test hashing weak password raises ValueError"""
        with pytest.raises(
            ValueError, match="Password does not meet security requirements"
        ):
            self.auth.hash_password("weak")

    def test_verify_password_exception_handling(self):
        """Test password verification handles exceptions gracefully"""
        # Invalid hash format should return False, not raise
        result = self.auth.verify_password("test", "invalid_hash")
        assert result is False


class TestSecurePasswordGeneration:
    """Test secure password and PIN generation"""

    def setup_method(self):
        self.auth = AuthenticationService()

    def test_generate_secure_password_default_length(self):
        """Test generating secure password with default length"""
        password = self.auth.generate_secure_password()
        assert len(password) == 12
        # Check contains only allowed characters (letters, numbers, special chars)
        allowed_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        )
        assert all(c in allowed_chars for c in password)

    def test_generate_secure_password_custom_length(self):
        """Test generating secure password with custom length"""
        password = self.auth.generate_secure_password(length=20)
        assert len(password) == 20

    def test_generate_child_pin(self):
        """Test generating 4-digit PIN for children"""
        pin = self.auth.generate_child_pin()
        assert len(pin) == 4
        assert pin.isdigit()

    def test_pin_hashing_and_verification(self):
        """Test PIN hashing and verification"""
        pin = "1234"
        hashed_pin = self.auth.hash_pin(pin)

        assert isinstance(hashed_pin, str)
        assert len(hashed_pin) > 0
        assert self.auth.verify_pin(pin, hashed_pin) is True
        assert self.auth.verify_pin("9999", hashed_pin) is False


class TestJWTTokenManagement:
    """Test JWT token creation and verification"""

    def setup_method(self):
        self.auth = AuthenticationService()

    def test_create_access_token_with_custom_expiry(self):
        """Test creating access token with custom expiration"""
        user_data = {"user_id": "123", "username": "testuser"}
        expires_delta = timedelta(minutes=30)

        token = self.auth.create_access_token(user_data, expires_delta)

        assert isinstance(token, str)
        payload = jwt.decode(token, self.auth.config.SECRET_KEY, algorithms=["HS256"])
        assert payload["user_id"] == "123"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        user_id = "user_123"

        refresh_token = self.auth.create_refresh_token(user_id)

        assert isinstance(refresh_token, str)
        payload = jwt.decode(
            refresh_token, self.auth.config.SECRET_KEY, algorithms=["HS256"]
        )
        assert payload["user_id"] == user_id
        assert payload["type"] == "refresh"
        assert "jti" in payload

        # Verify token is stored in refresh_tokens dict
        jti = payload["jti"]
        assert jti in self.auth.refresh_tokens
        assert self.auth.refresh_tokens[jti]["is_active"] is True

    def test_verify_token_expired(self):
        """Test verifying expired token raises HTTPException"""
        # Create token that expires immediately
        user_data = {"user_id": "123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = self.auth.create_access_token(user_data, expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            self.auth.verify_token(token)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_token_invalid(self):
        """Test verifying invalid token raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            self.auth.verify_token("invalid.token.here")
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()

    def test_refresh_access_token_success(self):
        """Test refreshing access token with valid refresh token"""
        user_id = "user_456"
        refresh_token = self.auth.create_refresh_token(user_id)

        new_access_token, new_refresh_token = self.auth.refresh_access_token(
            refresh_token
        )

        assert isinstance(new_access_token, str)
        assert isinstance(new_refresh_token, str)
        assert new_access_token != new_refresh_token

        # Verify old refresh token is revoked
        old_payload = jwt.decode(
            refresh_token, self.auth.config.SECRET_KEY, algorithms=["HS256"]
        )
        old_jti = old_payload["jti"]
        assert self.auth.refresh_tokens[old_jti]["is_active"] is False

    def test_refresh_access_token_wrong_type(self):
        """Test refreshing with access token (not refresh token) fails"""
        user_data = {"user_id": "123"}
        access_token = self.auth.create_access_token(user_data)

        with pytest.raises(HTTPException) as exc_info:
            self.auth.refresh_access_token(access_token)
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()

    def test_refresh_access_token_revoked(self):
        """Test refreshing with revoked token fails"""
        user_id = "user_789"
        refresh_token = self.auth.create_refresh_token(user_id)

        # Revoke the token
        self.auth.revoke_refresh_token(refresh_token)

        # Try to refresh with revoked token
        with pytest.raises(HTTPException) as exc_info:
            self.auth.refresh_access_token(refresh_token)
        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

    def test_revoke_refresh_token_success(self):
        """Test revoking refresh token"""
        user_id = "user_revoke"
        refresh_token = self.auth.create_refresh_token(user_id)

        result = self.auth.revoke_refresh_token(refresh_token)

        assert result is True
        payload = jwt.decode(
            refresh_token, self.auth.config.SECRET_KEY, algorithms=["HS256"]
        )
        jti = payload["jti"]
        assert self.auth.refresh_tokens[jti]["is_active"] is False

    def test_revoke_refresh_token_invalid(self):
        """Test revoking invalid refresh token returns False"""
        result = self.auth.revoke_refresh_token("invalid.token")
        assert result is False


class TestSessionManagement:
    """Test session creation, retrieval, and management"""

    def setup_method(self):
        self.auth = AuthenticationService()

    def test_create_session_basic(self):
        """Test creating basic session"""
        user_id = "user_123"

        session_id = self.auth.create_session(user_id)

        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert session_id in self.auth.active_sessions

        session = self.auth.active_sessions[session_id]
        assert session.user_id == user_id
        assert session.is_active is True

    def test_create_session_with_device_info(self):
        """Test creating session with device information"""
        user_id = "user_456"
        device_info = {"browser": "Chrome", "os": "macOS"}
        ip_address = "192.168.1.1"

        session_id = self.auth.create_session(user_id, device_info, ip_address)

        session = self.auth.active_sessions[session_id]
        assert session.device_info == device_info
        assert session.ip_address == ip_address

    def test_create_session_max_sessions_limit(self):
        """Test session cleanup when max sessions reached"""
        user_id = "user_multi"

        # Create MAX_SESSIONS_PER_USER + 1 sessions
        session_ids = []
        for i in range(self.auth.config.MAX_SESSIONS_PER_USER + 1):
            session_id = self.auth.create_session(user_id)
            session_ids.append(session_id)

        # First session should be deactivated
        first_session = self.auth.active_sessions[session_ids[0]]
        assert first_session.is_active is False

    def test_get_session_valid(self):
        """Test getting valid active session"""
        user_id = "user_get"
        session_id = self.auth.create_session(user_id)

        session = self.auth.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id
        assert session.user_id == user_id

    def test_get_session_nonexistent(self):
        """Test getting nonexistent session returns None"""
        session = self.auth.get_session("nonexistent_session_id")
        assert session is None

    def test_get_session_expired(self):
        """Test getting expired session returns None"""
        user_id = "user_expired"
        session_id = self.auth.create_session(user_id)

        # Manually expire session by setting old last_activity
        session = self.auth.active_sessions[session_id]
        session.last_activity = datetime.now(timezone.utc) - timedelta(hours=24)

        # Try to get expired session
        result = self.auth.get_session(session_id)

        assert result is None
        assert session.is_active is False

    def test_update_session_activity_success(self):
        """Test updating session activity timestamp"""
        user_id = "user_activity"
        session_id = self.auth.create_session(user_id)

        original_activity = self.auth.active_sessions[session_id].last_activity

        # Update activity
        result = self.auth.update_session_activity(session_id)

        assert result is True
        new_activity = self.auth.active_sessions[session_id].last_activity
        assert new_activity >= original_activity

    def test_update_session_activity_inactive(self):
        """Test updating inactive session fails"""
        user_id = "user_inactive"
        session_id = self.auth.create_session(user_id)
        self.auth.active_sessions[session_id].is_active = False

        result = self.auth.update_session_activity(session_id)
        assert result is False

    def test_revoke_session_success(self):
        """Test revoking session"""
        user_id = "user_revoke_session"
        session_id = self.auth.create_session(user_id)

        result = self.auth.revoke_session(session_id)

        assert result is True
        assert self.auth.active_sessions[session_id].is_active is False

    def test_revoke_session_nonexistent(self):
        """Test revoking nonexistent session returns False"""
        result = self.auth.revoke_session("nonexistent")
        assert result is False

    def test_revoke_all_user_sessions(self):
        """Test revoking all sessions for a user"""
        user_id = "user_revoke_all"

        # Create multiple sessions
        session_ids = [self.auth.create_session(user_id) for _ in range(3)]

        # Revoke all sessions
        count = self.auth.revoke_all_user_sessions(user_id)

        assert count == 3
        for session_id in session_ids:
            assert self.auth.active_sessions[session_id].is_active is False


class TestAuthenticationMethods:
    """Test user authentication methods"""

    def setup_method(self):
        self.auth = AuthenticationService()

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        password = "TestPassword123"
        hashed_password = self.auth.hash_password(password)

        user_data = {
            "password_hash": hashed_password,
            "username": "testuser",
            "role": "user",
        }

        result = self.auth.authenticate_user("user_123", password, user_data)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert "session_id" in result
        assert isinstance(result["expires_in"], int)

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password fails"""
        password = "TestPassword123"
        hashed_password = self.auth.hash_password(password)

        user_data = {
            "password_hash": hashed_password,
            "username": "testuser",
            "role": "user",
        }

        with pytest.raises(HTTPException) as exc_info:
            self.auth.authenticate_user("user_123", "WrongPassword", user_data)
        assert exc_info.value.status_code == 401

    def test_authenticate_child_pin_success(self):
        """Test successful child PIN authentication"""
        pin = "1234"
        pin_hash = self.auth.hash_pin(pin)

        user_data = {
            "pin_hash": pin_hash,
            "username": "child_user",
            "role": "child",
        }

        result = self.auth.authenticate_child_pin("child_123", pin, user_data)

        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert "session_id" in result

    def test_authenticate_child_pin_wrong_pin(self):
        """Test child authentication with wrong PIN fails"""
        pin = "1234"
        pin_hash = self.auth.hash_pin(pin)

        user_data = {
            "pin_hash": pin_hash,
            "username": "child_user",
            "role": "child",
        }

        with pytest.raises(HTTPException) as exc_info:
            self.auth.authenticate_child_pin("child_123", "9999", user_data)
        assert exc_info.value.status_code == 401

    def test_authenticate_child_pin_missing_hash(self):
        """Test child authentication with missing pin_hash fails"""
        user_data = {
            "username": "child_user",
            "role": "child",
        }

        with pytest.raises(HTTPException) as exc_info:
            self.auth.authenticate_child_pin("child_123", "1234", user_data)
        assert exc_info.value.status_code == 401


class TestHelperFunctions:
    """Test module-level helper functions"""

    def test_hash_password_function(self):
        """Test module-level hash_password function"""
        hashed = hash_password("TestPassword123")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_function(self):
        """Test module-level verify_password function"""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_create_access_token_function(self):
        """Test module-level create_access_token function"""
        user_data = {"user_id": "123", "username": "test"}
        token = create_access_token(user_data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_function(self):
        """Test module-level verify_token function"""
        user_data = {"user_id": "123"}
        token = create_access_token(user_data)
        payload = verify_token(token)
        assert payload["user_id"] == "123"

    def test_generate_secure_token(self):
        """Test generating secure token"""
        token = generate_secure_token()
        assert isinstance(token, str)
        assert len(token) >= 32

        # Custom length
        token = generate_secure_token(length=64)
        assert len(token) >= 64

    def test_generate_api_key(self):
        """Test generating API key"""
        api_key = generate_api_key()
        assert isinstance(api_key, str)
        assert len(api_key) > 0


class TestAuthConfigDataclasses:
    """Test authentication dataclasses"""

    def test_token_data_creation(self):
        """Test TokenData dataclass"""
        now = datetime.now(timezone.utc)
        token_data = TokenData(
            user_id="user_123",
            username="testuser",
            role=UserRoleEnum.PARENT,
            session_id="session_456",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
        )

        assert token_data.user_id == "user_123"
        assert token_data.username == "testuser"
        assert isinstance(token_data.role, UserRoleEnum)

    def test_session_data_creation(self):
        """Test SessionData dataclass"""
        now = datetime.now(timezone.utc)
        session_data = SessionData(
            session_id="session_789",
            user_id="user_789",
            device_info={"browser": "Firefox"},
            ip_address="10.0.0.1",
            created_at=now,
            last_activity=now,
            is_active=True,
        )

        assert session_data.session_id == "session_789"
        assert session_data.device_info["browser"] == "Firefox"
        assert session_data.is_active is True

    def test_session_data_default_device_info(self):
        """Test SessionData with default device_info"""
        now = datetime.now(timezone.utc)
        session_data = SessionData(
            session_id="session_default",
            user_id="user_default",
            created_at=now,
            last_activity=now,
        )

        assert isinstance(session_data.device_info, dict)
        assert len(session_data.device_info) == 0


class TestAuthConfig:
    """Test AuthConfig initialization"""

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


class TestGetCurrentUserFromToken:
    """Test get_current_user_from_token method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.auth = AuthenticationService()

    def test_get_current_user_from_token_success(self):
        """Test successfully getting current user from valid token"""
        # Create a session and token
        session_id = self.auth.create_session(user_id="user_123")

        user_data = {
            "user_id": "user_123",
            "username": "testuser",
            "role": UserRoleEnum.PARENT.value,
            "session_id": session_id,
        }
        token = self.auth.create_access_token(user_data)

        # Get current user from token
        user_data = self.auth.get_current_user_from_token(token)

        assert user_data["user_id"] == "user_123"
        assert user_data["username"] == "testuser"
        assert user_data["role"] == UserRoleEnum.PARENT.value

    def test_get_current_user_from_token_refresh_token_rejected(self):
        """Test that refresh tokens are rejected"""
        refresh_token = self.auth.create_refresh_token("user_123")

        with pytest.raises(HTTPException) as exc_info:
            self.auth.get_current_user_from_token(refresh_token)

        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    def test_get_current_user_expired_session(self):
        """Test that expired sessions are detected"""
        # Create session
        session_id = self.auth.create_session(user_id="user_123")

        # Create token
        user_data = {
            "user_id": "user_123",
            "username": "testuser",
            "role": UserRoleEnum.PARENT.value,
            "session_id": session_id,
        }
        token = self.auth.create_access_token(user_data)

        # Revoke session to simulate expiration
        self.auth.revoke_session(session_id)

        with pytest.raises(HTTPException) as exc_info:
            self.auth.get_current_user_from_token(token)

        assert exc_info.value.status_code == 401
        assert "Session has expired" in exc_info.value.detail


class TestCleanupExpiredSessions:
    """Test cleanup_expired_sessions method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.auth = AuthenticationService()

    def test_cleanup_expired_sessions_none_expired(self):
        """Test cleanup when no sessions are expired"""
        # Create fresh sessions
        self.auth.create_session("user_1")
        self.auth.create_session("user_2")

        count = self.auth.cleanup_expired_sessions()
        assert count == 0

    def test_cleanup_expired_sessions_with_expired(self):
        """Test cleanup when sessions are expired"""
        # Create sessions
        session_id_1 = self.auth.create_session("user_1")
        session_id_2 = self.auth.create_session("user_2")

        # Manually expire the first session
        session = self.auth.active_sessions[session_id_1]
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        session.last_activity = old_time

        count = self.auth.cleanup_expired_sessions()

        # One session should be marked as inactive
        assert count == 1
        assert not self.auth.active_sessions[session_id_1].is_active

    def test_cleanup_expired_refresh_tokens(self):
        """Test cleanup of expired refresh tokens"""
        # Create refresh token
        refresh_token = self.auth.create_refresh_token("user_123")
        payload = self.auth.verify_token(refresh_token)
        jti = payload.get("jti")

        # Manually expire the refresh token
        old_time = datetime.now(timezone.utc) - timedelta(days=31)
        self.auth.refresh_tokens[jti]["created_at"] = old_time

        count = self.auth.cleanup_expired_sessions()

        # One refresh token should be removed
        assert count == 1
        assert jti not in self.auth.refresh_tokens


class TestFastAPIDependencies:
    """Test FastAPI dependency functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.auth = AuthenticationService()

    async def test_get_current_user_success(self):
        """Test get_current_user dependency with valid token"""
        from fastapi.security import HTTPAuthorizationCredentials

        from app.services.auth import get_current_user

        # Create token
        user_data = {
            "user_id": "user_123",
            "username": "testuser",
            "role": UserRoleEnum.PARENT.value,
        }
        token = self.auth.create_access_token(user_data)

        # Mock credentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Test dependency
        user_data = await get_current_user(credentials)
        assert user_data["user_id"] == "user_123"

    async def test_get_current_user_no_credentials(self):
        """Test get_current_user dependency without credentials"""
        from app.services.auth import get_current_user

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail

    async def test_get_current_active_user(self):
        """Test get_current_active_user dependency"""
        from app.services.auth import get_current_active_user

        current_user = {"user_id": "user_123", "username": "testuser"}
        result = await get_current_active_user(current_user)
        assert result == current_user

    async def test_require_role_success(self):
        """Test require_role dependency with correct role"""
        from app.services.auth import require_role

        current_user = {"user_id": "user_123", "role": "parent"}
        checker = await require_role(UserRoleEnum.PARENT)
        result = checker(current_user)
        assert result == current_user

    async def test_require_role_forbidden(self):
        """Test require_role dependency with incorrect role"""
        from app.services.auth import require_role

        current_user = {"user_id": "user_123", "role": "child"}
        checker = await require_role(UserRoleEnum.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user)

        assert exc_info.value.status_code == 403
        assert "requires admin role" in exc_info.value.detail


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit"""
        from app.services.auth import RateLimiter

        limiter = RateLimiter()
        key = "test_key"

        # Should allow 5 requests with max of 5
        for i in range(5):
            assert limiter.is_allowed(key, max_requests=5, window_seconds=60)

    def test_rate_limiter_blocks_excess_requests(self):
        """Test that rate limiter blocks requests exceeding limit"""
        from app.services.auth import RateLimiter

        limiter = RateLimiter()
        key = "test_key_2"

        # Allow 3 requests
        for i in range(3):
            assert limiter.is_allowed(key, max_requests=3, window_seconds=60)

        # 4th request should be blocked
        assert not limiter.is_allowed(key, max_requests=3, window_seconds=60)

    def test_rate_limiter_cleans_old_entries(self):
        """Test that rate limiter cleans old entries"""
        from app.services.auth import RateLimiter

        limiter = RateLimiter()
        key = "test_key_3"

        # Add requests in the past
        limiter.requests[key] = [
            (datetime.now(timezone.utc) - timedelta(seconds=120), 1),
            (datetime.now(timezone.utc) - timedelta(seconds=90), 1),
        ]

        # Should allow new request (old ones should be cleaned)
        assert limiter.is_allowed(key, max_requests=1, window_seconds=60)

    def test_check_rate_limit_function(self):
        """Test check_rate_limit function with mock request"""
        from unittest.mock import Mock

        from app.services.auth import check_rate_limit

        # Create mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"

        # Should not raise exception for first request
        check_rate_limit(mock_request, max_requests=10, window_seconds=60)

    def test_check_rate_limit_exceeds_limit(self):
        """Test check_rate_limit raises exception when limit exceeded"""
        from unittest.mock import Mock

        from app.services.auth import check_rate_limit, rate_limiter

        # Create mock request
        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        # Manually set rate limit to exceeded
        key = "rate_limit:192.168.1.1"
        rate_limiter.requests[key] = [
            (datetime.now(timezone.utc), 1) for _ in range(100)
        ]

        with pytest.raises(HTTPException) as exc_info:
            check_rate_limit(mock_request, max_requests=10, window_seconds=60)

        assert exc_info.value.status_code == 429
