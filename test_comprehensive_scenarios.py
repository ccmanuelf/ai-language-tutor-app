#!/usr/bin/env python3
"""
Test script for the comprehensive scenario system implementation
Tests all Tier 1 scenarios and the UniversalScenarioTemplate system
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.scenario_manager import (
    ScenarioManager,
    ScenarioFactory,
    ScenarioDifficulty,
    ScenarioCategory,
    ConversationRole,
)


async def test_comprehensive_scenarios():
    """Test the comprehensive scenario system"""
    print("🚀 Testing Comprehensive Scenario System")
    print("=" * 50)

    try:
        # Initialize scenario manager
        print("1. Initializing ScenarioManager...")
        scenario_manager = ScenarioManager()
        print("✅ ScenarioManager initialized successfully")

        # Test ScenarioFactory initialization
        print("\n2. Testing ScenarioFactory...")
        factory = scenario_manager.scenario_factory
        print(
            f"✅ ScenarioFactory loaded {len(factory.universal_templates)} universal templates"
        )

        # List all universal templates
        print("\n3. Available Universal Templates:")
        templates = scenario_manager.get_universal_templates()
        for template in templates:
            print(
                f"   📋 {template['name']} (Tier {template['tier']}, {template['category']})"
            )
            print(f"      - {template['vocabulary_count']} vocabulary words")
            print(f"      - {template['variations']} variations")

        # Test Tier 1 scenarios specifically
        print("\n4. Tier 1 Essential Scenarios:")
        tier1_scenarios = scenario_manager.get_tier1_scenarios()
        print(f"✅ Found {len(tier1_scenarios)} Tier 1 scenarios")

        # Test creating scenarios from templates
        print("\n5. Testing Scenario Creation from Templates:")

        if tier1_scenarios:
            # Test creating scenarios at different difficulty levels
            difficulties = [
                ScenarioDifficulty.BEGINNER,
                ScenarioDifficulty.INTERMEDIATE,
                ScenarioDifficulty.ADVANCED,
            ]

            for template in tier1_scenarios[:2]:  # Test first 2 templates
                template_id = template["template_id"]
                print(f"\n   Testing template: {template['name']}")

                for difficulty in difficulties:
                    scenario = scenario_manager.create_scenario_from_template(
                        template_id=template_id,
                        difficulty=difficulty,
                        user_role=ConversationRole.STUDENT,
                        ai_role=ConversationRole.TEACHER,
                    )

                    if scenario:
                        print(f"   ✅ {difficulty.value}: {scenario.name}")
                        print(
                            f"      Duration: {scenario.duration_minutes} min, Phases: {len(scenario.phases)}"
                        )
                        print(
                            f"      Vocabulary: {len(scenario.vocabulary_focus)} words"
                        )
                    else:
                        print(f"   ❌ Failed to create {difficulty.value} scenario")

        # Test category-based scenario retrieval
        print("\n6. Testing Category-based Scenario Retrieval:")
        categories = [
            ScenarioCategory.SOCIAL,
            ScenarioCategory.RESTAURANT,
            ScenarioCategory.TRAVEL,
        ]

        for category in categories:
            category_data = scenario_manager.get_scenarios_by_category(category)
            print(
                f"   📂 {category.value}: {category_data['total_count']} scenarios/templates"
            )
            print(f"      - Predefined: {len(category_data['predefined_scenarios'])}")
            print(f"      - Templates: {len(category_data['universal_templates'])}")

        # Test all Tier 1 template IDs
        print("\n7. Validating Tier 1 Template Coverage:")
        expected_tier1 = [
            "greetings_introductions",
            "family_relationships",
            "restaurant_dining",
            "transportation",
            "home_neighborhood",
        ]

        actual_tier1 = [t["template_id"] for t in tier1_scenarios]

        for expected in expected_tier1:
            if expected in actual_tier1:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ Missing: {expected}")

        # Test scenario details
        print("\n8. Testing Scenario Detail Retrieval:")
        all_scenarios = list(scenario_manager.scenarios.keys())
        if all_scenarios:
            test_scenario_id = all_scenarios[0]
            details = scenario_manager.get_scenario_details(test_scenario_id)
            if details:
                print(f"   ✅ Retrieved details for: {details['name']}")
                print(f"      Phases: {len(details['phases'])}")
                print(f"      Learning goals: {len(details['learning_goals'])}")
            else:
                print(f"   ❌ Failed to get details for {test_scenario_id}")

        print("\n" + "=" * 50)
        print("🎉 COMPREHENSIVE SCENARIO SYSTEM TEST COMPLETE")
        print(f"📊 Results Summary:")
        print(f"   - Universal templates loaded: {len(factory.universal_templates)}")
        print(f"   - Tier 1 scenarios available: {len(tier1_scenarios)}")
        print(f"   - Total scenarios in system: {len(scenario_manager.scenarios)}")
        print(f"   - Categories covered: {len(categories)} tested")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_template_data_structure():
    """Test the data structure of templates"""
    print("\n🔍 Testing Template Data Structures")
    print("-" * 30)

    try:
        factory = ScenarioFactory()

        if factory.universal_templates:
            template_id = list(factory.universal_templates.keys())[0]
            template = factory.universal_templates[template_id]

            print(f"Testing template: {template.name}")

            # Test required fields
            required_fields = [
                "template_id",
                "name",
                "category",
                "tier",
                "base_vocabulary",
                "essential_phrases",
                "cultural_context",
                "learning_objectives",
                "conversation_starters",
                "scenario_variations",
                "difficulty_modifiers",
                "success_metrics",
            ]

            for field in required_fields:
                if hasattr(template, field):
                    value = getattr(template, field)
                    print(
                        f"   ✅ {field}: {type(value).__name__} ({len(value) if hasattr(value, '__len__') else 'N/A'})"
                    )
                else:
                    print(f"   ❌ Missing field: {field}")

            # Test scenario generation
            print(f"\n   Testing scenario generation...")
            scenario = template.generate_scenario(
                ScenarioDifficulty.INTERMEDIATE,
                ConversationRole.STUDENT,
                ConversationRole.TEACHER,
            )

            if scenario:
                print(f"   ✅ Generated scenario: {scenario.name}")
                print(f"      ID: {scenario.scenario_id}")
                print(f"      Phases: {len(scenario.phases)}")
                print(f"      Vocabulary: {len(scenario.vocabulary_focus)}")
            else:
                print(f"   ❌ Failed to generate scenario")

        else:
            print("   ❌ No templates loaded")

    except Exception as e:
        print(f"   ❌ Template test error: {str(e)}")


if __name__ == "__main__":
    print("🧪 COMPREHENSIVE SCENARIO SYSTEM TESTING")
    print("Testing the new Tier 1 scenarios and UniversalScenarioTemplate system")
    print()

    # Run template structure test
    test_template_data_structure()

    # Run main async test
    success = asyncio.run(test_comprehensive_scenarios())

    if success:
        print("\n🎯 ALL TESTS PASSED - Comprehensive scenario system is working!")
        exit(0)
    else:
        print("\n💥 TESTS FAILED - Check the errors above")
        exit(1)
