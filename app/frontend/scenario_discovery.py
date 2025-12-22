"""
Scenario Discovery Hub Interface
AI Language Tutor App - Session 133

Discovery interface for finding scenarios through:
- Search with filters
- Trending scenarios
- Top-rated scenarios
- Popular scenarios
- Personalized recommendations
- Public collections

Features:
- Multi-tab discovery interface
- Real-time search with filters
- Scenario cards with ratings
- Bookmark integration
- Collection browsing
"""

import logging
from typing import Dict, List, Optional

import httpx
from fasthtml.common import *

from app.core.security import require_auth
from app.database.config import get_db_session
from app.models.simple_user import SimpleUser

logger = logging.getLogger(__name__)


def discovery_hub_styles():
    """CSS styles for discovery hub interface"""
    return Style("""
        .discovery-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .discovery-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 16px;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        }

        .discovery-header h1 {
            margin: 0 0 12px 0;
            font-size: 3rem;
            font-weight: 700;
        }

        .discovery-header p {
            margin: 0;
            opacity: 0.95;
            font-size: 1.2rem;
        }

        /* Search Section */
        .search-section {
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        .search-box {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }

        .search-input {
            flex: 1;
            padding: 14px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }

        .search-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .search-btn {
            padding: 14px 32px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1rem;
        }

        .search-btn:hover {
            background: #5568d3;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .search-filters {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .filter-select {
            padding: 10px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.95rem;
            cursor: pointer;
            background: white;
            transition: all 0.3s;
        }

        .filter-select:focus {
            outline: none;
            border-color: #667eea;
        }

        /* Tabs */
        .discovery-tabs {
            display: flex;
            background: white;
            border-radius: 12px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .discovery-tab {
            flex: 1;
            padding: 20px 24px;
            background: #f8fafc;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #64748b;
            transition: all 0.3s;
            text-align: center;
            font-size: 1rem;
            position: relative;
        }

        .discovery-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .discovery-tab:hover:not(.active) {
            background: #e2e8f0;
        }

        .discovery-tab .badge {
            display: inline-block;
            background: rgba(255,255,255,0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-left: 8px;
        }

        .discovery-tab.active .badge {
            background: rgba(255,255,255,0.4);
        }

        /* Content Sections */
        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .section-header {
            margin-bottom: 24px;
        }

        .section-header h2 {
            margin: 0 0 8px 0;
            font-size: 1.8rem;
            color: #1e293b;
        }

        .section-header p {
            margin: 0;
            color: #64748b;
            font-size: 1rem;
        }

        /* Scenario Grid */
        .scenario-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }

        /* Scenario Card */
        .scenario-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
        }

        .scenario-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }

        .scenario-card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: white;
        }

        .scenario-category {
            display: inline-block;
            background: rgba(255,255,255,0.3);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .scenario-card h3 {
            margin: 0 0 8px 0;
            font-size: 1.3rem;
            line-height: 1.3;
        }

        .scenario-difficulty {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .difficulty-beginner {
            background: rgba(34, 197, 94, 0.2);
            color: #15803d;
        }

        .difficulty-intermediate {
            background: rgba(234, 179, 8, 0.2);
            color: #a16207;
        }

        .difficulty-advanced {
            background: rgba(239, 68, 68, 0.2);
            color: #b91c1c;
        }

        .scenario-card-body {
            padding: 20px;
        }

        .scenario-description {
            color: #64748b;
            margin-bottom: 16px;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .scenario-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
        }

        .scenario-rating {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            color: #f59e0b;
        }

        .scenario-rating .stars {
            font-size: 1.1rem;
        }

        .scenario-rating .count {
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 400;
        }

        .scenario-stats {
            display: flex;
            gap: 16px;
            font-size: 0.9rem;
            color: #64748b;
        }

        .scenario-stats .stat {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .scenario-actions {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }

        .scenario-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
        }

        .btn-secondary {
            background: #f1f5f9;
            color: #475569;
        }

        .btn-secondary:hover {
            background: #e2e8f0;
        }

        .bookmark-btn {
            padding: 10px 16px;
            background: #f1f5f9;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1.2rem;
        }

        .bookmark-btn:hover {
            background: #e2e8f0;
        }

        .bookmark-btn.bookmarked {
            background: #fef3c7;
            color: #f59e0b;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        .empty-state h3 {
            margin: 0 0 8px 0;
            color: #1e293b;
        }

        .empty-state p {
            margin: 0;
            color: #64748b;
        }

        /* Loading State */
        .loading-spinner {
            text-align: center;
            padding: 40px;
        }

        .spinner {
            border: 4px solid #f1f5f9;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 48px;
            height: 48px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Collections Section */
        .collection-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            transition: all 0.3s;
            cursor: pointer;
        }

        .collection-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }

        .collection-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
        }

        .collection-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }

        .collection-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .collection-description {
            color: #64748b;
            margin-bottom: 16px;
            line-height: 1.6;
        }

        .collection-meta {
            display: flex;
            gap: 16px;
            font-size: 0.9rem;
            color: #64748b;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
        }

        /* Trending Badge */
        .trending-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            background: linear-gradient(135deg, #f59e0b 0%, #dc2626 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 4px;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
        }

        .trending-badge::before {
            content: "🔥";
        }

        /* Responsive */
        @media (max-width: 768px) {
            .discovery-header h1 {
                font-size: 2rem;
            }

            .discovery-tabs {
                flex-direction: column;
            }

            .discovery-tab {
                padding: 16px;
            }

            .scenario-grid {
                grid-template-columns: 1fr;
            }

            .search-box {
                flex-direction: column;
            }

            .search-filters {
                flex-direction: column;
            }
        }
    """)


def create_scenario_card(scenario: Dict, show_trending: bool = False) -> Div:
    """
    Create a scenario card component.

    Args:
        scenario: Scenario data dictionary
        show_trending: Whether to show trending badge

    Returns:
        Div containing scenario card
    """
    # Extract scenario data
    title = scenario.get("title", "Untitled Scenario")
    description = scenario.get("description", "No description available")
    category = scenario.get("category", "general").title()
    difficulty = scenario.get("difficulty", "intermediate")
    scenario_id = scenario.get("scenario_id", "")

    # Rating data
    rating_data = scenario.get("rating", {})
    avg_rating = rating_data.get("average", 0.0)
    rating_count = rating_data.get("count", 0)

    # Stats
    completion_count = scenario.get("completion_count", 0)
    duration = scenario.get("estimated_duration", 20)

    # Generate star display
    stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))

    card_content = [
        # Trending badge (if applicable)
        Div(
            "TRENDING",
            cls="trending-badge",
            style="display: none;" if not show_trending else "",
        ),
        # Card header
        Div(
            Span(category, cls="scenario-category"),
            H3(title),
            Span(
                difficulty.title(), cls=f"scenario-difficulty difficulty-{difficulty}"
            ),
            cls="scenario-card-header",
        ),
        # Card body
        Div(
            P(description, cls="scenario-description"),
            # Meta information
            Div(
                Div(
                    Span(stars, cls="stars"),
                    Span(f"{avg_rating:.1f}", style="margin-left: 4px;"),
                    Span(f"({rating_count})", cls="count") if rating_count > 0 else "",
                    cls="scenario-rating",
                ),
                Div(
                    Div(Span("⏱️"), Span(f"{duration} min"), cls="stat"),
                    Div(Span("✓"), Span(f"{completion_count}"), cls="stat"),
                    cls="scenario-stats",
                ),
                cls="scenario-meta",
            ),
            # Actions
            Div(
                Button(
                    "View Details",
                    cls="scenario-btn btn-primary",
                    onclick=f"viewScenario('{scenario_id}')",
                ),
                Button(
                    "Start",
                    cls="scenario-btn btn-secondary",
                    onclick=f"startScenario('{scenario_id}')",
                ),
                Button(
                    "🔖",
                    cls="bookmark-btn",
                    id=f"bookmark-{scenario_id}",
                    onclick=f"toggleBookmark('{scenario_id}')",
                ),
                cls="scenario-actions",
            ),
            cls="scenario-card-body",
        ),
    ]

    return Div(*card_content, cls="scenario-card", **{"data-scenario-id": scenario_id})


def create_collection_card(collection: Dict) -> Div:
    """
    Create a collection card component.

    Args:
        collection: Collection data dictionary

    Returns:
        Div containing collection card
    """
    name = collection.get("name", "Untitled Collection")
    description = collection.get("description", "No description")
    item_count = collection.get("item_count", 0)
    is_learning_path = collection.get("is_learning_path", False)
    collection_id = collection.get("collection_id", "")

    return Div(
        Div(
            H3(name, cls="collection-title"),
            Span(
                "Learning Path" if is_learning_path else "Collection",
                cls="collection-badge",
            ),
            cls="collection-header",
        ),
        P(description, cls="collection-description"),
        Div(
            Span(f"📚 {item_count} scenarios"),
            Span(f"👤 By {collection.get('creator', 'Unknown')}"),
            cls="collection-meta",
        ),
        cls="collection-card",
        onclick=f"viewCollection('{collection_id}')",
    )


def create_discovery_hub_route():
    """
    Create the discovery hub route handler.

    Returns:
        Route handler function
    """

    @require_auth
    def discovery_hub_page(current_user: SimpleUser):
        """Discovery hub page handler"""

        # Create tabs
        tabs = Div(
            Button("🔍 Search", cls="discovery-tab active", **{"data-tab": "search"}),
            Button("🔥 Trending", cls="discovery-tab", **{"data-tab": "trending"}),
            Button("⭐ Top Rated", cls="discovery-tab", **{"data-tab": "top-rated"}),
            Button("📈 Popular", cls="discovery-tab", **{"data-tab": "popular"}),
            Button("💡 For You", cls="discovery-tab", **{"data-tab": "recommended"}),
            Button(
                "📚 Collections", cls="discovery-tab", **{"data-tab": "collections"}
            ),
            cls="discovery-tabs",
        )

        # Search tab content
        search_content = Div(
            Div(
                H2("Search Scenarios"),
                P("Find the perfect scenario for your learning goals"),
                cls="section-header",
            ),
            Div(
                Div(
                    Input(
                        type="text",
                        placeholder="Search scenarios by title, description, or tags...",
                        cls="search-input",
                        id="search-query",
                    ),
                    Button("Search", cls="search-btn", onclick="performSearch()"),
                    cls="search-box",
                ),
                Div(
                    Select(
                        Option("All Categories", value=""),
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
                        cls="filter-select",
                        id="filter-category",
                    ),
                    Select(
                        Option("All Levels", value=""),
                        Option("Beginner", value="beginner"),
                        Option("Intermediate", value="intermediate"),
                        Option("Advanced", value="advanced"),
                        cls="filter-select",
                        id="filter-difficulty",
                    ),
                    Select(
                        Option("Any Rating", value=""),
                        Option("4+ Stars", value="4"),
                        Option("3+ Stars", value="3"),
                        cls="filter-select",
                        id="filter-rating",
                    ),
                    cls="search-filters",
                ),
                cls="search-section",
            ),
            # Results container
            Div(id="search-results", cls="scenario-grid"),
            cls="tab-content active",
            id="tab-search",
        )

        # Trending tab
        trending_content = Div(
            Div(
                H2("Trending Scenarios"),
                P("Most popular scenarios right now based on recent activity"),
                cls="section-header",
            ),
            Div(id="trending-results", cls="scenario-grid"),
            cls="tab-content",
            id="tab-trending",
        )

        # Top rated tab
        top_rated_content = Div(
            Div(
                H2("Top Rated Scenarios"),
                P("Highest rated scenarios by the community"),
                cls="section-header",
            ),
            Div(id="top-rated-results", cls="scenario-grid"),
            cls="tab-content",
            id="tab-top-rated",
        )

        # Popular tab
        popular_content = Div(
            Div(
                H2("Most Popular Scenarios"),
                P("Most completed scenarios of all time"),
                cls="section-header",
            ),
            Div(id="popular-results", cls="scenario-grid"),
            cls="tab-content",
            id="tab-popular",
        )

        # Recommended tab
        recommended_content = Div(
            Div(
                H2("Recommended For You"),
                P("Personalized scenario recommendations based on your learning"),
                cls="section-header",
            ),
            Div(id="recommended-results", cls="scenario-grid"),
            cls="tab-content",
            id="tab-recommended",
        )

        # Collections tab
        collections_content = Div(
            Div(
                H2("Public Collections"),
                P("Curated scenario collections from the community"),
                cls="section-header",
            ),
            Div(id="collections-results", cls="scenario-grid"),
            cls="tab-content",
            id="tab-collections",
        )

        # JavaScript for interactivity
        discovery_script = Script("""
            // Tab switching
            document.querySelectorAll('.discovery-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    // Update active tab
                    document.querySelectorAll('.discovery-tab').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');

                    // Show corresponding content
                    const tabName = this.dataset.tab;
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                    document.getElementById(`tab-${tabName}`).classList.add('active');

                    // Load data for tab
                    loadTabData(tabName);
                });
            });

            // Load initial data for search tab
            loadTabData('search');

            async function loadTabData(tabName) {
                const container = document.getElementById(`${tabName}-results`);
                if (!container) return;

                // Show loading
                container.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Loading...</p></div>';

                try {
                    let url;
                    switch(tabName) {
                        case 'trending':
                            url = '/api/v1/scenario-organization/trending?limit=12';
                            break;
                        case 'top-rated':
                            url = '/api/v1/scenario-organization/trending?limit=12';  // Will use top-rated endpoint
                            break;
                        case 'popular':
                            url = '/api/v1/scenario-organization/popular?limit=12';
                            break;
                        case 'recommended':
                            url = '/api/v1/scenario-organization/recommended?limit=12';
                            break;
                        case 'collections':
                            url = '/api/v1/scenario-organization/public-collections?limit=12';
                            break;
                        case 'search':
                            // Initial load shows trending
                            url = '/api/v1/scenario-organization/trending?limit=12';
                            break;
                        default:
                            return;
                    }

                    const response = await fetch(url);
                    const data = await response.json();

                    if (data.success) {
                        renderResults(container, data, tabName);
                    } else {
                        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📭</div><h3>No Results Found</h3><p>Try adjusting your filters or search terms</p></div>';
                    }
                } catch (error) {
                    console.error('Error loading data:', error);
                    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Error Loading Data</h3><p>Please try again later</p></div>';
                }
            }

            function renderResults(container, data, tabName) {
                container.innerHTML = '';

                if (tabName === 'collections') {
                    const collections = data.collections || [];
                    if (collections.length === 0) {
                        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📚</div><h3>No Collections Yet</h3><p>Public collections will appear here</p></div>';
                        return;
                    }
                    // Render collections (would need server-side rendering or JS template)
                } else {
                    const scenarios = data.scenarios || [];
                    if (scenarios.length === 0) {
                        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔍</div><h3>No Scenarios Found</h3><p>Try different filters or search terms</p></div>';
                        return;
                    }
                    // Render scenarios (would need server-side rendering or JS template)
                }
            }

            async function performSearch() {
                const query = document.getElementById('search-query').value;
                const category = document.getElementById('filter-category').value;
                const difficulty = document.getElementById('filter-difficulty').value;
                const minRating = document.getElementById('filter-rating').value;

                const container = document.getElementById('search-results');
                container.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Searching...</p></div>';

                try {
                    const params = new URLSearchParams();
                    if (query) params.append('q', query);
                    if (category) params.append('category', category);
                    if (difficulty) params.append('difficulty', difficulty);
                    if (minRating) params.append('min_rating', minRating);
                    params.append('limit', '20');

                    const url = `/api/v1/scenario-organization/search?${params.toString()}`;
                    const response = await fetch(url);
                    const data = await response.json();

                    if (data.success && data.scenarios && data.scenarios.length > 0) {
                        renderResults(container, data, 'search');
                    } else {
                        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔍</div><h3>No Results Found</h3><p>Try different search terms or filters</p></div>';
                    }
                } catch (error) {
                    console.error('Search error:', error);
                    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Search Error</h3><p>Please try again</p></div>';
                }
            }

            async function toggleBookmark(scenarioId) {
                const btn = document.getElementById(`bookmark-${scenarioId}`);
                const isBookmarked = btn.classList.contains('bookmarked');

                try {
                    if (isBookmarked) {
                        await fetch(`/api/v1/scenario-organization/bookmarks/${scenarioId}`, {
                            method: 'DELETE'
                        });
                        btn.classList.remove('bookmarked');
                        btn.textContent = '🔖';
                    } else {
                        await fetch(`/api/v1/scenario-organization/bookmarks?scenario_id=${scenarioId}`, {
                            method: 'POST'
                        });
                        btn.classList.add('bookmarked');
                        btn.textContent = '📌';
                    }
                } catch (error) {
                    console.error('Bookmark error:', error);
                }
            }

            function viewScenario(scenarioId) {
                window.location.href = `/scenarios/${scenarioId}`;
            }

            function startScenario(scenarioId) {
                window.location.href = `/chat?scenario=${scenarioId}`;
            }

            function viewCollection(collectionId) {
                window.location.href = `/collections/${collectionId}`;
            }
        """)

        # Main page structure
        page_content = Div(
            discovery_hub_styles(),
            Div(
                H1("🔍 Discover Scenarios"),
                P(
                    "Explore thousands of conversation scenarios to enhance your language learning"
                ),
                cls="discovery-header",
            ),
            tabs,
            search_content,
            trending_content,
            top_rated_content,
            popular_content,
            recommended_content,
            collections_content,
            discovery_script,
            cls="discovery-container",
        )

        return page_content

    return discovery_hub_page
