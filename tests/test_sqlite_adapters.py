"""
Tests for app/utils/sqlite_adapters.py
Coverage target: 34.55% → 100.00%
"""

import sqlite3
from datetime import date, datetime, timezone

import pytest

from app.utils.sqlite_adapters import (
    adapt_date_iso,
    adapt_datetime_iso,
    convert_date,
    convert_datetime,
    register_sqlite_adapters,
)


class TestAdaptDatetimeIso:
    """Test adapt_datetime_iso function"""

    def test_adapt_datetime_with_timezone(self):
        """Test adapting datetime with timezone info"""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        result = adapt_datetime_iso(dt)
        assert result == "2024-01-15T10:30:45+00:00"

    def test_adapt_datetime_naive_assumes_utc(self):
        """Test adapting naive datetime assumes UTC (covers line 28->31)"""
        # Naive datetime without timezone info
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = adapt_datetime_iso(dt)
        # Should add UTC timezone
        assert result == "2024-01-15T10:30:45+00:00"


class TestAdaptDateIso:
    """Test adapt_date_iso function"""

    def test_adapt_date(self):
        """Test adapting date to ISO format"""
        d = date(2024, 1, 15)
        result = adapt_date_iso(d)
        assert result == "2024-01-15"


class TestConvertDatetime:
    """Test convert_datetime function"""

    def test_convert_datetime_with_microseconds_and_z(self):
        """Test converting datetime with microseconds ending in Z"""
        # ISO 8601 with microseconds and Z timezone indicator
        timestamp_bytes = b"2024-01-15T10:30:45.123456Z"
        result = convert_datetime(timestamp_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45
        assert result.microsecond == 123456
        assert result.tzinfo is not None

    def test_convert_datetime_with_microseconds_and_offset(self):
        """Test converting datetime with microseconds and timezone offset"""
        timestamp_bytes = b"2024-01-15T10:30:45.123456+02:00"
        result = convert_datetime(timestamp_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.microsecond == 123456
        assert result.tzinfo is not None

    def test_convert_datetime_with_microseconds_no_tz(self):
        """Test converting datetime with microseconds but no timezone (assumes UTC)"""
        timestamp_bytes = b"2024-01-15T10:30:45.123456"
        result = convert_datetime(timestamp_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.microsecond == 123456
        assert result.tzinfo == timezone.utc  # Should assume UTC

    def test_convert_datetime_without_microseconds_with_z(self):
        """Test converting datetime without microseconds, ending in Z"""
        timestamp_bytes = b"2024-01-15T10:30:45Z"
        result = convert_datetime(timestamp_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.second == 45
        assert result.tzinfo is not None

    def test_convert_datetime_without_microseconds_with_offset(self):
        """Test converting datetime without microseconds but with timezone offset"""
        timestamp_bytes = b"2024-01-15T10:30:45+02:00"
        result = convert_datetime(timestamp_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.tzinfo is not None

    def test_convert_datetime_without_microseconds_no_tz(self):
        """Test converting datetime without microseconds or timezone (assumes UTC)"""
        timestamp_bytes = b"2024-01-15T10:30:45"
        result = convert_datetime(timestamp_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.tzinfo == timezone.utc  # Should assume UTC

    def test_convert_datetime_invalid_value_error(self):
        """Test converting invalid datetime returns None and logs warning (covers lines 90-93)"""
        # Invalid ISO 8601 format
        timestamp_bytes = b"invalid-datetime-format"
        result = convert_datetime(timestamp_bytes)

        # Should return None on ValueError
        assert result is None

    def test_convert_datetime_decode_error(self):
        """Test converting bytes that can't be decoded properly (covers exception handling)"""
        # Bytes with invalid UTF-8 encoding that will cause decoding issues
        # This tests the exception handling paths
        timestamp_bytes = b"\xff\xfe"  # Invalid UTF-8 bytes
        result = convert_datetime(timestamp_bytes)

        # Should return None when decoding fails
        assert result is None


class TestConvertDate:
    """Test convert_date function"""

    def test_convert_date_success(self):
        """Test converting date from bytes"""
        date_bytes = b"2024-01-15"
        result = convert_date(date_bytes)

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_convert_date_invalid_value_error(self):
        """Test converting invalid date returns None and logs warning (covers lines 106-108)"""
        # Invalid date format
        date_bytes = b"invalid-date"
        result = convert_date(date_bytes)

        # Should return None on ValueError
        assert result is None

    def test_convert_date_decode_error(self):
        """Test converting bytes that can't be decoded properly (covers exception handling)"""
        # Bytes with invalid UTF-8 encoding
        date_bytes = b"\xff\xfe"  # Invalid UTF-8 bytes
        result = convert_date(date_bytes)

        # Should return None when decoding fails
        assert result is None


class TestRegisterSqliteAdapters:
    """Test register_sqlite_adapters function"""

    def test_register_sqlite_adapters(self):
        """Test that register_sqlite_adapters registers all adapters"""
        # This function is called on module import, but we can call it again
        register_sqlite_adapters()

        # Test that adapters work by creating an in-memory database
        conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        # Create table with datetime and date columns
        cursor.execute("CREATE TABLE test (dt datetime, d date)")

        # Insert datetime and date
        test_datetime = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        test_date = date(2024, 1, 15)
        cursor.execute("INSERT INTO test VALUES (?, ?)", (test_datetime, test_date))

        # Retrieve and verify
        cursor.execute("SELECT dt, d FROM test")
        row = cursor.fetchone()

        retrieved_dt, retrieved_d = row

        # Verify datetime was adapted and converted correctly
        assert isinstance(retrieved_dt, datetime)
        assert retrieved_dt.year == 2024
        assert retrieved_dt.month == 1
        assert retrieved_dt.day == 15

        # Verify date was adapted and converted correctly
        assert isinstance(retrieved_d, date)
        assert retrieved_d.year == 2024
        assert retrieved_d.month == 1
        assert retrieved_d.day == 15

        conn.close()


class TestAutoRegistration:
    """Test that adapters are auto-registered on module import"""

    def test_adapters_registered_on_import(self):
        """Test that adapters are automatically registered when module is imported"""
        # The module auto-registers on import, so adapters should already be registered
        # We can verify this by using sqlite3 directly

        conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE test (dt datetime)")
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        cursor.execute("INSERT INTO test VALUES (?)", (dt,))

        cursor.execute("SELECT dt FROM test")
        result = cursor.fetchone()[0]

        # Should be a datetime object (not a string)
        assert isinstance(result, datetime)

        conn.close()
