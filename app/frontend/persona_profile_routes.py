"""
Persona Profile Route Handlers
AI Language Tutor App - Personal Family Educational Tool

This module provides FastHTML route handlers for the persona selection interface,
allowing users to view and select their AI tutor's teaching personality.
"""

import logging
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fasthtml.common import *
from sqlalchemy.orm import Session

from app.database.config import get_primary_db_session
from app.frontend.layout import create_footer, create_header
from app.frontend.persona_selection import create_persona_selection_section
from app.frontend.styles import load_styles
from app.models.database import User
from app.services.auth import get_current_user
from app.services.persona_service import get_persona_service

logger = logging.getLogger(__name__)


def create_persona_profile_routes(app):
    """Create persona profile routes for the FastHTML app"""

    @app.get("/profile/persona")
    async def persona_profile_page():
        """Persona selection page"""
        try:
            # TODO: Add proper authentication when session management is implemented
            # For now, use demo user ID
            user_id = 1
            db = get_primary_db_session()

            # Get persona service
            persona_service = get_persona_service()

            # Get all available personas
            available_personas = persona_service.get_available_personas()

            # Get user from database
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )

                # Get user's persona preference
                user_preferences = user.preferences or {}
                persona_pref = user_preferences.get("persona_preference", {})

                # Extract current persona settings
                persona_type_str = persona_pref.get("persona_type")
                subject = persona_pref.get("subject", "")
                learner_level = persona_pref.get("learner_level", "beginner")

                # Determine current persona
                if persona_type_str and persona_service.validate_persona_type(
                    persona_type_str
                ):
                    current_persona_metadata = persona_service.get_persona_metadata(
                        persona_type_str
                    )
                else:
                    # Use default persona
                    default_type = persona_service.get_default_persona()
                    current_persona_metadata = persona_service.get_persona_metadata(
                        default_type.value
                    )
                    persona_type_str = default_type.value

                # Add persona_type to metadata for selection highlighting
                current_persona_metadata["persona_type"] = persona_type_str

                # Prepare current customization
                current_customization = {
                    "subject": subject,
                    "learner_level": learner_level,
                }

                # Create the full persona profile page
                return Html(
                    Head(
                        Title("AI Tutor Persona - Profile Settings"),
                        Meta(charset="utf-8"),
                        Meta(
                            name="viewport",
                            content="width=device-width, initial-scale=1.0",
                        ),
                        load_styles(),
                    ),
                    Body(
                        create_header("profile"),
                        Main(
                            Div(
                                # Page header
                                Div(
                                    H1(
                                        "Profile Settings",
                                        cls="text-3xl font-bold text-white mb-2",
                                    ),
                                    P(
                                        "Personalize your AI tutor and learning experience",
                                        cls="text-gray-300 text-sm mb-6",
                                    ),
                                    A(
                                        "← Back to Profile",
                                        href="/profile",
                                        cls="text-purple-400 hover:text-purple-300 text-sm",
                                    ),
                                    cls="mb-8",
                                ),
                                # Persona selection section
                                create_persona_selection_section(
                                    available_personas=available_personas,
                                    current_persona=current_persona_metadata,
                                    current_customization=current_customization,
                                ),
                                # Additional settings sections can be added here
                                cls="container mx-auto px-4 py-8 max-w-6xl",
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
            logger.error(f"Error in persona profile page: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load persona profile page",
            )


def register_persona_profile_routes(app):
    """Register persona profile routes with the FastHTML app"""
    create_persona_profile_routes(app)
    logger.info("Persona profile routes registered successfully")
