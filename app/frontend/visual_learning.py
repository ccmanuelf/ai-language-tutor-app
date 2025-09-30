"""
Visual Learning Frontend
AI Language Tutor App - Task 3.2 Implementation

Frontend UI for visual learning tools:
- Grammar flowchart viewer
- Progress visualizations
- Visual vocabulary tools
- Pronunciation guides

Modern, interactive, mobile-responsive design.
"""

from fasthtml.common import *
from .layout import create_layout, create_card, create_grid
from .styles import load_styles


def create_visual_learning_routes(app):
    """Create visual learning UI routes"""

    @app.route("/visual-learning")
    def visual_learning_home():
        """Main visual learning tools page"""
        return create_layout(
            Div(
                H1("🎨 Visual Learning Tools", style="margin-bottom: 2rem;"),
                P(
                    "Enhance your learning with interactive visualizations, flowcharts, and visual aids.",
                    cls="subtitle",
                ),
                # Tool categories
                create_grid(
                    [
                        create_card(
                            [
                                Div(
                                    "📊", style="font-size: 3rem; margin-bottom: 1rem;"
                                ),
                                H3("Grammar Flowcharts"),
                                P(
                                    "Interactive flowcharts explaining grammar concepts step-by-step."
                                ),
                                A(
                                    "Explore Flowcharts →",
                                    href="/visual-learning/flowcharts",
                                    cls="btn btn-primary",
                                    style="margin-top: 1rem; display: inline-block;",
                                ),
                            ]
                        ),
                        create_card(
                            [
                                Div(
                                    "📈", style="font-size: 3rem; margin-bottom: 1rem;"
                                ),
                                H3("Progress Visualizations"),
                                P(
                                    "See your learning progress with beautiful charts and graphs."
                                ),
                                A(
                                    "View Progress →",
                                    href="/visual-learning/visualizations",
                                    cls="btn btn-primary",
                                    style="margin-top: 1rem; display: inline-block;",
                                ),
                            ]
                        ),
                        create_card(
                            [
                                Div(
                                    "📚", style="font-size: 3rem; margin-bottom: 1rem;"
                                ),
                                H3("Visual Vocabulary"),
                                P(
                                    "Learn words with images, context, and visual associations."
                                ),
                                A(
                                    "Study Vocabulary →",
                                    href="/visual-learning/vocabulary",
                                    cls="btn btn-primary",
                                    style="margin-top: 1rem; display: inline-block;",
                                ),
                            ]
                        ),
                        create_card(
                            [
                                Div("🗣️", style="font-size: 3rem; margin-bottom: 1rem;"),
                                H3("Pronunciation Guides"),
                                P("Master pronunciation with visual and audio guides."),
                                A(
                                    "Practice Pronunciation →",
                                    href="/visual-learning/pronunciation",
                                    cls="btn btn-primary",
                                    style="margin-top: 1rem; display: inline-block;",
                                ),
                            ]
                        ),
                    ],
                    columns=2,
                ),
                # Quick stats
                Div(
                    H2(
                        "Learning Resources",
                        style="margin-top: 3rem; margin-bottom: 1.5rem;",
                    ),
                    create_grid(
                        [
                            Div(
                                Div(
                                    "24",
                                    style="font-size: 2.5rem; font-weight: bold; color: var(--primary-color);",
                                ),
                                P(
                                    "Grammar Flowcharts",
                                    style="color: var(--text-secondary);",
                                ),
                                cls="text-center",
                                style="padding: 2rem; background: var(--bg-primary); border-radius: var(--radius); box-shadow: var(--shadow-sm);",
                            ),
                            Div(
                                Div(
                                    "156",
                                    style="font-size: 2.5rem; font-weight: bold; color: var(--secondary-color);",
                                ),
                                P(
                                    "Visual Vocabulary",
                                    style="color: var(--text-secondary);",
                                ),
                                cls="text-center",
                                style="padding: 2rem; background: var(--bg-primary); border-radius: var(--radius); box-shadow: var(--shadow-sm);",
                            ),
                            Div(
                                Div(
                                    "89",
                                    style="font-size: 2.5rem; font-weight: bold; color: var(--accent-color);",
                                ),
                                P(
                                    "Pronunciation Guides",
                                    style="color: var(--text-secondary);",
                                ),
                                cls="text-center",
                                style="padding: 2rem; background: var(--bg-primary); border-radius: var(--radius); box-shadow: var(--shadow-sm);",
                            ),
                        ],
                        columns=3,
                    ),
                ),
            ),
            current_page="visual-learning",
            title="Visual Learning Tools - AI Language Tutor",
        )

    @app.route("/visual-learning/flowcharts")
    def flowcharts_page():
        """Grammar flowcharts page"""
        return create_layout(
            Div(
                # Header
                Div(
                    H1("📊 Grammar Flowcharts"),
                    P("Interactive visual guides for understanding grammar concepts"),
                    style="margin-bottom: 2rem;",
                ),
                # Filter options
                Div(
                    Div(
                        Label("Language:"),
                        Select(
                            Option("All Languages", value=""),
                            Option("Spanish", value="es"),
                            Option("French", value="fr"),
                            Option("Chinese", value="zh"),
                            id="language-filter",
                            style="margin-left: 0.5rem; padding: 0.5rem; border-radius: var(--radius); border: 1px solid var(--border-color);",
                        ),
                        style="display: inline-block; margin-right: 2rem;",
                    ),
                    Div(
                        Label("Difficulty:"),
                        Select(
                            Option("All Levels", value=""),
                            Option("Beginner (1-2)", value="1-2"),
                            Option("Intermediate (3)", value="3"),
                            Option("Advanced (4-5)", value="4-5"),
                            id="difficulty-filter",
                            style="margin-left: 0.5rem; padding: 0.5rem; border-radius: var(--radius); border: 1px solid var(--border-color);",
                        ),
                        style="display: inline-block;",
                    ),
                    cls="card",
                    style="margin-bottom: 2rem;",
                ),
                # Flowchart examples
                Div(
                    H2("Available Flowcharts", style="margin-bottom: 1.5rem;"),
                    create_grid(
                        [
                            _create_flowchart_card(
                                "Spanish Verb Conjugation",
                                "Present Tense",
                                "es",
                                2,
                                "Learn regular -ar, -er, -ir verb conjugations",
                            ),
                            _create_flowchart_card(
                                "French Sentence Structure",
                                "Subject-Verb-Object",
                                "fr",
                                1,
                                "Master basic French sentence construction",
                            ),
                            _create_flowchart_card(
                                "Chinese Tense Usage",
                                "Time Expressions",
                                "zh",
                                3,
                                "Understanding time in Mandarin Chinese",
                            ),
                            _create_flowchart_card(
                                "Spanish Conditional Forms",
                                "Si Clauses",
                                "es",
                                4,
                                "Master conditional sentences in Spanish",
                            ),
                        ],
                        columns=2,
                    ),
                ),
            ),
            current_page="visual-learning",
            title="Grammar Flowcharts - Visual Learning",
        )

    @app.route("/visual-learning/visualizations")
    def visualizations_page():
        """Progress visualizations page"""
        return create_layout(
            Div(
                H1("📈 Progress Visualizations", style="margin-bottom: 2rem;"),
                P(
                    "Track your learning journey with interactive charts",
                    cls="subtitle",
                ),
                # Visualization tabs
                Div(
                    Div(
                        Button(
                            "Weekly Progress",
                            cls="tab-btn active",
                            **{"data-tab": "weekly"},
                        ),
                        Button(
                            "Skill Breakdown", cls="tab-btn", **{"data-tab": "skills"}
                        ),
                        Button(
                            "Learning Streaks", cls="tab-btn", **{"data-tab": "streaks"}
                        ),
                        Button("Word Mastery", cls="tab-btn", **{"data-tab": "words"}),
                        cls="tab-nav",
                        style="display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;",
                    ),
                    # Weekly progress tab
                    Div(
                        create_card(
                            [
                                H3("Weekly Learning Activity"),
                                Div(
                                    # Placeholder for chart
                                    Div(
                                        style="height: 300px; display: flex; align-items: flex-end; justify-content: space-around; padding: 2rem; background: var(--bg-secondary); border-radius: var(--radius);",
                                        children=[
                                            Div(
                                                style=f"width: 60px; height: {h}%; background: var(--primary-color); border-radius: var(--radius-sm);"
                                            )
                                            for h in [45, 70, 55, 85, 90, 60, 75]
                                        ],
                                    ),
                                    P(
                                        "Mon   Tue   Wed   Thu   Fri   Sat   Sun",
                                        style="text-align: center; margin-top: 1rem; color: var(--text-secondary);",
                                    ),
                                ),
                            ]
                        ),
                        **{"data-content": "weekly", "class": "tab-content active"},
                    ),
                    # Skills tab
                    Div(
                        create_card(
                            [
                                H3("Skill Development"),
                                Div(
                                    _create_skill_bar(
                                        "Speaking", 75, "--secondary-color"
                                    ),
                                    _create_skill_bar(
                                        "Listening", 82, "--primary-color"
                                    ),
                                    _create_skill_bar("Reading", 68, "--accent-color"),
                                    _create_skill_bar("Writing", 55, "--warning-color"),
                                    style="padding: 1rem 0;",
                                ),
                            ]
                        ),
                        **{
                            "data-content": "skills",
                            "class": "tab-content",
                            "style": "display: none;",
                        },
                    ),
                    # Streaks tab
                    Div(
                        create_card(
                            [
                                H3("Learning Streaks"),
                                Div(
                                    Div(
                                        Div("🔥", style="font-size: 4rem;"),
                                        Div(
                                            "14 Days",
                                            style="font-size: 2.5rem; font-weight: bold; color: var(--primary-color);",
                                        ),
                                        P(
                                            "Current Streak",
                                            style="color: var(--text-secondary);",
                                        ),
                                        cls="text-center",
                                    ),
                                    Div(
                                        Div(
                                            P(
                                                "Longest Streak: 28 days",
                                                style="font-weight: 600;",
                                            ),
                                            P(
                                                "This Month: 20 days",
                                                style="color: var(--text-secondary);",
                                            ),
                                            P(
                                                "Total Active Days: 156",
                                                style="color: var(--text-secondary);",
                                            ),
                                        ),
                                        style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border-color);",
                                    ),
                                ),
                            ]
                        ),
                        **{
                            "data-content": "streaks",
                            "class": "tab-content",
                            "style": "display: none;",
                        },
                    ),
                    # Words tab
                    Div(
                        create_card(
                            [
                                H3("Vocabulary Mastery"),
                                Div(
                                    _create_mastery_ring(147, 250, "Words Learned"),
                                    Div(
                                        Div(
                                            Span(
                                                "●",
                                                style="color: var(--success-color); font-size: 1.5rem;",
                                            ),
                                            Span(
                                                " Mastered: 89",
                                                style="margin-left: 0.5rem; font-weight: 600;",
                                            ),
                                            style="margin-bottom: 0.5rem;",
                                        ),
                                        Div(
                                            Span(
                                                "●",
                                                style="color: var(--primary-color); font-size: 1.5rem;",
                                            ),
                                            Span(
                                                " Learning: 47",
                                                style="margin-left: 0.5rem; font-weight: 600;",
                                            ),
                                            style="margin-bottom: 0.5rem;",
                                        ),
                                        Div(
                                            Span(
                                                "●",
                                                style="color: var(--warning-color); font-size: 1.5rem;",
                                            ),
                                            Span(
                                                " Review: 11",
                                                style="margin-left: 0.5rem; font-weight: 600;",
                                            ),
                                        ),
                                        style="margin-top: 2rem;",
                                    ),
                                ),
                            ]
                        ),
                        **{
                            "data-content": "words",
                            "class": "tab-content",
                            "style": "display: none;",
                        },
                    ),
                ),
            ),
            current_page="visual-learning",
            title="Progress Visualizations - Visual Learning",
        )

    @app.route("/visual-learning/vocabulary")
    def vocabulary_page():
        """Visual vocabulary page"""
        return create_layout(
            Div(
                H1("📚 Visual Vocabulary", style="margin-bottom: 2rem;"),
                P(
                    "Learn words with images, context, and visual associations",
                    cls="subtitle",
                ),
                # Vocabulary cards
                create_grid(
                    [
                        _create_vocabulary_card(
                            "casa",
                            "house",
                            "es",
                            "/kɑː.sɑː/",
                            "Mi casa es grande.",
                            "My house is big.",
                        ),
                        _create_vocabulary_card(
                            "manger",
                            "to eat",
                            "fr",
                            "/mɑ̃.ʒe/",
                            "J'aime manger des pommes.",
                            "I like to eat apples.",
                        ),
                        _create_vocabulary_card(
                            "学习",
                            "to study",
                            "zh",
                            "/xué xí/",
                            "我喜欢学习中文。",
                            "I like to study Chinese.",
                        ),
                        _create_vocabulary_card(
                            "amigo",
                            "friend",
                            "es",
                            "/ɑː.miː.ɡoʊ/",
                            "Él es mi mejor amigo.",
                            "He is my best friend.",
                        ),
                    ],
                    columns=2,
                ),
            ),
            current_page="visual-learning",
            title="Visual Vocabulary - Visual Learning",
        )

    @app.route("/visual-learning/pronunciation")
    def pronunciation_page():
        """Pronunciation guides page"""
        return create_layout(
            Div(
                H1("🗣️ Pronunciation Guides", style="margin-bottom: 2rem;"),
                P("Master pronunciation with visual and audio guides", cls="subtitle"),
                # Pronunciation guide cards
                Div(
                    create_grid(
                        [
                            _create_pronunciation_card(
                                "gracias",
                                "es",
                                "/ˈɡɾa.sjas/",
                                "gra-see-as",
                                ["Roll the 'r' sound", "Stress on first syllable"],
                            ),
                            _create_pronunciation_card(
                                "merci",
                                "fr",
                                "/mɛʁ.si/",
                                "mehr-see",
                                ["Nasal 'r' sound", "Short 'i' at end"],
                            ),
                            _create_pronunciation_card(
                                "谢谢",
                                "zh",
                                "/ɕjè.ɕjè/",
                                "shyeh-shyeh",
                                ["Both syllables use falling tone", "Soft 'sh' sound"],
                            ),
                        ],
                        columns=3,
                    )
                ),
            ),
            current_page="visual-learning",
            title="Pronunciation Guides - Visual Learning",
        )


# Helper functions for creating visual elements


def _create_flowchart_card(
    title: str, subtitle: str, language: str, difficulty: int, description: str
):
    """Create a flowchart preview card"""
    lang_colors = {"es": "#f59e0b", "fr": "#3b82f6", "zh": "#ef4444"}
    difficulty_stars = "⭐" * difficulty

    return create_card(
        [
            Div(
                Span(
                    language.upper(),
                    style=f"background: {lang_colors.get(language, '#6366f1')}; color: white; padding: 0.25rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.75rem; font-weight: 600;",
                ),
                Span(difficulty_stars, style="margin-left: 0.5rem; font-size: 0.9rem;"),
                style="margin-bottom: 1rem;",
            ),
            H3(title, style="margin-bottom: 0.5rem;"),
            P(
                subtitle,
                style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;",
            ),
            P(
                description,
                style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;",
            ),
            Button("View Flowchart →", cls="btn btn-secondary", style="width: 100%;"),
        ]
    )


def _create_skill_bar(skill: str, percentage: int, color: str):
    """Create a skill progress bar"""
    return Div(
        Div(
            Span(skill, style="font-weight: 600;"),
            Span(f"{percentage}%", style="float: right; color: var(--text-secondary);"),
            style="margin-bottom: 0.5rem;",
        ),
        Div(
            Div(
                style=f"height: 100%; width: {percentage}%; background: var({color}); border-radius: var(--radius-sm); transition: width 0.3s ease;"
            ),
            style="height: 12px; background: var(--bg-tertiary); border-radius: var(--radius-sm); overflow: hidden;",
        ),
        style="margin-bottom: 1.5rem;",
    )


def _create_mastery_ring(current: int, total: int, label: str):
    """Create a circular progress indicator"""
    percentage = int((current / total) * 100)

    return Div(
        Div(
            Div(
                Div(
                    str(current),
                    style="font-size: 2.5rem; font-weight: bold; color: var(--primary-color);",
                ),
                Div(
                    f"of {total}",
                    style="color: var(--text-secondary); font-size: 0.9rem;",
                ),
                Div(
                    label,
                    style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;",
                ),
                style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;",
            ),
            style=f"width: 200px; height: 200px; border-radius: 50%; background: conic-gradient(var(--primary-color) 0% {percentage}%, var(--bg-tertiary) {percentage}% 100%); position: relative; margin: 2rem auto;",
        )
    )


def _create_vocabulary_card(
    word: str,
    translation: str,
    language: str,
    phonetic: str,
    example: str,
    example_translation: str,
):
    """Create a vocabulary learning card"""
    lang_colors = {"es": "#f59e0b", "fr": "#3b82f6", "zh": "#ef4444"}

    return create_card(
        [
            Div(
                Span(
                    language.upper(),
                    style=f"background: {lang_colors.get(language, '#6366f1')}; color: white; padding: 0.25rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.75rem; font-weight: 600;",
                ),
                style="margin-bottom: 1rem;",
            ),
            Div(
                Div(
                    word,
                    style="font-size: 2rem; font-weight: bold; color: var(--primary-color); margin-bottom: 0.25rem;",
                ),
                Div(
                    translation,
                    style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 0.5rem;",
                ),
                Div(
                    phonetic,
                    style="font-family: monospace; color: var(--text-muted); font-size: 0.9rem;",
                ),
            ),
            Div(
                Div(
                    "Example:",
                    style="font-weight: 600; margin-bottom: 0.5rem; margin-top: 1.5rem;",
                ),
                P(example, style="font-style: italic; margin-bottom: 0.25rem;"),
                P(
                    example_translation,
                    style="color: var(--text-secondary); font-size: 0.9rem;",
                ),
            ),
            Div(
                Button("🔊 Listen", cls="btn btn-sm", style="margin-right: 0.5rem;"),
                Button("📝 Practice", cls="btn btn-sm btn-secondary"),
                style="margin-top: 1.5rem;",
            ),
        ]
    )


def _create_pronunciation_card(
    word: str, language: str, ipa: str, phonetic: str, tips: list
):
    """Create a pronunciation guide card"""
    lang_colors = {"es": "#f59e0b", "fr": "#3b82f6", "zh": "#ef4444"}

    return create_card(
        [
            Div(
                Span(
                    language.upper(),
                    style=f"background: {lang_colors.get(language, '#6366f1')}; color: white; padding: 0.25rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.75rem; font-weight: 600;",
                ),
                style="margin-bottom: 1rem;",
            ),
            Div(
                word,
                style="font-size: 2rem; font-weight: bold; color: var(--primary-color); margin-bottom: 0.5rem; text-align: center;",
            ),
            Div(
                Div(
                    f"IPA: {ipa}",
                    style="font-family: monospace; color: var(--text-secondary); font-size: 0.9rem; text-align: center;",
                ),
                Div(
                    phonetic,
                    style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem; text-align: center;",
                ),
            ),
            Div(
                Div(
                    "Tips:",
                    style="font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem;",
                ),
                Ul(
                    *[
                        Li(
                            tip,
                            style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;",
                        )
                        for tip in tips
                    ],
                    style="padding-left: 1.5rem;",
                ),
            ),
            Button(
                "🔊 Listen & Practice",
                cls="btn btn-primary",
                style="width: 100%; margin-top: 1rem;",
            ),
        ]
    )
