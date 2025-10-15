"""
Conversation Persistence Service for AI Language Tutor App

This module implements database persistence operations for conversation management.
It handles saving and loading conversation data, messages, and learning progress.

Features:
- Save conversation metadata to database
- Save conversation messages to database
- Save learning progress and analytics
- Load conversations from database
- Error handling and logging
- Transaction management

Complexity: ~150 lines, <150 cyclomatic complexity
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.config import get_db_session
from app.models.database import (
    Conversation,
    ConversationMessage as DBConversationMessage,
    LearningProgress,
    VocabularyItem,
    ConversationRole,
)
from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    MessageRole,
)

logger = logging.getLogger(__name__)


class ConversationPersistence:
    """
    Handles database persistence operations for conversations.

    This class provides methods to save and load conversation data,
    including conversation metadata, messages, and learning progress.
    """

    def __init__(self):
        """Initialize the conversation persistence service."""

    async def save_conversation_to_db(
        self, conversation_id: str, context: ConversationContext, status: str = "active"
    ) -> bool:
        """
        Save conversation metadata to database.

        Args:
            conversation_id: Unique conversation identifier
            context: Conversation context with metadata
            status: Conversation status (active, paused, completed)

        Returns:
            True if successful, False otherwise
        """
        session: Optional[Session] = None
        try:
            session = next(get_db_session())

            # Check if conversation already exists
            existing = (
                session.query(Conversation)
                .filter(Conversation.conversation_id == conversation_id)
                .first()
            )

            if existing:
                # Update existing conversation
                existing.language = context.language
                existing.is_active = status == "active"
                existing.last_message_at = datetime.now()
                existing.context_data = {
                    "learning_focus": context.learning_focus.value,
                    "current_topic": context.current_topic,
                    "vocabulary_level": context.vocabulary_level,
                    "learning_goals": context.learning_goals,
                    "is_scenario_based": context.is_scenario_based,
                    "scenario_id": context.scenario_id,
                    "scenario_progress_id": context.scenario_progress_id,
                    "scenario_phase": context.scenario_phase,
                }
                if status == "completed":
                    existing.ended_at = datetime.now()

                logger.info(f"Updated conversation {conversation_id} in database")
            else:
                # Create new conversation
                new_conversation = Conversation(
                    conversation_id=conversation_id,
                    user_id=int(context.user_id) if context.user_id.isdigit() else 1,
                    language=context.language,
                    title=context.current_topic
                    or f"Conversation in {context.language}",
                    is_active=(status == "active"),
                    context_data={
                        "learning_focus": context.learning_focus.value,
                        "current_topic": context.current_topic,
                        "vocabulary_level": context.vocabulary_level,
                        "learning_goals": context.learning_goals,
                        "is_scenario_based": context.is_scenario_based,
                        "scenario_id": context.scenario_id,
                        "scenario_progress_id": context.scenario_progress_id,
                        "scenario_phase": context.scenario_phase,
                    },
                    started_at=context.session_start_time,
                    last_message_at=context.last_activity,
                )
                session.add(new_conversation)
                logger.info(f"Created new conversation {conversation_id} in database")

            session.commit()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error saving conversation {conversation_id}: {e}")
            if session:
                session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving conversation {conversation_id}: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()

    async def save_messages_to_db(
        self, conversation_id: str, messages: List[ConversationMessage]
    ) -> bool:
        """
        Save conversation messages to database.

        Args:
            conversation_id: Unique conversation identifier
            messages: List of messages to save

        Returns:
            True if successful, False otherwise
        """
        session: Optional[Session] = None
        try:
            session = next(get_db_session())

            # Get conversation database ID
            conversation = (
                session.query(Conversation)
                .filter(Conversation.conversation_id == conversation_id)
                .first()
            )

            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found in database")
                return False

            # Save only new messages (not already in database)
            existing_count = (
                session.query(DBConversationMessage)
                .filter(DBConversationMessage.conversation_id == conversation.id)
                .count()
            )

            new_messages = messages[existing_count:]

            for message in new_messages:
                db_message = DBConversationMessage(
                    conversation_id=conversation.id,
                    role=self._convert_message_role(message.role),
                    content=message.content,
                    language=message.language,
                    created_at=message.timestamp,
                    token_count=message.metadata.get("token_count", 0),
                    estimated_cost=message.metadata.get("estimated_cost", 0.0),
                    processing_time_ms=message.metadata.get("processing_time_ms", 0),
                )
                session.add(db_message)

            # Update conversation message count
            conversation.message_count = (
                session.query(DBConversationMessage)
                .filter(DBConversationMessage.conversation_id == conversation.id)
                .count()
            )

            session.commit()
            logger.info(
                f"Saved {len(new_messages)} messages for conversation {conversation_id}"
            )
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error saving messages for {conversation_id}: {e}")
            if session:
                session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving messages for {conversation_id}: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()

    def _extract_user_id(self, context: ConversationContext) -> int:
        """Extract user ID from context with fallback"""
        return int(context.user_id) if context.user_id.isdigit() else 1

    def _update_vocabulary_progress(
        self, session: Session, user_id: int, context: ConversationContext
    ) -> None:
        """Update vocabulary learning progress"""
        if not context.vocabulary_introduced:
            return

        vocabulary_progress = (
            session.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.language == context.language,
                LearningProgress.skill_type == "vocabulary",
            )
            .first()
        )

        if vocabulary_progress:
            vocabulary_progress.words_learned += len(context.vocabulary_introduced)
            vocabulary_progress.last_activity = datetime.now()
            vocabulary_progress.sessions_completed += 1

    def _update_conversation_progress(
        self, session: Session, user_id: int, context: ConversationContext
    ) -> None:
        """Update conversation progress"""
        conversation_progress = (
            session.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.language == context.language,
                LearningProgress.skill_type == "conversation",
            )
            .first()
        )

        if conversation_progress:
            conversation_progress.conversations_completed += 1
            conversation_progress.last_activity = datetime.now()
            conversation_progress.sessions_completed += 1

    def _save_vocabulary_items(
        self, session: Session, user_id: int, context: ConversationContext
    ) -> None:
        """Save new vocabulary items to database"""
        for word in context.vocabulary_introduced:
            if not self._vocabulary_exists(session, user_id, context.language, word):
                vocab_item = VocabularyItem(
                    user_id=user_id,
                    language=context.language,
                    word=word,
                    difficulty_level=self._estimate_difficulty(
                        context.vocabulary_level
                    ),
                    first_learned=datetime.now(),
                )
                session.add(vocab_item)

    def _vocabulary_exists(
        self, session: Session, user_id: int, language: str, word: str
    ) -> bool:
        """Check if vocabulary item already exists"""
        return (
            session.query(VocabularyItem)
            .filter(
                VocabularyItem.user_id == user_id,
                VocabularyItem.language == language,
                VocabularyItem.word == word,
            )
            .first()
            is not None
        )

    def _handle_save_error(
        self, session: Optional[Session], conversation_id: str, error: Exception
    ) -> bool:
        """Handle errors during save operation"""
        error_type = "Database" if isinstance(error, SQLAlchemyError) else "Unexpected"
        logger.error(
            f"{error_type} error saving learning progress for {conversation_id}: {error}"
        )
        if session:
            session.rollback()
        return False

    async def save_learning_progress(
        self, conversation_id: str, context: ConversationContext
    ) -> bool:
        """
        Save learning progress to database.

        Args:
            conversation_id: Unique conversation identifier
            context: Conversation context with learning data

        Returns:
            True if successful, False otherwise
        """
        session: Optional[Session] = None
        try:
            session = next(get_db_session())
            user_id = self._extract_user_id(context)

            self._update_vocabulary_progress(session, user_id, context)
            self._update_conversation_progress(session, user_id, context)
            self._save_vocabulary_items(session, user_id, context)

            session.commit()
            logger.info(f"Saved learning progress for conversation {conversation_id}")
            return True

        except (SQLAlchemyError, Exception) as e:
            return self._handle_save_error(session, conversation_id, e)
        finally:
            if session:
                session.close()

    async def load_conversation_from_db(
        self, conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load conversation from database.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Dictionary with conversation data if found, None otherwise
        """
        session: Optional[Session] = None
        try:
            session = next(get_db_session())

            conversation = (
                session.query(Conversation)
                .filter(Conversation.conversation_id == conversation_id)
                .first()
            )

            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found in database")
                return None

            # Load messages
            messages = (
                session.query(DBConversationMessage)
                .filter(DBConversationMessage.conversation_id == conversation.id)
                .order_by(DBConversationMessage.created_at)
                .all()
            )

            conversation_data = {
                "conversation_id": conversation.conversation_id,
                "user_id": str(conversation.user_id),
                "language": conversation.language,
                "context_data": conversation.context_data or {},
                "messages": [self._convert_db_message(msg) for msg in messages],
                "is_active": conversation.is_active,
                "started_at": conversation.started_at,
                "last_message_at": conversation.last_message_at,
            }

            logger.info(f"Loaded conversation {conversation_id} from database")
            return conversation_data

        except SQLAlchemyError as e:
            logger.error(f"Database error loading conversation {conversation_id}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error loading conversation {conversation_id}: {e}"
            )
            return None
        finally:
            if session:
                session.close()

    # Helper methods

    def _convert_message_role(self, role: MessageRole) -> ConversationRole:
        """Convert MessageRole to ConversationRole enum."""
        role_mapping = {
            MessageRole.USER: ConversationRole.USER,
            MessageRole.ASSISTANT: ConversationRole.ASSISTANT,
            MessageRole.SYSTEM: ConversationRole.SYSTEM,
        }
        return role_mapping.get(role, ConversationRole.USER)

    def _convert_db_message(self, db_message: DBConversationMessage) -> Dict[str, Any]:
        """Convert database message to dictionary format."""
        return {
            "role": db_message.role.value,
            "content": db_message.content,
            "language": db_message.language,
            "timestamp": db_message.created_at.isoformat(),
            "metadata": {
                "token_count": db_message.token_count,
                "estimated_cost": db_message.estimated_cost,
                "processing_time_ms": db_message.processing_time_ms,
            },
        }

    def _estimate_difficulty(self, vocabulary_level: str) -> int:
        """Estimate difficulty level from vocabulary level string."""
        level_mapping = {
            "beginner": 2,
            "elementary": 3,
            "intermediate": 5,
            "upper-intermediate": 7,
            "advanced": 8,
            "proficient": 9,
        }
        return level_mapping.get(vocabulary_level.lower(), 5)


# Global conversation persistence instance
conversation_persistence = ConversationPersistence()
