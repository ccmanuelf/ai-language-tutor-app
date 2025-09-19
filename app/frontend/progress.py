"""
Frontend Progress Route
AI Language Tutor App - Learning Progress Tracking

Provides learning analytics and progress visualization:
- Learning streaks and statistics
- Language proficiency progress
- Conversation history metrics
"""

from fasthtml.common import *
from .layout import create_layout


def create_progress_route(app):
    """Create learning progress tracking route"""

    @app.route("/progress")
    def progress():
        """Learning progress tracking page with analytics"""
        return create_layout(
            Div(
                H1("Learning Progress", style="margin-bottom: 2rem;"),
                # Progress overview
                Div(
                    H2("Overview"),
                    Div(
                        Div(
                            H3("Current Streak"),
                            P(
                                "5 days",
                                style="font-size: 2rem; font-weight: bold; color: var(--primary-color);",
                            ),
                            cls="card",
                        ),
                        Div(
                            H3("Total Conversations"),
                            P(
                                "23",
                                style="font-size: 2rem; font-weight: bold; color: var(--secondary-color);",
                            ),
                            cls="card",
                        ),
                        Div(
                            H3("Words Learned"),
                            P(
                                "147",
                                style="font-size: 2rem; font-weight: bold; color: var(--accent-color);",
                            ),
                            cls="card",
                        ),
                        cls="grid grid-3",
                    ),
                    cls="card",
                ),
                # Language progress
                Div(
                    H2("Language Progress"),
                    Div(
                        Div(
                            H3("Spanish"),
                            P("Intermediate - 67% complete"),
                            Div(
                                style="background: var(--border-color); height: 8px; border-radius: 4px; margin: 1rem 0;",
                                children=[
                                    Div(
                                        style="background: var(--secondary-color); height: 100%; width: 67%; border-radius: 4px;"
                                    )
                                ],
                            ),
                        ),
                        Div(
                            H3("French"),
                            P("Beginner - 34% complete"),
                            Div(
                                style="background: var(--border-color); height: 8px; border-radius: 4px; margin: 1rem 0;",
                                children=[
                                    Div(
                                        style="background: var(--accent-color); height: 100%; width: 34%; border-radius: 4px;"
                                    )
                                ],
                            ),
                        ),
                        cls="grid grid-2",
                    ),
                    cls="card",
                ),
            ),
            current_page="progress",
            title="Progress Tracking - AI Language Tutor",
        )
