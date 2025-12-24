"""
SM-2 Spaced Repetition Algorithm Implementation
Task 4.2.2 - Extracted from SpacedRepetitionManager

This module contains the core SM-2 spaced repetition algorithm logic,
including configuration management, review calculations, and item management.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.services.sr_database import DatabaseManager
from app.services.sr_models import (
    ItemType,
    ReviewResult,
    SpacedRepetitionItem,
)

logger = logging.getLogger(__name__)


class SM2Algorithm:
    """
    SM-2 Spaced Repetition Algorithm implementation

    This class handles the core spaced repetition logic including:
    - Algorithm configuration management
    - Next review calculation using SM-2 algorithm
    - Learning item creation and management
    - Item review processing
    - Due items retrieval

    Uses DatabaseManager for all database operations and SR models for data structures.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize SM-2 Algorithm with database manager

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager
        self.config = self._load_algorithm_config()

    def _load_algorithm_config(self) -> Dict[str, Any]:
        """
        Load spaced repetition algorithm configuration from database

        Retrieves SM-2 algorithm parameters including ease factors, intervals,
        thresholds, and gamification settings. Falls back to sensible defaults
        if no configuration is found.

        Returns:
            Dictionary containing algorithm configuration parameters:
            - initial_ease_factor: Starting ease factor (default: 2.5)
            - minimum_ease_factor: Minimum allowed ease factor (default: 1.3)
            - maximum_ease_factor: Maximum allowed ease factor (default: 3.0)
            - ease_factor_change: Change per review (default: 0.15)
            - initial_interval_days: First interval (default: 1)
            - graduation_interval_days: Second interval (default: 4)
            - easy_interval_days: Easy first interval (default: 7)
            - maximum_interval_days: Maximum interval (default: 365)
            - mastery_threshold: Mastery level threshold (default: 0.85)
            - review_threshold: Review threshold (default: 0.7)
            - difficulty_threshold: Difficulty threshold (default: 0.5)
            - retention_threshold: Retention threshold (default: 0.8)
            - points_per_correct: Points awarded per correct review (default: 10)
            - points_per_streak_day: Points per streak day (default: 5)
            - points_per_goal_achieved: Points per goal (default: 100)
            - daily_goal_default: Default daily goal (default: 30)
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT config_type, initial_ease_factor, minimum_ease_factor,
                           maximum_ease_factor, ease_factor_change, initial_interval_days,
                           graduation_interval_days, easy_interval_days, maximum_interval_days,
                           mastery_threshold, review_threshold, difficulty_threshold,
                           retention_threshold, points_per_correct, points_per_streak_day,
                           points_per_goal_achieved, daily_goal_default
                    FROM admin_spaced_repetition_config
                    WHERE is_active = 1
                """)

                config = {}
                for row in cursor.fetchall():
                    config.update(dict(row))

                # Set defaults if no config found
                if not config:
                    config = {
                        "initial_ease_factor": 2.5,
                        "minimum_ease_factor": 1.3,
                        "maximum_ease_factor": 3.0,
                        "ease_factor_change": 0.15,
                        "initial_interval_days": 1,
                        "graduation_interval_days": 4,
                        "easy_interval_days": 7,
                        "maximum_interval_days": 365,
                        "mastery_threshold": 0.85,
                        "review_threshold": 0.7,
                        "difficulty_threshold": 0.5,
                        "retention_threshold": 0.8,
                        "points_per_correct": 10,
                        "points_per_streak_day": 5,
                        "points_per_goal_achieved": 100,
                        "daily_goal_default": 30,
                    }

                return config

        except Exception as e:
            logger.error(f"Error loading algorithm config: {e}")
            return {
                "initial_ease_factor": 2.5,
                "minimum_ease_factor": 1.3,
                "maximum_ease_factor": 3.0,
                "ease_factor_change": 0.15,
                "initial_interval_days": 1,
                "graduation_interval_days": 4,
                "easy_interval_days": 7,
                "maximum_interval_days": 365,
                "mastery_threshold": 0.85,
                "review_threshold": 0.7,
                "difficulty_threshold": 0.5,
                "retention_threshold": 0.8,
                "points_per_correct": 10,
                "points_per_streak_day": 5,
                "points_per_goal_achieved": 100,
                "daily_goal_default": 30,
            }

    def calculate_next_review(
        self,
        item: SpacedRepetitionItem,
        review_result: ReviewResult,
        response_time_ms: int = 0,
    ) -> Tuple[float, int, datetime]:
        """
        Calculate next review date using enhanced SM-2 algorithm

        This is the core SM-2 algorithm implementation that determines:
        - New ease factor based on review performance
        - Next review interval in days
        - Specific next review date

        The algorithm adjusts based on review result:
        - AGAIN: Reset to initial interval, decrease ease factor
        - HARD: Slight decrease in ease factor, modest interval increase
        - GOOD: Standard SM-2 progression
        - EASY: Increase ease factor, accelerated interval increase

        Args:
            item: SpacedRepetitionItem to calculate next review for
            review_result: ReviewResult indicating performance (AGAIN/HARD/GOOD/EASY)
            response_time_ms: Response time in milliseconds (for future optimizations)

        Returns:
            Tuple containing:
            - new_ease_factor (float): Updated ease factor for item
            - new_interval_days (int): Days until next review
            - next_review_date (datetime): Specific date/time for next review
        """
        ease_factor = item.ease_factor
        interval = item.interval_days
        repetition = item.repetition_number

        # Adjust ease factor based on review result
        if review_result == ReviewResult.AGAIN:
            # Reset interval and decrease ease factor
            ease_factor = max(
                ease_factor - self.config["ease_factor_change"],
                self.config["minimum_ease_factor"],
            )
            interval = self.config["initial_interval_days"]
            repetition = 0
        elif review_result == ReviewResult.HARD:
            # Decrease ease factor slightly
            ease_factor = max(
                ease_factor - self.config["ease_factor_change"] * 0.5,
                self.config["minimum_ease_factor"],
            )
            interval = int(max(interval * 1.2, interval + 1))
            repetition += 1
        elif review_result == ReviewResult.GOOD:
            # Standard progression
            if repetition == 0:
                interval = self.config["initial_interval_days"]
            elif repetition == 1:
                interval = self.config["graduation_interval_days"]
            else:
                interval = int(interval * ease_factor)
            repetition += 1
        elif review_result == ReviewResult.EASY:
            # Increase ease factor and jump ahead
            ease_factor = min(
                ease_factor + self.config["ease_factor_change"],
                self.config["maximum_ease_factor"],
            )
            if repetition == 0:
                interval = self.config["easy_interval_days"]
            else:
                interval = int(interval * ease_factor * 1.3)
            repetition += 1

        # Cap interval at maximum
        interval = min(interval, self.config["maximum_interval_days"])

        # Calculate next review date
        next_review = datetime.now() + timedelta(days=interval)

        return ease_factor, interval, next_review

    def add_learning_item(
        self,
        user_id: int,
        language_code: str,
        content: str,
        item_type: ItemType,
        translation: str = "",
        definition: str = "",
        pronunciation_guide: str = "",
        example_usage: str = "",
        context_tags: Optional[List[str]] = None,
        source_session_id: str = "",
        source_content: str = "",
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Add a new item to spaced repetition system

        Creates a new learning item with initial SM-2 parameters and schedules
        it for immediate review. Checks for duplicates before insertion.

        Args:
            user_id: User ID who owns this item
            language_code: Language code (e.g., 'es', 'fr')
            content: Primary content (word, phrase, etc.)
            item_type: Type of item (VOCABULARY, PHRASE, etc.)
            translation: Translation of the content
            definition: Definition or explanation
            pronunciation_guide: Pronunciation help
            example_usage: Example sentence or usage
            context_tags: List of context tags for categorization
            source_session_id: Session where item was learned
            source_content: Original content source
            metadata: Additional metadata dictionary

        Returns:
            String containing the item_id (UUID) of the created or existing item

        Raises:
            Exception: If database insertion fails
        """
        item_id = str(uuid.uuid4())
        item = SpacedRepetitionItem(
            item_id=item_id,
            user_id=user_id,
            language_code=language_code,
            item_type=item_type.value,
            content=content,
            translation=translation,
            definition=definition,
            pronunciation_guide=pronunciation_guide,
            example_usage=example_usage,
            context_tags=context_tags or [],
            source_session_id=source_session_id,
            source_content=source_content,
            metadata=metadata or {},
        )

        # Set initial review date to now (immediate review)
        item.next_review_date = datetime.now()

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Check if item already exists for this user/language
                cursor.execute(
                    """
                    SELECT item_id FROM spaced_repetition_items
                    WHERE user_id = ? AND language_code = ? AND content = ? AND item_type = ?
                """,
                    (user_id, language_code, content, item_type.value),
                )

                existing = cursor.fetchone()
                if existing:
                    logger.info(f"Item already exists: {content}")
                    return existing["item_id"]

                # Insert new item
                cursor.execute(
                    """
                    INSERT INTO spaced_repetition_items (
                        item_id, user_id, language_code, item_type, content, translation,
                        definition, pronunciation_guide, example_usage, context_tags,
                        difficulty_level, ease_factor, repetition_number, interval_days,
                        next_review_date, source_session_id, source_content, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item.item_id,
                        item.user_id,
                        item.language_code,
                        item.item_type,
                        item.content,
                        item.translation,
                        item.definition,
                        item.pronunciation_guide,
                        item.example_usage,
                        json.dumps(item.context_tags),
                        item.difficulty_level,
                        item.ease_factor,
                        item.repetition_number,
                        item.interval_days,
                        item.next_review_date,
                        item.source_session_id,
                        item.source_content,
                        json.dumps(item.metadata),
                    ),
                )

                conn.commit()
                logger.info(f"Added new learning item: {content}")
                return item_id

        except Exception as e:
            logger.error(f"Error adding learning item: {e}")
            raise

    def review_item(
        self,
        item_id: str,
        review_result: ReviewResult,
        response_time_ms: int = 0,
        confidence_score: float = 0.0,
    ) -> bool:
        """
        Process item review and update spaced repetition data

        This method handles the complete review workflow:
        1. Retrieves current item data
        2. Calculates new SM-2 parameters using calculate_next_review
        3. Updates performance metrics (accuracy, streaks, mastery)
        4. Updates response time running average
        5. Calculates retention rate
        6. Persists all updates to database

        Args:
            item_id: UUID of the item being reviewed
            review_result: Result of the review (AGAIN/HARD/GOOD/EASY)
            response_time_ms: Time taken to respond in milliseconds
            confidence_score: User's confidence score (0.0-1.0)

        Returns:
            Boolean indicating success (True) or failure (False)
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Get current item data
                cursor.execute(
                    """
                    SELECT * FROM spaced_repetition_items WHERE item_id = ?
                """,
                    (item_id,),
                )

                row = cursor.fetchone()
                if not row:
                    logger.error(f"Item not found: {item_id}")
                    return False

                # Convert to dataclass (exclude database fields not in dataclass)
                row_dict = dict(row)
                row_dict.pop("id", None)  # Remove database ID field
                row_dict.pop("created_at", None)  # Remove created_at field
                row_dict.pop("updated_at", None)  # Remove updated_at field

                item = SpacedRepetitionItem(**row_dict)
                item.context_tags = (
                    json.loads(item.context_tags) if item.context_tags else []
                )
                item.metadata = json.loads(item.metadata) if item.metadata else {}

                # Calculate new values using SM-2 algorithm
                new_ease, new_interval, next_review = self.calculate_next_review(
                    item, review_result, response_time_ms
                )

                # Update performance metrics
                item.total_reviews += 1
                if review_result in [
                    ReviewResult.GOOD,
                    ReviewResult.EASY,
                    ReviewResult.HARD,
                ]:
                    item.correct_reviews += 1
                    item.streak_count += 1
                else:
                    item.incorrect_reviews += 1
                    item.streak_count = 0

                # Update mastery level based on performance
                accuracy = (
                    item.correct_reviews / item.total_reviews
                    if item.total_reviews > 0
                    else 0
                )
                item.mastery_level = min(accuracy * (item.streak_count / 10 + 1), 1.0)

                # Update response time (running average)
                if response_time_ms > 0:
                    if item.average_response_time_ms == 0:
                        item.average_response_time_ms = response_time_ms
                    else:
                        item.average_response_time_ms = int(
                            (item.average_response_time_ms + response_time_ms) / 2
                        )

                # Update confidence score
                item.confidence_score = confidence_score

                # Update timestamps
                item.last_review_date = datetime.now()
                item.last_studied_date = datetime.now()
                item.next_review_date = next_review
                item.ease_factor = new_ease
                item.interval_days = new_interval
                item.repetition_number += 1

                # Calculate retention rate
                if item.total_reviews >= 5:  # Need some history for meaningful rate
                    item.retention_rate = item.correct_reviews / item.total_reviews

                # Update in database
                cursor.execute(
                    """
                    UPDATE spaced_repetition_items SET
                        ease_factor = ?, repetition_number = ?, interval_days = ?,
                        last_review_date = ?, next_review_date = ?, total_reviews = ?,
                        correct_reviews = ?, incorrect_reviews = ?, streak_count = ?,
                        mastery_level = ?, confidence_score = ?, last_studied_date = ?,
                        average_response_time_ms = ?, retention_rate = ?, updated_at = ?
                    WHERE item_id = ?
                """,
                    (
                        item.ease_factor,
                        item.repetition_number,
                        item.interval_days,
                        item.last_review_date,
                        item.next_review_date,
                        item.total_reviews,
                        item.correct_reviews,
                        item.incorrect_reviews,
                        item.streak_count,
                        item.mastery_level,
                        item.confidence_score,
                        item.last_studied_date,
                        item.average_response_time_ms,
                        item.retention_rate,
                        datetime.now(),
                        item_id,
                    ),
                )

                conn.commit()

                logger.info(
                    f"Reviewed item {item_id}: {review_result.name}, next review in {new_interval} days"
                )
                return True

        except Exception as e:
            logger.error(f"Error reviewing item: {e}")
            return False

    def get_due_items(
        self, user_id: int, language_code: str, limit: int = 20
    ) -> List[Dict]:
        """
        Get items due for review

        Retrieves learning items that are due for review, prioritizing:
        1. New items (never reviewed)
        2. Overdue items (by review date)
        3. Items with lower mastery level

        Args:
            user_id: User ID to get items for
            language_code: Language code to filter by
            limit: Maximum number of items to return (default: 20)

        Returns:
            List of dictionaries containing item data, with context_tags
            and metadata deserialized from JSON. Sorted by priority.
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM spaced_repetition_items
                    WHERE user_id = ? AND language_code = ? AND is_active = 1
                    AND (next_review_date IS NULL OR next_review_date <= ?)
                    ORDER BY
                        CASE WHEN next_review_date IS NULL THEN 0 ELSE 1 END,
                        next_review_date ASC,
                        mastery_level ASC
                    LIMIT ?
                """,
                    (user_id, language_code, datetime.now(), limit),
                )

                items = []
                for row in cursor.fetchall():
                    item_dict = dict(row)
                    item_dict["context_tags"] = (
                        json.loads(item_dict["context_tags"])
                        if item_dict["context_tags"]
                        else []
                    )
                    item_dict["metadata"] = (
                        json.loads(item_dict["metadata"])
                        if item_dict["metadata"]
                        else {}
                    )
                    items.append(item_dict)

                return items

        except Exception as e:
            logger.error(f"Error getting due items: {e}")
            return []

    def update_algorithm_config(self, config_updates: Dict[str, Any]) -> bool:
        """
        Update spaced repetition algorithm configuration

        Allows runtime modification of SM-2 algorithm parameters. Updates are
        applied to all active configuration records and immediately reloaded.
        Verifies that updates were successfully applied.

        Args:
            config_updates: Dictionary of configuration keys and new values.
                          Keys must match columns in admin_spaced_repetition_config table.
                          Example: {"initial_ease_factor": 2.6, "mastery_threshold": 0.9}

        Returns:
            Boolean indicating whether all updates were successfully applied and verified
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Update existing config values across all config records
                for key, value in config_updates.items():
                    cursor.execute(
                        f"""
                        UPDATE admin_spaced_repetition_config
                        SET {key} = ?, updated_at = ?
                        WHERE {key} IS NOT NULL
                    """,
                        (value, datetime.now()),
                    )

                conn.commit()

                # Reload config to verify changes
                self.config = self._load_algorithm_config()

                # Verify the updates were applied
                all_updated = True
                for key, expected_value in config_updates.items():
                    actual_value = self.config.get(key)
                    if actual_value != expected_value:
                        logger.warning(
                            f"Config update verification failed for {key}: expected {expected_value}, got {actual_value}"
                        )
                        all_updated = False

                if all_updated:
                    logger.info(f"Updated algorithm config: {config_updates}")
                    return True
                else:
                    logger.error("Some config updates were not applied correctly")
                    return False

        except Exception as e:
            logger.error(f"Error updating algorithm config: {e}")
            return False


__all__ = ["SM2Algorithm"]
