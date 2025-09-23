#!/usr/bin/env python3
"""
Comprehensive AI Service JSON Capability Test
Tests all available AI services for structured JSON response capability
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_all_ai_services():
    """Test all AI services for JSON capability"""
    try:
        from app.services.ai_router import ai_router

        print("🔍 COMPREHENSIVE AI SERVICE JSON CAPABILITY TEST (WITH DEEPSEEK)")
        print("=" * 70)

        # Test prompt requesting strict JSON
        test_prompt = """
        Analyze this content: "Python is a programming language used for web development"

        You must return ONLY a valid JSON object with this exact structure (no additional text):
        {
            "topics": ["topic1", "topic2"],
            "difficulty_level": "beginner",
            "key_concepts": ["concept1", "concept2"],
            "detected_language": "en"
        }
        """

        messages = [{"role": "user", "content": test_prompt}]

        # Get available providers
        available_providers = list(ai_router.providers.keys())
        print(f"Available providers: {available_providers}")

        results = {}

        for provider_name in available_providers:
            print(f"\n🧪 Testing {provider_name.upper()}:")
            print("-" * 50)

            try:
                # Get the service
                service = ai_router.providers[provider_name]
                print(f"Service available: {service.is_available}")

                if not service.is_available:
                    print(f"❌ Service {provider_name} not available")
                    results[provider_name] = {
                        "available": False,
                        "error": "Service unavailable",
                    }
                    continue

                # Test direct service call with timeout
                print("Making API call...")
                response = await asyncio.wait_for(
                    service.generate_response(
                        messages=messages,
                        language="en",
                        max_tokens=200,
                        temperature=0.1,  # Lower temperature for structured responses
                    ),
                    timeout=30,  # 30 second timeout per service
                )

                print(f"Status: {response.status}")
                print(f"Model: {response.model}")
                print(f"Cost: ${response.cost}")

                # Show first 200 chars of content
                content_preview = response.content[:200]
                print(f"Content preview: {repr(content_preview)}")

                # Try to parse as JSON
                try:
                    parsed = json.loads(response.content)
                    print(f"✅ JSON VALID")
                    print(f"   Topics: {parsed.get('topics', [])}")
                    print(f"   Difficulty: {parsed.get('difficulty_level', 'unknown')}")
                    print(
                        f"   Key concepts: {len(parsed.get('key_concepts', []))} found"
                    )
                    print(f"   Language: {parsed.get('detected_language', 'unknown')}")

                    results[provider_name] = {
                        "available": True,
                        "json_valid": True,
                        "content": response.content,
                        "cost": response.cost,
                        "model": response.model,
                        "parsed_data": parsed,
                    }
                except json.JSONDecodeError as e:
                    print(f"❌ JSON INVALID: {e}")
                    print(f"   Raw content start: {repr(response.content[:100])}")
                    results[provider_name] = {
                        "available": True,
                        "json_valid": False,
                        "content": response.content,
                        "cost": response.cost,
                        "model": response.model,
                        "json_error": str(e),
                    }

            except asyncio.TimeoutError:
                print(f"❌ TIMEOUT: {provider_name} took longer than 30 seconds")
                results[provider_name] = {
                    "available": True,
                    "error": "Timeout after 30 seconds",
                }
            except Exception as e:
                print(f"❌ ERROR: {str(e)[:200]}")
                results[provider_name] = {"available": True, "error": str(e)[:200]}

        return results

    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback

        traceback.print_exc()
        return {}


def print_results(results):
    """Print comprehensive results summary"""
    print("\n📊 FINAL RESULTS SUMMARY:")
    print("=" * 70)
    valid_json_providers = []
    failed_providers = []
    costs = []

    for provider, result in results.items():
        if not result.get("available", False):
            print(f"{provider}: ❌ UNAVAILABLE - {result.get('error', 'Unknown')}")
            failed_providers.append(provider)
        elif result.get("json_valid", False):
            cost = result.get("cost", 0)
            model = result.get("model", "Unknown")
            print(f"{provider}: ✅ JSON VALID | Cost: ${cost:.4f} | Model: {model}")
            valid_json_providers.append(provider)
            costs.append((provider, cost))
        else:
            error = result.get("error", result.get("json_error", "Unknown error"))
            print(f"{provider}: ❌ JSON FAILED | Error: {error[:100]}")
            failed_providers.append(provider)

    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"✅ Valid JSON providers: {valid_json_providers}")
    print(f"❌ Failed providers: {failed_providers}")

    if results:
        success_rate = len(valid_json_providers) / len(results) * 100
        print(
            f"📊 Success rate: {len(valid_json_providers)}/{len(results)} ({success_rate:.1f}%)"
        )

    if costs:
        costs.sort(key=lambda x: x[1])  # Sort by cost
        print(f"\n💰 COST RANKING (cheapest first):")
        for provider, cost in costs:
            print(f"   {provider}: ${cost:.4f}")

    recommended = valid_json_providers[0] if valid_json_providers else "None working"
    print(f"\n🏆 RECOMMENDED: {recommended}")

    return {
        "valid_providers": valid_json_providers,
        "failed_providers": failed_providers,
        "success_rate": success_rate if results else 0,
        "recommended": recommended,
    }


async def main():
    """Main test execution"""
    results = await test_all_ai_services()
    summary = print_results(results)

    # Save results to file
    with open("ai_service_test_results.json", "w") as f:
        json.dump(
            {
                "test_timestamp": str(asyncio.get_event_loop().time()),
                "detailed_results": results,
                "summary": summary,
            },
            f,
            indent=2,
        )

    print(f"\n📁 Results saved to: ai_service_test_results.json")

    return len(summary["valid_providers"]) > 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
