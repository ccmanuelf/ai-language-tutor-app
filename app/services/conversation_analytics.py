"""
Learning Analytics Module for AI Language Tutor App

This module provides learning analytics and insights generation for language
learning conversations. It analyzes user messages, conversation patterns, and
generates actionable learning insights to track progress and guide learning.

Features:
- User message analysis for complexity and engagement
- Learning insights generation from conversation exchanges
- Vocabulary tracking and analysis
- Conversation quality scoring
- Context updates based on learning progress

This module is extracted from conversation_manager to provide focused,
reusable analytics functionality with minimal dependencies.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    LearningInsight,
    MessageRole,
)

logger = logging.getLogger(__name__)


class LearningAnalyzer:
    """
    Analyzes learning conversations and generates insights.

    This class provides methods for analyzing user messages, generating learning
    insights from conversation exchanges, and tracking learning progress over time.
    It focuses on extracting meaningful learning metrics without external dependencies.
    """

    def __init__(self):
        """Initialize the learning analyzer."""
        self.logger = logger

    async def analyze_user_message(
        self, user_message: str, context: ConversationContext
    ) -> Dict[str, Any]:
        """
        Analyze a user message for learning insights.

        Performs a lightweight analysis of the user's message to extract metrics
        about message complexity, engagement indicators, and writing style. This
        analysis helps track the student's progress and engagement level.

        Args:
            user_message: The text content of the user's message
            context: Current conversation context with learning state

        Returns:
            Dictionary containing:
                - message_length: Total character count
                - word_count: Number of words in the message
                - complexity_score: Estimated complexity (0.0-1.0)
                - engagement_indicators: Dict with boolean flags for:
                    - questions: Contains question marks
                    - excitement: Contains exclamation marks
                    - formal_language: Uses formal/polite phrases

        Example:
            >>> analyzer = LearningAnalyzer()
            >>> result = await analyzer.analyze_user_message(
            ...     "Could you please explain this?",
            ...     context
            ... )
            >>> result['engagement_indicators']['formal_language']
            True
        """
        # Calculate basic message metrics
        word_count = len(user_message.split())
        message_length = len(user_message)

        # Compute complexity score based on word count
        # Longer messages with more words indicate higher complexity
        complexity_score = min(word_count / 10, 1.0)

        # Detect engagement indicators in the message
        engagement_indicators = {
            "questions": "?" in user_message,
            "excitement": "!" in user_message,
            "formal_language": any(
                phrase in user_message.lower()
                for phrase in ["please", "thank you", "could you", "would you"]
            ),
        }

        analysis = {
            "message_length": message_length,
            "word_count": word_count,
            "complexity_score": complexity_score,
            "engagement_indicators": engagement_indicators,
        }

        self.logger.debug(
            f"Analyzed user message: {word_count} words, "
            f"complexity={complexity_score:.2f}"
        )

        return analysis

    async def generate_learning_insights(
        self,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        context: ConversationContext,
    ) -> LearningInsight:
        """
        Generate comprehensive learning insights from a conversation exchange.

        Analyzes a complete conversation exchange (user message + AI response) to
        extract learning metrics including new vocabulary, engagement levels, and
        conversation quality. This simplified version uses heuristics that can be
        enhanced with NLP libraries in future iterations.

        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's message text
            ai_response: The AI tutor's response text
            context: Current conversation context with learning history

        Returns:
            LearningInsight object containing:
                - vocabulary_new: New vocabulary words from AI response
                - vocabulary_practiced: Words the student used successfully
                - grammar_corrections: List of grammar corrections (empty for now)
                - pronunciation_feedback: Pronunciation tips (empty for now)
                - conversation_quality_score: Quality metric (0.0-1.0)
                - engagement_level: 'low', 'medium', or 'high'
                - suggested_focus: Recommended learning focus area

        Note:
            This is a simplified implementation using basic heuristics.
            Future enhancements could include:
            - NLP-based grammar analysis
            - Vocabulary difficulty assessment
            - Context-aware vocabulary tracking
            - Advanced sentiment and engagement analysis
        """
        # Extract potential new vocabulary from AI response
        # Split into words and convert to lowercase for comparison
        ai_words = set(ai_response.lower().split())

        # Get words already introduced in this session
        recent_vocabulary = set(context.vocabulary_introduced or [])

        # Find new words (limit to 3 for focused learning)
        potential_new_vocab = list(ai_words - recent_vocabulary)[:3]

        # Calculate engagement score based on message characteristics
        message_length = len(user_message)
        engagement_score = min(message_length / 50, 1.0)

        # Map engagement score to level
        engagement_levels = ["low", "medium", "high"]
        engagement_level = engagement_levels[min(int(engagement_score * 3), 2)]

        # Calculate conversation quality score using multiple factors
        quality_factors = [
            message_length > 10,  # Meaningful message length
            "?" in user_message or "!" in user_message,  # Engagement indicators
            len(user_message.split()) >= 3,  # Multiple words used
        ]

        # Average of quality factors
        quality_score = sum(quality_factors) / len(quality_factors)

        insights = LearningInsight(
            vocabulary_new=potential_new_vocab,
            vocabulary_practiced=[],  # Can be enhanced with vocabulary matching
            grammar_corrections=[],  # Requires NLP for proper implementation
            pronunciation_feedback=[],  # Requires audio analysis
            conversation_quality_score=quality_score,
            engagement_level=engagement_level,
            suggested_focus=context.learning_focus.value,
        )

        self.logger.info(
            f"Generated insights for conversation {conversation_id}: "
            f"quality={quality_score:.2f}, engagement={engagement_level}, "
            f"new_vocab={len(potential_new_vocab)}"
        )

        return insights

    async def generate_session_insights(
        self,
        conversation_id: str,
        context: ConversationContext,
        messages: List[ConversationMessage],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights for an entire learning session.

        Analyzes the full conversation history to provide session-level insights
        including vocabulary usage, learning progress, engagement metrics, and
        session statistics. This public method provides a complete view of the
        learning session.

        Args:
            conversation_id: Unique identifier for the conversation
            context: Current conversation context with learning state
            messages: List of all conversation messages

        Returns:
            Dictionary containing:
                - vocabulary_used: List of vocabulary words from recent exchanges
                - learning_progress: Dict with quality and engagement metrics
                - message_count: Total number of messages
                - session_duration: Duration in minutes
                - new_vocabulary: Recently introduced vocabulary words
                - error: Error message if insights cannot be generated

        Example:
            >>> analyzer = LearningAnalyzer()
            >>> insights = await analyzer.generate_session_insights(
            ...     conv_id, context, messages
            ... )
            >>> insights['learning_progress']['engagement_level']
            'high'
        """
        # Handle edge case: conversation just started
        if len(messages) < 2:
            return {
                "vocabulary_used": [],
                "learning_progress": "conversation_just_started",
                "message_count": len(messages),
                "engagement_level": "beginning",
            }

        # Extract user and AI messages
        user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
        ai_messages = [msg for msg in messages if msg.role == MessageRole.ASSISTANT]

        # Generate insights from most recent exchange
        if user_messages and ai_messages:
            latest_user_msg = user_messages[-1].content
            latest_ai_msg = ai_messages[-1].content

            # Generate learning insights for the latest exchange
            insights = await self.generate_learning_insights(
                conversation_id, latest_user_msg, latest_ai_msg, context
            )

            # Calculate session duration in minutes
            session_duration = (
                datetime.now() - context.session_start_time
            ).total_seconds() / 60

            return {
                "vocabulary_used": context.vocabulary_introduced[-10:],  # Last 10 words
                "learning_progress": {
                    "conversation_quality": insights.conversation_quality_score,
                    "engagement_level": insights.engagement_level,
                    "focus_area": insights.suggested_focus,
                },
                "message_count": len(messages),
                "session_duration": session_duration,
                "new_vocabulary": insights.vocabulary_new,
            }

        # Fallback for basic interaction without full exchange
        return {
            "vocabulary_used": context.vocabulary_introduced,
            "learning_progress": "basic_interaction",
            "message_count": len(messages),
        }

    async def update_conversation_context(
        self, context: ConversationContext, insights: LearningInsight
    ) -> ConversationContext:
        """
        Update conversation context with new learning insights.

        Updates the conversation context by incorporating newly discovered vocabulary
        and updating the last activity timestamp. This ensures the context reflects
        the current state of the learning session.

        Args:
            context: Current conversation context to update
            insights: Learning insights generated from recent exchange

        Returns:
            Updated conversation context with new vocabulary and timestamp

        Note:
            - Vocabulary list is kept unique (no duplicates)
            - Vocabulary list is limited to last 50 words for performance
            - Last activity timestamp is updated to current time
        """
        # Add new vocabulary to the context
        context.vocabulary_introduced.extend(insights.vocabulary_new)

        # Keep vocabulary list unique and limit to 50 most recent words
        context.vocabulary_introduced = list(set(context.vocabulary_introduced or []))[
            -50:
        ]

        # Update last activity timestamp
        context.last_activity = datetime.now()

        self.logger.debug(
            f"Updated context for conversation {context.conversation_id}: "
            f"{len(insights.vocabulary_new)} new words added, "
            f"total vocabulary: {len(context.vocabulary_introduced)}"
        )

        return context


# Global analyzer instance for easy access
learning_analyzer = LearningAnalyzer()
