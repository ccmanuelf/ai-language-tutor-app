"""
Conversation Manager Facade for AI Language Tutor App

This module provides a clean facade that delegates all conversation operations
to specialized modules: state_manager, message_handler, and learning_analyzer.

Simple orchestration layer - no complex logic, just routing to appropriate modules.
"""

import logging
from typing import Dict, List, Any, Optional

from app.services.conversation_models import ConversationContext, LearningFocus
from app.services.conversation_state import conversation_state_manager
from app.services.conversation_messages import message_handler
from app.services.conversation_analytics import learning_analyzer

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Facade for conversation management - delegates to specialized modules.

    Delegates to:
    - state_manager: Lifecycle and state transitions
    - message_handler: Message processing and AI responses
    - learning_analyzer: Learning insights and analytics
    """

    def __init__(self):
        self.state_manager = conversation_state_manager
        self.message_handler = message_handler
        self.learning_analyzer = learning_analyzer

    # Convenience properties for backward compatibility
    @property
    def active_conversations(self) -> Dict[str, ConversationContext]:
        """Access active conversations from state manager."""
        return self.state_manager.active_conversations

    @property
    def context_cache(self) -> Dict[str, Any]:
        """Access context cache from state manager."""
        return self.state_manager.context_cache

    @property
    def message_history(self) -> Dict[str, List[Any]]:
        """Access message history from message handler."""
        return self.message_handler.message_history

    # Public API - all methods delegate to specialized modules

    async def start_conversation(
        self,
        user_id: str,
        language: str,
        learning_focus: LearningFocus = LearningFocus.CONVERSATION,
        topic: Optional[str] = None,
        learning_goals: Optional[List[str]] = None,
        scenario_id: Optional[str] = None,
    ) -> str:
        """Start new conversation → state_manager"""
        return await self.state_manager.start_conversation(
            user_id=user_id,
            language=language,
            learning_focus=learning_focus,
            topic=topic,
            learning_goals=learning_goals,
            scenario_id=scenario_id,
        )

    async def send_message(
        self,
        conversation_id: str,
        user_message: str,
        include_pronunciation_feedback: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send message and get AI response → message_handler"""
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found or inactive")

        context = self.active_conversations[conversation_id]

        response = await self.message_handler.send_message(
            conversation_id=conversation_id,
            user_message=user_message,
            context=context,
            include_pronunciation_feedback=include_pronunciation_feedback,
            **kwargs,
        )

        # Save messages after processing
        await self.state_manager._save_messages_to_db(conversation_id)

        return response

    async def get_conversation_history(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history → message_handler"""
        return await self.message_handler.get_conversation_history(
            conversation_id, limit
        )

    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary → state_manager"""
        return await self.state_manager.get_conversation_summary(conversation_id)

    async def pause_conversation(self, conversation_id: str) -> None:
        """Pause conversation → state_manager"""
        await self.state_manager.pause_conversation(conversation_id)

    async def resume_conversation(self, conversation_id: str) -> bool:
        """Resume conversation → state_manager"""
        return await self.state_manager.resume_conversation(conversation_id)

    async def end_conversation(
        self, conversation_id: str, save_learning_progress: bool = True
    ) -> Dict[str, Any]:
        """End conversation → state_manager"""
        return await self.state_manager.end_conversation(
            conversation_id, save_learning_progress
        )

    async def generate_learning_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Generate learning insights → learning_analyzer"""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}

        context = self.active_conversations[conversation_id]
        messages = self.message_handler.message_history.get(conversation_id, [])

        return await self.learning_analyzer.generate_session_insights(
            conversation_id=conversation_id, context=context, messages=messages
        )


# Global instance
conversation_manager = ConversationManager()


# Convenience functions for backward compatibility
async def start_learning_conversation(
    user_id: str,
    language: str,
    learning_focus: str = "conversation",
    topic: Optional[str] = None,
) -> str:
    """Start a new learning conversation."""
    focus = LearningFocus(learning_focus)
    return await conversation_manager.start_conversation(
        user_id=user_id, language=language, learning_focus=focus, topic=topic
    )


async def send_learning_message(
    conversation_id: str, user_message: str, user_id: str, **kwargs
) -> Dict[str, Any]:
    """Send a message in a learning conversation."""
    return await conversation_manager.send_message(
        conversation_id=conversation_id,
        user_message=user_message,
        user_id=user_id,
        **kwargs,
    )


async def get_conversation_summary(conversation_id: str) -> Dict[str, Any]:
    """Get conversation summary."""
    return await conversation_manager.get_conversation_summary(conversation_id)


async def end_learning_conversation(conversation_id: str) -> Dict[str, Any]:
    """End a learning conversation."""
    return await conversation_manager.end_conversation(conversation_id)
