"""
AI Provider Performance Benchmarking
Tests response times and reliability of AI service providers
"""

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.database.config import DatabaseManager
from app.services.claude_service import ClaudeService
from app.services.deepseek_service import DeepSeekService
from app.services.mistral_service import MistralService


class AIProviderBenchmark:
    """Benchmark AI provider performance"""

    def __init__(self):
        self.results: Dict[str, List[float]] = {
            "claude": [],
            "mistral": [],
            "deepseek": [],
        }

    def record_response_time(self, provider: str, duration: float):
        """Record response time for provider"""
        if provider in self.results:
            self.results[provider].append(duration)

    def get_statistics(self, provider: str) -> Dict[str, float]:
        """Get statistics for provider"""
        times = self.results.get(provider, [])
        if not times:
            return {"count": 0}

        sorted_times = sorted(times)
        n = len(sorted_times)

        return {
            "count": n,
            "avg": sum(times) / n,
            "min": min(times),
            "max": max(times),
            "median": sorted_times[n // 2],
            "p95": sorted_times[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_times[int(n * 0.99)] if n > 0 else 0,
        }

    def print_comparison(self):
        """Print provider comparison"""
        print("\n📊 AI PROVIDER PERFORMANCE COMPARISON:")

        for provider in ["claude", "mistral", "deepseek"]:
            stats = self.get_statistics(provider)
            if stats["count"] == 0:
                print(f"\n  {provider.upper()}: No data")
                continue

            print(f"\n  {provider.upper()}:")
            print(f"    Requests: {stats['count']}")
            print(f"    Avg: {stats['avg']:.3f}s")
            print(f"    Min: {stats['min']:.3f}s")
            print(f"    Max: {stats['max']:.3f}s")
            print(f"    Median: {stats['median']:.3f}s")
            print(f"    P95: {stats['p95']:.3f}s")
            print(f"    P99: {stats['p99']:.3f}s")


@pytest.fixture
def ai_benchmark():
    """Setup AI provider benchmark"""
    return AIProviderBenchmark()


# ============================================================================
# AI PROVIDER PERFORMANCE TESTS (Mocked - No actual API calls)
# ============================================================================


@pytest.mark.performance
@pytest.mark.asyncio
async def test_claude_service_performance(db_manager, ai_benchmark):
    """Test: Claude service performance (mocked)"""
    service = ClaudeService()

    # Mock the API client
    mock_response = Mock()
    mock_response.content = [Mock(text="Bonjour! Comment puis-je vous aider?")]
    mock_response.usage = Mock(input_tokens=100, output_tokens=50)

    with patch.object(service, "client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        # Benchmark 10 requests
        for i in range(10):
            start = time.time()

            response = await service.generate_response(
                message="Hello, how are you?",
                language="fr",
            )

            duration = time.time() - start
            ai_benchmark.record_response_time("claude", duration)

    stats = ai_benchmark.get_statistics("claude")
    print(f"\n📊 Claude Service Performance:")
    print(f"  Avg response: {stats['avg']:.3f}s")
    print(f"  P95: {stats['p95']:.3f}s")

    # Assertions
    assert stats["avg"] < 0.1, "Mocked Claude should respond in < 100ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_mistral_service_performance(db_manager, ai_benchmark):
    """Test: Mistral service performance (mocked)"""
    service = MistralService()

    # Mock the API client
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Bonjour! Comment allez-vous?"))]
    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)

    with patch.object(service, "client") as mock_client:
        mock_client.chat.complete = AsyncMock(return_value=mock_response)

        # Benchmark 10 requests
        for i in range(10):
            start = time.time()

            response = await service.generate_response(
                message="Hello, how are you?",
                language="fr",
            )

            duration = time.time() - start
            ai_benchmark.record_response_time("mistral", duration)

    stats = ai_benchmark.get_statistics("mistral")
    print(f"\n📊 Mistral Service Performance:")
    print(f"  Avg response: {stats['avg']:.3f}s")
    print(f"  P95: {stats['p95']:.3f}s")

    # Assertions
    assert stats["avg"] < 0.1, "Mocked Mistral should respond in < 100ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_deepseek_service_performance(db_manager, ai_benchmark):
    """Test: DeepSeek service performance (mocked)"""
    service = DeepSeekService()

    # Mock the API client
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="Hello! I'm doing well, thank you!"))
    ]
    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)

    with patch.object(service, "client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Benchmark 10 requests
        for i in range(10):
            start = time.time()

            response = await service.generate_response(
                message="Hello, how are you?",
                language="en",
            )

            duration = time.time() - start
            ai_benchmark.record_response_time("deepseek", duration)

    stats = ai_benchmark.get_statistics("deepseek")
    print(f"\n📊 DeepSeek Service Performance:")
    print(f"  Avg response: {stats['avg']:.3f}s")
    print(f"  P95: {stats['p95']:.3f}s")

    # Assertions
    assert stats["avg"] < 0.1, "Mocked DeepSeek should respond in < 100ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_provider_comparison(db_manager, ai_benchmark):
    """Test: Compare all AI providers"""

    # Test all providers
    await test_claude_service_performance(db_manager, ai_benchmark)
    await test_mistral_service_performance(db_manager, ai_benchmark)
    await test_deepseek_service_performance(db_manager, ai_benchmark)

    # Print comparison
    ai_benchmark.print_comparison()

    # Verify all providers respond reasonably
    for provider in ["claude", "mistral", "deepseek"]:
        stats = ai_benchmark.get_statistics(provider)
        assert stats["count"] > 0, f"{provider} should have benchmark data"
        assert stats["avg"] < 1.0, f"{provider} avg response should be < 1s (mocked)"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_concurrent_requests(db_manager):
    """Test: Concurrent AI requests handling"""
    service = ClaudeService()

    # Mock the API client
    mock_response = Mock()
    mock_response.content = [Mock(text="Response")]
    mock_response.usage = Mock(input_tokens=100, output_tokens=50)

    with patch.object(service, "client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        # Send 20 concurrent requests
        start = time.time()

        tasks = [
            service.generate_response(message=f"Request {i}", language="fr")
            for i in range(20)
        ]

        responses = await asyncio.gather(*tasks)

        duration = time.time() - start

    print(f"\n📊 Concurrent AI Requests:")
    print(f"  Total requests: 20")
    print(f"  Total time: {duration:.3f}s")
    print(f"  Avg per request: {duration / 20:.3f}s")
    print(f"  Throughput: {20 / duration:.2f} req/s")

    # Assertions
    assert len(responses) == 20, "All requests should complete"
    assert duration < 2.0, "20 concurrent requests should complete in < 2s (mocked)"


@pytest.mark.performance
def test_ai_service_initialization_time(db_manager):
    """Test: AI service initialization performance"""

    # Test Claude initialization
    start = time.time()
    claude = ClaudeService()
    claude_init = time.time() - start

    # Test Mistral initialization
    start = time.time()
    mistral = MistralService()
    mistral_init = time.time() - start

    # Test DeepSeek initialization
    start = time.time()
    deepseek = DeepSeekService()
    deepseek_init = time.time() - start

    print(f"\n📊 AI Service Initialization Times:")
    print(f"  Claude: {claude_init * 1000:.2f}ms")
    print(f"  Mistral: {mistral_init * 1000:.2f}ms")
    print(f"  DeepSeek: {deepseek_init * 1000:.2f}ms")

    # Assertions
    assert claude_init < 0.5, "Claude init should be < 500ms"
    assert mistral_init < 0.5, "Mistral init should be < 500ms"
    assert deepseek_init < 0.5, "DeepSeek init should be < 500ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_error_handling_performance(db_manager):
    """Test: AI service error handling doesn't degrade performance"""
    service = ClaudeService()

    # Mock failures
    with patch.object(service, "client") as mock_client:
        mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))

        start = time.time()

        # Try 10 requests that will fail
        for i in range(10):
            try:
                await service.generate_response(message="Test", language="fr")
            except Exception:
                pass  # Expected

        duration = time.time() - start

    print(f"\n📊 Error Handling Performance:")
    print(f"  10 failed requests: {duration:.3f}s")
    print(f"  Avg per failure: {duration / 10:.3f}s")

    # Assertions
    assert duration < 1.0, "Error handling should be fast (< 100ms per error)"
