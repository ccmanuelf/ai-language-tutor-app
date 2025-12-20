"""
Content Study Tracking API Endpoints
AI Language Tutor App - Session 129

Provides:
- Start/update/complete study sessions
- Get study history
- Get mastery status
- Get study statistics
- Multi-user isolation
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser as User
from app.services.content_study_tracking_service import ContentStudyTrackingService

router = APIRouter()


# Request/Response Models


class StartStudySessionResponse(BaseModel):
    """Response model for starting a study session"""

    session_id: int
    content_id: str
    started_at: str


class UpdateStudySessionRequest(BaseModel):
    """Request model for updating a study session"""

    materials_studied: Optional[Dict] = Field(None, description="Materials studied")
    items_correct: Optional[int] = Field(None, ge=0, description="Items correct")
    items_total: Optional[int] = Field(None, ge=0, description="Total items")
    completion_percentage: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Completion percentage"
    )


class CompleteStudySessionRequest(BaseModel):
    """Request model for completing a study session"""

    duration_seconds: int = Field(..., ge=0, description="Duration in seconds")
    final_stats: Optional[Dict] = Field(None, description="Final statistics")


class StudySessionResponse(BaseModel):
    """Response model for study session"""

    id: int
    user_id: int
    content_id: str
    started_at: str
    ended_at: Optional[str]
    duration_seconds: Optional[int]
    materials_studied: Dict
    items_correct: int
    items_total: int
    completion_percentage: float


class MasteryStatusResponse(BaseModel):
    """Response model for mastery status"""

    id: int
    user_id: int
    content_id: str
    mastery_level: str
    total_study_time_seconds: int
    total_sessions: int
    last_studied_at: Optional[str]
    items_mastered: int
    items_total: int
    updated_at: str


class StudyStatsResponse(BaseModel):
    """Response model for study statistics"""

    total_sessions: int
    total_study_time_seconds: int
    total_study_time_hours: float
    mastery_breakdown: Dict[str, int]
    total_items_mastered: int
    content_mastered: int
    content_reviewing: int
    content_learning: int
    content_not_started: int


# API Endpoints


@router.post(
    "/{content_id}/study/start",
    response_model=StartStudySessionResponse,
    status_code=201,
)
def start_study_session(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Start a new study session for content

    Args:
        content_id: Content ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Study session ID and metadata

    Raises:
        HTTPException: If content not found or error occurs
    """
    try:
        service = ContentStudyTrackingService(db)

        session_id = service.start_study_session(
            user_id=current_user.id, content_id=content_id
        )

        # Get session details
        from app.models.database import ContentStudySession

        session = (
            db.query(ContentStudySession)
            .filter(ContentStudySession.id == session_id)
            .first()
        )

        return {
            "session_id": session.id,
            "content_id": session.content_id,
            "started_at": session.started_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting study session: {e}"
        )


@router.put("/{content_id}/study/{session_id}")
def update_study_session(
    content_id: str,
    session_id: int,
    request: UpdateStudySessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Update an ongoing study session with progress

    Args:
        content_id: Content ID (for validation)
        session_id: Study session ID
        request: Update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If session not found or access denied
    """
    try:
        service = ContentStudyTrackingService(db)

        updated = service.update_study_session(
            session_id=session_id,
            user_id=current_user.id,
            materials_studied=request.materials_studied,
            items_correct=request.items_correct,
            items_total=request.items_total,
            completion_percentage=request.completion_percentage,
        )

        return {"success": updated, "message": "Study session updated"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating study session: {e}"
        )


@router.post(
    "/{content_id}/study/{session_id}/complete", response_model=MasteryStatusResponse
)
def complete_study_session(
    content_id: str,
    session_id: int,
    request: CompleteStudySessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Complete a study session and update mastery status

    Args:
        content_id: Content ID (for validation)
        session_id: Study session ID
        request: Completion data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated mastery status

    Raises:
        HTTPException: If session not found or error occurs
    """
    try:
        service = ContentStudyTrackingService(db)

        mastery = service.complete_study_session(
            session_id=session_id,
            user_id=current_user.id,
            duration_seconds=request.duration_seconds,
            final_stats=request.final_stats,
        )

        return mastery.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error completing study session: {e}"
        )


@router.get("/{content_id}/study/history", response_model=List[StudySessionResponse])
def get_study_history(
    content_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get study history for content

    Args:
        content_id: Content ID
        limit: Maximum sessions to return (default: 50)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of study sessions

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentStudyTrackingService(db)

        sessions = service.get_study_history(
            content_id=content_id, user_id=current_user.id, limit=limit
        )

        return [session.to_dict() for session in sessions]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving study history: {e}"
        )


@router.get("/{content_id}/mastery", response_model=MasteryStatusResponse)
def get_mastery_status(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get mastery status for content

    Args:
        content_id: Content ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Mastery status

    Raises:
        HTTPException: If not found or error occurs
    """
    try:
        service = ContentStudyTrackingService(db)

        mastery = service.get_mastery_status(
            content_id=content_id, user_id=current_user.id
        )

        if not mastery:
            raise HTTPException(
                status_code=404, detail="No mastery status found for this content"
            )

        return mastery.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving mastery status: {e}"
        )


@router.get("/study/stats", response_model=StudyStatsResponse)
def get_study_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get overall study statistics for user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Study statistics

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentStudyTrackingService(db)

        stats = service.get_user_study_stats(user_id=current_user.id)

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving study stats: {e}"
        )


@router.get("/study/recent", response_model=List[StudySessionResponse])
def get_recent_study_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_primary_db_session),
):
    """
    Get recent study activity for user

    Args:
        limit: Maximum sessions to return (default: 10)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of recent study sessions

    Raises:
        HTTPException: If error occurs
    """
    try:
        service = ContentStudyTrackingService(db)

        sessions = service.get_recent_study_activity(
            user_id=current_user.id, limit=limit
        )

        return [session.to_dict() for session in sessions]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving recent activity: {e}"
        )
