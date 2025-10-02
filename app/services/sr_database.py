"""
Database utilities for Spaced Repetition system
Provides connection management and common query helpers
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime

# Register SQLite datetime adapters for Python 3.12+ compatibility
from app.utils.sqlite_adapters import register_sqlite_adapters

register_sqlite_adapters()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Shared database utilities for spaced repetition modules"""

    def __init__(self, db_path: str = "data/ai_language_tutor.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite Row to dictionary"""
        if row is None:
            return {}
        return dict(row)

    @staticmethod
    def serialize_json(data: Any) -> str:
        """Serialize data to JSON string for database storage"""
        if data is None:
            return "{}"
        if isinstance(data, str):
            return data
        return json.dumps(data)

    @staticmethod
    def deserialize_json(data: str) -> Any:
        """Deserialize JSON string from database"""
        if not data or data == "{}":
            return {}
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return {}

    @staticmethod
    def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
        """Convert datetime to ISO format string for database"""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        return dt.isoformat()

    @staticmethod
    def deserialize_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Convert ISO format string to datetime"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def safe_mean(values: List[float]) -> float:
        """Calculate mean with empty list protection"""
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def safe_percentage(numerator: float, denominator: float) -> float:
        """Calculate percentage with zero division protection"""
        if denominator == 0:
            return 0.0
        return (numerator / denominator) * 100.0

    def execute_query(
        self, query: str, params: tuple = (), fetch_one: bool = False
    ) -> Optional[Any]:
        """Execute query and return result(s)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)

                if fetch_one:
                    row = cursor.fetchone()
                    return self.row_to_dict(row) if row else None
                else:
                    rows = cursor.fetchall()
                    return [self.row_to_dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return None

    def execute_insert(self, query: str, params: tuple = ()) -> Optional[int]:
        """Execute insert and return lastrowid"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Database insert error: {e}")
            return None

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute update/delete and return success"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")
            return False


# Singleton instance for shared use
_db_manager_instance = None


def get_db_manager(db_path: str = "data/ai_language_tutor.db") -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager_instance
    if _db_manager_instance is None or _db_manager_instance.db_path != db_path:
        _db_manager_instance = DatabaseManager(db_path)
    return _db_manager_instance
