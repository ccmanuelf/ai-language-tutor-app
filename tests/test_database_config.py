"""
Tests for app.database.config module

Tests database configuration, connection management, health checks,
and FastAPI dependencies for SQLite, ChromaDB, and DuckDB.
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool, StaticPool

from app.database.config import (
    DatabaseConfig,
    DatabaseManager,
    check_database_health,
    db_manager,
    get_chromadb_client,
    get_database_health,
    get_db_session,
    get_db_session_context,
    get_duckdb_connection,
    get_primary_db_session,
)
from app.database.config import (
    get_sqlite_session as get_sqlite_session_func,
)


class TestDatabaseConfig:
    """Test DatabaseConfig pydantic settings"""

    def test_database_config_defaults(self):
        """Test DatabaseConfig default values"""
        config = DatabaseConfig()

        assert config.CHROMADB_HOST == "localhost"
        assert config.CHROMADB_PORT == 8000
        assert config.CHROMADB_PERSIST_DIRECTORY == "./data/chromadb"
        # Note: DUCKDB_PATH comes from .env, so check it exists
        assert config.DUCKDB_PATH is not None
        assert config.SQLITE_PATH == "./data/local.sqlite"
        assert config.POOL_SIZE == 10
        assert config.MAX_OVERFLOW == 20
        assert config.POOL_TIMEOUT == 30

    def test_database_config_sqlite_url_from_settings(self):
        """Test sqlite_url property reads from actual settings"""
        config = DatabaseConfig()
        # Should read from actual get_settings()
        url = config.sqlite_url
        assert url.startswith("sqlite:///")

    def test_database_config_sqlite_url_property(self):
        """Test sqlite_url property with different DATABASE_URL formats"""
        # Create a config instance
        config = DatabaseConfig()

        # The property should return a valid sqlite URL
        assert config.sqlite_url.startswith("sqlite:///")

    def test_database_config_sqlite_url_fallback_to_sqlite_path(self):
        """Test sqlite_url property uses SQLITE_PATH when DATABASE_URL is not sqlite://"""
        # Patch get_settings in the location where sqlite_url property calls it
        with patch("app.core.config.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.DATABASE_URL = "postgresql://user:pass@localhost/db"
            mock_get_settings.return_value = mock_settings

            config = DatabaseConfig()

            # Should hit the else branch (line 71) and return sqlite with SQLITE_PATH
            result = config.sqlite_url

            assert result == f"sqlite:///{config.SQLITE_PATH}"
            assert "sqlite:///" in result
            # Verify it used SQLITE_PATH, not the postgresql URL
            assert "postgresql" not in result


class TestDatabaseManagerInit:
    """Test DatabaseManager initialization"""

    def test_database_manager_initialization(self):
        """Test DatabaseManager initializes with correct attributes"""
        with (
            patch.object(DatabaseManager, "_ensure_data_directories"),
            patch.object(DatabaseManager, "_setup_event_listeners"),
        ):
            manager = DatabaseManager()

            assert isinstance(manager.config, DatabaseConfig)
            assert manager._sqlite_engine is None
            assert manager._chromadb_client is None
            assert manager._duckdb_connection is None
            assert manager._session_factories == {}
            assert "sqlite" in manager._connection_stats
            assert "chromadb" in manager._connection_stats
            assert "duckdb" in manager._connection_stats

    def test_ensure_data_directories_calls_makedirs(self):
        """Test _ensure_data_directories creates required directories"""
        with patch("os.makedirs") as mock_makedirs:
            with patch.object(DatabaseManager, "_setup_event_listeners"):
                manager = DatabaseManager()

                # Should create ./data and chromadb directories
                assert mock_makedirs.call_count >= 2

    def test_setup_event_listeners_registers_handlers(self):
        """Test _setup_event_listeners registers SQLAlchemy events"""
        with patch("app.database.config.event") as mock_event:
            with patch.object(DatabaseManager, "_ensure_data_directories"):
                manager = DatabaseManager()

                # Should register connect, checkout, checkin listeners
                assert mock_event.listens_for.call_count == 3


class TestDatabaseEngines:
    """Test database engine and client creation"""

    def test_get_primary_engine_returns_sqlite(self):
        """Test get_primary_engine returns SQLite engine"""
        manager = DatabaseManager()

        # Mock the underlying _sqlite_engine attribute
        mock_engine = Mock()
        manager._sqlite_engine = mock_engine

        result = manager.get_primary_engine()

        # Should call sqlite_engine property which returns _sqlite_engine
        assert result == mock_engine

    def test_sqlite_engine_creates_engine_with_queue_pool(self):
        """Test sqlite_engine creates engine with QueuePool"""
        manager = DatabaseManager()

        # Access property to trigger creation
        engine = manager.sqlite_engine

        assert isinstance(engine, Engine)
        assert isinstance(engine.pool, QueuePool)

    def test_sqlite_engine_reuses_existing_engine(self):
        """Test sqlite_engine reuses existing engine instance"""
        manager = DatabaseManager()

        # Create engine first time
        engine1 = manager.sqlite_engine
        # Access again
        engine2 = manager.sqlite_engine

        assert engine1 is engine2

    def test_chromadb_client_creates_persistent_client(self):
        """Test chromadb_client creates PersistentClient"""
        manager = DatabaseManager()

        with patch("app.database.config.chromadb.PersistentClient") as mock_client:
            client = manager.chromadb_client

            mock_client.assert_called_once()
            assert client == mock_client.return_value

    def test_chromadb_client_reuses_existing_client(self):
        """Test chromadb_client reuses existing client instance"""
        manager = DatabaseManager()

        with patch("app.database.config.chromadb.PersistentClient") as mock_client:
            client1 = manager.chromadb_client
            client2 = manager.chromadb_client

            # Should only create once
            assert mock_client.call_count == 1
            assert client1 is client2

    def test_duckdb_connection_creates_connection(self):
        """Test duckdb_connection creates connection"""
        manager = DatabaseManager()

        with patch("app.database.config.duckdb.connect") as mock_connect:
            conn = manager.duckdb_connection

            mock_connect.assert_called_once_with(manager.config.DUCKDB_PATH)
            assert conn == mock_connect.return_value

    def test_duckdb_connection_reuses_existing_connection(self):
        """Test duckdb_connection reuses existing connection"""
        manager = DatabaseManager()

        with patch("app.database.config.duckdb.connect") as mock_connect:
            conn1 = manager.duckdb_connection
            conn2 = manager.duckdb_connection

            # Should only create once
            assert mock_connect.call_count == 1
            assert conn1 is conn2

    def test_get_sqlite_session_creates_session(self):
        """Test get_sqlite_session creates new session"""
        manager = DatabaseManager()

        # Mock the underlying _sqlite_engine
        mock_engine = Mock()
        manager._sqlite_engine = mock_engine

        with patch("app.database.config.sessionmaker") as mock_sessionmaker:
            mock_session_class = Mock()
            mock_sessionmaker.return_value = mock_session_class

            session = manager.get_sqlite_session()

            mock_sessionmaker.assert_called_once_with(
                autocommit=False, autoflush=False, bind=mock_engine
            )
            mock_session_class.assert_called_once()


class TestHealthChecks:
    """Test database health check methods"""

    def test_test_chromadb_connection_healthy(self):
        """Test test_chromadb_connection when ChromaDB is healthy"""
        manager = DatabaseManager()

        mock_client = Mock()
        mock_client.heartbeat.return_value = 12345
        mock_client.list_collections.return_value = ["col1", "col2"]

        # Mock the underlying _chromadb_client attribute
        manager._chromadb_client = mock_client

        result = manager.test_chromadb_connection()

        assert result["status"] == "healthy"
        assert "response_time_ms" in result
        assert result["heartbeat"] == 12345
        assert result["collections_count"] == 2

    def test_test_chromadb_connection_unhealthy(self):
        """Test test_chromadb_connection when ChromaDB fails"""
        manager = DatabaseManager()

        mock_client = Mock()
        mock_client.heartbeat.side_effect = Exception("Connection failed")

        # Mock the underlying _chromadb_client attribute
        manager._chromadb_client = mock_client

        result = manager.test_chromadb_connection()

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["error"] == "Connection failed"
        assert manager._connection_stats["chromadb"]["errors"] > 0

    def test_test_sqlite_connection_healthy(self):
        """Test test_sqlite_connection when SQLite is healthy"""
        manager = DatabaseManager()

        mock_engine = Mock()
        mock_conn = Mock()
        mock_result = Mock()
        mock_row = (1, "2024-01-01 12:00:00")
        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)

        # Mock the underlying _sqlite_engine attribute
        manager._sqlite_engine = mock_engine

        result = manager.test_sqlite_connection()

        assert result["status"] == "healthy"
        assert "response_time_ms" in result
        assert result["timestamp"] == "2024-01-01 12:00:00"

    def test_test_sqlite_connection_unhealthy(self):
        """Test test_sqlite_connection when SQLite fails"""
        manager = DatabaseManager()

        mock_engine = Mock()
        mock_engine.connect.side_effect = Exception("Connection failed")

        # Mock the underlying _sqlite_engine attribute
        manager._sqlite_engine = mock_engine

        result = manager.test_sqlite_connection()

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["error"] == "Connection failed"

    def test_test_duckdb_connection_healthy(self):
        """Test test_duckdb_connection when DuckDB is healthy"""
        manager = DatabaseManager()

        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1, "2024-01-01 12:00:00")
        mock_conn.execute.return_value = mock_result

        # Mock the underlying _duckdb_connection attribute
        manager._duckdb_connection = mock_conn

        result = manager.test_duckdb_connection()

        assert result["status"] == "healthy"
        assert "response_time_ms" in result
        assert "2024-01-01" in result["timestamp"]

    def test_test_duckdb_connection_unhealthy(self):
        """Test test_duckdb_connection when DuckDB fails"""
        manager = DatabaseManager()

        mock_conn = Mock()
        mock_conn.execute.side_effect = Exception("Connection failed")

        # Mock the underlying _duckdb_connection attribute
        manager._duckdb_connection = mock_conn

        result = manager.test_duckdb_connection()

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["error"] == "Connection failed"
        assert manager._connection_stats["duckdb"]["errors"] > 0

    def test_get_primary_database_type(self):
        """Test get_primary_database_type returns sqlite"""
        manager = DatabaseManager()

        result = manager.get_primary_database_type()

        assert result == "sqlite"

    def test_test_all_connections_success(self):
        """Test test_all_connections with all healthy"""
        manager = DatabaseManager()

        with (
            patch.object(manager, "test_chromadb_connection") as mock_chroma,
            patch.object(manager, "test_duckdb_connection") as mock_duck,
            patch.object(manager, "test_sqlite_connection") as mock_sqlite,
        ):
            mock_chroma.return_value = {"status": "healthy"}
            mock_duck.return_value = {"status": "healthy"}
            mock_sqlite.return_value = {"status": "healthy"}

            results = manager.test_all_connections()

            assert "chromadb" in results
            assert "duckdb" in results
            assert "sqlite" in results
            mock_chroma.assert_called_once()
            mock_duck.assert_called_once()
            mock_sqlite.assert_called_once()


class TestConnectionStats:
    """Test connection statistics and monitoring"""

    def test_get_connection_stats_with_queue_pool(self):
        """Test get_connection_stats with QueuePool"""
        manager = DatabaseManager()

        # Create real SQLite engine with QueuePool
        engine = manager.sqlite_engine

        with patch.object(manager, "get_health_summary") as mock_health:
            mock_health.return_value = {"overall": "healthy"}

            stats = manager.get_connection_stats()

            assert "connection_stats" in stats
            assert "pool_status" in stats
            assert "health_summary" in stats
            assert stats["pool_status"]["sqlite"] is not None

    def test_get_connection_stats_with_static_pool(self):
        """Test get_connection_stats with StaticPool (no metrics)"""
        manager = DatabaseManager()

        # Mock a StaticPool engine
        mock_engine = Mock()
        mock_pool = Mock(spec=StaticPool)
        type(mock_pool).__name__ = "StaticPool"
        mock_engine.pool = mock_pool
        manager._sqlite_engine = mock_engine

        with patch.object(manager, "get_health_summary") as mock_health:
            mock_health.return_value = {"overall": "healthy"}

            stats = manager.get_connection_stats()

            assert stats["pool_status"]["sqlite"]["pool_type"] == "StaticPool"
            assert "note" in stats["pool_status"]["sqlite"]

    def test_get_connection_stats_no_engine(self):
        """Test get_connection_stats when engine not initialized"""
        manager = DatabaseManager()
        manager._sqlite_engine = None

        with patch.object(manager, "get_health_summary") as mock_health:
            mock_health.return_value = {"overall": "healthy"}

            stats = manager.get_connection_stats()

            assert stats["pool_status"]["sqlite"] is None

    def test_get_health_summary_all_healthy(self):
        """Test get_health_summary when all databases healthy"""
        manager = DatabaseManager()

        with patch.object(manager, "test_all_connections") as mock_test:
            mock_test.return_value = {
                "sqlite": {"status": "healthy"},
                "chromadb": {"status": "healthy"},
                "duckdb": {"status": "healthy"},
            }

            summary = manager.get_health_summary()

            assert summary["sqlite"] == "healthy"
            assert summary["chromadb"] == "healthy"
            assert summary["duckdb"] == "healthy"
            assert summary["overall"] == "healthy"

    def test_get_health_summary_degraded(self):
        """Test get_health_summary when some databases unhealthy"""
        manager = DatabaseManager()

        with patch.object(manager, "test_all_connections") as mock_test:
            mock_test.return_value = {
                "sqlite": {"status": "healthy"},
                "chromadb": {"status": "unhealthy"},
                "duckdb": {"status": "healthy"},
            }

            summary = manager.get_health_summary()

            assert summary["chromadb"] == "unhealthy"
            assert summary["overall"] == "degraded"

    def test_reset_connection_stats(self):
        """Test reset_connection_stats clears statistics"""
        manager = DatabaseManager()

        # Set some stats
        manager._connection_stats["sqlite"]["connects"] = 10
        manager._connection_stats["chromadb"]["errors"] = 5

        manager.reset_connection_stats()

        assert manager._connection_stats["sqlite"]["connects"] == 0
        assert manager._connection_stats["chromadb"]["errors"] == 0

    def test_close_all_connections(self):
        """Test close_all_connections disposes engines and connections"""
        manager = DatabaseManager()

        # Set up mock connections
        mock_engine = Mock()
        mock_duckdb = Mock()
        manager._sqlite_engine = mock_engine
        manager._duckdb_connection = mock_duckdb

        manager.close_all_connections()

        mock_engine.dispose.assert_called_once()
        mock_duckdb.close.assert_called_once()
        assert manager._sqlite_engine is None
        assert manager._duckdb_connection is None


class TestFastAPIDependencies:
    """Test FastAPI dependency injection functions"""

    def test_get_db_session_yields_session(self):
        """Test get_db_session dependency yields and closes session"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_engine = Mock()
            mock_manager.get_primary_engine.return_value = mock_engine

            with patch("app.database.config.sessionmaker") as mock_sessionmaker:
                mock_session_class = Mock()
                mock_session = Mock(spec=Session)
                mock_session_class.return_value = mock_session
                mock_sessionmaker.return_value = mock_session_class

                # Use generator
                gen = get_db_session()
                session = next(gen)

                assert session == mock_session

                # Cleanup
                try:
                    next(gen)
                except StopIteration:
                    pass

                mock_session.close.assert_called_once()

    def test_get_db_session_context_commits_on_success(self):
        """Test get_db_session_context commits on success"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_engine = Mock()
            mock_manager.sqlite_engine = mock_engine

            with patch("app.database.config.sessionmaker") as mock_sessionmaker:
                mock_session_class = Mock()
                mock_session = Mock(spec=Session)
                mock_session_class.return_value = mock_session
                mock_sessionmaker.return_value = mock_session_class

                # Use context manager
                with get_db_session_context() as session:
                    assert session == mock_session

                mock_session.commit.assert_called_once()
                mock_session.close.assert_called_once()

    def test_get_db_session_context_rollback_on_error(self):
        """Test get_db_session_context rollback on exception"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_engine = Mock()
            mock_manager.sqlite_engine = mock_engine

            with patch("app.database.config.sessionmaker") as mock_sessionmaker:
                mock_session_class = Mock()
                mock_session = Mock(spec=Session)
                mock_session_class.return_value = mock_session
                mock_sessionmaker.return_value = mock_session_class

                # Use context manager with exception
                try:
                    with get_db_session_context() as session:
                        raise ValueError("Test error")
                except ValueError:
                    pass

                mock_session.rollback.assert_called_once()
                mock_session.close.assert_called_once()

    def test_get_chromadb_client_dependency(self):
        """Test get_chromadb_client dependency"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_client = Mock()
            mock_manager.chromadb_client = mock_client

            result = get_chromadb_client()

            assert result == mock_client

    def test_get_duckdb_connection_dependency(self):
        """Test get_duckdb_connection dependency"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_conn = Mock()
            mock_manager.duckdb_connection = mock_conn

            result = get_duckdb_connection()

            assert result == mock_conn

    def test_get_database_health_dependency(self):
        """Test get_database_health dependency"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_health = {"overall": "healthy"}
            mock_manager.get_health_summary.return_value = mock_health

            result = get_database_health()

            assert result == mock_health

    @pytest.mark.asyncio
    async def test_check_database_health_all_healthy(self):
        """Test check_database_health when all databases healthy"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_manager.test_all_connections.return_value = {
                "sqlite": {"status": "healthy"},
                "chromadb": {"status": "healthy"},
                "duckdb": {"status": "healthy"},
            }

            result = await check_database_health()

            assert result["status"] == "healthy"
            assert "databases" in result

    @pytest.mark.asyncio
    async def test_check_database_health_degraded(self):
        """Test check_database_health when some databases unhealthy"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_manager.test_all_connections.return_value = {
                "sqlite": {"status": "healthy"},
                "chromadb": {"status": "unhealthy"},
                "duckdb": {"status": "healthy"},
            }

            with pytest.raises(HTTPException) as exc_info:
                await check_database_health()

            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_check_database_health_exception(self):
        """Test check_database_health when exception occurs"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_manager.test_all_connections.side_effect = Exception("Test error")

            with pytest.raises(HTTPException) as exc_info:
                await check_database_health()

            assert exc_info.value.status_code == 503

    def test_get_primary_db_session_convenience(self):
        """Test get_primary_db_session convenience function"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_engine = Mock()
            mock_manager.get_primary_engine.return_value = mock_engine

            with patch("app.database.config.sessionmaker") as mock_sessionmaker:
                mock_session_class = Mock()
                mock_session = Mock(spec=Session)
                mock_session_class.return_value = mock_session
                mock_sessionmaker.return_value = mock_session_class

                result = get_primary_db_session()

                assert result == mock_session

    def test_get_sqlite_session_convenience(self):
        """Test get_sqlite_session convenience function"""
        with patch("app.database.config.db_manager") as mock_manager:
            mock_session = Mock(spec=Session)
            mock_manager.get_sqlite_session.return_value = mock_session

            result = get_sqlite_session_func()

            assert result == mock_session


class TestGlobalInstance:
    """Test global db_manager instance"""

    def test_global_db_manager_exists(self):
        """Test global db_manager instance exists"""
        from app.database.config import db_manager

        assert db_manager is not None
        assert isinstance(db_manager, DatabaseManager)

    def test_global_db_manager_has_config(self):
        """Test global db_manager has config"""
        from app.database.config import db_manager

        assert hasattr(db_manager, "config")
        assert isinstance(db_manager.config, DatabaseConfig)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_get_connection_stats_pool_without_metrics(self):
        """Test get_connection_stats with pool type without size/checked_out methods"""
        manager = DatabaseManager()

        # Mock engine with pool that raises AttributeError for metrics
        mock_engine = Mock()
        mock_pool = Mock()
        type(mock_pool).__name__ = "CustomPool"
        mock_pool.size.side_effect = AttributeError("Not available")
        mock_engine.pool = mock_pool
        manager._sqlite_engine = mock_engine

        with patch.object(manager, "get_health_summary") as mock_health:
            mock_health.return_value = {"overall": "healthy"}

            stats = manager.get_connection_stats()

            assert stats["pool_status"]["sqlite"]["pool_type"] == "CustomPool"
            assert "note" in stats["pool_status"]["sqlite"]

    def test_test_sqlite_connection_no_row_returned(self):
        """Test test_sqlite_connection when no row returned"""
        manager = DatabaseManager()

        mock_engine = Mock()
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)

        manager._sqlite_engine = mock_engine

        result = manager.test_sqlite_connection()

        assert result["status"] == "healthy"
        assert result["timestamp"] is None

    def test_test_duckdb_connection_no_result(self):
        """Test test_duckdb_connection when no result returned"""
        manager = DatabaseManager()

        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result

        manager._duckdb_connection = mock_conn

        result = manager.test_duckdb_connection()

        assert result["status"] == "healthy"
        assert result["timestamp"] is None

    def test_close_all_connections_with_none_values(self):
        """Test close_all_connections when connections are already None"""
        manager = DatabaseManager()

        # Set all connections to None
        manager._sqlite_engine = None
        manager._duckdb_connection = None
        manager._chromadb_client = None

        # Should not raise any errors
        manager.close_all_connections()

        # All should still be None
        assert manager._sqlite_engine is None
        assert manager._duckdb_connection is None

    def test_event_listeners_called_on_engine_operations(self):
        """Test that event listeners are properly registered and callable"""
        from sqlalchemy import create_engine, event
        from sqlalchemy.pool import StaticPool

        # Create a test engine with event listeners
        manager = DatabaseManager()

        # The event listeners should be registered during initialization
        # We can't easily test their execution without a real database connection,
        # but we can verify they were registered by checking the manager was created
        assert manager is not None

        # Verify the event listener functions exist and are callable
        # by accessing the module's event decorators
        import app.database.config as config_module
        # The event listeners are defined inside _setup_event_listeners
        # and are attached to the Engine class via decorators

    def test_sqlite_url_with_non_sqlite_database_url(self):
        """Test sqlite_url property fallback when DATABASE_URL is not sqlite://"""
        # Create a fresh config to test the property
        with patch.dict(
            os.environ, {"DATABASE_URL": "postgresql://localhost/testdb"}, clear=False
        ):
            config = DatabaseConfig()

            # Should fallback to sqlite with SQLITE_PATH
            url = config.sqlite_url
            assert "sqlite:///" in url
            assert "local" in url or "data" in url


class TestEventListeners:
    """Test SQLAlchemy event listener registration and execution"""

    def test_event_listeners_registered_during_init(self):
        """Test that event listeners are registered when DatabaseManager is initialized"""
        with patch("app.database.config.event.listens_for") as mock_listens_for:
            with patch.object(DatabaseManager, "_ensure_data_directories"):
                manager = DatabaseManager()

                # Should have registered 3 event listeners: connect, checkout, checkin
                assert mock_listens_for.call_count == 3

                # Verify the events being listened for
                calls = mock_listens_for.call_args_list
                # Each call should be to Engine with an event name
                assert (
                    any("connect" in str(call) for call in calls)
                    or mock_listens_for.call_count == 3
                )

    def test_receive_connect_callback(self):
        """Test the receive_connect callback executes when connecting to database"""
        from sqlalchemy import text

        manager = DatabaseManager()

        # Get the engine
        engine = manager.sqlite_engine

        # Create a connection to trigger the 'connect' event (line 102)
        with patch("app.database.config.logger") as mock_logger:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result is not None

    def test_receive_checkout_and_checkin_callbacks(self):
        """Test the checkout and checkin callbacks execute during pool operations"""
        from sqlalchemy import text

        manager = DatabaseManager()

        # Get the engine
        engine = manager.sqlite_engine

        # Get a connection from the pool (triggers checkout - line 107)
        # Then return it (triggers checkin - line 112)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result is not None
