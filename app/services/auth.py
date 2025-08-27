"""
User Authentication System for AI Language Tutor App

This module provides secure authentication features including:
- Password hashing and verification
- JWT token management
- Session handling
- Family-friendly authentication (simplified for children)
- Security utilities and validation
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import jwt
import bcrypt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.core.config import get_settings
from app.models.schemas import UserRoleEnum


logger = logging.getLogger(__name__)


class AuthConfig:
    """Authentication configuration"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # JWT Configuration
        self.SECRET_KEY = self.settings.SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
        self.REFRESH_TOKEN_EXPIRE_DAYS = 30
        
        # Password Configuration
        self.PASSWORD_MIN_LENGTH = 8
        self.PASSWORD_MAX_LENGTH = 128
        
        # Session Configuration
        self.SESSION_EXPIRE_HOURS = 12
        self.MAX_SESSIONS_PER_USER = 5
        
        # Family Authentication (simplified for children)
        self.CHILD_PIN_LENGTH = 4
        self.CHILD_SESSION_EXPIRE_HOURS = 8


# Global auth config
auth_config = AuthConfig()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for token authentication
security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """Token data structure"""
    user_id: str
    username: str
    role: UserRoleEnum
    session_id: str
    issued_at: datetime
    expires_at: datetime


class SessionData(BaseModel):
    """Session data structure"""
    session_id: str
    user_id: str
    device_info: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    is_active: bool = True


class AuthenticationService:
    """Main authentication service"""
    
    def __init__(self):
        self.config = auth_config
        self.active_sessions: Dict[str, SessionData] = {}
        self.refresh_tokens: Dict[str, Dict[str, Any]] = {}
    
    # Password Management
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        if not self.validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if not password:
            return False
        
        if len(password) < self.config.PASSWORD_MIN_LENGTH:
            return False
        
        if len(password) > self.config.PASSWORD_MAX_LENGTH:
            return False
        
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        return has_letter and has_number
    
    def generate_secure_password(self, length: int = 12) -> str:
        """Generate a secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    # PIN Management (for children)
    def generate_child_pin(self) -> str:
        """Generate a 4-digit PIN for child accounts"""
        return ''.join(secrets.choice('0123456789') for _ in range(self.config.CHILD_PIN_LENGTH))
    
    def hash_pin(self, pin: str) -> str:
        """Hash a PIN (simpler than password hashing)"""
        return hashlib.sha256(f"{pin}{self.config.SECRET_KEY}".encode()).hexdigest()
    
    def verify_pin(self, pin: str, hashed_pin: str) -> bool:
        """Verify a PIN against its hash"""
        return self.hash_pin(pin) == hashed_pin
    
    # JWT Token Management
    def create_access_token(self, user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = user_data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token"""
        token_data = {
            "user_id": user_id,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32),  # JWT ID for token revocation
            "exp": datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow()
        }
        
        try:
            encoded_jwt = jwt.encode(token_data, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)
            
            # Store refresh token for revocation tracking
            self.refresh_tokens[token_data["jti"]] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create refresh token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh an access token using a refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            jti = payload.get("jti")
            if not jti or jti not in self.refresh_tokens or not self.refresh_tokens[jti]["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked"
                )
            
            user_id = payload.get("user_id")
            
            # Create new access token
            new_access_token = self.create_access_token({"user_id": user_id})
            
            # Create new refresh token and revoke old one
            self.refresh_tokens[jti]["is_active"] = False
            new_refresh_token = self.create_refresh_token(user_id)
            
            return new_access_token, new_refresh_token
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])
            jti = payload.get("jti")
            
            if jti and jti in self.refresh_tokens:
                self.refresh_tokens[jti]["is_active"] = False
                return True
            
            return False
        except Exception as e:
            logger.error(f"Token revocation error: {e}")
            return False
    
    # Session Management
    def create_session(self, user_id: str, device_info: Dict[str, Any] = None, ip_address: str = None) -> str:
        """Create a new user session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            device_info=device_info or {},
            ip_address=ip_address,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True
        )
        
        # Clean up old sessions for this user (keep only latest N sessions)
        user_sessions = [s for s in self.active_sessions.values() if s.user_id == user_id and s.is_active]
        if len(user_sessions) >= self.config.MAX_SESSIONS_PER_USER:
            # Deactivate oldest session
            oldest_session = min(user_sessions, key=lambda s: s.created_at)
            oldest_session.is_active = False
        
        self.active_sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data"""
        session = self.active_sessions.get(session_id)
        
        if not session or not session.is_active:
            return None
        
        # Check if session has expired
        expire_hours = self.config.SESSION_EXPIRE_HOURS
        if session.last_activity < datetime.utcnow() - timedelta(hours=expire_hours):
            session.is_active = False
            return None
        
        return session
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp"""
        session = self.active_sessions.get(session_id)
        if session and session.is_active:
            session.last_activity = datetime.utcnow()
            return True
        return False
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        session = self.active_sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False
    
    def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user"""
        count = 0
        for session in self.active_sessions.values():
            if session.user_id == user_id and session.is_active:
                session.is_active = False
                count += 1
        return count
    
    # Authentication Methods
    def authenticate_user(self, user_id: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate a user with username/password"""
        # Verify password
        if not self.verify_password(password, user_data.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create session
        session_id = self.create_session(user_id)
        
        # Create tokens
        token_data = {
            "user_id": user_id,
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "session_id": session_id
        }
        
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "session_id": session_id,
            "expires_in": self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def authenticate_child_pin(self, user_id: str, pin: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate a child user with PIN"""
        # Verify PIN
        stored_pin_hash = user_data.get("pin_hash")
        if not stored_pin_hash or not self.verify_pin(pin, stored_pin_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect PIN"
            )
        
        # Create session with shorter expiry for children
        session_id = self.create_session(user_id)
        
        # Create tokens with shorter expiry
        token_data = {
            "user_id": user_id,
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "session_id": session_id
        }
        
        access_token = self.create_access_token(
            token_data,
            expires_delta=timedelta(hours=self.config.CHILD_SESSION_EXPIRE_HOURS)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "session_id": session_id,
            "expires_in": self.config.CHILD_SESSION_EXPIRE_HOURS * 3600
        }
    
    def get_current_user_from_token(self, token: str) -> Dict[str, Any]:
        """Get current user data from access token"""
        payload = self.verify_token(token)
        
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Verify session is still active
        session_id = payload.get("session_id")
        if session_id:
            session = self.get_session(session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session has expired"
                )
            
            # Update session activity
            self.update_session_activity(session_id)
        
        return payload
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and refresh tokens"""
        count = 0
        now = datetime.utcnow()
        
        # Clean expired sessions
        for session in list(self.active_sessions.values()):
            if session.last_activity < now - timedelta(hours=self.config.SESSION_EXPIRE_HOURS):
                session.is_active = False
                count += 1
        
        # Clean expired refresh tokens
        for jti, token_data in list(self.refresh_tokens.items()):
            if token_data["created_at"] < now - timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS):
                del self.refresh_tokens[jti]
                count += 1
        
        return count


# Global authentication service
auth_service = AuthenticationService()


# FastAPI Dependencies
async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_service.get_current_user_from_token(credentials.credentials)


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """FastAPI dependency to get current active user"""
    # Additional checks can be added here (e.g., user is active, verified, etc.)
    return current_user


async def require_role(required_role: UserRoleEnum):
    """FastAPI dependency factory to require specific role"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role.value} role"
            )
        return current_user
    return role_checker


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return auth_service.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return auth_service.verify_password(plain_password, hashed_password)


def create_access_token(user_data: Dict[str, Any]) -> str:
    """Create an access token"""
    return auth_service.create_access_token(user_data)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify a token"""
    return auth_service.verify_token(token)


# Security utilities
def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate an API key"""
    return f"ak_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(f"{api_key}{auth_config.SECRET_KEY}".encode()).hexdigest()


def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key"""
    return hash_api_key(api_key) == hashed_api_key


# Rate limiting helpers (basic implementation)
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count), ...]}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed under rate limit"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old entries
        if key in self.requests:
            self.requests[key] = [(ts, count) for ts, count in self.requests[key] if ts > window_start]
        else:
            self.requests[key] = []
        
        # Count current requests
        current_count = sum(count for ts, count in self.requests[key])
        
        if current_count >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append((now, 1))
        return True


# Global rate limiter
rate_limiter = RateLimiter()


def check_rate_limit(request: Request, max_requests: int = 100, window_seconds: int = 3600):
    """Check rate limit for a request"""
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    if not rate_limiter.is_allowed(key, max_requests, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )