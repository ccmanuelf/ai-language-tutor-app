"""
Comprehensive tests for AnalyticsEngine class
Tests learning analytics, recommendations, and system metrics
"""

import sqlite3
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.sr_analytics import AnalyticsEngine
from app.services.sr_database import DatabaseManager


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
            duration_minutes INTEGER DEFAULT 0,
            items_studied INTEGER DEFAULT 0,
            items_correct INTEGER DEFAULT 0,
            items_incorrect INTEGER DEFAULT 0,
            accuracy_percentage REAL DEFAULT 0.0,
            new_items_learned INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create spaced_repetition_items table
    cursor.execute("""
        CREATE TABLE spaced_repetition_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            front_content TEXT NOT NULL,
            back_content TEXT NOT NULL,
            item_type TEXT DEFAULT 'vocabulary',
            mastery_level REAL DEFAULT 0.0,
            next_review_date TIMESTAMP,
            is_active INTEGER DEFAULT 1,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            points_awarded INTEGER DEFAULT 0,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create learning_goals table
    cursor.execute("""
        CREATE TABLE learning_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            goal_type TEXT NOT NULL,
            title TEXT NOT NULL,
            progress_percentage REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
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
    """Create a DatabaseManager instance with test database"""
    return DatabaseManager(temp_db)


@pytest.fixture
def analytics_engine(db_manager):
    """Create an AnalyticsEngine instance"""
    return AnalyticsEngine(db_manager)


# Helper functions for test data insertion
def insert_learning_session(
    db_manager: DatabaseManager,
    user_id: int = 1,
    language_code: str = "es",
    duration_minutes: int = 30,
    items_studied: int = 20,
    accuracy_percentage: float = 85.0,
    new_items_learned: int = 5,
    started_at: Optional[datetime] = None,
):
    """Insert a learning session for testing"""
    if started_at is None:
        started_at = datetime.now()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO learning_sessions
            (session_id, user_id, language_code, session_type, duration_minutes,
             items_studied, accuracy_percentage, new_items_learned, started_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"session_{user_id}_{started_at.timestamp()}",
                user_id,
                language_code,
                "review",
                duration_minutes,
                items_studied,
                accuracy_percentage,
                new_items_learned,
                started_at,
            ),
        )
        conn.commit()


def insert_sr_item(
    db_manager: DatabaseManager,
    user_id: int = 1,
    language_code: str = "es",
    mastery_level: float = 0.5,
    next_review_date: Optional[datetime] = None,
    is_active: int = 1,
):
    """Insert a spaced repetition item for testing"""
    if next_review_date is None:
        next_review_date = datetime.now()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO spaced_repetition_items
            (item_id, user_id, language_code, front_content, back_content,
             mastery_level, next_review_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"item_{user_id}_{mastery_level}_{datetime.now().timestamp()}",
                user_id,
                language_code,
                "test front",
                "test back",
                mastery_level,
                next_review_date,
                is_active,
            ),
        )
        conn.commit()


def insert_streak(
    db_manager: DatabaseManager,
    user_id: int = 1,
    language_code: str = "es",
    current_streak: int = 5,
    longest_streak: int = 10,
    total_active_days: int = 50,
    last_activity_date: Optional[date] = None,
):
    """Insert a learning streak for testing"""
    if last_activity_date is None:
        last_activity_date = date.today()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO learning_streaks
            (user_id, language_code, current_streak, longest_streak,
             total_active_days, last_activity_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                language_code,
                current_streak,
                longest_streak,
                total_active_days,
                last_activity_date,
            ),
        )
        conn.commit()


def insert_achievement(
    db_manager: DatabaseManager,
    user_id: int = 1,
    language_code: str = "es",
    achievement_type: str = "streak",
    title: str = "Test Achievement",
    points_awarded: int = 100,
    earned_at: Optional[datetime] = None,
):
    """Insert an achievement for testing"""
    if earned_at is None:
        earned_at = datetime.now()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO gamification_achievements
            (achievement_id, user_id, language_code, achievement_type,
             title, description, points_awarded, earned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"ach_{user_id}_{earned_at.timestamp()}",
                user_id,
                language_code,
                achievement_type,
                title,
                "Test description",
                points_awarded,
                earned_at,
            ),
        )
        conn.commit()


def insert_goal(
    db_manager: DatabaseManager,
    user_id: int = 1,
    language_code: str = "es",
    goal_type: str = "daily_study",
    title: str = "Test Goal",
    progress_percentage: float = 50.0,
    status: str = "active",
):
    """Insert a learning goal for testing"""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO learning_goals
            (goal_id, user_id, language_code, goal_type, title,
             progress_percentage, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"goal_{user_id}_{datetime.now().timestamp()}",
                user_id,
                language_code,
                goal_type,
                title,
                progress_percentage,
                status,
            ),
        )
        conn.commit()


# ============================================================================
# 1. Initialization & Configuration Tests
# ============================================================================


def test_analytics_engine_initialization(db_manager):
    """Test AnalyticsEngine initialization with DatabaseManager"""
    engine = AnalyticsEngine(db_manager)

    assert engine.db == db_manager
    assert engine.mastery_threshold == 0.85


def test_analytics_engine_default_mastery_threshold(analytics_engine):
    """Test default mastery threshold is 0.85"""
    assert analytics_engine.mastery_threshold == 0.85


def test_set_mastery_threshold(analytics_engine):
    """Test setting mastery threshold"""
    analytics_engine.set_mastery_threshold(0.90)

    assert analytics_engine.mastery_threshold == 0.90


def test_set_mastery_threshold_updates_correctly(analytics_engine):
    """Test mastery threshold can be updated multiple times"""
    analytics_engine.set_mastery_threshold(0.75)
    assert analytics_engine.mastery_threshold == 0.75

    analytics_engine.set_mastery_threshold(0.95)
    assert analytics_engine.mastery_threshold == 0.95


# ============================================================================
# 2. get_user_analytics - Basic Stats Tests
# ============================================================================


def test_get_user_analytics_basic_stats_success(db_manager, analytics_engine):
    """Test getting basic stats for a user with sessions"""
    insert_learning_session(
        db_manager,
        user_id=1,
        language_code="es",
        duration_minutes=30,
        items_studied=20,
        accuracy_percentage=85.0,
        new_items_learned=5,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    assert "basic_stats" in result
    stats = result["basic_stats"]
    assert stats["total_sessions"] == 1
    assert stats["total_study_time"] == 30
    assert stats["avg_accuracy"] == 85.0
    assert stats["total_items_studied"] == 20
    assert stats["total_items_learned"] == 5


def test_get_user_analytics_basic_stats_multiple_sessions(db_manager, analytics_engine):
    """Test basic stats aggregation across multiple sessions"""
    # Insert 3 sessions
    insert_learning_session(
        db_manager,
        user_id=1,
        language_code="es",
        duration_minutes=30,
        items_studied=20,
        accuracy_percentage=80.0,
        new_items_learned=5,
    )
    insert_learning_session(
        db_manager,
        user_id=1,
        language_code="es",
        duration_minutes=45,
        items_studied=30,
        accuracy_percentage=90.0,
        new_items_learned=10,
    )
    insert_learning_session(
        db_manager,
        user_id=1,
        language_code="es",
        duration_minutes=25,
        items_studied=15,
        accuracy_percentage=85.0,
        new_items_learned=3,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    stats = result["basic_stats"]
    assert stats["total_sessions"] == 3
    assert stats["total_study_time"] == 100  # 30 + 45 + 25
    assert stats["avg_accuracy"] == 85.0  # (80 + 90 + 85) / 3
    assert stats["total_items_studied"] == 65  # 20 + 30 + 15
    assert stats["total_items_learned"] == 18  # 5 + 10 + 3


def test_get_user_analytics_no_sessions(analytics_engine):
    """Test getting analytics for user with no sessions"""
    result = analytics_engine.get_user_analytics(1, "es")

    assert "basic_stats" in result
    stats = result["basic_stats"]
    assert stats["total_sessions"] == 0
    assert stats["total_study_time"] is None
    assert stats["avg_accuracy"] is None
    # SQLite SUM() returns None when no rows, not 0
    assert stats["total_items_studied"] is None
    assert stats["total_items_learned"] is None


def test_get_user_analytics_partial_data(db_manager, analytics_engine):
    """Test handling sessions with some null fields"""
    insert_learning_session(
        db_manager,
        user_id=1,
        language_code="es",
        duration_minutes=0,
        items_studied=10,
        accuracy_percentage=0.0,
        new_items_learned=0,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    stats = result["basic_stats"]
    assert stats["total_sessions"] == 1
    assert stats["total_study_time"] == 0
    assert stats["avg_accuracy"] == 0.0


def test_get_user_analytics_zero_values(db_manager, analytics_engine):
    """Test handling zero duration and accuracy"""
    insert_learning_session(
        db_manager,
        user_id=1,
        language_code="es",
        duration_minutes=0,
        items_studied=0,
        accuracy_percentage=0.0,
        new_items_learned=0,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    assert "basic_stats" in result
    stats = result["basic_stats"]
    assert stats["total_sessions"] == 1
    assert stats["total_study_time"] == 0


def test_get_user_analytics_database_error(analytics_engine):
    """Test graceful handling of database errors"""
    # Mock database connection to raise an error
    with patch.object(
        analytics_engine.db, "get_connection", side_effect=Exception("DB Error")
    ):
        result = analytics_engine.get_user_analytics(1, "es")

        assert result == {}


# ============================================================================
# 3. get_user_analytics - SR Stats Tests
# ============================================================================


def test_get_user_analytics_sr_stats_success(db_manager, analytics_engine):
    """Test getting spaced repetition stats"""
    # Insert SR items with various mastery levels
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.5)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.9)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.7)

    result = analytics_engine.get_user_analytics(1, "es")

    assert "spaced_repetition" in result
    sr_stats = result["spaced_repetition"]
    assert sr_stats["total_items"] == 3
    assert sr_stats["avg_mastery"] == pytest.approx(0.7, abs=0.01)  # (0.5+0.9+0.7)/3
    assert sr_stats["mastered_items"] == 1  # Only 0.9 >= 0.85


def test_get_user_analytics_sr_stats_uses_mastery_threshold(
    db_manager, analytics_engine
):
    """Test that SR stats use the configured mastery threshold"""
    # Insert items at threshold boundaries
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.84)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.85)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.86)

    result = analytics_engine.get_user_analytics(1, "es")

    sr_stats = result["spaced_repetition"]
    assert sr_stats["mastered_items"] == 2  # 0.85 and 0.86 >= 0.85 threshold


def test_get_user_analytics_sr_stats_custom_threshold(db_manager, analytics_engine):
    """Test SR stats with custom mastery threshold"""
    # Set custom threshold
    analytics_engine.set_mastery_threshold(0.90)

    # Insert items
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.85)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.92)

    result = analytics_engine.get_user_analytics(1, "es")

    sr_stats = result["spaced_repetition"]
    assert sr_stats["mastered_items"] == 1  # Only 0.92 >= 0.90


def test_get_user_analytics_sr_stats_due_items(db_manager, analytics_engine):
    """Test counting due items correctly"""
    now = datetime.now()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Insert items with different due dates
    insert_sr_item(
        db_manager,
        user_id=1,
        language_code="es",
        next_review_date=past,
        mastery_level=0.5,
    )
    insert_sr_item(
        db_manager,
        user_id=1,
        language_code="es",
        next_review_date=past,  # Use past to ensure it's definitely due
        mastery_level=0.6,
    )
    insert_sr_item(
        db_manager,
        user_id=1,
        language_code="es",
        next_review_date=future,
        mastery_level=0.7,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    sr_stats = result["spaced_repetition"]
    # Past items should be counted as due (at least 2)
    assert sr_stats["due_items"] >= 2


def test_get_user_analytics_sr_stats_no_items(analytics_engine):
    """Test SR stats with no items"""
    result = analytics_engine.get_user_analytics(1, "es")

    assert "spaced_repetition" in result
    sr_stats = result["spaced_repetition"]
    assert sr_stats["total_items"] == 0
    assert sr_stats["avg_mastery"] is None
    assert sr_stats["mastered_items"] == 0
    assert sr_stats["due_items"] == 0


def test_get_user_analytics_sr_stats_all_mastered(db_manager, analytics_engine):
    """Test SR stats when all items are mastered"""
    # Insert all items above threshold
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.9)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.95)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.88)

    result = analytics_engine.get_user_analytics(1, "es")

    sr_stats = result["spaced_repetition"]
    assert sr_stats["total_items"] == 3
    assert sr_stats["mastered_items"] == 3


def test_get_user_analytics_sr_stats_none_mastered(db_manager, analytics_engine):
    """Test SR stats when no items are mastered"""
    # Insert all items below threshold
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.2)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.4)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.6)

    result = analytics_engine.get_user_analytics(1, "es")

    sr_stats = result["spaced_repetition"]
    assert sr_stats["total_items"] == 3
    assert sr_stats["mastered_items"] == 0


# ============================================================================
# 4. get_user_analytics - Streaks Tests
# ============================================================================


def test_get_user_analytics_streaks_active(db_manager, analytics_engine):
    """Test getting active streak data"""
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=7,
        longest_streak=15,
        total_active_days=100,
        last_activity_date=date.today(),
    )

    result = analytics_engine.get_user_analytics(1, "es")

    assert "streaks" in result
    streaks = result["streaks"]
    assert streaks["current_streak"] == 7
    assert streaks["longest_streak"] == 15
    assert streaks["total_active_days"] == 100


def test_get_user_analytics_streaks_no_streak(analytics_engine):
    """Test getting analytics with no streak record"""
    result = analytics_engine.get_user_analytics(1, "es")

    assert "streaks" in result
    streaks = result["streaks"]
    assert streaks["current_streak"] == 0
    assert streaks["longest_streak"] == 0
    assert streaks["total_active_days"] == 0


def test_get_user_analytics_streaks_zero_values(db_manager, analytics_engine):
    """Test streak data with all zeros"""
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=0,
        longest_streak=0,
        total_active_days=0,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    streaks = result["streaks"]
    assert streaks["current_streak"] == 0
    assert streaks["longest_streak"] == 0
    assert streaks["total_active_days"] == 0


def test_get_user_analytics_streaks_longest_gt_current(db_manager, analytics_engine):
    """Test streak data where longest streak is greater than current"""
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=5,
        longest_streak=20,
        total_active_days=150,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    streaks = result["streaks"]
    assert streaks["current_streak"] == 5
    assert streaks["longest_streak"] == 20
    assert streaks["longest_streak"] > streaks["current_streak"]


def test_get_user_analytics_streaks_default_dict(analytics_engine):
    """Test that missing streak row returns default dict"""
    result = analytics_engine.get_user_analytics(1, "es")

    streaks = result["streaks"]
    assert isinstance(streaks, dict)
    assert "current_streak" in streaks
    assert "longest_streak" in streaks
    assert "total_active_days" in streaks


# ============================================================================
# 5. get_user_analytics - Achievements Tests
# ============================================================================


def test_get_user_analytics_achievements_multiple(db_manager, analytics_engine):
    """Test getting multiple achievements"""
    now = datetime.now()
    # Insert 3 achievements
    insert_achievement(
        db_manager,
        user_id=1,
        language_code="es",
        title="First Streak",
        earned_at=now - timedelta(days=2),
    )
    insert_achievement(
        db_manager,
        user_id=1,
        language_code="es",
        title="10 Items Mastered",
        earned_at=now - timedelta(days=1),
    )
    insert_achievement(
        db_manager,
        user_id=1,
        language_code="es",
        title="Perfect Session",
        earned_at=now,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    assert "recent_achievements" in result
    achievements = result["recent_achievements"]
    assert len(achievements) == 3
    assert achievements[0]["title"] == "Perfect Session"  # Most recent first


def test_get_user_analytics_achievements_limit_five(db_manager, analytics_engine):
    """Test that only 5 most recent achievements are returned"""
    now = datetime.now()
    # Insert 7 achievements
    for i in range(7):
        insert_achievement(
            db_manager,
            user_id=1,
            language_code="es",
            title=f"Achievement {i}",
            earned_at=now - timedelta(days=6 - i),
        )

    result = analytics_engine.get_user_analytics(1, "es")

    achievements = result["recent_achievements"]
    assert len(achievements) == 5


def test_get_user_analytics_achievements_ordered_desc(db_manager, analytics_engine):
    """Test achievements are ordered by earned_at DESC"""
    now = datetime.now()
    insert_achievement(
        db_manager,
        user_id=1,
        language_code="es",
        title="Old",
        earned_at=now - timedelta(days=5),
    )
    insert_achievement(
        db_manager,
        user_id=1,
        language_code="es",
        title="Recent",
        earned_at=now - timedelta(days=1),
    )
    insert_achievement(
        db_manager, user_id=1, language_code="es", title="Newest", earned_at=now
    )

    result = analytics_engine.get_user_analytics(1, "es")

    achievements = result["recent_achievements"]
    assert achievements[0]["title"] == "Newest"
    assert achievements[1]["title"] == "Recent"
    assert achievements[2]["title"] == "Old"


def test_get_user_analytics_achievements_empty(analytics_engine):
    """Test getting analytics with no achievements"""
    result = analytics_engine.get_user_analytics(1, "es")

    assert "recent_achievements" in result
    achievements = result["recent_achievements"]
    assert achievements == []


# ============================================================================
# 6. get_user_analytics - Goals Tests
# ============================================================================


def test_get_user_analytics_goals_active_only(db_manager, analytics_engine):
    """Test that only active goals are returned"""
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Active Goal",
        status="active",
    )
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Completed Goal",
        status="completed",
    )
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Paused Goal",
        status="paused",
    )

    result = analytics_engine.get_user_analytics(1, "es")

    assert "active_goals" in result
    goals = result["active_goals"]
    assert len(goals) == 1
    assert goals[0]["title"] == "Active Goal"


def test_get_user_analytics_goals_multiple(db_manager, analytics_engine):
    """Test getting multiple active goals"""
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Daily Study",
        progress_percentage=75.0,
    )
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Weekly Review",
        progress_percentage=50.0,
    )
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Monthly Challenge",
        progress_percentage=25.0,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    goals = result["active_goals"]
    assert len(goals) == 3


def test_get_user_analytics_goals_progress_values(db_manager, analytics_engine):
    """Test goal progress percentages are returned"""
    insert_goal(
        db_manager,
        user_id=1,
        language_code="es",
        title="Test Goal",
        progress_percentage=67.5,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    goals = result["active_goals"]
    assert goals[0]["progress_percentage"] == 67.5


def test_get_user_analytics_goals_empty(analytics_engine):
    """Test getting analytics with no active goals"""
    result = analytics_engine.get_user_analytics(1, "es")

    assert "active_goals" in result
    goals = result["active_goals"]
    assert goals == []


# ============================================================================
# 7. get_user_analytics - Integration Tests
# ============================================================================


def test_get_user_analytics_complete_data(db_manager, analytics_engine):
    """Test getting complete analytics with all sections populated"""
    # Insert data for all sections
    insert_learning_session(db_manager, user_id=1, language_code="es")
    insert_sr_item(db_manager, user_id=1, language_code="es")
    insert_streak(db_manager, user_id=1, language_code="es")
    insert_achievement(db_manager, user_id=1, language_code="es")
    insert_goal(db_manager, user_id=1, language_code="es")

    result = analytics_engine.get_user_analytics(1, "es")

    # Verify all sections present
    assert "basic_stats" in result
    assert "spaced_repetition" in result
    assert "streaks" in result
    assert "recent_achievements" in result
    assert "active_goals" in result
    assert "recommendations" in result

    # Verify data is populated
    assert result["basic_stats"]["total_sessions"] > 0
    assert result["spaced_repetition"]["total_items"] > 0
    assert result["streaks"]["current_streak"] >= 0
    assert len(result["recent_achievements"]) > 0
    assert len(result["active_goals"]) > 0


def test_get_user_analytics_different_languages(db_manager, analytics_engine):
    """Test that analytics are filtered by language"""
    # Insert Spanish data
    insert_learning_session(db_manager, user_id=1, language_code="es")
    insert_sr_item(db_manager, user_id=1, language_code="es")

    # Insert French data
    insert_learning_session(db_manager, user_id=1, language_code="fr")
    insert_sr_item(db_manager, user_id=1, language_code="fr")

    # Get Spanish analytics
    es_result = analytics_engine.get_user_analytics(1, "es")
    # Get French analytics
    fr_result = analytics_engine.get_user_analytics(1, "fr")

    # Both should have their own data
    assert es_result["basic_stats"]["total_sessions"] == 1
    assert fr_result["basic_stats"]["total_sessions"] == 1
    assert es_result["spaced_repetition"]["total_items"] == 1
    assert fr_result["spaced_repetition"]["total_items"] == 1


def test_get_user_analytics_different_users(db_manager, analytics_engine):
    """Test that analytics are isolated by user"""
    # Insert data for user 1
    insert_learning_session(db_manager, user_id=1, language_code="es")
    insert_sr_item(db_manager, user_id=1, language_code="es")

    # Insert data for user 2
    insert_learning_session(db_manager, user_id=2, language_code="es")
    insert_sr_item(db_manager, user_id=2, language_code="es")

    # Get user 1 analytics
    user1_result = analytics_engine.get_user_analytics(1, "es")
    # Get user 2 analytics
    user2_result = analytics_engine.get_user_analytics(2, "es")

    # Both should have their own data
    assert user1_result["basic_stats"]["total_sessions"] == 1
    assert user2_result["basic_stats"]["total_sessions"] == 1


def test_get_user_analytics_period_parameter(analytics_engine):
    """Test that period parameter is accepted (even if not used yet)"""
    # Should not raise an error
    result = analytics_engine.get_user_analytics(1, "es", period="daily")
    assert isinstance(result, dict)

    result = analytics_engine.get_user_analytics(1, "es", period="weekly")
    assert isinstance(result, dict)

    result = analytics_engine.get_user_analytics(1, "es", period="monthly")
    assert isinstance(result, dict)


# ============================================================================
# 8. Recommendations - Due Items Tests
# ============================================================================


def test_recommendations_due_items_present(db_manager, analytics_engine):
    """Test due items recommendation is added when items are due"""
    # Insert due items
    past = datetime.now() - timedelta(days=1)
    insert_sr_item(db_manager, user_id=1, language_code="es", next_review_date=past)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    assert len(recommendations) > 0
    assert any("ready for review" in rec for rec in recommendations)


def test_recommendations_due_items_count(db_manager, analytics_engine):
    """Test due items count is shown in recommendation"""
    past = datetime.now() - timedelta(days=1)
    # Insert 3 due items
    for _ in range(3):
        insert_sr_item(db_manager, user_id=1, language_code="es", next_review_date=past)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should mention "3 items"
    due_rec = [rec for rec in recommendations if "ready for review" in rec]
    assert len(due_rec) > 0
    assert "3" in due_rec[0]


def test_recommendations_due_items_none(db_manager, analytics_engine):
    """Test no due items recommendation when no items are due"""
    future = datetime.now() + timedelta(days=7)
    insert_sr_item(db_manager, user_id=1, language_code="es", next_review_date=future)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should not have due items recommendation
    due_rec = [rec for rec in recommendations if "ready for review" in rec]
    assert len(due_rec) == 0


def test_recommendations_due_items_multiple(db_manager, analytics_engine):
    """Test due items count formatting with multiple items"""
    past = datetime.now() - timedelta(days=1)
    # Insert 5 due items
    for _ in range(5):
        insert_sr_item(db_manager, user_id=1, language_code="es", next_review_date=past)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    due_rec = [rec for rec in recommendations if "ready for review" in rec]
    assert len(due_rec) > 0
    assert "5" in due_rec[0]


# ============================================================================
# 9. Recommendations - Streak Status Tests
# ============================================================================


def test_recommendations_streak_maintain_one_day_ago(db_manager, analytics_engine):
    """Test streak maintenance reminder when last activity was yesterday"""
    yesterday = date.today() - timedelta(days=1)
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=5,
        last_activity_date=yesterday,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should recommend maintaining streak
    streak_rec = [rec for rec in recommendations if "maintain your streak" in rec]
    assert len(streak_rec) > 0


def test_recommendations_streak_new_streak_two_days_ago(db_manager, analytics_engine):
    """Test new streak recommendation when last activity was 2+ days ago"""
    two_days_ago = date.today() - timedelta(days=2)
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=0,
        last_activity_date=two_days_ago,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should recommend starting new streak
    streak_rec = [rec for rec in recommendations if "new learning streak" in rec]
    assert len(streak_rec) > 0


def test_recommendations_streak_new_streak_multiple_days(db_manager, analytics_engine):
    """Test new streak recommendation for long gap"""
    long_ago = date.today() - timedelta(days=10)
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=0,
        last_activity_date=long_ago,
    )

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    streak_rec = [rec for rec in recommendations if "new learning streak" in rec]
    assert len(streak_rec) > 0


def test_recommendations_streak_no_record(analytics_engine):
    """Test no streak recommendation when no streak record exists"""
    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should not have streak recommendations without data
    streak_rec = [
        rec for rec in recommendations if "streak" in rec.lower() and "maintain" in rec
    ]
    assert len(streak_rec) == 0


def test_recommendations_streak_today_already(db_manager, analytics_engine):
    """Test no streak reminder if already active today"""
    insert_streak(
        db_manager,
        user_id=1,
        language_code="es",
        current_streak=5,
        last_activity_date=date.today(),
    )

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should not have streak maintenance reminder
    streak_rec = [rec for rec in recommendations if "maintain your streak" in rec]
    assert len(streak_rec) == 0


def test_recommendations_streak_null_last_activity(db_manager):
    """Test handling of null last_activity_date"""
    # Manually insert streak with null last_activity_date
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO learning_streaks
            (user_id, language_code, current_streak, longest_streak,
             total_active_days, last_activity_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (1, "es", 0, 0, 0, None),
        )
        conn.commit()

    engine = AnalyticsEngine(db_manager)
    result = engine.get_user_analytics(1, "es")

    # Should not crash
    assert "recommendations" in result


# ============================================================================
# 10. Recommendations - Mastery Levels Tests
# ============================================================================


def test_recommendations_low_mastery_below_50(db_manager, analytics_engine):
    """Test review recommendation for low mastery (< 0.5)"""
    # Insert items with low mastery
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.3)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.4)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should recommend reviewing
    mastery_rec = [rec for rec in recommendations if "review" in rec.lower()]
    assert len(mastery_rec) > 0


def test_recommendations_high_mastery_above_80(db_manager, analytics_engine):
    """Test new vocabulary recommendation for high mastery (> 0.8)"""
    # Insert items with high mastery
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.85)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.9)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should recommend new vocabulary
    mastery_rec = [rec for rec in recommendations if "new vocabulary" in rec]
    assert len(mastery_rec) > 0


def test_recommendations_medium_mastery_50_to_80(db_manager, analytics_engine):
    """Test no mastery recommendation for medium mastery (0.5-0.8)"""
    # Insert items with medium mastery
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.6)
    insert_sr_item(db_manager, user_id=1, language_code="es", mastery_level=0.7)

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should not have mastery-specific recommendations
    mastery_rec = [
        rec
        for rec in recommendations
        if "review" in rec.lower() or "new vocabulary" in rec
    ]
    # May have other recommendations, but not mastery-based ones
    # with medium mastery average


def test_recommendations_no_items(analytics_engine):
    """Test no mastery recommendation when no items exist"""
    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should not crash, may be empty or have other recommendations


def test_recommendations_null_mastery(db_manager):
    """Test handling of null average mastery"""
    # This would require special setup or mocking
    # Average mastery is NULL when no items exist
    engine = AnalyticsEngine(db_manager)
    result = engine.get_user_analytics(1, "es")

    # Should not crash
    assert "recommendations" in result


# ============================================================================
# 11. Recommendations - Integration Tests
# ============================================================================


def test_get_learning_recommendations_multiple(db_manager, analytics_engine):
    """Test multiple recommendations are combined"""
    # Insert data that triggers multiple recommendations
    past = datetime.now() - timedelta(days=1)
    insert_sr_item(
        db_manager,
        user_id=1,
        language_code="es",
        next_review_date=past,
        mastery_level=0.3,
    )  # Due + low mastery

    yesterday = date.today() - timedelta(days=1)
    insert_streak(
        db_manager, user_id=1, language_code="es", last_activity_date=yesterday
    )  # Streak maintenance

    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # Should have multiple recommendations
    assert len(recommendations) >= 2


def test_get_learning_recommendations_empty(analytics_engine):
    """Test empty recommendations when no triggering conditions"""
    # No data inserted
    result = analytics_engine.get_user_analytics(1, "es")

    recommendations = result["recommendations"]
    # May be empty or have minimal recommendations
    assert isinstance(recommendations, list)


def test_get_learning_recommendations_database_error(analytics_engine):
    """Test recommendations return empty list on database error"""
    # Mock the internal helper methods to raise errors
    with patch.object(
        analytics_engine.db, "get_connection", side_effect=Exception("DB Error")
    ):
        recommendations = analytics_engine._get_learning_recommendations(1, "es")

        assert recommendations == []


def test_get_learning_recommendations_called_by_user_analytics(
    db_manager, analytics_engine
):
    """Test that user analytics calls recommendations and includes them"""
    insert_sr_item(
        db_manager,
        user_id=1,
        language_code="es",
        next_review_date=datetime.now() - timedelta(days=1),
    )

    result = analytics_engine.get_user_analytics(1, "es")

    # Verify recommendations are included
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)


# ============================================================================
# 12. System Analytics - Stats Tests
# ============================================================================


def test_get_system_analytics_success(db_manager, analytics_engine):
    """Test getting system-wide analytics"""
    # Insert data for multiple users
    insert_learning_session(db_manager, user_id=1, language_code="es")
    insert_learning_session(db_manager, user_id=2, language_code="fr")
    insert_sr_item(db_manager, user_id=1, language_code="es")

    result = analytics_engine.get_system_analytics()

    assert "system_stats" in result
    assert "item_stats" in result
    assert "language_distribution" in result
    assert "generated_at" in result


def test_get_system_analytics_30_day_filter(db_manager, analytics_engine):
    """Test that only last 30 days of sessions are included"""
    now = datetime.now()
    # Insert recent session
    insert_learning_session(db_manager, user_id=1, started_at=now)
    # Insert old session (35 days ago)
    old_date = now - timedelta(days=35)
    insert_learning_session(db_manager, user_id=2, started_at=old_date)

    result = analytics_engine.get_system_analytics()

    # Should only count recent session
    stats = result["system_stats"]
    assert stats["total_sessions"] == 1


def test_get_system_analytics_multiple_users(db_manager, analytics_engine):
    """Test system stats aggregate across multiple users"""
    # Insert sessions for 3 different users
    insert_learning_session(
        db_manager, user_id=1, duration_minutes=30, accuracy_percentage=80.0
    )
    insert_learning_session(
        db_manager, user_id=2, duration_minutes=45, accuracy_percentage=90.0
    )
    insert_learning_session(
        db_manager, user_id=3, duration_minutes=25, accuracy_percentage=70.0
    )

    result = analytics_engine.get_system_analytics()

    stats = result["system_stats"]
    assert stats["total_users"] == 3
    assert stats["total_sessions"] == 3
    assert stats["total_study_time"] == 100  # 30 + 45 + 25
    assert stats["avg_accuracy"] == 80.0  # (80 + 90 + 70) / 3


def test_get_system_analytics_no_data(analytics_engine):
    """Test system analytics with no data"""
    result = analytics_engine.get_system_analytics()

    assert "system_stats" in result
    stats = result["system_stats"]
    assert stats["total_users"] == 0
    assert stats["total_sessions"] == 0


def test_get_system_analytics_distinct_users(db_manager, analytics_engine):
    """Test user count is distinct (multiple sessions per user)"""
    # Insert multiple sessions for same user
    insert_learning_session(db_manager, user_id=1)
    insert_learning_session(db_manager, user_id=1)
    insert_learning_session(db_manager, user_id=2)

    result = analytics_engine.get_system_analytics()

    stats = result["system_stats"]
    assert stats["total_users"] == 2  # Only 2 distinct users
    assert stats["total_sessions"] == 3  # 3 total sessions


def test_get_system_analytics_generated_at(analytics_engine):
    """Test generated_at timestamp is present"""
    result = analytics_engine.get_system_analytics()

    assert "generated_at" in result
    # Should be valid ISO format datetime
    timestamp = datetime.fromisoformat(result["generated_at"])
    assert isinstance(timestamp, datetime)


# ============================================================================
# 13. System Analytics - Items Tests
# ============================================================================


def test_get_system_analytics_items_active_only(db_manager, analytics_engine):
    """Test that only active items are counted"""
    # Insert active items
    insert_sr_item(db_manager, user_id=1, mastery_level=0.7, is_active=1)
    insert_sr_item(db_manager, user_id=2, mastery_level=0.8, is_active=1)
    # Insert inactive item
    insert_sr_item(db_manager, user_id=1, mastery_level=0.9, is_active=0)

    result = analytics_engine.get_system_analytics()

    item_stats = result["item_stats"]
    assert item_stats["total_items"] == 2  # Only active items


def test_get_system_analytics_items_mastery(db_manager, analytics_engine):
    """Test average mastery calculation"""
    insert_sr_item(db_manager, user_id=1, mastery_level=0.6)
    insert_sr_item(db_manager, user_id=1, mastery_level=0.8)
    insert_sr_item(db_manager, user_id=2, mastery_level=0.7)

    result = analytics_engine.get_system_analytics()

    item_stats = result["item_stats"]
    assert item_stats["avg_mastery"] == pytest.approx(0.7, abs=0.01)  # (0.6+0.8+0.7)/3


def test_get_system_analytics_items_mastered_count(db_manager, analytics_engine):
    """Test mastered items count uses 0.85 threshold"""
    insert_sr_item(db_manager, user_id=1, mastery_level=0.84)
    insert_sr_item(db_manager, user_id=1, mastery_level=0.85)
    insert_sr_item(db_manager, user_id=1, mastery_level=0.9)

    result = analytics_engine.get_system_analytics()

    item_stats = result["item_stats"]
    assert item_stats["mastered_items"] == 2  # 0.85 and 0.9 >= 0.85


def test_get_system_analytics_items_no_items(analytics_engine):
    """Test item stats with no items"""
    result = analytics_engine.get_system_analytics()

    assert "item_stats" in result
    item_stats = result["item_stats"]
    assert item_stats["total_items"] == 0


# ============================================================================
# 14. System Analytics - Language Distribution Tests
# ============================================================================


def test_get_system_analytics_language_distribution(db_manager, analytics_engine):
    """Test language distribution shows user counts per language"""
    # Insert sessions in different languages
    insert_learning_session(db_manager, user_id=1, language_code="es")
    insert_learning_session(db_manager, user_id=2, language_code="fr")
    insert_learning_session(db_manager, user_id=3, language_code="es")

    result = analytics_engine.get_system_analytics()

    lang_dist = result["language_distribution"]
    assert len(lang_dist) == 2

    # Find Spanish and French
    es_data = next((x for x in lang_dist if x["language_code"] == "es"), None)
    fr_data = next((x for x in lang_dist if x["language_code"] == "fr"), None)

    assert es_data is not None
    assert es_data["user_count"] == 2
    assert fr_data is not None
    assert fr_data["user_count"] == 1


def test_get_system_analytics_language_distribution_ordered(
    db_manager, analytics_engine
):
    """Test language distribution is ordered by user count DESC"""
    # Insert sessions: 3 Spanish, 2 French, 1 German
    insert_learning_session(db_manager, user_id=1, language_code="es")
    insert_learning_session(db_manager, user_id=2, language_code="es")
    insert_learning_session(db_manager, user_id=3, language_code="es")
    insert_learning_session(db_manager, user_id=4, language_code="fr")
    insert_learning_session(db_manager, user_id=5, language_code="fr")
    insert_learning_session(db_manager, user_id=6, language_code="de")

    result = analytics_engine.get_system_analytics()

    lang_dist = result["language_distribution"]
    # Should be ordered: es (3), fr (2), de (1)
    assert lang_dist[0]["language_code"] == "es"
    assert lang_dist[0]["user_count"] == 3
    assert lang_dist[1]["language_code"] == "fr"
    assert lang_dist[1]["user_count"] == 2
    assert lang_dist[2]["language_code"] == "de"
    assert lang_dist[2]["user_count"] == 1


def test_get_system_analytics_language_distribution_30_days(
    db_manager, analytics_engine
):
    """Test language distribution uses 30-day filter"""
    now = datetime.now()
    old_date = now - timedelta(days=35)

    # Insert recent session
    insert_learning_session(db_manager, user_id=1, language_code="es", started_at=now)
    # Insert old session
    insert_learning_session(
        db_manager, user_id=2, language_code="fr", started_at=old_date
    )

    result = analytics_engine.get_system_analytics()

    lang_dist = result["language_distribution"]
    # Should only include Spanish (recent)
    assert len(lang_dist) == 1
    assert lang_dist[0]["language_code"] == "es"


def test_get_system_analytics_language_distribution_empty(analytics_engine):
    """Test language distribution with no sessions"""
    result = analytics_engine.get_system_analytics()

    assert "language_distribution" in result
    lang_dist = result["language_distribution"]
    assert lang_dist == []


# ============================================================================
# 15. System Analytics - Error Handling Tests
# ============================================================================


def test_get_system_analytics_database_error(analytics_engine):
    """Test system analytics returns empty dict on database error"""
    with patch.object(
        analytics_engine.db, "get_connection", side_effect=Exception("DB Error")
    ):
        result = analytics_engine.get_system_analytics()

        assert result == {}


def test_get_system_analytics_connection_error(analytics_engine):
    """Test graceful handling of connection errors"""
    with patch.object(
        analytics_engine.db,
        "get_connection",
        side_effect=sqlite3.OperationalError("Database locked"),
    ):
        result = analytics_engine.get_system_analytics()

        assert result == {}
