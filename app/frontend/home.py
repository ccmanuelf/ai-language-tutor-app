"""
Frontend Home Route
AI Language Tutor App - Landing Page and Health Check

Provides:
- Welcome page with system status
- Quick action buttons
- Health check endpoint
"""

from datetime import datetime
from fasthtml.common import *
from .layout import create_layout


def create_home_routes(app):
    """Create home and health check routes"""

    @app.route("/")
    def home():
        """Main landing page with system overview"""
        return create_layout(
            Div(
                # Welcome section
                Div(
                    H1(
                        "Welcome to AI Language Tutor",
                        style="text-align: center; margin-bottom: 2rem;",
                    ),
                    P(
                        "Your personal AI-powered language learning companion for the whole family.",
                        style="text-align: center; font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 3rem;",
                    ),
                    cls="card",
                ),
                # System status
                Div(
                    H2("System Status", style="margin-bottom: 1.5rem;"),
                    Div(
                        Div(
                            Span("🎤", style="font-size: 2rem;"),
                            H3("Speech Processing"),
                            Span(
                                "Watson STT/TTS Operational",
                                cls="status-indicator status-success",
                            ),
                            P("Real-time speech recognition and synthesis ready"),
                        ),
                        Div(
                            Span("🤖", style="font-size: 2rem;"),
                            H3("AI Services"),
                            Span(
                                "Claude + Mistral + Qwen Active",
                                cls="status-indicator status-success",
                            ),
                            P("Multi-language AI conversation partners available"),
                        ),
                        Div(
                            Span("🗄️", style="font-size: 2rem;"),
                            H3("Database"),
                            Span(
                                "Multi-DB Architecture Ready",
                                cls="status-indicator status-success",
                            ),
                            P("SQLite + ChromaDB + DuckDB operational"),
                        ),
                        cls="grid grid-3",
                    ),
                    cls="card",
                ),
                # Quick actions
                Div(
                    H2("Quick Start", style="margin-bottom: 1.5rem;"),
                    Div(
                        A(
                            Span(
                                "👤",
                                style="font-size: 2rem; margin-bottom: 1rem; display: block;",
                            ),
                            H3("Create Profile"),
                            P("Set up your language learning profile"),
                            href="/profile",
                            cls="btn btn-primary card",
                            style="text-decoration: none; display: block; text-align: center;",
                        ),
                        A(
                            Span(
                                "💬",
                                style="font-size: 2rem; margin-bottom: 1rem; display: block;",
                            ),
                            H3("Start Conversation"),
                            P("Begin AI-powered language practice"),
                            href="/chat",
                            cls="btn btn-primary card",
                            style="text-decoration: none; display: block; text-align: center;",
                        ),
                        cls="grid grid-2",
                    ),
                    cls="card",
                ),
            ),
            current_page="home",
        )

    @app.route("/health")
    def frontend_health():
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "service": "ai-language-tutor-frontend",
            "timestamp": str(datetime.now()),
        }
