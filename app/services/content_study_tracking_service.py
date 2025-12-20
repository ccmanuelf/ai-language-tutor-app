"""
Content Study Tracking Service
AI Language Tutor App - Session 129

Provides:
- Track study sessions for content
- Calculate mastery levels
- Aggregate study statistics
- Monitor learning progress
- Multi-user isolation

This service tracks how users interact with content and determines
mastery levels based on study time, session count, and correctness.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.database import (
    ContentMasteryStatus,
    ContentStudySession,
    ProcessedContent,
)

logger = logging.getLogger(__name__)


class ContentStudyTrackingService:
    """Service for tracking content study sessions and mastery"""

    # Mastery level thresholds
    MASTERY_THRESHOLDS = {
        "not_started": {"sessions": 0, "mastery_pct": 0},
        "learning": {"sessions": 1, "mastery_pct": 0},
        "reviewing": {"sessions": 3, "mastery_pct": 50},
        "mastered": {"sessions": 5, "mastery_pct": 80},
    }

    def __init__(self, db: Session):
        """
        Initialize the service with a database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def start_study_session(self, user_id: int, content_id: str) -> int:
        """
        Start a new study session for content

        Args:
            user_id: User ID
            content_id: Content ID

        Returns:
            Study session ID

        Raises:
            ValueError: If content not found or not owned by user
        """
        # Verify content exists and user owns it
        content = (
            self.db.query(ProcessedContent)
            .filter(
                and_(
                    ProcessedContent.content_id == content_id,
                    ProcessedContent.user_id == user_id,
                )
            )
            .first()
        )

        if not content:
            raise ValueError(f"Content {content_id} not found or not owned by user")

        # Create study session
        session = ContentStudySession(
            user_id=user_id,
            content_id=content_id,
            started_at=datetime.now(),
            materials_studied={},
            items_correct=0,
            items_total=0,
            completion_percentage=0.0,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        logger.info(
            f"Started study session {session.id} for content {content_id}, user {user_id}"
        )
        return session.id

    def update_study_session(
        self,
        session_id: int,
        user_id: int,
        materials_studied: Optional[Dict] = None,
        items_correct: Optional[int] = None,
        items_total: Optional[int] = None,
        completion_percentage: Optional[float] = None,
    ) -> bool:
        """
        Update an ongoing study session with progress

        Args:
            session_id: Study session ID
            user_id: User ID (for ownership verification)
            materials_studied: Dictionary of materials studied
            items_correct: Number of items answered correctly
            items_total: Total number of items attempted
            completion_percentage: Completion percentage (0-100)

        Returns:
            True if updated successfully

        Raises:
            ValueError: If session not found
            PermissionError: If user doesn't own the session
        """
        session = (
            self.db.query(ContentStudySession)
            .filter(ContentStudySession.id == session_id)
            .first()
        )

        if not session:
            raise ValueError(f"Study session {session_id} not found")

        if session.user_id != user_id:
            raise PermissionError(
                f"User {user_id} does not own study session {session_id}"
            )

        # Update fields if provided
        if materials_studied is not None:
            session.materials_studied = materials_studied

        if items_correct is not None:
            session.items_correct = items_correct

        if items_total is not None:
            session.items_total = items_total

        if completion_percentage is not None:
            session.completion_percentage = min(100.0, max(0.0, completion_percentage))

        self.db.commit()

        logger.info(f"Updated study session {session_id}")
        return True

    def complete_study_session(
        self,
        session_id: int,
        user_id: int,
        duration_seconds: int,
        final_stats: Optional[Dict] = None,
    ) -> ContentMasteryStatus:
        """
        Complete a study session and update mastery status

        Args:
            session_id: Study session ID
            user_id: User ID (for ownership verification)
            duration_seconds: Total duration of study session in seconds
            final_stats: Final statistics (optional)

        Returns:
            Updated ContentMasteryStatus object

        Raises:
            ValueError: If session not found or already completed
            PermissionError: If user doesn't own the session
        """
        session = (
            self.db.query(ContentStudySession)
            .filter(ContentStudySession.id == session_id)
            .first()
        )

        if not session:
            raise ValueError(f"Study session {session_id} not found")

        if session.user_id != user_id:
            raise PermissionError(
                f"User {user_id} does not own study session {session_id}"
            )

        if session.ended_at is not None:
            raise ValueError(f"Study session {session_id} already completed")

        # Update session end info
        session.ended_at = datetime.now()
        session.duration_seconds = duration_seconds

        # Update final stats if provided
        if final_stats:
            if "items_correct" in final_stats:
                session.items_correct = final_stats["items_correct"]
            if "items_total" in final_stats:
                session.items_total = final_stats["items_total"]
            if "completion_percentage" in final_stats:
                session.completion_percentage = final_stats["completion_percentage"]

        self.db.commit()

        # Update mastery status
        mastery = self._update_mastery_status(
            user_id,
            session.content_id,
            duration_seconds,
            session.items_correct,
            session.items_total,
        )

        logger.info(
            f"Completed study session {session_id}, mastery level: {mastery.mastery_level}"
        )
        return mastery

    def _update_mastery_status(
        self,
        user_id: int,
        content_id: str,
        duration_seconds: int,
        items_correct: int,
        items_total: int,
    ) -> ContentMasteryStatus:
        """
        Update or create mastery status for content

        Args:
            user_id: User ID
            content_id: Content ID
            duration_seconds: Session duration in seconds
            items_correct: Number of correct items
            items_total: Total number of items

        Returns:
            ContentMasteryStatus object
        """
        # Get existing mastery status or create new
        mastery = (
            self.db.query(ContentMasteryStatus)
            .filter(
                and_(
                    ContentMasteryStatus.user_id == user_id,
                    ContentMasteryStatus.content_id == content_id,
                )
            )
            .first()
        )

        if not mastery:
            mastery = ContentMasteryStatus(
                user_id=user_id,
                content_id=content_id,
                mastery_level="not_started",
                total_study_time_seconds=0,
                total_sessions=0,
                items_mastered=0,
                items_total=0,
            )
            self.db.add(mastery)

        # Update statistics
        mastery.total_study_time_seconds += duration_seconds
        mastery.total_sessions += 1
        mastery.last_studied_at = datetime.now()

        # Update items mastered (cumulative, not per-session)
        if items_total > 0:
            # Use the higher of current total or new total
            mastery.items_total = max(mastery.items_total, items_total)
            # Update items mastered based on current session performance
            # This is a simplified approach - could be more sophisticated
            mastery.items_mastered = max(mastery.items_mastered, items_correct)

        # Calculate new mastery level
        mastery.mastery_level = self.calculate_mastery_level(
            mastery.total_sessions,
            mastery.items_mastered,
            mastery.items_total,
            mastery.last_studied_at,
        )

        mastery.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(mastery)

        return mastery

    def calculate_mastery_level(
        self,
        session_count: int,
        items_mastered: int,
        items_total: int,
        last_studied: Optional[datetime] = None,
    ) -> str:
        """
        Calculate mastery level based on statistics

        Mastery Levels:
        - not_started: 0 sessions
        - learning: < 50% items mastered, < 3 sessions
        - reviewing: 50-80% items mastered, 3+ sessions
        - mastered: > 80% items mastered, 5+ sessions, recent review

        Args:
            session_count: Total number of study sessions
            items_mastered: Number of items mastered
            items_total: Total number of items
            last_studied: Last study date

        Returns:
            Mastery level string
        """
        if session_count == 0:
            return "not_started"

        # Calculate mastery percentage
        mastery_pct = 0.0
        if items_total > 0:
            mastery_pct = (items_mastered / items_total) * 100

        # Determine level based on thresholds
        if session_count >= 5 and mastery_pct > 80:
            return "mastered"
        elif session_count >= 3 and mastery_pct >= 50:
            return "reviewing"
        else:
            return "learning"

    def get_study_history(
        self, content_id: str, user_id: int, limit: int = 50
    ) -> List[ContentStudySession]:
        """
        Get study history for content

        Args:
            content_id: Content ID
            user_id: User ID
            limit: Maximum number of sessions to return (default: 50)

        Returns:
            List of ContentStudySession objects
        """
        sessions = (
            self.db.query(ContentStudySession)
            .filter(
                and_(
                    ContentStudySession.content_id == content_id,
                    ContentStudySession.user_id == user_id,
                )
            )
            .order_by(desc(ContentStudySession.started_at))
            .limit(limit)
            .all()
        )

        logger.info(
            f"Retrieved {len(sessions)} study sessions for content {content_id}"
        )
        return sessions

    def get_mastery_status(
        self, content_id: str, user_id: int
    ) -> Optional[ContentMasteryStatus]:
        """
        Get mastery status for content

        Args:
            content_id: Content ID
            user_id: User ID

        Returns:
            ContentMasteryStatus object or None if not started
        """
        mastery = (
            self.db.query(ContentMasteryStatus)
            .filter(
                and_(
                    ContentMasteryStatus.content_id == content_id,
                    ContentMasteryStatus.user_id == user_id,
                )
            )
            .first()
        )

        if mastery:
            logger.info(
                f"Retrieved mastery status for content {content_id}: {mastery.mastery_level}"
            )
        else:
            logger.info(f"No mastery status found for content {content_id}")

        return mastery

    def get_user_study_stats(self, user_id: int) -> Dict:
        """
        Get overall study statistics for user

        Args:
            user_id: User ID

        Returns:
            Dictionary with study statistics
        """
        # Count total sessions
        total_sessions = (
            self.db.query(func.count(ContentStudySession.id))
            .filter(ContentStudySession.user_id == user_id)
            .scalar()
            or 0
        )

        # Sum total study time
        total_study_time = (
            self.db.query(func.sum(ContentStudySession.duration_seconds))
            .filter(
                and_(
                    ContentStudySession.user_id == user_id,
                    ContentStudySession.ended_at.isnot(None),
                )
            )
            .scalar()
            or 0
        )

        # Count mastery levels
        mastery_counts = (
            self.db.query(
                ContentMasteryStatus.mastery_level,
                func.count(ContentMasteryStatus.id),
            )
            .filter(ContentMasteryStatus.user_id == user_id)
            .group_by(ContentMasteryStatus.mastery_level)
            .all()
        )

        mastery_breakdown = {level: 0 for level in self.MASTERY_THRESHOLDS.keys()}
        for level, count in mastery_counts:
            mastery_breakdown[level] = count

        # Get total items mastered
        total_items_mastered = (
            self.db.query(func.sum(ContentMasteryStatus.items_mastered))
            .filter(ContentMasteryStatus.user_id == user_id)
            .scalar()
            or 0
        )

        stats = {
            "total_sessions": total_sessions,
            "total_study_time_seconds": total_study_time,
            "total_study_time_hours": round(total_study_time / 3600, 2),
            "mastery_breakdown": mastery_breakdown,
            "total_items_mastered": total_items_mastered,
            "content_mastered": mastery_breakdown.get("mastered", 0),
            "content_reviewing": mastery_breakdown.get("reviewing", 0),
            "content_learning": mastery_breakdown.get("learning", 0),
            "content_not_started": mastery_breakdown.get("not_started", 0),
        }

        logger.info(f"Retrieved study stats for user {user_id}")
        return stats

    def get_recent_study_activity(
        self, user_id: int, limit: int = 10
    ) -> List[ContentStudySession]:
        """
        Get recent study activity for user

        Args:
            user_id: User ID
            limit: Maximum number of sessions to return (default: 10)

        Returns:
            List of recent ContentStudySession objects
        """
        sessions = (
            self.db.query(ContentStudySession)
            .filter(ContentStudySession.user_id == user_id)
            .order_by(desc(ContentStudySession.started_at))
            .limit(limit)
            .all()
        )

        logger.info(f"Retrieved {len(sessions)} recent sessions for user {user_id}")
        return sessions
