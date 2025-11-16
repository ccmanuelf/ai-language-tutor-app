"""
Comprehensive tests for Ollama Service
Achieves >90% test coverage for ollama_service.py
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import aiohttp
import pytest

from app.services.ai_service_base import AIResponse
from app.services.ollama_service import (
    OllamaManager,
    OllamaModel,
    OllamaModelSize,
    OllamaService,
    generate_local_response,
    get_ollama_status,
    is_ollama_available,
    ollama_manager,
    ollama_service,
    setup_ollama_for_language_learning,
)


class TestOllamaServiceInitialization:
    """Test Ollama service initialization"""

    def test_service_initialization(self):
        """Test service initializes with correct defaults"""
        service = OllamaService()
        assert service.service_name == "ollama"
        assert service.default_model == "llama2:7b"
        assert "localhost" in service.base_url or "11434" in service.base_url
        assert service.session is None
        assert len(service.available_models) > 0

    def test_get_available_models(self):
        """Test getting available models dictionary"""
        service = OllamaService()
        models = service._get_available_models()

        assert "llama2:7b" in models
        assert "mistral:7b" in models
        assert isinstance(models["llama2:7b"], OllamaModel)
        assert models["llama2:7b"].size == OllamaModelSize.SMALL

    def test_available_models_structure(self):
        """Test available models have correct structure"""
        service = OllamaService()

        for model_name, model in service.available_models.items():
            assert isinstance(model, OllamaModel)
            assert model.name == model_name
            assert isinstance(model.languages, list)
            assert len(model.languages) > 0
            assert model.memory_gb > 0


class TestSessionManagement:
    """Test HTTP session management"""

    @pytest.mark.asyncio
    async def test_get_session_creates_new(self):
        """Test getting session creates new one if none exists"""
        service = OllamaService()

        session = await service._get_session()

        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)
        assert not session.closed

        await session.close()

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing(self):
        """Test getting session reuses existing open session"""
        service = OllamaService()

        session1 = await service._get_session()
        session2 = await service._get_session()

        assert session1 is session2

        await session1.close()

    @pytest.mark.asyncio
    async def test_get_session_recreates_if_closed(self):
        """Test getting session recreates if previous was closed"""
        service = OllamaService()

        session1 = await service._get_session()
        await session1.close()

        session2 = await service._get_session()

        assert session1 is not session2
        assert not session2.closed

        await session2.close()


class TestCheckAvailability:
    """Test Ollama availability checking"""

    @pytest.mark.asyncio
    async def test_check_availability_success(self):
        """Test availability check when server is running"""
        service = OllamaService()

        # Create proper async context manager mock
        mock_response = Mock()
        mock_response.status = 200

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.check_availability()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_availability_server_error(self):
        """Test availability check when server returns error"""
        service = OllamaService()

        mock_response = Mock()
        mock_response.status = 500

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.check_availability()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_availability_connection_error(self):
        """Test availability check when connection fails"""
        service = OllamaService()

        mock_session = Mock()
        mock_session.get = Mock(side_effect=aiohttp.ClientError("Connection refused"))

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.check_availability()

        assert result is False


class TestListModels:
    """Test listing installed models"""

    @pytest.mark.asyncio
    async def test_list_models_success(self):
        """Test listing models when server returns models"""
        service = OllamaService()

        mock_models = {
            "models": [
                {"name": "llama2:7b", "size": 3800000000},
                {"name": "mistral:7b", "size": 4100000000},
            ]
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_models)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.list_models()

        assert len(result) == 2
        assert result[0]["name"] == "llama2:7b"

    @pytest.mark.asyncio
    async def test_list_models_empty(self):
        """Test listing models when no models installed"""
        service = OllamaService()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"models": []})

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.list_models()

        assert result == []

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        """Test listing models when request fails"""
        service = OllamaService()

        mock_session = Mock()
        mock_session.get = Mock(side_effect=Exception("Connection error"))

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.list_models()

        assert result == []


class TestPullModel:
    """Test pulling/downloading models"""

    @pytest.mark.asyncio
    async def test_pull_model_success(self):
        """Test successful model pull"""
        service = OllamaService()

        # Mock streaming response with progress updates
        progress_lines = [
            b'{"status": "downloading", "completed": 0}\n',
            b'{"status": "downloading", "completed": 50}\n',
            b'{"status": "success", "completed": 100}\n',
        ]

        async def mock_content_iter():
            for line in progress_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.pull_model("llama2:7b")

        assert result is True

    @pytest.mark.asyncio
    async def test_pull_model_server_error(self):
        """Test model pull when server returns error"""
        service = OllamaService()

        mock_response = Mock()
        mock_response.status = 500

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.pull_model("llama2:7b")

        assert result is False

    @pytest.mark.asyncio
    async def test_pull_model_connection_error(self):
        """Test model pull when connection fails"""
        service = OllamaService()

        mock_session = Mock()
        mock_session.post = Mock(side_effect=Exception("Connection error"))

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.pull_model("llama2:7b")

        assert result is False

    @pytest.mark.asyncio
    async def test_pull_model_progress_without_status_key(self):
        """Test model pull when progress doesn't have 'status' key (branch 153->150)"""
        service = OllamaService()

        # Mock streaming response with progress data lacking "status" key
        progress_lines = [
            b'{"digest": "sha256:abc123", "total": 1000}\n',  # No "status" key
            b'{"completed": 500, "total": 1000}\n',  # No "status" key
            b'{"status": "success"}\n',  # Has "status" key
        ]

        async def mock_content_iter():
            for line in progress_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.pull_model("llama2:7b")

        # Should return True for successful pull
        assert result is True


class TestEnsureModelAvailable:
    """Test ensuring model availability"""

    @pytest.mark.asyncio
    async def test_ensure_model_already_installed(self):
        """Test ensuring model when already installed"""
        service = OllamaService()

        mock_models = [{"name": "llama2:7b"}]

        with patch.object(service, "list_models", return_value=mock_models):
            result = await service.ensure_model_available("llama2:7b")

        assert result is True

    @pytest.mark.asyncio
    async def test_ensure_model_needs_pull(self):
        """Test ensuring model when needs to be pulled"""
        service = OllamaService()

        mock_models = []

        with patch.object(service, "list_models", return_value=mock_models):
            with patch.object(service, "pull_model", return_value=True):
                result = await service.ensure_model_available("llama2:7b")

        assert result is True

    @pytest.mark.asyncio
    async def test_ensure_model_pull_fails(self):
        """Test ensuring model when pull fails"""
        service = OllamaService()

        mock_models = []

        with patch.object(service, "list_models", return_value=mock_models):
            with patch.object(service, "pull_model", return_value=False):
                result = await service.ensure_model_available("llama2:7b")

        assert result is False


class TestGetRecommendedModel:
    """Test model recommendation logic"""

    def test_get_recommended_model_english(self):
        """Test recommended model for English"""
        service = OllamaService()

        model = service.get_recommended_model("en")

        assert model in ["neural-chat:7b", "llama2:7b", "codellama:7b"]

    def test_get_recommended_model_french(self):
        """Test recommended model for French"""
        service = OllamaService()

        model = service.get_recommended_model("fr")

        assert model == "mistral:7b"

    def test_get_recommended_model_technical_english(self):
        """Test recommended model for technical English"""
        service = OllamaService()

        model = service.get_recommended_model("en", "technical")

        assert model == "codellama:7b"

    def test_get_recommended_model_grammar_spanish(self):
        """Test recommended model for Spanish grammar"""
        service = OllamaService()

        model = service.get_recommended_model("es", "grammar")

        assert model == "llama2:13b"

    def test_get_recommended_model_unknown_language(self):
        """Test recommended model for unknown language defaults to llama2"""
        service = OllamaService()

        model = service.get_recommended_model("unknown")

        assert model == "llama2:7b"


class TestGenerateResponse:
    """Test response generation"""

    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        mock_api_response = {
            "response": "Hello! How can I help you learn today?",
            "done": True,
            "context": [1, 2, 3],
            "total_duration": 1000000000,
            "load_duration": 100000000,
            "prompt_eval_count": 5,
            "eval_count": 10,
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                result = await service.generate_response(messages, language="en")

        assert isinstance(result, AIResponse)
        assert result.content == "Hello! How can I help you learn today?"
        assert result.provider == "ollama"
        assert result.cost == 0.0
        assert result.metadata["local_processing"] is True

    @pytest.mark.asyncio
    async def test_generate_response_model_not_available(self):
        """Test response generation when model cannot be obtained"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        with patch.object(service, "ensure_model_available", return_value=False):
            with pytest.raises(Exception) as exc_info:
                await service.generate_response(messages, language="en")

        assert "not available" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self):
        """Test response generation when API returns error"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                with pytest.raises(Exception) as exc_info:
                    await service.generate_response(messages, language="en")

        assert "ollama api error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_response_with_custom_model(self):
        """Test response generation with custom model"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        mock_api_response = {"response": "Response text", "done": True}

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                result = await service.generate_response(
                    messages, language="en", model="mistral:7b"
                )

        assert result.model == "mistral:7b"


class TestFormatPrompt:
    """Test prompt formatting for language learning"""

    def test_format_prompt_english(self):
        """Test prompt formatting for English"""
        service = OllamaService()

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        prompt = service._format_prompt_for_language_learning(messages, "en")

        assert "English language tutor" in prompt
        assert "Student: Hello" in prompt
        assert "Tutor: Hi there!" in prompt
        assert "Student: How are you?" in prompt
        assert prompt.endswith("Tutor: ")

    def test_format_prompt_french(self):
        """Test prompt formatting for French"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Bonjour"}]

        prompt = service._format_prompt_for_language_learning(messages, "fr")

        assert "français" in prompt
        assert "Student: Bonjour" in prompt

    def test_format_prompt_spanish(self):
        """Test prompt formatting for Spanish"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hola"}]

        prompt = service._format_prompt_for_language_learning(messages, "es")

        assert "español" in prompt
        assert "Student: Hola" in prompt

    def test_format_prompt_unknown_language(self):
        """Test prompt formatting for unknown language"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        prompt = service._format_prompt_for_language_learning(messages, "unknown")

        assert "language tutor" in prompt
        assert "Student: Hello" in prompt

    def test_format_prompt_with_system_role(self):
        """Test prompt formatting with non-user/assistant roles (branch 377->371)"""
        service = OllamaService()

        messages = [
            {"role": "system", "content": "You are a helpful tutor"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
            {"role": "function", "content": "Some function output"},
        ]

        prompt = service._format_prompt_for_language_learning(messages, "en")

        # System and function roles should be skipped (else branch)
        # Only user and assistant should be formatted
        assert "Student: Hello" in prompt
        assert "Tutor: Hi!" in prompt
        # System and function content should not appear as Student/Tutor
        assert "Student: You are a helpful tutor" not in prompt
        assert "Tutor: You are a helpful tutor" not in prompt
        assert "Student: Some function output" not in prompt
        assert "Tutor: Some function output" not in prompt


class TestGetHealthStatus:
    """Test health status checking"""

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self):
        """Test health status when server is healthy"""
        service = OllamaService()

        mock_models = [{"name": "llama2:7b"}, {"name": "mistral:7b"}]

        with patch.object(service, "check_availability", return_value=True):
            with patch.object(service, "list_models", return_value=mock_models):
                status = await service.get_health_status()

        assert status["service_name"] == "ollama"
        assert status["status"] == "healthy"
        assert status["models_installed"] == 2
        assert "llama2:7b" in status["available_models"]

    @pytest.mark.asyncio
    async def test_get_health_status_unavailable(self):
        """Test health status when server is unavailable"""
        service = OllamaService()

        with patch.object(service, "check_availability", return_value=False):
            status = await service.get_health_status()

        assert status["status"] == "unavailable"
        assert "recommendations" in status
        assert len(status["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_get_health_status_error(self):
        """Test health status when check fails"""
        service = OllamaService()

        with patch.object(
            service, "check_availability", side_effect=Exception("Network error")
        ):
            status = await service.get_health_status()

        assert status["status"] == "error"
        assert "error" in status


class TestOllamaManager:
    """Test Ollama manager functionality"""

    @pytest.mark.asyncio
    async def test_check_installation_not_installed(self):
        """Test installation check when Ollama not running"""
        manager = OllamaManager()

        mock_status = {"status": "unavailable", "recommendations": ["Install Ollama"]}

        with patch.object(
            manager.service, "get_health_status", return_value=mock_status
        ):
            result = await manager.check_installation()

        assert result["installed"] is False
        assert result["running"] is False
        assert result["setup_required"] is True

    @pytest.mark.asyncio
    async def test_check_installation_installed_no_models(self):
        """Test installation check when installed but no models"""
        manager = OllamaManager()

        mock_status = {"status": "healthy"}

        with patch.object(
            manager.service, "get_health_status", return_value=mock_status
        ):
            with patch.object(manager.service, "list_models", return_value=[]):
                result = await manager.check_installation()

        assert result["installed"] is True
        assert result["running"] is True
        assert result["setup_required"] is True

    @pytest.mark.asyncio
    async def test_check_installation_ready(self):
        """Test installation check when fully set up"""
        manager = OllamaManager()

        mock_status = {"status": "healthy"}
        mock_models = [{"name": "llama2:7b"}]

        with patch.object(
            manager.service, "get_health_status", return_value=mock_status
        ):
            with patch.object(manager.service, "list_models", return_value=mock_models):
                result = await manager.check_installation()

        assert result["installed"] is True
        assert result["running"] is True
        assert result["models"] == 1
        assert result["setup_required"] is False

    def test_get_recommended_setup(self):
        """Test getting recommended setup commands"""
        manager = OllamaManager()

        commands = manager._get_recommended_setup()

        assert len(commands) > 0
        assert any("llama2:7b" in cmd for cmd in commands)
        assert any("mistral:7b" in cmd for cmd in commands)

    @pytest.mark.asyncio
    async def test_setup_for_language_learning_server_unavailable(self):
        """Test setup when server is not available"""
        manager = OllamaManager()

        with patch.object(manager.service, "check_availability", return_value=False):
            result = await manager.setup_for_language_learning()

        assert result["success"] is False
        assert "not available" in result["message"]

    @pytest.mark.asyncio
    async def test_setup_for_language_learning_success(self):
        """Test successful setup"""
        manager = OllamaManager()

        with patch.object(manager.service, "check_availability", return_value=True):
            with patch.object(manager.service, "pull_model", return_value=True):
                result = await manager.setup_for_language_learning()

        assert result["success"] is True
        assert len(result["models_setup"]) > 0

    @pytest.mark.asyncio
    async def test_setup_for_language_learning_partial_success(self):
        """Test setup with some models failing"""
        manager = OllamaManager()

        def mock_pull(model_name):
            return model_name == "llama2:7b"  # Only llama2 succeeds

        with patch.object(manager.service, "check_availability", return_value=True):
            with patch.object(manager.service, "pull_model", side_effect=mock_pull):
                result = await manager.setup_for_language_learning()

        assert result["success"] is True  # At least one succeeded
        assert "llama2:7b" in result["models_setup"]


class TestGlobalInstances:
    """Test global instances and convenience functions"""

    def test_global_ollama_service_exists(self):
        """Test global ollama_service instance exists"""
        assert ollama_service is not None
        assert isinstance(ollama_service, OllamaService)

    def test_global_ollama_manager_exists(self):
        """Test global ollama_manager instance exists"""
        assert ollama_manager is not None
        assert isinstance(ollama_manager, OllamaManager)


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.mark.asyncio
    async def test_get_ollama_status(self):
        """Test get_ollama_status convenience function"""
        mock_status = {"status": "healthy"}

        with patch.object(
            ollama_service, "get_health_status", return_value=mock_status
        ):
            result = await get_ollama_status()

        assert result == mock_status

    @pytest.mark.asyncio
    async def test_is_ollama_available(self):
        """Test is_ollama_available convenience function"""
        with patch.object(ollama_service, "check_availability", return_value=True):
            result = await is_ollama_available()

        assert result is True

    @pytest.mark.asyncio
    async def test_generate_local_response(self):
        """Test generate_local_response convenience function"""
        messages = [{"role": "user", "content": "Hello"}]
        mock_response = AIResponse(
            content="Hello!",
            model="llama2:7b",
            provider="ollama",
            language="en",
            processing_time=1.0,
            cost=0.0,
        )

        with patch.object(
            ollama_service, "generate_response", return_value=mock_response
        ):
            result = await generate_local_response(messages, language="en")

        assert result == mock_response

    @pytest.mark.asyncio
    async def test_setup_ollama_for_language_learning(self):
        """Test setup_ollama_for_language_learning convenience function"""
        mock_result = {"success": True}

        with patch.object(
            ollama_manager, "setup_for_language_learning", return_value=mock_result
        ):
            result = await setup_ollama_for_language_learning()

        assert result == mock_result


class TestCloseSession:
    """Test session cleanup"""

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test closing HTTP session"""
        service = OllamaService()

        # Create a session
        session = await service._get_session()
        assert not session.closed

        # Close it
        await service.close()

        assert service.session.closed

    @pytest.mark.asyncio
    async def test_close_no_session(self):
        """Test closing when no session exists"""
        service = OllamaService()

        # Should not raise error
        await service.close()

        assert True  # No exception raised


class TestGenerateStreamingResponse:
    """Test streaming response generation"""

    @pytest.mark.asyncio
    async def test_generate_streaming_response_success(self):
        """Test successful streaming response generation"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        # Mock streaming chunks
        chunk_lines = [
            b'{"response": "Hello ", "done": false}\n',
            b'{"response": "there!", "done": false}\n',
            b'{"response": "", "done": true, "context": [1, 2, 3]}\n',
        ]

        async def mock_content_iter():
            for line in chunk_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        chunks = []
        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                async for chunk in service.generate_streaming_response(
                    messages, language="en"
                ):
                    chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0].content == "Hello "
        assert chunks[0].is_final is False
        assert chunks[2].is_final is True

    @pytest.mark.asyncio
    async def test_generate_streaming_response_model_not_available(self):
        """Test streaming when model not available"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        with patch.object(service, "ensure_model_available", return_value=False):
            with pytest.raises(Exception) as exc_info:
                async for chunk in service.generate_streaming_response(
                    messages, language="en"
                ):
                    pass

        assert "not available" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_streaming_response_api_error(self):
        """Test streaming when API returns error"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                with pytest.raises(Exception) as exc_info:
                    async for chunk in service.generate_streaming_response(
                        messages, language="en"
                    ):
                        pass

        assert "ollama streaming error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_streaming_response_with_custom_model(self):
        """Test streaming with custom model"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        chunk_lines = [b'{"response": "Hi", "done": true}\n']

        async def mock_content_iter():
            for line in chunk_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        chunks = []
        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                async for chunk in service.generate_streaming_response(
                    messages, language="en", model="mistral:7b"
                ):
                    chunks.append(chunk)

        assert chunks[0].model == "mistral:7b"

    @pytest.mark.asyncio
    async def test_generate_streaming_response_invalid_json(self):
        """Test streaming handles invalid JSON gracefully"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        # Mix valid and invalid JSON
        chunk_lines = [
            b'{"response": "Valid", "done": false}\n',
            b"Invalid JSON here\n",
            b'{"response": " chunk", "done": true}\n',
        ]

        async def mock_content_iter():
            for line in chunk_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        chunks = []
        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                async for chunk in service.generate_streaming_response(
                    messages, language="en"
                ):
                    chunks.append(chunk)

        # Should have 2 valid chunks (invalid JSON skipped)
        assert len(chunks) == 2
        assert chunks[0].content == "Valid"
        assert chunks[1].content == " chunk"

    @pytest.mark.asyncio
    async def test_generate_streaming_response_chunk_without_response_key(self):
        """Test streaming when chunk doesn't have 'response' key (branch 319->315)"""
        service = OllamaService()

        messages = [{"role": "user", "content": "Hello"}]

        # Mix chunks with and without "response" key
        chunk_lines = [
            b'{"response": "Hello", "done": false}\n',
            b'{"status": "processing", "done": false}\n',  # No "response" key
            b'{"model": "llama2", "done": false}\n',  # No "response" key
            b'{"response": " world", "done": true}\n',
        ]

        async def mock_content_iter():
            for line in chunk_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        chunks = []
        with patch.object(service, "_get_session", side_effect=mock_get_session):
            with patch.object(service, "ensure_model_available", return_value=True):
                async for chunk in service.generate_streaming_response(
                    messages, language="en"
                ):
                    chunks.append(chunk)

        # Should only yield chunks with "response" key
        assert len(chunks) == 2
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " world"


class TestExceptionHandling:
    """Test exception handling in error paths"""

    @pytest.mark.asyncio
    async def test_list_models_with_non_200_status(self):
        """Test list_models returns empty list when status is not 200"""
        service = OllamaService()

        # Mock response with non-200 status
        mock_response = Mock()
        mock_response.status = 404

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.list_models()

        # Should return empty list when status is not 200
        assert result == []

    @pytest.mark.asyncio
    async def test_list_models_exception_in_json_parsing(self):
        """Test list_models handles exception when JSON parsing fails"""
        service = OllamaService()

        # Mock response that raises exception during json() call
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=Exception("JSON parsing error"))

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.list_models()

        # Should return empty list on exception
        assert result == []

    @pytest.mark.asyncio
    async def test_pull_model_with_malformed_json_lines(self):
        """Test pull_model handles malformed JSON in streaming response"""
        service = OllamaService()

        # Mix of valid, invalid, and malformed JSON lines
        progress_lines = [
            b'{"status": "downloading"}\n',
            b"invalid json {{\n",  # Malformed JSON
            b"not json at all\n",  # Not JSON
            b'{"status": "complete"}\n',
        ]

        async def mock_content_iter():
            for line in progress_lines:
                yield line

        mock_content = MagicMock()
        mock_content.__aiter__ = lambda self: mock_content_iter()

        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = mock_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_cm.__aexit__.return_value = None

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_cm)

        async def mock_get_session():
            return mock_session

        with patch.object(service, "_get_session", side_effect=mock_get_session):
            result = await service.pull_model("test-model")

        # Should complete successfully despite malformed lines
        assert result is True
