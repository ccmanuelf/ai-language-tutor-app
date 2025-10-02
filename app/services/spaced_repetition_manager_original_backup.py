"""
Spaced Repetition & Progress Analytics Manager
Task 3.1.4 - Comprehensive Learning Analytics System

This service implements SM-2 spaced repetition algorithm, learning analytics,
gamification, and progress tracking for the AI Language Tutor App.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import math
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ItemType(Enum):
    """Types of learning items for spaced repetition"""

    VOCABULARY = "vocabulary"
    PHRASE = "phrase"
    GRAMMAR = "grammar"
    PRONUNCIATION = "pronunciation"


class SessionType(Enum):
    """Types of learning sessions"""

    VOCABULARY = "vocabulary"
    CONVERSATION = "conversation"
    TUTOR_MODE = "tutor_mode"
    SCENARIO = "scenario"
    CONTENT_REVIEW = "content_review"


class ReviewResult(Enum):
    """Results of item review"""

    AGAIN = 0  # Incorrect, review again soon
    HARD = 1  # Correct but difficult
    GOOD = 2  # Correct with normal effort
    EASY = 3  # Correct and easy


class AchievementType(Enum):
    """Types of achievements"""

    STREAK = "streak"
    VOCABULARY = "vocabulary"
    CONVERSATION = "conversation"
    GOAL = "goal"
    MASTERY = "mastery"
    DEDICATION = "dedication"


@dataclass
class SpacedRepetitionItem:
    """Data class for spaced repetition items"""

    item_id: str
    user_id: int
    language_code: str
    item_type: str
    content: str
    translation: str = ""
    definition: str = ""
    pronunciation_guide: str = ""
    example_usage: str = ""
    context_tags: List[str] = None
    difficulty_level: int = 1
    ease_factor: float = 2.5
    repetition_number: int = 0
    interval_days: int = 1
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    total_reviews: int = 0
    correct_reviews: int = 0
    incorrect_reviews: int = 0
    streak_count: int = 0
    mastery_level: float = 0.0
    confidence_score: float = 0.0
    first_seen_date: datetime = None
    last_studied_date: Optional[datetime] = None
    average_response_time_ms: int = 0
    learning_speed_factor: float = 1.0
    retention_rate: float = 0.0
    source_session_id: str = ""
    source_content: str = ""
    metadata: Dict = None
    is_active: bool = True

    def __post_init__(self):
        if self.context_tags is None:
            self.context_tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.first_seen_date is None:
            self.first_seen_date = datetime.now()


@dataclass
class LearningSession:
    """Data class for learning sessions"""

    session_id: str
    user_id: int
    language_code: str
    session_type: str
    mode_specific_data: Dict = None
    duration_minutes: int = 0
    items_studied: int = 0
    items_correct: int = 0
    items_incorrect: int = 0
    accuracy_percentage: float = 0.0
    average_response_time_ms: int = 0
    confidence_score: float = 0.0
    engagement_score: float = 0.0
    difficulty_level: int = 1
    new_items_learned: int = 0
    items_reviewed: int = 0
    streak_contributions: int = 0
    goal_progress: float = 0.0
    content_source: str = ""
    ai_model_used: str = ""
    tutor_mode: str = ""
    scenario_id: str = ""
    started_at: datetime = None
    ended_at: Optional[datetime] = None

    def __post_init__(self):
        if self.mode_specific_data is None:
            self.mode_specific_data = {}
        if self.started_at is None:
            self.started_at = datetime.now()


@dataclass
class LearningGoal:
    """Data class for learning goals"""

    goal_id: str
    user_id: int
    language_code: str
    goal_type: str
    title: str
    description: str
    target_value: float
    current_value: float = 0.0
    unit: str = "items"
    difficulty_level: int = 2
    priority: int = 2
    is_daily: bool = False
    is_weekly: bool = False
    is_monthly: bool = False
    is_custom: bool = True
    progress_percentage: float = 0.0
    milestones_reached: int = 0
    total_milestones: int = 5
    last_progress_update: Optional[datetime] = None
    start_date: datetime = None
    target_date: datetime = None
    completed_date: Optional[datetime] = None
    status: str = "active"

    def __post_init__(self):
        if self.start_date is None:
            self.start_date = datetime.now()
        if self.target_date is None:
            self.target_date = datetime.now() + timedelta(days=30)


class SpacedRepetitionManager:
    """Comprehensive manager for spaced repetition and learning analytics"""

    def __init__(self, db_path: str = "data/ai_language_tutor.db"):
        self.db_path = db_path
        self.config = self._load_algorithm_config()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_algorithm_config(self) -> Dict[str, Any]:
        """Load spaced repetition algorithm configuration"""
        try:
            with self._get_connection() as conn:
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

    # ============= SPACED REPETITION CORE ALGORITHM =============

    def calculate_next_review(
        self,
        item: SpacedRepetitionItem,
        review_result: ReviewResult,
        response_time_ms: int = 0,
    ) -> Tuple[float, int, datetime]:
        """
        Calculate next review date using enhanced SM-2 algorithm

        Returns:
            Tuple of (new_ease_factor, new_interval_days, next_review_date)
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
            interval = max(interval * 1.2, interval + 1)
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
        context_tags: List[str] = None,
        source_session_id: str = "",
        source_content: str = "",
        metadata: Dict = None,
    ) -> str:
        """Add a new item to spaced repetition system"""

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
            with self._get_connection() as conn:
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
        """Process item review and update spaced repetition data"""

        try:
            with self._get_connection() as conn:
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

                # Check for achievements
                self._check_item_achievements(item, review_result)

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
        """Get items due for review"""

        try:
            with self._get_connection() as conn:
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

    # ============= LEARNING SESSIONS MANAGEMENT =============

    def start_learning_session(
        self,
        user_id: int,
        language_code: str,
        session_type: SessionType,
        mode_specific_data: Dict = None,
        content_source: str = "",
        ai_model_used: str = "",
        tutor_mode: str = "",
        scenario_id: str = "",
    ) -> str:
        """Start a new learning session"""

        session_id = str(uuid.uuid4())
        session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            language_code=language_code,
            session_type=session_type.value,
            mode_specific_data=mode_specific_data or {},
            content_source=content_source,
            ai_model_used=ai_model_used,
            tutor_mode=tutor_mode,
            scenario_id=scenario_id,
        )

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO learning_sessions (
                        session_id, user_id, language_code, session_type, mode_specific_data,
                        content_source, ai_model_used, tutor_mode, scenario_id, started_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.session_id,
                        session.user_id,
                        session.language_code,
                        session.session_type,
                        json.dumps(session.mode_specific_data),
                        session.content_source,
                        session.ai_model_used,
                        session.tutor_mode,
                        session.scenario_id,
                        session.started_at,
                    ),
                )

                conn.commit()
                logger.info(f"Started learning session: {session_id}")
                return session_id

        except Exception as e:
            logger.error(f"Error starting learning session: {e}")
            raise

    def end_learning_session(
        self,
        session_id: str,
        items_studied: int = 0,
        items_correct: int = 0,
        items_incorrect: int = 0,
        average_response_time_ms: int = 0,
        confidence_score: float = 0.0,
        engagement_score: float = 0.0,
        new_items_learned: int = 0,
    ) -> bool:
        """End a learning session and calculate metrics"""

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get session start time
                cursor.execute(
                    """
                    SELECT started_at FROM learning_sessions WHERE session_id = ?
                """,
                    (session_id,),
                )

                row = cursor.fetchone()
                if not row:
                    logger.error(f"Session not found: {session_id}")
                    return False

                started_at = datetime.fromisoformat(row["started_at"])
                ended_at = datetime.now()
                duration_minutes = int((ended_at - started_at).total_seconds() / 60)

                # Calculate accuracy
                total_items = items_correct + items_incorrect
                accuracy_percentage = (
                    (items_correct / total_items * 100) if total_items > 0 else 0
                )

                # Update session
                cursor.execute(
                    """
                    UPDATE learning_sessions SET
                        duration_minutes = ?, items_studied = ?, items_correct = ?,
                        items_incorrect = ?, accuracy_percentage = ?, average_response_time_ms = ?,
                        confidence_score = ?, engagement_score = ?, new_items_learned = ?,
                        items_reviewed = ?, ended_at = ?
                    WHERE session_id = ?
                """,
                    (
                        duration_minutes,
                        items_studied,
                        items_correct,
                        items_incorrect,
                        accuracy_percentage,
                        average_response_time_ms,
                        confidence_score,
                        engagement_score,
                        new_items_learned,
                        items_studied - new_items_learned,
                        ended_at,
                        session_id,
                    ),
                )

                conn.commit()

                # Update streaks and check achievements
                self._update_learning_streaks(
                    cursor.execute(
                        "SELECT user_id, language_code FROM learning_sessions WHERE session_id = ?",
                        (session_id,),
                    ).fetchone()
                )

                logger.info(
                    f"Ended learning session: {session_id} ({duration_minutes} minutes)"
                )
                return True

        except Exception as e:
            logger.error(f"Error ending learning session: {e}")
            return False

    # ============= GAMIFICATION & ACHIEVEMENTS =============

    def _check_item_achievements(
        self, item: SpacedRepetitionItem, review_result: ReviewResult
    ):
        """Check and award achievements based on item review"""

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
            self._award_achievement(
                item.user_id,
                item.language_code,
                achievement["type"],
                achievement["title"],
                achievement["description"],
                points_awarded=achievement["points"],
            )

    def _award_achievement(
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
        """Award an achievement to a user"""

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

    def _update_learning_streaks(self, session_info: Dict):
        """Update learning streaks based on session completion"""

        if not session_info:
            return

        user_id = session_info["user_id"]
        language_code = session_info["language_code"]
        today = date.today()

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get or create streak record
                cursor.execute(
                    """
                    SELECT * FROM learning_streaks
                    WHERE user_id = ? AND language_code = ?
                """,
                    (user_id, language_code),
                )

                streak_row = cursor.fetchone()

                if streak_row:
                    # Update existing streak
                    last_activity = (
                        date.fromisoformat(streak_row["last_activity_date"])
                        if streak_row["last_activity_date"]
                        else None
                    )
                    current_streak = streak_row["current_streak"]

                    if last_activity == today:
                        # Already studied today, no streak change
                        return
                    elif last_activity == today - timedelta(days=1):
                        # Consecutive day, increase streak
                        current_streak += 1
                    elif last_activity and (today - last_activity).days > 1:
                        # Broke streak, reset
                        current_streak = 1
                    else:
                        # First day or continuing
                        current_streak = max(current_streak, 1)

                    # Update streak record
                    longest_streak = max(streak_row["longest_streak"], current_streak)
                    total_active_days = streak_row["total_active_days"] + 1

                    cursor.execute(
                        """
                        UPDATE learning_streaks SET
                            current_streak = ?, longest_streak = ?, total_active_days = ?,
                            last_activity_date = ?, updated_at = ?
                        WHERE user_id = ? AND language_code = ?
                    """,
                        (
                            current_streak,
                            longest_streak,
                            total_active_days,
                            today,
                            datetime.now(),
                            user_id,
                            language_code,
                        ),
                    )

                else:
                    # Create new streak record
                    cursor.execute(
                        """
                        INSERT INTO learning_streaks (
                            user_id, language_code, current_streak, longest_streak,
                            total_active_days, last_activity_date, streak_start_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (user_id, language_code, 1, 1, 1, today, today),
                    )
                    current_streak = 1

                conn.commit()

                # Check for streak achievements
                self._check_streak_achievements(user_id, language_code, current_streak)

        except Exception as e:
            logger.error(f"Error updating learning streaks: {e}")

    def _check_streak_achievements(
        self, user_id: int, language_code: str, current_streak: int
    ):
        """Check and award streak-based achievements"""

        streak_milestones = [7, 14, 30, 60, 100, 365]

        for milestone in streak_milestones:
            if current_streak == milestone:
                if milestone == 7:
                    title, desc, points = (
                        "Week Warrior",
                        "Studied for 7 consecutive days",
                        50,
                    )
                elif milestone == 14:
                    title, desc, points = (
                        "Two Week Champion",
                        "Studied for 14 consecutive days",
                        100,
                    )
                elif milestone == 30:
                    title, desc, points = (
                        "Monthly Master",
                        "Studied for 30 consecutive days",
                        200,
                    )
                elif milestone == 60:
                    title, desc, points = (
                        "Dedication Legend",
                        "Studied for 60 consecutive days",
                        400,
                    )
                elif milestone == 100:
                    title, desc, points = (
                        "Century Scholar",
                        "Studied for 100 consecutive days",
                        750,
                    )
                elif milestone == 365:
                    title, desc, points = (
                        "Year-Long Learner",
                        "Studied for 365 consecutive days",
                        1500,
                    )

                self._award_achievement(
                    user_id,
                    language_code,
                    AchievementType.STREAK,
                    title,
                    desc,
                    points_awarded=points,
                    badge_icon="🔥",
                    rarity="rare" if milestone >= 30 else "common",
                )

    # ============= ANALYTICS & REPORTING =============

    def get_user_analytics(
        self, user_id: int, language_code: str, period: str = "daily"
    ) -> Dict[str, Any]:
        """Get comprehensive learning analytics for a user"""

        try:
            with self._get_connection() as conn:
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
                    (self.config["mastery_threshold"], user_id, language_code),
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
        """Generate personalized learning recommendations"""

        recommendations = []

        try:
            with self._get_connection() as conn:
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

    # ============= ADMIN CONFIGURATION =============

    def update_algorithm_config(self, config_updates: Dict[str, Any]) -> bool:
        """Update spaced repetition algorithm configuration"""

        try:
            with self._get_connection() as conn:
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

    def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide learning analytics for admin dashboard"""

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Total users and sessions
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
__all__ = [
    "SpacedRepetitionManager",
    "ItemType",
    "SessionType",
    "ReviewResult",
    "AchievementType",
]
