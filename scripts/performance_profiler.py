#!/usr/bin/env python3
"""
Performance Profiling and Optimization Tool for AI Language Tutor App
Task 4.2 - Performance Optimization

This script provides comprehensive performance analysis including:
1. Code profiling to identify bottlenecks
2. Memory usage analysis
3. Database query performance monitoring
4. API endpoint response time measurements
5. Cache effectiveness analysis
6. Algorithm complexity assessment
"""

import sys
import time
import psutil
import asyncio
import logging
import cProfile
import pstats
import io
import json
import tracemalloc
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text  # noqa: E402 - Required after sys.path modification for script execution
from app.database.config import db_manager  # noqa: E402 - Required after sys.path modification for script execution
from app.services.response_cache import response_cache  # noqa: E402 - Required after sys.path modification for script execution
from app.services.scenario_manager import scenario_manager  # noqa: E402 - Required after sys.path modification for script execution

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    component: str
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    timestamp: str
    details: Dict[str, Any] = None

    def to_dict(self):
        return asdict(self)


class PerformanceProfiler:
    """Comprehensive performance profiling tool"""

    def __init__(self, output_dir: str = "performance_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metrics: List[PerformanceMetrics] = []
        self.baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024

    def measure_performance(self, component: str, operation: str):
        """Decorator to measure performance of functions"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Start measurements
                process = psutil.Process()
                start_time = time.time()
                start_memory = process.memory_info().rss / 1024 / 1024
                start_cpu = process.cpu_percent()

                # Execute function
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {component}.{operation}: {e}")
                    raise

                # End measurements
                end_time = time.time()
                end_memory = process.memory_info().rss / 1024 / 1024
                end_cpu = process.cpu_percent()

                # Record metrics
                metric = PerformanceMetrics(
                    component=component,
                    operation=operation,
                    duration_ms=(end_time - start_time) * 1000,
                    memory_mb=end_memory - start_memory,
                    cpu_percent=end_cpu - start_cpu,
                    timestamp=datetime.now().isoformat(),
                )
                self.metrics.append(metric)

                logger.info(
                    f"{component}.{operation}: {metric.duration_ms:.2f}ms, "
                    f"Memory: {metric.memory_mb:+.2f}MB, CPU: {metric.cpu_percent:+.1f}%"
                )

                return result

            return wrapper

        return decorator

    async def profile_database_operations(self) -> Dict[str, Any]:
        """Profile database query performance"""
        logger.info("🔍 Profiling database operations...")

        results = {
            "connection_tests": {},
            "query_performance": {},
            "connection_pool_status": {},
        }

        # Test all database connections
        @self.measure_performance("database", "connection_health_check")
        def test_connections():
            return db_manager.test_all_connections()

        results["connection_tests"] = test_connections()

        # Profile common queries
        queries = [
            ("simple_select", "SELECT 1"),
            ("timestamp_query", "SELECT datetime('now')"),
            ("table_list", "SELECT name FROM sqlite_master WHERE type='table'"),
        ]

        for query_name, query in queries:

            @self.measure_performance("database", f"query_{query_name}")
            def run_query():
                with db_manager.sqlite_engine.connect() as conn:
                    return conn.execute(text(query)).fetchall()

            try:
                run_query()
                results["query_performance"][query_name] = "success"
            except Exception as e:
                results["query_performance"][query_name] = f"error: {str(e)}"

        # Check connection pool status
        results["connection_pool_status"] = db_manager.get_connection_stats()

        return results

    async def profile_cache_performance(self) -> Dict[str, Any]:
        """Profile response cache effectiveness"""
        logger.info("🔍 Profiling cache performance...")

        @self.measure_performance("cache", "get_stats")
        def get_cache_stats():
            return response_cache.get_stats()

        stats = get_cache_stats()

        # Test cache operations
        test_messages = [
            [{"role": "user", "content": "Hello"}],
            [{"role": "user", "content": "How are you?"}],
            [{"role": "user", "content": "Goodbye"}],
        ]

        cache_operations = []
        for i, messages in enumerate(test_messages):

            @self.measure_performance("cache", f"get_operation_{i}")
            def test_get():
                return response_cache.get(messages, "en")

            @self.measure_performance("cache", f"set_operation_{i}")
            def test_set():
                return response_cache.set(
                    messages, "en", f"Test response {i}", "test_provider"
                )

            cache_operations.append({"get": test_get() is not None, "set": test_set()})

        return {"stats": stats, "test_operations": cache_operations}

    async def profile_memory_usage(self) -> Dict[str, Any]:
        """Profile memory usage across components"""
        logger.info("🔍 Profiling memory usage...")

        tracemalloc.start()

        # Snapshot before operations
        snapshot_before = tracemalloc.take_snapshot()

        # Perform memory-intensive operations
        @self.measure_performance("memory", "scenario_loading")
        def load_scenarios():
            return scenario_manager.get_all_scenarios()

        load_scenarios()

        # Snapshot after operations
        snapshot_after = tracemalloc.take_snapshot()

        # Analyze memory differences
        top_stats = snapshot_after.compare_to(snapshot_before, "lineno")

        memory_report = {
            "total_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
            "baseline_memory_mb": self.baseline_memory,
            "memory_increase_mb": psutil.Process().memory_info().rss / 1024 / 1024
            - self.baseline_memory,
            "top_memory_consumers": [],
        }

        # Get top 10 memory consumers
        for stat in top_stats[:10]:
            memory_report["top_memory_consumers"].append(
                {
                    "file": str(stat.traceback),
                    "size_mb": stat.size_diff / 1024 / 1024,
                    "count": stat.count_diff,
                }
            )

        tracemalloc.stop()

        return memory_report

    def profile_algorithm_complexity(self) -> Dict[str, Any]:
        """Analyze algorithm complexity and identify optimization opportunities"""
        logger.info("🔍 Analyzing algorithm complexity...")

        complexity_analysis = {"file_analysis": [], "recommendations": []}

        # Analyze critical files for nested loops and complexity
        critical_files = [
            "app/services/ai_router.py",
            "app/services/conversation_manager.py",
            "app/services/scenario_manager.py",
            "app/services/spaced_repetition_manager.py",
            "app/database/config.py",
        ]

        for file_path in critical_files:
            full_path = Path(__file__).parent.parent / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r") as f:
                        content = f.read()

                    # Simple complexity indicators
                    nested_loops = content.count("for ") * content.count("    for ")
                    nested_ifs = content.count("if ") * content.count("    if ")

                    complexity_analysis["file_analysis"].append(
                        {
                            "file": file_path,
                            "lines": len(content.split("\n")),
                            "nested_loop_indicator": nested_loops,
                            "nested_conditional_indicator": nested_ifs,
                            "complexity_score": nested_loops + nested_ifs,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Could not analyze {file_path}: {e}")

        # Sort by complexity score
        complexity_analysis["file_analysis"].sort(
            key=lambda x: x["complexity_score"], reverse=True
        )

        # Generate recommendations
        for analysis in complexity_analysis["file_analysis"][:3]:
            if analysis["complexity_score"] > 10:
                complexity_analysis["recommendations"].append(
                    {
                        "file": analysis["file"],
                        "issue": "High algorithmic complexity detected",
                        "suggestion": "Consider refactoring nested loops and conditionals",
                    }
                )

        return complexity_analysis

    def profile_code_hotspots(self) -> Dict[str, Any]:
        """Identify code hotspots using cProfile"""
        logger.info("🔍 Profiling code hotspots...")

        profiler = cProfile.Profile()
        profiler.enable()

        # Run typical operations
        try:
            # Database operations
            db_manager.test_all_connections()

            # Cache operations
            response_cache.get_stats()

            # Scenario operations
            scenario_manager.get_all_scenarios()

        except Exception as e:
            logger.warning(f"Error during profiling: {e}")

        profiler.disable()

        # Capture profile stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)

        profile_output = stream.getvalue()

        # Save full profile
        profile_file = (
            self.output_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(profile_file, "w") as f:
            f.write(profile_output)

        return {
            "profile_file": str(profile_file),
            "top_functions": profile_output.split("\n")[:30],
        }

    def analyze_monolithic_risks(self) -> Dict[str, Any]:
        """Analyze potential monolithic code patterns"""
        logger.info("🔍 Analyzing monolithic code risks...")

        analysis = {"large_files": [], "god_objects": [], "recommendations": []}

        # Find large files
        for py_file in Path("app").rglob("*.py"):
            try:
                lines = len(py_file.read_text().split("\n"))
                if lines > 500:
                    analysis["large_files"].append(
                        {
                            "file": str(py_file),
                            "lines": lines,
                            "risk_level": "high" if lines > 1000 else "medium",
                        }
                    )
            except Exception as e:
                logger.warning(f"Could not analyze {py_file}: {e}")

        # Sort by size
        analysis["large_files"].sort(key=lambda x: x["lines"], reverse=True)

        # Generate recommendations
        for file_info in analysis["large_files"][:5]:
            if file_info["lines"] > 800:
                analysis["recommendations"].append(
                    {
                        "file": file_info["file"],
                        "issue": f"Large file detected ({file_info['lines']} lines)",
                        "suggestion": "Consider splitting into smaller, focused modules",
                    }
                )

        return analysis

    async def run_full_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        logger.info("=" * 80)
        logger.info("🚀 Starting Comprehensive Performance Analysis")
        logger.info("=" * 80)

        start_time = time.time()

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "memory_available_gb": psutil.virtual_memory().available
                / 1024
                / 1024
                / 1024,
            },
            "database_performance": await self.profile_database_operations(),
            "cache_performance": await self.profile_cache_performance(),
            "memory_analysis": await self.profile_memory_usage(),
            "algorithm_complexity": self.profile_algorithm_complexity(),
            "code_hotspots": self.profile_code_hotspots(),
            "monolithic_analysis": self.analyze_monolithic_risks(),
            "metrics": [m.to_dict() for m in self.metrics],
        }

        duration = time.time() - start_time
        report["analysis_duration_seconds"] = duration

        # Save report
        report_file = (
            self.output_dir
            / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("=" * 80)
        logger.info(f"✅ Analysis complete in {duration:.2f}s")
        logger.info(f"📊 Report saved to: {report_file}")
        logger.info("=" * 80)

        # Print summary
        self.print_summary(report)

        return report

    def print_summary(self, report: Dict[str, Any]):
        """Print performance summary"""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE ANALYSIS SUMMARY")
        print("=" * 80)

        # Database performance
        print("\n🗄️  DATABASE PERFORMANCE:")
        db_perf = report["database_performance"]
        for db_name, status in db_perf["connection_tests"].items():
            health = status.get("status", "unknown")
            resp_time = status.get("response_time_ms", "N/A")
            print(f"  • {db_name}: {health} ({resp_time}ms)")

        # Cache performance
        print("\n💾 CACHE PERFORMANCE:")
        cache_stats = report["cache_performance"]["stats"]
        print(f"  • Hit Rate: {cache_stats['hit_rate']}%")
        print(
            f"  • Total Entries: {cache_stats['entries']}/{cache_stats['max_entries']}"
        )
        print(f"  • Total Requests: {cache_stats['total_requests']}")

        # Memory usage
        print("\n🧠 MEMORY USAGE:")
        mem = report["memory_analysis"]
        print(f"  • Total Memory: {mem['total_memory_mb']:.2f} MB")
        print(f"  • Baseline: {mem['baseline_memory_mb']:.2f} MB")
        print(f"  • Increase: {mem['memory_increase_mb']:+.2f} MB")

        # Algorithm complexity
        print("\n⚡ ALGORITHM COMPLEXITY:")
        complexity = report["algorithm_complexity"]
        if complexity["file_analysis"]:
            top_complex = complexity["file_analysis"][0]
            print(f"  • Most Complex File: {top_complex['file']}")
            print(f"  • Complexity Score: {top_complex['complexity_score']}")

        # Monolithic risks
        print("\n🏗️  MONOLITHIC RISKS:")
        mono = report["monolithic_analysis"]
        if mono["large_files"]:
            print(f"  • Large Files Detected: {len(mono['large_files'])}")
            largest = mono["large_files"][0]
            print(f"  • Largest File: {largest['file']} ({largest['lines']} lines)")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        all_recommendations = complexity.get("recommendations", []) + mono.get(
            "recommendations", []
        )
        if all_recommendations:
            for i, rec in enumerate(all_recommendations[:5], 1):
                print(f"  {i}. {rec['issue']}")
                print(f"     → {rec['suggestion']}")
        else:
            print("  ✅ No critical issues detected")

        print("\n" + "=" * 80)


async def main():
    """Main entry point"""
    profiler = PerformanceProfiler()

    try:
        await profiler.run_full_analysis()

        # Exit with success
        sys.exit(0)

    except Exception as e:
        logger.error(f"Performance profiling failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
