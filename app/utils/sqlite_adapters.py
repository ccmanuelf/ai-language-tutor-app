"""
SQLite datetime adapters for Python 3.12+ compatibility

Python 3.12 deprecated the default datetime adapter for SQLite.
This module provides custom adapters to replace the deprecated defaults.

Usage:
    from app.utils.sqlite_adapters import register_sqlite_adapters
    register_sqlite_adapters()  # Call once at app startup
"""

import sqlite3
from datetime import datetime, date, timezone
from typing import Optional


def adapt_datetime_iso(val: datetime) -> str:
    """
    Adapt datetime.datetime to ISO 8601 string for SQLite storage.

    Args:
        val: datetime object to adapt

    Returns:
        ISO 8601 formatted string with timezone info
    """
    # Ensure timezone awareness
    if val.tzinfo is None:
        # Assume UTC for naive datetimes
        val = val.replace(tzinfo=timezone.utc)
    return val.isoformat()


def adapt_date_iso(val: date) -> str:
    """
    Adapt datetime.date to ISO 8601 string for SQLite storage.

    Args:
        val: date object to adapt

    Returns:
        ISO 8601 formatted date string
    """
    return val.isoformat()


def convert_datetime(val: bytes) -> Optional[datetime]:
    """
    Convert ISO 8601 string from SQLite to datetime.datetime.

    Args:
        val: bytes from SQLite containing ISO 8601 timestamp

    Returns:
        datetime object with timezone info, or None if invalid
    """
    try:
        # Decode bytes to string
        timestamp_str = val.decode("utf-8")

        # Parse ISO 8601 format
        # Handle both with and without microseconds
        if "." in timestamp_str:
            # Has microseconds
            if timestamp_str.endswith("Z"):
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            elif "+" in timestamp_str or timestamp_str.count("-") > 2:
                dt = datetime.fromisoformat(timestamp_str)
            else:
                # No timezone info, assume UTC
                dt = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
        else:
            # No microseconds
            if timestamp_str.endswith("Z"):
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            elif "+" in timestamp_str or timestamp_str.count("-") > 2:
                dt = datetime.fromisoformat(timestamp_str)
            else:
                # No timezone info, assume UTC
                dt = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)

        return dt
    except (ValueError, AttributeError) as e:
        # Log error but don't crash
        import logging

        logging.warning(f"Failed to convert datetime from SQLite: {val} - {e}")
        return None


def convert_date(val: bytes) -> Optional[date]:
    """
    Convert ISO 8601 date string from SQLite to datetime.date.

    Args:
        val: bytes from SQLite containing ISO 8601 date

    Returns:
        date object, or None if invalid
    """
    try:
        date_str = val.decode("utf-8")
        return date.fromisoformat(date_str)
    except (ValueError, AttributeError) as e:
        import logging

        logging.warning(f"Failed to convert date from SQLite: {val} - {e}")
        return None


def register_sqlite_adapters():
    """
    Register custom SQLite adapters for Python 3.12+ compatibility.

    This replaces the deprecated default datetime adapters with explicit
    ISO 8601 conversion that's compatible with Python 3.12 and later.

    Should be called once at application startup before any database operations.
    """
    # Register adapters (Python -> SQLite)
    sqlite3.register_adapter(datetime, adapt_datetime_iso)
    sqlite3.register_adapter(date, adapt_date_iso)

    # Register converters (SQLite -> Python)
    sqlite3.register_converter("datetime", convert_datetime)
    sqlite3.register_converter("timestamp", convert_datetime)
    sqlite3.register_converter("date", convert_date)


# Auto-register when module is imported
register_sqlite_adapters()
