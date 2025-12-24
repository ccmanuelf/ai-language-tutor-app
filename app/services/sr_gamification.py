"""
Gamification Engine for Spaced Repetition System
Task 4.2.2 - Modularization: Extract Gamification/Achievement Methods

This module handles achievement detection, milestone tracking, and awards
for the spaced repetition system.
"""

import json
import logging
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Optional

from app.services.sr_database import DatabaseManager
from app.services.sr_models import AchievementType, ReviewResult, SpacedRepetitionItem

# Configure logging
logger = logging.getLogger(__name__)


class GamificationEngine:
    """
    Handles gamification features including achievements and milestones
    for the spaced repetition system.
    """

    def __init__(
        self, db_manager: DatabaseManager, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the GamificationEngine.

        Args:
            db_manager: Database manager instance for DB operations
            config: Configuration dictionary containing thresholds and settings
        """
        self.db_manager = db_manager
        self.config = config or self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "mastery_threshold": 0.85,
            "points_per_correct": 10,
            "points_per_streak": 5,
        }

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = self.db_manager.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def check_item_achievements(
        self, item: SpacedRepetitionItem, review_result: ReviewResult
    ):
        """
        Check and award achievements based on item review.

        This method detects milestone achievements for:
        - Vocabulary streaks (5 and 10 correct reviews)
        - Content mastery (reaching mastery threshold)

        Args:
            item: The spaced repetition item being reviewed
            review_result: The result of the review (AGAIN, HARD, GOOD, EASY)
        """
        achievements = []

        # Vocabulary milestone achievements
        if item.item_type == "vocabulary":
            if item.streak_count == 5:
                achievements.append(
                    {
                        "type": AchievementType.VOCABULARY,
                        "title": "Vocabulary Streak",
                        "description": f"Correctly reviewed '{item.content}' 5 times in a row",
                        "points": 25,
                    }
                )
            elif item.streak_count == 10:
                achievements.append(
                    {
                        "type": AchievementType.VOCABULARY,
                        "title": "Word Master",
                        "description": f"Achieved 10-review streak with '{item.content}'",
                        "points": 50,
                    }
                )

        # Mastery achievements
        if item.mastery_level >= self.config["mastery_threshold"]:
            achievements.append(
                {
                    "type": AchievementType.MASTERY,
                    "title": "Content Mastery",
                    "description": f"Mastered '{item.content}' with {item.mastery_level:.1%} proficiency",
                    "points": 30,
                }
            )

        # Award achievements
        for achievement in achievements:
            self.award_achievement(
                item.user_id,
                item.language_code,
                achievement["type"],
                achievement["title"],
                achievement["description"],
                points_awarded=achievement["points"],
            )

    def award_achievement(
        self,
        user_id: int,
        language_code: str,
        achievement_type: AchievementType,
        title: str,
        description: str,
        points_awarded: int = 10,
        badge_icon: str = "🏆",
        badge_color: str = "#FFD700",
        rarity: str = "common",
        earned_in_session: str = "",
        earned_activity: str = "",
        milestone_level: int = 1,
    ):
        """
        Award an achievement to a user.

        This method creates a new achievement record in the database with
        duplicate prevention (same achievement cannot be awarded twice within 24 hours).

        Args:
            user_id: The ID of the user receiving the achievement
            language_code: The language code (e.g., 'es', 'fr', 'de')
            achievement_type: Type of achievement (from AchievementType enum)
            title: Display title of the achievement
            description: Detailed description of what was achieved
            points_awarded: Points awarded for this achievement (default: 10)
            badge_icon: Icon/emoji for the achievement (default: 🏆)
            badge_color: Color code for the badge (default: #FFD700 gold)
            rarity: Rarity level (common, rare, epic, legendary)
            earned_in_session: Session ID where achievement was earned
            earned_activity: Activity type that triggered the achievement
            milestone_level: Numeric milestone level (1-N)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                achievement_id = str(uuid.uuid4())

                # Check if similar achievement already exists (prevent duplicates)
                cursor.execute(
                    """
                    SELECT achievement_id FROM gamification_achievements
                    WHERE user_id = ? AND achievement_type = ? AND title = ?
                    AND earned_at > datetime('now', '-1 day')
                """,
                    (user_id, achievement_type.value, title),
                )

                if cursor.fetchone():
                    logger.info(f"Achievement already awarded recently: {title}")
                    return

                cursor.execute(
                    """
                    INSERT INTO gamification_achievements (
                        achievement_id, user_id, language_code, achievement_type, title,
                        description, badge_icon, badge_color, points_awarded,
                        criteria_met, required_criteria, rarity, earned_in_session,
                        earned_activity, milestone_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        achievement_id,
                        user_id,
                        language_code,
                        achievement_type.value,
                        title,
                        description,
                        badge_icon,
                        badge_color,
                        points_awarded,
                        json.dumps({"earned": True}),
                        json.dumps({"criteria": "met"}),
                        rarity,
                        earned_in_session,
                        earned_activity,
                        milestone_level,
                    ),
                )

                conn.commit()
                logger.info(f"Awarded achievement: {title} to user {user_id}")

        except Exception as e:
            logger.error(f"Error awarding achievement: {e}")
