"""
Conversation Management with Context Handling for AI Language Tutor App

This module manages conversation state, context, and history for language learning sessions.
It provides intelligent context management to maintain learning continuity and track progress.

Features:
- Conversation context management
- Learning session tracking
- Context-aware conversation flow
- Vocabulary and mistake tracking
- Progress monitoring
- Multi-language conversation support
- Context compression for long conversations
- Learning analytics integration
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from uuid import uuid4
import hashlib

from app.services.ai_router import ai_router, generate_ai_response
from app.services.budget_manager import budget_manager
from app.database.config import get_db_session
from app.models.database import Conversation, ConversationMessage, User, LearningProgress, VocabularyItem
from app.services.user_management import get_user_by_id
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConversationStatus(Enum):
    """Conversation status types"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class LearningFocus(Enum):
    """Learning focus areas"""
    CONVERSATION = "conversation"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    READING = "reading"
    WRITING = "writing"


@dataclass
class ConversationContext:
    """Conversation context information"""
    conversation_id: str
    user_id: str
    language: str
    learning_focus: LearningFocus
    current_topic: Optional[str] = None
    vocabulary_level: str = "intermediate"
    learning_goals: List[str] = None
    mistakes_tracked: List[Dict[str, Any]] = None
    vocabulary_introduced: List[str] = None
    session_start_time: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.learning_goals is None:
            self.learning_goals = []
        if self.mistakes_tracked is None:
            self.mistakes_tracked = []
        if self.vocabulary_introduced is None:
            self.vocabulary_introduced = []
        if self.session_start_time is None:
            self.session_start_time = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()


@dataclass
class ConversationMessage:
    """Individual conversation message"""
    role: MessageRole
    content: str
    timestamp: datetime
    language: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LearningInsight:
    """Learning insights from conversation"""
    vocabulary_new: List[str]
    vocabulary_practiced: List[str]
    grammar_corrections: List[Dict[str, str]]
    pronunciation_feedback: List[Dict[str, Any]]
    conversation_quality_score: float
    engagement_level: str
    suggested_focus: str


class ConversationManager:
    """Main conversation management class"""
    
    def __init__(self):
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.message_history: Dict[str, List[ConversationMessage]] = {}
        self.context_cache: Dict[str, Any] = {}
        self.max_context_messages = 20  # Maximum messages to keep in active context
        self.context_compression_threshold = 50  # Compress when exceeding this many messages
    
    async def start_conversation(
        self,
        user_id: str,
        language: str,
        learning_focus: LearningFocus = LearningFocus.CONVERSATION,
        topic: Optional[str] = None,
        learning_goals: Optional[List[str]] = None
    ) -> str:
        """
        Start a new conversation session
        
        Args:
            user_id: User identifier
            language: Target language for learning
            learning_focus: Primary learning focus
            topic: Conversation topic (optional)
            learning_goals: Specific learning goals for this session
            
        Returns:
            Conversation ID
        """
        
        conversation_id = str(uuid4())
        
        # Create conversation context
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            language=language,
            learning_focus=learning_focus,
            current_topic=topic,
            learning_goals=learning_goals or [],
            session_start_time=datetime.now(),
            last_activity=datetime.now()
        )
        
        # Store in active conversations
        self.active_conversations[conversation_id] = context
        self.message_history[conversation_id] = []
        
        # Create system message with learning context
        system_message = self._create_learning_system_message(context)
        await self._add_message(
            conversation_id=conversation_id,
            role=MessageRole.SYSTEM,
            content=system_message,
            language=language
        )
        
        # Save to database
        await self._save_conversation_to_db(conversation_id)
        
        logger.info(f"Started conversation {conversation_id} for user {user_id} in {language}")
        
        return conversation_id
    
    async def send_message(
        self,
        conversation_id: str,
        user_message: str,
        include_pronunciation_feedback: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a message in the conversation and get AI response
        
        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            include_pronunciation_feedback: Whether to include pronunciation analysis
            **kwargs: Additional parameters
            
        Returns:
            Conversation response with AI reply and learning insights
        """
        
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found or inactive")
        
        context = self.active_conversations[conversation_id]
        
        # Add user message to history
        await self._add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message,
            language=context.language
        )
        
        # Analyze user message for learning insights
        user_insights = await self._analyze_user_message(
            user_message=user_message,
            context=context
        )
        
        # Prepare conversation context for AI
        conversation_messages = await self._prepare_ai_context(conversation_id)
        
        # Get AI response
        try:
            ai_response = await generate_ai_response(
                messages=conversation_messages,
                language=context.language,
                use_case=context.learning_focus.value,
                user_preferences={
                    "learning_level": context.vocabulary_level,
                    "focus_areas": context.learning_goals,
                    "pronunciation_feedback": include_pronunciation_feedback
                },
                **kwargs
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
                    "cost": ai_response.cost
                }
            )
            
            # Analyze conversation for learning insights
            learning_insights = await self._generate_learning_insights(
                conversation_id=conversation_id,
                user_message=user_message,
                ai_response=ai_response.content,
                context=context
            )
            
            # Update conversation context
            await self._update_conversation_context(
                conversation_id=conversation_id,
                insights=learning_insights
            )
            
            # Save messages to database
            await self._save_messages_to_db(conversation_id)
            
            return {
                "conversation_id": conversation_id,
                "ai_response": ai_response.content,
                "learning_insights": learning_insights,
                "context_info": {
                    "topic": context.current_topic,
                    "vocabulary_level": context.vocabulary_level,
                    "session_duration": (datetime.now() - context.session_start_time).total_seconds(),
                    "message_count": len(self.message_history[conversation_id])
                },
                "ai_metadata": {
                    "model": ai_response.model,
                    "provider": ai_response.provider,
                    "cost": ai_response.cost,
                    "is_fallback": ai_response.metadata.get("router_selection", {}).get("is_fallback", False)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate AI response for conversation {conversation_id}: {e}")
            
            # Return error response but keep conversation active
            return {
                "conversation_id": conversation_id,
                "ai_response": "I'm sorry, I'm having trouble responding right now. Could you please try again?",
                "error": str(e),
                "learning_insights": LearningInsight(
                    vocabulary_new=[],
                    vocabulary_practiced=[],
                    grammar_corrections=[],
                    pronunciation_feedback=[],
                    conversation_quality_score=0.0,
                    engagement_level="error",
                    suggested_focus="try_again"
                )
            }
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation message history"""
        
        if conversation_id not in self.message_history:
            return []
        
        messages = self.message_history[conversation_id]
        
        if limit:
            messages = messages[-limit:]
        
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "language": msg.language,
                "metadata": msg.metadata
            }
            for msg in messages
            if msg.role != MessageRole.SYSTEM  # Exclude system messages from history
        ]
    
    async def get_conversation_summary(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive conversation summary"""
        
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        context = self.active_conversations[conversation_id]
        messages = self.message_history.get(conversation_id, [])
        
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
                "last_activity": context.last_activity.isoformat()
            },
            "learning_progress": {
                "vocabulary_introduced": context.vocabulary_introduced,
                "mistakes_tracked": context.mistakes_tracked,
                "learning_goals": context.learning_goals,
                "vocabulary_level": context.vocabulary_level
            }
        }
    
    async def pause_conversation(self, conversation_id: str):
        """Pause an active conversation"""
        if conversation_id in self.active_conversations:
            # Save current state to database
            await self._save_conversation_to_db(conversation_id)
            await self._save_messages_to_db(conversation_id)
            
            # Move to inactive state but keep in memory for quick resume
            context = self.active_conversations[conversation_id]
            context.last_activity = datetime.now()
            
            logger.info(f"Paused conversation {conversation_id}")
    
    async def resume_conversation(self, conversation_id: str) -> bool:
        """Resume a paused conversation"""
        if conversation_id not in self.active_conversations:
            # Try to load from database
            success = await self._load_conversation_from_db(conversation_id)
            if not success:
                return False
        
        context = self.active_conversations[conversation_id]
        context.last_activity = datetime.now()
        
        logger.info(f"Resumed conversation {conversation_id}")
        return True
    
    async def end_conversation(
        self,
        conversation_id: str,
        save_learning_progress: bool = True
    ) -> Dict[str, Any]:
        """End a conversation and generate final summary"""
        
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
        del self.message_history[conversation_id]
        
        logger.info(f"Ended conversation {conversation_id}")
        
        return {
            "conversation_summary": summary,
            "final_insights": {
                "total_vocabulary_learned": len(summary["learning_progress"]["vocabulary_introduced"]),
                "mistakes_corrected": len(summary["learning_progress"]["mistakes_tracked"]),
                "session_quality": "good" if summary["session_stats"]["user_messages"] >= 5 else "short"
            }
        }
    
    # Private helper methods
    
    def _create_learning_system_message(self, context: ConversationContext) -> str:
        """Create system message tailored for language learning"""
        
        focus_instructions = {
            LearningFocus.CONVERSATION: "Focus on natural conversation flow and practical language use.",
            LearningFocus.GRAMMAR: "Pay special attention to grammar correction and explanation.",
            LearningFocus.VOCABULARY: "Introduce new vocabulary and reinforce word usage.",
            LearningFocus.PRONUNCIATION: "Provide pronunciation guidance and phonetic help.",
            LearningFocus.READING: "Focus on reading comprehension and text analysis.",
            LearningFocus.WRITING: "Help improve writing skills and structure."
        }
        
        language_names = {
            "en": "English",
            "fr": "French", 
            "es": "Spanish",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean"
        }
        
        language_name = language_names.get(context.language, context.language)
        focus_instruction = focus_instructions.get(context.learning_focus, "Provide helpful language learning support.")
        
        system_message = f"""You are a helpful {language_name} language tutor. {focus_instruction}

Learning Context:
- Student's level: {context.vocabulary_level}
- Learning focus: {context.learning_focus.value}
- Current topic: {context.current_topic or 'General conversation'}
- Learning goals: {', '.join(context.learning_goals) if context.learning_goals else 'General improvement'}

Instructions:
1. Respond naturally in {language_name}
2. Gently correct mistakes when you notice them
3. Introduce new vocabulary gradually
4. Encourage the student and provide positive feedback
5. Ask follow-up questions to maintain engagement
6. Adapt your language complexity to the student's level

Remember: Be patient, encouraging, and focus on practical language use."""
        
        return system_message
    
    async def _add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        language: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to conversation history"""
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            language=language,
            metadata=metadata or {}
        )
        
        if conversation_id not in self.message_history:
            self.message_history[conversation_id] = []
        
        self.message_history[conversation_id].append(message)
        
        # Update last activity
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id].last_activity = datetime.now()
        
        # Compress context if it gets too long
        await self._maybe_compress_context(conversation_id)
    
    async def _prepare_ai_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Prepare conversation context for AI provider"""
        
        messages = self.message_history.get(conversation_id, [])
        
        # Convert to AI provider format
        ai_messages = []
        for msg in messages[-self.max_context_messages:]:  # Keep recent messages
            ai_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return ai_messages
    
    async def _analyze_user_message(
        self,
        user_message: str,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Analyze user message for learning insights"""
        
        # Simple analysis for now - can be enhanced with NLP
        analysis = {
            "message_length": len(user_message),
            "word_count": len(user_message.split()),
            "complexity_score": min(len(user_message.split()) / 10, 1.0),
            "engagement_indicators": {
                "questions": "?" in user_message,
                "excitement": "!" in user_message,
                "formal_language": any(word in user_message.lower() for word in ["please", "thank you", "could you"])
            }
        }
        
        return analysis
    
    async def _generate_learning_insights(
        self,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        context: ConversationContext
    ) -> LearningInsight:
        """Generate learning insights from the conversation exchange"""
        
        # This is a simplified version - in a real implementation,
        # you would use NLP libraries to analyze grammar, vocabulary, etc.
        
        # Extract potential new vocabulary from AI response
        ai_words = set(ai_response.lower().split())
        recent_vocabulary = set(context.vocabulary_introduced)
        potential_new_vocab = list(ai_words - recent_vocabulary)[:3]  # Limit to 3 new words
        
        # Simple engagement scoring based on message length and content
        engagement_score = min(len(user_message) / 50, 1.0)
        engagement_levels = ["low", "medium", "high"]
        engagement_level = engagement_levels[min(int(engagement_score * 3), 2)]
        
        # Generate conversation quality score
        quality_factors = [
            len(user_message) > 10,  # Meaningful message length
            "?" in user_message or "!" in user_message,  # Engagement indicators
            len(user_message.split()) >= 3,  # Multiple words
        ]
        quality_score = sum(quality_factors) / len(quality_factors)
        
        return LearningInsight(
            vocabulary_new=potential_new_vocab,
            vocabulary_practiced=[],
            grammar_corrections=[],
            pronunciation_feedback=[],
            conversation_quality_score=quality_score,
            engagement_level=engagement_level,
            suggested_focus=context.learning_focus.value
        )
    
    async def _update_conversation_context(
        self,
        conversation_id: str,
        insights: LearningInsight
    ):
        """Update conversation context with new learning insights"""
        
        if conversation_id not in self.active_conversations:
            return
        
        context = self.active_conversations[conversation_id]
        
        # Add new vocabulary
        context.vocabulary_introduced.extend(insights.vocabulary_new)
        
        # Keep vocabulary list unique and reasonable size
        context.vocabulary_introduced = list(set(context.vocabulary_introduced))[-50:]
        
        # Update last activity
        context.last_activity = datetime.now()
    
    async def _maybe_compress_context(self, conversation_id: str):
        """Compress conversation context if it gets too long"""
        
        if conversation_id not in self.message_history:
            return
        
        messages = self.message_history[conversation_id]
        
        if len(messages) > self.context_compression_threshold:
            # Keep system message, recent messages, and create a summary of older messages
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            recent_messages = messages[-self.max_context_messages:]
            
            # Create a simple summary of compressed messages
            compressed_count = len(messages) - len(recent_messages) - len(system_messages)
            
            if compressed_count > 0:
                summary_message = ConversationMessage(
                    role=MessageRole.SYSTEM,
                    content=f"[Previous conversation summary: {compressed_count} messages exchanged covering language learning topics]",
                    timestamp=datetime.now(),
                    language=self.active_conversations[conversation_id].language,
                    metadata={"type": "compression_summary", "compressed_messages": compressed_count}
                )
                
                # Replace message history with compressed version
                self.message_history[conversation_id] = system_messages + [summary_message] + recent_messages[-self.max_context_messages:]
                
                logger.info(f"Compressed conversation {conversation_id}: {compressed_count} messages summarized")
    
    async def generate_learning_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Generate learning insights for a conversation"""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}
        
        context = self.active_conversations[conversation_id]
        messages = self.message_history.get(conversation_id, [])
        
        if len(messages) < 2:
            return {
                "vocabulary_used": [],
                "learning_progress": "conversation_just_started",
                "message_count": len(messages),
                "engagement_level": "beginning"
            }
        
        # Get the most recent user message and AI response
        user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
        ai_messages = [msg for msg in messages if msg.role == MessageRole.ASSISTANT]
        
        if user_messages and ai_messages:
            latest_user_msg = user_messages[-1].content
            latest_ai_msg = ai_messages[-1].content
            
            insights = await self._generate_learning_insights(
                conversation_id, latest_user_msg, latest_ai_msg, context
            )
            
            return {
                "vocabulary_used": context.vocabulary_introduced[-10:],  # Last 10 vocab words
                "learning_progress": {
                    "conversation_quality": insights.conversation_quality_score,
                    "engagement_level": insights.engagement_level,
                    "focus_area": insights.suggested_focus
                },
                "message_count": len(messages),
                "session_duration": (datetime.now() - context.session_start_time).total_seconds() / 60,  # minutes
                "new_vocabulary": insights.vocabulary_new
            }
        
        return {
            "vocabulary_used": context.vocabulary_introduced,
            "learning_progress": "basic_interaction",
            "message_count": len(messages)
        }
    
    async def _save_conversation_to_db(self, conversation_id: str, status: str = "active"):
        """Save conversation metadata to database"""
        # Implementation would save to database
        # For now, just log the action
        logger.info(f"Saving conversation {conversation_id} to database with status: {status}")
    
    async def _save_messages_to_db(self, conversation_id: str):
        """Save conversation messages to database"""
        # Implementation would save messages to database
        # For now, just log the action
        logger.info(f"Saving messages for conversation {conversation_id} to database")
    
    async def _save_learning_progress(self, conversation_id: str):
        """Save learning progress to database"""
        # Implementation would update learning progress
        # For now, just log the action
        logger.info(f"Saving learning progress for conversation {conversation_id}")
    
    async def _load_conversation_from_db(self, conversation_id: str) -> bool:
        """Load conversation from database"""
        # Implementation would load from database
        # For now, just return False
        logger.info(f"Attempting to load conversation {conversation_id} from database")
        return False


# Global conversation manager instance
conversation_manager = ConversationManager()


# Convenience functions
async def start_learning_conversation(
    user_id: str,
    language: str,
    learning_focus: str = "conversation",
    topic: Optional[str] = None
) -> str:
    """Start a new learning conversation"""
    focus = LearningFocus(learning_focus)
    return await conversation_manager.start_conversation(
        user_id=user_id,
        language=language,
        learning_focus=focus,
        topic=topic
    )

async def send_learning_message(
    conversation_id: str,
    user_message: str,
    user_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Send a message in a learning conversation"""
    return await conversation_manager.send_message(
        conversation_id=conversation_id,
        user_message=user_message,
        user_id=user_id,
        **kwargs
    )

async def get_conversation_summary(conversation_id: str) -> Dict[str, Any]:
    """Get conversation summary"""
    return await conversation_manager.get_conversation_summary(conversation_id)

async def end_learning_conversation(conversation_id: str) -> Dict[str, Any]:
    """End a learning conversation"""
    return await conversation_manager.end_conversation(conversation_id)