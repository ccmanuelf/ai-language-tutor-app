"""
Pydantic Schemas for AI Language Tutor App

This module defines Pydantic models for API request/response validation,
data serialization, and type checking.
"""

from pydantic import (
    BaseModel,
    field_validator,
    Field,
    EmailStr,
    ConfigDict,
)
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums for validation
class UserRoleEnum(str, Enum):
    """User roles"""

    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"


class LanguageEnum(str, Enum):
    """Supported languages"""

    CHINESE = "zh"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    ENGLISH = "en"


class ConversationRoleEnum(str, Enum):
    """Conversation roles"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DocumentTypeEnum(str, Enum):
    """Document types"""

    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    URL = "url"
    YOUTUBE = "youtube"


class LearningStatusEnum(str, Enum):
    """Learning status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# User Schemas
class UserBase(BaseSchema):
    """Base user schema"""

    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: UserRoleEnum = UserRoleEnum.CHILD
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    ui_language: str = Field("en", max_length=10)
    timezone: str = Field("UTC", max_length=50)


class UserCreate(UserBase):
    """Schema for creating a user"""

    user_id: str = Field(..., min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    privacy_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        """Validate user_id format"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "User ID can only contain letters, numbers, hyphens, and underscores"
            )
        return v.lower()


class UserUpdate(BaseSchema):
    """Schema for updating a user"""

    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    ui_language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    preferences: Optional[Dict[str, Any]] = None
    privacy_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user responses"""

    id: int
    user_id: str
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserProfile(UserResponse):
    """Extended user profile with learning data"""

    languages: List[Dict[str, Any]] = Field(default_factory=list)
    learning_progress: List[Dict[str, Any]] = Field(default_factory=list)
    total_conversations: int = 0
    total_study_time_minutes: int = 0


# Language Schemas
class LanguageBase(BaseSchema):
    """Base language schema"""

    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=100)
    native_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    has_speech_support: bool = False
    has_tts_support: bool = False


class LanguageCreate(LanguageBase):
    """Schema for creating a language"""

    speech_api_config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LanguageResponse(LanguageBase):
    """Schema for language responses"""

    id: int
    speech_api_config: Dict[str, Any] = Field(default_factory=dict)


# Conversation Schemas
class ConversationBase(BaseSchema):
    """Base conversation schema"""

    title: Optional[str] = Field(None, max_length=255)
    language: str = Field(..., max_length=10)
    ai_model: Optional[str] = Field(None, max_length=50)


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""

    conversation_id: str = Field(..., max_length=100)
    context_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationUpdate(BaseSchema):
    """Schema for updating a conversation"""

    title: Optional[str] = Field(None, max_length=255)
    context_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation responses"""

    id: int
    conversation_id: str
    user_id: int
    context_data: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    message_count: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    started_at: datetime
    last_message_at: datetime
    ended_at: Optional[datetime] = None


# Message Schemas
class MessageBase(BaseSchema):
    """Base message schema"""

    role: ConversationRoleEnum
    content: str = Field(..., min_length=1)
    language: Optional[str] = Field(None, max_length=10)


class MessageCreate(MessageBase):
    """Schema for creating a message"""

    conversation_id: int
    pronunciation_feedback: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageResponse(MessageBase):
    """Schema for message responses"""

    id: int
    conversation_id: int
    token_count: int = 0
    estimated_cost: float = 0.0
    processing_time_ms: int = 0
    audio_url: Optional[str] = None
    pronunciation_score: Optional[float] = None
    pronunciation_feedback: Dict[str, Any] = Field(default_factory=dict)
    sentiment_score: Optional[float] = None
    complexity_score: Optional[float] = None
    vocabulary_level: Optional[int] = None
    created_at: datetime


# Document Schemas
class DocumentBase(BaseSchema):
    """Base document schema"""

    filename: str = Field(..., max_length=255)
    document_type: DocumentTypeEnum
    language: Optional[str] = Field(None, max_length=10)


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""

    document_id: str = Field(..., max_length=100)
    original_filename: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = None
    content: Optional[str] = None


class DocumentUpdate(BaseSchema):
    """Schema for updating a document"""

    filename: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field(None, max_length=10)
    summary: Optional[str] = None
    is_processed: Optional[bool] = None
    processing_status: Optional[str] = Field(None, max_length=50)


class DocumentResponse(DocumentBase):
    """Schema for document responses"""

    id: int
    document_id: str
    user_id: int
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    summary: Optional[str] = None
    file_url: Optional[str] = None
    is_processed: bool = False
    processing_status: str = "pending"
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    word_count: int = 0
    complexity_score: Optional[float] = None
    reading_time_minutes: int = 0
    key_topics: List[str] = Field(default_factory=list)
    vocabulary_extracted: List[str] = Field(default_factory=list)
    uploaded_at: datetime
    processed_at: Optional[datetime] = None


class DocumentWithContent(DocumentResponse):
    """Document response with content included"""

    content: Optional[str] = None
    processed_content: Optional[str] = None


# Learning Progress Schemas
class LearningProgressBase(BaseSchema):
    """Base learning progress schema"""

    language: str = Field(..., max_length=10)
    skill_type: str = Field(..., max_length=50)
    target_level: int = Field(10, ge=1, le=10)


class LearningProgressCreate(LearningProgressBase):
    """Schema for creating learning progress"""

    current_level: int = Field(1, ge=1, le=10)
    goals: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LearningProgressUpdate(BaseSchema):
    """Schema for updating learning progress"""

    current_level: Optional[int] = Field(None, ge=1, le=10)
    target_level: Optional[int] = Field(None, ge=1, le=10)
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    total_study_time_minutes: Optional[int] = Field(None, ge=0)
    sessions_completed: Optional[int] = Field(None, ge=0)
    words_learned: Optional[int] = Field(None, ge=0)
    conversations_completed: Optional[int] = Field(None, ge=0)
    status: Optional[LearningStatusEnum] = None
    goals: Optional[Dict[str, Any]] = None


class LearningProgressResponse(LearningProgressBase):
    """Schema for learning progress responses"""

    id: int
    user_id: int
    current_level: int = 1
    progress_percentage: float = 0.0
    total_study_time_minutes: int = 0
    sessions_completed: int = 0
    words_learned: int = 0
    conversations_completed: int = 0
    average_accuracy: float = 0.0
    improvement_rate: float = 0.0
    consistency_score: float = 0.0
    status: LearningStatusEnum = LearningStatusEnum.NOT_STARTED
    goals: Dict[str, Any] = Field(default_factory=dict)
    achievements: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    updated_at: datetime


# Vocabulary Schemas
class VocabularyBase(BaseSchema):
    """Base vocabulary schema"""

    language: str = Field(..., max_length=10)
    word: str = Field(..., max_length=255)
    translation: Optional[str] = Field(None, max_length=255)
    definition: Optional[str] = None
    pronunciation: Optional[str] = Field(None, max_length=255)


class VocabularyCreate(VocabularyBase):
    """Schema for creating vocabulary items"""

    phonetic_transcription: Optional[str] = Field(None, max_length=255)
    difficulty_level: int = Field(1, ge=1, le=10)
    example_sentences: Optional[List[str]] = Field(default_factory=list)
    context_tags: Optional[List[str]] = Field(default_factory=list)
    source_document_id: Optional[str] = Field(None, max_length=100)


class VocabularyUpdate(BaseSchema):
    """Schema for updating vocabulary items"""

    translation: Optional[str] = Field(None, max_length=255)
    definition: Optional[str] = None
    pronunciation: Optional[str] = Field(None, max_length=255)
    phonetic_transcription: Optional[str] = Field(None, max_length=255)
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    example_sentences: Optional[List[str]] = None
    context_tags: Optional[List[str]] = None
    mastery_level: Optional[float] = Field(None, ge=0.0, le=1.0)


class VocabularyResponse(VocabularyBase):
    """Schema for vocabulary responses"""

    id: int
    user_id: int
    phonetic_transcription: Optional[str] = None
    difficulty_level: int = 1
    frequency_score: float = 0.0
    importance_score: float = 0.0
    times_studied: int = 0
    times_correct: int = 0
    times_incorrect: int = 0
    mastery_level: float = 0.0
    example_sentences: List[str] = Field(default_factory=list)
    context_tags: List[str] = Field(default_factory=list)
    source_document_id: Optional[str] = None
    next_review_date: Optional[datetime] = None
    repetition_interval_days: int = 1
    ease_factor: float = 2.5
    first_learned: datetime
    last_reviewed: Optional[datetime] = None
    updated_at: datetime


# API Usage Schemas
class APIUsageBase(BaseSchema):
    """Base API usage schema"""

    api_provider: str = Field(..., max_length=50)
    api_endpoint: str = Field(..., max_length=100)
    request_type: str = Field(..., max_length=50)


class APIUsageCreate(APIUsageBase):
    """Schema for creating API usage records"""

    user_id: Optional[int] = None
    tokens_used: int = Field(0, ge=0)
    estimated_cost: float = Field(0.0, ge=0.0)
    request_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    response_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: str = Field("success", max_length=20)
    error_message: Optional[str] = None


class APIUsageResponse(APIUsageBase):
    """Schema for API usage responses"""

    id: int
    user_id: Optional[int] = None
    tokens_used: int = 0
    estimated_cost: float = 0.0
    actual_cost: Optional[float] = None
    request_metadata: Dict[str, Any] = Field(default_factory=dict)
    response_metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "success"
    error_message: Optional[str] = None
    created_at: datetime


# Special Request/Response Schemas
class ConversationWithMessages(ConversationResponse):
    """Conversation with included messages"""

    messages: List[MessageResponse] = Field(default_factory=list)


class UserLanguageAssociation(BaseSchema):
    """Schema for user-language association"""

    language: str = Field(..., max_length=10)
    proficiency_level: int = Field(1, ge=1, le=10)
    is_primary: bool = False


class BulkOperation(BaseSchema):
    """Schema for bulk operations"""

    operation: str = Field(..., max_length=50)
    items: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BulkOperationResponse(BaseSchema):
    """Schema for bulk operation responses"""

    operation: str
    total_items: int
    successful_items: int
    failed_items: int
    errors: List[str] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)


class SearchRequest(BaseSchema):
    """Schema for search requests"""

    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResponse(BaseSchema):
    """Schema for search responses"""

    query: str
    total_results: int
    limit: int
    offset: int
    results: List[Dict[str, Any]] = Field(default_factory=list)
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseSchema):
    """Schema for error responses"""

    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseSchema):
    """Schema for success responses"""

    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Export commonly used schemas
__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    # Language schemas
    "LanguageCreate",
    "LanguageResponse",
    # Conversation schemas
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationWithMessages",
    # Message schemas
    "MessageCreate",
    "MessageResponse",
    # Document schemas
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentWithContent",
    # Learning progress schemas
    "LearningProgressCreate",
    "LearningProgressUpdate",
    "LearningProgressResponse",
    # Vocabulary schemas
    "VocabularyCreate",
    "VocabularyUpdate",
    "VocabularyResponse",
    # API usage schemas
    "APIUsageCreate",
    "APIUsageResponse",
    # Utility schemas
    "UserLanguageAssociation",
    "BulkOperation",
    "BulkOperationResponse",
    "SearchRequest",
    "SearchResponse",
    "ErrorResponse",
    "SuccessResponse",
    # Enums
    "UserRoleEnum",
    "LanguageEnum",
    "ConversationRoleEnum",
    "DocumentTypeEnum",
    "LearningStatusEnum",
]
