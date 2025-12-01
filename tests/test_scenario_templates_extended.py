"""
Comprehensive tests for scenario_templates_extended.py

This test module achieves TRUE 100% coverage for the ExtendedScenarioTemplates class,
validating all 27 scenario template creator methods across Tiers 2-4.

Test Strategy:
- Test each tier's getter method (get_tier2, get_tier3, get_tier4)
- Test the aggregate getter (get_all_extended_templates)
- Test each individual template creator method (27 total)
- Validate all template properties and data structures
- Ensure no regressions in template data quality
"""

from typing import List

import pytest

from app.services.scenario_models import (
    ScenarioCategory,
    UniversalScenarioTemplate,
)
from app.services.scenario_templates_extended import ExtendedScenarioTemplates


class TestTierGetters:
    """Test the tier getter methods"""

    def test_get_tier2_templates(self):
        """Test get_tier2_templates returns 10 templates"""
        templates = ExtendedScenarioTemplates.get_tier2_templates()

        assert isinstance(templates, list)
        assert len(templates) == 10

        # All should be tier 2
        for template in templates:
            assert isinstance(template, UniversalScenarioTemplate)
            assert template.tier == 2

        # Verify expected template IDs
        template_ids = {t.template_id for t in templates}
        expected_ids = {
            "daily_routine",
            "basic_conversations",
            "job_work",
            "weather_climate",
            "clothing",
            "general_shopping",
            "making_plans",
            "common_topics",
            "numbers",
            "celebrations",
        }
        assert template_ids == expected_ids

    def test_get_tier3_templates(self):
        """Test get_tier3_templates returns 10 templates"""
        templates = ExtendedScenarioTemplates.get_tier3_templates()

        assert isinstance(templates, list)
        assert len(templates) == 10

        # All should be tier 3
        for template in templates:
            assert isinstance(template, UniversalScenarioTemplate)
            assert template.tier == 3

        # Verify expected template IDs
        template_ids = {t.template_id for t in templates}
        expected_ids = {
            "sports_activities",
            "grocery_shopping",
            "education",
            "office_work_life",
            "permissions_etiquette",
            "physical_health",
            "trip_places",
            "public_places",
            "describing_someone",
            "feelings_emotions",
        }
        assert template_ids == expected_ids

    def test_get_tier4_templates(self):
        """Test get_tier4_templates returns 7 templates"""
        templates = ExtendedScenarioTemplates.get_tier4_templates()

        assert isinstance(templates, list)
        assert len(templates) == 7

        # All should be tier 4
        for template in templates:
            assert isinstance(template, UniversalScenarioTemplate)
            assert template.tier == 4

        # Verify expected template IDs
        template_ids = {t.template_id for t in templates}
        expected_ids = {
            "difficulties_solutions",
            "health_wellbeing",
            "advanced_making_plans",
            "getting_house",
            "music_performing_arts",
            "past_activities",
            "money_finances",
        }
        assert template_ids == expected_ids

    def test_get_all_extended_templates(self):
        """Test get_all_extended_templates returns all 27 templates"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        assert isinstance(all_templates, list)
        assert len(all_templates) == 27  # 10 + 10 + 7

        # Verify tier distribution
        tier2_count = sum(1 for t in all_templates if t.tier == 2)
        tier3_count = sum(1 for t in all_templates if t.tier == 3)
        tier4_count = sum(1 for t in all_templates if t.tier == 4)

        assert tier2_count == 10
        assert tier3_count == 10
        assert tier4_count == 7

        # Verify all are UniversalScenarioTemplate instances
        for template in all_templates:
            assert isinstance(template, UniversalScenarioTemplate)

    def test_all_templates_aggregate_consistency(self):
        """Test that get_all_extended_templates matches sum of individual tiers"""
        tier2 = ExtendedScenarioTemplates.get_tier2_templates()
        tier3 = ExtendedScenarioTemplates.get_tier3_templates()
        tier4 = ExtendedScenarioTemplates.get_tier4_templates()
        all_extended = ExtendedScenarioTemplates.get_all_extended_templates()

        # Should match individual tier counts
        expected_total = len(tier2) + len(tier3) + len(tier4)
        assert len(all_extended) == expected_total

        # Should contain same template IDs
        individual_ids = (
            {t.template_id for t in tier2}
            | {t.template_id for t in tier3}
            | {t.template_id for t in tier4}
        )
        all_ids = {t.template_id for t in all_extended}
        assert individual_ids == all_ids


class TestTier2Templates:
    """Test all Tier 2 template creator methods"""

    def test_create_daily_routine_template(self):
        """Test _create_daily_routine_template"""
        template = ExtendedScenarioTemplates._create_daily_routine_template()

        assert template.template_id == "daily_routine"
        assert template.name == "Daily Routine"
        assert template.category == ScenarioCategory.DAILY_LIFE
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert "morning" in template.base_vocabulary
        assert len(template.essential_phrases) > 0
        assert len(template.learning_objectives) > 0
        assert len(template.conversation_starters) > 0
        assert len(template.scenario_variations) > 0
        assert len(template.success_metrics) > 0

    def test_create_basic_conversations_template(self):
        """Test _create_basic_conversations_template"""
        template = ExtendedScenarioTemplates._create_basic_conversations_template()

        assert template.template_id == "basic_conversations"
        assert template.name == "Basic Conversations"
        assert template.category == ScenarioCategory.SOCIAL
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert "yes" in template.base_vocabulary or "no" in template.base_vocabulary

    def test_create_job_work_template(self):
        """Test _create_job_work_template"""
        template = ExtendedScenarioTemplates._create_job_work_template()

        assert template.template_id == "job_work"
        assert template.name == "Job and Work"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_weather_climate_template(self):
        """Test _create_weather_climate_template"""
        template = ExtendedScenarioTemplates._create_weather_climate_template()

        assert template.template_id == "weather_climate"
        assert template.name == "Weather and Climate"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_clothing_template(self):
        """Test _create_clothing_template"""
        template = ExtendedScenarioTemplates._create_clothing_template()

        assert template.template_id == "clothing"
        assert template.name == "Clothing"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_shopping_template(self):
        """Test _create_shopping_template"""
        template = ExtendedScenarioTemplates._create_shopping_template()

        assert template.template_id == "general_shopping"
        assert template.name == "General Shopping"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_plans_template(self):
        """Test _create_plans_template"""
        template = ExtendedScenarioTemplates._create_plans_template()

        assert template.template_id == "making_plans"
        assert template.name == "Making Plans"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_common_topics_template(self):
        """Test _create_common_topics_template"""
        template = ExtendedScenarioTemplates._create_common_topics_template()

        assert template.template_id == "common_topics"
        assert template.name == "Common Topics"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_numbers_template(self):
        """Test _create_numbers_template"""
        template = ExtendedScenarioTemplates._create_numbers_template()

        assert template.template_id == "numbers"
        assert template.name == "Numbers"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_celebrations_template(self):
        """Test _create_celebrations_template"""
        template = ExtendedScenarioTemplates._create_celebrations_template()

        assert template.template_id == "celebrations"
        assert template.name == "Celebrations"
        assert template.tier == 2
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0


class TestTier3Templates:
    """Test all Tier 3 template creator methods"""

    def test_create_sports_activities_template(self):
        """Test _create_sports_activities_template"""
        template = ExtendedScenarioTemplates._create_sports_activities_template()

        assert template.template_id == "sports_activities"
        assert template.name == "Sports and Physical Activities"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_grocery_shopping_template(self):
        """Test _create_grocery_shopping_template"""
        template = ExtendedScenarioTemplates._create_grocery_shopping_template()

        assert template.template_id == "grocery_shopping"
        assert template.name == "Grocery Shopping"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_education_template(self):
        """Test _create_education_template"""
        template = ExtendedScenarioTemplates._create_education_template()

        assert template.template_id == "education"
        assert template.name == "Education"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_office_work_life_template(self):
        """Test _create_office_work_life_template"""
        template = ExtendedScenarioTemplates._create_office_work_life_template()

        assert template.template_id == "office_work_life"
        assert template.name == "Office and Work Life"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_permissions_etiquette_template(self):
        """Test _create_permissions_etiquette_template"""
        template = ExtendedScenarioTemplates._create_permissions_etiquette_template()

        assert template.template_id == "permissions_etiquette"
        assert template.name == "Permissions and Etiquette"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_physical_health_template(self):
        """Test _create_physical_health_template"""
        template = ExtendedScenarioTemplates._create_physical_health_template()

        assert template.template_id == "physical_health"
        assert template.name == "Physical Health"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_trip_places_template(self):
        """Test _create_trip_places_template"""
        template = ExtendedScenarioTemplates._create_trip_places_template()

        assert template.template_id == "trip_places"
        assert template.name == "Trip to Places"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_public_places_template(self):
        """Test _create_public_places_template"""
        template = ExtendedScenarioTemplates._create_public_places_template()

        assert template.template_id == "public_places"
        assert template.name == "Public Places"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_describing_someone_template(self):
        """Test _create_describing_someone_template"""
        template = ExtendedScenarioTemplates._create_describing_someone_template()

        assert template.template_id == "describing_someone"
        assert template.name == "Describing Someone"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_feelings_emotions_template(self):
        """Test _create_feelings_emotions_template"""
        template = ExtendedScenarioTemplates._create_feelings_emotions_template()

        assert template.template_id == "feelings_emotions"
        assert template.name == "Feelings and Emotions"
        assert template.tier == 3
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0


class TestTier4Templates:
    """Test all Tier 4 template creator methods"""

    def test_create_difficulties_solutions_template(self):
        """Test _create_difficulties_solutions_template"""
        template = ExtendedScenarioTemplates._create_difficulties_solutions_template()

        assert template.template_id == "difficulties_solutions"
        assert template.name == "Difficulties and Solutions"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_health_wellbeing_template(self):
        """Test _create_health_wellbeing_template"""
        template = ExtendedScenarioTemplates._create_health_wellbeing_template()

        assert template.template_id == "health_wellbeing"
        assert template.name == "Health and Well-being"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_making_plans_template(self):
        """Test _create_making_plans_template"""
        template = ExtendedScenarioTemplates._create_making_plans_template()

        assert template.template_id == "advanced_making_plans"
        assert template.name == "Advanced Making Plans"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_getting_house_template(self):
        """Test _create_getting_house_template"""
        template = ExtendedScenarioTemplates._create_getting_house_template()

        assert template.template_id == "getting_house"
        assert template.name == "Getting a House"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_music_performing_arts_template(self):
        """Test _create_music_performing_arts_template"""
        template = ExtendedScenarioTemplates._create_music_performing_arts_template()

        assert template.template_id == "music_performing_arts"
        assert template.name == "Music and Performing Arts"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_past_activities_template(self):
        """Test _create_past_activities_template"""
        template = ExtendedScenarioTemplates._create_past_activities_template()

        assert template.template_id == "past_activities"
        assert template.name == "Past Activities"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0

    def test_create_money_finances_template(self):
        """Test _create_money_finances_template"""
        template = ExtendedScenarioTemplates._create_money_finances_template()

        assert template.template_id == "money_finances"
        assert template.name == "Money and Finances"
        assert template.tier == 4
        assert len(template.base_vocabulary) > 0
        assert len(template.essential_phrases) > 0


class TestTemplateDataQuality:
    """Test data quality across all templates"""

    def test_all_templates_have_required_fields(self):
        """Test that all 27 templates have all required fields populated"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            # Required string fields
            assert template.template_id
            assert template.name
            assert isinstance(template.template_id, str)
            assert isinstance(template.name, str)

            # Required enum/int fields
            assert isinstance(template.category, ScenarioCategory)
            assert isinstance(template.tier, int)
            assert template.tier in [2, 3, 4]

            # Required list fields (must not be empty)
            assert isinstance(template.base_vocabulary, list)
            assert len(template.base_vocabulary) > 0

            assert isinstance(template.learning_objectives, list)
            assert len(template.learning_objectives) > 0

            assert isinstance(template.conversation_starters, list)
            assert len(template.conversation_starters) > 0

            assert isinstance(template.scenario_variations, list)
            assert len(template.scenario_variations) > 0

            assert isinstance(template.success_metrics, list)
            assert len(template.success_metrics) > 0

            # Required dict fields
            assert isinstance(template.essential_phrases, dict)
            assert len(template.essential_phrases) > 0

            assert isinstance(template.cultural_context, dict)
            assert len(template.cultural_context) > 0

            assert isinstance(template.difficulty_modifiers, dict)
            assert len(template.difficulty_modifiers) > 0

    def test_all_template_ids_unique(self):
        """Test that all template IDs are unique"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()
        template_ids = [t.template_id for t in all_templates]

        assert len(template_ids) == len(set(template_ids)), (
            "Duplicate template IDs found"
        )

    def test_all_template_names_unique(self):
        """Test that all template names are unique"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()
        template_names = [t.name for t in all_templates]

        assert len(template_names) == len(set(template_names)), (
            "Duplicate template names found"
        )

    def test_essential_phrases_structure(self):
        """Test that essential_phrases dict has expected structure"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            phrases = template.essential_phrases

            # Should have at least beginner level
            assert (
                "beginner" in phrases
                or "intermediate" in phrases
                or "advanced" in phrases
            )

            # All values should be lists
            for level, phrase_list in phrases.items():
                assert isinstance(phrase_list, list)
                assert len(phrase_list) > 0
                assert all(isinstance(p, str) for p in phrase_list)

    def test_scenario_variations_structure(self):
        """Test that scenario_variations list has expected structure"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            variations = template.scenario_variations
            assert len(variations) > 0

            for variation in variations:
                assert isinstance(variation, dict)
                assert "id" in variation
                assert "description" in variation
                # phases is optional but if present should be a list
                if "phases" in variation:
                    assert isinstance(variation["phases"], list)

    def test_difficulty_modifiers_structure(self):
        """Test that difficulty_modifiers dict has expected structure"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            modifiers = template.difficulty_modifiers

            # Should have at least one difficulty level
            assert len(modifiers) > 0

            # All values should be dicts
            for level, config in modifiers.items():
                assert isinstance(config, dict)
                # Common keys: duration, vocabulary_limit, etc.
                assert len(config) > 0

    def test_categories_distribution(self):
        """Test that templates cover multiple categories"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()
        categories = {t.category for t in all_templates}

        # Should have multiple categories represented
        assert len(categories) >= 3, (
            "Templates should cover at least 3 different categories"
        )

    def test_vocabulary_lists_not_empty(self):
        """Test that all base_vocabulary lists contain actual words"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            vocab = template.base_vocabulary
            assert len(vocab) >= 5, (
                f"{template.template_id} should have at least 5 vocabulary words"
            )

            # All should be non-empty strings
            for word in vocab:
                assert isinstance(word, str)
                assert len(word.strip()) > 0

    def test_learning_objectives_not_empty(self):
        """Test that all learning_objectives are non-empty strings"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            objectives = template.learning_objectives
            assert len(objectives) >= 1

            for objective in objectives:
                assert isinstance(objective, str)
                assert len(objective.strip()) > 0

    def test_conversation_starters_not_empty(self):
        """Test that all conversation_starters are non-empty strings"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            starters = template.conversation_starters
            assert len(starters) >= 1

            for starter in starters:
                assert isinstance(starter, str)
                assert len(starter.strip()) > 0

    def test_success_metrics_not_empty(self):
        """Test that all success_metrics are non-empty strings"""
        all_templates = ExtendedScenarioTemplates.get_all_extended_templates()

        for template in all_templates:
            metrics = template.success_metrics
            assert len(metrics) >= 1

            for metric in metrics:
                assert isinstance(metric, str)
                assert len(metric.strip()) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_tier_results_in_empty_list(self):
        """Test that calling individual methods always returns non-empty lists"""
        # This is more of a sanity check - the methods should never return empty
        tier2 = ExtendedScenarioTemplates.get_tier2_templates()
        tier3 = ExtendedScenarioTemplates.get_tier3_templates()
        tier4 = ExtendedScenarioTemplates.get_tier4_templates()

        assert len(tier2) > 0
        assert len(tier3) > 0
        assert len(tier4) > 0

    def test_template_immutability(self):
        """Test that getting templates multiple times returns consistent data"""
        first_call = ExtendedScenarioTemplates.get_all_extended_templates()
        second_call = ExtendedScenarioTemplates.get_all_extended_templates()

        # Should return same number of templates
        assert len(first_call) == len(second_call)

        # Should have same template IDs
        first_ids = {t.template_id for t in first_call}
        second_ids = {t.template_id for t in second_call}
        assert first_ids == second_ids

    def test_no_tier_overlap(self):
        """Test that each template appears in only one tier"""
        tier2 = ExtendedScenarioTemplates.get_tier2_templates()
        tier3 = ExtendedScenarioTemplates.get_tier3_templates()
        tier4 = ExtendedScenarioTemplates.get_tier4_templates()

        tier2_ids = {t.template_id for t in tier2}
        tier3_ids = {t.template_id for t in tier3}
        tier4_ids = {t.template_id for t in tier4}

        # No overlap between tiers
        assert tier2_ids.isdisjoint(tier3_ids)
        assert tier2_ids.isdisjoint(tier4_ids)
        assert tier3_ids.isdisjoint(tier4_ids)

    def test_all_extended_contains_all_tiers(self):
        """Test that get_all_extended_templates contains templates from all tiers"""
        tier2 = ExtendedScenarioTemplates.get_tier2_templates()
        tier3 = ExtendedScenarioTemplates.get_tier3_templates()
        tier4 = ExtendedScenarioTemplates.get_tier4_templates()
        all_extended = ExtendedScenarioTemplates.get_all_extended_templates()

        tier2_ids = {t.template_id for t in tier2}
        tier3_ids = {t.template_id for t in tier3}
        tier4_ids = {t.template_id for t in tier4}
        all_ids = {t.template_id for t in all_extended}

        # All tier templates should be in all_extended
        assert tier2_ids.issubset(all_ids)
        assert tier3_ids.issubset(all_ids)
        assert tier4_ids.issubset(all_ids)

        # all_extended should not have extras
        assert all_ids == tier2_ids | tier3_ids | tier4_ids
