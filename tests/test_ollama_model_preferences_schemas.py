"""
Unit tests for Ollama model preference fields in AIProviderSettings schema.

Tests validate the new Ollama model selection fields added in Session 98.
"""

import pytest
from app.models.schemas import AIProviderSettings, ProviderSelectionMode


class TestOllamaModelPreferencesSchema:
    """Unit tests for Ollama model preference fields in AIProviderSettings"""

    def test_ai_provider_settings_with_preferred_ollama_model(self):
        """Test AIProviderSettings with general preferred Ollama model"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
            preferred_ollama_model="llama2:13b",
        )

        assert settings.preferred_ollama_model == "llama2:13b"
        assert settings.ollama_model_by_language == {}
        assert settings.ollama_model_by_use_case == {}

    def test_ai_provider_settings_with_language_specific_models(self):
        """Test AIProviderSettings with language-specific Ollama models"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
            ollama_model_by_language={
                "en": "neural-chat:7b",
                "fr": "mistral:7b",
                "es": "llama2:7b",
            },
        )

        assert settings.preferred_ollama_model is None
        assert settings.ollama_model_by_language == {
            "en": "neural-chat:7b",
            "fr": "mistral:7b",
            "es": "llama2:7b",
        }
        assert settings.ollama_model_by_use_case == {}

    def test_ai_provider_settings_with_use_case_specific_models(self):
        """Test AIProviderSettings with use-case specific Ollama models"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
            ollama_model_by_use_case={
                "technical": "codellama:7b",
                "grammar": "llama2:13b",
                "conversation": "neural-chat:7b",
            },
        )

        assert settings.preferred_ollama_model is None
        assert settings.ollama_model_by_language == {}
        assert settings.ollama_model_by_use_case == {
            "technical": "codellama:7b",
            "grammar": "llama2:13b",
            "conversation": "neural-chat:7b",
        }

    def test_ai_provider_settings_all_ollama_fields_optional(self):
        """Test that all Ollama model preference fields are optional"""
        # Should work without any Ollama preferences
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
        )

        assert settings.preferred_ollama_model is None
        assert settings.ollama_model_by_language == {}
        assert settings.ollama_model_by_use_case == {}

    def test_ai_provider_settings_with_all_ollama_preferences(self):
        """Test AIProviderSettings with all Ollama preference fields populated"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
            preferred_ollama_model="llama2:13b",
            ollama_model_by_language={
                "en": "neural-chat:7b",
                "fr": "mistral:7b",
            },
            ollama_model_by_use_case={
                "technical": "codellama:7b",
                "grammar": "llama2:13b",
            },
        )

        # All fields should be set
        assert settings.preferred_ollama_model == "llama2:13b"
        assert settings.ollama_model_by_language == {
            "en": "neural-chat:7b",
            "fr": "mistral:7b",
        }
        assert settings.ollama_model_by_use_case == {
            "technical": "codellama:7b",
            "grammar": "llama2:13b",
        }

    def test_ai_provider_settings_backward_compatible(self):
        """Test that existing settings without Ollama preferences still work"""
        # This simulates existing user settings that don't have Ollama preferences
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.USER_CHOICE,
            default_provider="claude",
            enforce_budget_limits=True,
            budget_override_allowed=True,
            alert_on_budget_threshold=0.75,
            notify_on_provider_change=True,
            notify_on_budget_alert=True,
            auto_fallback_to_ollama=False,
            prefer_local_when_available=False,
        )

        # All existing fields should work
        assert settings.provider_selection_mode == ProviderSelectionMode.USER_CHOICE
        assert settings.default_provider == "claude"
        assert settings.enforce_budget_limits is True

        # New fields should have default values
        assert settings.preferred_ollama_model is None
        assert settings.ollama_model_by_language == {}
        assert settings.ollama_model_by_use_case == {}

    def test_ai_provider_settings_model_names_validation(self):
        """Test that various Ollama model name formats are accepted"""
        # Different model name formats
        model_formats = [
            "llama2:7b",
            "llama2:13b",
            "mistral:7b",
            "neural-chat:7b",
            "codellama:7b",
            "llama2",  # Without size specification
            "custom-model:latest",  # Custom models
        ]

        for model_name in model_formats:
            settings = AIProviderSettings(
                provider_selection_mode=ProviderSelectionMode.BALANCED,
                preferred_ollama_model=model_name,
            )
            assert settings.preferred_ollama_model == model_name

    def test_ai_provider_settings_empty_dictionaries(self):
        """Test that empty dictionaries work for language and use_case mappings"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
            ollama_model_by_language={},
            ollama_model_by_use_case={},
        )

        assert settings.ollama_model_by_language == {}
        assert settings.ollama_model_by_use_case == {}

    def test_ai_provider_settings_dict_serialization(self):
        """Test that settings with Ollama preferences serialize correctly"""
        settings = AIProviderSettings(
            provider_selection_mode=ProviderSelectionMode.BALANCED,
            preferred_ollama_model="llama2:13b",
            ollama_model_by_language={"en": "neural-chat:7b", "fr": "mistral:7b"},
            ollama_model_by_use_case={"technical": "codellama:7b"},
        )

        # Convert to dict
        settings_dict = settings.model_dump()

        # Verify serialization
        assert settings_dict["preferred_ollama_model"] == "llama2:13b"
        assert settings_dict["ollama_model_by_language"] == {
            "en": "neural-chat:7b",
            "fr": "mistral:7b",
        }
        assert settings_dict["ollama_model_by_use_case"] == {"technical": "codellama:7b"}

    def test_ai_provider_settings_from_dict(self):
        """Test that settings can be created from dict with Ollama preferences"""
        settings_dict = {
            "provider_selection_mode": "balanced",
            "default_provider": "claude",
            "enforce_budget_limits": True,
            "budget_override_allowed": True,
            "alert_on_budget_threshold": 0.80,
            "notify_on_provider_change": True,
            "notify_on_budget_alert": True,
            "auto_fallback_to_ollama": True,
            "prefer_local_when_available": False,
            "preferred_ollama_model": "llama2:13b",
            "ollama_model_by_language": {"en": "neural-chat:7b"},
            "ollama_model_by_use_case": {"technical": "codellama:7b"},
        }

        settings = AIProviderSettings(**settings_dict)

        assert settings.preferred_ollama_model == "llama2:13b"
        assert settings.ollama_model_by_language == {"en": "neural-chat:7b"}
        assert settings.ollama_model_by_use_case == {"technical": "codellama:7b"}
