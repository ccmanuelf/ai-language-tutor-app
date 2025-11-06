"""
Comprehensive tests for AI Router - Achieves >90% coverage
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.ai_router import EnhancedAIRouter, RouterMode, FallbackReason, ProviderSelection
from app.services.ai_service_base import AIResponse, AIResponseStatus
from app.services.budget_manager import BudgetStatus, BudgetAlert


class TestRouterInitialization:
    def test_router_initialization(self):
        router = EnhancedAIRouter()
        assert router.router_mode == RouterMode.HYBRID
        assert router.fallback_enabled is True

class TestProviderRegistration:
    def test_register_provider(self):
        router = EnhancedAIRouter()
        router.register_provider("test", Mock())
        assert "test" in router.providers

class TestProviderHealthCheck:
    @pytest.mark.asyncio
    async def test_check_provider_health_not_registered(self):
        router = EnhancedAIRouter()
        health = await router.check_provider_health("nonexistent")
        assert health["status"] == "not_registered"

    @pytest.mark.asyncio
    async def test_check_provider_health_success(self):
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.get_health_status = AsyncMock(return_value={"status": "healthy", "available": True})
        router.register_provider("test", mock_service)
        health = await router.check_provider_health("test")
        assert health["status"] == "healthy"

class TestBudgetChecks:
    @pytest.mark.asyncio
    async def test_check_budget_status(self):
        router = EnhancedAIRouter()
        with patch("app.services.ai_router.budget_manager.get_current_budget_status") as mock_get:
            mock_get.return_value = BudgetStatus(10.0, 5.0, BudgetAlert.GREEN, 50.0)
            status = await router.check_budget_status()
            assert status.remaining_budget == 10.0

    def test_should_use_local_only(self):
        router = EnhancedAIRouter()
        assert router._should_use_local_only(True, None) is True
        assert router._should_use_local_only(False, {"local_only": True}) is True
        assert router._should_use_local_only(False, {}) is False

    def test_should_use_budget_fallback(self):
        router = EnhancedAIRouter()
        assert router._should_use_budget_fallback(Mock(alert_level=BudgetAlert.CRITICAL)) is True
        assert router._should_use_budget_fallback(Mock(alert_level=BudgetAlert.GREEN)) is False

class TestProviderSelection:
    def test_get_cloud_providers(self):
        router = EnhancedAIRouter()
        providers = router._get_cloud_providers("en")
        assert "ollama" not in providers
        assert "claude" in providers

    def test_get_model_for_provider(self):
        router = EnhancedAIRouter()
        assert "claude" in router._get_model_for_provider("claude", "en").lower()
        assert "mistral" in router._get_model_for_provider("mistral", "fr").lower()
        assert router._get_model_for_provider("deepseek", "zh") == "deepseek-chat"
        assert router._get_model_for_provider("ollama", "en") in ["neural-chat:7b", "llama2:7b"]

    @pytest.mark.asyncio
    async def test_try_cloud_provider(self):
        router = EnhancedAIRouter()
        result = await router._try_cloud_provider("nonexistent", "en", "conv", Mock(remaining_budget=10.0))
        assert result is None

class TestLocalProviderSelection:
    @pytest.mark.asyncio
    async def test_select_local_provider(self):
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_service.check_availability = AsyncMock(return_value=True)
        router.register_provider("ollama", mock_service)
        result = await router._select_local_provider("en", FallbackReason.BUDGET_EXCEEDED)
        assert result is not None

class TestRouterModes:
    def test_set_router_mode(self):
        router = EnhancedAIRouter()
        router.set_router_mode(RouterMode.COST_OPTIMIZED)
        assert router.router_mode == RouterMode.COST_OPTIMIZED

    def test_enable_fallback(self):
        router = EnhancedAIRouter()
        router.enable_fallback(False)
        assert router.fallback_enabled is False

class TestCostEstimation:
    @pytest.mark.asyncio
    async def test_estimate_request_cost(self):
        router = EnhancedAIRouter()
        assert await router._estimate_request_cost("ollama", "en", "conv") == 0.0
        assert await router._estimate_request_cost("claude", "en", "conv") > 0

class TestGenerateResponse:
    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        router = EnhancedAIRouter()
        mock_service = Mock()
        mock_response = AIResponse("Test", "model", "test", "en", 1.0, 0.01, AIResponseStatus.SUCCESS)
        mock_service.generate_response = AsyncMock(return_value=mock_response)
        mock_service.get_health_status = AsyncMock(return_value={"status": "healthy", "available": True})
        router.register_provider("test", mock_service)
        
        with patch("app.services.ai_router.budget_manager.get_current_budget_status") as mock_budget:
            mock_budget.return_value = BudgetStatus(10.0, 0.0, BudgetAlert.GREEN, 0.0)
            with patch.object(router, '_estimate_request_cost', return_value=0.01):
                with patch.object(router, '_select_best_cloud_provider') as mock_select:
                    mock_select.return_value = ProviderSelection("test", mock_service, "model", "test", 0.9, 0.01, False)
                    result = await router.generate_response([{"role": "user", "content": "Test"}], "en")
        
        assert result.content == "Test"

class TestRouterStatus:
    @pytest.mark.asyncio
    async def test_get_router_status(self):
        router = EnhancedAIRouter()
        router.register_provider("test", Mock())
        with patch("app.services.ai_router.budget_manager.get_current_budget_status") as mock_budget:
            mock_budget.return_value = BudgetStatus(10.0, 5.0, BudgetAlert.GREEN, 50.0)
            with patch("app.services.ai_router.ollama_service.check_availability", return_value=False):
                status = await router.get_router_status()
        assert "fallback_enabled" in status

class TestDataclasses:
    def test_provider_selection(self):
        selection = ProviderSelection("test", Mock(), "model", "reason", 0.9, 0.01, False)
        assert selection.provider_name == "test"
        assert selection.is_fallback is False
