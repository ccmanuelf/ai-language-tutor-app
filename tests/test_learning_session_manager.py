"""
Unit Tests for Learning Session Manager
AI Language Tutor App - Session 129A

Tests:
- Session creation (start_session)
- Session updates (update_session)
- Session completion (complete_session)
- Session retrieval (get_session)
- User session queries (get_user_sessions)
- Error handling and edge cases
- Convenience functions
- Singleton pattern
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.database.config import get_primary_db_session
from app.models.database import LearningSession
from app.services.learning_session_manager import (
    LearningSessionManager,
    get_session_manager,
    start_learning_session,
    complete_learning_session,
    update_learning_session,
)


class TestLearningSessionManager:
    """Test suite for LearningSessionManager class"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.db = get_primary_db_session()
        self.manager = LearningSessionManager(self.db)

        yield

        # Cleanup
        self.db.close()

    @pytest.mark.asyncio
    async def test_start_session_basic(self):
        """Test starting a basic learning session"""
        session_id = await self.manager.start_session(
            user_id=1,
            session_type="scenario",
            language="es"
        )

        assert session_id is not None
        assert session_id.isdigit()

        # Verify session in active sessions
        assert session_id in self.manager.active_sessions

        # Verify session in database
        session = self.db.query(LearningSession).filter(
            LearningSession.id == int(session_id)
        ).first()

        assert session is not None
        assert session.user_id == 1
        assert session.session_type == "scenario"
        assert session.language == "es"
        assert session.started_at is not None
        assert session.ended_at is None

    @pytest.mark.asyncio
    async def test_start_session_with_source_and_metadata(self):
        """Test starting a session with source ID and metadata"""
        metadata = {
            "difficulty": "intermediate",
            "scenario_name": "Restaurant Ordering"
        }

        session_id = await self.manager.start_session(
            user_id=2,
            session_type="scenario",
            language="fr",
            source_id="scenario_123",
            metadata=metadata
        )

        session = await self.manager.get_session(session_id)

        assert session.source_id == "scenario_123"
        assert session.session_metadata == metadata
        assert session.session_metadata["difficulty"] == "intermediate"

    @pytest.mark.asyncio
    async def test_start_session_all_types(self):
        """Test starting sessions of all types"""
        session_types = [
            "scenario",
            "content_study",
            "vocabulary_review",
            "conversation"
        ]

        for session_type in session_types:
            session_id = await self.manager.start_session(
                user_id=3,
                session_type=session_type,
                language="de"
            )

            session = await self.manager.get_session(session_id)
            assert session.session_type == session_type

    @pytest.mark.asyncio
    async def test_update_session_metrics(self):
        """Test updating session metrics"""
        # Start session
        session_id = await self.manager.start_session(
            user_id=4,
            session_type="vocabulary_review",
            language="es"
        )

        # Update with metrics
        updated_session = await self.manager.update_session(
            session_id=session_id,
            items_studied=10,
            items_correct=8,
            items_incorrect=2
        )

        assert updated_session.items_studied == 10
        assert updated_session.items_correct == 8
        assert updated_session.items_incorrect == 2
        assert updated_session.accuracy_rate == 0.8  # 8/10

    @pytest.mark.asyncio
    async def test_update_session_accuracy_calculation(self):
        """Test accuracy rate calculation"""
        session_id = await self.manager.start_session(
            user_id=5,
            session_type="scenario",
            language="fr"
        )

        # Perfect accuracy
        await self.manager.update_session(
            session_id=session_id,
            items_correct=10,
            items_incorrect=0
        )
        session = await self.manager.get_session(session_id)
        assert session.accuracy_rate == 1.0

        # Zero accuracy
        await self.manager.update_session(
            session_id=session_id,
            items_correct=0,
            items_incorrect=10
        )
        session = await self.manager.get_session(session_id)
        assert session.accuracy_rate == 0.0

        # Partial accuracy
        await self.manager.update_session(
            session_id=session_id,
            items_correct=7,
            items_incorrect=3
        )
        session = await self.manager.get_session(session_id)
        assert session.accuracy_rate == 0.7

    @pytest.mark.asyncio
    async def test_update_session_metadata(self):
        """Test updating session metadata"""
        session_id = await self.manager.start_session(
            user_id=6,
            session_type="content_study",
            language="de",
            metadata={"initial": "value"}
        )

        # Update metadata
        await self.manager.update_session(
            session_id=session_id,
            metadata_update={"new_key": "new_value", "progress": 50}
        )

        session = await self.manager.get_session(session_id)
        assert session.session_metadata["initial"] == "value"
        assert session.session_metadata["new_key"] == "new_value"
        assert session.session_metadata["progress"] == 50

    @pytest.mark.asyncio
    async def test_update_session_not_in_active(self):
        """Test updating a session not in active sessions"""
        # Start session
        session_id = await self.manager.start_session(
            user_id=7,
            session_type="scenario",
            language="es"
        )

        # Remove from active sessions
        del self.manager.active_sessions[session_id]

        # Should still be able to update from database
        updated_session = await self.manager.update_session(
            session_id=session_id,
            items_studied=5
        )

        assert updated_session.items_studied == 5

    @pytest.mark.asyncio
    async def test_update_session_not_found(self):
        """Test updating a non-existent session"""
        with pytest.raises(ValueError, match="Learning session .* not found"):
            await self.manager.update_session(
                session_id="999999",
                items_studied=5
            )

    @pytest.mark.asyncio
    async def test_complete_session_basic(self):
        """Test completing a session"""
        # Start session
        session_id = await self.manager.start_session(
            user_id=8,
            session_type="scenario",
            language="fr"
        )

        # Complete session
        completed_session = await self.manager.complete_session(session_id)

        assert completed_session.ended_at is not None
        assert completed_session.duration_seconds is not None
        assert completed_session.duration_seconds >= 0  # Can be 0 in fast tests

        # Should be removed from active sessions
        assert session_id not in self.manager.active_sessions

    @pytest.mark.asyncio
    async def test_complete_session_with_metrics(self):
        """Test completing a session with metrics"""
        # Start session
        session_id = await self.manager.start_session(
            user_id=9,
            session_type="vocabulary_review",
            language="de"
        )

        # Update with metrics
        await self.manager.update_session(
            session_id=session_id,
            items_studied=20,
            items_correct=18,
            items_incorrect=2
        )

        # Complete session
        completed_session = await self.manager.complete_session(session_id)

        assert completed_session.items_studied == 20
        assert completed_session.items_correct == 18
        assert completed_session.items_incorrect == 2
        assert completed_session.accuracy_rate == 0.9
        assert completed_session.duration_seconds >= 0  # Can be 0 in fast tests

    @pytest.mark.asyncio
    async def test_complete_session_not_in_active(self):
        """Test completing a session not in active sessions"""
        # Start session
        session_id = await self.manager.start_session(
            user_id=10,
            session_type="scenario",
            language="es"
        )

        # Remove from active sessions
        del self.manager.active_sessions[session_id]

        # Should still be able to complete from database
        completed_session = await self.manager.complete_session(session_id)

        assert completed_session.ended_at is not None

    @pytest.mark.asyncio
    async def test_complete_session_not_found(self):
        """Test completing a non-existent session"""
        with pytest.raises(ValueError, match="Learning session .* not found"):
            await self.manager.complete_session("999999")


    @pytest.mark.asyncio
    async def test_get_session_from_active(self):
        """Test retrieving a session from active sessions"""
        # Start session
        session_id = await self.manager.start_session(
            user_id=11,
            session_type="scenario",
            language="fr"
        )

        # Get session
        session = await self.manager.get_session(session_id)

        assert session is not None
        assert session.id == int(session_id)
        assert session.user_id == 11

    @pytest.mark.asyncio
    async def test_get_session_from_database(self):
        """Test retrieving a session from database"""
        # Start and complete session
        session_id = await self.manager.start_session(
            user_id=12,
            session_type="scenario",
            language="de"
        )

        await self.manager.complete_session(session_id)

        # Session should be removed from active
        assert session_id not in self.manager.active_sessions

        # Should still be retrievable from database
        session = await self.manager.get_session(session_id)

        assert session is not None
        assert session.id == int(session_id)
        assert session.ended_at is not None

    @pytest.mark.asyncio
    async def test_get_session_not_found(self):
        """Test retrieving a non-existent session"""
        session = await self.manager.get_session("999999")
        assert session is None

    @pytest.mark.asyncio
    async def test_get_user_sessions_basic(self):
        """Test retrieving user sessions"""
        user_id = 13

        # Create multiple sessions
        for i in range(3):
            session_id = await self.manager.start_session(
                user_id=user_id,
                session_type="scenario",
                language="es"
            )
            await self.manager.complete_session(session_id)

        # Retrieve sessions
        sessions = await self.manager.get_user_sessions(user_id)

        assert len(sessions) >= 3
        assert all(s.user_id == user_id for s in sessions)

    @pytest.mark.asyncio
    async def test_get_user_sessions_filter_by_type(self):
        """Test filtering sessions by type"""
        user_id = 14

        # Create sessions of different types
        await self.manager.start_session(
            user_id=user_id,
            session_type="scenario",
            language="es"
        )
        await self.manager.start_session(
            user_id=user_id,
            session_type="vocabulary_review",
            language="es"
        )
        await self.manager.start_session(
            user_id=user_id,
            session_type="scenario",
            language="es"
        )

        # Filter by type
        scenario_sessions = await self.manager.get_user_sessions(
            user_id=user_id,
            session_type="scenario"
        )

        assert len(scenario_sessions) >= 2
        assert all(s.session_type == "scenario" for s in scenario_sessions)

    @pytest.mark.asyncio
    async def test_get_user_sessions_filter_by_language(self):
        """Test filtering sessions by language"""
        user_id = 15

        # Create sessions in different languages
        await self.manager.start_session(
            user_id=user_id,
            session_type="scenario",
            language="es"
        )
        await self.manager.start_session(
            user_id=user_id,
            session_type="scenario",
            language="fr"
        )
        await self.manager.start_session(
            user_id=user_id,
            session_type="scenario",
            language="es"
        )

        # Filter by language
        spanish_sessions = await self.manager.get_user_sessions(
            user_id=user_id,
            language="es"
        )

        assert len(spanish_sessions) >= 2
        assert all(s.language == "es" for s in spanish_sessions)

    @pytest.mark.asyncio
    async def test_get_user_sessions_with_limit(self):
        """Test limiting number of sessions returned"""
        user_id = 16

        # Create many sessions
        for i in range(15):
            await self.manager.start_session(
                user_id=user_id,
                session_type="scenario",
                language="es"
            )

        # Get with limit
        sessions = await self.manager.get_user_sessions(user_id, limit=5)

        assert len(sessions) == 5

    @pytest.mark.asyncio
    async def test_get_user_sessions_ordered_by_date(self):
        """Test sessions are ordered by started_at descending"""
        user_id = 17

        # Create sessions
        session_ids = []
        for i in range(3):
            session_id = await self.manager.start_session(
                user_id=user_id,
                session_type="scenario",
                language="es"
            )
            session_ids.append(session_id)

        # Get sessions
        sessions = await self.manager.get_user_sessions(user_id)

        # Most recent should be first
        assert sessions[0].id == int(session_ids[-1])


class TestSingletonAndConvenienceFunctions:
    """Test singleton pattern and convenience functions"""

    @pytest.mark.asyncio
    async def test_get_session_manager_singleton(self):
        """Test singleton pattern for session manager"""
        manager1 = get_session_manager()
        manager2 = get_session_manager()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_start_learning_session_convenience(self):
        """Test convenience function for starting session"""
        session_id = await start_learning_session(
            user_id=100,
            session_type="scenario",
            language="es",
            source_id="test_scenario",
            metadata={"test": "data"}
        )

        assert session_id is not None
        assert session_id.isdigit()

        # Verify in database
        db = get_primary_db_session()
        session = db.query(LearningSession).filter(
            LearningSession.id == int(session_id)
        ).first()

        assert session is not None
        assert session.user_id == 100
        assert session.source_id == "test_scenario"
        db.close()

    @pytest.mark.asyncio
    async def test_complete_learning_session_convenience(self):
        """Test convenience function for completing session"""
        # Start session
        session_id = await start_learning_session(
            user_id=101,
            session_type="scenario",
            language="fr"
        )

        # Complete session
        completed = await complete_learning_session(session_id)

        assert completed.ended_at is not None
        assert completed.duration_seconds is not None

    @pytest.mark.asyncio
    async def test_update_learning_session_convenience(self):
        """Test convenience function for updating session"""
        # Start session
        session_id = await start_learning_session(
            user_id=102,
            session_type="vocabulary_review",
            language="de"
        )

        # Update session
        updated = await update_learning_session(
            session_id=session_id,
            items_studied=15,
            items_correct=12,
            items_incorrect=3,
            metadata_update={"difficulty": "hard"}
        )

        assert updated.items_studied == 15
        assert updated.items_correct == 12
        assert updated.accuracy_rate == 0.8  # 12/15
        assert updated.session_metadata["difficulty"] == "hard"


class TestErrorHandling:
    """Test error handling in learning session manager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.db = get_primary_db_session()
        self.manager = LearningSessionManager(self.db)

        yield

        self.db.close()

    @pytest.mark.asyncio
    async def test_start_session_db_error(self):
        """Test error handling when database fails during start"""
        # Mock database to raise error
        with patch.object(self.manager.db, 'add', side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await self.manager.start_session(
                    user_id=200,
                    session_type="scenario",
                    language="es"
                )

    @pytest.mark.asyncio
    async def test_update_session_db_error(self):
        """Test error handling when database fails during update"""
        # Start session normally
        session_id = await self.manager.start_session(
            user_id=201,
            session_type="scenario",
            language="fr"
        )

        # Mock commit to raise error
        with patch.object(self.manager.db, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await self.manager.update_session(
                    session_id=session_id,
                    items_studied=10
                )

    @pytest.mark.asyncio
    async def test_complete_session_db_error(self):
        """Test error handling when database fails during complete"""
        # Start session normally
        session_id = await self.manager.start_session(
            user_id=202,
            session_type="scenario",
            language="de"
        )

        # Mock commit to raise error
        with patch.object(self.manager.db, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await self.manager.complete_session(session_id)

    @pytest.mark.asyncio
    async def test_get_session_error_handling(self):
        """Test error handling in get_session"""
        # Mock query to raise error
        with patch.object(self.manager.db, 'query', side_effect=Exception("DB Error")):
            session = await self.manager.get_session("123")
            # Should return None instead of raising
            assert session is None

    @pytest.mark.asyncio
    async def test_get_user_sessions_error_handling(self):
        """Test error handling in get_user_sessions"""
        # Mock query to raise error
        with patch.object(self.manager.db, 'query', side_effect=Exception("DB Error")):
            sessions = await self.manager.get_user_sessions(203)
            # Should return empty list instead of raising
            assert sessions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
