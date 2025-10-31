"""
Comprehensive tests for conversation_analytics module.

Tests cover:
- LearningAnalyzer initialization
- User message analysis
- Learning insights generation
- Session insights generation
- Context updates with learning insights
- Edge cases and error handling
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from app.services.conversation_analytics import LearningAnalyzer, learning_analyzer
from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    LearningFocus,
    LearningInsight,
    MessageRole,
)


class TestLearningAnalyzerInit:
    """Test LearningAnalyzer initialization."""

    def test_learning_analyzer_initialization(self):
        """Test LearningAnalyzer initializes correctly."""
        analyzer = LearningAnalyzer()

        assert analyzer.logger is not None

    def test_global_learning_analyzer_instance(self):
        """Test that global learning_analyzer instance exists."""
        assert learning_analyzer is not None
        assert isinstance(learning_analyzer, LearningAnalyzer)


class TestAnalyzeUserMessage:
    """Test analyze_user_message method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LearningAnalyzer()
        self.context = Mock(spec=ConversationContext)
        self.context.language = "en"

    @pytest.mark.asyncio
    async def test_analyze_user_message_basic_metrics(self):
        """Test basic message analysis with word count and length."""
        user_message = "Hello how are you doing today"

        result = await self.analyzer.analyze_user_message(user_message, self.context)

        assert result["word_count"] == 6
        assert result["message_length"] == len(user_message)
        assert "complexity_score" in result
        assert "engagement_indicators" in result

    @pytest.mark.asyncio
    async def test_analyze_user_message_complexity_score(self):
        """Test complexity score calculation based on word count."""
        # Short message (low complexity)
        short_message = "Hello"
        result_short = await self.analyzer.analyze_user_message(
            short_message, self.context
        )
        assert result_short["complexity_score"] < 0.5

        # Medium message (medium complexity)
        medium_message = "Hello how are you doing"
        result_medium = await self.analyzer.analyze_user_message(
            medium_message, self.context
        )
        assert 0.3 <= result_medium["complexity_score"] <= 0.7

        # Long message (high complexity)
        long_message = " ".join(["word"] * 15)
        result_long = await self.analyzer.analyze_user_message(
            long_message, self.context
        )
        assert result_long["complexity_score"] >= 0.9

    @pytest.mark.asyncio
    async def test_analyze_user_message_complexity_capped_at_one(self):
        """Test complexity score is capped at 1.0."""
        very_long_message = " ".join(["word"] * 100)

        result = await self.analyzer.analyze_user_message(
            very_long_message, self.context
        )

        assert result["complexity_score"] == 1.0

    @pytest.mark.asyncio
    async def test_analyze_user_message_detects_questions(self):
        """Test detection of question marks as engagement indicator."""
        message_with_question = "How are you?"

        result = await self.analyzer.analyze_user_message(
            message_with_question, self.context
        )

        assert result["engagement_indicators"]["questions"] is True

    @pytest.mark.asyncio
    async def test_analyze_user_message_detects_excitement(self):
        """Test detection of exclamation marks as engagement indicator."""
        message_with_excitement = "That's amazing!"

        result = await self.analyzer.analyze_user_message(
            message_with_excitement, self.context
        )

        assert result["engagement_indicators"]["excitement"] is True

    @pytest.mark.asyncio
    async def test_analyze_user_message_detects_formal_language(self):
        """Test detection of formal/polite phrases."""
        formal_messages = [
            "Could you please help me?",
            "Thank you for your assistance",
            "Would you mind explaining this?",
        ]

        for message in formal_messages:
            result = await self.analyzer.analyze_user_message(message, self.context)
            assert result["engagement_indicators"]["formal_language"] is True

    @pytest.mark.asyncio
    async def test_analyze_user_message_no_engagement_indicators(self):
        """Test message without engagement indicators."""
        plain_message = "I am learning"

        result = await self.analyzer.analyze_user_message(plain_message, self.context)

        assert result["engagement_indicators"]["questions"] is False
        assert result["engagement_indicators"]["excitement"] is False
        assert result["engagement_indicators"]["formal_language"] is False

    @pytest.mark.asyncio
    async def test_analyze_user_message_multiple_engagement_indicators(self):
        """Test message with multiple engagement indicators."""
        message = "Could you please explain this? Thank you!"

        result = await self.analyzer.analyze_user_message(message, self.context)

        assert result["engagement_indicators"]["questions"] is True
        assert result["engagement_indicators"]["excitement"] is True
        assert result["engagement_indicators"]["formal_language"] is True


class TestGenerateLearningInsights:
    """Test generate_learning_insights method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LearningAnalyzer()
        self.conversation_id = "test-conv-123"
        self.context = Mock(spec=ConversationContext)
        self.context.vocabulary_introduced = []
        self.context.learning_focus = LearningFocus.CONVERSATION

    @pytest.mark.asyncio
    async def test_generate_learning_insights_extracts_new_vocabulary(self):
        """Test extraction of new vocabulary from AI response."""
        user_message = "Hello"
        ai_response = "Bonjour means hello in French"
        self.context.vocabulary_introduced = []

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, user_message, ai_response, self.context
        )

        # Should extract up to 3 new vocabulary words
        assert isinstance(insights, LearningInsight)
        assert len(insights.vocabulary_new) <= 3

    @pytest.mark.asyncio
    async def test_generate_learning_insights_excludes_known_vocabulary(self):
        """Test that known vocabulary is not included in new words."""
        user_message = "Hello"
        ai_response = "hello world"
        self.context.vocabulary_introduced = ["hello", "world"]

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, user_message, ai_response, self.context
        )

        # Should not include words already in vocabulary_introduced
        assert len(insights.vocabulary_new) == 0

    @pytest.mark.asyncio
    async def test_generate_learning_insights_engagement_level_low(self):
        """Test low engagement level for short message."""
        user_message = "Hi"
        ai_response = "Hello!"

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, user_message, ai_response, self.context
        )

        assert insights.engagement_level == "low"

    @pytest.mark.asyncio
    async def test_generate_learning_insights_engagement_level_medium(self):
        """Test medium engagement level for moderate message."""
        user_message = "Hello, how are you doing today?"
        ai_response = "I'm doing well, thank you!"

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, user_message, ai_response, self.context
        )

        assert insights.engagement_level in ["medium", "high"]

    @pytest.mark.asyncio
    async def test_generate_learning_insights_engagement_level_high(self):
        """Test high engagement level for long message."""
        user_message = " ".join(["word"] * 20)
        ai_response = "Great response!"

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, user_message, ai_response, self.context
        )

        assert insights.engagement_level == "high"

    @pytest.mark.asyncio
    async def test_generate_learning_insights_quality_score_calculation(self):
        """Test conversation quality score calculation."""
        # High quality message
        high_quality_message = "Could you please explain this concept?"
        ai_response = "Sure, let me explain"

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, high_quality_message, ai_response, self.context
        )

        # All quality factors should be true (length > 10, has ?, has >= 3 words)
        assert insights.conversation_quality_score > 0.5

    @pytest.mark.asyncio
    async def test_generate_learning_insights_quality_factors(self):
        """Test individual quality factors contribution."""
        # Message with all quality factors
        message_all_factors = "How are you doing today?"  # >10 chars, has ?, >=3 words
        ai_response = "Response"

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, message_all_factors, ai_response, self.context
        )

        # All 3 quality factors met, score should be 1.0
        assert insights.conversation_quality_score == 1.0

    @pytest.mark.asyncio
    async def test_generate_learning_insights_suggested_focus(self):
        """Test suggested_focus matches context learning_focus."""
        self.context.learning_focus = LearningFocus.GRAMMAR

        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, "test", "response", self.context
        )

        assert insights.suggested_focus == "grammar"

    @pytest.mark.asyncio
    async def test_generate_learning_insights_empty_lists(self):
        """Test that grammar_corrections and pronunciation_feedback are empty."""
        insights = await self.analyzer.generate_learning_insights(
            self.conversation_id, "test", "response", self.context
        )

        assert insights.grammar_corrections == []
        assert insights.pronunciation_feedback == []
        assert insights.vocabulary_practiced == []


class TestGenerateSessionInsights:
    """Test generate_session_insights method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LearningAnalyzer()
        self.conversation_id = "test-conv-123"
        self.context = Mock(spec=ConversationContext)
        self.context.conversation_id = self.conversation_id
        self.context.vocabulary_introduced = ["hello", "world", "test"]
        self.context.learning_focus = LearningFocus.CONVERSATION
        self.context.session_start_time = datetime.now() - timedelta(minutes=10)

    @pytest.mark.asyncio
    async def test_generate_session_insights_conversation_just_started(self):
        """Test session insights when conversation just started."""
        messages = [
            ConversationMessage(
                role=MessageRole.USER,
                content="Hello",
                timestamp=datetime.now(),
                language="en",
            )
        ]

        insights = await self.analyzer.generate_session_insights(
            self.conversation_id, self.context, messages
        )

        assert insights["learning_progress"] == "conversation_just_started"
        assert insights["engagement_level"] == "beginning"
        assert insights["message_count"] == 1

    @pytest.mark.asyncio
    async def test_generate_session_insights_with_full_exchange(self):
        """Test session insights with complete user-AI exchange."""
        messages = [
            ConversationMessage(
                role=MessageRole.USER,
                content="How are you doing today?",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="I'm doing well, thank you for asking!",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        insights = await self.analyzer.generate_session_insights(
            self.conversation_id, self.context, messages
        )

        assert "learning_progress" in insights
        assert isinstance(insights["learning_progress"], dict)
        assert "conversation_quality" in insights["learning_progress"]
        assert "engagement_level" in insights["learning_progress"]
        assert "focus_area" in insights["learning_progress"]
        assert "message_count" in insights
        assert "session_duration" in insights
        assert "new_vocabulary" in insights

    @pytest.mark.asyncio
    async def test_generate_session_insights_vocabulary_used_limited(self):
        """Test that vocabulary_used is limited to last 10 words."""
        self.context.vocabulary_introduced = [f"word{i}" for i in range(20)]
        messages = [
            ConversationMessage(
                role=MessageRole.USER,
                content="Test message",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="Response",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        insights = await self.analyzer.generate_session_insights(
            self.conversation_id, self.context, messages
        )

        # Should only return last 10 words
        assert len(insights["vocabulary_used"]) == 10

    @pytest.mark.asyncio
    async def test_generate_session_insights_session_duration(self):
        """Test session duration calculation in minutes."""
        self.context.session_start_time = datetime.now() - timedelta(minutes=15)
        messages = [
            ConversationMessage(
                role=MessageRole.USER,
                content="Test",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="Response",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        insights = await self.analyzer.generate_session_insights(
            self.conversation_id, self.context, messages
        )

        # Session duration should be approximately 15 minutes
        assert 14 <= insights["session_duration"] <= 16

    @pytest.mark.asyncio
    async def test_generate_session_insights_fallback_basic_interaction(self):
        """Test fallback when no full user-AI exchange exists."""
        # Only user messages, no AI response
        messages = [
            ConversationMessage(
                role=MessageRole.USER,
                content="Hello",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.USER,
                content="Are you there?",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        insights = await self.analyzer.generate_session_insights(
            self.conversation_id, self.context, messages
        )

        assert insights["learning_progress"] == "basic_interaction"
        assert insights["message_count"] == 2
        assert insights["vocabulary_used"] == self.context.vocabulary_introduced

    @pytest.mark.asyncio
    async def test_generate_session_insights_message_count(self):
        """Test message count includes all messages."""
        messages = [
            ConversationMessage(
                role=MessageRole.USER,
                content="1",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="2",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.USER,
                content="3",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="4",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        insights = await self.analyzer.generate_session_insights(
            self.conversation_id, self.context, messages
        )

        assert insights["message_count"] == 4


class TestUpdateConversationContext:
    """Test update_conversation_context method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LearningAnalyzer()
        self.context = Mock(spec=ConversationContext)
        self.context.conversation_id = "test-conv-123"
        self.context.vocabulary_introduced = ["hello", "world"]
        self.context.last_activity = datetime.now() - timedelta(minutes=5)

    @pytest.mark.asyncio
    async def test_update_conversation_context_adds_new_vocabulary(self):
        """Test that new vocabulary is added to context."""
        insights = Mock(spec=LearningInsight)
        insights.vocabulary_new = ["bonjour", "salut"]

        updated_context = await self.analyzer.update_conversation_context(
            self.context, insights
        )

        assert "bonjour" in updated_context.vocabulary_introduced
        assert "salut" in updated_context.vocabulary_introduced

    @pytest.mark.asyncio
    async def test_update_conversation_context_keeps_unique_vocabulary(self):
        """Test that vocabulary list remains unique (no duplicates)."""
        self.context.vocabulary_introduced = ["hello", "world"]
        insights = Mock(spec=LearningInsight)
        insights.vocabulary_new = ["hello", "test"]  # "hello" is duplicate

        updated_context = await self.analyzer.update_conversation_context(
            self.context, insights
        )

        # Count occurrences of "hello"
        hello_count = updated_context.vocabulary_introduced.count("hello")
        assert hello_count == 1

    @pytest.mark.asyncio
    async def test_update_conversation_context_limits_vocabulary_to_50(self):
        """Test that vocabulary list is limited to 50 most recent words."""
        # Add 60 words to vocabulary
        self.context.vocabulary_introduced = [f"word{i}" for i in range(60)]
        insights = Mock(spec=LearningInsight)
        insights.vocabulary_new = ["new_word"]

        updated_context = await self.analyzer.update_conversation_context(
            self.context, insights
        )

        # Should be limited to 50 words
        assert len(updated_context.vocabulary_introduced) == 50

    @pytest.mark.asyncio
    async def test_update_conversation_context_updates_last_activity(self):
        """Test that last_activity timestamp is updated."""
        old_timestamp = self.context.last_activity
        insights = Mock(spec=LearningInsight)
        insights.vocabulary_new = []

        # Small delay to ensure timestamp difference
        import asyncio

        await asyncio.sleep(0.01)

        updated_context = await self.analyzer.update_conversation_context(
            self.context, insights
        )

        # last_activity should be more recent than before
        assert updated_context.last_activity > old_timestamp

    @pytest.mark.asyncio
    async def test_update_conversation_context_empty_new_vocabulary(self):
        """Test context update when no new vocabulary is provided."""
        original_vocab = self.context.vocabulary_introduced.copy()
        insights = Mock(spec=LearningInsight)
        insights.vocabulary_new = []

        updated_context = await self.analyzer.update_conversation_context(
            self.context, insights
        )

        # Vocabulary should remain the same (but made unique)
        assert set(updated_context.vocabulary_introduced) == set(original_vocab)

    @pytest.mark.asyncio
    async def test_update_conversation_context_returns_context(self):
        """Test that updated context is returned."""
        insights = Mock(spec=LearningInsight)
        insights.vocabulary_new = ["test"]

        updated_context = await self.analyzer.update_conversation_context(
            self.context, insights
        )

        assert updated_context is self.context
        assert updated_context.conversation_id == "test-conv-123"
