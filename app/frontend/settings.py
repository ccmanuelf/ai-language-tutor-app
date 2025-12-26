"""
User Settings Page
AI Language Tutor App - Unified Settings Interface

Provides easy access to:
- Tutor persona selection
- Base language configuration
- Target learning language configuration
"""

from fasthtml.common import *

from .layout import create_layout


def create_settings_routes(app):
    """Create unified settings route"""

    @app.route("/settings")
    def settings_page():
        """Main settings page with persona and language configuration"""
        return create_layout(
            Div(
                H1(
                    "Settings", style="margin-bottom: 2rem; color: var(--text-primary);"
                ),
                # Settings grid
                Div(
                    # Tutor Persona Card
                    Div(
                        Div(
                            H2(
                                "🎓 Select Your Tutor",
                                style="margin-bottom: 1rem; font-size: 1.5rem;",
                            ),
                            P(
                                "Choose the teaching style that works best for you.",
                                style="color: var(--text-secondary); margin-bottom: 1.5rem;",
                            ),
                            A(
                                "Configure Tutor Persona →",
                                href="/profile/persona",
                                style="""
                                    display: inline-block;
                                    background: var(--primary-color);
                                    color: white;
                                    padding: 0.75rem 1.5rem;
                                    border-radius: var(--radius);
                                    text-decoration: none;
                                    font-weight: 600;
                                    transition: all 0.2s;
                                """,
                                onmouseover="this.style.background='var(--primary-dark)'",
                                onmouseout="this.style.background='var(--primary-color)'",
                            ),
                            style="padding: 2rem; background: var(--bg-primary); border-radius: var(--radius-lg); box-shadow: var(--shadow);",
                        ),
                    ),
                    # Language Configuration Card
                    Div(
                        Div(
                            H2(
                                "🌍 Language Settings",
                                style="margin-bottom: 1rem; font-size: 1.5rem;",
                            ),
                            P(
                                "Set your native language and the language you want to learn.",
                                style="color: var(--text-secondary); margin-bottom: 1.5rem;",
                            ),
                            # Base Language
                            Div(
                                Label(
                                    "Your Native Language",
                                    style="display: block; font-weight: 600; margin-bottom: 0.5rem;",
                                ),
                                Select(
                                    Option("English", value="en", selected=True),
                                    Option("Spanish", value="es"),
                                    Option("French", value="fr"),
                                    Option("German", value="de"),
                                    Option("Italian", value="it"),
                                    Option("Portuguese", value="pt"),
                                    Option("Chinese", value="zh"),
                                    Option("Japanese", value="ja"),
                                    Option("Korean", value="ko"),
                                    name="base_language",
                                    id="base_language",
                                    style="""
                                        width: 100%;
                                        padding: 0.75rem;
                                        border: 2px solid var(--border-color);
                                        border-radius: var(--radius);
                                        font-size: 1rem;
                                    """,
                                ),
                                style="margin-bottom: 1.5rem;",
                            ),
                            # Target Language
                            Div(
                                Label(
                                    "Language to Learn",
                                    style="display: block; font-weight: 600; margin-bottom: 0.5rem;",
                                ),
                                Select(
                                    Option("Spanish", value="es", selected=True),
                                    Option("English", value="en"),
                                    Option("French", value="fr"),
                                    Option("German", value="de"),
                                    Option("Italian", value="it"),
                                    Option("Portuguese", value="pt"),
                                    Option("Chinese", value="zh"),
                                    Option("Japanese", value="ja"),
                                    Option("Korean", value="ko"),
                                    name="target_language",
                                    id="target_language",
                                    style="""
                                        width: 100%;
                                        padding: 0.75rem;
                                        border: 2px solid var(--border-color);
                                        border-radius: var(--radius);
                                        font-size: 1rem;
                                    """,
                                ),
                                style="margin-bottom: 1.5rem;",
                            ),
                            Button(
                                "Save Language Settings",
                                onclick="saveLanguageSettings()",
                                style="""
                                    background: var(--success);
                                    color: white;
                                    padding: 0.75rem 1.5rem;
                                    border: none;
                                    border-radius: var(--radius);
                                    font-weight: 600;
                                    font-size: 1rem;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                """,
                                onmouseover="this.style.opacity='0.9'",
                                onmouseout="this.style.opacity='1'",
                            ),
                            style="padding: 2rem; background: var(--bg-primary); border-radius: var(--radius-lg); box-shadow: var(--shadow);",
                        ),
                    ),
                    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; margin-bottom: 2rem;",
                ),
                # JavaScript for saving
                Script("""
                    async function saveLanguageSettings() {
                        const baseLanguage = document.getElementById('base_language').value;
                        const targetLanguage = document.getElementById('target_language').value;

                        // TODO: Call backend API to save language preferences
                        // For now, just show confirmation
                        alert(`Settings saved!\\nNative: ${baseLanguage}\\nLearning: ${targetLanguage}`);

                        // Store in localStorage temporarily
                        localStorage.setItem('base_language', baseLanguage);
                        localStorage.setItem('target_language', targetLanguage);
                    }

                    // Load saved settings on page load
                    window.addEventListener('DOMContentLoaded', () => {
                        const savedBase = localStorage.getItem('base_language');
                        const savedTarget = localStorage.getItem('target_language');

                        if (savedBase) {
                            document.getElementById('base_language').value = savedBase;
                        }
                        if (savedTarget) {
                            document.getElementById('target_language').value = savedTarget;
                        }
                    });
                """),
                style="max-width: 1200px; margin: 0 auto; padding: 2rem;",
            ),
            title="Settings - AI Language Tutor",
        )
