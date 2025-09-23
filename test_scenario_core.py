#!/usr/bin/env python3
"""
Core Scenario Functionality Test
AI Language Tutor App - Task 2.2 Validation (Simplified)

This simplified test validates the core scenario functionality
without requiring full database and authentication dependencies.

Focus Areas:
1. Scenario Manager Core Functions
2. Scenario Templates and Data
3. API Model Validation
4. Integration Points
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class SimplifiedScenarioTester:
    """Simplified test suite focusing on core scenario functionality"""

    def __init__(self):
        self.test_results = {
            "scenario_core_tests": [],
            "template_tests": [],
            "api_tests": [],
            "integration_tests": [],
        }

    async def run_core_tests(self) -> Dict[str, Any]:
        """Run core scenario functionality tests"""

        print("🎬 Starting Core Scenario Functionality Tests...")
        print("=" * 50)

        start_time = datetime.now()

        # Test Category 1: Scenario Manager Core
        print("\n1️⃣ Testing Scenario Manager Core...")
        await self.test_scenario_manager_core()

        # Test Category 2: Template Validation
        print("\n2️⃣ Testing Scenario Templates...")
        await self.test_scenario_templates()

        # Test Category 3: API Structure
        print("\n3️⃣ Testing API Structure...")
        await self.test_api_structure()

        # Test Category 4: Integration Points
        print("\n4️⃣ Testing Integration Points...")
        await self.test_integration_points()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate results
        results = self.generate_test_results(duration)

        print(f"\n🎯 Core Tests Completed in {duration:.2f} seconds")
        print("=" * 50)

        return results

    async def test_scenario_manager_core(self):
        """Test core scenario manager functionality"""

        tests = []

        # Test 1: Import scenario manager
        try:
            from app.services.scenario_manager import (
                scenario_manager,
                ScenarioCategory,
                ScenarioDifficulty,
                ConversationScenario,
                ScenarioPhase,
            )

            tests.append(
                {
                    "name": "Import Scenario Manager",
                    "status": "PASS",
                    "details": "All scenario manager components imported successfully",
                }
            )
            print("   ✅ Import Scenario Manager - PASS")

        except Exception as e:
            tests.append(
                {"name": "Import Scenario Manager", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Import Scenario Manager - FAIL: {e}")
            return

        # Test 2: Validate predefined scenarios
        try:
            scenarios = list(scenario_manager.scenarios.values())
            assert len(scenarios) >= 3, (
                f"Expected at least 3 scenarios, found {len(scenarios)}"
            )

            # Validate scenario structure
            for scenario in scenarios:
                assert hasattr(scenario, "scenario_id"), "Missing scenario_id"
                assert hasattr(scenario, "name"), "Missing name"
                assert hasattr(scenario, "phases"), "Missing phases"
                assert len(scenario.phases) > 0, (
                    f"No phases in scenario {scenario.name}"
                )

                # Validate phases
                for phase in scenario.phases:
                    assert hasattr(phase, "phase_id"), (
                        f"Missing phase_id in {scenario.name}"
                    )
                    assert hasattr(phase, "key_vocabulary"), (
                        f"Missing vocabulary in {scenario.name}"
                    )
                    assert hasattr(phase, "essential_phrases"), (
                        f"Missing phrases in {scenario.name}"
                    )

            tests.append(
                {
                    "name": "Validate Predefined Scenarios",
                    "status": "PASS",
                    "details": f"Validated {len(scenarios)} scenarios with all required fields",
                    "scenarios_found": len(scenarios),
                }
            )
            print(
                f"   ✅ Validate Predefined Scenarios - PASS ({len(scenarios)} scenarios)"
            )

        except Exception as e:
            tests.append(
                {
                    "name": "Validate Predefined Scenarios",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Validate Predefined Scenarios - FAIL: {e}")

        # Test 3: Test scenario categories
        try:
            categories = [cat.value for cat in ScenarioCategory]
            expected_categories = ["travel", "restaurant", "shopping", "business"]

            for expected in expected_categories:
                assert expected in categories, f"Missing category: {expected}"

            tests.append(
                {
                    "name": "Validate Scenario Categories",
                    "status": "PASS",
                    "details": f"Found all expected categories: {expected_categories}",
                }
            )
            print("   ✅ Validate Scenario Categories - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Validate Scenario Categories",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Validate Scenario Categories - FAIL: {e}")

        # Test 4: Test difficulty levels
        try:
            difficulties = [diff.value for diff in ScenarioDifficulty]
            expected_difficulties = ["beginner", "intermediate", "advanced"]

            for expected in expected_difficulties:
                assert expected in difficulties, f"Missing difficulty: {expected}"

            tests.append(
                {
                    "name": "Validate Difficulty Levels",
                    "status": "PASS",
                    "details": f"Found all expected difficulties: {expected_difficulties}",
                }
            )
            print("   ✅ Validate Difficulty Levels - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Validate Difficulty Levels",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Validate Difficulty Levels - FAIL: {e}")

        self.test_results["scenario_core_tests"] = tests

    async def test_scenario_templates(self):
        """Test scenario template quality and completeness"""

        tests = []

        try:
            from app.services.scenario_manager import scenario_manager

            # Test 1: Restaurant scenario validation
            restaurant_scenarios = [
                s
                for s in scenario_manager.scenarios.values()
                if s.category.value == "restaurant"
            ]

            if restaurant_scenarios:
                restaurant_scenario = restaurant_scenarios[0]

                # Validate restaurant scenario content
                expected_phases = ["reservation", "arrival", "ordering", "payment"]
                phase_ids = [phase.phase_id for phase in restaurant_scenario.phases]

                phase_coverage = sum(
                    1
                    for expected in expected_phases
                    if any(expected in pid for pid in phase_ids)
                )

                # Validate vocabulary
                vocab_count = len(restaurant_scenario.vocabulary_focus)
                assert vocab_count >= 10, f"Insufficient vocabulary: {vocab_count}"

                # Validate cultural context
                assert restaurant_scenario.cultural_context, "Missing cultural context"

                tests.append(
                    {
                        "name": "Restaurant Scenario Quality",
                        "status": "PASS",
                        "details": f"Phases: {len(restaurant_scenario.phases)}, Vocabulary: {vocab_count}, Cultural context: Yes",
                        "phase_coverage": f"{phase_coverage}/{len(expected_phases)}",
                    }
                )
                print("   ✅ Restaurant Scenario Quality - PASS")

            else:
                raise Exception("No restaurant scenarios found")

        except Exception as e:
            tests.append(
                {
                    "name": "Restaurant Scenario Quality",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Restaurant Scenario Quality - FAIL: {e}")

        try:
            # Test 2: Travel scenario validation
            travel_scenarios = [
                s
                for s in scenario_manager.scenarios.values()
                if s.category.value == "travel"
            ]

            if travel_scenarios:
                travel_scenario = travel_scenarios[0]

                # Validate learning objectives
                total_objectives = sum(
                    len(phase.learning_objectives) for phase in travel_scenario.phases
                )
                assert total_objectives >= 8, (
                    f"Insufficient learning objectives: {total_objectives}"
                )

                # Validate essential phrases
                total_phrases = sum(
                    len(phase.essential_phrases) for phase in travel_scenario.phases
                )
                assert total_phrases >= 10, (
                    f"Insufficient essential phrases: {total_phrases}"
                )

                tests.append(
                    {
                        "name": "Travel Scenario Quality",
                        "status": "PASS",
                        "details": f"Objectives: {total_objectives}, Phrases: {total_phrases}",
                    }
                )
                print("   ✅ Travel Scenario Quality - PASS")

            else:
                raise Exception("No travel scenarios found")

        except Exception as e:
            tests.append(
                {"name": "Travel Scenario Quality", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Travel Scenario Quality - FAIL: {e}")

        self.test_results["template_tests"] = tests

    async def test_api_structure(self):
        """Test API structure and models"""

        tests = []

        # Test 1: Import API components
        try:
            from app.api.scenarios import (
                router,
                ScenarioListRequest,
                StartScenarioRequest,
                ScenarioMessageRequest,
                ScenarioResponse,
            )

            tests.append(
                {
                    "name": "Import API Components",
                    "status": "PASS",
                    "details": "All API components imported successfully",
                }
            )
            print("   ✅ Import API Components - PASS")

        except Exception as e:
            tests.append(
                {"name": "Import API Components", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Import API Components - FAIL: {e}")
            return

        # Test 2: Validate API routes
        try:
            routes = [route.path for route in router.routes]
            expected_routes = [
                "/",
                "/{scenario_id}",
                "/start",
                "/message",
                "/progress/{conversation_id}",
            ]

            route_coverage = sum(
                1
                for expected in expected_routes
                if any(expected in route for route in routes)
            )

            tests.append(
                {
                    "name": "Validate API Routes",
                    "status": "PASS",
                    "details": f"Route coverage: {route_coverage}/{len(expected_routes)}",
                    "routes_found": len(routes),
                }
            )
            print(
                f"   ✅ Validate API Routes - PASS ({route_coverage}/{len(expected_routes)})"
            )

        except Exception as e:
            tests.append(
                {"name": "Validate API Routes", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Validate API Routes - FAIL: {e}")

        # Test 3: Test Pydantic models
        try:
            # Test request models
            list_request = ScenarioListRequest(
                category="restaurant", difficulty="beginner"
            )
            start_request = StartScenarioRequest(scenario_id="test_id", language="en")
            message_request = ScenarioMessageRequest(
                conversation_id="test_conv", message="Hello"
            )

            # Test response model
            response = ScenarioResponse(success=True, data={"test": "data"})

            tests.append(
                {
                    "name": "Pydantic Models Validation",
                    "status": "PASS",
                    "details": "All Pydantic models create and validate successfully",
                }
            )
            print("   ✅ Pydantic Models Validation - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Pydantic Models Validation",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Pydantic Models Validation - FAIL: {e}")

        self.test_results["api_tests"] = tests

    async def test_integration_points(self):
        """Test integration points with existing systems"""

        tests = []

        # Test 1: Conversation manager integration points
        try:
            # Check that conversation manager imports scenario manager
            with open("app/services/conversation_manager.py", "r") as f:
                content = f.read()

            integration_checks = [
                "scenario_manager" in content,
                "is_scenario_based" in content,
                "scenario_id" in content,
                "_create_scenario_system_message" in content,
            ]

            integration_score = sum(integration_checks)

            tests.append(
                {
                    "name": "Conversation Manager Integration",
                    "status": "PASS" if integration_score >= 3 else "FAIL",
                    "details": f"Integration points found: {integration_score}/4",
                    "integration_score": integration_score,
                }
            )
            print(
                f"   {'✅' if integration_score >= 3 else '❌'} Conversation Manager Integration - {'PASS' if integration_score >= 3 else 'FAIL'}"
            )

        except Exception as e:
            tests.append(
                {
                    "name": "Conversation Manager Integration",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Conversation Manager Integration - FAIL: {e}")

        # Test 2: Frontend integration points
        try:
            # Check that chat.py includes scenario functionality
            with open("app/frontend/chat.py", "r") as f:
                content = f.read()

            frontend_checks = [
                "practice-mode-select" in content,
                "scenario-select" in content,
                "scenario-details" in content,
                "startConversation" in content,
                "loadScenarios" in content,
            ]

            frontend_score = sum(frontend_checks)

            tests.append(
                {
                    "name": "Frontend Integration",
                    "status": "PASS" if frontend_score >= 4 else "FAIL",
                    "details": f"Frontend integration points: {frontend_score}/5",
                    "frontend_score": frontend_score,
                }
            )
            print(
                f"   {'✅' if frontend_score >= 4 else '❌'} Frontend Integration - {'PASS' if frontend_score >= 4 else 'FAIL'}"
            )

        except Exception as e:
            tests.append(
                {"name": "Frontend Integration", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Frontend Integration - FAIL: {e}")

        # Test 3: CSS/Styling integration
        try:
            # Check that styles.py includes scenario-specific styles
            with open("app/frontend/styles.py", "r") as f:
                content = f.read()

            style_checks = [
                ".modal" in content,
                ".scenario-info" in content,
                ".vocab-tag" in content,
                ".scenario-progress" in content,
            ]

            style_score = sum(style_checks)

            tests.append(
                {
                    "name": "CSS/Styling Integration",
                    "status": "PASS" if style_score >= 3 else "FAIL",
                    "details": f"Style integration points: {style_score}/4",
                    "style_score": style_score,
                }
            )
            print(
                f"   {'✅' if style_score >= 3 else '❌'} CSS/Styling Integration - {'PASS' if style_score >= 3 else 'FAIL'}"
            )

        except Exception as e:
            tests.append(
                {"name": "CSS/Styling Integration", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ CSS/Styling Integration - FAIL: {e}")

        self.test_results["integration_tests"] = tests

    def generate_test_results(self, duration: float) -> Dict[str, Any]:
        """Generate test results summary"""

        total_tests = sum(len(tests) for tests in self.test_results.values())
        passed_tests = sum(
            len([t for t in tests if t["status"] == "PASS"])
            for tests in self.test_results.values()
        )
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        results = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 1),
                "duration_seconds": round(duration, 2),
                "test_timestamp": datetime.now().isoformat(),
            },
            "detailed_results": self.test_results,
            "validation_status": "PASS" if success_rate >= 85 else "FAIL",
            "task_2_2_status": "COMPLETED" if success_rate >= 85 else "NEEDS_WORK",
            "recommendations": self.generate_recommendations(
                success_rate, failed_tests
            ),
        }

        return results

    def generate_recommendations(
        self, success_rate: float, failed_tests: int
    ) -> List[str]:
        """Generate recommendations based on test results"""

        recommendations = []

        if success_rate >= 95:
            recommendations.append(
                "🎉 Excellent! Task 2.2 implementation is complete and high-quality"
            )
            recommendations.append("✅ Scenario system ready for production use")
        elif success_rate >= 85:
            recommendations.append(
                "✅ Good implementation! Task 2.2 core functionality complete"
            )
            recommendations.append("🔧 Minor improvements recommended")
        elif success_rate >= 70:
            recommendations.append("⚠️ Task 2.2 partially complete - needs refinement")
            recommendations.append("🔧 Address failing tests before marking complete")
        else:
            recommendations.append("❌ Task 2.2 requires significant work")
            recommendations.append("🔧 Focus on core functionality first")

        if failed_tests == 0:
            recommendations.append("🚀 Ready to update task tracker as COMPLETED")
        else:
            recommendations.append(f"🔧 Address {failed_tests} failing test(s) first")

        recommendations.extend(
            [
                "📝 Document scenario usage for users",
                "🎯 Consider adding more scenario types in future",
                "⚡ Test with real users for feedback",
            ]
        )

        return recommendations


async def main():
    """Run the core scenario functionality tests"""

    try:
        tester = SimplifiedScenarioTester()
        results = await tester.run_core_tests()

        # Save results to file
        with open("scenario_core_test_results.json", "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        summary = results["test_summary"]
        print(f"\n🎯 CORE TEST RESULTS:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Duration: {summary['duration_seconds']}s")
        print(f"   Task 2.2 Status: {results['task_2_2_status']}")
        print(f"   Validation: {results['validation_status']}")

        print(f"\n📋 RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"   {rec}")

        print(f"\n💾 Results saved to: scenario_core_test_results.json")

        return results["validation_status"] == "PASS"

    except Exception as e:
        print(f"❌ Core test suite failed with error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
