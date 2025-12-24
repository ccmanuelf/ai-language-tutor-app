"""
Achievement Service for AI Language Tutor App

This service manages achievement unlocking, tracking, and validation.
Handles event-driven achievement checking and user progress tracking.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.data.achievement_definitions import ALL_ACHIEVEMENTS, get_achievement_by_id
from app.models.gamification_models import Achievement, UserAchievement
from app.models.scenario_db_models import (
    ScenarioBookmark,
    ScenarioCollection,
    ScenarioRating,
)

# Note: ScenarioCompletion model will be added in future update
# For now, completion-based achievement checking will use placeholder logic

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing achievements"""

    def __init__(self, db: Session):
        self.db = db

    # =====================================================================
    # ACHIEVEMENT INITIALIZATION
    # =====================================================================

    async def initialize_achievements(self) -> int:
        """
        Initialize achievement definitions in database.
        Should be called on app startup or during setup.

        Returns:
            int: Number of achievements created
        """
        try:
            created_count = 0

            for ach_def in ALL_ACHIEVEMENTS:
                # Check if achievement already exists
                existing = (
                    self.db.query(Achievement)
                    .filter(Achievement.achievement_id == ach_def["achievement_id"])
                    .first()
                )

                if not existing:
                    achievement = Achievement(
                        achievement_id=ach_def["achievement_id"],
                        name=ach_def["name"],
                        description=ach_def["description"],
                        category=ach_def["category"],
                        rarity=ach_def["rarity"],
                        icon_url=ach_def["icon_url"],
                        xp_reward=ach_def["xp_reward"],
                        criteria=ach_def["criteria"],
                        is_active=True,
                        display_order=ach_def.get("display_order", 0),
                    )
                    self.db.add(achievement)
                    created_count += 1
                else:
                    # Update existing achievement (in case definition changed)
                    existing.name = ach_def["name"]
                    existing.description = ach_def["description"]
                    existing.category = ach_def["category"]
                    existing.rarity = ach_def["rarity"]
                    existing.icon_url = ach_def["icon_url"]
                    existing.xp_reward = ach_def["xp_reward"]
                    existing.criteria = ach_def["criteria"]
                    existing.display_order = ach_def.get("display_order", 0)

            self.db.commit()
            logger.info(
                f"Initialized {created_count} new achievements, updated {len(ALL_ACHIEVEMENTS) - created_count}"
            )
            return created_count

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error initializing achievements: {e}")
            raise

    # =====================================================================
    # ACHIEVEMENT UNLOCKING
    # =====================================================================

    async def unlock_achievement(
        self, user_id: int, achievement_id: str, metadata: Optional[Dict] = None
    ) -> Optional[UserAchievement]:
        """
        Unlock an achievement for a user.

        Args:
            user_id: User ID
            achievement_id: Achievement identifier (e.g., "first_steps")
            metadata: Optional context data

        Returns:
            UserAchievement if newly unlocked, None if already unlocked
        """
        try:
            # Get achievement definition
            achievement = (
                self.db.query(Achievement)
                .filter(Achievement.achievement_id == achievement_id)
                .first()
            )

            if not achievement:
                logger.warning(f"Achievement not found: {achievement_id}")
                return None

            # Check if already unlocked
            existing = (
                self.db.query(UserAchievement)
                .filter(
                    and_(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == achievement.id,
                    )
                )
                .first()
            )

            if existing:
                logger.debug(
                    f"Achievement {achievement_id} already unlocked for user {user_id}"
                )
                return None

            # Create user achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                unlocked_at=datetime.now(UTC),
                progress=100,
                metadata=metadata or {},
            )

            self.db.add(user_achievement)
            self.db.commit()
            self.db.refresh(user_achievement)

            logger.info(
                f"Unlocked achievement {achievement_id} for user {user_id}, awarded {achievement.xp_reward} XP"
            )

            return user_achievement

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unlocking achievement: {e}")
            raise

    # =====================================================================
    # EVENT-DRIVEN ACHIEVEMENT CHECKING
    # =====================================================================

    async def check_achievements(
        self, user_id: int, event_type: str, event_data: Optional[Dict[str, Any]] = None
    ) -> List[UserAchievement]:
        """
        Check and unlock achievements based on user events.

        Args:
            user_id: User ID
            event_type: Event type (e.g., "scenario_completed", "streak_updated")
            event_data: Additional event context

        Returns:
            List of newly unlocked achievements
        """
        try:
            newly_unlocked = []
            event_data = event_data or {}

            # Get all active achievements
            achievements = (
                self.db.query(Achievement).filter(Achievement.is_active == True).all()
            )

            for achievement in achievements:
                criteria = achievement.criteria
                criteria_type = criteria.get("type")

                # Check if this achievement is relevant to the event
                should_check = self._should_check_achievement(event_type, criteria_type)

                if not should_check:
                    continue

                # Check if criteria met
                is_met = await self._check_criteria(user_id, criteria, event_data)

                if is_met:
                    # Attempt to unlock
                    user_achievement = await self.unlock_achievement(
                        user_id=user_id,
                        achievement_id=achievement.achievement_id,
                        metadata={"unlocked_via": event_type, "event_data": event_data},
                    )

                    if user_achievement:
                        newly_unlocked.append(user_achievement)

            return newly_unlocked

        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []

    def _should_check_achievement(self, event_type: str, criteria_type: str) -> bool:
        """Determine if achievement should be checked based on event"""
        event_to_criteria_mapping = {
            "scenario_completed": [
                "scenario_completions",
                "category_completions",
                "difficulty_completions",
                "perfect_rating",
                "perfect_rating_streak",
                "high_cultural_accuracy",
                "fast_completion",
            ],
            "streak_updated": ["current_streak"],
            "streak_freeze_used": ["streak_freeze_used"],
            "rating_given": ["ratings_given"],
            "collection_created": ["collections_created"],
            "bookmark_created": ["bookmarks_created"],
            "scenario_shared": ["scenarios_shared"],
            "vocabulary_learned": ["words_learned"],
        }

        return criteria_type in event_to_criteria_mapping.get(event_type, [])

    async def _check_criteria(
        self, user_id: int, criteria: Dict[str, Any], event_data: Dict[str, Any]
    ) -> bool:
        """Check if achievement criteria is met"""
        criteria_type = criteria.get("type")

        # COMPLETION CRITERIA
        if criteria_type == "scenario_completions":
            return await self._check_scenario_completions(user_id, criteria)

        elif criteria_type == "category_completions":
            return await self._check_category_completions(user_id, criteria)

        elif criteria_type == "difficulty_completions":
            return await self._check_difficulty_completions(user_id, criteria)

        # STREAK CRITERIA
        elif criteria_type == "current_streak":
            return await self._check_current_streak(user_id, criteria)

        elif criteria_type == "streak_freeze_used":
            return await self._check_streak_freeze_used(user_id, criteria)

        # QUALITY CRITERIA
        elif criteria_type == "perfect_rating":
            return await self._check_perfect_rating(user_id, criteria)

        elif criteria_type == "perfect_rating_streak":
            return await self._check_perfect_rating_streak(user_id, criteria)

        elif criteria_type == "high_cultural_accuracy":
            return await self._check_high_cultural_accuracy(user_id, criteria)

        elif criteria_type == "fast_completion":
            return await self._check_fast_completion(user_id, criteria, event_data)

        # ENGAGEMENT CRITERIA
        elif criteria_type == "ratings_given":
            return await self._check_ratings_given(user_id, criteria)

        elif criteria_type == "collections_created":
            return await self._check_collections_created(user_id, criteria)

        elif criteria_type == "bookmarks_created":
            return await self._check_bookmarks_created(user_id, criteria)

        elif criteria_type == "scenarios_shared":
            return await self._check_scenarios_shared(user_id, criteria)

        # LEARNING CRITERIA
        elif criteria_type == "words_learned":
            return await self._check_words_learned(user_id, criteria)

        elif criteria_type == "languages_practiced":
            return await self._check_languages_practiced(user_id, criteria)

        else:
            logger.warning(f"Unknown criteria type: {criteria_type}")
            return False

    # =====================================================================
    # CRITERIA CHECKERS - COMPLETION
    # =====================================================================

    async def _check_scenario_completions(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has completed N scenarios"""
        required_count = criteria.get("count", 0)

        # TODO: Implement when ScenarioCompletion model is available
        # For now, return False (achievements will unlock when completion tracking is added)
        return False

    async def _check_category_completions(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has completed all scenarios in a category"""
        category = criteria.get("category")
        percentage = criteria.get("percentage", 100)

        # This would require scenario data - simplified for now
        # In production, compare completed scenarios in category vs total scenarios in category
        # For now, return False (will be implemented when scenario categorization is ready)
        return False

    async def _check_difficulty_completions(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has completed all scenarios of a difficulty level"""
        difficulty = criteria.get("difficulty")
        percentage = criteria.get("percentage", 100)

        # Similar to category completions - requires scenario difficulty data
        return False

    # =====================================================================
    # CRITERIA CHECKERS - STREAK
    # =====================================================================

    async def _check_current_streak(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has achieved a streak milestone"""
        from app.models.gamification_models import UserStreak

        required_days = criteria.get("days", 0)

        streak = self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()

        if not streak:
            return False

        return streak.current_streak >= required_days

    async def _check_streak_freeze_used(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has used streak freezes"""
        from app.models.gamification_models import UserStreak

        required_count = criteria.get("count", 1)

        streak = self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()

        if not streak:
            return False

        return streak.total_freezes_used >= required_count

    # =====================================================================
    # CRITERIA CHECKERS - QUALITY
    # =====================================================================

    async def _check_perfect_rating(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has achieved perfect ratings"""
        required_count = criteria.get("count", 1)

        count = (
            self.db.query(func.count(ScenarioRating.id))
            .filter(
                and_(
                    ScenarioRating.user_id == user_id,
                    ScenarioRating.rating == 5,
                )
            )
            .scalar()
        )

        return (count or 0) >= required_count

    async def _check_perfect_rating_streak(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has consecutive perfect ratings"""
        required_count = criteria.get("count", 5)

        # Get last N ratings
        recent_ratings = (
            self.db.query(ScenarioRating)
            .filter(ScenarioRating.user_id == user_id)
            .order_by(ScenarioRating.created_at.desc())
            .limit(required_count)
            .all()
        )

        if len(recent_ratings) < required_count:
            return False

        return all(rating.rating == 5 for rating in recent_ratings)

    async def _check_high_cultural_accuracy(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has high cultural accuracy ratings"""
        threshold = criteria.get("threshold", 90)
        required_count = criteria.get("count", 10)

        count = (
            self.db.query(func.count(ScenarioRating.id))
            .filter(
                and_(
                    ScenarioRating.user_id == user_id,
                    ScenarioRating.cultural_accuracy_rating
                    >= (threshold / 10),  # Assuming 1-10 scale
                )
            )
            .scalar()
        )

        return (count or 0) >= required_count

    async def _check_fast_completion(
        self, user_id: int, criteria: Dict, event_data: Dict
    ) -> bool:
        """Check if scenario was completed faster than estimated"""
        speed_multiplier = criteria.get("speed_multiplier", 0.5)

        # Get completion time from event data
        actual_time = event_data.get("completion_time")
        estimated_time = event_data.get("estimated_time")

        if not actual_time or not estimated_time:
            return False

        return actual_time <= (estimated_time * speed_multiplier)

    # =====================================================================
    # CRITERIA CHECKERS - ENGAGEMENT
    # =====================================================================

    async def _check_ratings_given(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has given N ratings"""
        required_count = criteria.get("count", 10)

        count = (
            self.db.query(func.count(ScenarioRating.id))
            .filter(ScenarioRating.user_id == user_id)
            .scalar()
        )

        return (count or 0) >= required_count

    async def _check_collections_created(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has created N collections"""
        required_count = criteria.get("count", 5)

        count = (
            self.db.query(func.count(ScenarioCollection.id))
            .filter(ScenarioCollection.created_by == user_id)
            .scalar()
        )

        return (count or 0) >= required_count

    async def _check_bookmarks_created(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has bookmarked N scenarios"""
        required_count = criteria.get("count", 20)

        count = (
            self.db.query(func.count(ScenarioBookmark.id))
            .filter(ScenarioBookmark.user_id == user_id)
            .scalar()
        )

        return (count or 0) >= required_count

    async def _check_scenarios_shared(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has shared N scenarios"""
        required_count = criteria.get("count", 10)

        # Would require scenario sharing tracking table
        # For now, return False (to be implemented)
        return False

    # =====================================================================
    # CRITERIA CHECKERS - LEARNING
    # =====================================================================

    async def _check_words_learned(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has learned N words"""
        required_count = criteria.get("count", 100)

        # Would require vocabulary tracking table
        # For now, return False (to be implemented)
        return False

    async def _check_languages_practiced(self, user_id: int, criteria: Dict) -> bool:
        """Check if user has practiced in N languages"""
        required_count = criteria.get("count", 3)

        # Would require tracking scenarios by language
        # For now, return False (to be implemented)
        return False

    # =====================================================================
    # ACHIEVEMENT QUERIES
    # =====================================================================

    async def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Get all achievements unlocked by user"""
        try:
            achievements = (
                self.db.query(UserAchievement)
                .filter(UserAchievement.user_id == user_id)
                .order_by(UserAchievement.unlocked_at.desc())
                .all()
            )

            return achievements

        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return []

    async def get_achievement_progress(
        self, user_id: int, achievement_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get progress towards a specific achievement"""
        try:
            achievement = (
                self.db.query(Achievement)
                .filter(Achievement.achievement_id == achievement_id)
                .first()
            )

            if not achievement:
                return None

            # Check if already unlocked
            user_achievement = (
                self.db.query(UserAchievement)
                .filter(
                    and_(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == achievement.id,
                    )
                )
                .first()
            )

            if user_achievement:
                return {
                    "achievement": achievement.to_dict(),
                    "unlocked": True,
                    "progress": 100,
                    "unlocked_at": user_achievement.unlocked_at.isoformat(),
                }

            # Calculate progress
            criteria = achievement.criteria
            progress = await self._calculate_progress(user_id, criteria)

            return {
                "achievement": achievement.to_dict(),
                "unlocked": False,
                "progress": progress,
                "unlocked_at": None,
            }

        except Exception as e:
            logger.error(f"Error getting achievement progress: {e}")
            return None

    async def _calculate_progress(self, user_id: int, criteria: Dict) -> int:
        """Calculate progress percentage towards achievement (0-100)"""
        criteria_type = criteria.get("type")

        # For count-based achievements
        if criteria_type in [
            "scenario_completions",
            "ratings_given",
            "collections_created",
            "bookmarks_created",
        ]:
            required = criteria.get("count", 1)

            if criteria_type == "scenario_completions":
                # TODO: Implement when ScenarioCompletion model is available
                current = 0
            elif criteria_type == "ratings_given":
                current = (
                    self.db.query(func.count(ScenarioRating.id))
                    .filter(ScenarioRating.user_id == user_id)
                    .scalar()
                    or 0
                )
            elif criteria_type == "collections_created":
                current = (
                    self.db.query(func.count(ScenarioCollection.id))
                    .filter(ScenarioCollection.created_by == user_id)
                    .scalar()
                    or 0
                )
            elif criteria_type == "bookmarks_created":
                current = (
                    self.db.query(func.count(ScenarioBookmark.id))
                    .filter(ScenarioBookmark.user_id == user_id)
                    .scalar()
                    or 0
                )
            else:
                current = 0

            progress = min(100, int((current / required) * 100))
            return progress

        # For streak-based achievements
        elif criteria_type == "current_streak":
            from app.models.gamification_models import UserStreak

            required = criteria.get("days", 1)
            streak = (
                self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            )
            current = streak.current_streak if streak else 0

            progress = min(100, int((current / required) * 100))
            return progress

        # Default: no progress
        return 0

    async def get_all_achievements(self) -> List[Achievement]:
        """Get all achievement definitions"""
        try:
            return (
                self.db.query(Achievement).filter(Achievement.is_active == True).all()
            )
        except Exception as e:
            logger.error(f"Error getting all achievements: {e}")
            return []
