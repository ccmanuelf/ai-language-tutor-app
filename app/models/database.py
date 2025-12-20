"""
Database Models for AI Language Tutor App

This module defines SQLAlchemy models for the SQLite database.
Includes user management, conversations, documents, learning progress, and more.
"""

from enum import Enum as PyEnum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.sql import func

Base = declarative_base()


# Enums for better type safety
class UserRole(PyEnum):
    """User roles in the system"""

    PARENT = "PARENT"
    CHILD = "CHILD"
    ADMIN = "ADMIN"


class LanguageCode(PyEnum):
    """Supported languages

    Note: This enum is maintained for backwards compatibility.
    New languages can be added to the database via init_sample_data.py
    without requiring code changes to this enum.
    """

    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"


class ConversationRole(PyEnum):
    """Role in conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DocumentType(PyEnum):
    """Types of uploaded documents"""

    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    URL = "url"
    YOUTUBE = "youtube"


class LearningStatus(PyEnum):
    """Learning progress status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"


class SupportLevel(PyEnum):
    """Language support level indicating available features"""

    FULL = "FULL"  # Full TTS + STT support
    STT_ONLY = "STT_ONLY"  # STT works, TTS uses fallback voice
    FUTURE = "FUTURE"  # Planned for future implementation


# Association table for user languages (many-to-many)
user_languages = Table(
    "user_languages",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("language_id", Integer, ForeignKey("languages.id"), primary_key=True),
    Column("proficiency_level", Integer, default=1),  # 1-10 scale
    Column("is_primary", Boolean, default=False),
    Column("created_at", DateTime, default=func.now()),
)


class User(Base):
    """User model for storing user profiles and authentication"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for demo/development
    role = Column(Enum(UserRole), default=UserRole.CHILD, nullable=False)

    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Preferences and settings
    preferences = Column(JSON, default=dict)
    ui_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")

    # Privacy and parental controls
    privacy_settings = Column(JSON, default=dict)
    parental_controls = Column(JSON, default=dict)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # languages = relationship("Language", secondary=user_languages, back_populates="users")  # Temporarily disabled
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    # documents = relationship(
    #     "Document", back_populates="user", cascade="all, delete-orphan"
    # )  # Temporarily disabled
    # learning_progress = relationship(
    #     "LearningProgress", back_populates="user", cascade="all, delete-orphan"
    # )  # Temporarily disabled
    # vocabulary_lists = relationship(
    #     "VocabularyItem", back_populates="user", cascade="all, delete-orphan"
    # )  # Temporarily disabled

    # Indexes
    __table_args__ = (
        Index("idx_user_role", "role"),
        Index("idx_user_active", "is_active"),
        Index("idx_user_created", "created_at"),
    )

    @validates("email")
    def validate_email(self, key, email):
        """Basic email validation"""
        if email and "@" not in email:
            raise ValueError("Invalid email format")
        return email

    @validates("user_id")
    def validate_user_id(self, key, user_id):
        """Validate user_id format"""
        if not user_id or len(user_id) < 3:
            raise ValueError("User ID must be at least 3 characters")
        return user_id

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email if include_sensitive else None,
            "role": self.role.value if self.role else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar_url": self.avatar_url,
            "preferences": self.preferences or {},
            "ui_language": self.ui_language,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

    def get_ai_provider_settings(self) -> dict:
        """
        Get user's AI provider settings with defaults

        Returns:
            Dictionary with AI provider settings
        """
        # Default AI provider settings
        default_settings = {
            "provider_selection_mode": "balanced",
            "default_provider": "claude",
            "enforce_budget_limits": True,
            "budget_override_allowed": True,
            "alert_on_budget_threshold": 0.80,
            "notify_on_provider_change": True,
            "notify_on_budget_alert": True,
            "auto_fallback_to_ollama": False,
            "prefer_local_when_available": False,
        }

        # Get current preferences
        preferences = self.preferences or {}

        # Merge with defaults (user settings override defaults)
        ai_settings = preferences.get("ai_provider_settings", {})
        return {**default_settings, **ai_settings}

    def set_ai_provider_settings(self, settings: dict) -> None:
        """
        Update user's AI provider settings

        Args:
            settings: Dictionary with AI provider settings to update
        """
        # Ensure preferences is a dictionary
        if self.preferences is None:
            self.preferences = {}

        # Get current AI settings or create new
        current_ai_settings = self.preferences.get("ai_provider_settings", {})

        # Merge new settings with existing
        current_ai_settings.update(settings)

        # Update preferences
        self.preferences["ai_provider_settings"] = current_ai_settings


class Language(Base):
    """Language model for supported languages"""

    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)  # ISO language code
    name = Column(String(100), nullable=False)
    native_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

    # Language-specific settings
    has_speech_support = Column(Boolean, default=False)
    has_tts_support = Column(Boolean, default=False)
    support_level = Column(
        Enum(SupportLevel), default=SupportLevel.FULL, nullable=False
    )
    speech_api_config = Column(JSON, default=dict)

    # Relationships
    # users = relationship("User", secondary=user_languages, back_populates="languages")  # Temporarily disabled

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "native_name": self.native_name,
            "is_active": self.is_active,
            "has_speech_support": self.has_speech_support,
            "has_tts_support": self.has_tts_support,
            "support_level": self.support_level.value if self.support_level else "FULL",
            "speech_api_config": self.speech_api_config or {},
        }


class Conversation(Base):
    """Conversation model for storing chat history"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Conversation metadata
    title = Column(String(255), nullable=True)
    language = Column(String(10), nullable=False)
    ai_model = Column(String(50), nullable=True)  # claude, deepseek, mistral, etc.

    # Conversation content and context
    context_data = Column(JSON, default=dict)  # Context, documents, etc.

    # Status and metrics
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)

    # Timestamps
    started_at = Column(DateTime, default=func.now(), nullable=False)
    last_message_at = Column(DateTime, default=func.now(), nullable=False)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_conversation_user_language", "user_id", "language"),
        Index("idx_conversation_active", "is_active"),
        Index("idx_conversation_started", "started_at"),
    )

    def to_dict(self, include_messages=False):
        data = {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "title": self.title,
            "language": self.language,
            "ai_model": self.ai_model,
            "context_data": self.context_data or {},
            "is_active": self.is_active,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_message_at": self.last_message_at.isoformat()
            if self.last_message_at
            else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }

        if include_messages:
            data["messages"] = [msg.to_dict() for msg in self.messages]

        return data


class ConversationMessage(Base):
    """Individual messages within conversations"""

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)

    # Message content
    role = Column(Enum(ConversationRole), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)

    # Message metadata
    token_count = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    processing_time_ms = Column(Integer, default=0)

    # Speech and pronunciation data
    audio_url = Column(String(500), nullable=True)
    pronunciation_score = Column(Float, nullable=True)
    pronunciation_feedback = Column(JSON, default=dict)

    # Message analysis
    sentiment_score = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    vocabulary_level = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index("idx_message_conversation_role", "conversation_id", "role"),
        Index("idx_message_created", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role.value if self.role else None,
            "content": self.content,
            "language": self.language,
            "token_count": self.token_count,
            "estimated_cost": self.estimated_cost,
            "processing_time_ms": self.processing_time_ms,
            "audio_url": self.audio_url,
            "pronunciation_score": self.pronunciation_score,
            "pronunciation_feedback": self.pronunciation_feedback or {},
            "sentiment_score": self.sentiment_score,
            "complexity_score": self.complexity_score,
            "vocabulary_level": self.vocabulary_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Document(Base):
    """Document model for uploaded files and content"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Document metadata
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    language = Column(String(10), nullable=True)
    file_size = Column(Integer, nullable=True)

    # Content and processing
    content = Column(Text, nullable=True)
    processed_content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    # File storage
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)

    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    processing_metadata = Column(JSON, default=dict)

    # Content analysis
    word_count = Column(Integer, default=0)
    complexity_score = Column(Float, nullable=True)
    reading_time_minutes = Column(Integer, default=0)
    key_topics = Column(JSON, default=list)
    vocabulary_extracted = Column(JSON, default=list)

    # Timestamps
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    # user = relationship("User", back_populates="documents")  # Temporarily disabled to match User model
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_document_user_type", "user_id", "document_type"),
        Index("idx_document_processed", "is_processed"),
        Index("idx_document_uploaded", "uploaded_at"),
    )

    def to_dict(self, include_content=False):
        data = {
            "id": self.id,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "document_type": self.document_type.value if self.document_type else None,
            "language": self.language,
            "file_size": self.file_size,
            "summary": self.summary,
            "file_url": self.file_url,
            "is_processed": self.is_processed,
            "processing_status": self.processing_status,
            "processing_metadata": self.processing_metadata or {},
            "word_count": self.word_count,
            "complexity_score": self.complexity_score,
            "reading_time_minutes": self.reading_time_minutes,
            "key_topics": self.key_topics or [],
            "vocabulary_extracted": self.vocabulary_extracted or [],
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
        }

        if include_content:
            data["content"] = self.content
            data["processed_content"] = self.processed_content

        return data


class LearningProgress(Base):
    """Learning progress tracking for users"""

    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language = Column(String(10), nullable=False)

    # Progress metrics
    skill_type = Column(
        String(50), nullable=False
    )  # vocabulary, pronunciation, conversation
    current_level = Column(Integer, default=1)
    target_level = Column(Integer, default=10)
    progress_percentage = Column(Float, default=0.0)

    # Learning data
    total_study_time_minutes = Column(Integer, default=0)
    sessions_completed = Column(Integer, default=0)
    words_learned = Column(Integer, default=0)
    conversations_completed = Column(Integer, default=0)

    # Performance metrics
    average_accuracy = Column(Float, default=0.0)
    improvement_rate = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)

    # Status and goals
    status = Column(Enum(LearningStatus), default=LearningStatus.NOT_STARTED)
    goals = Column(JSON, default=dict)
    achievements = Column(JSON, default=list)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship(
        "User"
    )  # Removed back_populates due to commented User relationship

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id", "language", "skill_type", name="uq_user_language_skill"
        ),
        Index("idx_progress_user_language", "user_id", "language"),
        Index("idx_progress_status", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "language": self.language,
            "skill_type": self.skill_type,
            "current_level": self.current_level,
            "target_level": self.target_level,
            "progress_percentage": self.progress_percentage,
            "total_study_time_minutes": self.total_study_time_minutes,
            "sessions_completed": self.sessions_completed,
            "words_learned": self.words_learned,
            "conversations_completed": self.conversations_completed,
            "average_accuracy": self.average_accuracy,
            "improvement_rate": self.improvement_rate,
            "consistency_score": self.consistency_score,
            "status": self.status.value if self.status else None,
            "goals": self.goals or {},
            "achievements": self.achievements or [],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_activity": self.last_activity.isoformat()
            if self.last_activity
            else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VocabularyItem(Base):
    """Vocabulary words and phrases for learning"""

    __tablename__ = "vocabulary_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language = Column(String(10), nullable=False)

    # Word/phrase data
    word = Column(String(255), nullable=False)
    translation = Column(String(255), nullable=True)
    definition = Column(Text, nullable=True)
    pronunciation = Column(String(255), nullable=True)
    phonetic_transcription = Column(String(255), nullable=True)

    # Learning metadata
    difficulty_level = Column(Integer, default=1)  # 1-10 scale
    frequency_score = Column(Float, default=0.0)
    importance_score = Column(Float, default=0.0)

    # Learning progress
    times_studied = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)
    mastery_level = Column(Float, default=0.0)  # 0-1 scale

    # Context and usage
    example_sentences = Column(JSON, default=list)
    context_tags = Column(JSON, default=list)
    source_type = Column(
        String(50), nullable=True
    )  # 'scenario', 'document', 'manual', 'conversation'
    source_document_id = Column(
        String(100), nullable=True
    )  # Where it was learned (scenario_id, content_id, etc.)

    # Spaced repetition
    next_review_date = Column(DateTime, nullable=True)
    repetition_interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)

    # Timestamps
    first_learned = Column(DateTime, default=func.now())
    last_reviewed = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship(
        "User"
    )  # Removed back_populates due to commented User relationship

    # Indexes
    __table_args__ = (
        Index("idx_vocab_user_language", "user_id", "language"),
        Index("idx_vocab_review_date", "next_review_date"),
        Index("idx_vocab_mastery", "mastery_level"),
        UniqueConstraint("user_id", "language", "word", name="uq_user_language_word"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "language": self.language,
            "word": self.word,
            "translation": self.translation,
            "definition": self.definition,
            "pronunciation": self.pronunciation,
            "phonetic_transcription": self.phonetic_transcription,
            "difficulty_level": self.difficulty_level,
            "frequency_score": self.frequency_score,
            "importance_score": self.importance_score,
            "times_studied": self.times_studied,
            "times_correct": self.times_correct,
            "times_incorrect": self.times_incorrect,
            "mastery_level": self.mastery_level,
            "example_sentences": self.example_sentences or [],
            "context_tags": self.context_tags or [],
            "source_type": self.source_type,
            "source_document_id": self.source_document_id,
            "next_review_date": self.next_review_date.isoformat()
            if self.next_review_date
            else None,
            "repetition_interval_days": self.repetition_interval_days,
            "ease_factor": self.ease_factor,
            "first_learned": self.first_learned.isoformat()
            if self.first_learned
            else None,
            "last_reviewed": self.last_reviewed.isoformat()
            if self.last_reviewed
            else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ScenarioProgressHistory(Base):
    """Historical record of completed scenarios for progress tracking and analytics"""

    __tablename__ = "scenario_progress_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Scenario identification
    scenario_id = Column(String(100), nullable=False)
    progress_id = Column(String(100), nullable=False)  # Unique progress session ID

    # Timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    # Progress metrics
    phases_completed = Column(Integer, nullable=False)
    total_phases = Column(Integer, nullable=False)

    # Learning data (JSON for flexibility)
    vocabulary_mastered = Column(JSON, default=list)  # List of mastered vocabulary
    objectives_completed = Column(JSON, default=list)  # List of completed objectives

    # Performance metrics
    success_rate = Column(Float, default=0.0)  # 0-1 scale
    completion_score = Column(Float, default=0.0)  # 0-100 scale

    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_scenario_history_user", "user_id"),
        Index("idx_scenario_history_scenario", "scenario_id"),
        Index("idx_scenario_history_completed", "completed_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scenario_id": self.scenario_id,
            "progress_id": self.progress_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "duration_minutes": self.duration_minutes,
            "phases_completed": self.phases_completed,
            "total_phases": self.total_phases,
            "vocabulary_mastered": self.vocabulary_mastered or [],
            "objectives_completed": self.objectives_completed or [],
            "success_rate": self.success_rate,
            "completion_score": self.completion_score,
        }


class LearningSession(Base):
    """Track individual learning sessions for all activities (scenarios, content study, reviews)"""

    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session type and source
    session_type = Column(
        String(50), nullable=False
    )  # 'scenario', 'content_study', 'vocabulary_review', 'conversation'
    source_id = Column(String(100), nullable=True)  # scenario_id, content_id, etc.
    language = Column(String(10), nullable=False)

    # Timing
    started_at = Column(DateTime, default=func.now(), nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)

    # Metrics
    items_studied = Column(Integer, default=0)  # Words, phrases, questions, etc.
    items_correct = Column(Integer, default=0)
    items_incorrect = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)  # 0-1 scale

    # Session metadata (JSON for flexibility)
    session_metadata = Column(JSON, default=dict)

    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_learning_session_user", "user_id"),
        Index("idx_learning_session_type", "session_type"),
        Index("idx_learning_session_date", "started_at"),
        Index("idx_learning_session_source", "source_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_type": self.session_type,
            "source_id": self.source_id,
            "language": self.language,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "items_studied": self.items_studied,
            "items_correct": self.items_correct,
            "items_incorrect": self.items_incorrect,
            "accuracy_rate": self.accuracy_rate,
            "session_metadata": self.session_metadata or {},
        }


class APIUsage(Base):
    """Track API usage for cost monitoring"""

    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # API details
    api_provider = Column(
        String(50), nullable=False
    )  # claude, mistral, deepseek, ollama, etc.
    api_endpoint = Column(String(100), nullable=False)
    request_type = Column(String(50), nullable=False)  # chat, speech, embedding, etc.

    # Usage metrics
    tokens_used = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, nullable=True)

    # Request metadata
    request_metadata = Column(JSON, default=dict)
    response_metadata = Column(JSON, default=dict)

    # Status
    status = Column(String(20), default="success")  # success, error, timeout
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_api_usage_provider", "api_provider"),
        Index("idx_api_usage_date", "created_at"),
        Index("idx_api_usage_user", "user_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "api_provider": self.api_provider,
            "api_endpoint": self.api_endpoint,
            "request_type": self.request_type,
            "tokens_used": self.tokens_used,
            "estimated_cost": self.estimated_cost,
            "actual_cost": self.actual_cost,
            "request_metadata": self.request_metadata or {},
            "response_metadata": self.response_metadata or {},
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ProcessedContent(Base):
    """Processed content storage for YouTube videos, documents, etc."""

    __tablename__ = "processed_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Content metadata
    title = Column(String(500), nullable=False)
    content_type = Column(
        String(50), nullable=False
    )  # youtube_video, pdf_document, etc.
    source_url = Column(String(1000), nullable=True)
    language = Column(String(10), nullable=False)

    # Content data
    raw_content = Column(Text, nullable=False)  # Original extracted content
    processed_content = Column(Text, nullable=False)  # Cleaned/processed content

    # Metadata fields
    duration = Column(Float, nullable=True)  # In minutes
    word_count = Column(Integer, default=0)
    difficulty_level = Column(
        String(20), nullable=True
    )  # beginner, intermediate, advanced
    topics = Column(JSON, default=list)  # List of topics/tags
    author = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)

    # Processing stats
    processing_stats = Column(JSON, default=dict)  # Processing metadata and stats

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    learning_materials = relationship(
        "LearningMaterialDB",
        back_populates="parent_content",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_processed_content_user", "user_id"),
        Index("idx_processed_content_type", "content_type"),
        Index("idx_processed_content_language", "language"),
        Index("idx_processed_content_created", "created_at"),
    )

    def to_dict(self, include_content=False):
        data = {
            "id": self.id,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "title": self.title,
            "content_type": self.content_type,
            "source_url": self.source_url,
            "language": self.language,
            "duration": self.duration,
            "word_count": self.word_count,
            "difficulty_level": self.difficulty_level,
            "topics": self.topics or [],
            "author": self.author,
            "file_size": self.file_size,
            "processing_stats": self.processing_stats or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_content:
            data["raw_content"] = self.raw_content
            data["processed_content"] = self.processed_content

        return data


class LearningMaterialDB(Base):
    """Learning materials generated from processed content"""

    __tablename__ = "learning_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String(100), unique=True, nullable=False, index=True)
    content_id = Column(
        String(100), ForeignKey("processed_content.content_id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Material metadata
    material_type = Column(
        String(50), nullable=False
    )  # summary, flashcards, quiz, etc.
    title = Column(String(500), nullable=False)
    difficulty_level = Column(String(20), nullable=True)
    estimated_time = Column(Integer, default=0)  # In minutes
    tags = Column(JSON, default=list)

    # Material content (structured JSON based on type)
    content = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    parent_content = relationship(
        "ProcessedContent", back_populates="learning_materials"
    )

    # Indexes
    __table_args__ = (
        Index("idx_learning_materials_user", "user_id"),
        Index("idx_learning_materials_content", "content_id"),
        Index("idx_learning_materials_type", "material_type"),
        Index("idx_learning_materials_created", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "material_id": self.material_id,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "material_type": self.material_type,
            "title": self.title,
            "difficulty_level": self.difficulty_level,
            "estimated_time": self.estimated_time,
            "tags": self.tags or [],
            "content": self.content or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ContentCollection(Base):
    """Content collections for organizing related content"""

    __tablename__ = "content_collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collection_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(20), nullable=True)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    items = relationship(
        "ContentCollectionItem",
        back_populates="collection",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_collections_user", "user_id"),
        Index("idx_collections_id", "collection_id"),
    )

    def to_dict(self, include_items=False):
        data = {
            "id": self.id,
            "collection_id": self.collection_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_items and self.items:
            data["items"] = [item.to_dict() for item in self.items]
            data["item_count"] = len(self.items)
        else:
            data["item_count"] = len(self.items) if self.items else 0

        return data


class ContentCollectionItem(Base):
    """Items in content collections"""

    __tablename__ = "content_collection_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(
        String(100), ForeignKey("content_collections.collection_id"), nullable=False
    )
    content_id = Column(
        String(100), ForeignKey("processed_content.content_id"), nullable=False
    )
    added_at = Column(DateTime, default=func.now(), nullable=False)
    position = Column(Integer, default=0)

    # Relationships
    collection = relationship("ContentCollection", back_populates="items")
    content = relationship("ProcessedContent")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_collection_items_collection", "collection_id"),
        Index("idx_collection_items_content", "content_id"),
        UniqueConstraint("collection_id", "content_id", name="uq_collection_content"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "content_id": self.content_id,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "position": self.position,
        }


class ContentTag(Base):
    """Tags for content organization and discovery"""

    __tablename__ = "content_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(
        String(100), ForeignKey("processed_content.content_id"), nullable=False
    )
    tag = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    content = relationship("ProcessedContent")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_tags_user", "user_id"),
        Index("idx_tags_content", "content_id"),
        Index("idx_tags_tag", "tag"),
        UniqueConstraint("user_id", "content_id", "tag", name="uq_user_content_tag"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "tag": self.tag,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ContentFavorite(Base):
    """User's favorite content"""

    __tablename__ = "content_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(
        String(100), ForeignKey("processed_content.content_id"), nullable=False
    )
    favorited_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    content = relationship("ProcessedContent")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_favorites_user", "user_id"),
        Index("idx_favorites_content", "content_id"),
        UniqueConstraint("user_id", "content_id", name="uq_user_content_favorite"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "favorited_at": self.favorited_at.isoformat()
            if self.favorited_at
            else None,
        }


class ContentStudySession(Base):
    """Study sessions for tracking content usage"""

    __tablename__ = "content_study_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(
        String(100), ForeignKey("processed_content.content_id"), nullable=False
    )
    started_at = Column(DateTime, default=func.now(), nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    materials_studied = Column(JSON, default=dict)
    items_correct = Column(Integer, default=0)
    items_total = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)

    # Relationships
    user = relationship("User")
    content = relationship("ProcessedContent")

    # Indexes
    __table_args__ = (
        Index("idx_study_sessions_user", "user_id"),
        Index("idx_study_sessions_content", "content_id"),
        Index("idx_study_sessions_date", "started_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "materials_studied": self.materials_studied or {},
            "items_correct": self.items_correct,
            "items_total": self.items_total,
            "completion_percentage": self.completion_percentage,
        }


class ContentMasteryStatus(Base):
    """Mastery status for content items"""

    __tablename__ = "content_mastery_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(
        String(100), ForeignKey("processed_content.content_id"), nullable=False
    )
    mastery_level = Column(String(20), default="not_started")
    total_study_time_seconds = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    last_studied_at = Column(DateTime, nullable=True)
    items_mastered = Column(Integer, default=0)
    items_total = Column(Integer, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    content = relationship("ProcessedContent")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_mastery_user", "user_id"),
        Index("idx_mastery_content", "content_id"),
        Index("idx_mastery_level", "mastery_level"),
        UniqueConstraint("user_id", "content_id", name="uq_user_content_mastery"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "mastery_level": self.mastery_level,
            "total_study_time_seconds": self.total_study_time_seconds,
            "total_sessions": self.total_sessions,
            "last_studied_at": self.last_studied_at.isoformat()
            if self.last_studied_at
            else None,
            "items_mastered": self.items_mastered,
            "items_total": self.items_total,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Database session management
def get_db_session():
    """
    Get database session for dependency injection

    This function provides a database session that can be used
    with FastAPI's Depends() for automatic session management
    and cleanup.
    """
    from app.database.config import db_manager

    session = None  # Initialize to avoid UnboundLocalError in exception handlers
    try:
        # Use SQLite session from db_manager
        session = db_manager.get_sqlite_session()
        yield session
    except Exception as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


# Export all models for easy importing
__all__ = [
    "Base",
    "User",
    "Language",
    "Conversation",
    "ConversationMessage",
    "Document",
    "LearningProgress",
    "VocabularyItem",
    "ScenarioProgressHistory",
    "LearningSession",
    "APIUsage",
    "ProcessedContent",
    "LearningMaterialDB",
    "ContentCollection",
    "ContentCollectionItem",
    "ContentTag",
    "ContentFavorite",
    "ContentStudySession",
    "ContentMasteryStatus",
    "UserRole",
    "LanguageCode",
    "ConversationRole",
    "DocumentType",
    "LearningStatus",
    "SupportLevel",
    "user_languages",
    "get_db_session",
]
