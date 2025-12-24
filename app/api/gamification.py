"""
Gamification API Endpoints for AI Language Tutor App

This module provides API endpoints for:
- Achievements (definitions, user unlocks, progress)
- Streaks (status, updates, freezes)
- XP and Leveling (awarding, history, rankings)
- Leaderboards (global, category, user ranks)
"""

import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import require_auth
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser
from app.services.achievement_service import AchievementService
from app.services.leaderboard_service import LeaderboardService
from app.services.streak_service import StreakService
from app.services.xp_service import XPService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/gamification", tags=["Gamification"])


# =====================================================================
# REQUEST/RESPONSE MODELS
# =====================================================================


class AwardXPRequest(BaseModel):
    """Request model for awarding XP"""

    xp_amount: int = Field(..., gt=0, le=10000)
    reason: str = Field(..., min_length=3, max_length=100)
    reference_id: Optional[str] = None
    metadata: Optional[dict] = None


class UseStreakFreezeRequest(BaseModel):
    """Request model for using streak freeze"""

    confirm: bool = Field(..., description="Confirmation to use freeze")


class CalculateScenarioXPRequest(BaseModel):
    """Request model for calculating scenario XP"""

    scenario_difficulty: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    cultural_accuracy: Optional[int] = Field(None, ge=1, le=10)
    completion_time_minutes: Optional[int] = None
    estimated_time_minutes: Optional[int] = None


# =====================================================================
# ACHIEVEMENT ENDPOINTS
# =====================================================================


@router.get("/achievements")
async def get_all_achievements(
    category: Optional[str] = Query(None, description="Filter by category"),
    rarity: Optional[str] = Query(None, description="Filter by rarity"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get all achievement definitions"""
    try:
        service = AchievementService(db)
        achievements = await service.get_all_achievements()

        # Filter by category if provided
        if category:
            achievements = [a for a in achievements if a.category == category]

        # Filter by rarity if provided
        if rarity:
            achievements = [a for a in achievements if a.rarity == rarity]

        return {
            "success": True,
            "count": len(achievements),
            "achievements": [a.to_dict() for a in achievements],
        }

    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements/my")
async def get_my_achievements(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's unlocked achievements"""
    try:
        service = AchievementService(db)
        user_achievements = await service.get_user_achievements(current_user.id)

        return {
            "success": True,
            "count": len(user_achievements),
            "achievements": [ua.to_dict() for ua in user_achievements],
        }

    except Exception as e:
        logger.error(f"Error getting user achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements/{achievement_id}/progress")
async def get_achievement_progress(
    achievement_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get progress towards a specific achievement"""
    try:
        service = AchievementService(db)
        progress = await service.get_achievement_progress(
            current_user.id, achievement_id
        )

        if not progress:
            raise HTTPException(status_code=404, detail="Achievement not found")

        return {
            "success": True,
            "progress": progress,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting achievement progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/achievements/check")
async def check_achievements_manually(
    event_type: str = Query(..., description="Event type to check"),
    event_data: Optional[dict] = None,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Manually trigger achievement checking (for testing/admin)"""
    try:
        service = AchievementService(db)
        newly_unlocked = await service.check_achievements(
            user_id=current_user.id,
            event_type=event_type,
            event_data=event_data or {},
        )

        return {
            "success": True,
            "newly_unlocked_count": len(newly_unlocked),
            "newly_unlocked": [ua.to_dict() for ua in newly_unlocked],
        }

    except Exception as e:
        logger.error(f"Error checking achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# STREAK ENDPOINTS
# =====================================================================


@router.get("/streak/status")
async def get_streak_status(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's current streak status"""
    try:
        service = StreakService(db)
        status = await service.get_streak_status(current_user.id)

        if not status:
            # Initialize streak if doesn't exist
            await service.initialize_user_streak(current_user.id)
            status = await service.get_streak_status(current_user.id)

        return {
            "success": True,
            "streak": status,
        }

    except Exception as e:
        logger.error(f"Error getting streak status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/streak/update")
async def update_streak(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Update user's streak (called on daily activity)"""
    try:
        service = StreakService(db)
        result = await service.update_user_streak(current_user.id)

        return {
            "success": True,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error updating streak: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/streak/freeze")
async def use_streak_freeze(
    request: UseStreakFreezeRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Use a streak freeze to protect streak"""
    try:
        if not request.confirm:
            return {
                "success": False,
                "message": "Freeze usage not confirmed",
            }

        service = StreakService(db)
        result = await service.use_streak_freeze(current_user.id)

        return result

    except Exception as e:
        logger.error(f"Error using streak freeze: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streak/history")
async def get_streak_history(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's streak history"""
    try:
        service = StreakService(db)
        history = await service.get_streak_history(current_user.id, days)

        return {
            "success": True,
            "days": days,
            "history": history,
        }

    except Exception as e:
        logger.error(f"Error getting streak history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# XP AND LEVELING ENDPOINTS
# =====================================================================


@router.get("/xp/level")
async def get_my_level(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's current level and XP"""
    try:
        service = XPService(db)
        level_info = await service.get_user_level(current_user.id)

        if not level_info:
            # Initialize XP if doesn't exist
            await service.initialize_user_xp(current_user.id)
            level_info = await service.get_user_level(current_user.id)

        return {
            "success": True,
            "level": level_info,
        }

    except Exception as e:
        logger.error(f"Error getting user level: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/xp/award")
async def award_xp(
    request: AwardXPRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Award XP to user (admin/system use)"""
    try:
        service = XPService(db)
        result = await service.award_xp(
            user_id=current_user.id,
            xp_amount=request.xp_amount,
            reason=request.reason,
            reference_id=request.reference_id,
            metadata=request.metadata,
        )

        return result

    except Exception as e:
        logger.error(f"Error awarding XP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/xp/calculate-scenario")
async def calculate_scenario_xp(
    request: CalculateScenarioXPRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Calculate XP for a scenario completion"""
    try:
        xp_service = XPService(db)
        streak_service = StreakService(db)

        # Get streak multiplier
        streak_multiplier = await streak_service.calculate_streak_bonus(current_user.id)

        # Calculate XP
        xp_breakdown = await xp_service.calculate_scenario_completion_xp(
            scenario_difficulty=request.scenario_difficulty,
            rating=request.rating,
            cultural_accuracy=request.cultural_accuracy,
            completion_time_minutes=request.completion_time_minutes,
            estimated_time_minutes=request.estimated_time_minutes,
            streak_multiplier=streak_multiplier,
        )

        return {
            "success": True,
            "xp_breakdown": xp_breakdown,
        }

    except Exception as e:
        logger.error(f"Error calculating scenario XP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/xp/history")
async def get_xp_history(
    limit: int = Query(50, ge=1, le=200, description="Max transactions to return"),
    reason_filter: Optional[str] = Query(None, description="Filter by reason"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's XP transaction history"""
    try:
        service = XPService(db)
        history = await service.get_xp_history(
            user_id=current_user.id,
            limit=limit,
            reason_filter=reason_filter,
        )

        return {
            "success": True,
            "count": len(history),
            "history": history,
        }

    except Exception as e:
        logger.error(f"Error getting XP history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/xp/statistics")
async def get_xp_statistics(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get comprehensive XP statistics"""
    try:
        service = XPService(db)
        stats = await service.get_xp_statistics(current_user.id)

        return {
            "success": True,
            "statistics": stats,
        }

    except Exception as e:
        logger.error(f"Error getting XP statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# LEADERBOARD ENDPOINTS
# =====================================================================


@router.get("/leaderboard/{metric}")
async def get_leaderboard(
    metric: str = Path(..., description="Metric to rank by"),
    limit: int = Query(100, ge=1, le=500, description="Number of results"),
    use_cache: bool = Query(True, description="Use cached results"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get global leaderboard for a metric"""
    try:
        service = LeaderboardService(db)
        leaderboard = await service.get_global_leaderboard(
            metric=metric,
            limit=limit,
            use_cache=use_cache,
        )

        return {
            "success": True,
            "metric": metric,
            "count": len(leaderboard),
            "leaderboard": leaderboard,
        }

    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard/{metric}/my-rank")
async def get_my_rank(
    metric: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's rank for a specific metric"""
    try:
        service = LeaderboardService(db)
        rank_info = await service.get_user_rank(current_user.id, metric)

        if not rank_info:
            return {
                "success": True,
                "ranked": False,
                "message": "User not ranked yet",
            }

        return {
            "success": True,
            "ranked": True,
            "rank_info": rank_info,
        }

    except Exception as e:
        logger.error(f"Error getting user rank: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard/{metric}/historical")
async def get_historical_leaderboard(
    metric: str,
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    snapshot_date: date = Query(..., description="Date of snapshot"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get historical leaderboard snapshot"""
    try:
        service = LeaderboardService(db)
        historical = await service.get_historical_leaderboard(
            metric=metric,
            period=period,
            snapshot_date=snapshot_date,
        )

        if not historical:
            raise HTTPException(status_code=404, detail="Snapshot not found")

        return {
            "success": True,
            "metric": metric,
            "period": period,
            "snapshot_date": snapshot_date.isoformat(),
            "leaderboard": historical,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leaderboard/refresh")
async def refresh_leaderboards(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Refresh all leaderboard caches (admin only)"""
    try:
        # TODO: Add admin check
        service = LeaderboardService(db)
        await service.refresh_all_leaderboards()

        return {
            "success": True,
            "message": "All leaderboards refreshed",
        }

    except Exception as e:
        logger.error(f"Error refreshing leaderboards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# DASHBOARD/OVERVIEW ENDPOINTS
# =====================================================================


@router.get("/dashboard")
async def get_gamification_dashboard(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get comprehensive gamification dashboard data"""
    try:
        achievement_service = AchievementService(db)
        streak_service = StreakService(db)
        xp_service = XPService(db)
        leaderboard_service = LeaderboardService(db)

        # Get all data in parallel
        user_achievements = await achievement_service.get_user_achievements(
            current_user.id
        )
        all_achievements = await achievement_service.get_all_achievements()
        streak_status = await streak_service.get_streak_status(current_user.id)
        level_info = await xp_service.get_user_level(current_user.id)
        xp_rank = await leaderboard_service.get_user_rank(
            current_user.id, "xp_all_time"
        )

        # Calculate progress
        achievements_unlocked = len(user_achievements)
        total_achievements = len(all_achievements)
        achievement_percentage = (
            (achievements_unlocked / total_achievements * 100)
            if total_achievements > 0
            else 0
        )

        return {
            "success": True,
            "dashboard": {
                "level": level_info,
                "streak": streak_status,
                "achievements": {
                    "unlocked": achievements_unlocked,
                    "total": total_achievements,
                    "percentage": round(achievement_percentage, 2),
                    "recent": [ua.to_dict() for ua in user_achievements[:5]],  # Last 5
                },
                "leaderboard_rank": xp_rank,
            },
        }

    except Exception as e:
        logger.error(f"Error getting gamification dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# INITIALIZATION ENDPOINT (ADMIN)
# =====================================================================


@router.post("/initialize")
async def initialize_gamification(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Initialize gamification system (load achievement definitions)"""
    try:
        # TODO: Add admin check
        achievement_service = AchievementService(db)
        created_count = await achievement_service.initialize_achievements()

        return {
            "success": True,
            "message": f"Initialized {created_count} new achievements",
        }

    except Exception as e:
        logger.error(f"Error initializing gamification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
