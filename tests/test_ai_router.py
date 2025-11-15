"""
Comprehensive tests for AI Router - Achieves 100% coverage
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.ai_router import (
    EnhancedAIRouter,
    FallbackReason,
    ProviderSelection,
    RouterMode,
    ai_router,
    generate_ai_response,
    generate_streaming_ai_response,
    get_ai_router_status,
    register_ai_provider,
)
from app.services.ai_service_base import AIResponse, AIResponseStatus, StreamingResponse
from app.services.budget_manager import BudgetAlert, BudgetStatus


class TestRouterInitialization:
    def test_router_initialization(self):
        """Test router initializes with correct defaults"""
        router = EnhancedAIRouter()
        assert router.router_mode == RouterMode.HYBRID
        assert router.fallback_enabled is True
        assert len(router.language_preferences) > 0
        assert "en" in router.language_preferences
        assert "fr" in router.language_preferences
        assert "zh" in router.language_preferences

    def test_language_preferences_initialized(self):
        """Test language preferences are properly initialized"""
        router = EnhancedAIRouter()
        # English preferences
        assert "claude" in router.language_preferences["en"]
        assert "ollama" in router.language_preferences["en"]
        # French preferences
        assert "mistral" in router.language_preferences["fr"]
        # Chinese preferences
        assert "deepseek" in router.language_preferences["zh"]


class TestProviderRegistration:
    def test_register_provider(self):
        """Test registering a new provider"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        router.register_provider("test_provider", mock_service)
        assert "test_provider" in router.providers
        assert router.providers["test_provider"] == mock_service


class TestProviderHealthCheck:
    @pytest.mark.asyncio
    async def test_check_provider_health_not_registered(self):
        """Test health check for unregistered provider"""
        router = EnhancedAIRouter()
        health = await router.check_provider_health("nonexistent")
        assert health["status"] == "not_registered"
        assert health["available"] is False

    @pytest.mark.asyncio
    async def test_check_provider_health_success(self):
        """Test successful health check"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        router.register_provider("test", mock_service)
        health = await router.check_provider_health("test")
        assert health["status"] == "healthy"
        assert health["available"] is True

    @pytest.mark.asyncio
    async def test_check_provider_health_cached(self):
        """Test health check uses cache within 5 minutes"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        call_count = 0

        async def mock_health():
            nonlocal call_count
            call_count += 1
            return {"status": "healthy", "available": True}

        mock_service.get_health_status = mock_health
        router.register_provider("test", mock_service)

        # First call
        health1 = await router.check_provider_health("test")
        # Second call should use cache
        health2 = await router.check_provider_health("test")

        assert call_count == 1  # Only called once due to caching
        assert health1["status"] == "healthy"
        assert health2["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_check_provider_health_no_method(self):
        """Test health check for provider without get_health_status method"""
        router = EnhancedAIRouter()
        mock_service = Mock(spec=[])  # No get_health_status method
        router.register_provider("test", mock_service)
        health = await router.check_provider_health("test")
        assert health["status"] == "available"
        assert health["available"] is True

    @pytest.mark.asyncio
    async def test_check_provider_health_error(self):
        """Test health check error handling"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        router.register_provider("test", mock_service)
        health = await router.check_provider_health("test")
        assert health["status"] == "error"
        assert health["available"] is False
        assert "error" in health


class TestBudgetChecks:
    @pytest.mark.asyncio
    async def test_check_budget_status(self):
        """Test budget status checking"""
        router = EnhancedAIRouter()
        with patch(
            "app.services.ai_router.budget_manager.get_current_budget_status"
        ) as mock_get:
            mock_get.return_value = BudgetStatus(
                total_budget=30.0,
                used_budget=5.0,
                remaining_budget=25.0,
                percentage_used=16.67,
                alert_level=BudgetAlert.GREEN,
                days_remaining=20,
                projected_monthly_cost=7.5,
                is_over_budget=False,
            )
            status = await router.check_budget_status()
            assert status.remaining_budget == 25.0
            assert status.alert_level == BudgetAlert.GREEN

    def test_should_use_local_only_force(self):
        """Test force local mode"""
        router = EnhancedAIRouter()
        assert router._should_use_local_only(True, None) is True
        assert router._should_use_local_only(True, {}) is True

    def test_should_use_local_only_preferences(self):
        """Test local mode from user preferences"""
        router = EnhancedAIRouter()
        assert router._should_use_local_only(False, {"local_only": True}) is True

    def test_should_use_local_only_false(self):
        """Test when local mode is not requested"""
        router = EnhancedAIRouter()
        assert router._should_use_local_only(False, {}) is False
        assert router._should_use_local_only(False, None) is False

    def test_should_use_budget_fallback_critical(self):
        """Test budget fallback on critical alert"""
        router = EnhancedAIRouter()
        budget_status = Mock(alert_level=BudgetAlert.CRITICAL)
        assert router._should_use_budget_fallback(budget_status) is True

    def test_should_use_budget_fallback_red(self):
        """Test budget fallback on red alert"""
        router = EnhancedAIRouter()
        budget_status = Mock(alert_level=BudgetAlert.RED)
        assert router._should_use_budget_fallback(budget_status) is True

    def test_should_use_budget_fallback_green(self):
        """Test no budget fallback on green alert"""
        router = EnhancedAIRouter()
        budget_status = Mock(alert_level=BudgetAlert.GREEN)
        assert router._should_use_budget_fallback(budget_status) is False


class TestProviderSelection:
    def test_get_cloud_providers_english(self):
        """Test getting cloud providers for English"""
        router = EnhancedAIRouter()
        providers = router._get_cloud_providers("en")
        assert "ollama" not in providers
        assert "claude" in providers

    def test_get_cloud_providers_french(self):
        """Test getting cloud providers for French"""
        router = EnhancedAIRouter()
        providers = router._get_cloud_providers("fr")
        assert "ollama" not in providers
        assert "mistral" in providers

    def test_get_cloud_providers_chinese(self):
        """Test getting cloud providers for Chinese"""
        router = EnhancedAIRouter()
        providers = router._get_cloud_providers("zh")
        assert "ollama" not in providers
        assert "deepseek" in providers

    def test_get_model_for_provider_claude(self):
        """Test getting model for Claude provider"""
        router = EnhancedAIRouter()
        model = router._get_model_for_provider("claude", "en")
        assert "claude" in model.lower()
        assert "haiku" in model.lower()

    def test_get_model_for_provider_mistral(self):
        """Test getting model for Mistral provider"""
        router = EnhancedAIRouter()
        model = router._get_model_for_provider("mistral", "fr")
        assert "mistral" in model.lower()

    def test_get_model_for_provider_qwen(self):
        """Test getting model for Qwen provider"""
        router = EnhancedAIRouter()
        model = router._get_model_for_provider("qwen", "zh")
        assert model == "qwen-plus"

    def test_get_model_for_provider_ollama(self):
        """Test getting model for Ollama provider"""
        router = EnhancedAIRouter()
        with patch(
            "app.services.ai_router.ollama_service.get_recommended_model"
        ) as mock_get:
            mock_get.return_value = "llama2:7b"
            model = router._get_model_for_provider("ollama", "en")
            assert model == "llama2:7b"

    def test_get_model_for_provider_unknown(self):
        """Test getting model for unknown provider"""
        router = EnhancedAIRouter()
        model = router._get_model_for_provider("unknown", "en")
        assert model == "default"

    @pytest.mark.asyncio
    async def test_try_cloud_provider_not_registered(self):
        """Test trying unregistered provider"""
        router = EnhancedAIRouter()
        budget_status = Mock(remaining_budget=10.0)
        result = await router._try_cloud_provider(
            "nonexistent", "en", "conversation", budget_status
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_try_cloud_provider_unhealthy(self):
        """Test trying unhealthy provider"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "unhealthy", "available": False}
        )
        router.register_provider("test", mock_service)
        budget_status = Mock(remaining_budget=10.0)
        result = await router._try_cloud_provider(
            "test", "en", "conversation", budget_status
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_try_cloud_provider_too_expensive(self):
        """Test trying provider when budget insufficient"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        router.register_provider("test", mock_service)
        budget_status = Mock(remaining_budget=0.001)  # Very low budget

        with patch.object(router, "_estimate_request_cost", return_value=1.0):
            result = await router._try_cloud_provider(
                "test", "en", "conversation", budget_status
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_try_cloud_provider_success(self):
        """Test successfully selecting cloud provider"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        router.register_provider("test", mock_service)
        budget_status = Mock(remaining_budget=10.0)

        with patch.object(router, "_estimate_request_cost", return_value=0.01):
            result = await router._try_cloud_provider(
                "test", "en", "conversation", budget_status
            )

        assert result is not None
        assert result.provider_name == "test"
        assert result.is_fallback is False

    @pytest.mark.asyncio
    async def test_try_cloud_provider_error(self):
        """Test error handling in cloud provider selection"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            side_effect=Exception("Network error")
        )
        router.register_provider("test", mock_service)
        budget_status = Mock(remaining_budget=10.0)

        result = await router._try_cloud_provider(
            "test", "en", "conversation", budget_status
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_select_best_cloud_provider_success(self):
        """Test selecting best cloud provider from list"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        router.register_provider("test", mock_service)
        budget_status = Mock(remaining_budget=10.0)

        with patch.object(router, "_estimate_request_cost", return_value=0.01):
            result = await router._select_best_cloud_provider(
                ["test"], "en", "conversation", budget_status
            )

        assert result is not None
        assert result.provider_name == "test"

    @pytest.mark.asyncio
    async def test_select_best_cloud_provider_none_available(self):
        """Test when no cloud providers are available"""
        router = EnhancedAIRouter()
        budget_status = Mock(remaining_budget=10.0)

        result = await router._select_best_cloud_provider(
            ["nonexistent"], "en", "conversation", budget_status
        )

        assert result is None


class TestLocalProviderSelection:
    @pytest.mark.asyncio
    async def test_select_local_provider_success(self):
        """Test selecting local Ollama provider"""
        router = EnhancedAIRouter()

        with patch(
            "app.services.ai_router.ollama_service.check_availability"
        ) as mock_check:
            with patch(
                "app.services.ai_router.ollama_service.get_recommended_model"
            ) as mock_model:
                mock_check.return_value = True
                mock_model.return_value = "llama2:7b"

                result = await router._select_local_provider("en", "budget_exceeded")

        assert result.provider_name == "ollama"
        assert result.is_fallback is True
        assert result.cost_estimate == 0.0
        assert result.fallback_reason == FallbackReason("budget_exceeded")

    @pytest.mark.asyncio
    async def test_select_local_provider_unavailable(self):
        """Test error when Ollama is unavailable"""
        router = EnhancedAIRouter()

        with patch(
            "app.services.ai_router.ollama_service.check_availability"
        ) as mock_check:
            mock_check.return_value = False

            with pytest.raises(Exception) as exc_info:
                await router._select_local_provider("en", "budget_exceeded")

            assert "No AI providers available" in str(exc_info.value)


class TestSelectProvider:
    @pytest.mark.asyncio
    async def test_select_provider_force_local(self):
        """Test forcing local provider selection"""
        router = EnhancedAIRouter()

        with patch(
            "app.services.ai_router.ollama_service.check_availability"
        ) as mock_check:
            with patch(
                "app.services.ai_router.ollama_service.get_recommended_model"
            ) as mock_model:
                mock_check.return_value = True
                mock_model.return_value = "llama2:7b"

                result = await router.select_provider(force_local=True)

        assert result.provider_name == "ollama"
        assert result.is_fallback is True

    @pytest.mark.asyncio
    async def test_select_provider_user_preference_local(self):
        """Test local provider from user preferences"""
        router = EnhancedAIRouter()

        with patch(
            "app.services.ai_router.ollama_service.check_availability"
        ) as mock_check:
            with patch(
                "app.services.ai_router.ollama_service.get_recommended_model"
            ) as mock_model:
                mock_check.return_value = True
                mock_model.return_value = "llama2:7b"

                result = await router.select_provider(
                    user_preferences={"local_only": True}
                )

        assert result.provider_name == "ollama"

    @pytest.mark.asyncio
    async def test_select_provider_budget_exceeded(self):
        """Test fallback when budget exceeded"""
        router = EnhancedAIRouter()

        with patch(
            "app.services.ai_router.budget_manager.get_current_budget_status"
        ) as mock_budget:
            with patch(
                "app.services.ai_router.ollama_service.check_availability"
            ) as mock_check:
                with patch(
                    "app.services.ai_router.ollama_service.get_recommended_model"
                ) as mock_model:
                    mock_budget.return_value = BudgetStatus(
                        total_budget=30.0,
                        used_budget=28.0,
                        remaining_budget=2.0,
                        percentage_used=93.33,
                        alert_level=BudgetAlert.RED,
                        days_remaining=5,
                        projected_monthly_cost=35.0,
                        is_over_budget=False,
                    )
                    mock_check.return_value = True
                    mock_model.return_value = "llama2:7b"

                    result = await router.select_provider()

        assert result.provider_name == "ollama"
        assert result.fallback_reason == FallbackReason("budget_exceeded")

    @pytest.mark.asyncio
    async def test_select_provider_cloud_success(self):
        """Test successful cloud provider selection"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        router.register_provider("claude", mock_service)

        with patch(
            "app.services.ai_router.budget_manager.get_current_budget_status"
        ) as mock_budget:
            with patch.object(router, "_estimate_request_cost", return_value=0.01):
                mock_budget.return_value = BudgetStatus(
                    total_budget=30.0,
                    used_budget=5.0,
                    remaining_budget=25.0,
                    percentage_used=16.67,
                    alert_level=BudgetAlert.GREEN,
                    days_remaining=20,
                    projected_monthly_cost=7.5,
                    is_over_budget=False,
                )

                result = await router.select_provider(language="en")

        assert result.provider_name == "claude"
        assert result.is_fallback is False

    @pytest.mark.asyncio
    async def test_select_provider_fallback_on_failure(self):
        """Test fallback to local when cloud providers fail"""
        router = EnhancedAIRouter()

        with patch(
            "app.services.ai_router.budget_manager.get_current_budget_status"
        ) as mock_budget:
            with patch(
                "app.services.ai_router.ollama_service.check_availability"
            ) as mock_check:
                with patch(
                    "app.services.ai_router.ollama_service.get_recommended_model"
                ) as mock_model:
                    mock_budget.return_value = BudgetStatus(
                        total_budget=30.0,
                        used_budget=5.0,
                        remaining_budget=25.0,
                        percentage_used=16.67,
                        alert_level=BudgetAlert.GREEN,
                        days_remaining=20,
                        projected_monthly_cost=7.5,
                        is_over_budget=False,
                    )
                    mock_check.return_value = True
                    mock_model.return_value = "llama2:7b"

                    # No providers registered, should fall back
                    result = await router.select_provider()

        assert result.provider_name == "ollama"
        assert result.fallback_reason == FallbackReason("api_unavailable")


class TestCostEstimation:
    @pytest.mark.asyncio
    async def test_estimate_request_cost_ollama(self):
        """Test cost estimation for free Ollama service"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.cost_per_token_input = 0.0
        mock_service.cost_per_token_output = 0.0
        router.register_provider("ollama", mock_service)

        cost = await router._estimate_request_cost("ollama", "en", "conversation")
        assert cost == 0.0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_claude(self):
        """Test cost estimation for Claude service"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.cost_per_token_input = 0.00001
        mock_service.cost_per_token_output = 0.00003
        router.register_provider("claude", mock_service)

        cost = await router._estimate_request_cost("claude", "en", "conversation")
        assert cost > 0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_translation(self):
        """Test cost estimation for translation use case"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.cost_per_token_input = 0.00001
        mock_service.cost_per_token_output = 0.00003
        router.register_provider("test", mock_service)

        cost = await router._estimate_request_cost("test", "en", "translation")
        assert cost > 0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_complex(self):
        """Test cost estimation for complex use cases"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.cost_per_token_input = 0.00001
        mock_service.cost_per_token_output = 0.00003
        router.register_provider("test", mock_service)

        cost = await router._estimate_request_cost("test", "en", "analysis")
        assert cost > 0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_unregistered(self):
        """Test cost estimation for unregistered provider"""
        router = EnhancedAIRouter()
        cost = await router._estimate_request_cost("nonexistent", "en", "conversation")
        assert cost == 0.0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_no_pricing(self):
        """Test cost estimation when provider has no pricing info"""
        router = EnhancedAIRouter()
        mock_service = Mock(spec=[])  # No cost attributes
        router.register_provider("test", mock_service)

        cost = await router._estimate_request_cost("test", "en", "conversation")
        assert cost == 0.0


class TestSortProvidersByCost:
    @pytest.mark.asyncio
    async def test_sort_providers_low_budget(self):
        """Test provider sorting with low budget"""
        router = EnhancedAIRouter()
        budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=25.0,
            remaining_budget=5.0,
            percentage_used=83.33,
            alert_level=BudgetAlert.ORANGE,
            days_remaining=10,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )

        providers = ["claude", "mistral", "deepseek"]
        sorted_providers = await router._sort_providers_by_cost_efficiency(
            providers, "en", "conversation", budget_status
        )

        # With low budget, cheapest (deepseek) should be first
        assert sorted_providers[0] == "deepseek"

    @pytest.mark.asyncio
    async def test_sort_providers_simple_use_case(self):
        """Test provider sorting for simple use cases"""
        router = EnhancedAIRouter()
        budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=5.0,
            remaining_budget=25.0,
            percentage_used=16.67,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=7.5,
            is_over_budget=False,
        )

        providers = ["claude", "mistral", "deepseek"]
        sorted_providers = await router._sort_providers_by_cost_efficiency(
            providers, "en", "conversation", budget_status
        )

        # Simple use case should prefer cost efficiency
        assert "deepseek" in sorted_providers[:2]  # Cheapest should be near front

    @pytest.mark.asyncio
    async def test_sort_providers_complex_use_case(self):
        """Test provider sorting for complex use cases"""
        router = EnhancedAIRouter()
        budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=5.0,
            remaining_budget=25.0,
            percentage_used=16.67,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=7.5,
            is_over_budget=False,
        )

        providers = ["claude", "mistral", "deepseek"]
        sorted_providers = await router._sort_providers_by_cost_efficiency(
            providers, "en", "analysis", budget_status
        )

        # Complex use case should prefer quality
        assert "claude" in sorted_providers[:2]  # Best quality should be near front

    @pytest.mark.asyncio
    async def test_sort_providers_unknown(self):
        """Test sorting with unknown provider"""
        router = EnhancedAIRouter()
        budget_status = Mock(remaining_budget=25.0)

        providers = ["claude", "unknown_provider"]
        sorted_providers = await router._sort_providers_by_cost_efficiency(
            providers, "en", "conversation", budget_status
        )

        # Unknown provider should be last
        assert sorted_providers[-1] == "unknown_provider"


class TestGenerateResponse:
    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_response = AIResponse(
            content="Test response",
            model="test-model",
            provider="test",
            language="en",
            processing_time=1.0,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
        )
        mock_service.generate_response = AsyncMock(return_value=mock_response)

        selection = ProviderSelection(
            "test", mock_service, "test-model", "reason", 0.9, 0.01, False
        )

        with patch.object(router, "select_provider", return_value=selection):
            with patch(
                "app.services.ai_router.budget_manager.track_usage"
            ) as mock_track:
                result = await router.generate_response(
                    [{"role": "user", "content": "Test"}], "en"
                )

        assert result.content == "Test response"
        assert "router_selection" in result.metadata

    @pytest.mark.asyncio
    async def test_generate_response_with_fallback(self):
        """Test response generation with fallback attempt"""
        router = EnhancedAIRouter()

        call_count = 0

        async def mock_select_provider(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt failed")
            # Second attempt with force_local
            mock_service = Mock()
            mock_service.generate_response = AsyncMock(
                return_value=AIResponse(
                    "Fallback response",
                    "llama2",
                    "ollama",
                    "en",
                    1.0,
                    0.0,
                    AIResponseStatus.SUCCESS,
                )
            )
            return ProviderSelection(
                "ollama",
                mock_service,
                "llama2",
                "fallback",
                0.7,
                0.0,
                True,
                FallbackReason.API_UNAVAILABLE,
            )

        with patch.object(router, "select_provider", side_effect=mock_select_provider):
            result = await router.generate_response(
                [{"role": "user", "content": "Test"}]
            )

        assert call_count == 2  # Called twice - original + fallback
        assert result.content == "Fallback response"

    @pytest.mark.asyncio
    async def test_generate_response_all_fail(self):
        """Test when all providers fail"""
        router = EnhancedAIRouter()

        with patch.object(
            router, "select_provider", side_effect=Exception("All failed")
        ):
            with pytest.raises(Exception) as exc_info:
                await router.generate_response([{"role": "user", "content": "Test"}])

            assert "All AI providers failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_response_local_no_cost_tracking(self):
        """Test that local responses don't track cost"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_response = AIResponse(
            "Local response",
            "llama2",
            "ollama",
            "en",
            1.0,
            0.0,
            AIResponseStatus.SUCCESS,
        )
        mock_service.generate_response = AsyncMock(return_value=mock_response)

        with patch.object(router, "select_provider") as mock_select:
            with patch(
                "app.services.ai_router.budget_manager.track_usage"
            ) as mock_track:
                mock_select.return_value = ProviderSelection(
                    "ollama",
                    mock_service,
                    "llama2",
                    "local",
                    0.7,
                    0.0,
                    True,
                    FallbackReason.USER_PREFERENCE,
                )

                await router.generate_response([{"role": "user", "content": "Test"}])

                # Should not track cost for fallback
                mock_track.assert_not_called()


class TestGenerateStreamingResponse:
    @pytest.mark.asyncio
    async def test_generate_streaming_response_supported(self):
        """Test streaming response with provider that supports it"""
        router = EnhancedAIRouter()
        mock_service = Mock()

        async def mock_stream(*args, **kwargs):
            yield StreamingResponse(
                "chunk1", "model", "test", "en", False, 0.5, 0.01, {}
            )
            yield StreamingResponse(
                "chunk2", "model", "test", "en", True, 1.0, 0.01, {}
            )

        mock_service.generate_streaming_response = mock_stream

        selection = ProviderSelection(
            "test", mock_service, "model", "reason", 0.9, 0.01, False
        )

        with patch.object(router, "select_provider", return_value=selection):
            chunks = []
            async for chunk in router.generate_streaming_response(
                [{"role": "user", "content": "Test"}], "en"
            ):
                chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0].content == "chunk1"
        assert chunks[1].is_final is True
        assert chunks[0].metadata["router_provider"] == "test"

    @pytest.mark.asyncio
    async def test_generate_streaming_response_not_supported(self):
        """Test streaming response with provider that doesn't support it"""
        router = EnhancedAIRouter()
        mock_service = Mock(spec=["generate_response"])
        mock_service.generate_response = AsyncMock(
            return_value=AIResponse(
                "Full response",
                "model",
                "test",
                "en",
                1.0,
                0.01,
                AIResponseStatus.SUCCESS,
                {},
            )
        )

        selection = ProviderSelection(
            "test", mock_service, "model", "reason", 0.9, 0.01, False
        )

        with patch.object(router, "select_provider", return_value=selection):
            chunks = []
            async for chunk in router.generate_streaming_response(
                [{"role": "user", "content": "Test"}], "en"
            ):
                chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].content == "Full response"
        assert chunks[0].metadata["converted_from_non_streaming"] is True

    @pytest.mark.asyncio
    async def test_generate_streaming_response_with_fallback(self):
        """Test streaming response with fallback on error"""
        router = EnhancedAIRouter()

        call_count = 0

        async def mock_select_provider(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and not kwargs.get("force_local"):
                raise Exception("First attempt failed")

            mock_service = Mock()

            async def mock_stream(*args, **kwargs):
                yield StreamingResponse(
                    "fallback", "llama2", "ollama", "en", True, 1.0, 0.0, {}
                )

            mock_service.generate_streaming_response = mock_stream
            return ProviderSelection(
                "ollama", mock_service, "llama2", "fallback", 0.7, 0.0, True
            )

        with patch.object(router, "select_provider", side_effect=mock_select_provider):
            chunks = []
            async for chunk in router.generate_streaming_response(
                [{"role": "user", "content": "Test"}]
            ):
                chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].content == "fallback"


class TestRouterModes:
    def test_set_router_mode_cost_optimized(self):
        """Test setting cost-optimized mode"""
        router = EnhancedAIRouter()
        router.set_router_mode(RouterMode.COST_OPTIMIZED)
        assert router.router_mode == RouterMode.COST_OPTIMIZED

    def test_set_router_mode_quality_optimized(self):
        """Test setting quality-optimized mode"""
        router = EnhancedAIRouter()
        router.set_router_mode(RouterMode.QUALITY_OPTIMIZED)
        assert router.router_mode == RouterMode.QUALITY_OPTIMIZED

    def test_enable_fallback_true(self):
        """Test enabling fallback"""
        router = EnhancedAIRouter()
        router.enable_fallback(True)
        assert router.fallback_enabled is True

    def test_enable_fallback_false(self):
        """Test disabling fallback"""
        router = EnhancedAIRouter()
        router.enable_fallback(False)
        assert router.fallback_enabled is False


class TestRouterStatus:
    @pytest.mark.asyncio
    async def test_get_router_status(self):
        """Test getting comprehensive router status"""
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )
        router.register_provider("test", mock_service)

        with patch(
            "app.services.ai_router.budget_manager.get_current_budget_status"
        ) as mock_budget:
            with patch(
                "app.services.ai_router.ollama_service.get_health_status"
            ) as mock_ollama:
                mock_budget.return_value = BudgetStatus(
                    30.0, 5.0, 25.0, 16.67, BudgetAlert.GREEN, 20, 7.5, False
                )
                mock_ollama.return_value = {"status": "healthy", "models_installed": 3}

                status = await router.get_router_status()

        assert "router_mode" in status
        assert "fallback_enabled" in status
        assert "budget_status" in status
        assert "providers" in status
        assert "fallback_status" in status
        assert status["fallback_status"]["ollama_available"] is True


class TestCaching:
    @pytest.mark.asyncio
    async def test_should_use_cache_short_conversation(self):
        """Test cache decision for short conversations"""
        router = EnhancedAIRouter()
        messages = []  # Empty
        result = await router._should_use_cache(messages, "en")
        assert result is False

    @pytest.mark.asyncio
    async def test_should_use_cache_long_conversation(self):
        """Test cache decision for long conversations"""
        router = EnhancedAIRouter()
        messages = [{"role": "user", "content": "msg"} for _ in range(15)]
        result = await router._should_use_cache(messages, "en")
        assert result is False

    @pytest.mark.asyncio
    async def test_should_use_cache_cacheable_pattern(self):
        """Test cache decision for cacheable patterns"""
        router = EnhancedAIRouter()
        messages = [{"role": "user", "content": "Hello, how are you?"}]
        result = await router._should_use_cache(messages, "en")
        assert result is True

    @pytest.mark.asyncio
    async def test_should_use_cache_non_cacheable(self):
        """Test cache decision for non-cacheable patterns"""
        router = EnhancedAIRouter()
        messages = [
            {
                "role": "user",
                "content": "Some complex unique query about quantum physics",
            }
        ]
        result = await router._should_use_cache(messages, "en")
        assert result is False


class TestLegacyCostEstimation:
    @pytest.mark.asyncio
    async def test_estimate_request_cost_legacy_claude(self):
        """Test legacy cost estimation for Claude"""
        router = EnhancedAIRouter()
        cost = await router._estimate_request_cost_legacy(
            "claude", "en", "conversation"
        )
        assert cost > 0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_legacy_ollama(self):
        """Test legacy cost estimation for Ollama"""
        router = EnhancedAIRouter()
        cost = await router._estimate_request_cost_legacy(
            "ollama", "en", "conversation"
        )
        assert cost == 0.0

    @pytest.mark.asyncio
    async def test_estimate_request_cost_legacy_use_cases(self):
        """Test legacy cost estimation for different use cases"""
        router = EnhancedAIRouter()
        grammar_cost = await router._estimate_request_cost_legacy(
            "claude", "en", "grammar"
        )
        conv_cost = await router._estimate_request_cost_legacy(
            "claude", "en", "conversation"
        )
        # Grammar should cost more than conversation
        assert grammar_cost > conv_cost


class TestGlobalInstance:
    def test_global_router_exists(self):
        """Test global router instance exists"""
        assert ai_router is not None
        assert isinstance(ai_router, EnhancedAIRouter)

    def test_global_router_has_providers(self):
        """Test global router has providers registered"""
        assert len(ai_router.providers) > 0
        assert "claude" in ai_router.providers
        assert "mistral" in ai_router.providers
        assert "deepseek" in ai_router.providers
        assert "ollama" in ai_router.providers


class TestConvenienceFunctions:
    @pytest.mark.asyncio
    async def test_generate_ai_response_cached(self):
        """Test convenience function with cached response"""
        with patch("app.services.ai_router.response_cache.get") as mock_get:
            mock_cached = Mock()
            mock_cached.content = "Cached response"
            mock_cached.provider = "claude"
            mock_cached.cache_type.value = "exact_match"
            mock_cached.hit_count = 5
            mock_get.return_value = mock_cached

            response = await generate_ai_response(
                [{"role": "user", "content": "Hello"}]
            )

            assert response.content == "Cached response"
            assert response.metadata["cached"] is True

    @pytest.mark.asyncio
    async def test_generate_ai_response_not_cached(self):
        """Test convenience function without cache"""
        with patch("app.services.ai_router.response_cache.get") as mock_get:
            with patch("app.services.ai_router.response_cache.set") as mock_set:
                with patch.object(ai_router, "generate_response") as mock_gen:
                    mock_get.return_value = None
                    mock_gen.return_value = AIResponse(
                        "New response",
                        "model",
                        "claude",
                        "en",
                        1.0,
                        0.01,
                        AIResponseStatus.SUCCESS,
                    )

                    response = await generate_ai_response(
                        [{"role": "user", "content": "Test"}]
                    )

                    assert response.content == "New response"
                    mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_ai_response_fallback(self):
        """Test convenience function fallback on AttributeError"""
        with patch("app.services.ai_router.response_cache.get") as mock_get:
            with patch("app.services.ai_router.response_cache.set") as mock_set:
                with patch.object(
                    ai_router, "generate_response", side_effect=AttributeError
                ):
                    with patch.object(ai_router, "select_provider") as mock_select:
                        mock_get.return_value = None
                        mock_service = Mock()
                        mock_service.generate_response = AsyncMock(
                            return_value=AIResponse(
                                "Fallback",
                                "m",
                                "p",
                                "en",
                                1.0,
                                0.01,
                                AIResponseStatus.SUCCESS,
                            )
                        )
                        mock_select.return_value = ProviderSelection(
                            "p", mock_service, "m", "r", 0.9, 0.01, False
                        )

                        response = await generate_ai_response(
                            [{"role": "user", "content": "Test"}]
                        )

                        assert response.content == "Fallback"

    @pytest.mark.asyncio
    async def test_generate_streaming_ai_response(self):
        """Test convenience function for streaming"""
        with patch.object(ai_router, "generate_streaming_response") as mock_stream:

            async def mock_gen(*args, **kwargs):
                yield StreamingResponse("chunk", "m", "p", "en", True, 1.0, 0.01, {})

            mock_stream.return_value = mock_gen()

            chunks = []
            async for chunk in generate_streaming_ai_response(
                [{"role": "user", "content": "Test"}]
            ):
                chunks.append(chunk)

            assert len(chunks) == 1

    @pytest.mark.asyncio
    async def test_get_ai_router_status(self):
        """Test convenience function for router status"""
        with patch.object(ai_router, "get_router_status") as mock_status:
            with patch.object(ai_router, "check_budget_status") as mock_budget:
                with patch(
                    "app.services.ai_router.response_cache.get_stats"
                ) as mock_cache_stats:
                    mock_status.return_value = {"router_mode": "hybrid"}
                    mock_budget.return_value = BudgetStatus(
                        30.0, 5.0, 25.0, 16.67, BudgetAlert.GREEN, 20, 7.5, False
                    )
                    mock_cache_stats.return_value = {"hits": 10, "misses": 5}

                    status = await get_ai_router_status()

                    assert "cost_optimization" in status
                    assert "cache_stats" in status["cost_optimization"]

    def test_register_ai_provider(self):
        """Test registering provider via convenience function"""
        mock_service = Mock()
        register_ai_provider("test_new_provider", mock_service)
        assert "test_new_provider" in ai_router.providers


class TestDataclasses:
    def test_provider_selection_creation(self):
        """Test ProviderSelection dataclass creation"""
        selection = ProviderSelection(
            provider_name="test",
            service=Mock(),
            model="test-model",
            reason="test reason",
            confidence=0.95,
            cost_estimate=0.01,
            is_fallback=False,
        )
        assert selection.provider_name == "test"
        assert selection.model == "test-model"
        assert selection.confidence == 0.95
        assert selection.is_fallback is False
        assert selection.fallback_reason is None

    def test_provider_selection_with_fallback(self):
        """Test ProviderSelection with fallback reason"""
        selection = ProviderSelection(
            provider_name="ollama",
            service=Mock(),
            model="llama2",
            reason="budget exceeded",
            confidence=0.7,
            cost_estimate=0.0,
            is_fallback=True,
            fallback_reason=FallbackReason.BUDGET_EXCEEDED,
        )
        assert selection.is_fallback is True
        assert selection.fallback_reason == FallbackReason.BUDGET_EXCEEDED


class TestEnums:
    def test_router_mode_values(self):
        """Test RouterMode enum values"""
        assert RouterMode.COST_OPTIMIZED.value == "cost_optimized"
        assert RouterMode.QUALITY_OPTIMIZED.value == "quality_optimized"
        assert RouterMode.HYBRID.value == "hybrid"

    def test_fallback_reason_values(self):
        """Test FallbackReason enum values"""
        assert FallbackReason.BUDGET_EXCEEDED.value == "budget_exceeded"
        assert FallbackReason.API_UNAVAILABLE.value == "api_unavailable"
        assert FallbackReason.USER_PREFERENCE.value == "user_preference"


class TestEdgeCaseCoverage:
    """Test edge cases for complete coverage"""

    @pytest.mark.asyncio
    async def test_try_cloud_provider_exception_handling(self):
        """Test that _try_cloud_provider catches exceptions and returns None

        This tests lines 209-211 in ai_router.py where exceptions are caught
        in the _try_cloud_provider method.
        """
        router = EnhancedAIRouter()

        # Create a mock service that will pass health checks
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(
            return_value={"status": "healthy", "available": True}
        )

        # Register the provider so it exists in self.providers
        router.register_provider("test_provider", mock_service)

        # Mock budget status
        mock_budget = Mock()
        mock_budget.remaining_budget = 10.0

        # Mock _estimate_request_cost to raise an exception after health check passes
        # This will trigger the exception handler at lines 209-211
        with patch.object(
            router,
            "_estimate_request_cost",
            new=AsyncMock(side_effect=Exception("Cost calculation error")),
        ):
            with patch("app.services.ai_router.logger") as mock_logger:
                result = await router._try_cloud_provider(
                    provider_name="test_provider",
                    language="en",
                    use_case="conversation",
                    budget_status=mock_budget,
                )

                # Verify the warning was logged (line 210)
                mock_logger.warning.assert_called_once()
                assert "check failed" in str(mock_logger.warning.call_args)

                # Should return None when exception occurs (line 211)
                assert result is None

    @pytest.mark.asyncio
    async def test_streaming_all_providers_fail_raises_exception(self):
        """Test that streaming raises exception when all providers fail

        This tests line 517 in ai_router.py where an exception is raised
        when both initial and fallback streaming attempts fail.
        """
        router = EnhancedAIRouter()

        # Mock select_provider to always raise an exception
        # This will cause both the initial attempt and the fallback attempt to fail
        with patch.object(
            router,
            "select_provider",
            side_effect=Exception("No providers available"),
        ):
            # Expect the exception to be raised with "All streaming providers failed"
            with pytest.raises(Exception, match="All streaming providers failed"):
                async for _ in router.generate_streaming_response(
                    messages=[{"role": "user", "content": "test"}], language="en"
                ):
                    pass

    @pytest.mark.asyncio
    async def test_cost_optimization_default_balanced_scoring(self):
        """Test cost optimization uses balanced scoring for unrecognized use cases

        This tests line 620 in ai_router.py where the default balanced scoring
        is used for use cases that don't match simple or complex categories.
        """
        router = EnhancedAIRouter()

        # Create budget status with sufficient budget (>= $10) to avoid low budget path
        budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=5.0,
            remaining_budget=25.0,  # >= 10.0 to avoid low budget path
            percentage_used=16.67,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=7.5,
            is_over_budget=False,
        )

        providers = ["claude", "mistral", "deepseek"]

        # Use a use_case that's NOT in simple_use_cases or complex_use_cases
        # simple_use_cases = ["conversation", "translation", "simple_qa"]
        # complex_use_cases = ["analysis", "reasoning", "content_generation", "educational"]
        # This should trigger the default balanced scoring at line 620
        sorted_providers = await router._sort_providers_by_cost_efficiency(
            providers=providers,
            language="en",
            use_case="unknown_category",  # Not in any predefined category
            budget_status=budget_status,
        )

        # Should return all providers sorted by balanced scoring (50% cost, 50% quality)
        assert len(sorted_providers) == 3
        assert all(p in sorted_providers for p in providers)


class TestMissingBranchCoverage:
    """Tests to achieve TRUE 100% branch coverage for ai_router.py"""

    @pytest.mark.asyncio
    async def test_select_local_provider_ollama_already_registered(self):
        """Test branch 287->290: ollama already registered in providers"""
        router = EnhancedAIRouter()

        # Pre-register ollama provider to skip the registration branch
        mock_ollama = AsyncMock()
        mock_ollama.check_availability = AsyncMock(return_value=True)
        mock_ollama.get_recommended_model = Mock(return_value="llama2")
        router.register_provider("ollama", mock_ollama)

        # Now call _select_local_provider - should skip "if ollama not in providers" branch
        # Use valid FallbackReason enum value
        with patch("app.services.ai_router.ollama_service", mock_ollama):
            selection = await router._select_local_provider(
                "en", FallbackReason.USER_PREFERENCE.value
            )

        assert selection.provider_name == "ollama"
        assert selection.model == "llama2"
        assert selection.service == mock_ollama

    @pytest.mark.asyncio
    async def test_generate_ai_response_fallback_no_content(self):
        """Test branch 756->764: fallback response without content"""
        # Mock ai_router to trigger AttributeError, then fallback returns empty response
        mock_router = Mock()
        mock_router.generate_response = Mock(
            side_effect=AttributeError("Method not found")
        )

        # Mock select_provider to return a selection
        mock_service = AsyncMock()
        mock_selection = ProviderSelection(
            provider_name="test",
            model="test-model",
            service=mock_service,
            reason="test",
            confidence=1.0,
            cost_estimate=0.0,
            is_fallback=True,
        )
        mock_router.select_provider = AsyncMock(return_value=mock_selection)

        # Mock service to return response WITHOUT content (empty string)
        empty_response = AIResponse(
            content="",  # Empty content to trigger else branch
            provider="test",
            model="test-model",
            language="en",
            processing_time=0.1,
            cost=0.0,
            status=AIResponseStatus.SUCCESS,
        )
        mock_service.generate_response = AsyncMock(return_value=empty_response)

        with patch("app.services.ai_router.ai_router", mock_router):
            with patch("app.services.ai_router.response_cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)  # No cached response
                result = await generate_ai_response(
                    [{"role": "user", "content": "test"}], "en"
                )

        # Should return the response, but NOT call cache.set due to empty content
        assert result == empty_response
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_ai_response_fallback_none_response(self):
        """Test branch 756->764: fallback returns None response"""
        # Mock ai_router to trigger AttributeError
        mock_router = Mock()
        mock_router.generate_response = Mock(
            side_effect=AttributeError("Method not found")
        )

        # Mock select_provider
        mock_service = AsyncMock()
        mock_selection = ProviderSelection(
            provider_name="test",
            model="test-model",
            service=mock_service,
            reason="test",
            confidence=1.0,
            cost_estimate=0.0,
            is_fallback=True,
        )
        mock_router.select_provider = AsyncMock(return_value=mock_selection)

        # Mock service to return None
        mock_service.generate_response = AsyncMock(return_value=None)

        with patch("app.services.ai_router.ai_router", mock_router):
            with patch("app.services.ai_router.response_cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)  # No cached response
                result = await generate_ai_response(
                    [{"role": "user", "content": "test"}], "en"
                )

        # Should return None and NOT call cache.set
        assert result is None
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_ai_router_status_no_alert_level(self):
        """Test branch 789->794: budget_status.alert_level is None"""
        # Mock ai_router.get_router_status to return base status
        base_status = {
            "mode": "hybrid",
            "providers": ["claude", "ollama"],
            "fallback_enabled": True,
        }

        # Mock check_budget_status to return budget status with None alert_level
        budget_status = BudgetStatus(
            total_budget=100.0,
            used_budget=10.0,
            remaining_budget=90.0,
            percentage_used=10.0,
            alert_level=None,  # None to trigger else branch
            days_remaining=30,
            projected_monthly_cost=10.0,
            is_over_budget=False,
        )

        # Mock response_cache.get_stats (not get_cache_stats)
        cache_stats = {
            "hits": 5,
            "misses": 10,
            "total_requests": 15,
            "hit_rate": 0.33,
            "size": 100,
        }

        with patch("app.services.ai_router.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(return_value=base_status)
            mock_router.check_budget_status = AsyncMock(return_value=budget_status)

            with patch("app.services.ai_router.response_cache") as mock_cache:
                mock_cache.get_stats = Mock(return_value=cache_stats)

                status = await get_ai_router_status()

        # Should use "green" as default when alert_level is None
        assert status["cost_optimization"]["budget_status"]["alert_level"] == "green"
        assert status["cost_optimization"]["budget_status"]["remaining"] == 90.0
        assert (
            status["cost_optimization"]["estimated_cache_savings_usd"] == 0.05
        )  # 5 hits * $0.01

    @pytest.mark.asyncio
    async def test_generate_ai_response_try_block_no_content(self):
        """Test branch 735->743: normal try path with no content (not AttributeError fallback)"""
        # Mock ai_router.generate_response to succeed but return response without content
        mock_router = Mock()

        # Return response with empty content (no AttributeError)
        empty_response = AIResponse(
            content="",  # Empty content to trigger else branch at line 735
            provider="test",
            model="test-model",
            language="en",
            processing_time=0.1,
            cost=0.0,
            status=AIResponseStatus.SUCCESS,
        )
        mock_router.generate_response = AsyncMock(return_value=empty_response)

        with patch("app.services.ai_router.ai_router", mock_router):
            with patch("app.services.ai_router.response_cache") as mock_cache:
                mock_cache.get = Mock(return_value=None)  # No cached response
                result = await generate_ai_response(
                    [{"role": "user", "content": "test"}], "en"
                )

        # Should return the response, but NOT call cache.set due to empty content
        assert result == empty_response
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_ai_router_status_with_alert_level(self):
        """Test branch 789->794: budget_status.alert_level has a value (not None)"""
        # Mock ai_router.get_router_status to return base status
        base_status = {
            "mode": "hybrid",
            "providers": ["claude", "ollama"],
            "fallback_enabled": True,
        }

        # Mock check_budget_status to return budget status with alert_level set
        budget_status = BudgetStatus(
            total_budget=100.0,
            used_budget=85.0,
            remaining_budget=15.0,
            percentage_used=85.0,
            alert_level=BudgetAlert.RED,  # Has value to trigger if branch
            days_remaining=5,
            projected_monthly_cost=85.0,
            is_over_budget=False,
        )

        # Mock response_cache.get_stats
        cache_stats = {
            "hits": 10,
            "misses": 5,
            "total_requests": 15,
            "hit_rate": 0.67,
            "size": 200,
        }

        with patch("app.services.ai_router.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(return_value=base_status)
            mock_router.check_budget_status = AsyncMock(return_value=budget_status)

            with patch("app.services.ai_router.response_cache") as mock_cache:
                mock_cache.get_stats = Mock(return_value=cache_stats)

                status = await get_ai_router_status()

        # Should use alert_level.value when alert_level is not None
        assert status["cost_optimization"]["budget_status"]["alert_level"] == "red"
        assert status["cost_optimization"]["budget_status"]["remaining"] == 15.0
        assert (
            status["cost_optimization"]["estimated_cache_savings_usd"] == 0.1
        )  # 10 hits * $0.01

    @pytest.mark.asyncio
    async def test_get_ai_router_status_zero_cache_hits(self):
        """Test branch 789->794: cache_stats hits = 0 (no cache savings calculation)"""
        # Mock ai_router.get_router_status to return base status
        base_status = {
            "mode": "hybrid",
            "providers": ["claude", "ollama"],
            "fallback_enabled": True,
        }

        # Mock check_budget_status
        budget_status = BudgetStatus(
            total_budget=100.0,
            used_budget=10.0,
            remaining_budget=90.0,
            percentage_used=10.0,
            alert_level=BudgetAlert.GREEN,
            days_remaining=30,
            projected_monthly_cost=10.0,
            is_over_budget=False,
        )

        # Mock response_cache.get_stats with ZERO hits to trigger else branch
        cache_stats = {
            "hits": 0,  # Zero hits - should skip savings calculation
            "misses": 10,
            "total_requests": 10,
            "hit_rate": 0.0,
            "size": 0,
        }

        with patch("app.services.ai_router.ai_router") as mock_router:
            mock_router.get_router_status = AsyncMock(return_value=base_status)
            mock_router.check_budget_status = AsyncMock(return_value=budget_status)

            with patch("app.services.ai_router.response_cache") as mock_cache:
                mock_cache.get_stats = Mock(return_value=cache_stats)

                status = await get_ai_router_status()

        # Should have cache_savings = 0.0 since hits = 0
        assert status["cost_optimization"]["estimated_cache_savings_usd"] == 0.0
        assert status["cost_optimization"]["cache_stats"]["hits"] == 0
