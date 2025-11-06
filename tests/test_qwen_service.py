"""
Comprehensive tests for Qwen Service
Achieves >90% test coverage for qwen_service.py
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.qwen_service import (
    QwenService,
    qwen_service,
    QWEN_AVAILABLE,
)
from app.services.ai_service_base import AIResponse, AIResponseStatus


class TestQwenServiceInitialization:
    """Test Qwen service initialization"""

    def test_service_initialization_with_deepseek_key(self):
        """Test initialization with DeepSeek API key"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY="test-deepseek-key",
                QWEN_API_KEY=None
            )
            with patch("app.services.qwen_service.QWEN_AVAILABLE", True):
                with patch("app.services.qwen_service.openai") as mock_openai:
                    mock_client = Mock()
                    mock_openai.OpenAI.return_value = mock_client
                    
                    service = QwenService()
                    
                    assert service.is_available is True
                    assert service.client == mock_client
                    assert service.service_name == "qwen"

    def test_service_initialization_with_qwen_key(self):
        """Test initialization with Qwen API key"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY=None,
                QWEN_API_KEY="test-qwen-key"
            )
            with patch("app.services.qwen_service.QWEN_AVAILABLE", True):
                with patch("app.services.qwen_service.openai") as mock_openai:
                    mock_client = Mock()
                    mock_openai.OpenAI.return_value = mock_client
                    
                    service = QwenService()
                    
                    assert service.is_available is True
                    assert service.client == mock_client

    def test_service_initialization_without_api_key(self):
        """Test initialization without API key"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY=None,
                QWEN_API_KEY=None
            )
            with patch("app.services.qwen_service.QWEN_AVAILABLE", True):
                service = QwenService()
                
                assert service.is_available is False
                assert service.client is None

    def test_service_initialization_library_not_available(self):
        """Test initialization when openai library not available"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY="test-key"
            )
            with patch("app.services.qwen_service.QWEN_AVAILABLE", False):
                service = QwenService()
                
                assert service.is_available is False

    def test_service_initialization_client_error(self):
        """Test initialization when client creation fails"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY="test-key"
            )
            with patch("app.services.qwen_service.QWEN_AVAILABLE", True):
                with patch("app.services.qwen_service.openai") as mock_openai:
                    mock_openai.OpenAI.side_effect = Exception("Client error")
                    
                    service = QwenService()
                    
                    assert service.is_available is False


class TestConversationPromptGeneration:
    """Test conversation prompt generation"""

    def test_get_conversation_prompt_chinese(self):
        """Test Chinese prompt generation"""
        service = QwenService()
        
        prompt = service._get_conversation_prompt("zh", "你好")
        
        assert "小李" in prompt
        assert "中文" in prompt
        assert "你好" in prompt
        assert "北京" in prompt

    def test_get_conversation_prompt_chinese_taiwan(self):
        """Test Chinese (Taiwan) prompt generation"""
        service = QwenService()
        
        prompt = service._get_conversation_prompt("zh-tw", "你好")
        
        assert "小李" in prompt
        assert "你好" in prompt

    def test_get_conversation_prompt_english(self):
        """Test English prompt generation"""
        service = QwenService()
        
        prompt = service._get_conversation_prompt("en", "Hello")
        
        assert "Xiao Li" in prompt
        assert "Chinese teacher" in prompt
        assert "Hello" in prompt

    def test_get_conversation_prompt_other_language(self):
        """Test prompt for other supported languages"""
        service = QwenService()
        
        prompt = service._get_conversation_prompt("ja", "こんにちは")
        
        assert "Xiao Li" in prompt
        assert "こんにちは" in prompt


class TestHelperMethods:
    """Test helper methods"""

    def test_extract_user_message_from_message_param(self):
        """Test extracting message from message parameter"""
        service = QwenService()
        
        result = service._extract_user_message("Hello", None)
        
        assert result == "Hello"

    def test_extract_user_message_from_messages_list(self):
        """Test extracting message from messages list"""
        service = QwenService()
        
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Last message"}
        ]
        
        result = service._extract_user_message(None, messages)
        
        assert result == "Last message"

    def test_extract_user_message_default(self):
        """Test default message when no input provided"""
        service = QwenService()
        
        result = service._extract_user_message(None, None)
        
        assert "你好" in result
        assert "中文" in result

    def test_extract_user_message_empty_messages(self):
        """Test extraction with empty messages list"""
        service = QwenService()
        
        result = service._extract_user_message(None, [])
        
        assert "你好" in result

    def test_select_model_with_deepseek(self):
        """Test model selection with DeepSeek API"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY="test-key",
                QWEN_API_KEY=None
            )
            service = QwenService()
            
            model = service._select_model(None)
            
            assert model == "deepseek-chat"

    def test_select_model_with_qwen(self):
        """Test model selection with Qwen API"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY=None,
                QWEN_API_KEY="test-key"
            )
            service = QwenService()
            
            model = service._select_model(None)
            
            assert model == "qwen-plus"

    def test_select_model_custom(self):
        """Test custom model selection"""
        service = QwenService()
        
        model = service._select_model("custom-model")
        
        assert model == "custom-model"

    def test_call_qwen_api(self):
        """Test calling Qwen API"""
        service = QwenService()
        service.client = Mock()
        
        mock_response = Mock()
        service.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = service._call_qwen_api("qwen-plus", "Test prompt", {})
        
        assert result == mock_response
        service.client.chat.completions.create.assert_called_once()

    def test_call_qwen_api_with_params(self):
        """Test calling API with custom parameters"""
        service = QwenService()
        service.client = Mock()
        
        mock_response = Mock()
        service.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = service._call_qwen_api(
            "qwen-plus",
            "Test prompt",
            {"max_tokens": 500, "temperature": 0.9}
        )
        
        assert result == mock_response

    def test_calculate_cost(self):
        """Test cost calculation"""
        service = QwenService()
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50
        
        cost, input_tokens, output_tokens = service._calculate_cost(mock_usage)
        
        assert input_tokens == 100
        assert output_tokens == 50
        assert cost > 0

    def test_calculate_cost_no_usage(self):
        """Test cost calculation with no usage data"""
        service = QwenService()
        
        cost, input_tokens, output_tokens = service._calculate_cost(None)
        
        assert cost == 0
        assert input_tokens == 0
        assert output_tokens == 0

    def test_extract_response_content_with_choices(self):
        """Test extracting content from response"""
        service = QwenService()
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response text"))]
        
        result = service._extract_response_content(mock_response)
        
        assert result == "Response text"

    def test_extract_response_content_no_choices(self):
        """Test extracting content when no choices"""
        service = QwenService()
        
        mock_response = Mock()
        mock_response.choices = []
        
        result = service._extract_response_content(mock_response)
        
        assert "抱歉" in result


class TestFallbackMessages:
    """Test fallback message generation"""

    def test_get_fallback_message_chinese(self):
        """Test Chinese fallback message"""
        service = QwenService()
        
        msg = service._get_fallback_message("zh")
        
        assert any('\u4e00' <= char <= '\u9fff' for char in msg)  # Has Chinese characters

    def test_get_fallback_message_english(self):
        """Test English fallback message"""
        service = QwenService()
        
        msg = service._get_fallback_message("en")
        
        assert "connection" in msg.lower()
        assert not any('\u4e00' <= char <= '\u9fff' for char in msg)


class TestResponseBuilding:
    """Test response building"""

    def test_build_success_response(self):
        """Test building successful response"""
        service = QwenService()
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Success!"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
        
        result = service._build_success_response(
            mock_response,
            "qwen-plus",
            "zh",
            1.5,
            {"user_id": "test123"}
        )
        
        assert isinstance(result, AIResponse)
        assert result.content == "Success!"
        assert result.status == AIResponseStatus.SUCCESS
        assert result.provider == "qwen"
        assert result.metadata["user_id"] == "test123"

    def test_build_success_response_no_context(self):
        """Test building response without context"""
        service = QwenService()
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Success!"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
        
        result = service._build_success_response(
            mock_response,
            "qwen-plus",
            "zh",
            1.5,
            None
        )
        
        assert result.metadata["user_id"] is None

    def test_build_error_response(self):
        """Test building error response"""
        service = QwenService()
        
        error = Exception("API Error")
        
        result = service._build_error_response(error, "qwen-plus", "zh", 1.0)
        
        assert isinstance(result, AIResponse)
        assert result.status == AIResponseStatus.ERROR
        assert result.error_message == "API Error"
        assert result.cost == 0.0
        assert result.metadata["fallback_response"] is True

    def test_build_error_response_no_model(self):
        """Test building error response without model"""
        service = QwenService()
        
        error = Exception("API Error")
        
        result = service._build_error_response(error, None, "zh", 1.0)
        
        assert result.model == "qwen-plus"


class TestGenerateResponse:
    """Test response generation"""

    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation"""
        service = QwenService()
        service.is_available = True
        service.client = Mock()
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="你好！很高兴见到你！"))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=30)
        
        service.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = await service.generate_response(
            message="你好",
            language="zh"
        )
        
        assert isinstance(result, AIResponse)
        assert result.content == "你好！很高兴见到你！"
        assert result.status == AIResponseStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_generate_response_not_available(self):
        """Test response when service not available"""
        service = QwenService()
        service.is_available = False
        
        with pytest.raises(Exception) as exc_info:
            await service.generate_response(message="Hello")
        
        assert "not available" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self):
        """Test response generation with API error"""
        service = QwenService()
        service.is_available = True
        service.client = Mock()
        
        service.client.chat.completions.create = Mock(
            side_effect=Exception("API Error")
        )
        
        result = await service.generate_response(
            message="Hello",
            language="zh"
        )
        
        assert result.status == AIResponseStatus.ERROR
        assert "API Error" in result.error_message

    @pytest.mark.asyncio
    async def test_generate_response_with_messages_list(self):
        """Test response with messages list"""
        service = QwenService()
        service.is_available = True
        service.client = Mock()
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
        
        service.client.chat.completions.create = Mock(return_value=mock_response)
        
        messages = [{"role": "user", "content": "Hello"}]
        result = await service.generate_response(messages=messages, language="zh")
        
        assert result.status == AIResponseStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_generate_response_with_context(self):
        """Test response with user context"""
        service = QwenService()
        service.is_available = True
        service.client = Mock()
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
        
        service.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = await service.generate_response(
            message="Hello",
            language="zh",
            context={"user_id": "user123"}
        )
        
        assert result.metadata["user_id"] == "user123"


class TestAvailabilityAndHealth:
    """Test availability and health checks"""

    @pytest.mark.asyncio
    async def test_check_availability_no_client(self):
        """Test availability check with no client"""
        service = QwenService()
        service.client = None
        
        result = await service.check_availability()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_check_availability_success_deepseek(self):
        """Test successful availability check with DeepSeek"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY="test-key",
                QWEN_API_KEY=None
            )
            service = QwenService()
            service.client = Mock()
            
            mock_response = Mock()
            service.client.chat.completions.create = Mock(return_value=mock_response)
            
            result = await service.check_availability()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_check_availability_success_qwen(self):
        """Test successful availability check with Qwen"""
        with patch("app.services.qwen_service.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                DEEPSEEK_API_KEY=None,
                QWEN_API_KEY="test-key"
            )
            service = QwenService()
            service.client = Mock()
            
            mock_response = Mock()
            service.client.chat.completions.create = Mock(return_value=mock_response)
            
            result = await service.check_availability()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_check_availability_error(self):
        """Test availability check with error"""
        service = QwenService()
        service.client = Mock()
        
        service.client.chat.completions.create = Mock(
            side_effect=Exception("Connection error")
        )
        
        result = await service.check_availability()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self):
        """Test health status when service is healthy"""
        service = QwenService()
        service.client = Mock()
        
        mock_response = Mock()
        service.client.chat.completions.create = Mock(return_value=mock_response)
        
        status = await service.get_health_status()
        
        assert status["status"] == "healthy"
        assert status["available"] is True
        assert status["service_name"] == "qwen"
        assert "zh" in status["supported_languages"]
        assert status["specialization"] == "Chinese language optimization"

    @pytest.mark.asyncio
    async def test_get_health_status_error(self):
        """Test health status when service has error"""
        service = QwenService()
        service.client = None
        
        status = await service.get_health_status()
        
        assert status["status"] == "error"
        assert status["available"] is False


class TestGlobalInstance:
    """Test global instance"""

    def test_global_instance_exists(self):
        """Test global qwen_service instance exists"""
        assert qwen_service is not None
        assert isinstance(qwen_service, QwenService)

    def test_global_instance_has_correct_attributes(self):
        """Test global instance has expected attributes"""
        assert qwen_service.service_name == "qwen"
        assert "zh" in qwen_service.supported_languages
        assert qwen_service.max_tokens_per_request == 6000
