"""
End-to-end tests for Phase 4 model validation.

Tests the complete flow from API → Router → Service with model validation.
Session 98 - Phase 4
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.ollama import get_recommended_models
from app.services.ai_router import EnhancedAIRouter
from app.services.ollama_service import OllamaService


class TestPhase4EndToEndValidation:
    """End-to-end tests for Phase 4 validation flow"""

    @pytest.fixture
    def router(self):
        """Create router instance for testing"""
        return EnhancedAIRouter()

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return MagicMock(user_id="test_user")

    @pytest.mark.asyncio
    async def test_e2e_api_returns_only_installed_models(self, mock_user):
        """
        E2E: API endpoint returns recommendations only from installed models
        """
        # Simulate user has only 2 models installed
        mock_installed = [
            {"name": "llama2:7b"},
            {"name": "mistral:7b"},
        ]

        with (
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
            patch.object(
                OllamaService, "get_recommended_model", return_value="llama2:7b"
            ) as mock_recommend,
        ):
            mock_list.return_value = mock_installed

            result = await get_recommended_models(
                language="en", use_case="conversation", current_user=mock_user
            )

            # Verify API called list_models
            mock_list.assert_called_once()

            # Verify get_recommended_model received installed models
            mock_recommend.assert_called_once_with(
                "en", "conversation", installed_models=mock_installed
            )

            # Verify response contains only installed models
            assert result["recommended_model"] == "llama2:7b"
            all_models = [result["recommended_model"]] + result["alternatives"]
            assert all(model in ["llama2:7b", "mistral:7b"] for model in all_models)

    @pytest.mark.asyncio
    async def test_e2e_api_handles_no_installed_models(self, mock_user):
        """
        E2E: API endpoint gracefully handles when no models are installed
        """
        with patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = []  # No models installed

            result = await get_recommended_models(current_user=mock_user)

            assert result["recommended_model"] is None
            assert result["alternatives"] == []
            assert "No Ollama models installed" in result["message"]

    @pytest.mark.asyncio
    async def test_e2e_router_validates_user_preference_against_installed(self, router):
        """
        E2E: Router validates user's preferred model is actually installed
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "codellama:7b",  # User wants this
            }
        }

        # Only llama2:7b is installed, NOT codellama:7b
        mock_installed = [{"name": "llama2:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Should fallback to installed model, not use the unavailable preference
            assert selection.model == "llama2:7b"
            assert selection.model != "codellama:7b"

    @pytest.mark.asyncio
    async def test_e2e_router_uses_preference_if_installed(self, router):
        """
        E2E: Router uses user's preference when it IS installed
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "codellama:7b",
            }
        }

        # codellama:7b IS installed
        mock_installed = [{"name": "codellama:7b"}, {"name": "llama2:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Should use the preference since it's installed
            assert selection.model == "codellama:7b"

    @pytest.mark.asyncio
    async def test_e2e_language_specific_preference_validated(self, router):
        """
        E2E: Language-specific preferences are validated against installed models
        """
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_language": {
                    "fr": "mistral:7b",  # User wants mistral for French
                }
            }
        }

        # Mistral NOT installed, only llama2:7b
        mock_installed = [{"name": "llama2:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="fr",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Should fallback because mistral:7b is not installed
            assert selection.model == "llama2:7b"
            assert selection.model != "mistral:7b"

    @pytest.mark.asyncio
    async def test_e2e_use_case_preference_validated(self, router):
        """
        E2E: Use-case preferences are validated against installed models
        """
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b",  # User wants codellama for technical
                }
            }
        }

        # Only neural-chat installed
        mock_installed = [{"name": "neural-chat:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="technical",
                user_preferences=user_preferences,
            )

            # Should fallback to installed model
            assert selection.model == "neural-chat:7b"
            assert selection.model != "codellama:7b"

    @pytest.mark.asyncio
    async def test_e2e_user_preference_validated_then_capability_selection(
        self, router
    ):
        """
        E2E: Phase 5 - User preferences validated, then capability-based auto-selection
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",  # NOT installed
                "ollama_model_by_language": {"en": "neural-chat:7b"},  # Priority 2
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b"
                },  # Priority 1, NOT installed
            }
        }

        # Only neural-chat and mistral installed
        # Preference codellama:7b is NOT installed
        mock_installed = [{"name": "neural-chat:7b"}, {"name": "mistral:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="technical",
                user_preferences=user_preferences,
            )

            # Phase 5: User preference (codellama:7b) not installed, falls back to capability-based
            # Should select from installed models based on capabilities
            # Either neural-chat or mistral is acceptable (both installed)
            assert selection.model in ["neural-chat:7b", "mistral:7b"]

            # Verify it's one of the installed models
            installed_names = [m["name"] for m in mock_installed]
            assert selection.model in installed_names

    @pytest.mark.asyncio
    async def test_e2e_complete_fallback_chain(self, router):
        """
        E2E: Test complete fallback chain when all preferences are unavailable
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",  # NOT installed
                "ollama_model_by_language": {"en": "neural-chat:7b"},  # NOT installed
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b"
                },  # NOT installed
            }
        }

        # Only mistral:7b is installed
        mock_installed = [{"name": "mistral:7b"}]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="technical",
                user_preferences=user_preferences,
            )

            # Should fallback all the way to auto-selection from installed
            assert selection.model == "mistral:7b"
