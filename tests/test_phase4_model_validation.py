"""
Phase 4 Tests - Model Validation Against Installed Models

Critical tests ensuring the router only uses models that are actually installed.
This prevents the hardcoded model selection bug identified by the user.

Session 98 - Phase 4
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_router import EnhancedAIRouter
from app.services.ollama_service import OllamaService


class TestPhase4ModelValidation:
    """Tests for Phase 4 installed model validation"""

    @pytest.fixture
    def router(self):
        """Create router instance"""
        return EnhancedAIRouter()

    @pytest.mark.asyncio
    async def test_preferred_model_not_installed_falls_back(self, router):
        """
        CRITICAL: User specifies llama2:13b but only llama2:7b is installed.
        System should detect this and fall back to installed model.
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",  # NOT installed
            }
        }

        mock_installed = [
            {"name": "llama2:7b"},  # Only this is installed
            {"name": "mistral:7b"},
        ]

        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail, patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list, patch.object(
            OllamaService, "get_recommended_model", return_value="llama2:7b"
        ) as mock_recommend:
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        # Should NOT use llama2:13b (not installed)
        assert selection.model != "llama2:13b"
        # Should use llama2:7b (is installed)
        assert selection.model == "llama2:7b"
        # Should have called get_recommended_model with installed_models
        mock_recommend.assert_called_once()
        call_args = mock_recommend.call_args
        assert call_args[1]["installed_models"] == mock_installed

    @pytest.mark.asyncio
    async def test_language_specific_model_not_installed_falls_back(self, router):
        """
        User sets French → mistral:7b but mistral is not installed.
        Should fall back to auto-selection from installed models.
        """
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_language": {
                    "fr": "mistral:7b",  # NOT installed
                }
            }
        }

        mock_installed = [
            {"name": "llama2:7b"},  # Only llama2 installed
        ]

        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail, patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list, patch.object(
            OllamaService, "get_recommended_model", return_value="llama2:7b"
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="fr",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        # Should use llama2:7b (the only installed model)
        assert selection.model == "llama2:7b"

    @pytest.mark.asyncio
    async def test_use_case_model_not_installed_falls_back(self, router):
        """
        User sets technical → codellama:7b but codellama not installed.
        Should fall back to installed models.
        """
        user_preferences = {
            "ai_provider_settings": {
                "ollama_model_by_use_case": {
                    "technical": "codellama:7b",  # NOT installed
                }
            }
        }

        mock_installed = [
            {"name": "neural-chat:7b"},
            {"name": "llama2:7b"},
        ]

        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail, patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list, patch.object(
            OllamaService, "get_recommended_model", return_value="neural-chat:7b"
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="technical",
                user_preferences=user_preferences,
            )

        # Should NOT use codellama:7b (not installed)
        assert selection.model != "codellama:7b"
        # Should use one of the installed models
        assert selection.model in ["neural-chat:7b", "llama2:7b"]

    @pytest.mark.asyncio
    async def test_preferred_model_is_installed_uses_it(self, router):
        """
        User specifies llama2:13b AND it's installed.
        Should use it without fallback.
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "llama2:13b",
            }
        }

        mock_installed = [
            {"name": "llama2:7b"},
            {"name": "llama2:13b"},  # IS installed
            {"name": "mistral:7b"},
        ]

        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail, patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list:
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            selection = await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

        # Should use llama2:13b (user preference AND installed)
        assert selection.model == "llama2:13b"

    @pytest.mark.asyncio
    async def test_get_recommended_model_only_returns_installed(self, router):
        """
        Test OllamaService.get_recommended_model only returns installed models.
        """
        mock_installed = [
            {"name": "llama2:7b"},  # Only llama2:7b installed
        ]

        service = OllamaService()
        
        # Request neural-chat (preferred for English), but only llama2 installed
        recommended = service.get_recommended_model(
            language="en",
            use_case="conversation",
            installed_models=mock_installed
        )

        # Should return llama2:7b (installed), NOT neural-chat:7b (not installed)
        assert recommended == "llama2:7b"

    @pytest.mark.asyncio
    async def test_get_recommended_model_technical_use_case_installed(self, router):
        """
        Test use-case specific model selection from installed models.
        """
        mock_installed = [
            {"name": "codellama:7b"},  # Code model installed
            {"name": "llama2:7b"},
        ]

        service = OllamaService()
        
        recommended = service.get_recommended_model(
            language="en",
            use_case="technical",
            installed_models=mock_installed
        )

        # Should recommend codellama:7b (use-case match + installed)
        assert recommended == "codellama:7b"

    @pytest.mark.asyncio
    async def test_get_recommended_model_no_preferred_returns_first_installed(self, router):
        """
        When no preferred models are installed, return first available.
        """
        mock_installed = [
            {"name": "custom-model:latest"},  # Not in any preference list
            {"name": "another-model:v1"},
        ]

        service = OllamaService()
        
        recommended = service.get_recommended_model(
            language="en",
            use_case="conversation",
            installed_models=mock_installed
        )

        # Should return first installed model (custom-model:latest)
        assert recommended == "custom-model:latest"

    @pytest.mark.asyncio
    async def test_router_logs_warning_when_preferred_not_installed(self, router):
        """
        Router should log warning when user's preference isn't installed.
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "nonexistent:model",
            }
        }

        mock_installed = [{"name": "llama2:7b"}]

        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail, patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list, patch.object(
            OllamaService, "get_recommended_model", return_value="llama2:7b"
        ), patch("app.services.ai_router.logger") as mock_logger:
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            await router._select_local_provider(
                language="en",
                reason="user_preference",
                use_case="conversation",
                user_preferences=user_preferences,
            )

            # Should have logged warning about nonexistent model
            mock_logger.warning.assert_called()
            warning_msg = str(mock_logger.warning.call_args)
            assert "nonexistent:model" in warning_msg
            assert "not installed" in warning_msg.lower()

    @pytest.mark.asyncio
    async def test_empty_installed_models_handled_gracefully(self, router):
        """
        If no models are installed, should handle gracefully.
        """
        mock_installed = []  # No models installed

        service = OllamaService()
        
        # Should return fallback (won't work, but shouldn't crash)
        recommended = service.get_recommended_model(
            language="en",
            use_case="conversation",
            installed_models=mock_installed
        )

        # Should return something (llama2:7b fallback)
        assert recommended is not None
        assert isinstance(recommended, str)

    @pytest.mark.asyncio
    async def test_all_three_preference_types_validated(self, router):
        """
        Test that all three preference types are validated against installed models.
        """
        user_preferences = {
            "ai_provider_settings": {
                "preferred_ollama_model": "not-installed:1",
                "ollama_model_by_language": {
                    "en": "not-installed:2",
                },
                "ollama_model_by_use_case": {
                    "technical": "not-installed:3",
                },
            }
        }

        mock_installed = [
            {"name": "llama2:7b"},  # Only this installed
        ]

        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail, patch.object(
            OllamaService, "list_models", new_callable=AsyncMock
        ) as mock_list, patch.object(
            OllamaService, "get_recommended_model", return_value="llama2:7b"
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_installed

            # Test general preference
            sel1 = await router._select_local_provider(
                "de", "user_preference", "conversation", user_preferences
            )
            
            # Test language preference
            sel2 = await router._select_local_provider(
                "en", "user_preference", "conversation", user_preferences
            )
            
            # Test use-case preference
            sel3 = await router._select_local_provider(
                "en", "user_preference", "technical", user_preferences
            )

        # All should fall back to llama2:7b (the only installed model)
        assert sel1.model == "llama2:7b"
        assert sel2.model == "llama2:7b"
        assert sel3.model == "llama2:7b"
