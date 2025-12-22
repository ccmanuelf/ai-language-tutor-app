"""
Basic Tests for Scenario Builder
AI Language Tutor App - Session 131

Basic smoke tests to verify the scenario builder system works.
Comprehensive tests can be added later.
"""

import pytest

from app.services.scenario_templates import (
    get_all_templates,
    get_template_by_id,
    get_template_categories,
    get_templates_by_category,
)


class TestScenarioTemplates:
    """Test scenario template functions"""

    def test_get_all_templates(self):
        """Test getting all templates"""
        templates = get_all_templates()
        assert len(templates) == 10, "Should have 10 templates"

        # Verify each template has required fields
        for template in templates:
            assert "template_id" in template
            assert "title" in template
            assert "category" in template
            assert "difficulty" in template
            assert "phases" in template
            assert len(template["phases"]) >= 2, "Should have at least 2 phases"

    def test_get_template_by_id(self):
        """Test getting template by ID"""
        template = get_template_by_id("template_restaurant_basic")
        assert template is not None
        assert template["title"] == "Restaurant Dining Experience"
        assert template["category"] == "restaurant"

        # Test non-existent template
        none_template = get_template_by_id("non_existent")
        assert none_template is None

    def test_get_templates_by_category(self):
        """Test filtering templates by category"""
        restaurant_templates = get_templates_by_category("restaurant")
        assert len(restaurant_templates) == 1
        assert restaurant_templates[0]["category"] == "restaurant"

    def test_get_template_categories(self):
        """Test getting all template categories"""
        categories = get_template_categories()
        assert len(categories) == 10
        expected_categories = [
            "restaurant",
            "travel",
            "shopping",
            "business",
            "social",
            "healthcare",
            "emergency",
            "daily_life",
            "hobbies",
            "education",
        ]
        for cat in expected_categories:
            assert cat in categories

    def test_template_phases_structure(self):
        """Test that template phases have correct structure"""
        templates = get_all_templates()

        for template in templates:
            for phase in template["phases"]:
                assert "name" in phase
                assert "description" in phase
                assert "key_vocabulary" in phase
                assert "essential_phrases" in phase
                assert "learning_objectives" in phase
                assert "success_criteria" in phase

                # Verify minimum requirements
                assert len(phase["key_vocabulary"]) >= 3
                assert len(phase["essential_phrases"]) >= 3
                assert len(phase["learning_objectives"]) >= 1
                assert len(phase["success_criteria"]) >= 1


class TestScenarioValidation:
    """Test scenario validation logic"""

    def test_import_scenario_builder_service(self):
        """Test that ScenarioBuilderService can be imported"""
        from app.services.scenario_builder_service import ScenarioBuilderService

        assert ScenarioBuilderService is not None

    def test_import_scenario_models(self):
        """Test that scenario models can be imported"""
        from app.models.scenario_db_models import Scenario, ScenarioPhase

        assert Scenario is not None
        assert ScenarioPhase is not None

    def test_import_scenario_schemas(self):
        """Test that scenario schemas can be imported"""
        from app.schemas.scenario_builder_schemas import (
            CreateScenarioRequest,
            ScenarioResponse,
            UpdateScenarioRequest,
        )

        assert CreateScenarioRequest is not None
        assert UpdateScenarioRequest is not None
        assert ScenarioResponse is not None


class TestScenarioAPI:
    """Test scenario API endpoints"""

    def test_import_scenario_builder_api(self):
        """Test that API router can be imported"""
        from app.api.scenario_builder import router

        assert router is not None
        assert len(router.routes) == 10, "Should have 10 API endpoints"

    def test_api_route_paths(self):
        """Test that all expected routes are registered"""
        from app.api.scenario_builder import router

        # Get all route paths
        paths = [route.path for route in router.routes]

        # Expected endpoints
        expected_paths = [
            "/api/v1/scenario-builder/templates",
            "/api/v1/scenario-builder/scenarios",
            "/api/v1/scenario-builder/scenarios/from-template",
            "/api/v1/scenario-builder/scenarios/{scenario_id}",
            "/api/v1/scenario-builder/my-scenarios",
            "/api/v1/scenario-builder/public-scenarios",
            "/api/v1/scenario-builder/scenarios/{scenario_id}/duplicate",
            "/api/v1/scenario-builder/scenarios/{scenario_id}/visibility",
        ]

        for expected_path in expected_paths:
            assert any(expected_path in path for path in paths), (
                f"Expected path {expected_path} not found in routes"
            )


class TestDatabaseModels:
    """Test database model structure"""

    def test_scenario_model_attributes(self):
        """Test that Scenario model has all required attributes"""
        from app.models.scenario_db_models import Scenario

        # Check that class has expected attributes
        expected_attrs = [
            "scenario_id",
            "title",
            "description",
            "category",
            "difficulty",
            "estimated_duration",
            "created_by",
            "is_system_scenario",
            "is_public",
            "phases",
        ]

        for attr in expected_attrs:
            assert hasattr(Scenario, attr), f"Scenario should have attribute {attr}"

    def test_scenario_phase_model_attributes(self):
        """Test that ScenarioPhase model has all required attributes"""
        from app.models.scenario_db_models import ScenarioPhase

        expected_attrs = [
            "scenario_id",
            "phase_number",
            "phase_id",
            "name",
            "description",
            "key_vocabulary",
            "essential_phrases",
            "learning_objectives",
            "success_criteria",
        ]

        for attr in expected_attrs:
            assert hasattr(ScenarioPhase, attr), (
                f"ScenarioPhase should have attribute {attr}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
