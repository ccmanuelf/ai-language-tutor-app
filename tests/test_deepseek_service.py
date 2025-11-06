"""
Comprehensive tests for DeepSeek AI Service

Tests cover:
- Service initialization (with/without API key, with/without library)
- Conversation prompt generation (multilingual-optimized)
- Request validation
- Helper methods (message extraction, API calls, cost calculation)
- Response content extraction
- Response building (success and error)
- Fallback messages (multilingual)
- Health checks and availability
- Generate response integration

Coverage target: >90%
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.services.ai_service_base import AIResponse, AIResponseStatus
from app.services.deepseek_service import DeepSeekService, deepseek_service


class TestDeepSeekServiceInitialization:
    """Test DeepSeek service initialization"""

    def test_service_initialization_with_api_key(self):
        """Test service initializes correctly with API key"""
        with patch("app.services.deepseek_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(DEEPSEEK_API_KEY="test-key")

            with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", True):
                with patch("app.services.deepseek_service.openai") as mock_openai:
                    mock_client = Mock()
                    mock_openai.OpenAI.return_value = mock_client

                    service = DeepSeekService()

                    assert service.service_name == "deepseek"
                    assert service.is_available is True
                    assert service.client == mock_client
                    assert "zh" in service.supported_languages
                    assert service.cost_per_token_input == 0.0001 / 1000
                    assert service.cost_per_token_output == 0.0002 / 1000
                    assert service.max_tokens_per_request == 8000
                    assert service.rate_limit_per_minute == 1000

    def test_service_initialization_without_api_key(self):
        """Test service initialization without API key"""
        with patch("app.services.deepseek_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(spec=[])  # No DEEPSEEK_API_KEY attribute

            with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", True):
                service = DeepSeekService()

                assert service.is_available is False
                assert service.client is None

    def test_service_initialization_library_not_available(self):
        """Test service initialization when openai library not available"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            service = DeepSeekService()

            assert service.is_available is False
            assert service.client is None

    def test_service_initialization_client_error(self):
        """Test service handles client initialization error"""
        with patch("app.services.deepseek_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(DEEPSEEK_API_KEY="test-key")

            with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", True):
                with patch("app.services.deepseek_service.openai") as mock_openai:
                    mock_openai.OpenAI.side_effect = Exception("API error")

                    service = DeepSeekService()

                    assert service.is_available is False
                    assert service.client is None


class TestConversationPromptGeneration:
    """Test conversation prompt generation"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            self.service = DeepSeekService()

    def test_get_conversation_prompt_chinese(self):
        """Test prompt generation for Chinese"""
        prompt = self.service._get_conversation_prompt("zh", "你好!")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "小李" in prompt
        assert "你好!" in prompt

    def test_get_conversation_prompt_spanish(self):
        """Test prompt generation for Spanish"""
        prompt = self.service._get_conversation_prompt("es", "Hola!")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "María" in prompt
        assert "Hola!" in prompt

    def test_get_conversation_prompt_french(self):
        """Test prompt generation for French"""
        prompt = self.service._get_conversation_prompt("fr", "Bonjour!")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Pierre" in prompt
        assert "Bonjour!" in prompt

    def test_get_conversation_prompt_english(self):
        """Test prompt generation for English"""
        prompt = self.service._get_conversation_prompt("en", "Hello!")

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Hello!" in prompt

    def test_get_conversation_prompt_other_languages(self):
        """Test prompt generation for other supported languages"""
        for lang in ["ja", "ko", "de"]:
            prompt = self.service._get_conversation_prompt(lang, "Test message")

            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "Test message" in prompt


class TestHelperMethods:
    """Test helper methods for request/response processing"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            self.service = DeepSeekService()
        self.service.client = Mock()

    def test_extract_user_message_from_message_param(self):
        """Test extracting user message from message parameter"""
        result = self.service._extract_user_message("Test message", None)

        assert result == "Test message"

    def test_extract_user_message_from_messages_list(self):
        """Test extracting user message from messages list"""
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Last message"},
        ]

        result = self.service._extract_user_message(None, messages)

        assert result == "Last message"

    def test_extract_user_message_default(self):
        """Test default message when no input provided"""
        result = self.service._extract_user_message(None, None)

        assert "practice conversation" in result.lower()

    def test_extract_user_message_empty_messages(self):
        """Test extraction from empty messages list"""
        result = self.service._extract_user_message(None, [])

        assert "practice conversation" in result.lower()

    def test_call_deepseek_api(self):
        """Test calling DeepSeek API"""
        mock_response = Mock()
        self.service.client.chat.completions.create = Mock(return_value=mock_response)

        result = self.service._call_deepseek_api(
            "deepseek-chat", "Test prompt", {"max_tokens": 500, "temperature": 0.9}
        )

        assert result == mock_response
        self.service.client.chat.completions.create.assert_called_once()

    def test_call_deepseek_api_default_params(self):
        """Test API call with default parameters"""
        mock_response = Mock()
        self.service.client.chat.completions.create = Mock(return_value=mock_response)

        result = self.service._call_deepseek_api("deepseek-chat", "Test prompt", {})

        assert result == mock_response

    def test_calculate_cost(self):
        """Test cost calculation from usage"""
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50

        cost, input_tokens, output_tokens = self.service._calculate_cost(mock_usage)

        assert cost > 0
        assert input_tokens == 100
        assert output_tokens == 50
        assert isinstance(cost, float)

    def test_calculate_cost_no_usage(self):
        """Test cost calculation when usage is None"""
        cost, input_tokens, output_tokens = self.service._calculate_cost(None)

        assert cost == 0
        assert input_tokens == 0
        assert output_tokens == 0

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

        assert "couldn't generate" in content.lower() or "sorry" in content.lower()


class TestFallbackMessages:
    """Test language-specific fallback messages"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            self.service = DeepSeekService()

    def test_get_fallback_message_chinese(self):
        """Test Chinese fallback message"""
        msg = self.service._get_fallback_message("zh")

        assert isinstance(msg, str)
        assert len(msg) > 0
        # Should contain Chinese characters
        assert any("\u4e00" <= char <= "\u9fff" for char in msg)

    def test_get_fallback_message_spanish(self):
        """Test Spanish fallback message"""
        msg = self.service._get_fallback_message("es")

        assert isinstance(msg, str)
        assert "conexión" in msg.lower() or "problemas" in msg.lower()

    def test_get_fallback_message_french(self):
        """Test French fallback message"""
        msg = self.service._get_fallback_message("fr")

        assert isinstance(msg, str)
        assert "connexion" in msg.lower() or "problèmes" in msg.lower()

    def test_get_fallback_message_english(self):
        """Test English fallback message (default)"""
        msg = self.service._get_fallback_message("en")

        assert isinstance(msg, str)
        assert "connection trouble" in msg.lower() or "try again" in msg.lower()


class TestResponseBuilding:
    """Test response building methods"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            self.service = DeepSeekService()

    def test_build_success_response(self):
        """Test building successful response"""
        mock_response = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"

        context = {"user_id": "user123"}

        result = self.service._build_success_response(
            mock_response, "deepseek-chat", "zh", 1.5, context
        )

        assert isinstance(result, AIResponse)
        assert result.content == "Test response"
        assert result.model == "deepseek-chat"
        assert result.provider == "deepseek"
        assert result.language == "zh"
        assert result.processing_time == 1.5
        assert result.cost > 0
        assert result.status == AIResponseStatus.SUCCESS
        assert result.metadata["input_tokens"] == 100
        assert result.metadata["output_tokens"] == 50
        assert result.metadata["user_id"] == "user123"

    def test_build_success_response_no_context(self):
        """Test building successful response without context"""
        mock_response = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"

        result = self.service._build_success_response(
            mock_response, "deepseek-chat", "en", 1.5, None
        )

        assert result.metadata["user_id"] is None

    def test_build_error_response(self):
        """Test building error response"""
        error = Exception("API error occurred")

        result = self.service._build_error_response(error, "deepseek-chat", "zh", 0.5)

        assert isinstance(result, AIResponse)
        assert result.model == "deepseek-chat"
        assert result.provider == "deepseek"
        assert result.language == "zh"
        assert result.processing_time == 0.5
        assert result.cost == 0.0
        assert result.status == AIResponseStatus.ERROR
        assert result.error_message == "API error occurred"
        assert result.metadata["fallback_response"] is True

    def test_build_error_response_no_model(self):
        """Test building error response without model"""
        error = Exception("Error")

        result = self.service._build_error_response(error, None, "en", 0.5)

        assert result.model == "deepseek-chat"  # Uses default


class TestGenerateResponse:
    """Test main generate_response method"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            self.service = DeepSeekService()
        self.service.client = Mock()

    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation"""
        self.service.is_available = True

        # Mock DeepSeek response
        mock_response = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 25
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "你好! 我能帮你什么?"

        self.service.client.chat.completions.create = Mock(return_value=mock_response)

        result = await self.service.generate_response(
            message="你好", language="zh", model="deepseek-chat"
        )

        assert isinstance(result, AIResponse)
        assert result.content == "你好! 我能帮你什么?"
        assert result.status == AIResponseStatus.SUCCESS
        assert result.provider == "deepseek"
        assert result.language == "zh"
        assert result.cost > 0

    @pytest.mark.asyncio
    async def test_generate_response_not_available(self):
        """Test response generation when service not available raises exception"""
        self.service.is_available = False

        with pytest.raises(Exception) as exc_info:
            await self.service.generate_response(message="Hello", language="en")

        assert "not available" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self):
        """Test response generation with API error"""
        self.service.is_available = True
        self.service.client.chat.completions.create = Mock(
            side_effect=Exception("API error")
        )

        result = await self.service.generate_response(message="Hello", language="en")

        assert result.status == AIResponseStatus.ERROR
        assert result.error_message == "API error"
        assert result.cost == 0.0

    @pytest.mark.asyncio
    async def test_generate_response_with_messages_list(self):
        """Test response generation with messages list"""
        self.service.is_available = True

        mock_response = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 25
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"

        self.service.client.chat.completions.create = Mock(return_value=mock_response)

        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Reply"},
            {"role": "user", "content": "Second"},
        ]

        result = await self.service.generate_response(messages=messages, language="zh")

        assert result.status == AIResponseStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_generate_response_with_context(self):
        """Test response generation with user context"""
        self.service.is_available = True

        mock_response = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 25
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"

        self.service.client.chat.completions.create = Mock(return_value=mock_response)

        context = {"user_id": "user123", "session_id": "session456"}

        result = await self.service.generate_response(
            message="Hello", language="zh", context=context
        )

        assert result.status == AIResponseStatus.SUCCESS
        assert result.metadata["user_id"] == "user123"


class TestAvailabilityAndHealth:
    """Test availability and health check methods"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("app.services.deepseek_service.DEEPSEEK_AVAILABLE", False):
            self.service = DeepSeekService()

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
        self.service.client.chat.completions.create = Mock(return_value=Mock())

        result = await self.service.check_availability()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_availability_error(self):
        """Test availability check with error"""
        self.service.client = Mock()
        self.service.client.chat.completions.create = Mock(
            side_effect=Exception("Connection error")
        )

        result = await self.service.check_availability()

        assert result is False

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self):
        """Test health status when service is healthy"""
        self.service.client = Mock()
        self.service.client.chat.completions.create = Mock(return_value=Mock())

        status = await self.service.get_health_status()

        assert status["status"] == "healthy"
        assert status["available"] is True
        assert status["service_name"] == "deepseek"
        assert "zh" in status["supported_languages"]
        assert status["max_tokens"] == 8000
        assert status["cost_per_1k_input_tokens"] == 0.0001
        assert status["cost_per_1k_output_tokens"] == 0.0002
        assert status["api_configured"] is True
        assert status["specialization"] == "Multilingual conversation optimization"
        assert "last_check" in status

    @pytest.mark.asyncio
    async def test_get_health_status_error(self):
        """Test health status when service has error"""
        self.service.client = Mock()
        self.service.client.chat.completions.create = Mock(
            side_effect=Exception("Error")
        )

        status = await self.service.get_health_status()

        assert status["status"] == "error"
        assert status["available"] is False


class TestGlobalInstance:
    """Test global deepseek_service instance"""

    def test_global_instance_exists(self):
        """Test that global instance is created"""
        assert deepseek_service is not None
        assert isinstance(deepseek_service, DeepSeekService)

    def test_global_instance_has_correct_attributes(self):
        """Test global instance has expected attributes"""
        assert deepseek_service.service_name == "deepseek"
        assert hasattr(deepseek_service, "generate_response")
        assert hasattr(deepseek_service, "check_availability")
        assert hasattr(deepseek_service, "get_health_status")
