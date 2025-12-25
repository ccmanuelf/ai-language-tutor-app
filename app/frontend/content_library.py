"""
Content Library Page
AI Language Tutor App - Session 129 Frontend

Main hub for accessing all processed content with Session 129 features:
- View all content in grid/list layout
- Favorite/unfavorite content
- Tag content and filter by tags
- Add content to collections
- See mastery levels
- Start study sessions
- Extensible for future content features

User Stories Implemented:
- US-2.1, US-2.2, US-2.3, US-2.4: Tags
- US-3.1, US-3.2, US-3.3: Favorites
- US-4.1, US-4.4: Study tracking
- US-1.2: Add to collections

Design: Central content management hub
"""

from fasthtml.common import *


def create_content_library_routes(app):
    """Create content library routes"""

    @app.route("/library")
    def content_library():
        """Main content library page with all Session 129 features"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("Content Library - AI Language Tutor"),
                Style("""
                    :root {
                        --primary-color: #6366f1;
                        --primary-dark: #4338ca;
                        --success: #22c55e;
                        --warning: #f59e0b;
                        --info: #3b82f6;
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
                        max-width: 1400px;
                        margin: 0 auto;
                        padding: 2rem;
                    }

                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 2rem;
                        flex-wrap: wrap;
                        gap: 1rem;
                    }

                    .header h1 {
                        color: var(--primary-color);
                        font-size: 2rem;
                        font-weight: 700;
                    }

                    .header-actions {
                        display: flex;
                        gap: 0.75rem;
                        flex-wrap: wrap;
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
                    }

                    .btn-secondary {
                        background: var(--bg-tertiary);
                        color: var(--text-primary);
                    }

                    .btn-secondary:hover {
                        background: var(--border-color);
                    }

                    .filters-bar {
                        background: var(--bg-primary);
                        padding: 1.5rem;
                        border-radius: var(--radius-lg);
                        margin-bottom: 2rem;
                        box-shadow: var(--shadow);
                    }

                    .filters-row {
                        display: flex;
                        gap: 1rem;
                        flex-wrap: wrap;
                        align-items: center;
                    }

                    .filter-group {
                        flex: 1;
                        min-width: 200px;
                    }

                    .filter-label {
                        display: block;
                        margin-bottom: 0.5rem;
                        color: var(--text-secondary);
                        font-size: 0.875rem;
                        font-weight: 600;
                    }

                    .filter-input {
                        width: 100%;
                        padding: 0.625rem;
                        border: 2px solid var(--border-color);
                        border-radius: var(--radius);
                        font-size: 0.875rem;
                    }

                    .filter-input:focus {
                        outline: none;
                        border-color: var(--primary-color);
                    }

                    .tags-cloud {
                        display: flex;
                        gap: 0.5rem;
                        flex-wrap: wrap;
                        margin-top: 1rem;
                        padding-top: 1rem;
                        border-top: 1px solid var(--border-color);
                    }

                    .tag-chip {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.375rem;
                        padding: 0.375rem 0.75rem;
                        background: var(--bg-secondary);
                        border: 1px solid var(--border-color);
                        border-radius: 999px;
                        font-size: 0.875rem;
                        color: var(--text-secondary);
                        cursor: pointer;
                        transition: all 0.2s;
                    }

                    .tag-chip:hover {
                        background: var(--primary-color);
                        color: white;
                        border-color: var(--primary-color);
                    }

                    .tag-chip.active {
                        background: var(--primary-color);
                        color: white;
                        border-color: var(--primary-color);
                    }

                    .tag-count {
                        background: rgba(255, 255, 255, 0.3);
                        padding: 0.125rem 0.375rem;
                        border-radius: 999px;
                        font-size: 0.75rem;
                    }

                    .content-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                        gap: 1.5rem;
                        margin-bottom: 2rem;
                    }

                    .content-card {
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                        padding: 1.5rem;
                        box-shadow: var(--shadow);
                        border: 2px solid var(--border-color);
                        transition: all 0.2s;
                        position: relative;
                    }

                    .content-card:hover {
                        border-color: var(--primary-color);
                        transform: translateY(-2px);
                        box-shadow: var(--shadow-lg);
                    }

                    .card-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-start;
                        margin-bottom: 0.75rem;
                    }

                    .card-title {
                        font-size: 1.125rem;
                        font-weight: 600;
                        color: var(--text-primary);
                        margin-bottom: 0.5rem;
                        flex: 1;
                        cursor: pointer;
                    }

                    .card-title:hover {
                        color: var(--primary-color);
                    }

                    .favorite-btn {
                        background: none;
                        border: none;
                        font-size: 1.5rem;
                        cursor: pointer;
                        padding: 0.25rem;
                        transition: transform 0.2s;
                    }

                    .favorite-btn:hover {
                        transform: scale(1.2);
                    }

                    .favorite-btn.active {
                        color: var(--danger);
                    }

                    .card-meta {
                        display: flex;
                        gap: 0.75rem;
                        flex-wrap: wrap;
                        margin-bottom: 0.75rem;
                        font-size: 0.875rem;
                        color: var(--text-muted);
                    }

                    .card-collections {
                        display: flex;
                        gap: 0.5rem;
                        flex-wrap: wrap;
                        margin-bottom: 0.75rem;
                    }

                    .collection-badge {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.25rem;
                        padding: 0.25rem 0.625rem;
                        background: var(--bg-tertiary);
                        border-radius: 999px;
                        font-size: 0.75rem;
                        color: var(--text-secondary);
                        cursor: pointer;
                    }

                    .collection-badge:hover {
                        background: var(--primary-color);
                        color: white;
                    }

                    .card-tags {
                        display: flex;
                        gap: 0.375rem;
                        flex-wrap: wrap;
                        margin-bottom: 0.75rem;
                    }

                    .content-tag {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.25rem;
                        padding: 0.25rem 0.5rem;
                        background: var(--info);
                        color: white;
                        border-radius: 999px;
                        font-size: 0.75rem;
                    }

                    .tag-remove {
                        background: none;
                        border: none;
                        color: white;
                        cursor: pointer;
                        padding: 0;
                        font-size: 0.875rem;
                        opacity: 0.7;
                    }

                    .tag-remove:hover {
                        opacity: 1;
                    }

                    .tag-input-container {
                        display: flex;
                        gap: 0.5rem;
                        margin-bottom: 0.75rem;
                    }

                    .tag-input {
                        flex: 1;
                        padding: 0.5rem;
                        border: 1px solid var(--border-color);
                        border-radius: var(--radius);
                        font-size: 0.875rem;
                    }

                    .mastery-badge {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.375rem;
                        padding: 0.375rem 0.75rem;
                        border-radius: var(--radius);
                        font-size: 0.875rem;
                        font-weight: 600;
                        margin-bottom: 0.75rem;
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
                        background: #d1fae5;
                        color: #065f46;
                    }

                    .card-actions {
                        display: flex;
                        gap: 0.5rem;
                        flex-wrap: wrap;
                    }

                    .btn-sm {
                        padding: 0.5rem 1rem;
                        font-size: 0.875rem;
                    }

                    .loading {
                        text-align: center;
                        padding: 3rem;
                        color: var(--text-muted);
                    }

                    .empty-state {
                        text-align: center;
                        padding: 4rem 2rem;
                        background: var(--bg-primary);
                        border-radius: var(--radius-lg);
                    }

                    .empty-state-icon {
                        font-size: 4rem;
                        margin-bottom: 1rem;
                    }

                    /* Modal styles reused from collections.py */
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
                        max-height: 80vh;
                        overflow-y: auto;
                    }

                    .modal-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 1.5rem;
                    }

                    .modal-header h2 {
                        color: var(--text-primary);
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

                    .checkbox-list {
                        max-height: 300px;
                        overflow-y: auto;
                    }

                    .checkbox-item {
                        display: flex;
                        align-items: center;
                        padding: 0.75rem;
                        border-radius: var(--radius);
                        cursor: pointer;
                        transition: background 0.2s;
                    }

                    .checkbox-item:hover {
                        background: var(--bg-secondary);
                    }

                    .checkbox-item input {
                        margin-right: 0.75rem;
                    }

                    @media (max-width: 768px) {
                        .container {
                            padding: 1rem;
                        }

                        .content-grid {
                            grid-template-columns: 1fr;
                        }

                        .header {
                            flex-direction: column;
                            align-items: stretch;
                        }

                        .filters-row {
                            flex-direction: column;
                        }
                    }
                """),
            ),
            Body(
                Div(
                    # Header
                    Div(
                        H1("📚 Content Library"),
                        Div(
                            A(
                                "📚 Collections",
                                href="/collections",
                                cls="btn btn-secondary btn-sm",
                            ),
                            A(
                                "⭐ Favorites",
                                href="/favorites",
                                cls="btn btn-secondary btn-sm",
                            ),
                            A(
                                "📊 Study Stats",
                                href="/study-stats",
                                cls="btn btn-secondary btn-sm",
                            ),
                            cls="header-actions",
                        ),
                        cls="header",
                    ),
                    # Filters
                    Div(
                        Div(
                            Div(
                                Label("Search", cls="filter-label"),
                                Input(
                                    type="text",
                                    id="searchInput",
                                    cls="filter-input",
                                    placeholder="Search content...",
                                    oninput="filterContent()",
                                ),
                                cls="filter-group",
                            ),
                            Div(
                                Label("Content Type", cls="filter-label"),
                                Select(
                                    Option("All Types", value=""),
                                    Option("YouTube Video", value="youtube_video"),
                                    Option("PDF Document", value="pdf_document"),
                                    Option("Word Document", value="word_document"),
                                    id="typeFilter",
                                    cls="filter-input",
                                    onchange="filterContent()",
                                ),
                                cls="filter-group",
                            ),
                            Div(
                                Label("Language", cls="filter-label"),
                                Select(
                                    Option("All Languages", value=""),
                                    Option("Spanish", value="es"),
                                    Option("French", value="fr"),
                                    Option("German", value="de"),
                                    Option("Italian", value="it"),
                                    Option("Portuguese", value="pt"),
                                    id="languageFilter",
                                    cls="filter-input",
                                    onchange="filterContent()",
                                ),
                                cls="filter-group",
                            ),
                            cls="filters-row",
                        ),
                        # Tags cloud
                        Div(
                            Div(
                                "Popular Tags:",
                                style="margin-right: 1rem; font-weight: 600; color: var(--text-secondary);",
                            ),
                            Div(
                                id="tagsCloud",
                                style="display: flex; gap: 0.5rem; flex-wrap: wrap; flex: 1;",
                            ),
                            id="tagsSection",
                            cls="tags-cloud",
                            style="display: none;",
                        ),
                        cls="filters-bar",
                    ),
                    # Loading state
                    Div("Loading content library...", id="loadingState", cls="loading"),
                    # Content grid
                    Div(id="contentGrid", cls="content-grid", style="display: none;"),
                    # Empty state
                    Div(
                        Div("📚", cls="empty-state-icon"),
                        H2("No Content Yet"),
                        P(
                            "Upload or process content to see it here",
                            style="color: var(--text-muted); margin-bottom: 1.5rem;",
                        ),
                        A("Upload Content", href="/", cls="btn"),
                        id="emptyState",
                        cls="empty-state",
                        style="display: none;",
                    ),
                    cls="container",
                ),
                # Add to Collection Modal
                Div(
                    Div(
                        Div(
                            H2("Add to Collections"),
                            Button(
                                "✕",
                                cls="close-btn",
                                onclick="hideAddToCollectionModal()",
                            ),
                            cls="modal-header",
                        ),
                        Div(id="collectionCheckboxes", cls="checkbox-list"),
                        Div(
                            Button(
                                "Cancel",
                                cls="btn btn-secondary",
                                onclick="hideAddToCollectionModal()",
                            ),
                            Button(
                                "Add to Selected",
                                cls="btn",
                                onclick="addToSelectedCollections()",
                            ),
                            style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;",
                        ),
                        cls="modal-content",
                    ),
                    id="addToCollectionModal",
                    cls="modal",
                ),
                # Embed study session modal HTML from study_session.py
                Script("""
                    // Will be populated with study session modal HTML
                    const studyModalHTML = `
                        <div id="studySessionModal" class="modal">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h2>📖 Study Session</h2>
                                    <button class="close-btn" onclick="cancelStudySession()">✕</button>
                                </div>
                                <div class="session-timer" style="text-align: center; padding: 2rem; background: var(--bg-secondary); border-radius: var(--radius); margin-bottom: 1.5rem;">
                                    <div id="timerDisplay" style="font-size: 3rem; font-weight: 700; color: var(--primary-color);">00:00</div>
                                    <div style="color: var(--text-muted); margin-top: 0.5rem;">Elapsed Time</div>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                                    <div>
                                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Items Studied</label>
                                        <input type="number" id="itemsStudied" value="0" min="0" class="filter-input">
                                    </div>
                                    <div>
                                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Items Correct</label>
                                        <input type="number" id="itemsCorrect" value="0" min="0" class="filter-input">
                                    </div>
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.875rem;">
                                        <span>Progress</span>
                                        <span id="progressPercent">0%</span>
                                    </div>
                                    <div style="height: 8px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden;">
                                        <div id="progressBar" style="height: 100%; background: var(--primary-color); width: 0%; transition: width 0.3s;"></div>
                                    </div>
                                </div>
                                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                                    <button class="btn btn-secondary" onclick="cancelStudySession()">Cancel</button>
                                    <button class="btn" onclick="completeStudySession()">Complete Session</button>
                                </div>
                            </div>
                        </div>
                    `;
                    document.body.insertAdjacentHTML('beforeend', studyModalHTML);
                """),
                # JavaScript for content library functionality
                Script("""
                    let allContent = [];
                    let allTags = [];
                    let allCollections = [];
                    let currentContentId = null;
                    let activeSessionId = null;
                    let sessionStartTime = null;
                    let timerInterval = null;
                    let activeTagFilter = null;

                    document.addEventListener('DOMContentLoaded', init);

                    async function init() {
                        await loadContent();
                        await loadTags();
                        await loadCollections();
                    }

                    async function loadContent() {
                        try {
                            const response = await fetch('/api/content/library', {
                                credentials: 'include'
                            });

                            if (!response.ok) throw new Error('Failed to load content');

                            const data = await response.json();
                            allContent = data.content || [];

                            document.getElementById('loadingState').style.display = 'none';

                            if (allContent.length === 0) {
                                document.getElementById('emptyState').style.display = 'block';
                            } else {
                                document.getElementById('contentGrid').style.display = 'grid';
                                displayContent(allContent);
                            }

                        } catch (error) {
                            console.error('Error:', error);
                            document.getElementById('loadingState').innerHTML =
                                '<div style="color: var(--danger);">Failed to load content. Please try again.</div>';
                        }
                    }

                    async function loadTags() {
                        try {
                            const response = await fetch('/api/content/tags', {
                                credentials: 'include'
                            });

                            if (!response.ok) return;

                            allTags = await response.json();

                            if (allTags.length > 0) {
                                document.getElementById('tagsSection').style.display = 'flex';
                                displayTagsCloud();
                            }

                        } catch (error) {
                            console.error('Error loading tags:', error);
                        }
                    }

                    async function loadCollections() {
                        try {
                            const response = await fetch('/api/content/collections', {
                                credentials: 'include'
                            });

                            if (!response.ok) return;

                            allCollections = await response.json();

                        } catch (error) {
                            console.error('Error loading collections:', error);
                        }
                    }

                    function displayTagsCloud() {
                        const cloud = document.getElementById('tagsCloud');
                        cloud.innerHTML = allTags.map(t => `
                            <div class="tag-chip ${activeTagFilter === t.tag ? 'active' : ''}" onclick="filterByTag('${t.tag}')">
                                🏷️ ${t.tag}
                                <span class="tag-count">${t.count}</span>
                            </div>
                        `).join('');
                    }

                    function filterByTag(tag) {
                        if (activeTagFilter === tag) {
                            activeTagFilter = null;
                        } else {
                            activeTagFilter = tag;
                        }
                        displayTagsCloud();
                        filterContent();
                    }

                    function filterContent() {
                        const search = document.getElementById('searchInput').value.toLowerCase();
                        const type = document.getElementById('typeFilter').value;
                        const language = document.getElementById('languageFilter').value;

                        let filtered = allContent.filter(item => {
                            const matchesSearch = !search ||
                                item.metadata.title.toLowerCase().includes(search) ||
                                (item.metadata.topics || []).some(t => t.toLowerCase().includes(search));

                            const matchesType = !type || item.metadata.content_type === type;
                            const matchesLanguage = !language || item.metadata.language === language;
                            const matchesTag = !activeTagFilter || (item.tags || []).includes(activeTagFilter);

                            return matchesSearch && matchesType && matchesLanguage && matchesTag;
                        });

                        displayContent(filtered);
                    }

                    function displayContent(content) {
                        const grid = document.getElementById('contentGrid');

                        if (content.length === 0) {
                            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">No content matches your filters</div>';
                            return;
                        }

                        grid.innerHTML = content.map(item => createContentCard(item)).join('');
                    }

                    function createContentCard(item) {
                        const isFavorite = item.is_favorite || false;
                        const tags = item.tags || [];
                        const collections = item.collections || [];
                        const masteryLevel = item.mastery_level || 'not_started';
                        const masteryClass = 'mastery-' + masteryLevel.replace('_', '-');
                        const masteryLabels = {
                            'not_started': '⚪ Not Started',
                            'learning': '🟡 Learning',
                            'reviewing': '🔵 Reviewing',
                            'mastered': '🟢 Mastered'
                        };

                        return `
                            <div class="content-card">
                                <div class="card-header">
                                    <h3 class="card-title" onclick="viewContent('${item.metadata.content_id}')">
                                        ${item.metadata.title}
                                    </h3>
                                    <button class="favorite-btn ${isFavorite ? 'active' : ''}"
                                            onclick="toggleFavorite('${item.metadata.content_id}', this)">
                                        ${isFavorite ? '♥' : '♡'}
                                    </button>
                                </div>

                                <div class="card-meta">
                                    <span>${item.metadata.content_type}</span>
                                    <span>•</span>
                                    <span>${item.metadata.language}</span>
                                    <span>•</span>
                                    <span>${item.metadata.word_count} words</span>
                                </div>

                                <div class="mastery-badge ${masteryClass}">
                                    ${masteryLabels[masteryLevel]}
                                </div>

                                ${collections.length > 0 ? `
                                    <div class="card-collections">
                                        ${collections.map(c => `
                                            <span class="collection-badge" onclick="window.location.href='/collections/${c.collection_id}'">
                                                ${c.icon || '📚'} ${c.name}
                                            </span>
                                        `).join('')}
                                    </div>
                                ` : ''}

                                <div class="card-tags">
                                    ${tags.map(tag => `
                                        <span class="content-tag">
                                            🏷️ ${tag}
                                            <button class="tag-remove" onclick="removeTag('${item.metadata.content_id}', '${tag}')">✕</button>
                                        </span>
                                    `).join('')}
                                </div>

                                <div class="tag-input-container">
                                    <input type="text"
                                           class="tag-input"
                                           placeholder="Add tag..."
                                           id="tagInput-${item.metadata.content_id}"
                                           onkeypress="handleTagInput(event, '${item.metadata.content_id}')">
                                    <button class="btn btn-sm btn-secondary"
                                            onclick="addTag('${item.metadata.content_id}')">
                                        Add
                                    </button>
                                </div>

                                <div class="card-actions">
                                    <button class="btn btn-sm" onclick="viewContent('${item.metadata.content_id}')">
                                        View
                                    </button>
                                    <button class="btn btn-sm btn-secondary" onclick="startStudy('${item.metadata.content_id}')">
                                        📖 Study
                                    </button>
                                    <button class="btn btn-sm btn-secondary" onclick="showAddToCollectionModal('${item.metadata.content_id}')">
                                        ➕ Collection
                                    </button>
                                </div>
                            </div>
                        `;
                    }

                    function viewContent(contentId) {
                        window.location.href = `/content/${contentId}`;
                    }

                    async function toggleFavorite(contentId, button) {
                        const isFavorite = button.classList.contains('active');
                        const method = isFavorite ? 'DELETE' : 'POST';

                        try {
                            const response = await fetch(`/api/content/${contentId}/favorite`, {
                                method: method,
                                credentials: 'include'
                            });

                            if (!response.ok) throw new Error('Failed to toggle favorite');

                            button.classList.toggle('active');
                            button.textContent = button.classList.contains('active') ? '♥' : '♡';

                            // Update in allContent array
                            const item = allContent.find(c => c.metadata.content_id === contentId);
                            if (item) item.is_favorite = !isFavorite;

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to toggle favorite');
                        }
                    }

                    async function addTag(contentId) {
                        const input = document.getElementById(`tagInput-${contentId}`);
                        const tag = input.value.trim();

                        if (!tag) return;

                        try {
                            const response = await fetch(`/api/content/${contentId}/tags`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include',
                                body: JSON.stringify({ tag })
                            });

                            if (!response.ok) throw new Error('Failed to add tag');

                            input.value = '';
                            await loadContent();
                            await loadTags();

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to add tag');
                        }
                    }

                    function handleTagInput(event, contentId) {
                        if (event.key === 'Enter') {
                            event.preventDefault();
                            addTag(contentId);
                        }
                    }

                    async function removeTag(contentId, tag) {
                        try {
                            const response = await fetch(`/api/content/${contentId}/tags/${encodeURIComponent(tag)}`, {
                                method: 'DELETE',
                                credentials: 'include'
                            });

                            if (!response.ok) throw new Error('Failed to remove tag');

                            await loadContent();
                            await loadTags();

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to remove tag');
                        }
                    }

                    function showAddToCollectionModal(contentId) {
                        currentContentId = contentId;

                        const checkboxes = document.getElementById('collectionCheckboxes');
                        checkboxes.innerHTML = allCollections.map(c => `
                            <label class="checkbox-item">
                                <input type="checkbox" value="${c.collection_id}">
                                ${c.icon || '📚'} ${c.name}
                            </label>
                        `).join('');

                        document.getElementById('addToCollectionModal').classList.add('active');
                    }

                    function hideAddToCollectionModal() {
                        document.getElementById('addToCollectionModal').classList.remove('active');
                        currentContentId = null;
                    }

                    async function addToSelectedCollections() {
                        const checkboxes = document.querySelectorAll('#collectionCheckboxes input:checked');
                        const collectionIds = Array.from(checkboxes).map(cb => cb.value);

                        if (collectionIds.length === 0) {
                            alert('Please select at least one collection');
                            return;
                        }

                        try {
                            for (const collectionId of collectionIds) {
                                await fetch(`/api/content/collections/${collectionId}/items`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    credentials: 'include',
                                    body: JSON.stringify({ content_id: currentContentId })
                                });
                            }

                            hideAddToCollectionModal();
                            await loadContent();
                            alert('Added to collections successfully!');

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to add to collections');
                        }
                    }

                    // Study session functions (from study_session.py)
                    async function startStudy(contentId) {
                        currentContentId = contentId;

                        try {
                            const response = await fetch(`/api/content/${contentId}/study/start`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include',
                                body: JSON.stringify({})
                            });

                            if (!response.ok) throw new Error('Failed to start session');

                            const session = await response.json();
                            activeSessionId = session.id;
                            sessionStartTime = new Date();

                            document.getElementById('studySessionModal').classList.add('active');
                            document.getElementById('itemsStudied').value = '0';
                            document.getElementById('itemsCorrect').value = '0';
                            startTimer();

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to start study session');
                        }
                    }

                    function startTimer() {
                        timerInterval = setInterval(() => {
                            if (!sessionStartTime) return;
                            const elapsed = Math.floor((new Date() - sessionStartTime) / 1000);
                            const minutes = Math.floor(elapsed / 60);
                            const seconds = elapsed % 60;
                            document.getElementById('timerDisplay').textContent =
                                `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                        }, 1000);
                    }

                    function cancelStudySession() {
                        if (confirm('Cancel session? Progress will not be saved.')) {
                            document.getElementById('studySessionModal').classList.remove('active');
                            if (timerInterval) clearInterval(timerInterval);
                            activeSessionId = null;
                            sessionStartTime = null;
                        }
                    }

                    async function completeStudySession() {
                        if (!activeSessionId) return;

                        const duration = Math.floor((new Date() - sessionStartTime) / 1000);
                        const studied = parseInt(document.getElementById('itemsStudied').value) || 0;
                        const correct = parseInt(document.getElementById('itemsCorrect').value) || 0;

                        try {
                            const response = await fetch(`/api/content/${currentContentId}/study/${activeSessionId}/complete`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include',
                                body: JSON.stringify({
                                    duration_seconds: duration,
                                    items_total: studied,
                                    items_correct: correct
                                })
                            });

                            if (!response.ok) throw new Error('Failed to complete session');

                            const result = await response.json();
                            alert(`Session completed! Mastery level: ${result.mastery_level}`);

                            document.getElementById('studySessionModal').classList.remove('active');
                            if (timerInterval) clearInterval(timerInterval);
                            activeSessionId = null;
                            sessionStartTime = null;

                            await loadContent();

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to complete session');
                        }
                    }

                    // Update progress as user types
                    document.addEventListener('DOMContentLoaded', () => {
                        const updateProgress = () => {
                            const studied = parseInt(document.getElementById('itemsStudied').value) || 0;
                            const correct = parseInt(document.getElementById('itemsCorrect').value) || 0;

                            if (studied > 0) {
                                const percent = Math.round((correct / studied) * 100);
                                document.getElementById('progressBar').style.width = percent + '%';
                                document.getElementById('progressPercent').textContent = percent + '%';
                            }
                        };

                        setTimeout(() => {
                            const studiedInput = document.getElementById('itemsStudied');
                            const correctInput = document.getElementById('itemsCorrect');
                            if (studiedInput) studiedInput.addEventListener('input', updateProgress);
                            if (correctInput) correctInput.addEventListener('input', updateProgress);
                        }, 1000);
                    });
                """),
            ),
        )

    @app.route("/favorites")
    def favorites_page():
        """Favorites page - filtered view showing only favorited content - US-3.2"""
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("Favorites - AI Language Tutor"),
                Link(
                    rel="stylesheet",
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
                ),
                Style("""
                    /* Reuse all styles from content_library */
                    :root {
                        --primary-color: #6366f1;
                        --danger: #ef4444;
                        --text-primary: #0f172a;
                        --text-secondary: #64748b;
                        --text-muted: #94a3b8;
                        --bg-primary: #ffffff;
                        --bg-secondary: #f8fafc;
                        --border-color: #e2e8f0;
                        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        --radius: 0.5rem;
                        --radius-lg: 1rem;
                    }
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
                        background: var(--bg-secondary);
                        color: var(--text-primary);
                    }
                    .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
                    .header h1 { color: var(--primary-color); font-size: 2rem; }
                    .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem;
                           background: var(--primary-color); color: white; text-decoration: none;
                           border-radius: var(--radius); font-weight: 600; border: none; cursor: pointer; }
                    .btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); }
                    .content-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
                    .content-card { background: var(--bg-primary); border-radius: var(--radius-lg); padding: 1.5rem;
                                   box-shadow: var(--shadow); border: 2px solid var(--border-color); }
                    .card-title { font-size: 1.125rem; font-weight: 600; margin-bottom: 0.75rem; cursor: pointer; }
                    .card-title:hover { color: var(--primary-color); }
                    .card-meta { color: var(--text-muted); font-size: 0.875rem; margin-bottom: 0.75rem; }
                    .favorite-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--danger); }
                    .empty-state { text-align: center; padding: 4rem 2rem; background: var(--bg-primary);
                                  border-radius: var(--radius-lg); }
                    .empty-state-icon { font-size: 4rem; margin-bottom: 1rem; }
                    .loading { text-align: center; padding: 3rem; color: var(--text-muted); }
                    @media (max-width: 768px) {
                        .container { padding: 1rem; }
                        .content-grid { grid-template-columns: 1fr; }
                    }
                """),
            ),
            Body(
                Div(
                    Div(
                        H1("⭐ My Favorites"),
                        A(
                            "← Back to Library",
                            href="/library",
                            cls="btn btn-secondary",
                        ),
                        cls="header",
                    ),
                    Div("Loading favorites...", id="loadingState", cls="loading"),
                    Div(id="contentGrid", cls="content-grid", style="display: none;"),
                    Div(
                        Div("⭐", cls="empty-state-icon"),
                        H2("No Favorites Yet"),
                        P(
                            "Mark content as favorite to see it here",
                            style="color: var(--text-muted); margin-bottom: 1.5rem;",
                        ),
                        A("Browse Library", href="/library", cls="btn"),
                        id="emptyState",
                        cls="empty-state",
                        style="display: none;",
                    ),
                    cls="container",
                ),
                Script("""
                    document.addEventListener('DOMContentLoaded', loadFavorites);

                    async function loadFavorites() {
                        try {
                            const response = await fetch('/api/content/favorites', {
                                credentials: 'include'
                            });

                            if (!response.ok) throw new Error('Failed to load favorites');

                            const favorites = await response.json();

                            document.getElementById('loadingState').style.display = 'none';

                            if (favorites.length === 0) {
                                document.getElementById('emptyState').style.display = 'block';
                            } else {
                                document.getElementById('contentGrid').style.display = 'grid';
                                displayFavorites(favorites);
                            }

                        } catch (error) {
                            console.error('Error:', error);
                            document.getElementById('loadingState').innerHTML =
                                '<div style="color: var(--danger);">Failed to load favorites</div>';
                        }
                    }

                    function displayFavorites(favorites) {
                        const grid = document.getElementById('contentGrid');
                        grid.innerHTML = favorites.map(item => `
                            <div class="content-card">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <h3 class="card-title" onclick="window.location.href='/content/${item.content_id}'">
                                        ${item.title}
                                    </h3>
                                    <button class="favorite-btn" onclick="unfavorite('${item.content_id}', this)">
                                        ♥
                                    </button>
                                </div>
                                <div class="card-meta">
                                    ${item.content_type} • ${item.language} • ${item.word_count} words
                                </div>
                                <div style="margin-top: 1rem;">
                                    <button class="btn" style="font-size: 0.875rem; padding: 0.5rem 1rem;"
                                            onclick="window.location.href='/content/${item.content_id}'">
                                        View Content
                                    </button>
                                </div>
                            </div>
                        `).join('');
                    }

                    async function unfavorite(contentId, button) {
                        try {
                            const response = await fetch(`/api/content/${contentId}/favorite`, {
                                method: 'DELETE',
                                credentials: 'include'
                            });

                            if (!response.ok) throw new Error('Failed to unfavorite');

                            // Remove card from view
                            button.closest('.content-card').remove();

                            // Check if empty
                            const grid = document.getElementById('contentGrid');
                            if (grid.children.length === 0) {
                                grid.style.display = 'none';
                                document.getElementById('emptyState').style.display = 'block';
                            }

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to unfavorite');
                        }
                    }
                """),
            ),
        )

    @app.route("/discover")
    def discover_redirect():
        """Redirect /discover to /library (they serve the same purpose)"""
        return RedirectResponse(url="/library", status_code=301)
