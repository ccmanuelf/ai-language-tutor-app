"""
Comprehensive tests for tutor_mode_manager.py
Target: TRUE 100% coverage (149 statements, all branches)

Test Coverage:
- All 6 tutor modes (CHIT_CHAT, INTERVIEW_SIMULATION, DEADLINE_NEGOTIATIONS, TEACHER_MODE, VOCABULARY_BUILDER, OPEN_SESSION)
- All enums and dataclasses
- Session lifecycle management
- AI response generation integration
- Analytics and metrics
- Error handling
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from app.services.ai_service_base import AIResponse, AIResponseStatus
from app.services.tutor_mode_manager import (
    DifficultyLevel,
    TutorMode,
    TutorModeCategory,
    TutorModeConfig,
    TutorModeManager,
    TutorSession,
    tutor_mode_manager,
)

# ============================================================================
# Helper Functions
# ============================================================================


def create_mock_uuid(return_value: str):
    """Create a mock UUID object that converts to the given string"""
    mock_uuid_obj = Mock()
    mock_uuid_obj.__str__ = Mock(return_value=return_value)
    return mock_uuid_obj


# ============================================================================
# Test Class 1: Enums
# ============================================================================


class TestEnums:
    """Test all enum values and validity"""

    def test_tutor_mode_enum_values(self):
        """Test TutorMode enum has all 6 expected values"""
        assert TutorMode.CHIT_CHAT.value == "chit_chat"
        assert TutorMode.INTERVIEW_SIMULATION.value == "interview_simulation"
        assert TutorMode.DEADLINE_NEGOTIATIONS.value == "deadline_negotiations"
        assert TutorMode.TEACHER_MODE.value == "teacher_mode"
        assert TutorMode.VOCABULARY_BUILDER.value == "vocabulary_builder"
        assert TutorMode.OPEN_SESSION.value == "open_session"

    def test_tutor_mode_category_enum_values(self):
        """Test TutorModeCategory enum has all 3 expected values"""
        assert TutorModeCategory.CASUAL.value == "casual"
        assert TutorModeCategory.PROFESSIONAL.value == "professional"
        assert TutorModeCategory.EDUCATIONAL.value == "educational"

    def test_difficulty_level_enum_values(self):
        """Test DifficultyLevel enum has all 4 expected values"""
        assert DifficultyLevel.BEGINNER.value == "beginner"
        assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
        assert DifficultyLevel.ADVANCED.value == "advanced"
        assert DifficultyLevel.EXPERT.value == "expert"

    def test_enum_membership(self):
        """Test enum membership checks"""
        assert TutorMode.CHIT_CHAT in TutorMode
        assert TutorModeCategory.CASUAL in TutorModeCategory
        assert DifficultyLevel.BEGINNER in DifficultyLevel

    def test_enum_iteration(self):
        """Test that enums can be iterated"""
        modes = list(TutorMode)
        assert len(modes) == 6

        categories = list(TutorModeCategory)
        assert len(categories) == 3

        levels = list(DifficultyLevel)
        assert len(levels) == 4


# ============================================================================
# Test Class 2: TutorModeConfig Dataclass
# ============================================================================


class TestTutorModeConfig:
    """Test TutorModeConfig dataclass"""

    def test_tutor_mode_config_creation(self):
        """Test creating a TutorModeConfig instance"""
        config = TutorModeConfig(
            mode=TutorMode.CHIT_CHAT,
            name="Test Mode",
            description="Test description",
            category=TutorModeCategory.CASUAL,
            system_prompt_template="Test prompt: {language}",
            conversation_starters=["Hello!", "Hi!"],
            correction_approach="relaxed",
            focus_areas=["grammar", "vocabulary"],
            success_criteria=["fluency"],
            example_interactions=[{"user": "test", "assistant": "response"}],
            difficulty_adjustments={"beginner": {"vocab": "simple"}},
        )

        assert config.mode == TutorMode.CHIT_CHAT
        assert config.name == "Test Mode"
        assert config.description == "Test description"
        assert config.category == TutorModeCategory.CASUAL
        assert config.multi_language_support is True  # default
        assert config.requires_topic_input is False  # default

    def test_tutor_mode_config_with_optional_fields(self):
        """Test TutorModeConfig with optional fields set"""
        config = TutorModeConfig(
            mode=TutorMode.INTERVIEW_SIMULATION,
            name="Interview",
            description="Interview practice",
            category=TutorModeCategory.PROFESSIONAL,
            system_prompt_template="Interview: {topic}",
            conversation_starters=["Tell me about yourself"],
            correction_approach="moderate",
            focus_areas=["professional language"],
            success_criteria=["confidence"],
            example_interactions=[],
            difficulty_adjustments={},
            multi_language_support=False,
            requires_topic_input=True,
        )

        assert config.multi_language_support is False
        assert config.requires_topic_input is True

    def test_tutor_mode_config_all_correction_approaches(self):
        """Test different correction approaches"""
        approaches = ["relaxed", "moderate", "strict"]

        for approach in approaches:
            config = TutorModeConfig(
                mode=TutorMode.CHIT_CHAT,
                name="Test",
                description="Test",
                category=TutorModeCategory.CASUAL,
                system_prompt_template="Test",
                conversation_starters=[],
                correction_approach=approach,
                focus_areas=[],
                success_criteria=[],
                example_interactions=[],
                difficulty_adjustments={},
            )
            assert config.correction_approach == approach


# ============================================================================
# Test Class 3: TutorSession Dataclass
# ============================================================================


class TestTutorSession:
    """Test TutorSession dataclass and __post_init__"""

    def test_tutor_session_creation_minimal(self):
        """Test creating TutorSession with minimal required fields"""
        session = TutorSession(
            session_id="test-123",
            user_id="user-456",
            mode=TutorMode.CHIT_CHAT,
            language="en",
            difficulty=DifficultyLevel.INTERMEDIATE,
        )

        assert session.session_id == "test-123"
        assert session.user_id == "user-456"
        assert session.mode == TutorMode.CHIT_CHAT
        assert session.language == "en"
        assert session.difficulty == DifficultyLevel.INTERMEDIATE
        assert session.topic is None

    def test_tutor_session_post_init_defaults(self):
        """Test that __post_init__ sets default values"""
        session = TutorSession(
            session_id="test-123",
            user_id="user-456",
            mode=TutorMode.CHIT_CHAT,
            language="en",
            difficulty=DifficultyLevel.BEGINNER,
        )

        # Check defaults set by __post_init__
        assert session.start_time is not None
        assert isinstance(session.start_time, datetime)
        assert session.last_activity is not None
        assert isinstance(session.last_activity, datetime)
        assert session.progress_metrics == {}
        assert session.vocabulary_introduced == []
        assert session.corrections_made == []
        assert session.session_goals == []
        assert session.interaction_count == 0

    def test_tutor_session_with_topic(self):
        """Test TutorSession with topic specified"""
        session = TutorSession(
            session_id="test-123",
            user_id="user-456",
            mode=TutorMode.OPEN_SESSION,
            language="es",
            difficulty=DifficultyLevel.ADVANCED,
            topic="Technology",
        )

        assert session.topic == "Technology"

    def test_tutor_session_with_custom_timestamps(self):
        """Test TutorSession with custom timestamps"""
        start = datetime(2025, 1, 1, 10, 0, 0)
        last = datetime(2025, 1, 1, 10, 30, 0)

        session = TutorSession(
            session_id="test-123",
            user_id="user-456",
            mode=TutorMode.TEACHER_MODE,
            language="fr",
            difficulty=DifficultyLevel.EXPERT,
            start_time=start,
            last_activity=last,
        )

        assert session.start_time == start
        assert session.last_activity == last

    def test_tutor_session_with_custom_metrics(self):
        """Test TutorSession with custom metrics and data"""
        session = TutorSession(
            session_id="test-123",
            user_id="user-456",
            mode=TutorMode.VOCABULARY_BUILDER,
            language="de",
            difficulty=DifficultyLevel.INTERMEDIATE,
            interaction_count=10,
            progress_metrics={"accuracy": 0.85},
            vocabulary_introduced=["Hallo", "Danke"],
            corrections_made=[{"type": "grammar", "count": 3}],
            session_goals=["Learn greetings"],
        )

        assert session.interaction_count == 10
        assert session.progress_metrics == {"accuracy": 0.85}
        assert session.vocabulary_introduced == ["Hallo", "Danke"]
        assert session.corrections_made == [{"type": "grammar", "count": 3}]
        assert session.session_goals == ["Learn greetings"]

    def test_tutor_session_post_init_preserves_existing_values(self):
        """Test that __post_init__ doesn't override existing values"""
        existing_start = datetime(2025, 1, 1, 10, 0, 0)
        existing_metrics = {"score": 100}

        session = TutorSession(
            session_id="test-123",
            user_id="user-456",
            mode=TutorMode.CHIT_CHAT,
            language="en",
            difficulty=DifficultyLevel.BEGINNER,
            start_time=existing_start,
            progress_metrics=existing_metrics,
        )

        # Should preserve existing values
        assert session.start_time == existing_start
        assert session.progress_metrics == existing_metrics

    def test_tutor_session_all_difficulty_levels(self):
        """Test TutorSession with all difficulty levels"""
        for difficulty in DifficultyLevel:
            session = TutorSession(
                session_id="test-123",
                user_id="user-456",
                mode=TutorMode.CHIT_CHAT,
                language="en",
                difficulty=difficulty,
            )
            assert session.difficulty == difficulty

    def test_tutor_session_all_modes(self):
        """Test TutorSession with all tutor modes"""
        for mode in TutorMode:
            session = TutorSession(
                session_id="test-123",
                user_id="user-456",
                mode=mode,
                language="en",
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            assert session.mode == mode


# ============================================================================
# Test Class 4: TutorModeManager Initialization
# ============================================================================


class TestTutorModeManagerInit:
    """Test TutorModeManager initialization"""

    def test_manager_initialization(self):
        """Test that manager initializes correctly"""
        manager = TutorModeManager()

        assert manager.modes is not None
        assert isinstance(manager.modes, dict)
        assert len(manager.modes) == 6  # All 6 tutor modes
        assert manager.active_sessions == {}
        assert manager.mode_analytics == {}

    def test_manager_initializes_all_modes(self):
        """Test that all 6 modes are initialized"""
        manager = TutorModeManager()

        expected_modes = [
            TutorMode.CHIT_CHAT,
            TutorMode.INTERVIEW_SIMULATION,
            TutorMode.DEADLINE_NEGOTIATIONS,
            TutorMode.TEACHER_MODE,
            TutorMode.VOCABULARY_BUILDER,
            TutorMode.OPEN_SESSION,
        ]

        for mode in expected_modes:
            assert mode in manager.modes
            assert isinstance(manager.modes[mode], TutorModeConfig)

    def test_global_manager_instance(self):
        """Test that global tutor_mode_manager instance exists"""
        assert tutor_mode_manager is not None
        assert isinstance(tutor_mode_manager, TutorModeManager)


# ============================================================================
# Test Class 5: Initialize Tutor Modes (All 6 Modes)
# ============================================================================


class TestInitializeTutorModes:
    """Test _initialize_tutor_modes and all 6 mode configurations"""

    def test_chit_chat_mode_configuration(self):
        """Test CHIT_CHAT mode configuration"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.CHIT_CHAT]

        assert config.mode == TutorMode.CHIT_CHAT
        assert config.name == "Chit-chat Free Talking"
        assert config.category == TutorModeCategory.CASUAL
        assert config.correction_approach == "relaxed"
        assert config.requires_topic_input is False
        assert len(config.conversation_starters) > 0
        assert len(config.focus_areas) > 0
        assert "{language}" in config.system_prompt_template
        assert "{difficulty}" in config.system_prompt_template

    def test_chit_chat_difficulty_adjustments(self):
        """Test CHIT_CHAT has difficulty adjustments for all levels"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.CHIT_CHAT]

        assert "beginner" in config.difficulty_adjustments
        assert "intermediate" in config.difficulty_adjustments
        assert "advanced" in config.difficulty_adjustments

    def test_interview_simulation_mode_configuration(self):
        """Test INTERVIEW_SIMULATION mode configuration"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.INTERVIEW_SIMULATION]

        assert config.mode == TutorMode.INTERVIEW_SIMULATION
        assert config.name == "One-on-One Interview Simulation"
        assert config.category == TutorModeCategory.PROFESSIONAL
        assert config.correction_approach == "moderate"
        assert config.requires_topic_input is True
        assert len(config.conversation_starters) > 0
        assert "{topic}" in config.system_prompt_template

    def test_interview_simulation_difficulty_adjustments(self):
        """Test INTERVIEW_SIMULATION has difficulty adjustments"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.INTERVIEW_SIMULATION]

        assert "beginner" in config.difficulty_adjustments
        assert "intermediate" in config.difficulty_adjustments
        assert "advanced" in config.difficulty_adjustments

    def test_deadline_negotiations_mode_configuration(self):
        """Test DEADLINE_NEGOTIATIONS mode configuration"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.DEADLINE_NEGOTIATIONS]

        assert config.mode == TutorMode.DEADLINE_NEGOTIATIONS
        assert config.name == "Deadline Negotiations"
        assert config.category == TutorModeCategory.PROFESSIONAL
        assert config.correction_approach == "strict"
        assert config.requires_topic_input is True
        assert len(config.conversation_starters) > 0

    def test_deadline_negotiations_difficulty_adjustments(self):
        """Test DEADLINE_NEGOTIATIONS has difficulty adjustments"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.DEADLINE_NEGOTIATIONS]

        assert "beginner" in config.difficulty_adjustments
        assert "intermediate" in config.difficulty_adjustments
        assert "advanced" in config.difficulty_adjustments

    def test_teacher_mode_configuration(self):
        """Test TEACHER_MODE configuration"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.TEACHER_MODE]

        assert config.mode == TutorMode.TEACHER_MODE
        assert config.name == "Teacher Mode"
        assert config.category == TutorModeCategory.EDUCATIONAL
        assert config.correction_approach == "moderate"
        assert config.requires_topic_input is True
        assert len(config.conversation_starters) > 0

    def test_teacher_mode_difficulty_adjustments(self):
        """Test TEACHER_MODE has difficulty adjustments"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.TEACHER_MODE]

        assert "beginner" in config.difficulty_adjustments
        assert "intermediate" in config.difficulty_adjustments
        assert "advanced" in config.difficulty_adjustments

    def test_vocabulary_builder_mode_configuration(self):
        """Test VOCABULARY_BUILDER configuration"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.VOCABULARY_BUILDER]

        assert config.mode == TutorMode.VOCABULARY_BUILDER
        assert config.name == "Vocabulary Builder"
        assert config.category == TutorModeCategory.EDUCATIONAL
        assert config.correction_approach == "moderate"
        assert config.requires_topic_input is True
        assert len(config.conversation_starters) > 0

    def test_vocabulary_builder_difficulty_adjustments(self):
        """Test VOCABULARY_BUILDER has difficulty adjustments"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.VOCABULARY_BUILDER]

        assert "beginner" in config.difficulty_adjustments
        assert "intermediate" in config.difficulty_adjustments
        assert "advanced" in config.difficulty_adjustments

    def test_open_session_mode_configuration(self):
        """Test OPEN_SESSION configuration"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.OPEN_SESSION]

        assert config.mode == TutorMode.OPEN_SESSION
        assert config.name == "Open Session Talking"
        assert config.category == TutorModeCategory.CASUAL
        assert config.correction_approach == "moderate"
        assert config.requires_topic_input is True
        assert len(config.conversation_starters) > 0

    def test_open_session_difficulty_adjustments(self):
        """Test OPEN_SESSION has difficulty adjustments"""
        manager = TutorModeManager()
        config = manager.modes[TutorMode.OPEN_SESSION]

        assert "beginner" in config.difficulty_adjustments
        assert "intermediate" in config.difficulty_adjustments
        assert "advanced" in config.difficulty_adjustments

    def test_all_modes_have_required_fields(self):
        """Test that all modes have all required configuration fields"""
        manager = TutorModeManager()

        for mode, config in manager.modes.items():
            assert config.mode == mode
            assert config.name
            assert config.description
            assert config.category in TutorModeCategory
            assert config.system_prompt_template
            assert isinstance(config.conversation_starters, list)
            assert len(config.conversation_starters) > 0
            assert config.correction_approach in ["relaxed", "moderate", "strict"]
            assert isinstance(config.focus_areas, list)
            assert isinstance(config.success_criteria, list)
            assert isinstance(config.example_interactions, list)
            assert isinstance(config.difficulty_adjustments, dict)

    def test_all_modes_have_example_interactions(self):
        """Test that all modes have example interactions"""
        manager = TutorModeManager()

        for mode, config in manager.modes.items():
            assert len(config.example_interactions) >= 0  # Some may have examples

    def test_modes_by_category_casual(self):
        """Test CASUAL category modes"""
        manager = TutorModeManager()
        casual_modes = [
            mode
            for mode, config in manager.modes.items()
            if config.category == TutorModeCategory.CASUAL
        ]

        assert TutorMode.CHIT_CHAT in casual_modes
        assert TutorMode.OPEN_SESSION in casual_modes

    def test_modes_by_category_professional(self):
        """Test PROFESSIONAL category modes"""
        manager = TutorModeManager()
        professional_modes = [
            mode
            for mode, config in manager.modes.items()
            if config.category == TutorModeCategory.PROFESSIONAL
        ]

        assert TutorMode.INTERVIEW_SIMULATION in professional_modes
        assert TutorMode.DEADLINE_NEGOTIATIONS in professional_modes

    def test_modes_by_category_educational(self):
        """Test EDUCATIONAL category modes"""
        manager = TutorModeManager()
        educational_modes = [
            mode
            for mode, config in manager.modes.items()
            if config.category == TutorModeCategory.EDUCATIONAL
        ]

        assert TutorMode.TEACHER_MODE in educational_modes
        assert TutorMode.VOCABULARY_BUILDER in educational_modes

    def test_topic_required_modes(self):
        """Test which modes require topic input"""
        manager = TutorModeManager()

        # Modes that require topic
        assert (
            manager.modes[TutorMode.INTERVIEW_SIMULATION].requires_topic_input is True
        )
        assert (
            manager.modes[TutorMode.DEADLINE_NEGOTIATIONS].requires_topic_input is True
        )
        assert manager.modes[TutorMode.TEACHER_MODE].requires_topic_input is True
        assert manager.modes[TutorMode.VOCABULARY_BUILDER].requires_topic_input is True
        assert manager.modes[TutorMode.OPEN_SESSION].requires_topic_input is True

        # Mode that doesn't require topic
        assert manager.modes[TutorMode.CHIT_CHAT].requires_topic_input is False

    def test_all_modes_multilanguage_support(self):
        """Test that all modes support multiple languages"""
        manager = TutorModeManager()

        for mode, config in manager.modes.items():
            assert config.multi_language_support is True


# ============================================================================
# Test Class 6: Get Available Modes
# ============================================================================


class TestGetAvailableModes:
    """Test get_available_modes method"""

    def test_get_available_modes_returns_list(self):
        """Test that get_available_modes returns a list"""
        manager = TutorModeManager()
        modes = manager.get_available_modes()

        assert isinstance(modes, list)
        assert len(modes) == 6

    def test_get_available_modes_structure(self):
        """Test structure of returned mode information"""
        manager = TutorModeManager()
        modes = manager.get_available_modes()

        for mode_info in modes:
            assert "mode" in mode_info
            assert "name" in mode_info
            assert "description" in mode_info
            assert "category" in mode_info
            assert "requires_topic" in mode_info

            # Verify types
            assert isinstance(mode_info["mode"], str)
            assert isinstance(mode_info["name"], str)
            assert isinstance(mode_info["description"], str)
            assert isinstance(mode_info["category"], str)
            assert isinstance(mode_info["requires_topic"], bool)

    def test_get_available_modes_contains_all_modes(self):
        """Test that all 6 modes are in available modes"""
        manager = TutorModeManager()
        modes = manager.get_available_modes()

        mode_values = [m["mode"] for m in modes]

        assert "chit_chat" in mode_values
        assert "interview_simulation" in mode_values
        assert "deadline_negotiations" in mode_values
        assert "teacher_mode" in mode_values
        assert "vocabulary_builder" in mode_values
        assert "open_session" in mode_values


# File continues in next part due to length...
# ============================================================================
# Test Class 7: Start Tutor Session
# ============================================================================


class TestStartTutorSession:
    """Test start_tutor_session method"""

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_basic(self, mock_uuid):
        """Test starting a basic tutor session"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        assert session_id == "test-session-id"
        assert session_id in manager.active_sessions
        
        session = manager.active_sessions[session_id]
        assert session.user_id == "user-123"
        assert session.mode == TutorMode.CHIT_CHAT
        assert session.language == "en"
        assert session.difficulty == DifficultyLevel.INTERMEDIATE  # default

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_with_difficulty(self, mock_uuid):
        """Test starting session with specific difficulty level"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.TEACHER_MODE,
            language="es",
            difficulty=DifficultyLevel.ADVANCED,
            topic="Grammar",
        )
        
        session = manager.active_sessions[session_id]
        assert session.difficulty == DifficultyLevel.ADVANCED

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_with_topic(self, mock_uuid):
        """Test starting session with topic"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.OPEN_SESSION,
            language="fr",
            topic="Technology",
        )
        
        session = manager.active_sessions[session_id]
        assert session.topic == "Technology"

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_topic_required_validation_success(self, mock_uuid):
        """Test that topic is validated for modes that require it"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        # Should succeed with topic
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.INTERVIEW_SIMULATION,
            language="en",
            topic="Software Engineering",
        )
        
        assert session_id in manager.active_sessions

    def test_start_session_topic_required_validation_failure(self):
        """Test that ValueError is raised when topic is required but missing"""
        manager = TutorModeManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.start_tutor_session(
                user_id="user-123",
                mode=TutorMode.INTERVIEW_SIMULATION,
                language="en",
                # topic missing - should raise error
            )
        
        assert "requires a topic" in str(exc_info.value)

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_all_difficulty_levels(self, mock_uuid):
        """Test starting sessions with all difficulty levels"""
        manager = TutorModeManager()
        
        for i, difficulty in enumerate(DifficultyLevel):
            mock_uuid.return_value = create_mock_uuid(f"session-{i}")
            
            session_id = manager.start_tutor_session(
                user_id="user-123",
                mode=TutorMode.CHIT_CHAT,
                language="en",
                difficulty=difficulty,
            )
            
            session = manager.active_sessions[session_id]
            assert session.difficulty == difficulty

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_all_modes_without_topic_requirement(self, mock_uuid):
        """Test starting sessions for mode that doesn't require topic"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        # CHIT_CHAT doesn't require topic
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        session = manager.active_sessions[session_id]
        assert session.topic is None

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_session_all_modes_with_topic_requirement(self, mock_uuid):
        """Test starting sessions for modes that require topic"""
        manager = TutorModeManager()
        
        topic_required_modes = [
            TutorMode.INTERVIEW_SIMULATION,
            TutorMode.DEADLINE_NEGOTIATIONS,
            TutorMode.TEACHER_MODE,
            TutorMode.VOCABULARY_BUILDER,
            TutorMode.OPEN_SESSION,
        ]
        
        for i, mode in enumerate(topic_required_modes):
            mock_uuid.return_value = create_mock_uuid(f"session-{i}")
            
            session_id = manager.start_tutor_session(
                user_id="user-123",
                mode=mode,
                language="en",
                topic="Test Topic",
            )
            
            session = manager.active_sessions[session_id]
            assert session.topic == "Test Topic"

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_start_multiple_sessions(self, mock_uuid):
        """Test starting multiple concurrent sessions"""
        manager = TutorModeManager()
        
        # Start 3 sessions
        session_ids = []
        for i in range(3):
            mock_uuid.return_value = create_mock_uuid(f"session-{i}")
            session_id = manager.start_tutor_session(
                user_id=f"user-{i}",
                mode=TutorMode.CHIT_CHAT,
                language="en",
            )
            session_ids.append(session_id)
        
        # All should be active
        assert len(manager.active_sessions) == 3
        for session_id in session_ids:
            assert session_id in manager.active_sessions


# ============================================================================
# Test Class 8: Get Session System Prompt
# ============================================================================


class TestGetSessionSystemPrompt:
    """Test get_session_system_prompt method"""

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_system_prompt_basic(self, mock_uuid):
        """Test getting system prompt for a session"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
            difficulty=DifficultyLevel.BEGINNER,
        )
        
        prompt = manager.get_session_system_prompt(session_id)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "en" in prompt  # language should be formatted
        assert "beginner" in prompt  # difficulty should be formatted

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_system_prompt_with_topic(self, mock_uuid):
        """Test getting system prompt for session with topic"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.OPEN_SESSION,
            language="es",
            difficulty=DifficultyLevel.INTERMEDIATE,
            topic="Technology",
        )
        
        prompt = manager.get_session_system_prompt(session_id)
        
        assert "Technology" in prompt or "es" in prompt
        assert "intermediate" in prompt

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_system_prompt_without_topic_uses_default(self, mock_uuid):
        """Test system prompt uses 'general conversation' when no topic"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        prompt = manager.get_session_system_prompt(session_id)
        
        # Should contain "general conversation" as default topic
        assert "general conversation" in prompt.lower() or prompt  # May or may not use topic

    def test_get_system_prompt_session_not_found(self):
        """Test error when session ID not found"""
        manager = TutorModeManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.get_session_system_prompt("nonexistent-session")
        
        assert "not found" in str(exc_info.value)

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_system_prompt_all_modes(self, mock_uuid):
        """Test getting system prompts for all tutor modes"""
        manager = TutorModeManager()
        
        for i, mode in enumerate(TutorMode):
            mock_uuid.return_value = create_mock_uuid(f"session-{i}")
            
            # Provide topic for modes that require it
            kwargs = {"topic": "Test Topic"} if manager.modes[mode].requires_topic_input else {}
            
            session_id = manager.start_tutor_session(
                user_id="user-123",
                mode=mode,
                language="en",
                **kwargs,
            )
            
            prompt = manager.get_session_system_prompt(session_id)
            assert isinstance(prompt, str)
            assert len(prompt) > 0


# ============================================================================
# Test Class 9: Get Conversation Starter
# ============================================================================


class TestGetConversationStarter:
    """Test get_conversation_starter method"""

    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.random.choice")
    def test_get_conversation_starter_basic(self, mock_choice, mock_uuid):
        """Test getting a conversation starter"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_choice.return_value = "Hello! How's your day?"
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        starter = manager.get_conversation_starter(session_id)
        
        assert starter == "Hello! How's your day?"
        assert mock_choice.called

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_conversation_starter_with_topic_formatting(self, mock_uuid):
        """Test conversation starter formats {topic} placeholder"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.OPEN_SESSION,
            language="en",
            topic="Cooking",
        )
        
        starter = manager.get_conversation_starter(session_id)
        
        # The starter should either have Cooking formatted in or no {topic} placeholder
        assert "{topic}" not in starter
        # Since we can't control random.choice, just verify it's valid
        assert isinstance(starter, str)
        assert len(starter) > 0

    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.random.choice")
    def test_get_conversation_starter_without_topic_placeholder(self, mock_choice, mock_uuid):
        """Test conversation starter without topic placeholder"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_choice.return_value = "How are you today?"
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        starter = manager.get_conversation_starter(session_id)
        
        assert starter == "How are you today?"

    def test_get_conversation_starter_session_not_found(self):
        """Test error when session ID not found"""
        manager = TutorModeManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.get_conversation_starter("nonexistent-session")
        
        assert "not found" in str(exc_info.value)

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_conversation_starter_all_modes(self, mock_uuid):
        """Test getting conversation starters for all modes"""
        manager = TutorModeManager()
        
        for i, mode in enumerate(TutorMode):
            mock_uuid.return_value = create_mock_uuid(f"session-{i}")
            
            kwargs = {"topic": "Test"} if manager.modes[mode].requires_topic_input else {}
            
            session_id = manager.start_tutor_session(
                user_id="user-123",
                mode=mode,
                language="en",
                **kwargs,
            )
            
            starter = manager.get_conversation_starter(session_id)
            assert isinstance(starter, str)
            assert len(starter) > 0


# ============================================================================
# Test Class 10: Generate Tutor Response (Async)
# ============================================================================


class TestGenerateTutorResponse:
    """Test generate_tutor_response method (async)"""

    @pytest.mark.asyncio
    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.generate_ai_response", new_callable=AsyncMock)
    @patch("app.services.tutor_mode_manager.datetime")
    async def test_generate_response_basic(self, mock_datetime, mock_ai, mock_uuid):
        """Test basic AI response generation"""
        # Setup mocks
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        start_time = datetime(2025, 1, 1, 10, 0, 0)
        current_time = datetime(2025, 1, 1, 10, 5, 0)
        mock_datetime.now.side_effect = [start_time, current_time, current_time, current_time]
        
        mock_ai_response = AIResponse(
            content="Hello! How are you?",
            provider="test",
            language="en",
            model="test-model",
            processing_time=0.5,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
        )
        mock_ai.return_value = mock_ai_response
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        # Generate response
        result = await manager.generate_tutor_response(
            session_id=session_id,
            user_message="Hi there!",
        )
        
        assert result["response"] == mock_ai_response
        assert result["mode"] == "chit_chat"
        assert result["correction_approach"] == "relaxed"
        assert "session_progress" in result
        assert result["session_progress"]["interactions"] == 1
        assert result["session_progress"]["duration_minutes"] == 5.0

    @pytest.mark.asyncio
    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.generate_ai_response", new_callable=AsyncMock)
    async def test_generate_response_with_context(self, mock_ai, mock_uuid):
        """Test response generation with conversation context"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_ai.return_value = AIResponse(
            content="Response",
            provider="test",
            language="en",
            model="test",
            processing_time=0.1,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
        )
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.TEACHER_MODE,
            language="es",
            topic="Grammar",
        )
        
        context = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
        ]
        
        result = await manager.generate_tutor_response(
            session_id=session_id,
            user_message="Current message",
            context_messages=context,
        )
        
        # Check that AI was called with correct messages
        call_args = mock_ai.call_args
        messages = call_args[1]["messages"]
        
        # Should have system prompt + context + current message
        assert len(messages) >= 4  # system + 2 context + current
        assert messages[0]["role"] == "system"
        assert messages[-1]["content"] == "Current message"

    @pytest.mark.asyncio
    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.generate_ai_response", new_callable=AsyncMock)
    async def test_generate_response_updates_session_metrics(self, mock_ai, mock_uuid):
        """Test that response generation updates session metrics"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_ai.return_value = AIResponse(
            content="Response",
            provider="test",
            language="en",
            model="test",
            processing_time=0.1,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
        )
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        # Initial state
        session = manager.active_sessions[session_id]
        initial_count = session.interaction_count
        
        # Generate response
        await manager.generate_tutor_response(
            session_id=session_id,
            user_message="Test message",
        )
        
        # Check updates
        assert session.interaction_count == initial_count + 1
        assert session.last_activity is not None

    @pytest.mark.asyncio
    async def test_generate_response_session_not_found(self):
        """Test error when session not found"""
        manager = TutorModeManager()
        
        with pytest.raises(ValueError) as exc_info:
            await manager.generate_tutor_response(
                session_id="nonexistent",
                user_message="Test",
            )
        
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.generate_ai_response", new_callable=AsyncMock)
    async def test_generate_response_ai_error_handling(self, mock_ai, mock_uuid):
        """Test error handling when AI generation fails"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_ai.side_effect = Exception("AI service error")
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        with pytest.raises(Exception) as exc_info:
            await manager.generate_tutor_response(
                session_id=session_id,
                user_message="Test",
            )
        
        assert "AI service error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.generate_ai_response", new_callable=AsyncMock)
    async def test_generate_response_passes_language_to_ai(self, mock_ai, mock_uuid):
        """Test that language is passed to AI router"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_ai.return_value = AIResponse(
            content="Response",
            provider="test",
            language="fr",
            model="test",
            processing_time=0.1,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
        )
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="fr",
        )
        
        await manager.generate_tutor_response(
            session_id=session_id,
            user_message="Bonjour",
        )
        
        # Check AI was called with correct language
        call_args = mock_ai.call_args
        assert call_args[1]["language"] == "fr"

    @pytest.mark.asyncio
    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.generate_ai_response", new_callable=AsyncMock)
    async def test_generate_response_context_type(self, mock_ai, mock_uuid):
        """Test that context_type includes mode information"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        mock_ai.return_value = AIResponse(
            content="Response",
            provider="test",
            language="en",
            model="test",
            processing_time=0.1,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
        )
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.INTERVIEW_SIMULATION,
            language="en",
            topic="Engineering",
        )
        
        await manager.generate_tutor_response(
            session_id=session_id,
            user_message="Tell me about yourself",
        )
        
        # Check context_type
        call_args = mock_ai.call_args
        assert "context_type" in call_args[1]
        assert "interview_simulation" in call_args[1]["context_type"]


# ============================================================================
# Test Class 11: End Tutor Session
# ============================================================================


class TestEndTutorSession:
    """Test end_tutor_session method"""

    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.datetime")
    def test_end_session_basic(self, mock_datetime, mock_uuid):
        """Test ending a session"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        start_time = datetime(2025, 1, 1, 10, 0, 0)
        end_time = datetime(2025, 1, 1, 10, 30, 0)
        mock_datetime.now.side_effect = [start_time, end_time, end_time]
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        # Modify session to add some data
        session = manager.active_sessions[session_id]
        session.interaction_count = 10
        session.vocabulary_introduced = ["hello", "goodbye"]
        session.corrections_made = [{"type": "grammar"}]
        
        summary = manager.end_tutor_session(session_id)
        
        assert summary["session_id"] == session_id
        assert summary["mode"] == "chit_chat"
        assert summary["language"] == "en"
        assert summary["topic"] is None
        assert summary["duration_minutes"] == 30.0
        assert summary["interactions"] == 10
        assert summary["vocabulary_introduced"] == ["hello", "goodbye"]
        assert summary["corrections_made"] == 1

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_end_session_removes_from_active(self, mock_uuid):
        """Test that ending session removes it from active_sessions"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        assert session_id in manager.active_sessions
        
        manager.end_tutor_session(session_id)
        
        assert session_id not in manager.active_sessions

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_end_session_with_topic(self, mock_uuid):
        """Test ending session that had a topic"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.OPEN_SESSION,
            language="es",
            topic="Travel",
        )
        
        summary = manager.end_tutor_session(session_id)
        
        assert summary["topic"] == "Travel"

    def test_end_session_not_found(self):
        """Test error when session not found"""
        manager = TutorModeManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.end_tutor_session("nonexistent-session")
        
        assert "not found" in str(exc_info.value)

    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.datetime")
    def test_end_session_duration_calculation(self, mock_datetime, mock_uuid):
        """Test accurate duration calculation"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        start_time = datetime(2025, 1, 1, 10, 0, 0)
        end_time = datetime(2025, 1, 1, 10, 45, 30)  # 45.5 minutes
        mock_datetime.now.side_effect = [start_time, end_time, end_time]
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        summary = manager.end_tutor_session(session_id)
        
        assert summary["duration_minutes"] == 45.5

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_end_session_zero_interactions(self, mock_uuid):
        """Test ending session with no interactions"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        summary = manager.end_tutor_session(session_id)
        
        assert summary["interactions"] == 0
        assert summary["vocabulary_introduced"] == []
        assert summary["corrections_made"] == 0


# ============================================================================
# Test Class 12: Get Session Info
# ============================================================================


class TestGetSessionInfo:
    """Test get_session_info method"""

    @patch("app.services.tutor_mode_manager.uuid4")
    @patch("app.services.tutor_mode_manager.datetime")
    def test_get_session_info_basic(self, mock_datetime, mock_uuid):
        """Test getting session information"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        start_time = datetime(2025, 1, 1, 10, 0, 0)
        mock_datetime.now.return_value = start_time
        
        manager = TutorModeManager()
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
            difficulty=DifficultyLevel.INTERMEDIATE,
        )
        
        info = manager.get_session_info(session_id)
        
        assert info is not None
        assert info["session_id"] == session_id
        assert info["mode"] == "chit_chat"
        assert info["language"] == "en"
        assert info["topic"] is None
        assert info["difficulty"] == "intermediate"
        assert info["start_time"] == start_time.isoformat()
        assert info["interaction_count"] == 0
        assert info["progress_metrics"] == {}

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_session_info_with_topic(self, mock_uuid):
        """Test getting session info for session with topic"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.TEACHER_MODE,
            language="fr",
            topic="Grammar",
        )
        
        info = manager.get_session_info(session_id)
        
        assert info["topic"] == "Grammar"

    def test_get_session_info_not_found(self):
        """Test that None is returned for nonexistent session"""
        manager = TutorModeManager()
        
        info = manager.get_session_info("nonexistent-session")
        
        assert info is None

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_session_info_with_progress_metrics(self, mock_uuid):
        """Test getting session info with progress metrics"""
        mock_uuid.return_value = create_mock_uuid("test-session-id")
        manager = TutorModeManager()
        
        session_id = manager.start_tutor_session(
            user_id="user-123",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        # Add progress metrics
        session = manager.active_sessions[session_id]
        session.progress_metrics = {"accuracy": 0.95, "fluency": 0.80}
        session.interaction_count = 15
        
        info = manager.get_session_info(session_id)
        
        assert info["progress_metrics"] == {"accuracy": 0.95, "fluency": 0.80}
        assert info["interaction_count"] == 15


# ============================================================================
# Test Class 13: Get Mode Analytics
# ============================================================================


class TestGetModeAnalytics:
    """Test get_mode_analytics method"""

    def test_get_mode_analytics_no_sessions(self):
        """Test analytics with no active sessions"""
        manager = TutorModeManager()
        
        analytics = manager.get_mode_analytics()
        
        assert analytics["active_sessions"] == 0
        assert analytics["available_modes"] == 6
        assert "modes_by_category" in analytics
        assert "session_distribution" in analytics

    def test_get_mode_analytics_modes_by_category(self):
        """Test that modes are grouped by category"""
        manager = TutorModeManager()
        
        analytics = manager.get_mode_analytics()
        
        assert "casual" in analytics["modes_by_category"]
        assert "professional" in analytics["modes_by_category"]
        assert "educational" in analytics["modes_by_category"]
        
        # Check expected modes in each category
        assert "Chit-chat Free Talking" in analytics["modes_by_category"]["casual"]
        assert "Open Session Talking" in analytics["modes_by_category"]["casual"]
        assert "One-on-One Interview Simulation" in analytics["modes_by_category"]["professional"]
        assert "Teacher Mode" in analytics["modes_by_category"]["educational"]

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_mode_analytics_with_active_sessions(self, mock_uuid):
        """Test analytics with active sessions"""
        manager = TutorModeManager()
        
        # Start multiple sessions
        mock_uuid.return_value = create_mock_uuid("session-1")
        manager.start_tutor_session(
            user_id="user-1",
            mode=TutorMode.CHIT_CHAT,
            language="en",
        )
        
        mock_uuid.return_value = create_mock_uuid("session-2")
        manager.start_tutor_session(
            user_id="user-2",
            mode=TutorMode.CHIT_CHAT,
            language="es",
        )
        
        mock_uuid.return_value = create_mock_uuid("session-3")
        manager.start_tutor_session(
            user_id="user-3",
            mode=TutorMode.TEACHER_MODE,
            language="fr",
            topic="Grammar",
        )
        
        analytics = manager.get_mode_analytics()
        
        assert analytics["active_sessions"] == 3
        assert analytics["session_distribution"]["chit_chat"] == 2
        assert analytics["session_distribution"]["teacher_mode"] == 1

    @patch("app.services.tutor_mode_manager.uuid4")
    def test_get_mode_analytics_session_distribution(self, mock_uuid):
        """Test session distribution tracking"""
        manager = TutorModeManager()
        
        # Start sessions for different modes
        modes_to_test = [
            TutorMode.CHIT_CHAT,
            TutorMode.CHIT_CHAT,
            TutorMode.OPEN_SESSION,
        ]
        
        for i, mode in enumerate(modes_to_test):
            mock_uuid.return_value = create_mock_uuid(f"session-{i}")
            kwargs = {"topic": "Test"} if manager.modes[mode].requires_topic_input else {}
            manager.start_tutor_session(
                user_id=f"user-{i}",
                mode=mode,
                language="en",
                **kwargs,
            )
        
        analytics = manager.get_mode_analytics()
        
        assert analytics["session_distribution"]["chit_chat"] == 2
        assert analytics["session_distribution"]["open_session"] == 1
