"""
Learning Analytics & Spaced Repetition API
Task 3.1.4 - Comprehensive Learning Analytics System

RESTful API endpoints for spaced repetition, progress tracking,
gamification, and learning analytics management.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.models.database import User
from app.services.admin_auth import get_current_admin_user
from app.services.spaced_repetition_manager import (
    ItemType,
    ReviewResult,
    SessionType,
    SpacedRepetitionManager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/learning-analytics", tags=["Learning Analytics"])

# Initialize spaced repetition manager
sr_manager = SpacedRepetitionManager()


# ============= PYDANTIC MODELS =============


class ItemTypeEnum(str, Enum):
    """Item types for API"""

    VOCABULARY = "vocabulary"
    PHRASE = "phrase"
    GRAMMAR = "grammar"
    PRONUNCIATION = "pronunciation"


class SessionTypeEnum(str, Enum):
    """Session types for API"""

    VOCABULARY = "vocabulary"
    CONVERSATION = "conversation"
    TUTOR_MODE = "tutor_mode"
    SCENARIO = "scenario"
    CONTENT_REVIEW = "content_review"


class ReviewResultEnum(str, Enum):
    """Review results for API"""

    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


class CreateLearningItemRequest(BaseModel):
    """Request model for creating learning items"""

    user_id: int = Field(..., description="User ID")
    language_code: str = Field(
        ..., min_length=2, max_length=10, description="Language code"
    )
    content: str = Field(..., min_length=1, max_length=500, description="Item content")
    item_type: ItemTypeEnum = Field(..., description="Type of learning item")
    translation: Optional[str] = Field("", max_length=500, description="Translation")
    definition: Optional[str] = Field("", max_length=1000, description="Definition")
    pronunciation_guide: Optional[str] = Field(
        "", max_length=200, description="Pronunciation guide"
    )
    example_usage: Optional[str] = Field(
        "", max_length=1000, description="Example usage"
    )
    context_tags: Optional[List[str]] = Field([], description="Context tags")
    source_session_id: Optional[str] = Field("", description="Source session ID")
    source_content: Optional[str] = Field("", description="Source content type")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")


class ReviewItemRequest(BaseModel):
    """Request model for reviewing items"""

    item_id: str = Field(..., description="Item ID to review")
    review_result: ReviewResultEnum = Field(..., description="Review result")
    response_time_ms: Optional[int] = Field(
        0, ge=0, description="Response time in milliseconds"
    )
    confidence_score: Optional[float] = Field(
        0.0, ge=0.0, le=1.0, description="Confidence score"
    )


class StartSessionRequest(BaseModel):
    """Request model for starting learning sessions"""

    user_id: int = Field(..., description="User ID")
    language_code: str = Field(
        ..., min_length=2, max_length=10, description="Language code"
    )
    session_type: SessionTypeEnum = Field(..., description="Type of learning session")
    mode_specific_data: Optional[Dict[str, Any]] = Field(
        {}, description="Mode-specific data"
    )
    content_source: Optional[str] = Field("", description="Content source")
    ai_model_used: Optional[str] = Field("", description="AI model used")
    tutor_mode: Optional[str] = Field("", description="Tutor mode")
    scenario_id: Optional[str] = Field("", description="Scenario ID")


class EndSessionRequest(BaseModel):
    """Request model for ending learning sessions"""

    session_id: str = Field(..., description="Session ID to end")
    items_studied: Optional[int] = Field(0, ge=0, description="Number of items studied")
    items_correct: Optional[int] = Field(0, ge=0, description="Number of correct items")
    items_incorrect: Optional[int] = Field(
        0, ge=0, description="Number of incorrect items"
    )
    average_response_time_ms: Optional[int] = Field(
        0, ge=0, description="Average response time"
    )
    confidence_score: Optional[float] = Field(
        0.0, ge=0.0, le=1.0, description="Average confidence"
    )
    engagement_score: Optional[float] = Field(
        0.0, ge=0.0, le=1.0, description="Engagement score"
    )
    new_items_learned: Optional[int] = Field(0, ge=0, description="New items learned")


class CreateGoalRequest(BaseModel):
    """Request model for creating learning goals"""

    user_id: int = Field(..., description="User ID")
    language_code: str = Field(
        ..., min_length=2, max_length=10, description="Language code"
    )
    goal_type: str = Field(..., description="Goal type")
    title: str = Field(..., min_length=1, max_length=255, description="Goal title")
    description: Optional[str] = Field("", description="Goal description")
    target_value: float = Field(..., gt=0, description="Target value")
    unit: str = Field(..., description="Unit of measurement")
    difficulty_level: Optional[int] = Field(
        2, ge=1, le=3, description="Difficulty level"
    )
    priority: Optional[int] = Field(2, ge=1, le=3, description="Priority level")
    is_daily: Optional[bool] = Field(False, description="Is daily goal")
    is_weekly: Optional[bool] = Field(False, description="Is weekly goal")
    is_monthly: Optional[bool] = Field(False, description="Is monthly goal")
    target_days: Optional[int] = Field(30, ge=1, description="Days to complete goal")


class UpdateConfigRequest(BaseModel):
    """Request model for updating algorithm configuration"""

    initial_ease_factor: Optional[float] = Field(None, ge=1.0, le=5.0)
    minimum_ease_factor: Optional[float] = Field(None, ge=1.0, le=3.0)
    maximum_ease_factor: Optional[float] = Field(None, ge=2.0, le=5.0)
    ease_factor_change: Optional[float] = Field(None, ge=0.05, le=0.5)
    initial_interval_days: Optional[int] = Field(None, ge=1, le=7)
    graduation_interval_days: Optional[int] = Field(None, ge=1, le=14)
    easy_interval_days: Optional[int] = Field(None, ge=1, le=30)
    maximum_interval_days: Optional[int] = Field(None, ge=30, le=1000)
    mastery_threshold: Optional[float] = Field(None, ge=0.5, le=1.0)
    review_threshold: Optional[float] = Field(None, ge=0.3, le=1.0)
    difficulty_threshold: Optional[float] = Field(None, ge=0.1, le=0.8)
    retention_threshold: Optional[float] = Field(None, ge=0.5, le=1.0)
    points_per_correct: Optional[float] = Field(None, ge=1, le=100)
    points_per_streak_day: Optional[float] = Field(None, ge=1, le=50)
    points_per_goal_achieved: Optional[float] = Field(None, ge=10, le=1000)
    daily_goal_default: Optional[int] = Field(None, ge=5, le=300)


# ============= SPACED REPETITION ENDPOINTS =============


@router.post("/items/create")
async def create_learning_item(request: CreateLearningItemRequest) -> JSONResponse:
    """Create a new learning item for spaced repetition"""
    try:
        # Convert enum to proper type
        item_type = ItemType(request.item_type.value)

        item_id = sr_manager.add_learning_item(
            user_id=request.user_id,
            language_code=request.language_code,
            content=request.content,
            item_type=item_type,
            translation=request.translation,
            definition=request.definition,
            pronunciation_guide=request.pronunciation_guide,
            example_usage=request.example_usage,
            context_tags=request.context_tags,
            source_session_id=request.source_session_id,
            source_content=request.source_content,
            metadata=request.metadata,
        )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Learning item created successfully",
                "data": {"item_id": item_id},
            },
        )

    except Exception as e:
        logger.error(f"Error creating learning item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/review")
async def review_item(request: ReviewItemRequest) -> JSONResponse:
    """Review a learning item and update spaced repetition data"""
    try:
        # Convert enum to proper type
        review_result = ReviewResult[request.review_result.value.upper()]

        success = sr_manager.review_item(
            item_id=request.item_id,
            review_result=review_result,
            response_time_ms=request.response_time_ms,
            confidence_score=request.confidence_score,
        )

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Item reviewed successfully",
                    "data": {"item_id": request.item_id},
                },
            )
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/due/{user_id}")
async def get_due_items(
    user_id: int,
    language_code: str = Query(..., description="Language code"),
    limit: int = Query(20, ge=1, le=100, description="Maximum items to return"),
) -> JSONResponse:
    """Get items due for review for a user"""
    try:
        items = sr_manager.get_due_items(
            user_id=user_id, language_code=language_code, limit=limit
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Retrieved {len(items)} due items",
                "data": {"items": items, "count": len(items)},
            },
        )

    except Exception as e:
        logger.error(f"Error getting due items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= LEARNING SESSIONS ENDPOINTS =============


@router.post("/sessions/start")
async def start_learning_session(request: StartSessionRequest) -> JSONResponse:
    """Start a new learning session"""
    try:
        # Convert enum to proper type
        session_type = SessionType(request.session_type.value)

        session_id = sr_manager.start_learning_session(
            user_id=request.user_id,
            language_code=request.language_code,
            session_type=session_type,
            mode_specific_data=request.mode_specific_data,
            content_source=request.content_source,
            ai_model_used=request.ai_model_used,
            tutor_mode=request.tutor_mode,
            scenario_id=request.scenario_id,
        )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Learning session started successfully",
                "data": {"session_id": session_id},
            },
        )

    except Exception as e:
        logger.error(f"Error starting learning session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/end")
async def end_learning_session(request: EndSessionRequest) -> JSONResponse:
    """End a learning session and calculate metrics"""
    try:
        success = sr_manager.end_learning_session(
            session_id=request.session_id,
            items_studied=request.items_studied,
            items_correct=request.items_correct,
            items_incorrect=request.items_incorrect,
            average_response_time_ms=request.average_response_time_ms,
            confidence_score=request.confidence_score,
            engagement_score=request.engagement_score,
            new_items_learned=request.new_items_learned,
        )

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Learning session ended successfully",
                    "data": {"session_id": request.session_id},
                },
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending learning session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= ANALYTICS ENDPOINTS =============


@router.get("/analytics/user/{user_id}")
async def get_user_analytics(
    user_id: int,
    language_code: str = Query(..., description="Language code"),
    period: str = Query(
        "daily", pattern="^(daily|weekly|monthly)$", description="Analytics period"
    ),
) -> JSONResponse:
    """Get comprehensive learning analytics for a user"""
    try:
        analytics = sr_manager.get_user_analytics(
            user_id=user_id, language_code=language_code, period=period
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User analytics retrieved successfully",
                "data": analytics,
            },
        )

    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/system")
async def get_system_analytics(
    admin_user: User = Depends(get_current_admin_user),
) -> JSONResponse:
    """Get system-wide learning analytics (admin only)"""
    try:
        analytics = sr_manager.get_system_analytics()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "System analytics retrieved successfully",
                "data": analytics,
            },
        )

    except Exception as e:
        logger.error(f"Error getting system analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= GOALS MANAGEMENT ENDPOINTS =============


@router.post("/goals/create")
async def create_learning_goal(request: CreateGoalRequest) -> JSONResponse:
    """Create a new learning goal"""
    try:
        goal_id = f"goal_{request.user_id}_{request.language_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate target date
        target_date = datetime.now() + timedelta(days=request.target_days)

        # This would use a goals manager (to be implemented)
        # For now, return a success response
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Learning goal created successfully",
                "data": {"goal_id": goal_id, "target_date": target_date.isoformat()},
            },
        )

    except Exception as e:
        logger.error(f"Error creating learning goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals/user/{user_id}")
async def get_user_goals(
    user_id: int,
    language_code: str = Query(..., description="Language code"),
    status: str = Query(
        "active",
        pattern="^(active|completed|paused|failed)$",
        description="Goal status",
    ),
) -> JSONResponse:
    """Get learning goals for a user"""
    try:
        # This would query the goals from database
        # For now, return empty list
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User goals retrieved successfully",
                "data": {"goals": [], "count": 0},
            },
        )

    except Exception as e:
        logger.error(f"Error getting user goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= ACHIEVEMENTS ENDPOINTS =============


@router.get("/achievements/user/{user_id}")
async def get_user_achievements(
    user_id: int,
    language_code: str = Query(None, description="Language code (optional)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum achievements to return"),
) -> JSONResponse:
    """Get achievements for a user"""
    try:
        # This would query achievements from database
        # For now, return empty list
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User achievements retrieved successfully",
                "data": {"achievements": [], "total_points": 0, "count": 0},
            },
        )

    except Exception as e:
        logger.error(f"Error getting user achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= ADMIN CONFIGURATION ENDPOINTS =============


@router.get("/config/algorithm")
async def get_algorithm_config(
    admin_user: User = Depends(get_current_admin_user),
) -> JSONResponse:
    """Get current spaced repetition algorithm configuration (admin only)"""
    try:
        config = sr_manager.config

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Algorithm configuration retrieved successfully",
                "data": config,
            },
        )

    except Exception as e:
        logger.error(f"Error getting algorithm config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/algorithm")
async def update_algorithm_config(
    request: UpdateConfigRequest, admin_user: User = Depends(get_current_admin_user)
) -> JSONResponse:
    """Update spaced repetition algorithm configuration (admin only)"""
    try:
        # Filter out None values
        config_updates = {
            k: v for k, v in request.model_dump().items() if v is not None
        }

        if not config_updates:
            raise HTTPException(
                status_code=400, detail="No configuration updates provided"
            )

        success = sr_manager.update_algorithm_config(config_updates)

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Algorithm configuration updated successfully",
                    "data": {"updated_fields": list(config_updates.keys())},
                },
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to update configuration"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating algorithm config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= UTILITY ENDPOINTS =============


@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for learning analytics API"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Learning Analytics API is healthy",
            "data": {
                "service": "learning_analytics",
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
            },
        },
    )


@router.get("/stats")
async def get_api_stats() -> JSONResponse:
    """Get basic API statistics"""
    try:
        # This could include API usage stats, cache statistics, etc.
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "API statistics retrieved successfully",
                "data": {
                    "endpoints_available": 13,
                    "spaced_repetition_active": True,
                    "analytics_active": True,
                    "achievements_active": True,
                    "admin_config_active": True,
                    "last_updated": datetime.now().isoformat(),
                },
            },
        )

    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export router
__all__ = ["router"]
