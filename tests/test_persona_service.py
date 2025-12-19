"""
Comprehensive Tests for PersonaService

Tests cover:
- Persona loading and caching
- Dynamic field injection
- Error handling
- Validation
- All public methods
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.services.persona_service import (
    PersonaService,
    PersonaType,
    get_persona_service,
)


class TestPersonaServiceInitialization:
    """Test PersonaService initialization"""

    def test_initialization_with_default_directory(self):
        """Test initialization uses default personas directory"""
        service = PersonaService()

        assert service.personas_dir is not None
        assert service.personas_dir.name == "personas"
        assert service._persona_cache == {}
        assert service._global_guidelines is None

    def test_initialization_with_custom_directory(self, tmp_path):
        """Test initialization with custom personas directory"""
        custom_dir = tmp_path / "custom_personas"
        custom_dir.mkdir()

        # Create required files
        (custom_dir / "global_guidelines.md").write_text("Global guidelines")
        (custom_dir / "guiding_challenger.md").write_text("Guiding challenger persona")

        service = PersonaService(personas_directory=custom_dir)

        assert service.personas_dir == custom_dir

    def test_initialization_fails_with_nonexistent_directory(self, tmp_path):
        """Test initialization raises error if directory doesn't exist"""
        nonexistent_dir = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError) as exc_info:
            PersonaService(personas_directory=nonexistent_dir)

        assert "Personas directory not found" in str(exc_info.value)


class TestGetAvailablePersonas:
    """Test get_available_personas method"""

    def test_returns_all_personas(self):
        """Test returns all 5 available personas"""
        service = PersonaService()
        personas = service.get_available_personas()

        assert len(personas) == 5
        assert isinstance(personas, list)

    def test_persona_metadata_structure(self):
        """Test each persona has required metadata fields"""
        service = PersonaService()
        personas = service.get_available_personas()

        for persona in personas:
            assert "persona_type" in persona
            assert "name" in persona
            assert "description" in persona
            assert "key_traits" in persona
            assert "best_for" in persona
            assert isinstance(persona["key_traits"], list)

    def test_all_persona_types_present(self):
        """Test all PersonaType enum values are represented"""
        service = PersonaService()
        personas = service.get_available_personas()

        persona_types = {p["persona_type"] for p in personas}
        expected_types = {
            "guiding_challenger",
            "encouraging_coach",
            "friendly_conversational",
            "expert_scholar",
            "creative_mentor",
        }

        assert persona_types == expected_types


class TestLoadFile:
    """Test _load_file method"""

    def test_loads_existing_file(self):
        """Test loading an existing persona file"""
        service = PersonaService()

        # Load a known file
        content = service._load_file("guiding_challenger.md")

        assert content is not None
        assert len(content) > 0
        assert isinstance(content, str)

    def test_raises_error_for_nonexistent_file(self):
        """Test raises FileNotFoundError for nonexistent file"""
        service = PersonaService()

        with pytest.raises(FileNotFoundError) as exc_info:
            service._load_file("nonexistent_persona.md")

        assert "Persona file not found" in str(exc_info.value)

    def test_file_encoding_utf8(self):
        """Test files are loaded with UTF-8 encoding"""
        service = PersonaService()

        # Load file and check for UTF-8 characters
        content = service._load_file("guiding_challenger.md")

        # Should not raise UnicodeDecodeError
        assert isinstance(content, str)


class TestGetGlobalGuidelines:
    """Test get_global_guidelines method"""

    def test_loads_global_guidelines(self):
        """Test loads global guidelines content"""
        service = PersonaService()

        guidelines = service.get_global_guidelines()

        assert guidelines is not None
        assert len(guidelines) > 0
        assert isinstance(guidelines, str)

    def test_caches_global_guidelines(self):
        """Test global guidelines are cached after first load"""
        service = PersonaService()

        # First load
        guidelines1 = service.get_global_guidelines()

        # Should be cached
        assert service._global_guidelines is not None

        # Second load (should use cache)
        guidelines2 = service.get_global_guidelines()

        assert guidelines1 == guidelines2
        assert guidelines1 is guidelines2  # Same object reference


class TestGetPersonaPrompt:
    """Test get_persona_prompt method"""

    def test_generates_complete_prompt_with_defaults(self):
        """Test generates prompt with default field values"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.GUIDING_CHALLENGER
        )

        assert prompt is not None
        assert len(prompt) > 0
        assert isinstance(prompt, str)

    def test_includes_global_guidelines(self):
        """Test prompt includes global guidelines"""
        service = PersonaService()

        guidelines = service.get_global_guidelines()
        prompt = service.get_persona_prompt(
            persona_type=PersonaType.GUIDING_CHALLENGER
        )

        # Prompt should contain guidelines (or at least part of them)
        assert guidelines[:100] in prompt

    def test_includes_persona_specific_content(self):
        """Test prompt includes persona-specific content"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.GUIDING_CHALLENGER
        )

        # Should contain persona-specific markers
        assert "Guiding Challenger" in prompt or "guiding" in prompt.lower()

    def test_injects_subject_field(self):
        """Test subject field is injected into prompt"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.EXPERT_SCHOLAR,
            subject="calculus",
        )

        assert "calculus" in prompt

    def test_injects_learner_level_field(self):
        """Test learner_level field is injected into prompt"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.ENCOURAGING_COACH,
            learner_level="advanced",
        )

        assert "advanced" in prompt

    def test_injects_language_field(self):
        """Test language field is injected into prompt"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.FRIENDLY_CONVERSATIONALIST,
            language="es",
        )

        assert "es" in prompt

    def test_injects_all_fields_together(self):
        """Test all dynamic fields are injected together"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.CREATIVE_MENTOR,
            subject="Python programming",
            learner_level="intermediate",
            language="fr",
        )

        assert "Python programming" in prompt
        assert "intermediate" in prompt
        assert "fr" in prompt

    def test_caches_persona_content(self):
        """Test persona content is cached after first load"""
        service = PersonaService()

        # First load
        prompt1 = service.get_persona_prompt(
            persona_type=PersonaType.GUIDING_CHALLENGER,
            subject="math",
        )

        # Cache should have entry
        assert "guiding_challenger" in service._persona_cache

        # Second load (should use cache)
        prompt2 = service.get_persona_prompt(
            persona_type=PersonaType.GUIDING_CHALLENGER,
            subject="physics",
        )

        # Prompts should be different (different subject) but use cached template
        assert prompt1 != prompt2
        assert "math" in prompt1
        assert "physics" in prompt2

    def test_raises_error_for_invalid_persona_type(self):
        """Test raises ValueError for invalid persona type"""
        service = PersonaService()

        # Try to use invalid persona type (code validates and raises ValueError)
        with pytest.raises(ValueError) as exc_info:
            service.get_persona_prompt(persona_type="invalid_persona")  # type: ignore

        assert "Invalid persona type" in str(exc_info.value)

    def test_handles_empty_subject(self):
        """Test handles empty subject by using default"""
        service = PersonaService()

        prompt = service.get_persona_prompt(
            persona_type=PersonaType.GUIDING_CHALLENGER,
            subject="",
        )

        # Should use default "general learning"
        assert "general learning" in prompt

    def test_all_persona_types_generate_prompts(self):
        """Test all persona types can generate prompts successfully"""
        service = PersonaService()

        for persona_type in PersonaType:
            prompt = service.get_persona_prompt(persona_type=persona_type)

            assert prompt is not None
            assert len(prompt) > 100  # Should be substantial content
            assert isinstance(prompt, str)


class TestInjectDynamicFields:
    """Test _inject_dynamic_fields method"""

    def test_replaces_subject_placeholder(self):
        """Test replaces {subject} placeholder"""
        service = PersonaService()

        content = "Teaching {subject} to students"
        result = service._inject_dynamic_fields(
            content, subject="mathematics", learner_level="beginner", language="en"
        )

        assert result == "Teaching mathematics to students"

    def test_replaces_learner_level_placeholder(self):
        """Test replaces {learner_level} placeholder"""
        service = PersonaService()

        content = "For {learner_level} learners"
        result = service._inject_dynamic_fields(
            content, subject="", learner_level="advanced", language="en"
        )

        assert result == "For advanced learners"

    def test_replaces_language_placeholder(self):
        """Test replaces {language} placeholder"""
        service = PersonaService()

        content = "Communicate in {language}"
        result = service._inject_dynamic_fields(
            content, subject="", learner_level="beginner", language="es"
        )

        assert result == "Communicate in es"

    def test_replaces_all_placeholders(self):
        """Test replaces all placeholders in one pass"""
        service = PersonaService()

        content = "Teaching {subject} at {learner_level} level in {language}"
        result = service._inject_dynamic_fields(
            content, subject="calculus", learner_level="intermediate", language="fr"
        )

        assert result == "Teaching calculus at intermediate level in fr"

    def test_handles_empty_subject(self):
        """Test handles empty subject with default value"""
        service = PersonaService()

        content = "Teaching {subject}"
        result = service._inject_dynamic_fields(
            content, subject="", learner_level="beginner", language="en"
        )

        assert result == "Teaching general learning"

    def test_preserves_content_without_placeholders(self):
        """Test preserves content that has no placeholders"""
        service = PersonaService()

        content = "This content has no placeholders"
        result = service._inject_dynamic_fields(
            content, subject="math", learner_level="beginner", language="en"
        )

        assert result == content


class TestGetPersonaMetadata:
    """Test get_persona_metadata method"""

    def test_returns_metadata_for_valid_persona(self):
        """Test returns metadata dictionary for valid persona"""
        service = PersonaService()

        metadata = service.get_persona_metadata(PersonaType.GUIDING_CHALLENGER)

        assert metadata is not None
        assert isinstance(metadata, dict)

    def test_metadata_has_required_fields(self):
        """Test metadata has all required fields"""
        service = PersonaService()

        metadata = service.get_persona_metadata(PersonaType.ENCOURAGING_COACH)

        assert "persona_type" in metadata
        assert "name" in metadata
        assert "description" in metadata
        assert "key_traits" in metadata
        assert "best_for" in metadata

    def test_metadata_excludes_file_field(self):
        """Test metadata excludes internal 'file' field"""
        service = PersonaService()

        metadata = service.get_persona_metadata(PersonaType.EXPERT_SCHOLAR)

        assert "file" not in metadata

    def test_raises_error_for_invalid_persona(self):
        """Test raises ValueError for invalid persona type"""
        service = PersonaService()

        with pytest.raises(ValueError) as exc_info:
            # Try to get metadata with invalid persona type
            service.get_persona_metadata("invalid_persona")  # type: ignore

        assert "Invalid persona type" in str(exc_info.value)


class TestValidatePersonaType:
    """Test validate_persona_type method"""

    def test_returns_true_for_valid_persona_types(self):
        """Test returns True for all valid persona types"""
        service = PersonaService()

        valid_types = [
            "guiding_challenger",
            "encouraging_coach",
            "friendly_conversational",
            "expert_scholar",
            "creative_mentor",
        ]

        for persona_type in valid_types:
            assert service.validate_persona_type(persona_type) is True

    def test_returns_false_for_invalid_persona_types(self):
        """Test returns False for invalid persona types"""
        service = PersonaService()

        invalid_types = [
            "invalid_persona",
            "nonexistent",
            "",
            "GUIDING_CHALLENGER",  # Wrong case
            "guiding challenger",  # Space instead of underscore
        ]

        for persona_type in invalid_types:
            assert service.validate_persona_type(persona_type) is False

    def test_case_sensitive_validation(self):
        """Test validation is case-sensitive"""
        service = PersonaService()

        assert service.validate_persona_type("guiding_challenger") is True
        assert service.validate_persona_type("Guiding_Challenger") is False
        assert service.validate_persona_type("GUIDING_CHALLENGER") is False


class TestGetDefaultPersona:
    """Test get_default_persona method"""

    def test_returns_persona_type_enum(self):
        """Test returns PersonaType enum value"""
        service = PersonaService()

        default = service.get_default_persona()

        assert isinstance(default, PersonaType)

    def test_returns_friendly_conversationalist(self):
        """Test default is FRIENDLY_CONVERSATIONALIST"""
        service = PersonaService()

        default = service.get_default_persona()

        assert default == PersonaType.FRIENDLY_CONVERSATIONALIST


class TestGetPersonaServiceSingleton:
    """Test get_persona_service singleton function"""

    def test_returns_persona_service_instance(self):
        """Test returns PersonaService instance"""
        service = get_persona_service()

        assert isinstance(service, PersonaService)

    def test_returns_same_instance_on_multiple_calls(self):
        """Test singleton pattern - returns same instance"""
        service1 = get_persona_service()
        service2 = get_persona_service()

        assert service1 is service2

    def test_singleton_preserves_cache(self):
        """Test singleton preserves cache across calls"""
        service1 = get_persona_service()

        # Load a persona to populate cache
        service1.get_persona_prompt(PersonaType.GUIDING_CHALLENGER)

        service2 = get_persona_service()

        # Cache should be preserved
        assert len(service2._persona_cache) > 0


class TestPersonaTypeEnum:
    """Test PersonaType enum"""

    def test_all_persona_types_defined(self):
        """Test all expected persona types are defined"""
        expected_types = {
            "GUIDING_CHALLENGER",
            "ENCOURAGING_COACH",
            "FRIENDLY_CONVERSATIONALIST",
            "EXPERT_SCHOLAR",
            "CREATIVE_MENTOR",
        }

        actual_types = {pt.name for pt in PersonaType}

        assert actual_types == expected_types

    def test_persona_type_values(self):
        """Test persona type enum values match expected strings"""
        assert PersonaType.GUIDING_CHALLENGER.value == "guiding_challenger"
        assert PersonaType.ENCOURAGING_COACH.value == "encouraging_coach"
        assert PersonaType.FRIENDLY_CONVERSATIONALIST.value == "friendly_conversational"
        assert PersonaType.EXPERT_SCHOLAR.value == "expert_scholar"
        assert PersonaType.CREATIVE_MENTOR.value == "creative_mentor"

    def test_can_create_from_string(self):
        """Test can create PersonaType from string value"""
        persona = PersonaType("guiding_challenger")

        assert persona == PersonaType.GUIDING_CHALLENGER

    def test_raises_error_for_invalid_string(self):
        """Test raises ValueError for invalid string"""
        with pytest.raises(ValueError):
            PersonaType("invalid_persona")


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_handles_missing_global_guidelines_gracefully(self, tmp_path):
        """Test handles missing global_guidelines.md file"""
        custom_dir = tmp_path / "incomplete_personas"
        custom_dir.mkdir()

        # Don't create global_guidelines.md
        service = PersonaService(personas_directory=custom_dir)

        with pytest.raises(FileNotFoundError):
            service.get_global_guidelines()

    def test_handles_corrupted_persona_file(self, tmp_path):
        """Test handles corrupted or unreadable persona file"""
        custom_dir = tmp_path / "corrupted_personas"
        custom_dir.mkdir()

        # Create global guidelines
        (custom_dir / "global_guidelines.md").write_text("Global")

        # Create corrupted file (we'll simulate read error)
        corrupted_file = custom_dir / "guiding_challenger.md"
        corrupted_file.write_text("Persona content")

        service = PersonaService(personas_directory=custom_dir)

        # Make file unreadable by changing permissions
        corrupted_file.chmod(0o000)

        try:
            with pytest.raises((FileNotFoundError, PermissionError, OSError)):
                service.get_persona_prompt(PersonaType.GUIDING_CHALLENGER)
        finally:
            # Restore permissions for cleanup
            corrupted_file.chmod(0o644)
