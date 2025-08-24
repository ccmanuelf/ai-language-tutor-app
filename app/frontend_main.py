"""
FastHTML Frontend Server Entry Point
AI Language Tutor App - Personal Family Educational Tool
"""

from fasthtml.common import *
import uvicorn
from pathlib import Path

# Import core configuration
from app.core.config import get_settings

def create_frontend_app():
    """Create and configure FastHTML application"""
    settings = get_settings()
    
    # FastHTML app with basic configuration
    app = FastHTML(
        debug=settings.DEBUG,
        static_path="/Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app/app/static"
    )
    
    # Basic route for testing
    @app.route("/")
    def home():
        return Html(
            Head(
                Title("AI Language Tutor"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Link(rel="stylesheet", href="/static/css/style.css", type="text/css"),
            ),
            Body(
                Div(
                    H1("🎯 AI Language Tutor", cls="title"),
                    P("Personal Family Educational Tool", cls="subtitle"),
                    P("FastHTML Frontend is running successfully!", cls="status"),
                    cls="container"
                ),
                Script(src="/static/js/app.js")
            )
        )
    
    # Health check
    @app.route("/health")
    def frontend_health():
        return {"status": "healthy", "service": "ai-language-tutor-frontend"}
    
    return app

# Create frontend app
frontend_app = create_frontend_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "frontend_main:frontend_app",
        host=settings.HOST,
        port=settings.FRONTEND_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )