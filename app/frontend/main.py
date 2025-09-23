"""
Frontend Main Application
AI Language Tutor App - Modular Frontend Architecture

Main FastHTML application that orchestrates all frontend components:
- Imports all modular route components
- Configures application settings
- Registers all routes
- Provides application factory
"""

from fasthtml.common import *
from pathlib import Path

# Import core configuration and services
from app.core.config import get_settings

# Import modular frontend components
from .diagnostic import create_diagnostic_route
from .home import create_home_routes
from .profile import create_profile_route
from .chat import create_chat_route
from .progress import create_progress_route
from .content_view import create_content_view_route


def create_frontend_app():
    """Create and configure comprehensive FastHTML application with modular structure"""
    settings = get_settings()

    # FastHTML app with enhanced configuration
    app = FastHTML(
        debug=settings.DEBUG,
        static_path=str(Path(__file__).parent / "static"),
        title="AI Language Tutor - Family Educational Tool",
    )

    # Register all route modules
    create_diagnostic_route(app)
    create_home_routes(app)
    create_profile_route(app)
    create_chat_route(app)
    create_progress_route(app)
    create_content_view_route(app)

    return app


# Create frontend app instance
frontend_app = create_frontend_app()
