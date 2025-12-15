"""
Budget Management API Endpoints

Provides comprehensive budget management for users and admins:
- View budget status and usage
- Configure budget settings
- Manual budget reset
- Budget history and analytics
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.auth import SimpleUser, require_auth
from app.database.config import get_primary_db_session
from app.models.budget import (
    BudgetAlert,
    BudgetPeriod,
    BudgetResetLog,
    UserBudgetSettings,
)
from app.models.database import APIUsage, User, UserRole
from app.services.admin_auth import require_admin_access
from app.services.budget_manager import budget_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/budget", tags=["budget"])


# Pydantic Models for API
class BudgetStatusResponse(BaseModel):
    """Budget status information"""

    user_id: str
    total_budget: float
    used_budget: float
    remaining_budget: float
    percentage_used: float
    alert_level: str
    days_remaining_in_period: int
    projected_period_cost: float
    is_over_budget: bool
    period_start: str
    period_end: Optional[str]
    budget_period: str
    can_view_budget: bool
    can_modify_limit: bool
    can_reset_budget: bool


class BudgetSettingsResponse(BaseModel):
    """Budget configuration settings"""

    user_id: str
    monthly_limit_usd: float
    custom_limit_usd: Optional[float]
    budget_period: str
    custom_period_days: Optional[int]
    enforce_budget: bool
    allow_budget_override: bool
    auto_fallback_to_ollama: bool
    alert_threshold_yellow: float
    alert_threshold_orange: float
    alert_threshold_red: float
    budget_visible_to_user: bool
    user_can_modify_limit: bool
    user_can_reset_budget: bool
    admin_notes: Optional[str]
    configured_by: Optional[str]


class UpdateBudgetSettingsRequest(BaseModel):
    """Request to update budget settings"""

    monthly_limit_usd: Optional[float] = Field(None, ge=0, le=10000)
    custom_limit_usd: Optional[float] = Field(None, ge=0, le=10000)
    budget_period: Optional[str] = Field(
        None, pattern="^(monthly|weekly|daily|custom)$"
    )
    custom_period_days: Optional[int] = Field(None, ge=1, le=365)
    enforce_budget: Optional[bool] = None
    allow_budget_override: Optional[bool] = None
    auto_fallback_to_ollama: Optional[bool] = None
    alert_threshold_yellow: Optional[float] = Field(None, ge=0, le=100)
    alert_threshold_orange: Optional[float] = Field(None, ge=0, le=100)
    alert_threshold_red: Optional[float] = Field(None, ge=0, le=100)


class AdminUpdateBudgetRequest(BaseModel):
    """Admin request to update user budget configuration"""

    target_user_id: str
    budget_visible_to_user: Optional[bool] = None
    user_can_modify_limit: Optional[bool] = None
    user_can_reset_budget: Optional[bool] = None
    monthly_limit_usd: Optional[float] = Field(None, ge=0, le=10000)
    admin_notes: Optional[str] = Field(None, max_length=500)


class BudgetResetRequest(BaseModel):
    """Request to manually reset budget"""

    reason: Optional[str] = Field(None, max_length=500)


class BudgetUsageBreakdown(BaseModel):
    """Detailed budget usage breakdown"""

    user_id: str
    period_start: str
    period_end: Optional[str]
    total_spent: float
    by_provider: dict
    by_service_type: dict
    by_day: List[dict]
    top_expensive_operations: List[dict]


# Helper Functions


def _get_or_create_budget_settings(user_id: str, db: Session) -> UserBudgetSettings:
    """Get budget settings for user, create if doesn't exist"""
    settings = (
        db.query(UserBudgetSettings)
        .filter(UserBudgetSettings.user_id == user_id)
        .first()
    )

    if not settings:
        # Create default settings
        settings = UserBudgetSettings(
            user_id=user_id,
            monthly_limit_usd=30.0,
            budget_period=BudgetPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=_calculate_period_end(BudgetPeriod.MONTHLY, None),
            last_reset_date=datetime.now(),
            enforce_budget=True,
            allow_budget_override=True,
            auto_fallback_to_ollama=False,
            alert_threshold_yellow=50.0,
            alert_threshold_orange=75.0,
            alert_threshold_red=90.0,
            budget_visible_to_user=True,
            user_can_modify_limit=False,  # Default: only admin can modify
            user_can_reset_budget=False,  # Default: only admin can reset
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def _calculate_period_end(period: BudgetPeriod, custom_days: Optional[int]) -> datetime:
    """Calculate period end date"""
    now = datetime.now()

    if period == BudgetPeriod.MONTHLY:
        if now.month == 12:
            return datetime(now.year + 1, 1, 1, 0, 0, 0)
        else:
            return datetime(now.year, now.month + 1, 1, 0, 0, 0)

    elif period == BudgetPeriod.WEEKLY:
        return now + timedelta(days=7)

    elif period == BudgetPeriod.DAILY:
        tomorrow = now + timedelta(days=1)
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)

    elif period == BudgetPeriod.CUSTOM and custom_days:
        return now + timedelta(days=custom_days)

    # Default: monthly
    if now.month == 12:
        return datetime(now.year + 1, 1, 1, 0, 0, 0)
    else:
        return datetime(now.year, now.month + 1, 1, 0, 0, 0)


def _check_budget_permissions(
    user: SimpleUser, settings: UserBudgetSettings, required_permission: str
) -> bool:
    """Check if user has required budget permission"""
    # Admins always have full access
    if user.role == UserRole.ADMIN.value:
        return True

    # Check specific permissions
    if required_permission == "view":
        return settings.budget_visible_to_user
    elif required_permission == "modify":
        return settings.user_can_modify_limit
    elif required_permission == "reset":
        return settings.user_can_reset_budget

    return False


# API Endpoints


@router.get("/status", response_model=BudgetStatusResponse)
async def get_budget_status(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get current budget status for authenticated user

    Returns detailed budget information including:
    - Total budget limit
    - Amount used this period
    - Remaining budget
    - Alert level
    - Days remaining in period
    - Projected costs
    """
    # Get or create budget settings
    settings = _get_or_create_budget_settings(current_user.user_id, db)

    # Check permission to view budget
    if not _check_budget_permissions(current_user, settings, "view"):
        raise HTTPException(
            status_code=403,
            detail="Budget visibility is disabled for your account. Contact an administrator.",
        )

    # Get usage for current period
    # Note: APIUsage.user_id is Integer FK to users.id, but current_user.user_id is String
    # We need to use current_user.id (the numeric ID) for the query
    total_cost = (
        db.query(func.sum(APIUsage.estimated_cost))
        .filter(
            APIUsage.user_id == current_user.id,
            APIUsage.created_at >= settings.current_period_start,
        )
        .scalar()
        or 0.0
    )

    # Calculate budget metrics
    effective_limit = settings.get_effective_limit()
    remaining = max(0, effective_limit - total_cost)
    percentage_used = (total_cost / effective_limit * 100) if effective_limit > 0 else 0

    # Determine alert level
    if percentage_used >= settings.alert_threshold_red:
        alert_level = "red"
    elif percentage_used >= settings.alert_threshold_orange:
        alert_level = "orange"
    elif percentage_used >= settings.alert_threshold_yellow:
        alert_level = "yellow"
    else:
        alert_level = "green"

    # Calculate days remaining
    now = datetime.now()
    days_remaining = 0
    if settings.current_period_end:
        days_remaining = max(0, (settings.current_period_end - now).days)

    # Project period cost
    days_elapsed = (now - settings.current_period_start).days + 1
    daily_average = total_cost / days_elapsed if days_elapsed > 0 else 0

    if settings.budget_period == BudgetPeriod.MONTHLY:
        projected_cost = daily_average * 30
    elif settings.budget_period == BudgetPeriod.WEEKLY:
        projected_cost = daily_average * 7
    elif settings.budget_period == BudgetPeriod.DAILY:
        projected_cost = total_cost  # Already at end of day
    elif settings.budget_period == BudgetPeriod.CUSTOM and settings.custom_period_days:
        projected_cost = daily_average * settings.custom_period_days
    else:
        projected_cost = daily_average * 30

    return BudgetStatusResponse(
        user_id=current_user.user_id,
        total_budget=effective_limit,
        used_budget=total_cost,
        remaining_budget=remaining,
        percentage_used=percentage_used,
        alert_level=alert_level,
        days_remaining_in_period=days_remaining,
        projected_period_cost=projected_cost,
        is_over_budget=total_cost > effective_limit,
        period_start=settings.current_period_start.isoformat(),
        period_end=settings.current_period_end.isoformat()
        if settings.current_period_end
        else None,
        budget_period=settings.budget_period.value
        if settings.budget_period
        else "monthly",
        can_view_budget=True,  # They're viewing it now
        can_modify_limit=_check_budget_permissions(current_user, settings, "modify"),
        can_reset_budget=_check_budget_permissions(current_user, settings, "reset"),
    )


@router.get("/settings", response_model=BudgetSettingsResponse)
async def get_budget_settings(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get budget configuration settings for authenticated user"""
    settings = _get_or_create_budget_settings(current_user.user_id, db)

    # Check permission
    if not _check_budget_permissions(current_user, settings, "view"):
        raise HTTPException(
            status_code=403, detail="Budget visibility is disabled for your account"
        )

    return BudgetSettingsResponse(**settings.to_dict())


@router.put("/settings", response_model=BudgetSettingsResponse)
async def update_budget_settings(
    request: UpdateBudgetSettingsRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Update budget settings for authenticated user

    Users can only modify settings if admin has granted permission.
    Admins can always modify their own settings.
    """
    settings = _get_or_create_budget_settings(current_user.user_id, db)

    # Check permission
    if not _check_budget_permissions(current_user, settings, "modify"):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to modify budget settings. Contact an administrator.",
        )

    # Update allowed fields
    if request.monthly_limit_usd is not None:
        settings.monthly_limit_usd = request.monthly_limit_usd

    if request.custom_limit_usd is not None:
        settings.custom_limit_usd = request.custom_limit_usd

    if request.budget_period is not None:
        settings.budget_period = BudgetPeriod(request.budget_period)
        # Recalculate period end
        settings.current_period_end = _calculate_period_end(
            settings.budget_period, request.custom_period_days
        )

    if request.custom_period_days is not None:
        settings.custom_period_days = request.custom_period_days

    if request.enforce_budget is not None:
        settings.enforce_budget = request.enforce_budget

    if request.allow_budget_override is not None:
        settings.allow_budget_override = request.allow_budget_override

    if request.auto_fallback_to_ollama is not None:
        settings.auto_fallback_to_ollama = request.auto_fallback_to_ollama

    if request.alert_threshold_yellow is not None:
        settings.alert_threshold_yellow = request.alert_threshold_yellow

    if request.alert_threshold_orange is not None:
        settings.alert_threshold_orange = request.alert_threshold_orange

    if request.alert_threshold_red is not None:
        settings.alert_threshold_red = request.alert_threshold_red

    # Validate threshold ordering: yellow < orange < red
    if not (
        settings.alert_threshold_yellow
        < settings.alert_threshold_orange
        < settings.alert_threshold_red
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid threshold values. Must satisfy: yellow < orange < red",
        )

    db.commit()
    db.refresh(settings)

    return BudgetSettingsResponse(**settings.to_dict())


@router.post("/reset")
async def reset_budget(
    request: BudgetResetRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Manually reset budget for current period

    Starts a new budget period immediately. Requires permission.
    """
    settings = _get_or_create_budget_settings(current_user.user_id, db)

    # Check permission
    if not _check_budget_permissions(current_user, settings, "reset"):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to reset budget. Contact an administrator.",
        )

    # Get current spent amount
    current_spent = (
        db.query(func.sum(APIUsage.estimated_cost))
        .filter(
            APIUsage.user_id == current_user.id,
            APIUsage.created_at >= settings.current_period_start,
        )
        .scalar()
        or 0.0
    )

    # Log the reset
    reset_log = BudgetResetLog(
        user_id=current_user.user_id,
        reset_type="manual",
        reset_by=current_user.user_id,
        previous_limit=settings.get_effective_limit(),
        new_limit=settings.get_effective_limit(),
        previous_spent=current_spent,
        previous_period_start=settings.current_period_start,
        previous_period_end=settings.current_period_end or datetime.now(),
        new_period_start=datetime.now(),
        new_period_end=_calculate_period_end(
            settings.budget_period, settings.custom_period_days
        ),
        reason=request.reason or "Manual reset by user",
    )
    db.add(reset_log)

    # Reset budget period
    settings.current_period_start = datetime.now()
    settings.current_period_end = _calculate_period_end(
        settings.budget_period, settings.custom_period_days
    )
    settings.last_reset_date = datetime.now()

    db.commit()

    return {
        "success": True,
        "message": "Budget reset successfully",
        "new_period_start": settings.current_period_start.isoformat(),
        "new_period_end": settings.current_period_end.isoformat()
        if settings.current_period_end
        else None,
        "previous_spent": current_spent,
    }


@router.get("/usage/breakdown", response_model=BudgetUsageBreakdown)
async def get_usage_breakdown(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get detailed breakdown of budget usage

    Returns usage by provider, service type, daily trends, and top expenses.
    """
    settings = _get_or_create_budget_settings(current_user.user_id, db)

    # Check permission
    if not _check_budget_permissions(current_user, settings, "view"):
        raise HTTPException(
            status_code=403, detail="Budget visibility is disabled for your account"
        )

    # Get all usage records for current period
    usage_records = (
        db.query(APIUsage)
        .filter(
            APIUsage.user_id == current_user.id,
            APIUsage.created_at >= settings.current_period_start,
        )
        .all()
    )

    # Calculate breakdowns
    by_provider = {}
    by_service_type = {}
    by_day = {}

    for record in usage_records:
        # By provider
        provider = record.api_provider or "unknown"
        by_provider[provider] = by_provider.get(provider, 0.0) + (
            record.estimated_cost or 0.0
        )

        # By service type
        service = record.request_type or "unknown"
        by_service_type[service] = by_service_type.get(service, 0.0) + (
            record.estimated_cost or 0.0
        )

        # By day
        day_key = (
            record.created_at.date().isoformat() if record.created_at else "unknown"
        )
        if day_key not in by_day:
            by_day[day_key] = {"date": day_key, "cost": 0.0, "requests": 0}
        by_day[day_key]["cost"] += record.estimated_cost or 0.0
        by_day[day_key]["requests"] += 1

    # Get top expensive operations
    top_operations = sorted(
        [
            {
                "timestamp": r.created_at.isoformat() if r.created_at else None,
                "provider": r.api_provider,
                "service_type": r.request_type,
                "cost": r.estimated_cost,
                "tokens_used": r.tokens_used,
            }
            for r in usage_records
        ],
        key=lambda x: x["cost"] or 0,
        reverse=True,
    )[:10]  # Top 10

    total_spent = sum(r.estimated_cost or 0.0 for r in usage_records)

    return BudgetUsageBreakdown(
        user_id=current_user.user_id,
        period_start=settings.current_period_start.isoformat(),
        period_end=settings.current_period_end.isoformat()
        if settings.current_period_end
        else None,
        total_spent=total_spent,
        by_provider=by_provider,
        by_service_type=by_service_type,
        by_day=sorted(by_day.values(), key=lambda x: x["date"]),
        top_expensive_operations=top_operations,
    )


@router.get("/history", response_model=List[dict])
async def get_budget_reset_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get budget reset history for authenticated user"""
    settings = _get_or_create_budget_settings(current_user.user_id, db)

    # Check permission
    if not _check_budget_permissions(current_user, settings, "view"):
        raise HTTPException(
            status_code=403, detail="Budget visibility is disabled for your account"
        )

    # Get reset logs
    logs = (
        db.query(BudgetResetLog)
        .filter(BudgetResetLog.user_id == current_user.user_id)
        .order_by(BudgetResetLog.reset_timestamp.desc())
        .limit(limit)
        .all()
    )

    return [log.to_dict() for log in logs]


# Admin Endpoints


@router.put("/admin/configure", response_model=BudgetSettingsResponse)
async def admin_configure_user_budget(
    request: AdminUpdateBudgetRequest,
    current_user: SimpleUser = Depends(require_admin_access),
    db: Session = Depends(get_primary_db_session),
):
    """
    Admin endpoint to configure budget settings for any user

    Allows admins to:
    - Enable/disable budget visibility for users
    - Grant/revoke permission to modify budget
    - Grant/revoke permission to reset budget
    - Set budget limits
    - Add admin notes
    """
    # Get or create settings for target user
    settings = _get_or_create_budget_settings(request.target_user_id, db)

    # Update admin-controlled fields
    if request.budget_visible_to_user is not None:
        settings.budget_visible_to_user = request.budget_visible_to_user

    if request.user_can_modify_limit is not None:
        settings.user_can_modify_limit = request.user_can_modify_limit

    if request.user_can_reset_budget is not None:
        settings.user_can_reset_budget = request.user_can_reset_budget

    if request.monthly_limit_usd is not None:
        settings.monthly_limit_usd = request.monthly_limit_usd

    if request.admin_notes is not None:
        settings.admin_notes = request.admin_notes

    settings.configured_by = current_user.user_id

    db.commit()
    db.refresh(settings)

    return BudgetSettingsResponse(**settings.to_dict())


@router.get("/admin/users", response_model=List[BudgetSettingsResponse])
async def admin_list_all_budget_settings(
    current_user: SimpleUser = Depends(require_admin_access),
    db: Session = Depends(get_primary_db_session),
):
    """Admin endpoint to list budget settings for all users"""
    all_settings = db.query(UserBudgetSettings).all()
    return [BudgetSettingsResponse(**s.to_dict()) for s in all_settings]


@router.post("/admin/reset/{user_id}")
async def admin_reset_user_budget(
    user_id: str,
    request: BudgetResetRequest,
    current_user: SimpleUser = Depends(require_admin_access),
    db: Session = Depends(get_primary_db_session),
):
    """Admin endpoint to reset budget for any user"""
    settings = _get_or_create_budget_settings(user_id, db)

    # Get the user's numeric ID for querying APIUsage
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get current spent amount
    current_spent = (
        db.query(func.sum(APIUsage.estimated_cost))
        .filter(
            APIUsage.user_id == user.id,
            APIUsage.created_at >= settings.current_period_start,
        )
        .scalar()
        or 0.0
    )

    # Log the reset
    reset_log = BudgetResetLog(
        user_id=user_id,
        reset_type="manual",
        reset_by=current_user.user_id,  # Admin who reset it
        previous_limit=settings.get_effective_limit(),
        new_limit=settings.get_effective_limit(),
        previous_spent=current_spent,
        previous_period_start=settings.current_period_start,
        previous_period_end=settings.current_period_end or datetime.now(),
        new_period_start=datetime.now(),
        new_period_end=_calculate_period_end(
            settings.budget_period, settings.custom_period_days
        ),
        reason=request.reason or f"Manual reset by admin {current_user.user_id}",
    )
    db.add(reset_log)

    # Reset budget period
    settings.current_period_start = datetime.now()
    settings.current_period_end = _calculate_period_end(
        settings.budget_period, settings.custom_period_days
    )
    settings.last_reset_date = datetime.now()

    db.commit()

    return {
        "success": True,
        "message": f"Budget reset successfully for user {user_id}",
        "reset_by": current_user.user_id,
        "new_period_start": settings.current_period_start.isoformat(),
        "new_period_end": settings.current_period_end.isoformat()
        if settings.current_period_end
        else None,
        "previous_spent": current_spent,
    }
