"""
Frontend Main Application
AI Language Tutor App - Modular Frontend Architecture

Main FastHTML application that orchestrates all frontend components:
- Imports all modular route components
- Configures application settings
- Registers all routes
- Provides application factory
"""

from pathlib import Path

from fasthtml.common import *

# Import admin API router
from app.api.admin import admin_router

# Import core configuration and services
from app.core.config import get_settings

from .admin_routes import register_admin_routes
from .chat import create_chat_route
from .collections import create_collections_routes
from .content_library import create_content_library_routes
from .content_view import create_content_view_route

# Import modular frontend components
from .diagnostic import create_diagnostic_route
from .home import create_home_routes
from .persona_profile_routes import register_persona_profile_routes
from .profile import create_profile_route
from .progress import create_progress_route
from .study_session import create_study_routes
from .user_budget_routes import register_user_budget_routes
from .visual_learning import create_visual_learning_routes


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
    create_visual_learning_routes(app)

    # Session 129: Content Organization & Study Tracking
    create_content_library_routes(app)  # Main content hub
    create_collections_routes(app)
    create_study_routes(app)

    # Register user budget dashboard routes
    register_user_budget_routes(app)

    # Register persona profile routes
    register_persona_profile_routes(app)

    # Register admin dashboard routes and API
    register_admin_routes(app, admin_router)

    return app


# Create frontend app instance
frontend_app = create_frontend_app()
