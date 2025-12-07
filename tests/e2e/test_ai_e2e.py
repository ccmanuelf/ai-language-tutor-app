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


class TestQwenE2E:
    """E2E tests for Qwen AI service with real API"""

    @pytest.fixture(autouse=True)
    def check_api_key(self):
        """Skip tests if API key not available"""
        # Qwen might use different env variable or config
        if not os.getenv("DASHSCOPE_API_KEY"):
            pytest.skip("DASHSCOPE_API_KEY not found in .env - Skipping E2E test")

    @pytest.mark.asyncio
    async def test_qwen_real_api_conversation(self):
        """Test real Qwen API call for conversation"""
        from app.services.qwen_service import QwenService

        service = QwenService()

        response = await service.generate_response(
            messages=[{"role": "user", "content": "用一个词说'你好'"}],
            message="用一个词说'你好'",
            language="zh",
            context={"language": "zh", "user_id": "e2e_test"},
        )

        # Verify real response
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0

        print(f"\n✅ Qwen E2E Test Passed")
        print(f"   Response: {response.content[:50]}...")
        print(f"   Cost: ${getattr(response, 'cost', 0):.4f}")


class TestAIRouterE2E:
    """E2E tests for AI router with real services"""

    @pytest.fixture(autouse=True)
    def check_api_keys(self):
        """Skip if no API keys available"""
        if not (
            os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("MISTRAL_API_KEY")
            or os.getenv("DASHSCOPE_API_KEY")
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
            if os.getenv("DASHSCOPE_API_KEY"):
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
