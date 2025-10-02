"""
Conversation State Management for AI Language Tutor App

This module manages conversation lifecycle state transitions including starting,
pausing, resuming, and ending conversations. It handles the active conversation
registry, context caching, and coordination with persistence and message handlers.

Features:
- Start new conversation sessions
- Pause and resume conversations
- End conversations with summary generation
- Get comprehensive conversation summaries
- Manage active conversations dictionary
- Coordinate with persistence and message handlers
- Support scenario-based conversations

Extracted from conversation_manager.py to provide focused state lifecycle
management with clear separation of concerns.

Complexity: ~200 lines, <250 cyclomatic complexity
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from app.services.conversation_models import (
    ConversationContext,
    ConversationStatus,
    MessageRole,
    LearningFocus,
)
from app.services.conversation_persistence import conversation_persistence
from app.services.conversation_messages import message_handler
from app.services.scenario_manager import scenario_manager
from app.services.conversation_prompts import (
    create_learning_system_message,
    create_scenario_system_message,
)

logger = logging.getLogger(__name__)


class ConversationStateManager:
    """
    Manages conversation lifecycle and state transitions.

    This class handles the complete lifecycle of conversations including creation,
    state transitions (pause/resume/end), and summary generation. It maintains
    the active conversations registry and coordinates with persistence and message
    handlers for state management operations.
    """

    def __init__(self):
        """Initialize the conversation state manager with empty registries."""
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.context_cache: Dict[str, Any] = {}

    async def start_conversation(
        self,
        user_id: str,
        language: str,
        learning_focus: LearningFocus = LearningFocus.CONVERSATION,
        topic: Optional[str] = None,
        learning_goals: Optional[List[str]] = None,
        scenario_id: Optional[str] = None,
    ) -> str:
        """
        Start a new conversation session.

        Creates a new conversation context, initializes scenario-based learning
        if applicable, sets up the system message, and persists to database.

        Args:
            user_id: User identifier
            language: Target language for learning
            learning_focus: Primary learning focus area
            topic: Conversation topic (optional)
            learning_goals: Specific learning goals for this session
            scenario_id: Optional scenario ID for structured practice

        Returns:
            Newly created conversation ID

        Raises:
            Exception: If scenario setup or database persistence fails
        """
        conversation_id = str(uuid4())

        # Handle scenario-based conversation setup
        scenario_progress_id = None
        if scenario_id:
            # Start scenario conversation
            scenario_data = await scenario_manager.start_scenario_conversation(
                user_id=user_id, scenario_id=scenario_id, language=language
            )
            scenario_progress_id = scenario_data["progress_id"]
            topic = scenario_data["scenario"]  # Use scenario name as topic

        # Create conversation context
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            language=language,
            learning_focus=learning_focus,
            current_topic=topic,
            learning_goals=learning_goals or [],
            session_start_time=datetime.now(),
            last_activity=datetime.now(),
            is_scenario_based=bool(scenario_id),
            scenario_id=scenario_id,
            scenario_progress_id=scenario_progress_id,
        )

        # Store in active conversations
        self.active_conversations[conversation_id] = context

        # Create system message with learning context
        if context.is_scenario_based and scenario_progress_id:
            # Get scenario opening message
            scenario_data = await scenario_manager.get_scenario_progress(
                scenario_progress_id
            )
            if scenario_data:
                system_message = create_scenario_system_message(context, scenario_data)
            else:
                system_message = create_learning_system_message(context)
        else:
            system_message = create_learning_system_message(context)

        await message_handler._add_message(
            conversation_id=conversation_id,
            role=MessageRole.SYSTEM,
            content=system_message,
            language=language,
        )

        # Save to database
        await self._save_conversation_to_db(conversation_id)

        logger.info(
            f"Started conversation {conversation_id} for user {user_id} in {language}"
        )

        return conversation_id

    async def pause_conversation(self, conversation_id: str) -> None:
        """
        Pause an active conversation.

        Saves the current state to database and updates the last activity
        timestamp. The conversation remains in memory for quick resume.

        Args:
            conversation_id: Conversation identifier to pause

        Raises:
            ValueError: If conversation_id is not found in active conversations
        """
        if conversation_id in self.active_conversations:
            # Save current state to database
            await self._save_conversation_to_db(conversation_id)
            await self._save_messages_to_db(conversation_id)

            # Move to inactive state but keep in memory for quick resume
            context = self.active_conversations[conversation_id]
            context.last_activity = datetime.now()

            logger.info(f"Paused conversation {conversation_id}")
        else:
            logger.warning(
                f"Attempted to pause non-existent conversation {conversation_id}"
            )

    async def resume_conversation(self, conversation_id: str) -> bool:
        """
        Resume a paused conversation.

        Loads conversation from database if not in memory, updates last activity
        timestamp, and prepares for continued interaction.

        Args:
            conversation_id: Conversation identifier to resume

        Returns:
            True if successfully resumed, False if conversation not found

        Raises:
            Exception: If database load operation fails
        """
        if conversation_id not in self.active_conversations:
            # Try to load from database
            success = await self._load_conversation_from_db(conversation_id)
            if not success:
                logger.warning(
                    f"Failed to resume conversation {conversation_id}: not found in database"
                )
                return False

        context = self.active_conversations[conversation_id]
        context.last_activity = datetime.now()

        logger.info(f"Resumed conversation {conversation_id}")
        return True

    async def end_conversation(
        self, conversation_id: str, save_learning_progress: bool = True
    ) -> Dict[str, Any]:
        """
        End a conversation and generate final summary.

        Generates comprehensive conversation summary, saves final state to
        database, optionally saves learning progress, and cleans up from
        active conversations and message history.

        Args:
            conversation_id: Conversation identifier to end
            save_learning_progress: Whether to save learning progress to database

        Returns:
            Dictionary containing conversation summary and final insights

        Raises:
            ValueError: If conversation_id not found in active conversations
        """
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Generate final learning summary
        summary = await self.get_conversation_summary(conversation_id)

        # Save to database
        await self._save_conversation_to_db(conversation_id, status="completed")
        await self._save_messages_to_db(conversation_id)

        if save_learning_progress:
            await self._save_learning_progress(conversation_id)

        # Clean up from active conversations
        del self.active_conversations[conversation_id]
        if conversation_id in message_handler.message_history:
            del message_handler.message_history[conversation_id]

        logger.info(f"Ended conversation {conversation_id}")

        return {
            "conversation_summary": summary,
            "final_insights": {
                "total_vocabulary_learned": len(
                    summary["learning_progress"]["vocabulary_introduced"]
                ),
                "mistakes_corrected": len(
                    summary["learning_progress"]["mistakes_tracked"]
                ),
                "session_quality": "good"
                if summary["session_stats"]["user_messages"] >= 5
                else "short",
            },
        }

    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get comprehensive conversation summary.

        Generates detailed summary including session statistics, learning
        progress, and conversation metadata.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Dictionary with comprehensive conversation summary including:
                - conversation_id, user_id, language, learning_focus
                - session_stats (duration, message counts, timestamps)
                - learning_progress (vocabulary, mistakes, goals)

        Raises:
            ValueError: If conversation_id not found in active conversations
        """
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        context = self.active_conversations[conversation_id]
        messages = message_handler.message_history.get(conversation_id, [])

        # Calculate session statistics
        user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
        ai_messages = [msg for msg in messages if msg.role == MessageRole.ASSISTANT]

        session_duration = (datetime.now() - context.session_start_time).total_seconds()

        return {
            "conversation_id": conversation_id,
            "user_id": context.user_id,
            "language": context.language,
            "learning_focus": context.learning_focus.value,
            "current_topic": context.current_topic,
            "session_stats": {
                "duration_minutes": round(session_duration / 60, 2),
                "user_messages": len(user_messages),
                "ai_messages": len(ai_messages),
                "total_messages": len(messages),
                "started_at": context.session_start_time.isoformat(),
                "last_activity": context.last_activity.isoformat(),
            },
            "learning_progress": {
                "vocabulary_introduced": context.vocabulary_introduced,
                "mistakes_tracked": context.mistakes_tracked,
                "learning_goals": context.learning_goals,
                "vocabulary_level": context.vocabulary_level,
            },
        }

    # Private helper methods

    async def _save_conversation_to_db(
        self, conversation_id: str, status: str = "active"
    ) -> None:
        """
        Save conversation metadata to database.

        Args:
            conversation_id: Conversation identifier
            status: Conversation status (active, paused, completed)
        """
        context = self.active_conversations.get(conversation_id)
        if context:
            await conversation_persistence.save_conversation_to_db(
                conversation_id=conversation_id, context=context, status=status
            )

    async def _save_messages_to_db(self, conversation_id: str) -> None:
        """
        Save conversation messages to database.

        Args:
            conversation_id: Conversation identifier
        """
        messages = message_handler.message_history.get(conversation_id, [])
        if messages:
            await conversation_persistence.save_messages_to_db(
                conversation_id=conversation_id, messages=messages
            )

    async def _save_learning_progress(self, conversation_id: str) -> None:
        """
        Save learning progress to database.

        Args:
            conversation_id: Conversation identifier
        """
        context = self.active_conversations.get(conversation_id)
        if context:
            await conversation_persistence.save_learning_progress(
                conversation_id=conversation_id, context=context
            )

    async def _load_conversation_from_db(self, conversation_id: str) -> bool:
        """
        Load conversation from database and restore to active state.

        Reconstructs conversation context and message history from database
        and restores them to the active conversations registry.

        Args:
            conversation_id: Conversation identifier to load

        Returns:
            True if successfully loaded, False if not found or error occurred
        """
        conversation_data = await conversation_persistence.load_conversation_from_db(
            conversation_id=conversation_id
        )

        if not conversation_data:
            return False

        # Reconstruct conversation context from database data
        context_data = conversation_data.get("context_data", {})
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=conversation_data["user_id"],
            language=conversation_data["language"],
            learning_focus=LearningFocus(
                context_data.get("learning_focus", "conversation")
            ),
            current_topic=context_data.get("current_topic"),
            vocabulary_level=context_data.get("vocabulary_level", "intermediate"),
            learning_goals=context_data.get("learning_goals", []),
            session_start_time=conversation_data.get("started_at"),
            last_activity=conversation_data.get("last_message_at"),
            is_scenario_based=context_data.get("is_scenario_based", False),
            scenario_id=context_data.get("scenario_id"),
            scenario_progress_id=context_data.get("scenario_progress_id"),
            scenario_phase=context_data.get("scenario_phase"),
        )

        # Restore conversation context
        self.active_conversations[conversation_id] = context

        # Restore message history
        db_messages = conversation_data.get("messages", [])
        restored_messages = []
        for msg in db_messages:
            from app.services.conversation_models import ConversationMessage

            message = ConversationMessage(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                language=msg["language"],
                metadata=msg.get("metadata", {}),
            )
            restored_messages.append(message)

        message_handler.message_history[conversation_id] = restored_messages

        logger.info(f"Successfully loaded conversation {conversation_id} from database")
        return True


# Global conversation state manager instance
conversation_state_manager = ConversationStateManager()
