"""
DuckDB and SQLite Configuration for AI Language Tutor App

This module handles local/offline database operations using:
- DuckDB for analytical queries and complex data processing
- SQLite for simple local storage and offline capability
- Hybrid approach for optimal performance and functionality
"""

import logging
from typing import Dict, List, Optional
from contextlib import contextmanager
from pathlib import Path
import duckdb
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json
from datetime import datetime


logger = logging.getLogger(__name__)


class LocalDatabaseManager:
    """Manages local database operations for offline functionality"""

    def __init__(self, data_directory: str = "./data"):
        """
        Initialize local database manager

        Args:
            data_directory: Directory to store local database files
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)

        # Database file paths
        self.duckdb_path = self.data_directory / "analytics.duckdb"
        self.sqlite_path = self.data_directory / "local.sqlite"

        # Connection objects
        self._duckdb_conn = None
        self._sqlite_engine = None
        self._sqlite_session_factory = None

    @property
    def duckdb_connection(self):
        """Get or create DuckDB connection"""
        if self._duckdb_conn is None:
            self._duckdb_conn = duckdb.connect(str(self.duckdb_path))
            self._setup_duckdb_extensions()
        return self._duckdb_conn

    @property
    def sqlite_engine(self) -> Engine:
        """Get or create SQLite engine"""
        if self._sqlite_engine is None:
            self._sqlite_engine = create_engine(
                f"sqlite:///{self.sqlite_path}",
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20,
                    "isolation_level": None,  # Autocommit mode
                },
                echo=False,  # Set to True for debugging
            )
        return self._sqlite_engine

    @property
    def sqlite_session_factory(self):
        """Get or create SQLite session factory"""
        if self._sqlite_session_factory is None:
            self._sqlite_session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.sqlite_engine
            )
        return self._sqlite_session_factory

    def _setup_duckdb_extensions(self):
        """Setup DuckDB extensions for enhanced functionality"""
        try:
            # Install JSON extension for JSON operations
            self.duckdb_connection.execute("INSTALL json;")
            self.duckdb_connection.execute("LOAD json;")

            # Install httpfs for potential web data access
            self.duckdb_connection.execute("INSTALL httpfs;")
            self.duckdb_connection.execute("LOAD httpfs;")

            logger.info("DuckDB extensions loaded successfully")
        except Exception as e:
            logger.warning(f"Some DuckDB extensions failed to load: {e}")

    def initialize_local_schemas(self):
        """Initialize all local database schemas"""
        self._initialize_sqlite_schema()
        self._initialize_duckdb_schema()
        logger.info("Local database schemas initialized")

    def _initialize_sqlite_schema(self):
        """Initialize SQLite schema for basic local storage"""
        schema_sql = """
        -- User profiles and preferences (offline access)
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            email TEXT,
            preferences TEXT, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- User settings (offline access)
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, setting_key),
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );

        -- Local conversation history (essential offline data)
        CREATE TABLE IF NOT EXISTS local_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            message_type TEXT NOT NULL, -- 'user' or 'assistant'
            content TEXT NOT NULL,
            language TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT, -- JSON string for additional data
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );

        -- Learning progress tracking (offline access)
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            language TEXT NOT NULL,
            skill_type TEXT, -- 'vocabulary', 'pronunciation', 'conversation'
            progress_data TEXT, -- JSON string
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );

        -- Cached document content (offline access)
        CREATE TABLE IF NOT EXISTS cached_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            document_id TEXT UNIQUE NOT NULL,
            filename TEXT,
            content TEXT,
            document_type TEXT,
            language TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );

        -- Vocabulary lists (offline access)
        CREATE TABLE IF NOT EXISTS vocabulary_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            language TEXT NOT NULL,
            word TEXT NOT NULL,
            translation TEXT,
            definition TEXT,
            pronunciation TEXT,
            difficulty_level INTEGER DEFAULT 1,
            learned_count INTEGER DEFAULT 0,
            last_reviewed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );

        -- Sync tracking for data synchronization
        CREATE TABLE IF NOT EXISTS sync_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            record_id TEXT NOT NULL,
            action TEXT NOT NULL, -- 'insert', 'update', 'delete'
            sync_status TEXT DEFAULT 'pending', -- 'pending', 'synced', 'failed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
        CREATE INDEX IF NOT EXISTS idx_local_conversations_user_id ON local_conversations(user_id);
        CREATE INDEX IF NOT EXISTS idx_learning_progress_user_id ON learning_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_cached_documents_user_id ON cached_documents(user_id);
        CREATE INDEX IF NOT EXISTS idx_vocabulary_lists_user_id ON vocabulary_lists(user_id);
        CREATE INDEX IF NOT EXISTS idx_sync_tracking_status ON sync_tracking(sync_status);
        """

        with self.sqlite_engine.connect() as conn:
            for statement in schema_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()

    def _initialize_duckdb_schema(self):
        """Initialize DuckDB schema for analytics and complex queries"""
        schema_sql = """
        -- Learning analytics and patterns
        CREATE TABLE IF NOT EXISTS learning_analytics (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_date DATE NOT NULL,
            language TEXT NOT NULL,
            session_duration_minutes INTEGER,
            words_learned INTEGER DEFAULT 0,
            conversations_count INTEGER DEFAULT 0,
            pronunciation_attempts INTEGER DEFAULT 0,
            pronunciation_accuracy FLOAT,
            topics_covered TEXT[], -- Array of topics
            difficulty_levels INTEGER[],
            session_metadata JSON
        );

        -- Conversation analysis
        CREATE TABLE IF NOT EXISTS conversation_analysis (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            language TEXT NOT NULL,
            conversation_date TIMESTAMP,
            turn_count INTEGER,
            avg_response_time_seconds FLOAT,
            vocabulary_complexity_score FLOAT,
            grammar_accuracy_score FLOAT,
            conversation_topics TEXT[],
            sentiment_scores FLOAT[],
            analysis_metadata JSON
        );

        -- Document processing analytics
        CREATE TABLE IF NOT EXISTS document_analytics (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            document_type TEXT,
            language TEXT,
            word_count INTEGER,
            complexity_score FLOAT,
            reading_time_estimate_minutes INTEGER,
            key_topics TEXT[],
            vocabulary_extracted TEXT[],
            processing_metadata JSON,
            processed_at TIMESTAMP
        );

        -- User performance metrics
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            metric_date DATE NOT NULL,
            language TEXT NOT NULL,
            metric_type TEXT NOT NULL, -- 'daily', 'weekly', 'monthly'
            total_study_time_minutes INTEGER,
            words_learned_count INTEGER,
            conversations_completed INTEGER,
            pronunciation_improvement_score FLOAT,
            consistency_score FLOAT,
            achievement_badges TEXT[],
            metrics_metadata JSON
        );
        """

        # Execute schema creation
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        for statement in statements:
            try:
                self.duckdb_connection.execute(statement)
                self.duckdb_connection.commit()
            except Exception as e:
                logger.warning(f"DuckDB schema statement failed: {e}")

    @contextmanager
    def sqlite_session(self):
        """Context manager for SQLite sessions"""
        session = self.sqlite_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def duckdb_cursor(self):
        """Context manager for DuckDB operations"""
        try:
            yield self.duckdb_connection
        except Exception:
            self.duckdb_connection.rollback()
            raise

    def add_user_profile(self, user_id: str, username: str, email: str = None, preferences: Dict = None) -> bool:
        """Add or update user profile in local SQLite database"""
        try:
            with self.sqlite_session() as session:
                preferences_json = json.dumps(preferences or {})

                # Use raw SQL for better control
                session.execute(text("""
                    INSERT OR REPLACE INTO user_profiles
                    (user_id, username, email, preferences, updated_at)
                    VALUES (:user_id, :username, :email, :preferences, :updated_at)
                """), {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "preferences": preferences_json,
                    "updated_at": datetime.now()
                })

                logger.info(f"User profile added/updated: {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding user profile: {e}")
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from local SQLite database"""
        try:
            with self.sqlite_session() as session:
                result = session.execute(text("""
                    SELECT user_id, username, email, preferences, created_at, updated_at
                    FROM user_profiles WHERE user_id = :user_id
                """), {"user_id": user_id}).fetchone()

                if result:
                    return {
                        "user_id": result[0],
                        "username": result[1],
                        "email": result[2],
                        "preferences": json.loads(result[3] or "{}"),
                        "created_at": result[4],
                        "updated_at": result[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    def save_conversation_locally(self, user_id: str, conversation_id: str,
                                message_type: str, content: str, language: str = None,
                                metadata: Dict = None) -> bool:
        """Save conversation message to local SQLite database"""
        try:
            with self.sqlite_session() as session:
                metadata_json = json.dumps(metadata or {})

                session.execute(text("""
                    INSERT INTO local_conversations
                    (user_id, conversation_id, message_type, content, language, metadata)
                    VALUES (:user_id, :conversation_id, :message_type, :content, :language, :metadata)
                """), {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "message_type": message_type,
                    "content": content,
                    "language": language,
                    "metadata": metadata_json
                })

                return True
        except Exception as e:
            logger.error(f"Error saving conversation locally: {e}")
            return False

    def get_recent_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent conversations from local SQLite database"""
        try:
            with self.sqlite_session() as session:
                results = session.execute(text("""
                    SELECT conversation_id, message_type, content, language, timestamp, metadata
                    FROM local_conversations
                    WHERE user_id = :user_id
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """), {"user_id": user_id, "limit": limit}).fetchall()

                return [
                    {
                        "conversation_id": row[0],
                        "message_type": row[1],
                        "content": row[2],
                        "language": row[3],
                        "timestamp": row[4],
                        "metadata": json.loads(row[5] or "{}")
                    }
                    for row in results
                ]
        except Exception as e:
            logger.error(f"Error getting recent conversations: {e}")
            return []

    def analyze_learning_patterns(self, user_id: str, language: str) -> Dict:
        """Analyze learning patterns using DuckDB analytics"""
        try:
            with self.duckdb_cursor() as conn:
                # Aggregate learning data
                query = """
                SELECT
                    COUNT(*) as total_sessions,
                    AVG(session_duration_minutes) as avg_session_duration,
                    SUM(words_learned) as total_words_learned,
                    AVG(pronunciation_accuracy) as avg_pronunciation_accuracy,
                    ARRAY_AGG(DISTINCT topics_covered) as all_topics
                FROM learning_analytics
                WHERE user_id = ? AND language = ?
                AND session_date >= CURRENT_DATE - INTERVAL '30 days'
                """

                result = conn.execute(query, [user_id, language]).fetchone()

                if result:
                    return {
                        "total_sessions": result[0] or 0,
                        "avg_session_duration": result[1] or 0,
                        "total_words_learned": result[2] or 0,
                        "avg_pronunciation_accuracy": result[3] or 0,
                        "topics_covered": result[4] or []
                    }
                return {}
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
            return {}

    def export_user_data(self, user_id: str) -> Dict:
        """Export all user data for backup or transfer"""
        try:
            data = {
                "profile": self.get_user_profile(user_id),
                "conversations": self.get_recent_conversations(user_id, limit=1000),
                "export_timestamp": datetime.now().isoformat()
            }

            # Add analytics data if available
            with self.duckdb_cursor() as conn:
                analytics_query = """
                SELECT * FROM learning_analytics WHERE user_id = ?
                """
                analytics_results = conn.execute(analytics_query, [user_id]).fetchall()
                data["analytics"] = [dict(zip([col[0] for col in conn.description], row))
                                   for row in analytics_results]

            return data
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return {}

    def delete_user_data_locally(self, user_id: str) -> bool:
        """Delete all local user data (GDPR compliance)"""
        try:
            # SQLite cleanup
            tables_to_clean = [
                "user_profiles", "user_settings", "local_conversations",
                "learning_progress", "cached_documents", "vocabulary_lists"
            ]

            with self.sqlite_session() as session:
                for table in tables_to_clean:
                    session.execute(text(f"DELETE FROM {table} WHERE user_id = :user_id"),
                                  {"user_id": user_id})

            # DuckDB cleanup
            with self.duckdb_cursor() as conn:
                duckdb_tables = [
                    "learning_analytics", "conversation_analysis",
                    "document_analytics", "performance_metrics"
                ]
                for table in duckdb_tables:
                    try:
                        conn.execute(f"DELETE FROM {table} WHERE user_id = ?", [user_id])
                    except Exception as e:
                        logger.warning(f"Error cleaning {table}: {e}")

            logger.info(f"User data deleted locally: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user data locally: {e}")
            return False

    def get_database_stats(self) -> Dict:
        """Get statistics about local databases"""
        stats = {"sqlite": {}, "duckdb": {}}

        try:
            # SQLite stats
            with self.sqlite_session() as session:
                sqlite_tables = [
                    "user_profiles", "user_settings", "local_conversations",
                    "learning_progress", "cached_documents", "vocabulary_lists"
                ]
                for table in sqlite_tables:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    stats["sqlite"][table] = result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting SQLite stats: {e}")

        try:
            # DuckDB stats
            with self.duckdb_cursor() as conn:
                duckdb_tables = [
                    "learning_analytics", "conversation_analysis",
                    "document_analytics", "performance_metrics"
                ]
                for table in duckdb_tables:
                    try:
                        result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                        stats["duckdb"][table] = result[0] if result else 0
                    except Exception:
                        stats["duckdb"][table] = 0
        except Exception as e:
            logger.error(f"Error getting DuckDB stats: {e}")

        return stats

    def close_connections(self):
        """Close all database connections"""
        if self._duckdb_conn:
            self._duckdb_conn.close()
            self._duckdb_conn = None

        if self._sqlite_engine:
            self._sqlite_engine.dispose()
            self._sqlite_engine = None
            self._sqlite_session_factory = None


# Global local database manager instance
local_db_manager = LocalDatabaseManager()

# Convenience functions


def initialize_local_databases():
    """Initialize local database schemas"""
    local_db_manager.initialize_local_schemas()


def get_local_db_manager():
    """Get local database manager instance"""
    return local_db_manager


def save_user_profile_locally(user_id: str, username: str, email: str = None, preferences: Dict = None):
    """Save user profile locally"""
    return local_db_manager.add_user_profile(user_id, username, email, preferences)


def get_user_profile_locally(user_id: str):
    """Get user profile from local storage"""
    return local_db_manager.get_user_profile(user_id)
