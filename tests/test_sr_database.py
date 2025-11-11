"""
Comprehensive tests for sr_database module
Tests DatabaseManager and database utility functions
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from app.services.sr_database import DatabaseManager, get_db_manager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    # Create simple test table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value INTEGER,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def db_manager(temp_db):
    """Create DatabaseManager instance with temp database"""
    return DatabaseManager(db_path=temp_db)


# =============================================================================
# CATEGORY 1: Initialization Tests (2 tests)
# =============================================================================


def test_database_manager_init_default_path():
    """Test DatabaseManager initialization with default path"""
    manager = DatabaseManager()
    assert manager.db_path == "data/ai_language_tutor.db"


def test_database_manager_init_custom_path():
    """Test DatabaseManager initialization with custom path"""
    custom_path = "/custom/path/test.db"
    manager = DatabaseManager(db_path=custom_path)
    assert manager.db_path == custom_path


# =============================================================================
# CATEGORY 2: Connection Management Tests (3 tests)
# =============================================================================


def test_get_connection_success(db_manager):
    """Test successful database connection"""
    conn = db_manager.get_connection()

    assert conn is not None
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory == sqlite3.Row

    # Verify connection works
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1

    conn.close()


def test_get_connection_row_factory(db_manager):
    """Test connection has row factory for dict-like access"""
    conn = db_manager.get_connection()

    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 42))
    conn.commit()

    cursor.execute("SELECT name, value FROM test_table WHERE name = ?", ("test",))
    row = cursor.fetchone()

    # Row should support dict-like access
    assert row["name"] == "test"
    assert row["value"] == 42

    conn.close()


def test_get_connection_multiple_calls(db_manager):
    """Test multiple connection calls return independent connections"""
    conn1 = db_manager.get_connection()
    conn2 = db_manager.get_connection()

    # Different connection objects
    assert conn1 is not conn2

    conn1.close()
    conn2.close()


# =============================================================================
# CATEGORY 3: Row Conversion Tests (3 tests)
# =============================================================================


def test_row_to_dict_valid_row(db_manager):
    """Test converting valid SQLite Row to dictionary"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 123))
    conn.commit()

    cursor.execute("SELECT id, name, value FROM test_table WHERE name = ?", ("test",))
    row = cursor.fetchone()

    result = DatabaseManager.row_to_dict(row)

    assert isinstance(result, dict)
    assert result["name"] == "test"
    assert result["value"] == 123
    assert "id" in result

    conn.close()


def test_row_to_dict_none_row():
    """Test converting None row returns empty dict"""
    result = DatabaseManager.row_to_dict(None)
    assert result == {}


def test_row_to_dict_empty_row(db_manager):
    """Test converting row with NULL values"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", None))
    conn.commit()

    cursor.execute("SELECT name, value FROM test_table WHERE name = ?", ("test",))
    row = cursor.fetchone()

    result = DatabaseManager.row_to_dict(row)

    assert isinstance(result, dict)
    assert result["name"] == "test"
    assert result["value"] is None

    conn.close()


# =============================================================================
# CATEGORY 4: JSON Serialization Tests (5 tests)
# =============================================================================


def test_serialize_json_dict():
    """Test serializing dictionary to JSON string"""
    data = {"key": "value", "number": 42, "nested": {"inner": "data"}}
    result = DatabaseManager.serialize_json(data)

    assert isinstance(result, str)
    assert json.loads(result) == data


def test_serialize_json_list():
    """Test serializing list to JSON string"""
    data = ["item1", "item2", 123, {"key": "value"}]
    result = DatabaseManager.serialize_json(data)

    assert isinstance(result, str)
    assert json.loads(result) == data


def test_serialize_json_none():
    """Test serializing None returns empty JSON object"""
    result = DatabaseManager.serialize_json(None)
    assert result == "{}"


def test_serialize_json_string_passthrough():
    """Test that string input is passed through unchanged"""
    json_string = '{"already": "json"}'
    result = DatabaseManager.serialize_json(json_string)
    assert result == json_string


def test_serialize_json_complex_types():
    """Test serializing various data types"""
    data = {
        "string": "text",
        "int": 42,
        "float": 3.14,
        "bool": True,
        "null": None,
        "list": [1, 2, 3],
        "nested": {"deep": {"value": "here"}},
    }
    result = DatabaseManager.serialize_json(data)

    assert isinstance(result, str)
    deserialized = json.loads(result)
    assert deserialized == data


# =============================================================================
# CATEGORY 5: JSON Deserialization Tests (5 tests)
# =============================================================================


def test_deserialize_json_valid_dict():
    """Test deserializing valid JSON string to dict"""
    json_string = '{"key": "value", "number": 42}'
    result = DatabaseManager.deserialize_json(json_string)

    assert result == {"key": "value", "number": 42}


def test_deserialize_json_valid_list():
    """Test deserializing valid JSON array"""
    json_string = '["item1", "item2", 123]'
    result = DatabaseManager.deserialize_json(json_string)

    assert result == ["item1", "item2", 123]


def test_deserialize_json_empty_string():
    """Test deserializing empty string returns empty dict"""
    result = DatabaseManager.deserialize_json("")
    assert result == {}


def test_deserialize_json_empty_object():
    """Test deserializing empty JSON object"""
    result = DatabaseManager.deserialize_json("{}")
    assert result == {}


def test_deserialize_json_invalid():
    """Test deserializing invalid JSON returns empty dict"""
    invalid_json = "not valid json {{{["
    result = DatabaseManager.deserialize_json(invalid_json)
    assert result == {}


def test_deserialize_json_none_type():
    """Test deserializing None returns empty dict (TypeError handling)"""
    result = DatabaseManager.deserialize_json(None)
    assert result == {}


# =============================================================================
# CATEGORY 6: Datetime Serialization Tests (4 tests)
# =============================================================================


def test_serialize_datetime_valid():
    """Test serializing datetime to ISO format string"""
    dt = datetime(2025, 11, 14, 10, 30, 45)
    result = DatabaseManager.serialize_datetime(dt)

    assert result == "2025-11-14T10:30:45"


def test_serialize_datetime_none():
    """Test serializing None datetime returns None"""
    result = DatabaseManager.serialize_datetime(None)
    assert result is None


def test_serialize_datetime_string_passthrough():
    """Test that string input is passed through unchanged"""
    date_string = "2025-11-14T10:30:45"
    result = DatabaseManager.serialize_datetime(date_string)
    assert result == date_string


def test_serialize_datetime_with_microseconds():
    """Test serializing datetime with microseconds"""
    dt = datetime(2025, 11, 14, 10, 30, 45, 123456)
    result = DatabaseManager.serialize_datetime(dt)

    assert "2025-11-14T10:30:45" in result
    assert "123456" in result


# =============================================================================
# CATEGORY 7: Datetime Deserialization Tests (5 tests)
# =============================================================================


def test_deserialize_datetime_valid_iso():
    """Test deserializing valid ISO format string"""
    iso_string = "2025-11-14T10:30:45"
    result = DatabaseManager.deserialize_datetime(iso_string)

    assert isinstance(result, datetime)
    assert result.year == 2025
    assert result.month == 11
    assert result.day == 14
    assert result.hour == 10
    assert result.minute == 30
    assert result.second == 45


def test_deserialize_datetime_with_microseconds():
    """Test deserializing ISO string with microseconds"""
    iso_string = "2025-11-14T10:30:45.123456"
    result = DatabaseManager.deserialize_datetime(iso_string)

    assert isinstance(result, datetime)
    assert result.microsecond == 123456


def test_deserialize_datetime_none():
    """Test deserializing None returns None"""
    result = DatabaseManager.deserialize_datetime(None)
    assert result is None


def test_deserialize_datetime_empty_string():
    """Test deserializing empty string returns None"""
    result = DatabaseManager.deserialize_datetime("")
    assert result is None


def test_deserialize_datetime_invalid_format():
    """Test deserializing invalid format returns None (ValueError handling)"""
    invalid_string = "not a valid date"
    result = DatabaseManager.deserialize_datetime(invalid_string)
    assert result is None


def test_deserialize_datetime_none_type():
    """Test deserializing None returns None (TypeError handling)"""
    result = DatabaseManager.deserialize_datetime(None)
    assert result is None


# =============================================================================
# CATEGORY 8: Safe Mean Tests (3 tests)
# =============================================================================


def test_safe_mean_normal_values():
    """Test calculating mean with normal values"""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    result = DatabaseManager.safe_mean(values)
    assert result == 30.0


def test_safe_mean_empty_list():
    """Test calculating mean with empty list returns 0.0"""
    result = DatabaseManager.safe_mean([])
    assert result == 0.0


def test_safe_mean_single_value():
    """Test calculating mean with single value"""
    result = DatabaseManager.safe_mean([42.5])
    assert result == 42.5


def test_safe_mean_mixed_values():
    """Test calculating mean with mixed positive/negative values"""
    values = [10.0, -5.0, 20.0, -10.0, 15.0]
    result = DatabaseManager.safe_mean(values)
    assert result == 6.0


# =============================================================================
# CATEGORY 9: Safe Percentage Tests (4 tests)
# =============================================================================


def test_safe_percentage_normal_calculation():
    """Test calculating percentage with normal values"""
    result = DatabaseManager.safe_percentage(25, 100)
    assert result == 25.0


def test_safe_percentage_zero_denominator():
    """Test calculating percentage with zero denominator returns 0.0"""
    result = DatabaseManager.safe_percentage(10, 0)
    assert result == 0.0


def test_safe_percentage_100_percent():
    """Test calculating 100%"""
    result = DatabaseManager.safe_percentage(100, 100)
    assert result == 100.0


def test_safe_percentage_fractional():
    """Test calculating fractional percentage"""
    result = DatabaseManager.safe_percentage(33, 100)
    assert result == 33.0

    result = DatabaseManager.safe_percentage(1, 3)
    assert abs(result - 33.333333) < 0.0001


# =============================================================================
# CATEGORY 10: Execute Query Tests (7 tests)
# =============================================================================


def test_execute_query_fetch_one_success(db_manager):
    """Test execute_query with fetch_one returns single row"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test1", 100))
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test2", 200))
    conn.commit()
    conn.close()

    query = "SELECT name, value FROM test_table WHERE name = ?"
    result = db_manager.execute_query(query, ("test1",), fetch_one=True)

    assert result is not None
    assert isinstance(result, dict)
    assert result["name"] == "test1"
    assert result["value"] == 100


def test_execute_query_fetch_all_success(db_manager):
    """Test execute_query with fetch_all returns multiple rows"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test1", 100))
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test2", 200))
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test3", 300))
    conn.commit()
    conn.close()

    query = "SELECT name, value FROM test_table ORDER BY value"
    result = db_manager.execute_query(query)

    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["value"] == 100
    assert result[1]["value"] == 200
    assert result[2]["value"] == 300


def test_execute_query_fetch_one_no_results(db_manager):
    """Test execute_query with fetch_one returns None when no results"""
    query = "SELECT name, value FROM test_table WHERE name = ?"
    result = db_manager.execute_query(query, ("nonexistent",), fetch_one=True)

    assert result is None


def test_execute_query_fetch_all_empty_results(db_manager):
    """Test execute_query with fetch_all returns empty list when no results"""
    query = "SELECT name, value FROM test_table WHERE value > ?"
    result = db_manager.execute_query(query, (9999,))

    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0


def test_execute_query_with_no_params(db_manager):
    """Test execute_query without parameters"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 42))
    conn.commit()
    conn.close()

    query = "SELECT COUNT(*) as count FROM test_table"
    result = db_manager.execute_query(query, fetch_one=True)

    assert result is not None
    assert result["count"] == 1


def test_execute_query_error_handling(db_manager):
    """Test execute_query handles SQLite errors gracefully"""
    # Invalid SQL query
    query = "SELECT * FROM nonexistent_table"
    result = db_manager.execute_query(query)

    assert result is None


def test_execute_query_error_handling_fetch_one(db_manager):
    """Test execute_query handles SQLite errors gracefully with fetch_one"""
    # Invalid SQL query
    query = "SELECT * FROM nonexistent_table WHERE id = ?"
    result = db_manager.execute_query(query, (1,), fetch_one=True)

    assert result is None


# =============================================================================
# CATEGORY 11: Execute Insert Tests (4 tests)
# =============================================================================


def test_execute_insert_success(db_manager):
    """Test execute_insert successfully inserts row and returns lastrowid"""
    query = "INSERT INTO test_table (name, value) VALUES (?, ?)"
    lastrowid = db_manager.execute_insert(query, ("test_insert", 999))

    assert lastrowid is not None
    assert isinstance(lastrowid, int)
    assert lastrowid > 0

    # Verify insertion
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, value FROM test_table WHERE id = ?", (lastrowid,))
    row = cursor.fetchone()
    assert row["name"] == "test_insert"
    assert row["value"] == 999
    conn.close()


def test_execute_insert_multiple_inserts(db_manager):
    """Test multiple execute_insert calls return different lastrowids"""
    query = "INSERT INTO test_table (name, value) VALUES (?, ?)"

    id1 = db_manager.execute_insert(query, ("insert1", 100))
    id2 = db_manager.execute_insert(query, ("insert2", 200))
    id3 = db_manager.execute_insert(query, ("insert3", 300))

    assert id1 != id2 != id3
    assert id1 < id2 < id3


def test_execute_insert_error_handling(db_manager):
    """Test execute_insert handles SQLite errors gracefully"""
    # Invalid table name
    query = "INSERT INTO nonexistent_table (name) VALUES (?)"
    result = db_manager.execute_insert(query, ("test",))

    assert result is None


def test_execute_insert_constraint_violation(db_manager):
    """Test execute_insert handles constraint violations"""
    # First insert
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE UNIQUE INDEX idx_name ON test_table(name)")
    conn.commit()
    conn.close()

    query = "INSERT INTO test_table (name, value) VALUES (?, ?)"
    db_manager.execute_insert(query, ("unique_name", 100))

    # Try to insert duplicate
    result = db_manager.execute_insert(query, ("unique_name", 200))
    assert result is None


# =============================================================================
# CATEGORY 12: Execute Update Tests (5 tests)
# =============================================================================


def test_execute_update_success(db_manager):
    """Test execute_update successfully updates row"""
    # Insert test data
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 100))
    conn.commit()
    conn.close()

    # Update
    query = "UPDATE test_table SET value = ? WHERE name = ?"
    result = db_manager.execute_update(query, (200, "test"))

    assert result is True

    # Verify update
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM test_table WHERE name = ?", ("test",))
    row = cursor.fetchone()
    assert row["value"] == 200
    conn.close()


def test_execute_update_delete_success(db_manager):
    """Test execute_update works for DELETE statements"""
    # Insert test data
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_table (name, value) VALUES (?, ?)", ("to_delete", 999)
    )
    conn.commit()
    conn.close()

    # Delete
    query = "DELETE FROM test_table WHERE name = ?"
    result = db_manager.execute_update(query, ("to_delete",))

    assert result is True

    # Verify deletion
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as count FROM test_table WHERE name = ?", ("to_delete",)
    )
    row = cursor.fetchone()
    assert row["count"] == 0
    conn.close()


def test_execute_update_no_rows_affected(db_manager):
    """Test execute_update returns True even when no rows affected"""
    query = "UPDATE test_table SET value = ? WHERE name = ?"
    result = db_manager.execute_update(query, (999, "nonexistent"))

    # Still returns True (no error occurred)
    assert result is True


def test_execute_update_error_handling(db_manager):
    """Test execute_update handles SQLite errors gracefully"""
    # Invalid table name
    query = "UPDATE nonexistent_table SET value = ?"
    result = db_manager.execute_update(query, (100,))

    assert result is False


def test_execute_update_multiple_rows(db_manager):
    """Test execute_update can update multiple rows"""
    # Insert test data
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test1", 100))
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test2", 100))
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test3", 100))
    conn.commit()
    conn.close()

    # Update all rows with value 100
    query = "UPDATE test_table SET value = ? WHERE value = ?"
    result = db_manager.execute_update(query, (999, 100))

    assert result is True

    # Verify all updated
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM test_table WHERE value = ?", (999,))
    row = cursor.fetchone()
    assert row["count"] == 3
    conn.close()


# =============================================================================
# CATEGORY 13: Singleton Pattern Tests (3 tests)
# =============================================================================


def test_get_db_manager_returns_instance():
    """Test get_db_manager returns DatabaseManager instance"""
    manager = get_db_manager()

    assert manager is not None
    assert isinstance(manager, DatabaseManager)


def test_get_db_manager_singleton_same_instance():
    """Test get_db_manager returns same instance on multiple calls"""
    # Reset singleton
    import app.services.sr_database

    app.services.sr_database._db_manager_instance = None

    manager1 = get_db_manager()
    manager2 = get_db_manager()

    assert manager1 is manager2


def test_get_db_manager_different_path_creates_new_instance():
    """Test get_db_manager creates new instance for different db_path"""
    # Reset singleton
    import app.services.sr_database

    app.services.sr_database._db_manager_instance = None

    manager1 = get_db_manager("data/test1.db")
    manager2 = get_db_manager("data/test2.db")

    assert manager1 is not manager2
    assert manager1.db_path == "data/test1.db"
    assert manager2.db_path == "data/test2.db"


def test_get_db_manager_default_path():
    """Test get_db_manager uses default path when not specified"""
    # Reset singleton
    import app.services.sr_database

    app.services.sr_database._db_manager_instance = None

    manager = get_db_manager()
    assert manager.db_path == "data/ai_language_tutor.db"
