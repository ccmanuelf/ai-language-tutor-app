"""
Tests for spaced_repetition_manager.py
Comprehensive test coverage for facade pattern implementation
"""

import sqlite3
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from app.services.spaced_repetition_manager import (
    SpacedRepetitionManager,
    get_spaced_repetition_manager,
)
from app.services.sr_models import (
    AchievementType,
    ItemType,
    ReviewResult,
    SessionType,
    SpacedRepetitionItem,
)

# ============================================================================
# Test Class 1: Initialization
# ============================================================================


class TestSpacedRepetitionManagerInit:
    """Test initialization of SpacedRepetitionManager"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_init_creates_all_submodules(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test that __init__ creates all required sub-modules"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {"test": "config"}
        mock_algorithm_class.return_value = mock_algorithm

        # Act
        manager = SpacedRepetitionManager(db_path="test.db")

        # Assert
        assert manager.db_path == "test.db"
        assert manager.db_manager == mock_db_manager
        mock_get_db_manager.assert_called_once_with("test.db")

        # Verify all sub-modules initialized
        mock_algorithm_class.assert_called_once_with(mock_db_manager)
        mock_session_class.assert_called_once_with(mock_db_manager)
        mock_gamification_class.assert_called_once_with(
            mock_db_manager, mock_algorithm.config
        )
        mock_analytics_class.assert_called_once_with(mock_db_manager)

        # Verify config exposed
        assert manager.config == {"test": "config"}

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_init_with_default_db_path(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test initialization with default database path"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager
        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        # Act
        manager = SpacedRepetitionManager()

        # Assert
        assert manager.db_path == "data/ai_language_tutor.db"
        mock_get_db_manager.assert_called_once_with("data/ai_language_tutor.db")


# ============================================================================
# Test Class 2: SM-2 Algorithm - Calculate Next Review
# ============================================================================


class TestCalculateNextReview:
    """Test calculate_next_review delegation to SM2Algorithm"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_calculate_next_review_delegates_to_algorithm(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test that calculate_next_review delegates to SM2Algorithm"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm.calculate_next_review.return_value = (2.5, 2, 5)
        mock_algorithm_class.return_value = mock_algorithm

        manager = SpacedRepetitionManager()

        # Act
        result = manager.calculate_next_review(
            ease_factor=2.5,
            repetition_number=1,
            interval_days=1,
            review_result=ReviewResult.GOOD,
        )

        # Assert
        assert result == (2.5, 2, 5)
        mock_algorithm.calculate_next_review.assert_called_once_with(
            2.5, 1, 1, ReviewResult.GOOD
        )


# ============================================================================
# Test Class 3: SM-2 Algorithm - Add Learning Item
# ============================================================================


class TestAddLearningItem:
    """Test add_learning_item delegation to SM2Algorithm"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_add_learning_item_delegates_to_algorithm(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test that add_learning_item delegates to SM2Algorithm"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm.add_learning_item.return_value = "test_item_123"
        mock_algorithm_class.return_value = mock_algorithm

        manager = SpacedRepetitionManager()

        # Act
        result = manager.add_learning_item(
            user_id=1,
            language_code="es",
            content="hola",
            item_type=ItemType.VOCABULARY,
            translation="hello",
            extra_field="test",
        )

        # Assert
        assert result == "test_item_123"
        mock_algorithm.add_learning_item.assert_called_once_with(
            1, "es", "hola", ItemType.VOCABULARY, "hello", extra_field="test"
        )


# ============================================================================
# Test Class 4: SM-2 Algorithm - Review Item
# ============================================================================


class TestReviewItem:
    """Test review_item with achievement checks"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_review_item_success_with_achievement_check(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test successful review_item triggers achievement check"""
        # Arrange
        mock_db_manager = MagicMock()
        mock_get_db_manager.return_value = mock_db_manager

        # Mock database connection and query
        mock_conn = MagicMock()
        mock_cursor = Mock()
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock database row
        mock_row = {
            "item_id": "item_123",
            "user_id": 1,
            "language_code": "es",
            "item_type": "vocabulary",
            "content": "hola",
            "translation": "hello",
            "streak_count": 5,
            "mastery_level": 0.8,
            "total_reviews": 10,
        }
        mock_cursor.fetchone.return_value = mock_row

        # Mock algorithm and gamification
        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm.review_item.return_value = True
        mock_algorithm_class.return_value = mock_algorithm

        mock_gamification = Mock()
        mock_gamification_class.return_value = mock_gamification

        manager = SpacedRepetitionManager()

        # Act
        result = manager.review_item(
            item_id="item_123",
            review_result=ReviewResult.GOOD,
            response_time_ms=1500,
            session_id="session_456",
        )

        # Assert
        assert result is True

        # Verify database query
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM spaced_repetition_items WHERE item_id = ?", ("item_123",)
        )

        # Verify algorithm review called
        mock_algorithm.review_item.assert_called_once_with(
            "item_123", ReviewResult.GOOD, 1500, "session_456"
        )

        # Verify gamification achievement check called
        mock_gamification.check_item_achievements.assert_called_once()
        call_args = mock_gamification.check_item_achievements.call_args
        item_arg = call_args[0][0]
        result_arg = call_args[0][1]

        assert isinstance(item_arg, SpacedRepetitionItem)
        assert item_arg.item_id == "item_123"
        assert item_arg.user_id == 1
        assert item_arg.streak_count == 5
        assert result_arg == ReviewResult.GOOD

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    @patch("app.services.spaced_repetition_manager.logger")
    def test_review_item_not_found_returns_false(
        self,
        mock_logger,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test review_item returns False when item not found"""
        # Arrange
        mock_db_manager = MagicMock()
        mock_get_db_manager.return_value = mock_db_manager

        # Mock database connection - item not found
        mock_conn = MagicMock()
        mock_cursor = Mock()
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        mock_gamification = Mock()
        mock_gamification_class.return_value = mock_gamification

        manager = SpacedRepetitionManager()

        # Act
        result = manager.review_item(
            item_id="nonexistent",
            review_result=ReviewResult.GOOD,
        )

        # Assert
        assert result is False
        mock_logger.error.assert_called_once_with("Item not found: nonexistent")
        mock_algorithm.review_item.assert_not_called()
        mock_gamification.check_item_achievements.assert_not_called()

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_review_item_algorithm_failure_skips_achievement_check(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test review_item skips achievement check when algorithm fails"""
        # Arrange
        mock_db_manager = MagicMock()
        mock_get_db_manager.return_value = mock_db_manager

        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = Mock()
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_row = {
            "item_id": "item_123",
            "user_id": 1,
            "language_code": "es",
            "item_type": "vocabulary",
            "content": "hola",
            "translation": "hello",
            "streak_count": 0,
            "mastery_level": 0.0,
            "total_reviews": 0,
        }
        mock_cursor.fetchone.return_value = mock_row

        # Mock algorithm to return False (failure)
        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm.review_item.return_value = False
        mock_algorithm_class.return_value = mock_algorithm

        mock_gamification = Mock()
        mock_gamification_class.return_value = mock_gamification

        manager = SpacedRepetitionManager()

        # Act
        result = manager.review_item(
            item_id="item_123",
            review_result=ReviewResult.AGAIN,
        )

        # Assert
        assert result is False
        mock_algorithm.review_item.assert_called_once()
        mock_gamification.check_item_achievements.assert_not_called()


# ============================================================================
# Test Class 5: SM-2 Algorithm - Get Due Items
# ============================================================================


class TestGetDueItems:
    """Test get_due_items delegation to SM2Algorithm"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_get_due_items_delegates_to_algorithm(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test that get_due_items delegates to SM2Algorithm"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm.get_due_items.return_value = [
            {"item_id": "1", "content": "hola"},
            {"item_id": "2", "content": "adiós"},
        ]
        mock_algorithm_class.return_value = mock_algorithm

        manager = SpacedRepetitionManager()

        # Act
        result = manager.get_due_items(
            user_id=1, language_code="es", limit=10, item_type="vocabulary"
        )

        # Assert
        assert len(result) == 2
        assert result[0]["item_id"] == "1"
        mock_algorithm.get_due_items.assert_called_once_with(1, "es", 10)


# ============================================================================
# Test Class 6: SM-2 Algorithm - Update Config
# ============================================================================


class TestUpdateAlgorithmConfig:
    """Test update_algorithm_config delegation"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_update_algorithm_config_success_updates_facade_config(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test successful config update updates facade config"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {"old": "config"}
        mock_algorithm.update_algorithm_config.return_value = True
        mock_algorithm_class.return_value = mock_algorithm

        manager = SpacedRepetitionManager()
        assert manager.config == {"old": "config"}

        # Update algorithm config after update
        mock_algorithm.config = {"new": "config"}

        # Act
        result = manager.update_algorithm_config({"new": "config"})

        # Assert
        assert result is True
        assert manager.config == {"new": "config"}
        mock_algorithm.update_algorithm_config.assert_called_once_with(
            {"new": "config"}
        )

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_update_algorithm_config_failure_keeps_old_config(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test failed config update keeps old config"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {"old": "config"}
        mock_algorithm.update_algorithm_config.return_value = False
        mock_algorithm_class.return_value = mock_algorithm

        manager = SpacedRepetitionManager()

        # Act
        result = manager.update_algorithm_config({"new": "config"})

        # Assert
        assert result is False
        assert manager.config == {"old": "config"}


# ============================================================================
# Test Class 7: Session Management Methods
# ============================================================================


class TestSessionMethods:
    """Test session management delegation to SessionManager"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_start_learning_session_delegates_to_session_manager(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test start_learning_session delegates to SessionManager"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        mock_sessions = Mock()
        mock_sessions.start_learning_session.return_value = "session_abc123"
        mock_session_class.return_value = mock_sessions

        manager = SpacedRepetitionManager()

        # Act
        result = manager.start_learning_session(
            user_id=1,
            language_code="fr",
            session_type="vocabulary",
            goal_items=20,
        )

        # Assert
        assert result == "session_abc123"
        mock_sessions.start_learning_session.assert_called_once_with(
            1, "fr", "vocabulary", goal_items=20
        )

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_end_learning_session_delegates_to_session_manager(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test end_learning_session delegates to SessionManager"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        mock_sessions = Mock()
        mock_sessions.end_learning_session.return_value = True
        mock_session_class.return_value = mock_sessions

        manager = SpacedRepetitionManager()

        # Act
        result = manager.end_learning_session(
            session_id="session_123",
            items_studied=15,
            items_correct=12,
            items_incorrect=3,
            avg_response_time=2500,
        )

        # Assert
        assert result is True
        mock_sessions.end_learning_session.assert_called_once_with(
            "session_123", 15, 12, 3, avg_response_time=2500
        )


# ============================================================================
# Test Class 8: Analytics Methods
# ============================================================================


class TestAnalyticsMethods:
    """Test analytics delegation to AnalyticsEngine"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_get_user_analytics_delegates_to_analytics_engine(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test get_user_analytics delegates to AnalyticsEngine"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        mock_analytics = Mock()
        mock_analytics.get_user_analytics.return_value = {
            "total_items": 100,
            "mastery_rate": 0.75,
        }
        mock_analytics_class.return_value = mock_analytics

        manager = SpacedRepetitionManager()

        # Act
        result = manager.get_user_analytics(
            user_id=1, language_code="de", period="week"
        )

        # Assert
        assert result["total_items"] == 100
        assert result["mastery_rate"] == 0.75
        mock_analytics.get_user_analytics.assert_called_once_with(1, "de", "week")

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_get_system_analytics_delegates_to_analytics_engine(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test get_system_analytics delegates to AnalyticsEngine"""
        # Arrange
        mock_db_manager = Mock()
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        mock_analytics = Mock()
        mock_analytics.get_system_analytics.return_value = {
            "total_users": 500,
            "total_items": 10000,
        }
        mock_analytics_class.return_value = mock_analytics

        manager = SpacedRepetitionManager()

        # Act
        result = manager.get_system_analytics()

        # Assert
        assert result["total_users"] == 500
        assert result["total_items"] == 10000
        mock_analytics.get_system_analytics.assert_called_once_with()


# ============================================================================
# Test Class 9: Database Connection
# ============================================================================


class TestDatabaseConnection:
    """Test direct database connection access"""

    @patch("app.services.spaced_repetition_manager.get_db_manager")
    @patch("app.services.spaced_repetition_manager.SM2Algorithm")
    @patch("app.services.spaced_repetition_manager.SessionManager")
    @patch("app.services.spaced_repetition_manager.GamificationEngine")
    @patch("app.services.spaced_repetition_manager.AnalyticsEngine")
    def test_get_connection_returns_db_manager_connection(
        self,
        mock_analytics_class,
        mock_gamification_class,
        mock_session_class,
        mock_algorithm_class,
        mock_get_db_manager,
    ):
        """Test _get_connection returns database manager connection"""
        # Arrange
        mock_db_manager = Mock()
        mock_connection = Mock(spec=sqlite3.Connection)
        mock_db_manager.get_connection.return_value = mock_connection
        mock_get_db_manager.return_value = mock_db_manager

        mock_algorithm = Mock()
        mock_algorithm.config = {}
        mock_algorithm_class.return_value = mock_algorithm

        manager = SpacedRepetitionManager()

        # Act
        result = manager._get_connection()

        # Assert
        assert result == mock_connection
        mock_db_manager.get_connection.assert_called_once_with()


# ============================================================================
# Test Class 10: Singleton Pattern
# ============================================================================


class TestSingletonPattern:
    """Test module-level singleton pattern"""

    def test_get_spaced_repetition_manager_returns_singleton(self):
        """Test that get_spaced_repetition_manager returns same instance"""
        with patch("app.services.spaced_repetition_manager.get_db_manager"):
            with patch("app.services.spaced_repetition_manager.SM2Algorithm"):
                with patch("app.services.spaced_repetition_manager.SessionManager"):
                    with patch(
                        "app.services.spaced_repetition_manager.GamificationEngine"
                    ):
                        with patch(
                            "app.services.spaced_repetition_manager.AnalyticsEngine"
                        ):
                            # Act
                            manager1 = get_spaced_repetition_manager("test1.db")
                            manager2 = get_spaced_repetition_manager("test1.db")

                            # Assert
                            assert manager1 is manager2

    def test_get_spaced_repetition_manager_new_instance_for_different_db(self):
        """Test that different db_path creates new instance"""
        with patch("app.services.spaced_repetition_manager.get_db_manager"):
            with patch("app.services.spaced_repetition_manager.SM2Algorithm"):
                with patch("app.services.spaced_repetition_manager.SessionManager"):
                    with patch(
                        "app.services.spaced_repetition_manager.GamificationEngine"
                    ):
                        with patch(
                            "app.services.spaced_repetition_manager.AnalyticsEngine"
                        ):
                            # Act
                            manager1 = get_spaced_repetition_manager("test1.db")
                            manager2 = get_spaced_repetition_manager("test2.db")

                            # Assert
                            assert manager1 is not manager2
                            assert manager1.db_path == "test1.db"
                            assert manager2.db_path == "test2.db"

    def test_get_spaced_repetition_manager_uses_default_path(self):
        """Test that get_spaced_repetition_manager uses default path"""
        with patch("app.services.spaced_repetition_manager.get_db_manager"):
            with patch("app.services.spaced_repetition_manager.SM2Algorithm"):
                with patch("app.services.spaced_repetition_manager.SessionManager"):
                    with patch(
                        "app.services.spaced_repetition_manager.GamificationEngine"
                    ):
                        with patch(
                            "app.services.spaced_repetition_manager.AnalyticsEngine"
                        ):
                            # Act
                            manager = get_spaced_repetition_manager()

                            # Assert
                            assert manager.db_path == "data/ai_language_tutor.db"
