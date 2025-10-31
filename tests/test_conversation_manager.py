"""
Comprehensive tests for conversation_manager.py - Conversation Manager Facade

Focus on reaching 90%+ coverage by testing all delegation methods,
error handling, and convenience functions.

Target: 70% -> 90%+ coverage (17 uncovered lines to cover)
"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.conversation_manager import (
    ConversationManager,
    conversation_manager,
    end_learning_conversation,
    get_conversation_summary,
    send_learning_message,
    start_learning_conversation,
)
from app.services.conversation_models import ConversationContext, LearningFocus


class TestConversationManagerProperties:
    """Test ConversationManager property accessors"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    def test_active_conversations_property(self):
        """Test accessing active_conversations property"""
        active_convs = self.manager.active_conversations
        assert isinstance(active_convs, dict)

    def test_context_cache_property(self):
        """Test accessing context_cache property"""
        cache = self.manager.context_cache
        assert isinstance(cache, dict)

    def test_message_history_property(self):
        """Test accessing message_history property"""
        history = self.manager.message_history
        assert isinstance(history, dict)


class TestStartConversation:
    """Test start_conversation delegation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_start_conversation_basic(self):
        """Test starting a basic conversation"""
        with patch.object(
            self.manager.state_manager, "start_conversation", new_callable=AsyncMock
        ) as mock_start:
            mock_start.return_value = "conv_123"

            result = await self.manager.start_conversation(
                user_id="user_1", language="en"
            )

            assert result == "conv_123"
            mock_start.assert_called_once()
            call_kwargs = mock_start.call_args.kwargs
            assert call_kwargs["user_id"] == "user_1"
            assert call_kwargs["language"] == "en"

    @pytest.mark.asyncio
    async def test_start_conversation_with_all_params(self):
        """Test starting conversation with all parameters"""
        with patch.object(
            self.manager.state_manager, "start_conversation", new_callable=AsyncMock
        ) as mock_start:
            mock_start.return_value = "conv_456"

            result = await self.manager.start_conversation(
                user_id="user_2",
                language="fr",
                learning_focus=LearningFocus.VOCABULARY,
                topic="food",
                learning_goals=["learn greetings"],
                scenario_id="scenario_1",
            )

            assert result == "conv_456"
            call_kwargs = mock_start.call_args.kwargs
            assert call_kwargs["user_id"] == "user_2"
            assert call_kwargs["language"] == "fr"
            assert call_kwargs["learning_focus"] == LearningFocus.VOCABULARY
            assert call_kwargs["topic"] == "food"
            assert call_kwargs["learning_goals"] == ["learn greetings"]
            assert call_kwargs["scenario_id"] == "scenario_1"


class TestSendMessage:
    """Test send_message delegation and error handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successfully sending a message"""
        # Mock active conversation
        mock_context = MagicMock(spec=ConversationContext)
        mock_context.conversation_id = "conv_123"

        with patch.dict(self.manager.active_conversations, {"conv_123": mock_context}):
            with patch.object(
                self.manager.message_handler, "send_message", new_callable=AsyncMock
            ) as mock_send:
                with patch.object(
                    self.manager.state_manager,
                    "_save_messages_to_db",
                    new_callable=AsyncMock,
                ) as mock_save:
                    mock_send.return_value = {
                        "response": "Hello!",
                        "message_id": "msg_1",
                    }

                    result = await self.manager.send_message(
                        conversation_id="conv_123",
                        user_message="Hi",
                        include_pronunciation_feedback=True,
                    )

                    assert result["response"] == "Hello!"
                    assert result["message_id"] == "msg_1"
                    mock_send.assert_called_once()
                    mock_save.assert_called_once_with("conv_123")

    @pytest.mark.asyncio
    async def test_send_message_conversation_not_found(self):
        """Test sending message to non-existent conversation"""
        with patch.dict(self.manager.active_conversations, {}):
            with pytest.raises(ValueError) as exc_info:
                await self.manager.send_message(
                    conversation_id="nonexistent", user_message="Hi"
                )

            assert "Conversation nonexistent not found or inactive" in str(
                exc_info.value
            )

    @pytest.mark.asyncio
    async def test_send_message_with_extra_kwargs(self):
        """Test sending message with extra kwargs passed through"""
        mock_context = MagicMock(spec=ConversationContext)
        mock_context.conversation_id = "conv_123"

        with patch.dict(self.manager.active_conversations, {"conv_123": mock_context}):
            with patch.object(
                self.manager.message_handler, "send_message", new_callable=AsyncMock
            ) as mock_send:
                with patch.object(
                    self.manager.state_manager,
                    "_save_messages_to_db",
                    new_callable=AsyncMock,
                ):
                    mock_send.return_value = {"response": "Good!"}

                    await self.manager.send_message(
                        conversation_id="conv_123",
                        user_message="How are you?",
                        custom_param="value",
                        another_param=42,
                    )

                    call_kwargs = mock_send.call_args.kwargs
                    assert call_kwargs["custom_param"] == "value"
                    assert call_kwargs["another_param"] == 42


class TestConversationHistory:
    """Test get_conversation_history delegation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_get_conversation_history_no_limit(self):
        """Test getting conversation history without limit"""
        with patch.object(
            self.manager.message_handler,
            "get_conversation_history",
            new_callable=AsyncMock,
        ) as mock_history:
            mock_history.return_value = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]

            result = await self.manager.get_conversation_history("conv_123")

            assert len(result) == 2
            mock_history.assert_called_once_with("conv_123", None)

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_limit(self):
        """Test getting conversation history with limit"""
        with patch.object(
            self.manager.message_handler,
            "get_conversation_history",
            new_callable=AsyncMock,
        ) as mock_history:
            mock_history.return_value = [{"role": "user", "content": "Hello"}]

            result = await self.manager.get_conversation_history("conv_456", limit=10)

            assert len(result) == 1
            mock_history.assert_called_once_with("conv_456", 10)


class TestConversationSummary:
    """Test get_conversation_summary delegation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        with patch.object(
            self.manager.state_manager,
            "get_conversation_summary",
            new_callable=AsyncMock,
        ) as mock_summary:
            mock_summary.return_value = {
                "conversation_id": "conv_123",
                "message_count": 10,
                "duration_minutes": 15,
            }

            result = await self.manager.get_conversation_summary("conv_123")

            assert result["conversation_id"] == "conv_123"
            assert result["message_count"] == 10
            mock_summary.assert_called_once_with("conv_123")


class TestPauseResume:
    """Test pause and resume conversation methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_pause_conversation(self):
        """Test pausing a conversation"""
        with patch.object(
            self.manager.state_manager, "pause_conversation", new_callable=AsyncMock
        ) as mock_pause:
            await self.manager.pause_conversation("conv_123")

            mock_pause.assert_called_once_with("conv_123")

    @pytest.mark.asyncio
    async def test_resume_conversation_success(self):
        """Test successfully resuming a conversation"""
        with patch.object(
            self.manager.state_manager, "resume_conversation", new_callable=AsyncMock
        ) as mock_resume:
            mock_resume.return_value = True

            result = await self.manager.resume_conversation("conv_123")

            assert result is True
            mock_resume.assert_called_once_with("conv_123")

    @pytest.mark.asyncio
    async def test_resume_conversation_failure(self):
        """Test failing to resume a conversation"""
        with patch.object(
            self.manager.state_manager, "resume_conversation", new_callable=AsyncMock
        ) as mock_resume:
            mock_resume.return_value = False

            result = await self.manager.resume_conversation("conv_456")

            assert result is False
            mock_resume.assert_called_once_with("conv_456")


class TestEndConversation:
    """Test end_conversation delegation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_end_conversation_with_save(self):
        """Test ending conversation with saving progress"""
        with patch.object(
            self.manager.state_manager, "end_conversation", new_callable=AsyncMock
        ) as mock_end:
            mock_end.return_value = {
                "conversation_id": "conv_123",
                "status": "completed",
            }

            result = await self.manager.end_conversation(
                "conv_123", save_learning_progress=True
            )

            assert result["status"] == "completed"
            mock_end.assert_called_once_with("conv_123", True)

    @pytest.mark.asyncio
    async def test_end_conversation_without_save(self):
        """Test ending conversation without saving progress"""
        with patch.object(
            self.manager.state_manager, "end_conversation", new_callable=AsyncMock
        ) as mock_end:
            mock_end.return_value = {
                "conversation_id": "conv_456",
                "status": "cancelled",
            }

            result = await self.manager.end_conversation(
                "conv_456", save_learning_progress=False
            )

            assert result["status"] == "cancelled"
            mock_end.assert_called_once_with("conv_456", False)


class TestGenerateLearningInsights:
    """Test generate_learning_insights method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationManager()

    @pytest.mark.asyncio
    async def test_generate_learning_insights_success(self):
        """Test successfully generating learning insights"""
        mock_context = MagicMock(spec=ConversationContext)
        mock_context.conversation_id = "conv_123"

        mock_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

        with patch.dict(self.manager.active_conversations, {"conv_123": mock_context}):
            with patch.dict(
                self.manager.message_handler.message_history,
                {"conv_123": mock_messages},
            ):
                with patch.object(
                    self.manager.learning_analyzer,
                    "generate_session_insights",
                    new_callable=AsyncMock,
                ) as mock_insights:
                    mock_insights.return_value = {
                        "vocabulary_learned": 5,
                        "grammar_points": 2,
                    }

                    result = await self.manager.generate_learning_insights("conv_123")

                    assert result["vocabulary_learned"] == 5
                    assert result["grammar_points"] == 2
                    mock_insights.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_learning_insights_conversation_not_found(self):
        """Test generating insights for non-existent conversation"""
        with patch.dict(self.manager.active_conversations, {}):
            result = await self.manager.generate_learning_insights("nonexistent")

            assert result == {"error": "Conversation not found"}


class TestConvenienceFunctions:
    """Test convenience/backward compatibility functions"""

    @pytest.mark.asyncio
    async def test_start_learning_conversation(self):
        """Test start_learning_conversation convenience function"""
        with patch.object(
            conversation_manager, "start_conversation", new_callable=AsyncMock
        ) as mock_start:
            mock_start.return_value = "conv_789"

            result = await start_learning_conversation(
                user_id="user_1",
                language="es",
                learning_focus="vocabulary",
                topic="colors",
            )

            assert result == "conv_789"
            call_kwargs = mock_start.call_args.kwargs
            assert call_kwargs["user_id"] == "user_1"
            assert call_kwargs["language"] == "es"
            assert call_kwargs["learning_focus"] == LearningFocus.VOCABULARY
            assert call_kwargs["topic"] == "colors"

    @pytest.mark.asyncio
    async def test_send_learning_message(self):
        """Test send_learning_message convenience function"""
        with patch.object(
            conversation_manager, "send_message", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = {"response": "Hola!", "message_id": "msg_5"}

            result = await send_learning_message(
                conversation_id="conv_789",
                user_message="Hola",
                user_id="user_1",
                extra_param="test",
            )

            assert result["response"] == "Hola!"
            call_kwargs = mock_send.call_args.kwargs
            assert call_kwargs["conversation_id"] == "conv_789"
            assert call_kwargs["user_message"] == "Hola"
            assert call_kwargs["user_id"] == "user_1"
            assert call_kwargs["extra_param"] == "test"

    @pytest.mark.asyncio
    async def test_get_conversation_summary_convenience(self):
        """Test get_conversation_summary convenience function"""
        with patch.object(
            conversation_manager, "get_conversation_summary", new_callable=AsyncMock
        ) as mock_summary:
            mock_summary.return_value = {"summary": "Great session"}

            result = await get_conversation_summary("conv_789")

            assert result["summary"] == "Great session"
            mock_summary.assert_called_once_with("conv_789")

    @pytest.mark.asyncio
    async def test_end_learning_conversation(self):
        """Test end_learning_conversation convenience function"""
        with patch.object(
            conversation_manager, "end_conversation", new_callable=AsyncMock
        ) as mock_end:
            mock_end.return_value = {"status": "completed", "insights": {}}

            result = await end_learning_conversation("conv_789")

            assert result["status"] == "completed"
            mock_end.assert_called_once_with("conv_789")


class TestGlobalInstance:
    """Test global conversation_manager instance"""

    def test_global_instance_exists(self):
        """Test that global instance exists and is correct type"""
        assert conversation_manager is not None
        assert isinstance(conversation_manager, ConversationManager)

    def test_global_instance_has_managers(self):
        """Test that global instance has required managers"""
        assert hasattr(conversation_manager, "state_manager")
        assert hasattr(conversation_manager, "message_handler")
        assert hasattr(conversation_manager, "learning_analyzer")
