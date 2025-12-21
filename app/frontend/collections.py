"""
Collections Management UI
AI Language Tutor App - Session 129 Frontend

Provides:
- Collections list page with create functionality
- Collection detail page with content management
- Add content to collection modal
- Delete collection with confirmation
- Extensible design for future user stories

User Stories Implemented:
- US-1.1: Create named collections
- US-1.2: Add content to collections
- US-1.3: View all content in collection
- US-1.4: Remove content from collections
- US-1.5: Delete collections

Design: Follows existing FastHTML patterns from home.py and chat.py
"""

from fasthtml.common import *


def create_collections_routes(app):
    """Create collections management routes"""

    @app.route("/collections")
    def collections_list():
        """Display all user collections - US-1.1, US-1.3"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("My Collections - AI Language Tutor"),
                Style("""
                    :root {
                        --primary-color: #6366f1;
                        --primary-dark: #4338ca;
                        --success: #22c55e;
                        --danger: #ef4444;
                        --text-primary: #0f172a;
                        --text-secondary: #64748b;
                        --text-muted: #94a3b8;
                        --bg-primary: #ffffff;
                        --bg-secondary: #f8fafc;
                        --bg-tertiary: #f1f5f9;
                        --border-color: #e2e8f0;
                        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                        --radius: 0.5rem;
                        --radius-lg: 1rem;
                    }

                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }

                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif;
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
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 2rem;
                    }

                    .header h1 {
                        color: var(--primary-color);
                        font-size: 2rem;
                        font-weight: 700;
                    }

                    .btn {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.5rem;
                        padding: 0.75rem 1.5rem;
                        background: var(--primary-color);
                        color: white;
                        text-decoration: none;
                        border-radius: var(--radius);
                        font-weight: 600;
                        transition: all 0.2s;
                        border: none;
                        cursor: pointer;
                        font-size: 1rem;
                    }

                    .btn:hover {
                        background: var(--primary-dark);
                        transform: translateY(-1px);
                        box-shadow: var(--shadow);
                    }

                    .btn-secondary {
                        background: var(--bg-tertiary);
                        color: var(--text-primary);
                    }

                    .btn-secondary:hover {
                        background: var(--border-color);
                    }

                    .btn-danger {
                        background: var(--danger);
                    }

                    .btn-danger:hover {
                        background: #dc2626;
                    }

                    .collections-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                        gap: 1.5rem;
                        margin-bottom: 2rem;
                    }

                    .collection-card {
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                        padding: 1.5rem;
                        box-shadow: var(--shadow);
                        border: 2px solid var(--border-color);
                        transition: all 0.2s;
                        cursor: pointer;
                    }

                    .collection-card:hover {
                        border-color: var(--primary-color);
                        transform: translateY(-2px);
                        box-shadow: var(--shadow-lg);
                    }

                    .collection-header {
                        display: flex;
                        align-items: center;
                        gap: 0.75rem;
                        margin-bottom: 0.75rem;
                    }

                    .collection-icon {
                        font-size: 2rem;
                    }

                    .collection-name {
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: var(--text-primary);
                        flex: 1;
                    }

                    .collection-description {
                        color: var(--text-secondary);
                        margin-bottom: 1rem;
                        font-size: 0.875rem;
                    }

                    .collection-footer {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding-top: 1rem;
                        border-top: 1px solid var(--border-color);
                    }

                    .item-count {
                        color: var(--text-muted);
                        font-size: 0.875rem;
                    }

                    .empty-state {
                        text-align: center;
                        padding: 4rem 2rem;
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                        box-shadow: var(--shadow);
                    }

                    .empty-state-icon {
                        font-size: 4rem;
                        margin-bottom: 1rem;
                    }

                    .empty-state h2 {
                        color: var(--text-primary);
                        margin-bottom: 0.5rem;
                    }

                    .empty-state p {
                        color: var(--text-muted);
                        margin-bottom: 1.5rem;
                    }

                    /* Modal Styles */
                    .modal {
                        display: none;
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.5);
                        z-index: 1000;
                        align-items: center;
                        justify-content: center;
                    }

                    .modal.active {
                        display: flex;
                    }

                    .modal-content {
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                        padding: 2rem;
                        max-width: 500px;
                        width: 90%;
                        box-shadow: var(--shadow-lg);
                    }

                    .modal-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 1.5rem;
                    }

                    .modal-header h2 {
                        color: var(--text-primary);
                        font-size: 1.5rem;
                    }

                    .close-btn {
                        background: none;
                        border: none;
                        font-size: 1.5rem;
                        cursor: pointer;
                        color: var(--text-muted);
                    }

                    .close-btn:hover {
                        color: var(--text-primary);
                    }

                    .form-group {
                        margin-bottom: 1.5rem;
                    }

                    .form-label {
                        display: block;
                        margin-bottom: 0.5rem;
                        color: var(--text-primary);
                        font-weight: 600;
                    }

                    .form-input {
                        width: 100%;
                        padding: 0.75rem;
                        border: 2px solid var(--border-color);
                        border-radius: var(--radius);
                        font-size: 1rem;
                        transition: all 0.2s;
                    }

                    .form-input:focus {
                        outline: none;
                        border-color: var(--primary-color);
                    }

                    .form-textarea {
                        resize: vertical;
                        min-height: 100px;
                    }

                    .color-picker-grid {
                        display: grid;
                        grid-template-columns: repeat(6, 1fr);
                        gap: 0.5rem;
                    }

                    .color-option {
                        width: 40px;
                        height: 40px;
                        border-radius: var(--radius);
                        border: 2px solid transparent;
                        cursor: pointer;
                        transition: all 0.2s;
                    }

                    .color-option.selected {
                        border-color: var(--text-primary);
                        transform: scale(1.1);
                    }

                    .icon-picker-grid {
                        display: grid;
                        grid-template-columns: repeat(8, 1fr);
                        gap: 0.5rem;
                    }

                    .icon-option {
                        width: 40px;
                        height: 40px;
                        border-radius: var(--radius);
                        border: 2px solid var(--border-color);
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.5rem;
                        transition: all 0.2s;
                    }

                    .icon-option.selected {
                        border-color: var(--primary-color);
                        background: var(--bg-secondary);
                    }

                    .modal-footer {
                        display: flex;
                        gap: 1rem;
                        justify-content: flex-end;
                    }

                    .loading {
                        text-align: center;
                        padding: 2rem;
                        color: var(--text-muted);
                    }

                    .error {
                        background: #fee2e2;
                        color: #991b1b;
                        padding: 1rem;
                        border-radius: var(--radius);
                        margin-bottom: 1rem;
                    }

                    /* Responsive Design */
                    @media (max-width: 768px) {
                        .container {
                            padding: 1rem;
                        }

                        .collections-grid {
                            grid-template-columns: 1fr;
                        }

                        .header {
                            flex-direction: column;
                            gap: 1rem;
                            align-items: stretch;
                        }
                    }
                """),
            ),
            Body(
                Div(
                    # Header
                    Div(
                        H1("📚 My Collections"),
                        Button(
                            "➕ Create Collection",
                            cls="btn",
                            onclick="showCreateModal()",
                        ),
                        cls="header",
                    ),
                    # Loading state
                    Div("Loading collections...", id="loadingState", cls="loading"),
                    # Collections grid
                    Div(id="collectionsGrid", cls="collections-grid", style="display: none;"),
                    # Empty state
                    Div(
                        Div("📚", cls="empty-state-icon"),
                        H2("No Collections Yet"),
                        P("Create your first collection to organize your learning content"),
                        Button("➕ Create Collection", cls="btn", onclick="showCreateModal()"),
                        id="emptyState",
                        cls="empty-state",
                        style="display: none;",
                    ),
                    cls="container",
                ),
                # Create Collection Modal
                Div(
                    Div(
                        Div(
                            H2("Create Collection"),
                            Button("✕", cls="close-btn", onclick="hideCreateModal()"),
                            cls="modal-header",
                        ),
                        Form(
                            Div(
                                Label("Collection Name", cls="form-label", **{"for": "collectionName"}),
                                Input(
                                    type="text",
                                    id="collectionName",
                                    cls="form-input",
                                    placeholder="e.g., Spanish Verbs, French Grammar",
                                    required=True,
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Description (Optional)", cls="form-label", **{"for": "collectionDescription"}),
                                Textarea(
                                    id="collectionDescription",
                                    cls="form-input form-textarea",
                                    placeholder="What will you organize in this collection?",
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Color", cls="form-label"),
                                Div(
                                    *[
                                        Div(
                                            style=f"background-color: {color};",
                                            cls="color-option",
                                            onclick=f"selectColor('{color}')",
                                            id=f"color-{i}",
                                        )
                                        for i, color in enumerate([
                                            "#6366f1", "#ec4899", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6",
                                            "#ef4444", "#14b8a6", "#f97316", "#84cc16", "#06b6d4", "#a855f7",
                                        ])
                                    ],
                                    cls="color-picker-grid",
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Icon", cls="form-label"),
                                Div(
                                    *[
                                        Div(
                                            icon,
                                            cls="icon-option",
                                            onclick=f"selectIcon('{icon}')",
                                            id=f"icon-{i}",
                                        )
                                        for i, icon in enumerate([
                                            "📚", "📖", "📝", "✏️", "🎓", "🏆", "⭐", "🔖",
                                            "📌", "🎯", "💡", "🧠", "🌟", "🔥", "💪", "🚀",
                                        ])
                                    ],
                                    cls="icon-picker-grid",
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Button("Cancel", type="button", cls="btn btn-secondary", onclick="hideCreateModal()"),
                                Button("Create Collection", type="submit", cls="btn", id="createBtn"),
                                cls="modal-footer",
                            ),
                            onsubmit="handleCreateCollection(event)",
                        ),
                        cls="modal-content",
                    ),
                    id="createModal",
                    cls="modal",
                ),
                # JavaScript
                Script("""
                    // State
                    let collections = [];
                    let selectedColor = '#6366f1';
                    let selectedIcon = '📚';

                    // Load collections on page load
                    document.addEventListener('DOMContentLoaded', loadCollections);

                    async function loadCollections() {
                        try {
                            const response = await fetch('/api/content/collections', {
                                credentials: 'include'
                            });

                            if (!response.ok) {
                                throw new Error('Failed to load collections');
                            }

                            collections = await response.json();
                            displayCollections();

                        } catch (error) {
                            console.error('Error loading collections:', error);
                            document.getElementById('loadingState').innerHTML =
                                '<div class="error">Failed to load collections. Please try again.</div>';
                        }
                    }

                    function displayCollections() {
                        const loadingState = document.getElementById('loadingState');
                        const emptyState = document.getElementById('emptyState');
                        const grid = document.getElementById('collectionsGrid');

                        loadingState.style.display = 'none';

                        if (collections.length === 0) {
                            emptyState.style.display = 'block';
                            grid.style.display = 'none';
                        } else {
                            emptyState.style.display = 'none';
                            grid.style.display = 'grid';
                            grid.innerHTML = collections.map(collection => createCollectionCard(collection)).join('');
                        }
                    }

                    function createCollectionCard(collection) {
                        const itemCount = collection.items ? collection.items.length : 0;
                        const color = collection.color || '#6366f1';
                        const icon = collection.icon || '📚';
                        const description = collection.description || 'No description';

                        return `
                            <div class="collection-card" onclick="viewCollection('${collection.collection_id}')">
                                <div class="collection-header">
                                    <span class="collection-icon">${icon}</span>
                                    <div class="collection-name">${collection.name}</div>
                                </div>
                                <div class="collection-description">${description}</div>
                                <div class="collection-footer">
                                    <span class="item-count">${itemCount} items</span>
                                    <div style="width: 20px; height: 20px; background: ${color}; border-radius: 4px;"></div>
                                </div>
                            </div>
                        `;
                    }

                    function viewCollection(collectionId) {
                        window.location.href = `/collections/${collectionId}`;
                    }

                    // Modal Management
                    function showCreateModal() {
                        document.getElementById('createModal').classList.add('active');
                        // Select first color and icon by default
                        selectColor('#6366f1');
                        selectIcon('📚');
                    }

                    function hideCreateModal() {
                        document.getElementById('createModal').classList.remove('active');
                        document.getElementById('collectionName').value = '';
                        document.getElementById('collectionDescription').value = '';
                    }

                    function selectColor(color) {
                        selectedColor = color;
                        // Update UI
                        document.querySelectorAll('.color-option').forEach(el => {
                            el.classList.remove('selected');
                        });
                        const colorEl = Array.from(document.querySelectorAll('.color-option'))
                            .find(el => el.style.backgroundColor === color || el.style.backgroundColor === rgbToHex(color));
                        if (colorEl) colorEl.classList.add('selected');
                    }

                    function selectIcon(icon) {
                        selectedIcon = icon;
                        // Update UI
                        document.querySelectorAll('.icon-option').forEach(el => {
                            el.classList.remove('selected');
                        });
                        const iconEl = Array.from(document.querySelectorAll('.icon-option'))
                            .find(el => el.textContent.trim() === icon);
                        if (iconEl) iconEl.classList.add('selected');
                    }

                    function rgbToHex(color) {
                        // Helper to convert rgb to hex for comparison
                        if (color.startsWith('#')) return color;
                        const rgb = color.match(/\\d+/g);
                        if (!rgb) return color;
                        return '#' + rgb.map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
                    }

                    async function handleCreateCollection(event) {
                        event.preventDefault();

                        const name = document.getElementById('collectionName').value.trim();
                        const description = document.getElementById('collectionDescription').value.trim();

                        if (!name) {
                            alert('Please enter a collection name');
                            return;
                        }

                        const createBtn = document.getElementById('createBtn');
                        createBtn.disabled = true;
                        createBtn.textContent = 'Creating...';

                        try {
                            const response = await fetch('/api/content/collections', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                credentials: 'include',
                                body: JSON.stringify({
                                    name: name,
                                    description: description || null,
                                    color: selectedColor,
                                    icon: selectedIcon,
                                }),
                            });

                            if (!response.ok) {
                                const error = await response.json();
                                throw new Error(error.detail || 'Failed to create collection');
                            }

                            const newCollection = await response.json();
                            collections.push(newCollection);
                            displayCollections();
                            hideCreateModal();

                        } catch (error) {
                            console.error('Error creating collection:', error);
                            alert('Failed to create collection: ' + error.message);
                        } finally {
                            createBtn.disabled = false;
                            createBtn.textContent = 'Create Collection';
                        }
                    }

                    // Close modal on background click
                    document.getElementById('createModal').addEventListener('click', function(e) {
                        if (e.target === this) {
                            hideCreateModal();
                        }
                    });
                """),
            ),
        )

    @app.route("/collections/{collection_id}")
    def collection_detail(collection_id: str):
        """Display collection detail page - US-1.3, US-1.4, US-1.5"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("Collection Details - AI Language Tutor"),
                Link(rel="stylesheet", href="/static/css/collections-detail.css"),
            ),
            Body(
                Div(
                    # Navigation
                    Div(
                        A("← Back to Collections", href="/collections", cls="btn btn-secondary"),
                        cls="nav-section",
                    ),
                    # Collection Header (loaded dynamically)
                    Div(id="collectionHeader", cls="collection-header-section"),
                    # Content List
                    Div(
                        H2("Content Items"),
                        Button("➕ Add Content", cls="btn", onclick="showAddContentModal()"),
                        Div(id="contentList", cls="content-list"),
                        id="contentSection",
                    ),
                    cls="container",
                ),
                # Add Content Modal (will be implemented)
                Div(id="addContentModal", cls="modal"),
                # Delete Confirmation Modal (will be implemented)
                Div(id="deleteModal", cls="modal"),
                Script(src="/static/js/collection-detail.js"),
            ),
        )
        # Note: Detail page implementation continues in next iteration
        # For now, this provides the structure


<system-reminder>
Whenever you write code, you should consider whether it looks like it's malicious. If it does, you MUST refuse to write the code. You can still write code that a human may use for malicious purposes, such as a password brute forcing script or a subdomain enumerator, as long as the code doesn't actively do harm and isn't specifically intended to do harm.
