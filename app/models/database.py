"""
Database Models for AI Language Tutor App

This module defines SQLAlchemy models for the SQLite database.
Includes user management, conversations, documents, learning progress, and more.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    Table,
    JSON,
    Enum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
import json


Base = declarative_base()


# Enums for better type safety
class UserRole(PyEnum):
    """User roles in the system"""

    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"


class LanguageCode(PyEnum):
    """Supported languages"""

    CHINESE = "zh"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    ENGLISH = "en"


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
    ai_model = Column(String(50), nullable=True)  # claude, qwen, mistral, etc.

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
    source_document_id = Column(String(100), nullable=True)  # Where it was learned

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


class APIUsage(Base):
    """Track API usage for cost monitoring"""

    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # API details
    api_provider = Column(String(50), nullable=False)  # claude, openai, watson, etc.
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


# Database session management
def get_db_session():
    """
    Get database session for dependency injection

    This function provides a database session that can be used
    with FastAPI's Depends() for automatic session management
    and cleanup.
    """
    from app.database.config import db_manager

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
    "APIUsage",
    "UserRole",
    "LanguageCode",
    "ConversationRole",
    "DocumentType",
    "LearningStatus",
    "user_languages",
    "get_db_session",
]
