"""
Tests for Ollama API endpoints

Session 113: Complete coverage of app/api/ollama.py
Targeting exception handlers and edge cases
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.ollama import (
    get_ollama_status,
    get_recommended_models,
    list_ollama_models,
)


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {"username": "testuser", "user_id": 1}


@pytest.fixture
def mock_ollama_service():
    """Mock ollama service"""
    with patch("app.api.ollama.ollama_service") as mock:
        yield mock


class TestListOllamaModels:
    """Test list_ollama_models endpoint"""

    @pytest.mark.asyncio
    async def test_list_models_success_with_capabilities(
        self, mock_user, mock_ollama_service
    ):
        """Test successful model listing with capabilities analysis"""
        # Setup
        mock_ollama_service.check_availability = AsyncMock(return_value=True)
        mock_ollama_service.list_models = AsyncMock(
            return_value=[
                {"name": "llama2:7b", "size": "3.8GB"},
                {"name": "codellama:7b", "size": "3.8GB"},
            ]
        )
        mock_ollama_service._analyze_model_capabilities = MagicMock(
            return_value={
                "is_code_model": False,
                "is_multilingual": True,
                "is_chat_optimized": True,
                "language_support": ["en", "es"],
                "size_category": "medium",
            }
        )

        # Execute
        result = await list_ollama_models(current_user=mock_user)

        # Verify
        assert result["available"] is True
        assert len(result["models"]) == 2
        assert len(result["model_capabilities"]) == 2
        assert result["message"] == "2 Ollama model(s) available"
        assert result["model_capabilities"][0]["name"] == "llama2:7b"

    @pytest.mark.asyncio
    async def test_list_models_service_not_available(
        self, mock_user, mock_ollama_service
    ):
        """Test when Ollama service is not running"""
        # Setup
        mock_ollama_service.check_availability = AsyncMock(return_value=False)

        # Execute
        result = await list_ollama_models(current_user=mock_user)

        # Verify
        assert result["available"] is False
        assert result["models"] == []
        assert result["recommended"] == {}
        assert "not running" in result["message"]

    @pytest.mark.asyncio
    async def test_list_models_with_empty_model_name(
        self, mock_user, mock_ollama_service
    ):
        """Test handling of models with empty names"""
        # Setup
        mock_ollama_service.check_availability = AsyncMock(return_value=True)
        mock_ollama_service.list_models = AsyncMock(
            return_value=[
                {"name": "llama2:7b", "size": "3.8GB"},
                {"name": "", "size": "1.0GB"},  # Empty name
                {"size": "2.0GB"},  # Missing name
            ]
        )
        mock_ollama_service._analyze_model_capabilities = MagicMock(
            return_value={
                "is_code_model": False,
                "is_multilingual": True,
                "is_chat_optimized": True,
                "language_support": ["en"],
                "size_category": "small",
            }
        )

        # Execute
        result = await list_ollama_models(current_user=mock_user)

        # Verify - should only have capabilities for valid model
        assert result["available"] is True
        assert len(result["models"]) == 3
        assert len(result["model_capabilities"]) == 1  # Only valid name
        assert result["model_capabilities"][0]["name"] == "llama2:7b"

    @pytest.mark.asyncio
    async def test_list_models_exception_handling(self, mock_user, mock_ollama_service):
        """Test exception handling in list_ollama_models - COVERS LINES 88-89"""
        # Setup - force an exception
        mock_ollama_service.check_availability = AsyncMock(
            side_effect=Exception("Service error")
        )

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await list_ollama_models(current_user=mock_user)

        assert exc_info.value.status_code == 500
        assert "Error listing Ollama models" in str(exc_info.value.detail)
        assert "Service error" in str(exc_info.value.detail)


class TestGetRecommendedModels:
    """Test get_recommended_models endpoint"""

    @pytest.mark.asyncio
    async def test_get_recommended_success(self, mock_user, mock_ollama_service):
        """Test successful recommendation"""
        # Setup
        mock_ollama_service.list_models = AsyncMock(
            return_value=[
                {"name": "llama2:7b"},
                {"name": "codellama:7b"},
                {"name": "mistral:7b"},
            ]
        )
        mock_ollama_service.get_recommended_model = MagicMock(
            return_value="codellama:7b"
        )

        # Execute
        result = await get_recommended_models(
            language="en", use_case="technical", current_user=mock_user
        )

        # Verify
        assert result["language"] == "en"
        assert result["use_case"] == "technical"
        assert result["recommended_model"] == "codellama:7b"
        assert "llama2:7b" in result["alternatives"]
        assert "mistral:7b" in result["alternatives"]
        assert "codellama:7b" not in result["alternatives"]
        assert "3 installed model(s)" in result["message"]

    @pytest.mark.asyncio
    async def test_get_recommended_no_models_installed(
        self, mock_user, mock_ollama_service
    ):
        """Test when no models are installed"""
        # Setup
        mock_ollama_service.list_models = AsyncMock(return_value=[])

        # Execute
        result = await get_recommended_models(
            language="fr", use_case="conversation", current_user=mock_user
        )

        # Verify
        assert result["language"] == "fr"
        assert result["use_case"] == "conversation"
        assert result["recommended_model"] is None
        assert result["alternatives"] == []
        assert "No Ollama models installed" in result["message"]

    @pytest.mark.asyncio
    async def test_get_recommended_default_parameters(
        self, mock_user, mock_ollama_service
    ):
        """Test with default language and use_case"""
        # Setup
        mock_ollama_service.list_models = AsyncMock(
            return_value=[
                {"name": "llama2:7b"},
            ]
        )
        mock_ollama_service.get_recommended_model = MagicMock(return_value="llama2:7b")

        # Execute (using defaults: language="en", use_case="conversation")
        result = await get_recommended_models(current_user=mock_user)

        # Verify
        assert result["language"] == "en"
        assert result["use_case"] == "conversation"
        assert result["recommended_model"] == "llama2:7b"

    @pytest.mark.asyncio
    async def test_get_recommended_exception_handling(
        self, mock_user, mock_ollama_service
    ):
        """Test exception handling in get_recommended_models - COVERS LINES 158-159"""
        # Setup - force an exception
        mock_ollama_service.list_models = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await get_recommended_models(
                language="es", use_case="grammar", current_user=mock_user
            )

        assert exc_info.value.status_code == 500
        assert "Error getting recommended model" in str(exc_info.value.detail)
        assert "Database error" in str(exc_info.value.detail)


class TestGetOllamaStatus:
    """Test get_ollama_status endpoint"""

    @pytest.mark.asyncio
    async def test_get_status_available_with_models(
        self, mock_user, mock_ollama_service
    ):
        """Test status when Ollama is available with models"""
        # Setup
        mock_ollama_service.check_availability = AsyncMock(return_value=True)
        mock_ollama_service.list_models = AsyncMock(
            return_value=[
                {"name": "llama2:7b"},
                {"name": "codellama:7b"},
                {"name": "mistral:7b"},
            ]
        )

        # Execute
        result = await get_ollama_status(current_user=mock_user)

        # Verify
        assert result["available"] is True
        assert result["version"] == "unknown"
        assert result["models_count"] == 3
        assert "running with 3 model(s)" in result["message"]

    @pytest.mark.asyncio
    async def test_get_status_available_no_models(self, mock_user, mock_ollama_service):
        """Test status when Ollama is available but no models installed"""
        # Setup
        mock_ollama_service.check_availability = AsyncMock(return_value=True)
        mock_ollama_service.list_models = AsyncMock(return_value=[])

        # Execute
        result = await get_ollama_status(current_user=mock_user)

        # Verify
        assert result["available"] is True
        assert result["models_count"] == 0
        assert "0 model(s)" in result["message"]

    @pytest.mark.asyncio
    async def test_get_status_not_available(self, mock_user, mock_ollama_service):
        """Test status when Ollama is not running"""
        # Setup
        mock_ollama_service.check_availability = AsyncMock(return_value=False)

        # Execute
        result = await get_ollama_status(current_user=mock_user)

        # Verify
        assert result["available"] is False
        assert result["version"] is None
        assert result["models_count"] == 0
        assert "not running" in result["message"]

    @pytest.mark.asyncio
    async def test_get_status_exception_handling(self, mock_user, mock_ollama_service):
        """Test exception handling in get_ollama_status - COVERS LINES 206-207"""
        # Setup - force an exception
        mock_ollama_service.check_availability = AsyncMock(
            side_effect=Exception("Connection timeout")
        )

        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await get_ollama_status(current_user=mock_user)

        assert exc_info.value.status_code == 500
        assert "Error checking Ollama status" in str(exc_info.value.detail)
        assert "Connection timeout" in str(exc_info.value.detail)
