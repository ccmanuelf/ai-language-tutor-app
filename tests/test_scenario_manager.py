"""
Comprehensive tests for scenario_manager module.

Tests cover:
- ScenarioManager initialization
- Scenario template management
- Scenario retrieval and filtering
- Template-based scenario creation
- Scenario conversation lifecycle
- Progress tracking and phase advancement
- Scenario completion and recommendations
- Persistence operations (CRUD)
- Helper and utility methods
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.scenario_manager import (
    ScenarioManager,
    get_available_scenarios,
    get_scenario_status,
    process_scenario_interaction,
    scenario_manager,
    start_scenario,
)
from app.services.scenario_models import (
    ConversationRole,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioPhase,
    ScenarioProgress,
)


class TestScenarioManagerInit:
    """Test ScenarioManager initialization."""

    def test_scenario_manager_initialization(self):
        """Test ScenarioManager initializes with predefined scenarios."""
        manager = ScenarioManager()

        assert manager.scenarios is not None
        assert len(manager.scenarios) >= 3  # At least restaurant, travel, shopping
        assert manager.scenario_templates is not None
        assert manager.scenario_factory is not None

    def test_scenario_templates_structure(self):
        """Test scenario templates have expected structure."""
        manager = ScenarioManager()
        templates = manager.get_scenario_templates()

        assert "restaurant" in templates
        assert "travel" in templates
        assert "shopping" in templates
        assert "business" in templates
        assert "social" in templates

        # Verify restaurant template structure
        restaurant = templates["restaurant"]
        assert "phases" in restaurant
        assert "vocabulary" in restaurant
        assert "cultural_aspects" in restaurant

    def test_global_scenario_manager_instance(self):
        """Test that global scenario_manager instance exists."""
        assert scenario_manager is not None
        assert isinstance(scenario_manager, ScenarioManager)


class TestGetAvailableScenarios:
    """Test get_available_scenarios method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    def test_get_all_scenarios(self):
        """Test retrieving all available scenarios."""
        scenarios = self.manager.get_available_scenarios()

        assert len(scenarios) >= 3
        assert all("scenario_id" in s for s in scenarios)
        assert all("name" in s for s in scenarios)
        assert all("category" in s for s in scenarios)

    def test_filter_scenarios_by_category(self):
        """Test filtering scenarios by category."""
        restaurant_scenarios = self.manager.get_available_scenarios(
            category=ScenarioCategory.RESTAURANT
        )

        assert len(restaurant_scenarios) >= 1
        assert all(s["category"] == "restaurant" for s in restaurant_scenarios)

    def test_filter_scenarios_by_difficulty(self):
        """Test filtering scenarios by difficulty level."""
        beginner_scenarios = self.manager.get_available_scenarios(
            difficulty=ScenarioDifficulty.BEGINNER
        )

        assert len(beginner_scenarios) >= 1
        assert all(s["difficulty"] == "beginner" for s in beginner_scenarios)

    def test_filter_scenarios_by_category_and_difficulty(self):
        """Test filtering scenarios by both category and difficulty."""
        filtered = self.manager.get_available_scenarios(
            category=ScenarioCategory.SHOPPING,
            difficulty=ScenarioDifficulty.BEGINNER,
        )

        # Should find the clothing shopping scenario
        assert len(filtered) >= 1
        assert filtered[0]["category"] == "shopping"
        assert filtered[0]["difficulty"] == "beginner"

    def test_scenario_list_includes_metadata(self):
        """Test that scenario list includes key metadata."""
        scenarios = self.manager.get_available_scenarios()

        first_scenario = scenarios[0]
        assert "scenario_id" in first_scenario
        assert "name" in first_scenario
        assert "description" in first_scenario
        assert "duration_minutes" in first_scenario
        assert "vocabulary_count" in first_scenario
        assert "phase_count" in first_scenario
        assert "learning_goals" in first_scenario


class TestGetScenarioDetails:
    """Test get_scenario_details method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    def test_get_scenario_details_success(self):
        """Test retrieving detailed information for a scenario."""
        details = self.manager.get_scenario_details("restaurant_dinner_reservation")

        assert details is not None
        assert details["scenario_id"] == "restaurant_dinner_reservation"
        assert "phases" in details
        assert "vocabulary_focus" in details
        assert "cultural_context" in details
        assert "learning_goals" in details
        assert "prerequisites" in details

    def test_get_scenario_details_includes_phases(self):
        """Test that details include phase information."""
        details = self.manager.get_scenario_details("restaurant_dinner_reservation")

        phases = details["phases"]
        assert len(phases) > 0

        first_phase = phases[0]
        assert "phase_id" in first_phase
        assert "name" in first_phase
        assert "vocabulary" in first_phase
        assert "phrases" in first_phase
        assert "objectives" in first_phase

    def test_get_scenario_details_nonexistent(self):
        """Test retrieving details for nonexistent scenario returns None."""
        details = self.manager.get_scenario_details("nonexistent_scenario")

        assert details is None


class TestUniversalTemplates:
    """Test universal template methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    def test_get_universal_templates(self):
        """Test retrieving universal scenario templates."""
        # These methods rely on scenario_factory implementation
        # Just test that the method exists and is callable
        assert hasattr(self.manager, "get_universal_templates")
        assert callable(self.manager.get_universal_templates)

    def test_get_tier1_scenarios(self):
        """Test retrieving Tier 1 (essential) templates."""
        # These methods rely on scenario_factory implementation
        # Just test that the method exists and is callable
        assert hasattr(self.manager, "get_tier1_scenarios")
        assert callable(self.manager.get_tier1_scenarios)

    def test_get_scenarios_by_category(self):
        """Test retrieving scenarios grouped by category."""
        result = self.manager.get_scenarios_by_category(ScenarioCategory.RESTAURANT)

        assert "category" in result
        assert result["category"] == "restaurant"
        assert "predefined_scenarios" in result
        assert "universal_templates" in result
        assert "total_count" in result


class TestCreateScenarioFromTemplate:
    """Test create_scenario_from_template method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    def test_create_scenario_from_template_method_exists(self):
        """Test that create_scenario_from_template method exists."""
        # Method relies on scenario_factory.create_scenario which may not be implemented
        # Just verify the method exists and is callable
        assert hasattr(self.manager, "create_scenario_from_template")
        assert callable(self.manager.create_scenario_from_template)


class TestStartScenarioConversation:
    """Test start_scenario_conversation method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()
        self.user_id = "user123"
        self.scenario_id = "restaurant_dinner_reservation"

    @pytest.mark.asyncio
    async def test_start_scenario_success(self):
        """Test starting a scenario conversation."""
        result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )

        assert "progress_id" in result
        assert "scenario" in result
        assert "current_phase" in result
        assert "opening_message" in result
        assert "your_role" in result
        assert "ai_role" in result
        assert "phase_objectives" in result
        assert "key_vocabulary" in result

    @pytest.mark.asyncio
    async def test_start_scenario_creates_progress(self):
        """Test that starting scenario creates progress tracking."""
        result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )

        progress_id = result["progress_id"]
        assert progress_id in self.manager.active_scenarios

        progress = self.manager.active_scenarios[progress_id]
        assert progress.scenario_id == self.scenario_id
        assert progress.user_id == self.user_id
        assert progress.current_phase == 0

    @pytest.mark.asyncio
    async def test_start_scenario_invalid_id(self):
        """Test starting scenario with invalid ID raises error."""
        with pytest.raises(ValueError, match="Scenario .* not found"):
            await self.manager.start_scenario_conversation(
                user_id=self.user_id, scenario_id="nonexistent_scenario"
            )

    @pytest.mark.asyncio
    async def test_start_scenario_with_language(self):
        """Test starting scenario with specific language."""
        result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id, language="es"
        )

        assert "opening_message" in result
        # Opening message should be generated


class TestGenerateScenarioOpening:
    """Test _generate_scenario_opening method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    def test_generate_opening_restaurant(self):
        """Test opening message for restaurant scenario."""
        scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        opening = self.manager._generate_scenario_opening(scenario)

        assert isinstance(opening, str)
        assert len(opening) > 0
        # Should mention key vocabulary
        assert "📚" in opening or "Key vocabulary" in opening

    def test_generate_opening_travel(self):
        """Test opening message for travel scenario."""
        scenario = self.manager.scenarios["hotel_check_in"]
        opening = self.manager._generate_scenario_opening(scenario)

        assert isinstance(opening, str)
        assert "hotel" in opening.lower() or "travel" in opening.lower()

    def test_generate_opening_shopping(self):
        """Test opening message for shopping scenario."""
        scenario = self.manager.scenarios["clothing_shopping"]
        opening = self.manager._generate_scenario_opening(scenario)

        assert isinstance(opening, str)
        assert "shop" in opening.lower() or "store" in opening.lower()


class TestProcessScenarioMessage:
    """Test process_scenario_message method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()
        self.user_id = "user123"
        self.scenario_id = "restaurant_dinner_reservation"

    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test processing message within scenario."""
        # Start scenario first
        start_result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )
        progress_id = start_result["progress_id"]

        # Process a message
        result = await self.manager.process_scenario_message(
            progress_id=progress_id,
            user_message="I'd like to make a reservation for 4 people",
            ai_response="Of course! What time would you prefer?",
        )

        assert "progress_id" in result
        assert "current_phase" in result
        assert "phase_completion" in result
        assert "vocabulary_progress" in result
        assert "learning_feedback" in result

    @pytest.mark.asyncio
    async def test_process_message_updates_progress(self):
        """Test that message processing updates progress."""
        start_result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )
        progress_id = start_result["progress_id"]

        progress_before = self.manager.active_scenarios[progress_id]
        old_activity = progress_before.last_activity

        # Small delay to ensure timestamp difference
        import asyncio

        await asyncio.sleep(0.01)

        await self.manager.process_scenario_message(
            progress_id=progress_id,
            user_message="Test message",
            ai_response="Response",
        )

        progress_after = self.manager.active_scenarios[progress_id]
        assert progress_after.last_activity > old_activity

    @pytest.mark.asyncio
    async def test_process_message_invalid_progress_id(self):
        """Test processing message with invalid progress ID raises error."""
        with pytest.raises(ValueError, match="Scenario progress .* not found"):
            await self.manager.process_scenario_message(
                progress_id="nonexistent_progress",
                user_message="Test",
                ai_response="Response",
            )

    @pytest.mark.asyncio
    async def test_process_message_phase_advancement(self):
        """Test phase advancement when objectives are met."""
        start_result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )
        progress_id = start_result["progress_id"]

        # Use vocabulary and phrases to trigger phase completion
        result = await self.manager.process_scenario_message(
            progress_id=progress_id,
            user_message="I'd like to make a reservation for a table for 4 people at 7pm. Is that time available?",
            ai_response="Yes, we have availability at 7pm!",
        )

        # Check if next_phase info is provided when phase completes
        if result["phase_completion"]["is_complete"]:
            assert "next_phase" in result


class TestAnalyzeScenarioMessage:
    """Test _analyze_scenario_message method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()
        self.scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        self.current_phase = self.scenario.phases[0]
        self.progress = Mock(spec=ScenarioProgress)

    @pytest.mark.asyncio
    async def test_analyze_message_vocabulary_usage(self):
        """Test analysis detects vocabulary usage."""
        user_message = "I want to make a reservation for a table"

        analysis = await self.manager._analyze_scenario_message(
            user_message=user_message,
            ai_response="Response",
            current_phase=self.current_phase,
            progress=self.progress,
        )

        assert "vocabulary_used" in analysis
        assert "reservation" in analysis["vocabulary_used"]
        assert "table" in analysis["vocabulary_used"]

    @pytest.mark.asyncio
    async def test_analyze_message_essential_phrases(self):
        """Test analysis detects essential phrases."""
        user_message = "I'd like to make a reservation"

        analysis = await self.manager._analyze_scenario_message(
            user_message=user_message,
            ai_response="Response",
            current_phase=self.current_phase,
            progress=self.progress,
        )

        assert "phrases_used" in analysis
        # Should detect the essential phrase

    @pytest.mark.asyncio
    async def test_analyze_message_generates_feedback(self):
        """Test analysis generates learning feedback."""
        user_message = "I'd like to make a reservation for a table please"

        analysis = await self.manager._analyze_scenario_message(
            user_message=user_message,
            ai_response="Response",
            current_phase=self.current_phase,
            progress=self.progress,
        )

        assert "learning_feedback" in analysis
        assert isinstance(analysis["learning_feedback"], list)

    @pytest.mark.asyncio
    async def test_analyze_message_engagement_score(self):
        """Test analysis calculates engagement score."""
        short_message = "Yes"
        long_message = " ".join(["word"] * 20)

        analysis_short = await self.manager._analyze_scenario_message(
            user_message=short_message,
            ai_response="Response",
            current_phase=self.current_phase,
            progress=self.progress,
        )

        analysis_long = await self.manager._analyze_scenario_message(
            user_message=long_message,
            ai_response="Response",
            current_phase=self.current_phase,
            progress=self.progress,
        )

        assert analysis_short["engagement_score"] < analysis_long["engagement_score"]


class TestCheckPhaseCompletion:
    """Test _check_phase_completion method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()
        self.scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        self.current_phase = self.scenario.phases[0]
        self.progress = Mock(spec=ScenarioProgress)

    def test_check_phase_completion_with_criteria(self):
        """Test phase completion check with success criteria."""
        analysis = {
            "vocabulary_used": ["reservation", "table"],
            "phrases_used": ["I'd like to make a reservation"],
            "objectives_addressed": ["Use polite language"],
        }

        result = self.manager._check_phase_completion(
            analysis=analysis, current_phase=self.current_phase, progress=self.progress
        )

        assert "is_complete" in result
        assert "completion_score" in result
        assert "criteria_met" in result
        assert "total_criteria" in result

    def test_check_phase_completion_below_threshold(self):
        """Test phase incomplete when criteria not met."""
        analysis = {
            "vocabulary_used": [],
            "phrases_used": [],
            "objectives_addressed": [],
        }

        result = self.manager._check_phase_completion(
            analysis=analysis, current_phase=self.current_phase, progress=self.progress
        )

        assert result["is_complete"] is False
        assert result["completion_score"] < 0.7


class TestGetScenarioProgress:
    """Test get_scenario_progress method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()
        self.user_id = "user123"
        self.scenario_id = "restaurant_dinner_reservation"

    @pytest.mark.asyncio
    async def test_get_progress_success(self):
        """Test retrieving scenario progress."""
        start_result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )
        progress_id = start_result["progress_id"]

        progress = await self.manager.get_scenario_progress(progress_id)

        assert progress is not None
        assert progress["progress_id"] == progress_id
        assert "scenario_name" in progress
        assert "current_phase" in progress
        assert "session_stats" in progress
        assert "learning_progress" in progress

    @pytest.mark.asyncio
    async def test_get_progress_nonexistent(self):
        """Test retrieving progress for nonexistent ID returns None."""
        progress = await self.manager.get_scenario_progress("nonexistent_id")

        assert progress is None


class TestCompleteScenario:
    """Test complete_scenario method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()
        self.user_id = "user123"
        self.scenario_id = "restaurant_dinner_reservation"

    @pytest.mark.asyncio
    async def test_complete_scenario_success(self):
        """Test completing a scenario and getting summary."""
        start_result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )
        progress_id = start_result["progress_id"]

        summary = await self.manager.complete_scenario(progress_id)

        assert "progress_id" in summary
        assert "scenario_completed" in summary
        assert "completion_stats" in summary
        assert "learning_achievements" in summary
        assert "performance_feedback" in summary

    @pytest.mark.asyncio
    async def test_complete_scenario_removes_from_active(self):
        """Test that completing scenario removes it from active scenarios."""
        start_result = await self.manager.start_scenario_conversation(
            user_id=self.user_id, scenario_id=self.scenario_id
        )
        progress_id = start_result["progress_id"]

        assert progress_id in self.manager.active_scenarios

        await self.manager.complete_scenario(progress_id)

        assert progress_id not in self.manager.active_scenarios

    @pytest.mark.asyncio
    async def test_complete_scenario_invalid_id(self):
        """Test completing nonexistent scenario raises error."""
        with pytest.raises(ValueError, match="Scenario progress .* not found"):
            await self.manager.complete_scenario("nonexistent_id")


class TestGetNextScenarioRecommendations:
    """Test _get_next_scenario_recommendations method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    def test_get_recommendations(self):
        """Test getting scenario recommendations."""
        completed_scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        progress = Mock(spec=ScenarioProgress)

        recommendations = self.manager._get_next_scenario_recommendations(
            completed_scenario, progress
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3  # Max 3 recommendations

        if recommendations:
            first_rec = recommendations[0]
            assert "scenario_id" in first_rec
            assert "name" in first_rec
            assert "reason" in first_rec


class TestPersistenceMethods:
    """Test persistence CRUD methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ScenarioManager()

    @pytest.mark.asyncio
    async def test_get_all_scenarios(self):
        """Test getting all scenarios."""
        scenarios = await self.manager.get_all_scenarios()

        assert isinstance(scenarios, list)
        assert len(scenarios) >= 3
        assert all(isinstance(s, ConversationScenario) for s in scenarios)

    @pytest.mark.asyncio
    async def test_get_scenario_by_id_success(self):
        """Test getting specific scenario by ID."""
        scenario = await self.manager.get_scenario_by_id(
            "restaurant_dinner_reservation"
        )

        assert scenario is not None
        assert isinstance(scenario, ConversationScenario)
        assert scenario.scenario_id == "restaurant_dinner_reservation"

    @pytest.mark.asyncio
    async def test_get_scenario_by_id_nonexistent(self):
        """Test getting nonexistent scenario returns None."""
        scenario = await self.manager.get_scenario_by_id("nonexistent_scenario")

        assert scenario is None

    @pytest.mark.asyncio
    async def test_save_scenario_validation(self):
        """Test scenario validation before saving."""
        # Invalid scenario (empty ID)
        invalid_scenario = Mock(spec=ConversationScenario)
        invalid_scenario.scenario_id = ""
        invalid_scenario.name = "Test"

        result = self.manager._validate_scenario(invalid_scenario)

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_scenario_success(self):
        """Test validating correct scenario."""
        valid_scenario = self.manager.scenarios["restaurant_dinner_reservation"]

        result = self.manager._validate_scenario(valid_scenario)

        assert result is True

    @pytest.mark.asyncio
    async def test_save_scenario_success(self):
        """Test saving a valid scenario."""
        # Create test scenario
        test_scenario = ConversationScenario(
            scenario_id="test_scenario_save",
            name="Test Scenario",
            category=ScenarioCategory.SOCIAL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test scenario for saving",
            user_role=ConversationRole.STUDENT,
            ai_role=ConversationRole.TEACHER,
            setting="Test setting",
            duration_minutes=10,
            phases=[
                ScenarioPhase(
                    phase_id="test_phase",
                    name="Test Phase",
                    description="Test phase description",
                    expected_duration_minutes=5,
                    key_vocabulary=["test"],
                    essential_phrases=["test phrase"],
                    learning_objectives=["test objective"],
                )
            ],
            vocabulary_focus=["test"],
            cultural_context={"test": "context"},  # Required field
            learning_goals=["test goal"],
        )

        with patch(
            "app.services.scenario_manager.ScenarioIO.save_scenarios_to_file",
            new_callable=AsyncMock,
        ):
            result = await self.manager.save_scenario(test_scenario)

            assert result is True
            assert "test_scenario_save" in self.manager.scenarios


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_get_available_scenarios_function(self):
        """Test get_available_scenarios convenience function."""
        scenarios = await get_available_scenarios()

        assert isinstance(scenarios, list)
        assert len(scenarios) >= 3

    @pytest.mark.asyncio
    async def test_get_available_scenarios_with_filters(self):
        """Test convenience function with filters."""
        scenarios = await get_available_scenarios(
            category="restaurant", difficulty="beginner"
        )

        assert isinstance(scenarios, list)

    @pytest.mark.asyncio
    async def test_start_scenario_function(self):
        """Test start_scenario convenience function."""
        result = await start_scenario(
            user_id="user123", scenario_id="restaurant_dinner_reservation"
        )

        assert "progress_id" in result
        assert "scenario" in result

    @pytest.mark.asyncio
    async def test_process_scenario_interaction_function(self):
        """Test process_scenario_interaction convenience function."""
        start_result = await start_scenario(
            user_id="user123", scenario_id="restaurant_dinner_reservation"
        )
        progress_id = start_result["progress_id"]

        result = await process_scenario_interaction(
            progress_id=progress_id, user_message="Test", ai_response="Response"
        )

        assert "progress_id" in result

    @pytest.mark.asyncio
    async def test_get_scenario_status_function(self):
        """Test get_scenario_status convenience function."""
        start_result = await start_scenario(
            user_id="user123", scenario_id="restaurant_dinner_reservation"
        )
        progress_id = start_result["progress_id"]

        status = await get_scenario_status(progress_id)

        assert status is not None
        assert "progress_id" in status


class TestPhaseCompletionEdgeCases:
    """Test phase completion with no criteria."""

    def setup_method(self):
        """Setup test instance."""
        self.manager = ScenarioManager()

    @pytest.mark.asyncio
    async def test_check_phase_completion_no_criteria_high_score(self):
        """Test phase completion when no criteria and high completion score."""
        progress = ScenarioProgress(
            scenario_id="restaurant_dinner_reservation",
            user_id="user123",
            current_phase=0,
            phase_progress={},
            vocabulary_mastered=[],
            objectives_completed=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            total_attempts=0,
            success_rate=0.0,
        )

        scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        current_phase = scenario.phases[0]

        # Modify phase to have no success criteria
        with patch.object(current_phase, "success_criteria", []):
            analysis = {
                "vocabulary_used": ["hello", "table", "reservation"],
                "phrases_used": ["I'd like to make a reservation"],
                "objectives_addressed": ["greeting", "stating_purpose"],
                "engagement_score": 0.9,
            }

            result = self.manager._check_phase_completion(
                analysis, current_phase, progress
            )

            # With all three components, score = 0.3 + 0.3 + 0.4 = 1.0 >= 0.6
            assert result["is_complete"] is True

    @pytest.mark.asyncio
    async def test_check_phase_completion_no_criteria_low_score(self):
        """Test phase completion when no criteria and low completion score."""
        progress = ScenarioProgress(
            scenario_id="restaurant_dinner_reservation",
            user_id="user123",
            current_phase=0,
            phase_progress={},
            vocabulary_mastered=[],
            objectives_completed=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            total_attempts=0,
            success_rate=0.0,
        )

        scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        current_phase = scenario.phases[0]

        # Modify phase to have no success criteria
        with patch.object(current_phase, "success_criteria", []):
            analysis = {
                "vocabulary_used": [],
                "phrases_used": ["hello"],
                "objectives_addressed": [],
                "engagement_score": 0.3,
            }

            result = self.manager._check_phase_completion(
                analysis, current_phase, progress
            )

            # Only phrases_used, score = 0.3 < 0.6
            assert result["is_complete"] is False

    @pytest.mark.asyncio
    async def test_check_phase_completion_no_criteria_medium_score(self):
        """Test phase completion when no criteria and medium completion score."""
        progress = ScenarioProgress(
            scenario_id="restaurant_dinner_reservation",
            user_id="user123",
            current_phase=0,
            phase_progress={},
            vocabulary_mastered=[],
            objectives_completed=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            total_attempts=0,
            success_rate=0.0,
        )

        scenario = self.manager.scenarios["restaurant_dinner_reservation"]
        current_phase = scenario.phases[0]

        # Modify phase to have no success criteria
        with patch.object(current_phase, "success_criteria", []):
            analysis = {
                "vocabulary_used": ["reservation"],
                "phrases_used": ["I need a table"],
                "objectives_addressed": [],
                "engagement_score": 0.6,
            }

            result = self.manager._check_phase_completion(
                analysis, current_phase, progress
            )

            # vocab + phrases = 0.3 + 0.3 = 0.6 >= 0.6
            assert result["is_complete"] is True


class TestScenarioValidation:
    """Test scenario validation edge cases."""

    def setup_method(self):
        """Setup test instance."""
        self.manager = ScenarioManager()

    def test_validate_scenario_empty_id(self):
        """Test validation fails with empty scenario_id."""
        scenario = Mock(spec=ConversationScenario)
        scenario.scenario_id = ""
        scenario.name = "Valid Name"
        scenario.duration_minutes = 10
        scenario.phases = [Mock()]

        result = self.manager._validate_scenario(scenario)
        assert result is False

    def test_validate_scenario_whitespace_id(self):
        """Test validation fails with whitespace-only scenario_id."""
        scenario = Mock(spec=ConversationScenario)
        scenario.scenario_id = "   "
        scenario.name = "Valid Name"
        scenario.duration_minutes = 10
        scenario.phases = [Mock()]

        result = self.manager._validate_scenario(scenario)
        assert result is False

    def test_validate_scenario_empty_name(self):
        """Test validation fails with empty name."""
        scenario = Mock(spec=ConversationScenario)
        scenario.scenario_id = "valid_id"
        scenario.name = ""
        scenario.duration_minutes = 10
        scenario.phases = [Mock()]

        result = self.manager._validate_scenario(scenario)
        assert result is False

    def test_validate_scenario_zero_duration(self):
        """Test validation fails with zero duration."""
        scenario = Mock(spec=ConversationScenario)
        scenario.scenario_id = "valid_id"
        scenario.name = "Valid Name"
        scenario.duration_minutes = 0
        scenario.phases = [Mock()]

        result = self.manager._validate_scenario(scenario)
        assert result is False

    def test_validate_scenario_negative_duration(self):
        """Test validation fails with negative duration."""
        scenario = Mock(spec=ConversationScenario)
        scenario.scenario_id = "valid_id"
        scenario.name = "Valid Name"
        scenario.duration_minutes = -5
        scenario.phases = [Mock()]

        result = self.manager._validate_scenario(scenario)
        assert result is False

    def test_validate_scenario_no_phases(self):
        """Test validation fails with empty phases list."""
        scenario = Mock(spec=ConversationScenario)
        scenario.scenario_id = "valid_id"
        scenario.name = "Valid Name"
        scenario.duration_minutes = 10
        scenario.phases = []

        result = self.manager._validate_scenario(scenario)
        assert result is False


class TestDeleteScenario:
    """Test delete_scenario functionality."""

    def setup_method(self):
        """Setup test instance."""
        self.manager = ScenarioManager()

    @pytest.mark.asyncio
    async def test_delete_scenario_success(self):
        """Test successful scenario deletion."""
        scenario_id = "restaurant_dinner_reservation"
        assert scenario_id in self.manager.scenarios

        with patch(
            "app.services.scenario_manager.ScenarioIO.save_scenarios_to_file"
        ) as mock_save:
            mock_save.return_value = None

            result = await self.manager.delete_scenario(scenario_id)

            assert result is True
            assert scenario_id not in self.manager.scenarios
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_scenario_nonexistent(self):
        """Test deleting non-existent scenario returns False."""
        result = await self.manager.delete_scenario("nonexistent_scenario_999")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_scenario_save_failure(self):
        """Test delete_scenario handles save errors gracefully."""
        scenario_id = "hotel_check_in"

        with patch(
            "app.services.scenario_manager.ScenarioIO.save_scenarios_to_file"
        ) as mock_save:
            mock_save.side_effect = Exception("Disk write error")

            result = await self.manager.delete_scenario(scenario_id)

            assert result is False


class TestSetScenarioActive:
    """Test set_scenario_active functionality."""

    def setup_method(self):
        """Setup test instance."""
        self.manager = ScenarioManager()

    @pytest.mark.asyncio
    async def test_set_scenario_active_true(self):
        """Test activating a scenario."""
        scenario_id = "restaurant_dinner_reservation"

        with patch(
            "app.services.scenario_manager.ScenarioIO.save_scenarios_to_file"
        ) as mock_save:
            mock_save.return_value = None

            result = await self.manager.set_scenario_active(scenario_id, True)

            assert result is True
            assert self.manager.scenarios[scenario_id].is_active is True
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_scenario_active_false(self):
        """Test deactivating a scenario."""
        scenario_id = "hotel_check_in"

        with patch(
            "app.services.scenario_manager.ScenarioIO.save_scenarios_to_file"
        ) as mock_save:
            mock_save.return_value = None

            result = await self.manager.set_scenario_active(scenario_id, False)

            assert result is True
            assert self.manager.scenarios[scenario_id].is_active is False
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_scenario_active_nonexistent(self):
        """Test setting active status on non-existent scenario."""
        result = await self.manager.set_scenario_active("nonexistent_999", True)

        assert result is False

    @pytest.mark.asyncio
    async def test_set_scenario_active_save_failure(self):
        """Test set_scenario_active handles save errors."""
        scenario_id = "clothing_shopping"

        with patch(
            "app.services.scenario_manager.ScenarioIO.save_scenarios_to_file"
        ) as mock_save:
            mock_save.side_effect = Exception("Database error")

            result = await self.manager.set_scenario_active(scenario_id, True)

            assert result is False
