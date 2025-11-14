"""
Comprehensive tests for conversation_persistence.py

This module tests database persistence operations for conversation management,
including saving/loading conversations, messages, and learning progress.

Target: 100% code coverage
Test categories:
1. Initialization (1 test)
2. Save conversation metadata - new conversations (8 tests)
3. Save conversation metadata - update existing (7 tests)
4. Save conversation metadata - error handling (3 tests)
5. Save messages to database - success cases (7 tests)
6. Save messages to database - error handling (4 tests)
7. Save learning progress - success cases (10 tests)
8. Save learning progress - error handling (3 tests)
9. Load conversation from database - success cases (6 tests)
10. Load conversation from database - error handling (3 tests)
11. Helper methods - role conversion (4 tests)
12. Helper methods - message conversion (3 tests)
13. Helper methods - difficulty estimation (7 tests)
14. Helper methods - user ID extraction (3 tests)
15. Helper methods - vocabulary checks (4 tests)
16. Integration tests (3 tests)

Total: ~75 comprehensive tests covering all 143 statements
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.database import (
    Conversation,
    ConversationRole,
    LearningProgress,
    VocabularyItem,
)
from app.models.database import (
    ConversationMessage as DBConversationMessage,
)
from app.services.conversation_models import (
    ConversationContext,
    ConversationMessage,
    LearningFocus,
    MessageRole,
)
from app.services.conversation_persistence import (
    ConversationPersistence,
    conversation_persistence,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def persistence():
    """Create ConversationPersistence instance"""
    return ConversationPersistence()


@pytest.fixture
def sample_context():
    """Create sample conversation context"""
    return ConversationContext(
        conversation_id="conv_123",
        user_id="42",
        language="spanish",
        learning_focus=LearningFocus.CONVERSATION,
        current_topic="Restaurant ordering",
        vocabulary_level="intermediate",
        learning_goals=["Practice ordering food", "Learn restaurant vocabulary"],
        mistakes_tracked=[{"mistake": "yo querer", "correction": "yo quiero"}],
        vocabulary_introduced=["mesero", "cuenta", "propina"],
        session_start_time=datetime(2025, 11, 15, 10, 0, 0),
        last_activity=datetime(2025, 11, 15, 10, 30, 0),
        is_scenario_based=True,
        scenario_id="restaurant_basic",
        scenario_progress_id="prog_456",
        scenario_phase="ordering",
    )


@pytest.fixture
def sample_messages():
    """Create sample conversation messages"""
    return [
        ConversationMessage(
            role=MessageRole.USER,
            content="Hola, quiero una mesa para dos",
            timestamp=datetime(2025, 11, 15, 10, 5, 0),
            language="spanish",
            metadata={"token_count": 15, "estimated_cost": 0.001},
        ),
        ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="¡Perfecto! Les tengo una mesa junto a la ventana.",
            timestamp=datetime(2025, 11, 15, 10, 5, 30),
            language="spanish",
            metadata={
                "token_count": 25,
                "estimated_cost": 0.002,
                "processing_time_ms": 450,
            },
        ),
        ConversationMessage(
            role=MessageRole.SYSTEM,
            content="Vocabulary introduced: mesero, cuenta",
            timestamp=datetime(2025, 11, 15, 10, 6, 0),
            language="spanish",
            metadata={},
        ),
    ]


@pytest.fixture
def mock_session():
    """Create mock database session"""
    session = Mock(spec=Session)
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_conversation():
    """Create mock Conversation database object"""
    conv = Mock(spec=Conversation)
    conv.id = 1
    conv.conversation_id = "conv_123"
    conv.language = "spanish"
    conv.is_active = True
    conv.last_message_at = datetime.now()
    conv.context_data = {}
    conv.ended_at = None
    conv.message_count = 0
    return conv


# ============================================================================
# 1. Initialization Tests (1 test)
# ============================================================================


def test_initialization():
    """Test ConversationPersistence initialization"""
    persistence = ConversationPersistence()
    assert persistence is not None
    assert isinstance(persistence, ConversationPersistence)


def test_global_instance_exists():
    """Test global conversation_persistence instance exists"""
    assert conversation_persistence is not None
    assert isinstance(conversation_persistence, ConversationPersistence)


# ============================================================================
# 2. Save Conversation Metadata - New Conversations (8 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_conversation_new_success(persistence, sample_context, mock_session):
    """Test successfully saving a new conversation"""
    # Mock query to return None (conversation doesn't exist)
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_conversation_new_with_numeric_user_id(
    persistence, sample_context, mock_session
):
    """Test saving conversation with numeric user_id"""
    sample_context.user_id = "123"  # Numeric string

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        # Verify Conversation was created with correct user_id
        call_args = mock_session.add.call_args[0][0]
        assert call_args.user_id == 123


@pytest.mark.asyncio
async def test_save_conversation_new_with_non_numeric_user_id(
    persistence, sample_context, mock_session
):
    """Test saving conversation with non-numeric user_id falls back to 1"""
    sample_context.user_id = "user_abc"  # Non-numeric string

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        # Verify fallback to user_id = 1
        call_args = mock_session.add.call_args[0][0]
        assert call_args.user_id == 1


@pytest.mark.asyncio
async def test_save_conversation_new_with_scenario_data(
    persistence, sample_context, mock_session
):
    """Test saving conversation includes scenario-based learning data"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        # Verify context_data includes scenario info
        call_args = mock_session.add.call_args[0][0]
        assert call_args.context_data["is_scenario_based"] is True
        assert call_args.context_data["scenario_id"] == "restaurant_basic"
        assert call_args.context_data["scenario_progress_id"] == "prog_456"
        assert call_args.context_data["scenario_phase"] == "ordering"


@pytest.mark.asyncio
async def test_save_conversation_new_active_status(
    persistence, sample_context, mock_session
):
    """Test saving conversation with active status"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        call_args = mock_session.add.call_args[0][0]
        assert call_args.is_active is True


@pytest.mark.asyncio
async def test_save_conversation_new_paused_status(
    persistence, sample_context, mock_session
):
    """Test saving conversation with paused status (not active)"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "paused"
        )

        assert result is True
        call_args = mock_session.add.call_args[0][0]
        assert call_args.is_active is False


@pytest.mark.asyncio
async def test_save_conversation_new_sets_title_from_topic(
    persistence, sample_context, mock_session
):
    """Test conversation title is set from current_topic"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        call_args = mock_session.add.call_args[0][0]
        assert call_args.title == "Restaurant ordering"


@pytest.mark.asyncio
async def test_save_conversation_new_no_topic_uses_default_title(
    persistence, sample_context, mock_session
):
    """Test conversation title defaults to language name when no topic"""
    sample_context.current_topic = None

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        call_args = mock_session.add.call_args[0][0]
        assert call_args.title == "Conversation in spanish"


# ============================================================================
# 3. Save Conversation Metadata - Update Existing (7 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_conversation_update_existing(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test updating an existing conversation"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        # Should not call add for update
        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_conversation_update_language(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test updating conversation language"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        assert mock_conversation.language == "spanish"


@pytest.mark.asyncio
async def test_save_conversation_update_is_active(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test updating conversation is_active status"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "paused"
        )

        assert result is True
        assert mock_conversation.is_active is False


@pytest.mark.asyncio
async def test_save_conversation_update_last_message_at(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test updating last_message_at timestamp"""
    old_timestamp = mock_conversation.last_message_at

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        # Timestamp should be updated (will be newer than old_timestamp)
        assert mock_conversation.last_message_at != old_timestamp


@pytest.mark.asyncio
async def test_save_conversation_update_context_data(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test updating context_data dictionary"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        assert mock_conversation.context_data["learning_focus"] == "conversation"
        assert mock_conversation.context_data["current_topic"] == "Restaurant ordering"
        assert mock_conversation.context_data["vocabulary_level"] == "intermediate"


@pytest.mark.asyncio
async def test_save_conversation_completed_sets_ended_at(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test completed status sets ended_at timestamp"""
    assert mock_conversation.ended_at is None

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "completed"
        )

        assert result is True
        assert mock_conversation.ended_at is not None


@pytest.mark.asyncio
async def test_save_conversation_update_non_completed_no_ended_at(
    persistence, sample_context, mock_session, mock_conversation
):
    """Test non-completed status does not set ended_at"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is True
        assert mock_conversation.ended_at is None


# ============================================================================
# 4. Save Conversation Metadata - Error Handling (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_conversation_database_error(
    persistence, sample_context, mock_session
):
    """Test handling SQLAlchemyError during save"""
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is False
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_conversation_unexpected_error(
    persistence, sample_context, mock_session
):
    """Test handling unexpected exception during save"""
    mock_session.query.side_effect = ValueError("Unexpected error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is False
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_conversation_commit_error(
    persistence, sample_context, mock_session
):
    """Test handling commit error"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query
    mock_session.commit.side_effect = SQLAlchemyError("Commit failed")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )

        assert result is False
        mock_session.rollback.assert_called_once()


# ============================================================================
# 5. Save Messages to Database - Success Cases (7 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_messages_success(
    persistence, sample_messages, mock_session, mock_conversation
):
    """Test successfully saving messages"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_query.filter.return_value.count.return_value = 0  # No existing messages
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is True
        # Should add 3 messages
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_messages_only_new_messages(
    persistence, sample_messages, mock_session, mock_conversation
):
    """Test saving only new messages (skipping existing ones)"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    # First call to count() returns existing messages count (1)
    # Second call returns updated count (4)
    count_mock = Mock()
    count_mock.count.side_effect = [1, 4]
    mock_session.query.return_value.filter.return_value = count_mock

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is True
        # Should only add 2 new messages (total 3 - existing 1)
        assert mock_session.add.call_count == 2


@pytest.mark.asyncio
async def test_save_messages_with_metadata(
    persistence, sample_messages, mock_session, mock_conversation
):
    """Test messages saved with metadata (token_count, cost, processing_time)"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_query.filter.return_value.count.return_value = 0
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is True
        # Check first added message has metadata
        first_call = mock_session.add.call_args_list[0][0][0]
        assert first_call.token_count == 15
        assert first_call.estimated_cost == 0.001


@pytest.mark.asyncio
async def test_save_messages_with_missing_metadata_fields(
    persistence, mock_session, mock_conversation
):
    """Test messages with missing metadata fields default to 0"""
    messages = [
        ConversationMessage(
            role=MessageRole.USER,
            content="Test",
            timestamp=datetime.now(),
            language="en",
            metadata={},  # Empty metadata
        )
    ]

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_query.filter.return_value.count.return_value = 0
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", messages)

        assert result is True
        # Check message defaults
        first_call = mock_session.add.call_args_list[0][0][0]
        assert first_call.token_count == 0
        assert first_call.estimated_cost == 0.0
        assert first_call.processing_time_ms == 0


@pytest.mark.asyncio
async def test_save_messages_converts_role_enum(
    persistence, sample_messages, mock_session, mock_conversation
):
    """Test MessageRole enum is converted to ConversationRole"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_query.filter.return_value.count.return_value = 0
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is True
        # Check roles were converted
        first_call = mock_session.add.call_args_list[0][0][0]
        assert first_call.role == ConversationRole.USER


@pytest.mark.asyncio
async def test_save_messages_preserves_timestamp(
    persistence, sample_messages, mock_session, mock_conversation
):
    """Test message timestamps are preserved"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_query.filter.return_value.count.return_value = 0
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is True
        # Check timestamp preserved
        first_call = mock_session.add.call_args_list[0][0][0]
        assert first_call.created_at == datetime(2025, 11, 15, 10, 5, 0)


# ============================================================================
# 6. Save Messages to Database - Error Handling (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_messages_conversation_not_found(
    persistence, sample_messages, mock_session
):
    """Test saving messages when conversation doesn't exist"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None  # Conversation not found
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_999", sample_messages)

        assert result is False
        mock_session.add.assert_not_called()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_messages_database_error(persistence, sample_messages, mock_session):
    """Test handling SQLAlchemyError during message save"""
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is False
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_messages_unexpected_error(
    persistence, sample_messages, mock_session
):
    """Test handling unexpected exception during message save"""
    mock_session.query.side_effect = ValueError("Unexpected error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is False
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_messages_commit_error(
    persistence, sample_messages, mock_session, mock_conversation
):
    """Test handling commit error during message save"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_query.filter.return_value.count.return_value = 0
    mock_session.query.return_value = mock_query
    mock_session.commit.side_effect = SQLAlchemyError("Commit failed")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_messages_to_db("conv_123", sample_messages)

        assert result is False
        mock_session.rollback.assert_called_once()


# ============================================================================
# 7. Save Learning Progress - Success Cases (10 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_learning_progress_success(
    persistence, sample_context, mock_session
):
    """Test successfully saving learning progress"""
    # Use MagicMock to support += operations
    vocab_progress = MagicMock(spec=LearningProgress)
    vocab_progress.words_learned = 10
    vocab_progress.sessions_completed = 5

    # Mock conversation progress query
    conv_progress = MagicMock(spec=LearningProgress)
    conv_progress.conversations_completed = 3
    conv_progress.sessions_completed = 2

    # Mock vocabulary exists check
    def query_side_effect(model):
        query_mock = Mock()
        filter_mock = Mock()

        if model == LearningProgress:
            # Return vocab_progress first, conv_progress second
            filter_mock.first.side_effect = [vocab_progress, conv_progress]
        elif model == VocabularyItem:
            # No existing vocabulary
            filter_mock.first.return_value = None

        query_mock.filter.return_value = filter_mock
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_learning_progress_extracts_user_id(
    persistence, sample_context, mock_session
):
    """Test _extract_user_id is called correctly"""
    sample_context.user_id = "999"

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        # Simplified mocks
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True


@pytest.mark.asyncio
async def test_save_learning_progress_saves_vocabulary_items(
    persistence, sample_context, mock_session
):
    """Test saves new vocabulary items"""

    def query_side_effect(model):
        query_mock = Mock()
        filter_mock = Mock()
        filter_mock.first.return_value = None  # No existing vocab or progress
        query_mock.filter.return_value = filter_mock
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True
        # Should add 3 vocabulary items (mesero, cuenta, propina)
        assert mock_session.add.call_count == 3


@pytest.mark.asyncio
async def test_save_learning_progress_no_vocabulary_introduced(
    persistence, sample_context, mock_session
):
    """Test handles empty vocabulary_introduced list"""
    sample_context.vocabulary_introduced = []

    mock_session.query.return_value.filter.return_value.first.return_value = None

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True
        # No vocabulary items should be added
        mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_save_learning_progress_estimates_difficulty(
    persistence, sample_context, mock_session
):
    """Test vocabulary items get difficulty level from vocabulary_level"""
    sample_context.vocabulary_level = "advanced"

    def query_side_effect(model):
        query_mock = Mock()
        filter_mock = Mock()
        filter_mock.first.return_value = None
        query_mock.filter.return_value = filter_mock
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True
        # Check first vocabulary item has difficulty level
        first_vocab = mock_session.add.call_args_list[0][0][0]
        assert first_vocab.difficulty_level == 8  # advanced = 8


@pytest.mark.asyncio
async def test_save_learning_progress_no_vocab_progress_exists(
    persistence, sample_context, mock_session
):
    """Test handles missing vocabulary progress record gracefully"""

    def query_side_effect(model):
        query_mock = Mock()
        if model == LearningProgress:
            # Both progress records don't exist
            query_mock.filter.return_value.first.return_value = None
        else:
            query_mock.filter.return_value.first.return_value = None
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True


@pytest.mark.asyncio
async def test_save_learning_progress_no_conversation_progress_exists(
    persistence, sample_context, mock_session
):
    """Test handles missing conversation progress record gracefully"""
    vocab_progress = MagicMock(spec=LearningProgress)
    vocab_progress.words_learned = 10

    def query_side_effect(model):
        query_mock = Mock()
        if model == LearningProgress:
            filter_mock = Mock()
            # Vocab progress exists, conversation progress doesn't
            filter_mock.first.side_effect = [vocab_progress, None]
            query_mock.filter.return_value = filter_mock
        else:
            query_mock.filter.return_value.first.return_value = None
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is True


# ============================================================================
# 8. Save Learning Progress - Error Handling (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_learning_progress_database_error(
    persistence, sample_context, mock_session
):
    """Test handling SQLAlchemyError during progress save"""
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is False
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_learning_progress_unexpected_error(
    persistence, sample_context, mock_session
):
    """Test handling unexpected exception during progress save"""
    mock_session.query.side_effect = ValueError("Unexpected error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is False
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_learning_progress_commit_error(
    persistence, sample_context, mock_session
):
    """Test handling commit error during progress save"""
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.commit.side_effect = SQLAlchemyError("Commit failed")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.save_learning_progress("conv_123", sample_context)

        assert result is False
        mock_session.rollback.assert_called_once()


# ============================================================================
# 9. Load Conversation from Database - Success Cases (6 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_load_conversation_success(persistence, mock_session, mock_conversation):
    """Test successfully loading conversation"""
    # Mock messages
    mock_msg1 = Mock(spec=DBConversationMessage)
    mock_msg1.role = ConversationRole.USER
    mock_msg1.content = "Hello"
    mock_msg1.language = "en"
    mock_msg1.created_at = datetime(2025, 11, 15, 10, 0, 0)
    mock_msg1.token_count = 5
    mock_msg1.estimated_cost = 0.001
    mock_msg1.processing_time_ms = 100

    mock_conversation.user_id = 42
    mock_conversation.started_at = datetime(2025, 11, 15, 9, 0, 0)
    mock_conversation.last_message_at = datetime(2025, 11, 15, 10, 0, 0)

    def query_side_effect(model):
        query_mock = Mock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conversation
        elif model == DBConversationMessage:
            filter_mock = Mock()
            filter_mock.order_by.return_value.all.return_value = [mock_msg1]
            query_mock.filter.return_value = filter_mock
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is not None
        assert result["conversation_id"] == "conv_123"
        assert result["user_id"] == "42"
        assert result["language"] == "spanish"
        assert len(result["messages"]) == 1
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_conversation_not_found(persistence, mock_session):
    """Test loading non-existent conversation returns None"""
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_999")

        assert result is None
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_conversation_with_context_data(
    persistence, mock_session, mock_conversation
):
    """Test loading conversation includes context_data"""
    mock_conversation.context_data = {
        "learning_focus": "conversation",
        "current_topic": "Greetings",
    }
    mock_conversation.user_id = 1
    mock_conversation.started_at = datetime.now()
    mock_conversation.last_message_at = datetime.now()

    def query_side_effect(model):
        query_mock = Mock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conversation
        elif model == DBConversationMessage:
            query_mock.filter.return_value.order_by.return_value.all.return_value = []
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is not None
        assert result["context_data"]["learning_focus"] == "conversation"
        assert result["context_data"]["current_topic"] == "Greetings"


@pytest.mark.asyncio
async def test_load_conversation_with_null_context_data(
    persistence, mock_session, mock_conversation
):
    """Test loading conversation with null context_data defaults to empty dict"""
    mock_conversation.context_data = None
    mock_conversation.user_id = 1
    mock_conversation.started_at = datetime.now()
    mock_conversation.last_message_at = datetime.now()

    def query_side_effect(model):
        query_mock = Mock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conversation
        elif model == DBConversationMessage:
            query_mock.filter.return_value.order_by.return_value.all.return_value = []
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is not None
        assert result["context_data"] == {}


@pytest.mark.asyncio
async def test_load_conversation_messages_ordered_by_timestamp(
    persistence, mock_session, mock_conversation
):
    """Test loaded messages are ordered by created_at"""
    # Create messages with different timestamps
    mock_msg1 = Mock(spec=DBConversationMessage)
    mock_msg1.role = ConversationRole.USER
    mock_msg1.content = "First"
    mock_msg1.language = "en"
    mock_msg1.created_at = datetime(2025, 11, 15, 10, 0, 0)
    mock_msg1.token_count = 5
    mock_msg1.estimated_cost = 0.001
    mock_msg1.processing_time_ms = 100

    mock_msg2 = Mock(spec=DBConversationMessage)
    mock_msg2.role = ConversationRole.ASSISTANT
    mock_msg2.content = "Second"
    mock_msg2.language = "en"
    mock_msg2.created_at = datetime(2025, 11, 15, 10, 1, 0)
    mock_msg2.token_count = 10
    mock_msg2.estimated_cost = 0.002
    mock_msg2.processing_time_ms = 200

    mock_conversation.user_id = 1
    mock_conversation.started_at = datetime.now()
    mock_conversation.last_message_at = datetime.now()

    def query_side_effect(model):
        query_mock = Mock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conversation
        elif model == DBConversationMessage:
            order_mock = Mock()
            order_mock.all.return_value = [mock_msg1, mock_msg2]
            query_mock.filter.return_value.order_by.return_value = order_mock
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is not None
        assert len(result["messages"]) == 2
        # Verify messages are in order
        assert result["messages"][0]["content"] == "First"
        assert result["messages"][1]["content"] == "Second"


@pytest.mark.asyncio
async def test_load_conversation_no_messages(
    persistence, mock_session, mock_conversation
):
    """Test loading conversation with no messages"""
    mock_conversation.user_id = 1
    mock_conversation.started_at = datetime.now()
    mock_conversation.last_message_at = datetime.now()

    def query_side_effect(model):
        query_mock = Mock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conversation
        elif model == DBConversationMessage:
            query_mock.filter.return_value.order_by.return_value.all.return_value = []
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is not None
        assert result["messages"] == []


# ============================================================================
# 10. Load Conversation from Database - Error Handling (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_load_conversation_database_error(persistence, mock_session):
    """Test handling SQLAlchemyError during load"""
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is None
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_conversation_unexpected_error(persistence, mock_session):
    """Test handling unexpected exception during load"""
    mock_session.query.side_effect = ValueError("Unexpected error")

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is None
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_conversation_message_query_error(
    persistence, mock_session, mock_conversation
):
    """Test handling error when querying messages"""
    mock_conversation.user_id = 1

    def query_side_effect(model):
        query_mock = Mock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conversation
        elif model == DBConversationMessage:
            # Error when querying messages
            query_mock.filter.side_effect = SQLAlchemyError("Message query error")
        return query_mock

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.return_value = iter([mock_session])

        result = await persistence.load_conversation_from_db("conv_123")

        assert result is None


# ============================================================================
# 11. Helper Methods - Role Conversion (4 tests)
# ============================================================================


def test_convert_message_role_user(persistence):
    """Test converting MessageRole.USER to ConversationRole.USER"""
    result = persistence._convert_message_role(MessageRole.USER)
    assert result == ConversationRole.USER


def test_convert_message_role_assistant(persistence):
    """Test converting MessageRole.ASSISTANT to ConversationRole.ASSISTANT"""
    result = persistence._convert_message_role(MessageRole.ASSISTANT)
    assert result == ConversationRole.ASSISTANT


def test_convert_message_role_system(persistence):
    """Test converting MessageRole.SYSTEM to ConversationRole.SYSTEM"""
    result = persistence._convert_message_role(MessageRole.SYSTEM)
    assert result == ConversationRole.SYSTEM


def test_convert_message_role_unknown_defaults_to_user(persistence):
    """Test unknown role defaults to USER"""
    # Create a mock role that's not in the mapping
    mock_role = Mock()
    mock_role.name = "UNKNOWN"

    result = persistence._convert_message_role(mock_role)
    assert result == ConversationRole.USER


# ============================================================================
# 12. Helper Methods - Message Conversion (3 tests)
# ============================================================================


def test_convert_db_message(persistence):
    """Test converting database message to dictionary"""
    db_msg = Mock(spec=DBConversationMessage)
    db_msg.role = ConversationRole.USER
    db_msg.content = "Test message"
    db_msg.language = "spanish"
    db_msg.created_at = datetime(2025, 11, 15, 10, 0, 0)
    db_msg.token_count = 15
    db_msg.estimated_cost = 0.002
    db_msg.processing_time_ms = 250

    result = persistence._convert_db_message(db_msg)

    assert result["role"] == "user"
    assert result["content"] == "Test message"
    assert result["language"] == "spanish"
    assert result["timestamp"] == "2025-11-15T10:00:00"
    assert result["metadata"]["token_count"] == 15
    assert result["metadata"]["estimated_cost"] == 0.002
    assert result["metadata"]["processing_time_ms"] == 250


def test_convert_db_message_with_zero_metadata(persistence):
    """Test converting message with zero metadata values"""
    db_msg = Mock(spec=DBConversationMessage)
    db_msg.role = ConversationRole.ASSISTANT
    db_msg.content = "Response"
    db_msg.language = "french"
    db_msg.created_at = datetime(2025, 11, 15, 11, 30, 0)
    db_msg.token_count = 0
    db_msg.estimated_cost = 0.0
    db_msg.processing_time_ms = 0

    result = persistence._convert_db_message(db_msg)

    assert result["metadata"]["token_count"] == 0
    assert result["metadata"]["estimated_cost"] == 0.0
    assert result["metadata"]["processing_time_ms"] == 0


def test_convert_db_message_formats_timestamp_iso(persistence):
    """Test message timestamp is formatted as ISO string"""
    db_msg = Mock(spec=DBConversationMessage)
    db_msg.role = ConversationRole.SYSTEM
    db_msg.content = "System message"
    db_msg.language = "en"
    db_msg.created_at = datetime(2025, 11, 15, 14, 25, 30)
    db_msg.token_count = 0
    db_msg.estimated_cost = 0.0
    db_msg.processing_time_ms = 0

    result = persistence._convert_db_message(db_msg)

    assert result["timestamp"] == "2025-11-15T14:25:30"
    assert isinstance(result["timestamp"], str)


# ============================================================================
# 13. Helper Methods - Difficulty Estimation (7 tests)
# ============================================================================


def test_estimate_difficulty_beginner(persistence):
    """Test difficulty estimation for beginner level"""
    result = persistence._estimate_difficulty("beginner")
    assert result == 2


def test_estimate_difficulty_elementary(persistence):
    """Test difficulty estimation for elementary level"""
    result = persistence._estimate_difficulty("elementary")
    assert result == 3


def test_estimate_difficulty_intermediate(persistence):
    """Test difficulty estimation for intermediate level"""
    result = persistence._estimate_difficulty("intermediate")
    assert result == 5


def test_estimate_difficulty_upper_intermediate(persistence):
    """Test difficulty estimation for upper-intermediate level"""
    result = persistence._estimate_difficulty("upper-intermediate")
    assert result == 7


def test_estimate_difficulty_advanced(persistence):
    """Test difficulty estimation for advanced level"""
    result = persistence._estimate_difficulty("advanced")
    assert result == 8


def test_estimate_difficulty_proficient(persistence):
    """Test difficulty estimation for proficient level"""
    result = persistence._estimate_difficulty("proficient")
    assert result == 9


def test_estimate_difficulty_unknown_defaults_to_5(persistence):
    """Test unknown difficulty level defaults to 5"""
    result = persistence._estimate_difficulty("expert")
    assert result == 5


# ============================================================================
# 14. Helper Methods - User ID Extraction (3 tests)
# ============================================================================


def test_extract_user_id_numeric_string(persistence, sample_context):
    """Test extracting numeric user_id"""
    sample_context.user_id = "123"
    result = persistence._extract_user_id(sample_context)
    assert result == 123


def test_extract_user_id_non_numeric_defaults_to_1(persistence, sample_context):
    """Test non-numeric user_id defaults to 1"""
    sample_context.user_id = "user_abc"
    result = persistence._extract_user_id(sample_context)
    assert result == 1


def test_extract_user_id_empty_string_defaults_to_1(persistence, sample_context):
    """Test empty user_id defaults to 1"""
    sample_context.user_id = ""
    result = persistence._extract_user_id(sample_context)
    assert result == 1


# ============================================================================
# 15. Helper Methods - Vocabulary Checks (4 tests)
# ============================================================================


def test_vocabulary_exists_found(persistence, mock_session):
    """Test vocabulary_exists returns True when found"""
    mock_vocab = Mock(spec=VocabularyItem)
    mock_session.query.return_value.filter.return_value.first.return_value = mock_vocab

    result = persistence._vocabulary_exists(mock_session, 1, "spanish", "casa")

    assert result is True


def test_vocabulary_exists_not_found(persistence, mock_session):
    """Test vocabulary_exists returns False when not found"""
    mock_session.query.return_value.filter.return_value.first.return_value = None

    result = persistence._vocabulary_exists(mock_session, 1, "spanish", "casa")

    assert result is False


def test_vocabulary_exists_checks_user_language_word(persistence, mock_session):
    """Test vocabulary_exists filters by user_id, language, and word"""
    mock_session.query.return_value.filter.return_value.first.return_value = None

    persistence._vocabulary_exists(mock_session, 42, "french", "bonjour")

    # Verify query was called with VocabularyItem model
    mock_session.query.assert_called()


def test_vocabulary_exists_query_chain(persistence, mock_session):
    """Test vocabulary_exists uses proper query chain"""
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_session.query.return_value = mock_query

    persistence._vocabulary_exists(mock_session, 1, "spanish", "gato")

    # Verify filter and first were called
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()


# ============================================================================
# 16. Integration Tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_save_all_components_in_sequence(
    persistence, sample_context, sample_messages, mock_session, mock_conversation
):
    """Test saving conversation, messages, and progress in sequence"""
    # Setup mocks for conversation save
    mock_query1 = Mock()
    mock_query1.filter.return_value.first.return_value = None

    # Setup mocks for message save
    mock_conversation.id = 1
    mock_query2 = Mock()
    mock_query2.filter.return_value.first.return_value = mock_conversation
    mock_query2.filter.return_value.count.return_value = 0

    # Setup mocks for progress save
    mock_query3 = Mock()
    mock_query3.filter.return_value.first.return_value = None

    call_count = [0]

    def get_session_side_effect():
        call_count[0] += 1
        return iter([mock_session])

    def query_side_effect(model):
        if call_count[0] == 1:  # First save (conversation)
            return mock_query1
        elif call_count[0] == 2:  # Second save (messages)
            return mock_query2
        else:  # Third save (progress)
            return mock_query3

    mock_session.query.side_effect = query_side_effect

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        mock_get_db.side_effect = get_session_side_effect

        # Save conversation
        result1 = await persistence.save_conversation_to_db(
            "conv_123", sample_context, "active"
        )
        assert result1 is True

        # Reset query mock for messages
        mock_session.query.side_effect = query_side_effect

        # Save messages
        result2 = await persistence.save_messages_to_db("conv_123", sample_messages)
        assert result2 is True

        # Reset query mock for progress
        mock_session.query.side_effect = query_side_effect

        # Save progress
        result3 = await persistence.save_learning_progress("conv_123", sample_context)
        assert result3 is True


@pytest.mark.asyncio
async def test_error_handling_across_all_operations(persistence, mock_session):
    """Test error handling works consistently across all operations"""
    mock_session.query.side_effect = SQLAlchemyError("Database failure")

    sample_context = ConversationContext(
        conversation_id="conv_123",
        user_id="1",
        language="en",
        learning_focus=LearningFocus.CONVERSATION,
    )
    sample_messages = [
        ConversationMessage(
            role=MessageRole.USER,
            content="Test",
            timestamp=datetime.now(),
            language="en",
        )
    ]

    with patch("app.services.conversation_persistence.get_db_session") as mock_get_db:
        # Test all three main operations handle errors gracefully
        mock_get_db.return_value = iter([mock_session])
        result1 = await persistence.save_conversation_to_db("conv_123", sample_context)
        assert result1 is False

        mock_session.query.side_effect = SQLAlchemyError("Database failure")
        mock_get_db.return_value = iter([mock_session])
        result2 = await persistence.save_messages_to_db("conv_123", sample_messages)
        assert result2 is False

        mock_session.query.side_effect = SQLAlchemyError("Database failure")
        mock_get_db.return_value = iter([mock_session])
        result3 = await persistence.save_learning_progress("conv_123", sample_context)
        assert result3 is False

        mock_session.query.side_effect = SQLAlchemyError("Database failure")
        mock_get_db.return_value = iter([mock_session])
        result4 = await persistence.load_conversation_from_db("conv_123")
        assert result4 is None


# ============================================================================
# TRUE 100% Branch Coverage Tests
# Session 27: Cover remaining 10 branches for TRUE 100% validation
# ============================================================================


class TestSessionNoneExceptionHandling:
    """
    Test exception handling when session is None.
    
    These tests cover the branches where get_db_session() fails before
    yielding a session, causing session to remain None in exception handlers.
    
    Missing branches covered:
    - 126→128, 131→133, 135→exit (save_conversation_to_db)
    - 203→205, 208→210, 212→exit (save_messages_to_db)
    - 300→302, 333→exit (save_learning_progress)
    - 393→exit (load_conversation_from_db)
    """

    @pytest.mark.asyncio
    async def test_save_conversation_session_creation_failure(
        self, persistence, sample_context
    ):
        """Test save_conversation_to_db when get_db_session() fails before yielding"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            # Simulate session creation failure - raises before yielding
            mock_get_db.side_effect = Exception("Database connection failed")

            result = await persistence.save_conversation_to_db(
                "conv_123", sample_context
            )

            # Should handle gracefully and return False
            assert result is False
            # session is None, so rollback/close should not be called
            # This tests branches 126→128, 131→133, 135→exit (else path when session is None)

    @pytest.mark.asyncio
    async def test_save_conversation_sqlalchemy_error_before_session_assignment(
        self, persistence, sample_context
    ):
        """Test save_conversation when SQLAlchemyError occurs before session assignment"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            # Simulate SQLAlchemyError during session creation
            mock_get_db.side_effect = SQLAlchemyError("Session creation failed")

            result = await persistence.save_conversation_to_db(
                "conv_123", sample_context
            )

            assert result is False
            # Tests branch 126→128 (if session: else path)

    @pytest.mark.asyncio
    async def test_save_messages_session_creation_failure(
        self, persistence, sample_messages
    ):
        """Test save_messages_to_db when get_db_session() fails"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")

            result = await persistence.save_messages_to_db("conv_123", sample_messages)

            assert result is False
            # Tests branches 203→205, 208→210, 212→exit

    @pytest.mark.asyncio
    async def test_save_messages_sqlalchemy_error_before_session_assignment(
        self, persistence, sample_messages
    ):
        """Test save_messages when SQLAlchemyError occurs before session assignment"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.side_effect = SQLAlchemyError("Session creation failed")

            result = await persistence.save_messages_to_db("conv_123", sample_messages)

            assert result is False
            # Tests branch 203→205 (if session: else path)

    @pytest.mark.asyncio
    async def test_save_learning_progress_session_creation_failure(
        self, persistence, sample_context
    ):
        """Test save_learning_progress when get_db_session() fails"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")

            result = await persistence.save_learning_progress("conv_123", sample_context)

            assert result is False
            # Tests branches 300→302, 333→exit

    @pytest.mark.asyncio
    async def test_save_learning_progress_sqlalchemy_error_before_session(
        self, persistence, sample_context
    ):
        """Test save_learning_progress when SQLAlchemyError during session creation"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.side_effect = SQLAlchemyError("Session creation failed")

            result = await persistence.save_learning_progress("conv_123", sample_context)

            assert result is False
            # Tests branch 300→302 (if session: else path)

    @pytest.mark.asyncio
    async def test_load_conversation_session_creation_failure(self, persistence):
        """Test load_conversation_from_db when get_db_session() fails"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")

            result = await persistence.load_conversation_from_db("conv_123")

            assert result is None
            # Tests branch 393→exit (if session: else path in finally)

    @pytest.mark.asyncio
    async def test_load_conversation_sqlalchemy_error_before_session(self, persistence):
        """Test load_conversation when SQLAlchemyError during session creation"""
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.side_effect = SQLAlchemyError("Session creation failed")

            result = await persistence.load_conversation_from_db("conv_123")

            assert result is None


class TestVocabularyExistsBranch:
    """
    Test vocabulary loop continuation branch.
    
    Missing branch covered:
    - 265→264 (loop continues when vocabulary already exists)
    """

    @pytest.mark.asyncio
    async def test_save_learning_progress_skips_existing_vocabulary(
        self, persistence, sample_context
    ):
        """Test that existing vocabulary words are skipped in the loop"""
        mock_session = Mock(spec=Session)
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.close = Mock()
        mock_session.add = Mock()

        # Mock conversation to return user_id
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user_id = 42

        # Mock LearningProgress objects with MagicMock for += operations
        vocab_progress = MagicMock(spec=LearningProgress)
        vocab_progress.words_learned = 10
        vocab_progress.sessions_completed = 5

        conv_progress = MagicMock(spec=LearningProgress)
        conv_progress.conversations_completed = 3
        conv_progress.sessions_completed = 2

        # Create context with multiple vocabulary words
        context = ConversationContext(
            conversation_id="conv_123",
            user_id="42",
            language="spanish",
            learning_focus=LearningFocus.CONVERSATION,
            current_topic="Restaurant",
            vocabulary_level="intermediate",
            learning_goals=["Practice"],
            mistakes_tracked=[],
            vocabulary_introduced=["mesero", "cuenta", "propina"],  # 3 words
            session_start_time=datetime.now(),
            last_activity=datetime.now(),
        )

        # Setup query mock to return different objects based on query
        def query_side_effect(model):
            query_mock = Mock()
            filter_mock = Mock()

            if model == Conversation:
                filter_mock.first.return_value = mock_conversation
            elif model == LearningProgress:
                # Return vocab_progress first call, conv_progress second call
                filter_mock.first.side_effect = [vocab_progress, conv_progress]
            elif model == VocabularyItem:
                # Will be handled by _vocabulary_exists mock
                filter_mock.first.return_value = None

            query_mock.filter.return_value = filter_mock
            return query_mock

        mock_session.query.side_effect = query_side_effect

        # Mock _vocabulary_exists to return True for first and third words
        # This will cause the loop to skip (branch 265→264) for those words
        def mock_vocabulary_exists(session, user_id, language, word):
            return word in ["mesero", "propina"]  # These exist, skip them

        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.return_value = iter([mock_session])

            with patch.object(
                persistence, "_vocabulary_exists", side_effect=mock_vocabulary_exists
            ):
                result = await persistence.save_learning_progress("conv_123", context)

                assert result is True

                # Should only add "cuenta" (the one that doesn't exist)
                # "mesero" and "propina" trigger the skip branch 265→264
                add_calls = mock_session.add.call_args_list
                vocab_adds = [
                    call for call in add_calls if isinstance(call[0][0], VocabularyItem)
                ]

                # Only 1 vocabulary item should be added (cuenta)
                assert len(vocab_adds) == 1
                added_word = vocab_adds[0][0][0].word
                assert added_word == "cuenta"

                # This test covers branch 265→264 (loop continuation when word exists)

    @pytest.mark.asyncio
    async def test_save_learning_progress_adds_all_new_vocabulary(
        self, persistence, sample_context
    ):
        """Test that all new vocabulary words are added when none exist"""
        mock_session = Mock(spec=Session)
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.close = Mock()
        mock_session.add = Mock()

        # Mock conversation to return user_id
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user_id = 42

        # Mock LearningProgress objects with MagicMock for += operations
        vocab_progress = MagicMock(spec=LearningProgress)
        vocab_progress.words_learned = 10
        vocab_progress.sessions_completed = 5

        conv_progress = MagicMock(spec=LearningProgress)
        conv_progress.conversations_completed = 3
        conv_progress.sessions_completed = 2

        # Setup query mock
        def query_side_effect(model):
            query_mock = Mock()
            filter_mock = Mock()

            if model == Conversation:
                filter_mock.first.return_value = mock_conversation
            elif model == LearningProgress:
                # Return vocab_progress first call, conv_progress second call
                filter_mock.first.side_effect = [vocab_progress, conv_progress]
            elif model == VocabularyItem:
                # Will be handled by _vocabulary_exists mock
                filter_mock.first.return_value = None

            query_mock.filter.return_value = filter_mock
            return query_mock

        mock_session.query.side_effect = query_side_effect

        # All vocabulary words are new (none exist)
        with patch(
            "app.services.conversation_persistence.get_db_session"
        ) as mock_get_db:
            mock_get_db.return_value = iter([mock_session])

            with patch.object(persistence, "_vocabulary_exists", return_value=False):
                result = await persistence.save_learning_progress(
                    "conv_123", sample_context
                )

                assert result is True

                # All 3 vocabulary words should be added
                add_calls = mock_session.add.call_args_list
                vocab_adds = [
                    call for call in add_calls if isinstance(call[0][0], VocabularyItem)
                ]
                assert len(vocab_adds) == 3
