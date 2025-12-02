"""
Comprehensive tests for app/services/scenario_templates.py

This test suite achieves TRUE 100% coverage (statement + branch) for the
ScenarioTemplates class, which provides factory methods for creating
core scenario templates (Tier 1 and Tier 2).

Module Structure:
- 7 template creator methods (5 Tier 1, 2 Tier 2)
- 2 tier getter methods
- Pure data template factory (no complex logic)

Test Strategy:
1. Test each template creator method individually
2. Test tier getter methods
3. Validate data quality and structure
4. Ensure all required fields are present and valid

Coverage Target: TRUE 100% (statement + branch)
"""

import pytest

from app.services.scenario_models import (
    ScenarioCategory,
    UniversalScenarioTemplate,
)
from app.services.scenario_templates import ScenarioTemplates


class TestScenarioTemplatesGetters:
    """Test suite for tier getter methods"""

    def test_get_tier1_templates_returns_list(self):
        """Test that get_tier1_templates returns a list"""
        templates = ScenarioTemplates.get_tier1_templates()
        assert isinstance(templates, list)
        assert len(templates) == 5

    def test_get_tier1_templates_all_tier1(self):
        """Test that all returned templates are tier 1"""
        templates = ScenarioTemplates.get_tier1_templates()
        for template in templates:
            assert isinstance(template, UniversalScenarioTemplate)
            assert template.tier == 1

    def test_get_tier2_templates_returns_list(self):
        """Test that get_tier2_templates returns a list"""
        templates = ScenarioTemplates.get_tier2_templates()
        assert isinstance(templates, list)
        assert len(templates) == 2

    def test_get_tier2_templates_all_tier2(self):
        """Test that all returned templates are tier 2"""
        templates = ScenarioTemplates.get_tier2_templates()
        for template in templates:
            assert isinstance(template, UniversalScenarioTemplate)
            assert template.tier == 2


class TestGreetingsTemplate:
    """Test suite for create_greetings_template"""

    def test_greetings_template_basic_structure(self):
        """Test greetings template basic structure"""
        template = ScenarioTemplates.create_greetings_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "greetings_introductions"
        assert template.name == "Greetings and Introductions"
        assert template.category == ScenarioCategory.SOCIAL
        assert template.tier == 1

    def test_greetings_template_has_vocabulary(self):
        """Test greetings template has base vocabulary"""
        template = ScenarioTemplates.create_greetings_template()
        assert len(template.base_vocabulary) > 0
        assert "hello" in template.base_vocabulary
        assert "goodbye" in template.base_vocabulary

    def test_greetings_template_has_essential_phrases(self):
        """Test greetings template has essential phrases for all levels"""
        template = ScenarioTemplates.create_greetings_template()
        assert "beginner" in template.essential_phrases
        assert "intermediate" in template.essential_phrases
        assert "advanced" in template.essential_phrases
        assert len(template.essential_phrases["beginner"]) > 0

    def test_greetings_template_has_cultural_context(self):
        """Test greetings template has cultural context"""
        template = ScenarioTemplates.create_greetings_template()
        assert "notes" in template.cultural_context
        assert len(template.cultural_context["notes"]) > 0

    def test_greetings_template_has_learning_objectives(self):
        """Test greetings template has learning objectives"""
        template = ScenarioTemplates.create_greetings_template()
        assert len(template.learning_objectives) > 0

    def test_greetings_template_has_conversation_starters(self):
        """Test greetings template has conversation starters"""
        template = ScenarioTemplates.create_greetings_template()
        assert len(template.conversation_starters) > 0

    def test_greetings_template_has_scenario_variations(self):
        """Test greetings template has scenario variations"""
        template = ScenarioTemplates.create_greetings_template()
        assert len(template.scenario_variations) > 0
        assert all("id" in v for v in template.scenario_variations)

    def test_greetings_template_has_difficulty_modifiers(self):
        """Test greetings template has difficulty modifiers"""
        template = ScenarioTemplates.create_greetings_template()
        assert "beginner" in template.difficulty_modifiers
        assert "intermediate" in template.difficulty_modifiers
        assert "advanced" in template.difficulty_modifiers

    def test_greetings_template_has_success_metrics(self):
        """Test greetings template has success metrics"""
        template = ScenarioTemplates.create_greetings_template()
        assert len(template.success_metrics) > 0


class TestDailyRoutineTemplate:
    """Test suite for create_daily_routine_template"""

    def test_daily_routine_template_basic_structure(self):
        """Test daily routine template basic structure"""
        template = ScenarioTemplates.create_daily_routine_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "daily_routine"
        assert template.name == "Daily Routine"
        assert template.category == ScenarioCategory.DAILY_LIFE
        assert template.tier == 2

    def test_daily_routine_template_has_required_fields(self):
        """Test daily routine template has all required fields"""
        template = ScenarioTemplates.create_daily_routine_template()
        assert len(template.base_vocabulary) > 0
        assert "beginner" in template.essential_phrases
        assert "notes" in template.cultural_context
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert "beginner" in template.difficulty_modifiers
        assert len(template.success_metrics) > 0


class TestBasicConversationsTemplate:
    """Test suite for create_basic_conversations_template"""

    def test_basic_conversations_template_basic_structure(self):
        """Test basic conversations template basic structure"""
        template = ScenarioTemplates.create_basic_conversations_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "basic_conversations"
        assert template.name == "Basic Conversations"
        assert template.category == ScenarioCategory.SOCIAL
        assert template.tier == 2

    def test_basic_conversations_template_has_required_fields(self):
        """Test basic conversations template has all required fields"""
        template = ScenarioTemplates.create_basic_conversations_template()
        assert len(template.base_vocabulary) > 0
        assert "beginner" in template.essential_phrases
        assert "notes" in template.cultural_context
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert "beginner" in template.difficulty_modifiers
        assert len(template.success_metrics) > 0


class TestFamilyTemplate:
    """Test suite for create_family_template"""

    def test_family_template_basic_structure(self):
        """Test family template basic structure"""
        template = ScenarioTemplates.create_family_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "family_relationships"
        assert template.name == "Family and Relationships"
        assert template.category == ScenarioCategory.SOCIAL
        assert template.tier == 1

    def test_family_template_has_required_fields(self):
        """Test family template has all required fields"""
        template = ScenarioTemplates.create_family_template()
        assert len(template.base_vocabulary) > 0
        assert "family" in template.base_vocabulary
        assert "beginner" in template.essential_phrases
        assert "notes" in template.cultural_context
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert "beginner" in template.difficulty_modifiers
        assert len(template.success_metrics) > 0


class TestRestaurantTemplate:
    """Test suite for create_restaurant_template"""

    def test_restaurant_template_basic_structure(self):
        """Test restaurant template basic structure"""
        template = ScenarioTemplates.create_restaurant_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "restaurant_dining"
        assert template.name == "Restaurant and Dining"
        assert template.category == ScenarioCategory.RESTAURANT
        assert template.tier == 1

    def test_restaurant_template_has_required_fields(self):
        """Test restaurant template has all required fields"""
        template = ScenarioTemplates.create_restaurant_template()
        assert len(template.base_vocabulary) > 0
        assert "restaurant" in template.base_vocabulary
        assert "beginner" in template.essential_phrases
        assert "notes" in template.cultural_context
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert "beginner" in template.difficulty_modifiers
        assert len(template.success_metrics) > 0


class TestTransportationTemplate:
    """Test suite for create_transportation_template"""

    def test_transportation_template_basic_structure(self):
        """Test transportation template basic structure"""
        template = ScenarioTemplates.create_transportation_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "transportation"
        assert template.name == "Transportation"
        assert template.category == ScenarioCategory.TRAVEL
        assert template.tier == 1

    def test_transportation_template_has_required_fields(self):
        """Test transportation template has all required fields"""
        template = ScenarioTemplates.create_transportation_template()
        assert len(template.base_vocabulary) > 0
        assert "bus" in template.base_vocabulary
        assert "beginner" in template.essential_phrases
        assert "notes" in template.cultural_context
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert "beginner" in template.difficulty_modifiers
        assert len(template.success_metrics) > 0


class TestHomeNeighborhoodTemplate:
    """Test suite for create_home_neighborhood_template"""

    def test_home_neighborhood_template_basic_structure(self):
        """Test home neighborhood template basic structure"""
        template = ScenarioTemplates.create_home_neighborhood_template()
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == "home_neighborhood"
        assert template.name == "Home and Neighborhood"
        assert template.category == ScenarioCategory.DAILY_LIFE
        assert template.tier == 1

    def test_home_neighborhood_template_has_required_fields(self):
        """Test home neighborhood template has all required fields"""
        template = ScenarioTemplates.create_home_neighborhood_template()
        assert len(template.base_vocabulary) > 0
        assert "home" in template.base_vocabulary
        assert "beginner" in template.essential_phrases
        assert "notes" in template.cultural_context
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert "beginner" in template.difficulty_modifiers
        assert len(template.success_metrics) > 0


class TestDataQuality:
    """Test suite for data quality validation across all templates"""

    def test_all_templates_have_unique_ids(self):
        """Test that all templates have unique IDs"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        ids = [t.template_id for t in all_templates]
        assert len(ids) == len(set(ids)), "Duplicate template IDs found"

    def test_all_templates_have_valid_categories(self):
        """Test that all templates have valid ScenarioCategory values"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert isinstance(template.category, ScenarioCategory)

    def test_all_templates_have_three_difficulty_levels(self):
        """Test that all templates have beginner, intermediate, and advanced levels"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert "beginner" in template.essential_phrases
            assert "intermediate" in template.essential_phrases
            assert "advanced" in template.essential_phrases
            assert "beginner" in template.difficulty_modifiers
            assert "intermediate" in template.difficulty_modifiers
            assert "advanced" in template.difficulty_modifiers

    def test_all_templates_have_non_empty_vocabulary(self):
        """Test that all templates have non-empty base vocabulary"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert len(template.base_vocabulary) > 0, (
                f"Empty vocabulary in {template.template_id}"
            )

    def test_all_templates_have_learning_objectives(self):
        """Test that all templates have learning objectives"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert len(template.learning_objectives) > 0, (
                f"No learning objectives in {template.template_id}"
            )

    def test_all_templates_have_conversation_starters(self):
        """Test that all templates have conversation starters"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert len(template.conversation_starters) > 0, (
                f"No conversation starters in {template.template_id}"
            )

    def test_all_templates_have_scenario_variations(self):
        """Test that all templates have scenario variations"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert len(template.scenario_variations) > 0, (
                f"No scenario variations in {template.template_id}"
            )

    def test_all_templates_have_success_metrics(self):
        """Test that all templates have success metrics"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert len(template.success_metrics) > 0, (
                f"No success metrics in {template.template_id}"
            )

    def test_all_templates_have_cultural_context(self):
        """Test that all templates have cultural context with notes"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            assert "notes" in template.cultural_context, (
                f"No cultural notes in {template.template_id}"
            )
            assert len(template.cultural_context["notes"]) > 0, (
                f"Empty cultural notes in {template.template_id}"
            )

    def test_scenario_variations_have_required_fields(self):
        """Test that all scenario variations have required fields"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            for variation in template.scenario_variations:
                assert "id" in variation, (
                    f"Missing 'id' in variation for {template.template_id}"
                )
                assert "description" in variation, (
                    f"Missing 'description' in variation for {template.template_id}"
                )
                assert "phases" in variation, (
                    f"Missing 'phases' in variation for {template.template_id}"
                )

    def test_difficulty_modifiers_have_duration(self):
        """Test that all difficulty modifiers have duration field"""
        t1 = ScenarioTemplates.get_tier1_templates()
        t2 = ScenarioTemplates.get_tier2_templates()
        all_templates = t1 + t2

        for template in all_templates:
            for level in ["beginner", "intermediate", "advanced"]:
                assert "duration" in template.difficulty_modifiers[level], (
                    f"Missing duration in {level} difficulty for {template.template_id}"
                )
