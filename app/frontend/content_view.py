"""
Content View Page
AI Language Tutor App - Display processed content and learning materials

Provides:
- View processed content details
- Display generated learning materials
- Navigate between different material types
- Study mode interface
"""

from fasthtml.common import *


def create_content_view_route(app):
    """Create content view routes"""

    @app.route("/content/{content_id}")
    def content_view(content_id: str):
        """Display processed content and learning materials"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title(f"Content Viewer - {content_id}"),
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

                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 2rem;
                    }

                    .header {
                        margin-bottom: 2rem;
                        text-align: center;
                    }

                    .content-card {
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                        padding: 2rem;
                        margin-bottom: 2rem;
                        box-shadow: var(--shadow);
                    }

                    .material-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 1.5rem;
                        margin-top: 2rem;
                    }

                    .material-card {
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                        padding: 1.5rem;
                        box-shadow: var(--shadow);
                        border: 2px solid var(--border-light);
                        transition: all 0.2s;
                    }

                    .material-card:hover {
                        border-color: var(--primary-color);
                        transform: translateY(-2px);
                    }

                    .btn {
                        display: inline-block;
                        padding: 0.75rem 1.5rem;
                        background: var(--primary-color);
                        color: white;
                        text-decoration: none;
                        border-radius: var(--radius);
                        font-weight: 600;
                        transition: all 0.2s;
                        border: none;
                        cursor: pointer;
                    }

                    .btn:hover {
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
                """),
            ),
            Body(
                Div(
                    # Header
                    Div(
                        H1(
                            "Content Viewer",
                            style="color: var(--primary-color); margin-bottom: 0.5rem;",
                        ),
                        P(
                            f"Content ID: {content_id}",
                            style="color: var(--text-muted);",
                        ),
                        A(
                            "← Back to Home",
                            href="/",
                            cls="btn btn-secondary",
                            style="margin-top: 1rem;",
                        ),
                        cls="header",
                    ),
                    # Loading state (will be replaced by JavaScript)
                    Div(
                        Div(
                            H2(
                                "Loading Content...",
                                style="color: var(--text-primary);",
                            ),
                            P(
                                "Please wait while we fetch your processed content.",
                                style="color: var(--text-muted);",
                            ),
                            cls="content-card",
                        ),
                        id="loadingState",
                    ),
                    # Content display (hidden initially)
                    Div(
                        Div(
                            H2(
                                "Content Details",
                                id="contentTitle",
                                style="color: var(--text-primary); margin-bottom: 1rem;",
                            ),
                            Div(
                                P(Strong("Type: "), Span(id="contentType")),
                                P(Strong("Topics: "), Span(id="contentTopics")),
                                P(Strong("Difficulty: "), Span(id="contentDifficulty")),
                                P(Strong("Word Count: "), Span(id="contentWordCount")),
                                P(Strong("Created: "), Span(id="contentCreated")),
                                style="margin-bottom: 1rem; color: var(--text-secondary);",
                            ),
                            Div(
                                H3("Content Preview", style="margin-bottom: 0.5rem;"),
                                P(
                                    id="contentPreview",
                                    style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius); line-height: 1.8;",
                                ),
                                style="margin-bottom: 1rem;",
                            ),
                            cls="content-card",
                        ),
                        # Learning Materials
                        Div(
                            H2(
                                "Learning Materials",
                                style="color: var(--text-primary); margin-bottom: 1rem; text-align: center;",
                            ),
                            P(
                                "Generated learning materials to help you study this content.",
                                style="color: var(--text-muted); text-align: center; margin-bottom: 2rem;",
                            ),
                            Div(id="materialsGrid", cls="material-grid"),
                        ),
                        id="contentDisplay",
                        style="display: none;",
                    ),
                    # Error state (hidden initially)
                    Div(
                        Div(
                            H2(
                                "Content Not Found", style="color: var(--text-primary);"
                            ),
                            P(
                                "The requested content could not be found or is still being processed.",
                                style="color: var(--text-muted);",
                            ),
                            A("← Back to Home", href="/", cls="btn"),
                            cls="content-card",
                        ),
                        id="errorState",
                        style="display: none;",
                    ),
                    cls="container",
                ),
                # JavaScript for loading content
                Script(f"""
                    // Load content data
                    async function loadContent() {{
                        try {{
                            const response = await fetch('/api/content/content/{content_id}');

                            if (!response.ok) {{
                                throw new Error('Content not found');
                            }}

                            const data = await response.json();
                            displayContent(data);

                        }} catch (error) {{
                            console.error('Error loading content:', error);
                            showError();
                        }}
                    }}

                    function displayContent(data) {{
                        // Hide loading state
                        document.getElementById('loadingState').style.display = 'none';

                        // Show content
                        document.getElementById('contentDisplay').style.display = 'block';

                        // Fill content details
                        document.getElementById('contentTitle').textContent = data.metadata.title;
                        document.getElementById('contentType').textContent = data.metadata.content_type;
                        document.getElementById('contentTopics').textContent = data.metadata.topics.join(', ');
                        document.getElementById('contentDifficulty').textContent = data.metadata.difficulty_level;
                        document.getElementById('contentWordCount').textContent = data.metadata.word_count;
                        document.getElementById('contentCreated').textContent = new Date(data.metadata.created_at).toLocaleDateString();
                        document.getElementById('contentPreview').textContent = data.content_preview;

                        // Display learning materials
                        const materialsGrid = document.getElementById('materialsGrid');
                        materialsGrid.innerHTML = '';

                        data.learning_materials.forEach(material => {{
                            const materialCard = createMaterialCard(material);
                            materialsGrid.appendChild(materialCard);
                        }});
                    }}

                    function createMaterialCard(material) {{
                        const card = document.createElement('div');
                        card.className = 'material-card';

                        const typeIcons = {{
                            'summary': '📄',
                            'flashcards': '🎴',
                            'quiz': '❓',
                            'key_concepts': '🔑',
                            'notes': '📝'
                        }};

                        const icon = typeIcons[material.material_type] || '📚';

                        card.innerHTML = `
                            <h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">
                                ${{icon}} ${{material.material_type.replace('_', ' ').toUpperCase()}}
                            </h3>
                            <p style="color: var(--text-muted); margin-bottom: 1rem;">
                                Estimated time: ${{material.estimated_time}} minutes
                            </p>
                            <button onclick="viewMaterial('${{material.material_id}}')" class="btn">
                                View Material
                            </button>
                        `;

                        return card;
                    }}

                    function viewMaterial(materialId) {{
                        // For now, just show an alert
                        alert('Material viewer not yet implemented. Material ID: ' + materialId);
                        // TODO: Implement material viewer
                    }}

                    function showError() {{
                        document.getElementById('loadingState').style.display = 'none';
                        document.getElementById('errorState').style.display = 'block';
                    }}

                    // Load content when page loads
                    document.addEventListener('DOMContentLoaded', loadContent);
                """),
                style="margin: 0; padding: 0;",
            ),
        )
