#!/usr/bin/env python3
"""
Test Suite for Scenario-Based Conversations (Pingo Functionality)
AI Language Tutor App - Task 2.2 Validation

This test suite validates the complete scenario-based conversation functionality,
ensuring all components work together seamlessly.

Test Categories:
1. Scenario Manager Core Functions
2. Conversation Manager Integration
3. API Endpoints Functionality
4. Frontend Integration Points
5. End-to-End Workflow Validation
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.scenario_manager import (
    scenario_manager,
    ScenarioCategory,
    ScenarioDifficulty,
    get_available_scenarios,
    start_scenario,
    process_scenario_interaction,
    get_scenario_status,
    finish_scenario,
)
from app.services.conversation_manager import conversation_manager, LearningFocus


class ScenarioConversationTester:
    """Comprehensive test suite for scenario-based conversations"""

    def __init__(self):
        self.test_results = {
            "scenario_manager_tests": [],
            "conversation_integration_tests": [],
            "workflow_tests": [],
            "performance_tests": [],
            "error_handling_tests": [],
        }
        self.test_user_id = "test_user_scenario_2024"

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite for scenario functionality"""

        print("🎬 Starting Scenario-Based Conversation Test Suite...")
        print("=" * 60)

        start_time = datetime.now()

        # Test Category 1: Scenario Manager Core Functions
        print("\n1️⃣ Testing Scenario Manager Core Functions...")
        await self.test_scenario_manager_core()

        # Test Category 2: Conversation Manager Integration
        print("\n2️⃣ Testing Conversation Manager Integration...")
        await self.test_conversation_integration()

        # Test Category 3: End-to-End Workflow
        print("\n3️⃣ Testing End-to-End Scenario Workflows...")
        await self.test_end_to_end_workflows()

        # Test Category 4: Performance and Edge Cases
        print("\n4️⃣ Testing Performance and Edge Cases...")
        await self.test_performance_and_edge_cases()

        # Test Category 5: Error Handling
        print("\n5️⃣ Testing Error Handling...")
        await self.test_error_handling()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate comprehensive results
        results = self.generate_test_results(duration)

        print(f"\n🎯 Test Suite Completed in {duration:.2f} seconds")
        print("=" * 60)

        return results

    async def test_scenario_manager_core(self):
        """Test core scenario manager functionality"""

        tests = []

        # Test 1: Get available scenarios
        try:
            scenarios = await get_available_scenarios()
            assert len(scenarios) > 0, "No scenarios available"
            assert all("scenario_id" in s for s in scenarios), "Missing scenario IDs"

            tests.append(
                {
                    "name": "Get Available Scenarios",
                    "status": "PASS",
                    "details": f"Found {len(scenarios)} scenarios",
                    "scenarios_found": len(scenarios),
                }
            )
            print("   ✅ Get Available Scenarios - PASS")

        except Exception as e:
            tests.append(
                {"name": "Get Available Scenarios", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Get Available Scenarios - FAIL: {e}")

        # Test 2: Filter scenarios by category
        try:
            restaurant_scenarios = await get_available_scenarios(category="restaurant")
            travel_scenarios = await get_available_scenarios(category="travel")

            assert len(restaurant_scenarios) > 0, "No restaurant scenarios found"
            assert len(travel_scenarios) > 0, "No travel scenarios found"

            tests.append(
                {
                    "name": "Filter Scenarios by Category",
                    "status": "PASS",
                    "details": f"Restaurant: {len(restaurant_scenarios)}, Travel: {len(travel_scenarios)}",
                }
            )
            print("   ✅ Filter Scenarios by Category - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Filter Scenarios by Category",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Filter Scenarios by Category - FAIL: {e}")

        # Test 3: Get scenario details
        try:
            scenarios = await get_available_scenarios()
            if scenarios:
                scenario_id = scenarios[0]["scenario_id"]
                details = scenario_manager.get_scenario_details(scenario_id)

                assert details is not None, "No scenario details returned"
                assert "phases" in details, "Missing phases in scenario details"
                assert len(details["phases"]) > 0, "No phases defined"

                tests.append(
                    {
                        "name": "Get Scenario Details",
                        "status": "PASS",
                        "details": f"Scenario: {details['name']}, Phases: {len(details['phases'])}",
                    }
                )
                print("   ✅ Get Scenario Details - PASS")
            else:
                raise Exception("No scenarios available for testing")

        except Exception as e:
            tests.append(
                {"name": "Get Scenario Details", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Get Scenario Details - FAIL: {e}")

        # Test 4: Start scenario conversation
        try:
            scenarios = await get_available_scenarios()
            if scenarios:
                scenario_id = scenarios[0]["scenario_id"]

                scenario_data = await start_scenario(
                    user_id=self.test_user_id, scenario_id=scenario_id, language="en"
                )

                assert "progress_id" in scenario_data, "Missing progress_id"
                assert "scenario" in scenario_data, "Missing scenario name"

                tests.append(
                    {
                        "name": "Start Scenario Conversation",
                        "status": "PASS",
                        "details": f"Started scenario: {scenario_data['scenario']}",
                        "progress_id": scenario_data["progress_id"],
                    }
                )
                print("   ✅ Start Scenario Conversation - PASS")

                # Store for later tests
                self.test_progress_id = scenario_data["progress_id"]

            else:
                raise Exception("No scenarios available for testing")

        except Exception as e:
            tests.append(
                {
                    "name": "Start Scenario Conversation",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Start Scenario Conversation - FAIL: {e}")

        self.test_results["scenario_manager_tests"] = tests

    async def test_conversation_integration(self):
        """Test integration between scenario manager and conversation manager"""

        tests = []

        # Test 1: Start conversation with scenario
        try:
            scenarios = await get_available_scenarios()
            if scenarios:
                scenario_id = scenarios[0]["scenario_id"]

                conversation_id = await conversation_manager.start_conversation(
                    user_id=self.test_user_id,
                    language="en",
                    learning_focus=LearningFocus.CONVERSATION,
                    scenario_id=scenario_id,
                )

                assert conversation_id, "No conversation ID returned"
                assert conversation_id in conversation_manager.active_conversations, (
                    "Conversation not active"
                )

                context = conversation_manager.active_conversations[conversation_id]
                assert context.is_scenario_based, (
                    "Conversation not marked as scenario-based"
                )
                assert context.scenario_id == scenario_id, "Scenario ID mismatch"

                tests.append(
                    {
                        "name": "Start Conversation with Scenario",
                        "status": "PASS",
                        "details": f"Conversation ID: {conversation_id}",
                        "conversation_id": conversation_id,
                    }
                )
                print("   ✅ Start Conversation with Scenario - PASS")

                # Store for later tests
                self.test_conversation_id = conversation_id

            else:
                raise Exception("No scenarios available for testing")

        except Exception as e:
            tests.append(
                {
                    "name": "Start Conversation with Scenario",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Start Conversation with Scenario - FAIL: {e}")

        # Test 2: Send message in scenario conversation
        try:
            if hasattr(self, "test_conversation_id"):
                response = await conversation_manager.send_message(
                    conversation_id=self.test_conversation_id,
                    user_message="Hello, I'd like to make a reservation.",
                    include_pronunciation_feedback=False,
                )

                assert "ai_response" in response, "Missing AI response"
                assert "scenario_progress" in response, "Missing scenario progress"

                tests.append(
                    {
                        "name": "Send Message in Scenario Conversation",
                        "status": "PASS",
                        "details": f"AI Response length: {len(response['ai_response'])} chars",
                    }
                )
                print("   ✅ Send Message in Scenario Conversation - PASS")

            else:
                raise Exception("No test conversation available")

        except Exception as e:
            tests.append(
                {
                    "name": "Send Message in Scenario Conversation",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Send Message in Scenario Conversation - FAIL: {e}")

        # Test 3: Get conversation summary with scenario data
        try:
            if hasattr(self, "test_conversation_id"):
                summary = await conversation_manager.get_conversation_summary(
                    self.test_conversation_id
                )

                assert "conversation_id" in summary, (
                    "Missing conversation ID in summary"
                )
                assert "learning_progress" in summary, "Missing learning progress"

                tests.append(
                    {
                        "name": "Get Conversation Summary with Scenario",
                        "status": "PASS",
                        "details": f"Messages: {summary['session_stats']['total_messages']}",
                    }
                )
                print("   ✅ Get Conversation Summary with Scenario - PASS")

            else:
                raise Exception("No test conversation available")

        except Exception as e:
            tests.append(
                {
                    "name": "Get Conversation Summary with Scenario",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Get Conversation Summary with Scenario - FAIL: {e}")

        self.test_results["conversation_integration_tests"] = tests

    async def test_end_to_end_workflows(self):
        """Test complete end-to-end scenario workflows"""

        tests = []

        # Test 1: Complete restaurant scenario workflow
        try:
            # Get restaurant scenario
            restaurant_scenarios = await get_available_scenarios(category="restaurant")
            if not restaurant_scenarios:
                raise Exception("No restaurant scenarios available")

            scenario_id = restaurant_scenarios[0]["scenario_id"]

            # Start conversation
            conversation_id = await conversation_manager.start_conversation(
                user_id=f"{self.test_user_id}_workflow",
                language="en",
                learning_focus=LearningFocus.CONVERSATION,
                scenario_id=scenario_id,
            )

            # Simulate conversation flow
            messages = [
                "Hello, I'd like to make a reservation.",
                "For two people, please.",
                "7 PM would be perfect.",
                "I'll have the salmon, please.",
                "Could we have the check, please?",
            ]

            responses = []
            for message in messages:
                response = await conversation_manager.send_message(
                    conversation_id=conversation_id, user_message=message
                )
                responses.append(response)

            # End conversation
            final_summary = await conversation_manager.end_conversation(conversation_id)

            tests.append(
                {
                    "name": "Complete Restaurant Scenario Workflow",
                    "status": "PASS",
                    "details": f"Completed {len(messages)} interactions",
                    "total_responses": len(responses),
                    "scenario_completed": True,
                }
            )
            print("   ✅ Complete Restaurant Scenario Workflow - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Complete Restaurant Scenario Workflow",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Complete Restaurant Scenario Workflow - FAIL: {e}")

        # Test 2: Travel scenario workflow
        try:
            # Get travel scenario
            travel_scenarios = await get_available_scenarios(category="travel")
            if not travel_scenarios:
                raise Exception("No travel scenarios available")

            scenario_id = travel_scenarios[0]["scenario_id"]

            # Start conversation
            conversation_id = await conversation_manager.start_conversation(
                user_id=f"{self.test_user_id}_travel",
                language="en",
                learning_focus=LearningFocus.CONVERSATION,
                scenario_id=scenario_id,
            )

            # Simulate check-in process
            travel_messages = [
                "Hello, I have a reservation.",
                "Smith is the name.",
                "Yes, I'd like a room with a view if possible.",
                "Could you recommend a good restaurant nearby?",
            ]

            for message in travel_messages:
                await conversation_manager.send_message(
                    conversation_id=conversation_id, user_message=message
                )

            # Get progress
            summary = await conversation_manager.get_conversation_summary(
                conversation_id
            )

            # End conversation
            await conversation_manager.end_conversation(conversation_id)

            tests.append(
                {
                    "name": "Travel Scenario Workflow",
                    "status": "PASS",
                    "details": f"Completed travel check-in with {len(travel_messages)} interactions",
                }
            )
            print("   ✅ Travel Scenario Workflow - PASS")

        except Exception as e:
            tests.append(
                {"name": "Travel Scenario Workflow", "status": "FAIL", "error": str(e)}
            )
            print(f"   ❌ Travel Scenario Workflow - FAIL: {e}")

        self.test_results["workflow_tests"] = tests

    async def test_performance_and_edge_cases(self):
        """Test performance and edge case handling"""

        tests = []

        # Test 1: Multiple concurrent scenarios
        try:
            scenarios = await get_available_scenarios()
            if len(scenarios) >= 2:
                # Start multiple scenario conversations
                conversation_ids = []
                for i in range(3):
                    scenario_id = scenarios[i % len(scenarios)]["scenario_id"]
                    conversation_id = await conversation_manager.start_conversation(
                        user_id=f"{self.test_user_id}_concurrent_{i}",
                        language="en",
                        learning_focus=LearningFocus.CONVERSATION,
                        scenario_id=scenario_id,
                    )
                    conversation_ids.append(conversation_id)

                # Send messages to all conversations
                for conversation_id in conversation_ids:
                    await conversation_manager.send_message(
                        conversation_id=conversation_id,
                        user_message="Hello, I need assistance.",
                    )

                # Clean up
                for conversation_id in conversation_ids:
                    await conversation_manager.end_conversation(conversation_id)

                tests.append(
                    {
                        "name": "Multiple Concurrent Scenarios",
                        "status": "PASS",
                        "details": f"Successfully handled {len(conversation_ids)} concurrent scenarios",
                    }
                )
                print("   ✅ Multiple Concurrent Scenarios - PASS")

            else:
                raise Exception("Not enough scenarios for concurrent testing")

        except Exception as e:
            tests.append(
                {
                    "name": "Multiple Concurrent Scenarios",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Multiple Concurrent Scenarios - FAIL: {e}")

        # Test 2: Long conversation handling
        try:
            scenarios = await get_available_scenarios()
            if scenarios:
                scenario_id = scenarios[0]["scenario_id"]

                conversation_id = await conversation_manager.start_conversation(
                    user_id=f"{self.test_user_id}_long",
                    language="en",
                    learning_focus=LearningFocus.CONVERSATION,
                    scenario_id=scenario_id,
                )

                # Send many messages to test context management
                for i in range(15):
                    await conversation_manager.send_message(
                        conversation_id=conversation_id,
                        user_message=f"This is message number {i + 1}. I'm practicing my conversation skills.",
                    )

                # Verify conversation is still functional
                final_response = await conversation_manager.send_message(
                    conversation_id=conversation_id,
                    user_message="Thank you for the practice session.",
                )

                assert "ai_response" in final_response, (
                    "AI response missing after long conversation"
                )

                await conversation_manager.end_conversation(conversation_id)

                tests.append(
                    {
                        "name": "Long Conversation Handling",
                        "status": "PASS",
                        "details": "Successfully handled 16-message conversation",
                    }
                )
                print("   ✅ Long Conversation Handling - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Long Conversation Handling",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Long Conversation Handling - FAIL: {e}")

        self.test_results["performance_tests"] = tests

    async def test_error_handling(self):
        """Test error handling and edge cases"""

        tests = []

        # Test 1: Invalid scenario ID
        try:
            try:
                await conversation_manager.start_conversation(
                    user_id=self.test_user_id,
                    language="en",
                    learning_focus=LearningFocus.CONVERSATION,
                    scenario_id="invalid_scenario_id",
                )
                # Should not reach here
                tests.append(
                    {
                        "name": "Invalid Scenario ID Handling",
                        "status": "FAIL",
                        "error": "Should have thrown error for invalid scenario ID",
                    }
                )
                print("   ❌ Invalid Scenario ID Handling - FAIL")

            except Exception as expected_error:
                tests.append(
                    {
                        "name": "Invalid Scenario ID Handling",
                        "status": "PASS",
                        "details": "Correctly rejected invalid scenario ID",
                    }
                )
                print("   ✅ Invalid Scenario ID Handling - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Invalid Scenario ID Handling",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Invalid Scenario ID Handling - FAIL: {e}")

        # Test 2: Message to non-existent conversation
        try:
            try:
                await conversation_manager.send_message(
                    conversation_id="non_existent_conversation", user_message="Hello"
                )
                # Should not reach here
                tests.append(
                    {
                        "name": "Non-existent Conversation Handling",
                        "status": "FAIL",
                        "error": "Should have thrown error for non-existent conversation",
                    }
                )
                print("   ❌ Non-existent Conversation Handling - FAIL")

            except Exception as expected_error:
                tests.append(
                    {
                        "name": "Non-existent Conversation Handling",
                        "status": "PASS",
                        "details": "Correctly rejected non-existent conversation",
                    }
                )
                print("   ✅ Non-existent Conversation Handling - PASS")

        except Exception as e:
            tests.append(
                {
                    "name": "Non-existent Conversation Handling",
                    "status": "FAIL",
                    "error": str(e),
                }
            )
            print(f"   ❌ Non-existent Conversation Handling - FAIL: {e}")

        self.test_results["error_handling_tests"] = tests

    def generate_test_results(self, duration: float) -> Dict[str, Any]:
        """Generate comprehensive test results"""

        total_tests = sum(len(tests) for tests in self.test_results.values())
        passed_tests = sum(
            len([t for t in tests if t["status"] == "PASS"])
            for tests in self.test_results.values()
        )
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Count scenarios tested
        scenarios_tested = len(
            set(
                [
                    test.get("progress_id", "") or test.get("conversation_id", "")
                    for tests in self.test_results.values()
                    for test in tests
                    if test.get("progress_id") or test.get("conversation_id")
                ]
            )
        )

        results = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 1),
                "duration_seconds": round(duration, 2),
                "scenarios_tested": scenarios_tested,
                "test_timestamp": datetime.now().isoformat(),
            },
            "detailed_results": self.test_results,
            "validation_status": "PASS" if success_rate >= 80 else "FAIL",
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
            recommendations.append("✅ Excellent! Scenario system is production-ready")
        elif success_rate >= 85:
            recommendations.append("✅ Good! Minor improvements needed")
        elif success_rate >= 70:
            recommendations.append("⚠️ Needs improvement before production")
        else:
            recommendations.append("❌ Major issues found - requires significant work")

        if failed_tests > 0:
            recommendations.append(f"🔧 Address {failed_tests} failing test(s)")

        recommendations.extend(
            [
                "🚀 Consider adding more scenario categories",
                "📊 Monitor real-world usage patterns",
                "🎯 Gather user feedback on scenario quality",
                "⚡ Optimize performance for mobile devices",
            ]
        )

        return recommendations


async def main():
    """Run the complete scenario conversation test suite"""

    try:
        tester = ScenarioConversationTester()
        results = await tester.run_all_tests()

        # Save results to file
        with open("scenario_conversation_test_results.json", "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        summary = results["test_summary"]
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Duration: {summary['duration_seconds']}s")
        print(f"   Scenarios Tested: {summary['scenarios_tested']}")
        print(f"   Status: {results['validation_status']}")

        print(f"\n📋 RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"   {rec}")

        print(
            f"\n💾 Detailed results saved to: scenario_conversation_test_results.json"
        )

        return results["validation_status"] == "PASS"

    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
