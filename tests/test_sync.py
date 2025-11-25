"""
Comprehensive tests for app/services/sync.py

Tests for data synchronization service including:
- Enums and dataclasses
- DataSyncService initialization
- User data synchronization
- Individual sync methods (profiles, conversations, learning progress, vocabulary, documents)
- Conflict resolution
- Background sync
- Status monitoring
- Convenience functions

Target: TRUE 100% coverage (267 statements, 78 branches)
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest
from sqlalchemy.orm import Session

from app.models.database import Conversation, ConversationMessage, Document, User
from app.services.sync import (
    ConflictResolution,
    DataSyncService,
    SyncDirection,
    SyncItem,
    SyncResult,
    SyncStatus,
    get_sync_status,
    start_background_sync,
    sync_service,
    sync_user_data,
)

# ============================================================================
# Test Enums
# ============================================================================


class TestSyncEnums:
    """Test sync-related enums"""

    def test_sync_direction_values(self):
        """Test SyncDirection enum values"""
        assert SyncDirection.UP.value == "up"
        assert SyncDirection.DOWN.value == "down"
        assert SyncDirection.BIDIRECTIONAL.value == "bidirectional"

    def test_sync_status_values(self):
        """Test SyncStatus enum values"""
        assert SyncStatus.PENDING.value == "pending"
        assert SyncStatus.IN_PROGRESS.value == "in_progress"
        assert SyncStatus.COMPLETED.value == "completed"
        assert SyncStatus.FAILED.value == "failed"
        assert SyncStatus.CONFLICT.value == "conflict"

    def test_conflict_resolution_values(self):
        """Test ConflictResolution enum values"""
        assert ConflictResolution.SERVER_WINS.value == "server_wins"
        assert ConflictResolution.LOCAL_WINS.value == "local_wins"
        assert ConflictResolution.LATEST_TIMESTAMP.value == "latest_timestamp"
        assert ConflictResolution.MANUAL_REVIEW.value == "manual_review"


# ============================================================================
# Test Dataclasses
# ============================================================================


class TestSyncDataclasses:
    """Test sync dataclasses"""

    def test_sync_item_creation(self):
        """Test SyncItem dataclass creation"""
        timestamp = datetime.now()
        item = SyncItem(
            table_name="users",
            record_id="user123",
            action="insert",
            data={"name": "Test"},
            timestamp=timestamp,
            user_id="user123",
            priority=1,
        )

        assert item.table_name == "users"
        assert item.record_id == "user123"
        assert item.action == "insert"
        assert item.data == {"name": "Test"}
        assert item.timestamp == timestamp
        assert item.user_id == "user123"
        assert item.priority == 1

    def test_sync_item_default_priority(self):
        """Test SyncItem default priority is 1"""
        timestamp = datetime.now()
        item = SyncItem(
            table_name="users",
            record_id="user123",
            action="insert",
            data={},
            timestamp=timestamp,
            user_id="user123",
        )
        assert item.priority == 1

    def test_sync_result_creation(self):
        """Test SyncResult dataclass creation"""
        timestamp = datetime.now()
        result = SyncResult(
            success=True,
            items_processed=10,
            items_success=9,
            items_failed=1,
            conflicts=[{"type": "conflict1"}],
            errors=["error1"],
            sync_duration=2.5,
            timestamp=timestamp,
        )

        assert result.success is True
        assert result.items_processed == 10
        assert result.items_success == 9
        assert result.items_failed == 1
        assert result.conflicts == [{"type": "conflict1"}]
        assert result.errors == ["error1"]
        assert result.sync_duration == 2.5
        assert result.timestamp == timestamp


# ============================================================================
# Test DataSyncService Initialization
# ============================================================================


class TestDataSyncServiceInitialization:
    """Test DataSyncService initialization"""

    def test_service_initialization(self):
        """Test service initializes with correct attributes"""
        service = DataSyncService()

        assert service.db_manager is not None
        assert service.local_db_manager is not None
        assert service.chroma_manager is not None
        assert service.sync_queue == []
        assert service.conflict_resolution == ConflictResolution.LATEST_TIMESTAMP
        assert service.last_sync_times == {}
        assert service.is_syncing is False


# ============================================================================
# Test Main Sync Orchestrator
# ============================================================================


class TestSyncUserData:
    """Test main user data synchronization"""

    @pytest.mark.asyncio
    async def test_sync_user_data_success_all_tasks(self):
        """Test successful sync with all tasks completing"""
        service = DataSyncService()

        # Mock all sync functions to return success
        mock_result = SyncResult(
            success=True,
            items_processed=2,
            items_success=2,
            items_failed=0,
            conflicts=[],
            errors=[],
            sync_duration=0.5,
            timestamp=datetime.now(),
        )

        with (
            patch.object(service, "_sync_user_profiles", return_value=mock_result),
            patch.object(service, "_sync_conversations", return_value=mock_result),
            patch.object(service, "_sync_learning_progress", return_value=mock_result),
            patch.object(service, "_sync_vocabulary", return_value=mock_result),
            patch.object(service, "_sync_documents", return_value=mock_result),
        ):
            result = await service.sync_user_data(
                "user123", SyncDirection.BIDIRECTIONAL
            )

            assert result.success is True
            assert result.items_processed == 10  # 2 items × 5 tasks
            assert result.items_success == 10
            assert result.items_failed == 0
            assert result.errors == []
            assert result.conflicts == []
            assert service.last_sync_times.get("user123") is not None
            assert service.is_syncing is False

    @pytest.mark.asyncio
    async def test_sync_user_data_with_task_failure(self):
        """Test sync when one task fails"""
        service = DataSyncService()

        success_result = SyncResult(True, 2, 2, 0, [], [], 0.5, datetime.now())

        # Mock one task to raise exception
        with (
            patch.object(service, "_sync_user_profiles", return_value=success_result),
            patch.object(
                service, "_sync_conversations", side_effect=Exception("Sync error")
            ),
            patch.object(
                service, "_sync_learning_progress", return_value=success_result
            ),
            patch.object(service, "_sync_vocabulary", return_value=success_result),
            patch.object(service, "_sync_documents", return_value=success_result),
        ):
            result = await service.sync_user_data("user123")

            assert result.success is False  # One task failed
            assert result.items_processed == 8  # 4 successful tasks × 2 items
            assert result.items_success == 8
            assert result.items_failed == 0
            assert len(result.errors) == 1
            assert "conversations" in result.errors[0]
            assert service.is_syncing is False

    @pytest.mark.asyncio
    async def test_sync_user_data_complete_failure(self):
        """Test sync when main orchestrator fails"""
        service = DataSyncService()

        # Mock all sync methods - first one fails, rest should still be called
        mock_result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        with (
            patch.object(
                service, "_sync_user_profiles", side_effect=Exception("Critical error")
            ),
            patch.object(service, "_sync_conversations", return_value=mock_result),
            patch.object(service, "_sync_learning_progress", return_value=mock_result),
            patch.object(service, "_sync_vocabulary", return_value=mock_result),
            patch.object(service, "_sync_documents", return_value=mock_result),
        ):
            result = await service.sync_user_data("user123")

            assert result.success is False
            assert result.items_processed == 0
            assert result.items_success == 0
            assert result.items_failed == 0
            assert len(result.errors) == 1
            assert "user_profiles" in result.errors[0]
            assert service.is_syncing is False

    @pytest.mark.asyncio
    async def test_sync_user_data_sets_is_syncing_flag(self):
        """Test that is_syncing flag is properly managed"""
        service = DataSyncService()
        mock_result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        async def check_syncing_flag(*args):
            assert service.is_syncing is True
            return mock_result

        with (
            patch.object(
                service, "_sync_user_profiles", side_effect=check_syncing_flag
            ),
            patch.object(service, "_sync_conversations", return_value=mock_result),
            patch.object(service, "_sync_learning_progress", return_value=mock_result),
            patch.object(service, "_sync_vocabulary", return_value=mock_result),
            patch.object(service, "_sync_documents", return_value=mock_result),
        ):
            result = await service.sync_user_data("user123")
        assert service.is_syncing is False

    @pytest.mark.asyncio
    async def test_sync_user_data_different_directions(self):
        """Test sync with different sync directions"""
        service = DataSyncService()
        mock_result = SyncResult(True, 1, 1, 0, [], [], 0.0, datetime.now())

        with (
            patch.object(service, "_sync_user_profiles", return_value=mock_result),
            patch.object(service, "_sync_conversations", return_value=mock_result),
            patch.object(service, "_sync_learning_progress", return_value=mock_result),
            patch.object(service, "_sync_vocabulary", return_value=mock_result),
            patch.object(service, "_sync_documents", return_value=mock_result),
        ):
            # Test UP direction
            result_up = await service.sync_user_data("user123", SyncDirection.UP)
            assert result_up.success is True

            # Test DOWN direction
            result_down = await service.sync_user_data("user123", SyncDirection.DOWN)
            assert result_down.success is True

            # Test BIDIRECTIONAL direction
            result_bi = await service.sync_user_data(
                "user123", SyncDirection.BIDIRECTIONAL
            )
            assert result_bi.success is True

    @pytest.mark.asyncio
    async def test_sync_user_data_outer_exception_handler(self):
        """Test outer exception handler in sync_user_data (lines 174-176)"""
        service = DataSyncService()

        # Mock SyncResult to raise exception on FIRST call, then work normally
        # This tests the outer try/except block (lines 174-176)
        from app.services.sync import SyncResult as RealSyncResult

        with patch("app.services.sync.SyncResult") as mock_sync_result:
            # First call raises exception, second call returns real object
            mock_sync_result.side_effect = [
                Exception("SyncResult initialization failed"),
                RealSyncResult(
                    False,
                    0,
                    0,
                    0,
                    [],
                    ["SyncResult initialization failed"],
                    0.0,
                    datetime.now(),
                ),
            ]

            result = await service.sync_user_data("user123")

            # Outer exception handler should catch and return error result
            assert result.success is False
            assert result.items_processed == 0
            assert result.items_success == 0
            assert result.items_failed == 0
            assert len(result.errors) == 1
            assert "SyncResult initialization failed" in result.errors[0]
            # Finally block should still execute
            assert service.is_syncing is False


# ============================================================================
# Test User Profile Sync
# ============================================================================


class TestSyncUserProfiles:
    """Test user profile synchronization"""

    def setup_method(self):
        """Setup method to add missing database methods to mocks"""
        # This will be called before each test method
        pass

    @pytest.mark.asyncio
    async def test_sync_user_profiles_down_with_user(self):
        """Test downloading user profile from server to local"""
        service = DataSyncService()

        # Mock server user
        mock_user = Mock(spec=User)
        mock_user.user_id = "user123"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.preferences = {"language": "en"}

        # Mock session and query
        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_user

        # Mock context manager
        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        # Add the method to the mock db_manager
        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)

        with patch.object(
            service.local_db_manager, "add_user_profile", return_value=True
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.DOWN)

            assert result.success is True
            assert result.items_processed == 1
            assert result.items_success == 1
            assert result.items_failed == 0

    @pytest.mark.asyncio
    async def test_sync_user_profiles_down_no_user(self):
        """Test downloading when user doesn't exist on server"""
        service = DataSyncService()

        # Mock session to return None (no user found)
        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_user_profiles("user123", SyncDirection.DOWN)

        assert result.success is True
        assert result.items_processed == 0
        assert result.items_success == 0
        assert result.items_failed == 0

    @pytest.mark.asyncio
    async def test_sync_user_profiles_down_save_failure(self):
        """Test when saving profile locally fails"""
        service = DataSyncService()

        mock_user = Mock(spec=User)
        mock_user.user_id = "user123"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.preferences = {}

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "add_user_profile", return_value=False
            ),
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.DOWN)

            assert result.success is True
            assert result.items_processed == 1
            assert result.items_success == 0
            assert result.items_failed == 1
            assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_sync_user_profiles_up_local_newer(self):
        """Test uploading when local profile is newer than server"""
        service = DataSyncService()

        local_profile = {
            "user_id": "user123",
            "preferences": {"language": "es"},
            "updated_at": "2025-01-25T12:00:00",
        }

        mock_server_user = Mock(spec=User)
        mock_server_user.user_id = "user123"
        mock_server_user.updated_at = datetime(2025, 1, 24, 12, 0, 0)
        mock_server_user.preferences = {"language": "en"}

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_server_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "get_user_profile", return_value=local_profile
            ),
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.UP)

            assert result.success is True
            assert result.items_processed == 1
            assert result.items_success == 1
            assert mock_server_user.preferences == {"language": "es"}

    @pytest.mark.asyncio
    async def test_sync_user_profiles_up_server_newer(self):
        """Test uploading when server profile is newer than local"""
        service = DataSyncService()

        local_profile = {
            "user_id": "user123",
            "preferences": {"language": "es"},
            "updated_at": "2025-01-24T12:00:00",
        }

        mock_server_user = Mock(spec=User)
        mock_server_user.user_id = "user123"
        mock_server_user.username = "testuser"
        mock_server_user.email = "test@example.com"
        mock_server_user.updated_at = datetime(2025, 1, 25, 12, 0, 0)
        mock_server_user.preferences = {"language": "en"}

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_server_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "get_user_profile", return_value=local_profile
            ),
            patch.object(
                service.local_db_manager, "add_user_profile", return_value=True
            ),
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.UP)

            assert result.success is True
            assert result.items_processed == 1
            assert result.items_success == 1

    @pytest.mark.asyncio
    async def test_sync_user_profiles_up_no_local_profile(self):
        """Test uploading when no local profile exists"""
        service = DataSyncService()

        with patch.object(
            service.local_db_manager, "get_user_profile", return_value=None
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.UP)

            assert result.success is True
            assert result.items_processed == 0
            assert result.items_success == 0

    @pytest.mark.asyncio
    async def test_sync_user_profiles_bidirectional(self):
        """Test bidirectional sync"""
        service = DataSyncService()

        # Mock for DOWN direction
        mock_user = Mock(spec=User)
        mock_user.user_id = "user123"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.preferences = {}

        # Mock for UP direction
        local_profile = None

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "add_user_profile", return_value=True
            ),
            patch.object(
                service.local_db_manager, "get_user_profile", return_value=local_profile
            ),
        ):
            result = await service._sync_user_profiles(
                "user123", SyncDirection.BIDIRECTIONAL
            )

            assert result.success is True
            assert result.items_processed == 1  # Only DOWN portion executed

    @pytest.mark.asyncio
    async def test_sync_user_profiles_exception(self):
        """Test exception handling in user profile sync"""
        service = DataSyncService()

        with patch.object(
            service.db_manager,
            "mariadb_session_scope",
            side_effect=Exception("DB error"),
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.DOWN)

            assert result.success is False
            assert len(result.errors) == 1
            assert "DB error" in result.errors[0]

    @pytest.mark.asyncio
    async def test_sync_user_profiles_up_no_server_user(self):
        """Test uploading when server user doesn't exist (branch 223->219)"""
        service = DataSyncService()

        local_profile = {
            "user_id": "user123",
            "preferences": {"language": "es"},
            "updated_at": "2025-01-25T12:00:00",
        }

        # Mock session to return None (no server user found)
        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "get_user_profile", return_value=local_profile
            ),
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.UP)

            # Should succeed but nothing synced (no server user to update)
            assert result.success is True
            assert result.items_processed == 0
            assert result.items_success == 0

    @pytest.mark.asyncio
    async def test_sync_user_profiles_up_equal_timestamps(self):
        """Test uploading when timestamps are equal (branch 238->219)"""
        service = DataSyncService()

        equal_time = datetime(2025, 1, 25, 12, 0, 0)
        local_profile = {
            "user_id": "user123",
            "preferences": {"language": "es"},
            "updated_at": equal_time.isoformat(),
        }

        mock_server_user = Mock(spec=User)
        mock_server_user.user_id = "user123"
        mock_server_user.username = "testuser"
        mock_server_user.email = "test@example.com"
        mock_server_user.updated_at = equal_time
        mock_server_user.preferences = {"language": "en"}

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_server_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "get_user_profile", return_value=local_profile
            ),
        ):
            result = await service._sync_user_profiles("user123", SyncDirection.UP)

            # Should succeed but nothing synced (timestamps equal, no conflict)
            assert result.success is True
            assert result.items_processed == 0
            assert result.items_success == 0
            # Preferences should remain unchanged
            assert mock_server_user.preferences == {"language": "en"}


# ============================================================================
# Test Conversation Sync
# ============================================================================


class TestSyncConversations:
    """Test conversation synchronization"""

    @pytest.mark.asyncio
    async def test_sync_conversations_down(self):
        """Test downloading conversations from server"""
        service = DataSyncService()

        with (
            patch.object(service, "_get_last_sync_time", return_value=datetime.min),
            patch.object(
                service, "_download_conversations_from_server"
            ) as mock_download,
        ):
            result = await service._sync_conversations("user123", SyncDirection.DOWN)

            assert result.success is True
            mock_download.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_conversations_up(self):
        """Test uploading conversations to server"""
        service = DataSyncService()

        with (
            patch.object(service, "_get_last_sync_time", return_value=datetime.min),
            patch.object(service, "_upload_conversations_to_server") as mock_upload,
        ):
            result = await service._sync_conversations("user123", SyncDirection.UP)

            assert result.success is True
            mock_upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_conversations_bidirectional(self):
        """Test bidirectional conversation sync"""
        service = DataSyncService()

        with (
            patch.object(service, "_get_last_sync_time", return_value=datetime.min),
            patch.object(
                service, "_download_conversations_from_server"
            ) as mock_download,
            patch.object(service, "_upload_conversations_to_server") as mock_upload,
        ):
            result = await service._sync_conversations(
                "user123", SyncDirection.BIDIRECTIONAL
            )

            assert result.success is True
            mock_download.assert_called_once()
            mock_upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_conversations_exception(self):
        """Test exception handling in conversation sync"""
        service = DataSyncService()

        with patch.object(
            service, "_get_last_sync_time", side_effect=Exception("Sync error")
        ):
            result = await service._sync_conversations("user123", SyncDirection.DOWN)

            assert result.success is False
            assert len(result.errors) == 1


# ============================================================================
# Test Conversation Sync Helper Methods
# ============================================================================


class TestConversationSyncHelpers:
    """Test conversation sync helper methods"""

    def test_get_last_sync_time_exists(self):
        """Test getting last sync time when it exists"""
        service = DataSyncService()
        test_time = datetime(2025, 1, 25, 12, 0, 0)
        service.last_sync_times["user123_conversations"] = test_time

        result = service._get_last_sync_time("user123", "conversations")
        assert result == test_time

    def test_get_last_sync_time_not_exists(self):
        """Test getting last sync time when it doesn't exist"""
        service = DataSyncService()
        result = service._get_last_sync_time("user123", "conversations")
        assert result == datetime.min

    def test_download_conversations_from_server(self):
        """Test downloading conversations from server"""
        service = DataSyncService()
        last_sync = datetime.min
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_conv = Mock(spec=Conversation)
        mock_conv.id = 1
        mock_conv.conversation_id = "conv123"

        mock_session = MagicMock(spec=Session)
        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service, "_fetch_server_conversations", return_value=[mock_conv]
            ),
            patch.object(service, "_fetch_conversation_messages", return_value=[]),
            patch.object(service, "_save_messages_locally"),
        ):
            service._download_conversations_from_server("user123", last_sync, result)

    def test_fetch_server_conversations(self):
        """Test fetching conversations from server"""
        service = DataSyncService()
        last_sync = datetime.min

        mock_user_id = 1
        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = []

        # Mock the scalar query for user ID
        mock_scalar_query = mock_session.query.return_value.filter.return_value
        mock_scalar_query.scalar.return_value = mock_user_id

        conversations = service._fetch_server_conversations(
            mock_session, "user123", last_sync
        )
        assert conversations == []

    def test_fetch_conversation_messages(self):
        """Test fetching messages for a conversation"""
        service = DataSyncService()

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = []

        messages = service._fetch_conversation_messages(mock_session, 1)
        assert messages == []

    def test_save_messages_locally_success(self):
        """Test saving messages locally successfully"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_conv = Mock()
        mock_conv.conversation_id = "conv123"

        mock_msg = Mock()
        mock_msg.role = Mock(value="user")
        mock_msg.content = "Hello"
        mock_msg.language = "en"
        mock_msg.created_at = datetime.now()
        mock_msg.token_count = 5
        mock_msg.pronunciation_score = 0.95

        with patch.object(
            service.local_db_manager, "save_conversation_locally", return_value=True
        ):
            service._save_messages_locally("user123", mock_conv, [mock_msg], result)

            assert result.items_processed == 1
            assert result.items_success == 1
            assert result.items_failed == 0

    def test_save_messages_locally_failure(self):
        """Test saving messages locally with failure"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_conv = Mock()
        mock_conv.conversation_id = "conv123"

        mock_msg = Mock()
        mock_msg.role = Mock(value="user")
        mock_msg.content = "Hello"
        mock_msg.language = "en"
        mock_msg.created_at = datetime.now()
        mock_msg.token_count = 5
        mock_msg.pronunciation_score = 0.95

        with patch.object(
            service.local_db_manager, "save_conversation_locally", return_value=False
        ):
            service._save_messages_locally("user123", mock_conv, [mock_msg], result)

            assert result.items_processed == 1
            assert result.items_success == 0
            assert result.items_failed == 1

    def test_upload_conversations_to_server_no_user(self):
        """Test uploading when user doesn't exist on server"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None  # No user found

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager, "get_recent_conversations", return_value=[]
            ),
        ):
            service._upload_conversations_to_server("user123", result)

            assert len(result.errors) == 1
            assert "not found" in result.errors[0]

    def test_upload_conversations_to_server_with_user(self):
        """Test uploading conversations when user exists"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_user = Mock(spec=User)
        mock_user.user_id = "user123"

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        recent_conversations = [
            {
                "conversation_id": "conv1",
                "content": "msg1",
                "timestamp": datetime.now().isoformat(),
            }
        ]

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.local_db_manager,
                "get_recent_conversations",
                return_value=recent_conversations,
            ),
            patch.object(service, "_group_messages_by_conversation", return_value={}),
            patch.object(service, "_sync_conversations_to_server"),
        ):
            service._upload_conversations_to_server("user123", result)

    def test_group_messages_by_conversation(self):
        """Test grouping messages by conversation ID"""
        service = DataSyncService()

        messages = [
            {"conversation_id": "conv1", "content": "msg1"},
            {"conversation_id": "conv1", "content": "msg2"},
            {"conversation_id": "conv2", "content": "msg3"},
        ]

        grouped = service._group_messages_by_conversation(messages)

        assert "conv1" in grouped
        assert "conv2" in grouped
        assert len(grouped["conv1"]) == 2
        assert len(grouped["conv2"]) == 1

    def test_sync_conversations_to_server(self):
        """Test syncing conversations to server"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_session = MagicMock(spec=Session)
        mock_user = Mock(spec=User)

        mock_conv = Mock(spec=Conversation)
        mock_conv.id = 1

        conversations_to_sync = {
            "conv1": [
                {
                    "content": "msg1",
                    "timestamp": datetime.now().isoformat(),
                    "language": "en",
                }
            ]
        }

        with (
            patch.object(
                service, "_get_or_create_server_conversation", return_value=mock_conv
            ),
            patch.object(service, "_sync_messages_to_server"),
        ):
            service._sync_conversations_to_server(
                mock_session, mock_user, conversations_to_sync, result
            )

    def test_get_or_create_server_conversation_exists(self):
        """Test getting existing conversation from server"""
        service = DataSyncService()

        mock_conv = Mock(spec=Conversation)
        mock_conv.conversation_id = "conv123"

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_conv

        mock_user = Mock()
        messages = [
            {
                "content": "msg1",
                "timestamp": datetime.now().isoformat(),
                "language": "en",
            }
        ]

        result = service._get_or_create_server_conversation(
            mock_session, mock_user, "conv123", messages
        )

        assert result == mock_conv

    def test_get_or_create_server_conversation_create_new(self):
        """Test creating new conversation on server"""
        service = DataSyncService()

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None  # Conversation doesn't exist

        mock_user = Mock()
        mock_user.id = 1

        timestamp = datetime.now().isoformat()
        messages = [
            {"content": "msg1", "timestamp": timestamp, "language": "en"},
            {"content": "msg2", "timestamp": timestamp, "language": "en"},
        ]

        result = service._get_or_create_server_conversation(
            mock_session, mock_user, "conv123", messages
        )

        # Verify conversation was created
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    def test_sync_messages_to_server_new_message(self):
        """Test syncing new message to server"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_session = MagicMock(spec=Session)
        mock_conv = Mock()
        mock_conv.id = 1

        timestamp = datetime.now().isoformat()
        messages = [
            {
                "message_type": "user",
                "content": "Hello",
                "language": "en",
                "timestamp": timestamp,
            }
        ]

        with patch.object(service, "_message_exists_on_server", return_value=False):
            service._sync_messages_to_server(mock_session, mock_conv, messages, result)

            assert result.items_processed == 1
            assert result.items_success == 1
            mock_session.add.assert_called_once()

    def test_sync_messages_to_server_existing_message(self):
        """Test syncing when message already exists on server"""
        service = DataSyncService()
        result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        mock_session = MagicMock(spec=Session)
        mock_conv = Mock()
        mock_conv.id = 1

        timestamp = datetime.now().isoformat()
        messages = [
            {
                "message_type": "user",
                "content": "Hello",
                "language": "en",
                "timestamp": timestamp,
            }
        ]

        with patch.object(service, "_message_exists_on_server", return_value=True):
            service._sync_messages_to_server(mock_session, mock_conv, messages, result)

            assert result.items_processed == 0
            assert result.items_success == 0
            mock_session.add.assert_not_called()

    def test_message_exists_on_server_true(self):
        """Test checking if message exists on server - exists"""
        service = DataSyncService()

        mock_msg = Mock(spec=ConversationMessage)
        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_msg

        msg = {"content": "Hello", "timestamp": datetime.now().isoformat()}

        result = service._message_exists_on_server(mock_session, 1, msg)
        assert result is True

    def test_message_exists_on_server_false(self):
        """Test checking if message exists on server - doesn't exist"""
        service = DataSyncService()

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        msg = {"content": "Hello", "timestamp": datetime.now().isoformat()}

        result = service._message_exists_on_server(mock_session, 1, msg)
        assert result is False


# ============================================================================
# Test Learning Progress Sync
# ============================================================================


class TestSyncLearningProgress:
    """Test learning progress synchronization"""

    @pytest.mark.asyncio
    async def test_sync_learning_progress_up_with_user(self):
        """Test uploading learning progress when user exists"""
        service = DataSyncService()

        mock_user = Mock(spec=User)
        mock_user.user_id = "user123"

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_learning_progress("user123", SyncDirection.UP)

        assert result.success is True
        assert result.items_processed == 1
        assert result.items_success == 1

    @pytest.mark.asyncio
    async def test_sync_learning_progress_up_no_user(self):
        """Test uploading learning progress when user doesn't exist"""
        service = DataSyncService()

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_learning_progress("user123", SyncDirection.UP)

        assert result.success is True
        assert result.items_processed == 0
        assert result.items_success == 0

    @pytest.mark.asyncio
    async def test_sync_learning_progress_bidirectional(self):
        """Test bidirectional learning progress sync"""
        service = DataSyncService()

        mock_user = Mock(spec=User)

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_user

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_learning_progress(
            "user123", SyncDirection.BIDIRECTIONAL
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_sync_learning_progress_down(self):
        """Test downloading learning progress (not implemented)"""
        service = DataSyncService()

        result = await service._sync_learning_progress("user123", SyncDirection.DOWN)

        assert result.success is True
        assert result.items_processed == 0  # Not implemented yet

    @pytest.mark.asyncio
    async def test_sync_learning_progress_exception(self):
        """Test exception handling in learning progress sync"""
        service = DataSyncService()

        with patch.object(
            service.db_manager,
            "mariadb_session_scope",
            side_effect=Exception("DB error"),
        ):
            result = await service._sync_learning_progress("user123", SyncDirection.UP)

            assert result.success is False
            assert len(result.errors) == 1


# ============================================================================
# Test Vocabulary Sync
# ============================================================================


class TestSyncVocabulary:
    """Test vocabulary synchronization"""

    @pytest.mark.asyncio
    async def test_sync_vocabulary_all_directions(self):
        """Test vocabulary sync (currently returns empty result)"""
        service = DataSyncService()

        result_up = await service._sync_vocabulary("user123", SyncDirection.UP)
        assert result_up.success is True
        assert result_up.items_processed == 0

        result_down = await service._sync_vocabulary("user123", SyncDirection.DOWN)
        assert result_down.success is True
        assert result_down.items_processed == 0

        result_bi = await service._sync_vocabulary(
            "user123", SyncDirection.BIDIRECTIONAL
        )
        assert result_bi.success is True
        assert result_bi.items_processed == 0


# ============================================================================
# Test Document Sync
# ============================================================================


class TestSyncDocuments:
    """Test document and embedding synchronization"""

    @pytest.mark.asyncio
    async def test_sync_documents_down_with_documents(self):
        """Test downloading documents and syncing to ChromaDB"""
        service = DataSyncService()

        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.user_id = "user123"

        mock_doc = Mock(spec=Document)
        mock_doc.document_id = "doc123"
        mock_doc.is_processed = True
        mock_doc.processed_content = "Document content"
        mock_doc.filename = "test.txt"
        mock_doc.language = "en"
        mock_doc.document_type = Mock(value="text")
        mock_doc.uploaded_at = datetime.now()

        mock_session = MagicMock(spec=Session)
        mock_user_query = mock_session.query.return_value
        mock_user_filter = mock_user_query.filter.return_value
        mock_user_filter.first.return_value = mock_user

        # Mock document query
        def query_side_effect(model):
            if model == User:
                return mock_user_query
            elif model == Document:
                mock_doc_query = Mock()
                mock_doc_filter = mock_doc_query.filter.return_value
                mock_doc_filter.all.return_value = [mock_doc]
                return mock_doc_query

        mock_session.query.side_effect = query_side_effect

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(service.chroma_manager, "add_document_embedding"),
        ):
            result = await service._sync_documents("user123", SyncDirection.DOWN)

            assert result.success is True
            assert result.items_processed == 1
            assert result.items_success == 1

    @pytest.mark.asyncio
    async def test_sync_documents_down_no_user(self):
        """Test downloading documents when user doesn't exist"""
        service = DataSyncService()

        mock_session = MagicMock(spec=Session)
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_documents("user123", SyncDirection.DOWN)

        assert result.success is True
        assert result.items_processed == 0

    @pytest.mark.asyncio
    async def test_sync_documents_down_unprocessed_document(self):
        """Test downloading documents that aren't processed yet"""
        service = DataSyncService()

        mock_user = Mock(spec=User)
        mock_user.id = 1

        mock_doc = Mock(spec=Document)
        mock_doc.is_processed = False  # Not processed

        mock_session = MagicMock(spec=Session)

        def query_side_effect(model):
            if model == User:
                mock_user_query = Mock()
                mock_user_filter = mock_user_query.filter.return_value
                mock_user_filter.first.return_value = mock_user
                return mock_user_query
            elif model == Document:
                mock_doc_query = Mock()
                mock_doc_filter = mock_doc_query.filter.return_value
                mock_doc_filter.all.return_value = [mock_doc]
                return mock_doc_query

        mock_session.query.side_effect = query_side_effect

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_documents("user123", SyncDirection.DOWN)

        assert result.success is True
        assert result.items_processed == 0  # Skipped unprocessed document

    @pytest.mark.asyncio
    async def test_sync_documents_down_no_processed_content(self):
        """Test downloading documents without processed content"""
        service = DataSyncService()

        mock_user = Mock(spec=User)
        mock_user.id = 1

        mock_doc = Mock(spec=Document)
        mock_doc.is_processed = True
        mock_doc.processed_content = None  # No content

        mock_session = MagicMock(spec=Session)

        def query_side_effect(model):
            if model == User:
                mock_user_query = Mock()
                mock_user_filter = mock_user_query.filter.return_value
                mock_user_filter.first.return_value = mock_user
                return mock_user_query
            elif model == Document:
                mock_doc_query = Mock()
                mock_doc_filter = mock_doc_query.filter.return_value
                mock_doc_filter.all.return_value = [mock_doc]
                return mock_doc_query

        mock_session.query.side_effect = query_side_effect

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        service.db_manager.mariadb_session_scope = Mock(return_value=mock_session_scope)
        result = await service._sync_documents("user123", SyncDirection.DOWN)

        assert result.success is True
        assert result.items_processed == 0

    @pytest.mark.asyncio
    async def test_sync_documents_embedding_failure(self):
        """Test when adding document embedding fails"""
        service = DataSyncService()

        mock_user = Mock(spec=User)
        mock_user.id = 1

        mock_doc = Mock(spec=Document)
        mock_doc.document_id = "doc123"
        mock_doc.is_processed = True
        mock_doc.processed_content = "Content"
        mock_doc.filename = "test.txt"
        mock_doc.language = "en"
        mock_doc.document_type = Mock(value="text")
        mock_doc.uploaded_at = datetime.now()

        mock_session = MagicMock(spec=Session)

        def query_side_effect(model):
            if model == User:
                mock_user_query = Mock()
                mock_user_filter = mock_user_query.filter.return_value
                mock_user_filter.first.return_value = mock_user
                return mock_user_query
            elif model == Document:
                mock_doc_query = Mock()
                mock_doc_filter = mock_doc_query.filter.return_value
                mock_doc_filter.all.return_value = [mock_doc]
                return mock_doc_query

        mock_session.query.side_effect = query_side_effect

        mock_session_scope = MagicMock()
        mock_session_scope.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.__exit__ = Mock(return_value=False)

        with (
            patch.object(
                service.db_manager,
                "mariadb_session_scope",
                return_value=mock_session_scope,
            ),
            patch.object(
                service.chroma_manager,
                "add_document_embedding",
                side_effect=Exception("Embedding error"),
            ),
        ):
            result = await service._sync_documents("user123", SyncDirection.DOWN)

            assert result.success is True  # Continues despite individual failures
            assert result.items_processed == 0  # Not incremented on error
            assert result.items_failed == 1

    @pytest.mark.asyncio
    async def test_sync_documents_up(self):
        """Test uploading documents (not implemented)"""
        service = DataSyncService()

        result = await service._sync_documents("user123", SyncDirection.UP)

        assert result.success is True
        assert result.items_processed == 0

    @pytest.mark.asyncio
    async def test_sync_documents_exception(self):
        """Test exception handling in document sync"""
        service = DataSyncService()

        with patch.object(
            service.db_manager,
            "mariadb_session_scope",
            side_effect=Exception("DB error"),
        ):
            result = await service._sync_documents("user123", SyncDirection.DOWN)

            assert result.success is False
            assert len(result.errors) == 1


# ============================================================================
# Test Conflict Resolution
# ============================================================================


class TestConflictResolution:
    """Test conflict resolution strategies"""

    def test_resolve_conflict_server_wins(self):
        """Test SERVER_WINS resolution strategy"""
        service = DataSyncService()

        conflict_data = {
            "local_data": {"value": "local"},
            "server_data": {"value": "server"},
        }

        result = service.resolve_conflict(conflict_data, ConflictResolution.SERVER_WINS)
        assert result == {"value": "server"}

    def test_resolve_conflict_local_wins(self):
        """Test LOCAL_WINS resolution strategy"""
        service = DataSyncService()

        conflict_data = {
            "local_data": {"value": "local"},
            "server_data": {"value": "server"},
        }

        result = service.resolve_conflict(conflict_data, ConflictResolution.LOCAL_WINS)
        assert result == {"value": "local"}

    def test_resolve_conflict_latest_timestamp_server_newer(self):
        """Test LATEST_TIMESTAMP resolution - server is newer"""
        service = DataSyncService()

        conflict_data = {
            "local_data": {"value": "local", "updated_at": "2025-01-24T12:00:00"},
            "server_data": {"value": "server", "updated_at": "2025-01-25T12:00:00"},
        }

        result = service.resolve_conflict(
            conflict_data, ConflictResolution.LATEST_TIMESTAMP
        )
        assert result == {"value": "server", "updated_at": "2025-01-25T12:00:00"}

    def test_resolve_conflict_latest_timestamp_local_newer(self):
        """Test LATEST_TIMESTAMP resolution - local is newer"""
        service = DataSyncService()

        conflict_data = {
            "local_data": {"value": "local", "updated_at": "2025-01-25T12:00:00"},
            "server_data": {"value": "server", "updated_at": "2025-01-24T12:00:00"},
        }

        result = service.resolve_conflict(
            conflict_data, ConflictResolution.LATEST_TIMESTAMP
        )
        assert result == {"value": "local", "updated_at": "2025-01-25T12:00:00"}

    def test_resolve_conflict_manual_review(self):
        """Test MANUAL_REVIEW resolution strategy"""
        service = DataSyncService()

        conflict_data = {
            "local_data": {"value": "local"},
            "server_data": {"value": "server"},
        }

        result = service.resolve_conflict(
            conflict_data, ConflictResolution.MANUAL_REVIEW
        )

        assert result["status"] == "requires_manual_review"
        assert result["local"] == {"value": "local"}
        assert result["server"] == {"value": "server"}


# ============================================================================
# Test Background Sync
# ============================================================================


class TestBackgroundSync:
    """Test background synchronization"""

    @pytest.mark.asyncio
    async def test_start_background_sync_single_iteration(self):
        """Test background sync executes sync_user_data"""
        service = DataSyncService()

        # Mock sync_user_data to track calls and stop after first iteration
        call_count = 0

        async def mock_sync(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        # Use asyncio.sleep to allow controlled iteration
        original_sleep = asyncio.sleep

        async def controlled_sleep(seconds):
            if call_count >= 1:
                # Cancel after first iteration
                raise asyncio.CancelledError()
            await original_sleep(0.01)  # Short sleep for testing

        with (
            patch.object(service, "sync_user_data", side_effect=mock_sync),
            patch("asyncio.sleep", side_effect=controlled_sleep),
        ):
            try:
                await service.start_background_sync("user123", interval_minutes=15)
            except asyncio.CancelledError:
                pass

            assert call_count == 1

    @pytest.mark.asyncio
    async def test_start_background_sync_skips_when_already_syncing(self):
        """Test background sync skips when sync is already in progress"""
        service = DataSyncService()
        service.is_syncing = True  # Simulate sync in progress

        call_count = 0

        async def mock_sync(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())

        async def controlled_sleep(seconds):
            if call_count >= 0:  # Exit immediately
                raise asyncio.CancelledError()
            await asyncio.sleep(0.01)

        with (
            patch.object(service, "sync_user_data", side_effect=mock_sync),
            patch("asyncio.sleep", side_effect=controlled_sleep),
        ):
            try:
                await service.start_background_sync("user123", interval_minutes=15)
            except asyncio.CancelledError:
                pass

            assert call_count == 0  # Should not have called sync_user_data

    @pytest.mark.asyncio
    async def test_start_background_sync_handles_exception(self):
        """Test background sync handles exceptions and retries"""
        service = DataSyncService()

        call_count = 0

        async def mock_sync(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("Sync error")

        async def controlled_sleep(seconds):
            if call_count >= 1:
                raise asyncio.CancelledError()
            await asyncio.sleep(0.01)

        with (
            patch.object(service, "sync_user_data", side_effect=mock_sync),
            patch("asyncio.sleep", side_effect=controlled_sleep),
        ):
            try:
                await service.start_background_sync("user123", interval_minutes=15)
            except asyncio.CancelledError:
                pass

            assert call_count == 1  # Should have attempted sync once


# ============================================================================
# Test Sync Status and Monitoring
# ============================================================================


class TestSyncStatusMonitoring:
    """Test sync status and monitoring methods"""

    def test_get_sync_status_with_last_sync(self):
        """Test getting sync status when last sync time exists"""
        service = DataSyncService()
        test_time = datetime(2025, 1, 25, 12, 0, 0)
        service.last_sync_times["user123"] = test_time

        with patch.object(service, "_check_connectivity", return_value=True):
            status = service.get_sync_status("user123")

            assert status["user_id"] == "user123"
            assert status["last_sync"] == test_time.isoformat()
            assert status["is_syncing"] is False
            assert status["pending_items"] == 0
            assert status["sync_interval_minutes"] == 15
            assert status["online_status"] is True

    def test_get_sync_status_without_last_sync(self):
        """Test getting sync status when no last sync time"""
        service = DataSyncService()

        with patch.object(service, "_check_connectivity", return_value=False):
            status = service.get_sync_status("user123")

            assert status["user_id"] == "user123"
            assert status["last_sync"] is None
            assert status["is_syncing"] is False
            assert status["online_status"] is False

    def test_get_sync_status_while_syncing(self):
        """Test getting sync status while sync is in progress"""
        service = DataSyncService()
        service.is_syncing = True

        with patch.object(service, "_check_connectivity", return_value=True):
            status = service.get_sync_status("user123")

            assert status["is_syncing"] is True

    def test_get_sync_status_with_pending_items(self):
        """Test getting sync status with items in queue"""
        service = DataSyncService()
        service.sync_queue = [
            SyncItem("table1", "id1", "insert", {}, datetime.now(), "user123"),
            SyncItem("table2", "id2", "update", {}, datetime.now(), "user123"),
        ]

        with patch.object(service, "_check_connectivity", return_value=True):
            status = service.get_sync_status("user123")

            assert status["pending_items"] == 2

    def test_check_connectivity_healthy(self):
        """Test connectivity check when database is healthy"""
        service = DataSyncService()

        service.db_manager.test_mariadb_connection = Mock(
            return_value={"status": "healthy"}
        )
        result = service._check_connectivity()
        assert result is True

    def test_check_connectivity_unhealthy(self):
        """Test connectivity check when database is unhealthy"""
        service = DataSyncService()

        service.db_manager.test_mariadb_connection = Mock(
            return_value={"status": "unhealthy"}
        )
        result = service._check_connectivity()
        assert result is False

    def test_check_connectivity_exception(self):
        """Test connectivity check when exception occurs"""
        service = DataSyncService()

        with patch.object(
            service.db_manager,
            "test_mariadb_connection",
            side_effect=Exception("Connection error"),
        ):
            result = service._check_connectivity()
        assert result is False

    def test_get_sync_statistics(self):
        """Test getting sync statistics"""
        service = DataSyncService()
        test_time = datetime(2025, 1, 25, 12, 0, 0)
        service.last_sync_times["user123"] = test_time

        stats = service.get_sync_statistics("user123", days=7)

        assert stats["user_id"] == "user123"
        assert stats["period_days"] == 7
        assert stats["total_syncs"] == 10
        assert stats["successful_syncs"] == 9
        assert stats["failed_syncs"] == 1
        assert stats["items_synced"] == 150
        assert stats["conflicts_resolved"] == 2
        assert stats["last_successful_sync"] == test_time
        assert stats["average_sync_duration"] == 2.5

    def test_get_sync_statistics_different_days(self):
        """Test getting sync statistics for different periods"""
        service = DataSyncService()

        stats_7 = service.get_sync_statistics("user123", days=7)
        stats_30 = service.get_sync_statistics("user123", days=30)

        assert stats_7["period_days"] == 7
        assert stats_30["period_days"] == 30


# ============================================================================
# Test Global Instance and Convenience Functions
# ============================================================================


class TestGlobalInstanceAndConvenience:
    """Test global sync service instance and convenience functions"""

    def test_global_sync_service_exists(self):
        """Test global sync_service instance exists"""
        assert sync_service is not None
        assert isinstance(sync_service, DataSyncService)

    @pytest.mark.asyncio
    async def test_convenience_sync_user_data(self):
        """Test convenience function sync_user_data"""
        with patch.object(
            sync_service, "sync_user_data", new_callable=AsyncMock
        ) as mock_sync:
            mock_result = SyncResult(True, 0, 0, 0, [], [], 0.0, datetime.now())
            mock_sync.return_value = mock_result

            result = await sync_user_data("user123", SyncDirection.BIDIRECTIONAL)

            assert result == mock_result
            mock_sync.assert_called_once_with("user123", SyncDirection.BIDIRECTIONAL)

    def test_convenience_get_sync_status(self):
        """Test convenience function get_sync_status"""
        with patch.object(sync_service, "get_sync_status") as mock_status:
            mock_status.return_value = {"user_id": "user123"}

            result = get_sync_status("user123")

            assert result == {"user_id": "user123"}
            mock_status.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_convenience_start_background_sync(self):
        """Test convenience function start_background_sync"""
        with patch.object(
            sync_service, "start_background_sync", new_callable=AsyncMock
        ) as mock_bg_sync:
            await start_background_sync("user123", interval_minutes=15)

            mock_bg_sync.assert_called_once_with("user123", 15)
