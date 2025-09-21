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


def create_heroicon_svg(icon_name, size="20", stroke_width="1.5"):
    """Create HeroIcons SVG elements"""
    icons = {
        "plus": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
        "search": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>',
        "history": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l4 2"></path></svg>',
        "user": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
        "chat": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>',
        "book": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>',
        "target": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
        "folder": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>',
        "help": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><point cx="12" cy="17" r="1"></point></svg>',
        "globe": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
        "gift": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><polyline points="20,12 20,22 4,22 4,12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>',
        "star": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon></svg>',
        "cards": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
        "quiz": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h4l3 3v-8l-3-3z"></path><path d="M14 15V9a2 2 0 0 0-2-2H5"></path></svg>',
        "microphone": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>',
        "note": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10,9 9,9 8,9"></polyline></svg>',
        "summary": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><line x1="10" y1="9" x2="8" y2="9"></line></svg>',
        "upload": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7,10 12,5 17,10"></polyline><line x1="12" y1="5" x2="12" y2="15"></line></svg>',
        "link": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>',
        "record": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>',
        "arrow-up": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5,12 12,5 19,12"></polyline></svg>',
    }
    return icons.get(icon_name, icons["help"])


def create_youlearn_sidebar():
    """Create YouLearn-style sidebar navigation with HeroIcons"""
    return Div(
        # Logo section
        Div(
            Div(
                Span(
                    create_heroicon_svg("target", "24"),
                    style="margin-right: 0.5rem; color: var(--primary-color);",
                ),
                Span("AI Language Tutor", style="font-weight: 700; font-size: 1.1rem;"),
                style="display: flex; align-items: center; margin-bottom: 2rem; padding: 1rem 0;",
            ),
            style="border-bottom: 1px solid var(--border-light);",
        ),
        # Main navigation
        Div(
            A(
                Span(create_heroicon_svg("plus", "20"), style="margin-right: 0.75rem;"),
                "Add content",
                href="/chat",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("search", "20"), style="margin-right: 0.75rem;"
                ),
                "Search",
                href="/profile",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("history", "20"), style="margin-right: 0.75rem;"
                ),
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
            Div(
                H3(
                    "Spaces",
                    style="color: var(--text-primary); font-size: 1rem; margin-bottom: 1rem; padding: 0 1rem;",
                ),
                A(
                    Span(
                        create_heroicon_svg("plus", "16"),
                        style="color: var(--text-muted);",
                    ),
                    href="/chat",
                    style="text-decoration: none; padding: 0.25rem; border-radius: var(--radius); transition: all 0.2s;",
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                    title="Create Space",
                ),
                style="display: flex; justify-content: space-between; align-items: center; padding: 0 1rem; margin-bottom: 1rem;",
            ),
            A(
                Div(
                    Span(
                        create_heroicon_svg("user", "20"),
                        style="margin-right: 0.75rem; color: var(--text-muted);",
                    ),
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
        # Help & Tools section
        Div(
            H3(
                "Help & Tools",
                style="color: var(--text-primary); font-size: 1rem; margin-bottom: 1rem; padding: 0 1rem;",
            ),
            A(
                Span(
                    create_heroicon_svg("globe", "20"),
                    style="margin-right: 0.75rem; color: var(--text-muted);",
                ),
                "Chrome Extension",
                href="/test",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("chat", "20"),
                    style="margin-right: 0.75rem; color: var(--text-muted);",
                ),
                "Discord Server",
                href="/test",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("gift", "20"),
                    style="margin-right: 0.75rem; color: var(--text-muted);",
                ),
                "Invite & Earn",
                href="/test",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("star", "20"),
                    style="margin-right: 0.75rem; color: var(--text-muted);",
                ),
                "New Features",
                href="/test",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("help", "20"),
                    style="margin-right: 0.75rem; color: var(--text-muted);",
                ),
                "Feedback",
                href="/test",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("book", "20"),
                    style="margin-right: 0.75rem; color: var(--text-muted);",
                ),
                "Quick Guide",
                href="/health",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 2rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            style="border-top: 1px solid var(--border-light); padding-top: 1rem; margin-bottom: 2rem;",
        ),
        # User profile section at bottom
        Div(
            A(
                Div(
                    Span(
                        create_heroicon_svg("user", "20"),
                        style="margin-right: 0.75rem; color: var(--text-muted);",
                    ),
                    Div(
                        Div(
                            "User Profile",
                            style="font-weight: 600; font-size: 0.9rem;",
                        ),
                        Div(
                            "Free Plan",
                            style="font-size: 0.8rem; color: var(--text-muted);",
                        ),
                        style="flex: 1;",
                    ),
                    style="display: flex; align-items: center;",
                ),
                href="/profile",
                style="display: block; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); transition: all 0.2s; border-top: 1px solid var(--border-light);",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            style="position: absolute; bottom: 1rem; left: 0; right: 0; padding: 0 1rem;",
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
        # Top bar with language selector and toolbar
        Div(
            # Language selector (left side)
            Div(
                Span("🇺🇸", style="margin-right: 0.25rem;"),
                Span("🇬🇧", style="margin-right: 0.5rem;"),
                Span(
                    "english", style="color: var(--text-secondary); font-size: 0.9rem;"
                ),
                style="display: flex; align-items: center;",
            ),
            # Center toolbar with YouLearn features
            Div(
                A(
                    Span(
                        create_heroicon_svg("chat", "18"), style="margin-right: 0.5rem;"
                    ),
                    "Chat",
                    href="/chat",
                    style="""
                        display: flex; align-items: center;
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                        margin-right: 0.5rem;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
                A(
                    Span(
                        create_heroicon_svg("cards", "18"),
                        style="margin-right: 0.5rem;",
                    ),
                    "Flashcards",
                    href="/test",
                    style="""
                        display: flex; align-items: center;
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                        margin-right: 0.5rem;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
                A(
                    Span(
                        create_heroicon_svg("quiz", "18"), style="margin-right: 0.5rem;"
                    ),
                    "Quizzes",
                    href="/test",
                    style="""
                        display: flex; align-items: center;
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                        margin-right: 0.5rem;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
                A(
                    Span(
                        create_heroicon_svg("microphone", "18"),
                        style="margin-right: 0.5rem;",
                    ),
                    "Podcast",
                    href="/test",
                    style="""
                        display: flex; align-items: center;
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                        margin-right: 0.5rem;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
                A(
                    Span(
                        create_heroicon_svg("summary", "18"),
                        style="margin-right: 0.5rem;",
                    ),
                    "Summary",
                    href="/test",
                    style="""
                        display: flex; align-items: center;
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                        margin-right: 0.5rem;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
                A(
                    Span(
                        create_heroicon_svg("note", "18"), style="margin-right: 0.5rem;"
                    ),
                    "Notes",
                    href="/test",
                    style="""
                        display: flex; align-items: center;
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
                style="display: flex; align-items: center;",
            ),
            # Sign in and upgrade buttons
            Div(
                A(
                    "Sign in",
                    href="/profile",
                    style="""
                        color: var(--text-primary);
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 0.9rem;
                        margin-right: 1rem;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        transition: all 0.2s;
                    """,
                    onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                    onmouseout="this.style.backgroundColor='transparent'",
                ),
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
                style="display: flex; align-items: center;",
            ),
            style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; border-bottom: 1px solid var(--border-light);",
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
                            create_heroicon_svg("upload", "32"),
                            style="margin-bottom: 0.5rem; display: block; color: var(--primary-color);",
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
                            create_heroicon_svg("link", "32"),
                            style="margin-bottom: 0.5rem; display: block; color: var(--primary-color);",
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
                            create_heroicon_svg("record", "32"),
                            style="margin-bottom: 0.5rem; display: block; color: var(--primary-color);",
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
                    create_heroicon_svg("arrow-up", "16"),
                    style="""
                    position: absolute;
                    right: 1rem;
                    top: 50%;
                    transform: translateY(-50%);
                    background: var(--primary-color);
                    color: white;
                    padding: 0.5rem;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                """,
                ),
                style="position: relative; max-width: 600px; margin: 0 auto 3rem auto;",
            ),
            # Learn+ feature
            Div(
                A(
                    "Learn+",
                    href="/chat",
                    style="""
                        background: var(--bg-primary);
                        border: 2px solid var(--primary-color);
                        border-radius: var(--radius-lg);
                        padding: 1rem 2rem;
                        text-decoration: none;
                        color: var(--primary-color);
                        font-weight: 600;
                        font-size: 1rem;
                        transition: all 0.3s ease;
                        display: inline-block;
                        margin-bottom: 3rem;
                    """,
                    onmouseover="this.style.background='var(--primary-color)'; this.style.color='white'; this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'",
                    onmouseout="this.style.background='var(--bg-primary)'; this.style.color='var(--primary-color)'; this.style.transform='translateY(0)'; this.style.boxShadow='none'",
                ),
                style="text-align: center;",
            ),
            # Explore section
            Div(
                Div(
                    H2(
                        "Explore",
                        style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);",
                    ),
                    A(
                        "View all",
                        href="/progress",
                        style="""
                            color: var(--primary-color);
                            text-decoration: none;
                            font-weight: 500;
                            font-size: 0.9rem;
                            transition: all 0.2s;
                        """,
                        onmouseover="this.style.textDecoration='underline'",
                        onmouseout="this.style.textDecoration='none'",
                    ),
                    style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;",
                ),
                # Content grid with sample items
                Div(
                    A(
                        Div(
                            Div(
                                "🧠",
                                style="""
                                    width: 100%;
                                    height: 120px;
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    border-radius: var(--radius);
                                    margin-bottom: 0.75rem;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    color: white;
                                    font-size: 3rem;
                                """,
                            ),
                            Div(
                                Div(
                                    "Optimal Protocols for Studying and Learning",
                                    style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; line-height: 1.3;",
                                ),
                                Div(
                                    "6 months ago",
                                    style="font-size: 0.8rem; color: var(--text-muted);",
                                ),
                                style="padding: 0.5rem 0;",
                            ),
                        ),
                        href="/chat",
                        style="""
                            display: block;
                            text-decoration: none;
                            color: var(--text-primary);
                            background: var(--bg-primary);
                            border-radius: var(--radius-lg);
                            overflow: hidden;
                            transition: all 0.3s ease;
                            border: 1px solid var(--border-light);
                        """,
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'; this.style.borderColor='var(--border-color)'",
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border-light)'",
                    ),
                    A(
                        Div(
                            Div(
                                "🤖",
                                style="""
                                    width: 100%;
                                    height: 120px;
                                    background: var(--bg-tertiary);
                                    border-radius: var(--radius);
                                    margin-bottom: 0.75rem;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 3rem;
                                """,
                            ),
                            Div(
                                Div(
                                    "Introduction To Advanced Algorithms",
                                    style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; line-height: 1.3;",
                                ),
                                Div(
                                    "6 months ago",
                                    style="font-size: 0.8rem; color: var(--text-muted);",
                                ),
                                style="padding: 0.5rem 0;",
                            ),
                        ),
                        href="/chat",
                        style="""
                            display: block;
                            text-decoration: none;
                            color: var(--text-primary);
                            background: var(--bg-primary);
                            border-radius: var(--radius-lg);
                            overflow: hidden;
                            transition: all 0.3s ease;
                            border: 1px solid var(--border-light);
                        """,
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'; this.style.borderColor='var(--border-color)'",
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border-light)'",
                    ),
                    A(
                        Div(
                            Div(
                                "💬",
                                style="""
                                    width: 100%;
                                    height: 120px;
                                    background: var(--bg-tertiary);
                                    border-radius: var(--radius);
                                    margin-bottom: 0.75rem;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 3rem;
                                """,
                            ),
                            Div(
                                Div(
                                    "Think Fast, Talk Smart: Communication",
                                    style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; line-height: 1.3;",
                                ),
                                Div(
                                    "6 months ago",
                                    style="font-size: 0.8rem; color: var(--text-muted);",
                                ),
                                style="padding: 0.5rem 0;",
                            ),
                        ),
                        href="/chat",
                        style="""
                            display: block;
                            text-decoration: none;
                            color: var(--text-primary);
                            background: var(--bg-primary);
                            border-radius: var(--radius-lg);
                            overflow: hidden;
                            transition: all 0.3s ease;
                            border: 1px solid var(--border-light);
                        """,
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'; this.style.borderColor='var(--border-color)'",
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border-light)'",
                    ),
                    A(
                        Div(
                            Div(
                                "🧬",
                                style="""
                                    width: 100%;
                                    height: 120px;
                                    background: var(--bg-tertiary);
                                    border-radius: var(--radius);
                                    margin-bottom: 0.75rem;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 3rem;
                                """,
                            ),
                            Div(
                                Div(
                                    "Introduction to Cell Biology",
                                    style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; line-height: 1.3;",
                                ),
                                Div(
                                    "6 months ago",
                                    style="font-size: 0.8rem; color: var(--text-muted);",
                                ),
                                style="padding: 0.5rem 0;",
                            ),
                        ),
                        href="/chat",
                        style="""
                            display: block;
                            text-decoration: none;
                            color: var(--text-primary);
                            background: var(--bg-primary);
                            border-radius: var(--radius-lg);
                            overflow: hidden;
                            transition: all 0.3s ease;
                            border: 1px solid var(--border-light);
                        """,
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'; this.style.borderColor='var(--border-color)'",
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border-light)'",
                    ),
                    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;",
                ),
                # Show more button
                Div(
                    A(
                        "Show more",
                        href="/progress",
                        style="""
                            color: var(--primary-color);
                            text-decoration: none;
                            font-weight: 500;
                            font-size: 0.9rem;
                            padding: 0.75rem 1.5rem;
                            border: 1px solid var(--border-color);
                            border-radius: var(--radius);
                            transition: all 0.2s;
                            display: inline-block;
                        """,
                        onmouseover="this.style.backgroundColor='var(--bg-tertiary)'; this.style.borderColor='var(--primary-color)'",
                        onmouseout="this.style.backgroundColor='transparent'; this.style.borderColor='var(--border-color)'",
                    ),
                    style="text-align: center;",
                ),
                style="max-width: 1000px; margin: 0 auto;",
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
