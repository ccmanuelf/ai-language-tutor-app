"""
Streak Service for AI Language Tutor App

This service manages daily streak tracking, freeze tokens, and milestone rewards.
Handles timezone-aware streak calculations and automatic streak updates.
"""

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any, Dict, Optional

import pytz
from sqlalchemy.orm import Session

from app.models.gamification_models import StreakHistory, UserStreak

logger = logging.getLogger(__name__)


class StreakService:
    """Service for managing user streaks"""

    def __init__(self, db: Session):
        self.db = db

    # =====================================================================
    # STREAK INITIALIZATION
    # =====================================================================

    async def initialize_user_streak(
        self, user_id: int, timezone: str = "UTC"
    ) -> UserStreak:
        """
        Initialize streak tracking for a new user.

        Args:
            user_id: User ID
            timezone: User's timezone (default: UTC)

        Returns:
            UserStreak: Created streak record
        """
        try:
            # Check if streak already exists
            existing = (
                self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            )

            if existing:
                return existing

            # Create new streak
            user_streak = UserStreak(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                last_activity_date=None,
                streak_freezes_available=0,
                total_freezes_earned=0,
                total_freezes_used=0,
                timezone=timezone,
            )

            self.db.add(user_streak)
            self.db.commit()
            self.db.refresh(user_streak)

            logger.info(f"Initialized streak tracking for user {user_id}")
            return user_streak

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error initializing user streak: {e}")
            raise

    # =====================================================================
    # STREAK UPDATES
    # =====================================================================

    async def update_user_streak(self, user_id: int) -> Dict[str, Any]:
        """
        Update user's streak based on daily activity.
        Should be called when user completes a scenario.

        Args:
            user_id: User ID

        Returns:
            Dict with streak update results
        """
        try:
            # Get or create user streak
            user_streak = (
                self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            )

            if not user_streak:
                user_streak = await self.initialize_user_streak(user_id)

            # Get user's current date in their timezone
            tz = pytz.timezone(user_streak.timezone)
            user_today = datetime.now(tz).date()

            # Get last activity date
            last_activity = user_streak.last_activity_date

            # Determine streak action
            if last_activity is None:
                # First activity ever
                result = await self._start_streak(user_streak, user_today)
            elif last_activity == user_today:
                # Already recorded activity today
                result = {
                    "action": "no_change",
                    "current_streak": user_streak.current_streak,
                    "message": "Activity already recorded today",
                }
            elif last_activity == user_today - timedelta(days=1):
                # Consecutive day - increment streak
                result = await self._increment_streak(user_streak, user_today)
            elif last_activity < user_today - timedelta(days=1):
                # Streak broken - check if freeze available
                days_missed = (user_today - last_activity).days - 1

                if days_missed == 1 and user_streak.streak_freezes_available > 0:
                    # Can use freeze to save streak
                    result = {
                        "action": "freeze_available",
                        "current_streak": user_streak.current_streak,
                        "days_missed": days_missed,
                        "freezes_available": user_streak.streak_freezes_available,
                        "message": "Streak at risk! Use a freeze to protect it.",
                    }
                else:
                    # Streak lost
                    result = await self._reset_streak(
                        user_streak, user_today, days_missed
                    )
            else:
                # Future date (shouldn't happen, but handle gracefully)
                result = {
                    "action": "error",
                    "message": "Invalid date detected",
                }

            return result

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user streak: {e}")
            raise

    async def _start_streak(
        self, user_streak: UserStreak, today: date
    ) -> Dict[str, Any]:
        """Start a new streak"""
        user_streak.current_streak = 1
        user_streak.longest_streak = max(user_streak.longest_streak, 1)
        user_streak.last_activity_date = today

        # Record history
        self._record_streak_history(user_streak.user_id, today, 1, freeze_used=False)

        self.db.commit()

        logger.info(f"Started streak for user {user_streak.user_id}")

        return {
            "action": "started",
            "current_streak": 1,
            "longest_streak": user_streak.longest_streak,
            "message": "Streak started! 🔥",
            "milestone_reached": False,
        }

    async def _increment_streak(
        self, user_streak: UserStreak, today: date
    ) -> Dict[str, Any]:
        """Increment existing streak"""
        user_streak.current_streak += 1
        user_streak.longest_streak = max(
            user_streak.longest_streak, user_streak.current_streak
        )
        user_streak.last_activity_date = today

        # Check for freeze rewards (every 7 days)
        freeze_earned = False
        if (
            user_streak.current_streak % 7 == 0
            and user_streak.streak_freezes_available < 3
        ):
            user_streak.streak_freezes_available += 1
            user_streak.total_freezes_earned += 1
            user_streak.last_freeze_earned_at = datetime.now(UTC)
            freeze_earned = True

        # Check for milestones
        milestone_reached = user_streak.current_streak in [3, 7, 14, 30, 50, 100, 365]

        # Record history
        self._record_streak_history(
            user_streak.user_id, today, user_streak.current_streak, freeze_used=False
        )

        self.db.commit()

        logger.info(
            f"Incremented streak for user {user_streak.user_id} to {user_streak.current_streak}"
        )

        result = {
            "action": "incremented",
            "current_streak": user_streak.current_streak,
            "longest_streak": user_streak.longest_streak,
            "message": f"{user_streak.current_streak} day streak! 🔥",
            "milestone_reached": milestone_reached,
        }

        if freeze_earned:
            result["freeze_earned"] = True
            result["freezes_available"] = user_streak.streak_freezes_available
            result["message"] += " Freeze token earned! ❄️"

        return result

    async def _reset_streak(
        self, user_streak: UserStreak, today: date, days_missed: int
    ) -> Dict[str, Any]:
        """Reset streak after it was broken"""
        old_streak = user_streak.current_streak

        user_streak.current_streak = 1  # Start new streak
        user_streak.last_activity_date = today

        # Record history
        self._record_streak_history(user_streak.user_id, today, 1, freeze_used=False)

        self.db.commit()

        logger.info(
            f"Reset streak for user {user_streak.user_id}, lost {old_streak} day streak"
        )

        return {
            "action": "reset",
            "current_streak": 1,
            "previous_streak": old_streak,
            "days_missed": days_missed,
            "longest_streak": user_streak.longest_streak,
            "message": f"Streak reset. You lost a {old_streak} day streak.",
        }

    def _record_streak_history(
        self, user_id: int, activity_date: date, streak_value: int, freeze_used: bool
    ):
        """Record streak history entry"""
        try:
            history = StreakHistory(
                user_id=user_id,
                activity_date=activity_date,
                streak_value=streak_value,
                freeze_used=freeze_used,
            )
            self.db.add(history)
        except Exception as e:
            logger.warning(f"Error recording streak history: {e}")

    # =====================================================================
    # STREAK FREEZES
    # =====================================================================

    async def use_streak_freeze(self, user_id: int) -> Dict[str, Any]:
        """
        Use a streak freeze to protect a broken streak.

        Args:
            user_id: User ID

        Returns:
            Dict with freeze usage results
        """
        try:
            user_streak = (
                self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            )

            if not user_streak:
                return {
                    "success": False,
                    "message": "Streak not found",
                }

            # Check if freeze available
            if user_streak.streak_freezes_available <= 0:
                return {
                    "success": False,
                    "message": "No freezes available",
                    "current_streak": user_streak.current_streak,
                }

            # Get user's current date
            tz = pytz.timezone(user_streak.timezone)
            user_today = datetime.now(tz).date()
            last_activity = user_streak.last_activity_date

            # Verify streak is at risk
            if last_activity is None:
                return {
                    "success": False,
                    "message": "No active streak to protect",
                }

            days_since_activity = (user_today - last_activity).days

            if days_since_activity <= 1:
                return {
                    "success": False,
                    "message": "Streak is not at risk",
                    "current_streak": user_streak.current_streak,
                }

            if days_since_activity > 2:
                return {
                    "success": False,
                    "message": "Missed too many days. Freeze can only cover 1 day.",
                    "current_streak": user_streak.current_streak,
                }

            # Use freeze
            user_streak.streak_freezes_available -= 1
            user_streak.total_freezes_used += 1
            user_streak.last_freeze_used_at = datetime.now(UTC)

            # Record history with freeze flag
            yesterday = user_today - timedelta(days=1)
            self._record_streak_history(
                user_streak.user_id,
                yesterday,
                user_streak.current_streak,
                freeze_used=True,
            )

            self.db.commit()

            logger.info(
                f"User {user_id} used streak freeze, {user_streak.streak_freezes_available} remaining"
            )

            return {
                "success": True,
                "message": "Freeze used! Your streak is protected. ❄️",
                "current_streak": user_streak.current_streak,
                "freezes_remaining": user_streak.streak_freezes_available,
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error using streak freeze: {e}")
            raise

    # =====================================================================
    # STREAK QUERIES
    # =====================================================================

    async def get_streak_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user's current streak status.

        Args:
            user_id: User ID

        Returns:
            Dict with streak information
        """
        try:
            user_streak = (
                self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            )

            if not user_streak:
                return None

            # Calculate days until next freeze
            days_to_next_freeze = None
            if (
                user_streak.current_streak > 0
                and user_streak.streak_freezes_available < 3
            ):
                days_to_next_freeze = 7 - (user_streak.current_streak % 7)

            # Check if streak is at risk
            tz = pytz.timezone(user_streak.timezone)
            user_today = datetime.now(tz).date()

            is_at_risk = False
            days_since_activity = 0

            if user_streak.last_activity_date:
                days_since_activity = (user_today - user_streak.last_activity_date).days
                is_at_risk = days_since_activity > 0

            return {
                "user_id": user_id,
                "current_streak": user_streak.current_streak,
                "longest_streak": user_streak.longest_streak,
                "last_activity_date": user_streak.last_activity_date.isoformat()
                if user_streak.last_activity_date
                else None,
                "streak_freezes_available": user_streak.streak_freezes_available,
                "total_freezes_earned": user_streak.total_freezes_earned,
                "total_freezes_used": user_streak.total_freezes_used,
                "days_to_next_freeze": days_to_next_freeze,
                "is_at_risk": is_at_risk,
                "days_since_activity": days_since_activity,
                "timezone": user_streak.timezone,
            }

        except Exception as e:
            logger.error(f"Error getting streak status: {e}")
            return None

    async def get_streak_history(self, user_id: int, days: int = 30) -> list:
        """
        Get user's streak history.

        Args:
            user_id: User ID
            days: Number of days to retrieve

        Returns:
            List of streak history entries
        """
        try:
            cutoff_date = date.today() - timedelta(days=days)

            history = (
                self.db.query(StreakHistory)
                .filter(
                    StreakHistory.user_id == user_id,
                    StreakHistory.activity_date >= cutoff_date,
                )
                .order_by(StreakHistory.activity_date.desc())
                .all()
            )

            return [
                {
                    "date": entry.activity_date.isoformat(),
                    "streak_value": entry.streak_value,
                    "freeze_used": entry.freeze_used,
                }
                for entry in history
            ]

        except Exception as e:
            logger.error(f"Error getting streak history: {e}")
            return []

    async def calculate_streak_bonus(self, user_id: int) -> float:
        """
        Calculate XP multiplier based on current streak.

        Args:
            user_id: User ID

        Returns:
            Multiplier (1.0 = no bonus, 1.1 = 10% bonus, etc.)
        """
        try:
            user_streak = (
                self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            )

            if not user_streak or user_streak.current_streak == 0:
                return 1.0

            # Bonus tiers
            if user_streak.current_streak >= 100:
                return 1.5  # 50% bonus
            elif user_streak.current_streak >= 30:
                return 1.25  # 25% bonus
            elif user_streak.current_streak >= 7:
                return 1.10  # 10% bonus
            else:
                return 1.0  # No bonus

        except Exception as e:
            logger.error(f"Error calculating streak bonus: {e}")
            return 1.0
