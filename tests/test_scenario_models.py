"""
Comprehensive tests for scenario_models.py

Tests all dataclass models, enums, and __post_init__ methods to achieve 100% coverage.
"""

from datetime import datetime

import pytest

from app.services.scenario_models import (
    ConversationRole,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioPhase,
    ScenarioProgress,
    UniversalScenarioTemplate,
)


class TestScenarioEnums:
    """Test all enum definitions"""

    def test_scenario_category_enum(self):
        """Test ScenarioCategory enum has all expected values"""
        assert ScenarioCategory.TRAVEL.value == "travel"
        assert ScenarioCategory.RESTAURANT.value == "restaurant"
        assert ScenarioCategory.SHOPPING.value == "shopping"
        assert ScenarioCategory.BUSINESS.value == "business"
        assert ScenarioCategory.HEALTHCARE.value == "healthcare"
        assert ScenarioCategory.SOCIAL.value == "social"
        assert ScenarioCategory.EMERGENCY.value == "emergency"
        assert ScenarioCategory.EDUCATION.value == "education"
        assert ScenarioCategory.DAILY_LIFE.value == "daily_life"
        assert ScenarioCategory.HOBBIES.value == "hobbies"

    def test_scenario_difficulty_enum(self):
        """Test ScenarioDifficulty enum has all expected values"""
        assert ScenarioDifficulty.BEGINNER.value == "beginner"
        assert ScenarioDifficulty.INTERMEDIATE.value == "intermediate"
        assert ScenarioDifficulty.ADVANCED.value == "advanced"
        assert ScenarioDifficulty.NATIVE.value == "native"

    def test_conversation_role_enum(self):
        """Test ConversationRole enum has all expected values"""
        assert ConversationRole.CUSTOMER.value == "customer"
        assert ConversationRole.SERVICE_PROVIDER.value == "service_provider"
        assert ConversationRole.FRIEND.value == "friend"
        assert ConversationRole.COLLEAGUE.value == "colleague"
        assert ConversationRole.STUDENT.value == "student"
        assert ConversationRole.TEACHER.value == "teacher"
        assert ConversationRole.TOURIST.value == "tourist"
        assert ConversationRole.LOCAL.value == "local"


class TestScenarioPhase:
    """Test ScenarioPhase dataclass"""

    def test_scenario_phase_with_all_fields(self):
        """Test ScenarioPhase creation with all fields provided"""
        phase = ScenarioPhase(
            phase_id="phase_1",
            name="Ordering Food",
            description="Practice ordering food at a restaurant",
            expected_duration_minutes=10,
            key_vocabulary=["menu", "order", "waiter"],
            essential_phrases=["I would like", "Can I have"],
            learning_objectives=["Order food confidently"],
            cultural_notes="Tipping is customary",
            success_criteria=["Order complete meal", "Use polite phrases"],
        )

        assert phase.phase_id == "phase_1"
        assert phase.name == "Ordering Food"
        assert phase.cultural_notes == "Tipping is customary"
        assert len(phase.success_criteria) == 2

    def test_scenario_phase_with_none_success_criteria(self):
        """Test ScenarioPhase __post_init__ initializes success_criteria to empty list"""
        phase = ScenarioPhase(
            phase_id="phase_2",
            name="Test Phase",
            description="Test description",
            expected_duration_minutes=5,
            key_vocabulary=["test"],
            essential_phrases=["hello"],
            learning_objectives=["test objective"],
            success_criteria=None,  # This should be initialized to []
        )

        assert isinstance(phase.success_criteria, list)
        assert len(phase.success_criteria) == 0

    def test_scenario_phase_without_optional_fields(self):
        """Test ScenarioPhase creation without optional fields"""
        phase = ScenarioPhase(
            phase_id="phase_3",
            name="Simple Phase",
            description="Simple description",
            expected_duration_minutes=5,
            key_vocabulary=["word"],
            essential_phrases=["phrase"],
            learning_objectives=["objective"],
        )

        assert phase.cultural_notes is None
        assert isinstance(phase.success_criteria, list)
        assert len(phase.success_criteria) == 0


class TestConversationScenario:
    """Test ConversationScenario dataclass"""

    def test_conversation_scenario_with_all_fields(self):
        """Test ConversationScenario creation with all fields provided"""
        phase = ScenarioPhase(
            phase_id="phase_1",
            name="Introduction",
            description="Greet and introduce",
            expected_duration_minutes=5,
            key_vocabulary=["hello"],
            essential_phrases=["Nice to meet you"],
            learning_objectives=["Greet properly"],
        )

        scenario = ConversationScenario(
            scenario_id="scenario_1",
            name="Restaurant Dining",
            category=ScenarioCategory.RESTAURANT,
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            description="Full restaurant experience",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="French restaurant",
            duration_minutes=30,
            phases=[phase],
            vocabulary_focus=["food", "menu", "order"],
            cultural_context={"tipping": "15-20%", "dress_code": "casual"},
            learning_goals=["Order confidently"],
            learning_outcomes=["Can order in French"],
            prerequisites=["Basic French vocabulary"],
        )

        assert scenario.scenario_id == "scenario_1"
        assert scenario.category == ScenarioCategory.RESTAURANT
        assert len(scenario.prerequisites) == 1
        assert len(scenario.learning_outcomes) == 1
        assert len(scenario.learning_goals) == 1

    def test_conversation_scenario_with_none_optional_fields(self):
        """Test ConversationScenario __post_init__ initializes None fields to empty lists"""
        phase = ScenarioPhase(
            phase_id="phase_1",
            name="Test",
            description="Test",
            expected_duration_minutes=5,
            key_vocabulary=["test"],
            essential_phrases=["test"],
            learning_objectives=["test"],
        )

        scenario = ConversationScenario(
            scenario_id="scenario_2",
            name="Test Scenario",
            category=ScenarioCategory.TRAVEL,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="Test description",
            user_role=ConversationRole.TOURIST,
            ai_role=ConversationRole.LOCAL,
            setting="Airport",
            duration_minutes=15,
            phases=[phase],
            vocabulary_focus=["ticket", "gate"],
            cultural_context={},
            learning_goals=None,  # Should be initialized to []
            learning_outcomes=None,  # Should be initialized to []
            prerequisites=None,  # Should be initialized to []
        )

        assert isinstance(scenario.prerequisites, list)
        assert len(scenario.prerequisites) == 0
        assert isinstance(scenario.learning_outcomes, list)
        assert len(scenario.learning_outcomes) == 0
        assert isinstance(scenario.learning_goals, list)
        assert len(scenario.learning_goals) == 0

    def test_conversation_scenario_without_optional_fields(self):
        """Test ConversationScenario creation without optional fields"""
        phase = ScenarioPhase(
            phase_id="phase_1",
            name="Test",
            description="Test",
            expected_duration_minutes=5,
            key_vocabulary=["test"],
            essential_phrases=["test"],
            learning_objectives=["test"],
        )

        scenario = ConversationScenario(
            scenario_id="scenario_3",
            name="Minimal Scenario",
            category=ScenarioCategory.SHOPPING,
            difficulty=ScenarioDifficulty.ADVANCED,
            description="Minimal test",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Store",
            duration_minutes=10,
            phases=[phase],
            vocabulary_focus=["buy"],
            cultural_context={},
        )

        # All optional fields should be initialized to empty lists
        assert isinstance(scenario.prerequisites, list)
        assert isinstance(scenario.learning_outcomes, list)
        assert isinstance(scenario.learning_goals, list)


class TestScenarioProgress:
    """Test ScenarioProgress dataclass"""

    def test_scenario_progress_with_all_fields(self):
        """Test ScenarioProgress creation with all fields provided"""
        now = datetime.now()
        progress = ScenarioProgress(
            scenario_id="scenario_1",
            user_id="user_123",
            current_phase=2,
            phase_progress={"phase_1": 1.0, "phase_2": 0.5},
            vocabulary_mastered=["hello", "goodbye"],
            objectives_completed=["obj_1", "obj_2"],
            start_time=now,
            last_activity=now,
            total_attempts=3,
            success_rate=0.85,
            difficulty_adjustments=["increased_complexity"],
        )

        assert progress.scenario_id == "scenario_1"
        assert progress.current_phase == 2
        assert len(progress.difficulty_adjustments) == 1

    def test_scenario_progress_with_none_difficulty_adjustments(self):
        """Test ScenarioProgress __post_init__ initializes difficulty_adjustments to empty list"""
        now = datetime.now()
        progress = ScenarioProgress(
            scenario_id="scenario_2",
            user_id="user_456",
            current_phase=1,
            phase_progress={"phase_1": 0.3},
            vocabulary_mastered=["word1"],
            objectives_completed=["obj_1"],
            start_time=now,
            last_activity=now,
            total_attempts=1,
            success_rate=0.75,
            difficulty_adjustments=None,  # Should be initialized to []
        )

        assert isinstance(progress.difficulty_adjustments, list)
        assert len(progress.difficulty_adjustments) == 0

    def test_scenario_progress_without_optional_fields(self):
        """Test ScenarioProgress creation without optional fields"""
        now = datetime.now()
        progress = ScenarioProgress(
            scenario_id="scenario_3",
            user_id="user_789",
            current_phase=0,
            phase_progress={},
            vocabulary_mastered=[],
            objectives_completed=[],
            start_time=now,
            last_activity=now,
            total_attempts=0,
            success_rate=0.0,
        )

        assert isinstance(progress.difficulty_adjustments, list)
        assert len(progress.difficulty_adjustments) == 0


class TestUniversalScenarioTemplate:
    """Test UniversalScenarioTemplate dataclass"""

    def test_universal_scenario_template_with_all_fields(self):
        """Test UniversalScenarioTemplate creation with all fields provided"""
        template = UniversalScenarioTemplate(
            template_id="template_1",
            name="Restaurant Template",
            category=ScenarioCategory.RESTAURANT,
            tier=1,
            base_vocabulary=["menu", "order", "waiter"],
            essential_phrases={
                "beginner": ["I want", "Please"],
                "intermediate": ["I would like", "Could I have"],
            },
            cultural_context={"tipping": "customary"},
            learning_objectives=["Order food", "Pay bill"],
            conversation_starters=["Hello, table for two?"],
            scenario_variations=[{"setting": "fast_food"}, {"setting": "fine_dining"}],
            difficulty_modifiers={"beginner": {"vocabulary_limit": 50}},
            success_metrics=["Complete order", "Use phrases"],
        )

        assert template.template_id == "template_1"
        assert template.tier == 1
        assert len(template.scenario_variations) == 2
        assert len(template.difficulty_modifiers) == 1
        assert len(template.success_metrics) == 2

    def test_universal_scenario_template_with_none_optional_fields(self):
        """Test UniversalScenarioTemplate __post_init__ initializes None fields"""
        template = UniversalScenarioTemplate(
            template_id="template_2",
            name="Travel Template",
            category=ScenarioCategory.TRAVEL,
            tier=2,
            base_vocabulary=["ticket", "gate"],
            essential_phrases={"beginner": ["Where is"]},
            cultural_context={},
            learning_objectives=["Navigate airport"],
            conversation_starters=["Excuse me"],
            scenario_variations=None,  # Should be initialized to []
            difficulty_modifiers=None,  # Should be initialized to {}
            success_metrics=None,  # Should be initialized to []
        )

        assert isinstance(template.scenario_variations, list)
        assert len(template.scenario_variations) == 0
        assert isinstance(template.difficulty_modifiers, dict)
        assert len(template.difficulty_modifiers) == 0
        assert isinstance(template.success_metrics, list)
        assert len(template.success_metrics) == 0

    def test_universal_scenario_template_without_optional_fields(self):
        """Test UniversalScenarioTemplate creation without optional fields"""
        template = UniversalScenarioTemplate(
            template_id="template_3",
            name="Shopping Template",
            category=ScenarioCategory.SHOPPING,
            tier=3,
            base_vocabulary=["price", "buy"],
            essential_phrases={"beginner": ["How much"]},
            cultural_context={},
            learning_objectives=["Purchase item"],
            conversation_starters=["Can I help you?"],
        )

        # All optional fields should be initialized
        assert isinstance(template.scenario_variations, list)
        assert isinstance(template.difficulty_modifiers, dict)
        assert isinstance(template.success_metrics, list)


class TestDataclassIntegration:
    """Test dataclasses work together correctly"""

    def test_complete_scenario_creation_flow(self):
        """Test creating a complete scenario with all components"""
        # Create phases
        phase1 = ScenarioPhase(
            phase_id="intro",
            name="Introduction",
            description="Meet and greet",
            expected_duration_minutes=5,
            key_vocabulary=["hello", "name"],
            essential_phrases=["My name is"],
            learning_objectives=["Introduce yourself"],
        )

        phase2 = ScenarioPhase(
            phase_id="main",
            name="Main Conversation",
            description="Main interaction",
            expected_duration_minutes=15,
            key_vocabulary=["discuss", "opinion"],
            essential_phrases=["I think that"],
            learning_objectives=["Express opinions"],
            success_criteria=["Use at least 3 opinions"],
        )

        # Create scenario
        scenario = ConversationScenario(
            scenario_id="full_scenario",
            name="Coffee Chat",
            category=ScenarioCategory.SOCIAL,
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            description="Casual conversation over coffee",
            user_role=ConversationRole.FRIEND,
            ai_role=ConversationRole.FRIEND,
            setting="Coffee shop",
            duration_minutes=20,
            phases=[phase1, phase2],
            vocabulary_focus=["conversation", "opinions"],
            cultural_context={"formality": "informal"},
            learning_goals=["Casual conversation skills"],
        )

        # Create progress
        progress = ScenarioProgress(
            scenario_id=scenario.scenario_id,
            user_id="user_test",
            current_phase=1,
            phase_progress={"intro": 1.0, "main": 0.5},
            vocabulary_mastered=["hello", "name"],
            objectives_completed=["Introduce yourself"],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            total_attempts=1,
            success_rate=0.8,
        )

        # Verify integration
        assert len(scenario.phases) == 2
        assert progress.scenario_id == scenario.scenario_id
        assert progress.current_phase < len(scenario.phases)
        assert "intro" in progress.phase_progress

    def test_template_based_scenario_creation(self):
        """Test creating scenarios from templates"""
        template = UniversalScenarioTemplate(
            template_id="emergency_template",
            name="Emergency Situations",
            category=ScenarioCategory.EMERGENCY,
            tier=1,
            base_vocabulary=["help", "emergency", "doctor"],
            essential_phrases={
                "beginner": ["I need help", "Call doctor"],
                "advanced": ["I require medical assistance"],
            },
            cultural_context={"emergency_number": "911"},
            learning_objectives=["Handle emergencies"],
            conversation_starters=["Help!", "Emergency!"],
            scenario_variations=[
                {"type": "medical"},
                {"type": "accident"},
            ],
        )

        # Verify template can be used to create scenarios
        assert template.category == ScenarioCategory.EMERGENCY
        assert len(template.scenario_variations) == 2
        assert "beginner" in template.essential_phrases
        assert "advanced" in template.essential_phrases
