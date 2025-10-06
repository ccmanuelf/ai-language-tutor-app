"""
Spaced Repetition Manager - Facade Pattern
Unified API for spaced repetition system (refactored architecture)

This manager coordinates between specialized modules:
- sr_database: Database connection management
- sr_models: Data structures and enums
- sr_algorithm: SM-2 spaced repetition algorithm
- sr_sessions: Learning session management
- sr_gamification: Achievement and streak system
- sr_analytics: Progress analytics and recommendations
"""

import logging
from typing import Dict, List, Optional, Any

from .sr_database import get_db_manager
from .sr_models import (
    SpacedRepetitionItem,
    ReviewResult,
)
from .sr_algorithm import SM2Algorithm
from .sr_sessions import SessionManager
from .sr_gamification import GamificationEngine
from .sr_analytics import AnalyticsEngine

logger = logging.getLogger(__name__)


class SpacedRepetitionManager:
    """
    Unified facade for spaced repetition system
    Delegates to specialized modules while maintaining backward compatibility
    """

    def __init__(self, db_path: str = "data/ai_language_tutor.db"):
        """
        Initialize spaced repetition manager with all sub-modules

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.db_manager = get_db_manager(db_path)

        # Initialize specialized modules
        self.algorithm = SM2Algorithm(self.db_manager)
        self.sessions = SessionManager(self.db_manager)
        self.gamification = GamificationEngine(self.db_manager, self.algorithm.config)
        self.analytics = AnalyticsEngine(self.db_manager)

        # Expose config for backward compatibility
        self.config = self.algorithm.config

    # ========================================================================
    # SM-2 Algorithm Methods (delegate to sr_algorithm.SM2Algorithm)
    # ========================================================================

    def calculate_next_review(
        self,
        ease_factor: float,
        repetition_number: int,
        interval_days: int,
        review_result: ReviewResult,
    ) -> tuple:
        """Calculate next review parameters using SM-2 algorithm"""
        return self.algorithm.calculate_next_review(
            ease_factor, repetition_number, interval_days, review_result
        )

    def add_learning_item(
        self,
        user_id: int,
        language_code: str,
        item_type: str,
        content: str,
        translation: str = "",
        **kwargs,
    ) -> str:
        """Add new learning item to spaced repetition system"""
        return self.algorithm.add_learning_item(
            user_id, language_code, item_type, content, translation, **kwargs
        )

    def review_item(
        self,
        item_id: str,
        review_result: ReviewResult,
        response_time_ms: int = 0,
        session_id: str = "",
    ) -> bool:
        """
        Process item review and update all metrics
        Includes achievement check via gamification engine
        """
        # Get item before review for achievement checks
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM spaced_repetition_items WHERE item_id = ?", (item_id,)
            )
            row = cursor.fetchone()
            if not row:
                logger.error(f"Item not found: {item_id}")
                return False

            item_dict = dict(row)

        # Perform review (updates database)
        success = self.algorithm.review_item(
            item_id, review_result, response_time_ms, session_id
        )

        if success:
            # Convert row to SpacedRepetitionItem for achievement check
            item = SpacedRepetitionItem(
                item_id=item_dict["item_id"],
                user_id=item_dict["user_id"],
                language_code=item_dict["language_code"],
                item_type=item_dict["item_type"],
                content=item_dict["content"],
                translation=item_dict.get("translation", ""),
                streak_count=item_dict.get("streak_count", 0),
                mastery_level=item_dict.get("mastery_level", 0.0),
                total_reviews=item_dict.get("total_reviews", 0),
            )

            # Check for achievements
            self.gamification.check_item_achievements(item, review_result)

        return success

    def get_due_items(
        self,
        user_id: int,
        language_code: str,
        limit: int = 20,
        item_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get items due for review"""
        return self.algorithm.get_due_items(user_id, language_code, limit, item_type)

    def update_algorithm_config(self, config_updates: Dict[str, Any]) -> bool:
        """Update algorithm configuration"""
        success = self.algorithm.update_algorithm_config(config_updates)
        if success:
            self.config = self.algorithm.config  # Update facade config
        return success

    # ========================================================================
    # Session Management Methods (delegate to sr_sessions.SessionManager)
    # ========================================================================

    def start_learning_session(
        self,
        user_id: int,
        language_code: str,
        session_type: str,
        **kwargs,
    ) -> str:
        """Start new learning session"""
        return self.sessions.start_learning_session(
            user_id, language_code, session_type, **kwargs
        )

    def end_learning_session(
        self,
        session_id: str,
        items_studied: int = 0,
        items_correct: int = 0,
        items_incorrect: int = 0,
        **kwargs,
    ) -> bool:
        """End learning session with metrics"""
        return self.sessions.end_learning_session(
            session_id, items_studied, items_correct, items_incorrect, **kwargs
        )

    # ========================================================================
    # Analytics Methods (delegate to sr_analytics.AnalyticsEngine)
    # ========================================================================

    def get_user_analytics(
        self,
        user_id: int,
        language_code: str,
        period: str = "all",
    ) -> Dict[str, Any]:
        """Get comprehensive user learning analytics"""
        return self.analytics.get_user_analytics(user_id, language_code, period)

    def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics (admin view)"""
        return self.analytics.get_system_analytics()

    # ========================================================================
    # Direct Database Connection (for advanced use cases)
    # ========================================================================

    def _get_connection(self):
        """Get database connection (backward compatibility)"""
        return self.db_manager.get_connection()


# ============================================================================
# Module-level Functions (Backward Compatibility)
# ============================================================================

_manager_instance = None


def get_spaced_repetition_manager(
    db_path: str = "data/ai_language_tutor.db",
) -> SpacedRepetitionManager:
    """Get singleton spaced repetition manager instance"""
    global _manager_instance
    if _manager_instance is None or _manager_instance.db_path != db_path:
        _manager_instance = SpacedRepetitionManager(db_path)
    return _manager_instance
