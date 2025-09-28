#!/usr/bin/env python3
"""
Simple validation script for Task 3.1.6 - Scenario & Content Management Tools
Tests core functionality without complex test framework
"""

import asyncio
import sys
from pathlib import Path

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


async def test_scenario_manager_basic():
    """Test basic scenario manager functionality"""
    print("🧪 Testing ScenarioManager basic functionality...")

    # Initialize scenario manager
    await scenario_manager.initialize()
    print("✅ ScenarioManager initialized successfully")

    # Test getting scenarios
    scenarios = await scenario_manager.get_all_scenarios()
    print(f"✅ Retrieved {len(scenarios)} scenarios")

    # Test creating a simple scenario
    test_scenario = ConversationScenario(
        scenario_id="validation_test_001",
        name="Validation Test Scenario",
        category=ScenarioCategory.RESTAURANT,
        difficulty=ScenarioDifficulty.BEGINNER,
        description="Simple test scenario for validation",
        user_role=ConversationRole.CUSTOMER,
        ai_role=ConversationRole.SERVICE_PROVIDER,
        setting="Restaurant",
        duration_minutes=15,
        phases=[
            ScenarioPhase(
                phase_id="greeting",
                name="Greeting",
                description="Initial greeting phase",
                expected_duration_minutes=5,
                key_vocabulary=["hello", "table", "reservation"],
                essential_phrases=["Hello, I have a reservation"],
                learning_objectives=["Greet staff politely"],
            )
        ],
        vocabulary_focus=["restaurant", "reservation", "menu"],
        cultural_context={"dining_etiquette": "polite service interaction"},
        learning_goals=["order food politely", "interact with restaurant staff"],
    )

    # Test saving scenario
    success = await scenario_manager.save_scenario(test_scenario)
    if success:
        print("✅ Scenario saved successfully")
    else:
        print("❌ Failed to save scenario")
        return False

    # Test retrieving the saved scenario
    retrieved = await scenario_manager.get_scenario_by_id("validation_test_001")
    if retrieved and retrieved.name == "Validation Test Scenario":
        print("✅ Scenario retrieved successfully")
    else:
        print("❌ Failed to retrieve scenario")
        return False

    # Test updating scenario
    retrieved.description = "Updated test scenario description"
    update_success = await scenario_manager.update_scenario(
        "validation_test_001", retrieved
    )
    if update_success:
        print("✅ Scenario updated successfully")
    else:
        print("❌ Failed to update scenario")
        return False

    # Test deleting scenario
    delete_success = await scenario_manager.delete_scenario("validation_test_001")
    if delete_success:
        print("✅ Scenario deleted successfully")
    else:
        print("❌ Failed to delete scenario")
        return False

    return True


async def test_api_endpoints():
    """Test that API endpoints are properly defined"""
    print("\n🧪 Testing API endpoint definitions...")

    try:
        from app.api.scenario_management import (
            router,
            ensure_scenario_manager_initialized,
        )

        print("✅ API router imported successfully")

        # Test initialization function
        sm = await ensure_scenario_manager_initialized()
        if sm:
            print("✅ Scenario manager initialization function works")
        else:
            print("❌ Scenario manager initialization failed")
            return False

        return True
    except Exception as e:
        print(f"❌ API import failed: {str(e)}")
        return False


async def test_frontend_components():
    """Test that frontend components are properly defined"""
    print("\n🧪 Testing frontend component definitions...")

    try:
        from app.frontend.admin_scenario_management import (
            create_scenario_management_page,
        )

        print("✅ Frontend components imported successfully")

        # Test page creation
        page = create_scenario_management_page()
        if page:
            print("✅ Scenario management page created successfully")
        else:
            print("❌ Failed to create scenario management page")
            return False

        return True
    except Exception as e:
        print(f"❌ Frontend import failed: {str(e)}")
        return False


async def main():
    """Run all validation tests"""
    print("=" * 80)
    print("🎯 TASK 3.1.6 - SCENARIO & CONTENT MANAGEMENT TOOLS - VALIDATION")
    print("=" * 80)

    tests = [
        ("ScenarioManager Basic Functionality", test_scenario_manager_basic),
        ("API Endpoints", test_api_endpoints),
        ("Frontend Components", test_frontend_components),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")

    print("\n" + "=" * 80)
    print(f"📊 VALIDATION RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Task 3.1.6 implementation is VALIDATED!")
        return True
    else:
        print("⚠️  Some tests failed - Task 3.1.6 needs attention")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
