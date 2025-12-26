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
                # Feedback message area
                Div(
                    id="settings_feedback",
                    style="margin-top: 1rem; padding: 1rem; border-radius: var(--radius); display: none;",
                ),
                # JavaScript for saving and loading
                Script("""
                    // Load user settings from backend on page load
                    async function loadLanguageSettings() {
                        try {
                            // Get current user profile from backend
                            const response = await fetch('http://localhost:8000/api/v1/auth/me', {
                                method: 'GET',
                                credentials: 'include',
                                headers: {
                                    'Accept': 'application/json'
                                }
                            });

                            if (!response.ok) {
                                console.warn('Could not load user profile, using defaults');
                                return;
                            }

                            const user = await response.json();
                            const preferences = user.preferences || {};

                            // Set dropdowns to saved preferences
                            if (preferences.base_language) {
                                document.getElementById('base_language').value = preferences.base_language;
                            }
                            if (preferences.target_language) {
                                document.getElementById('target_language').value = preferences.target_language;
                            }
                        } catch (error) {
                            console.error('Failed to load language settings:', error);
                        }
                    }

                    async function saveLanguageSettings() {
                        const baseLanguage = document.getElementById('base_language').value;
                        const targetLanguage = document.getElementById('target_language').value;
                        const feedback = document.getElementById('settings_feedback');
                        const saveButton = event.target;

                        // Disable button and show loading
                        saveButton.disabled = true;
                        saveButton.textContent = 'Saving...';
                        feedback.style.display = 'none';

                        try {
                            // Get current user to merge preferences
                            const userResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
                                method: 'GET',
                                credentials: 'include',
                                headers: {
                                    'Accept': 'application/json'
                                }
                            });

                            if (!userResponse.ok) {
                                throw new Error('Could not fetch current user profile');
                            }

                            const user = await userResponse.json();
                            const currentPreferences = user.preferences || {};

                            // Merge language settings with existing preferences
                            const updatedPreferences = {
                                ...currentPreferences,
                                base_language: baseLanguage,
                                target_language: targetLanguage
                            };

                            // Save to backend via profile update endpoint
                            const formData = new FormData();
                            formData.append('preferences', JSON.stringify(updatedPreferences));

                            const response = await fetch('http://localhost:8000/api/v1/auth/profile', {
                                method: 'PUT',
                                credentials: 'include',
                                body: formData
                            });

                            if (!response.ok) {
                                const error = await response.json();
                                throw new Error(error.detail || 'Failed to save settings');
                            }

                            // Show success message
                            feedback.textContent = '✓ Language settings saved successfully!';
                            feedback.style.background = 'var(--success)';
                            feedback.style.color = 'white';
                            feedback.style.display = 'block';

                            // Also update localStorage as fallback for non-authenticated scenarios
                            localStorage.setItem('base_language', baseLanguage);
                            localStorage.setItem('target_language', targetLanguage);

                        } catch (error) {
                            console.error('Failed to save settings:', error);

                            // Show error message
                            feedback.textContent = '✗ Failed to save settings: ' + error.message;
                            feedback.style.background = 'var(--error, #dc2626)';
                            feedback.style.color = 'white';
                            feedback.style.display = 'block';
                        } finally {
                            // Re-enable button
                            saveButton.disabled = false;
                            saveButton.textContent = 'Save Language Settings';

                            // Hide feedback after 5 seconds
                            setTimeout(() => {
                                feedback.style.display = 'none';
                            }, 5000);
                        }
                    }

                    // Load settings when page loads
                    window.addEventListener('DOMContentLoaded', loadLanguageSettings);
                """),
                style="max-width: 1200px; margin: 0 auto; padding: 2rem;",
            ),
            title="Settings - AI Language Tutor",
        )
