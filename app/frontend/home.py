"""
Frontend Home Route
AI Language Tutor App - YouLearn-Style Landing Page

Provides:
- YouLearn-inspired main interface
- Upload, Paste, Record options
- Learning spaces and content exploration
- Clean, centered layout matching YouLearn design
"""

from datetime import datetime
from fasthtml.common import *


def create_youlearn_sidebar():
    """Create YouLearn-style sidebar navigation"""
    return Div(
        # Logo section
        Div(
            Div(
                Span("🎯", style="font-size: 1.5rem; margin-right: 0.5rem;"),
                Span("AI Language Tutor", style="font-weight: 700; font-size: 1.1rem;"),
                style="display: flex; align-items: center; margin-bottom: 2rem; padding: 1rem 0;",
            ),
            style="border-bottom: 1px solid var(--border-light);",
        ),
        # Main navigation
        Div(
            A(
                Span("📤", style="margin-right: 0.75rem;"),
                "Add content",
                href="/chat",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span("🔍", style="margin-right: 0.75rem;"),
                "Search",
                href="/profile",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span("📚", style="margin-right: 0.75rem;"),
                "History",
                href="/progress",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 2rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            style="margin-bottom: 2rem;",
        ),
        # Spaces section
        Div(
            H3(
                "Spaces",
                style="color: var(--text-primary); font-size: 1rem; margin-bottom: 1rem; padding: 0 1rem;",
            ),
            A(
                Div(
                    Span("👤", style="margin-right: 0.75rem;"),
                    Div(
                        Div(
                            "Family Learning Space",
                            style="font-weight: 600; font-size: 0.9rem;",
                        ),
                        Div(
                            "3 contents",
                            style="font-size: 0.8rem; color: var(--text-muted);",
                        ),
                        style="flex: 1;",
                    ),
                    style="display: flex; align-items: center;",
                ),
                href="/profile",
                style="display: block; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            style="margin-bottom: 2rem;",
        ),
        # Help section
        Div(
            A(
                Span("💬", style="margin-right: 0.75rem;"),
                "Feedback",
                href="/test",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span("📖", style="margin-right: 0.75rem;"),
                "Quick Guide",
                href="/health",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            style="border-top: 1px solid var(--border-light); padding-top: 1rem;",
        ),
        style="""
            width: 280px;
            height: 100vh;
            background: var(--bg-primary);
            border-right: 1px solid var(--border-light);
            padding: 1rem 0;
            position: fixed;
            top: 0;
            left: 0;
            overflow-y: auto;
        """,
    )


def create_main_content():
    """Create YouLearn-style main content area"""
    return Div(
        # Top bar with upgrade button
        Div(
            Div(style="flex: 1;"),  # Spacer
            A(
                "Upgrade",
                href="/profile",
                style="""
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                    color: white;
                    padding: 0.5rem 1.5rem;
                    border-radius: 2rem;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 0.9rem;
                    transition: all 0.2s;
                """,
                onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='var(--shadow-md)'",
                onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'",
            ),
            style="display: flex; align-items: center; padding: 1rem 2rem; border-bottom: 1px solid var(--border-light);",
        ),
        # Main learning interface
        Div(
            # Main heading
            H1(
                "What do you want to learn?",
                style="""
                    text-align: center;
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: var(--text-primary);
                    margin-bottom: 3rem;
                    letter-spacing: -0.02em;
                """,
            ),
            # Upload options
            Div(
                # Upload card
                Div(
                    Div(
                        Span(
                            "📤",
                            style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;",
                        ),
                        H3(
                            "Upload",
                            style="font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);",
                        ),
                        P(
                            "File, audio, video",
                            style="color: var(--text-muted); font-size: 0.9rem;",
                        ),
                        style="text-align: center;",
                    ),
                    style="""
                        background: var(--bg-primary);
                        border: 2px solid var(--border-color);
                        border-radius: var(--radius-lg);
                        padding: 2rem 1.5rem;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        min-height: 140px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    """,
                    onclick="window.location.href='/chat'",
                    onmouseover="this.style.borderColor='var(--primary-color)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'",
                    onmouseout="this.style.borderColor='var(--border-color)'; this.style.transform='translateY(0)'; this.style.boxShadow='none'",
                ),
                # Paste card (marked as popular)
                Div(
                    Div(
                        Span(
                            "Popular",
                            style="""
                            background: var(--primary-color);
                            color: white;
                            padding: 0.25rem 0.75rem;
                            border-radius: 1rem;
                            font-size: 0.75rem;
                            font-weight: 600;
                            position: absolute;
                            top: -0.5rem;
                            left: 50%;
                            transform: translateX(-50%);
                        """,
                        ),
                        style="position: relative;",
                    ),
                    Div(
                        Span(
                            "🔗",
                            style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;",
                        ),
                        H3(
                            "Paste",
                            style="font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);",
                        ),
                        P(
                            "YouTube, website, text",
                            style="color: var(--text-muted); font-size: 0.9rem;",
                        ),
                        style="text-align: center;",
                    ),
                    style="""
                        background: var(--bg-primary);
                        border: 2px solid var(--primary-color);
                        border-radius: var(--radius-lg);
                        padding: 2rem 1.5rem;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        min-height: 140px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        position: relative;
                    """,
                    onclick="window.location.href='/chat'",
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'",
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'",
                ),
                # Record card
                Div(
                    Div(
                        Span(
                            "🎤",
                            style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;",
                        ),
                        H3(
                            "Record",
                            style="font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);",
                        ),
                        P(
                            "Record class, video call",
                            style="color: var(--text-muted); font-size: 0.9rem;",
                        ),
                        style="text-align: center;",
                    ),
                    style="""
                        background: var(--bg-primary);
                        border: 2px solid var(--border-color);
                        border-radius: var(--radius-lg);
                        padding: 2rem 1.5rem;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        min-height: 140px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    """,
                    onclick="window.location.href='/chat'",
                    onmouseover="this.style.borderColor='var(--primary-color)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'",
                    onmouseout="this.style.borderColor='var(--border-color)'; this.style.transform='translateY(0)'; this.style.boxShadow='none'",
                ),
                style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 3rem; max-width: 800px; margin-left: auto; margin-right: auto;",
            ),
            # Search bar
            Div(
                Input(
                    placeholder="Learn anything",
                    style="""
                        width: 100%;
                        padding: 1rem 1.5rem;
                        border: 2px solid var(--border-color);
                        border-radius: 3rem;
                        font-size: 1rem;
                        background: var(--bg-primary);
                        transition: all 0.2s;
                    """,
                    onfocus="this.style.borderColor='var(--primary-color)'; this.style.boxShadow='0 0 0 4px rgba(99, 102, 241, 0.1)'",
                    onblur="this.style.borderColor='var(--border-color)'; this.style.boxShadow='none'",
                ),
                Span(
                    "⬆️",
                    style="""
                    position: absolute;
                    right: 1rem;
                    top: 50%;
                    transform: translateY(-50%);
                    background: var(--text-muted);
                    color: white;
                    padding: 0.5rem;
                    border-radius: 50%;
                    font-size: 0.8rem;
                    cursor: pointer;
                """,
                ),
                style="position: relative; max-width: 600px; margin: 0 auto 4rem auto;",
            ),
            style="flex: 1; padding: 3rem 2rem; overflow-y: auto;",
        ),
        style="margin-left: 280px; min-height: 100vh; background: var(--bg-secondary);",
    )


def create_home_routes(app):
    """Create YouLearn-style home routes"""

    @app.route("/")
    def home():
        """YouLearn-style main landing page"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("AI Language Tutor - Learn Anything"),
                Link(rel="stylesheet", href="/static/styles.css")
                if hasattr(app, "static")
                else None,
                Style("""
                    :root {
                        --primary-color: #6366f1;
                        --primary-dark: #4338ca;
                        --text-primary: #0f172a;
                        --text-secondary: #64748b;
                        --text-muted: #94a3b8;
                        --bg-primary: #ffffff;
                        --bg-secondary: #f8fafc;
                        --bg-tertiary: #f1f5f9;
                        --border-color: #e2e8f0;
                        --border-light: #f1f5f9;
                        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        --shadow-md: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
                        --radius: 0.5rem;
                        --radius-lg: 1rem;
                    }

                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }

                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
                        line-height: 1.6;
                        color: var(--text-primary);
                        background: var(--bg-secondary);
                        -webkit-font-smoothing: antialiased;
                    }
                """),
            ),
            Body(
                create_youlearn_sidebar(),
                create_main_content(),
                style="margin: 0; padding: 0;",
            ),
        )

    @app.route("/health")
    def frontend_health():
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "service": "ai-language-tutor-frontend",
            "timestamp": str(datetime.now()),
        }
