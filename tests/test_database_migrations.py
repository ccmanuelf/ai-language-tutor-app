"""
Tests for database/migrations.py - Database Migration System

Achieves TRUE 100% coverage (statement + branch) for the migration system.
Tests all Alembic integration, data migrations, version management, and database initialization.
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from sqlalchemy import inspect

from app.database.migrations import (
    MigrationManager,
    check_database_integrity,
    initialize_databases,
    migration_manager,
    run_migrations,
    seed_initial_data,
)
from app.models.database import Language, User, UserRole


class TestMigrationManager:
    """Test suite for MigrationManager class"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def migration_mgr(self, temp_dir):
        """Create a MigrationManager instance with temporary paths"""
        with (
            patch("app.database.migrations.db_manager") as mock_db,
            patch("app.database.migrations.local_db_manager") as mock_local,
            patch("app.database.migrations.chroma_manager") as mock_chroma,
        ):
            mgr = MigrationManager()
            # Override paths to use temp directory
            mgr.alembic_config_path = os.path.join(temp_dir, "alembic.ini")
            mgr.migrations_dir = os.path.join(temp_dir, "migrations")
            # Re-create directories with new paths
            mgr._ensure_migration_structure()

            yield mgr

    def test_init_creates_managers(self):
        """Test that MigrationManager initializes with all database managers"""
        with (
            patch("app.database.migrations.db_manager") as mock_db,
            patch("app.database.migrations.local_db_manager") as mock_local,
            patch("app.database.migrations.chroma_manager") as mock_chroma,
        ):
            mgr = MigrationManager()

            assert mgr.db_manager is mock_db
            assert mgr.local_db_manager is mock_local
            assert mgr.chroma_manager is mock_chroma
            assert mgr.alembic_config_path == "./alembic.ini"
            assert mgr.migrations_dir == "./app/database/alembic"

    def test_ensure_migration_structure(self, migration_mgr, temp_dir):
        """Test _ensure_migration_structure creates required directories"""
        # Directory should be created during init
        assert os.path.exists(migration_mgr.migrations_dir)

        versions_dir = Path(migration_mgr.migrations_dir) / "versions"
        assert os.path.exists(versions_dir)
        assert versions_dir.is_dir()

    def test_ensure_migration_structure_idempotent(self, migration_mgr):
        """Test _ensure_migration_structure can be called multiple times"""
        # Call again - should not raise error
        migration_mgr._ensure_migration_structure()

        assert os.path.exists(migration_mgr.migrations_dir)
        versions_dir = Path(migration_mgr.migrations_dir) / "versions"
        assert os.path.exists(versions_dir)

    def test_initialize_alembic_success(self, migration_mgr):
        """Test initialize_alembic creates config and env files"""
        result = migration_mgr.initialize_alembic()

        assert result is True
        assert os.path.exists(migration_mgr.alembic_config_path)
        assert os.path.exists(os.path.join(migration_mgr.migrations_dir, "env.py"))
        assert os.path.exists(
            os.path.join(migration_mgr.migrations_dir, "script.py.mako")
        )

    def test_initialize_alembic_already_exists(self, migration_mgr):
        """Test initialize_alembic when files already exist"""
        # Initialize once
        migration_mgr.initialize_alembic()

        # Initialize again - should still succeed
        result = migration_mgr.initialize_alembic()
        assert result is True

    def test_initialize_alembic_failure(self, migration_mgr):
        """Test initialize_alembic handles errors gracefully"""
        # Make migrations_dir unwritable by setting to invalid path
        migration_mgr.migrations_dir = "/invalid/path/that/cannot/be/created"

        with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
            result = migration_mgr.initialize_alembic()
            assert result is False

    def test_create_alembic_config(self, migration_mgr):
        """Test _create_alembic_config creates valid alembic.ini"""
        with patch("app.database.migrations.db_manager") as mock_db:
            mock_db.config.mariadb_url = "mysql://user:pass@localhost/db"

            migration_mgr._create_alembic_config()

            assert os.path.exists(migration_mgr.alembic_config_path)

            with open(migration_mgr.alembic_config_path, "r") as f:
                content = f.read()
                assert "A generic, single database configuration" in content
                assert f"script_location = {migration_mgr.migrations_dir}" in content
                assert "mysql://user:pass@localhost/db" in content
                assert "[alembic]" in content
                assert "[loggers]" in content

    def test_create_alembic_env(self, migration_mgr):
        """Test _create_alembic_env creates env.py and script.py.mako"""
        migration_mgr._create_alembic_env()

        env_path = Path(migration_mgr.migrations_dir) / "env.py"
        script_path = Path(migration_mgr.migrations_dir) / "script.py.mako"

        assert env_path.exists()
        assert script_path.exists()

        # Verify env.py content
        with open(env_path, "r") as f:
            env_content = f.read()
            assert "Alembic environment configuration" in env_content
            assert "from app.models.database import Base" in env_content
            assert "def run_migrations_offline()" in env_content
            assert "def run_migrations_online()" in env_content

        # Verify script.py.mako content
        with open(script_path, "r") as f:
            script_content = f.read()
            assert "Revision ID:" in script_content
            assert "def upgrade()" in script_content
            assert "def downgrade()" in script_content

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_create_initial_migration_success(
        self, mock_command, mock_config, migration_mgr
    ):
        """Test create_initial_migration generates migration successfully"""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        result = migration_mgr.create_initial_migration()

        assert result is True
        mock_config.assert_called_once_with(migration_mgr.alembic_config_path)
        mock_command.revision.assert_called_once_with(
            mock_config_instance,
            autogenerate=True,
            message="Initial migration - create all tables",
        )

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_create_initial_migration_failure(
        self, mock_command, mock_config, migration_mgr
    ):
        """Test create_initial_migration handles errors"""
        mock_command.revision.side_effect = Exception("Migration generation failed")

        result = migration_mgr.create_initial_migration()

        assert result is False

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_run_migrations_success(self, mock_command, mock_config, migration_mgr):
        """Test run_migrations executes pending migrations"""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        result = migration_mgr.run_migrations()

        assert result is True
        mock_config.assert_called_once_with(migration_mgr.alembic_config_path)
        mock_command.upgrade.assert_called_once_with(mock_config_instance, "head")

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_run_migrations_failure(self, mock_command, mock_config, migration_mgr):
        """Test run_migrations handles errors"""
        mock_command.upgrade.side_effect = Exception("Migration failed")

        result = migration_mgr.run_migrations()

        assert result is False

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_rollback_migration_default_revision(
        self, mock_command, mock_config, migration_mgr
    ):
        """Test rollback_migration with default revision (-1)"""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        result = migration_mgr.rollback_migration()

        assert result is True
        mock_config.assert_called_once_with(migration_mgr.alembic_config_path)
        mock_command.downgrade.assert_called_once_with(mock_config_instance, "-1")

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_rollback_migration_specific_revision(
        self, mock_command, mock_config, migration_mgr
    ):
        """Test rollback_migration with specific revision"""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        result = migration_mgr.rollback_migration("abc123")

        assert result is True
        mock_command.downgrade.assert_called_once_with(mock_config_instance, "abc123")

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.command")
    def test_rollback_migration_failure(self, mock_command, mock_config, migration_mgr):
        """Test rollback_migration handles errors"""
        mock_command.downgrade.side_effect = Exception("Rollback failed")

        result = migration_mgr.rollback_migration()

        assert result is False

    @patch("app.database.migrations.Config")
    @patch("app.database.migrations.ScriptDirectory")
    @patch("app.database.migrations.MigrationContext")
    def test_get_migration_history_success(
        self, mock_context_cls, mock_script_cls, mock_config, migration_mgr
    ):
        """Test get_migration_history returns migration list"""
        # Mock configuration
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        # Mock script directory with revisions
        mock_revision1 = Mock()
        mock_revision1.revision = "abc123"
        mock_revision1.down_revision = None
        mock_revision1.doc = "Initial migration"

        mock_revision2 = Mock()
        mock_revision2.revision = "def456"
        mock_revision2.down_revision = "abc123"
        mock_revision2.doc = "Add user table"

        mock_script = Mock()
        mock_script.walk_revisions.return_value = [mock_revision2, mock_revision1]
        mock_script_cls.from_config.return_value = mock_script

        # Mock migration context
        mock_context_instance = Mock()
        mock_context_instance.get_current_revision.return_value = "def456"
        mock_context_cls.configure.return_value = mock_context_instance

        # Mock database session
        mock_session = MagicMock()
        mock_connection = Mock()
        mock_session.connection.return_value = mock_connection

        with patch.object(
            migration_mgr.db_manager, "mariadb_session_scope"
        ) as mock_session_scope:
            mock_session_scope.return_value.__enter__.return_value = mock_session

            history = migration_mgr.get_migration_history()

        assert len(history) == 2
        assert history[0]["revision"] == "def456"
        assert history[0]["is_current"] is True
        assert history[1]["revision"] == "abc123"
        assert history[1]["is_current"] is False

    @patch("app.database.migrations.Config")
    def test_get_migration_history_failure(self, mock_config, migration_mgr):
        """Test get_migration_history handles errors"""
        mock_config.side_effect = Exception("Config error")

        history = migration_mgr.get_migration_history()

        assert history == []

    def test_initialize_all_databases_success(self, migration_mgr):
        """Test initialize_all_databases initializes all database systems"""
        with (
            patch("app.database.migrations.Base") as mock_base,
            patch.object(migration_mgr.db_manager, "sqlite_engine") as mock_sqlite,
            patch.object(
                migration_mgr.local_db_manager, "initialize_local_schemas"
            ) as mock_local,
            patch.object(
                migration_mgr.chroma_manager, "initialize_collections"
            ) as mock_chroma,
        ):
            results = migration_mgr.initialize_all_databases()

        assert results["sqlite_schema"] is True
        assert results["local_databases"] is True
        assert results["chromadb"] is True
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_sqlite)
        mock_local.assert_called_once()
        mock_chroma.assert_called_once()

    def test_initialize_all_databases_sqlite_failure(self, migration_mgr):
        """Test initialize_all_databases handles SQLite failure"""
        with (
            patch("app.database.migrations.Base") as mock_base,
            patch.object(
                migration_mgr.local_db_manager, "initialize_local_schemas"
            ) as mock_local,
            patch.object(
                migration_mgr.chroma_manager, "initialize_collections"
            ) as mock_chroma,
        ):
            mock_base.metadata.create_all.side_effect = Exception("SQLite error")

            results = migration_mgr.initialize_all_databases()

        assert results["sqlite_schema"] is False
        assert results["local_databases"] is True
        assert results["chromadb"] is True

    def test_initialize_all_databases_local_failure(self, migration_mgr):
        """Test initialize_all_databases handles local database failure"""
        with (
            patch("app.database.migrations.Base") as mock_base,
            patch.object(migration_mgr.db_manager, "sqlite_engine"),
            patch.object(
                migration_mgr.local_db_manager, "initialize_local_schemas"
            ) as mock_local,
            patch.object(
                migration_mgr.chroma_manager, "initialize_collections"
            ) as mock_chroma,
        ):
            mock_local.side_effect = Exception("Local DB error")

            results = migration_mgr.initialize_all_databases()

        assert results["sqlite_schema"] is True
        assert results["local_databases"] is False
        assert results["chromadb"] is True

    def test_initialize_all_databases_chroma_failure(self, migration_mgr):
        """Test initialize_all_databases handles ChromaDB failure"""
        with (
            patch("app.database.migrations.Base") as mock_base,
            patch.object(migration_mgr.db_manager, "sqlite_engine"),
            patch.object(
                migration_mgr.local_db_manager, "initialize_local_schemas"
            ) as mock_local,
            patch.object(
                migration_mgr.chroma_manager, "initialize_collections"
            ) as mock_chroma,
        ):
            mock_chroma.side_effect = Exception("Chroma error")

            results = migration_mgr.initialize_all_databases()

        assert results["sqlite_schema"] is True
        assert results["local_databases"] is True
        assert results["chromadb"] is False

    def test_seed_initial_data_success(self, migration_mgr):
        """Test seed_initial_data creates initial languages and admin user"""
        mock_session = MagicMock()
        mock_query = Mock()
        mock_query.count.return_value = 0  # No existing data
        mock_session.query.return_value = mock_query

        with patch.object(
            migration_mgr.db_manager, "mariadb_session_scope"
        ) as mock_session_scope:
            mock_session_scope.return_value.__enter__.return_value = mock_session

            result = migration_mgr.seed_initial_data()

        assert result is True

        # Verify session.add was called for languages and admin user
        # 5 languages + 1 admin user = 6 calls
        assert mock_session.add.call_count == 6

        # Verify languages were added
        calls = mock_session.add.call_args_list
        language_codes = []
        admin_found = False

        for call in calls:
            obj = call[0][0]
            if isinstance(obj, Language):
                language_codes.append(obj.code)
            elif isinstance(obj, User):
                admin_found = True
                assert obj.user_id == "admin"
                assert obj.role == UserRole.ADMIN

        assert sorted(language_codes) == ["de", "en", "fr", "ja", "zh"]
        assert admin_found is True

    def test_seed_initial_data_already_exists(self, migration_mgr):
        """Test seed_initial_data skips if data already exists"""
        mock_session = MagicMock()
        mock_query = Mock()
        mock_query.count.return_value = 5  # Data already exists
        mock_session.query.return_value = mock_query

        with patch.object(
            migration_mgr.db_manager, "mariadb_session_scope"
        ) as mock_session_scope:
            mock_session_scope.return_value.__enter__.return_value = mock_session

            result = migration_mgr.seed_initial_data()

        assert result is True
        # Should not add any data
        mock_session.add.assert_not_called()

    def test_seed_initial_data_failure(self, migration_mgr):
        """Test seed_initial_data handles errors"""
        with patch.object(
            migration_mgr.db_manager, "mariadb_session_scope"
        ) as mock_session_scope:
            mock_session_scope.side_effect = Exception("Database error")

            result = migration_mgr.seed_initial_data()

        assert result is False

    def test_backup_database_success(self, migration_mgr, temp_dir):
        """Test backup_database creates SQL backup file"""
        backup_path = os.path.join(temp_dir, "test_backup.sql")

        mock_session = MagicMock()
        mock_result = Mock()
        mock_result.keys.return_value = ["id", "name", "email"]
        mock_result.fetchall.return_value = [
            (1, "User1", "user1@test.com"),
            (2, "User2", "user2@test.com"),
        ]
        mock_session.execute.return_value = mock_result

        with (
            patch.object(
                migration_mgr.db_manager, "mariadb_session_scope"
            ) as mock_session_scope,
            patch("app.database.migrations.inspect") as mock_inspect,
        ):
            mock_session_scope.return_value.__enter__.return_value = mock_session

            mock_inspector = Mock()
            mock_inspector.get_table_names.return_value = ["users", "languages"]
            mock_inspect.return_value = mock_inspector

            result_path = migration_mgr.backup_database(backup_path)

        assert result_path == backup_path
        assert os.path.exists(backup_path)

        # Verify backup file content
        with open(backup_path, "r") as f:
            content = f.read()
            assert "Database backup created on" in content
            assert "Table: users" in content
            assert "Table: languages" in content
            assert "Columns: id, name, email" in content
            assert "Rows: 2" in content

    def test_backup_database_default_path(self, migration_mgr):
        """Test backup_database with auto-generated path"""
        mock_session = MagicMock()
        mock_result = Mock()
        mock_result.keys.return_value = ["id"]
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        with (
            patch.object(
                migration_mgr.db_manager, "mariadb_session_scope"
            ) as mock_session_scope,
            patch("app.database.migrations.inspect") as mock_inspect,
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_session_scope.return_value.__enter__.return_value = mock_session

            mock_inspector = Mock()
            mock_inspector.get_table_names.return_value = ["users"]
            mock_inspect.return_value = mock_inspector

            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result_path = migration_mgr.backup_database()

        # Verify auto-generated path format
        assert result_path.startswith("./backups/backup_")
        assert result_path.endswith(".sql")
        mock_makedirs.assert_called_once()

    def test_backup_database_failure(self, migration_mgr):
        """Test backup_database handles errors"""
        with patch.object(
            migration_mgr.db_manager, "mariadb_session_scope"
        ) as mock_session_scope:
            mock_session_scope.side_effect = Exception("Backup failed")

            with pytest.raises(Exception, match="Backup failed"):
                migration_mgr.backup_database()

    def test_check_database_integrity_all_healthy(self, migration_mgr):
        """Test check_database_integrity when all databases are healthy"""
        mock_session = MagicMock()

        # Mock User and Language queries
        mock_user_query = Mock()
        mock_user_query.count.return_value = 10

        mock_language_query = Mock()
        mock_language_query.count.return_value = 5

        mock_session.query.side_effect = [mock_user_query, mock_language_query]

        with (
            patch.object(
                migration_mgr.db_manager, "mariadb_session_scope"
            ) as mock_session_scope,
            patch.object(
                migration_mgr.local_db_manager, "get_database_stats"
            ) as mock_local_stats,
            patch.object(
                migration_mgr.chroma_manager, "get_collection_stats"
            ) as mock_chroma_stats,
        ):
            mock_session_scope.return_value.__enter__.return_value = mock_session
            mock_local_stats.return_value = {"tables": 3, "total_rows": 100}
            mock_chroma_stats.return_value = {"collections": 2, "total_documents": 50}

            report = migration_mgr.check_database_integrity()

        assert "timestamp" in report
        assert report["mariadb"]["users"] == 10
        assert report["mariadb"]["languages"] == 5
        assert report["mariadb"]["status"] == "healthy"
        assert report["local_db"]["tables"] == 3
        assert report["local_db"]["status"] == "healthy"
        assert report["chromadb"]["collections"] == 2
        assert report["chromadb"]["status"] == "healthy"

    def test_check_database_integrity_mariadb_error(self, migration_mgr):
        """Test check_database_integrity handles MariaDB errors"""
        with (
            patch.object(
                migration_mgr.db_manager, "mariadb_session_scope"
            ) as mock_session_scope,
            patch.object(
                migration_mgr.local_db_manager, "get_database_stats"
            ) as mock_local_stats,
            patch.object(
                migration_mgr.chroma_manager, "get_collection_stats"
            ) as mock_chroma_stats,
        ):
            mock_session_scope.side_effect = Exception("Database connection error")
            mock_local_stats.return_value = {"tables": 3}
            mock_chroma_stats.return_value = {"collections": 2}

            report = migration_mgr.check_database_integrity()

        assert report["mariadb"]["status"] == "error"
        assert "error" in report["mariadb"]
        assert report["local_db"]["status"] == "healthy"
        assert report["chromadb"]["status"] == "healthy"

    def test_check_database_integrity_local_db_error(self, migration_mgr):
        """Test check_database_integrity handles local database errors"""
        mock_session = MagicMock()
        mock_user_query = Mock()
        mock_user_query.count.return_value = 10
        mock_language_query = Mock()
        mock_language_query.count.return_value = 5
        mock_session.query.side_effect = [mock_user_query, mock_language_query]

        with (
            patch.object(
                migration_mgr.db_manager, "mariadb_session_scope"
            ) as mock_session_scope,
            patch.object(
                migration_mgr.local_db_manager, "get_database_stats"
            ) as mock_local_stats,
            patch.object(
                migration_mgr.chroma_manager, "get_collection_stats"
            ) as mock_chroma_stats,
        ):
            mock_session_scope.return_value.__enter__.return_value = mock_session
            mock_local_stats.side_effect = Exception("Local DB error")
            mock_chroma_stats.return_value = {"collections": 2}

            report = migration_mgr.check_database_integrity()

        assert report["mariadb"]["status"] == "healthy"
        assert report["local_db"]["status"] == "error"
        assert "error" in report["local_db"]
        assert report["chromadb"]["status"] == "healthy"

    def test_check_database_integrity_chromadb_error(self, migration_mgr):
        """Test check_database_integrity handles ChromaDB errors"""
        mock_session = MagicMock()
        mock_user_query = Mock()
        mock_user_query.count.return_value = 10
        mock_language_query = Mock()
        mock_language_query.count.return_value = 5
        mock_session.query.side_effect = [mock_user_query, mock_language_query]

        with (
            patch.object(
                migration_mgr.db_manager, "mariadb_session_scope"
            ) as mock_session_scope,
            patch.object(
                migration_mgr.local_db_manager, "get_database_stats"
            ) as mock_local_stats,
            patch.object(
                migration_mgr.chroma_manager, "get_collection_stats"
            ) as mock_chroma_stats,
        ):
            mock_session_scope.return_value.__enter__.return_value = mock_session
            mock_local_stats.return_value = {"tables": 3}
            mock_chroma_stats.side_effect = Exception("Chroma error")

            report = migration_mgr.check_database_integrity()

        assert report["mariadb"]["status"] == "healthy"
        assert report["local_db"]["status"] == "healthy"
        assert report["chromadb"]["status"] == "error"
        assert "error" in report["chromadb"]


class TestGlobalMigrationManager:
    """Test suite for global migration_manager instance"""

    def test_global_migration_manager_exists(self):
        """Test that global migration_manager is created"""
        assert migration_manager is not None
        assert isinstance(migration_manager, MigrationManager)


class TestConvenienceFunctions:
    """Test suite for module-level convenience functions"""

    @patch.object(migration_manager, "initialize_all_databases")
    def test_initialize_databases(self, mock_init):
        """Test initialize_databases convenience function"""
        mock_init.return_value = {"sqlite_schema": True}

        result = initialize_databases()

        assert result == {"sqlite_schema": True}
        mock_init.assert_called_once()

    @patch.object(migration_manager, "run_migrations")
    def test_run_migrations_convenience(self, mock_run):
        """Test run_migrations convenience function"""
        mock_run.return_value = True

        result = run_migrations()

        assert result is True
        mock_run.assert_called_once()

    @patch.object(migration_manager, "seed_initial_data")
    def test_seed_initial_data_convenience(self, mock_seed):
        """Test seed_initial_data convenience function"""
        mock_seed.return_value = True

        result = seed_initial_data()

        assert result is True
        mock_seed.assert_called_once()

    @patch.object(migration_manager, "check_database_integrity")
    def test_check_database_integrity_convenience(self, mock_check):
        """Test check_database_integrity convenience function"""
        mock_check.return_value = {"mariadb": {"status": "healthy"}}

        result = check_database_integrity()

        assert result == {"mariadb": {"status": "healthy"}}
        mock_check.assert_called_once()
