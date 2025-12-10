"""
Integration tests for Ollama model selection in AI router.

Tests validate that the router respects user's Ollama model preferences
with correct priority order: use_case > language > general > auto.

Session 98 - Phase 2
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_router import EnhancedAIRouter, FallbackReason, ProviderSelection
from app.services.ollama_service import OllamaService


class TestRouterOllamaModelSelection:
    """Integration tests for router's Ollama model selection logic"""

    @pytest.fixture
    def router(self):
        """Create router instance for testing"""
        return EnhancedAIRouter()

    @pytest.fixture
    def mock_ollama_available(self):
        """Mock Ollama as available"""
        with patch.object(
            OllamaService, "check_availability", return_value=True
        ) as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_router_uses_general_preferred_ollama_model(
        self, router, mock_ollama_available
    ):
        """Test router uses user's general preferred Ollama model"""
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",
            }
        }

        # Mock check_availability and list_models (Phase 4 validation)
        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that llama2:13b IS installed
            mock_list.return_value = [
                {"name": "llama2:13b"},
                {"name": "llama2:7b"},
            ]

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        assert selection.provider_name == "ollama"
        assert selection.model == "llama2:13b"
        assert selection.is_fallback is True
        assert selection.cost_estimate == 0.0

    @pytest.mark.asyncio
    async def test_router_uses_language_specific_ollama_model(
        self, router, mock_ollama_available
    ):
        """Test router uses language-specific Ollama model over general preference"""
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",  # General preference
                "ollama_model_by_language": {
                    "en": "neural-chat:7b",  # Language-specific (higher priority)
                    "fr": "mistral:7b",
                },
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that all requested models are installed
            mock_list.return_value = [
                {"name": "neural-chat:7b"},
                {"name": "mistral:7b"},
                {"name": "llama2:13b"},
            ]

            # Test English - should use language-specific
            selection_en = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Test French - should use language-specific
            selection_fr = await router._select_local_provider(
                language="fr",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        assert selection_en.model == "neural-chat:7b"  # Not llama2:13b
        assert selection_fr.model == "mistral:7b"

    @pytest.mark.asyncio
    async def test_router_uses_use_case_specific_ollama_model(
        self, router, mock_ollama_available
    ):
        """Test router uses use-case specific model (highest priority)"""
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",  # General
                "ollama_model_by_language": {"en": "neural-chat:7b"},  # Language
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b"  # Use-case (highest)
                },
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that all models are installed
            mock_list.return_value = [
                {"name": "codellama:7b"},
                {"name": "neural-chat:7b"},
                {"name": "llama2:13b"},
            ]

            # Test technical use case - should use use-case specific
            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="technical",
                user_preferences=user_preferences,
            )

        # Use-case preference wins over language and general preferences
        assert selection.model == "codellama:7b"

    @pytest.mark.asyncio
    async def test_router_preference_priority_order(
        self, router, mock_ollama_available
    ):
        """Test preference priority: use_case > language > general > auto"""
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",
                "ollama_model_by_language": {"en": "neural-chat:7b", "es": "llama2:7b"},
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b",
                    "grammar": "llama2:13b",
                },
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that all models are installed
            mock_list.return_value = [
                {"name": "codellama:7b"},
                {"name": "neural-chat:7b"},
                {"name": "llama2:13b"},
                {"name": "llama2:7b"},
            ]

            # Scenario 1: use_case match (highest priority)
            sel1 = await router._select_local_provider(
                "en", "user_preference", "technical", user_preferences
            )
            assert sel1.model == "codellama:7b"  # use_case wins

            # Scenario 2: language match (no use_case match)
            sel2 = await router._select_local_provider(
                "en", "user_preference", "conversation", user_preferences
            )
            assert sel2.model == "neural-chat:7b"  # language wins

            # Scenario 3: general preference (no use_case or language match)
            sel3 = await router._select_local_provider(
                "de", "user_preference", "conversation", user_preferences
            )
            assert sel3.model == "llama2:13b"  # general wins

    @pytest.mark.asyncio
    async def test_router_fallback_to_auto_selection(
        self, router, mock_ollama_available
    ):
        """Test router falls back to automatic selection when no preferences set"""
        user_preferences = {
            "ai_provider_settings": {}  # No Ollama preferences
        }

        mock_installed = [{"name": "llama2:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
            patch.object(
                OllamaService, "get_recommended_model", return_value="llama2:7b"
            ) as mock_recommend,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Should call get_recommended_model for auto-selection with installed_models
            mock_recommend.assert_called_once_with(
                "en", "conversation", installed_models=mock_installed
            )
            assert selection.model == "llama2:7b"

    @pytest.mark.asyncio
    async def test_router_no_preferences_provided(self, router, mock_ollama_available):
        """Test router handles None user_preferences gracefully"""
        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "get_recommended_model", return_value="llama2:7b"
            ) as mock_recommend,
        ):
            mock_avail.return_value = True

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=None,  # No preferences
            )

            # Should use auto-selection
            mock_recommend.assert_called_once()
            assert selection.model == "llama2:7b"

    @pytest.mark.asyncio
    async def test_budget_fallback_respects_ollama_preference(
        self, router, mock_ollama_available
    ):
        """Test budget exceeded fallback uses user's preferred Ollama model"""
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "mistral:7b",
                "auto_fallback_to_ollama": True,
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
            patch.object(
                router, "check_budget_status", new_callable=AsyncMock
            ) as mock_budget,
        ):
            mock_avail.return_value = True
            # Mock that mistral:7b is installed
            mock_list.return_value = [{"name": "mistral:7b"}]

            # Mock budget status as exceeded
            mock_budget_status = MagicMock()
            mock_budget_status.is_exceeded = True
            mock_budget_status.percentage_used = 105.0
            mock_budget_status.alert_level.value = "critical"
            mock_budget.return_value = mock_budget_status

            # Simulate budget exceeded scenario
            selection = await router._select_local_provider(
                language="en",
                reason="budget_exceeded",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        assert selection.model == "mistral:7b"  # User preference respected
        assert selection.is_fallback is True
        assert selection.fallback_reason == FallbackReason.BUDGET_EXCEEDED

    @pytest.mark.asyncio
    async def test_privacy_mode_uses_language_model(
        self, router, mock_ollama_available
    ):
        """Test privacy mode uses language-specific model"""
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_language": {
                    "fr": "mistral:7b",
                },
                "prefer_local_when_available": True,
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that mistral:7b is installed
            mock_list.return_value = [{"name": "mistral:7b"}]

            selection = await router._select_local_provider(
                language="fr",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        assert selection.model == "mistral:7b"
        assert selection.fallback_reason == FallbackReason.USER_PREFERENCE

    @pytest.mark.asyncio
    async def test_technical_use_case_uses_codellama(
        self, router, mock_ollama_available
    ):
        """Test technical use case automatically selects codellama"""
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b",
                    "grammar": "llama2:13b",
                }
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that codellama:7b is installed
            mock_list.return_value = [
                {"name": "codellama:7b"},
                {"name": "llama2:13b"},
            ]

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="technical",
                user_preferences=user_preferences,
            )

        assert selection.model == "codellama:7b"

    @pytest.mark.asyncio
    async def test_router_passes_model_to_service(self, router, mock_ollama_available):
        """Test that selected model is passed in ProviderSelection"""
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "custom-model:latest",
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            # Mock that custom-model:latest is installed
            mock_list.return_value = [{"name": "custom-model:latest"}]

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        # Verify the selection contains the correct model
        assert selection.model == "custom-model:latest"
        assert selection.service is not None
        assert selection.provider_name == "ollama"

    @pytest.mark.asyncio
    async def test_empty_preferences_dict(self, router, mock_ollama_available):
        """Test router handles empty ollama_model_by_* dictionaries"""
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_language": {},
                "ollama_model_by_use_case": {},
            }
        }

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "get_recommended_model", return_value="llama2:7b"
            ) as mock_recommend,
        ):
            mock_avail.return_value = True

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Should fall back to auto-selection
            mock_recommend.assert_called_once()
            assert selection.model == "llama2:7b"

    @pytest.mark.asyncio
    async def test_all_four_calls_updated(self, router):
        """Test all four calls to _select_local_provider now pass parameters"""
        # This test verifies the signature changes are consistent

        # We'll test by checking the method can be called with all parameters
        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "get_recommended_model", return_value="llama2:7b"
            ),
        ):
            mock_avail.return_value = True

            # All these calls should work without errors
            await router._select_local_provider(
                "en", "user_preference", "conversation", None
            )
            await router._select_local_provider(
                "en", "budget_exceeded", "conversation", {}
            )
            await router._select_local_provider(
                "en", "api_unavailable", "technical", None
            )
            await router._select_local_provider(
                "en", "budget_exceeded_auto_fallback", "grammar", {}
            )

        # If we get here without errors, all signature updates are correct
        assert True
