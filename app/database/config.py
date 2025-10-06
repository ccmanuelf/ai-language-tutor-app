""".
Database Configuration for AI Language Tutor App

This module provides database connection configurations for:
- SQLite (primary persistent storage)
- ChromaDB (vector storage for RAG)
- DuckDB (local analytics storage)

Features:
- Connection pooling and management
- Health monitoring
- Dependency injection for FastAPI
- Automatic reconnection handling
- Performance monitoring
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, Engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import chromadb
from chromadb.config import Settings as ChromaSettings
import duckdb

# Register SQLite datetime adapters for Python 3.12+ compatibility
from app.utils.sqlite_adapters import register_sqlite_adapters

register_sqlite_adapters()
from pydantic_settings import BaseSettings  # noqa: E402 - Required after warnings filter setup
from pydantic import ConfigDict  # noqa: E402 - Required after warnings filter setup
from fastapi import HTTPException  # noqa: E402 - Required after warnings filter setup
from app.core.config import get_settings  # noqa: E402 - Required after warnings filter setup

logger = logging.getLogger(__name__)


class DatabaseConfig(BaseSettings):
    """Database configuration settings"""

    # ChromaDB Configuration
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    CHROMADB_PERSIST_DIRECTORY: str = "./data/chromadb"

    # DuckDB/SQLite Configuration
    DUCKDB_PATH: str = "./data/local.duckdb"
    SQLITE_PATH: str = "./data/local.sqlite"

    # Connection Pool Settings
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30

    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def sqlite_url(self) -> str:
        """Generate SQLite connection URL"""
        # Use the same database file as specified in .env
        from app.core.config import get_settings

        settings = get_settings()
        if settings.DATABASE_URL.startswith("sqlite://"):
            return settings.DATABASE_URL
        else:
            return f"sqlite:///{self.SQLITE_PATH}"


class DatabaseManager:
    """Centralized database connection manager with enhanced features"""

    def __init__(self):
        self.config = DatabaseConfig()
        self._sqlite_engine: Optional[Engine] = None
        self._chromadb_client = None
        self._duckdb_connection = None
        self._session_factories = {}
        self._connection_stats = {
            "sqlite": {"connects": 0, "errors": 0, "last_check": None},
            "chromadb": {"connects": 0, "errors": 0, "last_check": None},
            "duckdb": {"connects": 0, "errors": 0, "last_check": None},
        }
        self._ensure_data_directories()
        self._setup_event_listeners()

    def _ensure_data_directories(self):
        """Create necessary data directories"""
        os.makedirs("./data", exist_ok=True)
        os.makedirs(self.config.CHROMADB_PERSIST_DIRECTORY, exist_ok=True)

    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for connection monitoring"""

        @event.listens_for(Engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Log database connections"""
            logger.debug("Database connection established")

        @event.listens_for(Engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Track connection checkouts"""
            pass  # Could add connection tracking here

        @event.listens_for(Engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Track connection checkins"""
            pass  # Could add connection tracking here

    def get_primary_engine(self) -> Engine:
        """Get primary database engine (SQLite)"""
        logger.info("Using SQLite as primary database")
        return self.sqlite_engine

    @property
    def sqlite_engine(self) -> Engine:
        """Get or create SQLite engine with optimized connection pooling"""
        if self._sqlite_engine is None:
            # Use QueuePool for better performance with multiple connections
            # StaticPool is only suitable for single-threaded applications
            self._sqlite_engine = create_engine(
                self.config.sqlite_url,
                poolclass=QueuePool,
                pool_size=self.config.POOL_SIZE,  # 10 connections
                max_overflow=self.config.MAX_OVERFLOW,  # 20 additional connections
                pool_timeout=self.config.POOL_TIMEOUT,  # 30 seconds
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,  # Recycle connections after 1 hour
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20,
                    # SQLite performance optimizations
                    "isolation_level": None,  # Autocommit mode for better concurrency
                },
                echo=get_settings().DEBUG,
                # Additional performance settings
                execution_options={
                    "compiled_cache": {},  # Enable query compilation caching
                },
            )
        return self._sqlite_engine

    @property
    def chromadb_client(self):
        """Get or create ChromaDB client"""
        if self._chromadb_client is None:
            self._chromadb_client = chromadb.PersistentClient(
                path=self.config.CHROMADB_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
        return self._chromadb_client

    @property
    def duckdb_connection(self):
        """Get or create DuckDB connection"""
        if self._duckdb_connection is None:
            self._duckdb_connection = duckdb.connect(self.config.DUCKDB_PATH)
        return self._duckdb_connection

    def get_sqlite_session(self) -> Session:
        """Create a new SQLite session"""
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.sqlite_engine
        )
        return SessionLocal()

    def test_chromadb_connection(self) -> Dict[str, Any]:
        """Test ChromaDB connection with health details"""
        start_time = time.time()
        try:
            heartbeat = self.chromadb_client.heartbeat()
            response_time = time.time() - start_time
            self._connection_stats["chromadb"]["last_check"] = time.time()

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "heartbeat": heartbeat,
                "collections_count": len(self.chromadb_client.list_collections()),
            }
        except Exception as e:
            self._connection_stats["chromadb"]["errors"] += 1
            response_time = time.time() - start_time
            logger.error(f"ChromaDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round(response_time * 1000, 2),
            }

    def test_sqlite_connection(self) -> Dict[str, Any]:
        """Test SQLite connection with health details"""
        start_time = time.time()
        try:
            with self.sqlite_engine.connect() as conn:
                result = conn.execute(
                    text("SELECT 1 as test, datetime('now') as timestamp")
                )
                row = result.fetchone()

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": row[1] if row else None,
                "database_path": str(self.config.sqlite_url),
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"SQLite health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round(response_time * 1000, 2),
            }

    def test_duckdb_connection(self) -> Dict[str, Any]:
        """Test DuckDB connection with health details"""
        start_time = time.time()
        try:
            result = self.duckdb_connection.execute(
                "SELECT 1 as test, current_timestamp as timestamp"
            ).fetchone()
            response_time = time.time() - start_time
            self._connection_stats["duckdb"]["last_check"] = time.time()

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": str(result[1]) if result else None,
                "database_path": str(self.config.DUCKDB_PATH),
            }
        except Exception as e:
            self._connection_stats["duckdb"]["errors"] += 1
            response_time = time.time() - start_time
            logger.error(f"DuckDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round(response_time * 1000, 2),
            }

    def get_primary_database_type(self) -> str:
        """Determine the primary database type (always SQLite)"""
        return "sqlite"

    def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Test all database connections with comprehensive health data"""
        results = {}

        # Always test ChromaDB and DuckDB
        results["chromadb"] = self.test_chromadb_connection()
        results["duckdb"] = self.test_duckdb_connection()

        # Test SQLite (primary database)
        results["sqlite"] = self.test_sqlite_connection()
        logger.info("Using SQLite as primary database")

        return results

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics and monitoring data"""
        pool_status = None
        if self._sqlite_engine:
            # StaticPool doesn't have size/checked_out/checked_in methods
            # Only QueuePool has these methods
            pool_type = type(self.sqlite_engine.pool).__name__
            if pool_type == "StaticPool":
                pool_status = {
                    "pool_type": "StaticPool",
                    "note": "StaticPool maintains single connection, no pool metrics",
                }
            else:
                # QueuePool or other pool types
                try:
                    pool_status = {
                        "pool_type": pool_type,
                        "size": self.sqlite_engine.pool.size(),
                        "checked_out": self.sqlite_engine.pool.checkedout(),
                        "checked_in": self.sqlite_engine.pool.checkedin(),
                    }
                except AttributeError:
                    pool_status = {
                        "pool_type": pool_type,
                        "note": "Pool metrics not available for this pool type",
                    }

        return {
            "connection_stats": self._connection_stats.copy(),
            "pool_status": {"sqlite": pool_status},
            "health_summary": self.get_health_summary(),
        }

    def get_health_summary(self) -> Dict[str, str]:
        """Get overall health summary"""
        health_checks = self.test_all_connections()
        summary = {}

        for db_name, check_result in health_checks.items():
            summary[db_name] = check_result.get("status", "unknown")

        # Overall status
        all_healthy = all(status == "healthy" for status in summary.values())
        summary["overall"] = "healthy" if all_healthy else "degraded"

        return summary

    def reset_connection_stats(self):
        """Reset connection statistics"""
        for db_name in self._connection_stats:
            self._connection_stats[db_name] = {
                "connects": 0,
                "errors": 0,
                "last_check": None,
            }
        logger.info("Connection statistics reset")

    def close_all_connections(self):
        """Close all database connections"""
        if self._sqlite_engine:
            self._sqlite_engine.dispose()
            self._sqlite_engine = None

        if self._duckdb_connection:
            self._duckdb_connection.close()
            self._duckdb_connection = None

        # ChromaDB client doesn't need explicit closing


# Global database manager instance
db_manager = DatabaseManager()


# FastAPI Dependencies
def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for primary database sessions"""
    # Use the primary SQLite engine
    engine = db_manager.get_primary_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@contextmanager
def get_db_session_context():
    """FastAPI dependency for SQLite sessions with context management"""
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_manager.sqlite_engine
    )
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_chromadb_client():
    """FastAPI dependency for ChromaDB client"""
    return db_manager.chromadb_client


def get_duckdb_connection():
    """FastAPI dependency for DuckDB connection"""
    return db_manager.duckdb_connection


def get_database_health():
    """FastAPI dependency for database health status"""
    return db_manager.get_health_summary()


# Health check endpoint helper
async def check_database_health():
    """Async health check for all databases"""
    try:
        health_data = db_manager.test_all_connections()
        overall_healthy = all(
            check.get("status") == "healthy" for check in health_data.values()
        )

        if not overall_healthy:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Database health check failed",
                    "details": health_data,
                },
            )

        return {"status": "healthy", "databases": health_data}
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        raise HTTPException(
            status_code=503,
            detail={"message": "Database health check failed", "error": str(e)},
        )


# Convenience functions for quick access
def get_primary_db_session() -> Session:
    """Get a session for the primary database (SQLite)"""
    engine = db_manager.get_primary_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def get_sqlite_session() -> Session:
    """Get a SQLite session"""
    return db_manager.get_sqlite_session()


def get_chromadb_client():
    """Get ChromaDB client"""
    return db_manager.chromadb_client


def get_duckdb_connection():
    """Get DuckDB connection"""
    return db_manager.duckdb_connection
