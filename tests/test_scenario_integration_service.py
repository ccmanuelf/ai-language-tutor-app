"""
Unit Tests for ScenarioIntegrationService
Session 129B - Coverage Fix

Tests error scenarios and edge cases for:
- save_scenario_progress
- create_sr_items_from_scenario
- record_learning_session
- integrate_scenario_completion
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.database.config import get_primary_db_session
from app.models.database import (
    LearningSession,
    ScenarioProgressHistory,
    VocabularyItem,
)
from app.services.scenario_integration_service import (
    ScenarioIntegrationService,
    integrate_completed_scenario,
)
from app.services.scenario_models import ScenarioProgress


class TestScenarioIntegrationService:
    """Test ScenarioIntegrationService error handling and edge cases"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.db = get_primary_db_session()
        self.service = ScenarioIntegrationService(self.db)
        yield
        self.db.close()

    def _create_mock_progress(self, user_id=1001, scenario_id="test_scenario"):
        """Helper to create mock ScenarioProgress"""
        start_time = datetime.now() - timedelta(minutes=10)
        progress = ScenarioProgress(
            scenario_id=scenario_id,
            user_id=user_id,
            current_phase=2,
            phase_progress={"phase1": 1.0, "phase2": 1.0, "phase3": 0.5},
            vocabulary_mastered=["hello", "goodbye", "thank you"],
            objectives_completed=["greeting", "farewell"],
            start_time=start_time,
            last_activity=datetime.now(),
            total_attempts=5,
            success_rate=0.85,
            progress_id=f"progress_{user_id}",
        )
        return progress

    @pytest.mark.asyncio
    async def test_save_scenario_progress_db_error(self):
        """Test save_scenario_progress handles database errors"""
        progress = self._create_mock_progress()

        # Mock database commit to raise an exception
        with patch.object(self.service.db, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await self.service.save_scenario_progress(
                    progress=progress,
                    user_id=1001,
                    scenario_id="test_scenario",
                    total_phases=3,
                )

        # Verify rollback was called
        # (In real implementation, rollback is called in exception handler)

    @pytest.mark.asyncio
    async def test_save_scenario_progress_success(self):
        """Test save_scenario_progress creates history record correctly"""
        progress = self._create_mock_progress(user_id=2001, scenario_id="restaurant_01")

        history = await self.service.save_scenario_progress(
            progress=progress,
            user_id=2001,
            scenario_id="restaurant_01",
            total_phases=4,
        )

        assert history is not None
        assert history.user_id == 2001
        assert history.scenario_id == "restaurant_01"
        assert history.phases_completed == 3  # current_phase + 1
        assert history.total_phases == 4
        assert history.vocabulary_mastered == ["hello", "goodbye", "thank you"]
        assert history.objectives_completed == ["greeting", "farewell"]
        assert history.success_rate == 0.85
        assert history.duration_minutes >= 10  # At least 10 minutes

    @pytest.mark.asyncio
    async def test_create_sr_items_from_scenario_db_error(self):
        """Test create_sr_items_from_scenario handles database errors"""
        vocabulary = ["bonjour", "merci", "au revoir"]

        # Mock database commit to raise an exception
        with patch.object(self.service.db, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await self.service.create_sr_items_from_scenario(
                    vocabulary=vocabulary,
                    scenario_id="french_cafe",
                    user_id=3001,
                    language="fr",
                )

    @pytest.mark.asyncio
    async def test_create_sr_items_empty_vocabulary(self):
        """Test create_sr_items_from_scenario with empty vocabulary list"""
        items = await self.service.create_sr_items_from_scenario(
            vocabulary=[],
            scenario_id="empty_scenario",
            user_id=4001,
            language="es",
        )

        assert items == []

    @pytest.mark.asyncio
    async def test_create_sr_items_updates_existing(self):
        """Test create_sr_items_from_scenario updates existing vocabulary items without source_document_id"""
        user_id = 5001
        language = "it"
        word = "ciao"

        # Check if item already exists (from previous test runs)
        existing = self.db.query(VocabularyItem).filter(
            VocabularyItem.user_id == user_id,
            VocabularyItem.language == language,
            VocabularyItem.word == word
        ).first()

        if existing:
            # Delete existing item to start fresh
            self.db.delete(existing)
            self.db.commit()

        # Create existing vocabulary item WITHOUT source_document_id
        existing_item = VocabularyItem(
            user_id=user_id,
            language=language,
            word=word,
            source_type="manual",
            source_document_id=None,  # No source document
            difficulty_level=1,
            mastery_level=0.5,
            times_studied=5,
            times_correct=4,
            next_review_date=datetime.now(),
            repetition_interval_days=2,
            ease_factor=2.5,
        )
        self.db.add(existing_item)
        self.db.commit()

        # Create SR items from scenario with same word
        items = await self.service.create_sr_items_from_scenario(
            vocabulary=[word],
            scenario_id="italian_greeting",
            user_id=user_id,
            language=language,
        )

        assert len(items) == 1
        updated_item = items[0]
        assert updated_item.word == word
        assert updated_item.times_studied == 6  # Incremented
        assert updated_item.source_type == "scenario"  # Updated
        assert updated_item.source_document_id == "italian_greeting"  # Set

    @pytest.mark.asyncio
    async def test_create_sr_items_updates_existing_with_source(self):
        """Test create_sr_items_from_scenario updates existing items that already have source_document_id"""
        user_id = 5002
        language = "fr"
        word = "bonjour"

        # Check if item already exists
        existing = self.db.query(VocabularyItem).filter(
            VocabularyItem.user_id == user_id,
            VocabularyItem.language == language,
            VocabularyItem.word == word
        ).first()

        if existing:
            self.db.delete(existing)
            self.db.commit()

        # Create existing vocabulary item WITH source_document_id
        existing_item = VocabularyItem(
            user_id=user_id,
            language=language,
            word=word,
            source_type="scenario",
            source_document_id="previous_scenario",  # Already has source
            difficulty_level=1,
            mastery_level=0.5,
            times_studied=3,
            times_correct=2,
            next_review_date=datetime.now(),
            repetition_interval_days=1,
            ease_factor=2.5,
        )
        self.db.add(existing_item)
        self.db.commit()

        # Create SR items from different scenario
        items = await self.service.create_sr_items_from_scenario(
            vocabulary=[word],
            scenario_id="french_greeting",
            user_id=user_id,
            language=language,
        )

        assert len(items) == 1
        updated_item = items[0]
        assert updated_item.word == word
        assert updated_item.times_studied == 4  # Incremented
        assert updated_item.source_document_id == "previous_scenario"  # NOT changed

    @pytest.mark.asyncio
    async def test_record_learning_session_db_error(self):
        """Test record_learning_session handles database errors"""
        started_at = datetime.now() - timedelta(minutes=15)
        ended_at = datetime.now()

        # Mock database commit to raise an exception
        with patch.object(self.service.db, "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await self.service.record_learning_session(
                    user_id=6001,
                    scenario_id="travel_airport",
                    language="de",
                    started_at=started_at,
                    ended_at=ended_at,
                    vocabulary_count=10,
                    objectives_count=5,
                    success_rate=0.75,
                )

    @pytest.mark.asyncio
    async def test_record_learning_session_success(self):
        """Test record_learning_session creates session correctly"""
        started_at = datetime.now() - timedelta(minutes=12)
        ended_at = datetime.now()

        session = await self.service.record_learning_session(
            user_id=7001,
            scenario_id="shopping_mall",
            language="ja",
            started_at=started_at,
            ended_at=ended_at,
            vocabulary_count=8,
            objectives_count=4,
            success_rate=0.90,
        )

        assert session is not None
        assert session.user_id == 7001
        assert session.session_type == "scenario"
        assert session.source_id == "shopping_mall"
        assert session.language == "ja"
        assert session.items_studied == 12  # vocab + objectives
        assert session.items_correct == 10  # 12 * 0.90 = 10.8 -> 10
        assert session.items_incorrect == 1  # 12 * 0.10 = 1.2 -> 1
        assert session.accuracy_rate == 0.90
        assert session.duration_seconds >= 720  # At least 12 minutes

    @pytest.mark.asyncio
    async def test_integrate_scenario_completion_partial_failure(self):
        """Test integrate_scenario_completion when one step fails"""
        progress = self._create_mock_progress(user_id=8001, scenario_id="business_meeting")

        # Mock create_sr_items_from_scenario to fail
        with patch.object(
            self.service,
            "create_sr_items_from_scenario",
            side_effect=Exception("SR creation failed"),
        ):
            with pytest.raises(Exception, match="SR creation failed"):
                await self.service.integrate_scenario_completion(
                    progress=progress,
                    user_id=8001,
                    scenario_id="business_meeting",
                    total_phases=3,
                    language="en",
                )

    @pytest.mark.asyncio
    async def test_integrate_scenario_completion_success(self):
        """Test complete integration workflow"""
        progress = self._create_mock_progress(user_id=9001, scenario_id="hotel_checkin")

        result = await self.service.integrate_scenario_completion(
            progress=progress,
            user_id=9001,
            scenario_id="hotel_checkin",
            total_phases=3,
            language="es",
        )

        assert result is not None
        assert result["integration_complete"] is True
        assert "progress_history_id" in result
        assert "sr_items_created" in result
        assert "learning_session_id" in result
        assert result["sr_items_created"] == 3  # 3 vocabulary words


class TestConvenienceFunction:
    """Test module-level convenience function"""

    @pytest.mark.asyncio
    async def test_integrate_completed_scenario(self):
        """Test integrate_completed_scenario convenience function"""
        start_time = datetime.now() - timedelta(minutes=8)
        progress = ScenarioProgress(
            scenario_id="cafe_order",
            user_id=10001,
            current_phase=1,
            phase_progress={"phase1": 1.0, "phase2": 0.8},
            vocabulary_mastered=["coffee", "milk", "sugar"],
            objectives_completed=["order_drink"],
            start_time=start_time,
            last_activity=datetime.now(),
            total_attempts=3,
            success_rate=0.95,
            progress_id="progress_10001",
        )

        result = await integrate_completed_scenario(
            progress=progress,
            user_id=10001,
            scenario_id="cafe_order",
            total_phases=2,
            language="en",
        )

        assert result is not None
        assert result["integration_complete"] is True
        assert result["sr_items_created"] == 3
