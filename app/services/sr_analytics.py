"""
Analytics Engine for Spaced Repetition System
Extracted from spaced_repetition_manager.py

This module provides comprehensive learning analytics for users and system-wide metrics.
Includes personalized learning recommendations based on user progress and behavior.
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Any

from app.services.sr_database import DatabaseManager
from app.services.sr_models import LearningGoal

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Analytics engine for spaced repetition learning system

    Provides:
    - User-specific learning analytics and statistics
    - Personalized learning recommendations
    - System-wide analytics for admin dashboards
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize analytics engine with database manager

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager
        self.mastery_threshold = 0.85  # Default mastery threshold

    def set_mastery_threshold(self, threshold: float):
        """Set the mastery threshold for analytics calculations"""
        self.mastery_threshold = threshold

    def get_user_analytics(
        self, user_id: int, language_code: str, period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get comprehensive learning analytics for a user

        Args:
            user_id: User identifier
            language_code: Language being studied (e.g., 'es', 'fr')
            period: Time period for analytics ('daily', 'weekly', 'monthly')

        Returns:
            Dictionary containing:
            - basic_stats: Session counts, study time, accuracy
            - spaced_repetition: SR item stats and mastery levels
            - streaks: Current streak, longest streak, total active days
            - recent_achievements: Latest 5 achievements earned
            - active_goals: Current active learning goals with progress
            - recommendations: Personalized learning recommendations
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Get basic stats
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_sessions,
                        SUM(duration_minutes) as total_study_time,
                        AVG(accuracy_percentage) as avg_accuracy,
                        SUM(items_studied) as total_items_studied,
                        SUM(new_items_learned) as total_items_learned
                    FROM learning_sessions
                    WHERE user_id = ? AND language_code = ?
                """,
                    (user_id, language_code),
                )

                basic_stats = dict(cursor.fetchone())

                # Get spaced repetition stats
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_items,
                        AVG(mastery_level) as avg_mastery,
                        COUNT(CASE WHEN mastery_level >= ? THEN 1 END) as mastered_items,
                        COUNT(CASE WHEN next_review_date <= datetime('now') THEN 1 END) as due_items
                    FROM spaced_repetition_items
                    WHERE user_id = ? AND language_code = ? AND is_active = 1
                """,
                    (self.mastery_threshold, user_id, language_code),
                )

                sr_stats = dict(cursor.fetchone())

                # Get streak info
                cursor.execute(
                    """
                    SELECT current_streak, longest_streak, total_active_days
                    FROM learning_streaks
                    WHERE user_id = ? AND language_code = ?
                """,
                    (user_id, language_code),
                )

                streak_row = cursor.fetchone()
                streak_stats = (
                    dict(streak_row)
                    if streak_row
                    else {
                        "current_streak": 0,
                        "longest_streak": 0,
                        "total_active_days": 0,
                    }
                )

                # Get recent achievements
                cursor.execute(
                    """
                    SELECT achievement_type, title, description, points_awarded, earned_at
                    FROM gamification_achievements
                    WHERE user_id = ? AND language_code = ?
                    ORDER BY earned_at DESC LIMIT 5
                """,
                    (user_id, language_code),
                )

                recent_achievements = [dict(row) for row in cursor.fetchall()]

                # Get goals progress
                cursor.execute(
                    """
                    SELECT goal_type, title, progress_percentage, status
                    FROM learning_goals
                    WHERE user_id = ? AND language_code = ? AND status = 'active'
                """,
                    (user_id, language_code),
                )

                active_goals = [dict(row) for row in cursor.fetchall()]

                analytics = {
                    "basic_stats": basic_stats,
                    "spaced_repetition": sr_stats,
                    "streaks": streak_stats,
                    "recent_achievements": recent_achievements,
                    "active_goals": active_goals,
                    "recommendations": self._get_learning_recommendations(
                        user_id, language_code
                    ),
                }

                return analytics

        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}

    def _get_learning_recommendations(
        self, user_id: int, language_code: str
    ) -> List[str]:
        """
        Generate personalized learning recommendations

        Analyzes user progress, streaks, and mastery levels to provide
        actionable recommendations for optimal learning.

        Args:
            user_id: User identifier
            language_code: Language being studied

        Returns:
            List of recommendation strings
        """
        recommendations = []

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Check for due items
                cursor.execute(
                    """
                    SELECT COUNT(*) as due_count FROM spaced_repetition_items
                    WHERE user_id = ? AND language_code = ? AND next_review_date <= datetime('now')
                """,
                    (user_id, language_code),
                )

                due_count = cursor.fetchone()["due_count"]
                if due_count > 0:
                    recommendations.append(
                        f"You have {due_count} items ready for review!"
                    )

                # Check streak status
                cursor.execute(
                    """
                    SELECT current_streak, last_activity_date FROM learning_streaks
                    WHERE user_id = ? AND language_code = ?
                """,
                    (user_id, language_code),
                )

                streak_row = cursor.fetchone()
                if streak_row and streak_row["last_activity_date"]:
                    last_activity = date.fromisoformat(streak_row["last_activity_date"])
                    days_since = (date.today() - last_activity).days
                    if days_since == 1:
                        recommendations.append("Study today to maintain your streak!")
                    elif days_since > 1:
                        recommendations.append("Start a new learning streak today!")

                # Check mastery levels
                cursor.execute(
                    """
                    SELECT AVG(mastery_level) as avg_mastery FROM spaced_repetition_items
                    WHERE user_id = ? AND language_code = ?
                """,
                    (user_id, language_code),
                )

                mastery_row = cursor.fetchone()
                if mastery_row and mastery_row["avg_mastery"]:
                    avg_mastery = mastery_row["avg_mastery"]
                    if avg_mastery < 0.5:
                        recommendations.append(
                            "Focus on reviewing previously learned items to improve retention."
                        )
                    elif avg_mastery > 0.8:
                        recommendations.append(
                            "Great progress! Consider learning new vocabulary."
                        )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        return recommendations

    def get_system_analytics(self) -> Dict[str, Any]:
        """
        Get system-wide learning analytics for admin dashboard

        Provides aggregate statistics across all users and languages,
        useful for monitoring platform usage and effectiveness.

        Returns:
            Dictionary containing:
            - system_stats: Total users, sessions, study time, average accuracy
            - item_stats: Total items, average mastery, mastered items count
            - language_distribution: User counts per language
            - generated_at: Timestamp of analytics generation
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Total users and sessions (last 30 days)
                cursor.execute("""
                    SELECT
                        COUNT(DISTINCT user_id) as total_users,
                        COUNT(*) as total_sessions,
                        SUM(duration_minutes) as total_study_time,
                        AVG(accuracy_percentage) as avg_accuracy
                    FROM learning_sessions
                    WHERE started_at >= date('now', '-30 days')
                """)

                system_stats = dict(cursor.fetchone())

                # Items and mastery
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_items,
                        AVG(mastery_level) as avg_mastery,
                        COUNT(CASE WHEN mastery_level >= 0.85 THEN 1 END) as mastered_items
                    FROM spaced_repetition_items WHERE is_active = 1
                """)

                item_stats = dict(cursor.fetchone())

                # Language distribution
                cursor.execute("""
                    SELECT language_code, COUNT(*) as user_count
                    FROM learning_sessions
                    WHERE started_at >= date('now', '-30 days')
                    GROUP BY language_code
                    ORDER BY user_count DESC
                """)

                language_distribution = [dict(row) for row in cursor.fetchall()]

                return {
                    "system_stats": system_stats,
                    "item_stats": item_stats,
                    "language_distribution": language_distribution,
                    "generated_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting system analytics: {e}")
            return {}


# Export the main class
__all__ = ["AnalyticsEngine"]
