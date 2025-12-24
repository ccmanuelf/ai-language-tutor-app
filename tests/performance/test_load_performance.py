"""
Performance Load Testing Suite
Tests system performance under concurrent user loads
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import pytest
from sqlalchemy.orm import Session

from app.database.config import DatabaseManager, get_primary_db_session
from app.services.auth import AuthenticationService
from app.services.conversation_manager import ConversationManager
from app.services.scenario_manager import ScenarioManager


class PerformanceMetrics:
    """Track performance metrics"""

    def __init__(self):
        self.response_times: List[float] = []
        self.errors: List[str] = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()
        self.end_time = None

    def record_success(self, response_time: float):
        self.response_times.append(response_time)
        self.successful_requests += 1

    def record_error(self, error: str):
        self.errors.append(error)
        self.failed_requests += 1

    def finalize(self):
        self.end_time = time.time()

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.response_times:
            return {
                "total_requests": self.successful_requests + self.failed_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "error_rate": 100.0 if self.failed_requests > 0 else 0.0,
                "total_duration": self.end_time - self.start_time
                if self.end_time
                else 0,
            }

        sorted_times = sorted(self.response_times)
        n = len(sorted_times)

        return {
            "total_requests": self.successful_requests + self.failed_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate": (
                self.failed_requests / (self.successful_requests + self.failed_requests)
            )
            * 100,
            "total_duration": self.end_time - self.start_time if self.end_time else 0,
            "avg_response_time": statistics.mean(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": sorted_times[int(n * 0.95)] if n > 0 else 0,
            "p99_response_time": sorted_times[int(n * 0.99)] if n > 0 else 0,
            "requests_per_second": self.successful_requests
            / (self.end_time - self.start_time)
            if self.end_time
            else 0,
        }


class LoadTestSimulator:
    """Simulate concurrent user load"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.auth_service = AuthenticationService(db_manager)
        self.metrics = PerformanceMetrics()

    async def simulate_user_login(self, user_index: int) -> bool:
        """Simulate user login"""
        start = time.time()
        try:
            # Create test user
            username = f"load_test_user_{user_index}"
            email = f"loadtest{user_index}@example.com"

            # Register user
            result = self.auth_service.register_user(
                username=username,
                email=email,
                password="TestPass123!",
                native_language="en",
                target_language="fr",
            )

            if result:
                # Login user
                user = self.auth_service.login_user(username, "TestPass123!")
                if user:
                    duration = time.time() - start
                    self.metrics.record_success(duration)
                    return True

            self.metrics.record_error("Login failed")
            return False

        except Exception as e:
            self.metrics.record_error(str(e))
            return False

    async def simulate_scenario_load(self, user_index: int) -> bool:
        """Simulate loading scenarios"""
        start = time.time()
        try:
            scenario_manager = ScenarioManager(self.db_manager)
            scenarios = scenario_manager.get_scenarios_by_category("restaurant")

            if scenarios:
                duration = time.time() - start
                self.metrics.record_success(duration)
                return True

            self.metrics.record_error("No scenarios found")
            return False

        except Exception as e:
            self.metrics.record_error(str(e))
            return False

    async def simulate_conversation_start(self, user_index: int) -> bool:
        """Simulate starting a conversation"""
        start = time.time()
        try:
            # Get or create test user
            db = get_primary_db_session()
            from app.models.user import User

            user = (
                db.query(User)
                .filter_by(username=f"load_test_user_{user_index}")
                .first()
            )

            if not user:
                return False

            # Create conversation manager
            conv_manager = ConversationManager(self.db_manager)

            # Start conversation with a test scenario
            scenario_manager = ScenarioManager(self.db_manager)
            scenarios = scenario_manager.get_scenarios_by_category("restaurant")

            if not scenarios:
                self.metrics.record_error("No scenarios available")
                return False

            scenario = scenarios[0]

            # Initialize conversation
            conversation_id = await conv_manager.start_conversation(
                user_id=str(user.id),
                scenario_id=scenario.scenario_id,
                language="fr",
            )

            if conversation_id:
                duration = time.time() - start
                self.metrics.record_success(duration)
                return True

            self.metrics.record_error("Conversation start failed")
            return False

        except Exception as e:
            self.metrics.record_error(str(e))
            return False

    async def run_concurrent_load(self, num_users: int, test_type: str = "login"):
        """Run concurrent load test"""
        print(f"\n🔥 Starting load test: {num_users} concurrent users ({test_type})")

        if test_type == "login":
            test_func = self.simulate_user_login
        elif test_type == "scenarios":
            test_func = self.simulate_scenario_load
        elif test_type == "conversations":
            test_func = self.simulate_conversation_start
        else:
            raise ValueError(f"Unknown test type: {test_type}")

        # Run concurrent tasks
        tasks = [test_func(i) for i in range(num_users)]
        await asyncio.gather(*tasks)

        self.metrics.finalize()
        return self.metrics.get_summary()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


@pytest.mark.performance
@pytest.mark.asyncio
async def test_load_10_concurrent_users_login(db_manager):
    """Test: 10 concurrent users logging in"""
    simulator = LoadTestSimulator(db_manager)
    summary = await simulator.run_concurrent_load(10, "login")

    print("\n📊 PERFORMANCE METRICS (10 users - Login):")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Successful: {summary['successful_requests']}")
    print(f"  Failed: {summary['failed_requests']}")
    print(f"  Error Rate: {summary['error_rate']:.2f}%")
    print(f"  Avg Response Time: {summary.get('avg_response_time', 0):.3f}s")
    print(f"  P95 Response Time: {summary.get('p95_response_time', 0):.3f}s")
    print(f"  Requests/sec: {summary.get('requests_per_second', 0):.2f}")

    # Assertions
    assert summary["error_rate"] < 5.0, "Error rate should be < 5%"
    assert summary.get("avg_response_time", 0) < 2.0, "Avg response time should be < 2s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_load_50_concurrent_users_login(db_manager):
    """Test: 50 concurrent users logging in"""
    simulator = LoadTestSimulator(db_manager)
    summary = await simulator.run_concurrent_load(50, "login")

    print("\n📊 PERFORMANCE METRICS (50 users - Login):")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Successful: {summary['successful_requests']}")
    print(f"  Failed: {summary['failed_requests']}")
    print(f"  Error Rate: {summary['error_rate']:.2f}%")
    print(f"  Avg Response Time: {summary.get('avg_response_time', 0):.3f}s")
    print(f"  P95 Response Time: {summary.get('p95_response_time', 0):.3f}s")
    print(f"  P99 Response Time: {summary.get('p99_response_time', 0):.3f}s")
    print(f"  Requests/sec: {summary.get('requests_per_second', 0):.2f}")

    # Assertions
    assert summary["error_rate"] < 10.0, "Error rate should be < 10%"
    assert summary.get("avg_response_time", 0) < 3.0, "Avg response time should be < 3s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_load_100_concurrent_users_login(db_manager):
    """Test: 100 concurrent users logging in"""
    simulator = LoadTestSimulator(db_manager)
    summary = await simulator.run_concurrent_load(100, "login")

    print("\n📊 PERFORMANCE METRICS (100 users - Login):")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Successful: {summary['successful_requests']}")
    print(f"  Failed: {summary['failed_requests']}")
    print(f"  Error Rate: {summary['error_rate']:.2f}%")
    print(f"  Avg Response Time: {summary.get('avg_response_time', 0):.3f}s")
    print(f"  P95 Response Time: {summary.get('p95_response_time', 0):.3f}s")
    print(f"  P99 Response Time: {summary.get('p99_response_time', 0):.3f}s")
    print(f"  Max Response Time: {summary.get('max_response_time', 0):.3f}s")
    print(f"  Requests/sec: {summary.get('requests_per_second', 0):.2f}")

    # Assertions
    assert summary["error_rate"] < 15.0, "Error rate should be < 15%"
    assert summary.get("avg_response_time", 0) < 5.0, "Avg response time should be < 5s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_load_scenarios_concurrent(db_manager):
    """Test: Concurrent scenario loading"""
    simulator = LoadTestSimulator(db_manager)
    summary = await simulator.run_concurrent_load(50, "scenarios")

    print("\n📊 PERFORMANCE METRICS (50 users - Scenario Loading):")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Successful: {summary['successful_requests']}")
    print(f"  Failed: {summary['failed_requests']}")
    print(f"  Error Rate: {summary['error_rate']:.2f}%")
    print(f"  Avg Response Time: {summary.get('avg_response_time', 0):.3f}s")
    print(f"  P95 Response Time: {summary.get('p95_response_time', 0):.3f}s")

    # Assertions
    assert summary["error_rate"] < 5.0, "Error rate should be < 5%"
    assert summary.get("avg_response_time", 0) < 1.0, "Avg response time should be < 1s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_load_conversations_concurrent(db_manager):
    """Test: Concurrent conversation initialization"""
    # First create test users
    simulator = LoadTestSimulator(db_manager)
    await simulator.run_concurrent_load(20, "login")

    # Now test conversation starts
    simulator = LoadTestSimulator(db_manager)
    summary = await simulator.run_concurrent_load(20, "conversations")

    print("\n📊 PERFORMANCE METRICS (20 users - Conversation Start):")
    print(f"  Total Requests: {summary['total_requests']}")
    print(f"  Successful: {summary['successful_requests']}")
    print(f"  Failed: {summary['failed_requests']}")
    print(f"  Error Rate: {summary['error_rate']:.2f}%")
    print(f"  Avg Response Time: {summary.get('avg_response_time', 0):.3f}s")
    print(f"  P95 Response Time: {summary.get('p95_response_time', 0):.3f}s")

    # Assertions
    assert summary["error_rate"] < 10.0, "Error rate should be < 10%"
    assert summary.get("avg_response_time", 0) < 3.0, "Avg response time should be < 3s"
