"""
Test module for core configuration
AI Language Tutor App - Personal Family Educational Tool
"""

import pytest
from app.core.config import get_settings, Settings


def test_settings_creation():
    """Test that settings can be created"""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_default_settings():
    """Test default settings values"""
    settings = get_settings()
    assert settings.DEBUG == True
    assert settings.HOST == "localhost"
    assert settings.PORT == 8000
    assert settings.FRONTEND_PORT == 3000
    assert settings.MONTHLY_BUDGET_USD == 30.0


def test_settings_caching():
    """Test that settings are cached"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Same instance due to lru_cache
