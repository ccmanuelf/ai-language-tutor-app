"""
Frontend Package
AI Language Tutor App - Modular Frontend Components

Exports main frontend application and components for external use.
"""

from .main import create_frontend_app, frontend_app
from .server import run_frontend_server

__all__ = ["create_frontend_app", "frontend_app", "run_frontend_server"]
