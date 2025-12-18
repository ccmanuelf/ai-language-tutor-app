"""
Learning Session Manager

Manages learning session lifecycle for all learning activities:
- Scenarios
- Content study (documents, YouTube)
- Vocabulary reviews
- Conversation practice
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.database.config import get_primary_db_session
from app.models.database import LearningSession

logger = logging.getLogger(__name__)


class LearningSessionManager:
    """Manager for tracking learning sessions across all activities"""

    def __init__(self, db_session: Optional[Session] = None):
        """Initialize with optional database session"""
        self.db = db_session or get_primary_db_session()
        self.active_sessions: Dict[str, LearningSession] = {}

    async def start_session(
        self,
        user_id: int,
        session_type: str,
        language: str,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new learning session

        Args:
            user_id: User ID
            session_type: Type of session ('scenario', 'content_study', 'vocabulary_review', 'conversation')
            language: Language code
            source_id: Optional source ID (scenario_id, content_id, etc.)
            metadata: Optional session metadata

        Returns:
            Session ID (string)
        """
        try:
            session = LearningSession(
                user_id=user_id,
                session_type=session_type,
                source_id=source_id,
                language=language,
                started_at=datetime.now(),
                session_metadata=metadata or {}
            )

            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            # Track in active sessions
            session_id = str(session.id)
            self.active_sessions[session_id] = session

            logger.info(
                f"Started learning session: id={session_id}, type={session_type}, "
                f"user={user_id}, language={language}"
            )

            return session_id

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to start learning session: {e}")
            raise

    async def update_session(
        self,
        session_id: str,
        items_studied: Optional[int] = None,
        items_correct: Optional[int] = None,
        items_incorrect: Optional[int] = None,
        metadata_update: Optional[Dict[str, Any]] = None
    ) -> LearningSession:
        """
        Update an active learning session with progress

        Args:
            session_id: Session ID
            items_studied: Number of items studied (optional)
            items_correct: Number of correct items (optional)
            items_incorrect: Number of incorrect items (optional)
            metadata_update: Additional metadata to merge (optional)

        Returns:
            Updated LearningSession
        """
        try:
            # Get session from active sessions or database
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
            else:
                session = self.db.query(LearningSession).filter(
                    LearningSession.id == int(session_id)
                ).first()

                if not session:
                    raise ValueError(f"Learning session {session_id} not found")

            # Update metrics
            if items_studied is not None:
                session.items_studied = items_studied
            if items_correct is not None:
                session.items_correct = items_correct
            if items_incorrect is not None:
                session.items_incorrect = items_incorrect

            # Calculate accuracy
            total_items = (session.items_correct or 0) + (session.items_incorrect or 0)
            if total_items > 0:
                session.accuracy_rate = session.items_correct / total_items

            # Merge metadata
            if metadata_update:
                current_metadata = session.session_metadata or {}
                current_metadata.update(metadata_update)
                session.session_metadata = current_metadata
                # Mark JSON field as modified for SQLAlchemy change tracking
                flag_modified(session, 'session_metadata')

            self.db.commit()
            self.db.refresh(session)

            logger.debug(f"Updated learning session {session_id}")

            return session

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update learning session: {e}")
            raise

    async def complete_session(self, session_id: str) -> LearningSession:
        """
        Complete and finalize a learning session

        Args:
            session_id: Session ID

        Returns:
            Completed LearningSession
        """
        try:
            # Get session
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
            else:
                session = self.db.query(LearningSession).filter(
                    LearningSession.id == int(session_id)
                ).first()

                if not session:
                    raise ValueError(f"Learning session {session_id} not found")

            # Finalize session
            session.ended_at = datetime.now()

            # Calculate duration (started_at is never NULL due to DB constraint)
            duration = (session.ended_at - session.started_at).total_seconds()
            session.duration_seconds = int(duration)

            # Final accuracy calculation
            total_items = (session.items_correct or 0) + (session.items_incorrect or 0)
            if total_items > 0:
                session.accuracy_rate = session.items_correct / total_items

            self.db.commit()
            self.db.refresh(session)

            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            logger.info(
                f"Completed learning session {session_id}: "
                f"duration={session.duration_seconds}s, "
                f"accuracy={session.accuracy_rate:.2%}"
            )

            return session

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to complete learning session: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[LearningSession]:
        """
        Get a learning session by ID

        Args:
            session_id: Session ID

        Returns:
            LearningSession or None if not found
        """
        try:
            # Check active sessions first
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]

            # Query database
            session = self.db.query(LearningSession).filter(
                LearningSession.id == int(session_id)
            ).first()

            return session

        except Exception as e:
            logger.error(f"Failed to get learning session: {e}")
            return None

    async def get_user_sessions(
        self,
        user_id: int,
        session_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 10
    ) -> list[LearningSession]:
        """
        Get recent learning sessions for a user

        Args:
            user_id: User ID
            session_type: Optional filter by session type
            language: Optional filter by language
            limit: Maximum number of sessions to return

        Returns:
            List of LearningSession objects
        """
        try:
            query = self.db.query(LearningSession).filter(
                LearningSession.user_id == user_id
            )

            if session_type:
                query = query.filter(LearningSession.session_type == session_type)

            if language:
                query = query.filter(LearningSession.language == language)

            sessions = query.order_by(
                LearningSession.started_at.desc()
            ).limit(limit).all()

            return sessions

        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []


# Module-level manager instance (singleton pattern)
_session_manager: Optional[LearningSessionManager] = None


def get_session_manager() -> LearningSessionManager:
    """Get or create the global learning session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = LearningSessionManager()
    return _session_manager


# Convenience functions
async def start_learning_session(
    user_id: int,
    session_type: str,
    language: str,
    source_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Convenience function to start a learning session"""
    manager = get_session_manager()
    return await manager.start_session(user_id, session_type, language, source_id, metadata)


async def complete_learning_session(session_id: str) -> LearningSession:
    """Convenience function to complete a learning session"""
    manager = get_session_manager()
    return await manager.complete_session(session_id)


async def update_learning_session(
    session_id: str,
    items_studied: Optional[int] = None,
    items_correct: Optional[int] = None,
    items_incorrect: Optional[int] = None,
    metadata_update: Optional[Dict[str, Any]] = None
) -> LearningSession:
    """Convenience function to update a learning session"""
    manager = get_session_manager()
    return await manager.update_session(
        session_id, items_studied, items_correct, items_incorrect, metadata_update
    )
