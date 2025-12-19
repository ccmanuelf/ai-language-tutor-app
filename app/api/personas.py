"""
Persona API Endpoints for AI Tutor Personality Management

This module provides RESTful API endpoints for managing user persona preferences,
allowing users to select and customize their AI tutor's teaching personality.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import require_auth
from app.database.config import get_primary_db_session
from app.models.database import User
from app.models.simple_user import SimpleUser
from app.services.persona_service import PersonaType, get_persona_service

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])
logger = logging.getLogger(__name__)


# Request/Response Models
class PersonaInfo(BaseModel):
    """Persona information for API responses"""

    persona_type: str
    name: str
    description: str
    key_traits: List[str]
    best_for: str


class PersonaPreferenceRequest(BaseModel):
    """Request model for setting user persona preference"""

    persona_type: str
    subject: Optional[str] = ""
    learner_level: Optional[str] = "beginner"


class PersonaPreferenceResponse(BaseModel):
    """Response model for persona preference operations"""

    persona_type: str
    subject: str
    learner_level: str
    persona_info: PersonaInfo


class PersonaListResponse(BaseModel):
    """Response model for listing available personas"""

    personas: List[PersonaInfo]
    default_persona: str
    total_count: int


@router.get("/available", response_model=PersonaListResponse)
async def get_available_personas():
    """
    Get list of all available tutor personas

    Returns:
        PersonaListResponse with all available personas and metadata
    """
    try:
        persona_service = get_persona_service()

        # Get all available personas
        personas_data = persona_service.get_available_personas()

        # Convert to PersonaInfo models
        personas = [PersonaInfo(**persona) for persona in personas_data]

        # Get default persona
        default_persona = persona_service.get_default_persona().value

        return PersonaListResponse(
            personas=personas,
            default_persona=default_persona,
            total_count=len(personas),
        )

    except Exception as e:
        logger.error(f"Error retrieving available personas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve available personas"
        )


@router.get("/current", response_model=PersonaPreferenceResponse)
async def get_current_persona(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get current user's persona preference

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        PersonaPreferenceResponse with current persona settings
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.user_id == current_user.user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        persona_service = get_persona_service()

        # Get persona preference from user preferences (or default)
        preferences = user.preferences or {}
        persona_pref = preferences.get("persona_preference", {})

        persona_type = persona_pref.get("persona_type")

        # If no preference set, use default
        if not persona_type:
            persona_type = persona_service.get_default_persona().value

        # Validate persona type
        if not persona_service.validate_persona_type(persona_type):
            logger.warning(f"Invalid persona type in preferences: {persona_type}, using default")
            persona_type = persona_service.get_default_persona().value

        # Get persona metadata
        persona_enum = PersonaType(persona_type)
        persona_metadata = persona_service.get_persona_metadata(persona_enum)

        return PersonaPreferenceResponse(
            persona_type=persona_type,
            subject=persona_pref.get("subject", ""),
            learner_level=persona_pref.get("learner_level", "beginner"),
            persona_info=PersonaInfo(**persona_metadata),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving current persona: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve current persona preference"
        )


@router.put("/preference", response_model=PersonaPreferenceResponse)
async def set_persona_preference(
    request: PersonaPreferenceRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Set user's persona preference

    Args:
        request: Persona preference settings
        current_user: Authenticated user
        db: Database session

    Returns:
        PersonaPreferenceResponse with updated persona settings
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.user_id == current_user.user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        persona_service = get_persona_service()

        # Validate persona type
        if not persona_service.validate_persona_type(request.persona_type):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid persona type: {request.persona_type}"
            )

        # Validate learner level
        valid_levels = ["beginner", "intermediate", "advanced"]
        if request.learner_level not in valid_levels:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid learner level: {request.learner_level}. Must be one of: {', '.join(valid_levels)}"
            )

        # Update user preferences
        if user.preferences is None:
            user.preferences = {}

        user.preferences["persona_preference"] = {
            "persona_type": request.persona_type,
            "subject": request.subject or "",
            "learner_level": request.learner_level,
        }

        # Mark preferences as modified for SQLAlchemy to detect change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "preferences")

        db.commit()
        db.refresh(user)

        # Get persona metadata
        persona_enum = PersonaType(request.persona_type)
        persona_metadata = persona_service.get_persona_metadata(persona_enum)

        logger.info(f"Updated persona preference for user {user.user_id}: {request.persona_type}")

        return PersonaPreferenceResponse(
            persona_type=request.persona_type,
            subject=request.subject or "",
            learner_level=request.learner_level,
            persona_info=PersonaInfo(**persona_metadata),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting persona preference: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update persona preference"
        )


@router.get("/info/{persona_type}", response_model=PersonaInfo)
async def get_persona_info(persona_type: str):
    """
    Get detailed information about a specific persona

    Args:
        persona_type: Persona type identifier

    Returns:
        PersonaInfo with persona details
    """
    try:
        persona_service = get_persona_service()

        # Validate persona type
        if not persona_service.validate_persona_type(persona_type):
            raise HTTPException(
                status_code=404,
                detail=f"Persona type not found: {persona_type}"
            )

        # Get persona metadata
        persona_enum = PersonaType(persona_type)
        persona_metadata = persona_service.get_persona_metadata(persona_enum)

        return PersonaInfo(**persona_metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving persona info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve persona information"
        )


@router.delete("/preference")
async def reset_persona_preference(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Reset user's persona preference to default

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message with default persona
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.user_id == current_user.user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        persona_service = get_persona_service()
        default_persona = persona_service.get_default_persona().value

        # Remove persona preference from user preferences
        if user.preferences and "persona_preference" in user.preferences:
            del user.preferences["persona_preference"]

            # Mark preferences as modified
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(user, "preferences")

            db.commit()

        logger.info(f"Reset persona preference for user {user.user_id} to default")

        return {
            "message": "Persona preference reset to default",
            "default_persona": default_persona,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting persona preference: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to reset persona preference"
        )
