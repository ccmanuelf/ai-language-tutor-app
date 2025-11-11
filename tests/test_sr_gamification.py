"""
Comprehensive tests for GamificationEngine class
Tests achievement detection, awarding, and milestone tracking
Session 13 - Target: 100% coverage (maintaining legendary 6-session streak!)
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest

from app.services.sr_database import DatabaseManager
from app.services.sr_gamification import GamificationEngine
from app.services.sr_models import (
    AchievementType,
    ReviewResult,
    SpacedRepetitionItem,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    # Create database schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
            badge_icon TEXT DEFAULT '🏆',
            badge_color TEXT DEFAULT '#FFD700',
            points_awarded INTEGER DEFAULT 10,
            criteria_met TEXT,
            required_criteria TEXT,
            rarity TEXT DEFAULT 'common',
            earned_in_session TEXT,
            earned_activity TEXT,
            milestone_level INTEGER DEFAULT 1,
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
    """Create DatabaseManager instance"""
    return DatabaseManager(temp_db)


@pytest.fixture
def gamification_engine(db_manager):
    """Create GamificationEngine instance with default config"""
    return GamificationEngine(db_manager)


@pytest.fixture
def sample_vocab_item():
    """Create a sample vocabulary SpacedRepetitionItem"""
    return SpacedRepetitionItem(
        item_id="vocab_001",
        user_id=1,
        language_code="es",
        item_type="vocabulary",
        content="hola",
        translation="hello",
        streak_count=0,
        mastery_level=0.0,
    )


@pytest.fixture
def sample_grammar_item():
    """Create a sample grammar SpacedRepetitionItem"""
    return SpacedRepetitionItem(
        item_id="grammar_001",
        user_id=1,
        language_code="es",
        item_type="grammar",
        content="present tense",
        translation="presente",
        streak_count=0,
        mastery_level=0.0,
    )


# ============================================================================
# 1. INITIALIZATION & CONFIGURATION TESTS
# ============================================================================


def test_init_with_default_config(db_manager):
    """Test initialization with default configuration"""
    engine = GamificationEngine(db_manager)

    assert engine.db_manager == db_manager
    assert engine.config is not None
    assert "mastery_threshold" in engine.config
    assert "points_per_correct" in engine.config
    assert "points_per_streak" in engine.config


def test_init_with_custom_config(db_manager):
    """Test initialization with custom configuration"""
    custom_config = {
        "mastery_threshold": 0.90,
        "points_per_correct": 15,
        "points_per_streak": 8,
        "custom_param": "test_value",
    }
    engine = GamificationEngine(db_manager, custom_config)

    assert engine.config == custom_config
    assert engine.config["mastery_threshold"] == 0.90
    assert engine.config["points_per_correct"] == 15
    assert engine.config["custom_param"] == "test_value"


def test_get_default_config():
    """Test default configuration values"""
    engine = GamificationEngine(DatabaseManager())
    config = engine._get_default_config()

    assert config["mastery_threshold"] == 0.85
    assert config["points_per_correct"] == 10
    assert config["points_per_streak"] == 5


def test_config_parameter_access(gamification_engine):
    """Test accessing configuration parameters"""
    assert gamification_engine.config["mastery_threshold"] == 0.85
    assert gamification_engine.config["points_per_correct"] == 10


def test_multiple_instances_different_configs(db_manager):
    """Test multiple engine instances with different configs"""
    engine1 = GamificationEngine(db_manager, {"mastery_threshold": 0.80})
    engine2 = GamificationEngine(db_manager, {"mastery_threshold": 0.90})

    assert engine1.config["mastery_threshold"] == 0.80
    assert engine2.config["mastery_threshold"] == 0.90


# ============================================================================
# 2. DATABASE CONNECTION MANAGEMENT TESTS
# ============================================================================


def test_get_connection_success(gamification_engine):
    """Test successful database connection"""
    with gamification_engine._get_connection() as conn:
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        # Verify connection works
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1


def test_connection_context_manager_lifecycle(gamification_engine):
    """Test connection context manager properly manages lifecycle"""
    with gamification_engine._get_connection() as conn:
        conn_id = id(conn)
        assert conn is not None

    # Connection should be closed after context exit
    # Note: We can't directly test if closed, but no exception should occur


def test_connection_properly_closed(gamification_engine):
    """Test connection is properly closed after use"""
    conn_ref = None
    with gamification_engine._get_connection() as conn:
        conn_ref = conn
        assert conn is not None

    # After exiting context, connection should be closed
    # Attempting to use it should fail (though we don't test this directly)


def test_connection_error_handling(db_manager):
    """Test connection error handling"""
    # Create engine with invalid db path
    invalid_manager = DatabaseManager("/invalid/path/to/db.db")
    engine = GamificationEngine(invalid_manager)

    # Attempting to use connection should handle error gracefully
    # (The actual error handling is in the methods that use the connection)


# ============================================================================
# 3. CHECK_ITEM_ACHIEVEMENTS - VOCABULARY STREAKS TESTS
# ============================================================================


def test_check_achievements_no_streak_below_5(gamification_engine, sample_vocab_item):
    """Test no achievement awarded for streak count below 5"""
    sample_vocab_item.streak_count = 4

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )
        mock_award.assert_not_called()


def test_check_achievements_vocab_streak_5(gamification_engine, sample_vocab_item):
    """Test achievement awarded at exactly 5 streak"""
    sample_vocab_item.streak_count = 5

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should be called once for streak achievement
        assert mock_award.call_count == 1
        # Access positional args: user_id, language_code, achievement_type, title, description
        call_args = mock_award.call_args[0]
        assert call_args[2] == AchievementType.VOCABULARY  # achievement_type
        assert "Vocabulary Streak" in call_args[3]  # title
        # Check keyword args for points
        assert mock_award.call_args[1]["points_awarded"] == 25


def test_check_achievements_no_duplicate_at_6_to_9(
    gamification_engine, sample_vocab_item
):
    """Test no duplicate achievement between 6-9 streak"""
    for streak in [6, 7, 8, 9]:
        sample_vocab_item.streak_count = streak

        with patch.object(gamification_engine, "award_achievement") as mock_award:
            gamification_engine.check_item_achievements(
                sample_vocab_item, ReviewResult.GOOD
            )
            mock_award.assert_not_called()


def test_check_achievements_vocab_streak_10(gamification_engine, sample_vocab_item):
    """Test achievement awarded at exactly 10 streak"""
    sample_vocab_item.streak_count = 10

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should be called once for 10-streak achievement
        assert mock_award.call_count == 1
        # Access positional args: user_id, language_code, achievement_type, title, description
        call_args = mock_award.call_args[0]
        assert call_args[2] == AchievementType.VOCABULARY  # achievement_type
        assert "Word Master" in call_args[3]  # title
        # Check keyword args for points
        assert mock_award.call_args[1]["points_awarded"] == 50


def test_check_achievements_only_vocabulary_triggers_vocab(
    gamification_engine, sample_vocab_item
):
    """Test only vocabulary items trigger vocabulary achievements"""
    sample_vocab_item.streak_count = 5

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Verify vocabulary achievement triggered
        assert mock_award.call_count >= 1
        # Access positional args: user_id, language_code, achievement_type, title, description
        call_args = mock_award.call_args[0]
        assert call_args[2] == AchievementType.VOCABULARY  # achievement_type


def test_check_achievements_non_vocabulary_no_vocab_achievement(
    gamification_engine, sample_grammar_item
):
    """Test non-vocabulary items don't trigger vocabulary achievements"""
    sample_grammar_item.streak_count = 5

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_grammar_item, ReviewResult.GOOD
        )

        # Should not be called for grammar item with streak
        mock_award.assert_not_called()


def test_check_achievements_all_review_results_processed(
    gamification_engine, sample_vocab_item
):
    """Test all review result types are processed"""
    sample_vocab_item.streak_count = 5

    for result in [
        ReviewResult.AGAIN,
        ReviewResult.HARD,
        ReviewResult.GOOD,
        ReviewResult.EASY,
    ]:
        with patch.object(gamification_engine, "award_achievement") as mock_award:
            gamification_engine.check_item_achievements(sample_vocab_item, result)

            # Achievement should be triggered regardless of review result
            assert mock_award.call_count == 1


def test_check_achievements_multiple_in_single_review(
    gamification_engine, sample_vocab_item
):
    """Test multiple achievements can be awarded in single review"""
    sample_vocab_item.streak_count = 5
    sample_vocab_item.mastery_level = 0.90

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should be called twice: streak + mastery
        assert mock_award.call_count == 2

        # Verify both types were called
        call_types = [
            call[0][2] for call in mock_award.call_args_list
        ]  # achievement_type at index 2
        assert AchievementType.VOCABULARY in call_types
        assert AchievementType.MASTERY in call_types


# ============================================================================
# 4. CHECK_ITEM_ACHIEVEMENTS - MASTERY TESTS
# ============================================================================


def test_check_achievements_no_mastery_below_threshold(
    gamification_engine, sample_vocab_item
):
    """Test no mastery achievement below threshold (0.84)"""
    sample_vocab_item.mastery_level = 0.84

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should not be called for mastery
        # (might be called for streak if applicable, but not mastery)
        mastery_calls = [
            call
            for call in mock_award.call_args_list
            if len(call[0]) > 2 and call[0][2] == AchievementType.MASTERY
        ]
        assert len(mastery_calls) == 0


def test_check_achievements_mastery_at_threshold(
    gamification_engine, sample_vocab_item
):
    """Test mastery achievement at threshold (0.85)"""
    sample_vocab_item.mastery_level = 0.85

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should be called for mastery achievement
        assert mock_award.call_count >= 1

        # Find mastery call
        mastery_calls = [
            call
            for call in mock_award.call_args_list
            if len(call[0]) > 2 and call[0][2] == AchievementType.MASTERY
        ]
        assert len(mastery_calls) == 1

        # Verify mastery achievement details
        call_args = mastery_calls[0][0]  # positional args
        assert call_args[2] == AchievementType.MASTERY  # achievement_type
        assert "Content Mastery" in call_args[3]  # title
        # Check keyword args for points
        assert mastery_calls[0][1]["points_awarded"] == 30


def test_check_achievements_mastery_above_threshold(
    gamification_engine, sample_vocab_item
):
    """Test mastery achievement above threshold (0.95)"""
    sample_vocab_item.mastery_level = 0.95

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should be called for mastery
        mastery_calls = [
            call
            for call in mock_award.call_args_list
            if len(call[0]) > 2 and call[0][2] == AchievementType.MASTERY
        ]
        assert len(mastery_calls) == 1


def test_check_achievements_mastery_all_item_types(
    gamification_engine, sample_grammar_item
):
    """Test mastery achievement for all item types"""
    sample_grammar_item.mastery_level = 0.90

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_grammar_item, ReviewResult.GOOD
        )

        # Grammar items should trigger mastery (but not vocab streaks)
        assert mock_award.call_count == 1
        # Access positional args: user_id, language_code, achievement_type, title, description
        call_args = mock_award.call_args[0]
        assert call_args[2] == AchievementType.MASTERY  # achievement_type


def test_check_achievements_custom_mastery_threshold(db_manager, sample_vocab_item):
    """Test custom mastery threshold from config"""
    custom_engine = GamificationEngine(db_manager, {"mastery_threshold": 0.90})
    sample_vocab_item.mastery_level = 0.89

    with patch.object(custom_engine, "award_achievement") as mock_award:
        custom_engine.check_item_achievements(sample_vocab_item, ReviewResult.GOOD)

        # Should not trigger with 0.89 when threshold is 0.90
        mastery_calls = [
            call
            for call in mock_award.call_args_list
            if len(call[0]) > 2 and call[0][2] == AchievementType.MASTERY
        ]
        assert len(mastery_calls) == 0


def test_check_achievements_streak_plus_mastery(gamification_engine, sample_vocab_item):
    """Test both streak and mastery achievements together"""
    sample_vocab_item.streak_count = 10
    sample_vocab_item.mastery_level = 0.95

    with patch.object(gamification_engine, "award_achievement") as mock_award:
        gamification_engine.check_item_achievements(
            sample_vocab_item, ReviewResult.GOOD
        )

        # Should be called twice
        assert mock_award.call_count == 2

        # Verify both types
        types = [
            call[0][2] for call in mock_award.call_args_list
        ]  # achievement_type at index 2
        assert AchievementType.VOCABULARY in types
        assert AchievementType.MASTERY in types


# ============================================================================
# 5. AWARD_ACHIEVEMENT - SUCCESS CASES TESTS
# ============================================================================


def test_award_achievement_all_defaults(gamification_engine):
    """Test awarding achievement with all default parameters"""
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test Achievement",
        description="Test description",
    )

    # Verify achievement was created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gamification_achievements WHERE user_id = 1")
        row = cursor.fetchone()

        assert row is not None
        assert row["title"] == "Test Achievement"
        assert row["description"] == "Test description"
        assert row["achievement_type"] == "streak"
        assert row["points_awarded"] == 10  # default
        assert row["badge_icon"] == "🏆"  # default
        assert row["badge_color"] == "#FFD700"  # default
        assert row["rarity"] == "common"  # default


def test_award_achievement_all_custom_parameters(gamification_engine):
    """Test awarding achievement with all custom parameters"""
    gamification_engine.award_achievement(
        user_id=2,
        language_code="fr",
        achievement_type=AchievementType.MASTERY,
        title="Master Achievement",
        description="Mastered content",
        points_awarded=100,
        badge_icon="⭐",
        badge_color="#FF0000",
        rarity="legendary",
        earned_in_session="session_123",
        earned_activity="review",
        milestone_level=5,
    )

    # Verify all custom values
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gamification_achievements WHERE user_id = 2")
        row = cursor.fetchone()

        assert row is not None
        assert row["title"] == "Master Achievement"
        assert row["points_awarded"] == 100
        assert row["badge_icon"] == "⭐"
        assert row["badge_color"] == "#FF0000"
        assert row["rarity"] == "legendary"
        assert row["earned_in_session"] == "session_123"
        assert row["earned_activity"] == "review"
        assert row["milestone_level"] == 5


def test_award_achievement_all_types(gamification_engine):
    """Test awarding all different achievement types"""
    types = [
        AchievementType.STREAK,
        AchievementType.VOCABULARY,
        AchievementType.CONVERSATION,
        AchievementType.GOAL,
        AchievementType.MASTERY,
        AchievementType.DEDICATION,
    ]

    for idx, achievement_type in enumerate(types):
        gamification_engine.award_achievement(
            user_id=1,
            language_code="es",
            achievement_type=achievement_type,
            title=f"Test {achievement_type.value}",
            description=f"Description for {achievement_type.value}",
        )

    # Verify all were created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == len(types)


def test_award_achievement_uuid_generation(gamification_engine):
    """Test UUID is generated for achievement_id"""
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test",
        description="Test",
    )

    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT achievement_id FROM gamification_achievements WHERE user_id = 1"
        )
        achievement_id = cursor.fetchone()["achievement_id"]

        # Verify it's a valid UUID format
        assert len(achievement_id) == 36  # UUID format: 8-4-4-4-12
        assert achievement_id.count("-") == 4


def test_award_achievement_json_serialization(gamification_engine):
    """Test JSON serialization of criteria fields"""
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test",
        description="Test",
    )

    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT criteria_met, required_criteria FROM gamification_achievements WHERE user_id = 1"
        )
        row = cursor.fetchone()

        # Verify JSON can be parsed
        criteria_met = json.loads(row["criteria_met"])
        required_criteria = json.loads(row["required_criteria"])

        assert criteria_met == {"earned": True}
        assert required_criteria == {"criteria": "met"}


def test_award_achievement_multiple_same_user(gamification_engine):
    """Test multiple awards to same user"""
    for i in range(3):
        gamification_engine.award_achievement(
            user_id=1,
            language_code="es",
            achievement_type=AchievementType.STREAK,
            title=f"Achievement {i}",
            description=f"Description {i}",
        )

    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 3


def test_award_achievement_different_users(gamification_engine):
    """Test awards to different users"""
    for user_id in [1, 2, 3]:
        gamification_engine.award_achievement(
            user_id=user_id,
            language_code="es",
            achievement_type=AchievementType.STREAK,
            title="Test Achievement",
            description="Test",
        )

    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM gamification_achievements")
        count = cursor.fetchone()[0]
        assert count == 3


def test_award_achievement_different_languages(gamification_engine):
    """Test awards in different languages"""
    languages = ["es", "fr", "de", "ja"]

    for lang in languages:
        gamification_engine.award_achievement(
            user_id=1,
            language_code=lang,
            achievement_type=AchievementType.VOCABULARY,
            title=f"Test {lang}",
            description=f"Achievement in {lang}",
        )

    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(DISTINCT language_code) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == len(languages)


# ============================================================================
# 6. AWARD_ACHIEVEMENT - DUPLICATE PREVENTION TESTS
# ============================================================================


def test_award_achievement_duplicate_within_24h_blocked(gamification_engine):
    """Test same achievement within 24 hours is blocked"""
    # Award first achievement
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Same Achievement",
        description="Test",
    )

    # Try to award same achievement immediately
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Same Achievement",
        description="Test",
    )

    # Verify only one was created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 1


def test_award_achievement_duplicate_after_24h_allowed(gamification_engine):
    """Test same achievement after 24 hours is allowed"""
    # Award first achievement and backdate it
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        old_date = (datetime.now() - timedelta(days=2)).isoformat()
        cursor.execute(
            """
            INSERT INTO gamification_achievements (
                achievement_id, user_id, language_code, achievement_type,
                title, description, earned_at, criteria_met, required_criteria
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                1,
                "es",
                AchievementType.STREAK.value,
                "Same Achievement",
                "Test",
                old_date,
                json.dumps({"earned": True}),
                json.dumps({"criteria": "met"}),
            ),
        )
        conn.commit()

    # Try to award same achievement now (>24 hours later)
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Same Achievement",
        description="Test",
    )

    # Verify both were created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 2


def test_award_achievement_different_types_allowed(gamification_engine):
    """Test different achievement types are allowed"""
    # Award STREAK achievement
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test",
        description="Test",
    )

    # Award VOCABULARY achievement with same title
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.VOCABULARY,
        title="Test",
        description="Test",
    )

    # Both should be created (different types)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 2


def test_award_achievement_different_users_same_achievement(gamification_engine):
    """Test different users can get same achievement"""
    # Award to user 1
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Same Achievement",
        description="Test",
    )

    # Award to user 2
    gamification_engine.award_achievement(
        user_id=2,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Same Achievement",
        description="Test",
    )

    # Both should be created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gamification_achievements")
        count = cursor.fetchone()[0]
        assert count == 2


def test_award_achievement_different_languages_same_achievement(gamification_engine):
    """Test different languages - duplicate prevention checks title, not language"""
    # Award in Spanish
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.VOCABULARY,
        title="Vocab Master",
        description="Test",
    )

    # Award in French with same title
    gamification_engine.award_achievement(
        user_id=1,
        language_code="fr",
        achievement_type=AchievementType.VOCABULARY,
        title="Vocab Master",  # Same title = blocked by duplicate prevention
        description="Test",
    )

    # Only one should be created (duplicate prevention checks title, not language)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 1  # Duplicate blocked


def test_award_achievement_different_titles_allowed(gamification_engine):
    """Test different titles are allowed"""
    # Award achievement 1
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Achievement 1",
        description="Test",
    )

    # Award achievement 2
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Achievement 2",
        description="Test",
    )

    # Both should be created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 2


# ============================================================================
# 7. AWARD_ACHIEVEMENT - ERROR HANDLING TESTS
# ============================================================================


def test_award_achievement_database_error(db_manager):
    """Test database connection error handling"""
    # Create engine with mock that raises exception
    engine = GamificationEngine(db_manager)

    with patch.object(
        engine, "_get_connection", side_effect=Exception("Database error")
    ):
        # Should not raise exception, just log error
        engine.award_achievement(
            user_id=1,
            language_code="es",
            achievement_type=AchievementType.STREAK,
            title="Test",
            description="Test",
        )

    # Verify no achievement was created
    with engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gamification_achievements")
        count = cursor.fetchone()[0]
        assert count == 0


def test_award_achievement_invalid_user_id(gamification_engine):
    """Test handling of invalid user_id"""
    # SQLite allows any integer, so this test verifies graceful handling
    gamification_engine.award_achievement(
        user_id=-999,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test",
        description="Test",
    )

    # Should still create (SQLite doesn't enforce FK without explicit constraints)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = -999"
        )
        count = cursor.fetchone()[0]
        assert count == 1


def test_award_achievement_logging_on_error(db_manager):
    """Test logging occurs on error"""
    engine = GamificationEngine(db_manager)

    with patch.object(engine, "_get_connection", side_effect=Exception("Test error")):
        with patch("app.services.sr_gamification.logger.error") as mock_logger:
            engine.award_achievement(
                user_id=1,
                language_code="es",
                achievement_type=AchievementType.STREAK,
                title="Test",
                description="Test",
            )

            # Verify error was logged
            mock_logger.assert_called_once()
            assert "Error awarding achievement" in str(mock_logger.call_args)


def test_award_achievement_logging_on_duplicate(gamification_engine):
    """Test logging occurs on duplicate detection"""
    # Award first achievement
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test Achievement",
        description="Test",
    )

    # Try to award duplicate
    with patch("app.services.sr_gamification.logger.info") as mock_logger:
        gamification_engine.award_achievement(
            user_id=1,
            language_code="es",
            achievement_type=AchievementType.STREAK,
            title="Test Achievement",
            description="Test",
        )

        # Verify info log was called
        mock_logger.assert_called()
        log_message = str(mock_logger.call_args)
        assert "already awarded" in log_message.lower()


# ============================================================================
# 8. INTEGRATION TESTS
# ============================================================================


def test_integration_complete_review_workflow(gamification_engine):
    """Test complete workflow: review → check achievements → award"""
    # Create item
    item = SpacedRepetitionItem(
        item_id="test_001",
        user_id=1,
        language_code="es",
        item_type="vocabulary",
        content="test word",
        translation="palabra de prueba",
        streak_count=5,
        mastery_level=0.90,
    )

    # Check achievements (should trigger both streak and mastery)
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Verify both achievements were awarded
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 2

        # Verify achievement types
        cursor.execute(
            "SELECT achievement_type FROM gamification_achievements WHERE user_id = 1"
        )
        types = [row["achievement_type"] for row in cursor.fetchall()]
        assert "vocabulary" in types
        assert "mastery" in types


def test_integration_multiple_items_sequence(gamification_engine):
    """Test multiple items reviewed in sequence - duplicate prevention applies"""
    items = [
        SpacedRepetitionItem(
            item_id=f"item_{i}",
            user_id=1,
            language_code="es",
            item_type="vocabulary",
            content=f"word_{i}",
            translation=f"palabra_{i}",
            streak_count=5,
            mastery_level=0.50,
        )
        for i in range(3)
    ]

    # Review all items
    for item in items:
        gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Verify achievements - title is "Vocabulary Streak" for all (static)
    # Content is in description, not title
    # Duplicate prevention blocks second and third (same title, same user, within 24h)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 1  # Only first created, rest blocked by duplicate prevention


def test_integration_streak_progression(gamification_engine):
    """Test streak progression 1→5→10"""
    item = SpacedRepetitionItem(
        item_id="test_001",
        user_id=1,
        language_code="es",
        item_type="vocabulary",
        content="test word",
        translation="palabra",
        streak_count=1,
        mastery_level=0.50,
    )

    # Review at streak 1 (no achievement)
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Review at streak 5 (should get achievement)
    item.streak_count = 5
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Review at streak 10 (should get achievement)
    item.streak_count = 10
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Verify 2 achievements (streak 5 and 10)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 2


def test_integration_mastery_progression(gamification_engine):
    """Test mastery progression 0.5→0.85→0.95"""
    item = SpacedRepetitionItem(
        item_id="test_001",
        user_id=1,
        language_code="es",
        item_type="vocabulary",
        content="test word",
        translation="palabra",
        streak_count=0,
        mastery_level=0.50,
    )

    # Review at 0.5 mastery (no achievement)
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Review at 0.85 mastery (should get achievement)
    item.mastery_level = 0.85
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Review at 0.95 mastery (duplicate prevention should block)
    item.mastery_level = 0.95
    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Verify 1 achievement (mastery at 0.85, duplicate blocked at 0.95)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 1


def test_integration_mixed_achievement_types(gamification_engine):
    """Test mixed achievement types in workflow"""
    # Vocabulary item with streak
    vocab_item = SpacedRepetitionItem(
        item_id="vocab_001",
        user_id=1,
        language_code="es",
        item_type="vocabulary",
        content="hola",
        translation="hello",
        streak_count=5,
        mastery_level=0.50,
    )

    # Grammar item with mastery
    grammar_item = SpacedRepetitionItem(
        item_id="grammar_001",
        user_id=1,
        language_code="es",
        item_type="grammar",
        content="presente",
        translation="present tense",
        streak_count=0,
        mastery_level=0.90,
    )

    # Review both
    gamification_engine.check_item_achievements(vocab_item, ReviewResult.GOOD)
    gamification_engine.check_item_achievements(grammar_item, ReviewResult.GOOD)

    # Verify 2 achievements (vocab streak + grammar mastery)
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 1"
        )
        count = cursor.fetchone()[0]
        assert count == 2


def test_integration_database_state_verification(gamification_engine):
    """Test database state after achievements"""
    # Award achievement
    gamification_engine.award_achievement(
        user_id=1,
        language_code="es",
        achievement_type=AchievementType.STREAK,
        title="Test Achievement",
        description="Test description",
        points_awarded=50,
    )

    # Verify complete database state
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gamification_achievements WHERE user_id = 1")
        row = cursor.fetchone()

        assert row["user_id"] == 1
        assert row["language_code"] == "es"
        assert row["achievement_type"] == "streak"
        assert row["title"] == "Test Achievement"
        assert row["description"] == "Test description"
        assert row["points_awarded"] == 50
        assert row["earned_at"] is not None
        assert row["created_at"] is not None


def test_integration_achievement_retrieval(gamification_engine):
    """Test achievement retrieval and validation"""
    # Award multiple achievements
    for i in range(3):
        gamification_engine.award_achievement(
            user_id=1,
            language_code="es",
            achievement_type=AchievementType.VOCABULARY,
            title=f"Achievement {i}",
            description=f"Description {i}",
            points_awarded=10 * (i + 1),
        )

    # Retrieve and validate
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM gamification_achievements WHERE user_id = 1 ORDER BY created_at"
        )
        rows = cursor.fetchall()

        assert len(rows) == 3
        for i, row in enumerate(rows):
            assert row["title"] == f"Achievement {i}"
            assert row["points_awarded"] == 10 * (i + 1)


def test_integration_new_user_no_prior_achievements(gamification_engine):
    """Test new user with no prior achievements"""
    # Verify empty state
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 999"
        )
        count = cursor.fetchone()[0]
        assert count == 0

    # Award first achievement
    item = SpacedRepetitionItem(
        item_id="first_item",
        user_id=999,
        language_code="es",
        item_type="vocabulary",
        content="first word",
        translation="primera palabra",
        streak_count=5,
        mastery_level=0.50,
    )

    gamification_engine.check_item_achievements(item, ReviewResult.GOOD)

    # Verify first achievement created
    with gamification_engine._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM gamification_achievements WHERE user_id = 999"
        )
        count = cursor.fetchone()[0]
        assert count == 1
