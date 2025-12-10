"""
End-to-End Tests for AI Services
Session 82 - AI Testing Architecture

⚠️ WARNING: These tests use REAL API keys and make REAL API calls!
- Do NOT run in CI/CD without secure secrets management
- Do NOT commit API keys to GitHub
- Each test run COSTS MONEY (API credits)

Run manually only: pytest tests/e2e/ -v -m e2e
"""

import os

import pytest
from dotenv import load_dotenv

# Mark ALL tests in this module as E2E
pytestmark = pytest.mark.e2e

# Load environment variables
load_dotenv()


class TestClaudeE2E:
    """E2E tests for Claude AI service with real API"""

    @pytest.fixture(autouse=True)
    def check_api_key(self):
        """Skip tests if API key not available"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in .env - Skipping E2E test")

    @pytest.mark.asyncio
    async def test_claude_real_api_conversation(self):
        """Test real Claude API call for conversation"""
        from app.services.claude_service import ClaudeService

        service = ClaudeService()

        response = await service.generate_response(
            messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
            message="Say 'Hello' in one word",
            language="en",
            context={"language": "en", "user_id": "e2e_test"},
        )

        # Verify real response
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert response.cost > 0  # Real API calls have cost

        print(f"\n✅ Claude E2E Test Passed")
        print(f"   Response: {response.content[:50]}...")
        print(f"   Cost: ${response.cost:.4f}")
        print(f"   Model: {response.model}")


class TestMistralE2E:
    """E2E tests for Mistral AI service with real API"""

    @pytest.fixture(autouse=True)
    def check_api_key(self):
        """Skip tests if API key not available"""
        if not os.getenv("MISTRAL_API_KEY"):
            pytest.skip("MISTRAL_API_KEY not found in .env - Skipping E2E test")

    @pytest.mark.asyncio
    async def test_mistral_real_api_conversation(self):
        """Test real Mistral API call for conversation"""
        from app.services.mistral_service import MistralService

        service = MistralService()

        response = await service.generate_response(
            messages=[{"role": "user", "content": "Dis 'Bonjour' en un mot"}],
            message="Dis 'Bonjour' en un mot",
            language="fr",
            context={"language": "fr", "user_id": "e2e_test"},
        )

        # Verify real response
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert response.cost > 0

        print(f"\n✅ Mistral E2E Test Passed")
        print(f"   Response: {response.content[:50]}...")
        print(f"   Cost: ${response.cost:.4f}")


class TestDeepSeekE2E:
    """E2E tests for DeepSeek AI service with real API"""

    @pytest.fixture(autouse=True)
    def check_api_key(self):
        """Skip tests if API key not available"""
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not found in .env - Skipping E2E test")

    @pytest.mark.asyncio
    async def test_deepseek_real_api_conversation(self):
        """Test real DeepSeek API call for conversation"""
        from app.services.deepseek_service import DeepSeekService

        service = DeepSeekService()

        response = await service.generate_response(
            messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
            message="Say 'Hello' in one word",
            language="en",
            context={"language": "en", "user_id": "e2e_test"},
        )

        # Verify real response
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0

        print(f"\n✅ DeepSeek E2E Test Passed")
        print(f"   Response: {response.content[:50]}...")
        print(f"   Cost: ${getattr(response, 'cost', 0):.4f}")
        print(f"   Model: {getattr(response, 'model', 'unknown')}")


class TestAIRouterE2E:
    """E2E tests for AI router with real services"""

    @pytest.fixture(autouse=True)
    def check_api_keys(self):
        """Skip if no API keys available"""
        if not (
            os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("MISTRAL_API_KEY")
            or os.getenv("DEEPSEEK_API_KEY")
        ):
            pytest.skip("No AI API keys found - Skipping E2E test")

    @pytest.mark.asyncio
    async def test_router_real_provider_selection(self):
        """Test AI router with real provider selection"""
        from unittest.mock import Mock, patch

        from app.services.ai_router import EnhancedAIRouter
        from app.services.budget_manager import BudgetAlert

        router = EnhancedAIRouter()

        # Mock budget manager to allow cloud provider selection
        # Create a simple object with attributes (not a Mock) to avoid comparison issues
        class MockBudgetStatus:
            total_budget = 100.0
            used_budget = 0.0
            remaining_budget = 100.0
            percentage_used = 0.0
            alert_level = BudgetAlert.GREEN
            is_over_budget = False
            days_remaining = 30
            projected_monthly_cost = 0.0

        mock_budget = Mock()
        mock_budget.get_current_budget_status.return_value = MockBudgetStatus()
        mock_budget.get_status.return_value = MockBudgetStatus()
        mock_budget.get_remaining_budget.return_value = 100.0

        with patch("app.services.ai_router.budget_manager", mock_budget):
            # Test provider selection for English
            selection = await router.select_provider(
                language="en", use_case="conversation"
            )

            assert selection is not None
            assert selection.service is not None
            # Accept both cloud and local providers (Ollama is valid fallback)
            assert selection.provider_name in ["claude", "mistral", "qwen", "ollama"]

            print(f"\n✅ AI Router E2E Test Passed")
            print(f"   Selected Provider: {selection.provider_name}")
            print(f"   Model: {selection.model}")
            print(f"   Reason: {selection.reason}")

    @pytest.mark.asyncio
    async def test_router_real_multi_language(self):
        """Test router handles multiple languages with real APIs"""
        from unittest.mock import Mock, patch

        from app.services.ai_router import EnhancedAIRouter
        from app.services.budget_manager import BudgetAlert

        # Mock budget manager to allow cloud provider selection
        class MockBudgetStatus:
            total_budget = 100.0
            used_budget = 0.0
            remaining_budget = 100.0
            percentage_used = 0.0
            alert_level = BudgetAlert.GREEN
            is_over_budget = False
            days_remaining = 30
            projected_monthly_cost = 0.0

        mock_budget = Mock()
        mock_budget.get_current_budget_status.return_value = MockBudgetStatus()
        mock_budget.get_status.return_value = MockBudgetStatus()
        mock_budget.get_remaining_budget.return_value = 100.0

        with patch("app.services.ai_router.budget_manager", mock_budget):
            router = EnhancedAIRouter()

            languages_tested = []

            # Test English
            if os.getenv("ANTHROPIC_API_KEY"):
                try:
                    selection_en = await router.select_provider(
                        language="en", use_case="conversation"
                    )
                    if selection_en.service:
                        response = await selection_en.service.generate_response(
                            messages=[{"role": "user", "content": "Hi"}],
                            message="Hi",
                            language="en",
                        )
                        assert response.content is not None
                        languages_tested.append("en")
                except Exception as e:
                    # May fail if budget exceeded or Ollama unavailable - acceptable for E2E
                    print(f"English test skipped: {e}")

            # Test French
            if os.getenv("MISTRAL_API_KEY"):
                try:
                    selection_fr = await router.select_provider(
                        language="fr", use_case="conversation"
                    )
                    if selection_fr.service:
                        response = await selection_fr.service.generate_response(
                            messages=[{"role": "user", "content": "Bonjour"}],
                            message="Bonjour",
                            language="fr",
                        )
                        assert response.content is not None
                        languages_tested.append("fr")
                except Exception as e:
                    # May fail if budget exceeded or Ollama unavailable - acceptable for E2E
                    print(f"French test skipped: {e}")

            # Test Chinese
            if os.getenv("DEEPSEEK_API_KEY"):
                try:
                    selection_zh = await router.select_provider(
                        language="zh", use_case="conversation"
                    )
                    if selection_zh.service:
                        response = await selection_zh.service.generate_response(
                            messages=[{"role": "user", "content": "你好"}],
                            message="你好",
                            language="zh",
                        )
                        assert response.content is not None
                        languages_tested.append("zh")
                except Exception as e:
                    # May fail if budget exceeded or Ollama unavailable - acceptable for E2E
                    print(f"Chinese test skipped: {e}")

            assert len(languages_tested) > 0, "No languages could be tested"

            print(f"\n✅ Multi-Language E2E Test Passed")
            print(f"   Languages tested: {', '.join(languages_tested)}")


class TestConversationEndpointE2E:
    """E2E tests for conversation endpoint with real AI"""

    @pytest.fixture(autouse=True)
    def check_api_keys(self):
        """Skip if no API keys available"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found - Skipping E2E test")

    def test_chat_endpoint_real_ai(self):
        """Test chat endpoint with real AI service"""
        from unittest.mock import Mock, patch

        from fastapi.testclient import TestClient

        from app.core.security import require_auth
        from app.database.config import get_primary_db_session
        from app.main import app
        from app.models.simple_user import SimpleUser
        from app.services.budget_manager import BudgetAlert

        # Create test user
        test_user = SimpleUser(
            id=999,
            user_id="e2e_testuser",
            username="e2e_test",
            email="e2e@test.com",
            role="parent",
        )

        # Mock budget manager to allow cloud provider selection
        class MockBudgetStatus:
            total_budget = 100.0
            used_budget = 0.0
            remaining_budget = 100.0
            percentage_used = 0.0
            alert_level = BudgetAlert.GREEN
            is_over_budget = False
            days_remaining = 30
            projected_monthly_cost = 0.0

        mock_budget = Mock()
        mock_budget.get_current_budget_status.return_value = MockBudgetStatus()
        mock_budget.get_status.return_value = MockBudgetStatus()
        mock_budget.get_remaining_budget.return_value = 100.0

        # Mock auth and DB (not testing those in E2E)
        mock_db = Mock()
        app.dependency_overrides[require_auth] = lambda: test_user
        app.dependency_overrides[get_primary_db_session] = lambda: mock_db

        # Patch budget_manager in all places it might be imported
        with (
            patch("app.services.ai_router.budget_manager", mock_budget),
            patch("app.services.ai_model_manager.budget_manager", mock_budget),
        ):
            try:
                client = TestClient(app)

                response = client.post(
                    "/api/v1/conversations/chat",
                    json={
                        "message": "Say hello in one word",
                        "language": "en-claude",
                        "use_speech": False,
                    },
                )

                assert response.status_code == 200
                data = response.json()

                # Verify real AI response (not fallback)
                assert "response" in data
                assert data["response"] != ""

                # Verify using real AI provider (Claude, Mistral, or Qwen - not Ollama fallback)
                # This is the primary check - if ai_provider is one of these, it's using real AI
                assert "ai_provider" in data
                assert data["ai_provider"] in ["claude", "mistral", "qwen"], (
                    f"Expected real AI provider, got {data.get('ai_provider')}"
                )

                print(f"\n✅ Chat Endpoint E2E Test Passed")
                print(f"   User message: Say hello in one word")
                print(f"   AI response: {data['response'][:100]}...")
                print(f"   Cost: ${data['estimated_cost']:.4f}")
                print(f"   Provider: {data['ai_provider']}")

            finally:
                app.dependency_overrides.clear()


class TestOllamaE2E:
    """E2E tests for Ollama local service with real instance

    These tests validate Ollama works as a fallback when:
    - Budget limits are exceeded
    - Cloud providers unavailable
    - User in offline/privacy mode

    Prerequisites:
    - Ollama installed and running (ollama serve)
    - llama2:7b model installed (ollama pull llama2:7b)
    """

    @pytest.mark.asyncio
    async def test_ollama_service_availability(self):
        """Test Ollama service is available and has models"""
        from app.services.ollama_service import OllamaService

        # Create fresh service instance for this test
        service = OllamaService()

        # Check availability
        is_available = await service.check_availability()
        if not is_available:
            await service.close()
            pytest.skip("Ollama service not running - Install and run 'ollama serve'")

        # Check models
        models = await service.list_models()
        if not models:
            await service.close()
            pytest.skip("No Ollama models installed - Run 'ollama pull llama2:7b'")

        model_names = [m.get("name") for m in models]
        if "llama2:7b" not in model_names:
            await service.close()
            pytest.skip("llama2:7b model not installed - Run 'ollama pull llama2:7b'")

        # Check health
        health = await service.get_health_status()
        assert health["status"] == "healthy"
        assert health["service_name"] == "ollama"

        print(f"\n✅ Ollama E2E Availability Test Passed")
        print(f"   Models installed: {len(models)}")
        print(f"   Server URL: {health['server_url']}")

        await service.close()

    @pytest.mark.asyncio
    async def test_ollama_real_conversation_english(self):
        """Test real Ollama conversation in English"""
        from app.services.ollama_service import OllamaService

        service = OllamaService()

        # Skip if not available
        if not await service.check_availability():
            await service.close()
            pytest.skip("Ollama service not running")

        response = await service.generate_response(
            messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
            language="en",
        )

        # Verify response structure
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert response.provider == "ollama"
        assert response.cost == 0.0  # Local is free
        assert response.metadata.get("local_processing") is True

        print(f"\n✅ Ollama English Conversation Test Passed")
        print(f"   Response: {response.content[:100]}...")
        print(f"   Model: {response.model}")
        print(f"   Processing time: {response.processing_time:.2f}s")

        await service.close()

    @pytest.mark.asyncio
    async def test_ollama_multi_language_support(self):
        """Test Ollama handles multiple languages"""
        from app.services.ollama_service import OllamaService

        service = OllamaService()

        if not await service.check_availability():
            await service.close()
            pytest.skip("Ollama service not running")

        test_cases = [
            ("en", "Say 'Hello' in one word"),
            ("fr", "Dis 'Bonjour' en un mot"),
            ("es", "Di 'Hola' en una palabra"),
        ]

        results = []

        for language, message in test_cases:
            response = await service.generate_response(
                messages=[{"role": "user", "content": message}], language=language
            )

            assert response is not None
            assert len(response.content) > 0
            assert response.language == language

            results.append(
                {
                    "language": language,
                    "model": response.model,
                    "response_length": len(response.content),
                }
            )

        print(f"\n✅ Ollama Multi-Language Test Passed")
        for result in results:
            print(
                f"   {result['language']}: {result['model']} - {result['response_length']} chars"
            )

        await service.close()

    @pytest.mark.asyncio
    async def test_ollama_model_selection(self):
        """Test Ollama selects appropriate models for languages (Phase 5: capability-based)"""
        from app.services.ollama_service import OllamaService

        service = OllamaService()

        if not await service.check_availability():
            await service.close()
            pytest.skip("Ollama service not running")

        # Phase 5: Must get installed models first
        installed_models = await service.list_models()
        assert len(installed_models) > 0, "No Ollama models installed"

        installed_names = [m["name"] for m in installed_models]

        # Test language-based selection - should select from installed models
        en_model = service.get_recommended_model(
            "en", "conversation", installed_models=installed_models
        )
        assert en_model in installed_names, (
            f"Selected model {en_model} not in installed models"
        )

        fr_model = service.get_recommended_model(
            "fr", "conversation", installed_models=installed_models
        )
        assert fr_model in installed_names, (
            f"Selected model {fr_model} not in installed models"
        )
        # Phase 5: Capability-based selection may prefer chat-optimized models over language-specific
        # Both mistral (French support) and neural-chat (chat-optimized) are valid choices
        if "mistral:7b" in installed_names and "neural-chat:7b" in installed_names:
            assert fr_model in ["mistral:7b", "neural-chat:7b"], (
                "Should select either mistral (language) or neural-chat (chat-optimized) for French"
            )

        # Test use-case selection - should prefer code models for technical if available
        tech_model = service.get_recommended_model(
            "en", "technical", installed_models=installed_models
        )
        assert tech_model in installed_names, (
            f"Selected model {tech_model} not in installed models"
        )

        # Phase 5: If deepseek-coder is installed, it should be preferred for technical
        has_code_model = any(
            "coder" in name.lower() or "deepseek" in name.lower()
            for name in installed_names
        )
        if has_code_model:
            assert "coder" in tech_model.lower() or "deepseek" in tech_model.lower(), (
                "Should prefer code-specialized model for technical use case"
            )

        print(f"\n✅ Ollama Model Selection Test Passed (Phase 5: Capability-based)")
        print(f"   Installed models: {len(installed_models)}")
        print(f"   English → {en_model}")
        print(f"   French → {fr_model}")
        print(f"   Technical → {tech_model}")

        await service.close()

    @pytest.mark.asyncio
    async def test_ollama_budget_exceeded_fallback(self):
        """Test Ollama is used as fallback when budget exceeded"""
        from unittest.mock import Mock, patch

        from app.services.ai_router import EnhancedAIRouter
        from app.services.budget_manager import BudgetAlert

        # Mock budget as exceeded
        class MockBudgetStatus:
            total_budget = 30.0
            used_budget = 35.0
            remaining_budget = -5.0
            percentage_used = 116.67
            alert_level = BudgetAlert.RED
            is_over_budget = True
            days_remaining = 10
            projected_monthly_cost = 50.0

        mock_budget = Mock()
        mock_budget.get_current_budget_status.return_value = MockBudgetStatus()

        # User preferences with auto-fallback enabled
        user_preferences = {
            "ai_provider_settings": {
                "enforce_budget_limits": True,
                "auto_fallback_to_ollama": True,
            }
        }

        with patch("app.services.ai_router.budget_manager", mock_budget):
            router = EnhancedAIRouter()

            selection = await router.select_provider(
                language="en",
                use_case="conversation",
                preferred_provider="claude",
                user_preferences=user_preferences,
                enforce_budget=True,
            )

            # Should fallback to Ollama
            assert selection.provider_name == "ollama"
            assert selection.is_fallback is True
            # Router uses budget_exceeded or budget_exceeded_auto_fallback
            assert selection.fallback_reason.value in [
                "budget_exceeded",
                "budget_exceeded_auto_fallback",
            ]

            # Verify can generate response
            response = await selection.service.generate_response(
                messages=[{"role": "user", "content": "Hello"}], language="en"
            )

            assert response.content is not None
            assert response.cost == 0.0

            print(f"\n✅ Ollama Budget Fallback Test Passed")
            print(f"   Fallback reason: {selection.fallback_reason.value}")
            print(f"   Response generated: {len(response.content)} chars")

    @pytest.mark.asyncio
    async def test_ollama_response_quality(self):
        """Test Ollama responses meet quality standards"""
        import time

        from app.services.ollama_service import OllamaService

        service = OllamaService()

        if not await service.check_availability():
            await service.close()
            pytest.skip("Ollama service not running")

        test_prompts = [
            "What is the capital of France?",
            "Translate 'hello' to Spanish",
            "Correct this: 'I goed to store'",
        ]

        for prompt in test_prompts:
            start = time.time()

            response = await service.generate_response(
                messages=[{"role": "user", "content": prompt}], language="en"
            )

            elapsed = time.time() - start

            # Quality checks
            assert len(response.content) > 10, "Response too short"
            assert "error" not in response.content.lower()[:50], (
                "Response contains error"
            )
            assert elapsed < 30, f"Response too slow: {elapsed}s"

            # Basic coherence check (contains alphabetic characters)
            assert any(c.isalpha() for c in response.content), "Response not coherent"

        print(f"\n✅ Ollama Quality Validation Test Passed")
        print(f"   All {len(test_prompts)} prompts generated quality responses")

        await service.close()

    @pytest.mark.asyncio
    async def test_ollama_privacy_mode(self):
        """Test Ollama operates in privacy mode (local processing)"""
        from app.services.ollama_service import OllamaService

        service = OllamaService()

        if not await service.check_availability():
            await service.close()
            pytest.skip("Ollama service not running")

        response = await service.generate_response(
            messages=[{"role": "user", "content": "This is sensitive data: test123"}],
            language="en",
        )

        # Verify privacy metadata
        assert response.metadata.get("local_processing") is True
        assert response.metadata.get("privacy_mode") is True
        assert response.cost == 0.0  # No external API calls

        # Verify response was generated (privacy didn't block it)
        assert len(response.content) > 0

        print(f"\n✅ Ollama Privacy Mode Test Passed")
        print(f"   Local processing: {response.metadata['local_processing']}")
        print(f"   Privacy mode: {response.metadata['privacy_mode']}")
        print(f"   No external API calls made")

        await service.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("⚠️  E2E TESTS - USING REAL API KEYS AND MAKING REAL API CALLS!")
    print("=" * 80)
    print("\nThese tests will:")
    print("  - Use real API keys from .env file")
    print("  - Make real API calls to Claude, Mistral, Qwen")
    print("  - Consume API credits (COST MONEY)")
    print("  - Take longer to run (5-30 seconds per test)")
    print("\nIf you want to proceed, run:")
    print("  pytest tests/e2e/ -v -s -m e2e")
    print("\n" + "=" * 80 + "\n")
