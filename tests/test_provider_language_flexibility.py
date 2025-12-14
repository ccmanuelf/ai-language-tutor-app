"""
Test AI Provider Language Flexibility

Verifies that ALL AI providers (Mistral, Claude, DeepSeek, Ollama) can be
selected for ANY language, regardless of default priority settings.

This ensures user choice is always respected - users can select any provider
for any language they want to learn.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_router import EnhancedAIRouter, ProviderSelection


class TestProviderLanguageFlexibility:
    """Test that all providers can be used with all languages"""

    @pytest.fixture
    def router(self):
        """Create router with all providers registered"""
        router = EnhancedAIRouter()

        # Register all providers with mocked services
        for provider in ["mistral", "claude", "deepseek", "ollama"]:
            mock_service = MagicMock()
            mock_service.get_health_status = AsyncMock(
                return_value={"status": "available", "available": True}
            )
            router.register_provider(provider, mock_service)

        return router

    @pytest.fixture
    def all_languages(self):
        """All supported language codes"""
        return [
            "en",  # English
            "fr",  # French
            "zh",  # Chinese
            "zh-cn",  # Simplified Chinese
            "zh-tw",  # Traditional Chinese
            "es",  # Spanish
            "de",  # German
            "it",  # Italian
            "pt",  # Portuguese
            "ja",  # Japanese
            "ko",  # Korean
        ]

    @pytest.fixture
    def all_providers(self):
        """All supported AI providers"""
        return ["mistral", "claude", "deepseek", "ollama"]

    @pytest.mark.asyncio
    async def test_mistral_works_with_all_languages(self, router, all_languages):
        """Test Mistral can be selected for all languages"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.001
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="mistral-small-latest"
            ) as mock_model,
        ):
            # Mock budget status - plenty of budget
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=5.0
            )

            for language in all_languages:
                selection = await router.select_provider(
                    language=language,
                    use_case="conversation",
                    preferred_provider="mistral",  # User explicitly chose Mistral
                    enforce_budget=True,
                )

                assert selection.provider_name == "mistral", (
                    f"Mistral should be selectable for {language}"
                )
                assert selection.service is not None
                assert selection.model == "mistral-small-latest"
                assert "preference" in selection.reason.lower()

    @pytest.mark.asyncio
    async def test_claude_works_with_all_languages(self, router, all_languages):
        """Test Claude can be selected for all languages"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.002
            ) as mock_cost,
            patch.object(
                router,
                "_get_model_for_provider",
                return_value="claude-3-5-sonnet-20241022",
            ) as mock_model,
        ):
            # Mock budget status - plenty of budget
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=10.0
            )

            for language in all_languages:
                selection = await router.select_provider(
                    language=language,
                    use_case="conversation",
                    preferred_provider="claude",  # User explicitly chose Claude
                    enforce_budget=True,
                )

                assert selection.provider_name == "claude", (
                    f"Claude should be selectable for {language}"
                )
                assert selection.service is not None
                assert selection.model == "claude-3-5-sonnet-20241022"
                assert "preference" in selection.reason.lower()

    @pytest.mark.asyncio
    async def test_deepseek_works_with_all_languages(self, router, all_languages):
        """Test DeepSeek can be selected for all languages (not just Chinese)"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.0005
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="deepseek-chat"
            ) as mock_model,
        ):
            # Mock budget status - plenty of budget
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=2.0
            )

            for language in all_languages:
                selection = await router.select_provider(
                    language=language,
                    use_case="conversation",
                    preferred_provider="deepseek",  # User explicitly chose DeepSeek
                    enforce_budget=True,
                )

                assert selection.provider_name == "deepseek", (
                    f"DeepSeek should be selectable for {language} (not just Chinese)"
                )
                assert selection.service is not None
                assert selection.model == "deepseek-chat"
                assert "preference" in selection.reason.lower()

    @pytest.mark.asyncio
    async def test_ollama_works_with_all_languages(self, router, all_languages):
        """Test Ollama can be selected for all languages"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.0
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="neural-chat:7b"
            ) as mock_model,
        ):
            # Mock budget status
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=0.0
            )

            for language in all_languages:
                selection = await router.select_provider(
                    language=language,
                    use_case="conversation",
                    preferred_provider="ollama",  # User explicitly chose Ollama
                    enforce_budget=True,
                )

                assert selection.provider_name == "ollama", (
                    f"Ollama should be selectable for {language}"
                )
                assert selection.service is not None
                assert selection.model == "neural-chat:7b"
                assert "preference" in selection.reason.lower()

    @pytest.mark.asyncio
    async def test_all_providers_work_with_chinese(self, router, all_providers):
        """Test ALL providers work with Chinese (not just DeepSeek priority)"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.001
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="test-model"
            ) as mock_model,
        ):
            # Mock budget status
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=5.0
            )

            for provider in all_providers:
                selection = await router.select_provider(
                    language="zh",  # Chinese
                    use_case="conversation",
                    preferred_provider=provider,  # User's explicit choice
                    enforce_budget=True,
                )

                assert selection.provider_name == provider, (
                    f"{provider} should be selectable for Chinese (user choice matters)"
                )
                assert selection.service is not None

    @pytest.mark.asyncio
    async def test_all_providers_work_with_french(self, router, all_providers):
        """Test ALL providers work with French (not just Mistral priority)"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.001
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="test-model"
            ) as mock_model,
        ):
            # Mock budget status
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=5.0
            )

            for provider in all_providers:
                selection = await router.select_provider(
                    language="fr",  # French
                    use_case="conversation",
                    preferred_provider=provider,  # User's explicit choice
                    enforce_budget=True,
                )

                assert selection.provider_name == provider, (
                    f"{provider} should be selectable for French (user choice matters)"
                )
                assert selection.service is not None

    @pytest.mark.asyncio
    async def test_provider_selection_ignores_language_priorities(self, router):
        """Test that explicit provider choice OVERRIDES language priority defaults"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.001
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="test-model"
            ) as mock_model,
        ):
            # Mock budget status
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=5.0
            )

            # English default priority: mistral, claude, ollama
            # But user wants DeepSeek - should still get DeepSeek
            selection = await router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="deepseek",  # Not in English priority list!
                enforce_budget=True,
            )

            assert selection.provider_name == "deepseek", (
                "User's explicit choice should override language priorities"
            )

    @pytest.mark.asyncio
    async def test_user_can_override_chinese_deepseek_default(self, router):
        """Test user can choose Mistral/Claude/Ollama for Chinese (not forced to DeepSeek)"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.001
            ) as mock_cost,
            patch.object(
                router, "_get_model_for_provider", return_value="test-model"
            ) as mock_model,
        ):
            # Mock budget status
            mock_budget.return_value = MagicMock(
                remaining_budget=10.0, percentage_used=5.0
            )

            # Chinese default priority: deepseek, mistral, claude, ollama
            # But user wants Mistral - should get Mistral
            selection = await router.select_provider(
                language="zh",
                use_case="conversation",
                preferred_provider="mistral",  # Override DeepSeek default
                enforce_budget=True,
            )

            assert selection.provider_name == "mistral", (
                "User should be able to choose Mistral for Chinese (not forced to DeepSeek)"
            )

    @pytest.mark.asyncio
    async def test_budget_warning_still_allows_user_choice(self, router):
        """Test that budget exceeded shows WARNING but still allows user's provider choice"""
        with (
            patch.object(router, "check_budget_status") as mock_budget,
            patch.object(
                router, "_estimate_request_cost", return_value=0.50
            ) as mock_cost,
            patch.object(
                router,
                "_get_model_for_provider",
                return_value="claude-3-5-sonnet-20241022",
            ) as mock_model,
        ):
            # Mock budget status - EXCEEDED
            mock_budget.return_value = MagicMock(
                remaining_budget=0.01,  # Only 1 cent left
                percentage_used=99.5,  # 99.5% used
            )

            # User wants Claude despite budget exceeded
            selection = await router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="claude",
                enforce_budget=True,
                user_preferences={
                    "ai_provider_settings": {
                        "auto_fallback_to_ollama": False  # Don't auto-fallback
                    }
                },
            )

            # Should STILL get Claude (with warning)
            assert selection.provider_name == "claude", (
                "Budget exceeded should show warning but allow user's choice"
            )
            assert selection.requires_budget_override is True
            assert selection.budget_warning is not None
