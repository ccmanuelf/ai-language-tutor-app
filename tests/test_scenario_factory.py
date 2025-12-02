"""
Comprehensive tests for ScenarioFactory module

Tests cover all functionality including:
- Factory initialization
- Template loading from JSON files
- Default template creation
- Template retrieval methods
- Error handling and edge cases

Target: TRUE 100% coverage (61/61 statements, 14/14 branches)
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from app.services.scenario_factory import ScenarioFactory
from app.services.scenario_models import (
    ScenarioCategory,
    UniversalScenarioTemplate,
)

# ============================================================================
# Test Class 1: Initialization
# ============================================================================


class TestScenarioFactoryInitialization:
    """Test factory initialization and setup"""

    def test_init_with_default_path(self):
        """Test initialization with default template directory"""
        with patch.object(ScenarioFactory, "_load_universal_templates"):
            factory = ScenarioFactory()
            assert factory.template_directory == Path("scenario_templates")
            assert factory.universal_templates == {}
            assert factory.content_cache == {}

    def test_init_with_custom_path(self):
        """Test initialization with custom template directory"""
        with patch.object(ScenarioFactory, "_load_universal_templates"):
            factory = ScenarioFactory(template_directory="custom_templates")
            assert factory.template_directory == Path("custom_templates")

    def test_init_calls_load_templates(self):
        """Test that initialization calls _load_universal_templates"""
        with patch.object(ScenarioFactory, "_load_universal_templates") as mock_load:
            factory = ScenarioFactory()
            mock_load.assert_called_once()

    def test_init_loads_default_templates(self):
        """Test that initialization actually loads default templates"""
        factory = ScenarioFactory()
        # Should have default templates loaded
        assert len(factory.universal_templates) > 0
        # Should have 32 unique templates (5 tier1 + 2 tier2 + 27 extended, with 2 duplicates)
        assert len(factory.universal_templates) == 32

    def test_init_caches_initialized(self):
        """Test that caches are properly initialized"""
        factory = ScenarioFactory()
        assert isinstance(factory.universal_templates, dict)
        assert isinstance(factory.content_cache, dict)


# ============================================================================
# Test Class 2: Load Templates - Path Not Exists
# ============================================================================


class TestLoadUniversalTemplatesPathNotExists:
    """Test template loading when scenarios directory doesn't exist"""

    def test_missing_directory_triggers_warning(self, caplog, tmp_path):
        """Test warning logged when scenarios directory not found"""
        # Create a fake __file__ location that doesn't have scenarios dir
        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            with caplog.at_level(
                logging.WARNING, logger="app.services.scenario_factory"
            ):
                factory = ScenarioFactory()
                assert any(
                    "Scenario templates directory not found" in record.message
                    for record in caplog.records
                )

    def test_missing_directory_creates_defaults(self, tmp_path):
        """Test that missing directory triggers default template creation"""
        # Create a fake __file__ location that doesn't have scenarios dir
        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            factory = ScenarioFactory()
            # Should have default templates (32 unique after deduplication)
            assert len(factory.universal_templates) == 32

    def test_missing_directory_calls_create_default(self, tmp_path):
        """Test that _create_default_templates is called when path missing"""
        # Create a fake __file__ location that doesn't have scenarios dir
        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            with patch.object(
                ScenarioFactory, "_create_default_templates"
            ) as mock_create:
                factory = ScenarioFactory.__new__(ScenarioFactory)
                factory.template_directory = Path("scenario_templates")
                factory.universal_templates = {}
                factory.content_cache = {}
                factory._load_universal_templates()
                mock_create.assert_called_once()


# ============================================================================
# Test Class 3: Load Templates - No JSON Files
# ============================================================================


class TestLoadUniversalTemplatesNoJSONFiles:
    """Test template loading when scenarios directory exists but has no JSON files"""

    def test_empty_directory_triggers_info(self, caplog, tmp_path):
        """Test info logged when no JSON files found"""
        # Create scenarios directory but leave it empty
        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            with caplog.at_level(logging.INFO, logger="app.services.scenario_factory"):
                factory = ScenarioFactory()
                assert any(
                    "No template JSON files found" in record.message
                    for record in caplog.records
                )

    def test_empty_directory_creates_defaults(self, tmp_path):
        """Test that empty directory triggers default template creation"""
        # Create scenarios directory but leave it empty
        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            factory = ScenarioFactory()
            assert len(factory.universal_templates) == 32

    def test_empty_directory_calls_create_default(self, tmp_path):
        """Test that _create_default_templates is called when no JSON files"""
        # Create scenarios directory but leave it empty
        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            with patch.object(
                ScenarioFactory, "_create_default_templates"
            ) as mock_create:
                factory = ScenarioFactory.__new__(ScenarioFactory)
                factory.template_directory = Path("scenario_templates")
                factory.universal_templates = {}
                factory.content_cache = {}
                factory._load_universal_templates()
                mock_create.assert_called_once()


# ============================================================================
# Test Class 4: Load Templates from JSON
# ============================================================================


class TestLoadUniversalTemplatesFromJSON:
    """Test template loading from JSON files"""

    def test_load_valid_json_file(self, caplog, tmp_path):
        """Test loading a valid JSON template file"""
        # Create a temporary JSON file
        template_data = {
            "template_id": "test_template",
            "name": "Test Template",
            "category": "travel",
            "tier": 1,
            "base_vocabulary": ["hello", "goodbye"],
            "essential_phrases": {"beginner": ["Hello!", "Goodbye!"]},
            "cultural_context": {"country": "Test"},
            "learning_objectives": ["Learn greetings"],
            "conversation_starters": ["Hello, how are you?"],
            "scenario_variations": [],
            "difficulty_modifiers": {},
            "success_metrics": [],
        }

        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)
        json_file = scenarios_dir / "test_template.json"
        json_file.write_text(json.dumps(template_data))

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            with caplog.at_level(logging.INFO, logger="app.services.scenario_factory"):
                factory = ScenarioFactory()
                assert "test_template" in factory.universal_templates
                assert (
                    factory.universal_templates["test_template"].name == "Test Template"
                )
                assert any(
                    "Loaded template: Test Template" in record.message
                    for record in caplog.records
                )

    def test_load_multiple_json_files(self, tmp_path):
        """Test loading multiple JSON template files"""
        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)

        # Create two template files
        for i in range(2):
            template_data = {
                "template_id": f"json_template_{i}",
                "name": f"Template {i}",
                "category": "travel",
                "tier": 1,
                "base_vocabulary": [],
                "essential_phrases": {},
                "cultural_context": {},
                "learning_objectives": [],
                "conversation_starters": [],
            "scenario_variations": [],
                "difficulty_modifiers": {},
                "success_metrics": []
            }
            json_file = scenarios_dir / f"template_{i}.json"
            json_file.write_text(json.dumps(template_data))

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            factory = ScenarioFactory()
            assert "json_template_0" in factory.universal_templates
            assert "json_template_1" in factory.universal_templates

    def test_invalid_json_logs_error(self, caplog, tmp_path):
        """Test that invalid JSON file triggers error logging"""
        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)

        # Create invalid JSON file
        json_file = scenarios_dir / "invalid.json"
        json_file.write_text("{invalid json content")

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            with caplog.at_level(logging.ERROR, logger="app.services.scenario_factory"):
                factory = ScenarioFactory()
                assert any(
                    "Failed to load template" in record.message
                    for record in caplog.records
                )

    def test_templates_stored_correctly(self, tmp_path):
        """Test that loaded templates are stored with correct ID as key"""
        scenarios_dir = tmp_path / "app" / "config" / "scenarios"
        scenarios_dir.mkdir(parents=True)

        template_data = {
            "template_id": "unique_json_id_123",
            "name": "Unique JSON Template",
            "category": "business",
            "tier": 2,
            "base_vocabulary": ["meeting", "presentation"],
            "essential_phrases": {},
            "cultural_context": {},
            "learning_objectives": [],
            "conversation_starters": [],
        "scenario_variations": [],
                "difficulty_modifiers": {},
                "success_metrics": []
            }
        json_file = scenarios_dir / "unique.json"
        json_file.write_text(json.dumps(template_data))

        fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
        fake_module_path.parent.mkdir(parents=True)

        with patch("app.services.scenario_factory.__file__", str(fake_module_path)):
            factory = ScenarioFactory()
            assert "unique_json_id_123" in factory.universal_templates
            template = factory.universal_templates["unique_json_id_123"]
            assert template.name == "Unique JSON Template"
            assert template.category == ScenarioCategory.BUSINESS
            assert template.tier == 2


# ============================================================================
# Test Class 5: Create Universal Template
# ============================================================================


class TestCreateUniversalTemplate:
    """Test creation of UniversalScenarioTemplate from data"""

    def test_create_template_from_valid_data(self):
        """Test creating template from valid dictionary data"""
        factory = ScenarioFactory()

        data = {
            "template_id": "test_id",
            "name": "Test Name",
            "category": "restaurant",
            "tier": 3,
            "base_vocabulary": ["menu", "order"],
            "essential_phrases": {"beginner": ["I'd like to order"]},
            "cultural_context": {"etiquette": "tip 15-20%"},
            "learning_objectives": ["Order food"],
            "conversation_starters": ["Hello, table for two?"],
            "scenario_variations": [{"type": "formal"}],
            "difficulty_modifiers": {"advanced": {"speed": "fast"}},
            "success_metrics": ["Complete order"],
        }

        template = factory._create_universal_template(data)

        assert template.template_id == "test_id"
        assert template.name == "Test Name"
        assert template.category == ScenarioCategory.RESTAURANT
        assert template.tier == 3
        assert template.base_vocabulary == ["menu", "order"]
        assert template.essential_phrases == {"beginner": ["I'd like to order"]}
        assert template.cultural_context == {"etiquette": "tip 15-20%"}
        assert template.learning_objectives == ["Order food"]
        assert template.conversation_starters == ["Hello, table for two?"]
        assert template.scenario_variations == [{"type": "formal"}]
        assert template.difficulty_modifiers == {"advanced": {"speed": "fast"}}
        assert template.success_metrics == ["Complete order"]

    def test_create_template_all_fields_mapped(self):
        """Test that all fields are correctly mapped from data to template"""
        factory = ScenarioFactory()

        data = {
            "template_id": "comprehensive_test",
            "name": "Comprehensive Test",
            "category": "healthcare",
            "tier": 4,
            "base_vocabulary": ["doctor", "patient", "symptoms"],
            "essential_phrases": {
                "beginner": ["I feel sick"],
                "intermediate": ["I have a headache"],
                "advanced": ["I've been experiencing chest pain"],
            },
            "cultural_context": {
                "insurance": "required",
                "appointment": "schedule in advance",
            },
            "learning_objectives": [
                "Describe symptoms",
                "Understand medical advice",
                "Ask questions about treatment",
            ],
            "conversation_starters": [
                "Good morning, what brings you in today?",
                "How long have you been feeling this way?",
            ],
            "scenario_variations": [
                {"setting": "emergency room"},
                {"setting": "clinic"},
                {"setting": "pharmacy"},
            ],
            "difficulty_modifiers": {
                "beginner": {"vocabulary": "simple", "speed": "slow"},
                "advanced": {"vocabulary": "medical", "speed": "normal"},
            },
            "success_metrics": [
                "Communicate symptoms clearly",
                "Understand diagnosis",
                "Follow treatment plan",
            ],
        }

        template = factory._create_universal_template(data)

        # Verify every field
        assert isinstance(template, UniversalScenarioTemplate)
        assert template.template_id == data["template_id"]
        assert template.name == data["name"]
        assert template.category == ScenarioCategory.HEALTHCARE
        assert template.tier == data["tier"]
        assert template.base_vocabulary == data["base_vocabulary"]
        assert template.essential_phrases == data["essential_phrases"]
        assert template.cultural_context == data["cultural_context"]
        assert template.learning_objectives == data["learning_objectives"]
        assert template.conversation_starters == data["conversation_starters"]
        assert template.scenario_variations == data["scenario_variations"]
        assert template.difficulty_modifiers == data["difficulty_modifiers"]
        assert template.success_metrics == data["success_metrics"]


# ============================================================================
# Test Class 6: Create Default Templates
# ============================================================================


class TestCreateDefaultTemplates:
    """Test creation of default templates"""

    def test_creates_all_default_templates(self, caplog):
        """Test that all default templates are created"""
        with caplog.at_level(logging.INFO, logger="app.services.scenario_factory"):
            factory = ScenarioFactory()

            # Should have 32 unique templates (5 tier1 + 2 tier2 + 27 extended, minus 2 duplicates)
            assert len(factory.universal_templates) == 32

            # Verify log message about comprehensive system
            assert any(
                "Creating comprehensive 32-scenario template system" in record.message
                for record in caplog.records
            )

    def test_import_error_fallback_to_tier1_tier2(self, caplog):
        """Test fallback to Tier 1-2 only when extended templates can't import"""
        import sys
        
        # Save and remove the extended templates module
        extended_mod = sys.modules.pop('app.services.scenario_templates_extended', None)
        
        try:
            # Force reimport with mocked failure
            import importlib
            
            # Mock to make import raise ImportError
            original_import = importlib.import_module
            
            def mock_import_module(name, *args, **kwargs):
                if 'scenario_templates_extended' in name:
                    raise ImportError("Mocked import error")
                return original_import(name, *args, **kwargs)
            
            with patch('importlib.import_module', side_effect=mock_import_module):
                # Also need to handle direct imports in the factory code
                import builtins
                real_import = builtins.__import__
                
                def custom_import(name, *args, **kwargs):
                    if 'scenario_templates_extended' in name:
                        raise ImportError("Cannot import extended templates")
                    return real_import(name, *args, **kwargs)
                
                with patch('builtins.__import__', side_effect=custom_import):
                    with caplog.at_level(logging.WARNING, logger='app.services.scenario_factory'):
                        factory = ScenarioFactory()
                        
                        # Check warning was logged
                        warning_msgs = [r.message for r in caplog.records if r.levelname == 'WARNING']
                        assert any('Could not load extended templates' in msg for msg in warning_msgs)
                        assert any('using Tier 1-2 only' in msg for msg in warning_msgs)
        finally:
            # Restore module
            if extended_mod:
                sys.modules['app.services.scenario_templates_extended'] = extended_mod

    def test_verify_template_count(self):
        """Test that correct number of templates are created"""
        factory = ScenarioFactory()

        # 5 Tier 1 + 2 Tier 2 + 27 extended = 34 total, but 2 duplicates = 32 unique
        assert len(factory.universal_templates) == 32

        # Count by tier
        tier1_count = sum(
            1 for t in factory.universal_templates.values() if t.tier == 1
        )
        tier2_count = sum(
            1 for t in factory.universal_templates.values() if t.tier == 2
        )
        tier3_count = sum(
            1 for t in factory.universal_templates.values() if t.tier == 3
        )
        tier4_count = sum(
            1 for t in factory.universal_templates.values() if t.tier == 4
        )

        assert tier1_count == 5
        # Tier 2 has 10 (not 2) due to extended templates
        assert tier2_count == 10
        assert tier3_count == 10
        assert tier4_count == 7

    def test_all_templates_added_to_dict(self):
        """Test that all templates are added to universal_templates dict"""
        factory = ScenarioFactory()

        # Verify all templates have template_id as key
        for template_id, template in factory.universal_templates.items():
            assert template.template_id == template_id
            assert isinstance(template, UniversalScenarioTemplate)

    def test_logger_messages_for_each_template(self, caplog):
        """Test that logger info is created for each template"""
        with caplog.at_level(logging.INFO, logger="app.services.scenario_factory"):
            factory = ScenarioFactory()

            # Should have log messages for each template created
            template_logs = [
                r for r in caplog.records if "Created template:" in r.message
            ]

            # Should have 34 template creation logs (includes duplicates that get overwritten)
            assert len(template_logs) == 34

            # Verify format: "Created template: {name} (Tier {tier})"
            assert any("(Tier 1)" in record.message for record in template_logs)
            assert any("(Tier 2)" in record.message for record in template_logs)


# ============================================================================
# Test Class 7: Get All Templates
# ============================================================================


class TestGetAllTemplates:
    """Test get_all_templates method"""

    def test_returns_all_loaded_templates(self):
        """Test that get_all_templates returns all loaded templates"""
        factory = ScenarioFactory()
        templates = factory.get_all_templates()

        assert len(templates) == 32
        assert all(isinstance(t, UniversalScenarioTemplate) for t in templates)

    def test_returns_list_not_dict(self):
        """Test that get_all_templates returns a list, not dict"""
        factory = ScenarioFactory()
        templates = factory.get_all_templates()

        assert isinstance(templates, list)
        assert not isinstance(templates, dict)


# ============================================================================
# Test Class 8: Get Template by ID
# ============================================================================


class TestGetTemplateById:
    """Test get_template_by_id method"""

    def test_valid_id_returns_template(self):
        """Test that valid ID returns correct template"""
        factory = ScenarioFactory()
        template = factory.get_template_by_id("greetings_introductions")

        assert template is not None
        assert template.template_id == "greetings_introductions"
        assert isinstance(template, UniversalScenarioTemplate)

    def test_invalid_id_returns_none(self):
        """Test that invalid ID returns None"""
        factory = ScenarioFactory()
        template = factory.get_template_by_id("nonexistent_template")

        assert template is None

    def test_exact_template_returned(self):
        """Test that exact template object is returned"""
        factory = ScenarioFactory()
        template = factory.get_template_by_id("greetings_introductions")

        # Should be same object as in dict
        assert template is factory.universal_templates["greetings_introductions"]


# ============================================================================
# Test Class 9: Get Templates by Tier
# ============================================================================


class TestGetTemplatesByTier:
    """Test get_templates_by_tier method"""

    def test_no_tier_returns_all_sorted(self):
        """Test that no tier argument returns all templates sorted"""
        factory = ScenarioFactory()
        templates = factory.get_templates_by_tier()

        assert len(templates) == 32

        # Verify sorted by (tier, name)
        for i in range(len(templates) - 1):
            curr = templates[i]
            next_t = templates[i + 1]
            assert (curr.tier, curr.name) <= (next_t.tier, next_t.name)

    def test_tier_1_filter(self):
        """Test filtering by tier 1"""
        factory = ScenarioFactory()
        templates = factory.get_templates_by_tier(tier=1)

        assert len(templates) == 5
        assert all(t.tier == 1 for t in templates)

        # Verify sorted by name within tier
        names = [t.name for t in templates]
        assert names == sorted(names)

    def test_tier_2_filter(self):
        """Test filtering by tier 2"""
        factory = ScenarioFactory()
        templates = factory.get_templates_by_tier(tier=2)

        assert len(templates) == 10
        assert all(t.tier == 2 for t in templates)

    def test_tier_3_or_4_filter(self):
        """Test filtering by tier 3 and 4"""
        factory = ScenarioFactory()
        tier3_templates = factory.get_templates_by_tier(tier=3)
        tier4_templates = factory.get_templates_by_tier(tier=4)

        # Together should have 17 templates (10 + 7)
        assert len(tier3_templates) + len(tier4_templates) == 17
        assert all(t.tier == 3 for t in tier3_templates)
        assert all(t.tier == 4 for t in tier4_templates)

    def test_sorting_by_tier_and_name(self):
        """Test that templates are sorted by (tier, name)"""
        factory = ScenarioFactory()
        templates = factory.get_templates_by_tier()

        # Manual verification of sort order
        sorted_templates = sorted(
            factory.universal_templates.values(), key=lambda t: (t.tier, t.name)
        )

        assert templates == sorted_templates


# ============================================================================
# Test Class 10: Get Templates by Category
# ============================================================================


class TestGetTemplatesByCategory:
    """Test get_templates_by_category method"""

    def test_filter_by_category_returns_matching(self):
        """Test that filtering by category returns only matching templates"""
        factory = ScenarioFactory()
        templates = factory.get_templates_by_category(ScenarioCategory.TRAVEL)

        assert len(templates) > 0
        assert all(t.category == ScenarioCategory.TRAVEL for t in templates)

    def test_multiple_categories(self):
        """Test filtering by different categories"""
        factory = ScenarioFactory()

        categories_to_test = [
            ScenarioCategory.RESTAURANT,
            ScenarioCategory.SHOPPING,
            ScenarioCategory.BUSINESS,
        ]

        for category in categories_to_test:
            templates = factory.get_templates_by_category(category)
            assert all(t.category == category for t in templates)

    def test_empty_result_for_unused_category(self):
        """Test that unused category returns empty list (not None)"""
        factory = ScenarioFactory()

        # Check if EMERGENCY category has templates
        templates = factory.get_templates_by_category(ScenarioCategory.EMERGENCY)

        # Should return list (may be empty or have templates)
        assert isinstance(templates, list)
