"""
Resource Utilization Monitoring
Monitors CPU, memory, and disk I/O during operations
"""

import time
from threading import Thread
from typing import Any, Dict, List

import psutil
import pytest


class ResourceMonitor:
    """Monitor system resource utilization"""

    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.monitoring = False
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []
        self.disk_io_samples: List[Dict[str, int]] = []
        self.monitor_thread = None
        self.process = psutil.Process()

    def _monitor_loop(self):
        """Monitoring loop"""
        baseline_io = psutil.disk_io_counters()

        while self.monitoring:
            # CPU usage
            cpu_percent = self.process.cpu_percent(interval=None)
            self.cpu_samples.append(cpu_percent)

            # Memory usage
            mem_info = self.process.memory_info()
            memory_mb = mem_info.rss / (1024 * 1024)
            self.memory_samples.append(memory_mb)

            # Disk I/O
            current_io = psutil.disk_io_counters()
            if current_io and baseline_io:
                io_stats = {
                    "read_bytes": current_io.read_bytes - baseline_io.read_bytes,
                    "write_bytes": current_io.write_bytes - baseline_io.write_bytes,
                    "read_count": current_io.read_count - baseline_io.read_count,
                    "write_count": current_io.write_count - baseline_io.write_count,
                }
                self.disk_io_samples.append(io_stats)

            time.sleep(self.interval)

    def start(self):
        """Start monitoring"""
        self.monitoring = True
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def get_statistics(self) -> Dict[str, Any]:
        """Get resource utilization statistics"""
        if not self.cpu_samples:
            return {"error": "No samples collected"}

        # CPU stats
        cpu_avg = sum(self.cpu_samples) / len(self.cpu_samples)
        cpu_max = max(self.cpu_samples)
        cpu_min = min(self.cpu_samples)

        # Memory stats
        mem_avg = sum(self.memory_samples) / len(self.memory_samples)
        mem_max = max(self.memory_samples)
        mem_min = min(self.memory_samples)
        mem_growth = mem_max - mem_min

        # Disk I/O stats
        total_read_bytes = 0
        total_write_bytes = 0
        total_read_count = 0
        total_write_count = 0

        if self.disk_io_samples:
            total_read_bytes = self.disk_io_samples[-1]["read_bytes"]
            total_write_bytes = self.disk_io_samples[-1]["write_bytes"]
            total_read_count = self.disk_io_samples[-1]["read_count"]
            total_write_count = self.disk_io_samples[-1]["write_count"]

        return {
            "cpu": {
                "avg_percent": cpu_avg,
                "max_percent": cpu_max,
                "min_percent": cpu_min,
                "samples": len(self.cpu_samples),
            },
            "memory": {
                "avg_mb": mem_avg,
                "max_mb": mem_max,
                "min_mb": mem_min,
                "growth_mb": mem_growth,
                "samples": len(self.memory_samples),
            },
            "disk_io": {
                "total_read_mb": total_read_bytes / (1024 * 1024),
                "total_write_mb": total_write_bytes / (1024 * 1024),
                "read_operations": total_read_count,
                "write_operations": total_write_count,
                "samples": len(self.disk_io_samples),
            },
        }

    def print_report(self):
        """Print resource utilization report"""
        stats = self.get_statistics()

        if "error" in stats:
            print(f"\n⚠️  {stats['error']}")
            return

        print("\n📊 RESOURCE UTILIZATION REPORT:")

        print(f"\n  CPU Usage:")
        print(f"    Average: {stats['cpu']['avg_percent']:.2f}%")
        print(f"    Peak: {stats['cpu']['max_percent']:.2f}%")
        print(f"    Samples: {stats['cpu']['samples']}")

        print(f"\n  Memory Usage:")
        print(f"    Average: {stats['memory']['avg_mb']:.2f} MB")
        print(f"    Peak: {stats['memory']['max_mb']:.2f} MB")
        print(f"    Growth: {stats['memory']['growth_mb']:.2f} MB")
        print(f"    Samples: {stats['memory']['samples']}")

        print(f"\n  Disk I/O:")
        print(
            f"    Read: {stats['disk_io']['total_read_mb']:.2f} MB ({stats['disk_io']['read_operations']} ops)"
        )
        print(
            f"    Write: {stats['disk_io']['total_write_mb']:.2f} MB ({stats['disk_io']['write_operations']} ops)"
        )


@pytest.fixture
def resource_monitor():
    """Setup resource monitor"""
    monitor = ResourceMonitor(interval=0.1)
    monitor.start()
    yield monitor
    monitor.stop()


# ============================================================================
# RESOURCE UTILIZATION TESTS
# ============================================================================


@pytest.mark.performance
def test_database_operations_resource_usage(db_manager, resource_monitor):
    """Test: Resource usage during database operations"""
    from app.models.database import User

    from app.database.config import get_primary_db_session

    # Perform 100 database operations
    for i in range(100):
        db = get_primary_db_session()
        users = db.query(User).limit(10).all()
        db.close()

        # Small delay to allow monitoring
        time.sleep(0.01)

    # Stop monitoring and get stats
    resource_monitor.stop()
    stats = resource_monitor.get_statistics()

    print("\n📊 Database Operations Resource Usage:")
    print(f"  CPU avg: {stats['cpu']['avg_percent']:.2f}%")
    print(f"  Memory avg: {stats['memory']['avg_mb']:.2f} MB")
    print(f"  Memory growth: {stats['memory']['growth_mb']:.2f} MB")

    # Assertions
    assert stats["cpu"]["avg_percent"] < 80.0, "CPU usage should be < 80%"
    assert stats["memory"]["growth_mb"] < 50.0, "Memory growth should be < 50 MB"


@pytest.mark.performance
def test_scenario_loading_resource_usage(db_manager, resource_monitor):
    """Test: Resource usage during scenario loading"""
    from app.services.scenario_manager import ScenarioManager

    # Load scenarios 50 times
    manager = ScenarioManager()
    for i in range(50):
        scenarios = manager.get_scenarios_by_category("restaurant")
        time.sleep(0.01)

    resource_monitor.stop()
    stats = resource_monitor.get_statistics()

    print("\n📊 Scenario Loading Resource Usage:")
    print(f"  CPU avg: {stats['cpu']['avg_percent']:.2f}%")
    print(f"  Memory avg: {stats['memory']['avg_mb']:.2f} MB")

    # Assertions
    assert stats["cpu"]["avg_percent"] < 70.0, "CPU usage should be < 70%"


@pytest.mark.performance
def test_conversation_initialization_resource_usage(db_manager, resource_monitor):
    """Test: Resource usage during conversation initialization"""
    from app.services.conversation_manager import ConversationManager

    # Initialize conversations
    manager = ConversationManager()
    for i in range(20):
        # Simulate conversation setup
        scenarios = manager.scenario_manager.get_scenarios_by_category("restaurant")
        time.sleep(0.05)

    resource_monitor.stop()
    stats = resource_monitor.get_statistics()

    print("\n📊 Conversation Initialization Resource Usage:")
    print(f"  CPU avg: {stats['cpu']['avg_percent']:.2f}%")
    print(f"  Memory avg: {stats['memory']['avg_mb']:.2f} MB")

    resource_monitor.print_report()

    # Assertions
    assert stats["cpu"]["avg_percent"] < 75.0, "CPU usage should be < 75%"


@pytest.mark.performance
def test_analytics_processing_resource_usage(db_manager, resource_monitor):
    """Test: Resource usage during analytics processing"""
    from app.models.database import LearningProgress

    from app.database.config import get_primary_db_session

    # Process analytics events
    db = get_primary_db_session()

    # Insert batch of events
    events = []
    for i in range(100):
        event = LearningProgress(
            user_id=f"test_user_{i % 10}",
            event_type="test_event",
            event_data={"index": i, "test": True},
        )
        events.append(event)

    db.bulk_save_objects(events)
    db.commit()

    # Query events
    for i in range(20):
        results = (
            db.query(LearningProgress).filter_by(event_type="test_event").limit(50).all()
        )
        time.sleep(0.01)

    # Cleanup
    db.query(LearningProgress).filter(LearningProgress.user_id.like("test_user_%")).delete()
    db.commit()
    db.close()

    resource_monitor.stop()
    stats = resource_monitor.get_statistics()

    print("\n📊 Analytics Processing Resource Usage:")
    print(f"  CPU avg: {stats['cpu']['avg_percent']:.2f}%")
    print(f"  Memory avg: {stats['memory']['avg_mb']:.2f} MB")
    print(f"  Disk writes: {stats['disk_io']['total_write_mb']:.2f} MB")

    # Assertions
    assert stats["cpu"]["avg_percent"] < 80.0, "CPU usage should be < 80%"


@pytest.mark.performance
def test_system_resource_baseline():
    """Test: Capture system resource baseline"""

    # Get current system stats
    cpu_percent = psutil.cpu_percent(interval=1.0)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    disk_io = psutil.disk_io_counters()

    print("\n📊 SYSTEM RESOURCE BASELINE:")

    print(f"\n  CPU:")
    print(f"    Total cores: {psutil.cpu_count()}")
    print(f"    Current usage: {cpu_percent}%")

    print(f"\n  Memory:")
    print(f"    Total: {memory.total / (1024**3):.2f} GB")
    print(f"    Available: {memory.available / (1024**3):.2f} GB")
    print(f"    Used: {memory.used / (1024**3):.2f} GB ({memory.percent}%)")

    print(f"\n  Disk:")
    print(f"    Total: {disk.total / (1024**3):.2f} GB")
    print(f"    Used: {disk.used / (1024**3):.2f} GB ({disk.percent}%)")
    print(f"    Free: {disk.free / (1024**3):.2f} GB")

    if disk_io:
        print(f"\n  Disk I/O:")
        print(f"    Read: {disk_io.read_bytes / (1024**3):.2f} GB")
        print(f"    Write: {disk_io.write_bytes / (1024**3):.2f} GB")

    # Basic assertions
    assert memory.percent < 90.0, "System memory usage should be < 90%"
    assert disk.percent < 90.0, "Disk usage should be < 90%"


@pytest.mark.performance
def test_process_resource_limits():
    """Test: Verify process resource limits"""
    process = psutil.Process()

    # Get process info
    with process.oneshot():
        cpu_times = process.cpu_times()
        memory_info = process.memory_info()
        num_threads = process.num_threads()
        num_fds = process.num_fds() if hasattr(process, "num_fds") else 0

    print("\n📊 PROCESS RESOURCE LIMITS:")

    print(f"\n  CPU Times:")
    print(f"    User: {cpu_times.user:.2f}s")
    print(f"    System: {cpu_times.system:.2f}s")

    print(f"\n  Memory:")
    print(f"    RSS: {memory_info.rss / (1024**2):.2f} MB")
    print(f"    VMS: {memory_info.vms / (1024**2):.2f} MB")

    print(f"\n  Resources:")
    print(f"    Threads: {num_threads}")
    if num_fds > 0:
        print(f"    File descriptors: {num_fds}")

    # Assertions
    assert memory_info.rss / (1024**2) < 1000, "Process memory should be < 1 GB"
    assert num_threads < 100, "Thread count should be < 100"
