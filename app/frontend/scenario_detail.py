"""
Scenario Detail Page
AI Language Tutor App - Session 133

Detailed view of individual scenarios with:
- Full scenario information
- Rating and review system
- Bookmark functionality
- Add to collection
- User tags
- Related scenarios
"""

import logging
from typing import Optional

from fastapi import Depends
from fasthtml.common import *

from app.core.security import require_auth
from app.database.config import get_db_session
from app.models.simple_user import SimpleUser
from app.services.scenario_organization_service import ScenarioOrganizationService

logger = logging.getLogger(__name__)


def scenario_detail_styles():
    """CSS styles for scenario detail page"""
    return Style("""
        .detail-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .detail-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 16px;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        }

        .detail-header h1 {
            margin: 0 0 12px 0;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .detail-header .category-badge {
            display: inline-block;
            background: rgba(255,255,255,0.3);
            padding: 6px 16px;
            border-radius: 16px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-right: 12px;
            text-transform: uppercase;
        }

        .detail-header .difficulty-badge {
            display: inline-block;
            background: rgba(255,255,255,0.3);
            padding: 6px 16px;
            border-radius: 16px;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .detail-header p {
            margin: 16px 0 0 0;
            opacity: 0.95;
            font-size: 1.1rem;
            line-height: 1.6;
        }

        .detail-actions {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .action-btn {
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }

        .action-btn.primary {
            background: white;
            color: #667eea;
        }

        .action-btn.primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,255,255,0.3);
        }

        .action-btn.secondary {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.5);
        }

        .action-btn.secondary:hover {
            background: rgba(255,255,255,0.3);
        }

        .detail-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }

        .detail-main {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }

        .detail-sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .sidebar-card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }

        .sidebar-card h3 {
            margin: 0 0 16px 0;
            font-size: 1.2rem;
            color: #1e293b;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .stat-item {
            text-align: center;
            padding: 16px;
            background: #f8fafc;
            border-radius: 8px;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #667eea;
            display: block;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #64748b;
            margin-top: 4px;
        }

        .rating-summary {
            margin-bottom: 24px;
        }

        .rating-stars {
            font-size: 2rem;
            color: #fbbf24;
            margin-bottom: 8px;
        }

        .rating-text {
            font-size: 1.1rem;
            color: #64748b;
        }

        .phase-list {
            margin-top: 24px;
        }

        .phase-item {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 16px;
            border-left: 4px solid #667eea;
        }

        .phase-item h4 {
            margin: 0 0 8px 0;
            color: #1e293b;
            font-size: 1.1rem;
        }

        .phase-item p {
            margin: 0 0 12px 0;
            color: #64748b;
            line-height: 1.6;
        }

        .vocabulary-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }

        .vocabulary-tag {
            background: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #667eea;
            border: 1px solid #e2e8f0;
        }

        .review-form {
            background: #f8fafc;
            padding: 24px;
            border-radius: 12px;
            margin-top: 30px;
        }

        .review-form h3 {
            margin: 0 0 20px 0;
            color: #1e293b;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #1e293b;
        }

        .star-rating {
            display: flex;
            gap: 8px;
            font-size: 2rem;
        }

        .star-rating .star {
            cursor: pointer;
            color: #cbd5e1;
            transition: color 0.2s;
        }

        .star-rating .star.active,
        .star-rating .star:hover {
            color: #fbbf24;
        }

        .form-textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            resize: vertical;
            min-height: 120px;
        }

        .form-textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .submit-btn {
            padding: 12px 32px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .submit-btn:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }

        .reviews-list {
            margin-top: 30px;
        }

        .review-item {
            background: white;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        .review-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .review-author {
            font-weight: 600;
            color: #1e293b;
        }

        .review-date {
            color: #94a3b8;
            font-size: 0.9rem;
        }

        .review-rating {
            color: #fbbf24;
            font-size: 1.2rem;
            margin-bottom: 8px;
        }

        .review-text {
            color: #64748b;
            line-height: 1.6;
        }

        .tags-section {
            margin-top: 24px;
        }

        .tag-input-group {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }

        .tag-input {
            flex: 1;
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.95rem;
        }

        .tag-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .add-tag-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }

        .tags-display {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .tag-badge {
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .tag-badge.ai-tag {
            background: #8b5cf6;
        }

        .tag-remove {
            cursor: pointer;
            font-weight: bold;
        }

        .collections-dropdown {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            margin-bottom: 12px;
        }

        @media (max-width: 768px) {
            .detail-content {
                grid-template-columns: 1fr;
            }

            .stat-grid {
                grid-template-columns: 1fr;
            }
        }
    """)


def create_scenario_detail_route():
    """Create scenario detail route handler"""

    async def scenario_detail(
        scenario_id: str, current_user: SimpleUser = Depends(require_auth)
    ):
        """Render scenario detail page"""
        db = next(get_db_session())
        service = ScenarioOrganizationService(db)

        try:
            # Get scenario data (this will need to integrate with scenario manager)
            # For now, we'll create a placeholder that fetches from the organization service

            # Get rating summary
            rating_summary = await service.get_scenario_rating_summary(scenario_id)

            # Get user's rating if exists
            user_rating = await service.get_user_rating(current_user.id, scenario_id)

            # Get scenario tags
            tags_data = await service.get_scenario_tags(scenario_id)
            user_tags = [t for t in tags_data if t.get("tag_type") == "user"]
            ai_tags = [t for t in tags_data if t.get("tag_type") == "ai"]

            # Check if bookmarked
            is_bookmarked = await service.is_bookmarked(current_user.id, scenario_id)

            # Get user's collections for "Add to Collection" dropdown
            user_collections = await service.get_user_collections(current_user.id)

            # Get reviews
            reviews = await service.get_scenario_ratings(
                scenario_id, public_only=True, limit=10
            )

            return Html(
                Head(
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1"
                    ),
                    Title(f"Scenario Details - AI Language Tutor"),
                    scenario_detail_styles(),
                ),
                Body(
                    Div(
                        # Header
                        Div(
                            Div(
                                Span("Category", cls="category-badge"),
                                Span("Difficulty", cls="difficulty-badge"),
                                cls="badges",
                            ),
                            H1(f"Scenario Title", id="scenario-title"),
                            P(
                                "Scenario description will load here...",
                                id="scenario-description",
                            ),
                            Div(
                                Button(
                                    "Start Scenario",
                                    cls="action-btn primary",
                                    onclick=f"startScenario('{scenario_id}')",
                                ),
                                Button(
                                    "🔖 Bookmark"
                                    if not is_bookmarked
                                    else "📌 Bookmarked",
                                    cls="action-btn secondary",
                                    id="bookmark-btn",
                                    onclick=f"toggleBookmark('{scenario_id}')",
                                ),
                                Button(
                                    "➕ Add to Collection",
                                    cls="action-btn secondary",
                                    onclick="showCollectionModal()",
                                ),
                                cls="detail-actions",
                            ),
                            cls="detail-header",
                        ),
                        # Main content
                        Div(
                            # Left column - Scenario details
                            Div(
                                # Overview section
                                Div(
                                    H2("Overview"),
                                    P(
                                        "Detailed scenario information will load here...",
                                        id="scenario-overview",
                                    ),
                                    cls="section",
                                ),
                                # Phases section
                                Div(
                                    H2("Learning Phases"),
                                    Div(id="phases-container", cls="phase-list"),
                                    cls="section",
                                ),
                                # Rating and Review section
                                Div(
                                    H2("Rate This Scenario"),
                                    Div(
                                        H3("Your Rating"),
                                        Div(
                                            Label("Overall Rating", cls="form-label"),
                                            Div(
                                                *[
                                                    Span(
                                                        "★",
                                                        cls="star",
                                                        id=f"star-{i}",
                                                        onclick=f"setRating({i})",
                                                    )
                                                    for i in range(1, 6)
                                                ],
                                                cls="star-rating",
                                                id="star-rating",
                                            ),
                                            cls="form-group",
                                        ),
                                        Div(
                                            Label(
                                                "Your Review (Optional)",
                                                cls="form-label",
                                            ),
                                            Textarea(
                                                placeholder="Share your experience with this scenario...",
                                                cls="form-textarea",
                                                id="review-text",
                                            ),
                                            cls="form-group",
                                        ),
                                        Div(
                                            Button(
                                                "Submit Rating",
                                                cls="submit-btn",
                                                onclick=f"submitRating('{scenario_id}')",
                                            ),
                                        ),
                                        cls="review-form",
                                    ),
                                    cls="section",
                                ),
                                # Reviews list
                                Div(
                                    H2(
                                        f"Reviews ({rating_summary.get('total_ratings', 0)})"
                                    ),
                                    Div(
                                        *[
                                            create_review_item(review)
                                            for review in reviews
                                        ],
                                        cls="reviews-list",
                                        id="reviews-container",
                                    ),
                                    cls="section",
                                ),
                                cls="detail-main",
                            ),
                            # Right column - Sidebar
                            Div(
                                # Stats card
                                Div(
                                    H3("Statistics"),
                                    Div(
                                        Div(
                                            Span(
                                                f"{rating_summary.get('average_rating', 0):.1f}",
                                                cls="stat-value",
                                            ),
                                            Span("Avg Rating", cls="stat-label"),
                                            cls="stat-item",
                                        ),
                                        Div(
                                            Span(
                                                f"{rating_summary.get('total_ratings', 0)}",
                                                cls="stat-value",
                                            ),
                                            Span("Reviews", cls="stat-label"),
                                            cls="stat-item",
                                        ),
                                        Div(
                                            Span(
                                                "0",
                                                cls="stat-value",
                                                id="completion-count",
                                            ),
                                            Span("Completions", cls="stat-label"),
                                            cls="stat-item",
                                        ),
                                        Div(
                                            Span("20", cls="stat-value", id="duration"),
                                            Span("Minutes", cls="stat-label"),
                                            cls="stat-item",
                                        ),
                                        cls="stat-grid",
                                    ),
                                    cls="sidebar-card",
                                ),
                                # Tags card
                                Div(
                                    H3("Tags"),
                                    Div(
                                        Input(
                                            type="text",
                                            placeholder="Add a tag...",
                                            cls="tag-input",
                                            id="tag-input",
                                        ),
                                        Button(
                                            "Add",
                                            cls="add-tag-btn",
                                            onclick=f"addTag('{scenario_id}')",
                                        ),
                                        cls="tag-input-group",
                                    ),
                                    Div(
                                        *[
                                            Span(
                                                tag.get("tag"),
                                                Span(
                                                    "×",
                                                    cls="tag-remove",
                                                    onclick=f"removeTag('{tag.get('id')}')",
                                                ),
                                                cls="tag-badge",
                                            )
                                            for tag in user_tags
                                        ],
                                        *[
                                            Span(
                                                f"🤖 {tag.get('tag')}",
                                                cls="tag-badge ai-tag",
                                            )
                                            for tag in ai_tags
                                        ],
                                        cls="tags-display",
                                        id="tags-container",
                                    ),
                                    cls="sidebar-card tags-section",
                                ),
                                cls="detail-sidebar",
                            ),
                            cls="detail-content",
                        ),
                        cls="detail-container",
                    ),
                    # Collection modal
                    create_collection_modal(user_collections, scenario_id),
                    # JavaScript
                    create_scenario_detail_scripts(
                        scenario_id, current_user.id, is_bookmarked
                    ),
                ),
            )

        except Exception as e:
            logger.error(f"Error loading scenario detail: {e}")
            return Div(
                H1("Error Loading Scenario"),
                P(f"Unable to load scenario details: {str(e)}"),
            )

    return scenario_detail


def create_review_item(review: dict) -> Div:
    """Create a review item component"""
    stars = "★" * int(review.get("rating", 0)) + "☆" * (
        5 - int(review.get("rating", 0))
    )

    return Div(
        Div(
            Span(review.get("user_name", "Anonymous"), cls="review-author"),
            Span(review.get("created_at", ""), cls="review-date"),
            cls="review-header",
        ),
        Div(stars, cls="review-rating"),
        P(review.get("review", ""), cls="review-text")
        if review.get("review")
        else None,
        cls="review-item",
    )


def create_collection_modal(collections: list, scenario_id: str) -> Div:
    """Create modal for adding scenario to collection"""
    return Div(
        Div(
            Div(
                H3("Add to Collection"),
                Div(
                    Select(
                        *[
                            Option(c.get("name"), value=c.get("id"))
                            for c in collections
                        ],
                        cls="collections-dropdown",
                        id="collection-select",
                    ),
                    Div(
                        Button(
                            "Cancel",
                            cls="action-btn secondary",
                            onclick="hideCollectionModal()",
                        ),
                        Button(
                            "Add",
                            cls="action-btn primary",
                            onclick=f"addToCollection('{scenario_id}')",
                        ),
                        style="display: flex; gap: 12px; justify-content: flex-end;",
                    ),
                ),
            ),
            style="background: white; padding: 30px; border-radius: 12px; max-width: 400px; margin: 100px auto;",
        ),
        id="collection-modal",
        style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;",
    )


def create_scenario_detail_scripts(
    scenario_id: str, user_id: int, is_bookmarked: bool
) -> Script:
    """Create JavaScript for scenario detail page"""
    return Script(f"""
        let currentRating = 0;
        let isBookmarked = {str(is_bookmarked).lower()};

        // Load scenario data on page load
        document.addEventListener('DOMContentLoaded', async function() {{
            await loadScenarioData('{scenario_id}');
        }});

        async function loadScenarioData(scenarioId) {{
            try {{
                // Fetch scenario data from scenarios API
                const response = await fetch(`/api/v1/scenarios/${{scenarioId}}`);
                if (response.ok) {{
                    const scenario = await response.json();

                    // Update page with scenario data
                    document.getElementById('scenario-title').textContent = scenario.title;
                    document.getElementById('scenario-description').textContent = scenario.description;
                    document.getElementById('scenario-overview').textContent = scenario.setting || scenario.description;

                    // Update badges
                    document.querySelector('.category-badge').textContent = scenario.category;
                    document.querySelector('.difficulty-badge').textContent = scenario.difficulty;

                    // Update stats
                    document.getElementById('duration').textContent = scenario.estimated_duration || '20';

                    // Load phases
                    if (scenario.phases) {{
                        const phasesContainer = document.getElementById('phases-container');
                        phasesContainer.innerHTML = '';

                        scenario.phases.forEach((phase, index) => {{
                            const phaseEl = createPhaseElement(phase, index + 1);
                            phasesContainer.appendChild(phaseEl);
                        }});
                    }}
                }}
            }} catch (error) {{
                console.error('Error loading scenario:', error);
            }}
        }}

        function createPhaseElement(phase, number) {{
            const div = document.createElement('div');
            div.className = 'phase-item';

            let vocabHtml = '';
            if (phase.key_vocabulary && phase.key_vocabulary.length > 0) {{
                vocabHtml = '<div class="vocabulary-list">' +
                    phase.key_vocabulary.map(word => `<span class="vocabulary-tag">${{word}}</span>`).join('') +
                    '</div>';
            }}

            div.innerHTML = `
                <h4>Phase ${{number}}: ${{phase.name}}</h4>
                <p>${{phase.description}}</p>
                ${{vocabHtml}}
            `;

            return div;
        }}

        function setRating(rating) {{
            currentRating = rating;

            for (let i = 1; i <= 5; i++) {{
                const star = document.getElementById(`star-${{i}}`);
                if (i <= rating) {{
                    star.classList.add('active');
                }} else {{
                    star.classList.remove('active');
                }}
            }}
        }}

        async function submitRating(scenarioId) {{
            if (currentRating === 0) {{
                alert('Please select a rating');
                return;
            }}

            const review = document.getElementById('review-text').value;

            try {{
                const response = await fetch('/api/v1/scenario-organization/ratings', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        scenario_id: scenarioId,
                        rating: currentRating,
                        review: review || null,
                        is_public: true
                    }})
                }});

                if (response.ok) {{
                    alert('Rating submitted successfully!');
                    location.reload();
                }} else {{
                    alert('Failed to submit rating');
                }}
            }} catch (error) {{
                console.error('Error submitting rating:', error);
                alert('Error submitting rating');
            }}
        }}

        async function toggleBookmark(scenarioId) {{
            try {{
                if (isBookmarked) {{
                    await fetch(`/api/v1/scenario-organization/bookmarks/${{scenarioId}}`, {{
                        method: 'DELETE'
                    }});
                    isBookmarked = false;
                    document.getElementById('bookmark-btn').textContent = '🔖 Bookmark';
                }} else {{
                    await fetch(`/api/v1/scenario-organization/bookmarks?scenario_id=${{scenarioId}}`, {{
                        method: 'POST'
                    }});
                    isBookmarked = true;
                    document.getElementById('bookmark-btn').textContent = '📌 Bookmarked';
                }}
            }} catch (error) {{
                console.error('Bookmark error:', error);
            }}
        }}

        async function addTag(scenarioId) {{
            const input = document.getElementById('tag-input');
            const tag = input.value.trim();

            if (!tag) return;

            try {{
                const response = await fetch(`/api/v1/scenario-organization/scenarios/${{scenarioId}}/tags`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ tag: tag }})
                }});

                if (response.ok) {{
                    location.reload();
                }}
            }} catch (error) {{
                console.error('Error adding tag:', error);
            }}
        }}

        async function removeTag(tagId) {{
            // Implementation depends on API endpoint for tag removal
            console.log('Remove tag:', tagId);
        }}

        function showCollectionModal() {{
            document.getElementById('collection-modal').style.display = 'block';
        }}

        function hideCollectionModal() {{
            document.getElementById('collection-modal').style.display = 'none';
        }}

        async function addToCollection(scenarioId) {{
            const collectionId = document.getElementById('collection-select').value;

            if (!collectionId) {{
                alert('Please select a collection');
                return;
            }}

            try {{
                const response = await fetch(`/api/v1/scenario-organization/collections/${{collectionId}}/scenarios`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ scenario_id: scenarioId }})
                }});

                if (response.ok) {{
                    alert('Added to collection!');
                    hideCollectionModal();
                }} else {{
                    alert('Failed to add to collection');
                }}
            }} catch (error) {{
                console.error('Error adding to collection:', error);
            }}
        }}

        function startScenario(scenarioId) {{
            window.location.href = `/chat?scenario=${{scenarioId}}`;
        }}
    """)
