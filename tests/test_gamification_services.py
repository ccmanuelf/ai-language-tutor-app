"""
Comprehensive tests for all gamification services.

Tests the actual implemented methods in:
- AchievementService
- StreakService
- XPService
- LeaderboardService
"""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.database import User
from app.models.gamification_models import (
    Achievement,
    AchievementCategory,
    LeaderboardMetric,
    UserAchievement,
    UserStreak,
    UserXP,
)
from app.services.achievement_service import AchievementService
from app.services.leaderboard_service import LeaderboardService
from app.services.streak_service import StreakService
from app.services.xp_service import XPService


@pytest.fixture
def test_user(db_session: Session):
    """Create test user"""
    user = User(
        user_id="test_user_gamification",
        username="test_user",
        email="test@gamification.com",
        password_hash="hashed_pass",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# ACHIEVEMENT SERVICE TESTS
# ============================================================================


class TestAchievementService:
    """Test AchievementService public methods"""

    @pytest.mark.asyncio
    async def test_initialize_achievements(self, db_session: Session):
        """Should initialize all 27 achievements"""
        service = AchievementService(db_session)
        count = await service.initialize_achievements()

        assert count == 27

        # Verify in database
        achievements = db_session.query(Achievement).all()
        assert len(achievements) == 27

        # Check all categories present
        categories = {a.category for a in achievements}
        assert AchievementCategory.COMPLETION.value in categories
        assert AchievementCategory.STREAK.value in categories
        assert AchievementCategory.QUALITY.value in categories

    @pytest.mark.asyncio
    async def test_unlock_achievement(self, db_session: Session, test_user: User):
        """Should unlock achievement for user"""
        service = AchievementService(db_session)
        await service.initialize_achievements()

        user_achievement = await service.unlock_achievement(
            user_id=test_user.id,
            achievement_id="first_steps",
            metadata={"test": "data"},
        )

        assert user_achievement is not None
        assert user_achievement.user_id == test_user.id
        assert user_achievement.progress == 100

        # Verify in database
        db_achievement = (
            db_session.query(UserAchievement).filter_by(user_id=test_user.id).first()
        )

        assert db_achievement is not None

    @pytest.mark.asyncio
    async def test_get_user_achievements(self, db_session: Session, test_user: User):
        """Should return user's achievements"""
        service = AchievementService(db_session)
        await service.initialize_achievements()

        # Unlock one achievement
        await service.unlock_achievement(test_user.id, "first_steps")

        # Get achievements
        achievements = await service.get_user_achievements(test_user.id)

        assert len(achievements) >= 1
        assert any(a.achievement.achievement_id == "first_steps" for a in achievements)

    @pytest.mark.asyncio
    async def test_get_all_achievements(self, db_session: Session):
        """Should return all achievement definitions"""
        service = AchievementService(db_session)
        await service.initialize_achievements()

        achievements = await service.get_all_achievements()

        assert len(achievements) == 27


# ============================================================================
# STREAK SERVICE TESTS
# ============================================================================


class TestStreakService:
    """Test StreakService public methods"""

    @pytest.mark.asyncio
    async def test_initialize_user_streak(self, db_session: Session, test_user: User):
        """Should initialize streak for new user"""
        service = StreakService(db_session)

        streak = await service.initialize_user_streak(test_user.id)

        assert streak.user_id == test_user.id
        assert streak.current_streak == 0
        assert streak.streak_freezes_available == 0  # Starting amount

    @pytest.mark.asyncio
    async def test_update_user_streak(self, db_session: Session, test_user: User):
        """Should update daily streak"""
        service = StreakService(db_session)
        await service.initialize_user_streak(test_user.id)

        result = await service.update_user_streak(test_user.id)

        assert "action" in result
        assert result["current_streak"] >= 1

    @pytest.mark.asyncio
    async def test_get_streak_status(self, db_session: Session, test_user: User):
        """Should get current streak status"""
        service = StreakService(db_session)
        await service.initialize_user_streak(test_user.id)
        await service.update_user_streak(test_user.id)

        status = await service.get_streak_status(test_user.id)

        assert "current_streak" in status
        assert "longest_streak" in status
        assert "streak_freezes_available" in status


# ============================================================================
# XP SERVICE TESTS
# ============================================================================


class TestXPService:
    """Test XPService public methods"""

    @pytest.mark.asyncio
    async def test_initialize_user_xp(self, db_session: Session, test_user: User):
        """Should initialize XP for new user"""
        service = XPService(db_session)

        user_xp = await service.initialize_user_xp(test_user.id)

        assert user_xp.user_id == test_user.id
        assert user_xp.total_xp == 0
        assert user_xp.current_level == 1

    @pytest.mark.asyncio
    async def test_award_xp(self, db_session: Session, test_user: User):
        """Should award XP to user"""
        service = XPService(db_session)
        await service.initialize_user_xp(test_user.id)

        result = await service.award_xp(
            user_id=test_user.id,
            xp_amount=100,
            reason="test_award",
            metadata={"test": "data"},
        )

        assert result["success"] is True
        assert result["xp_awarded"] == 100
        assert result["total_xp"] == 100
        assert "current_level" in result
        assert "level_up" in result

    @pytest.mark.asyncio
    async def test_get_user_level(self, db_session: Session, test_user: User):
        """Should get user level information"""
        service = XPService(db_session)
        await service.initialize_user_xp(test_user.id)
        await service.award_xp(test_user.id, 500, "test")

        level_info = await service.get_user_level(test_user.id)

        assert "current_level" in level_info
        assert "total_xp" in level_info
        assert level_info["total_xp"] == 500


# ============================================================================
# LEADERBOARD SERVICE TESTS
# ============================================================================


class TestLeaderboardService:
    """Test LeaderboardService public methods"""

    @pytest.mark.asyncio
    async def test_get_global_leaderboard_empty(self, db_session: Session):
        """Should return empty leaderboard when no users"""
        service = LeaderboardService(db_session)

        leaderboard = await service.get_global_leaderboard(
            metric=LeaderboardMetric.XP_ALL_TIME.value, limit=10
        )

        assert isinstance(leaderboard, list)
        assert len(leaderboard) == 0

    @pytest.mark.asyncio
    async def test_get_global_leaderboard_with_users(self, db_session: Session):
        """Should return ranked users"""
        # Create multiple users with XP
        xp_service = XPService(db_session)

        for i in range(3):
            user = User(
                user_id=f"test_user_{i}",
                username=f"user_{i}",
                email=f"user{i}@test.com",
                password_hash="hash",
                is_active=True,
            )
            db_session.add(user)
        db_session.commit()

        # Award different XP amounts
        users = db_session.query(User).all()
        for i, user in enumerate(users):
            await xp_service.initialize_user_xp(user.id)
            await xp_service.award_xp(user.id, (i + 1) * 100, "test")

        # Get leaderboard
        service = LeaderboardService(db_session)
        leaderboard = await service.get_global_leaderboard(
            metric=LeaderboardMetric.XP_ALL_TIME.value, limit=10
        )

        assert len(leaderboard) == 3
        # Should be sorted by XP descending
        assert leaderboard[0]["score"] > leaderboard[-1]["score"]
        assert leaderboard[0]["rank"] == 1
        assert "username" in leaderboard[0]
        assert "level" in leaderboard[0]

    @pytest.mark.asyncio
    async def test_get_user_rank(self, db_session: Session, test_user: User):
        """Should get user's rank in leaderboard"""
        service = LeaderboardService(db_session)
        xp_service = XPService(db_session)

        await xp_service.initialize_user_xp(test_user.id)
        await xp_service.award_xp(test_user.id, 200, "test")

        rank_info = await service.get_user_rank(
            user_id=test_user.id, metric=LeaderboardMetric.XP_ALL_TIME.value
        )

        assert "rank" in rank_info
        assert rank_info["rank"] == 1  # Only user


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestGamificationIntegration:
    """Test integration between services"""

    @pytest.mark.asyncio
    async def test_complete_user_flow(self, db_session: Session, test_user: User):
        """Test complete gamification flow for a user"""
        # Initialize all services
        achievement_service = AchievementService(db_session)
        streak_service = StreakService(db_session)
        xp_service = XPService(db_session)
        leaderboard_service = LeaderboardService(db_session)

        # Initialize achievements
        await achievement_service.initialize_achievements()

        # Initialize user gamification data
        await streak_service.initialize_user_streak(test_user.id)
        await xp_service.initialize_user_xp(test_user.id)

        # Award XP
        xp_result = await xp_service.award_xp(test_user.id, 150, "scenario_completed")
        assert xp_result["success"] is True

        # Update streak
        streak_result = await streak_service.update_user_streak(test_user.id)
        assert streak_result["action"] in [
            "started",
            "maintained",
            "increased",
            "broken",
        ]

        # Unlock achievement
        achievement_result = await achievement_service.unlock_achievement(
            test_user.id, "first_steps"
        )
        assert achievement_result is not None
        assert achievement_result.user_id == test_user.id

        # Check leaderboard
        rank_info = await leaderboard_service.get_user_rank(
            test_user.id, LeaderboardMetric.XP_ALL_TIME.value
        )
        assert rank_info["rank"] == 1

        # Verify all data is consistent
        level_info = await xp_service.get_user_level(test_user.id)
        assert level_info["total_xp"] == 150

        streak_status = await streak_service.get_streak_status(test_user.id)
        assert streak_status["current_streak"] >= 1

        user_achievements = await achievement_service.get_user_achievements(
            test_user.id
        )
        assert len(user_achievements) >= 1
