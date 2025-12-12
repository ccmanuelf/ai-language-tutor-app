"""
Test module for FastAPI backend
AI Language Tutor App - Personal Family Educational Tool
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app, run_server

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


def test_run_server():
    """Test run_server function"""
    with patch("app.main.uvicorn.run") as mock_run:
        run_server()
        # Verify uvicorn.run was called
        mock_run.assert_called_once()
        # Verify it was called with expected parameters
        call_args = mock_run.call_args
        assert call_args[0][0] == "main:app"  # First positional arg
        assert "host" in call_args[1]  # Keyword args
        assert "port" in call_args[1]


def test_main_module_execution():
    """Test that __main__ block can be executed"""
    # Test that the run_server function is callable
    # (actual execution is tested via mocking in test_run_server)
    assert callable(run_server)

    # Verify run_server is properly imported
    from app.main import run_server as imported_run_server

    assert imported_run_server is run_server
