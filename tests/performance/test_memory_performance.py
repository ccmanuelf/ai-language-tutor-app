"""
Memory Performance Testing
Detects memory leaks and monitors memory usage patterns
"""

import gc
import sys
import tracemalloc
from typing import Any, Dict, List

import pytest

from app.database.config import DatabaseManager, get_primary_db_session
from app.services.conversation_manager import ConversationManager
from app.services.scenario_manager import ScenarioManager


class MemoryProfiler:
    """Profile memory usage and detect leaks"""

    def __init__(self):
        self.snapshots: List[Any] = []
        self.baseline_memory = 0

    def start(self):
        """Start memory profiling"""
        gc.collect()
        tracemalloc.start()
        self.baseline_memory = self.get_current_memory()

    def snapshot(self, label: str = ""):
        """Take memory snapshot"""
        current = tracemalloc.take_snapshot()
        self.snapshots.append((label, current))
        return current

    def stop(self):
        """Stop memory profiling"""
        tracemalloc.stop()

    def get_current_memory(self) -> int:
        """Get current memory usage in bytes"""
        snapshot = tracemalloc.take_snapshot()
        total = sum(stat.size for stat in snapshot.statistics("filename"))
        return total

    def get_memory_growth(self) -> int:
        """Get memory growth since baseline"""
        return self.get_current_memory() - self.baseline_memory

    def analyze_growth(self) -> Dict[str, Any]:
        """Analyze memory growth between snapshots"""
        if len(self.snapshots) < 2:
            return {"error": "Need at least 2 snapshots"}

        first_label, first_snapshot = self.snapshots[0]
        last_label, last_snapshot = self.snapshots[-1]

        # Compare snapshots
        top_stats = last_snapshot.compare_to(first_snapshot, "lineno")

        # Get top 10 memory consumers
        top_10 = []
        for stat in top_stats[:10]:
            top_10.append(
                {
                    "filename": stat.traceback.format()[0],
                    "size_diff": stat.size_diff,
                    "count_diff": stat.count_diff,
                }
            )

        total_growth = sum(stat.size_diff for stat in top_stats)

        return {
            "first_snapshot": first_label,
            "last_snapshot": last_label,
            "total_growth_bytes": total_growth,
            "total_growth_mb": total_growth / (1024 * 1024),
            "top_10_consumers": top_10,
        }

    def print_memory_report(self):
        """Print memory analysis report"""
        analysis = self.analyze_growth()

        if "error" in analysis:
            print(f"\n⚠️  {analysis['error']}")
            return

        print(f"\n📊 MEMORY ANALYSIS REPORT")
        print(f"  From: {analysis['first_snapshot']}")
        print(f"  To: {analysis['last_snapshot']}")
        print(f"  Total Growth: {analysis['total_growth_mb']:.2f} MB")

        if analysis["total_growth_mb"] > 10:
            print(f"\n  ⚠️  WARNING: High memory growth detected!")

        print(f"\n  Top Memory Consumers:")
        for i, consumer in enumerate(analysis["top_10_consumers"], 1):
            size_mb = consumer["size_diff"] / (1024 * 1024)
            print(f"    {i}. {size_mb:+.2f} MB - {consumer['filename']}")


@pytest.fixture
def memory_profiler():
    """Setup memory profiler"""
    profiler = MemoryProfiler()
    profiler.start()
    yield profiler
    profiler.stop()


# ============================================================================
# MEMORY PERFORMANCE TESTS
# ============================================================================


@pytest.mark.performance
def test_conversation_manager_memory_leak(db_manager, memory_profiler):
    """Test: Detect memory leaks in ConversationManager"""
    memory_profiler.snapshot("baseline")

    # Create and destroy 100 conversation managers
    for i in range(100):
        manager = ConversationManager()
        # Simulate some operations
        scenarios = manager.scenario_manager.get_scenarios_by_category("restaurant")
        del manager

        # Force garbage collection every 10 iterations
        if i % 10 == 0:
            gc.collect()

    memory_profiler.snapshot("after_100_iterations")

    # Analyze growth
    analysis = memory_profiler.analyze_growth()
    print(f"\n📊 Conversation Manager Memory Test:")
    print(f"  Memory growth: {analysis['total_growth_mb']:.2f} MB")

    memory_profiler.print_memory_report()

    # Assertions
    assert analysis["total_growth_mb"] < 50, (
        "Memory growth should be < 50 MB for 100 iterations"
    )


@pytest.mark.performance
def test_scenario_manager_memory_leak(db_manager, memory_profiler):
    """Test: Detect memory leaks in ScenarioManager"""
    memory_profiler.snapshot("baseline")

    # Create and destroy 100 scenario managers
    for i in range(100):
        manager = ScenarioManager()
        # Load scenarios multiple times
        scenarios = manager.get_scenarios_by_category("restaurant")
        scenarios = manager.get_scenarios_by_category("travel")
        scenarios = manager.get_scenarios_by_category("shopping")
        del manager

        if i % 10 == 0:
            gc.collect()

    memory_profiler.snapshot("after_100_iterations")

    # Analyze growth
    analysis = memory_profiler.analyze_growth()
    print(f"\n📊 Scenario Manager Memory Test:")
    print(f"  Memory growth: {analysis['total_growth_mb']:.2f} MB")

    memory_profiler.print_memory_report()

    # Assertions
    assert analysis["total_growth_mb"] < 30, (
        "Memory growth should be < 30 MB for 100 iterations"
    )


# Skipping FeedbackAnalyzer test - service doesn't exist yet
# @pytest.mark.performance
# def test_feedback_analyzer_memory_leak(db_manager, memory_profiler):
#     """Test: Detect memory leaks in FeedbackAnalyzer"""
#     memory_profiler.snapshot("baseline")
#
#     # Create and destroy 50 feedback analyzers
#     for i in range(50):
#         analyzer = FeedbackAnalyzer(db_manager, language="fr")
#         # Simulate analysis operations
#         test_text = (
#             "Bonjour, comment allez-vous aujourd'hui? Je voudrais commander un café."
#         )
#         # Note: This won't actually analyze without AI, but tests object lifecycle
#         del analyzer
#
#         if i % 10 == 0:
#             gc.collect()
#
#     memory_profiler.snapshot("after_50_iterations")
#
#     # Analyze growth
#     analysis = memory_profiler.analyze_growth()
#     print(f"\n📊 Feedback Analyzer Memory Test:")
#     print(f"  Memory growth: {analysis['total_growth_mb']:.2f} MB")
#
#     memory_profiler.print_memory_report()
#
#     # Assertions
#     assert analysis["total_growth_mb"] < 20, (
#         "Memory growth should be < 20 MB for 50 iterations"
#     )


@pytest.mark.performance
def test_database_session_memory_leak(db_manager, memory_profiler):
    """Test: Detect memory leaks in database sessions"""
    memory_profiler.snapshot("baseline")

    # Create and destroy 100 database sessions
    for i in range(100):
        db = get_primary_db_session()
        # Perform some queries
        from app.models.user import User

        users = db.query(User).limit(10).all()
        db.close()

        if i % 10 == 0:
            gc.collect()

    memory_profiler.snapshot("after_100_sessions")

    # Analyze growth
    analysis = memory_profiler.analyze_growth()
    print(f"\n📊 Database Session Memory Test:")
    print(f"  Memory growth: {analysis['total_growth_mb']:.2f} MB")

    memory_profiler.print_memory_report()

    # Assertions
    assert analysis["total_growth_mb"] < 15, (
        "Memory growth should be < 15 MB for 100 sessions"
    )


@pytest.mark.performance
def test_large_conversation_history_memory(db_manager, memory_profiler):
    """Test: Memory usage with large conversation histories"""
    memory_profiler.snapshot("baseline")

    # Simulate large conversation history
    large_history = []
    for i in range(1000):
        large_history.append(
            {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"This is message number {i} in a very long conversation. "
                * 10,
                "timestamp": f"2025-12-24T{i % 24:02d}:00:00",
            }
        )

    memory_profiler.snapshot("after_large_history")

    # Analyze growth
    analysis = memory_profiler.analyze_growth()
    print(f"\n📊 Large Conversation History Memory Test:")
    print(f"  Messages: 1000")
    print(f"  Memory growth: {analysis['total_growth_mb']:.2f} MB")

    # Assertions
    assert analysis["total_growth_mb"] < 100, "1000-message history should use < 100 MB"

    # Cleanup
    del large_history
    gc.collect()


@pytest.mark.performance
def test_object_pool_efficiency(db_manager, memory_profiler):
    """Test: Object pooling efficiency for repeated operations"""
    memory_profiler.snapshot("baseline")

    # Test 1: Without object reuse
    for i in range(50):
        manager = ConversationManager()
        scenarios = manager.scenario_manager.get_scenarios_by_category("restaurant")
        del manager

    gc.collect()
    memory_profiler.snapshot("without_reuse")

    # Test 2: With object reuse
    manager = ConversationManager()
    for i in range(50):
        scenarios = manager.scenario_manager.get_scenarios_by_category("restaurant")
    del manager

    gc.collect()
    memory_profiler.snapshot("with_reuse")

    # Compare
    print(f"\n📊 Object Pooling Efficiency:")

    if len(memory_profiler.snapshots) >= 3:
        _, baseline = memory_profiler.snapshots[0]
        _, without_reuse = memory_profiler.snapshots[1]
        _, with_reuse = memory_profiler.snapshots[2]

        baseline_stats = baseline.statistics("filename")
        without_stats = without_reuse.statistics("filename")
        with_stats = with_reuse.statistics("filename")

        baseline_total = sum(s.size for s in baseline_stats)
        without_total = sum(s.size for s in without_stats)
        with_total = sum(s.size for s in with_stats)

        without_growth = (without_total - baseline_total) / (1024 * 1024)
        with_growth = (with_total - baseline_total) / (1024 * 1024)

        print(f"  Without reuse: {without_growth:.2f} MB growth")
        print(f"  With reuse: {with_growth:.2f} MB growth")
        print(f"  Efficiency gain: {without_growth - with_growth:.2f} MB saved")

        assert with_growth < without_growth, "Object reuse should use less memory"


@pytest.mark.performance
def test_memory_baseline_snapshot():
    """Test: Capture memory baseline for reference"""
    tracemalloc.start()

    # Get initial memory
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    print(f"\n📊 MEMORY BASELINE SNAPSHOT:")
    print(f"  Total allocations: {len(top_stats)}")

    total_size = sum(stat.size for stat in top_stats)
    print(f"  Total memory: {total_size / (1024 * 1024):.2f} MB")

    print(f"\n  Top 10 Memory Consumers:")
    for i, stat in enumerate(top_stats[:10], 1):
        size_mb = stat.size / (1024 * 1024)
        print(f"    {i}. {size_mb:.2f} MB - {stat.traceback.format()[0]}")

    tracemalloc.stop()
