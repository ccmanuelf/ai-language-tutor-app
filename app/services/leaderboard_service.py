"""
Leaderboard Service for AI Language Tutor App

This service manages leaderboard rankings, caching, and historical snapshots.
Handles global and category-specific leaderboards with performance optimization.
"""

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.database import User
from app.models.gamification_models import (
    LeaderboardCache,
    LeaderboardMetric,
    LeaderboardSnapshot,
    UserStreak,
    UserXP,
)

# Note: ScenarioCompletion model will be added in future update

logger = logging.getLogger(__name__)


class LeaderboardService:
    """Service for managing leaderboards"""

    # Cache TTL in minutes
    CACHE_TTL_MINUTES = 5

    def __init__(self, db: Session):
        self.db = db

    # =====================================================================
    # LEADERBOARD GENERATION
    # =====================================================================

    async def get_global_leaderboard(
        self,
        metric: str = LeaderboardMetric.XP_ALL_TIME.value,
        limit: int = 100,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get global leaderboard for a specific metric.

        Args:
            metric: Metric to rank by (xp_all_time, streak_current, etc.)
            limit: Number of results to return
            use_cache: Whether to use cached results

        Returns:
            List of ranked users
        """
        try:
            # Check if cache is fresh
            if use_cache:
                cached = await self._get_cached_leaderboard(metric, limit)
                if cached:
                    return cached

            # Generate fresh leaderboard
            leaderboard = await self._generate_leaderboard(metric, limit)

            # Update cache
            await self._update_leaderboard_cache(metric, leaderboard)

            return leaderboard

        except Exception as e:
            logger.error(f"Error getting global leaderboard: {e}")
            return []

    async def _generate_leaderboard(
        self, metric: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate leaderboard from source data"""

        if metric == LeaderboardMetric.XP_ALL_TIME.value:
            return await self._generate_xp_all_time_leaderboard(limit)

        elif metric == LeaderboardMetric.XP_WEEKLY.value:
            return await self._generate_xp_weekly_leaderboard(limit)

        elif metric == LeaderboardMetric.XP_MONTHLY.value:
            return await self._generate_xp_monthly_leaderboard(limit)

        elif metric == LeaderboardMetric.STREAK_CURRENT.value:
            return await self._generate_streak_current_leaderboard(limit)

        elif metric == LeaderboardMetric.STREAK_LONGEST.value:
            return await self._generate_streak_longest_leaderboard(limit)

        elif metric == LeaderboardMetric.SCENARIOS_COMPLETED.value:
            return await self._generate_scenarios_completed_leaderboard(limit)

        elif metric == LeaderboardMetric.ACHIEVEMENTS_UNLOCKED.value:
            return await self._generate_achievements_unlocked_leaderboard(limit)

        else:
            logger.warning(f"Unknown leaderboard metric: {metric}")
            return []

    async def _generate_xp_all_time_leaderboard(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate all-time XP leaderboard"""
        rankings = (
            self.db.query(UserXP, User)
            .join(User, UserXP.user_id == User.id)
            .order_by(desc(UserXP.total_xp))
            .limit(limit)
            .all()
        )

        return [
            {
                "rank": idx + 1,
                "user_id": user_xp.user_id,
                "username": user.username,
                "score": user_xp.total_xp,
                "level": user_xp.current_level,
                "title": user_xp.title,
                "metric": "total_xp",
            }
            for idx, (user_xp, user) in enumerate(rankings)
        ]

    async def _generate_xp_weekly_leaderboard(self, limit: int) -> List[Dict[str, Any]]:
        """Generate weekly XP leaderboard"""
        from app.models.gamification_models import XPTransaction

        week_ago = datetime.now(UTC) - timedelta(days=7)

        weekly_xp = (
            self.db.query(
                XPTransaction.user_id,
                func.sum(XPTransaction.xp_amount).label("weekly_xp"),
            )
            .filter(XPTransaction.created_at >= week_ago)
            .group_by(XPTransaction.user_id)
            .subquery()
        )

        rankings = (
            self.db.query(weekly_xp.c.user_id, weekly_xp.c.weekly_xp, User)
            .join(User, weekly_xp.c.user_id == User.id)
            .order_by(desc(weekly_xp.c.weekly_xp))
            .limit(limit)
            .all()
        )

        return [
            {
                "rank": idx + 1,
                "user_id": user_id,
                "username": user.username,
                "score": weekly_xp or 0,
                "metric": "weekly_xp",
            }
            for idx, (user_id, weekly_xp, user) in enumerate(rankings)
        ]

    async def _generate_xp_monthly_leaderboard(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate monthly XP leaderboard"""
        from app.models.gamification_models import XPTransaction

        month_ago = datetime.now(UTC) - timedelta(days=30)

        monthly_xp = (
            self.db.query(
                XPTransaction.user_id,
                func.sum(XPTransaction.xp_amount).label("monthly_xp"),
            )
            .filter(XPTransaction.created_at >= month_ago)
            .group_by(XPTransaction.user_id)
            .subquery()
        )

        rankings = (
            self.db.query(monthly_xp.c.user_id, monthly_xp.c.monthly_xp, User)
            .join(User, monthly_xp.c.user_id == User.id)
            .order_by(desc(monthly_xp.c.monthly_xp))
            .limit(limit)
            .all()
        )

        return [
            {
                "rank": idx + 1,
                "user_id": user_id,
                "username": user.username,
                "score": monthly_xp or 0,
                "metric": "monthly_xp",
            }
            for idx, (user_id, monthly_xp, user) in enumerate(rankings)
        ]

    async def _generate_streak_current_leaderboard(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate current streak leaderboard"""
        rankings = (
            self.db.query(UserStreak, User)
            .join(User, UserStreak.user_id == User.id)
            .order_by(desc(UserStreak.current_streak))
            .limit(limit)
            .all()
        )

        return [
            {
                "rank": idx + 1,
                "user_id": streak.user_id,
                "username": user.username,
                "score": streak.current_streak,
                "metric": "current_streak",
            }
            for idx, (streak, user) in enumerate(rankings)
        ]

    async def _generate_streak_longest_leaderboard(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate longest streak leaderboard"""
        rankings = (
            self.db.query(UserStreak, User)
            .join(User, UserStreak.user_id == User.id)
            .order_by(desc(UserStreak.longest_streak))
            .limit(limit)
            .all()
        )

        return [
            {
                "rank": idx + 1,
                "user_id": streak.user_id,
                "username": user.username,
                "score": streak.longest_streak,
                "metric": "longest_streak",
            }
            for idx, (streak, user) in enumerate(rankings)
        ]

    async def _generate_scenarios_completed_leaderboard(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate scenarios completed leaderboard"""
        # TODO: Implement when ScenarioCompletion model is available
        # For now, return empty list
        return []

    async def _generate_achievements_unlocked_leaderboard(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate achievements unlocked leaderboard"""
        from app.models.gamification_models import (
            UserAchievement as GamificationUserAchievement,
        )

        achievements = (
            self.db.query(
                GamificationUserAchievement.user_id,
                func.count(GamificationUserAchievement.id).label("achievement_count"),
            )
            .group_by(GamificationUserAchievement.user_id)
            .subquery()
        )

        rankings = (
            self.db.query(
                achievements.c.user_id, achievements.c.achievement_count, User
            )
            .join(User, achievements.c.user_id == User.id)
            .order_by(desc(achievements.c.achievement_count))
            .limit(limit)
            .all()
        )

        return [
            {
                "rank": idx + 1,
                "user_id": user_id,
                "username": user.username,
                "score": achievement_count or 0,
                "metric": "achievements_unlocked",
            }
            for idx, (user_id, achievement_count, user) in enumerate(rankings)
        ]

    # =====================================================================
    # LEADERBOARD CACHING
    # =====================================================================

    async def _get_cached_leaderboard(
        self, metric: str, limit: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached leaderboard if fresh"""
        try:
            cutoff_time = datetime.now(UTC) - timedelta(minutes=self.CACHE_TTL_MINUTES)

            cached_entries = (
                self.db.query(LeaderboardCache, User)
                .join(User, LeaderboardCache.user_id == User.id)
                .filter(
                    and_(
                        LeaderboardCache.metric == metric,
                        LeaderboardCache.cached_at >= cutoff_time,
                    )
                )
                .order_by(LeaderboardCache.rank)
                .limit(limit)
                .all()
            )

            if not cached_entries:
                return None

            return [
                {
                    "rank": entry.rank,
                    "user_id": entry.user_id,
                    "username": user.username,
                    "score": entry.score,
                    "rank_change": entry.rank_change,
                    "metric": entry.metric,
                }
                for entry, user in cached_entries
            ]

        except Exception as e:
            logger.error(f"Error getting cached leaderboard: {e}")
            return None

    async def _update_leaderboard_cache(
        self, metric: str, leaderboard: List[Dict[str, Any]]
    ):
        """Update leaderboard cache"""
        try:
            # Get total users for percentile calculation
            total_users = self.db.query(func.count(User.id)).scalar() or 1

            for entry in leaderboard:
                # Get previous rank
                existing = (
                    self.db.query(LeaderboardCache)
                    .filter(
                        and_(
                            LeaderboardCache.user_id == entry["user_id"],
                            LeaderboardCache.metric == metric,
                        )
                    )
                    .first()
                )

                previous_rank = existing.rank if existing else None
                rank_change = 0

                if previous_rank:
                    rank_change = previous_rank - entry["rank"]  # Positive = moved up

                # Calculate percentile
                percentile = (entry["rank"] / total_users) * 100

                # Update or create cache entry
                if existing:
                    existing.score = entry["score"]
                    existing.rank = entry["rank"]
                    existing.previous_rank = previous_rank
                    existing.rank_change = rank_change
                    existing.percentile = percentile
                    existing.cached_at = datetime.now(UTC)
                else:
                    cache_entry = LeaderboardCache(
                        user_id=entry["user_id"],
                        metric=metric,
                        score=entry["score"],
                        rank=entry["rank"],
                        previous_rank=None,
                        rank_change=0,
                        percentile=percentile,
                        cached_at=datetime.now(UTC),
                    )
                    self.db.add(cache_entry)

            self.db.commit()
            logger.info(
                f"Updated leaderboard cache for metric: {metric}, entries: {len(leaderboard)}"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating leaderboard cache: {e}")

    # =====================================================================
    # USER RANK QUERIES
    # =====================================================================

    async def get_user_rank(
        self, user_id: int, metric: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's rank for a specific metric.

        Args:
            user_id: User ID
            metric: Metric to check

        Returns:
            Dict with user's rank information
        """
        try:
            # Try cache first
            cached = (
                self.db.query(LeaderboardCache)
                .filter(
                    and_(
                        LeaderboardCache.user_id == user_id,
                        LeaderboardCache.metric == metric,
                    )
                )
                .first()
            )

            if cached and cached.cached_at >= (
                datetime.now(UTC) - timedelta(minutes=self.CACHE_TTL_MINUTES)
            ):
                return {
                    "user_id": user_id,
                    "metric": metric,
                    "rank": cached.rank,
                    "score": cached.score,
                    "previous_rank": cached.previous_rank,
                    "rank_change": cached.rank_change,
                    "percentile": round(cached.percentile, 2)
                    if cached.percentile
                    else None,
                }

            # Generate fresh ranking
            leaderboard = await self._generate_leaderboard(metric, limit=10000)

            # Find user in leaderboard
            for entry in leaderboard:
                if entry["user_id"] == user_id:
                    total_users = len(leaderboard)
                    percentile = (entry["rank"] / total_users) * 100

                    return {
                        "user_id": user_id,
                        "metric": metric,
                        "rank": entry["rank"],
                        "score": entry["score"],
                        "previous_rank": cached.previous_rank if cached else None,
                        "rank_change": cached.rank_change if cached else 0,
                        "percentile": round(percentile, 2),
                    }

            # User not in leaderboard
            return None

        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return None

    # =====================================================================
    # LEADERBOARD SNAPSHOTS
    # =====================================================================

    async def create_leaderboard_snapshot(
        self, metric: str, period: str = "daily"
    ) -> Optional[LeaderboardSnapshot]:
        """
        Create a historical snapshot of the leaderboard.

        Args:
            metric: Metric to snapshot
            period: daily, weekly, or monthly

        Returns:
            LeaderboardSnapshot if created
        """
        try:
            today = date.today()

            # Check if snapshot already exists
            existing = (
                self.db.query(LeaderboardSnapshot)
                .filter(
                    and_(
                        LeaderboardSnapshot.metric == metric,
                        LeaderboardSnapshot.period == period,
                        LeaderboardSnapshot.snapshot_date == today,
                    )
                )
                .first()
            )

            if existing:
                logger.info(f"Snapshot already exists for {metric} {period} {today}")
                return existing

            # Generate leaderboard
            leaderboard = await self._generate_leaderboard(metric, limit=100)

            # Create snapshot
            snapshot = LeaderboardSnapshot(
                metric=metric,
                period=period,
                snapshot_date=today,
                data={"top_100": leaderboard},
            )

            self.db.add(snapshot)
            self.db.commit()

            logger.info(f"Created leaderboard snapshot for {metric} {period} {today}")
            return snapshot

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating leaderboard snapshot: {e}")
            return None

    async def get_historical_leaderboard(
        self, metric: str, period: str, snapshot_date: date
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical leaderboard snapshot.

        Args:
            metric: Metric
            period: daily, weekly, or monthly
            snapshot_date: Date of snapshot

        Returns:
            Historical leaderboard data
        """
        try:
            snapshot = (
                self.db.query(LeaderboardSnapshot)
                .filter(
                    and_(
                        LeaderboardSnapshot.metric == metric,
                        LeaderboardSnapshot.period == period,
                        LeaderboardSnapshot.snapshot_date == snapshot_date,
                    )
                )
                .first()
            )

            if not snapshot:
                return None

            return snapshot.data.get("top_100", [])

        except Exception as e:
            logger.error(f"Error getting historical leaderboard: {e}")
            return None

    # =====================================================================
    # UTILITY METHODS
    # =====================================================================

    async def refresh_all_leaderboards(self):
        """Refresh all leaderboard caches (for scheduled tasks)"""
        try:
            metrics = [
                LeaderboardMetric.XP_ALL_TIME.value,
                LeaderboardMetric.XP_WEEKLY.value,
                LeaderboardMetric.XP_MONTHLY.value,
                LeaderboardMetric.STREAK_CURRENT.value,
                LeaderboardMetric.STREAK_LONGEST.value,
                LeaderboardMetric.SCENARIOS_COMPLETED.value,
                LeaderboardMetric.ACHIEVEMENTS_UNLOCKED.value,
            ]

            for metric in metrics:
                await self.get_global_leaderboard(metric=metric, use_cache=False)

            logger.info("Refreshed all leaderboard caches")

        except Exception as e:
            logger.error(f"Error refreshing leaderboards: {e}")
