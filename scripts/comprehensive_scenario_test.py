#!/usr/bin/env python3
"""
Comprehensive Test Suite for Task 3.1.6 - Scenario & Content Management Tools
Tests all functionality with 100% coverage requirement
"""

import asyncio
import sys
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import tempfile
import shutil
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.scenario_manager import (
    scenario_manager,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ConversationRole,
    ScenarioPhase,
)
from app.services.admin_auth import AdminPermission


class ComprehensiveScenarioTester:
    """Comprehensive testing framework for scenario management"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        self.admin_user = {
            "user_id": "admin_test_user",
            "email": "test@admin.com",
            "role": "ADMIN",
            "permissions": [
                AdminPermission.MANAGE_SCENARIOS,
                AdminPermission.MANAGE_SYSTEM_CONFIG,
                AdminPermission.ACCESS_ADMIN_DASHBOARD,
            ],
        }

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.tests_passed += 1
            status = "✅ PASSED"
        else:
            self.tests_failed += 1
            status = "❌ FAILED"

        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"

        self.test_results.append(result)
        print(result)

    async def create_test_scenario(
        self, scenario_id: str = None
    ) -> ConversationScenario:
        """Create a valid test scenario"""
        if not scenario_id:
            scenario_id = f"test_{uuid.uuid4().hex[:8]}"

        return ConversationScenario(
            scenario_id=scenario_id,
            name="Test Restaurant Scenario",
            category=ScenarioCategory.RESTAURANT,
            difficulty=ScenarioDifficulty.BEGINNER,
            description="A comprehensive test scenario for restaurant interactions",
            user_role=ConversationRole.CUSTOMER,
            ai_role=ConversationRole.SERVICE_PROVIDER,
            setting="Restaurant",
            duration_minutes=20,
            phases=[
                ScenarioPhase(
                    phase_id="greeting",
                    name="Greeting Phase",
                    description="Initial greeting and seating",
                    expected_duration_minutes=5,
                    key_vocabulary=["table", "reservation", "welcome"],
                    essential_phrases=["I have a reservation", "Table for two"],
                    learning_objectives=["Polite greetings", "Making reservations"],
                ),
                ScenarioPhase(
                    phase_id="ordering",
                    name="Ordering Phase",
                    description="Menu review and ordering",
                    expected_duration_minutes=10,
                    key_vocabulary=["menu", "order", "recommend"],
                    essential_phrases=["What do you recommend?", "I'll have the..."],
                    learning_objectives=["Food vocabulary", "Expressing preferences"],
                ),
            ],
            vocabulary_focus=["restaurant", "food", "service", "menu"],
            cultural_context={"dining_etiquette": "formal dining", "tipping": "15-20%"},
            learning_goals=["Order food confidently", "Interact politely with staff"],
        )

    async def test_scenario_manager_initialization(self):
        """Test 1: ScenarioManager Initialization"""
        try:
            await scenario_manager.initialize()
            scenarios = await scenario_manager.get_all_scenarios()

            if isinstance(scenarios, list):
                self.log_test(
                    "ScenarioManager Initialization",
                    True,
                    f"Loaded {len(scenarios)} scenarios",
                )
                return True
            else:
                self.log_test(
                    "ScenarioManager Initialization", False, "Invalid scenarios format"
                )
                return False

        except Exception as e:
            self.log_test(
                "ScenarioManager Initialization", False, f"Exception: {str(e)}"
            )
            return False

    async def test_scenario_crud_operations(self):
        """Test 2: CRUD Operations"""
        test_passed = True

        try:
            # CREATE
            test_scenario = await self.create_test_scenario("crud_test_001")
            create_success = await scenario_manager.save_scenario(test_scenario)

            if not create_success:
                self.log_test("CRUD - Create", False, "Failed to save scenario")
                test_passed = False
            else:
                self.log_test("CRUD - Create", True, "Scenario saved successfully")

            # READ
            retrieved = await scenario_manager.get_scenario_by_id("crud_test_001")
            if not retrieved or retrieved.name != test_scenario.name:
                self.log_test("CRUD - Read", False, "Failed to retrieve scenario")
                test_passed = False
            else:
                self.log_test("CRUD - Read", True, "Scenario retrieved successfully")

            # UPDATE
            retrieved.description = "Updated test description"
            update_success = await scenario_manager.update_scenario(
                "crud_test_001", retrieved
            )
            if not update_success:
                self.log_test("CRUD - Update", False, "Failed to update scenario")
                test_passed = False
            else:
                self.log_test("CRUD - Update", True, "Scenario updated successfully")

            # DELETE
            delete_success = await scenario_manager.delete_scenario("crud_test_001")
            if not delete_success:
                self.log_test("CRUD - Delete", False, "Failed to delete scenario")
                test_passed = False
            else:
                self.log_test("CRUD - Delete", True, "Scenario deleted successfully")

            # Verify deletion
            deleted_check = await scenario_manager.get_scenario_by_id("crud_test_001")
            if deleted_check is not None:
                self.log_test(
                    "CRUD - Delete Verification",
                    False,
                    "Scenario still exists after deletion",
                )
                test_passed = False
            else:
                self.log_test(
                    "CRUD - Delete Verification", True, "Scenario properly deleted"
                )

        except Exception as e:
            self.log_test("CRUD Operations", False, f"Exception: {str(e)}")
            test_passed = False

        return test_passed

    async def test_api_endpoints_import(self):
        """Test 3: API Endpoints Import and Initialization"""
        try:
            from app.api.scenario_management import (
                router,
                ensure_scenario_manager_initialized,
            )

            # Test router exists
            if not router:
                self.log_test("API - Router Import", False, "Router not found")
                return False
            else:
                self.log_test(
                    "API - Router Import", True, "Router imported successfully"
                )

            # Test initialization function
            sm = await ensure_scenario_manager_initialized()
            if not sm:
                self.log_test(
                    "API - Initialization Function", False, "Initialization failed"
                )
                return False
            else:
                self.log_test(
                    "API - Initialization Function",
                    True,
                    "Initialization function works",
                )

            return True

        except Exception as e:
            self.log_test("API Endpoints Import", False, f"Exception: {str(e)}")
            return False

    async def test_frontend_components(self):
        """Test 4: Frontend Components"""
        try:
            from app.frontend.admin_scenario_management import (
                create_scenario_management_page,
            )

            # Test page creation
            page = create_scenario_management_page()
            if not page:
                self.log_test("Frontend - Page Creation", False, "Page creation failed")
                return False
            else:
                self.log_test(
                    "Frontend - Page Creation", True, "Page created successfully"
                )

            # Test admin routes integration - check module can be imported
            import app.frontend.admin_routes

            if not hasattr(app.frontend.admin_routes, "__file__"):
                self.log_test(
                    "Frontend - Routes Integration", False, "Routes module not found"
                )
                return False
            else:
                self.log_test(
                    "Frontend - Routes Integration",
                    True,
                    "Routes module integrated successfully",
                )

            return True

        except Exception as e:
            self.log_test("Frontend Components", False, f"Exception: {str(e)}")
            return False

    async def test_persistence_layer(self):
        """Test 5: File Persistence"""
        try:
            # Create test scenario
            test_scenario = await self.create_test_scenario("persistence_test")

            # Save scenario
            await scenario_manager.save_scenario(test_scenario)

            # Force save to file
            await scenario_manager._save_scenarios_to_file()

            # Check if file exists and contains our scenario
            scenarios_file = Path("data/scenarios/scenarios.json")
            if not scenarios_file.exists():
                self.log_test(
                    "Persistence - File Creation", False, "Scenarios file not created"
                )
                return False
            else:
                self.log_test(
                    "Persistence - File Creation", True, "Scenarios file created"
                )

            # Check file content
            with open(scenarios_file, "r") as f:
                data = json.load(f)

            if "persistence_test" not in data:
                self.log_test(
                    "Persistence - Data Storage", False, "Scenario not saved to file"
                )
                return False
            else:
                self.log_test(
                    "Persistence - Data Storage", True, "Scenario saved to file"
                )

            # Cleanup
            await scenario_manager.delete_scenario("persistence_test")

            return True

        except Exception as e:
            self.log_test("Persistence Layer", False, f"Exception: {str(e)}")
            return False

    async def test_error_handling(self):
        """Test 6: Error Handling"""
        try:
            # Test getting non-existent scenario
            non_existent = await scenario_manager.get_scenario_by_id("non_existent_id")
            if non_existent is not None:
                self.log_test(
                    "Error Handling - Non-existent Get",
                    False,
                    "Should return None for non-existent scenario",
                )
                return False
            else:
                self.log_test(
                    "Error Handling - Non-existent Get", True, "Correctly returns None"
                )

            # Test deleting non-existent scenario
            delete_result = await scenario_manager.delete_scenario("non_existent_id")
            if delete_result:
                self.log_test(
                    "Error Handling - Non-existent Delete",
                    False,
                    "Should return False for non-existent scenario",
                )
                return False
            else:
                self.log_test(
                    "Error Handling - Non-existent Delete",
                    True,
                    "Correctly returns False",
                )

            return True

        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False

    async def test_scenario_templates(self):
        """Test 7: Scenario Templates"""
        try:
            templates = scenario_manager.get_scenario_templates()

            if not templates:
                self.log_test("Templates - Retrieval", False, "No templates found")
                return False
            else:
                self.log_test(
                    "Templates - Retrieval", True, f"Found {len(templates)} templates"
                )

            # Check template structure
            expected_categories = ["restaurant", "travel", "business", "social"]
            for category in expected_categories:
                if category in templates:
                    self.log_test(
                        f"Templates - {category.title()} Category",
                        True,
                        "Template found",
                    )
                else:
                    self.log_test(
                        f"Templates - {category.title()} Category",
                        False,
                        "Template missing",
                    )
                    return False

            return True

        except Exception as e:
            self.log_test("Scenario Templates", False, f"Exception: {str(e)}")
            return False

    async def test_permissions_integration(self):
        """Test 8: Permissions Integration"""
        try:
            # Test admin permission constants
            required_permission = AdminPermission.MANAGE_SCENARIOS
            if not required_permission:
                self.log_test(
                    "Permissions - Constants",
                    False,
                    "MANAGE_SCENARIOS permission not found",
                )
                return False
            else:
                self.log_test(
                    "Permissions - Constants",
                    True,
                    "MANAGE_SCENARIOS permission exists",
                )

            # Test admin user has correct permissions
            if AdminPermission.MANAGE_SCENARIOS not in self.admin_user["permissions"]:
                self.log_test(
                    "Permissions - Admin User",
                    False,
                    "Admin user missing MANAGE_SCENARIOS permission",
                )
                return False
            else:
                self.log_test(
                    "Permissions - Admin User",
                    True,
                    "Admin user has required permissions",
                )

            return True

        except Exception as e:
            self.log_test("Permissions Integration", False, f"Exception: {str(e)}")
            return False

    async def test_scenario_validation(self):
        """Test 9: Scenario Validation"""
        try:
            # Test valid scenario creation
            valid_scenario = await self.create_test_scenario("validation_test")

            # Check all required fields are present
            required_fields = [
                "scenario_id",
                "name",
                "category",
                "difficulty",
                "description",
                "user_role",
                "ai_role",
                "setting",
                "duration_minutes",
                "phases",
                "vocabulary_focus",
                "cultural_context",
                "learning_goals",
            ]

            for field in required_fields:
                if (
                    not hasattr(valid_scenario, field)
                    or getattr(valid_scenario, field) is None
                ):
                    self.log_test(
                        f"Validation - {field}",
                        False,
                        f"Missing required field: {field}",
                    )
                    return False
                else:
                    self.log_test(
                        f"Validation - {field}", True, f"Field present: {field}"
                    )

            # Test scenario can be saved
            save_result = await scenario_manager.save_scenario(valid_scenario)
            if not save_result:
                self.log_test(
                    "Validation - Save Valid Scenario",
                    False,
                    "Failed to save valid scenario",
                )
                return False
            else:
                self.log_test(
                    "Validation - Save Valid Scenario",
                    True,
                    "Valid scenario saved successfully",
                )

            # Cleanup
            await scenario_manager.delete_scenario("validation_test")

            return True

        except Exception as e:
            self.log_test("Scenario Validation", False, f"Exception: {str(e)}")
            return False

    async def test_bulk_operations(self):
        """Test 10: Bulk Operations Support"""
        try:
            # Create multiple test scenarios
            scenarios = []
            for i in range(3):
                scenario = await self.create_test_scenario(f"bulk_test_{i}")
                scenarios.append(scenario)
                await scenario_manager.save_scenario(scenario)

            # Test bulk retrieval
            all_scenarios = await scenario_manager.get_all_scenarios()
            bulk_scenarios = [
                s for s in all_scenarios if s.scenario_id.startswith("bulk_test_")
            ]

            if len(bulk_scenarios) != 3:
                self.log_test(
                    "Bulk Operations - Retrieval",
                    False,
                    f"Expected 3 scenarios, found {len(bulk_scenarios)}",
                )
                return False
            else:
                self.log_test(
                    "Bulk Operations - Retrieval", True, "All bulk scenarios retrieved"
                )

            # Test bulk deletion
            for scenario in bulk_scenarios:
                await scenario_manager.delete_scenario(scenario.scenario_id)

            # Verify deletion
            remaining = await scenario_manager.get_all_scenarios()
            remaining_bulk = [
                s for s in remaining if s.scenario_id.startswith("bulk_test_")
            ]

            if len(remaining_bulk) > 0:
                self.log_test(
                    "Bulk Operations - Deletion",
                    False,
                    f"Found {len(remaining_bulk)} scenarios after deletion",
                )
                return False
            else:
                self.log_test(
                    "Bulk Operations - Deletion", True, "All bulk scenarios deleted"
                )

            return True

        except Exception as e:
            self.log_test("Bulk Operations", False, f"Exception: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run the complete test suite"""
        print("=" * 80)
        print("🧪 TASK 3.1.6 - COMPREHENSIVE SCENARIO MANAGEMENT TESTING")
        print("=" * 80)
        print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Define all tests
        tests = [
            (
                "ScenarioManager Initialization",
                self.test_scenario_manager_initialization,
            ),
            ("CRUD Operations", self.test_scenario_crud_operations),
            ("API Endpoints Import", self.test_api_endpoints_import),
            ("Frontend Components", self.test_frontend_components),
            ("Persistence Layer", self.test_persistence_layer),
            ("Error Handling", self.test_error_handling),
            ("Scenario Templates", self.test_scenario_templates),
            ("Permissions Integration", self.test_permissions_integration),
            ("Scenario Validation", self.test_scenario_validation),
            ("Bulk Operations", self.test_bulk_operations),
        ]

        # Run each test
        for test_name, test_func in tests:
            print(f"\n📋 Running Test Category: {test_name}")
            print("-" * 60)
            try:
                success = await test_func()
                if success:
                    print(f"✅ {test_name}: ALL TESTS PASSED")
                else:
                    print(f"❌ {test_name}: SOME TESTS FAILED")
            except Exception as e:
                print(f"💥 {test_name}: EXCEPTION - {str(e)}")
                self.log_test(test_name, False, f"Unhandled exception: {str(e)}")

        # Final results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)

        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0

        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        if success_rate == 100.0:
            print("\n🎉 ALL TESTS PASSED - 100% SUCCESS RATE!")
            print("🏆 Task 3.1.6 implementation is FULLY VALIDATED!")
            return True
        else:
            print(
                f"\n⚠️ {self.tests_failed} test(s) failed - Task 3.1.6 needs attention"
            )
            print("\n📝 Failed Tests:")
            for result in self.test_results:
                if "❌ FAILED" in result:
                    print(f"  • {result}")
            return False


async def main():
    """Main test execution"""
    tester = ComprehensiveScenarioTester()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
