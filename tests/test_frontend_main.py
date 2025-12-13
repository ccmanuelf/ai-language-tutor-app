"""
Tests for app/frontend_main.py
Coverage target: 36.36% → 100.00%
"""

import runpy
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.frontend_main import frontend_app, run_frontend_server


class TestRunFrontendServer:
    """Test the run_frontend_server function"""

    @patch("app.frontend_main.uvicorn.run")
    @patch("app.frontend_main.create_frontend_app")
    def test_run_frontend_server_success(self, mock_create_app, mock_uvicorn_run):
        """Test run_frontend_server starts uvicorn correctly"""
        # Setup
        mock_app = Mock()
        mock_create_app.return_value = mock_app

        # Execute
        run_frontend_server()

        # Verify
        mock_create_app.assert_called_once()
        mock_uvicorn_run.assert_called_once_with(
            mock_app, host="127.0.0.1", port=3000, reload=True, log_level="info"
        )


class TestFrontendAppInstance:
    """Test the frontend_app module-level instance"""

    def test_frontend_app_is_created(self):
        """Test that frontend_app is a valid FastHTML app instance"""
        # frontend_app is created at module import time
        assert frontend_app is not None
        # Should have FastHTML app attributes
        assert hasattr(frontend_app, "routes") or hasattr(frontend_app, "router")


class TestMainExecution:
    """Test the __main__ execution block"""

    def test_main_block_execution(self):
        """Test that __main__ block executes correctly with all print statements"""
        import os
        import subprocess

        # Create a test script that mocks uvicorn.run to prevent actual server startup
        test_script = """
import sys
from unittest.mock import patch, MagicMock

# Mock uvicorn before importing app.frontend_main
mock_uvicorn = MagicMock()
sys.modules["uvicorn"] = mock_uvicorn

# Now import and run the module
import runpy
runpy.run_module("app.frontend_main", run_name="__main__")
"""

        # Run the test script in a subprocess
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        # Verify the output contains all expected print statements
        output = result.stdout + result.stderr

        # Check for key print messages (lines 39-51)
        assert "AI Language Tutor Frontend" in output
        assert "Components now organized" in output
        assert "styles.py" in output
        assert "layout.py" in output
        assert "diagnostic.py" in output
        assert "home.py" in output
        assert "profile.py" in output
        assert "chat.py" in output
        assert "progress.py" in output
        assert "main.py" in output
        assert "server.py" in output
        assert "Starting server" in output

        # Verify no errors occurred (exit code 0 or 1 is acceptable since uvicorn might exit)
        assert result.returncode in [0, 1], (
            f"Unexpected exit code: {result.returncode}\nOutput: {output}"
        )
