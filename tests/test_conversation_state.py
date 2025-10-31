"""
Comprehensive tests for conversation_state.py - Conversation State Management

Focus on reaching 90%+ coverage by testing conversation lifecycle,
state transitions, database operations, and scenario-based conversations.

Target: 58% -> 90%+ coverage (43 uncovered lines to cover)
"""

from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    LearningFocus,
    MessageRole,
)
from app.services.conversation_state import (
    ConversationStateManager,
    conversation_state_manager,
)


class TestConversationStateManagerInit:
    """Test ConversationStateManager initialization"""

    def test_init_creates_empty_registries(self):
        """Test that initialization creates empty dictionaries"""
        manager = ConversationStateManager()

        assert isinstance(manager.active_conversations, dict)
        assert len(manager.active_conversations) == 0
        assert isinstance(manager.context_cache, dict)
        assert len(manager.context_cache) == 0


class TestStartConversation:
    """Test start_conversation method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationStateManager()

    @pytest.mark.asyncio
    async def test_start_conversation_basic(self):
        """Test starting a basic conversation"""
        with patch.object(
            self.manager, "_save_conversation_to_db", new_callable=AsyncMock
        ):
            with patch(
                "app.services.conversation_state.message_handler._add_message",
                new_callable=AsyncMock,
            ):
                conv_id = await self.manager.start_conversation(
                    user_id="user_1", language="en"
                )

                assert conv_id is not None
                assert conv_id in self.manager.active_conversations

                context = self.manager.active_conversations[conv_id]
                assert context.user_id == "user_1"
                assert context.language == "en"
                assert context.learning_focus == LearningFocus.CONVERSATION

    @pytest.mark.asyncio
    async def test_start_conversation_with_all_params(self):
        """Test starting conversation with all parameters"""
        with patch.object(
            self.manager, "_save_conversation_to_db", new_callable=AsyncMock
        ):
            with patch(
                "app.services.conversation_state.message_handler._add_message",
                new_callable=AsyncMock,
            ):
                conv_id = await self.manager.start_conversation(
                    user_id="user_2",
                    language="fr",
                    learning_focus=LearningFocus.VOCABULARY,
                    topic="food",
                    learning_goals=["learn greetings", "practice pronunciation"],
                )

                context = self.manager.active_conversations[conv_id]
                assert context.language == "fr"
                assert context.learning_focus == LearningFocus.VOCABULARY
                assert context.current_topic == "food"
                assert len(context.learning_goals) == 2

    @pytest.mark.asyncio
    async def test_start_conversation_with_scenario(self):
        """Test starting a scenario-based conversation"""
        mock_scenario_data = {
            "progress_id": "progress_123",
            "scenario": "Restaurant ordering",
            "phase": "greeting",
        }

        with patch.object(
            self.manager, "_save_conversation_to_db", new_callable=AsyncMock
        ):
            with patch(
                "app.services.conversation_state.message_handler._add_message",
                new_callable=AsyncMock,
            ):
                with patch(
                    "app.services.conversation_state.scenario_manager.start_scenario_conversation",
                    new_callable=AsyncMock,
                    return_value=mock_scenario_data,
                ) as mock_start_scenario:
                    with patch(
                        "app.services.conversation_state.scenario_manager.get_scenario_progress",
                        new_callable=AsyncMock,
                        return_value={"phase": "greeting", "context": "restaurant"},
                    ):
                        conv_id = await self.manager.start_conversation(
                            user_id="user_3",
                            language="es",
                            scenario_id="scenario_456",
                        )

                        context = self.manager.active_conversations[conv_id]
                        assert context.is_scenario_based is True
                        assert context.scenario_id == "scenario_456"
                        assert context.scenario_progress_id == "progress_123"
                        assert context.current_topic == "Restaurant ordering"
                        mock_start_scenario.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_conversation_scenario_without_progress(self):
        """Test scenario conversation when scenario_manager returns no progress"""
        mock_scenario_data = {
            "progress_id": "progress_456",
            "scenario": "Shopping",
            "phase": "browsing",
        }

        with patch.object(
            self.manager, "_save_conversation_to_db", new_callable=AsyncMock
        ):
            with patch(
                "app.services.conversation_state.message_handler._add_message",
                new_callable=AsyncMock,
            ):
                with patch(
                    "app.services.conversation_state.scenario_manager.start_scenario_conversation",
                    new_callable=AsyncMock,
                    return_value=mock_scenario_data,
                ):
                    # Mock get_scenario_progress to return None
                    with patch(
                        "app.services.conversation_state.scenario_manager.get_scenario_progress",
                        new_callable=AsyncMock,
                        return_value=None,
                    ):
                        conv_id = await self.manager.start_conversation(
                            user_id="user_4",
                            language="de",
                            scenario_id="scenario_789",
                        )

                        # Should still create conversation with basic learning system message
                        assert conv_id in self.manager.active_conversations


class TestPauseConversation:
    """Test pause_conversation method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationStateManager()

    @pytest.mark.asyncio
    async def test_pause_existing_conversation(self):
        """Test pausing an active conversation"""
        # Create active conversation
        conv_id = "conv_123"
        context = MagicMock(spec=ConversationContext)
        context.conversation_id = conv_id
        context.last_activity = datetime.now()
        self.manager.active_conversations[conv_id] = context

        with patch.object(
            self.manager, "_save_conversation_to_db", new_callable=AsyncMock
        ) as mock_save_conv:
            with patch.object(
                self.manager, "_save_messages_to_db", new_callable=AsyncMock
            ) as mock_save_msgs:
                await self.manager.pause_conversation(conv_id)

                mock_save_conv.assert_called_once_with(conv_id)
                mock_save_msgs.assert_called_once_with(conv_id)
                # Conversation should still be in active_conversations
                assert conv_id in self.manager.active_conversations

    @pytest.mark.asyncio
    async def test_pause_nonexistent_conversation(self):
        """Test pausing a non-existent conversation"""
        with patch.object(
            self.manager, "_save_conversation_to_db", new_callable=AsyncMock
        ) as mock_save:
            await self.manager.pause_conversation("nonexistent")

            # Should not crash, just log warning
            mock_save.assert_not_called()


class TestResumeConversation:
    """Test resume_conversation method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationStateManager()

    @pytest.mark.asyncio
    async def test_resume_conversation_already_active(self):
        """Test resuming a conversation already in memory"""
        conv_id = "conv_456"
        context = MagicMock(spec=ConversationContext)
        context.conversation_id = conv_id
        context.last_activity = datetime.now()
        self.manager.active_conversations[conv_id] = context

        result = await self.manager.resume_conversation(conv_id)

        assert result is True
        assert conv_id in self.manager.active_conversations

    @pytest.mark.asyncio
    async def test_resume_conversation_from_database(self):
        """Test resuming a conversation from database"""
        conv_id = "conv_789"

        async def mock_load_side_effect(cid):
            # Simulate loading from DB by adding context
            context = MagicMock(spec=ConversationContext)
            context.last_activity = datetime.now()
            self.manager.active_conversations[cid] = context
            return True

        with patch.object(
            self.manager, "_load_conversation_from_db", new_callable=AsyncMock
        ) as mock_load:
            mock_load.side_effect = mock_load_side_effect

            result = await self.manager.resume_conversation(conv_id)

            assert result is True
            mock_load.assert_called_once_with(conv_id)
            assert conv_id in self.manager.active_conversations

    @pytest.mark.asyncio
    async def test_resume_conversation_not_found(self):
        """Test failing to resume non-existent conversation"""
        with patch.object(
            self.manager, "_load_conversation_from_db", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = False

            result = await self.manager.resume_conversation("nonexistent")

            assert result is False
            mock_load.assert_called_once_with("nonexistent")


class TestEndConversation:
    """Test end_conversation method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationStateManager()

    @pytest.mark.asyncio
    async def test_end_conversation_with_save(self):
        """Test ending conversation with saving progress"""
        conv_id = "conv_end_1"
        context = MagicMock(spec=ConversationContext)
        context.conversation_id = conv_id
        context.session_start_time = datetime.now()
        context.last_activity = datetime.now()
        context.user_id = "user_1"
        context.language = "en"
        context.learning_focus = LearningFocus.CONVERSATION
        context.current_topic = "travel"
        context.vocabulary_introduced = ["hello", "goodbye"]
        context.mistakes_tracked = [{"error": "grammer"}]
        context.learning_goals = []
        context.vocabulary_level = "beginner"

        self.manager.active_conversations[conv_id] = context

        with patch(
            "app.services.conversation_state.message_handler.message_history", {}
        ):
            with patch.object(
                self.manager, "_save_conversation_to_db", new_callable=AsyncMock
            ):
                with patch.object(
                    self.manager, "_save_messages_to_db", new_callable=AsyncMock
                ):
                    with patch.object(
                        self.manager, "_save_learning_progress", new_callable=AsyncMock
                    ) as mock_save_progress:
                        result = await self.manager.end_conversation(
                            conv_id, save_learning_progress=True
                        )

                        assert "conversation_summary" in result
                        assert "final_insights" in result
                        assert conv_id not in self.manager.active_conversations
                        mock_save_progress.assert_called_once_with(conv_id)

    @pytest.mark.asyncio
    async def test_end_conversation_without_save(self):
        """Test ending conversation without saving progress"""
        conv_id = "conv_end_2"
        context = MagicMock(spec=ConversationContext)
        context.conversation_id = conv_id
        context.session_start_time = datetime.now()
        context.last_activity = datetime.now()
        context.user_id = "user_2"
        context.language = "fr"
        context.learning_focus = LearningFocus.GRAMMAR
        context.current_topic = "verbs"
        context.vocabulary_introduced = []
        context.mistakes_tracked = []
        context.learning_goals = ["conjugation"]
        context.vocabulary_level = "intermediate"

        self.manager.active_conversations[conv_id] = context

        with patch(
            "app.services.conversation_state.message_handler.message_history",
            {conv_id: []},
        ):
            with patch.object(
                self.manager, "_save_conversation_to_db", new_callable=AsyncMock
            ):
                with patch.object(
                    self.manager, "_save_messages_to_db", new_callable=AsyncMock
                ):
                    with patch.object(
                        self.manager, "_save_learning_progress", new_callable=AsyncMock
                    ) as mock_save_progress:
                        result = await self.manager.end_conversation(
                            conv_id, save_learning_progress=False
                        )

                        assert result is not None
                        assert conv_id not in self.manager.active_conversations
                        mock_save_progress.assert_not_called()

    @pytest.mark.asyncio
    async def test_end_conversation_not_found(self):
        """Test ending non-existent conversation"""
        with pytest.raises(ValueError) as exc_info:
            await self.manager.end_conversation("nonexistent")

        assert "not found" in str(exc_info.value)


class TestGetConversationSummary:
    """Test get_conversation_summary method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationStateManager()

    @pytest.mark.asyncio
    async def test_get_conversation_summary_success(self):
        """Test getting conversation summary"""
        conv_id = "conv_summary_1"
        start_time = datetime.now()

        context = MagicMock(spec=ConversationContext)
        context.conversation_id = conv_id
        context.user_id = "user_1"
        context.language = "es"
        context.learning_focus = LearningFocus.PRONUNCIATION
        context.current_topic = "numbers"
        context.session_start_time = start_time
        context.last_activity = datetime.now()
        context.vocabulary_introduced = ["uno", "dos", "tres"]
        context.mistakes_tracked = []
        context.learning_goals = ["count to 10"]
        context.vocabulary_level = "beginner"

        self.manager.active_conversations[conv_id] = context

        # Mock messages
        mock_messages = [
            MagicMock(role=MessageRole.USER),
            MagicMock(role=MessageRole.ASSISTANT),
            MagicMock(role=MessageRole.USER),
            MagicMock(role=MessageRole.ASSISTANT),
        ]

        with patch(
            "app.services.conversation_state.message_handler.message_history",
            {conv_id: mock_messages},
        ):
            summary = await self.manager.get_conversation_summary(conv_id)

            assert summary["conversation_id"] == conv_id
            assert summary["user_id"] == "user_1"
            assert summary["language"] == "es"
            assert summary["learning_focus"] == "pronunciation"
            assert summary["session_stats"]["user_messages"] == 2
            assert summary["session_stats"]["ai_messages"] == 2
            assert summary["learning_progress"]["vocabulary_introduced"] == [
                "uno",
                "dos",
                "tres",
            ]

    @pytest.mark.asyncio
    async def test_get_conversation_summary_not_found(self):
        """Test getting summary for non-existent conversation"""
        with pytest.raises(ValueError) as exc_info:
            await self.manager.get_conversation_summary("nonexistent")

        assert "not found" in str(exc_info.value)


class TestPrivateHelperMethods:
    """Test private helper methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ConversationStateManager()

    @pytest.mark.asyncio
    async def test_save_conversation_to_db(self):
        """Test saving conversation to database"""
        conv_id = "conv_save_1"
        context = MagicMock(spec=ConversationContext)
        self.manager.active_conversations[conv_id] = context

        with patch(
            "app.services.conversation_state.conversation_persistence.save_conversation_to_db",
            new_callable=AsyncMock,
        ) as mock_save:
            await self.manager._save_conversation_to_db(conv_id, status="active")

            mock_save.assert_called_once_with(
                conversation_id=conv_id, context=context, status="active"
            )

    @pytest.mark.asyncio
    async def test_save_messages_to_db(self):
        """Test saving messages to database"""
        conv_id = "conv_save_2"
        mock_messages = [MagicMock(), MagicMock()]

        with patch(
            "app.services.conversation_state.message_handler.message_history",
            {conv_id: mock_messages},
        ):
            with patch(
                "app.services.conversation_state.conversation_persistence.save_messages_to_db",
                new_callable=AsyncMock,
            ) as mock_save:
                await self.manager._save_messages_to_db(conv_id)

                mock_save.assert_called_once_with(
                    conversation_id=conv_id, messages=mock_messages
                )

    @pytest.mark.asyncio
    async def test_save_learning_progress(self):
        """Test saving learning progress"""
        conv_id = "conv_save_3"
        context = MagicMock(spec=ConversationContext)
        self.manager.active_conversations[conv_id] = context

        with patch(
            "app.services.conversation_state.conversation_persistence.save_learning_progress",
            new_callable=AsyncMock,
        ) as mock_save:
            await self.manager._save_learning_progress(conv_id)

            mock_save.assert_called_once_with(conversation_id=conv_id, context=context)

    @pytest.mark.asyncio
    async def test_load_conversation_from_db_success(self):
        """Test successfully loading conversation from database"""
        conv_id = "conv_load_1"
        mock_db_data = {
            "user_id": "user_1",
            "language": "en",
            "started_at": datetime.now(),
            "last_message_at": datetime.now(),
            "context_data": {
                "learning_focus": "conversation",
                "current_topic": "weather",
                "vocabulary_level": "intermediate",
                "learning_goals": ["small talk"],
                "is_scenario_based": False,
            },
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": datetime.now().isoformat(),
                    "language": "en",
                    "metadata": {},
                }
            ],
        }

        with patch(
            "app.services.conversation_state.conversation_persistence.load_conversation_from_db",
            new_callable=AsyncMock,
            return_value=mock_db_data,
        ):
            with patch(
                "app.services.conversation_state.message_handler.message_history", {}
            ):
                result = await self.manager._load_conversation_from_db(conv_id)

                assert result is True
                assert conv_id in self.manager.active_conversations
                context = self.manager.active_conversations[conv_id]
                assert context.user_id == "user_1"
                assert context.language == "en"

    @pytest.mark.asyncio
    async def test_load_conversation_from_db_not_found(self):
        """Test loading non-existent conversation from database"""
        with patch(
            "app.services.conversation_state.conversation_persistence.load_conversation_from_db",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await self.manager._load_conversation_from_db("nonexistent")

            assert result is False


class TestGlobalInstance:
    """Test global conversation_state_manager instance"""

    def test_global_instance_exists(self):
        """Test that global instance exists"""
        assert conversation_state_manager is not None
        assert isinstance(conversation_state_manager, ConversationStateManager)

    def test_global_instance_has_registries(self):
        """Test that global instance has required attributes"""
        assert hasattr(conversation_state_manager, "active_conversations")
        assert hasattr(conversation_state_manager, "context_cache")
