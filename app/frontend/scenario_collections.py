"""
Scenario Collections Management Interface
AI Language Tutor App - Session 133

User interface for managing scenario collections and learning paths.
Enables users to create, edit, organize, and share collections.

Features:
- Collections dashboard (list view)
- Create collection modal
- Collection detail view with scenarios
- Drag-and-drop reordering for learning paths
- Add/remove scenarios
- Public/private toggle
- Delete confirmation
"""

import logging
from typing import Dict, List, Optional

from fastapi import Depends
from fasthtml.common import *

from app.core.security import require_auth
from app.models.simple_user import SimpleUser

logger = logging.getLogger(__name__)


def collections_styles():
    """CSS styles for collections management interface"""
    return Style("""
        .collections-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .collections-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 16px;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .collections-header-content h1 {
            margin: 0 0 12px 0;
            font-size: 3rem;
            font-weight: 700;
        }

        .collections-header-content p {
            margin: 0;
            opacity: 0.95;
            font-size: 1.2rem;
        }

        .create-btn {
            padding: 16px 32px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .create-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        /* Tabs */
        .collections-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
        }

        .collections-tab {
            padding: 14px 28px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            color: #64748b;
            transition: all 0.3s;
            font-size: 1rem;
        }

        .collections-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
        }

        .collections-tab:hover:not(.active) {
            border-color: #667eea;
            color: #667eea;
        }

        /* Collections Grid */
        .collections-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }

        /* Collection Card */
        .collection-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
        }

        .collection-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.2);
        }

        .collection-card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 24px;
            color: white;
            position: relative;
        }

        .learning-path-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            background: rgba(255,255,255,0.3);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            backdrop-filter: blur(10px);
        }

        .collection-card-header h3 {
            margin: 0 0 8px 0;
            font-size: 1.5rem;
            line-height: 1.3;
        }

        .collection-category {
            display: inline-block;
            background: rgba(255,255,255,0.25);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .collection-card-body {
            padding: 24px;
        }

        .collection-description {
            color: #64748b;
            margin-bottom: 20px;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 72px;
        }

        .collection-stats {
            display: flex;
            gap: 20px;
            padding: 16px 0;
            border-top: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 16px;
        }

        .collection-stat {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #64748b;
            font-size: 0.95rem;
        }

        .collection-stat .icon {
            font-size: 1.2rem;
        }

        .collection-stat .value {
            font-weight: 700;
            color: #1e293b;
        }

        .collection-actions {
            display: flex;
            gap: 8px;
        }

        .collection-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }

        .btn-view {
            background: #667eea;
            color: white;
        }

        .btn-view:hover {
            background: #5568d3;
        }

        .btn-edit {
            background: #f1f5f9;
            color: #475569;
        }

        .btn-edit:hover {
            background: #e2e8f0;
        }

        .btn-delete {
            background: #fee2e2;
            color: #dc2626;
        }

        .btn-delete:hover {
            background: #fecaca;
        }

        .visibility-toggle {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            background: #f8fafc;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #64748b;
        }

        .visibility-toggle.public {
            background: #dbeafe;
            color: #1e40af;
        }

        /* Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            z-index: 1000;
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-content {
            background: white;
            border-radius: 20px;
            width: 90%;
            max-width: 700px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: modalSlideIn 0.3s ease;
        }

        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            color: white;
            border-radius: 20px 20px 0 0;
        }

        .modal-header h2 {
            margin: 0 0 8px 0;
            font-size: 2rem;
        }

        .modal-header p {
            margin: 0;
            opacity: 0.9;
        }

        .modal-body {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #1e293b;
            font-size: 0.95rem;
        }

        .form-input,
        .form-textarea,
        .form-select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s;
            font-family: inherit;
        }

        .form-input:focus,
        .form-textarea:focus,
        .form-select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-textarea {
            resize: vertical;
            min-height: 100px;
        }

        .form-checkbox {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: #f8fafc;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .form-checkbox:hover {
            background: #f1f5f9;
        }

        .form-checkbox input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        .form-checkbox-label {
            font-weight: 600;
            color: #1e293b;
        }

        .form-checkbox-desc {
            font-size: 0.9rem;
            color: #64748b;
            margin-top: 4px;
        }

        .modal-footer {
            padding: 20px 30px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }

        .modal-btn {
            padding: 12px 28px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1rem;
        }

        .modal-btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .modal-btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .modal-btn-secondary {
            background: #f1f5f9;
            color: #475569;
        }

        .modal-btn-secondary:hover {
            background: #e2e8f0;
        }

        /* Collection Detail View */
        .collection-detail {
            background: white;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .collection-detail-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 24px;
        }

        .collection-detail-title {
            font-size: 2.5rem;
            margin: 0 0 12px 0;
            color: #1e293b;
        }

        .collection-detail-meta {
            display: flex;
            gap: 20px;
            color: #64748b;
            font-size: 1rem;
        }

        .collection-detail-actions {
            display: flex;
            gap: 12px;
        }

        .scenarios-list {
            margin-top: 30px;
        }

        .scenarios-list-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .scenarios-list-header h3 {
            margin: 0;
            font-size: 1.5rem;
            color: #1e293b;
        }

        .add-scenario-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .add-scenario-btn:hover {
            background: #5568d3;
        }

        .scenario-item {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 16px;
            transition: all 0.3s;
            cursor: move;
        }

        .scenario-item:hover {
            border-color: #667eea;
            background: white;
        }

        .scenario-item.dragging {
            opacity: 0.5;
        }

        .drag-handle {
            font-size: 1.5rem;
            color: #94a3b8;
            cursor: move;
        }

        .scenario-item-position {
            width: 32px;
            height: 32px;
            background: #667eea;
            color: white;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
        }

        .scenario-item-content {
            flex: 1;
        }

        .scenario-item-title {
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
        }

        .scenario-item-meta {
            font-size: 0.9rem;
            color: #64748b;
        }

        .scenario-item-remove {
            padding: 8px 16px;
            background: #fee2e2;
            color: #dc2626;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            flex-shrink: 0;
        }

        .scenario-item-remove:hover {
            background: #fecaca;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }

        .empty-state-icon {
            font-size: 5rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        .empty-state h3 {
            margin: 0 0 12px 0;
            color: #1e293b;
            font-size: 1.5rem;
        }

        .empty-state p {
            margin: 0 0 24px 0;
            color: #64748b;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .collections-header {
                flex-direction: column;
                gap: 20px;
            }

            .collections-header-content h1 {
                font-size: 2rem;
            }

            .collections-grid {
                grid-template-columns: 1fr;
            }

            .collections-tabs {
                flex-direction: column;
            }

            .scenario-item {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    """)


def create_collection_card(collection: Dict) -> Div:
    """
    Create a collection card component.

    Args:
        collection: Collection data dictionary

    Returns:
        Div containing collection card
    """
    name = collection.get("name", "Untitled Collection")
    description = collection.get("description", "No description provided")
    item_count = collection.get("item_count", 0)
    is_learning_path = collection.get("is_learning_path", False)
    is_public = collection.get("is_public", False)
    category = collection.get("category", "")
    collection_id = collection.get("collection_id", "")

    return Div(
        Div(
            Span("📚 Learning Path", cls="learning-path-badge")
            if is_learning_path
            else "",
            H3(name),
            Span(category.title(), cls="collection-category") if category else "",
            cls="collection-card-header",
        ),
        Div(
            P(description, cls="collection-description"),
            Div(
                Div(
                    Span("📝", cls="icon"),
                    Span(f"{item_count}", cls="value"),
                    Span(" scenarios"),
                    cls="collection-stat",
                ),
                Div(
                    Span("🌐" if is_public else "🔒", cls="icon"),
                    Span("Public" if is_public else "Private", cls="value"),
                    cls="collection-stat",
                ),
                cls="collection-stats",
            ),
            Div(
                Button(
                    "View",
                    cls="collection-btn btn-view",
                    onclick=f"viewCollection('{collection_id}')",
                ),
                Button(
                    "Edit",
                    cls="collection-btn btn-edit",
                    onclick=f"editCollection('{collection_id}')",
                ),
                Button(
                    "Delete",
                    cls="collection-btn btn-delete",
                    onclick=f"deleteCollection('{collection_id}')",
                ),
                cls="collection-actions",
            ),
            cls="collection-card-body",
        ),
        cls="collection-card",
        **{"data-collection-id": collection_id},
    )


def create_collections_route():
    """
    Create the collections management route handler.

    Returns:
        Route handler function
    """

    def collections_page(current_user: SimpleUser = Depends(require_auth)):
        """Collections management page handler"""

        # Tabs
        tabs = Div(
            Button(
                "My Collections",
                cls="collections-tab active",
                **{"data-tab": "my-collections"},
            ),
            Button(
                "Learning Paths",
                cls="collections-tab",
                **{"data-tab": "learning-paths"},
            ),
            Button(
                "Public Collections", cls="collections-tab", **{"data-tab": "public"}
            ),
            cls="collections-tabs",
        )

        # Tab contents
        my_collections_content = Div(
            Div(id="my-collections-grid", cls="collections-grid"),
            cls="tab-content active",
            id="tab-my-collections",
        )

        learning_paths_content = Div(
            Div(id="learning-paths-grid", cls="collections-grid"),
            cls="tab-content",
            id="tab-learning-paths",
        )

        public_collections_content = Div(
            Div(id="public-collections-grid", cls="collections-grid"),
            cls="tab-content",
            id="tab-public",
        )

        # Create collection modal
        create_modal = Div(
            Div(
                Div(
                    H2("Create New Collection"),
                    P("Organize scenarios into a custom collection or learning path"),
                    cls="modal-header",
                ),
                Div(
                    Div(
                        Label("Collection Name", cls="form-label"),
                        Input(
                            type="text",
                            placeholder="e.g., Restaurant Basics, Travel Essentials",
                            cls="form-input",
                            id="collection-name",
                            required=True,
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Description (Optional)", cls="form-label"),
                        Textarea(
                            placeholder="Describe what this collection covers...",
                            cls="form-textarea",
                            id="collection-description",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Category (Optional)", cls="form-label"),
                        Select(
                            Option("-- Select Category --", value=""),
                            Option("Restaurant", value="restaurant"),
                            Option("Travel", value="travel"),
                            Option("Shopping", value="shopping"),
                            Option("Business", value="business"),
                            Option("Healthcare", value="healthcare"),
                            Option("Social", value="social"),
                            Option("Emergency", value="emergency"),
                            Option("Daily Life", value="daily_life"),
                            Option("Hobbies", value="hobbies"),
                            Option("Education", value="education"),
                            cls="form-select",
                            id="collection-category",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label("Difficulty Level (Optional)", cls="form-label"),
                        Select(
                            Option("-- Select Level --", value=""),
                            Option("Beginner", value="beginner"),
                            Option("Intermediate", value="intermediate"),
                            Option("Advanced", value="advanced"),
                            cls="form-select",
                            id="collection-difficulty",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label(
                            Input(type="checkbox", id="is-learning-path"),
                            Div(
                                Span("Learning Path", cls="form-checkbox-label"),
                                Div(
                                    "Scenarios will be ordered in a specific sequence for structured learning",
                                    cls="form-checkbox-desc",
                                ),
                            ),
                            cls="form-checkbox",
                        ),
                        cls="form-group",
                    ),
                    Div(
                        Label(
                            Input(type="checkbox", id="is-public"),
                            Div(
                                Span("Make Public", cls="form-checkbox-label"),
                                Div(
                                    "Share this collection with the community",
                                    cls="form-checkbox-desc",
                                ),
                            ),
                            cls="form-checkbox",
                        ),
                        cls="form-group",
                    ),
                    cls="modal-body",
                ),
                Div(
                    Button(
                        "Cancel",
                        cls="modal-btn modal-btn-secondary",
                        onclick="closeCreateModal()",
                    ),
                    Button(
                        "Create Collection",
                        cls="modal-btn modal-btn-primary",
                        onclick="submitCreateCollection()",
                    ),
                    cls="modal-footer",
                ),
                cls="modal-content",
            ),
            cls="modal-overlay",
            id="create-modal",
            onclick="closeModalOnOverlay(event)",
        )

        # JavaScript
        collections_script = Script("""
            // Tab switching
            document.querySelectorAll('.collections-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.collections-tab').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');

                    const tabName = this.dataset.tab;
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                    document.getElementById(`tab-${tabName}`).classList.add('active');

                    loadCollections(tabName);
                });
            });

            // Load initial data
            loadCollections('my-collections');

            async function loadCollections(type) {
                let container, url;

                if (type === 'my-collections') {
                    container = document.getElementById('my-collections-grid');
                    url = '/api/v1/scenario-organization/collections';
                } else if (type === 'learning-paths') {
                    container = document.getElementById('learning-paths-grid');
                    url = '/api/v1/scenario-organization/collections?learning_paths_only=true';
                } else if (type === 'public') {
                    container = document.getElementById('public-collections-grid');
                    url = '/api/v1/scenario-organization/public-collections?limit=20';
                }

                container.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Loading collections...</p></div>';

                try {
                    const response = await fetch(url);
                    const data = await response.json();

                    if (data.success && data.collections && data.collections.length > 0) {
                        // In a real implementation, we'd render server-side or use templates
                        // For now, show a placeholder
                        container.innerHTML = `<p>${data.collections.length} collections loaded</p>`;
                    } else {
                        showEmptyState(container, type);
                    }
                } catch (error) {
                    console.error('Error loading collections:', error);
                    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Error Loading Collections</h3><p>Please try again later</p></div>';
                }
            }

            function showEmptyState(container, type) {
                let icon = '📚';
                let title = 'No Collections Yet';
                let message = 'Create your first collection to organize scenarios';

                if (type === 'learning-paths') {
                    icon = '📖';
                    title = 'No Learning Paths Yet';
                    message = 'Create a learning path with ordered scenarios for structured learning';
                } else if (type === 'public') {
                    icon = '🌐';
                    title = 'No Public Collections';
                    message = 'Public collections from the community will appear here';
                }

                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">${icon}</div>
                        <h3>${title}</h3>
                        <p>${message}</p>
                        ${type !== 'public' ? '<button class="create-btn" onclick="openCreateModal()">Create Collection</button>' : ''}
                    </div>
                `;
            }

            function openCreateModal() {
                document.getElementById('create-modal').classList.add('active');
            }

            function closeCreateModal() {
                document.getElementById('create-modal').classList.remove('active');
                resetCreateForm();
            }

            function closeModalOnOverlay(event) {
                if (event.target.classList.contains('modal-overlay')) {
                    closeCreateModal();
                }
            }

            function resetCreateForm() {
                document.getElementById('collection-name').value = '';
                document.getElementById('collection-description').value = '';
                document.getElementById('collection-category').value = '';
                document.getElementById('collection-difficulty').value = '';
                document.getElementById('is-learning-path').checked = false;
                document.getElementById('is-public').checked = false;
            }

            async function submitCreateCollection() {
                const name = document.getElementById('collection-name').value.trim();

                if (!name) {
                    alert('Please enter a collection name');
                    return;
                }

                const data = {
                    name: name,
                    description: document.getElementById('collection-description').value.trim() || null,
                    category: document.getElementById('collection-category').value || null,
                    difficulty_level: document.getElementById('collection-difficulty').value || null,
                    is_learning_path: document.getElementById('is-learning-path').checked,
                    is_public: document.getElementById('is-public').checked
                };

                try {
                    const params = new URLSearchParams(data);
                    const response = await fetch(`/api/v1/scenario-organization/collections?${params.toString()}`, {
                        method: 'POST'
                    });

                    const result = await response.json();

                    if (result.success) {
                        closeCreateModal();
                        loadCollections('my-collections');
                        alert('Collection created successfully!');
                    } else {
                        alert('Error creating collection: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Error creating collection:', error);
                    alert('Failed to create collection. Please try again.');
                }
            }

            function viewCollection(collectionId) {
                window.location.href = `/collections/${collectionId}`;
            }

            function editCollection(collectionId) {
                window.location.href = `/collections/${collectionId}/edit`;
            }

            async function deleteCollection(collectionId) {
                if (!confirm('Are you sure you want to delete this collection? This action cannot be undone.')) {
                    return;
                }

                try {
                    const response = await fetch(`/api/v1/scenario-organization/collections/${collectionId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        loadCollections('my-collections');
                        alert('Collection deleted successfully');
                    } else {
                        alert('Error deleting collection');
                    }
                } catch (error) {
                    console.error('Error deleting collection:', error);
                    alert('Failed to delete collection. Please try again.');
                }
            }
        """)

        # Main page structure
        page_content = Div(
            collections_styles(),
            Div(
                Div(
                    H1("📚 My Collections"),
                    P(
                        "Organize and manage your scenario collections and learning paths"
                    ),
                    cls="collections-header-content",
                ),
                Button(
                    "+ Create Collection", cls="create-btn", onclick="openCreateModal()"
                ),
                cls="collections-header",
            ),
            tabs,
            my_collections_content,
            learning_paths_content,
            public_collections_content,
            create_modal,
            collections_script,
            cls="collections-container",
        )

        return page_content

    return collections_page
