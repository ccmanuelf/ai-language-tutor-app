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
                    Div(
                        id="collectionsGrid",
                        cls="collections-grid",
                        style="display: none;",
                    ),
                    # Empty state
                    Div(
                        Div("📚", cls="empty-state-icon"),
                        H2("No Collections Yet"),
                        P(
                            "Create your first collection to organize your learning content"
                        ),
                        Button(
                            "➕ Create Collection",
                            cls="btn",
                            onclick="showCreateModal()",
                        ),
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
                                Label(
                                    "Collection Name",
                                    cls="form-label",
                                    **{"for": "collectionName"},
                                ),
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
                                Label(
                                    "Description (Optional)",
                                    cls="form-label",
                                    **{"for": "collectionDescription"},
                                ),
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
                                        for i, color in enumerate(
                                            [
                                                "#6366f1",
                                                "#ec4899",
                                                "#f59e0b",
                                                "#22c55e",
                                                "#3b82f6",
                                                "#8b5cf6",
                                                "#ef4444",
                                                "#14b8a6",
                                                "#f97316",
                                                "#84cc16",
                                                "#06b6d4",
                                                "#a855f7",
                                            ]
                                        )
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
                                        for i, icon in enumerate(
                                            [
                                                "📚",
                                                "📖",
                                                "📝",
                                                "✏️",
                                                "🎓",
                                                "🏆",
                                                "⭐",
                                                "🔖",
                                                "📌",
                                                "🎯",
                                                "💡",
                                                "🧠",
                                                "🌟",
                                                "🔥",
                                                "💪",
                                                "🚀",
                                            ]
                                        )
                                    ],
                                    cls="icon-picker-grid",
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Button(
                                    "Cancel",
                                    type="button",
                                    cls="btn btn-secondary",
                                    onclick="hideCreateModal()",
                                ),
                                Button(
                                    "Create Collection",
                                    type="submit",
                                    cls="btn",
                                    id="createBtn",
                                ),
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
                Style("""
                    /* Reuse CSS from collections list */
                    :root {
                        --primary-color: #6366f1;
                        --primary-dark: #4338ca;
                        --danger: #ef4444;
                        --text-primary: #0f172a;
                        --text-secondary: #64748b;
                        --bg-primary: #ffffff;
                        --bg-secondary: #f8fafc;
                        --border-color: #e2e8f0;
                        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        --radius: 0.5rem;
                        --radius-lg: 1rem;
                    }
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
                           background: var(--bg-secondary); color: var(--text-primary); }
                    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
                    .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem;
                           background: var(--primary-color); color: white; text-decoration: none;
                           border-radius: var(--radius); font-weight: 600; border: none; cursor: pointer; }
                    .btn:hover { background: var(--primary-dark); }
                    .btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); }
                    .btn-danger { background: var(--danger); }
                    .header-section { background: var(--bg-primary); padding: 2rem; border-radius: var(--radius-lg);
                                     box-shadow: var(--shadow); margin-bottom: 2rem; }
                    .header-actions { display: flex; gap: 1rem; margin-top: 1.5rem; }
                    .content-item { background: var(--bg-primary); padding: 1rem; border-radius: var(--radius);
                                   box-shadow: var(--shadow); margin-bottom: 1rem; display: flex;
                                   justify-content: space-between; align-items: center; }
                    .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                            background: rgba(0, 0, 0, 0.5); z-index: 1000; align-items: center; justify-content: center; }
                    .modal.active { display: flex; }
                    .modal-content { background: var(--bg-primary); border-radius: var(--radius-lg);
                                    padding: 2rem; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; }
                    .checkbox-item { padding: 0.75rem; border-radius: var(--radius); cursor: pointer; }
                    .checkbox-item:hover { background: var(--bg-secondary); }
                    .loading { text-align: center; padding: 2rem; color: var(--text-muted); }
                """),
            ),
            Body(
                Div(
                    A(
                        "← Back to Collections",
                        href="/collections",
                        cls="btn btn-secondary",
                        style="margin-bottom: 2rem;",
                    ),
                    Div(id="loadingState", cls="loading")("Loading collection..."),
                    Div(id="collectionHeader", style="display: none;"),
                    Div(
                        H2("Content Items", style="margin-bottom: 1rem;"),
                        Button(
                            "➕ Add Content", cls="btn", onclick="showAddContentModal()"
                        ),
                        Div(id="contentList", style="margin-top: 1.5rem;"),
                        id="contentSection",
                        style="display: none;",
                    ),
                    cls="container",
                ),
                # Add Content Modal
                Div(
                    Div(
                        Div(
                            H2("Add Content to Collection"),
                            Button(
                                "✕",
                                onclick="hideAddContentModal()",
                                style="background: none; border: none; font-size: 1.5rem; cursor: pointer;",
                            ),
                            style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;",
                        ),
                        Div(
                            id="availableContent",
                            style="max-height: 400px; overflow-y: auto;",
                        ),
                        Div(
                            Button(
                                "Cancel",
                                cls="btn btn-secondary",
                                onclick="hideAddContentModal()",
                            ),
                            Button(
                                "Add Selected",
                                cls="btn",
                                onclick="addSelectedContent()",
                            ),
                            style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;",
                        ),
                        cls="modal-content",
                    ),
                    id="addContentModal",
                    cls="modal",
                ),
                # Delete Confirmation Modal
                Div(
                    Div(
                        H2("Delete Collection?", style="margin-bottom: 1rem;"),
                        P(
                            "This will permanently delete the collection. Content items will not be deleted.",
                            style="margin-bottom: 1.5rem;",
                        ),
                        Div(
                            Button(
                                "Cancel",
                                cls="btn btn-secondary",
                                onclick="hideDeleteModal()",
                            ),
                            Button(
                                "Delete Collection",
                                cls="btn btn-danger",
                                onclick="confirmDelete()",
                            ),
                            style="display: flex; gap: 1rem; justify-content: flex-end;",
                        ),
                        cls="modal-content",
                    ),
                    id="deleteModal",
                    cls="modal",
                ),
                Script(f"""
                    const collectionId = '{collection_id}';
                    let collection = null;
                    let allContent = [];

                    document.addEventListener('DOMContentLoaded', loadCollection);

                    async function loadCollection() {{
                        try {{
                            const response = await fetch(`/api/content/collections/${{collectionId}}`, {{
                                credentials: 'include'
                            }});

                            if (!response.ok) throw new Error('Collection not found');

                            collection = await response.json();
                            displayCollection();

                            document.getElementById('loadingState').style.display = 'none';
                            document.getElementById('collectionHeader').style.display = 'block';
                            document.getElementById('contentSection').style.display = 'block';

                        }} catch (error) {{
                            console.error('Error:', error);
                            document.getElementById('loadingState').innerHTML =
                                '<div style="color: var(--danger);">Failed to load collection</div>';
                        }}
                    }}

                    function displayCollection() {{
                        const header = document.getElementById('collectionHeader');
                        header.innerHTML = `
                            <div class="header-section">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                    <span style="font-size: 3rem;">${{collection.icon || '📚'}}</span>
                                    <div style="flex: 1;">
                                        <h1 style="color: var(--primary-color); margin-bottom: 0.5rem;">${{collection.name}}</h1>
                                        <p style="color: var(--text-secondary);">${{collection.description || 'No description'}}</p>
                                    </div>
                                </div>
                                <div class="header-actions">
                                    <button class="btn btn-danger" onclick="showDeleteModal()">🗑️ Delete Collection</button>
                                </div>
                            </div>
                        `;

                        displayContentItems();
                    }}

                    function displayContentItems() {{
                        const list = document.getElementById('contentList');
                        const items = collection.items || [];

                        if (items.length === 0) {{
                            list.innerHTML = '<p style="text-align: center; padding: 3rem; color: var(--text-muted);">No content items yet. Click "Add Content" to get started.</p>';
                            return;
                        }}

                        list.innerHTML = items.map(item => `
                            <div class="content-item">
                                <div>
                                    <div style="font-weight: 600; margin-bottom: 0.25rem;">${{item.title}}</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                        ${{item.content_type}} • ${{item.language}}
                                    </div>
                                </div>
                                <div style="display: flex; gap: 0.5rem;">
                                    <button class="btn" style="padding: 0.5rem 1rem; font-size: 0.875rem;"
                                            onclick="window.location.href='/content/${{item.content_id}}'">
                                        View
                                    </button>
                                    <button class="btn btn-danger" style="padding: 0.5rem 1rem; font-size: 0.875rem;"
                                            onclick="removeContent('${{item.content_id}}')">
                                        Remove
                                    </button>
                                </div>
                            </div>
                        `).join('');
                    }}

                    async function removeContent(contentId) {{
                        if (!confirm('Remove this content from the collection?')) return;

                        try {{
                            const response = await fetch(`/api/content/collections/${{collectionId}}/items/${{contentId}}`, {{
                                method: 'DELETE',
                                credentials: 'include'
                            }});

                            if (!response.ok) throw new Error('Failed to remove');

                            await loadCollection();

                        }} catch (error) {{
                            console.error('Error:', error);
                            alert('Failed to remove content');
                        }}
                    }}

                    async function showAddContentModal() {{
                        try {{
                            const response = await fetch('/api/content/library', {{
                                credentials: 'include'
                            }});

                            if (!response.ok) throw new Error('Failed to load content');

                            const data = await response.json();
                            allContent = data.content || [];

                            const available = document.getElementById('availableContent');
                            available.innerHTML = allContent.map(item => `
                                <label class="checkbox-item" style="display: flex; align-items: center;">
                                    <input type="checkbox" value="${{item.metadata.content_id}}" style="margin-right: 0.75rem;">
                                    <div>
                                        <div style="font-weight: 600;">${{item.metadata.title}}</div>
                                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                            ${{item.metadata.content_type}} • ${{item.metadata.language}}
                                        </div>
                                    </div>
                                </label>
                            `).join('');

                            document.getElementById('addContentModal').classList.add('active');

                        }} catch (error) {{
                            console.error('Error:', error);
                            alert('Failed to load content');
                        }}
                    }}

                    function hideAddContentModal() {{
                        document.getElementById('addContentModal').classList.remove('active');
                    }}

                    async function addSelectedContent() {{
                        const checkboxes = document.querySelectorAll('#availableContent input:checked');
                        const contentIds = Array.from(checkboxes).map(cb => cb.value);

                        if (contentIds.length === 0) {{
                            alert('Please select at least one item');
                            return;
                        }}

                        try {{
                            for (const contentId of contentIds) {{
                                await fetch(`/api/content/collections/${{collectionId}}/items`, {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json' }},
                                    credentials: 'include',
                                    body: JSON.stringify({{ content_id: contentId }})
                                }});
                            }}

                            hideAddContentModal();
                            await loadCollection();

                        }} catch (error) {{
                            console.error('Error:', error);
                            alert('Failed to add content');
                        }}
                    }}

                    function showDeleteModal() {{
                        document.getElementById('deleteModal').classList.add('active');
                    }}

                    function hideDeleteModal() {{
                        document.getElementById('deleteModal').classList.remove('active');
                    }}

                    async function confirmDelete() {{
                        try {{
                            const response = await fetch(`/api/content/collections/${{collectionId}}`, {{
                                method: 'DELETE',
                                credentials: 'include'
                            }});

                            if (!response.ok) throw new Error('Failed to delete');

                            window.location.href = '/collections';

                        }} catch (error) {{
                            console.error('Error:', error);
                            alert('Failed to delete collection');
                        }}
                    }}
                """),
            ),
        )
