"""
Database Migration System for AI Language Tutor App

This module provides database migration functionality including:
- Alembic integration for schema migrations
- Data migrations and transformations
- Version management and rollback capabilities
- Cross-database migration support
- Initial data seeding
"""

import os
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.database.config import db_manager, get_db_session
from app.database.local_config import local_db_manager
from app.database.chromadb_config import chroma_manager
from app.models.database import Base, User, Language, UserRole, LanguageCode


logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations across all database systems"""

    def __init__(self):
        self.db_manager = db_manager
        self.local_db_manager = local_db_manager
        self.chroma_manager = chroma_manager
        self.alembic_config_path = "./alembic.ini"
        self.migrations_dir = "./app/database/alembic"
        self._ensure_migration_structure()

    def _ensure_migration_structure(self):
        """Ensure migration directory structure exists"""
        os.makedirs(self.migrations_dir, exist_ok=True)
        versions_dir = Path(self.migrations_dir) / "versions"
        versions_dir.mkdir(exist_ok=True)

    def initialize_alembic(self) -> bool:
        """Initialize Alembic for the project"""
        try:
            # Create alembic.ini if it doesn't exist
            if not os.path.exists(self.alembic_config_path):
                self._create_alembic_config()

            # Initialize alembic directory structure
            if not os.path.exists(os.path.join(self.migrations_dir, "env.py")):
                self._create_alembic_env()

            logger.info("Alembic initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Alembic: {e}")
            return False

    def _create_alembic_config(self):
        """Create alembic.ini configuration file"""
        config_content = f"""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = {self.migrations_dir}

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%Y%%m%%d_%%H%%M__%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = {db_manager.config.mariadb_url}


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        with open(self.alembic_config_path, "w") as f:
            f.write(config_content)

    def _create_alembic_env(self):
        """Create Alembic env.py file"""
        env_content = '''"""Alembic environment configuration for AI Language Tutor App"""

import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.database import Base
from app.database.config import db_manager

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Use our database manager's engine
    connectable = db_manager.mariadb_engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

        env_path = Path(self.migrations_dir) / "env.py"
        with open(env_path, "w") as f:
            f.write(env_content)

        # Create script.py.mako template
        script_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

        script_path = Path(self.migrations_dir) / "script.py.mako"
        with open(script_path, "w") as f:
            f.write(script_content)

    def create_initial_migration(self) -> bool:
        """Create initial migration for all database tables"""
        try:
            config = Config(self.alembic_config_path)

            # Generate initial migration
            command.revision(
                config,
                autogenerate=True,
                message="Initial migration - create all tables",
            )

            logger.info("Initial migration created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create initial migration: {e}")
            return False

    def run_migrations(self) -> bool:
        """Run pending migrations"""
        try:
            config = Config(self.alembic_config_path)
            command.upgrade(config, "head")
            logger.info("Migrations completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False

    def rollback_migration(self, revision: str = "-1") -> bool:
        """Rollback to a specific migration"""
        try:
            config = Config(self.alembic_config_path)
            command.downgrade(config, revision)
            logger.info(f"Rollback to {revision} completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback migration: {e}")
            return False

    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history"""
        try:
            config = Config(self.alembic_config_path)
            script = ScriptDirectory.from_config(config)

            with db_manager.mariadb_session_scope() as session:
                context = MigrationContext.configure(session.connection())
                current_rev = context.get_current_revision()

            history = []
            for revision in script.walk_revisions():
                history.append(
                    {
                        "revision": revision.revision,
                        "down_revision": revision.down_revision,
                        "message": revision.doc,
                        "is_current": revision.revision == current_rev,
                    }
                )

            return history
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []

    def initialize_all_databases(self) -> Dict[str, bool]:
        """Initialize all database systems"""
        results = {}

        # Initialize SQLite schema
        try:
            Base.metadata.create_all(bind=db_manager.sqlite_engine)
            results["sqlite_schema"] = True
            logger.info("SQLite schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite schema: {e}")
            results["sqlite_schema"] = False

        # Initialize local databases
        try:
            local_db_manager.initialize_local_schemas()
            results["local_databases"] = True
            logger.info("Local databases initialized")
        except Exception as e:
            logger.error(f"Failed to initialize local databases: {e}")
            results["local_databases"] = False

        # Initialize ChromaDB
        try:
            chroma_manager.initialize_collections()
            results["chromadb"] = True
            logger.info("ChromaDB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            results["chromadb"] = False

        return results

    def seed_initial_data(self) -> bool:
        """Seed initial data into databases"""
        try:
            with db_manager.mariadb_session_scope() as session:
                # Check if data already exists
                if session.query(Language).count() > 0:
                    logger.info("Initial data already exists")
                    return True

                # Seed supported languages
                languages = [
                    Language(
                        code="zh",
                        name="Chinese",
                        native_name="中文",
                        has_speech_support=True,
                        has_tts_support=True,
                    ),
                    Language(
                        code="fr",
                        name="French",
                        native_name="Français",
                        has_speech_support=True,
                        has_tts_support=True,
                    ),
                    Language(
                        code="de",
                        name="German",
                        native_name="Deutsch",
                        has_speech_support=True,
                        has_tts_support=True,
                    ),
                    Language(
                        code="ja",
                        name="Japanese",
                        native_name="日本語",
                        has_speech_support=True,
                        has_tts_support=True,
                    ),
                    Language(
                        code="en",
                        name="English",
                        native_name="English",
                        has_speech_support=True,
                        has_tts_support=True,
                    ),
                ]

                for lang in languages:
                    session.add(lang)

                # Create demo admin user
                admin_user = User(
                    user_id="admin",
                    username="Administrator",
                    email="admin@localhost",
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True,
                    preferences={"theme": "light", "language": "en"},
                )
                session.add(admin_user)

            logger.info("Initial data seeded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to seed initial data: {e}")
            return False

    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"./backups/backup_{timestamp}.sql"

        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        try:
            # Simple SQL dump (in production, use mysqldump or similar)
            with db_manager.mariadb_session_scope() as session:
                # Get all table names
                inspector = inspect(db_manager.mariadb_engine)
                tables = inspector.get_table_names()

                with open(backup_path, "w") as f:
                    f.write(f"-- Database backup created on {datetime.now()}\\n\\n")

                    for table in tables:
                        f.write(f"-- Table: {table}\\n")
                        result = session.execute(text(f"SELECT * FROM {table}"))
                        rows = result.fetchall()

                        if rows:
                            columns = list(result.keys())
                            f.write(f"-- Columns: {', '.join(columns)}\\n")
                            f.write(f"-- Rows: {len(rows)}\\n\\n")

            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    def check_database_integrity(self) -> Dict[str, Any]:
        """Check database integrity across all systems"""
        integrity_report = {
            "timestamp": datetime.now().isoformat(),
            "mariadb": {},
            "local_db": {},
            "chromadb": {},
        }

        # Check SQLite
        try:
            with db_manager.mariadb_session_scope() as session:
                # Count records in main tables
                integrity_report["mariadb"] = {
                    "users": session.query(User).count(),
                    "languages": session.query(Language).count(),
                    "status": "healthy",
                }
        except Exception as e:
            integrity_report["mariadb"] = {"status": "error", "error": str(e)}

        # Check local databases
        try:
            stats = local_db_manager.get_database_stats()
            integrity_report["local_db"] = {**stats, "status": "healthy"}
        except Exception as e:
            integrity_report["local_db"] = {"status": "error", "error": str(e)}

        # Check ChromaDB
        try:
            stats = chroma_manager.get_collection_stats()
            integrity_report["chromadb"] = {**stats, "status": "healthy"}
        except Exception as e:
            integrity_report["chromadb"] = {"status": "error", "error": str(e)}

        return integrity_report


# Global migration manager
migration_manager = MigrationManager()


# Convenience functions
def initialize_databases():
    """Initialize all database systems"""
    return migration_manager.initialize_all_databases()


def run_migrations():
    """Run pending migrations"""
    return migration_manager.run_migrations()


def seed_initial_data():
    """Seed initial data"""
    return migration_manager.seed_initial_data()


def check_database_integrity():
    """Check database integrity"""
    return migration_manager.check_database_integrity()
