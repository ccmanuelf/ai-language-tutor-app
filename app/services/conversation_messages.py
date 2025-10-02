"""
Message Handling and Conversation Flow for AI Language Tutor App

This module handles message processing, AI response generation, and conversation
flow management. It coordinates between user messages, AI responses, learning
analytics, and scenario interactions.

Features:
- User message processing and validation
- AI response generation with error handling
- Scenario-based interaction handling
- Conversation response building
- Message history management
- Context preparation for AI providers
- Context compression for long conversations

This module is extracted from conversation_manager to provide focused,
maintainable message handling with clear separation of concerns.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.conversation_models import (
    MessageRole,
    ConversationMessage,
    LearningInsight,
)
from app.services.conversation_analytics import learning_analyzer
from app.services.ai_router import generate_ai_response
from app.services.scenario_manager import scenario_manager

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles message processing and conversation flow.

    This class manages the complete message lifecycle including user message
    processing, AI response generation, scenario interactions, and response
    building. It maintains message history and handles context compression.
    """

    def __init__(self):
        """Initialize the message handler with empty message history."""
        self.message_history: Dict[str, List[ConversationMessage]] = {}
        self.max_context_messages = 20  # Maximum messages for AI context
        self.context_compression_threshold = 50  # Compress beyond this count

    async def send_message(
        self,
        conversation_id: str,
        user_message: str,
        context: Any,  # ConversationContext type
        include_pronunciation_feedback: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Main coordinator for sending a message and getting a response.

        This is the entry point for message processing. It orchestrates the
        complete flow: user message processing, AI response generation,
        scenario handling, and response building.

        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's message text
            context: Current conversation context
            include_pronunciation_feedback: Whether to include pronunciation analysis
            **kwargs: Additional parameters for AI generation

        Returns:
            Complete conversation response with AI reply and learning insights

        Raises:
            ValueError: If conversation_id is not found in message history
        """
        # Step 1: Process and add user message
        user_insights = await self.process_user_message(
            conversation_id, user_message, context
        )

        # Step 2: Generate AI response
        ai_response = await self.generate_ai_response(
            conversation_id, context, include_pronunciation_feedback, **kwargs
        )

        # Check if AI response generation failed
        if "error" in ai_response:
            return ai_response

        # Step 3: Handle scenario interactions if applicable
        scenario_progress = await self.handle_scenario_interaction(
            context, user_message, ai_response["content"]
        )

        # Update context with scenario phase if available
        if scenario_progress and "current_phase" in scenario_progress:
            context.scenario_phase = scenario_progress["current_phase"]

        # Step 4: Build and return complete response
        return await self.build_conversation_response(
            conversation_id=conversation_id,
            user_message=user_message,
            ai_response=ai_response,
            context=context,
            scenario_progress=scenario_progress,
        )

    async def process_user_message(
        self, conversation_id: str, user_message: str, context: Any
    ) -> Dict[str, Any]:
        """
        Process and add user message to conversation history.

        Validates the user message, adds it to the conversation history,
        and analyzes it for learning insights.

        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's message text
            context: Current conversation context

        Returns:
            Dictionary containing user message insights and analysis
        """
        # Add user message to history
        await self._add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message,
            language=context.language,
        )

        # Analyze user message for learning insights
        user_insights = await learning_analyzer.analyze_user_message(
            user_message=user_message, context=context
        )

        logger.debug(
            f"Processed user message for conversation {conversation_id}: "
            f"{user_insights.get('word_count', 0)} words"
        )

        return user_insights

    async def generate_ai_response(
        self,
        conversation_id: str,
        context: Any,
        include_pronunciation_feedback: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate AI response based on conversation context.

        Prepares the conversation context for the AI, generates a response,
        and adds it to the message history with metadata.

        Args:
            conversation_id: Unique identifier for the conversation
            context: Current conversation context
            include_pronunciation_feedback: Whether to include pronunciation analysis
            **kwargs: Additional parameters for AI generation

        Returns:
            Dictionary containing:
                - content: AI response text
                - model: Model used for generation
                - provider: AI provider used
                - processing_time: Time taken to generate response
                - cost: Cost of the API call
                - error: Error message if generation failed (optional)
        """
        try:
            # Prepare conversation context for AI
            conversation_messages = await self._prepare_ai_context(conversation_id)

            # Get AI response
            ai_response = await generate_ai_response(
                messages=conversation_messages,
                language=context.language,
                use_case=context.learning_focus.value,
                user_preferences={
                    "learning_level": context.vocabulary_level,
                    "focus_areas": context.learning_goals,
                    "pronunciation_feedback": include_pronunciation_feedback,
                },
                **kwargs,
            )

            # Add AI response to history
            await self._add_message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=ai_response.content,
                language=context.language,
                metadata={
                    "model": ai_response.model,
                    "provider": ai_response.provider,
                    "processing_time": ai_response.processing_time,
                    "cost": ai_response.cost,
                },
            )

            logger.info(
                f"Generated AI response for conversation {conversation_id}: "
                f"model={ai_response.model}, cost={ai_response.cost}"
            )

            return {
                "content": ai_response.content,
                "model": ai_response.model,
                "provider": ai_response.provider,
                "processing_time": ai_response.processing_time,
                "cost": ai_response.cost,
                "metadata": ai_response.metadata,
            }

        except Exception as e:
            logger.error(
                f"Failed to generate AI response for conversation {conversation_id}: {e}"
            )

            # Return error response
            return {
                "content": "I'm sorry, I'm having trouble responding right now. Could you please try again?",
                "error": str(e),
                "model": "error",
                "provider": "error",
                "processing_time": 0,
                "cost": 0,
            }

    async def handle_scenario_interaction(
        self, context: Any, user_message: str, ai_response: str
    ) -> Optional[Dict[str, Any]]:
        """
        Handle scenario-based interaction processing.

        Processes the message exchange in the context of a scenario-based
        learning session, updating scenario progress and tracking completion.

        Args:
            context: Current conversation context
            user_message: The user's message text
            ai_response: The AI's response text

        Returns:
            Dictionary with scenario progress information, or None if not
            applicable or if processing fails
        """
        # Only process if conversation is scenario-based
        if not context.is_scenario_based or not context.scenario_progress_id:
            return None

        try:
            scenario_progress = await scenario_manager.process_scenario_message(
                progress_id=context.scenario_progress_id,
                user_message=user_message,
                ai_response=ai_response,
            )

            logger.debug(
                f"Processed scenario interaction for progress_id "
                f"{context.scenario_progress_id}: "
                f"phase={scenario_progress.get('current_phase', 'unknown')}"
            )

            return scenario_progress

        except Exception as e:
            logger.error(f"Failed to process scenario interaction: {e}")
            return None

    async def build_conversation_response(
        self,
        conversation_id: str,
        user_message: str,
        ai_response: Dict[str, Any],
        context: Any,
        scenario_progress: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build the complete conversation response.

        Constructs a comprehensive response object that includes the AI reply,
        learning insights, context information, and scenario progress.

        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's original message
            ai_response: Dictionary with AI response and metadata
            context: Current conversation context
            scenario_progress: Optional scenario progress information

        Returns:
            Complete conversation response dictionary with:
                - conversation_id: Conversation identifier
                - ai_response: AI's text response
                - learning_insights: Learning metrics and feedback
                - context_info: Session and conversation metadata
                - ai_metadata: AI provider and cost information
                - scenario_progress: Scenario progress (if applicable)
                - error: Error message (if AI generation failed)
        """
        # Handle error response
        if "error" in ai_response:
            return {
                "conversation_id": conversation_id,
                "ai_response": ai_response["content"],
                "error": ai_response["error"],
                "learning_insights": LearningInsight(
                    vocabulary_new=[],
                    vocabulary_practiced=[],
                    grammar_corrections=[],
                    pronunciation_feedback=[],
                    conversation_quality_score=0.0,
                    engagement_level="error",
                    suggested_focus="try_again",
                ),
            }

        # Generate learning insights from the exchange
        learning_insights = await learning_analyzer.generate_learning_insights(
            conversation_id=conversation_id,
            user_message=user_message,
            ai_response=ai_response["content"],
            context=context,
        )

        # Update conversation context with insights
        updated_context = await learning_analyzer.update_conversation_context(
            context=context, insights=learning_insights
        )

        # Calculate session metrics
        session_duration = (datetime.now() - context.session_start_time).total_seconds()
        message_count = len(self.message_history.get(conversation_id, []))

        # Build response dictionary
        response_data = {
            "conversation_id": conversation_id,
            "ai_response": ai_response["content"],
            "learning_insights": learning_insights,
            "context_info": {
                "topic": context.current_topic,
                "vocabulary_level": context.vocabulary_level,
                "session_duration": session_duration,
                "message_count": message_count,
            },
            "ai_metadata": {
                "model": ai_response["model"],
                "provider": ai_response["provider"],
                "cost": ai_response["cost"],
                "is_fallback": ai_response.get("metadata", {})
                .get("router_selection", {})
                .get("is_fallback", False),
            },
        }

        # Add scenario progress if applicable
        if context.is_scenario_based and scenario_progress:
            response_data["scenario_progress"] = scenario_progress

        logger.info(
            f"Built conversation response for {conversation_id}: "
            f"quality={learning_insights.conversation_quality_score:.2f}, "
            f"engagement={learning_insights.engagement_level}"
        )

        return response_data

    async def get_conversation_history(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation message history.

        Retrieves the message history for a conversation, optionally limited
        to the most recent messages. System messages are excluded from the
        returned history.

        Args:
            conversation_id: Unique identifier for the conversation
            limit: Optional maximum number of recent messages to return

        Returns:
            List of message dictionaries with role, content, timestamp, and metadata.
            Returns empty list if conversation_id is not found.
        """
        if conversation_id not in self.message_history:
            return []

        messages = self.message_history[conversation_id]

        # Apply limit if specified
        if limit:
            messages = messages[-limit:]

        # Convert to dictionary format and exclude system messages
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "language": msg.language,
                "metadata": msg.metadata,
            }
            for msg in messages
            if msg.role != MessageRole.SYSTEM
        ]

    # Private helper methods

    async def _add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        language: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a message to conversation history.

        Creates a new ConversationMessage and appends it to the message history.
        Also triggers context compression if the message count exceeds the threshold.

        Args:
            conversation_id: Unique identifier for the conversation
            role: Message role (USER, ASSISTANT, or SYSTEM)
            content: Message text content
            language: Language of the message
            metadata: Optional metadata dictionary
        """
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            language=language,
            metadata=metadata or {},
        )

        # Initialize message history if not exists
        if conversation_id not in self.message_history:
            self.message_history[conversation_id] = []

        self.message_history[conversation_id].append(message)

        logger.debug(
            f"Added {role.value} message to conversation {conversation_id}: "
            f"{len(content)} characters"
        )

        # Compress context if needed
        await self._maybe_compress_context(conversation_id)

    async def _prepare_ai_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Prepare conversation context for AI provider.

        Converts conversation messages to the format expected by AI providers,
        keeping only the most recent messages for context.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        messages = self.message_history.get(conversation_id, [])

        # Convert to AI provider format, keeping recent messages
        ai_messages = []
        for msg in messages[-self.max_context_messages :]:
            ai_messages.append({"role": msg.role.value, "content": msg.content})

        logger.debug(
            f"Prepared AI context for conversation {conversation_id}: "
            f"{len(ai_messages)} messages"
        )

        return ai_messages

    async def _maybe_compress_context(self, conversation_id: str):
        """
        Compress conversation context if it exceeds threshold.

        When the message count exceeds the compression threshold, this method
        creates a summary of older messages and keeps only recent messages
        and system messages to maintain context quality while reducing size.

        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id not in self.message_history:
            return

        messages = self.message_history[conversation_id]

        # Check if compression is needed
        if len(messages) <= self.context_compression_threshold:
            return

        # Separate system messages and recent messages
        system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
        recent_messages = messages[-self.max_context_messages :]

        # Calculate number of compressed messages
        compressed_count = len(messages) - len(recent_messages) - len(system_messages)

        if compressed_count > 0:
            # Get language from recent messages
            language = recent_messages[0].language if recent_messages else "en"

            # Create compression summary message
            summary_message = ConversationMessage(
                role=MessageRole.SYSTEM,
                content=f"[Previous conversation summary: {compressed_count} messages exchanged covering language learning topics]",
                timestamp=datetime.now(),
                language=language,
                metadata={
                    "type": "compression_summary",
                    "compressed_messages": compressed_count,
                },
            )

            # Replace message history with compressed version
            self.message_history[conversation_id] = (
                system_messages
                + [summary_message]
                + recent_messages[-self.max_context_messages :]
            )

            logger.info(
                f"Compressed conversation {conversation_id}: "
                f"{compressed_count} messages summarized"
            )


# Global message handler instance
message_handler = MessageHandler()
