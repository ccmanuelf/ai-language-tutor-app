"""
Comprehensive tests for SessionManager class
Tests learning session lifecycle and streak management
"""

import json
import sqlite3
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.sr_database import DatabaseManager
from app.services.sr_models import LearningSession, SessionType
from app.services.sr_sessions import SessionManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    # Create database schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create learning_sessions table
    cursor.execute("""
        CREATE TABLE learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            session_type TEXT NOT NULL,
            mode_specific_data TEXT,
            duration_minutes INTEGER DEFAULT 0,
            items_studied INTEGER DEFAULT 0,
            items_correct INTEGER DEFAULT 0,
            items_incorrect INTEGER DEFAULT 0,
            accuracy_percentage REAL DEFAULT 0.0,
            average_response_time_ms INTEGER DEFAULT 0,
            confidence_score REAL DEFAULT 0.0,
            engagement_score REAL DEFAULT 0.0,
            difficulty_level INTEGER DEFAULT 1,
            new_items_learned INTEGER DEFAULT 0,
            items_reviewed INTEGER DEFAULT 0,
            streak_contributions INTEGER DEFAULT 0,
            goal_progress REAL DEFAULT 0.0,
            content_source TEXT,
            ai_model_used TEXT,
            tutor_mode TEXT,
            scenario_id TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create learning_streaks table
    cursor.execute("""
        CREATE TABLE learning_streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            total_active_days INTEGER DEFAULT 0,
            last_activity_date DATE,
            streak_start_date DATE,
            streak_freeze_days_available INTEGER DEFAULT 0,
            streak_freeze_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, language_code)
        )
    """)

    # Create gamification_achievements table
    cursor.execute("""
        CREATE TABLE gamification_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            achievement_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            badge_icon TEXT,
            badge_color TEXT,
            points_awarded INTEGER DEFAULT 0,
            criteria_met TEXT,
            required_criteria TEXT,
            rarity TEXT DEFAULT 'common',
            milestone_level INTEGER,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def db_manager(temp_db):
    """Create DatabaseManager with temp database"""
    return DatabaseManager(db_path=temp_db)


@pytest.fixture
def session_manager(db_manager):
    """Create SessionManager instance"""
    return SessionManager(db_manager=db_manager)


class TestSessionManagerInitialization:
    """Test SessionManager initialization"""

    def test_initialization_with_db_manager(self, db_manager):
        """Test manager initializes with DatabaseManager"""
        manager = SessionManager(db_manager=db_manager)

        assert manager.db is db_manager


class TestStartLearningSession:
    """Test start_learning_session method"""

    def test_start_basic_session(self, session_manager):
        """Test starting a basic learning session"""
        session_id = session_manager.start_learning_session(
            user_id=1,
            language_code="es",
            session_type=SessionType.VOCABULARY,
        )

        assert session_id is not None
        assert len(session_id) == 36  # UUID format

    def test_start_session_with_all_fields(self, session_manager):
        """Test starting session with all optional fields"""
        session_id = session_manager.start_learning_session(
            user_id=1,
            language_code="fr",
            session_type=SessionType.CONVERSATION,
            mode_specific_data={"difficulty": "intermediate"},
            content_source="textbook",
            ai_model_used="claude",
            tutor_mode="pierre",
            scenario_id="scenario-123",
        )

        assert session_id is not None

        # Verify all fields were stored
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM learning_sessions WHERE session_id = ?", (session_id,)
            )
            row = cursor.fetchone()

            assert row["user_id"] == 1
            assert row["language_code"] == "fr"
            assert row["session_type"] == SessionType.CONVERSATION.value
            assert json.loads(row["mode_specific_data"]) == {
                "difficulty": "intermediate"
            }
            assert row["content_source"] == "textbook"
            assert row["ai_model_used"] == "claude"
            assert row["tutor_mode"] == "pierre"
            assert row["scenario_id"] == "scenario-123"
            assert row["started_at"] is not None

    def test_start_session_with_enum_value(self, session_manager):
        """Test session_type accepts SessionType enum"""
        session_id = session_manager.start_learning_session(
            user_id=1,
            language_code="es",
            session_type=SessionType.TUTOR_MODE,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_type FROM learning_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            assert row["session_type"] == "tutor_mode"

    def test_start_session_with_string_value(self, session_manager):
        """Test session_type accepts string value"""
        session_id = session_manager.start_learning_session(
            user_id=1,
            language_code="es",
            session_type="vocabulary",  # String instead of enum
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_type FROM learning_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            assert row["session_type"] == "vocabulary"

    def test_start_session_with_empty_mode_data(self, session_manager):
        """Test session with None mode_specific_data defaults to empty dict"""
        session_id = session_manager.start_learning_session(
            user_id=1,
            language_code="es",
            session_type=SessionType.VOCABULARY,
            mode_specific_data=None,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mode_specific_data FROM learning_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            assert json.loads(row["mode_specific_data"]) == {}

    def test_start_session_records_timestamp(self, session_manager):
        """Test session records started_at timestamp"""
        before_start = datetime.now()
        session_id = session_manager.start_learning_session(
            user_id=1, language_code="es", session_type=SessionType.VOCABULARY
        )
        after_start = datetime.now()

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT started_at FROM learning_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            started_at = datetime.fromisoformat(row["started_at"])

            # Timestamp should be within the time window (handle timezone)
            time_diff = (
                datetime.now() - started_at.replace(tzinfo=None)
            ).total_seconds()
            assert time_diff < 5  # Within 5 seconds

    def test_start_session_database_error_raises(self, session_manager):
        """Test database errors are raised"""
        with patch.object(
            session_manager.db, "get_connection", side_effect=Exception("DB error")
        ):
            with pytest.raises(Exception, match="DB error"):
                session_manager.start_learning_session(
                    user_id=1, language_code="es", session_type=SessionType.VOCABULARY
                )


class TestEndLearningSession:
    """Test end_learning_session method"""

    def _start_session(self, session_manager, session_id="test-session"):
        """Helper to start a session"""
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            # Use naive datetime (no timezone) to match datetime.now() in end_learning_session
            started_at = datetime.now() - timedelta(minutes=15)
            cursor.execute(
                """
                INSERT INTO learning_sessions (
                    session_id, user_id, language_code, session_type, started_at
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    1,
                    "es",
                    "vocabulary",
                    started_at.isoformat(),
                ),
            )
            conn.commit()

    def test_end_session_success(self, session_manager):
        """Test successfully ending a session"""
        self._start_session(session_manager)

        result = session_manager.end_learning_session(
            session_id="test-session",
            items_studied=10,
            items_correct=8,
            items_incorrect=2,
        )

        assert result is True

    def test_end_session_not_found_returns_false(self, session_manager):
        """Test ending non-existent session returns False"""
        result = session_manager.end_learning_session(
            session_id="non-existent", items_studied=10
        )

        assert result is False

    def test_end_session_calculates_duration(self, session_manager):
        """Test session duration is calculated correctly"""
        # Start session 20 minutes ago (use naive datetime)
        start_time = datetime.now() - timedelta(minutes=20)
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_sessions (
                    session_id, user_id, language_code, session_type, started_at
                ) VALUES (?, ?, ?, ?, ?)
            """,
                ("test-session", 1, "es", "vocabulary", start_time.isoformat()),
            )
            conn.commit()

        session_manager.end_learning_session(session_id="test-session")

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT duration_minutes FROM learning_sessions WHERE session_id = ?",
                ("test-session",),
            )
            row = cursor.fetchone()
            # Should be approximately 20 minutes (allow 1 minute tolerance)
            assert 19 <= row["duration_minutes"] <= 21

    def test_end_session_calculates_accuracy(self, session_manager):
        """Test accuracy percentage is calculated correctly"""
        self._start_session(session_manager)

        session_manager.end_learning_session(
            session_id="test-session",
            items_studied=10,
            items_correct=8,
            items_incorrect=2,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT accuracy_percentage FROM learning_sessions WHERE session_id = ?",
                ("test-session",),
            )
            row = cursor.fetchone()
            # 8 correct out of 10 total = 80%
            assert row["accuracy_percentage"] == 80.0

    def test_end_session_accuracy_zero_when_no_items(self, session_manager):
        """Test accuracy is 0 when no items studied"""
        self._start_session(session_manager)

        session_manager.end_learning_session(
            session_id="test-session",
            items_studied=0,
            items_correct=0,
            items_incorrect=0,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT accuracy_percentage FROM learning_sessions WHERE session_id = ?",
                ("test-session",),
            )
            row = cursor.fetchone()
            assert row["accuracy_percentage"] == 0.0

    def test_end_session_updates_all_metrics(self, session_manager):
        """Test all metrics are updated correctly"""
        self._start_session(session_manager)

        session_manager.end_learning_session(
            session_id="test-session",
            items_studied=15,
            items_correct=12,
            items_incorrect=3,
            average_response_time_ms=1500,
            confidence_score=0.85,
            engagement_score=0.92,
            new_items_learned=5,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM learning_sessions WHERE session_id = ?",
                ("test-session",),
            )
            row = cursor.fetchone()

            assert row["items_studied"] == 15
            assert row["items_correct"] == 12
            assert row["items_incorrect"] == 3
            assert row["average_response_time_ms"] == 1500
            assert row["confidence_score"] == 0.85
            assert row["engagement_score"] == 0.92
            assert row["new_items_learned"] == 5
            assert row["items_reviewed"] == 10  # 15 studied - 5 new
            assert row["ended_at"] is not None

    def test_end_session_triggers_streak_update(self, session_manager):
        """Test ending session triggers streak update"""
        self._start_session(session_manager)

        with patch.object(
            session_manager, "_update_learning_streaks"
        ) as mock_update_streaks:
            session_manager.end_learning_session(session_id="test-session")

            # Should call streak update with session info
            mock_update_streaks.assert_called_once()
            call_args = mock_update_streaks.call_args[0][0]
            assert call_args["user_id"] == 1
            assert call_args["language_code"] == "es"

    def test_end_session_handles_database_error(self, session_manager):
        """Test handles database errors gracefully"""
        self._start_session(session_manager)

        with patch.object(
            session_manager.db, "get_connection", side_effect=Exception("DB error")
        ):
            result = session_manager.end_learning_session(session_id="test-session")

            assert result is False


class TestUpdateLearningStreaks:
    """Test _update_learning_streaks method"""

    def test_update_streaks_creates_new_streak(self, session_manager):
        """Test creates new streak for first session"""
        session_info = {"user_id": 1, "language_code": "es"}

        session_manager._update_learning_streaks(session_info)

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM learning_streaks WHERE user_id = ? AND language_code = ?",
                (1, "es"),
            )
            row = cursor.fetchone()

            assert row is not None
            assert row["current_streak"] == 1
            assert row["longest_streak"] == 1
            assert row["total_active_days"] == 1
            assert row["last_activity_date"] == str(date.today())

    def test_update_streaks_same_day_no_change(self, session_manager):
        """Test studying same day doesn't increase streak"""
        today = date.today()

        # Create existing streak
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_streaks (
                    user_id, language_code, current_streak, longest_streak,
                    total_active_days, last_activity_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (1, "es", 5, 5, 10, today),
            )
            conn.commit()

        session_info = {"user_id": 1, "language_code": "es"}
        session_manager._update_learning_streaks(session_info)

        # Streak should remain unchanged
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_streak FROM learning_streaks WHERE user_id = ?", (1,)
            )
            row = cursor.fetchone()
            assert row["current_streak"] == 5  # No change

    def test_update_streaks_consecutive_day_increments(self, session_manager):
        """Test consecutive day study increments streak"""
        yesterday = date.today() - timedelta(days=1)

        # Create existing streak from yesterday
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_streaks (
                    user_id, language_code, current_streak, longest_streak,
                    total_active_days, last_activity_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (1, "es", 5, 5, 10, yesterday),
            )
            conn.commit()

        session_info = {"user_id": 1, "language_code": "es"}
        session_manager._update_learning_streaks(session_info)

        # Streak should increment
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_streak, longest_streak, total_active_days FROM learning_streaks WHERE user_id = ?",
                (1,),
            )
            row = cursor.fetchone()
            assert row["current_streak"] == 6  # Incremented
            assert row["longest_streak"] == 6  # New longest
            assert row["total_active_days"] == 11  # Incremented

    def test_update_streaks_broken_streak_resets(self, session_manager):
        """Test gap > 1 day resets streak to 1"""
        three_days_ago = date.today() - timedelta(days=3)

        # Create existing streak from 3 days ago
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_streaks (
                    user_id, language_code, current_streak, longest_streak,
                    total_active_days, last_activity_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (1, "es", 10, 15, 25, three_days_ago),
            )
            conn.commit()

        session_info = {"user_id": 1, "language_code": "es"}
        session_manager._update_learning_streaks(session_info)

        # Streak should reset
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_streak, longest_streak FROM learning_streaks WHERE user_id = ?",
                (1,),
            )
            row = cursor.fetchone()
            assert row["current_streak"] == 1  # Reset
            assert row["longest_streak"] == 15  # Preserved

    def test_update_streaks_updates_longest_streak(self, session_manager):
        """Test longest_streak is updated when current exceeds it"""
        yesterday = date.today() - timedelta(days=1)

        # Current streak at 9, longest at 8
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_streaks (
                    user_id, language_code, current_streak, longest_streak,
                    total_active_days, last_activity_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (1, "es", 9, 8, 20, yesterday),
            )
            conn.commit()

        session_info = {"user_id": 1, "language_code": "es"}
        session_manager._update_learning_streaks(session_info)

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_streak, longest_streak FROM learning_streaks WHERE user_id = ?",
                (1,),
            )
            row = cursor.fetchone()
            assert row["current_streak"] == 10
            assert row["longest_streak"] == 10  # Updated

    def test_update_streaks_triggers_achievement_check(self, session_manager):
        """Test streak update triggers achievement check"""
        session_info = {"user_id": 1, "language_code": "es"}

        with patch.object(session_manager, "_check_streak_achievements") as mock_check:
            session_manager._update_learning_streaks(session_info)

            # Should call achievement check
            mock_check.assert_called_once_with(1, "es", 1)

    def test_update_streaks_handles_empty_session_info(self, session_manager):
        """Test handles None or empty session_info gracefully"""
        # Should not raise error
        session_manager._update_learning_streaks(None)
        session_manager._update_learning_streaks({})

    def test_update_streaks_handles_database_error(self, session_manager):
        """Test handles database errors gracefully"""
        session_info = {"user_id": 1, "language_code": "es"}

        with patch.object(
            session_manager.db, "get_connection", side_effect=Exception("DB error")
        ):
            # Should not raise, just log
            session_manager._update_learning_streaks(session_info)

    def test_update_streaks_null_last_activity_date(self, session_manager):
        """Test handles NULL last_activity_date edge case"""
        # Create streak with NULL last_activity_date
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_streaks (
                    user_id, language_code, current_streak, longest_streak,
                    total_active_days, last_activity_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (1, "es", 5, 5, 10, None),  # NULL last_activity_date
            )
            conn.commit()

        session_info = {"user_id": 1, "language_code": "es"}
        session_manager._update_learning_streaks(session_info)

        # Should handle gracefully and set streak to at least 1
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_streak FROM learning_streaks WHERE user_id = ?", (1,)
            )
            row = cursor.fetchone()
            assert row["current_streak"] >= 1  # Should be at least 1


class TestCheckStreakAchievements:
    """Test _check_streak_achievements method"""

    def test_check_achievements_7_day_milestone(self, session_manager):
        """Test 7-day streak achievement"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 7)

            mock_award.assert_called_once_with(
                1, "es", "Week Warrior", "Studied for 7 consecutive days", 50, 7
            )

    def test_check_achievements_14_day_milestone(self, session_manager):
        """Test 14-day streak achievement"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 14)

            mock_award.assert_called_once_with(
                1,
                "es",
                "Two Week Champion",
                "Studied for 14 consecutive days",
                100,
                14,
            )

    def test_check_achievements_30_day_milestone(self, session_manager):
        """Test 30-day streak achievement"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 30)

            mock_award.assert_called_once_with(
                1, "es", "Monthly Master", "Studied for 30 consecutive days", 200, 30
            )

    def test_check_achievements_60_day_milestone(self, session_manager):
        """Test 60-day streak achievement"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 60)

            mock_award.assert_called_once_with(
                1,
                "es",
                "Dedication Legend",
                "Studied for 60 consecutive days",
                400,
                60,
            )

    def test_check_achievements_100_day_milestone(self, session_manager):
        """Test 100-day streak achievement"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 100)

            mock_award.assert_called_once_with(
                1, "es", "Century Scholar", "Studied for 100 consecutive days", 750, 100
            )

    def test_check_achievements_365_day_milestone(self, session_manager):
        """Test 365-day streak achievement"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 365)

            mock_award.assert_called_once_with(
                1,
                "es",
                "Year-Long Learner",
                "Studied for 365 consecutive days",
                1500,
                365,
            )

    def test_check_achievements_non_milestone_no_award(self, session_manager):
        """Test non-milestone days don't trigger awards"""
        with patch.object(session_manager, "_award_streak_achievement") as mock_award:
            session_manager._check_streak_achievements(1, "es", 5)
            session_manager._check_streak_achievements(1, "es", 15)
            session_manager._check_streak_achievements(1, "es", 50)

            # Should not call award for non-milestone days
            mock_award.assert_not_called()


class TestAwardStreakAchievement:
    """Test _award_streak_achievement method"""

    def test_award_achievement_creates_record(self, session_manager):
        """Test achievement record is created"""
        session_manager._award_streak_achievement(
            user_id=1,
            language_code="es",
            title="Week Warrior",
            description="Studied for 7 consecutive days",
            points_awarded=50,
            milestone=7,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM gamification_achievements WHERE user_id = ? AND title = ?",
                (1, "Week Warrior"),
            )
            row = cursor.fetchone()

            assert row is not None
            assert row["achievement_type"] == "streak"
            assert row["title"] == "Week Warrior"
            assert row["description"] == "Studied for 7 consecutive days"
            assert row["points_awarded"] == 50
            assert row["badge_icon"] == "🔥"
            assert row["badge_color"] == "#FF6B35"
            assert row["milestone_level"] == 7
            assert row["rarity"] == "common"  # < 30 days

    def test_award_achievement_rare_for_30_plus_days(self, session_manager):
        """Test achievements >= 30 days are marked as rare"""
        session_manager._award_streak_achievement(
            user_id=1,
            language_code="es",
            title="Monthly Master",
            description="Studied for 30 consecutive days",
            points_awarded=200,
            milestone=30,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT rarity FROM gamification_achievements WHERE user_id = ? AND milestone_level = ?",
                (1, 30),
            )
            row = cursor.fetchone()
            assert row["rarity"] == "rare"

    def test_award_achievement_prevents_duplicates_within_24_hours(
        self, session_manager
    ):
        """Test duplicate achievements within 24 hours are not awarded"""
        # Award first achievement
        session_manager._award_streak_achievement(
            user_id=1,
            language_code="es",
            title="Week Warrior",
            description="Studied for 7 consecutive days",
            points_awarded=50,
            milestone=7,
        )

        # Try to award same achievement again
        session_manager._award_streak_achievement(
            user_id=1,
            language_code="es",
            title="Week Warrior",
            description="Studied for 7 consecutive days",
            points_awarded=50,
            milestone=7,
        )

        # Should only have one record
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM gamification_achievements WHERE user_id = ? AND title = ?",
                (1, "Week Warrior"),
            )
            row = cursor.fetchone()
            assert row["count"] == 1

    def test_award_achievement_stores_criteria_as_json(self, session_manager):
        """Test criteria are stored as JSON"""
        session_manager._award_streak_achievement(
            user_id=1,
            language_code="es",
            title="Week Warrior",
            description="Studied for 7 consecutive days",
            points_awarded=50,
            milestone=7,
        )

        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT criteria_met, required_criteria FROM gamification_achievements WHERE user_id = ?",
                (1,),
            )
            row = cursor.fetchone()

            criteria_met = json.loads(row["criteria_met"])
            required_criteria = json.loads(row["required_criteria"])

            assert criteria_met == {"streak_days": 7}
            assert required_criteria == {"required_days": 7}

    def test_award_achievement_handles_database_error(self, session_manager):
        """Test handles database errors gracefully"""
        with patch.object(
            session_manager.db, "get_connection", side_effect=Exception("DB error")
        ):
            # Should not raise, just log
            session_manager._award_streak_achievement(
                user_id=1,
                language_code="es",
                title="Week Warrior",
                description="Test",
                points_awarded=50,
                milestone=7,
            )


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_complete_session_workflow(self, session_manager):
        """Test complete workflow: start → end → streak update"""
        # Start session
        session_id = session_manager.start_learning_session(
            user_id=1, language_code="es", session_type=SessionType.VOCABULARY
        )

        # End session
        result = session_manager.end_learning_session(
            session_id=session_id,
            items_studied=20,
            items_correct=18,
            items_incorrect=2,
            new_items_learned=5,
        )

        assert result is True

        # Verify session data
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM learning_sessions WHERE session_id = ?", (session_id,)
            )
            row = cursor.fetchone()

            assert row["items_studied"] == 20
            assert row["items_correct"] == 18
            assert row["accuracy_percentage"] == 90.0
            assert row["items_reviewed"] == 15
            assert row["ended_at"] is not None

        # Verify streak created
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM learning_streaks WHERE user_id = ? AND language_code = ?",
                (1, "es"),
            )
            row = cursor.fetchone()

            assert row is not None
            assert row["current_streak"] == 1

    def test_streak_milestone_workflow(self, session_manager):
        """Test achieving streak milestone awards achievement"""
        # Create streak at 6 days
        yesterday = date.today() - timedelta(days=1)
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_streaks (
                    user_id, language_code, current_streak, longest_streak,
                    total_active_days, last_activity_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (1, "es", 6, 6, 6, yesterday),
            )
            conn.commit()

        # Start and end session (should trigger 7-day achievement)
        session_id = session_manager.start_learning_session(
            user_id=1, language_code="es", session_type=SessionType.VOCABULARY
        )

        session_manager.end_learning_session(
            session_id=session_id, items_studied=10, items_correct=8, items_incorrect=2
        )

        # Verify achievement awarded
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM gamification_achievements WHERE user_id = ? AND milestone_level = ?",
                (1, 7),
            )
            row = cursor.fetchone()

            assert row is not None
            assert row["title"] == "Week Warrior"
            assert row["points_awarded"] == 50

    def test_multiple_users_independent_streaks(self, session_manager):
        """Test different users have independent streaks"""
        # User 1 session
        session_id_1 = session_manager.start_learning_session(
            user_id=1, language_code="es", session_type=SessionType.VOCABULARY
        )
        session_manager.end_learning_session(session_id=session_id_1, items_studied=10)

        # User 2 session
        session_id_2 = session_manager.start_learning_session(
            user_id=2, language_code="es", session_type=SessionType.VOCABULARY
        )
        session_manager.end_learning_session(session_id=session_id_2, items_studied=5)

        # Verify separate streaks
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM learning_streaks")
            row = cursor.fetchone()
            assert row["count"] == 2

            # Each user has their own streak
            cursor.execute("SELECT user_id, current_streak FROM learning_streaks")
            rows = cursor.fetchall()
            assert len(rows) == 2
            assert all(row["current_streak"] == 1 for row in rows)

    def test_multiple_sessions_same_day_single_streak_increment(self, session_manager):
        """Test multiple sessions same day only count as one streak day"""
        # First session today
        session_id_1 = session_manager.start_learning_session(
            user_id=1, language_code="es", session_type=SessionType.VOCABULARY
        )
        session_manager.end_learning_session(session_id=session_id_1, items_studied=10)

        # Second session same day
        session_id_2 = session_manager.start_learning_session(
            user_id=1, language_code="es", session_type=SessionType.CONVERSATION
        )
        session_manager.end_learning_session(session_id=session_id_2, items_studied=5)

        # Verify streak is still 1
        with session_manager.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_streak FROM learning_streaks WHERE user_id = ?", (1,)
            )
            row = cursor.fetchone()
            assert row["current_streak"] == 1
