"""
Frontend Home Route
AI Language Tutor App - content-based learning-Style Landing Page

Provides:
- content-based learning-inspired main interface
- Upload, Paste, Record options
- Learning spaces and content exploration
- Clean, centered layout matching content-based learning design
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
    """Create content-based learning-style sidebar navigation with HeroIcons"""
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
        # Content Organization section (Session 129)
        Div(
            H3(
                "Content Organization",
                style="color: var(--text-primary); font-size: 1rem; margin-bottom: 1rem; padding: 0 1rem;",
            ),
            A(
                Span(create_heroicon_svg("book", "20"), style="margin-right: 0.75rem;"),
                "Content Library",
                href="/library",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("folder", "20"), style="margin-right: 0.75rem;"
                ),
                "My Collections",
                href="/collections",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(create_heroicon_svg("star", "20"), style="margin-right: 0.75rem;"),
                "Favorites",
                href="/favorites",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            A(
                Span(
                    create_heroicon_svg("target", "20"), style="margin-right: 0.75rem;"
                ),
                "Study Stats",
                href="/study-stats",
                style="display: flex; align-items: center; padding: 0.75rem 1rem; text-decoration: none; color: var(--text-primary); border-radius: var(--radius); margin-bottom: 0.5rem; transition: all 0.2s;",
                onmouseover="this.style.backgroundColor='var(--bg-tertiary)'",
                onmouseout="this.style.backgroundColor='transparent'",
            ),
            style="margin-bottom: 2rem; border-bottom: 1px solid var(--border-light); padding-bottom: 1rem;",
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
    """Create content-based learning-style main content area"""
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
            # Center toolbar with content-based learning features
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
                # Upload card - Updated for content processing
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
                            "PDF, DOCX, TXT files",
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
                    onclick="showContentProcessingModal('upload')",
                    onmouseover="this.style.borderColor='var(--primary-color)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'",
                    onmouseout="this.style.borderColor='var(--border-color)'; this.style.transform='translateY(0)'; this.style.boxShadow='none'",
                ),
                # Paste card (marked as popular) - Updated for content processing
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
                    onclick="showContentProcessingModal('paste')",
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
            # Trending Scenarios Section
            Div(
                Div(
                    H2(
                        "🔥 Trending Scenarios",
                        style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);",
                    ),
                    A(
                        "View all",
                        href="/discover",
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
                # Trending scenarios cards (loaded via JavaScript)
                Div(
                    id="trendingScenarios",
                    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;",
                ),
                style="max-width: 1000px; margin: 0 auto 3rem auto;",
            ),
            # Recommended For You Section
            Div(
                Div(
                    H2(
                        "✨ Recommended For You",
                        style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);",
                    ),
                    A(
                        "See more",
                        href="/discover?tab=for-you",
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
                # Recommended scenarios cards (loaded via JavaScript)
                Div(
                    id="recommendedScenarios",
                    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;",
                ),
                style="max-width: 1000px; margin: 0 auto 3rem auto;",
            ),
            # Popular Collections Section
            Div(
                Div(
                    H2(
                        "📚 Popular Collections",
                        style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);",
                    ),
                    A(
                        "Browse all",
                        href="/my-collections?tab=public",
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
                # Popular collections cards (loaded via JavaScript)
                Div(
                    id="popularCollections",
                    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;",
                ),
                style="max-width: 1000px; margin: 0 auto 3rem auto;",
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


def create_content_processing_modals():
    """Create modals for content processing functionality"""
    return Div(
        # Upload modal
        Div(
            Div(
                Div(
                    H2("Upload Content", cls="modal-title"),
                    Button("×", cls="close", onclick="closeModal('uploadModal')"),
                    cls="modal-header",
                ),
                Form(
                    Div(
                        Label("Choose File", cls="form-label"),
                        Input(
                            type="file",
                            id="fileInput",
                            accept=".pdf,.docx,.doc,.txt,.md",
                            cls="form-input",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Learning Materials to Generate", cls="form-label"),
                        Div(
                            Label(
                                Input(type="checkbox", value="summary", checked=True),
                                " Summary",
                                style="margin-right: 1rem; display: inline-flex; align-items: center;",
                            ),
                            Label(
                                Input(
                                    type="checkbox", value="flashcards", checked=True
                                ),
                                " Flashcards",
                                style="margin-right: 1rem; display: inline-flex; align-items: center;",
                            ),
                            Label(
                                Input(
                                    type="checkbox", value="key_concepts", checked=True
                                ),
                                " Key Concepts",
                                style="display: inline-flex; align-items: center;",
                            ),
                            style="display: flex; flex-wrap: wrap; gap: 0.5rem;",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Button(
                            "Cancel",
                            type="button",
                            cls="btn btn-secondary",
                            onclick="closeModal('uploadModal')",
                            style="margin-right: 1rem;",
                        ),
                        Button("Process Content", type="submit", cls="btn btn-primary"),
                        style="display: flex; justify-content: flex-end;",
                    ),
                    onsubmit="handleFileUpload(event)",
                ),
                Div(
                    Div(
                        id="uploadStatus",
                        style="font-weight: 600; margin-bottom: 0.5rem;",
                    ),
                    Div(
                        Div(id="uploadProgress", cls="progress-fill"),
                        cls="progress-bar",
                    ),
                    Div(
                        id="uploadDetails",
                        style="font-size: 0.9rem; color: var(--text-muted);",
                    ),
                    cls="processing-status",
                    id="uploadProcessingStatus",
                ),
                cls="modal-content",
            ),
            id="uploadModal",
            cls="modal",
        ),
        # Paste URL modal
        Div(
            Div(
                Div(
                    H2("Process from URL", cls="modal-title"),
                    Button("×", cls="close", onclick="closeModal('pasteModal')"),
                    cls="modal-header",
                ),
                Form(
                    Div(
                        Label("YouTube URL or Website", cls="form-label"),
                        Input(
                            type="url",
                            id="urlInput",
                            placeholder="https://youtube.com/watch?v=... or any website URL",
                            cls="form-input",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Learning Materials to Generate", cls="form-label"),
                        Div(
                            Label(
                                Input(type="checkbox", value="summary", checked=True),
                                " Summary",
                                style="margin-right: 1rem; display: inline-flex; align-items: center;",
                            ),
                            Label(
                                Input(
                                    type="checkbox", value="flashcards", checked=True
                                ),
                                " Flashcards",
                                style="margin-right: 1rem; display: inline-flex; align-items: center;",
                            ),
                            Label(
                                Input(
                                    type="checkbox", value="key_concepts", checked=True
                                ),
                                " Key Concepts",
                                style="display: inline-flex; align-items: center;",
                            ),
                            style="display: flex; flex-wrap: wrap; gap: 0.5rem;",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Button(
                            "Cancel",
                            type="button",
                            cls="btn btn-secondary",
                            onclick="closeModal('pasteModal')",
                            style="margin-right: 1rem;",
                        ),
                        Button("Process Content", type="submit", cls="btn btn-primary"),
                        style="display: flex; justify-content: flex-end;",
                    ),
                    onsubmit="handleUrlSubmit(event)",
                ),
                Div(
                    Div(
                        id="pasteStatus",
                        style="font-weight: 600; margin-bottom: 0.5rem;",
                    ),
                    Div(
                        Div(id="pasteProgress", cls="progress-fill"), cls="progress-bar"
                    ),
                    Div(
                        id="pasteDetails",
                        style="font-size: 0.9rem; color: var(--text-muted);",
                    ),
                    cls="processing-status",
                    id="pasteProcessingStatus",
                ),
                cls="modal-content",
            ),
            id="pasteModal",
            cls="modal",
        ),
    )


def create_content_processing_scripts():
    """Create JavaScript for content processing functionality"""
    return Script("""
        // Load trending scenarios, recommended scenarios, and collections on page load
        document.addEventListener('DOMContentLoaded', async function() {
            // Load trending scenarios
            try {
                const trendingResponse = await fetch('/api/v1/scenario-organization/trending?limit=4');
                if (trendingResponse.ok) {
                    const data = await trendingResponse.json();
                    renderScenarioCards(data.scenarios, 'trendingScenarios');
                }
            } catch (error) {
                console.error('Failed to load trending scenarios:', error);
            }

            // Load recommended scenarios (if user is logged in)
            try {
                const recommendedResponse = await fetch('/api/v1/scenario-organization/recommended?limit=4');
                if (recommendedResponse.ok) {
                    const data = await recommendedResponse.json();
                    renderScenarioCards(data.scenarios, 'recommendedScenarios');
                }
            } catch (error) {
                console.error('Failed to load recommended scenarios:', error);
                // Hide section if not logged in or error
                document.getElementById('recommendedScenarios').closest('div').style.display = 'none';
            }

            // Load popular collections
            try {
                const collectionsResponse = await fetch('/api/v1/scenario-organization/public-collections?limit=3');
                if (collectionsResponse.ok) {
                    const data = await collectionsResponse.json();
                    renderCollectionCards(data.collections, 'popularCollections');
                }
            } catch (error) {
                console.error('Failed to load popular collections:', error);
            }
        });

        // Render scenario cards
        function renderScenarioCards(scenarios, containerId) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            scenarios.forEach(scenario => {
                const card = createScenarioCard(scenario);
                container.appendChild(card);
            });
        }

        // Create scenario card element
        function createScenarioCard(scenario) {
            const card = document.createElement('a');
            card.href = `/chat?scenario_id=${scenario.scenario_id}`;
            card.style.cssText = `
                display: block;
                text-decoration: none;
                color: var(--text-primary);
                background: var(--bg-primary);
                border-radius: var(--radius-lg);
                overflow: hidden;
                transition: all 0.3s ease;
                border: 1px solid var(--border-light);
            `;

            const categoryColors = {
                'restaurant': '#10b981',
                'travel': '#3b82f6',
                'shopping': '#f59e0b',
                'business': '#6366f1',
                'social': '#ec4899',
                'healthcare': '#ef4444',
                'emergency': '#dc2626',
                'daily_life': '#8b5cf6',
                'hobbies': '#14b8a6',
                'education': '#0891b2'
            };

            const categoryColor = categoryColors[scenario.category] || '#6366f1';

            card.innerHTML = `
                <div style="padding: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                        <span style="background: ${categoryColor}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600;">
                            ${scenario.category}
                        </span>
                        ${scenario.difficulty ? `<span style="color: var(--text-muted); font-size: 0.75rem;">${scenario.difficulty}</span>` : ''}
                    </div>
                    <h3 style="font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem; line-height: 1.3;">${scenario.title}</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.5;">
                        ${scenario.description?.substring(0, 100)}${scenario.description?.length > 100 ? '...' : ''}
                    </p>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid var(--border-light);">
                        <div style="display: flex; align-items: center; gap: 0.25rem; color: var(--text-muted); font-size: 0.85rem;">
                            <span>⭐</span>
                            <span>${scenario.average_rating ? scenario.average_rating.toFixed(1) : 'New'}</span>
                        </div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">
                            ${scenario.estimated_duration || 15} min
                        </div>
                    </div>
                </div>
            `;

            card.onmouseover = function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = 'var(--shadow-md)';
                this.style.borderColor = 'var(--border-color)';
            };
            card.onmouseout = function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
                this.style.borderColor = 'var(--border-light)';
            };

            return card;
        }

        // Render collection cards
        function renderCollectionCards(collections, containerId) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            collections.forEach(collection => {
                const card = createCollectionCard(collection);
                container.appendChild(card);
            });
        }

        // Create collection card element
        function createCollectionCard(collection) {
            const card = document.createElement('a');
            card.href = `/my-collections?collection_id=${collection.id}`;
            card.style.cssText = `
                display: block;
                text-decoration: none;
                color: var(--text-primary);
                background: var(--bg-primary);
                border-radius: var(--radius-lg);
                overflow: hidden;
                transition: all 0.3s ease;
                border: 1px solid var(--border-light);
            `;

            card.innerHTML = `
                <div style="padding: 1.5rem;">
                    ${collection.is_learning_path ? `
                        <div style="margin-bottom: 0.75rem;">
                            <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600;">
                                Learning Path
                            </span>
                        </div>
                    ` : ''}
                    <h3 style="font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem; line-height: 1.3;">${collection.name}</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.5;">
                        ${collection.description?.substring(0, 100)}${collection.description?.length > 100 ? '...' : ''}
                    </p>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid var(--border-light);">
                        <div style="color: var(--text-muted); font-size: 0.85rem;">
                            ${collection.scenario_count || 0} scenarios
                        </div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">
                            By ${collection.creator_username || 'Anonymous'}
                        </div>
                    </div>
                </div>
            `;

            card.onmouseover = function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = 'var(--shadow-md)';
                this.style.borderColor = 'var(--border-color)';
            };
            card.onmouseout = function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
                this.style.borderColor = 'var(--border-light)';
            };

            return card;
        }

        // Modal functionality
        function showContentProcessingModal(type) {
            if (type === 'upload') {
                document.getElementById('uploadModal').style.display = 'block';
            } else if (type === 'paste') {
                document.getElementById('pasteModal').style.display = 'block';
            }
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
            // Reset forms and status
            if (modalId === 'uploadModal') {
                document.getElementById('uploadProcessingStatus').style.display = 'none';
                document.getElementById('uploadProgress').style.width = '0%';
            } else if (modalId === 'pasteModal') {
                document.getElementById('pasteProcessingStatus').style.display = 'none';
                document.getElementById('pasteProgress').style.width = '0%';
            }
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const uploadModal = document.getElementById('uploadModal');
            const pasteModal = document.getElementById('pasteModal');
            if (event.target === uploadModal) {
                closeModal('uploadModal');
            } else if (event.target === pasteModal) {
                closeModal('pasteModal');
            }
        }

        // Handle file upload
        async function handleFileUpload(event) {
            event.preventDefault();

            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];

            if (!file) {
                alert('Please select a file');
                return;
            }

            // Get selected material types
            const materialTypes = [];
            const checkboxes = event.target.querySelectorAll('input[type="checkbox"]:checked');
            checkboxes.forEach(cb => materialTypes.push(cb.value));

            // Show processing status
            document.getElementById('uploadProcessingStatus').style.display = 'block';
            document.getElementById('uploadStatus').textContent = 'Uploading file...';
            document.getElementById('uploadProgress').style.width = '10%';

            try {
                // Create form data
                const formData = new FormData();
                formData.append('file', file);
                materialTypes.forEach(type => formData.append('material_types', type));
                formData.append('language', 'en');

                // Upload file
                const response = await fetch('/api/content/process/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Upload failed');
                }

                const result = await response.json();
                const contentId = result.content_id;

                // Start polling for progress
                pollProcessingStatus(contentId, 'upload');

            } catch (error) {
                document.getElementById('uploadStatus').textContent = 'Error: ' + error.message;
                document.getElementById('uploadDetails').textContent = 'Please try again';
            }
        }

        // Handle URL submission
        async function handleUrlSubmit(event) {
            event.preventDefault();

            const urlInput = document.getElementById('urlInput');
            const url = urlInput.value.trim();

            if (!url) {
                alert('Please enter a URL');
                return;
            }

            // Get selected material types
            const materialTypes = [];
            const checkboxes = event.target.querySelectorAll('input[type="checkbox"]:checked');
            checkboxes.forEach(cb => materialTypes.push(cb.value));

            // Show processing status
            document.getElementById('pasteProcessingStatus').style.display = 'block';
            document.getElementById('pasteStatus').textContent = 'Processing URL...';
            document.getElementById('pasteProgress').style.width = '10%';

            try {
                // Submit URL for processing
                const response = await fetch('/api/content/process/url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: url,
                        material_types: materialTypes,
                        language: 'en'
                    })
                });

                if (!response.ok) {
                    throw new Error('URL processing failed');
                }

                const result = await response.json();
                const contentId = result.content_id;

                // Start polling for progress
                pollProcessingStatus(contentId, 'paste');

            } catch (error) {
                document.getElementById('pasteStatus').textContent = 'Error: ' + error.message;
                document.getElementById('pasteDetails').textContent = 'Please check the URL and try again';
            }
        }

        // Poll processing status
        async function pollProcessingStatus(contentId, type) {
            const statusId = type + 'Status';
            const progressId = type + 'Progress';
            const detailsId = type + 'Details';

            try {
                const response = await fetch(`/api/content/status/${contentId}`);
                const status = await response.json();

                // Update UI
                document.getElementById(statusId).textContent = status.current_step;
                document.getElementById(progressId).style.width = status.progress_percentage + '%';
                document.getElementById(detailsId).textContent = status.details;

                if (status.status === 'completed') {
                    document.getElementById(statusId).textContent = 'Processing completed!';
                    document.getElementById(detailsId).textContent = `Finished in ${status.time_elapsed.toFixed(1)}s. Redirecting to results...`;

                    // Redirect to content view after 2 seconds
                    setTimeout(() => {
                        window.location.href = `/content/${contentId}`;
                    }, 2000);

                } else if (status.status === 'failed') {
                    document.getElementById(statusId).textContent = 'Processing failed';
                    document.getElementById(detailsId).textContent = status.error_message || 'Unknown error occurred';

                } else {
                    // Continue polling every 2 seconds
                    setTimeout(() => pollProcessingStatus(contentId, type), 2000);
                }

            } catch (error) {
                document.getElementById(statusId).textContent = 'Error checking status';
                document.getElementById(detailsId).textContent = 'Please refresh the page';
            }
        }
    """)


def create_home_routes(app):
    """Create content-based learning-style home routes"""

    @app.route("/")
    def home():
        """content-based learning-style main landing page"""
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

                    /* Modal styles */
                    .modal {
                        display: none;
                        position: fixed;
                        z-index: 1000;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0,0,0,0.5);
                    }

                    .modal-content {
                        background-color: var(--bg-primary);
                        margin: 5% auto;
                        padding: 2rem;
                        border: none;
                        border-radius: var(--radius-lg);
                        width: 90%;
                        max-width: 500px;
                        box-shadow: var(--shadow-md);
                    }

                    .modal-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 1.5rem;
                    }

                    .modal-title {
                        font-size: 1.5rem;
                        font-weight: 700;
                        color: var(--text-primary);
                    }

                    .close {
                        color: var(--text-muted);
                        font-size: 1.5rem;
                        font-weight: bold;
                        cursor: pointer;
                        border: none;
                        background: none;
                    }

                    .close:hover {
                        color: var(--text-primary);
                    }

                    .form-group {
                        margin-bottom: 1rem;
                    }

                    .form-label {
                        display: block;
                        margin-bottom: 0.5rem;
                        font-weight: 600;
                        color: var(--text-primary);
                    }

                    .form-input {
                        width: 100%;
                        padding: 0.75rem;
                        border: 2px solid var(--border-color);
                        border-radius: var(--radius);
                        font-size: 1rem;
                        transition: border-color 0.2s;
                    }

                    .form-input:focus {
                        outline: none;
                        border-color: var(--primary-color);
                        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
                    }

                    .btn {
                        padding: 0.75rem 1.5rem;
                        border: none;
                        border-radius: var(--radius);
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                        text-decoration: none;
                        display: inline-block;
                        text-align: center;
                    }

                    .btn-primary {
                        background: var(--primary-color);
                        color: white;
                    }

                    .btn-primary:hover {
                        background: var(--primary-dark);
                        transform: translateY(-1px);
                    }

                    .btn-secondary {
                        background: var(--bg-tertiary);
                        color: var(--text-primary);
                    }

                    .btn-secondary:hover {
                        background: var(--border-color);
                    }

                    .processing-status {
                        margin-top: 1rem;
                        padding: 1rem;
                        background: var(--bg-secondary);
                        border-radius: var(--radius);
                        display: none;
                    }

                    .progress-bar {
                        width: 100%;
                        height: 0.5rem;
                        background: var(--bg-tertiary);
                        border-radius: 0.25rem;
                        overflow: hidden;
                        margin: 0.5rem 0;
                    }

                    .progress-fill {
                        height: 100%;
                        background: var(--primary-color);
                        width: 0%;
                        transition: width 0.3s ease;
                    }
                """),
            ),
            Body(
                create_youlearn_sidebar(),
                create_main_content(),
                create_content_processing_modals(),
                create_content_processing_scripts(),
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
