"""
User Budget Dashboard Route Handlers
AI Language Tutor App - Personal Family Educational Tool

This module provides FastHTML route handlers for the user budget dashboard,
allowing users to view and manage their AI API budget based on admin-configured permissions.
"""

import logging
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fasthtml.common import *
from sqlalchemy import func

from app.database.config import get_primary_db_session
from app.frontend.layout import create_footer, create_header
from app.frontend.styles import load_styles
from app.frontend.user_budget import create_user_budget_page
from app.models.budget import UserBudgetSettings
from app.models.database import APIUsage
from app.services.auth import get_current_user

logger = logging.getLogger(__name__)


def create_user_budget_routes(app):
    """Create user budget dashboard routes for the FastHTML app"""

    @app.get("/dashboard/budget")
    async def user_budget_dashboard():
        """User budget dashboard page"""
        try:
            # TODO: Add proper authentication when session management is implemented
            # For now, use demo user ID
            user_id = 1

            # Get user's budget settings
            db = get_primary_db_session()
            try:
                budget_settings = (
                    db.query(UserBudgetSettings)
                    .filter(UserBudgetSettings.user_id == user_id)
                    .first()
                )

                if not budget_settings:
                    # Create default budget settings if none exist
                    budget_settings = UserBudgetSettings(
                        user_id=user_id,
                        monthly_limit_usd=30.0,
                        enforce_budget=True,
                        budget_visible_to_user=True,
                        user_can_modify_limit=False,
                        user_can_reset_budget=False,
                    )
                    db.add(budget_settings)
                    db.commit()
                    db.refresh(budget_settings)

                # Check if budget is visible to user
                if not budget_settings.budget_visible_to_user:
                    return Html(
                        Head(
                            Title("Budget Dashboard - Access Denied"),
                            Meta(charset="utf-8"),
                            Meta(
                                name="viewport",
                                content="width=device-width, initial-scale=1.0",
                            ),
                            load_styles(),
                        ),
                        Body(
                            create_header("budget"),
                            Main(
                                Div(
                                    H1(
                                        "🔒 Budget Dashboard Access Denied",
                                        cls="text-3xl font-bold text-white mb-4",
                                    ),
                                    P(
                                        "Your administrator has disabled budget visibility for your account.",
                                        cls="text-gray-300 mb-4",
                                    ),
                                    P(
                                        "Please contact your administrator if you need access to budget information.",
                                        cls="text-gray-400",
                                    ),
                                    A(
                                        "← Back to Home",
                                        href="/",
                                        cls="text-purple-400 hover:text-purple-300",
                                    ),
                                    cls="container mx-auto px-4 py-8",
                                ),
                                cls="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                            ),
                            create_footer(),
                        ),
                    )

                # Calculate current usage
                total_spent = (
                    db.query(func.sum(APIUsage.estimated_cost))
                    .filter(
                        APIUsage.user_id == user_id,
                        APIUsage.created_at >= budget_settings.current_period_start,
                    )
                    .scalar()
                    or 0.0
                )

                # Calculate percentage used
                monthly_limit = budget_settings.get_effective_limit()
                percentage_used = (
                    (total_spent / monthly_limit * 100) if monthly_limit > 0 else 0
                )

                # Determine alert level
                if percentage_used >= budget_settings.alert_threshold_red:
                    alert_level = "red"
                elif percentage_used >= budget_settings.alert_threshold_orange:
                    alert_level = "orange"
                elif percentage_used >= budget_settings.alert_threshold_yellow:
                    alert_level = "yellow"
                else:
                    alert_level = "green"

                # Prepare budget status data
                budget_status = {
                    "monthly_limit": monthly_limit,
                    "current_spent": total_spent,
                    "period_start": budget_settings.current_period_start.strftime(
                        "%Y-%m-%d"
                    ),
                    "period_end": budget_settings.current_period_end.strftime(
                        "%Y-%m-%d"
                    ),
                    "alert_level": alert_level,
                    "percentage_used": percentage_used,
                }

                # Prepare settings data
                settings_data = {
                    "monthly_limit_usd": budget_settings.monthly_limit_usd,
                    "enforce_budget": budget_settings.enforce_budget,
                    "alert_threshold_yellow": budget_settings.alert_threshold_yellow,
                    "alert_threshold_orange": budget_settings.alert_threshold_orange,
                    "alert_threshold_red": budget_settings.alert_threshold_red,
                }

                # Get recent usage history (last 20 records)
                usage_records = (
                    db.query(APIUsage)
                    .filter(APIUsage.user_id == user_id)
                    .order_by(APIUsage.created_at.desc())
                    .limit(20)
                    .all()
                )

                usage_history = []
                for record in usage_records:
                    usage_history.append(
                        {
                            "timestamp": record.created_at.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "provider": record.api_provider or "Unknown",
                            "model": record.model_name or "Unknown",
                            "cost": record.estimated_cost or 0.0,
                            "tokens": (record.total_tokens or 0),
                        }
                    )

                # Calculate spending breakdown by provider
                provider_breakdown = (
                    db.query(
                        APIUsage.api_provider,
                        func.sum(APIUsage.estimated_cost).label("total_cost"),
                    )
                    .filter(
                        APIUsage.user_id == user_id,
                        APIUsage.created_at >= budget_settings.current_period_start,
                    )
                    .group_by(APIUsage.api_provider)
                    .all()
                )

                breakdown = {
                    "by_provider": {
                        provider: float(cost)
                        for provider, cost in provider_breakdown
                        if provider
                    },
                    "by_model": {},
                }

                # Create the full budget dashboard page
                return Html(
                    Head(
                        Title("My Budget Dashboard"),
                        Meta(charset="utf-8"),
                        Meta(
                            name="viewport",
                            content="width=device-width, initial-scale=1.0",
                        ),
                        load_styles(),
                    ),
                    Body(
                        create_header("budget"),
                        Main(
                            create_user_budget_page(
                                budget_status=budget_status,
                                budget_settings=settings_data,
                                usage_history=usage_history,
                                breakdown=breakdown,
                                can_modify_limit=budget_settings.user_can_modify_limit,
                                can_reset_budget=budget_settings.user_can_reset_budget,
                            ),
                            cls="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                        ),
                        create_footer(),
                    ),
                )

            finally:
                db.close()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in user budget dashboard: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load budget dashboard",
            )


def register_user_budget_routes(app):
    """Register user budget routes with the FastHTML app"""
    create_user_budget_routes(app)
    logger.info("User budget routes registered successfully")
