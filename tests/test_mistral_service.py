"""
Comprehensive tests for Mistral AI Service

Tests cover:
- Service initialization (with/without API key, with/without library)
- Conversation prompt generation (French-optimized)
- Request validation
- Helper methods (message extraction, model selection, request building)
- Cost estimation
- Response content extraction
- Response building (success and error)
- Health checks and availability
- Generate response integration

Coverage target: >90%
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.services.ai_service_base import AIResponse, AIResponseStatus
from app.services.mistral_service import MistralService, mistral_service


class TestZZZImportErrorHandling:
    """Test import error handling for mistralai library

    Note: Class name starts with ZZZ to ensure it runs last, avoiding interference
    with other tests that mock module-level imports.
    """

    def test_import_error_handling(self):
        """Test that ImportError is handled gracefully when mistralai is not available"""
        import importlib
        import sys

        # Save original modules before modification
        original_mistralai = sys.modules.get("mistralai")
        original_mistralai_models = sys.modules.get("mistralai.models")
        original_mistral_service = sys.modules.get("app.services.mistral_service")

        # Remove mistralai modules from sys.modules to simulate not being installed
        modules_to_remove = [
            k for k in list(sys.modules.keys()) if k.startswith("mistralai")
        ]
        for module in modules_to_remove:
            del sys.modules[module]

        # Mock the import to raise ImportError
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "mistralai" or name.startswith("mistralai."):
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        try:
            builtins.__import__ = mock_import

            # Remove the mistral_service module to force reimport
            if "app.services.mistral_service" in sys.modules:
                del sys.modules["app.services.mistral_service"]

            # Now import the module - this should trigger the except block
            import app.services.mistral_service as mistral_module

            # Verify that the ImportError was caught and handled
            assert mistral_module.MISTRAL_AVAILABLE is False
            assert mistral_module.Mistral is None
            assert mistral_module.UserMessage is None
            assert mistral_module.SystemMessage is None
            assert mistral_module.AssistantMessage is None

        finally:
            # Restore original import function
            builtins.__import__ = original_import

            # Restore original modules to their exact previous state
            if original_mistralai is not None:
                sys.modules["mistralai"] = original_mistralai
            if original_mistralai_models is not None:
                sys.modules["mistralai.models"] = original_mistralai_models

            # Restore the original mistral_service module
            if original_mistral_service is not None:
                sys.modules["app.services.mistral_service"] = original_mistral_service
            elif "app.services.mistral_service" in sys.modules:
                # If it didn't exist before our test, remove it
                del sys.modules["app.services.mistral_service"]


class TestMistralServiceInitialization:
    """Test Mistral service initialization"""

    def test_service_initialization_with_api_key(self):
        """Test service initializes correctly with API key"""
        with patch("app.services.mistral_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(MISTRAL_API_KEY="test-key")

            with patch("app.services.mistral_service.MISTRAL_AVAILABLE", True):
                with patch(
                    "app.services.mistral_service.Mistral"
                ) as mock_mistral_class:
                    mock_client = Mock()
                    mock_mistral_class.return_value = mock_client

                    service = MistralService()

                    assert service.service_name == "mistral"
                    assert service.is_available is True
                    assert service.client == mock_client
                    assert "fr" in service.supported_languages
                    assert service.cost_per_token_input == 0.0007 / 1000
                    assert service.cost_per_token_output == 0.002 / 1000
                    assert service.max_tokens_per_request == 8192
                    assert service.rate_limit_per_minute == 1000

    def test_service_initialization_without_api_key(self):
        """Test service initialization without API key"""
        with patch("app.services.mistral_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(MISTRAL_API_KEY=None)

            with patch("app.services.mistral_service.MISTRAL_AVAILABLE", True):
                service = MistralService()

                assert service.is_available is False
                assert service.client is None

    def test_service_initialization_library_not_available(self):
        """Test service initialization when mistralai library not available"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            service = MistralService()

            assert service.is_available is False
            assert service.client is None

    def test_service_initialization_client_error(self):
        """Test service handles client initialization error"""
        with patch("app.services.mistral_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(MISTRAL_API_KEY="test-key")

            with patch("app.services.mistral_service.MISTRAL_AVAILABLE", True):
                with patch(
                    "app.services.mistral_service.Mistral"
                ) as mock_mistral_class:
                    mock_mistral_class.side_effect = Exception("API error")

                    service = MistralService()

                    assert service.is_available is False
                    assert service.client is None


class TestConversationPromptGeneration:
    """Test conversation prompt generation"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            self.service = MistralService()

    def test_get_conversation_prompt_french(self):
        """Test prompt generation for French"""
        prompt = self.service._get_conversation_prompt("fr", "Bonjour!")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Pierre" in prompt
        assert "français" in prompt
        assert "Bonjour!" in prompt

    def test_get_conversation_prompt_english(self):
        """Test prompt generation for English"""
        prompt = self.service._get_conversation_prompt("en", "Hello!")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Pierre" in prompt
        assert "Hello!" in prompt

    def test_get_conversation_prompt_other_language(self):
        """Test prompt generation for other supported languages"""
        for lang in ["es", "de", "it"]:
            prompt = self.service._get_conversation_prompt(lang, "Test message")

            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "Test message" in prompt


class TestValidationMethods:
    """Test validation helper methods"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            self.service = MistralService()

    def test_validate_mistral_request_not_available(self):
        """Test validation fails when service not available"""
        self.service.is_available = False

        with pytest.raises(Exception) as exc_info:
            self.service._validate_mistral_request()

        assert "not available" in str(exc_info.value).lower()

    def test_validate_mistral_request_available(self):
        """Test validation passes when service available"""
        self.service.is_available = True

        # Should not raise exception
        self.service._validate_mistral_request()


class TestHelperMethods:
    """Test helper methods for request/response processing"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            self.service = MistralService()

    def test_extract_user_message_from_message_param(self):
        """Test extracting user message from message parameter"""
        result = self.service._extract_user_message(
            messages=None, message="Test message"
        )

        assert result == "Test message"

    def test_extract_user_message_from_messages_list(self):
        """Test extracting user message from messages list"""
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Last message"},
        ]

        result = self.service._extract_user_message(messages=messages, message=None)

        assert result == "Last message"

    def test_extract_user_message_default(self):
        """Test default message when no input provided"""
        result = self.service._extract_user_message(messages=None, message=None)

        assert "pratiquer" in result.lower() or "français" in result.lower()

    def test_extract_user_message_empty_messages(self):
        """Test extraction from empty messages list"""
        result = self.service._extract_user_message(messages=[], message=None)

        assert "français" in result.lower()

    def test_get_model_name_with_custom_model(self):
        """Test get model name with custom model"""
        result = self.service._get_model_name("mistral-large-latest")

        assert result == "mistral-large-latest"

    def test_get_model_name_with_default(self):
        """Test get model name defaults to mistral-small"""
        result = self.service._get_model_name(None)

        assert result == "mistral-small-latest"

    def test_build_mistral_request(self):
        """Test building Mistral API request with conversation history"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        request = self.service._build_mistral_request(
            model_name="mistral-small-latest",
            conversation_prompt="Test prompt",
            messages=messages,
            kwargs={"max_tokens": 500, "temperature": 0.9},
        )

        assert request["model"] == "mistral-small-latest"
        assert request["max_tokens"] == 500
        assert request["temperature"] == 0.9
        # Should have system message + 3 conversation messages
        assert len(request["messages"]) == 4

    def test_build_mistral_request_default_params(self):
        """Test building request with default parameters"""
        request = self.service._build_mistral_request(
            model_name="mistral-small-latest",
            conversation_prompt="Test prompt",
            messages=None,  # No conversation history
            kwargs={},
        )

        assert request["max_tokens"] == 300  # default
        assert request["temperature"] == 0.8  # default
        # Should have only system message when no conversation history
        assert len(request["messages"]) == 1

    def test_estimate_mistral_cost(self):
        """Test cost estimation from response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = "This is a test response with several words"

        conversation_prompt = "This is a test prompt with some words"

        cost, input_tokens, output_tokens = self.service._estimate_mistral_cost(
            conversation_prompt, mock_response
        )

        assert cost > 0
        assert input_tokens > 0
        assert output_tokens > 0
        assert isinstance(cost, float)
        assert isinstance(input_tokens, int)
        assert isinstance(output_tokens, int)

    def test_extract_response_content_with_choices(self):
        """Test extracting response content with choices"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is the response"

        content = self.service._extract_response_content(mock_response)

        assert content == "This is the response"

    def test_extract_response_content_no_choices(self):
        """Test extracting response content when no choices available"""
        mock_response = Mock()
        mock_response.choices = []

        content = self.service._extract_response_content(mock_response)

        assert "désolé" in content.lower() or "sorry" in content.lower()


class TestResponseBuilding:
    """Test response building methods"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            self.service = MistralService()

    def test_build_success_response(self):
        """Test building successful response"""
        context = {"user_id": "user123"}

        result = self.service._build_success_response(
            response_content="Test response",
            model_name="mistral-small-latest",
            language="fr",
            processing_time=1.5,
            cost=0.05,
            estimated_input_tokens=100,
            estimated_output_tokens=50,
            context=context,
        )

        assert isinstance(result, AIResponse)
        assert result.content == "Test response"
        assert result.model == "mistral-small-latest"
        assert result.provider == "mistral"
        assert result.language == "fr"
        assert result.processing_time == 1.5
        assert result.cost == 0.05
        assert result.status == AIResponseStatus.SUCCESS
        assert result.metadata["estimated_input_tokens"] == 100
        assert result.metadata["estimated_output_tokens"] == 50
        assert result.metadata["user_id"] == "user123"

    def test_build_success_response_no_context(self):
        """Test building successful response without context"""
        result = self.service._build_success_response(
            response_content="Test response",
            model_name="mistral-small-latest",
            language="fr",
            processing_time=1.5,
            cost=0.05,
            estimated_input_tokens=100,
            estimated_output_tokens=50,
            context=None,
        )

        assert result.metadata["user_id"] is None

    def test_build_error_response_french(self):
        """Test building error response for French"""
        error = Exception("API error occurred")

        result = self.service._build_error_response(
            error=error,
            model="mistral-small-latest",
            language="fr",
            processing_time=0.5,
        )

        assert isinstance(result, AIResponse)
        assert (
            "problème" in result.content.lower()
            or "réessayons" in result.content.lower()
        )
        assert result.model == "mistral-small-latest"
        assert result.provider == "mistral"
        assert result.language == "fr"
        assert result.processing_time == 0.5
        assert result.cost == 0.0
        assert result.status == AIResponseStatus.ERROR
        assert result.error_message == "API error occurred"
        assert result.metadata["fallback_response"] is True

    def test_build_error_response_english(self):
        """Test building error response for English"""
        error = Exception("Error")

        result = self.service._build_error_response(
            error=error, model=None, language="en", processing_time=0.5
        )

        assert (
            "connection trouble" in result.content.lower()
            or "try again" in result.content.lower()
        )
        assert result.model == "mistral-small-latest"  # Uses default


class TestGenerateResponse:
    """Test main generate_response method"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            self.service = MistralService()
        self.service.client = Mock()

    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation"""
        self.service.is_available = True

        # Mock Mistral response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = "Bonjour! Comment puis-je vous aider?"

        self.service.client.chat.complete = Mock(return_value=mock_response)

        result = await self.service.generate_response(
            message="Bonjour", language="fr", model="mistral-small-latest"
        )

        assert isinstance(result, AIResponse)
        assert result.content == "Bonjour! Comment puis-je vous aider?"
        assert result.status == AIResponseStatus.SUCCESS
        assert result.provider == "mistral"
        assert result.language == "fr"
        assert result.cost > 0

    @pytest.mark.asyncio
    async def test_generate_response_not_available(self):
        """Test response generation when service not available raises exception"""
        self.service.is_available = False

        with pytest.raises(Exception) as exc_info:
            await self.service.generate_response(message="Hello", language="fr")

        assert "not available" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self):
        """Test response generation with API error"""
        self.service.is_available = True
        self.service.client.chat.complete = Mock(side_effect=Exception("API error"))

        result = await self.service.generate_response(message="Bonjour", language="fr")

        assert result.status == AIResponseStatus.ERROR
        assert result.error_message == "API error"
        assert result.cost == 0.0

    @pytest.mark.asyncio
    async def test_generate_response_with_messages_list(self):
        """Test response generation with messages list"""
        self.service.is_available = True

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"

        self.service.client.chat.complete = Mock(return_value=mock_response)

        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Reply"},
            {"role": "user", "content": "Second"},
        ]

        result = await self.service.generate_response(messages=messages, language="fr")

        assert result.status == AIResponseStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_generate_response_with_context(self):
        """Test response generation with user context"""
        self.service.is_available = True

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"

        self.service.client.chat.complete = Mock(return_value=mock_response)

        context = {"user_id": "user123", "session_id": "session456"}

        result = await self.service.generate_response(
            message="Bonjour", language="fr", context=context
        )

        assert result.status == AIResponseStatus.SUCCESS
        assert result.metadata["user_id"] == "user123"


class TestAvailabilityAndHealth:
    """Test availability and health check methods"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.mistral_service.MISTRAL_AVAILABLE", False):
            self.service = MistralService()

    @pytest.mark.asyncio
    async def test_check_availability_no_client(self):
        """Test availability check with no client"""
        self.service.client = None

        result = await self.service.check_availability()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_availability_success(self):
        """Test successful availability check"""
        self.service.client = Mock()
        self.service.client.chat.complete = Mock(return_value=Mock())

        result = await self.service.check_availability()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_availability_error(self):
        """Test availability check with error"""
        self.service.client = Mock()
        self.service.client.chat.complete = Mock(
            side_effect=Exception("Connection error")
        )

        result = await self.service.check_availability()

        assert result is False

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self):
        """Test health status when service is healthy"""
        self.service.client = Mock()
        self.service.client.chat.complete = Mock(return_value=Mock())

        status = await self.service.get_health_status()

        assert status["status"] == "healthy"
        assert status["available"] is True
        assert status["service_name"] == "mistral"
        assert "fr" in status["supported_languages"]
        assert status["max_tokens"] == 8192
        assert (
            status["cost_per_1k_input_tokens"] == 0.0007
        )  # Already per token, multiplied by 1000 in method
        assert status["cost_per_1k_output_tokens"] == 0.002
        assert status["api_configured"] is True
        assert status["specialization"] == "French language optimization"
        assert "last_check" in status

    @pytest.mark.asyncio
    async def test_get_health_status_error(self):
        """Test health status when service has error"""
        self.service.client = Mock()
        self.service.client.chat.complete = Mock(side_effect=Exception("Error"))

        status = await self.service.get_health_status()

        assert status["status"] == "error"
        assert status["available"] is False


class TestGlobalInstance:
    """Test global mistral_service instance"""

    def test_global_instance_exists(self):
        """Test that global instance is created"""
        assert mistral_service is not None
        assert isinstance(mistral_service, MistralService)

    def test_global_instance_has_correct_attributes(self):
        """Test global instance has expected attributes"""
        assert mistral_service.service_name == "mistral"
        assert hasattr(mistral_service, "generate_response")
        assert hasattr(mistral_service, "check_availability")
        assert hasattr(mistral_service, "get_health_status")
