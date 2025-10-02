"""
Conversation Data Models and Enums for AI Language Tutor App

This module contains the core data structures used for conversation management,
including enums for conversation states and message roles, and dataclasses for
conversation context, messages, and learning insights.

These models are designed to be standalone with minimal dependencies, making them
easy to import and use across the application.

Features:
- Conversation status and message role enumerations
- Learning focus area definitions
- Conversation context management structures
- Message and learning insight data models
- Type-safe data structures with comprehensive validation
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class ConversationStatus(Enum):
    """
    Enumeration of possible conversation states.

    Attributes:
        ACTIVE: Conversation is currently active and accepting messages
        PAUSED: Conversation is temporarily paused but can be resumed
        COMPLETED: Conversation has been completed successfully
        ARCHIVED: Conversation has been archived for historical reference
    """

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(Enum):
    """
    Enumeration of message roles in a conversation.

    Attributes:
        USER: Message sent by the user/student
        ASSISTANT: Message sent by the AI assistant/tutor
        SYSTEM: System-generated message for context or instructions
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class LearningFocus(Enum):
    """
    Enumeration of learning focus areas for language learning sessions.

    Attributes:
        CONVERSATION: Focus on natural conversation and communication skills
        GRAMMAR: Focus on grammar rules, structure, and accuracy
        VOCABULARY: Focus on building and reinforcing vocabulary
        PRONUNCIATION: Focus on pronunciation, intonation, and phonetics
        READING: Focus on reading comprehension and text analysis
        WRITING: Focus on writing skills, composition, and structure
    """

    CONVERSATION = "conversation"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    READING = "reading"
    WRITING = "writing"


@dataclass
class ConversationContext:
    """
    Comprehensive context information for a conversation session.

    This dataclass maintains all the state and metadata for an active learning
    conversation, including user preferences, learning goals, progress tracking,
    and scenario-based learning support.

    Attributes:
        conversation_id: Unique identifier for the conversation
        user_id: Identifier of the user participating in the conversation
        language: Target language being learned (e.g., 'en', 'es', 'fr')
        learning_focus: Primary learning focus area for this session
        current_topic: Optional current conversation topic
        vocabulary_level: Student's vocabulary level (e.g., 'beginner', 'intermediate', 'advanced')
        learning_goals: List of specific learning objectives for the session
        mistakes_tracked: List of mistakes made during the conversation with corrections
        vocabulary_introduced: List of new vocabulary words introduced in the session
        session_start_time: Timestamp when the conversation session started
        last_activity: Timestamp of the most recent activity in the conversation
        is_scenario_based: Flag indicating if this is a scenario-based learning session
        scenario_id: Optional identifier of the scenario being practiced
        scenario_progress_id: Optional identifier for tracking scenario progress
        scenario_phase: Optional current phase within the scenario
    """

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
    # Scenario-based learning support
    is_scenario_based: bool = False
    scenario_id: Optional[str] = None
    scenario_progress_id: Optional[str] = None
    scenario_phase: Optional[str] = None

    def __post_init__(self):
        """
        Initialize default values for mutable fields and timestamps.

        This ensures that lists are properly initialized as empty lists rather
        than None, and timestamps are set to the current time if not provided.
        """
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
    """
    Individual message in a conversation.

    Represents a single message exchange in the conversation, including metadata
    about the message such as role, timestamp, and language.

    Attributes:
        role: The role of the message sender (USER, ASSISTANT, or SYSTEM)
        content: The actual text content of the message
        timestamp: When the message was created
        language: The language of the message content
        metadata: Optional dictionary for additional message-specific data
                 (e.g., AI model info, processing metrics, error details)
    """

    role: MessageRole
    content: str
    timestamp: datetime
    language: str
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """
        Initialize metadata as an empty dictionary if not provided.

        Ensures that metadata is always a dictionary, making it safe to
        access and update without null checks.
        """
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LearningInsight:
    """
    Learning insights and analytics from a conversation exchange.

    This dataclass captures various learning metrics and feedback generated
    from analyzing the conversation between the student and AI tutor.

    Attributes:
        vocabulary_new: List of new vocabulary words introduced in this exchange
        vocabulary_practiced: List of vocabulary words the student successfully used
        grammar_corrections: List of grammar corrections made, each containing
                           original text and corrected version
        pronunciation_feedback: List of pronunciation feedback items with
                               details about pronunciation issues and tips
        conversation_quality_score: Overall quality score for the conversation (0.0-1.0)
        engagement_level: Student's engagement level (e.g., 'low', 'medium', 'high')
        suggested_focus: Suggested focus area for continued learning
    """

    vocabulary_new: List[str]
    vocabulary_practiced: List[str]
    grammar_corrections: List[Dict[str, str]]
    pronunciation_feedback: List[Dict[str, Any]]
    conversation_quality_score: float
    engagement_level: str
    suggested_focus: str
