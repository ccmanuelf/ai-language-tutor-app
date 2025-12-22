"""
Scenario Organization API Endpoints
AI Language Tutor App - Session 133

RESTful API for scenario organization, discovery, and engagement.
Provides endpoints for collections, tagging, bookmarks, ratings, and discovery.

Endpoints Overview:
- Collections: 8 endpoints (create, read, update, delete, add/remove items, reorder)
- Tags: 4 endpoints (add user tag, add AI tags, get tags, search by tag)
- Bookmarks: 5 endpoints (add, remove, get user bookmarks, get folders, check if bookmarked)
- Ratings: 5 endpoints (add, get ratings, get user rating, delete, mark helpful)
- Discovery: 5 endpoints (search, trending, popular, recommended, discovery hub)

Total: 27 endpoints
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import require_auth
from app.database.config import get_db_session
from app.models.simple_user import SimpleUser
from app.services.scenario_organization_service import ScenarioOrganizationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/scenario-organization", tags=["Scenario Organization"]
)


# ============================================================================
# COLLECTIONS ENDPOINTS (8)
# ============================================================================


@router.post("/collections")
async def create_collection(
    name: str = Query(..., min_length=3, max_length=255),
    description: Optional[str] = Query(None, max_length=1000),
    is_public: bool = Query(False),
    is_learning_path: bool = Query(False),
    category: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Create a new scenario collection or learning path.

    Args:
        name: Collection name (3-255 characters)
        description: Optional description
        is_public: Whether collection is publicly visible
        is_learning_path: If true, scenarios have ordered progression
        category: Optional category filter
        difficulty_level: Optional difficulty level (beginner/intermediate/advanced)

    Returns:
        Created collection details
    """
    try:
        service = ScenarioOrganizationService(db)
        collection = await service.create_collection(
            user_id=current_user.id,
            name=name,
            description=description,
            is_public=is_public,
            is_learning_path=is_learning_path,
            category=category,
            difficulty_level=difficulty_level,
        )

        return {
            "success": True,
            "collection": collection.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to create collection")


@router.get("/collections/{collection_id}")
async def get_collection(
    collection_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get collection details with all scenarios.

    Args:
        collection_id: Collection identifier

    Returns:
        Collection details with items
    """
    try:
        service = ScenarioOrganizationService(db)
        collection = await service.get_collection(collection_id, current_user.id)

        if not collection:
            raise HTTPException(
                status_code=404,
                detail="Collection not found or you don't have access",
            )

        return {
            "success": True,
            "collection": collection.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collection")


@router.get("/collections")
async def get_user_collections(
    include_public: bool = Query(False),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get all collections for the current user.

    Args:
        include_public: If true, also include public collections

    Returns:
        List of collections
    """
    try:
        service = ScenarioOrganizationService(db)
        collections = await service.get_user_collections(
            user_id=current_user.id,
            include_public=include_public,
        )

        return {
            "success": True,
            "collections": [c.to_dict() for c in collections],
        }

    except Exception as e:
        logger.error(f"Error getting user collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collections")


@router.post("/collections/{collection_id}/scenarios")
async def add_scenario_to_collection(
    collection_id: str,
    scenario_id: int = Query(..., gt=0),
    notes: Optional[str] = Query(None, max_length=500),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Add a scenario to a collection.

    Args:
        collection_id: Collection identifier
        scenario_id: Scenario database ID to add
        notes: Optional notes about this scenario

    Returns:
        Created collection item
    """
    try:
        service = ScenarioOrganizationService(db)
        item = await service.add_scenario_to_collection(
            collection_id=collection_id,
            scenario_id=scenario_id,
            user_id=current_user.id,
            notes=notes,
        )

        return {
            "success": True,
            "item": item.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding scenario to collection: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to add scenario to collection"
        )


@router.delete("/collections/{collection_id}/scenarios/{scenario_id}")
async def remove_scenario_from_collection(
    collection_id: str,
    scenario_id: int,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Remove a scenario from a collection.

    Args:
        collection_id: Collection identifier
        scenario_id: Scenario database ID to remove

    Returns:
        Success status
    """
    try:
        service = ScenarioOrganizationService(db)
        success = await service.remove_scenario_from_collection(
            collection_id=collection_id,
            scenario_id=scenario_id,
            user_id=current_user.id,
        )

        return {
            "success": success,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing scenario from collection: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to remove scenario from collection"
        )


@router.put("/collections/{collection_id}/reorder")
async def reorder_collection(
    collection_id: str,
    scenario_order: List[int] = Query(..., description="Ordered list of scenario IDs"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Reorder scenarios in a collection (for learning paths).

    Args:
        collection_id: Collection identifier
        scenario_order: List of scenario IDs in desired order

    Returns:
        Success status
    """
    try:
        service = ScenarioOrganizationService(db)
        success = await service.reorder_collection(
            collection_id=collection_id,
            scenario_order=scenario_order,
            user_id=current_user.id,
        )

        return {
            "success": success,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error reordering collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to reorder collection")


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Delete a collection.

    Args:
        collection_id: Collection identifier

    Returns:
        Success status
    """
    try:
        service = ScenarioOrganizationService(db)
        success = await service.delete_collection(
            collection_id=collection_id,
            user_id=current_user.id,
        )

        return {
            "success": success,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete collection")


@router.get("/public-collections")
async def get_public_collections(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get publicly shared collections.

    Args:
        category: Optional category filter
        limit: Maximum number of results (1-100)

    Returns:
        List of public collections
    """
    try:
        service = ScenarioOrganizationService(db)
        collections = await service.get_user_collections(
            user_id=current_user.id,
            include_public=True,
        )

        # Filter by category if provided
        if category:
            collections = [c for c in collections if c.category == category]

        # Limit results
        collections = collections[:limit]

        return {
            "success": True,
            "collections": [c.to_dict() for c in collections],
        }

    except Exception as e:
        logger.error(f"Error getting public collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get public collections")


# ============================================================================
# TAGS ENDPOINTS (4)
# ============================================================================


@router.post("/scenarios/{scenario_id}/tags")
async def add_user_tag(
    scenario_id: int,
    tag: str = Query(..., min_length=2, max_length=50),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Add a user-generated tag to a scenario.

    Args:
        scenario_id: Scenario database ID
        tag: Tag text (2-50 characters)

    Returns:
        Created or updated tag
    """
    try:
        service = ScenarioOrganizationService(db)
        scenario_tag = await service.add_user_tag(
            scenario_id=scenario_id,
            tag=tag,
            user_id=current_user.id,
        )

        return {
            "success": True,
            "tag": scenario_tag.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding tag: {e}")
        raise HTTPException(status_code=500, detail="Failed to add tag")


@router.post("/scenarios/{scenario_id}/ai-tags")
async def add_ai_tags(
    scenario_id: int,
    tags: List[str] = Query(..., description="List of AI-generated tags"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Add AI-generated tags to a scenario.

    Args:
        scenario_id: Scenario database ID
        tags: List of AI-generated tags

    Returns:
        List of created tags

    Note: This endpoint is typically called internally by the AI service,
    but can be used by admins for manual tagging.
    """
    try:
        service = ScenarioOrganizationService(db)
        scenario_tags = await service.add_ai_tags(
            scenario_id=scenario_id,
            tags=tags,
        )

        return {
            "success": True,
            "tags": [tag.to_dict() for tag in scenario_tags],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding AI tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to add AI tags")


@router.get("/scenarios/{scenario_id}/tags")
async def get_scenario_tags(
    scenario_id: int,
    tag_type: Optional[str] = Query(None, pattern="^(user|ai)$"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get all tags for a scenario.

    Args:
        scenario_id: Scenario database ID
        tag_type: Optional filter for 'user' or 'ai' tags

    Returns:
        List of tags
    """
    try:
        service = ScenarioOrganizationService(db)
        tags = await service.get_scenario_tags(
            scenario_id=scenario_id,
            tag_type=tag_type,
        )

        return {
            "success": True,
            "tags": [tag.to_dict() for tag in tags],
        }

    except Exception as e:
        logger.error(f"Error getting scenario tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tags")


@router.get("/tags/search")
async def search_by_tag(
    tag: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Find scenarios by tag.

    Args:
        tag: Tag to search for
        limit: Maximum number of results (1-100)

    Returns:
        List of scenarios with this tag
    """
    try:
        service = ScenarioOrganizationService(db)
        scenarios = await service.search_by_tag(
            tag=tag,
            limit=limit,
        )

        return {
            "success": True,
            "scenarios": [s.to_dict() for s in scenarios],
        }

    except Exception as e:
        logger.error(f"Error searching by tag: {e}")
        raise HTTPException(status_code=500, detail="Failed to search by tag")


# ============================================================================
# BOOKMARKS ENDPOINTS (5)
# ============================================================================


@router.post("/bookmarks")
async def add_bookmark(
    scenario_id: int = Query(..., gt=0),
    folder: Optional[str] = Query(None, max_length=100),
    notes: Optional[str] = Query(None, max_length=500),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Bookmark a scenario.

    Args:
        scenario_id: Scenario database ID
        folder: Optional folder name for organization
        notes: Optional personal notes

    Returns:
        Created or updated bookmark
    """
    try:
        service = ScenarioOrganizationService(db)
        bookmark = await service.add_bookmark(
            user_id=current_user.id,
            scenario_id=scenario_id,
            folder=folder,
            notes=notes,
        )

        return {
            "success": True,
            "bookmark": bookmark.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding bookmark: {e}")
        raise HTTPException(status_code=500, detail="Failed to add bookmark")


@router.delete("/bookmarks/{scenario_id}")
async def remove_bookmark(
    scenario_id: int,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Remove a bookmark.

    Args:
        scenario_id: Scenario database ID

    Returns:
        Success status
    """
    try:
        service = ScenarioOrganizationService(db)
        success = await service.remove_bookmark(
            user_id=current_user.id,
            scenario_id=scenario_id,
        )

        return {
            "success": success,
        }

    except Exception as e:
        logger.error(f"Error removing bookmark: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove bookmark")


@router.get("/bookmarks")
async def get_user_bookmarks(
    folder: Optional[str] = Query(None),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get all bookmarks for the current user.

    Args:
        folder: Optional folder filter

    Returns:
        List of bookmarks with scenarios
    """
    try:
        service = ScenarioOrganizationService(db)
        bookmarks = await service.get_user_bookmarks(
            user_id=current_user.id,
            folder=folder,
        )

        return {
            "success": True,
            "bookmarks": [b.to_dict() for b in bookmarks],
        }

    except Exception as e:
        logger.error(f"Error getting bookmarks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bookmarks")


@router.get("/bookmarks/folders")
async def get_user_folders(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get all unique folder names for a user's bookmarks.

    Returns:
        List of folder names
    """
    try:
        service = ScenarioOrganizationService(db)
        folders = await service.get_user_folders(user_id=current_user.id)

        return {
            "success": True,
            "folders": folders,
        }

    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get folders")


@router.get("/bookmarks/{scenario_id}/check")
async def check_bookmark_status(
    scenario_id: int,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Check if a scenario is bookmarked by the current user.

    Args:
        scenario_id: Scenario database ID

    Returns:
        Bookmark status
    """
    try:
        service = ScenarioOrganizationService(db)
        is_bookmarked = await service.is_bookmarked(
            user_id=current_user.id,
            scenario_id=scenario_id,
        )

        return {
            "success": True,
            "is_bookmarked": is_bookmarked,
        }

    except Exception as e:
        logger.error(f"Error checking bookmark status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check bookmark status")


# ============================================================================
# RATINGS ENDPOINTS (5)
# ============================================================================


@router.post("/ratings")
async def add_rating(
    scenario_id: int = Query(..., gt=0),
    rating: int = Query(..., ge=1, le=5),
    review: Optional[str] = Query(None, max_length=2000),
    difficulty_rating: Optional[int] = Query(None, ge=1, le=5),
    usefulness_rating: Optional[int] = Query(None, ge=1, le=5),
    cultural_accuracy_rating: Optional[int] = Query(None, ge=1, le=5),
    is_public: bool = Query(True),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Add or update a rating/review for a scenario.

    Args:
        scenario_id: Scenario database ID
        rating: Overall rating (1-5 stars)
        review: Optional text review
        difficulty_rating: Optional difficulty rating (1-5)
        usefulness_rating: Optional usefulness rating (1-5)
        cultural_accuracy_rating: Optional cultural accuracy rating (1-5)
        is_public: Whether review is publicly visible

    Returns:
        Created or updated rating
    """
    try:
        service = ScenarioOrganizationService(db)
        scenario_rating = await service.add_rating(
            user_id=current_user.id,
            scenario_id=scenario_id,
            rating=rating,
            review=review,
            difficulty_rating=difficulty_rating,
            usefulness_rating=usefulness_rating,
            cultural_accuracy_rating=cultural_accuracy_rating,
            is_public=is_public,
        )

        return {
            "success": True,
            "rating": scenario_rating.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to add rating")


@router.get("/scenarios/{scenario_id}/ratings")
async def get_scenario_ratings(
    scenario_id: int,
    public_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get all ratings/reviews for a scenario.

    Args:
        scenario_id: Scenario database ID
        public_only: If true, only return public reviews
        limit: Maximum number of reviews (1-100)

    Returns:
        List of ratings/reviews
    """
    try:
        service = ScenarioOrganizationService(db)
        ratings = await service.get_scenario_ratings(
            scenario_id=scenario_id,
            public_only=public_only,
            limit=limit,
        )

        return {
            "success": True,
            "ratings": [r.to_dict() for r in ratings],
        }

    except Exception as e:
        logger.error(f"Error getting ratings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ratings")


@router.get("/scenarios/{scenario_id}/ratings/summary")
async def get_rating_summary(
    scenario_id: int,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get rating summary statistics for a scenario.

    Args:
        scenario_id: Scenario database ID

    Returns:
        Rating statistics including average, distribution, etc.
    """
    try:
        service = ScenarioOrganizationService(db)
        summary = await service.get_scenario_rating_summary(scenario_id=scenario_id)

        return {
            "success": True,
            "summary": summary,
        }

    except Exception as e:
        logger.error(f"Error getting rating summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rating summary")


@router.get("/ratings/my-rating/{scenario_id}")
async def get_user_rating(
    scenario_id: int,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get the current user's rating for a specific scenario.

    Args:
        scenario_id: Scenario database ID

    Returns:
        User's rating or null if not rated
    """
    try:
        service = ScenarioOrganizationService(db)
        rating = await service.get_user_rating(
            user_id=current_user.id,
            scenario_id=scenario_id,
        )

        return {
            "success": True,
            "rating": rating.to_dict() if rating else None,
        }

    except Exception as e:
        logger.error(f"Error getting user rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user rating")


@router.delete("/ratings/{scenario_id}")
async def delete_rating(
    scenario_id: int,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Delete the current user's rating.

    Args:
        scenario_id: Scenario database ID

    Returns:
        Success status
    """
    try:
        service = ScenarioOrganizationService(db)
        success = await service.delete_rating(
            user_id=current_user.id,
            scenario_id=scenario_id,
        )

        return {
            "success": success,
        }

    except Exception as e:
        logger.error(f"Error deleting rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete rating")


# ============================================================================
# DISCOVERY ENDPOINTS (5)
# ============================================================================


@router.get("/search")
async def search_scenarios(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(
        None, pattern="^(beginner|intermediate|advanced)$"
    ),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    limit: int = Query(20, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Search scenarios by text query and filters.

    Args:
        q: Search text (searches title, description, tags)
        category: Optional category filter
        difficulty: Optional difficulty filter (beginner/intermediate/advanced)
        min_rating: Optional minimum rating filter
        limit: Maximum number of results (1-100)

    Returns:
        List of matching scenarios
    """
    try:
        service = ScenarioOrganizationService(db)
        scenarios = await service.search_scenarios(
            query=q,
            category=category,
            difficulty=difficulty,
            min_rating=min_rating,
            limit=limit,
        )

        return {
            "success": True,
            "scenarios": [s.to_dict() for s in scenarios],
        }

    except Exception as e:
        logger.error(f"Error searching scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to search scenarios")


@router.get("/trending")
async def get_trending_scenarios(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get trending scenarios based on recent activity.

    Args:
        category: Optional category filter
        limit: Maximum number of results (1-100)

    Returns:
        List of trending scenarios with scores
    """
    try:
        service = ScenarioOrganizationService(db)
        results = await service.get_trending_scenarios(
            category=category,
            limit=limit,
        )

        return {
            "success": True,
            "scenarios": [
                {
                    "scenario": scenario.to_dict(),
                    "trending_score": score,
                }
                for scenario, score in results
            ],
        }

    except Exception as e:
        logger.error(f"Error getting trending scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending scenarios")


@router.get("/popular")
async def get_popular_scenarios(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get most popular scenarios by completion count.

    Args:
        category: Optional category filter
        limit: Maximum number of results (1-100)

    Returns:
        List of popular scenarios with completion counts
    """
    try:
        service = ScenarioOrganizationService(db)
        results = await service.get_popular_scenarios(
            category=category,
            limit=limit,
        )

        return {
            "success": True,
            "scenarios": [
                {
                    "scenario": scenario.to_dict(),
                    "completion_count": count,
                }
                for scenario, count in results
            ],
        }

    except Exception as e:
        logger.error(f"Error getting popular scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular scenarios")


@router.get("/recommended")
async def get_recommended_scenarios(
    limit: int = Query(10, ge=1, le=50),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get personalized scenario recommendations.

    Args:
        limit: Maximum number of results (1-50)

    Returns:
        List of recommended scenarios
    """
    try:
        service = ScenarioOrganizationService(db)
        scenarios = await service.get_recommended_scenarios(
            user_id=current_user.id,
            limit=limit,
        )

        return {
            "success": True,
            "scenarios": [s.to_dict() for s in scenarios],
        }

    except Exception as e:
        logger.error(f"Error getting recommended scenarios: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get recommended scenarios"
        )


@router.get("/discovery-hub")
async def get_discovery_hub(
    category: Optional[str] = Query(None),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get complete discovery hub data with multiple sections.

    Args:
        category: Optional category filter

    Returns:
        Discovery hub with trending, top-rated, popular, recommended, and recent collections
    """
    try:
        service = ScenarioOrganizationService(db)
        hub_data = await service.get_discovery_hub(
            user_id=current_user.id,
            category=category,
        )

        # Format the response
        formatted_hub = {
            "trending": [
                {
                    "scenario": scenario.to_dict(),
                    "trending_score": score,
                }
                for scenario, score in hub_data["trending"]
            ],
            "top_rated": [
                {
                    "scenario": scenario.to_dict(),
                    "average_rating": rating,
                }
                for scenario, rating in hub_data["top_rated"]
            ],
            "popular": [
                {
                    "scenario": scenario.to_dict(),
                    "completion_count": count,
                }
                for scenario, count in hub_data["popular"]
            ],
            "recommended": [s.to_dict() for s in hub_data.get("recommended", [])],
            "recent_collections": [c.to_dict() for c in hub_data["recent_collections"]],
        }

        return {
            "success": True,
            "hub": formatted_hub,
        }

    except Exception as e:
        logger.error(f"Error getting discovery hub: {e}")
        raise HTTPException(status_code=500, detail="Failed to get discovery hub")
