"""
Admin Dashboard Route Handlers
AI Language Tutor App - Personal Family Educational Tool

This module provides FastHTML route handlers for the admin dashboard,
integrating with the admin authentication system and dashboard frontend.
"""

import logging
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fasthtml.common import *

from app.database.config import get_db_session_context
from app.frontend.admin_ai_models import create_ai_models_page
from app.frontend.admin_budget import create_admin_budget_page
from app.frontend.admin_dashboard import create_user_management_page
from app.frontend.admin_feature_toggles import create_feature_toggle_page
from app.frontend.admin_language_config import (
    language_config_javascript,
    language_config_page,
)
from app.frontend.admin_scenario_management import create_scenario_management_page
from app.frontend.progress_analytics_dashboard import (
    progress_analytics_dashboard_page,
    progress_analytics_styles,
)
from app.models.database import User
from app.services.admin_auth import (
    AdminPermission,
    admin_auth_service,
)
from app.services.auth import get_current_user

logger = logging.getLogger(__name__)


def create_admin_routes(app):
    """Create admin dashboard routes for the FastHTML app"""

    @app.get("/dashboard/admin")
    async def admin_dashboard_redirect(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Redirect to user management (main admin page)"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            return RedirectResponse("/dashboard/admin/users", status_code=302)

        except Exception as e:
            logger.error(f"Error in admin dashboard redirect: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to access admin dashboard",
            )

    @app.get("/dashboard/admin/users")
    async def admin_users_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin user management page"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Get all users from database
            with get_db_session_context() as session:
                users = session.query(User).all()

                user_list = []
                for user in users:
                    user_list.append(
                        {
                            "user_id": user.user_id,
                            "username": user.username,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "role": user.role.name,
                            "is_active": user.is_active,
                            "is_verified": user.is_verified,
                            "created_at": user.created_at.isoformat()
                            if user.created_at
                            else None,
                            "updated_at": user.updated_at.isoformat()
                            if user.updated_at
                            else None,
                            "last_login": user.last_login.isoformat()
                            if user.last_login
                            else None,
                        }
                    )

            # Check for active guest session
            from app.services.admin_auth import GuestUserManager

            guest_manager = GuestUserManager()

            guest_info = None
            if guest_manager.active_guest_session:
                guest_info = {
                    "user_id": guest_manager.active_guest_session,
                    "created_at": guest_manager.guest_session_data.get(
                        "created_at", "Unknown"
                    ),
                    "status": "active",
                }

            # Create and return the page
            return create_user_management_page(user_list, current_user, guest_info)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin users page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load user management page",
            )

    @app.get("/dashboard/admin/languages")
    async def admin_languages_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin language configuration page"""
        try:
            # Check admin access and permissions
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check language management permission
            if not admin_auth_service.has_permission(
                current_user, AdminPermission.MANAGE_LANGUAGES
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Language management permission required",
                )

            # Create the full language configuration page with admin layout
            from app.frontend.layout import create_admin_header, create_admin_sidebar
            from app.frontend.styles import load_styles

            return Html(
                Head(
                    Title("Admin Dashboard - Language Configuration"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                    load_styles(),
                ),
                Body(
                    # Admin Layout Container
                    Div(
                        create_admin_sidebar("languages"),
                        Div(
                            create_admin_header(current_user, "Language Configuration"),
                            Div(language_config_page(), cls="p-6"),
                            cls="flex-1 ml-64 overflow-auto",
                        ),
                        cls="flex min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                    ),
                    # JavaScript for language configuration functionality
                    language_config_javascript(),
                    cls="font-sans antialiased",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin languages page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load language configuration page",
            )

    @app.get("/dashboard/admin/features")
    async def admin_features_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin feature toggle management page"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check feature toggle management permission
            if not admin_auth_service.has_permission(
                current_user, AdminPermission.MANAGE_FEATURES
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Feature management permission required",
                )

            # Create the full feature toggles page with admin layout
            from app.frontend.layout import create_admin_header, create_admin_sidebar
            from app.frontend.styles import load_styles

            return Html(
                Head(
                    Title("Admin Dashboard - Feature Toggles"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                    load_styles(),
                    # Add HTMX for dynamic updates
                    Script(src="https://unpkg.com/htmx.org@1.9.6"),
                ),
                Body(
                    # Admin Layout Container
                    Div(
                        create_admin_sidebar("features"),
                        Div(
                            create_admin_header(current_user, "Feature Toggles"),
                            Div(
                                create_feature_toggle_page(),
                                cls="p-6",
                            ),
                            cls="flex-1 ml-64 overflow-auto",
                        ),
                        cls="flex min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                    ),
                    cls="font-sans antialiased",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin features page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load feature management page",
            )

    @app.get("/dashboard/admin/ai-models")
    async def admin_ai_models_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin AI model management page"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check AI model management permission
            if not admin_auth_service.has_permission(
                current_user,
                AdminPermission.MANAGE_FEATURES,  # Using MANAGE_FEATURES as proxy for AI models
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="AI model management permission required",
                )

            # Create the full AI models page with admin layout
            from app.frontend.styles import load_styles

            return Html(
                Head(
                    Title("Admin Dashboard - AI Model Management"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                    load_styles(),
                    # Add HTMX for dynamic updates
                    Script(src="https://unpkg.com/htmx.org@1.9.6"),
                ),
                Body(
                    create_ai_models_page(),
                    cls="font-sans antialiased",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin AI models page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load AI model management page",
            )

    @app.get("/dashboard/admin/system")
    async def admin_system_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin system status page (placeholder)"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # TODO: Implement system status page
            return Html(
                Head(
                    Title("Admin Dashboard - System Status"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                ),
                Body(
                    H1("System Status"),
                    P("System monitoring interface coming soon..."),
                    A(
                        "Back to Users",
                        href="/dashboard/admin/users",
                        style="color: #3b82f6; text-decoration: none;",
                    ),
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin system page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load system status page",
            )

    @app.get("/dashboard/admin/scenarios")
    async def admin_scenarios_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin scenario and content management page"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check scenario management permission
            if not admin_auth_service.has_permission(
                current_user, AdminPermission.MANAGE_SCENARIOS
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Scenario management permission required",
                )

            # Create the full scenario management page with admin layout
            from app.frontend.layout import create_admin_header, create_admin_sidebar
            from app.frontend.styles import load_styles

            return Html(
                Head(
                    Title("Admin Dashboard - Scenario & Content Management"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                    load_styles(),
                    # Add HTMX for dynamic updates
                    Script(src="https://unpkg.com/htmx.org@1.9.6"),
                ),
                Body(
                    # Admin Layout Container
                    Div(
                        create_admin_sidebar("scenarios"),
                        Div(
                            create_admin_header(
                                current_user, "Scenario & Content Management"
                            ),
                            Div(
                                create_scenario_management_page(),
                                cls="p-6",
                            ),
                            cls="flex-1 ml-64 overflow-auto",
                        ),
                        cls="flex min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                    ),
                    cls="font-sans antialiased",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin scenarios page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load scenario management page",
            )

    @app.get("/dashboard/admin/progress-analytics")
    async def admin_progress_analytics_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin progress analytics dashboard page - Task 3.1.8"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check analytics viewing permission
            if not admin_auth_service.has_permission(
                current_user, AdminPermission.VIEW_ANALYTICS
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Analytics viewing permission required",
                )

            # Create the full progress analytics page with admin layout
            from app.frontend.layout import create_admin_header, create_admin_sidebar
            from app.frontend.styles import load_styles

            # Sample analytics data for demonstration
            analytics_data = {
                "conversation_analytics": {
                    "overview": {
                        "total_conversations": 47,
                        "total_conversation_time": 385.5,
                        "average_session_length": 8.2,
                        "total_exchanges": 1247,
                        "average_exchanges_per_session": 26.5,
                    },
                    "performance_metrics": {
                        "average_fluency_score": 0.78,
                        "average_grammar_accuracy": 0.72,
                        "average_pronunciation_clarity": 0.81,
                        "average_vocabulary_complexity": 0.68,
                        "average_confidence_level": 0.74,
                    },
                    "learning_progress": {
                        "total_new_vocabulary": 156,
                        "total_grammar_patterns": 23,
                        "total_cultural_contexts": 18,
                        "average_improvement_trend": 0.12,
                    },
                    "engagement_analysis": {
                        "average_engagement_score": 0.83,
                        "total_hesitations": 134,
                        "total_self_corrections": 67,
                        "hesitation_rate": 0.11,
                    },
                },
                "skill_analytics": {
                    "skill_overview": {
                        "total_skills_tracked": 8,
                        "average_skill_level": 67.3,
                        "overall_mastery_percentage": 72.1,
                        "strongest_skill": "vocabulary",
                        "weakest_skill": "pronunciation",
                    },
                },
                "learning_path": {
                    "path_title": "Comprehensive Language Mastery Path",
                    "path_description": "A balanced approach focusing on conversation skills while strengthening grammar foundations",
                    "confidence_score": 0.85,
                    "expected_success_rate": 0.78,
                    "estimated_duration_weeks": 12,
                    "time_commitment_hours_per_week": 5.5,
                },
                "memory_retention": {
                    "short_term_retention_rate": 0.82,
                    "medium_term_retention_rate": 0.67,
                    "long_term_retention_rate": 0.54,
                    "active_recall_success_rate": 0.73,
                    "average_exposures_to_master": 5.2,
                    "learning_velocity": 12.3,
                    "most_retained_item_types": ["vocabulary", "phrases"],
                },
                "recommendations": {
                    "recommendations": [
                        {
                            "icon": "🎯",
                            "priority": "High Priority",
                            "text": "Focus on pronunciation practice - clarity score could improve with daily phonetic exercises",
                            "action": "Start Pronunciation Course",
                        },
                        {
                            "icon": "📚",
                            "priority": "Medium Priority",
                            "text": "Grammar accuracy needs attention. Review conditional sentences and subjunctive mood patterns",
                            "action": "Review Grammar",
                        },
                        {
                            "icon": "🗣️",
                            "priority": "High Priority",
                            "text": "Practice speaking in more challenging scenarios to build confidence",
                            "action": "Try Advanced Scenarios",
                        },
                    ]
                },
            }

            return Html(
                Head(
                    Title("Admin Dashboard - Progress Analytics"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                    load_styles(),
                    progress_analytics_styles(),
                ),
                Body(
                    # Admin Layout Container
                    Div(
                        create_admin_sidebar("progress-analytics"),
                        Div(
                            create_admin_header(
                                current_user, "Progress Analytics Dashboard"
                            ),
                            Div(
                                progress_analytics_dashboard_page(
                                    user_data=current_user,
                                    analytics_data=analytics_data,
                                ),
                                cls="p-6",
                            ),
                            cls="flex-1 ml-64 overflow-auto",
                        ),
                        cls="flex min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                    ),
                    cls="font-sans antialiased",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin progress analytics page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load progress analytics page",
            )

    @app.get("/dashboard/admin/budget")
    async def admin_budget_page(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ):
        """Admin budget management page"""
        try:
            # Check admin access
            if not admin_auth_service.is_admin_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            # Check budget management permission (using MANAGE_FEATURES as proxy)
            if not admin_auth_service.has_permission(
                current_user, AdminPermission.MANAGE_FEATURES
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Budget management permission required",
                )

            # Create the full budget management page with admin layout
            from app.frontend.layout import create_admin_header, create_admin_sidebar
            from app.frontend.styles import load_styles

            return Html(
                Head(
                    Title("Admin Dashboard - Budget Management"),
                    Meta(charset="utf-8"),
                    Meta(
                        name="viewport", content="width=device-width, initial-scale=1.0"
                    ),
                    load_styles(),
                    # Add HTMX for dynamic updates
                    Script(src="https://unpkg.com/htmx.org@1.9.6"),
                ),
                Body(
                    # Admin Layout Container
                    Div(
                        create_admin_sidebar("budget"),
                        Div(
                            create_admin_header(current_user, "Budget Management"),
                            Div(
                                create_admin_budget_page(),
                                cls="p-6",
                            ),
                            cls="flex-1 ml-64 overflow-auto",
                        ),
                        cls="flex min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900",
                    ),
                    cls="font-sans antialiased",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in admin budget page: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load budget management page",
            )


def register_admin_routes(app, admin_api_router):
    """Register admin routes and API endpoints with the FastHTML app"""

    # Register dashboard routes
    create_admin_routes(app)

    # Note: FastHTML apps don't use include_router like FastAPI
    # The admin API endpoints will be registered separately via the backend API

    logger.info("Admin dashboard routes registered successfully")
