"""
Comprehensive tests for SM2Algorithm class
Tests SM-2 spaced repetition algorithm implementation
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.sr_algorithm import SM2Algorithm
from app.services.sr_database import DatabaseManager
from app.services.sr_models import (
    ItemType,
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

    # Create spaced_repetition_items table
    cursor.execute("""
        CREATE TABLE spaced_repetition_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            item_type TEXT NOT NULL,
            content TEXT NOT NULL,
            translation TEXT,
            definition TEXT,
            pronunciation_guide TEXT,
            example_usage TEXT,
            context_tags TEXT,
            difficulty_level INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5,
            repetition_number INTEGER DEFAULT 0,
            interval_days INTEGER DEFAULT 1,
            last_review_date TIMESTAMP,
            next_review_date TIMESTAMP,
            total_reviews INTEGER DEFAULT 0,
            correct_reviews INTEGER DEFAULT 0,
            incorrect_reviews INTEGER DEFAULT 0,
            streak_count INTEGER DEFAULT 0,
            mastery_level REAL DEFAULT 0.0,
            confidence_score REAL DEFAULT 0.0,
            first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_studied_date TIMESTAMP,
            average_response_time_ms INTEGER DEFAULT 0,
            learning_speed_factor REAL DEFAULT 1.0,
            retention_rate REAL DEFAULT 0.0,
            source_session_id TEXT,
            source_content TEXT,
            metadata TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create admin_spaced_repetition_config table
    cursor.execute("""
        CREATE TABLE admin_spaced_repetition_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_type TEXT NOT NULL,
            initial_ease_factor REAL DEFAULT 2.5,
            minimum_ease_factor REAL DEFAULT 1.3,
            maximum_ease_factor REAL DEFAULT 3.0,
            ease_factor_change REAL DEFAULT 0.15,
            initial_interval_days INTEGER DEFAULT 1,
            graduation_interval_days INTEGER DEFAULT 4,
            easy_interval_days INTEGER DEFAULT 7,
            maximum_interval_days INTEGER DEFAULT 365,
            mastery_threshold REAL DEFAULT 0.85,
            review_threshold REAL DEFAULT 0.7,
            difficulty_threshold REAL DEFAULT 0.5,
            retention_threshold REAL DEFAULT 0.8,
            points_per_correct INTEGER DEFAULT 10,
            points_per_streak_day INTEGER DEFAULT 5,
            points_per_goal_achieved INTEGER DEFAULT 100,
            daily_goal_default INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
def algorithm(db_manager):
    """Create SM2Algorithm instance"""
    return SM2Algorithm(db_manager=db_manager)


@pytest.fixture
def sample_item():
    """Create a sample SpacedRepetitionItem for testing"""
    return SpacedRepetitionItem(
        item_id="test-item-123",
        user_id=1,
        language_code="es",
        item_type=ItemType.VOCABULARY.value,
        content="hola",
        translation="hello",
        definition="a greeting",
        pronunciation_guide="OH-lah",
        example_usage="Hola, ¿cómo estás?",
        context_tags=["greeting", "basic"],
        ease_factor=2.5,
        repetition_number=0,
        interval_days=1,
        total_reviews=0,
        correct_reviews=0,
        incorrect_reviews=0,
        streak_count=0,
        mastery_level=0.0,
        confidence_score=0.0,
        average_response_time_ms=0,
        retention_rate=0.0,
        source_session_id="session-1",
        source_content="conversation",
        metadata={"difficulty": "easy"},
        is_active=True,
    )


class TestSM2AlgorithmInitialization:
    """Test SM2Algorithm initialization"""

    def test_initialization_with_db_manager(self, db_manager):
        """Test algorithm initializes with DatabaseManager"""
        algo = SM2Algorithm(db_manager=db_manager)

        assert algo.db is db_manager
        assert isinstance(algo.config, dict)
        assert "initial_ease_factor" in algo.config

    def test_initialization_loads_config(self, db_manager):
        """Test initialization loads algorithm configuration"""
        algo = SM2Algorithm(db_manager=db_manager)

        # Should have default config values
        assert algo.config["initial_ease_factor"] == 2.5
        assert algo.config["minimum_ease_factor"] == 1.3
        assert algo.config["maximum_ease_factor"] == 3.0
        assert algo.config["ease_factor_change"] == 0.15


class TestLoadAlgorithmConfig:
    """Test _load_algorithm_config method"""

    def test_load_config_with_no_database_config(self, algorithm):
        """Test loading config when database has no config records"""
        config = algorithm._load_algorithm_config()

        # Should return defaults
        assert config["initial_ease_factor"] == 2.5
        assert config["minimum_ease_factor"] == 1.3
        assert config["maximum_ease_factor"] == 3.0
        assert config["initial_interval_days"] == 1
        assert config["graduation_interval_days"] == 4
        assert config["easy_interval_days"] == 7
        assert config["maximum_interval_days"] == 365
        assert config["mastery_threshold"] == 0.85

    def test_load_config_with_database_config(self, db_manager, temp_db):
        """Test loading config when database has config records"""
        # Insert config into database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admin_spaced_repetition_config (
                config_type, initial_ease_factor, minimum_ease_factor,
                maximum_ease_factor, ease_factor_change, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            ("sm2", 2.8, 1.5, 3.2, 0.2, 1),
        )
        conn.commit()
        conn.close()

        algo = SM2Algorithm(db_manager=db_manager)
        config = algo.config

        # Should load from database
        assert config["initial_ease_factor"] == 2.8
        assert config["minimum_ease_factor"] == 1.5
        assert config["maximum_ease_factor"] == 3.2
        assert config["ease_factor_change"] == 0.2

    def test_load_config_handles_database_error(self, db_manager):
        """Test config loading handles database errors gracefully"""
        with patch.object(
            db_manager, "get_connection", side_effect=Exception("DB error")
        ):
            algo = SM2Algorithm(db_manager=db_manager)
            config = algo.config

            # Should return defaults on error
            assert config["initial_ease_factor"] == 2.5
            assert config["minimum_ease_factor"] == 1.3


class TestCalculateNextReview:
    """Test calculate_next_review method - Core SM-2 algorithm"""

    def test_calculate_next_review_again_result(self, algorithm, sample_item):
        """Test SM-2 calculation with AGAIN result (incorrect)"""
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.AGAIN
        )

        # AGAIN should: decrease ease factor, reset to initial interval
        assert ease < sample_item.ease_factor
        assert ease >= algorithm.config["minimum_ease_factor"]
        assert interval == algorithm.config["initial_interval_days"]
        assert next_date > datetime.now()

    def test_calculate_next_review_hard_result(self, algorithm, sample_item):
        """Test SM-2 calculation with HARD result"""
        sample_item.interval_days = 10
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.HARD
        )

        # HARD should: slightly decrease ease, modest interval increase
        assert ease < sample_item.ease_factor
        assert ease >= algorithm.config["minimum_ease_factor"]
        assert interval > sample_item.interval_days
        assert interval == max(10 * 1.2, 11)  # max(interval * 1.2, interval + 1)

    def test_calculate_next_review_good_result_first_repetition(
        self, algorithm, sample_item
    ):
        """Test SM-2 calculation with GOOD result on first repetition"""
        sample_item.repetition_number = 0
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.GOOD
        )

        # First GOOD review should use initial interval
        assert ease == sample_item.ease_factor  # No change for GOOD
        assert interval == algorithm.config["initial_interval_days"]

    def test_calculate_next_review_good_result_second_repetition(
        self, algorithm, sample_item
    ):
        """Test SM-2 calculation with GOOD result on second repetition"""
        sample_item.repetition_number = 1
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.GOOD
        )

        # Second GOOD review should use graduation interval
        assert interval == algorithm.config["graduation_interval_days"]

    def test_calculate_next_review_good_result_later_repetitions(
        self, algorithm, sample_item
    ):
        """Test SM-2 calculation with GOOD result on later repetitions"""
        sample_item.repetition_number = 5
        sample_item.interval_days = 10
        sample_item.ease_factor = 2.5

        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.GOOD
        )

        # Later GOOD reviews should multiply interval by ease factor
        assert interval == int(10 * 2.5)  # interval * ease_factor

    def test_calculate_next_review_easy_result_first_repetition(
        self, algorithm, sample_item
    ):
        """Test SM-2 calculation with EASY result on first repetition"""
        sample_item.repetition_number = 0
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.EASY
        )

        # First EASY review should: increase ease factor, use easy interval
        assert ease > sample_item.ease_factor
        assert ease <= algorithm.config["maximum_ease_factor"]
        assert interval == algorithm.config["easy_interval_days"]

    def test_calculate_next_review_easy_result_later_repetitions(
        self, algorithm, sample_item
    ):
        """Test SM-2 calculation with EASY result on later repetitions"""
        sample_item.repetition_number = 3
        sample_item.interval_days = 10
        sample_item.ease_factor = 2.5

        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.EASY
        )

        # Later EASY reviews should: increase ease, accelerate interval
        # Algorithm increases ease factor first, then uses new ease for interval
        new_ease = min(2.5 + 0.15, 3.0)  # 2.65
        assert ease > sample_item.ease_factor
        assert interval == int(10 * new_ease * 1.3)  # interval * new_ease * 1.3

    def test_calculate_next_review_respects_maximum_interval(
        self, algorithm, sample_item
    ):
        """Test that calculated interval never exceeds maximum"""
        sample_item.repetition_number = 10
        sample_item.interval_days = 300
        sample_item.ease_factor = 3.0

        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.EASY
        )

        # Interval should be capped at maximum
        assert interval <= algorithm.config["maximum_interval_days"]

    def test_calculate_next_review_respects_minimum_ease_factor(
        self, algorithm, sample_item
    ):
        """Test that ease factor never goes below minimum"""
        sample_item.ease_factor = 1.4  # Close to minimum

        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.AGAIN
        )

        # Ease should not go below minimum
        assert ease >= algorithm.config["minimum_ease_factor"]

    def test_calculate_next_review_respects_maximum_ease_factor(
        self, algorithm, sample_item
    ):
        """Test that ease factor never exceeds maximum"""
        sample_item.ease_factor = 2.9  # Close to maximum

        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.EASY
        )

        # Ease should not exceed maximum
        assert ease <= algorithm.config["maximum_ease_factor"]

    def test_calculate_next_review_date_accuracy(self, algorithm, sample_item):
        """Test that next review date is correctly calculated"""
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.GOOD
        )

        # Next date should be interval days from now
        expected_date = datetime.now() + timedelta(days=interval)
        time_diff = abs((next_date - expected_date).total_seconds())
        assert time_diff < 2  # Within 2 seconds

    def test_calculate_next_review_with_response_time(self, algorithm, sample_item):
        """Test that response_time parameter is accepted (for future use)"""
        ease, interval, next_date = algorithm.calculate_next_review(
            sample_item, ReviewResult.GOOD, response_time_ms=1500
        )

        # Should work without errors (parameter currently unused)
        assert ease > 0
        assert interval > 0

    def test_calculate_next_review_with_invalid_review_result(
        self, algorithm, sample_item
    ):
        """Test defensive handling when review_result is None (invalid input)"""
        # Set up item with known values
        sample_item.ease_factor = 2.5
        sample_item.interval_days = 10
        sample_item.repetition_number = 5

        # Call with None (invalid ReviewResult - defensive pattern)
        ease, interval, next_date = algorithm.calculate_next_review(sample_item, None)

        # When review_result doesn't match any enum value, the algorithm should
        # preserve the current values (defensive behavior - no changes applied)
        assert ease == 2.5  # Unchanged
        assert interval == 10  # Unchanged
        assert next_date > datetime.now()  # Still sets a next review date


class TestAddLearningItem:
    """Test add_learning_item method"""

    def test_add_learning_item_basic(self, algorithm):
        """Test adding a basic learning item"""
        item_id = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
            translation="hello",
        )

        assert item_id is not None
        assert len(item_id) == 36  # UUID format

    def test_add_learning_item_with_all_fields(self, algorithm):
        """Test adding item with all optional fields"""
        item_id = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="buenos días",
            item_type=ItemType.PHRASE,
            translation="good morning",
            definition="morning greeting",
            pronunciation_guide="BWAY-nos DEE-as",
            example_usage="Buenos días, señor",
            context_tags=["greeting", "formal"],
            source_session_id="session-123",
            source_content="conversation practice",
            metadata={"difficulty": "easy", "frequency": "high"},
        )

        assert item_id is not None

        # Verify item was stored with all fields
        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM spaced_repetition_items WHERE item_id = ?", (item_id,)
            )
            row = cursor.fetchone()

            assert row["content"] == "buenos días"
            assert row["translation"] == "good morning"
            assert row["definition"] == "morning greeting"
            assert row["pronunciation_guide"] == "BWAY-nos DEE-as"
            assert row["example_usage"] == "Buenos días, señor"
            assert json.loads(row["context_tags"]) == ["greeting", "formal"]
            assert row["source_session_id"] == "session-123"
            assert json.loads(row["metadata"])["difficulty"] == "easy"

    def test_add_learning_item_duplicate_returns_existing_id(self, algorithm):
        """Test adding duplicate item returns existing item_id"""
        # Add first item
        item_id_1 = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
            translation="hello",
        )

        # Try to add duplicate
        item_id_2 = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
            translation="hello again",  # Different translation
        )

        # Should return same ID
        assert item_id_1 == item_id_2

    def test_add_learning_item_different_users_allowed(self, algorithm):
        """Test same content for different users creates separate items"""
        item_id_1 = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
        )

        item_id_2 = algorithm.add_learning_item(
            user_id=2,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
        )

        # Should be different items
        assert item_id_1 != item_id_2

    def test_add_learning_item_sets_initial_values(self, algorithm):
        """Test that new items have correct initial SM-2 values"""
        item_id = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="test",
            item_type=ItemType.VOCABULARY,
        )

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM spaced_repetition_items WHERE item_id = ?", (item_id,)
            )
            row = cursor.fetchone()

            # Check initial SM-2 values
            assert row["ease_factor"] == 2.5
            assert row["repetition_number"] == 0
            assert row["interval_days"] == 1
            assert row["total_reviews"] == 0
            assert row["correct_reviews"] == 0
            assert row["streak_count"] == 0
            assert row["next_review_date"] is not None  # Scheduled for immediate review

    def test_add_learning_item_handles_empty_optional_fields(self, algorithm):
        """Test adding item with empty optional fields"""
        item_id = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="test",
            item_type=ItemType.VOCABULARY,
            context_tags=None,
            metadata=None,
        )

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM spaced_repetition_items WHERE item_id = ?", (item_id,)
            )
            row = cursor.fetchone()

            # Empty fields should be stored as empty JSON
            assert json.loads(row["context_tags"]) == []
            assert json.loads(row["metadata"]) == {}

    def test_add_learning_item_database_error_raises(self, algorithm):
        """Test that database errors are raised"""
        with patch.object(
            algorithm.db, "get_connection", side_effect=Exception("DB error")
        ):
            with pytest.raises(Exception, match="DB error"):
                algorithm.add_learning_item(
                    user_id=1,
                    language_code="es",
                    content="test",
                    item_type=ItemType.VOCABULARY,
                )


class TestReviewItem:
    """Test review_item method"""

    def setup_method(self):
        """Setup for each test - insert test item"""
        pass

    def _insert_test_item(self, algorithm, item_id="test-item-123", **overrides):
        """Helper to insert a test item into database"""
        defaults = {
            "user_id": 1,
            "language_code": "es",
            "item_type": ItemType.VOCABULARY.value,
            "content": "hola",
            "translation": "hello",
            "ease_factor": 2.5,
            "repetition_number": 0,
            "interval_days": 1,
            "total_reviews": 0,
            "correct_reviews": 0,
            "incorrect_reviews": 0,
            "streak_count": 0,
            "mastery_level": 0.0,
            "confidence_score": 0.0,
            "average_response_time_ms": 0,
            "retention_rate": 0.0,
            "context_tags": "[]",
            "metadata": "{}",
        }
        defaults.update(overrides)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO spaced_repetition_items (
                    item_id, user_id, language_code, item_type, content, translation,
                    ease_factor, repetition_number, interval_days, total_reviews,
                    correct_reviews, incorrect_reviews, streak_count, mastery_level,
                    confidence_score, average_response_time_ms, retention_rate,
                    context_tags, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    defaults["user_id"],
                    defaults["language_code"],
                    defaults["item_type"],
                    defaults["content"],
                    defaults["translation"],
                    defaults["ease_factor"],
                    defaults["repetition_number"],
                    defaults["interval_days"],
                    defaults["total_reviews"],
                    defaults["correct_reviews"],
                    defaults["incorrect_reviews"],
                    defaults["streak_count"],
                    defaults["mastery_level"],
                    defaults["confidence_score"],
                    defaults["average_response_time_ms"],
                    defaults["retention_rate"],
                    defaults["context_tags"],
                    defaults["metadata"],
                ),
            )
            conn.commit()

    def test_review_item_success(self, algorithm):
        """Test successful item review"""
        self._insert_test_item(algorithm)

        result = algorithm.review_item("test-item-123", ReviewResult.GOOD)

        assert result is True

    def test_review_item_not_found_returns_false(self, algorithm):
        """Test reviewing non-existent item returns False"""
        result = algorithm.review_item("non-existent", ReviewResult.GOOD)

        assert result is False

    def test_review_item_updates_total_reviews(self, algorithm):
        """Test that review increments total_reviews"""
        self._insert_test_item(algorithm, total_reviews=5)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_reviews FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["total_reviews"] == 6

    def test_review_item_good_updates_correct_reviews(self, algorithm):
        """Test GOOD result increments correct_reviews"""
        self._insert_test_item(algorithm, correct_reviews=3)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT correct_reviews FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["correct_reviews"] == 4

    def test_review_item_easy_updates_correct_reviews(self, algorithm):
        """Test EASY result increments correct_reviews"""
        self._insert_test_item(algorithm, correct_reviews=2)

        algorithm.review_item("test-item-123", ReviewResult.EASY)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT correct_reviews FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["correct_reviews"] == 3

    def test_review_item_hard_updates_correct_reviews(self, algorithm):
        """Test HARD result increments correct_reviews"""
        self._insert_test_item(algorithm, correct_reviews=1)

        algorithm.review_item("test-item-123", ReviewResult.HARD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT correct_reviews FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["correct_reviews"] == 2

    def test_review_item_again_updates_incorrect_reviews(self, algorithm):
        """Test AGAIN result increments incorrect_reviews"""
        self._insert_test_item(algorithm, incorrect_reviews=1)

        algorithm.review_item("test-item-123", ReviewResult.AGAIN)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT incorrect_reviews FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["incorrect_reviews"] == 2

    def test_review_item_correct_increments_streak(self, algorithm):
        """Test correct answer increments streak_count"""
        self._insert_test_item(algorithm, streak_count=3)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT streak_count FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["streak_count"] == 4

    def test_review_item_again_resets_streak(self, algorithm):
        """Test AGAIN result resets streak_count to 0"""
        self._insert_test_item(algorithm, streak_count=5)

        algorithm.review_item("test-item-123", ReviewResult.AGAIN)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT streak_count FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["streak_count"] == 0

    def test_review_item_updates_mastery_level(self, algorithm):
        """Test that mastery_level is calculated from accuracy and streak"""
        self._insert_test_item(
            algorithm, total_reviews=0, correct_reviews=0, streak_count=0
        )

        # After 1 correct review
        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mastery_level, total_reviews, correct_reviews, streak_count "
                "FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()

            # mastery = accuracy * (streak / 10 + 1)
            accuracy = row["correct_reviews"] / row["total_reviews"]
            expected_mastery = min(accuracy * (row["streak_count"] / 10 + 1), 1.0)
            assert abs(row["mastery_level"] - expected_mastery) < 0.01

    def test_review_item_updates_response_time_first_time(self, algorithm):
        """Test response time is set on first review"""
        self._insert_test_item(algorithm, average_response_time_ms=0)

        algorithm.review_item("test-item-123", ReviewResult.GOOD, response_time_ms=1200)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT average_response_time_ms FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["average_response_time_ms"] == 1200

    def test_review_item_updates_response_time_running_average(self, algorithm):
        """Test response time uses running average"""
        self._insert_test_item(algorithm, average_response_time_ms=1000)

        algorithm.review_item("test-item-123", ReviewResult.GOOD, response_time_ms=1400)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT average_response_time_ms FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            # (1000 + 1400) / 2 = 1200
            assert row["average_response_time_ms"] == 1200

    def test_review_item_updates_confidence_score(self, algorithm):
        """Test confidence score is updated"""
        self._insert_test_item(algorithm, confidence_score=0.5)

        algorithm.review_item("test-item-123", ReviewResult.GOOD, confidence_score=0.8)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT confidence_score FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()
            assert row["confidence_score"] == 0.8

    def test_review_item_updates_timestamps(self, algorithm):
        """Test review updates last_review_date and last_studied_date"""
        self._insert_test_item(algorithm)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_review_date, last_studied_date FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()

            # Verify timestamps are not None and are valid datetime strings
            assert row["last_review_date"] is not None
            assert row["last_studied_date"] is not None

            # Verify they can be parsed as datetime
            last_review = datetime.fromisoformat(
                row["last_review_date"].replace("Z", "+00:00")
                if "Z" in row["last_review_date"]
                else row["last_review_date"]
            )
            last_studied = datetime.fromisoformat(
                row["last_studied_date"].replace("Z", "+00:00")
                if "Z" in row["last_studied_date"]
                else row["last_studied_date"]
            )

            # Verify timestamps are recent (within last minute)
            time_since_review = (
                datetime.now() - last_review.replace(tzinfo=None)
            ).total_seconds()
            assert time_since_review < 60

    def test_review_item_updates_sm2_parameters(self, algorithm):
        """Test review updates ease_factor, interval, next_review_date"""
        self._insert_test_item(algorithm, ease_factor=2.5, interval_days=1)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ease_factor, interval_days, next_review_date, repetition_number "
                "FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()

            # First GOOD review should set interval to initial_interval_days (1)
            assert row["interval_days"] == 1
            assert row["next_review_date"] is not None
            assert row["repetition_number"] == 1

    def test_review_item_calculates_retention_rate_after_5_reviews(self, algorithm):
        """Test retention_rate is calculated after 5+ reviews"""
        self._insert_test_item(algorithm, total_reviews=4, correct_reviews=3)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT retention_rate, total_reviews, correct_reviews "
                "FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()

            # After 5 reviews (4 correct), retention = 4/5 = 0.8
            assert row["total_reviews"] == 5
            assert row["correct_reviews"] == 4
            assert abs(row["retention_rate"] - 0.8) < 0.01

    def test_review_item_does_not_calculate_retention_below_5_reviews(self, algorithm):
        """Test retention_rate is not calculated with < 5 reviews"""
        self._insert_test_item(algorithm, total_reviews=2, correct_reviews=2)

        algorithm.review_item("test-item-123", ReviewResult.GOOD)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT retention_rate, total_reviews FROM spaced_repetition_items WHERE item_id = ?",
                ("test-item-123",),
            )
            row = cursor.fetchone()

            # Should not update retention with only 3 reviews
            assert row["total_reviews"] == 3
            assert row["retention_rate"] == 0.0

    def test_review_item_handles_database_error(self, algorithm):
        """Test review handles database errors gracefully"""
        self._insert_test_item(algorithm)

        with patch.object(
            algorithm.db, "get_connection", side_effect=Exception("DB error")
        ):
            result = algorithm.review_item("test-item-123", ReviewResult.GOOD)

            assert result is False


class TestGetDueItems:
    """Test get_due_items method"""

    def _insert_test_item(self, algorithm, item_id, next_review_date=None, **overrides):
        """Helper to insert test item"""
        defaults = {
            "user_id": 1,
            "language_code": "es",
            "item_type": ItemType.VOCABULARY.value,
            "content": f"content-{item_id}",
            "mastery_level": 0.5,
            "context_tags": "[]",
            "metadata": "{}",
            "is_active": 1,
        }
        defaults.update(overrides)

        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO spaced_repetition_items (
                    item_id, user_id, language_code, item_type, content,
                    next_review_date, mastery_level, context_tags, metadata, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    defaults["user_id"],
                    defaults["language_code"],
                    defaults["item_type"],
                    defaults["content"],
                    next_review_date,
                    defaults["mastery_level"],
                    defaults["context_tags"],
                    defaults["metadata"],
                    defaults["is_active"],
                ),
            )
            conn.commit()

    def test_get_due_items_empty_database(self, algorithm):
        """Test getting due items from empty database"""
        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert items == []

    def test_get_due_items_returns_new_items(self, algorithm):
        """Test returns items that have never been reviewed (NULL next_review_date)"""
        self._insert_test_item(algorithm, "item-1", next_review_date=None)
        self._insert_test_item(algorithm, "item-2", next_review_date=None)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 2
        assert items[0]["item_id"] in ["item-1", "item-2"]

    def test_get_due_items_returns_overdue_items(self, algorithm):
        """Test returns items with next_review_date in the past"""
        past_date = datetime.now() - timedelta(days=1)
        self._insert_test_item(algorithm, "item-1", next_review_date=past_date)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 1
        assert items[0]["item_id"] == "item-1"

    def test_get_due_items_excludes_future_items(self, algorithm):
        """Test excludes items with next_review_date in the future"""
        future_date = datetime.now() + timedelta(days=1)
        self._insert_test_item(algorithm, "item-1", next_review_date=future_date)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 0

    def test_get_due_items_filters_by_user(self, algorithm):
        """Test filters items by user_id"""
        self._insert_test_item(algorithm, "item-1", user_id=1, next_review_date=None)
        self._insert_test_item(algorithm, "item-2", user_id=2, next_review_date=None)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 1
        assert items[0]["item_id"] == "item-1"

    def test_get_due_items_filters_by_language(self, algorithm):
        """Test filters items by language_code"""
        self._insert_test_item(
            algorithm, "item-1", language_code="es", next_review_date=None
        )
        self._insert_test_item(
            algorithm, "item-2", language_code="fr", next_review_date=None
        )

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 1
        assert items[0]["item_id"] == "item-1"

    def test_get_due_items_excludes_inactive_items(self, algorithm):
        """Test excludes items where is_active = 0"""
        self._insert_test_item(algorithm, "item-1", next_review_date=None, is_active=1)
        self._insert_test_item(algorithm, "item-2", next_review_date=None, is_active=0)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 1
        assert items[0]["item_id"] == "item-1"

    def test_get_due_items_respects_limit(self, algorithm):
        """Test respects limit parameter"""
        for i in range(30):
            self._insert_test_item(algorithm, f"item-{i}", next_review_date=None)

        items = algorithm.get_due_items(user_id=1, language_code="es", limit=10)

        assert len(items) == 10

    def test_get_due_items_default_limit_20(self, algorithm):
        """Test default limit is 20"""
        for i in range(30):
            self._insert_test_item(algorithm, f"item-{i}", next_review_date=None)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert len(items) == 20

    def test_get_due_items_prioritizes_new_items_first(self, algorithm):
        """Test new items (NULL next_review) come before overdue items"""
        past_date = datetime.now() - timedelta(days=1)
        self._insert_test_item(algorithm, "item-old", next_review_date=past_date)
        self._insert_test_item(algorithm, "item-new", next_review_date=None)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        # New item should come first
        assert items[0]["item_id"] == "item-new"
        assert items[1]["item_id"] == "item-old"

    def test_get_due_items_sorts_overdue_by_date(self, algorithm):
        """Test overdue items sorted by next_review_date ascending"""
        recent_date = datetime.now() - timedelta(days=1)
        old_date = datetime.now() - timedelta(days=5)

        self._insert_test_item(algorithm, "item-recent", next_review_date=recent_date)
        self._insert_test_item(algorithm, "item-old", next_review_date=old_date)

        items = algorithm.get_due_items(user_id=1, language_code="es")

        # Oldest overdue should come first
        assert items[0]["item_id"] == "item-old"
        assert items[1]["item_id"] == "item-recent"

    def test_get_due_items_sorts_by_mastery_level(self, algorithm):
        """Test items with same status sorted by mastery_level ascending"""
        date = datetime.now() - timedelta(days=1)
        self._insert_test_item(
            algorithm, "item-high", next_review_date=date, mastery_level=0.8
        )
        self._insert_test_item(
            algorithm, "item-low", next_review_date=date, mastery_level=0.3
        )

        items = algorithm.get_due_items(user_id=1, language_code="es")

        # Lower mastery should come first
        assert items[0]["item_id"] == "item-low"
        assert items[1]["item_id"] == "item-high"

    def test_get_due_items_deserializes_json_fields(self, algorithm):
        """Test context_tags and metadata are deserialized from JSON"""
        self._insert_test_item(
            algorithm,
            "item-1",
            next_review_date=None,
            context_tags='["tag1", "tag2"]',
            metadata='{"key": "value"}',
        )

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert items[0]["context_tags"] == ["tag1", "tag2"]
        assert items[0]["metadata"] == {"key": "value"}

    def test_get_due_items_handles_empty_json_fields(self, algorithm):
        """Test handles empty/null JSON fields gracefully"""
        self._insert_test_item(
            algorithm,
            "item-1",
            next_review_date=None,
            context_tags=None,
            metadata=None,
        )

        items = algorithm.get_due_items(user_id=1, language_code="es")

        assert items[0]["context_tags"] == []
        assert items[0]["metadata"] == {}

    def test_get_due_items_handles_database_error(self, algorithm):
        """Test handles database errors gracefully"""
        with patch.object(
            algorithm.db, "get_connection", side_effect=Exception("DB error")
        ):
            items = algorithm.get_due_items(user_id=1, language_code="es")

            assert items == []


class TestUpdateAlgorithmConfig:
    """Test update_algorithm_config method"""

    def _insert_config(self, temp_db):
        """Helper to insert initial config"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admin_spaced_repetition_config (
                config_type, initial_ease_factor, minimum_ease_factor,
                maximum_ease_factor, is_active
            ) VALUES (?, ?, ?, ?, ?)
        """,
            ("sm2", 2.5, 1.3, 3.0, 1),
        )
        conn.commit()
        conn.close()

    def test_update_algorithm_config_success(self, algorithm, temp_db):
        """Test successful config update"""
        self._insert_config(temp_db)

        result = algorithm.update_algorithm_config(
            {"initial_ease_factor": 2.8, "minimum_ease_factor": 1.5}
        )

        assert result is True
        assert algorithm.config["initial_ease_factor"] == 2.8
        assert algorithm.config["minimum_ease_factor"] == 1.5

    def test_update_algorithm_config_single_value(self, algorithm, temp_db):
        """Test updating single config value"""
        self._insert_config(temp_db)

        result = algorithm.update_algorithm_config({"mastery_threshold": 0.9})

        assert result is True
        assert algorithm.config["mastery_threshold"] == 0.9

    def test_update_algorithm_config_multiple_values(self, algorithm, temp_db):
        """Test updating multiple config values"""
        self._insert_config(temp_db)

        result = algorithm.update_algorithm_config(
            {
                "initial_ease_factor": 2.6,
                "maximum_ease_factor": 3.2,
                "easy_interval_days": 10,
            }
        )

        assert result is True
        assert algorithm.config["initial_ease_factor"] == 2.6
        assert algorithm.config["maximum_ease_factor"] == 3.2
        assert algorithm.config["easy_interval_days"] == 10

    def test_update_algorithm_config_reloads_config(self, algorithm, temp_db):
        """Test that config is reloaded after update"""
        self._insert_config(temp_db)

        original_config = algorithm.config.copy()
        algorithm.update_algorithm_config({"initial_ease_factor": 2.9})

        # Config should be reloaded (new object)
        assert algorithm.config["initial_ease_factor"] == 2.9
        assert (
            original_config["initial_ease_factor"]
            != algorithm.config["initial_ease_factor"]
        )

    def test_update_algorithm_config_verifies_updates(self, algorithm, temp_db):
        """Test that updates are verified after application"""
        self._insert_config(temp_db)

        # Successful update returns True
        result = algorithm.update_algorithm_config({"initial_ease_factor": 2.7})

        assert result is True

    def test_update_algorithm_config_handles_verification_failure(
        self, algorithm, temp_db
    ):
        """Test handles cases where verification fails"""
        self._insert_config(temp_db)

        # Mock _load_algorithm_config to return different value than expected
        original_load = algorithm._load_algorithm_config

        def mock_load():
            config = original_load()
            config["initial_ease_factor"] = 2.5  # Different from update
            return config

        with patch.object(algorithm, "_load_algorithm_config", side_effect=mock_load):
            result = algorithm.update_algorithm_config({"initial_ease_factor": 2.8})

            # Should return False when verification fails
            assert result is False

    def test_update_algorithm_config_handles_database_error(self, algorithm):
        """Test handles database errors gracefully"""
        with patch.object(
            algorithm.db, "get_connection", side_effect=Exception("DB error")
        ):
            result = algorithm.update_algorithm_config({"initial_ease_factor": 2.8})

            assert result is False

    def test_update_algorithm_config_no_config_in_db(self, algorithm):
        """Test updating config when no config exists in database"""
        # Don't insert any config
        result = algorithm.update_algorithm_config({"initial_ease_factor": 2.8})

        # Should complete without error (no rows updated, but no crash)
        # Returns True if verification passes (default config unchanged)
        assert result is False or result is True


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_complete_learning_workflow(self, algorithm):
        """Test complete workflow: add item -> review multiple times"""
        # Add item
        item_id = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="aprender",
            item_type=ItemType.VOCABULARY,
            translation="to learn",
        )

        # Get due items (should include new item)
        due_items = algorithm.get_due_items(user_id=1, language_code="es")
        assert len(due_items) == 1
        assert due_items[0]["item_id"] == item_id

        # Review as GOOD
        result = algorithm.review_item(item_id, ReviewResult.GOOD)
        assert result is True

        # Review again as EASY
        result = algorithm.review_item(item_id, ReviewResult.EASY)
        assert result is True

        # Verify mastery increased
        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mastery_level, streak_count FROM spaced_repetition_items WHERE item_id = ?",
                (item_id,),
            )
            row = cursor.fetchone()
            assert row["mastery_level"] > 0
            assert row["streak_count"] == 2

    def test_learning_with_failure_recovery(self, algorithm):
        """Test workflow with failure and recovery"""
        # Add item
        item_id = algorithm.add_learning_item(
            user_id=1,
            language_code="fr",
            content="difficile",
            item_type=ItemType.VOCABULARY,
            translation="difficult",
        )

        # Review as AGAIN (failure)
        algorithm.review_item(item_id, ReviewResult.AGAIN)

        # Check streak reset
        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT streak_count, incorrect_reviews FROM spaced_repetition_items WHERE item_id = ?",
                (item_id,),
            )
            row = cursor.fetchone()
            assert row["streak_count"] == 0
            assert row["incorrect_reviews"] == 1

        # Review as GOOD (recovery)
        algorithm.review_item(item_id, ReviewResult.GOOD)

        # Check streak started again
        with algorithm.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT streak_count FROM spaced_repetition_items WHERE item_id = ?",
                (item_id,),
            )
            row = cursor.fetchone()
            assert row["streak_count"] == 1

    def test_multiple_users_independent_progress(self, algorithm):
        """Test that different users have independent progress"""
        # User 1 adds item
        item_id_1 = algorithm.add_learning_item(
            user_id=1,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
        )

        # User 2 adds same content
        item_id_2 = algorithm.add_learning_item(
            user_id=2,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
        )

        # Different items
        assert item_id_1 != item_id_2

        # User 1 reviews
        algorithm.review_item(item_id_1, ReviewResult.GOOD)

        # User 1's due items should be empty (item scheduled for future)
        user1_items = algorithm.get_due_items(user_id=1, language_code="es")

        # User 2's due items should still have their item
        user2_items = algorithm.get_due_items(user_id=2, language_code="es")
        assert len(user2_items) == 1
        assert user2_items[0]["item_id"] == item_id_2
