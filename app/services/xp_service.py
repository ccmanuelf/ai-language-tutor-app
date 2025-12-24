"""
XP and Leveling Service for AI Language Tutor App

This service manages experience points, leveling system, and progression tracking.
Handles XP calculations, level-up rewards, and progression visualization.
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.gamification_models import UserTitle, UserXP, XPTransaction

logger = logging.getLogger(__name__)


class XPService:
    """Service for managing XP and levels"""

    # XP Formula Constants
    BASE_XP_PER_LEVEL = 100
    XP_MULTIPLIER = 1.15  # Exponential curve

    # Level Title Thresholds
    TITLE_THRESHOLDS = {
        UserTitle.NOVICE: 1,
        UserTitle.LEARNER: 11,
        UserTitle.ENTHUSIAST: 26,
        UserTitle.EXPERT: 41,
        UserTitle.MASTER: 61,
        UserTitle.VIRTUOSO: 81,
        UserTitle.LEGEND: 96,
    }

    def __init__(self, db: Session):
        self.db = db

    # =====================================================================
    # USER XP INITIALIZATION
    # =====================================================================

    async def initialize_user_xp(self, user_id: int) -> UserXP:
        """
        Initialize XP tracking for a new user.

        Args:
            user_id: User ID

        Returns:
            UserXP: Created XP record
        """
        try:
            # Check if XP already exists
            existing = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()

            if existing:
                return existing

            # Create new XP record
            user_xp = UserXP(
                user_id=user_id,
                total_xp=0,
                current_level=1,
                xp_to_next_level=self._calculate_xp_for_level(
                    2
                ),  # XP needed for level 2
                level_progress_percentage=0.0,
                title=UserTitle.NOVICE.value,
            )

            self.db.add(user_xp)
            self.db.commit()
            self.db.refresh(user_xp)

            logger.info(f"Initialized XP tracking for user {user_id}")
            return user_xp

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error initializing user XP: {e}")
            raise

    # =====================================================================
    # XP CALCULATIONS
    # =====================================================================

    def _calculate_xp_for_level(self, level: int) -> int:
        """
        Calculate total XP required to reach a specific level.
        Uses exponential curve: XP = BASE * (MULTIPLIER ^ (level - 1))

        Args:
            level: Target level (1-100)

        Returns:
            Total XP required to reach this level
        """
        if level <= 1:
            return 0

        total_xp = 0
        for lvl in range(2, level + 1):
            xp_for_level = int(
                self.BASE_XP_PER_LEVEL * (self.XP_MULTIPLIER ** (lvl - 2))
            )
            total_xp += xp_for_level

        return total_xp

    def _calculate_level_from_xp(self, total_xp: int) -> int:
        """
        Calculate current level based on total XP.

        Args:
            total_xp: Total XP earned

        Returns:
            Current level (1-100)
        """
        if total_xp <= 0:
            return 1

        level = 1
        cumulative_xp = 0

        while level < 100:
            xp_needed = self._calculate_xp_for_level(level + 1)
            if total_xp < xp_needed:
                break
            level += 1

        return level

    def _get_title_for_level(self, level: int) -> str:
        """
        Get user title based on level.

        Args:
            level: Current level

        Returns:
            Title string
        """
        for title, threshold in sorted(
            self.TITLE_THRESHOLDS.items(), key=lambda x: x[1], reverse=True
        ):
            if level >= threshold:
                return title.value

        return UserTitle.NOVICE.value

    # =====================================================================
    # AWARD XP
    # =====================================================================

    async def award_xp(
        self,
        user_id: int,
        xp_amount: int,
        reason: str,
        reference_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Award XP to a user and handle level-ups.

        Args:
            user_id: User ID
            xp_amount: Amount of XP to award (can be negative)
            reason: Reason for XP award (e.g., "scenario_completion")
            reference_id: Reference to source (e.g., scenario_id)
            metadata: Additional context

        Returns:
            Dict with XP award results and level-up info
        """
        try:
            # Get or create user XP
            user_xp = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()

            if not user_xp:
                user_xp = await self.initialize_user_xp(user_id)

            # Store previous state
            old_level = user_xp.current_level
            old_xp = user_xp.total_xp

            # Award XP
            user_xp.total_xp = max(0, user_xp.total_xp + xp_amount)

            # Recalculate level
            new_level = self._calculate_level_from_xp(user_xp.total_xp)
            user_xp.current_level = new_level

            # Update title if level changed
            if new_level != old_level:
                user_xp.title = self._get_title_for_level(new_level)

            # Calculate progress to next level
            if new_level >= 100:
                user_xp.xp_to_next_level = 0
                user_xp.level_progress_percentage = 100.0
            else:
                xp_for_current_level = self._calculate_xp_for_level(new_level)
                xp_for_next_level = self._calculate_xp_for_level(new_level + 1)
                xp_in_current_level = user_xp.total_xp - xp_for_current_level
                xp_needed_for_next = xp_for_next_level - xp_for_current_level

                user_xp.xp_to_next_level = xp_needed_for_next - xp_in_current_level
                user_xp.level_progress_percentage = (
                    xp_in_current_level / xp_needed_for_next
                ) * 100

            # Create XP transaction record
            transaction = XPTransaction(
                user_id=user_id,
                xp_amount=xp_amount,
                reason=reason,
                reference_id=reference_id,
                metadata=metadata or {},
            )
            self.db.add(transaction)

            self.db.commit()
            self.db.refresh(user_xp)

            # Determine if level-up occurred
            level_up = new_level > old_level

            logger.info(
                f"Awarded {xp_amount} XP to user {user_id} (reason: {reason}), "
                f"total: {user_xp.total_xp}, level: {new_level}"
            )

            result = {
                "success": True,
                "xp_awarded": xp_amount,
                "total_xp": user_xp.total_xp,
                "previous_xp": old_xp,
                "current_level": new_level,
                "previous_level": old_level,
                "level_up": level_up,
                "xp_to_next_level": user_xp.xp_to_next_level,
                "level_progress_percentage": round(
                    user_xp.level_progress_percentage, 2
                ),
                "title": user_xp.title,
            }

            # Add level-up specific info
            if level_up:
                result["levels_gained"] = new_level - old_level
                result["message"] = (
                    f"Level up! You are now level {new_level} - {user_xp.title}!"
                )

                # Award level-up rewards
                rewards = await self._award_level_up_rewards(
                    user_id, new_level, old_level
                )
                result["rewards"] = rewards

            return result

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error awarding XP: {e}")
            raise

    async def _award_level_up_rewards(
        self, user_id: int, new_level: int, old_level: int
    ) -> Dict[str, Any]:
        """
        Award rewards for leveling up.

        Args:
            user_id: User ID
            new_level: New level achieved
            old_level: Previous level

        Returns:
            Dict with rewards awarded
        """
        from app.models.gamification_models import UserStreak

        rewards = {
            "freeze_tokens": 0,
            "badges": [],
        }

        # Award freeze tokens at milestone levels
        freeze_milestones = [10, 25, 50, 75, 100]

        for milestone in freeze_milestones:
            if old_level < milestone <= new_level:
                # Award freeze token
                streak = (
                    self.db.query(UserStreak)
                    .filter(UserStreak.user_id == user_id)
                    .first()
                )
                if streak and streak.streak_freezes_available < 3:
                    streak.streak_freezes_available += 1
                    streak.total_freezes_earned += 1
                    rewards["freeze_tokens"] += 1

        # Check for title changes
        old_title = self._get_title_for_level(old_level)
        new_title = self._get_title_for_level(new_level)

        if old_title != new_title:
            rewards["new_title"] = new_title
            rewards["badges"].append(f"{new_title} Badge")

        if rewards["freeze_tokens"] > 0 or rewards["badges"]:
            self.db.commit()

        return rewards

    # =====================================================================
    # SCENARIO COMPLETION XP
    # =====================================================================

    async def calculate_scenario_completion_xp(
        self,
        scenario_difficulty: str,
        rating: Optional[int] = None,
        cultural_accuracy: Optional[int] = None,
        completion_time_minutes: Optional[int] = None,
        estimated_time_minutes: Optional[int] = None,
        streak_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calculate XP for completing a scenario.

        Args:
            scenario_difficulty: beginner, intermediate, or advanced
            rating: User's rating (1-5)
            cultural_accuracy: Cultural accuracy rating (1-10)
            completion_time_minutes: Actual completion time
            estimated_time_minutes: Estimated completion time
            streak_multiplier: Multiplier from active streak

        Returns:
            Dict with XP breakdown
        """
        # Base XP by difficulty
        base_xp = {
            "beginner": 50,
            "intermediate": 75,
            "advanced": 100,
        }.get(scenario_difficulty, 50)

        # Calculate bonuses
        rating_bonus = 0
        if rating == 5:
            rating_bonus = int(base_xp * 0.2)  # 20% bonus for perfect rating

        cultural_bonus = 0
        if cultural_accuracy and cultural_accuracy >= 9:
            cultural_bonus = int(base_xp * 0.15)  # 15% bonus for high cultural accuracy

        speed_bonus = 0
        if completion_time_minutes and estimated_time_minutes:
            if completion_time_minutes <= (estimated_time_minutes * 0.8):
                speed_bonus = int(base_xp * 0.1)  # 10% bonus for fast completion

        # Calculate total
        subtotal = base_xp + rating_bonus + cultural_bonus + speed_bonus
        streak_bonus = int(subtotal * (streak_multiplier - 1.0))
        total_xp = subtotal + streak_bonus

        return {
            "base_xp": base_xp,
            "rating_bonus": rating_bonus,
            "cultural_bonus": cultural_bonus,
            "speed_bonus": speed_bonus,
            "subtotal": subtotal,
            "streak_multiplier": streak_multiplier,
            "streak_bonus": streak_bonus,
            "total_xp": total_xp,
            "breakdown": [
                {"source": "Base XP", "amount": base_xp},
                {"source": "Perfect Rating", "amount": rating_bonus},
                {"source": "Cultural Accuracy", "amount": cultural_bonus},
                {"source": "Speed Bonus", "amount": speed_bonus},
                {
                    "source": f"Streak Bonus ({int((streak_multiplier - 1) * 100)}%)",
                    "amount": streak_bonus,
                },
            ],
        }

    # =====================================================================
    # XP QUERIES
    # =====================================================================

    async def get_user_level(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user's current level and progress.

        Args:
            user_id: User ID

        Returns:
            Dict with level information
        """
        try:
            user_xp = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()

            if not user_xp:
                return None

            return {
                "user_id": user_id,
                "total_xp": user_xp.total_xp,
                "current_level": user_xp.current_level,
                "xp_to_next_level": user_xp.xp_to_next_level,
                "level_progress_percentage": round(
                    user_xp.level_progress_percentage, 2
                ),
                "title": user_xp.title,
            }

        except Exception as e:
            logger.error(f"Error getting user level: {e}")
            return None

    async def get_xp_history(
        self, user_id: int, limit: int = 50, reason_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's XP transaction history.

        Args:
            user_id: User ID
            limit: Max number of transactions to return
            reason_filter: Filter by reason (optional)

        Returns:
            List of XP transactions
        """
        try:
            query = self.db.query(XPTransaction).filter(
                XPTransaction.user_id == user_id
            )

            if reason_filter:
                query = query.filter(XPTransaction.reason == reason_filter)

            transactions = (
                query.order_by(XPTransaction.created_at.desc()).limit(limit).all()
            )

            return [
                {
                    "id": tx.id,
                    "xp_amount": tx.xp_amount,
                    "reason": tx.reason,
                    "reference_id": tx.reference_id,
                    "metadata": tx.metadata,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None,
                }
                for tx in transactions
            ]

        except Exception as e:
            logger.error(f"Error getting XP history: {e}")
            return []

    async def get_leaderboard_xp_rankings(
        self, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get top users by total XP (for leaderboard).

        Args:
            limit: Number of users to return

        Returns:
            List of top users by XP
        """
        try:
            from app.models.database import User

            rankings = (
                self.db.query(UserXP, User)
                .join(User, UserXP.user_id == User.id)
                .order_by(UserXP.total_xp.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "rank": idx + 1,
                    "user_id": user_xp.user_id,
                    "username": user.username,
                    "total_xp": user_xp.total_xp,
                    "current_level": user_xp.current_level,
                    "title": user_xp.title,
                }
                for idx, (user_xp, user) in enumerate(rankings)
            ]

        except Exception as e:
            logger.error(f"Error getting XP leaderboard: {e}")
            return []

    async def get_xp_statistics(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive XP statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dict with XP statistics
        """
        try:
            from sqlalchemy import func

            user_xp = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()

            if not user_xp:
                return None

            # Get transaction stats
            total_transactions = (
                self.db.query(func.count(XPTransaction.id))
                .filter(XPTransaction.user_id == user_id)
                .scalar()
            ) or 0

            total_earned = (
                self.db.query(func.sum(XPTransaction.xp_amount))
                .filter(
                    XPTransaction.user_id == user_id,
                    XPTransaction.xp_amount > 0,
                )
                .scalar()
            ) or 0

            # XP by reason
            xp_by_reason = (
                self.db.query(
                    XPTransaction.reason,
                    func.sum(XPTransaction.xp_amount).label("total"),
                )
                .filter(XPTransaction.user_id == user_id)
                .group_by(XPTransaction.reason)
                .all()
            )

            return {
                "user_id": user_id,
                "total_xp": user_xp.total_xp,
                "current_level": user_xp.current_level,
                "title": user_xp.title,
                "total_transactions": total_transactions,
                "total_earned": total_earned,
                "xp_by_source": {reason: total for reason, total in xp_by_reason},
                "xp_to_next_level": user_xp.xp_to_next_level,
                "level_progress_percentage": round(
                    user_xp.level_progress_percentage, 2
                ),
            }

        except Exception as e:
            logger.error(f"Error getting XP statistics: {e}")
            return None
