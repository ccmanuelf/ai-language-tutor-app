"""
Tutor Modes API for AI Language Tutor App

This module provides RESTful API endpoints for Fluently-style tutor modes:
- Mode discovery and selection
- Session management (start, status, end)
- AI conversation generation per mode
- Progress tracking and analytics
- Multi-language support

All 6 tutor modes supported:
1. Chit-chat free talking
2. One-on-One interview simulation
3. Deadline negotiations
4. Teacher mode
5. Vocabulary builder
6. Open session talking
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field

from app.services.tutor_mode_manager import (
    tutor_mode_manager,
    TutorMode,
    DifficultyLevel,
)
from app.services.auth import get_current_user
from app.models.database import User

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/tutor-modes", tags=["tutor-modes"])


# Request/Response Models
class StartTutorSessionRequest(BaseModel):
    """Request to start a tutor mode session"""

    mode: str = Field(
        ..., description="Tutor mode (chit_chat, interview_simulation, etc.)"
    )
    language: str = Field(..., description="Target language code (en, es, fr, etc.)")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    topic: Optional[str] = Field(None, description="Topic for modes that require it")


class TutorSessionResponse(BaseModel):
    """Response for tutor session operations"""

    session_id: str
    mode: str
    language: str
    topic: Optional[str]
    difficulty: str
    status: str
    conversation_starter: Optional[str] = None
    message: str


class TutorConversationRequest(BaseModel):
    """Request for tutor conversation"""

    session_id: str = Field(..., description="Active tutor session ID")
    message: str = Field(..., description="User message")
    context_messages: Optional[List[Dict[str, str]]] = Field(
        None, description="Previous conversation context"
    )


class TutorConversationResponse(BaseModel):
    """Response from tutor conversation"""

    response: str
    mode: str
    correction_approach: str
    session_progress: Dict[str, Any]
    suggestions: Optional[List[str]] = None


class TutorModeInfo(BaseModel):
    """Information about a tutor mode"""

    mode: str
    name: str
    description: str
    category: str
    requires_topic: bool


class SessionInfo(BaseModel):
    """Information about an active session"""

    session_id: str
    mode: str
    language: str
    topic: Optional[str]
    difficulty: str
    start_time: str
    interaction_count: int
    progress_metrics: Dict[str, Any]


@router.get("/available", response_model=List[TutorModeInfo])
async def get_available_modes(
    current_user: User = Depends(get_current_user),
) -> List[TutorModeInfo]:
    """
    Get list of available tutor modes

    Returns all 6 Fluently-style tutor modes with descriptions and requirements.
    """
    try:
        modes = tutor_mode_manager.get_available_modes()
        return [TutorModeInfo(**mode) for mode in modes]

    except Exception as e:
        logger.error(f"Error getting available modes: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve available modes"
        )


@router.post("/session/start", response_model=TutorSessionResponse)
async def start_tutor_session(
    request: StartTutorSessionRequest, current_user: User = Depends(get_current_user)
) -> TutorSessionResponse:
    """
    Start a new tutor mode session

    Creates a new session with the specified mode, language, and settings.
    Returns session ID and conversation starter.
    """
    try:
        # Validate mode
        try:
            mode = TutorMode(request.mode)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid tutor mode: {request.mode}"
            )

        # Validate difficulty
        try:
            difficulty = DifficultyLevel(request.difficulty)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid difficulty level: {request.difficulty}",
            )

        # Start session
        session_id = tutor_mode_manager.start_tutor_session(
            user_id=str(current_user.id),
            mode=mode,
            language=request.language,
            difficulty=difficulty,
            topic=request.topic,
        )

        # Get conversation starter
        conversation_starter = tutor_mode_manager.get_conversation_starter(session_id)

        logger.info(f"Started tutor session {session_id} for user {current_user.id}")

        return TutorSessionResponse(
            session_id=session_id,
            mode=request.mode,
            language=request.language,
            topic=request.topic,
            difficulty=request.difficulty,
            status="active",
            conversation_starter=conversation_starter,
            message=f"Tutor session started successfully in {mode.value} mode",
        )

    except ValueError as e:
        logger.error(f"Validation error starting tutor session: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting tutor session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start tutor session")


@router.post("/conversation", response_model=TutorConversationResponse)
async def tutor_conversation(
    request: TutorConversationRequest, current_user: User = Depends(get_current_user)
) -> TutorConversationResponse:
    """
    Generate AI response in tutor mode conversation

    Processes user message and generates appropriate tutor response
    based on the active session's mode and settings.
    """
    try:
        # Validate session exists
        session_info = tutor_mode_manager.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Tutor session not found")

        # Generate tutor response
        response_data = await tutor_mode_manager.generate_tutor_response(
            session_id=request.session_id,
            user_message=request.message,
            context_messages=request.context_messages or [],
        )

        return TutorConversationResponse(
            response=response_data["response"],
            mode=response_data["mode"],
            correction_approach=response_data["correction_approach"],
            session_progress=response_data["session_progress"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tutor conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate tutor response")


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(
    session_id: str, current_user: User = Depends(get_current_user)
) -> SessionInfo:
    """
    Get information about an active tutor session

    Returns session details, progress, and current status.
    """
    try:
        session_info = tutor_mode_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Tutor session not found")

        return SessionInfo(**session_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve session information"
        )


@router.post("/session/{session_id}/end")
async def end_tutor_session(
    session_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    End an active tutor session

    Terminates the session and returns summary statistics.
    """
    try:
        session_summary = tutor_mode_manager.end_tutor_session(session_id)

        return {
            "success": True,
            "message": "Tutor session ended successfully",
            "summary": session_summary,
        }

    except ValueError as e:
        logger.error(f"Error ending tutor session: {e}")
        raise HTTPException(status_code=404, detail="Tutor session not found")
    except Exception as e:
        logger.error(f"Error ending tutor session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end tutor session")


@router.get("/modes/{mode}/details")
async def get_mode_details(
    mode: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific tutor mode

    Returns comprehensive details about mode features, requirements, and examples.
    """
    try:
        # Validate mode
        try:
            tutor_mode = TutorMode(mode)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tutor mode: {mode}")

        mode_config = tutor_mode_manager.modes[tutor_mode]

        return {
            "mode": mode,
            "name": mode_config.name,
            "description": mode_config.description,
            "category": mode_config.category.value,
            "requires_topic": mode_config.requires_topic_input,
            "correction_approach": mode_config.correction_approach,
            "focus_areas": mode_config.focus_areas,
            "success_criteria": mode_config.success_criteria,
            "example_interactions": mode_config.example_interactions[
                :2
            ],  # Limit examples
            "difficulty_levels": list(DifficultyLevel.__members__.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mode details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mode details")


@router.get("/analytics")
async def get_tutor_analytics(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get analytics and statistics about tutor mode usage

    Returns system-wide tutor mode analytics and user session statistics.
    """
    try:
        analytics = tutor_mode_manager.get_mode_analytics()

        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting tutor analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.post("/session/{session_id}/feedback")
async def submit_session_feedback(
    session_id: str,
    feedback: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Submit feedback for a tutor session

    Allows users to provide feedback on tutor mode experience for improvements.
    """
    try:
        # Validate session exists (or existed)
        session_info = tutor_mode_manager.get_session_info(session_id)
        if not session_info:
            # For ended sessions, we might want to store feedback differently
            logger.warning(f"Feedback submitted for non-active session {session_id}")

        # Store feedback (in a real implementation, this would go to a database)
        _feedback_data = {  # noqa: F841 - Intentional placeholder
            "session_id": session_id,
            "user_id": current_user.id,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Received feedback for session {session_id}: {feedback}")

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": session_id + "_feedback",  # Simple ID for demo
        }

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/categories")
async def get_mode_categories() -> Dict[str, Any]:
    """
    Get tutor mode categories and their descriptions

    Returns information about the different categories of tutor modes available.
    """
    try:
        categories = {
            "casual": {
                "name": "Casual Practice",
                "description": "Relaxed conversation practice with minimal pressure",
                "modes": ["chit_chat", "open_session"],
            },
            "professional": {
                "name": "Professional Communication",
                "description": "Business and professional language skills",
                "modes": ["interview_simulation", "deadline_negotiations"],
            },
            "educational": {
                "name": "Structured Learning",
                "description": "Systematic language instruction and skill building",
                "modes": ["teacher_mode", "vocabulary_builder"],
            },
        }

        return {"success": True, "categories": categories}

    except Exception as e:
        logger.error(f"Error getting mode categories: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve mode categories"
        )
