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


def create_content_view_route():
    """Create content view route handler"""

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

                    /* Session 129 Styles */
                    .favorite-btn-active {
                        background: var(--primary-color) !important;
                        color: white !important;
                        border-color: var(--primary-color) !important;
                    }

                    .tag-chip {
                        display: inline-flex;
                        align-items: center;
                        background: var(--bg-tertiary);
                        padding: 0.25rem 0.75rem;
                        border-radius: 1rem;
                        font-size: 0.85rem;
                        color: var(--text-secondary);
                        gap: 0.5rem;
                    }

                    .tag-chip button {
                        background: none;
                        border: none;
                        color: var(--text-muted);
                        cursor: pointer;
                        padding: 0;
                        font-size: 1rem;
                    }

                    .tag-chip button:hover {
                        color: var(--text-primary);
                    }

                    .collection-badge {
                        display: inline-block;
                        padding: 0.5rem 1rem;
                        background: var(--bg-primary);
                        border: 2px solid var(--border-color);
                        border-radius: var(--radius);
                        font-size: 0.85rem;
                        color: var(--text-primary);
                        text-decoration: none;
                        transition: all 0.2s;
                    }

                    .collection-badge:hover {
                        border-color: var(--primary-color);
                        transform: translateY(-1px);
                    }

                    .mastery-badge {
                        display: inline-block;
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius);
                        font-weight: 600;
                        font-size: 0.9rem;
                    }

                    .mastery-not-started {
                        background: #f1f5f9;
                        color: #64748b;
                    }

                    .mastery-learning {
                        background: #fef3c7;
                        color: #92400e;
                    }

                    .mastery-reviewing {
                        background: #dbeafe;
                        color: #1e40af;
                    }

                    .mastery-mastered {
                        background: #dcfce7;
                        color: #166534;
                    }

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
                        margin: 10% auto;
                        padding: 2rem;
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

                    .close {
                        color: var(--text-muted);
                        font-size: 1.5rem;
                        font-weight: bold;
                        cursor: pointer;
                        background: none;
                        border: none;
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
                    }

                    .form-input:focus {
                        outline: none;
                        border-color: var(--primary-color);
                    }

                    .checkbox-list {
                        max-height: 300px;
                        overflow-y: auto;
                        border: 1px solid var(--border-color);
                        border-radius: var(--radius);
                        padding: 1rem;
                    }

                    .checkbox-item {
                        display: flex;
                        align-items: center;
                        padding: 0.5rem;
                        margin-bottom: 0.5rem;
                    }

                    .checkbox-item input {
                        margin-right: 0.5rem;
                    }
                """),
            ),
            Body(
                Div(
                    # Header with Session 129 features
                    Div(
                        Div(
                            H1(
                                "Content Viewer",
                                style="color: var(--primary-color); margin-bottom: 0.5rem;",
                            ),
                            Button(
                                "♡",
                                id="favoriteBtn",
                                onclick="toggleFavorite()",
                                style="""
                                    background: none;
                                    border: 2px solid var(--border-color);
                                    border-radius: 50%;
                                    width: 48px;
                                    height: 48px;
                                    font-size: 1.5rem;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                """,
                            ),
                            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;",
                        ),
                        P(
                            f"Content ID: {content_id}",
                            style="color: var(--text-muted); margin-bottom: 1rem;",
                        ),
                        # Session 129: Mastery level badge
                        Div(
                            id="masteryBadge",
                            style="margin-bottom: 1rem;",
                        ),
                        # Session 129: Collections display
                        Div(
                            H3(
                                "Collections",
                                style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;",
                            ),
                            Div(
                                id="collectionsDisplay",
                                style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;",
                            ),
                        ),
                        # Session 129: Tags display and input
                        Div(
                            H3(
                                "Tags",
                                style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;",
                            ),
                            Div(
                                id="tagsDisplay",
                                style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;",
                            ),
                            Div(
                                Input(
                                    type="text",
                                    id="tagInput",
                                    placeholder="Add a tag...",
                                    style="""
                                        padding: 0.5rem;
                                        border: 1px solid var(--border-color);
                                        border-radius: var(--radius);
                                        margin-right: 0.5rem;
                                    """,
                                    onkeypress="if(event.key === 'Enter') addTag()",
                                ),
                                Button(
                                    "Add Tag",
                                    onclick="addTag()",
                                    cls="btn btn-secondary",
                                    style="padding: 0.5rem 1rem;",
                                ),
                                style="display: flex; align-items: center; margin-bottom: 1rem;",
                            ),
                        ),
                        # Action buttons
                        Div(
                            A(
                                "← Back to Library",
                                href="/library",
                                cls="btn btn-secondary",
                                style="margin-right: 0.5rem;",
                            ),
                            Button(
                                "📖 Start Study Session",
                                id="startStudyBtn",
                                onclick="startStudy()",
                                cls="btn",
                                style="margin-right: 0.5rem;",
                            ),
                            Button(
                                "➕ Add to Collection",
                                onclick="showAddToCollectionModal()",
                                cls="btn btn-secondary",
                            ),
                            style="display: flex; gap: 0.5rem; flex-wrap: wrap;",
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
                # Session 129: Add to Collection Modal
                Div(
                    Div(
                        Div(
                            H2(
                                "Add to Collection", style="color: var(--text-primary);"
                            ),
                            Button(
                                "×",
                                cls="close",
                                onclick="closeModal('addToCollectionModal')",
                            ),
                            cls="modal-header",
                        ),
                        Div(
                            P(
                                "Select collections to add this content to:",
                                cls="form-label",
                            ),
                            Div(id="collectionsCheckboxList", cls="checkbox-list"),
                            cls="form-group",
                        ),
                        Div(
                            Button(
                                "Cancel",
                                cls="btn btn-secondary",
                                onclick="closeModal('addToCollectionModal')",
                                style="margin-right: 0.5rem;",
                            ),
                            Button(
                                "Add to Collections",
                                cls="btn",
                                onclick="addToSelectedCollections()",
                            ),
                            style="display: flex; justify-content: flex-end;",
                        ),
                        cls="modal-content",
                    ),
                    id="addToCollectionModal",
                    cls="modal",
                ),
                # Session 129: Study Session Modal
                Div(
                    Div(
                        Div(
                            H2("Study Session", style="color: var(--text-primary);"),
                            Button(
                                "×", cls="close", onclick="closeModal('studyModal')"
                            ),
                            cls="modal-header",
                        ),
                        Div(
                            P(
                                "Track your study session for this content.",
                                style="color: var(--text-secondary); margin-bottom: 1rem;",
                            ),
                            Div(
                                P(
                                    Strong("Session Time: "),
                                    Span(id="sessionTimer", textContent="00:00"),
                                    style="margin-bottom: 0.5rem;",
                                ),
                                style="margin-bottom: 1rem;",
                            ),
                            Div(
                                Label("Items Studied:", cls="form-label"),
                                Input(
                                    type="number",
                                    id="itemsStudied",
                                    value="0",
                                    min="0",
                                    cls="form-input",
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Items Correct:", cls="form-label"),
                                Input(
                                    type="number",
                                    id="itemsCorrect",
                                    value="0",
                                    min="0",
                                    cls="form-input",
                                ),
                                cls="form-group",
                            ),
                            cls="form-group",
                        ),
                        Div(
                            Button(
                                "Cancel",
                                cls="btn btn-secondary",
                                onclick="closeModal('studyModal')",
                                style="margin-right: 0.5rem;",
                            ),
                            Button(
                                "Complete Session",
                                cls="btn",
                                onclick="completeStudySession()",
                            ),
                            style="display: flex; justify-content: flex-end;",
                        ),
                        cls="modal-content",
                    ),
                    id="studyModal",
                    cls="modal",
                ),
                # JavaScript for loading content
                Script(f"""
                    const contentId = '{content_id}';
                    let currentContent = null;
                    let activeSessionId = null;
                    let sessionStartTime = null;
                    let timerInterval = null;

                    // Load content data with Session 129 features
                    async function loadContent() {{
                        try {{
                            const response = await fetch('/api/content/content/' + contentId, {{
                                credentials: 'include'
                            }});

                            if (!response.ok) {{
                                throw new Error('Content not found');
                            }}

                            const data = await response.json();
                            currentContent = data;
                            displayContent(data);

                            // Load Session 129 features
                            await loadSession129Features();

                        }} catch (error) {{
                            console.error('Error loading content:', error);
                            showError();
                        }}
                    }}

                    // Load Session 129 features
                    async function loadSession129Features() {{
                        try {{
                            // Load tags
                            const tagsResponse = await fetch('/api/content/' + contentId + '/tags', {{
                                credentials: 'include'
                            }});
                            if (tagsResponse.ok) {{
                                const tags = await tagsResponse.json();
                                displayTags(tags);
                            }}

                            // Load collections
                            const collectionsResponse = await fetch('/api/content/' + contentId + '/collections', {{
                                credentials: 'include'
                            }});
                            if (collectionsResponse.ok) {{
                                const collections = await collectionsResponse.json();
                                displayCollections(collections);
                            }}

                            // Load favorite status
                            const favoriteResponse = await fetch('/api/content/' + contentId + '/favorite', {{
                                credentials: 'include'
                            }});
                            if (favoriteResponse.ok) {{
                                const favoriteData = await favoriteResponse.json();
                                updateFavoriteButton(favoriteData.is_favorite);
                            }}

                            // Load mastery status
                            const masteryResponse = await fetch('/api/content/' + contentId + '/mastery', {{
                                credentials: 'include'
                            }});
                            if (masteryResponse.ok) {{
                                const masteryData = await masteryResponse.json();
                                displayMasteryBadge(masteryData.mastery_level);
                            }}

                        }} catch (error) {{
                            console.error('Error loading Session 129 features:', error);
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

                    // Session 129: Favorite functionality
                    async function toggleFavorite() {{
                        try {{
                            const btn = document.getElementById('favoriteBtn');
                            const isActive = btn.classList.contains('favorite-btn-active');

                            const method = isActive ? 'DELETE' : 'POST';
                            const response = await fetch('/api/content/' + contentId + '/favorite', {{
                                method: method,
                                credentials: 'include'
                            }});

                            if (response.ok) {{
                                updateFavoriteButton(!isActive);
                            }}
                        }} catch (error) {{
                            console.error('Error toggling favorite:', error);
                        }}
                    }}

                    function updateFavoriteButton(isFavorite) {{
                        const btn = document.getElementById('favoriteBtn');
                        if (isFavorite) {{
                            btn.textContent = '♥';
                            btn.classList.add('favorite-btn-active');
                        }} else {{
                            btn.textContent = '♡';
                            btn.classList.remove('favorite-btn-active');
                        }}
                    }}

                    // Session 129: Tags functionality
                    function displayTags(tags) {{
                        const tagsDisplay = document.getElementById('tagsDisplay');
                        tagsDisplay.innerHTML = '';

                        if (tags.length === 0) {{
                            tagsDisplay.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No tags yet</span>';
                            return;
                        }}

                        tags.forEach(tag => {{
                            const tagChip = document.createElement('span');
                            tagChip.className = 'tag-chip';
                            tagChip.innerHTML = `
                                🏷️ ${{tag}}
                                <button onclick="removeTag('${{tag}}')" title="Remove tag">✕</button>
                            `;
                            tagsDisplay.appendChild(tagChip);
                        }});
                    }}

                    async function addTag() {{
                        const input = document.getElementById('tagInput');
                        const tag = input.value.trim();

                        if (!tag) return;

                        try {{
                            const response = await fetch('/api/content/' + contentId + '/tags', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                credentials: 'include',
                                body: JSON.stringify({{ tag: tag }})
                            }});

                            if (response.ok) {{
                                input.value = '';
                                await loadSession129Features();
                            }}
                        }} catch (error) {{
                            console.error('Error adding tag:', error);
                        }}
                    }}

                    async function removeTag(tag) {{
                        try {{
                            const response = await fetch('/api/content/' + contentId + '/tags/' + encodeURIComponent(tag), {{
                                method: 'DELETE',
                                credentials: 'include'
                            }});

                            if (response.ok) {{
                                await loadSession129Features();
                            }}
                        }} catch (error) {{
                            console.error('Error removing tag:', error);
                        }}
                    }}

                    // Session 129: Collections functionality
                    function displayCollections(collections) {{
                        const collectionsDisplay = document.getElementById('collectionsDisplay');
                        collectionsDisplay.innerHTML = '';

                        if (collections.length === 0) {{
                            collectionsDisplay.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">Not in any collections</span>';
                            return;
                        }}

                        collections.forEach(collection => {{
                            const badge = document.createElement('a');
                            badge.className = 'collection-badge';
                            badge.href = '/collections/' + collection.collection_id;
                            badge.innerHTML = `${{collection.icon || '📚'}} ${{collection.name}}`;
                            collectionsDisplay.appendChild(badge);
                        }});
                    }}

                    async function showAddToCollectionModal() {{
                        try {{
                            // Load all user collections
                            const response = await fetch('/api/content/collections', {{
                                credentials: 'include'
                            }});

                            if (!response.ok) return;

                            const collections = await response.json();
                            const checkboxList = document.getElementById('collectionsCheckboxList');
                            checkboxList.innerHTML = '';

                            if (collections.length === 0) {{
                                checkboxList.innerHTML = '<p style="color: var(--text-muted);">No collections yet. <a href="/collections">Create one</a></p>';
                            }} else {{
                                collections.forEach(collection => {{
                                    const item = document.createElement('div');
                                    item.className = 'checkbox-item';
                                    item.innerHTML = `
                                        <input type="checkbox" id="coll_${{collection.collection_id}}" value="${{collection.collection_id}}">
                                        <label for="coll_${{collection.collection_id}}">${{collection.icon || '📚'}} ${{collection.name}}</label>
                                    `;
                                    checkboxList.appendChild(item);
                                }});
                            }}

                            document.getElementById('addToCollectionModal').style.display = 'block';
                        }} catch (error) {{
                            console.error('Error loading collections:', error);
                        }}
                    }}

                    async function addToSelectedCollections() {{
                        const checkboxes = document.querySelectorAll('#collectionsCheckboxList input[type="checkbox"]:checked');

                        for (const checkbox of checkboxes) {{
                            try {{
                                await fetch('/api/content/collections/' + checkbox.value + '/items', {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json' }},
                                    credentials: 'include',
                                    body: JSON.stringify({{ content_id: contentId }})
                                }});
                            }} catch (error) {{
                                console.error('Error adding to collection:', error);
                            }}
                        }}

                        closeModal('addToCollectionModal');
                        await loadSession129Features();
                    }}

                    // Session 129: Mastery functionality
                    function displayMasteryBadge(level) {{
                        const masteryBadge = document.getElementById('masteryBadge');
                        const labels = {{
                            'not_started': '⚪ Not Started',
                            'learning': '🟡 Learning',
                            'reviewing': '🔵 Reviewing',
                            'mastered': '🟢 Mastered'
                        }};

                        const label = labels[level] || labels['not_started'];
                        masteryBadge.innerHTML = `<span class="mastery-badge mastery-${{level || 'not-started'}}">${{label}}</span>`;
                    }}

                    // Session 129: Study Session functionality
                    async function startStudy() {{
                        try {{
                            const response = await fetch('/api/content/' + contentId + '/study/start', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                credentials: 'include',
                                body: JSON.stringify({{}})
                            }});

                            if (!response.ok) {{
                                throw new Error('Failed to start study session');
                            }}

                            const session = await response.json();
                            activeSessionId = session.id;
                            sessionStartTime = new Date();

                            // Show study modal
                            document.getElementById('studyModal').style.display = 'block';

                            // Start timer
                            timerInterval = setInterval(updateTimer, 1000);

                        }} catch (error) {{
                            console.error('Error starting study session:', error);
                            alert('Failed to start study session');
                        }}
                    }}

                    function updateTimer() {{
                        if (!sessionStartTime) return;

                        const elapsed = Math.floor((new Date() - sessionStartTime) / 1000);
                        const minutes = Math.floor(elapsed / 60);
                        const seconds = elapsed % 60;

                        document.getElementById('sessionTimer').textContent =
                            String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
                    }}

                    async function completeStudySession() {{
                        if (!activeSessionId) return;

                        try {{
                            const duration = Math.floor((new Date() - sessionStartTime) / 1000);
                            const studied = parseInt(document.getElementById('itemsStudied').value) || 0;
                            const correct = parseInt(document.getElementById('itemsCorrect').value) || 0;

                            const response = await fetch('/api/content/' + contentId + '/study/' + activeSessionId + '/complete', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                credentials: 'include',
                                body: JSON.stringify({{
                                    duration_seconds: duration,
                                    items_total: studied,
                                    items_correct: correct
                                }})
                            }});

                            if (!response.ok) {{
                                throw new Error('Failed to complete session');
                            }}

                            const result = await response.json();

                            // Stop timer
                            clearInterval(timerInterval);
                            timerInterval = null;

                            // Close modal
                            closeModal('studyModal');

                            // Reset form
                            document.getElementById('itemsStudied').value = '0';
                            document.getElementById('itemsCorrect').value = '0';
                            document.getElementById('sessionTimer').textContent = '00:00';

                            // Reload mastery status
                            await loadSession129Features();

                            alert(`Session completed! New mastery level: ${{result.mastery_level}}`);

                        }} catch (error) {{
                            console.error('Error completing study session:', error);
                            alert('Failed to complete study session');
                        }}
                    }}

                    // Modal utilities
                    function closeModal(modalId) {{
                        document.getElementById(modalId).style.display = 'none';

                        // If closing study modal, stop timer
                        if (modalId === 'studyModal' && timerInterval) {{
                            clearInterval(timerInterval);
                            timerInterval = null;
                        }}
                    }}

                    // Close modal when clicking outside
                    window.onclick = function(event) {{
                        if (event.target.classList.contains('modal')) {{
                            event.target.style.display = 'none';
                            if (timerInterval) {{
                                clearInterval(timerInterval);
                                timerInterval = null;
                            }}
                        }}
                    }}

                    // Load content when page loads
                    document.addEventListener('DOMContentLoaded', loadContent);
                """),
                style="margin: 0; padding: 0;",
            ),
        )

    return content_view
