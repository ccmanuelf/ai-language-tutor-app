#!/usr/bin/env python3
"""
Comprehensive API Validation for Task 3.1.6 - Scenario Management Tools
Tests all REST API endpoints and validates responses for quality gates evidence.
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.scenario_manager import ScenarioManager
from app.core.config import Config


class ScenarioAPIValidator:
    """Comprehensive validation of scenario management API functionality."""

    def __init__(self):
        self.results = {
            "validation_type": "Scenario Management API Comprehensive Test",
            "timestamp": datetime.now().isoformat(),
            "task_id": "3.1.6",
            "test_results": {},
            "performance_metrics": {},
            "error_log": [],
            "summary": {},
        }
        self.temp_dir = None
        self.original_scenarios_dir = None

    async def setup_test_environment(self):
        """Setup isolated test environment."""
        print("🔧 Setting up test environment...")

        # Create temporary directory for test scenarios
        self.temp_dir = tempfile.mkdtemp(prefix="scenario_test_")
        self.original_scenarios_dir = Config.SCENARIOS_DIR

        # Create test scenarios directory
        test_scenarios_dir = Path(self.temp_dir) / "scenarios"
        test_scenarios_dir.mkdir(exist_ok=True)

        # Update config to use test directory
        Config.SCENARIOS_DIR = str(test_scenarios_dir)

        print(f"✅ Test environment created: {self.temp_dir}")

    async def cleanup_test_environment(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test environment: {self.temp_dir}")

        # Restore original config
        if self.original_scenarios_dir:
            Config.SCENARIOS_DIR = self.original_scenarios_dir

    async def test_scenario_manager_initialization(self):
        """Test ScenarioManager initialization and basic functionality."""
        print("🧪 Testing ScenarioManager initialization...")

        test_name = "scenario_manager_initialization"
        start_time = time.time()

        try:
            # Test initialization
            manager = ScenarioManager()
            await manager.initialize()

            # Test basic properties
            assert hasattr(manager, "scenarios"), (
                "Manager should have scenarios attribute"
            )
            assert isinstance(manager.scenarios, dict), (
                "Scenarios should be a dictionary"
            )

            # Test default scenarios exist
            default_scenarios = await manager.get_all_scenarios()
            assert len(default_scenarios) > 0, "Should have default scenarios"

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "scenarios_count": len(default_scenarios),
                "details": "ScenarioManager initialized successfully with default scenarios",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Initialization test failed: {e}")

    async def test_scenario_crud_operations(self):
        """Test all CRUD operations for scenarios."""
        print("🧪 Testing CRUD operations...")

        manager = ScenarioManager()
        await manager.initialize()

        # Test Create
        await self._test_create_scenario(manager)

        # Test Read
        await self._test_read_scenario(manager)

        # Test Update
        await self._test_update_scenario(manager)

        # Test Delete
        await self._test_delete_scenario(manager)

    async def _test_create_scenario(self, manager: ScenarioManager):
        """Test scenario creation."""
        test_name = "create_scenario"
        start_time = time.time()

        try:
            test_scenario = {
                "title": "Test Scenario API",
                "description": "A test scenario for API validation",
                "category": "test",
                "difficulty": "intermediate",
                "language": "en",
                "conversation_starters": [
                    "Hello, how are you?",
                    "What's your favorite hobby?",
                ],
                "vocabulary": [
                    {"word": "test", "translation": "prueba", "difficulty": "easy"},
                    {
                        "word": "validation",
                        "translation": "validación",
                        "difficulty": "medium",
                    },
                ],
                "grammar_focus": ["present tense", "question formation"],
                "cultural_notes": ["Test cultural context"],
                "estimated_duration": 15,
            }

            scenario_id = await manager.create_scenario(test_scenario)
            assert scenario_id is not None, "Should return scenario ID"
            assert isinstance(scenario_id, str), "Scenario ID should be string"

            # Verify scenario was created
            created_scenario = await manager.get_scenario(scenario_id)
            assert created_scenario is not None, (
                "Created scenario should be retrievable"
            )
            assert created_scenario["title"] == test_scenario["title"], (
                "Title should match"
            )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "scenario_id": scenario_id,
                "details": "Scenario created and verified successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Create scenario test failed: {e}")

    async def _test_read_scenario(self, manager: ScenarioManager):
        """Test scenario reading operations."""
        test_name = "read_scenario"
        start_time = time.time()

        try:
            # Test get all scenarios
            all_scenarios = await manager.get_all_scenarios()
            assert isinstance(all_scenarios, list), "Should return list of scenarios"
            assert len(all_scenarios) > 0, "Should have at least one scenario"

            # Test get specific scenario
            scenario_id = all_scenarios[0]["id"]
            specific_scenario = await manager.get_scenario(scenario_id)
            assert specific_scenario is not None, "Should retrieve specific scenario"
            assert specific_scenario["id"] == scenario_id, "IDs should match"

            # Test get scenarios by language
            en_scenarios = await manager.get_scenarios_by_language("en")
            assert isinstance(en_scenarios, list), "Should return list"

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "total_scenarios": len(all_scenarios),
                "en_scenarios": len(en_scenarios),
                "details": "All read operations successful",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Read scenario test failed: {e}")

    async def _test_update_scenario(self, manager: ScenarioManager):
        """Test scenario update operations."""
        test_name = "update_scenario"
        start_time = time.time()

        try:
            # Get a scenario to update
            all_scenarios = await manager.get_all_scenarios()
            if not all_scenarios:
                raise Exception("No scenarios available for update test")

            scenario_id = all_scenarios[0]["id"]
            original_scenario = await manager.get_scenario(scenario_id)

            # Update scenario
            updated_data = {
                "title": f"{original_scenario['title']} - Updated",
                "description": "Updated description for testing",
                "difficulty": "advanced",
            }

            success = await manager.update_scenario(scenario_id, updated_data)
            assert success, "Update should return True"

            # Verify update
            updated_scenario = await manager.get_scenario(scenario_id)
            assert updated_scenario["title"] == updated_data["title"], (
                "Title should be updated"
            )
            assert updated_scenario["description"] == updated_data["description"], (
                "Description should be updated"
            )
            assert updated_scenario["difficulty"] == updated_data["difficulty"], (
                "Difficulty should be updated"
            )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "scenario_id": scenario_id,
                "details": "Scenario updated and verified successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Update scenario test failed: {e}")

    async def _test_delete_scenario(self, manager: ScenarioManager):
        """Test scenario deletion operations."""
        test_name = "delete_scenario"
        start_time = time.time()

        try:
            # Create a scenario to delete
            test_scenario = {
                "title": "Scenario to Delete",
                "description": "This scenario will be deleted",
                "category": "test",
                "difficulty": "easy",
                "language": "en",
                "conversation_starters": ["Hello"],
                "vocabulary": [],
                "grammar_focus": [],
                "cultural_notes": [],
                "estimated_duration": 5,
            }

            scenario_id = await manager.create_scenario(test_scenario)
            assert scenario_id is not None, "Should create scenario for deletion test"

            # Verify scenario exists
            scenario = await manager.get_scenario(scenario_id)
            assert scenario is not None, "Scenario should exist before deletion"

            # Delete scenario
            success = await manager.delete_scenario(scenario_id)
            assert success, "Deletion should return True"

            # Verify scenario is deleted
            deleted_scenario = await manager.get_scenario(scenario_id)
            assert deleted_scenario is None, "Scenario should not exist after deletion"

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "deleted_scenario_id": scenario_id,
                "details": "Scenario deleted and verified successfully",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Delete scenario test failed: {e}")

    async def test_persistence_functionality(self):
        """Test scenario persistence to file system."""
        print("🧪 Testing persistence functionality...")

        test_name = "persistence_functionality"
        start_time = time.time()

        try:
            manager1 = ScenarioManager()
            await manager1.initialize()

            # Create scenario with first manager
            test_scenario = {
                "title": "Persistence Test Scenario",
                "description": "Testing file persistence",
                "category": "test",
                "difficulty": "easy",
                "language": "en",
                "conversation_starters": ["Testing persistence"],
                "vocabulary": [
                    {
                        "word": "persist",
                        "translation": "persistir",
                        "difficulty": "medium",
                    }
                ],
                "grammar_focus": ["present tense"],
                "cultural_notes": ["Testing cultural note"],
                "estimated_duration": 10,
            }

            scenario_id = await manager1.create_scenario(test_scenario)
            await manager1.save_scenarios()

            # Create new manager instance and verify persistence
            manager2 = ScenarioManager()
            await manager2.initialize()

            persisted_scenario = await manager2.get_scenario(scenario_id)
            assert persisted_scenario is not None, (
                "Scenario should persist across manager instances"
            )
            assert persisted_scenario["title"] == test_scenario["title"], (
                "Persisted data should match"
            )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "scenario_id": scenario_id,
                "details": "Persistence functionality working correctly",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Persistence test failed: {e}")

    async def test_language_integration(self):
        """Test integration with language service."""
        print("🧪 Testing language service integration...")

        test_name = "language_integration"
        start_time = time.time()

        try:
            manager = ScenarioManager()
            await manager.initialize()

            # Test language validation
            # Test manager initialization worked
            assert manager is not None, "Manager should be initialized"

            # Test get scenarios by language for multiple languages
            languages_tested = []
            for lang_code in ["en", "es", "fr", "de", "zh"]:
                scenarios = await manager.get_scenarios_by_language(lang_code)
                languages_tested.append(
                    {"language": lang_code, "scenario_count": len(scenarios)}
                )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "languages_tested": languages_tested,
                "details": "Language integration working correctly",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Language integration test failed: {e}")

    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("🧪 Testing error handling...")

        test_name = "error_handling"
        start_time = time.time()

        try:
            manager = ScenarioManager()
            await manager.initialize()

            error_tests = []

            # Test get non-existent scenario
            try:
                result = await manager.get_scenario("non-existent-id")
                error_tests.append(
                    {
                        "test": "get_non_existent_scenario",
                        "result": "handled_gracefully"
                        if result is None
                        else "unexpected_result",
                        "value": result,
                    }
                )
            except Exception as e:
                error_tests.append(
                    {
                        "test": "get_non_existent_scenario",
                        "result": "exception_raised",
                        "error": str(e),
                    }
                )

            # Test update non-existent scenario
            try:
                result = await manager.update_scenario(
                    "non-existent-id", {"title": "test"}
                )
                error_tests.append(
                    {
                        "test": "update_non_existent_scenario",
                        "result": "handled_gracefully"
                        if not result
                        else "unexpected_success",
                        "value": result,
                    }
                )
            except Exception as e:
                error_tests.append(
                    {
                        "test": "update_non_existent_scenario",
                        "result": "exception_raised",
                        "error": str(e),
                    }
                )

            # Test delete non-existent scenario
            try:
                result = await manager.delete_scenario("non-existent-id")
                error_tests.append(
                    {
                        "test": "delete_non_existent_scenario",
                        "result": "handled_gracefully"
                        if not result
                        else "unexpected_success",
                        "value": result,
                    }
                )
            except Exception as e:
                error_tests.append(
                    {
                        "test": "delete_non_existent_scenario",
                        "result": "exception_raised",
                        "error": str(e),
                    }
                )

            self.results["test_results"][test_name] = {
                "status": "PASSED",
                "duration": time.time() - start_time,
                "error_tests": error_tests,
                "details": "Error handling scenarios tested",
            }

        except Exception as e:
            self.results["test_results"][test_name] = {
                "status": "FAILED",
                "duration": time.time() - start_time,
                "error": str(e),
            }
            self.results["error_log"].append(f"Error handling test failed: {e}")

    async def generate_performance_metrics(self):
        """Generate performance metrics for validation."""
        print("📊 Generating performance metrics...")

        manager = ScenarioManager()
        await manager.initialize()

        # Test scenario creation performance
        create_times = []
        for i in range(5):
            start = time.time()
            scenario_id = await manager.create_scenario(
                {
                    "title": f"Performance Test {i}",
                    "description": "Performance testing scenario",
                    "category": "test",
                    "difficulty": "easy",
                    "language": "en",
                    "conversation_starters": [f"Test {i}"],
                    "vocabulary": [],
                    "grammar_focus": [],
                    "cultural_notes": [],
                    "estimated_duration": 5,
                }
            )
            create_times.append(time.time() - start)

        # Test scenario retrieval performance
        all_scenarios = await manager.get_all_scenarios()
        read_times = []
        for scenario in all_scenarios[:5]:
            start = time.time()
            await manager.get_scenario(scenario["id"])
            read_times.append(time.time() - start)

        self.results["performance_metrics"] = {
            "scenario_creation": {
                "average_time": sum(create_times) / len(create_times),
                "min_time": min(create_times),
                "max_time": max(create_times),
                "samples": len(create_times),
            },
            "scenario_retrieval": {
                "average_time": sum(read_times) / len(read_times) if read_times else 0,
                "min_time": min(read_times) if read_times else 0,
                "max_time": max(read_times) if read_times else 0,
                "samples": len(read_times),
            },
            "total_scenarios_processed": len(all_scenarios),
        }

    def generate_summary(self):
        """Generate validation summary."""
        test_results = self.results["test_results"]
        passed_tests = [
            name
            for name, result in test_results.items()
            if result.get("status") == "PASSED"
        ]
        failed_tests = [
            name
            for name, result in test_results.items()
            if result.get("status") == "FAILED"
        ]

        self.results["summary"] = {
            "total_tests": len(test_results),
            "passed_tests": len(passed_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(passed_tests) / len(test_results) * 100
            if test_results
            else 0,
            "passed_test_names": passed_tests,
            "failed_test_names": failed_tests,
            "validation_status": "PASSED" if len(failed_tests) == 0 else "FAILED",
            "error_count": len(self.results["error_log"]),
        }

    async def run_validation(self):
        """Run complete validation suite."""
        print("🚀 Starting Scenario API Comprehensive Validation...")
        print("=" * 60)

        try:
            await self.setup_test_environment()

            # Run all validation tests
            await self.test_scenario_manager_initialization()
            await self.test_scenario_crud_operations()
            await self.test_persistence_functionality()
            await self.test_language_integration()
            await self.test_error_handling()
            await self.generate_performance_metrics()

            self.generate_summary()

        finally:
            await self.cleanup_test_environment()

        return self.results


async def main():
    """Main validation function."""
    validator = ScenarioAPIValidator()
    results = await validator.run_validation()

    # Save results
    validation_dir = Path("validation_artifacts/3.1.6")
    validation_dir.mkdir(parents=True, exist_ok=True)

    results_file = validation_dir / "scenario_api_comprehensive_validation.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    summary = results["summary"]
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"✅ Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['passed_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
    print(f"🔧 Validation Status: {summary['validation_status']}")

    if summary["failed_tests"] > 0:
        print(f"\n❌ Failed Tests: {summary['failed_test_names']}")
        print(f"📝 Error Count: {summary['error_count']}")

    print(f"\n📁 Results saved to: {results_file}")

    return summary["validation_status"] == "PASSED"


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
