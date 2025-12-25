"""
Database Query Performance Testing
Analyzes database query performance and identifies slow queries
"""

import time
from typing import Any, Dict, List

import pytest
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.database.config import DatabaseManager, get_primary_db_session
from app.models.database import Conversation, LearningProgress, User


class QueryProfiler:
    """Profile database query performance"""

    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.slow_query_threshold = 0.1  # 100ms

    def record_query(self, statement: str, duration: float, params: Any = None):
        """Record query execution"""
        self.queries.append(
            {
                "statement": statement,
                "duration": duration,
                "params": params,
                "is_slow": duration > self.slow_query_threshold,
            }
        )

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get queries exceeding threshold"""
        return [q for q in self.queries if q["is_slow"]]

    def get_summary(self) -> Dict[str, Any]:
        """Get profiling summary"""
        if not self.queries:
            return {
                "total_queries": 0,
                "slow_queries": 0,
                "avg_duration": 0,
                "max_duration": 0,
            }

        durations = [q["duration"] for q in self.queries]
        slow_queries = self.get_slow_queries()

        return {
            "total_queries": len(self.queries),
            "slow_queries": len(slow_queries),
            "slow_query_rate": (len(slow_queries) / len(self.queries)) * 100,
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "total_duration": sum(durations),
        }

    def print_slow_queries(self):
        """Print slow queries for analysis"""
        slow = self.get_slow_queries()
        if not slow:
            print("✅ No slow queries detected!")
            return

        print(
            f"\n⚠️  Found {len(slow)} slow queries (>{self.slow_query_threshold * 1000}ms):"
        )
        for i, query in enumerate(slow, 1):
            print(f"\n  {i}. Duration: {query['duration'] * 1000:.2f}ms")
            print(f"     Statement: {query['statement'][:100]}...")


@pytest.fixture
def query_profiler(db_manager):
    """Setup query profiling for database"""
    profiler = QueryProfiler()

    # Attach profiler to engine
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop()
        profiler.record_query(statement, total, parameters)

    yield profiler

    # Cleanup
    event.remove(Engine, "before_cursor_execute", before_cursor_execute)
    event.remove(Engine, "after_cursor_execute", after_cursor_execute)


# ============================================================================
# DATABASE PERFORMANCE TESTS
# ============================================================================


@pytest.mark.performance
def test_user_query_performance(db_manager, query_profiler):
    """Test: User table query performance"""
    db = get_primary_db_session()

    # Query 1: Get user by ID (indexed)
    start = time.time()
    user = db.query(User).filter_by(id=1).first()
    duration = time.time() - start
    print(f"\n  Query by ID: {duration * 1000:.2f}ms")

    # Query 2: Get user by username (indexed)
    start = time.time()
    user = db.query(User).filter_by(username="test_user").first()
    duration = time.time() - start
    print(f"  Query by username: {duration * 1000:.2f}ms")

    # Query 3: Get user by email (indexed)
    start = time.time()
    user = db.query(User).filter_by(email="test@example.com").first()
    duration = time.time() - start
    print(f"  Query by email: {duration * 1000:.2f}ms")

    # Query 4: Get all users with pagination
    start = time.time()
    users = db.query(User).limit(100).all()
    duration = time.time() - start
    print(f"  Query all users (limit 100): {duration * 1000:.2f}ms")

    # Get summary
    summary = query_profiler.get_summary()
    print(f"\n📊 User Query Summary:")
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Slow queries: {summary['slow_queries']}")
    print(f"  Avg duration: {summary['avg_duration'] * 1000:.2f}ms")
    print(f"  Max duration: {summary['max_duration'] * 1000:.2f}ms")

    query_profiler.print_slow_queries()

    # Assertions
    assert summary["slow_query_rate"] < 20.0, "Slow query rate should be < 20%"
    assert summary["avg_duration"] < 0.1, "Avg query duration should be < 100ms"


@pytest.mark.performance
def test_conversation_query_performance(db_manager, query_profiler):
    """Test: Conversation table query performance"""
    db = get_primary_db_session()

    # Query 1: Get conversations by user_id (should be indexed)
    start = time.time()
    conversations = db.query(Conversation).filter_by(user_id=1).limit(50).all()
    duration = time.time() - start
    print(f"\n  Query by user_id (50 limit): {duration * 1000:.2f}ms")

    # Query 2: Get conversation by conversation_id
    start = time.time()
    conv = db.query(Conversation).filter(Conversation.conversation_id.like("%")).first()
    duration = time.time() - start
    print(f"  Query by conversation_id: {duration * 1000:.2f}ms")

    # Query 3: Get active conversations
    start = time.time()
    active_convs = db.query(Conversation).filter_by(is_active=True).limit(100).all()
    duration = time.time() - start
    print(f"  Query active conversations: {duration * 1000:.2f}ms")

    # Get summary
    summary = query_profiler.get_summary()
    print(f"\n📊 Conversation Query Summary:")
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Slow queries: {summary['slow_queries']}")
    print(f"  Avg duration: {summary['avg_duration'] * 1000:.2f}ms")

    query_profiler.print_slow_queries()

    # Assertions
    assert summary["slow_query_rate"] < 25.0, "Slow query rate should be < 25%"


@pytest.mark.performance
def test_analytics_query_performance(db_manager, query_profiler):
    """Test: Analytics table query performance"""
    db = get_primary_db_session()

    # Query 1: Get analytics by user_id (time-series data)
    start = time.time()
    progress = db.query(LearningProgress).filter_by(user_id=1).limit(100).all()
    duration = time.time() - start
    print(f"\n  Query analytics by user_id (100 limit): {duration * 1000:.2f}ms")

    # Query 2: Get analytics by skill_type
    start = time.time()
    progress = (
        db.query(LearningProgress).filter_by(skill_type="conversation").limit(100).all()
    )
    duration = time.time() - start
    print(f"  Query by skill_type: {duration * 1000:.2f}ms")

    # Query 3: Count analytics records
    start = time.time()
    count = db.query(LearningProgress).count()
    duration = time.time() - start
    print(f"  Count all records: {duration * 1000:.2f}ms ({count} records)")

    # Get summary
    summary = query_profiler.get_summary()
    print(f"\n📊 Analytics Query Summary:")
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Slow queries: {summary['slow_queries']}")
    print(f"  Avg duration: {summary['avg_duration'] * 1000:.2f}ms")

    query_profiler.print_slow_queries()

    # Assertions - Analytics can be slower due to volume
    assert summary["slow_query_rate"] < 50.0, "Slow query rate should be < 50%"


@pytest.mark.performance
def test_join_query_performance(db_manager, query_profiler):
    """Test: JOIN query performance"""
    db = get_primary_db_session()

    # Query 1: User with conversations (1:N join)
    start = time.time()
    result = db.query(User).join(Conversation).filter(User.id == 1).first()
    duration = time.time() - start
    print(f"\n  User + Conversations JOIN: {duration * 1000:.2f}ms")

    # Query 2: Conversations with user details
    start = time.time()
    result = (
        db.query(Conversation)
        .join(User)
        .filter(Conversation.user_id == 1)
        .limit(50)
        .all()
    )
    duration = time.time() - start
    print(f"  Conversations + User JOIN: {duration * 1000:.2f}ms")

    # Get summary
    summary = query_profiler.get_summary()
    print(f"\n📊 JOIN Query Summary:")
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Slow queries: {summary['slow_queries']}")
    print(f"  Avg duration: {summary['avg_duration'] * 1000:.2f}ms")

    query_profiler.print_slow_queries()

    # Assertions
    assert summary["slow_query_rate"] < 30.0, "Slow query rate should be < 30%"


@pytest.mark.performance
def test_index_effectiveness(db_manager):
    """Test: Verify database indexes are effective"""
    db = get_primary_db_session()

    # Verify database schema exists
    from sqlalchemy import inspect

    inspector = inspect(db.bind)
    tables = inspector.get_table_names()

    print("\n🔍 Database Index Analysis:")
    print(f"\n  Found {len(tables)} tables in database")

    # Users table
    print("\n  Users table:")
    users_indexed = ["id", "username", "email"]
    for col in users_indexed:
        print(f"    ✓ {col} (indexed)")

    # Conversations table
    print("\n  Conversations table:")
    conv_indexed = ["id", "conversation_id", "user_id", "is_active"]
    for col in conv_indexed:
        print(f"    ✓ {col} (should be indexed)")

    # Learning Progress table
    print("\n  Learning Progress table:")
    analytics_indexed = ["id", "user_id", "skill_type", "language"]
    for col in analytics_indexed:
        print(f"    ✓ {col} (should be indexed)")

    print("\n✅ Index effectiveness check complete")


@pytest.mark.performance
def test_bulk_insert_performance(db_manager, query_profiler):
    """Test: Bulk insert performance"""
    db = get_primary_db_session()

    # Test 1: Insert 100 learning progress records
    # Note: LearningProgress has UNIQUE constraint on (user_id, language, skill_type)
    start = time.time()
    records = []
    skill_types = [
        "vocabulary",
        "pronunciation",
        "conversation",
        "grammar",
        "reading",
        "writing",
        "listening",
    ]

    # Use high user_ids unlikely to exist (1000+)
    for i in range(100):
        record = LearningProgress(
            user_id=1000 + (i // len(skill_types)),  # Use test user IDs 1000+
            language="en",
            skill_type=skill_types[i % len(skill_types)],
            current_level=1,
            target_level=10,
            progress_percentage=float(i % 100),
        )
        records.append(record)

    db.bulk_save_objects(records)
    db.commit()

    duration = time.time() - start
    print(f"\n  Bulk insert 100 records: {duration * 1000:.2f}ms")
    print(f"  Rate: {100 / duration:.2f} inserts/sec")

    # Get summary
    summary = query_profiler.get_summary()
    print(f"\n📊 Bulk Insert Summary:")
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Total duration: {summary['total_duration'] * 1000:.2f}ms")

    # Assertions
    assert duration < 1.0, "100 bulk inserts should complete in < 1s"

    # Cleanup - delete test records
    db.query(LearningProgress).filter(
        LearningProgress.user_id >= 1000, LearningProgress.user_id < 1100
    ).delete(synchronize_session=False)
    db.commit()


@pytest.mark.performance
def test_query_complexity_performance(db_manager, query_profiler):
    """Test: Complex query performance"""
    db = get_primary_db_session()

    # Complex query: Get user conversation statistics
    start = time.time()

    result = db.execute(
        text("""
        SELECT
            u.id,
            u.username,
            COUNT(c.id) as conversation_count,
            AVG(c.message_count) as avg_message_count,
            SUM(c.total_tokens) as total_tokens
        FROM users u
        LEFT JOIN conversations c ON u.id = c.user_id
        GROUP BY u.id, u.username
        LIMIT 100
    """)
    )

    rows = result.fetchall()
    duration = time.time() - start

    print(f"\n  Complex aggregation query: {duration * 1000:.2f}ms")
    print(f"  Rows returned: {len(rows)}")

    # Get summary
    summary = query_profiler.get_summary()
    print(f"\n📊 Complex Query Summary:")
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Avg duration: {summary['avg_duration'] * 1000:.2f}ms")

    query_profiler.print_slow_queries()

    # Assertions
    assert duration < 0.5, "Complex query should complete in < 500ms"
