"""
Session Management for Spaced Repetition System
Handles learning session lifecycle and streak tracking
"""

import json
import logging
import uuid
from datetime import datetime, timedelta, date
from typing import Dict, Optional

from app.services.sr_database import DatabaseManager
from app.services.sr_models import LearningSession, SessionType

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages learning session lifecycle, duration tracking, and streak updates.

    Responsibilities:
    - Starting and ending learning sessions
    - Computing session metrics (duration, accuracy, engagement)
    - Updating learning streaks based on session completion
    - Tracking session contributions to goals and achievements
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize SessionManager with database connection.

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager

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
        """
        Start a new learning session and record it in the database.

        Args:
            user_id: ID of the user starting the session
            language_code: Language code for this session (e.g., 'es', 'fr')
            session_type: Type of learning session (SessionType enum)
            mode_specific_data: Dictionary containing mode-specific session data
            content_source: Source of learning content
            ai_model_used: AI model used for this session
            tutor_mode: Specific tutor mode being used
            scenario_id: ID of scenario if applicable

        Returns:
            str: Unique session_id for the newly created session

        Raises:
            Exception: If database insertion fails
        """
        session_id = str(uuid.uuid4())
        session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            language_code=language_code,
            session_type=session_type.value
            if hasattr(session_type, "value")
            else session_type,
            mode_specific_data=mode_specific_data or {},
            content_source=content_source,
            ai_model_used=ai_model_used,
            tutor_mode=tutor_mode,
            scenario_id=scenario_id,
        )

        try:
            with self.db.get_connection() as conn:
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
        """
        End a learning session and calculate final metrics.

        Computes session duration, accuracy percentage, and updates streak data.
        Also triggers streak-based achievements.

        Args:
            session_id: Unique identifier for the session to end
            items_studied: Total number of items studied in session
            items_correct: Number of items answered correctly
            items_incorrect: Number of items answered incorrectly
            average_response_time_ms: Average response time in milliseconds
            confidence_score: User's self-reported confidence (0.0-1.0)
            engagement_score: Computed engagement metric (0.0-1.0)
            new_items_learned: Number of new items introduced in this session

        Returns:
            bool: True if session ended successfully, False otherwise

        Notes:
            - Automatically calculates duration from start to end time
            - Computes accuracy percentage from correct/incorrect counts
            - Updates learning streaks and checks for streak achievements
            - Items reviewed = items_studied - new_items_learned
        """
        try:
            with self.db.get_connection() as conn:
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

                # Calculate accuracy percentage
                total_items = items_correct + items_incorrect
                accuracy_percentage = (
                    (items_correct / total_items * 100) if total_items > 0 else 0
                )

                # Update session with computed metrics
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

                # Get session info for streak update
                cursor.execute(
                    """
                    SELECT user_id, language_code FROM learning_sessions
                    WHERE session_id = ?
                """,
                    (session_id,),
                )

                session_info = cursor.fetchone()
                if session_info:
                    self._update_learning_streaks(dict(session_info))

                logger.info(
                    f"Ended learning session: {session_id} ({duration_minutes} minutes)"
                )
                return True

        except Exception as e:
            logger.error(f"Error ending learning session: {e}")
            return False

    def _update_learning_streaks(self, session_info: Dict):
        """
        Update learning streaks based on session completion.

        Handles streak logic:
        - Same day activity: no streak change
        - Consecutive day: increment streak
        - Broken streak (gap > 1 day): reset to 1
        - First activity: initialize streak

        Also checks for streak-based achievements at milestones.

        Args:
            session_info: Dictionary containing user_id and language_code
        """
        if not session_info:
            return

        user_id = session_info["user_id"]
        language_code = session_info["language_code"]
        today = date.today()

        try:
            with self.db.get_connection() as conn:
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

                # Check for streak achievements at milestones
                self._check_streak_achievements(user_id, language_code, current_streak)

        except Exception as e:
            logger.error(f"Error updating learning streaks: {e}")

    def _check_streak_achievements(
        self, user_id: int, language_code: str, current_streak: int
    ):
        """
        Check and award streak-based achievements at milestone days.

        Milestones:
        - 7 days: Week Warrior (50 points)
        - 14 days: Two Week Champion (100 points)
        - 30 days: Monthly Master (200 points)
        - 60 days: Dedication Legend (400 points)
        - 100 days: Century Scholar (750 points)
        - 365 days: Year-Long Learner (1500 points)

        Args:
            user_id: ID of the user to check
            language_code: Language code for the streak
            current_streak: Current consecutive day count

        Notes:
            Achievement is only awarded once at exact milestone.
            Requires integration with gamification system.
        """
        streak_milestones = [7, 14, 30, 60, 100, 365]

        for milestone in streak_milestones:
            if current_streak == milestone:
                # Map milestones to achievement details
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
                else:
                    continue

                # Award the achievement
                self._award_streak_achievement(
                    user_id,
                    language_code,
                    title,
                    desc,
                    points,
                    milestone,
                )

    def _award_streak_achievement(
        self,
        user_id: int,
        language_code: str,
        title: str,
        description: str,
        points_awarded: int,
        milestone: int,
    ):
        """
        Award a streak achievement to a user.

        Creates achievement record in database with streak-specific attributes.
        Prevents duplicate awards within 24 hours.

        Args:
            user_id: ID of the user earning the achievement
            language_code: Language code for the achievement
            title: Achievement title
            description: Achievement description
            points_awarded: Points awarded for achievement
            milestone: Streak milestone reached
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                achievement_id = str(uuid.uuid4())

                # Check if similar achievement already exists (prevent duplicates)
                cursor.execute(
                    """
                    SELECT achievement_id FROM gamification_achievements
                    WHERE user_id = ? AND achievement_type = ? AND title = ?
                    AND earned_at > datetime('now', '-1 day')
                """,
                    (user_id, "streak", title),
                )

                if cursor.fetchone():
                    logger.info(f"Achievement already awarded recently: {title}")
                    return

                # Determine rarity based on milestone
                rarity = "rare" if milestone >= 30 else "common"

                cursor.execute(
                    """
                    INSERT INTO gamification_achievements (
                        achievement_id, user_id, language_code, achievement_type, title,
                        description, badge_icon, badge_color, points_awarded,
                        criteria_met, required_criteria, rarity, milestone_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        achievement_id,
                        user_id,
                        language_code,
                        "streak",
                        title,
                        description,
                        "🔥",
                        "#FF6B35",
                        points_awarded,
                        json.dumps({"streak_days": milestone}),
                        json.dumps({"required_days": milestone}),
                        rarity,
                        milestone,
                    ),
                )

                conn.commit()
                logger.info(f"Awarded streak achievement: {title} to user {user_id}")

        except Exception as e:
            logger.error(f"Error awarding streak achievement: {e}")


__all__ = ["SessionManager"]
