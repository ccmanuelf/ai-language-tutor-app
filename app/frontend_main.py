"""
FastHTML Frontend Server Entry Point
AI Language Tutor App - Personal Family Educational Tool

REFACTORED: Now uses modular component architecture

Modern FastHTML frontend with:
- User authentication and profiles
- AI conversation interface
- Speech input/output using IBM Watson
- Multi-language support
- Family-safe design

Architecture:
- Modular components in app/frontend/ directory
- Separated concerns: styles, layout, routes
- Maintainable and scalable structure
"""

import uvicorn
from datetime import datetime

# Import the modular frontend application
from app.frontend.main import create_frontend_app


# Backward compatibility functions
def run_frontend_server():
    """Run the FastHTML frontend server - refactored for modular architecture"""
    app = create_frontend_app()

    uvicorn.run(app, host="127.0.0.1", port=3000, reload=True, log_level="info")


# Create frontend app for external imports
frontend_app = create_frontend_app()

# Entry point for direct execution
if __name__ == "__main__":
    print("🎯 AI Language Tutor Frontend - Modular Architecture")
    print("📁 Components now organized in app/frontend/:")
    print("   - styles.py: CSS framework and theming")
    print("   - layout.py: Header, footer, and layout components")
    print("   - diagnostic.py: System testing route")
    print("   - home.py: Landing page and health check")
    print("   - profile.py: User management and family features")
    print("   - chat.py: AI conversation interface")
    print("   - progress.py: Learning analytics")
    print("   - main.py: Application factory")
    print("   - server.py: Server startup")
    print("🚀 Starting server...")
    run_frontend_server()
