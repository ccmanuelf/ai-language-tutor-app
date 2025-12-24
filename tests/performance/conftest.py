"""
Performance Test Configuration
Shared fixtures and configuration for performance tests
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.config import DatabaseManager, get_primary_db_session


@pytest.fixture(scope="session")
def db_manager():
    """Create database manager for performance tests"""
    # Use singleton instance
    db_manager = DatabaseManager()
    yield db_manager


@pytest.fixture(scope="function")
def clean_db(db_manager):
    """Clean database before each test"""
    from app.models.database import Conversation, User

    db = get_primary_db_session()

    # Clean up test data
    db.query(Conversation).filter(Conversation.user_id.like("load_test_%")).delete()
    db.query(User).filter(User.username.like("load_test_%")).delete()

    db.commit()
    db.close()

    yield

    # Cleanup after test
    db = get_primary_db_session()
    db.query(Conversation).filter(Conversation.user_id.like("load_test_%")).delete()
    db.query(User).filter(User.username.like("load_test_%")).delete()
    db.commit()
    db.close()


def pytest_configure(config):
    """Configure pytest for performance tests"""
    config.addinivalue_line("markers", "performance: mark test as a performance test")
