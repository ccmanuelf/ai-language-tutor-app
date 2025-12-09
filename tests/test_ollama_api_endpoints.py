"""
API tests for Ollama endpoints.

Tests validate the Ollama API endpoint logic created in Session 98 Phase 3.
These tests call the endpoint functions directly to validate logic.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.ollama import get_ollama_status, get_recommended_models, list_ollama_models
from app.services.ollama_service import OllamaService


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return MagicMock(user_id="test_user")


class TestOllamaAPIEndpoints:
    """Tests for Ollama API endpoints"""

    @pytest.mark.asyncio
    async def test_list_ollama_models_when_unavailable(self, mock_user):
        """Test list_ollama_models when Ollama is not running"""
        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail:
            mock_avail.return_value = False

            result = await list_ollama_models(current_user=mock_user)

            assert result["available"] is False
            assert result["models"] == []
            assert "not running" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_list_ollama_models_when_available(self, mock_user):
        """Test list_ollama_models when Ollama is running"""
        mock_models = [
            {
                "name": "llama2:7b",
                "size": 3800000000,
                "modified": "2024-01-15T10:30:00Z",
            },
            {
                "name": "mistral:7b",
                "size": 4100000000,
                "modified": "2024-01-16T14:20:00Z",
            },
        ]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_models

            result = await list_ollama_models(current_user=mock_user)

            assert result["available"] is True
            assert len(result["models"]) == 2
            assert result["models"][0]["name"] == "llama2:7b"
            assert "recommended" in result
            assert "en" in result["recommended"]
            assert "2 Ollama" in result["message"]

    @pytest.mark.asyncio
    async def test_list_ollama_models_recommended_structure(self, mock_user):
        """Test that recommended models are properly structured"""
        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = []

            result = await list_ollama_models(current_user=mock_user)

            recommended = result["recommended"]

            # Check key languages have recommendations
            assert "en" in recommended
            assert "fr" in recommended
            assert "es" in recommended

            # Check English has expected models
            assert "neural-chat:7b" in recommended["en"]
            assert "llama2:7b" in recommended["en"]

    @pytest.mark.asyncio
    async def test_get_recommended_model_default_params(self, mock_user):
        """Test get_recommended_models with default params"""
        with patch.object(
            OllamaService, "get_recommended_model", return_value="neural-chat:7b"
        ) as mock_recommend:
            result = await get_recommended_models(current_user=mock_user)

            assert result["language"] == "en"  # Default
            assert result["use_case"] == "conversation"  # Default
            assert result["recommended_model"] == "neural-chat:7b"
            assert "alternatives" in result
            mock_recommend.assert_called_once_with("en", "conversation")

    @pytest.mark.asyncio
    async def test_get_recommended_model_with_language(self, mock_user):
        """Test get_recommended_models with language parameter"""
        with patch.object(
            OllamaService, "get_recommended_model", return_value="mistral:7b"
        ) as mock_recommend:
            result = await get_recommended_models(language="fr", current_user=mock_user)

            assert result["language"] == "fr"
            assert result["recommended_model"] == "mistral:7b"
            assert "llama2:7b" in result["alternatives"]  # Alternative for French
            mock_recommend.assert_called_once_with("fr", "conversation")

    @pytest.mark.asyncio
    async def test_get_recommended_model_with_use_case(self, mock_user):
        """Test get_recommended_models with use_case parameter"""
        with patch.object(
            OllamaService, "get_recommended_model", return_value="codellama:7b"
        ) as mock_recommend:
            result = await get_recommended_models(
                language="en", use_case="technical", current_user=mock_user
            )

            assert result["language"] == "en"
            assert result["use_case"] == "technical"
            assert result["recommended_model"] == "codellama:7b"
            mock_recommend.assert_called_once_with("en", "technical")

    @pytest.mark.asyncio
    async def test_get_recommended_model_alternatives_exclude_recommended(
        self, mock_user
    ):
        """Test that alternatives don't include the recommended model"""
        with patch.object(
            OllamaService, "get_recommended_model", return_value="neural-chat:7b"
        ):
            result = await get_recommended_models(language="en", current_user=mock_user)

            assert result["recommended_model"] == "neural-chat:7b"
            # neural-chat:7b should NOT be in alternatives
            assert "neural-chat:7b" not in result["alternatives"]
            # But other English models should be
            assert (
                "llama2:7b" in result["alternatives"]
                or "codellama:7b" in result["alternatives"]
            )

    @pytest.mark.asyncio
    async def test_get_ollama_status_when_unavailable(self, mock_user):
        """Test get_ollama_status when Ollama is not running"""
        with patch.object(
            OllamaService, "check_availability", new_callable=AsyncMock
        ) as mock_avail:
            mock_avail.return_value = False

            result = await get_ollama_status(current_user=mock_user)

            assert result["available"] is False
            assert result["models_count"] == 0
            assert "not running" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_get_ollama_status_when_available(self, mock_user):
        """Test get_ollama_status when Ollama is running"""
        mock_models = [
            {"name": "llama2:7b"},
            {"name": "mistral:7b"},
            {"name": "neural-chat:7b"},
        ]

        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
        ):
            mock_avail.return_value = True
            mock_list.return_value = mock_models

            result = await get_ollama_status(current_user=mock_user)

            assert result["available"] is True
            assert result["models_count"] == 3
            assert "3 model" in result["message"]

    @pytest.mark.asyncio
    async def test_all_endpoints_validate_logic(self, mock_user):
        """Test that all endpoint functions execute without errors"""
        with (
            patch.object(
                OllamaService, "check_availability", new_callable=AsyncMock
            ) as mock_avail,
            patch.object(
                OllamaService, "list_models", new_callable=AsyncMock
            ) as mock_list,
            patch.object(
                OllamaService, "get_recommended_model", return_value="llama2:7b"
            ),
        ):
            mock_avail.return_value = True
            mock_list.return_value = []

            # All these should execute without errors
            result1 = await list_ollama_models(current_user=mock_user)
            result2 = await get_recommended_models(current_user=mock_user)
            result3 = await get_ollama_status(current_user=mock_user)

            # Basic validation
            assert "available" in result1
            assert "recommended_model" in result2
            assert "models_count" in result3
