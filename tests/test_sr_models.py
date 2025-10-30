"""
Comprehensive tests for sr_models.py (Spaced Repetition Models)

Tests all dataclass models, enums, and __post_init__ methods to achieve 100% coverage.
"""

from datetime import datetime, timedelta

import pytest

from app.services.sr_models import (
    AchievementType,
    ItemType,
    LearningGoal,
    LearningSession,
    ReviewResult,
    SessionType,
    SpacedRepetitionItem,
)


class TestSREnums:
    """Test all spaced repetition enum definitions"""

    def test_item_type_enum(self):
        """Test ItemType enum has all expected values"""
        assert ItemType.VOCABULARY.value == "vocabulary"
        assert ItemType.PHRASE.value == "phrase"
        assert ItemType.GRAMMAR.value == "grammar"
        assert ItemType.PRONUNCIATION.value == "pronunciation"

    def test_session_type_enum(self):
        """Test SessionType enum has all expected values"""
        assert SessionType.VOCABULARY.value == "vocabulary"
        assert SessionType.CONVERSATION.value == "conversation"
        assert SessionType.TUTOR_MODE.value == "tutor_mode"
        assert SessionType.SCENARIO.value == "scenario"
        assert SessionType.CONTENT_REVIEW.value == "content_review"

    def test_review_result_enum(self):
        """Test ReviewResult enum has all SM-2 algorithm grades"""
        assert ReviewResult.AGAIN.value == 0
        assert ReviewResult.HARD.value == 1
        assert ReviewResult.GOOD.value == 2
        assert ReviewResult.EASY.value == 3

    def test_achievement_type_enum(self):
        """Test AchievementType enum has all gamification types"""
        assert AchievementType.STREAK.value == "streak"
        assert AchievementType.VOCABULARY.value == "vocabulary"
        assert AchievementType.CONVERSATION.value == "conversation"
        assert AchievementType.GOAL.value == "goal"
        assert AchievementType.MASTERY.value == "mastery"
        assert AchievementType.DEDICATION.value == "dedication"


class TestSpacedRepetitionItem:
    """Test SpacedRepetitionItem dataclass"""

    def test_spaced_repetition_item_with_all_fields(self):
        """Test SpacedRepetitionItem creation with all fields provided"""
        now = datetime.now()
        item = SpacedRepetitionItem(
            item_id="item_001",
            user_id=123,
            language_code="es",
            item_type="vocabulary",
            content="hola",
            translation="hello",
            definition="Spanish greeting",
            pronunciation_guide="OH-lah",
            example_usage="Hola, ¿cómo estás?",
            context_tags=["greeting", "basic"],
            difficulty_level=1,
            ease_factor=2.5,
            repetition_number=3,
            interval_days=7,
            last_review_date=now,
            next_review_date=now + timedelta(days=7),
            total_reviews=5,
            correct_reviews=4,
            incorrect_reviews=1,
            streak_count=3,
            mastery_level=0.8,
            confidence_score=0.85,
            first_seen_date=now,
            last_studied_date=now,
            average_response_time_ms=1500,
            learning_speed_factor=1.2,
            retention_rate=0.9,
            source_session_id="session_001",
            source_content="conversation",
            metadata={"difficulty": "easy"},
            is_active=True,
        )

        assert item.item_id == "item_001"
        assert item.user_id == 123
        assert item.language_code == "es"
        assert item.content == "hola"
        assert len(item.context_tags) == 2
        assert item.metadata["difficulty"] == "easy"

    def test_spaced_repetition_item_with_none_optional_fields(self):
        """Test SpacedRepetitionItem __post_init__ initializes None fields"""
        item = SpacedRepetitionItem(
            item_id="item_002",
            user_id=456,
            language_code="fr",
            item_type="phrase",
            content="bonjour",
            context_tags=None,  # Should be initialized to []
            metadata=None,  # Should be initialized to {}
            first_seen_date=None,  # Should be initialized to now
        )

        assert isinstance(item.context_tags, list)
        assert len(item.context_tags) == 0
        assert isinstance(item.metadata, dict)
        assert len(item.metadata) == 0
        assert isinstance(item.first_seen_date, datetime)

    def test_spaced_repetition_item_without_optional_fields(self):
        """Test SpacedRepetitionItem creation without optional fields"""
        item = SpacedRepetitionItem(
            item_id="item_003",
            user_id=789,
            language_code="de",
            item_type="vocabulary",
            content="danke",
        )

        # All optional fields should be initialized
        assert isinstance(item.context_tags, list)
        assert len(item.context_tags) == 0
        assert isinstance(item.metadata, dict)
        assert len(item.metadata) == 0
        assert isinstance(item.first_seen_date, datetime)
        assert item.translation == ""
        assert item.is_active is True

    def test_spaced_repetition_item_sm2_algorithm_fields(self):
        """Test SM-2 algorithm specific fields"""
        item = SpacedRepetitionItem(
            item_id="item_004",
            user_id=100,
            language_code="ja",
            item_type="vocabulary",
            content="ありがとう",
            ease_factor=2.5,  # SM-2 default
            repetition_number=0,
            interval_days=1,
        )

        assert item.ease_factor == 2.5
        assert item.repetition_number == 0
        assert item.interval_days == 1
        assert item.total_reviews == 0


class TestLearningSession:
    """Test LearningSession dataclass"""

    def test_learning_session_with_all_fields(self):
        """Test LearningSession creation with all fields provided"""
        now = datetime.now()
        session = LearningSession(
            session_id="session_001",
            user_id=123,
            language_code="es",
            session_type="vocabulary",
            mode_specific_data={"scenario_id": "restaurant"},
            duration_minutes=30,
            items_studied=20,
            items_correct=18,
            items_incorrect=2,
            accuracy_percentage=90.0,
            average_response_time_ms=2000,
            confidence_score=0.85,
            engagement_score=0.9,
            difficulty_level=2,
            new_items_learned=5,
            items_reviewed=15,
            streak_contributions=1,
            goal_progress=0.4,
            content_source="daily_practice",
            ai_model_used="gpt-4",
            tutor_mode="conversation",
            scenario_id="restaurant_001",
            started_at=now,
            ended_at=now + timedelta(minutes=30),
        )

        assert session.session_id == "session_001"
        assert session.duration_minutes == 30
        assert session.accuracy_percentage == 90.0
        assert session.mode_specific_data["scenario_id"] == "restaurant"

    def test_learning_session_with_none_optional_fields(self):
        """Test LearningSession __post_init__ initializes None fields"""
        session = LearningSession(
            session_id="session_002",
            user_id=456,
            language_code="fr",
            session_type="conversation",
            mode_specific_data=None,  # Should be initialized to {}
            started_at=None,  # Should be initialized to now
        )

        assert isinstance(session.mode_specific_data, dict)
        assert len(session.mode_specific_data) == 0
        assert isinstance(session.started_at, datetime)

    def test_learning_session_without_optional_fields(self):
        """Test LearningSession creation without optional fields"""
        session = LearningSession(
            session_id="session_003",
            user_id=789,
            language_code="de",
            session_type="scenario",
        )

        # All optional fields should have defaults
        assert isinstance(session.mode_specific_data, dict)
        assert isinstance(session.started_at, datetime)
        assert session.duration_minutes == 0
        assert session.items_studied == 0
        assert session.accuracy_percentage == 0.0

    def test_learning_session_accuracy_calculation(self):
        """Test session with accuracy metrics"""
        session = LearningSession(
            session_id="session_004",
            user_id=100,
            language_code="ja",
            session_type="vocabulary",
            items_studied=50,
            items_correct=45,
            items_incorrect=5,
            accuracy_percentage=90.0,
        )

        assert session.items_studied == 50
        assert session.items_correct == 45
        assert session.items_incorrect == 5
        assert session.accuracy_percentage == 90.0


class TestLearningGoal:
    """Test LearningGoal dataclass"""

    def test_learning_goal_with_all_fields(self):
        """Test LearningGoal creation with all fields provided"""
        now = datetime.now()
        target = now + timedelta(days=30)
        completed = now + timedelta(days=25)

        goal = LearningGoal(
            goal_id="goal_001",
            user_id=123,
            language_code="es",
            goal_type="vocabulary",
            title="Learn 100 Spanish words",
            description="Master 100 common Spanish vocabulary words",
            target_value=100.0,
            current_value=75.0,
            unit="words",
            difficulty_level=2,
            priority=1,
            is_daily=False,
            is_weekly=True,
            is_monthly=False,
            is_custom=False,
            progress_percentage=75.0,
            milestones_reached=3,
            total_milestones=5,
            last_progress_update=now,
            start_date=now,
            target_date=target,
            completed_date=completed,
            status="completed",
        )

        assert goal.goal_id == "goal_001"
        assert goal.target_value == 100.0
        assert goal.current_value == 75.0
        assert goal.progress_percentage == 75.0
        assert goal.is_weekly is True

    def test_learning_goal_with_none_optional_fields(self):
        """Test LearningGoal __post_init__ initializes None fields"""
        goal = LearningGoal(
            goal_id="goal_002",
            user_id=456,
            language_code="fr",
            goal_type="conversation",
            title="Daily conversation practice",
            description="Practice conversations daily",
            target_value=30.0,
            start_date=None,  # Should be initialized to now
            target_date=None,  # Should be initialized to now + 30 days
        )

        assert isinstance(goal.start_date, datetime)
        assert isinstance(goal.target_date, datetime)
        assert goal.target_date > goal.start_date

    def test_learning_goal_without_optional_fields(self):
        """Test LearningGoal creation without optional fields"""
        goal = LearningGoal(
            goal_id="goal_003",
            user_id=789,
            language_code="de",
            goal_type="mastery",
            title="Master German grammar",
            description="Complete all grammar modules",
            target_value=20.0,
        )

        # All optional fields should have defaults
        assert isinstance(goal.start_date, datetime)
        assert isinstance(goal.target_date, datetime)
        assert goal.current_value == 0.0
        assert goal.unit == "items"
        assert goal.status == "active"
        assert goal.is_custom is True

    def test_learning_goal_daily_type(self):
        """Test daily learning goal configuration"""
        goal = LearningGoal(
            goal_id="goal_004",
            user_id=100,
            language_code="ja",
            goal_type="daily_practice",
            title="Daily kanji practice",
            description="Learn 5 kanji per day",
            target_value=5.0,
            is_daily=True,
            is_weekly=False,
            is_monthly=False,
            is_custom=False,
        )

        assert goal.is_daily is True
        assert goal.is_weekly is False
        assert goal.is_monthly is False
        assert goal.is_custom is False

    def test_learning_goal_progress_tracking(self):
        """Test goal progress tracking fields"""
        goal = LearningGoal(
            goal_id="goal_005",
            user_id=200,
            language_code="es",
            goal_type="vocabulary",
            title="Vocabulary milestone goal",
            description="Reach vocabulary milestones",
            target_value=100.0,
            current_value=60.0,
            progress_percentage=60.0,
            milestones_reached=3,
            total_milestones=5,
        )

        assert goal.progress_percentage == 60.0
        assert goal.milestones_reached == 3
        assert goal.total_milestones == 5
        assert goal.milestones_reached < goal.total_milestones


class TestDataclassIntegration:
    """Test dataclasses work together correctly"""

    def test_complete_learning_flow(self):
        """Test complete learning flow with all models"""
        now = datetime.now()

        # Create learning goal
        goal = LearningGoal(
            goal_id="goal_flow_001",
            user_id=123,
            language_code="es",
            goal_type="vocabulary",
            title="Master 50 words",
            description="Learn 50 Spanish vocabulary words",
            target_value=50.0,
        )

        # Create learning session
        session = LearningSession(
            session_id="session_flow_001",
            user_id=goal.user_id,
            language_code=goal.language_code,
            session_type="vocabulary",
            items_studied=10,
            items_correct=9,
            new_items_learned=10,
        )

        # Create spaced repetition items
        items = []
        for i in range(10):
            item = SpacedRepetitionItem(
                item_id=f"item_flow_{i:03d}",
                user_id=goal.user_id,
                language_code=goal.language_code,
                item_type="vocabulary",
                content=f"word_{i}",
                source_session_id=session.session_id,
            )
            items.append(item)

        # Verify integration
        assert goal.user_id == session.user_id
        assert goal.language_code == session.language_code
        assert session.new_items_learned == len(items)
        assert all(item.user_id == goal.user_id for item in items)
        assert all(item.source_session_id == session.session_id for item in items)

    def test_sm2_algorithm_workflow(self):
        """Test SM-2 algorithm workflow with items"""
        item = SpacedRepetitionItem(
            item_id="sm2_test_001",
            user_id=456,
            language_code="fr",
            item_type="vocabulary",
            content="merci",
            translation="thank you",
            ease_factor=2.5,
            repetition_number=0,
            interval_days=1,
        )

        # Simulate first review (correct)
        item.repetition_number += 1
        item.interval_days = 1
        item.total_reviews += 1
        item.correct_reviews += 1

        # Simulate second review (correct)
        item.repetition_number += 1
        item.interval_days = 6
        item.total_reviews += 1
        item.correct_reviews += 1

        assert item.repetition_number == 2
        assert item.interval_days == 6
        assert item.total_reviews == 2
        assert item.correct_reviews == 2
        assert item.incorrect_reviews == 0

    def test_goal_with_multiple_sessions(self):
        """Test goal progress tracked across multiple sessions"""
        goal = LearningGoal(
            goal_id="multi_session_goal",
            user_id=789,
            language_code="de",
            goal_type="daily_practice",
            title="Daily practice goal",
            description="Practice daily",
            target_value=30.0,
            is_daily=True,
        )

        sessions = []
        for day in range(5):
            session = LearningSession(
                session_id=f"daily_session_{day:03d}",
                user_id=goal.user_id,
                language_code=goal.language_code,
                session_type="vocabulary",
                items_studied=10,
                started_at=datetime.now() + timedelta(days=day),
            )
            sessions.append(session)

        # Verify sessions align with goal
        assert len(sessions) == 5
        assert all(s.user_id == goal.user_id for s in sessions)
        assert all(s.language_code == goal.language_code for s in sessions)
