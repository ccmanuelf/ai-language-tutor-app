"""
Test module for FastAPI backend
AI Language Tutor App - Personal Family Educational Tool
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-language-tutor-api"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AI Language Tutor API" in data["message"]
    assert data["version"] == "0.1.0"


def test_static_files_mount():
    """Test that static files are properly mounted"""
    # This should return 404 for non-existent files but not crash
    response = client.get("/static/nonexistent.css")
    assert response.status_code == 404
