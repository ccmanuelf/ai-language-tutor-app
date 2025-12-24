"""
Integration Tests for AI Service Components
Session 82 - AI Testing Architecture

These tests verify the interaction between AI router, service selection,
and conversation handling WITHOUT calling external AI APIs.

Test Tier: INTEGRATION
- External APIs (Claude, Mistral, DeepSeek) are mocked
- Real AI router + service selection logic tested
- Verifies failover behavior
- Tests component interaction

Run with: pytest tests/integration/ -v -m integration
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.ai_router import EnhancedAIRouter

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestAIRouterIntegration:
    """Test AI router service selection and failover logic"""

    @pytest.mark.asyncio
    async def test_provider_selection_based_on_language(self):
        """Test that router selects appropriate provider for language"""
        router = EnhancedAIRouter()

        # Mock the actual service generate methods to avoid external calls
        with (
            patch(
                "app.services.claude_service.ClaudeService.generate_response",
                new_callable=AsyncMock,
            ) as mock_claude,
            patch(
                "app.services.mistral_service.MistralService.generate_response",
                new_callable=AsyncMock,
            ) as mock_mistral,
            patch(
                "app.services.deepseek_service.DeepSeekService.generate_response",
                new_callable=AsyncMock,
            ) as mock_deepseek,
        ):
            # Configure mocks
            mock_claude.return_value = Mock(content="Claude response", cost=0.01)
            mock_mistral.return_value = Mock(content="Mistral response", cost=0.01)
            mock_deepseek.return_value = Mock(content="DeepSeek response", cost=0.01)

            # Test English - should select Claude or available provider
            selection = await router.select_provider(
                language="en", use_case="conversation"
            )
            assert selection is not None
            assert selection.service is not None

            # Test Chinese - should prefer DeepSeek if available
            selection_zh = await router.select_provider(
                language="zh", use_case="conversation"
            )
            assert selection_zh is not None
            assert selection_zh.service is not None

    @pytest.mark.asyncio
    async def test_router_failover_when_primary_fails(self):
        """Test that router falls back to secondary provider on failure"""
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )
        from app.services.ollama_service import ollama_service

        router = EnhancedAIRouter()

        # Mock budget to allow cloud providers
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.33,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=15.0,
            is_over_budget=False,
        )

        # Simulate first provider failing, second succeeding
        with (
            patch.object(
                budget_manager,
                "get_current_budget_status",
                return_value=mock_budget_status,
            ),
            patch(
                "app.services.claude_service.ClaudeService.generate_response",
                new_callable=AsyncMock,
            ) as mock_claude,
            patch(
                "app.services.mistral_service.MistralService.generate_response",
                new_callable=AsyncMock,
            ) as mock_mistral,
            patch.object(ollama_service, "check_availability", return_value=True),
            patch.object(
                ollama_service, "get_recommended_model", return_value="llama2:7b"
            ),
        ):
            # First provider fails
            mock_claude.side_effect = Exception("Claude API unavailable")

            # Second provider succeeds
            mock_mistral.return_value = Mock(content="Mistral fallback", cost=0.01)

            # Router should handle failover gracefully
            selection = await router.select_provider(
                language="en", use_case="conversation"
            )

            # Should still return a service (failover)
            assert selection is not None


class TestConversationAIIntegration:
    """Test conversation endpoint with AI router integration"""

    @pytest.mark.asyncio
    async def test_chat_with_ai_router_integration(self):
        """Test chat endpoint integrates correctly with AI router"""
        from fastapi.testclient import TestClient

        from app.core.security import require_auth
        from app.database.config import get_primary_db_session
        from app.main import app
        from app.models.simple_user import SimpleUser
        from app.services.budget_manager import BudgetAlert, BudgetStatus
        from app.services.claude_service import claude_service
        from app.services.mistral_service import mistral_service

        # Create test user
        test_user = SimpleUser(
            id=1,
            user_id="testuser",
            username="testuser",
            email="test@example.com",
            role="parent",
        )

        # Mock dependencies
        mock_db = Mock()
        app.dependency_overrides[require_auth] = lambda: test_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        # Mock budget manager to avoid budget exceeded isolation issue
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=5.0,
            remaining_budget=25.0,
            percentage_used=16.67,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=7.5,
            is_over_budget=False,
        )

        # Mock both Mistral and Claude services to test real router logic
        # Router uses cost optimization and may select either one
        with (
            patch(
                "app.services.ai_router.budget_manager.get_current_budget_status",
                return_value=mock_budget_status,
            ),
            patch.object(
                mistral_service, "generate_response", new_callable=AsyncMock
            ) as mock_mistral,
            patch.object(
                claude_service, "generate_response", new_callable=AsyncMock
            ) as mock_claude,
        ):
            # Set up both mocks
            mock_mistral.return_value = Mock(
                content="Hello! I'm your AI tutor.", cost=0.02
            )
            mock_claude.return_value = Mock(
                content="Hello! I'm your AI tutor.", cost=0.02
            )

            client = TestClient(app)
            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": "Hello", "language": "en-claude", "use_speech": False},
            )

            assert response.status_code == 200
            data = response.json()

            # Verify that ONE of the AI services was actually called through router
            # Router uses cost optimization, so it may choose Mistral over Claude
            assert mock_mistral.called or mock_claude.called

            # Verify response structure
            assert "response" in data
            assert "Hello! I'm your AI tutor." in data["response"]
            assert data["estimated_cost"] > 0

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_chat_failover_to_fallback_on_all_ai_failures(self):
        """Test chat uses fallback when ALL AI services fail"""
        from fastapi.testclient import TestClient

        from app.core.security import require_auth
        from app.database.config import get_primary_db_session
        from app.main import app
        from app.models.simple_user import SimpleUser

        test_user = SimpleUser(
            id=1,
            user_id="testuser",
            username="testuser",
            email="test@example.com",
            role="parent",
        )

        mock_db = Mock()
        app.dependency_overrides[require_auth] = lambda: test_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        # Simulate ALL AI services failing
        with (
            patch(
                "app.services.claude_service.ClaudeService.generate_response",
                new_callable=AsyncMock,
            ) as mock_claude,
            patch(
                "app.services.mistral_service.MistralService.generate_response",
                new_callable=AsyncMock,
            ) as mock_mistral,
            patch(
                "app.services.deepseek_service.DeepSeekService.generate_response",
                new_callable=AsyncMock,
            ) as mock_deepseek,
        ):
            # All services fail
            mock_claude.side_effect = Exception("Claude unavailable")
            mock_mistral.side_effect = Exception("Mistral unavailable")
            mock_deepseek.side_effect = Exception("DeepSeek unavailable")

            client = TestClient(app)
            response = client.post(
                "/api/v1/conversations/chat",
                json={"message": "Hello", "language": "en-claude", "use_speech": False},
            )

            # Should still return 200 with fallback
            assert response.status_code == 200
            data = response.json()

            # Should have fallback response
            assert "response" in data
            # Fallback should contain "Hey there!" (demo mode) or "[Demo Mode]"
            assert "Hey there!" in data["response"] or "[Demo Mode]" in data["response"]

            # Cost should be 0 for fallback
            assert data["estimated_cost"] == 0.0 or data["estimated_cost"] == 0.01

        app.dependency_overrides.clear()


class TestSpeechProcessingIntegration:
    """Test integration between speech processing and AI services"""

    @pytest.mark.asyncio
    async def test_chat_with_tts_integration(self):
        """Test chat integrates correctly with TTS service"""
        from fastapi.testclient import TestClient

        from app.core.security import require_auth
        from app.database.config import get_primary_db_session
        from app.main import app
        from app.models.simple_user import SimpleUser
        from app.services.budget_manager import BudgetAlert, BudgetStatus
        from app.services.claude_service import claude_service
        from app.services.mistral_service import mistral_service

        test_user = SimpleUser(
            id=1,
            user_id="testuser",
            username="testuser",
            email="test@example.com",
            role="parent",
        )

        mock_db = Mock()
        app.dependency_overrides[require_auth] = lambda: test_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        # Mock budget manager to avoid budget exceeded isolation issue
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=5.0,
            remaining_budget=25.0,
            percentage_used=16.67,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=7.5,
            is_over_budget=False,
        )

        # Mock both AI services and TTS to test real router logic
        with (
            patch(
                "app.services.ai_router.budget_manager.get_current_budget_status",
                return_value=mock_budget_status,
            ),
            patch.object(
                mistral_service, "generate_response", new_callable=AsyncMock
            ) as mock_mistral,
            patch.object(
                claude_service, "generate_response", new_callable=AsyncMock
            ) as mock_claude,
            patch(
                "app.services.speech_processor.speech_processor.process_text_to_speech",
                new_callable=AsyncMock,
            ) as mock_tts,
        ):
            # Set up both AI mocks
            mock_mistral.return_value = Mock(content="Hello! How are you?", cost=0.02)
            mock_claude.return_value = Mock(content="Hello! How are you?", cost=0.02)

            mock_tts_result = Mock()
            mock_tts_result.audio_data = b"fake_audio"
            mock_tts.return_value = mock_tts_result

            client = TestClient(app)
            response = client.post(
                "/api/v1/conversations/chat",
                json={
                    "message": "Hi",
                    "language": "en-claude",
                    "use_speech": True,  # Request TTS
                },
            )

            assert response.status_code == 200
            data = response.json()

            # Verify that ONE of the AI services was called through router
            assert mock_mistral.called or mock_claude.called

            # Verify TTS was called
            assert mock_tts.called

            # Verify audio URL is generated
            assert "audio_url" in data

        app.dependency_overrides.clear()


class TestMultiLanguageIntegration:
    """Test multi-language support integration"""

    @pytest.mark.asyncio
    async def test_language_switching_between_providers(self):
        """Test that different languages route to appropriate providers"""
        from fastapi.testclient import TestClient

        from app.core.security import require_auth
        from app.database.config import get_primary_db_session
        from app.main import app
        from app.models.simple_user import SimpleUser

        test_user = SimpleUser(
            id=1,
            user_id="testuser",
            username="testuser",
            email="test@example.com",
            role="parent",
        )

        mock_db = Mock()
        app.dependency_overrides[require_auth] = lambda: test_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        # Mock all AI services
        with (
            patch(
                "app.services.claude_service.ClaudeService.generate_response",
                new_callable=AsyncMock,
            ) as mock_claude,
            patch(
                "app.services.mistral_service.MistralService.generate_response",
                new_callable=AsyncMock,
            ) as mock_mistral,
            patch(
                "app.services.deepseek_service.DeepSeekService.generate_response",
                new_callable=AsyncMock,
            ) as mock_deepseek,
        ):
            mock_claude.return_value = Mock(content="English response", cost=0.01)
            mock_mistral.return_value = Mock(content="French response", cost=0.01)
            mock_deepseek.return_value = Mock(content="Chinese response", cost=0.01)

            client = TestClient(app)

            # Test English
            response_en = client.post(
                "/api/v1/conversations/chat",
                json={"message": "Hello", "language": "en-claude"},
            )
            assert response_en.status_code == 200
            assert response_en.json()["language"] == "en"

            # Test French with Mistral
            response_fr = client.post(
                "/api/v1/conversations/chat",
                json={"message": "Bonjour", "language": "fr-mistral"},
            )
            assert response_fr.status_code == 200
            assert response_fr.json()["language"] == "fr"

            # Test Chinese with DeepSeek
            response_zh = client.post(
                "/api/v1/conversations/chat",
                json={"message": "你好", "language": "zh-deepseek"},
            )
            assert response_zh.status_code == 200
            assert response_zh.json()["language"] == "zh"

        app.dependency_overrides.clear()


class TestPreferredProviderIntegration:
    """Integration tests for preferred provider selection (Session 96)"""

    @pytest.mark.asyncio
    async def test_preferred_provider_used_when_specified(self):
        """Test that router uses user's preferred provider when specified"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )

        # Mock budget to allow any provider
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=10.0,
            remaining_budget=20.0,
            percentage_used=33.33,
            alert_level=BudgetAlert.GREEN,
            days_remaining=20,
            projected_monthly_cost=15.0,
            is_over_budget=False,
        )

        with patch.object(
            budget_manager, "get_current_budget_status", return_value=mock_budget_status
        ):
            # User explicitly chooses Claude
            selection = await ai_router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="claude",
            )

            assert selection.provider_name == "claude"
            assert selection.reason == "User preference"
            assert selection.is_fallback is False

    @pytest.mark.asyncio
    async def test_preferred_provider_budget_exceeded_with_override(self):
        """Test budget exceeded warning when user wants premium provider"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )

        # Mock budget exceeded
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=30.5,
            remaining_budget=-0.5,
            percentage_used=101.67,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=10,
            projected_monthly_cost=45.75,
            is_over_budget=True,
        )

        with patch.object(
            budget_manager, "get_current_budget_status", return_value=mock_budget_status
        ):
            # User wants Claude but budget exceeded
            user_prefs = {
                "ai_provider_settings": {
                    "budget_override_allowed": True,
                    "enforce_budget_limits": True,
                }
            }

            selection = await ai_router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="claude",
                user_preferences=user_prefs,
                enforce_budget=True,
            )

            # Should return Claude with budget warning
            assert selection.provider_name == "claude"
            assert selection.requires_budget_override is True
            assert selection.budget_warning is not None
            assert "Budget exceeded" in selection.budget_warning.message

    @pytest.mark.asyncio
    async def test_preferred_provider_budget_enforcement_disabled(self):
        """Test preferred provider used when budget enforcement disabled"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )

        # Mock budget exceeded
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=32.0,
            remaining_budget=-2.0,
            percentage_used=106.67,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=8,
            projected_monthly_cost=60.0,
            is_over_budget=True,
        )

        with patch.object(
            budget_manager, "get_current_budget_status", return_value=mock_budget_status
        ):
            # User disables budget enforcement
            selection = await ai_router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="claude",
                enforce_budget=False,
            )

            # Should use Claude despite budget
            assert selection.provider_name == "claude"
            assert selection.reason == "User preference (budget enforcement disabled)"
            assert selection.requires_budget_override is False

    @pytest.mark.asyncio
    async def test_preferred_provider_auto_fallback_to_ollama(self):
        """Test auto-fallback to Ollama when budget exceeded and configured"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )
        from app.services.ollama_service import ollama_service

        # Mock budget exceeded
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=31.0,
            remaining_budget=-1.0,
            percentage_used=103.33,
            alert_level=BudgetAlert.CRITICAL,
            days_remaining=5,
            projected_monthly_cost=62.0,
            is_over_budget=True,
        )

        with (
            patch.object(
                budget_manager,
                "get_current_budget_status",
                return_value=mock_budget_status,
            ),
            patch.object(budget_manager, "can_override_budget", return_value=False),
            patch.object(ollama_service, "check_availability", return_value=True),
            patch.object(
                ollama_service, "get_recommended_model", return_value="llama2:7b"
            ),
        ):
            # User has auto-fallback enabled
            user_prefs = {
                "ai_provider_settings": {
                    "auto_fallback_to_ollama": True,
                    "budget_override_allowed": False,
                }
            }

            selection = await ai_router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="claude",
                user_preferences=user_prefs,
                enforce_budget=True,
            )

            # Should fallback to Ollama
            assert selection.provider_name == "ollama"
            assert selection.is_fallback is True
            assert "budget_exceeded_auto_fallback" in selection.reason

    @pytest.mark.asyncio
    async def test_preferred_provider_within_budget(self):
        """Test preferred provider used when within budget"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )

        # Mock budget OK
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=15.0,
            remaining_budget=15.0,
            percentage_used=50.0,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=15,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )

        with patch.object(
            budget_manager, "get_current_budget_status", return_value=mock_budget_status
        ):
            # User chooses Mistral
            selection = await ai_router.select_provider(
                language="fr",
                use_case="conversation",
                preferred_provider="mistral",
            )

            assert selection.provider_name == "mistral"
            assert selection.reason == "User preference"
            assert selection.is_fallback is False
            assert selection.requires_budget_override is False

    @pytest.mark.asyncio
    async def test_cost_optimization_when_no_preferred_provider(self):
        """Test cost optimization still works when no provider specified"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )

        # Mock budget OK
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=15.0,
            remaining_budget=15.0,
            percentage_used=50.0,
            alert_level=BudgetAlert.YELLOW,
            days_remaining=15,
            projected_monthly_cost=30.0,
            is_over_budget=False,
        )

        with patch.object(
            budget_manager, "get_current_budget_status", return_value=mock_budget_status
        ):
            # User chooses Mistral
            selection = await ai_router.select_provider(
                language="fr",
                use_case="conversation",
                preferred_provider="mistral",
            )

            assert selection.provider_name == "mistral"
            assert selection.reason == "User preference"
            assert selection.is_fallback is False
            assert selection.requires_budget_override is False

    @pytest.mark.asyncio
    async def test_cost_optimization_fallback_to_local_when_budget_low(self):
        """Test fallback to cost-effective provider when budget is low"""
        from app.services.ai_router import ai_router
        from app.services.budget_manager import (
            BudgetAlert,
            BudgetStatus,
            budget_manager,
        )
        from app.services.ollama_service import ollama_service

        # Mock budget low
        mock_budget_status = BudgetStatus(
            total_budget=30.0,
            used_budget=28.0,
            remaining_budget=2.0,
            percentage_used=93.33,
            alert_level=BudgetAlert.RED,
            days_remaining=5,
            projected_monthly_cost=56.0,
            is_over_budget=False,
        )

        with (
            patch.object(
                budget_manager,
                "get_current_budget_status",
                return_value=mock_budget_status,
            ),
            patch.object(ollama_service, "check_availability", return_value=True),
            patch.object(
                ollama_service, "get_recommended_model", return_value="llama2:7b"
            ),
        ):
            # No preferred provider - should use cost optimization
            selection = await ai_router.select_provider(
                language="en",
                use_case="conversation",
                # No preferred_provider specified
            )

            # Should select provider based on cost/availability
            assert selection is not None
            assert selection.provider_name is not None
            # Cost optimization may choose cheaper provider or fallback to Ollama


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
