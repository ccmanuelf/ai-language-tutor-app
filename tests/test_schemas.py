"""
Comprehensive tests for models/schemas.py - Pydantic schema validation

Tests all enums, base schemas, validators, field constraints, and schema classes
to achieve TRUE 100% coverage (statement + branch).
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    # API usage schemas
    APIUsageBase,
    APIUsageCreate,
    APIUsageResponse,
    # Base
    BaseSchema,
    BulkOperation,
    BulkOperationResponse,
    # Conversation schemas
    ConversationBase,
    ConversationCreate,
    ConversationResponse,
    ConversationRoleEnum,
    ConversationUpdate,
    ConversationWithMessages,
    # Document schemas
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentTypeEnum,
    DocumentUpdate,
    DocumentWithContent,
    ErrorResponse,
    # Language schemas
    LanguageBase,
    LanguageCreate,
    LanguageEnum,
    LanguageResponse,
    # Learning progress schemas
    LearningProgressBase,
    LearningProgressCreate,
    LearningProgressResponse,
    LearningProgressUpdate,
    LearningStatusEnum,
    # Message schemas
    MessageBase,
    MessageCreate,
    MessageResponse,
    SearchRequest,
    SearchResponse,
    SuccessResponse,
    # User schemas
    UserBase,
    UserCreate,
    # Utility schemas
    UserLanguageAssociation,
    UserProfile,
    UserResponse,
    # Enums
    UserRoleEnum,
    UserUpdate,
    # Vocabulary schemas
    VocabularyBase,
    VocabularyCreate,
    VocabularyResponse,
    VocabularyUpdate,
)


class TestEnums:
    """Test all enum classes"""

    def test_user_role_enum_values(self):
        """Test UserRoleEnum has correct values"""
        assert UserRoleEnum.PARENT == "parent"
        assert UserRoleEnum.CHILD == "child"
        assert UserRoleEnum.ADMIN == "admin"

    def test_language_enum_values(self):
        """Test LanguageEnum has correct values"""
        assert LanguageEnum.CHINESE == "zh"
        assert LanguageEnum.FRENCH == "fr"
        assert LanguageEnum.GERMAN == "de"
        assert LanguageEnum.JAPANESE == "ja"
        assert LanguageEnum.ENGLISH == "en"

    def test_conversation_role_enum_values(self):
        """Test ConversationRoleEnum has correct values"""
        assert ConversationRoleEnum.USER == "user"
        assert ConversationRoleEnum.ASSISTANT == "assistant"
        assert ConversationRoleEnum.SYSTEM == "system"

    def test_document_type_enum_values(self):
        """Test DocumentTypeEnum has correct values"""
        assert DocumentTypeEnum.PDF == "pdf"
        assert DocumentTypeEnum.DOCX == "docx"
        assert DocumentTypeEnum.PPTX == "pptx"
        assert DocumentTypeEnum.TXT == "txt"
        assert DocumentTypeEnum.URL == "url"
        assert DocumentTypeEnum.YOUTUBE == "youtube"

    def test_learning_status_enum_values(self):
        """Test LearningStatusEnum has correct values"""
        assert LearningStatusEnum.NOT_STARTED == "not_started"
        assert LearningStatusEnum.IN_PROGRESS == "in_progress"
        assert LearningStatusEnum.COMPLETED == "completed"
        assert LearningStatusEnum.MASTERED == "mastered"


class TestBaseSchema:
    """Test BaseSchema configuration"""

    def test_base_schema_config(self):
        """Test BaseSchema has correct config"""
        schema = BaseSchema()
        assert schema.model_config["from_attributes"] is True
        assert schema.model_config["arbitrary_types_allowed"] is True


class TestUserSchemas:
    """Test user-related schemas"""

    def test_user_base_creation(self):
        """Test UserBase schema creation with valid data"""
        user = UserBase(
            username="testuser",
            email="test@example.com",
            role=UserRoleEnum.CHILD,
            first_name="Test",
            last_name="User",
            ui_language="en",
            timezone="UTC",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRoleEnum.CHILD

    def test_user_base_minimal(self):
        """Test UserBase with minimal required fields"""
        user = UserBase(username="testuser")
        assert user.username == "testuser"
        assert user.role == UserRoleEnum.CHILD  # Default
        assert user.ui_language == "en"  # Default
        assert user.timezone == "UTC"  # Default

    def test_user_create_valid(self):
        """Test UserCreate with valid user_id"""
        user = UserCreate(
            username="testuser",
            user_id="test_user_123",
            password="password123",
        )
        assert user.user_id == "test_user_123"
        assert user.password == "password123"

    def test_user_create_user_id_validator_valid_characters(self):
        """Test user_id validator accepts valid characters"""
        user = UserCreate(username="test", user_id="valid-user_123")
        assert user.user_id == "valid-user_123"

    def test_user_create_user_id_validator_lowercase_conversion(self):
        """Test user_id validator converts to lowercase"""
        user = UserCreate(username="test", user_id="TEST_USER")
        assert user.user_id == "test_user"

    def test_user_create_user_id_validator_invalid_characters(self):
        """Test user_id validator rejects invalid characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="test", user_id="invalid@user!")
        assert (
            "User ID can only contain letters, numbers, hyphens, and underscores"
            in str(exc_info.value)
        )

    def test_user_create_with_defaults(self):
        """Test UserCreate default values for optional fields"""
        user = UserCreate(username="test", user_id="test123")
        assert user.preferences == {}
        assert user.privacy_settings == {}

    def test_user_update_partial(self):
        """Test UserUpdate with partial data"""
        update = UserUpdate(username="newusername", email="new@example.com")
        assert update.username == "newusername"
        assert update.email == "new@example.com"

    def test_user_update_all_none(self):
        """Test UserUpdate with all None values"""
        update = UserUpdate()
        assert update.username is None
        assert update.email is None

    def test_user_response_complete(self):
        """Test UserResponse with complete data"""
        user = UserResponse(
            id=1,
            user_id="test123",
            username="testuser",
            email="test@example.com",
            role=UserRoleEnum.CHILD,
            avatar_url="http://example.com/avatar.jpg",
            preferences={"theme": "dark"},
            is_active=True,
            is_verified=False,
            last_login=datetime(2025, 1, 1, 12, 0, 0),
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2025, 1, 1, 0, 0, 0),
        )
        assert user.id == 1
        assert user.is_active is True
        assert user.preferences == {"theme": "dark"}

    def test_user_profile_extended(self):
        """Test UserProfile with extended learning data"""
        profile = UserProfile(
            id=1,
            user_id="test123",
            username="testuser",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2025, 1, 1),
            languages=[{"code": "fr", "level": 5}],
            learning_progress=[{"skill": "speaking", "level": 3}],
            total_conversations=42,
            total_study_time_minutes=1200,
        )
        assert profile.total_conversations == 42
        assert profile.total_study_time_minutes == 1200
        assert len(profile.languages) == 1


class TestLanguageSchemas:
    """Test language-related schemas"""

    def test_language_base_creation(self):
        """Test LanguageBase schema creation"""
        lang = LanguageBase(
            code="fr",
            name="French",
            native_name="Français",
            is_active=True,
            has_speech_support=True,
            has_tts_support=True,
        )
        assert lang.code == "fr"
        assert lang.name == "French"
        assert lang.has_speech_support is True

    def test_language_create_with_config(self):
        """Test LanguageCreate with API config"""
        lang = LanguageCreate(
            code="de",
            name="German",
            speech_api_config={"api_key": "test123"},
        )
        assert lang.speech_api_config == {"api_key": "test123"}

    def test_language_create_default_config(self):
        """Test LanguageCreate default API config"""
        lang = LanguageCreate(code="es", name="Spanish")
        assert lang.speech_api_config == {}

    def test_language_response_complete(self):
        """Test LanguageResponse with all fields"""
        lang = LanguageResponse(
            id=1,
            code="ja",
            name="Japanese",
            native_name="日本語",
            is_active=True,
            has_speech_support=False,
            has_tts_support=True,
            speech_api_config={"provider": "google"},
        )
        assert lang.id == 1
        assert lang.code == "ja"


class TestConversationSchemas:
    """Test conversation-related schemas"""

    def test_conversation_base_creation(self):
        """Test ConversationBase schema"""
        conv = ConversationBase(
            title="Test Conversation",
            language="fr",
            ai_model="claude-3",
        )
        assert conv.title == "Test Conversation"
        assert conv.language == "fr"

    def test_conversation_create_with_context(self):
        """Test ConversationCreate with context data"""
        conv = ConversationCreate(
            conversation_id="conv_123",
            title="Learning French",
            language="fr",
            context_data={"level": "beginner"},
        )
        assert conv.conversation_id == "conv_123"
        assert conv.context_data == {"level": "beginner"}

    def test_conversation_create_default_context(self):
        """Test ConversationCreate default context"""
        conv = ConversationCreate(conversation_id="conv_123", language="de")
        assert conv.context_data == {}

    def test_conversation_update_partial(self):
        """Test ConversationUpdate with partial fields"""
        update = ConversationUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.context_data is None

    def test_conversation_response_complete(self):
        """Test ConversationResponse with all fields"""
        conv = ConversationResponse(
            id=1,
            conversation_id="conv_123",
            user_id=5,
            title="French Practice",
            language="fr",
            ai_model="claude-3",
            context_data={"level": "intermediate"},
            is_active=True,
            message_count=15,
            total_tokens=5000,
            estimated_cost=0.25,
            started_at=datetime(2025, 1, 1, 10, 0, 0),
            last_message_at=datetime(2025, 1, 1, 11, 0, 0),
            ended_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        assert conv.id == 1
        assert conv.message_count == 15
        assert conv.estimated_cost == 0.25

    def test_conversation_with_messages(self):
        """Test ConversationWithMessages includes message list"""
        conv = ConversationWithMessages(
            id=1,
            conversation_id="conv_123",
            user_id=5,
            language="en",
            started_at=datetime(2025, 1, 1),
            last_message_at=datetime(2025, 1, 1),
            messages=[
                MessageResponse(
                    id=1,
                    conversation_id=1,
                    role=ConversationRoleEnum.USER,
                    content="Hello",
                    created_at=datetime(2025, 1, 1),
                )
            ],
        )
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"


class TestMessageSchemas:
    """Test message-related schemas"""

    def test_message_base_creation(self):
        """Test MessageBase schema"""
        msg = MessageBase(
            role=ConversationRoleEnum.USER,
            content="Hello, how are you?",
            language="en",
        )
        assert msg.role == ConversationRoleEnum.USER
        assert msg.content == "Hello, how are you?"

    def test_message_create_with_feedback(self):
        """Test MessageCreate with pronunciation feedback"""
        msg = MessageCreate(
            conversation_id=1,
            role=ConversationRoleEnum.USER,
            content="Bonjour",
            language="fr",
            pronunciation_feedback={"score": 8.5, "errors": []},
        )
        assert msg.conversation_id == 1
        assert msg.pronunciation_feedback == {"score": 8.5, "errors": []}

    def test_message_create_default_feedback(self):
        """Test MessageCreate default pronunciation feedback"""
        msg = MessageCreate(
            conversation_id=1,
            role=ConversationRoleEnum.ASSISTANT,
            content="Bonjour!",
        )
        assert msg.pronunciation_feedback == {}

    def test_message_response_complete(self):
        """Test MessageResponse with all fields"""
        msg = MessageResponse(
            id=1,
            conversation_id=1,
            role=ConversationRoleEnum.ASSISTANT,
            content="Hello! How can I help?",
            language="en",
            token_count=10,
            estimated_cost=0.001,
            processing_time_ms=150,
            audio_url="http://example.com/audio.mp3",
            pronunciation_score=9.2,
            pronunciation_feedback={"excellent": True},
            sentiment_score=0.8,
            complexity_score=3.5,
            vocabulary_level=4,
            created_at=datetime(2025, 1, 1, 10, 0, 0),
        )
        assert msg.id == 1
        assert msg.token_count == 10
        assert msg.pronunciation_score == 9.2


class TestDocumentSchemas:
    """Test document-related schemas"""

    def test_document_base_creation(self):
        """Test DocumentBase schema"""
        doc = DocumentBase(
            filename="test.pdf",
            document_type=DocumentTypeEnum.PDF,
            language="en",
        )
        assert doc.filename == "test.pdf"
        assert doc.document_type == DocumentTypeEnum.PDF

    def test_document_create_complete(self):
        """Test DocumentCreate with all fields"""
        doc = DocumentCreate(
            document_id="doc_123",
            filename="report.pdf",
            document_type=DocumentTypeEnum.PDF,
            original_filename="Original Report.pdf",
            file_size=1024000,
            content="Document content here",
            language="en",
        )
        assert doc.document_id == "doc_123"
        assert doc.file_size == 1024000

    def test_document_update_partial(self):
        """Test DocumentUpdate with partial fields"""
        update = DocumentUpdate(
            filename="renamed.pdf",
            summary="Updated summary",
            is_processed=True,
        )
        assert update.filename == "renamed.pdf"
        assert update.is_processed is True

    def test_document_response_complete(self):
        """Test DocumentResponse with all fields"""
        doc = DocumentResponse(
            id=1,
            document_id="doc_123",
            user_id=5,
            filename="article.pdf",
            document_type=DocumentTypeEnum.PDF,
            original_filename="French Article.pdf",
            file_size=2048000,
            summary="Article about French culture",
            file_url="http://example.com/files/article.pdf",
            is_processed=True,
            processing_status="completed",
            processing_metadata={"pages": 10},
            word_count=5000,
            complexity_score=6.5,
            reading_time_minutes=25,
            key_topics=["culture", "history"],
            vocabulary_extracted=["bonjour", "merci"],
            uploaded_at=datetime(2025, 1, 1, 9, 0, 0),
            processed_at=datetime(2025, 1, 1, 9, 30, 0),
        )
        assert doc.id == 1
        assert doc.word_count == 5000
        assert len(doc.key_topics) == 2

    def test_document_with_content(self):
        """Test DocumentWithContent includes content fields"""
        doc = DocumentWithContent(
            id=1,
            document_id="doc_123",
            user_id=5,
            filename="test.txt",
            document_type=DocumentTypeEnum.TXT,
            uploaded_at=datetime(2025, 1, 1),
            content="Original content",
            processed_content="Processed content",
        )
        assert doc.content == "Original content"
        assert doc.processed_content == "Processed content"


class TestLearningProgressSchemas:
    """Test learning progress schemas"""

    def test_learning_progress_base_creation(self):
        """Test LearningProgressBase schema"""
        progress = LearningProgressBase(
            language="fr",
            skill_type="speaking",
            target_level=8,
        )
        assert progress.language == "fr"
        assert progress.skill_type == "speaking"
        assert progress.target_level == 8

    def test_learning_progress_base_default_target(self):
        """Test LearningProgressBase default target level"""
        progress = LearningProgressBase(language="de", skill_type="reading")
        assert progress.target_level == 10

    def test_learning_progress_create_with_goals(self):
        """Test LearningProgressCreate with goals"""
        progress = LearningProgressCreate(
            language="ja",
            skill_type="writing",
            current_level=3,
            target_level=7,
            goals={"daily_practice": 30, "weekly_sessions": 5},
        )
        assert progress.current_level == 3
        assert progress.goals == {"daily_practice": 30, "weekly_sessions": 5}

    def test_learning_progress_create_defaults(self):
        """Test LearningProgressCreate default values"""
        progress = LearningProgressCreate(language="es", skill_type="listening")
        assert progress.current_level == 1
        assert progress.goals == {}

    def test_learning_progress_update_partial(self):
        """Test LearningProgressUpdate with partial fields"""
        update = LearningProgressUpdate(
            current_level=5,
            progress_percentage=62.5,
            words_learned=150,
        )
        assert update.current_level == 5
        assert update.progress_percentage == 62.5

    def test_learning_progress_response_complete(self):
        """Test LearningProgressResponse with all fields"""
        progress = LearningProgressResponse(
            id=1,
            user_id=5,
            language="fr",
            skill_type="speaking",
            current_level=6,
            target_level=9,
            progress_percentage=66.7,
            total_study_time_minutes=1800,
            sessions_completed=45,
            words_learned=350,
            conversations_completed=30,
            average_accuracy=85.5,
            improvement_rate=1.2,
            consistency_score=0.88,
            status=LearningStatusEnum.IN_PROGRESS,
            goals={"target_date": "2025-06-01"},
            achievements=["30_conversations", "300_words"],
            started_at=datetime(2024, 12, 1, 0, 0, 0),
            last_activity=datetime(2025, 1, 15, 0, 0, 0),
            updated_at=datetime(2025, 1, 15, 0, 0, 0),
        )
        assert progress.id == 1
        assert progress.words_learned == 350
        assert len(progress.achievements) == 2


class TestVocabularySchemas:
    """Test vocabulary schemas"""

    def test_vocabulary_base_creation(self):
        """Test VocabularyBase schema"""
        vocab = VocabularyBase(
            language="fr",
            word="bonjour",
            translation="hello",
            definition="A greeting used in the morning or during the day",
            pronunciation="bon-zhoor",
        )
        assert vocab.word == "bonjour"
        assert vocab.translation == "hello"

    def test_vocabulary_create_complete(self):
        """Test VocabularyCreate with all fields"""
        vocab = VocabularyCreate(
            language="de",
            word="Guten Tag",
            translation="Good day",
            definition="A formal German greeting",
            pronunciation="goo-ten tahk",
            phonetic_transcription="ˈɡuːtn̩ ˈtaːk",
            difficulty_level=3,
            example_sentences=["Guten Tag, wie geht es Ihnen?"],
            context_tags=["greeting", "formal"],
            source_document_id="doc_123",
        )
        assert vocab.difficulty_level == 3
        assert len(vocab.example_sentences) == 1

    def test_vocabulary_create_defaults(self):
        """Test VocabularyCreate default values"""
        vocab = VocabularyCreate(language="es", word="hola")
        assert vocab.difficulty_level == 1
        assert vocab.example_sentences == []
        assert vocab.context_tags == []

    def test_vocabulary_update_partial(self):
        """Test VocabularyUpdate with partial fields"""
        update = VocabularyUpdate(
            translation="hi",
            difficulty_level=2,
            mastery_level=0.75,
        )
        assert update.translation == "hi"
        assert update.mastery_level == 0.75

    def test_vocabulary_response_complete(self):
        """Test VocabularyResponse with all fields"""
        vocab = VocabularyResponse(
            id=1,
            user_id=5,
            language="ja",
            word="こんにちは",
            translation="hello",
            definition="A common Japanese greeting",
            pronunciation="konnichiwa",
            phonetic_transcription="koɴɲitɕiwa",
            difficulty_level=2,
            frequency_score=9.5,
            importance_score=8.0,
            times_studied=15,
            times_correct=12,
            times_incorrect=3,
            mastery_level=0.8,
            example_sentences=["こんにちは、元気ですか？"],
            context_tags=["greeting", "common"],
            source_document_id="doc_456",
            next_review_date=datetime(2025, 1, 20, 0, 0, 0),
            repetition_interval_days=7,
            ease_factor=2.5,
            first_learned=datetime(2024, 12, 1, 0, 0, 0),
            last_reviewed=datetime(2025, 1, 13, 0, 0, 0),
            updated_at=datetime(2025, 1, 13, 0, 0, 0),
        )
        assert vocab.id == 1
        assert vocab.mastery_level == 0.8
        assert vocab.times_studied == 15


class TestAPIUsageSchemas:
    """Test API usage schemas"""

    def test_api_usage_base_creation(self):
        """Test APIUsageBase schema"""
        usage = APIUsageBase(
            api_provider="openai",
            api_endpoint="/v1/chat/completions",
            request_type="chat_completion",
        )
        assert usage.api_provider == "openai"
        assert usage.api_endpoint == "/v1/chat/completions"

    def test_api_usage_create_complete(self):
        """Test APIUsageCreate with all fields"""
        usage = APIUsageCreate(
            api_provider="anthropic",
            api_endpoint="/v1/messages",
            request_type="message",
            user_id=5,
            tokens_used=1500,
            estimated_cost=0.015,
            request_metadata={"model": "claude-3"},
            response_metadata={"stop_reason": "end_turn"},
            status="success",
            error_message=None,
        )
        assert usage.user_id == 5
        assert usage.tokens_used == 1500

    def test_api_usage_create_defaults(self):
        """Test APIUsageCreate default values"""
        usage = APIUsageCreate(
            api_provider="mistral",
            api_endpoint="/v1/stt",
            request_type="transcription",
        )
        assert usage.tokens_used == 0
        assert usage.estimated_cost == 0.0
        assert usage.status == "success"

    def test_api_usage_response_complete(self):
        """Test APIUsageResponse with all fields"""
        usage = APIUsageResponse(
            id=1,
            api_provider="claude",
            api_endpoint="/v1/messages",
            request_type="conversation",
            user_id=5,
            tokens_used=2000,
            estimated_cost=0.02,
            actual_cost=0.018,
            request_metadata={"temperature": 0.7},
            response_metadata={"latency_ms": 250},
            status="success",
            error_message=None,
            created_at=datetime(2025, 1, 15, 10, 30, 0),
        )
        assert usage.id == 1
        assert usage.actual_cost == 0.018


class TestUtilitySchemas:
    """Test utility schemas"""

    def test_user_language_association(self):
        """Test UserLanguageAssociation schema"""
        assoc = UserLanguageAssociation(
            language="fr",
            proficiency_level=6,
            is_primary=True,
        )
        assert assoc.language == "fr"
        assert assoc.proficiency_level == 6
        assert assoc.is_primary is True

    def test_bulk_operation_request(self):
        """Test BulkOperation schema"""
        bulk = BulkOperation(
            operation="delete_messages",
            items=[{"id": 1}, {"id": 2}, {"id": 3}],
            options={"confirm": True},
        )
        assert bulk.operation == "delete_messages"
        assert len(bulk.items) == 3

    def test_bulk_operation_response(self):
        """Test BulkOperationResponse schema"""
        response = BulkOperationResponse(
            operation="import_vocabulary",
            total_items=100,
            successful_items=95,
            failed_items=5,
            errors=["Invalid format on line 23", "Duplicate entry on line 45"],
            results=[{"id": 1, "status": "created"}],
        )
        assert response.successful_items == 95
        assert response.failed_items == 5
        assert len(response.errors) == 2

    def test_search_request_with_filters(self):
        """Test SearchRequest with filters"""
        search = SearchRequest(
            query="French vocabulary",
            filters={"language": "fr", "difficulty": [1, 2, 3]},
            limit=25,
            offset=50,
        )
        assert search.query == "French vocabulary"
        assert search.limit == 25

    def test_search_request_defaults(self):
        """Test SearchRequest default values"""
        search = SearchRequest(query="test")
        assert search.limit == 10
        assert search.offset == 0
        assert search.filters == {}

    def test_search_response(self):
        """Test SearchResponse schema"""
        response = SearchResponse(
            query="bonjour",
            total_results=42,
            limit=10,
            offset=0,
            results=[{"word": "bonjour", "translation": "hello"}],
            filters_applied={"language": "fr"},
        )
        assert response.total_results == 42
        assert len(response.results) == 1

    def test_error_response(self):
        """Test ErrorResponse schema"""
        error = ErrorResponse(
            error_code="VALIDATION_ERROR",
            error_message="Invalid input data",
            details={"field": "email", "issue": "Invalid format"},
            timestamp=datetime(2025, 1, 15, 10, 0, 0),
        )
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details["field"] == "email"

    def test_error_response_default_timestamp(self):
        """Test ErrorResponse with default timestamp"""
        error = ErrorResponse(
            error_code="NOT_FOUND",
            error_message="Resource not found",
        )
        assert error.error_code == "NOT_FOUND"
        assert isinstance(error.timestamp, datetime)

    def test_success_response_with_data(self):
        """Test SuccessResponse with data"""
        response = SuccessResponse(
            message="User created successfully",
            data={"user_id": "user_123", "username": "testuser"},
            timestamp=datetime(2025, 1, 15, 10, 0, 0),
        )
        assert response.message == "User created successfully"
        assert response.data["user_id"] == "user_123"

    def test_success_response_defaults(self):
        """Test SuccessResponse default values"""
        response = SuccessResponse()
        assert response.message == "Operation completed successfully"
        assert response.data is None
        assert isinstance(response.timestamp, datetime)


class TestFieldValidation:
    """Test field validators and constraints"""

    def test_username_min_length_validation(self):
        """Test username minimum length constraint"""
        with pytest.raises(ValidationError):
            UserBase(username="ab")  # Too short (min 3)

    def test_username_max_length_validation(self):
        """Test username maximum length constraint"""
        with pytest.raises(ValidationError):
            UserBase(username="x" * 101)  # Too long (max 100)

    def test_password_min_length_validation(self):
        """Test password minimum length constraint"""
        with pytest.raises(ValidationError):
            UserCreate(username="test", user_id="test123", password="short")

    def test_learning_progress_level_ge_validation(self):
        """Test learning progress level >= 1 constraint"""
        with pytest.raises(ValidationError):
            LearningProgressBase(language="fr", skill_type="reading", target_level=0)

    def test_learning_progress_level_le_validation(self):
        """Test learning progress level <= 10 constraint"""
        with pytest.raises(ValidationError):
            LearningProgressBase(language="fr", skill_type="reading", target_level=11)

    def test_search_limit_ge_validation(self):
        """Test search limit >= 1 constraint"""
        with pytest.raises(ValidationError):
            SearchRequest(query="test", limit=0)

    def test_search_limit_le_validation(self):
        """Test search limit <= 100 constraint"""
        with pytest.raises(ValidationError):
            SearchRequest(query="test", limit=101)

    def test_search_offset_ge_validation(self):
        """Test search offset >= 0 constraint"""
        with pytest.raises(ValidationError):
            SearchRequest(query="test", offset=-1)

    def test_message_content_min_length_validation(self):
        """Test message content minimum length"""
        with pytest.raises(ValidationError):
            MessageBase(role=ConversationRoleEnum.USER, content="")

    def test_query_min_length_validation(self):
        """Test search query minimum length"""
        with pytest.raises(ValidationError):
            SearchRequest(query="")

    def test_query_max_length_validation(self):
        """Test search query maximum length"""
        with pytest.raises(ValidationError):
            SearchRequest(query="x" * 501)


class TestSchemaDefaults:
    """Test default values and field factories"""

    def test_user_create_preferences_default_factory(self):
        """Test preferences default_factory creates new dict"""
        user1 = UserCreate(username="user1", user_id="user1")
        user2 = UserCreate(username="user2", user_id="user2")
        # Verify they have different dict instances
        user1.preferences["key"] = "value1"
        assert "key" not in user2.preferences

    def test_conversation_create_context_default_factory(self):
        """Test context_data default_factory creates new dict"""
        conv1 = ConversationCreate(conversation_id="conv1", language="en")
        conv2 = ConversationCreate(conversation_id="conv2", language="fr")
        conv1.context_data["test"] = "value"
        assert "test" not in conv2.context_data

    def test_message_create_feedback_default_factory(self):
        """Test pronunciation_feedback default_factory"""
        msg1 = MessageCreate(
            conversation_id=1, role=ConversationRoleEnum.USER, content="test1"
        )
        msg2 = MessageCreate(
            conversation_id=2, role=ConversationRoleEnum.USER, content="test2"
        )
        msg1.pronunciation_feedback["score"] = 9.0
        assert "score" not in msg2.pronunciation_feedback

    def test_document_response_default_factories(self):
        """Test multiple default_factory fields in DocumentResponse"""
        doc = DocumentResponse(
            id=1,
            document_id="doc_123",
            user_id=5,
            filename="test.pdf",
            document_type=DocumentTypeEnum.PDF,
            uploaded_at=datetime(2025, 1, 1),
        )
        # All these should be separate instances
        assert doc.processing_metadata == {}
        assert doc.key_topics == []
        assert doc.vocabulary_extracted == []

    def test_learning_progress_response_default_factories(self):
        """Test default_factory fields in LearningProgressResponse"""
        progress = LearningProgressResponse(
            id=1,
            user_id=5,
            language="fr",
            skill_type="speaking",
            updated_at=datetime(2025, 1, 1),
        )
        assert progress.goals == {}
        assert progress.achievements == []

    def test_vocabulary_create_default_factories(self):
        """Test default_factory lists in VocabularyCreate"""
        vocab1 = VocabularyCreate(language="fr", word="word1")
        vocab2 = VocabularyCreate(language="de", word="word2")
        vocab1.example_sentences.append("sentence1")
        assert len(vocab2.example_sentences) == 0

    def test_bulk_operation_default_factory(self):
        """Test BulkOperation options default_factory"""
        op1 = BulkOperation(operation="delete", items=[{"id": 1}])
        op2 = BulkOperation(operation="update", items=[{"id": 2}])
        op1.options["confirm"] = True
        assert "confirm" not in op2.options

    def test_bulk_operation_response_default_factories(self):
        """Test BulkOperationResponse default_factory lists"""
        response = BulkOperationResponse(
            operation="test",
            total_items=10,
            successful_items=8,
            failed_items=2,
        )
        assert response.errors == []
        assert response.results == []

    def test_search_request_filters_default_factory(self):
        """Test SearchRequest filters default_factory"""
        search1 = SearchRequest(query="test1")
        search2 = SearchRequest(query="test2")
        search1.filters["lang"] = "fr"
        assert "lang" not in search2.filters

    def test_error_response_details_default_factory(self):
        """Test ErrorResponse details default_factory"""
        err1 = ErrorResponse(error_code="ERR1", error_message="Error 1")
        err2 = ErrorResponse(error_code="ERR2", error_message="Error 2")
        err1.details["field"] = "username"
        assert "field" not in err2.details
