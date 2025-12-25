#!/usr/bin/env python3
"""
Cost Optimization Testing for AI Language Tutor App
Tests the enhanced AI router with cost-aware routing, caching, and budget controls.
"""

import asyncio
import sys
import time
import json

sys.path.append(".")


async def test_cost_optimization():
    """Test the complete cost optimization system"""

    print("🧪 TESTING AI ROUTER COST OPTIMIZATION")
    print("=" * 60)

    try:
        from app.services.ai_router import generate_ai_response, get_ai_router_status
        from app.services.response_cache import response_cache

        # Clear cache for clean test
        response_cache.clear()

        print("✅ Successfully imported cost optimization modules")

        # Test 1: Cache Performance Test
        print("\n🎯 TEST 1: Cache Performance")
        print("-" * 40)

        # Common cacheable requests
        test_requests = [
            {
                "messages": [{"role": "user", "content": "Hello! How are you?"}],
                "language": "en",
            },
            {
                "messages": [{"role": "user", "content": "What is machine learning?"}],
                "language": "en",
            },
            {
                "messages": [{"role": "user", "content": "Translate: hello"}],
                "language": "en",
            },
            {
                "messages": [{"role": "user", "content": "Hello! How are you?"}],
                "language": "en",
            },  # Repeat for cache hit
        ]

        total_cost = 0.0
        cache_hits = 0

        for i, request in enumerate(test_requests):
            start_time = time.time()

            try:
                response = await generate_ai_response(**request)

                duration = time.time() - start_time
                cost = getattr(response, "cost", 0.0)
                is_cached = (
                    response.metadata.get("cached", False)
                    if hasattr(response, "metadata")
                    else False
                )

                total_cost += cost
                if is_cached:
                    cache_hits += 1

                print(
                    f"Request {i + 1}: {'CACHED' if is_cached else 'API'} | "
                    f"Time: {duration:.2f}s | Cost: ${cost:.6f}"
                )

            except Exception as e:
                print(f"Request {i + 1}: ERROR - {str(e)[:100]}...")

        print(f"\n📊 Cache Performance Summary:")
        print(f"Total Cost: ${total_cost:.6f}")
        print(f"Cache Hits: {cache_hits}/{len(test_requests)}")

        # Test 2: Provider Cost Efficiency
        print("\n🎯 TEST 2: Provider Cost Efficiency")
        print("-" * 40)

        # Test different types of requests
        test_scenarios = [
            {"type": "simple", "message": "Hi there!", "expected_provider": "deepseek"},
            {
                "type": "complex",
                "message": "Explain quantum computing in detail",
                "expected_provider": "claude",
            },
            {
                "type": "translation",
                "message": "Translate: Good morning",
                "expected_provider": "mistral",
            },
        ]

        for scenario in test_scenarios:
            try:
                request = {
                    "messages": [{"role": "user", "content": scenario["message"]}],
                    "language": "en",
                    "use_case": scenario["type"],
                }

                response = await generate_ai_response(**request)
                actual_provider = getattr(response, "provider", "unknown")
                cost = getattr(response, "cost", 0.0)

                print(
                    f"{scenario['type']:10} | Provider: {actual_provider:8} | Cost: ${cost:.6f}"
                )

            except Exception as e:
                print(f"{scenario['type']:10} | ERROR: {str(e)[:50]}...")

        # Test 3: System Status and Metrics
        print("\n🎯 TEST 3: System Status & Metrics")
        print("-" * 40)

        try:
            status = await get_ai_router_status()

            # Display key metrics
            if "cost_optimization" in status:
                cost_opt = status["cost_optimization"]

                cache_stats = cost_opt.get("cache_stats", {})
                print(f"Cache Hit Rate: {cache_stats.get('hit_rate', 0):.1f}%")
                print(f"Cache Entries: {cache_stats.get('entries', 0)}")
                print(
                    f"Cache Savings: ${cost_opt.get('estimated_cache_savings_usd', 0):.4f}"
                )

                budget_status = cost_opt.get("budget_status", {})
                print(f"Budget Remaining: ${budget_status.get('remaining', 0):.2f}")
                print(f"Budget Alert: {budget_status.get('alert_level', 'unknown')}")

            # Display provider availability
            if "providers" in status:
                print(f"\n📡 Provider Status:")
                for provider, info in status["providers"].items():
                    available = info.get("available", False)
                    status_text = "✅ Available" if available else "❌ Unavailable"
                    print(f"  {provider:10} | {status_text}")

        except Exception as e:
            print(f"Status check error: {e}")

        # Test 4: Budget Controls Simulation
        print("\n🎯 TEST 4: Budget Controls")
        print("-" * 40)

        try:
            from app.services.budget_manager import budget_manager

            # Get current budget status
            budget_status = budget_manager.get_current_budget_status()
            print(f"Monthly Budget: ${budget_status.monthly_budget:.2f}")
            print(f"Current Spent: ${budget_status.total_spent:.2f}")
            print(f"Remaining: ${budget_status.remaining_budget:.2f}")
            print(
                f"Alert Level: {budget_status.alert_level.value if budget_status.alert_level else 'green'}"
            )

        except Exception as e:
            print(f"Budget check error: {e}")

        print("\n🎉 COST OPTIMIZATION TESTING COMPLETED!")

        # Final recommendations
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        print("1. Monitor cache hit rate - target >30% for common conversations")
        print("2. Review provider routing for cost efficiency")
        print("3. Set up budget alerts for proactive cost management")
        print("4. Consider upgrading Ollama models for better offline fallback")

        return True

    except Exception as e:
        print(f"❌ Cost optimization test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_cost_optimization())
    exit(0 if success else 1)
