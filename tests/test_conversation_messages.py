"""
Comprehensive tests for conversation_messages module.

Tests cover:
- MessageHandler initialization
- User message processing
- AI response generation (success and error paths)
- Scenario interaction handling
- Conversation response building
- Message history retrieval
- Context preparation for AI
- Context compression
- Private helper methods
"""

from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.conversation_messages import MessageHandler, message_handler
from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    LearningFocus,
    LearningInsight,
    MessageRole,
)


class TestMessageHandlerInit:
    """Test MessageHandler initialization."""

    def test_message_handler_initialization(self):
        """Test MessageHandler initializes with correct default values."""
        handler = MessageHandler()

        assert handler.message_history == {}
        assert handler.max_context_messages == 20
        assert handler.context_compression_threshold == 50

    def test_global_message_handler_instance(self):
        """Test that global message_handler instance exists."""
        assert message_handler is not None
        assert isinstance(message_handler, MessageHandler)


class TestSendMessage:
    """Test send_message method - main message flow coordinator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.conversation_id = "test-conv-123"
        self.user_message = "Hello, how are you?"
        self.context = Mock(spec=ConversationContext)
        self.context.language = "en"
        self.context.learning_focus = LearningFocus.CONVERSATION
        self.context.vocabulary_level = "intermediate"
        self.context.learning_goals = ["grammar", "vocabulary"]
        self.context.is_scenario_based = False
        self.context.scenario_progress_id = None
        self.context.session_start_time = datetime.now()
        self.context.current_topic = "general"

    @pytest.mark.asyncio
    async def test_send_message_success_flow(self):
        """Test complete send_message flow with successful AI response."""
        # Mock all sub-methods
        with (
            patch.object(
                self.handler, "process_user_message", new_callable=AsyncMock
            ) as mock_process,
            patch.object(
                self.handler, "generate_ai_response", new_callable=AsyncMock
            ) as mock_generate,
            patch.object(
                self.handler, "handle_scenario_interaction", new_callable=AsyncMock
            ) as mock_scenario,
            patch.object(
                self.handler, "build_conversation_response", new_callable=AsyncMock
            ) as mock_build,
        ):
            # Set up return values
            mock_process.return_value = {"word_count": 4}
            mock_generate.return_value = {
                "content": "I'm doing well, thank you!",
                "model": "gpt-4",
                "provider": "openai",
            }
            mock_scenario.return_value = None
            mock_build.return_value = {
                "conversation_id": self.conversation_id,
                "ai_response": "I'm doing well, thank you!",
            }

            # Execute
            result = await self.handler.send_message(
                self.conversation_id, self.user_message, self.context
            )

            # Verify all steps were called
            mock_process.assert_called_once_with(
                self.conversation_id, self.user_message, self.context
            )
            mock_generate.assert_called_once()
            mock_scenario.assert_called_once()
            mock_build.assert_called_once()

            # Verify result
            assert result["conversation_id"] == self.conversation_id
            assert "ai_response" in result

    @pytest.mark.asyncio
    async def test_send_message_with_scenario_progress(self):
        """Test send_message updates context with scenario progress."""
        self.context.is_scenario_based = True
        self.context.scenario_progress_id = "scenario-123"
        self.context.scenario_phase = None

        with (
            patch.object(
                self.handler, "process_user_message", new_callable=AsyncMock
            ) as mock_process,
            patch.object(
                self.handler, "generate_ai_response", new_callable=AsyncMock
            ) as mock_generate,
            patch.object(
                self.handler, "handle_scenario_interaction", new_callable=AsyncMock
            ) as mock_scenario,
            patch.object(
                self.handler, "build_conversation_response", new_callable=AsyncMock
            ) as mock_build,
        ):
            mock_process.return_value = {"word_count": 4}
            mock_generate.return_value = {
                "content": "Great response!",
                "model": "gpt-4",
            }
            mock_scenario.return_value = {"current_phase": "phase_2"}
            mock_build.return_value = {"conversation_id": self.conversation_id}

            await self.handler.send_message(
                self.conversation_id, self.user_message, self.context
            )

            # Verify scenario phase was updated
            assert self.context.scenario_phase == "phase_2"

    @pytest.mark.asyncio
    async def test_send_message_handles_ai_error(self):
        """Test send_message handles AI generation error gracefully."""
        with (
            patch.object(self.handler, "process_user_message", new_callable=AsyncMock),
            patch.object(
                self.handler, "generate_ai_response", new_callable=AsyncMock
            ) as mock_generate,
        ):
            # Simulate AI error
            mock_generate.return_value = {
                "content": "I'm sorry, I'm having trouble...",
                "error": "API timeout",
            }

            result = await self.handler.send_message(
                self.conversation_id, self.user_message, self.context
            )

            # Should return error response immediately
            assert "error" in result


class TestProcessUserMessage:
    """Test process_user_message method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.conversation_id = "test-conv-123"
        self.user_message = "Test message"
        self.context = Mock(spec=ConversationContext)
        self.context.language = "en"

    @pytest.mark.asyncio
    async def test_process_user_message_adds_to_history(self):
        """Test that user message is added to history."""
        with (
            patch.object(
                self.handler, "_add_message", new_callable=AsyncMock
            ) as mock_add,
            patch(
                "app.services.conversation_messages.learning_analyzer.analyze_user_message",
                new_callable=AsyncMock,
            ) as mock_analyze,
        ):
            mock_analyze.return_value = {"word_count": 2}

            await self.handler.process_user_message(
                self.conversation_id, self.user_message, self.context
            )

            # Verify message was added
            mock_add.assert_called_once_with(
                conversation_id=self.conversation_id,
                role=MessageRole.USER,
                content=self.user_message,
                language=self.context.language,
            )

    @pytest.mark.asyncio
    async def test_process_user_message_analyzes_content(self):
        """Test that user message is analyzed for insights."""
        with (
            patch.object(self.handler, "_add_message", new_callable=AsyncMock),
            patch(
                "app.services.conversation_messages.learning_analyzer.analyze_user_message",
                new_callable=AsyncMock,
            ) as mock_analyze,
        ):
            expected_insights = {"word_count": 2, "complexity": "simple"}
            mock_analyze.return_value = expected_insights

            result = await self.handler.process_user_message(
                self.conversation_id, self.user_message, self.context
            )

            # Verify analysis was called and returned
            mock_analyze.assert_called_once_with(
                user_message=self.user_message, context=self.context
            )
            assert result == expected_insights


class TestGenerateAIResponse:
    """Test generate_ai_response method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.conversation_id = "test-conv-123"
        self.context = Mock(spec=ConversationContext)
        self.context.language = "en"
        self.context.learning_focus = LearningFocus.CONVERSATION
        self.context.vocabulary_level = "intermediate"
        self.context.learning_goals = ["grammar"]

    @pytest.mark.asyncio
    async def test_generate_ai_response_success(self):
        """Test successful AI response generation."""
        with (
            patch.object(
                self.handler, "_prepare_ai_context", new_callable=AsyncMock
            ) as mock_prepare,
            patch(
                "app.services.conversation_messages.generate_ai_response",
                new_callable=AsyncMock,
            ) as mock_generate,
            patch.object(self.handler, "_add_message", new_callable=AsyncMock),
        ):
            # Mock AI response
            mock_response = Mock()
            mock_response.content = "AI response text"
            mock_response.model = "gpt-4"
            mock_response.provider = "openai"
            mock_response.processing_time = 1.5
            mock_response.cost = 0.001
            mock_response.metadata = {}

            mock_prepare.return_value = [{"role": "user", "content": "Hello"}]
            mock_generate.return_value = mock_response

            result = await self.handler.generate_ai_response(
                self.conversation_id, self.context
            )

            # Verify result structure
            assert result["content"] == "AI response text"
            assert result["model"] == "gpt-4"
            assert result["provider"] == "openai"
            assert result["processing_time"] == 1.5
            assert result["cost"] == 0.001
            assert "error" not in result

    @pytest.mark.asyncio
    async def test_generate_ai_response_with_pronunciation_feedback(self):
        """Test AI generation with pronunciation feedback enabled."""
        with (
            patch.object(self.handler, "_prepare_ai_context", new_callable=AsyncMock),
            patch(
                "app.services.conversation_messages.generate_ai_response",
                new_callable=AsyncMock,
            ) as mock_generate,
            patch.object(self.handler, "_add_message", new_callable=AsyncMock),
        ):
            mock_response = Mock()
            mock_response.content = "Response"
            mock_response.model = "gpt-4"
            mock_response.provider = "openai"
            mock_response.processing_time = 1.0
            mock_response.cost = 0.001
            mock_response.metadata = {}

            mock_generate.return_value = mock_response

            await self.handler.generate_ai_response(
                self.conversation_id, self.context, include_pronunciation_feedback=True
            )

            # Verify user_preferences included pronunciation_feedback
            call_kwargs = mock_generate.call_args.kwargs
            assert call_kwargs["user_preferences"]["pronunciation_feedback"] is True

    @pytest.mark.asyncio
    async def test_generate_ai_response_handles_exception(self):
        """Test that exceptions during AI generation are handled gracefully."""
        with (
            patch.object(self.handler, "_prepare_ai_context", new_callable=AsyncMock),
            patch(
                "app.services.conversation_messages.generate_ai_response",
                new_callable=AsyncMock,
            ) as mock_generate,
        ):
            # Simulate exception
            mock_generate.side_effect = Exception("API connection failed")

            result = await self.handler.generate_ai_response(
                self.conversation_id, self.context
            )

            # Should return error response
            assert "error" in result
            assert result["error"] == "API connection failed"
            assert "I'm sorry" in result["content"]
            assert result["model"] == "error"
            assert result["provider"] == "error"


class TestHandleScenarioInteraction:
    """Test handle_scenario_interaction method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.context = Mock(spec=ConversationContext)
        self.context.is_scenario_based = True
        self.context.scenario_progress_id = "progress-123"
        self.user_message = "User message"
        self.ai_response = "AI response"

    @pytest.mark.asyncio
    async def test_handle_scenario_interaction_success(self):
        """Test successful scenario interaction processing."""
        with patch(
            "app.services.conversation_messages.scenario_manager.process_scenario_message",
            new_callable=AsyncMock,
        ) as mock_process:
            expected_progress = {"current_phase": "phase_2", "score": 85}
            mock_process.return_value = expected_progress

            result = await self.handler.handle_scenario_interaction(
                self.context, self.user_message, self.ai_response
            )

            # Verify scenario manager was called
            mock_process.assert_called_once_with(
                progress_id=self.context.scenario_progress_id,
                user_message=self.user_message,
                ai_response=self.ai_response,
            )
            assert result == expected_progress

    @pytest.mark.asyncio
    async def test_handle_scenario_interaction_not_scenario_based(self):
        """Test that non-scenario conversations return None."""
        self.context.is_scenario_based = False

        result = await self.handler.handle_scenario_interaction(
            self.context, self.user_message, self.ai_response
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_scenario_interaction_no_progress_id(self):
        """Test that conversations without progress_id return None."""
        self.context.scenario_progress_id = None

        result = await self.handler.handle_scenario_interaction(
            self.context, self.user_message, self.ai_response
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_scenario_interaction_handles_exception(self):
        """Test that exceptions during scenario processing are handled."""
        with patch(
            "app.services.conversation_messages.scenario_manager.process_scenario_message",
            new_callable=AsyncMock,
        ) as mock_process:
            mock_process.side_effect = Exception("Scenario processing failed")

            result = await self.handler.handle_scenario_interaction(
                self.context, self.user_message, self.ai_response
            )

            # Should return None on error
            assert result is None


class TestBuildConversationResponse:
    """Test build_conversation_response method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.conversation_id = "test-conv-123"
        self.user_message = "User message"
        self.context = Mock(spec=ConversationContext)
        self.context.current_topic = "weather"
        self.context.vocabulary_level = "intermediate"
        self.context.session_start_time = datetime.now()
        self.context.is_scenario_based = False

        # Initialize message history
        self.handler.message_history[self.conversation_id] = []

    @pytest.mark.asyncio
    async def test_build_conversation_response_success(self):
        """Test building complete conversation response."""
        ai_response = {
            "content": "AI response",
            "model": "gpt-4",
            "provider": "openai",
            "cost": 0.001,
            "metadata": {"router_selection": {"is_fallback": False}},
        }

        mock_insights = Mock(spec=LearningInsight)
        mock_insights.conversation_quality_score = 0.85
        mock_insights.engagement_level = "high"

        with (
            patch(
                "app.services.conversation_messages.learning_analyzer.generate_learning_insights",
                new_callable=AsyncMock,
            ) as mock_generate,
            patch(
                "app.services.conversation_messages.learning_analyzer.update_conversation_context",
                new_callable=AsyncMock,
            ),
        ):
            mock_generate.return_value = mock_insights

            result = await self.handler.build_conversation_response(
                conversation_id=self.conversation_id,
                user_message=self.user_message,
                ai_response=ai_response,
                context=self.context,
            )

            # Verify response structure
            assert result["conversation_id"] == self.conversation_id
            assert result["ai_response"] == "AI response"
            assert result["learning_insights"] == mock_insights
            assert "context_info" in result
            assert "ai_metadata" in result
            assert result["ai_metadata"]["model"] == "gpt-4"
            assert result["ai_metadata"]["provider"] == "openai"
            assert result["ai_metadata"]["is_fallback"] is False

    @pytest.mark.asyncio
    async def test_build_conversation_response_with_scenario_progress(self):
        """Test response includes scenario progress when applicable."""
        self.context.is_scenario_based = True

        ai_response = {
            "content": "AI response",
            "model": "gpt-4",
            "provider": "openai",
            "cost": 0.001,
            "metadata": {},
        }

        scenario_progress = {"current_phase": "phase_3", "completed": False}

        with (
            patch(
                "app.services.conversation_messages.learning_analyzer.generate_learning_insights",
                new_callable=AsyncMock,
            ) as mock_generate,
            patch(
                "app.services.conversation_messages.learning_analyzer.update_conversation_context",
                new_callable=AsyncMock,
            ),
        ):
            mock_insights = Mock(spec=LearningInsight)
            mock_insights.conversation_quality_score = 0.85
            mock_insights.engagement_level = "high"
            mock_generate.return_value = mock_insights

            result = await self.handler.build_conversation_response(
                conversation_id=self.conversation_id,
                user_message=self.user_message,
                ai_response=ai_response,
                context=self.context,
                scenario_progress=scenario_progress,
            )

            # Verify scenario progress is included
            assert "scenario_progress" in result
            assert result["scenario_progress"] == scenario_progress

    @pytest.mark.asyncio
    async def test_build_conversation_response_handles_error(self):
        """Test building response when AI generation had an error."""
        ai_response = {
            "content": "Error message",
            "error": "API timeout",
            "model": "error",
            "provider": "error",
        }

        result = await self.handler.build_conversation_response(
            conversation_id=self.conversation_id,
            user_message=self.user_message,
            ai_response=ai_response,
            context=self.context,
        )

        # Verify error response structure
        assert result["conversation_id"] == self.conversation_id
        assert result["ai_response"] == "Error message"
        assert "error" in result
        assert result["error"] == "API timeout"
        assert "learning_insights" in result
        assert result["learning_insights"].engagement_level == "error"


class TestGetConversationHistory:
    """Test get_conversation_history method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.conversation_id = "test-conv-123"

    @pytest.mark.asyncio
    async def test_get_conversation_history_returns_messages(self):
        """Test retrieving conversation history."""
        # Add some messages
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content="Hello",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="Hi there",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        history = await self.handler.get_conversation_history(self.conversation_id)

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there"

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_limit(self):
        """Test retrieving limited conversation history."""
        # Add multiple messages
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(10)
        ]

        history = await self.handler.get_conversation_history(
            self.conversation_id, limit=3
        )

        # Should return only last 3 messages
        assert len(history) == 3
        assert history[0]["content"] == "Message 7"
        assert history[2]["content"] == "Message 9"

    @pytest.mark.asyncio
    async def test_get_conversation_history_excludes_system_messages(self):
        """Test that system messages are excluded from history."""
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content="User message",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.SYSTEM,
                content="System message",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="Assistant message",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        history = await self.handler.get_conversation_history(self.conversation_id)

        # Should only have user and assistant messages
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_get_conversation_history_nonexistent_conversation(self):
        """Test retrieving history for nonexistent conversation returns empty list."""
        history = await self.handler.get_conversation_history("nonexistent-id")

        assert history == []


class TestPrivateHelperMethods:
    """Test private helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
        self.conversation_id = "test-conv-123"

    @pytest.mark.asyncio
    async def test_add_message_creates_conversation_history(self):
        """Test _add_message creates message history if not exists."""
        await self.handler._add_message(
            conversation_id=self.conversation_id,
            role=MessageRole.USER,
            content="Test message",
            language="en",
        )

        assert self.conversation_id in self.handler.message_history
        assert len(self.handler.message_history[self.conversation_id]) == 1

    @pytest.mark.asyncio
    async def test_add_message_appends_to_existing_history(self):
        """Test _add_message appends to existing message history."""
        # Add first message
        await self.handler._add_message(
            conversation_id=self.conversation_id,
            role=MessageRole.USER,
            content="First message",
            language="en",
        )

        # Add second message
        await self.handler._add_message(
            conversation_id=self.conversation_id,
            role=MessageRole.ASSISTANT,
            content="Second message",
            language="en",
        )

        assert len(self.handler.message_history[self.conversation_id]) == 2

    @pytest.mark.asyncio
    async def test_add_message_with_metadata(self):
        """Test _add_message includes metadata."""
        metadata = {"model": "gpt-4", "cost": 0.001}

        await self.handler._add_message(
            conversation_id=self.conversation_id,
            role=MessageRole.ASSISTANT,
            content="Test message",
            language="en",
            metadata=metadata,
        )

        message = self.handler.message_history[self.conversation_id][0]
        assert message.metadata == metadata

    @pytest.mark.asyncio
    async def test_add_message_triggers_compression_check(self):
        """Test _add_message calls compression check."""
        with patch.object(
            self.handler, "_maybe_compress_context", new_callable=AsyncMock
        ) as mock_compress:
            await self.handler._add_message(
                conversation_id=self.conversation_id,
                role=MessageRole.USER,
                content="Test",
                language="en",
            )

            mock_compress.assert_called_once_with(self.conversation_id)

    @pytest.mark.asyncio
    async def test_prepare_ai_context_formats_messages(self):
        """Test _prepare_ai_context formats messages for AI provider."""
        # Add messages to history
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content="Hello",
                timestamp=datetime.now(),
                language="en",
            ),
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content="Hi",
                timestamp=datetime.now(),
                language="en",
            ),
        ]

        ai_messages = await self.handler._prepare_ai_context(self.conversation_id)

        assert len(ai_messages) == 2
        assert ai_messages[0]["role"] == "user"
        assert ai_messages[0]["content"] == "Hello"
        assert ai_messages[1]["role"] == "assistant"
        assert ai_messages[1]["content"] == "Hi"

    @pytest.mark.asyncio
    async def test_prepare_ai_context_limits_messages(self):
        """Test _prepare_ai_context limits to max_context_messages."""
        # Add more messages than max_context_messages
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(30)
        ]

        ai_messages = await self.handler._prepare_ai_context(self.conversation_id)

        # Should return only last 20 messages (max_context_messages)
        assert len(ai_messages) == 20

    @pytest.mark.asyncio
    async def test_maybe_compress_context_no_compression_needed(self):
        """Test _maybe_compress_context does nothing below threshold."""
        # Add messages below compression threshold
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(10)
        ]

        original_count = len(self.handler.message_history[self.conversation_id])

        await self.handler._maybe_compress_context(self.conversation_id)

        # Should not compress
        assert len(self.handler.message_history[self.conversation_id]) == original_count

    @pytest.mark.asyncio
    async def test_maybe_compress_context_compresses_when_needed(self):
        """Test _maybe_compress_context compresses beyond threshold."""
        # Add messages beyond compression threshold (50)
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(60)
        ]

        await self.handler._maybe_compress_context(self.conversation_id)

        # Should compress to max_context_messages (20) + 1 summary message
        messages = self.handler.message_history[self.conversation_id]
        assert len(messages) <= 21  # 20 recent + 1 summary

        # Check for summary message
        summary_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
        assert len(summary_messages) > 0
        assert "Previous conversation summary" in summary_messages[0].content

    @pytest.mark.asyncio
    async def test_maybe_compress_context_preserves_system_messages(self):
        """Test _maybe_compress_context preserves original system messages."""
        # Add system message and many other messages
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.SYSTEM,
                content="Important system message",
                timestamp=datetime.now(),
                language="en",
            )
        ] + [
            ConversationMessage(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(60)
        ]

        await self.handler._maybe_compress_context(self.conversation_id)

        # Original system message should be preserved
        messages = self.handler.message_history[self.conversation_id]
        system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]

        # Should have original system message + compression summary
        assert len(system_messages) >= 1
        assert any("Important system message" in msg.content for msg in system_messages)

    @pytest.mark.asyncio
    async def test_maybe_compress_context_nonexistent_conversation(self):
        """Test _maybe_compress_context handles nonexistent conversation gracefully."""
        # Should not raise exception
        await self.handler._maybe_compress_context("nonexistent-id")

    @pytest.mark.asyncio
    async def test_maybe_compress_context_no_compression_when_compressed_count_zero(
        self,
    ):
        """Test _maybe_compress_context skips compression when compressed_count <= 0."""
        # This test covers the 515→exit branch
        # When compressed_count = len(messages) - len(recent) - len(system) <= 0
        # Create exactly 51 messages (over threshold of 50)
        # with 20 recent messages + 31 system messages
        # compressed_count = 51 - 20 - 31 = 0, so no compression occurs
        self.handler.message_history[self.conversation_id] = [
            ConversationMessage(
                role=MessageRole.SYSTEM,
                content=f"System message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(31)
        ] + [
            ConversationMessage(
                role=MessageRole.USER,
                content=f"Message {i}",
                timestamp=datetime.now(),
                language="en",
            )
            for i in range(20)
        ]

        original_count = len(self.handler.message_history[self.conversation_id])
        assert original_count == 51  # Verify we're over threshold

        await self.handler._maybe_compress_context(self.conversation_id)

        # Should NOT compress because compressed_count = 0
        assert len(self.handler.message_history[self.conversation_id]) == original_count
        # No compression summary should be added
        summary_count = sum(
            1
            for msg in self.handler.message_history[self.conversation_id]
            if msg.role == MessageRole.SYSTEM
            and "Previous conversation summary" in msg.content
        )
        assert summary_count == 0
