"""
Comprehensive tests for app/models/database.py

Tests ORM models, validators, to_dict() methods, and session management to achieve TRUE 100% coverage.
Focus: Cover missing branches in validators, optional parameters, and defensive session handling.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.database import (
    APIUsage,
    Conversation,
    ConversationMessage,
    ConversationRole,
    Document,
    DocumentType,
    Language,
    LearningProgress,
    LearningStatus,
    User,
    UserRole,
    VocabularyItem,
    get_db_session,
)


class TestUserValidators:
    """Test User model validators for edge cases"""

    def test_validate_email_with_none(self):
        """Test email validator allows None values"""
        user = User(user_id="test123", username="testuser")
        # Email is nullable, so None should be accepted
        user.email = None
        # Validator should return None without raising error
        assert user.validate_email("email", None) is None

    def test_validate_email_with_valid_email(self):
        """Test email validator accepts valid email"""
        user = User(user_id="test123", username="testuser")
        result = user.validate_email("email", "test@example.com")
        assert result == "test@example.com"

    def test_validate_email_with_invalid_email_raises_error(self):
        """Test email validator raises ValueError for invalid email"""
        user = User(user_id="test123", username="testuser")
        with pytest.raises(ValueError, match="Invalid email format"):
            user.validate_email("email", "invalid-email")

    def test_validate_user_id_with_short_id_raises_error(self):
        """Test user_id validator raises ValueError for short IDs"""
        user = User(user_id="test123", username="testuser")
        with pytest.raises(ValueError, match="User ID must be at least 3 characters"):
            user.validate_user_id("user_id", "ab")

    def test_validate_user_id_with_empty_id_raises_error(self):
        """Test user_id validator raises ValueError for empty IDs"""
        user = User(user_id="test123", username="testuser")
        with pytest.raises(ValueError, match="User ID must be at least 3 characters"):
            user.validate_user_id("user_id", "")

    def test_validate_user_id_with_valid_id(self):
        """Test user_id validator accepts valid IDs"""
        user = User(user_id="test123", username="testuser")
        result = user.validate_user_id("user_id", "validuser123")
        assert result == "validuser123"


class TestConversationToDictWithMessages:
    """Test Conversation.to_dict() with include_messages parameter"""

    def test_conversation_to_dict_includes_messages_when_requested(self):
        """Test to_dict(include_messages=True) includes message list"""
        # Create a conversation
        conversation = Conversation(
            conversation_id="conv123",
            user_id=1,
            language="en",
            ai_model="claude",
        )

        # Create real ConversationMessage instances (not mocks)
        message1 = ConversationMessage(
            conversation_id=1,
            role=ConversationRole.USER,
            content="Hello",
        )
        message2 = ConversationMessage(
            conversation_id=1,
            role=ConversationRole.ASSISTANT,
            content="Hi there",
        )

        # Use patch.object to override the messages relationship
        with patch.object(conversation, "messages", [message1, message2]):
            # Test with include_messages=True
            result = conversation.to_dict(include_messages=True)

            # Verify messages are included
            assert "messages" in result
            assert len(result["messages"]) == 2
            assert result["messages"][0]["content"] == "Hello"
            assert result["messages"][1]["content"] == "Hi there"

    def test_conversation_to_dict_excludes_messages_by_default(self):
        """Test to_dict() excludes messages when include_messages=False (default)"""
        conversation = Conversation(
            conversation_id="conv123",
            user_id=1,
            language="en",
            ai_model="claude",
        )

        # Create a real message instance
        message = ConversationMessage(
            conversation_id=1,
            role=ConversationRole.USER,
            content="Hello",
        )

        # Use patch.object to override the messages relationship
        with patch.object(conversation, "messages", [message]):
            # Test with default (include_messages=False)
            result = conversation.to_dict(include_messages=False)

            # Verify messages are NOT included
            assert "messages" not in result

    def test_conversation_to_dict_without_include_messages_parameter(self):
        """Test to_dict() without parameter defaults to excluding messages"""
        conversation = Conversation(
            conversation_id="conv123",
            user_id=1,
            language="en",
            ai_model="claude",
        )

        # Test without parameter
        result = conversation.to_dict()

        # Verify messages are NOT included
        assert "messages" not in result


class TestDocumentToDictWithContent:
    """Test Document.to_dict() with include_content parameter"""

    def test_document_to_dict_includes_content_when_requested(self):
        """Test to_dict(include_content=True) includes content fields"""
        document = Document(
            document_id="doc123",
            user_id=1,
            filename="test.pdf",
            document_type=DocumentType.PDF,
        )
        document.content = "Original content here"
        document.processed_content = "Processed content here"

        # Test with include_content=True
        result = document.to_dict(include_content=True)

        # Verify content fields are included
        assert "content" in result
        assert "processed_content" in result
        assert result["content"] == "Original content here"
        assert result["processed_content"] == "Processed content here"

    def test_document_to_dict_excludes_content_by_default(self):
        """Test to_dict() excludes content when include_content=False (default)"""
        document = Document(
            document_id="doc123",
            user_id=1,
            filename="test.pdf",
            document_type=DocumentType.PDF,
        )
        document.content = "Original content here"
        document.processed_content = "Processed content here"

        # Test with default (include_content=False)
        result = document.to_dict(include_content=False)

        # Verify content fields are NOT included
        assert "content" not in result
        assert "processed_content" not in result

    def test_document_to_dict_without_include_content_parameter(self):
        """Test to_dict() without parameter defaults to excluding content"""
        document = Document(
            document_id="doc123",
            user_id=1,
            filename="test.pdf",
            document_type=DocumentType.PDF,
        )
        document.content = "Original content here"

        # Test without parameter
        result = document.to_dict()

        # Verify content is NOT included
        assert "content" not in result
        assert "processed_content" not in result


class TestGetDbSessionDefensivePatterns:
    """Test get_db_session() defensive session handling"""

    @patch("app.database.config.db_manager")
    def test_get_db_session_rollback_on_exception(self, mock_db_manager):
        """Test session rollback when exception occurs during yield"""
        # Create a mock session
        mock_session = MagicMock()
        mock_db_manager.get_sqlite_session.return_value = mock_session

        # Create generator
        session_gen = get_db_session()

        # Get the session
        session = next(session_gen)
        assert session == mock_session

        # Simulate exception during usage
        try:
            session_gen.throw(SQLAlchemyError("Database error"))
        except SQLAlchemyError:
            pass

        # Verify rollback was called (defensive pattern: if session: session.rollback())
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("app.database.config.db_manager")
    def test_get_db_session_close_in_finally(self, mock_db_manager):
        """Test session close in finally block (normal case)"""
        # Create a mock session
        mock_session = MagicMock()
        mock_db_manager.get_sqlite_session.return_value = mock_session

        # Use the generator normally
        session_gen = get_db_session()
        session = next(session_gen)

        # Close the generator (simulates end of with statement)
        try:
            next(session_gen)
        except StopIteration:
            pass

        # Verify close was called (defensive pattern: if session: session.close())
        mock_session.close.assert_called_once()

    @patch("app.database.config.db_manager")
    def test_get_db_session_defensive_none_check_in_exception(self, mock_db_manager):
        """Test defensive None check in exception handler when session is None"""
        # Simulate scenario where session assignment fails
        mock_db_manager.get_sqlite_session.side_effect = Exception("Connection failed")

        # Create generator
        session_gen = get_db_session()

        # Try to get session (will fail)
        with pytest.raises(Exception, match="Connection failed"):
            next(session_gen)

        # The defensive pattern `if session: session.rollback()` should handle session=None
        # This test ensures no AttributeError occurs when session is None

    @patch("app.database.config.db_manager")
    def test_get_db_session_defensive_none_check_in_finally(self, mock_db_manager):
        """Test defensive None check in finally block when session is None"""
        # Simulate scenario where session is None before finally
        mock_db_manager.get_sqlite_session.side_effect = Exception("Connection failed")

        # Create generator
        session_gen = get_db_session()

        # Try to get session and let exception propagate
        with pytest.raises(Exception, match="Connection failed"):
            next(session_gen)

        # The defensive pattern `if session: session.close()` should handle session=None
        # This test ensures no AttributeError occurs when session is None in finally block


class TestModelToDictMethods:
    """Test to_dict() methods for all models"""

    def test_user_to_dict_includes_sensitive_data_when_requested(self):
        """Test User.to_dict(include_sensitive=True)"""
        user = User(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            role=UserRole.CHILD,
        )

        result = user.to_dict(include_sensitive=True)

        assert result["email"] == "test@example.com"

    def test_user_to_dict_excludes_sensitive_data_by_default(self):
        """Test User.to_dict() excludes email by default"""
        user = User(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            role=UserRole.CHILD,
        )

        result = user.to_dict(include_sensitive=False)

        assert result["email"] is None

    def test_language_to_dict(self):
        """Test Language.to_dict()"""
        language = Language(
            code="en",
            name="English",
            native_name="English",
            has_speech_support=True,
        )

        result = language.to_dict()

        assert result["code"] == "en"
        assert result["name"] == "English"
        assert result["has_speech_support"] is True

    def test_conversation_message_to_dict(self):
        """Test ConversationMessage.to_dict()"""
        message = ConversationMessage(
            conversation_id=1,
            role=ConversationRole.USER,
            content="Hello, how are you?",
        )

        result = message.to_dict()

        assert result["conversation_id"] == 1
        assert result["role"] == "user"
        assert result["content"] == "Hello, how are you?"

    def test_learning_progress_to_dict(self):
        """Test LearningProgress.to_dict()"""
        progress = LearningProgress(
            user_id=1,
            language="en",
            skill_type="vocabulary",
            current_level=5,
            status=LearningStatus.IN_PROGRESS,
        )

        result = progress.to_dict()

        assert result["user_id"] == 1
        assert result["language"] == "en"
        assert result["skill_type"] == "vocabulary"
        assert result["status"] == "in_progress"

    def test_vocabulary_item_to_dict(self):
        """Test VocabularyItem.to_dict()"""
        vocab = VocabularyItem(
            user_id=1,
            language="en",
            word="hello",
            translation="hola",
        )

        result = vocab.to_dict()

        assert result["user_id"] == 1
        assert result["word"] == "hello"
        assert result["translation"] == "hola"

    def test_api_usage_to_dict(self):
        """Test APIUsage.to_dict()"""
        api_usage = APIUsage(
            user_id=1,
            api_provider="claude",
            api_endpoint="/v1/messages",
            request_type="chat",
            tokens_used=150,
        )

        result = api_usage.to_dict()

        assert result["user_id"] == 1
        assert result["api_provider"] == "claude"
        assert result["tokens_used"] == 150


class TestModelEnums:
    """Test enum definitions"""

    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.PARENT.value == "PARENT"
        assert UserRole.CHILD.value == "CHILD"
        assert UserRole.ADMIN.value == "ADMIN"

    def test_conversation_role_enum(self):
        """Test ConversationRole enum values"""
        assert ConversationRole.USER.value == "user"
        assert ConversationRole.ASSISTANT.value == "assistant"
        assert ConversationRole.SYSTEM.value == "system"

    def test_document_type_enum(self):
        """Test DocumentType enum values"""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.DOCX.value == "docx"
        assert DocumentType.URL.value == "url"
        assert DocumentType.YOUTUBE.value == "youtube"

    def test_learning_status_enum(self):
        """Test LearningStatus enum values"""
        assert LearningStatus.NOT_STARTED.value == "not_started"
        assert LearningStatus.IN_PROGRESS.value == "in_progress"
        assert LearningStatus.COMPLETED.value == "completed"
        assert LearningStatus.MASTERED.value == "mastered"
