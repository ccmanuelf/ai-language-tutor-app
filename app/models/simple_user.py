"""
Simple User Models for Authentication
AI Language Tutor App - Minimal models for auth functionality
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()


class UserRole(PyEnum):
    """User roles in the system"""

    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"


class SimpleUser(Base):
    """Simplified user model for authentication"""

    __tablename__ = "simple_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for demo/development
    role = Column(Enum(UserRole), default=UserRole.CHILD, nullable=False)

    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Settings
    ui_language = Column(String(10), default="en")

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email if include_sensitive else None,
            "role": self.role.value if self.role else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
