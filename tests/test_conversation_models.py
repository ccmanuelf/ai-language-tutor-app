"""
Comprehensive tests for conversation_models.py

Tests all dataclass models, enums, and __post_init__ methods to achieve 100% coverage.
Focus: Cover the missing line 172 (ConversationMessage metadata initialization)
"""

from datetime import datetime

import pytest

from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    ConversationStatus,
    LearningFocus,
    LearningInsight,
    MessageRole,
)


class TestConversationEnums:
    """Test all conversation enum definitions"""

    def test_conversation_status_enum(self):
        """Test ConversationStatus enum has all expected values"""
        assert ConversationStatus.ACTIVE.value == "active"
        assert ConversationStatus.PAUSED.value == "paused"
        assert ConversationStatus.COMPLETED.value == "completed"
        assert ConversationStatus.ARCHIVED.value == "archived"

    def test_message_role_enum(self):
        """Test MessageRole enum has all expected values"""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"

    def test_learning_focus_enum(self):
        """Test LearningFocus enum has all expected values"""
        assert LearningFocus.CONVERSATION.value == "conversation"
        assert LearningFocus.GRAMMAR.value == "grammar"
        assert LearningFocus.VOCABULARY.value == "vocabulary"
        assert LearningFocus.PRONUNCIATION.value == "pronunciation"
        assert LearningFocus.READING.value == "reading"
        assert LearningFocus.WRITING.value == "writing"


class TestConversationContext:
    """Test ConversationContext dataclass"""

    def test_conversation_context_with_all_fields(self):
        """Test ConversationContext creation with all fields provided"""
        now = datetime.now()
        context = ConversationContext(
            conversation_id="conv_001",
            user_id="user_123",
            language="es",
            learning_focus=LearningFocus.CONVERSATION,
            current_topic="Travel",
            vocabulary_level="intermediate",
            learning_goals=["Practice greetings", "Learn directions"],
            mistakes_tracked=[{"error": "pronunciation", "correction": "hola"}],
            vocabulary_introduced=["hola", "adiós"],
            session_start_time=now,
            last_activity=now,
            is_scenario_based=True,
            scenario_id="travel_001",
            scenario_progress_id="progress_001",
            scenario_phase="greeting",
        )

        assert context.conversation_id == "conv_001"
        assert context.language == "es"
        assert len(context.learning_goals) == 2
        assert context.is_scenario_based is True

    def test_conversation_context_with_none_optional_fields(self):
        """Test ConversationContext __post_init__ initializes None fields"""
        context = ConversationContext(
            conversation_id="conv_002",
            user_id="user_456",
            language="fr",
            learning_focus=LearningFocus.GRAMMAR,
            learning_goals=None,  # Should be initialized to []
            mistakes_tracked=None,  # Should be initialized to []
            vocabulary_introduced=None,  # Should be initialized to []
            session_start_time=None,  # Should be initialized to now
            last_activity=None,  # Should be initialized to now
        )

        assert isinstance(context.learning_goals, list)
        assert len(context.learning_goals) == 0
        assert isinstance(context.mistakes_tracked, list)
        assert len(context.mistakes_tracked) == 0
        assert isinstance(context.vocabulary_introduced, list)
        assert len(context.vocabulary_introduced) == 0
        assert isinstance(context.session_start_time, datetime)
        assert isinstance(context.last_activity, datetime)

    def test_conversation_context_without_optional_fields(self):
        """Test ConversationContext creation without optional fields"""
        context = ConversationContext(
            conversation_id="conv_003",
            user_id="user_789",
            language="de",
            learning_focus=LearningFocus.VOCABULARY,
        )

        # All optional fields should be initialized
        assert isinstance(context.learning_goals, list)
        assert isinstance(context.mistakes_tracked, list)
        assert isinstance(context.vocabulary_introduced, list)
        assert context.is_scenario_based is False
        assert context.scenario_id is None


class TestConversationMessage:
    """Test ConversationMessage dataclass - CRITICAL for line 172 coverage"""

    def test_conversation_message_with_all_fields(self):
        """Test ConversationMessage creation with all fields provided"""
        now = datetime.now()
        message = ConversationMessage(
            role=MessageRole.USER,
            content="Hello, how are you?",
            timestamp=now,
            language="en",
            metadata={"confidence": 0.95, "model": "gpt-4"},
        )

        assert message.role == MessageRole.USER
        assert message.content == "Hello, how are you?"
        assert message.language == "en"
        assert message.metadata["confidence"] == 0.95

    def test_conversation_message_with_none_metadata(self):
        """Test ConversationMessage __post_init__ initializes metadata to {} - COVERS LINE 172"""
        now = datetime.now()
        message = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="I'm fine, thank you!",
            timestamp=now,
            language="en",
            metadata=None,  # This triggers line 172: self.metadata = {}
        )

        # Line 172 verification
        assert isinstance(message.metadata, dict)
        assert len(message.metadata) == 0

    def test_conversation_message_without_metadata(self):
        """Test ConversationMessage creation without metadata parameter"""
        now = datetime.now()
        message = ConversationMessage(
            role=MessageRole.SYSTEM,
            content="System message",
            timestamp=now,
            language="en",
        )

        # metadata defaults to None, then __post_init__ sets it to {}
        assert isinstance(message.metadata, dict)
        assert len(message.metadata) == 0

    def test_conversation_message_roles(self):
        """Test all message roles work correctly"""
        now = datetime.now()

        user_msg = ConversationMessage(
            role=MessageRole.USER,
            content="User message",
            timestamp=now,
            language="es",
        )
        assert user_msg.role == MessageRole.USER

        assistant_msg = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="Assistant message",
            timestamp=now,
            language="es",
        )
        assert assistant_msg.role == MessageRole.ASSISTANT

        system_msg = ConversationMessage(
            role=MessageRole.SYSTEM,
            content="System message",
            timestamp=now,
            language="es",
        )
        assert system_msg.role == MessageRole.SYSTEM


class TestLearningInsight:
    """Test LearningInsight dataclass"""

    def test_learning_insight_creation(self):
        """Test LearningInsight creation with all fields"""
        insight = LearningInsight(
            vocabulary_new=["hola", "gracias"],
            vocabulary_practiced=["buenos días", "por favor"],
            grammar_corrections=[{"original": "yo es", "corrected": "yo soy"}],
            pronunciation_feedback=[
                {"word": "hola", "issue": "stress", "tip": "Stress first syllable"}
            ],
            conversation_quality_score=0.85,
            engagement_level="high",
            suggested_focus="pronunciation",
        )

        assert len(insight.vocabulary_new) == 2
        assert insight.conversation_quality_score == 0.85
        assert insight.engagement_level == "high"

    def test_learning_insight_with_empty_lists(self):
        """Test LearningInsight with empty lists"""
        insight = LearningInsight(
            vocabulary_new=[],
            vocabulary_practiced=[],
            grammar_corrections=[],
            pronunciation_feedback=[],
            conversation_quality_score=0.0,
            engagement_level="low",
            suggested_focus="vocabulary",
        )

        assert len(insight.vocabulary_new) == 0
        assert len(insight.vocabulary_practiced) == 0
        assert insight.conversation_quality_score == 0.0


class TestDataclassIntegration:
    """Test dataclasses work together correctly"""

    def test_complete_conversation_flow(self):
        """Test complete conversation with context, messages, and insights"""
        now = datetime.now()

        # Create context
        context = ConversationContext(
            conversation_id="full_conv_001",
            user_id="user_integration",
            language="es",
            learning_focus=LearningFocus.CONVERSATION,
            current_topic="Restaurant",
        )

        # Create messages
        messages = []

        # System message
        system_msg = ConversationMessage(
            role=MessageRole.SYSTEM,
            content="Welcome to Spanish conversation practice",
            timestamp=now,
            language="en",
            metadata={"type": "greeting"},
        )
        messages.append(system_msg)

        # User message
        user_msg = ConversationMessage(
            role=MessageRole.USER,
            content="Hola, quiero una mesa para dos",
            timestamp=now,
            language="es",
            metadata=None,  # Tests line 172
        )
        messages.append(user_msg)

        # Assistant message
        assistant_msg = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="Por supuesto, sígame por favor",
            timestamp=now,
            language="es",
            metadata={"confidence": 0.92},
        )
        messages.append(assistant_msg)

        # Create insight
        insight = LearningInsight(
            vocabulary_new=["mesa", "sígame"],
            vocabulary_practiced=["hola", "quiero"],
            grammar_corrections=[],
            pronunciation_feedback=[],
            conversation_quality_score=0.88,
            engagement_level="high",
            suggested_focus="vocabulary",
        )

        # Verify integration
        assert context.conversation_id == "full_conv_001"
        assert len(messages) == 3
        assert messages[0].role == MessageRole.SYSTEM
        assert messages[1].role == MessageRole.USER
        assert messages[2].role == MessageRole.ASSISTANT
        assert insight.conversation_quality_score > 0.8

        # Verify metadata handling (line 172 coverage)
        assert isinstance(user_msg.metadata, dict)
        assert len(user_msg.metadata) == 0

    def test_scenario_based_conversation(self):
        """Test scenario-based conversation setup"""
        context = ConversationContext(
            conversation_id="scenario_conv",
            user_id="user_scenario",
            language="fr",
            learning_focus=LearningFocus.CONVERSATION,
            current_topic="Airport",
            is_scenario_based=True,
            scenario_id="airport_checkin",
            scenario_progress_id="progress_checkin_001",
            scenario_phase="greeting",
        )

        assert context.is_scenario_based is True
        assert context.scenario_id == "airport_checkin"
        assert context.scenario_phase == "greeting"

    def test_message_metadata_mutations(self):
        """Test that metadata can be safely modified after initialization"""
        now = datetime.now()

        # Create message with None metadata (triggers line 172)
        message = ConversationMessage(
            role=MessageRole.USER,
            content="Test message",
            timestamp=now,
            language="en",
            metadata=None,
        )

        # Verify line 172 initialized empty dict
        assert isinstance(message.metadata, dict)
        assert len(message.metadata) == 0

        # Safe to add metadata after initialization
        message.metadata["added_key"] = "added_value"
        assert message.metadata["added_key"] == "added_value"
