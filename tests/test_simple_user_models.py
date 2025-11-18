"""
Comprehensive Tests for Simple User Models
Tests all aspects of the SimpleUser model including:
- UserRole enum
- SimpleUser model creation
- to_dict method with all branch paths
- Field validation and constraints

Target: TRUE 100% coverage (statement + branch)
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.simple_user import Base, SimpleUser, UserRole


# Test Fixtures
@pytest.fixture(scope="function")
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestUserRoleEnum:
    """Test UserRole enum"""

    def test_user_role_values(self):
        """Test that UserRole enum has correct values"""
        assert UserRole.PARENT.value == "parent"
        assert UserRole.CHILD.value == "child"
        assert UserRole.ADMIN.value == "admin"

    def test_user_role_count(self):
        """Test that UserRole has exactly 3 roles"""
        assert len(UserRole) == 3


class TestSimpleUserModel:
    """Test SimpleUser model creation and basic operations"""

    def test_create_simple_user_minimal(self, db_session):
        """Test creating SimpleUser with minimal required fields"""
        user = SimpleUser(
            user_id="test_user_001",
            username="testuser",
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.user_id == "test_user_001"
        assert user.username == "testuser"
        assert user.email is None
        assert user.password_hash is None
        assert user.role == UserRole.CHILD  # Default role
        assert user.first_name is None
        assert user.last_name is None
        assert user.ui_language == "en"  # Default language
        assert user.is_active is True  # Default active
        assert user.is_verified is False  # Default not verified
        assert user.last_login is None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_simple_user_all_fields(self, db_session):
        """Test creating SimpleUser with all fields populated"""
        now = datetime.now()
        user = SimpleUser(
            user_id="parent_001",
            username="parentuser",
            email="parent@example.com",
            password_hash="hashed_password_here",
            role=UserRole.PARENT,
            first_name="Jane",
            last_name="Doe",
            ui_language="es",
            is_active=True,
            is_verified=True,
            last_login=now,
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.user_id == "parent_001"
        assert user.username == "parentuser"
        assert user.email == "parent@example.com"
        assert user.password_hash == "hashed_password_here"
        assert user.role == UserRole.PARENT
        assert user.first_name == "Jane"
        assert user.last_name == "Doe"
        assert user.ui_language == "es"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.last_login == now

    def test_create_admin_user(self, db_session):
        """Test creating admin user with ADMIN role"""
        user = SimpleUser(
            user_id="admin_001",
            username="adminuser",
            email="admin@example.com",
            role=UserRole.ADMIN,
        )
        db_session.add(user)
        db_session.commit()

        assert user.role == UserRole.ADMIN

    def test_user_id_uniqueness(self, db_session):
        """Test that user_id must be unique"""
        user1 = SimpleUser(user_id="duplicate_id", username="user1")
        user2 = SimpleUser(user_id="duplicate_id", username="user2")

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()

    def test_email_uniqueness(self, db_session):
        """Test that email must be unique when provided"""
        user1 = SimpleUser(user_id="user1", username="user1", email="same@example.com")
        user2 = SimpleUser(user_id="user2", username="user2", email="same@example.com")

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()


class TestSimpleUserToDict:
    """Test SimpleUser.to_dict() method with all branch paths"""

    def test_to_dict_default_not_sensitive(self, db_session):
        """Test to_dict() with default include_sensitive=False"""
        now = datetime.now()
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
            email="test@example.com",
            role=UserRole.CHILD,
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_verified=False,
            last_login=now,
        )
        db_session.add(user)
        db_session.commit()

        # Test default (include_sensitive=False)
        user_dict = user.to_dict()

        assert user_dict["id"] == user.id
        assert user_dict["user_id"] == "test_user"
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] is None  # Should be None when not sensitive
        assert user_dict["role"] == "child"
        assert user_dict["first_name"] == "John"
        assert user_dict["last_name"] == "Doe"
        assert user_dict["is_active"] is True
        assert user_dict["is_verified"] is False
        assert user_dict["last_login"] == now.isoformat()
        assert user_dict["created_at"] == user.created_at.isoformat()
        assert user_dict["updated_at"] == user.updated_at.isoformat()

    def test_to_dict_include_sensitive_true(self, db_session):
        """Test to_dict() with include_sensitive=True"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
            email="test@example.com",
            role=UserRole.PARENT,
        )
        db_session.add(user)
        db_session.commit()

        # Test with include_sensitive=True
        user_dict = user.to_dict(include_sensitive=True)

        assert user_dict["email"] == "test@example.com"  # Email should be included
        assert user_dict["role"] == "parent"

    def test_to_dict_include_sensitive_false_explicit(self, db_session):
        """Test to_dict() with explicit include_sensitive=False"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
            email="test@example.com",
        )
        db_session.add(user)
        db_session.commit()

        # Explicit False
        user_dict = user.to_dict(include_sensitive=False)

        assert user_dict["email"] is None  # Email should be None

    def test_to_dict_role_none(self):
        """Test to_dict() when role is None"""
        # This tests the 'if self.role else None' branch
        # Don't use db_session - test the object directly without committing
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
        )
        # Manually set role to None (bypassing default)
        user.role = None

        user_dict = user.to_dict()

        assert user_dict["role"] is None  # Role should be None

    def test_to_dict_last_login_none(self, db_session):
        """Test to_dict() when last_login is None"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
            last_login=None,  # Explicitly None
        )
        db_session.add(user)
        db_session.commit()

        user_dict = user.to_dict()

        assert user_dict["last_login"] is None

    def test_to_dict_last_login_present(self, db_session):
        """Test to_dict() when last_login has a value"""
        now = datetime.now()
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
            last_login=now,
        )
        db_session.add(user)
        db_session.commit()

        user_dict = user.to_dict()

        assert user_dict["last_login"] == now.isoformat()

    def test_to_dict_created_at_none(self, db_session):
        """Test to_dict() when created_at is None (edge case)"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
        )
        # Don't commit to database - created_at won't be set by func.now()
        # Manually set to None for testing
        user.created_at = None

        user_dict = user.to_dict()

        assert user_dict["created_at"] is None

    def test_to_dict_updated_at_none(self, db_session):
        """Test to_dict() when updated_at is None (edge case)"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
        )
        # Manually set to None for testing
        user.updated_at = None

        user_dict = user.to_dict()

        assert user_dict["updated_at"] is None

    def test_to_dict_all_timestamps_present(self, db_session):
        """Test to_dict() when all timestamps are present"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
        )
        db_session.add(user)
        db_session.commit()

        user_dict = user.to_dict()

        # All timestamps should be present and in ISO format
        assert user_dict["created_at"] is not None
        assert user_dict["updated_at"] is not None
        assert isinstance(user_dict["created_at"], str)
        assert isinstance(user_dict["updated_at"], str)

    def test_to_dict_all_roles(self, db_session):
        """Test to_dict() with all possible UserRole values"""
        roles = [UserRole.PARENT, UserRole.CHILD, UserRole.ADMIN]

        for idx, role in enumerate(roles):
            user = SimpleUser(
                user_id=f"user_{idx}",
                username=f"user{idx}",
                role=role,
            )
            db_session.add(user)
            db_session.commit()

            user_dict = user.to_dict()

            assert user_dict["role"] == role.value

            db_session.rollback()  # Reset for next iteration


class TestSimpleUserEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_nullable_fields(self, db_session):
        """Test that nullable fields can be None"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
            email=None,
            password_hash=None,
            first_name=None,
            last_name=None,
            last_login=None,
        )
        db_session.add(user)
        db_session.commit()

        assert user.email is None
        assert user.password_hash is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.last_login is None

    def test_default_values(self, db_session):
        """Test that default values are applied correctly"""
        user = SimpleUser(
            user_id="test_user",
            username="testuser",
        )
        db_session.add(user)
        db_session.commit()

        # Test defaults
        assert user.role == UserRole.CHILD
        assert user.ui_language == "en"
        assert user.is_active is True
        assert user.is_verified is False

    def test_inactive_user(self, db_session):
        """Test creating inactive user"""
        user = SimpleUser(
            user_id="inactive_user",
            username="inactive",
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        assert user.is_active is False

    def test_verified_user(self, db_session):
        """Test creating verified user"""
        user = SimpleUser(
            user_id="verified_user",
            username="verified",
            is_verified=True,
        )
        db_session.add(user)
        db_session.commit()

        assert user.is_verified is True
