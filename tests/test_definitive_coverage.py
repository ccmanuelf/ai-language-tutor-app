"""
Definitive test to achieve 100% coverage by executing the exact missing lines
AI Language Tutor App - Personal Family Educational Tool
"""

import pytest
from unittest.mock import patch
import sys
from pathlib import Path


class TestDefinitive100Coverage:
    """Final tests to hit the last 2 missing lines"""

    @patch("uvicorn.run")
    def test_execute_main_py_as_script(self, mock_uvicorn_run):
        """Execute main.py exactly as if 'python app/main.py' was run"""
        mock_uvicorn_run.return_value = None

        # Get the actual file path
        main_file = Path(__file__).parent.parent / "app" / "main.py"

        # Read the source code
        source_code = main_file.read_text()

        # Create a namespace with __name__ = '__main__'
        namespace = {
            "__name__": "__main__",
            "__file__": str(main_file),
        }

        # Execute the entire module as if it was run as a script
        exec(source_code, namespace)

        # Verify uvicorn.run was called (this means line 78 was executed)
        mock_uvicorn_run.assert_called_once()

    @patch("uvicorn.run")
    def test_execute_frontend_main_py_as_script(self, mock_uvicorn_run):
        """Execute frontend_main.py exactly as if 'python app/frontend_main.py' was run"""
        mock_uvicorn_run.return_value = None

        # Get the actual file path
        frontend_file = Path(__file__).parent.parent / "app" / "frontend_main.py"

        # Read the source code
        source_code = frontend_file.read_text()

        # Create a namespace with __name__ = '__main__'
        namespace = {
            "__name__": "__main__",
            "__file__": str(frontend_file),
        }

        # Execute the entire module as if it was run as a script
        exec(source_code, namespace)

        # Verify uvicorn.run was called (this means line 70 was executed)
        mock_uvicorn_run.assert_called_once()
