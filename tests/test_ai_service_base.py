"""
Tests for AI Service Base Module

Comprehensive tests for the BaseAIService abstract base class and related components.
Achieves TRUE 100% coverage (statement + branch).

Test Coverage:
- AIResponseStatus enum
- AIResponse dataclass
- StreamingResponse dataclass
- BaseAIService abstract base class
- MockAIService concrete implementation
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytest

from app.services.ai_service_base import (
    AIResponse,
    AIResponseStatus,
    BaseAIService,
    MockAIService,
    StreamingResponse,
)

# =============================================================================
# Test Class 1: AIResponseStatus Enum
# =============================================================================


class TestAIResponseStatus:
    """Test AIResponseStatus enum"""

    def test_enum_values_exist(self):
        """Test all enum values are defined"""
        assert hasattr(AIResponseStatus, "SUCCESS")
        assert hasattr(AIResponseStatus, "ERROR")
        assert hasattr(AIResponseStatus, "PARTIAL")
        assert hasattr(AIResponseStatus, "RATE_LIMITED")
        assert hasattr(AIResponseStatus, "BUDGET_EXCEEDED")

    def test_enum_value_strings(self):
        """Test enum values map to correct strings"""
        assert AIResponseStatus.SUCCESS.value == "success"
        assert AIResponseStatus.ERROR.value == "error"
        assert AIResponseStatus.PARTIAL.value == "partial"
        assert AIResponseStatus.RATE_LIMITED.value == "rate_limited"
        assert AIResponseStatus.BUDGET_EXCEEDED.value == "budget_exceeded"

    def test_enum_comparison(self):
        """Test enum value comparison"""
        status1 = AIResponseStatus.SUCCESS
        status2 = AIResponseStatus.SUCCESS
        status3 = AIResponseStatus.ERROR

        assert status1 == status2
        assert status1 != status3

    def test_enum_membership(self):
        """Test enum membership"""
        assert AIResponseStatus.SUCCESS in AIResponseStatus
        assert AIResponseStatus.ERROR in AIResponseStatus

    def test_enum_iteration(self):
        """Test enum can be iterated"""
        statuses = list(AIResponseStatus)
        assert len(statuses) == 5
        assert AIResponseStatus.SUCCESS in statuses


# =============================================================================
# Test Class 2: AIResponse Dataclass
# =============================================================================


class TestAIResponse:
    """Test AIResponse dataclass"""

    def test_creation_with_all_fields(self):
        """Test AIResponse creation with all fields"""
        response = AIResponse(
            content="Test content",
            model="test-model",
            provider="test-provider",
            language="en",
            processing_time=1.5,
            cost=0.01,
            status=AIResponseStatus.SUCCESS,
            metadata={"key": "value"},
            error_message="No error",
        )

        assert response.content == "Test content"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.language == "en"
        assert response.processing_time == 1.5
        assert response.cost == 0.01
        assert response.status == AIResponseStatus.SUCCESS
        assert response.metadata == {"key": "value"}
        assert response.error_message == "No error"

    def test_creation_with_minimal_fields(self):
        """Test AIResponse creation with only required fields"""
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            language="en",
            processing_time=1.0,
            cost=0.01,
        )

        assert response.content == "Test"
        assert response.model == "model"
        assert response.status == AIResponseStatus.SUCCESS  # Default value
        assert response.metadata == {}  # Default from __post_init__
        assert response.error_message is None  # Default None

    def test_post_init_metadata_none(self):
        """Test __post_init__ creates empty dict when metadata is None"""
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            language="en",
            processing_time=1.0,
            cost=0.01,
            metadata=None,  # Explicitly None
        )

        assert response.metadata == {}

    def test_post_init_metadata_provided(self):
        """Test __post_init__ preserves provided metadata"""
        metadata = {"custom": "data", "count": 5}
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            language="en",
            processing_time=1.0,
            cost=0.01,
            metadata=metadata,
        )

        assert response.metadata == metadata
        assert response.metadata["custom"] == "data"
        assert response.metadata["count"] == 5

    def test_status_default_value(self):
        """Test status defaults to SUCCESS"""
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            language="en",
            processing_time=1.0,
            cost=0.01,
        )

        assert response.status == AIResponseStatus.SUCCESS

    def test_different_status_values(self):
        """Test AIResponse with different status values"""
        for status in AIResponseStatus:
            response = AIResponse(
                content="Test",
                model="model",
                provider="provider",
                language="en",
                processing_time=1.0,
                cost=0.01,
                status=status,
            )
            assert response.status == status

    def test_error_message_optional(self):
        """Test error_message is optional"""
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            language="en",
            processing_time=1.0,
            cost=0.01,
            error_message="Something went wrong",
        )

        assert response.error_message == "Something went wrong"

    def test_float_cost_and_time(self):
        """Test processing_time and cost accept floats"""
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            language="en",
            processing_time=0.123456,
            cost=0.000789,
        )

        assert response.processing_time == 0.123456
        assert response.cost == 0.000789


# =============================================================================
# Test Class 3: StreamingResponse Dataclass
# =============================================================================


class TestStreamingResponse:
    """Test StreamingResponse dataclass"""

    def test_creation_with_all_fields(self):
        """Test StreamingResponse creation with all fields"""
        response = StreamingResponse(
            content="Chunk",
            model="test-model",
            provider="test-provider",
            language="en",
            is_final=True,
            processing_time=0.5,
            cost=0.001,
            status=AIResponseStatus.PARTIAL,
            metadata={"chunk_id": 1},
        )

        assert response.content == "Chunk"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.language == "en"
        assert response.is_final is True
        assert response.processing_time == 0.5
        assert response.cost == 0.001
        assert response.status == AIResponseStatus.PARTIAL
        assert response.metadata == {"chunk_id": 1}

    def test_creation_with_minimal_fields(self):
        """Test StreamingResponse creation with only required fields"""
        response = StreamingResponse(
            content="Chunk",
            model="model",
            provider="provider",
            language="fr",
            is_final=False,
            processing_time=0.3,
            cost=0.002,
        )

        assert response.content == "Chunk"
        assert response.is_final is False
        assert response.status == AIResponseStatus.SUCCESS  # Default
        assert response.metadata == {}  # Default from __post_init__

    def test_post_init_metadata_none(self):
        """Test __post_init__ creates empty dict when metadata is None"""
        response = StreamingResponse(
            content="Chunk",
            model="model",
            provider="provider",
            language="en",
            is_final=True,
            processing_time=0.1,
            cost=0.001,
            metadata=None,
        )

        assert response.metadata == {}

    def test_post_init_metadata_provided(self):
        """Test __post_init__ preserves provided metadata"""
        metadata = {"chunk": 3, "total": 10}
        response = StreamingResponse(
            content="Chunk",
            model="model",
            provider="provider",
            language="en",
            is_final=False,
            processing_time=0.1,
            cost=0.001,
            metadata=metadata,
        )

        assert response.metadata == metadata
        assert response.metadata["chunk"] == 3

    def test_is_final_true(self):
        """Test is_final=True"""
        response = StreamingResponse(
            content="Final chunk",
            model="model",
            provider="provider",
            language="en",
            is_final=True,
            processing_time=0.5,
            cost=0.005,
        )

        assert response.is_final is True

    def test_is_final_false(self):
        """Test is_final=False"""
        response = StreamingResponse(
            content="Intermediate chunk",
            model="model",
            provider="provider",
            language="en",
            is_final=False,
            processing_time=0.1,
            cost=0.001,
        )

        assert response.is_final is False

    def test_different_languages(self):
        """Test StreamingResponse with different languages"""
        languages = ["en", "fr", "es", "zh", "ja"]

        for lang in languages:
            response = StreamingResponse(
                content="Test",
                model="model",
                provider="provider",
                language=lang,
                is_final=True,
                processing_time=0.1,
                cost=0.001,
            )
            assert response.language == lang

    def test_status_values(self):
        """Test StreamingResponse with different status values"""
        response = StreamingResponse(
            content="Chunk",
            model="model",
            provider="provider",
            language="en",
            is_final=False,
            processing_time=0.1,
            cost=0.001,
            status=AIResponseStatus.RATE_LIMITED,
        )

        assert response.status == AIResponseStatus.RATE_LIMITED


# =============================================================================
# Test Class 4: BaseAIService Initialization
# =============================================================================


class TestBaseAIServiceInit:
    """Test BaseAIService initialization"""

    def test_cannot_instantiate_abstract_class(self):
        """Test BaseAIService cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseAIService()

    def test_mock_service_initialization(self):
        """Test MockAIService initializes BaseAIService attributes"""
        service = MockAIService()

        assert service.service_name == "mock"
        assert isinstance(service.supported_languages, list)
        assert len(service.supported_languages) > 0
        assert isinstance(service.cost_per_token_input, float)
        assert isinstance(service.cost_per_token_output, float)
        assert isinstance(service.max_tokens_per_request, int)
        assert isinstance(service.rate_limit_per_minute, int)
        assert isinstance(service.is_available, bool)
        assert service.last_health_check is None or isinstance(
            service.last_health_check, datetime
        )

    def test_mock_service_default_values(self):
        """Test MockAIService sets expected default values"""
        service = MockAIService()

        assert service.cost_per_token_input == 0.0001
        assert service.cost_per_token_output == 0.0003
        assert "en" in service.supported_languages
        assert "fr" in service.supported_languages

    def test_mock_service_languages(self):
        """Test MockAIService supports multiple languages"""
        service = MockAIService()

        expected_languages = ["en", "fr", "es", "de", "it", "pt", "zh", "ja", "ko"]
        for lang in expected_languages:
            assert lang in service.supported_languages

    def test_last_health_check_none_default(self):
        """Test last_health_check defaults to None"""
        service = MockAIService()
        assert service.last_health_check is None

    def test_is_available_true_default(self):
        """Test is_available defaults to True"""
        service = MockAIService()
        assert service.is_available is True


# =============================================================================
# Test Class 5: BaseAIService Methods
# =============================================================================


class TestBaseAIServiceMethods:
    """Test BaseAIService methods"""

    @pytest.mark.asyncio
    async def test_generate_streaming_response_default_implementation(self):
        """Test default generate_streaming_response implementation"""
        service = MockAIService()

        messages = [{"role": "user", "content": "Hello"}]

        chunks = []
        async for chunk in service.generate_streaming_response(messages, language="en"):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert isinstance(chunks[0], StreamingResponse)
        assert chunks[0].is_final is True

    @pytest.mark.asyncio
    async def test_generate_streaming_response_metadata_flag(self):
        """Test streaming response includes conversion flag in metadata"""
        service = MockAIService()

        messages = [{"role": "user", "content": "Test"}]

        async for chunk in service.generate_streaming_response(messages, language="en"):
            assert "converted_from_non_streaming" in chunk.metadata
            assert chunk.metadata["converted_from_non_streaming"] is True

    @pytest.mark.asyncio
    async def test_generate_streaming_response_preserves_data(self):
        """Test streaming response preserves data from generate_response"""
        service = MockAIService()

        messages = [{"role": "user", "content": "Hello world"}]

        async for chunk in service.generate_streaming_response(messages, language="fr"):
            assert chunk.language == "fr"
            assert chunk.provider == "mock"
            assert chunk.content != ""
            assert chunk.processing_time >= 0

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self):
        """Test get_health_status when service is healthy"""
        service = MockAIService()
        service.is_available = True

        health = await service.get_health_status()

        assert health["service_name"] == "mock"
        assert health["status"] == "healthy"
        assert isinstance(health["supported_languages"], list)
        assert health["last_check"] is None
        assert health["rate_limit_per_minute"] > 0

    @pytest.mark.asyncio
    async def test_get_health_status_unhealthy(self):
        """Test get_health_status when service is unhealthy"""
        service = MockAIService()
        service.is_available = False

        health = await service.get_health_status()

        assert health["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_get_health_status_with_last_check_none(self):
        """Test get_health_status with last_check=None"""
        service = MockAIService()
        service.last_health_check = None

        health = await service.get_health_status()

        assert health["last_check"] is None

    @pytest.mark.asyncio
    async def test_get_health_status_with_last_check_set(self):
        """Test get_health_status with last_check set"""
        service = MockAIService()
        now = datetime.now()
        service.last_health_check = now

        health = await service.get_health_status()

        assert health["last_check"] == now.isoformat()

    @pytest.mark.asyncio
    async def test_get_health_status_cost_per_1k_tokens(self):
        """Test get_health_status calculates cost per 1k tokens"""
        service = MockAIService()

        health = await service.get_health_status()

        # MockAIService: cost_per_token_input = 0.0001
        assert health["cost_per_1k_tokens_input"] == 0.1  # 0.0001 * 1000
        # MockAIService: cost_per_token_output = 0.0003
        assert health["cost_per_1k_tokens_output"] == 0.3  # 0.0003 * 1000

    def test_estimate_cost_calculation(self):
        """Test estimate_cost calculates correctly"""
        service = MockAIService()

        cost = service.estimate_cost(input_tokens=1000, output_tokens=500)

        # (1000 * 0.0001) + (500 * 0.0003) = 0.1 + 0.15 = 0.25
        assert cost == 0.25

    def test_estimate_cost_zero_tokens(self):
        """Test estimate_cost with zero tokens"""
        service = MockAIService()

        cost = service.estimate_cost(input_tokens=0, output_tokens=0)

        assert cost == 0.0

    def test_estimate_cost_only_input(self):
        """Test estimate_cost with only input tokens"""
        service = MockAIService()

        cost = service.estimate_cost(input_tokens=2000, output_tokens=0)

        assert cost == 0.2  # 2000 * 0.0001

    def test_estimate_cost_only_output(self):
        """Test estimate_cost with only output tokens"""
        service = MockAIService()

        cost = service.estimate_cost(input_tokens=0, output_tokens=1000)

        assert cost == 0.3  # 1000 * 0.0003

    def test_supports_language_empty_list(self):
        """Test supports_language returns True when supported_languages is empty"""
        service = MockAIService()
        service.supported_languages = []

        assert service.supports_language("xyz") is True
        assert service.supports_language("en") is True

    def test_supports_language_in_list(self):
        """Test supports_language returns True when language in list"""
        service = MockAIService()

        assert service.supports_language("en") is True
        assert service.supports_language("fr") is True

    def test_supports_language_not_in_list(self):
        """Test supports_language returns False when language not in list"""
        service = MockAIService()

        assert service.supports_language("xyz") is False
        assert service.supports_language("unknown") is False

    def test_format_error_response_structure(self):
        """Test format_error_response creates correct structure"""
        service = MockAIService()

        error_response = service.format_error_response(
            error_message="Test error", language="en"
        )

        assert isinstance(error_response, AIResponse)
        assert error_response.status == AIResponseStatus.ERROR
        assert error_response.error_message == "Test error"
        assert error_response.language == "en"
        assert error_response.provider == "mock"

    def test_format_error_response_content(self):
        """Test format_error_response has user-friendly content"""
        service = MockAIService()

        error_response = service.format_error_response(
            error_message="Internal error", language="en"
        )

        assert "error" in error_response.content.lower()
        assert "sorry" in error_response.content.lower()

    def test_format_error_response_metadata(self):
        """Test format_error_response includes metadata"""
        service = MockAIService()

        error_response = service.format_error_response(
            error_message="Test error", language="fr"
        )

        assert "error_type" in error_response.metadata
        assert error_response.metadata["error_type"] == "service_error"
        assert "timestamp" in error_response.metadata

    def test_format_error_response_zero_cost(self):
        """Test format_error_response has zero cost and processing time"""
        service = MockAIService()

        error_response = service.format_error_response(
            error_message="Test error", language="en"
        )

        assert error_response.cost == 0.0
        assert error_response.processing_time == 0.0

    def test_format_error_response_different_languages(self):
        """Test format_error_response with different languages"""
        service = MockAIService()

        for lang in ["en", "fr", "es", "zh"]:
            error_response = service.format_error_response(
                error_message="Error", language=lang
            )
            assert error_response.language == lang


# =============================================================================
# Test Class 6: get_language_specific_prompt
# =============================================================================


class TestGetLanguageSpecificPrompt:
    """Test get_language_specific_prompt method"""

    def test_english_prompt(self):
        """Test English language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Hello"}]

        optimized = service.get_language_specific_prompt(messages, "en")

        assert len(optimized) == 2
        assert optimized[0]["role"] == "system"
        assert "English" in optimized[0]["content"]
        assert "tutor" in optimized[0]["content"].lower()

    def test_french_prompt(self):
        """Test French language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Bonjour"}]

        optimized = service.get_language_specific_prompt(messages, "fr")

        assert optimized[0]["role"] == "system"
        assert "français" in optimized[0]["content"]

    def test_spanish_prompt(self):
        """Test Spanish language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Hola"}]

        optimized = service.get_language_specific_prompt(messages, "es")

        assert optimized[0]["role"] == "system"
        assert "español" in optimized[0]["content"]

    def test_german_prompt(self):
        """Test German language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Hallo"}]

        optimized = service.get_language_specific_prompt(messages, "de")

        assert optimized[0]["role"] == "system"
        assert "Deutschlehrer" in optimized[0]["content"]

    def test_italian_prompt(self):
        """Test Italian language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Ciao"}]

        optimized = service.get_language_specific_prompt(messages, "it")

        assert optimized[0]["role"] == "system"
        assert "italiano" in optimized[0]["content"]

    def test_portuguese_prompt(self):
        """Test Portuguese language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Olá"}]

        optimized = service.get_language_specific_prompt(messages, "pt")

        assert optimized[0]["role"] == "system"
        assert "português" in optimized[0]["content"]

    def test_chinese_prompt(self):
        """Test Chinese language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "你好"}]

        optimized = service.get_language_specific_prompt(messages, "zh")

        assert optimized[0]["role"] == "system"
        assert "中文" in optimized[0]["content"]

    def test_japanese_prompt(self):
        """Test Japanese language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "こんにちは"}]

        optimized = service.get_language_specific_prompt(messages, "ja")

        assert optimized[0]["role"] == "system"
        assert "日本語" in optimized[0]["content"]

    def test_korean_prompt(self):
        """Test Korean language prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "안녕하세요"}]

        optimized = service.get_language_specific_prompt(messages, "ko")

        assert optimized[0]["role"] == "system"
        assert "한국어" in optimized[0]["content"]

    def test_unknown_language_fallback(self):
        """Test unknown language uses fallback prompt"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        optimized = service.get_language_specific_prompt(messages, "xyz")

        assert optimized[0]["role"] == "system"
        assert "language tutor for xyz" in optimized[0]["content"]

    def test_with_existing_system_message(self):
        """Test updates existing system message"""
        service = MockAIService()
        messages = [
            {"role": "system", "content": "Old system message"},
            {"role": "user", "content": "Hello"},
        ]

        optimized = service.get_language_specific_prompt(messages, "en")

        assert len(optimized) == 2
        assert optimized[0]["role"] == "system"
        assert "English" in optimized[0]["content"]
        assert "Old system message" not in optimized[0]["content"]

    def test_without_system_message(self):
        """Test inserts system message when none exists"""
        service = MockAIService()
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        optimized = service.get_language_specific_prompt(messages, "en")

        assert len(optimized) == 3
        assert optimized[0]["role"] == "system"
        assert optimized[1]["role"] == "user"
        assert optimized[2]["role"] == "assistant"

    def test_message_list_not_mutated(self):
        """Test original message list is not mutated (copy check)"""
        service = MockAIService()
        original_messages = [{"role": "user", "content": "Hello"}]
        original_length = len(original_messages)

        optimized = service.get_language_specific_prompt(original_messages, "en")

        assert len(original_messages) == original_length
        assert len(optimized) != len(original_messages)
        assert optimized is not original_messages


# =============================================================================
# Test Class 7: validate_request
# =============================================================================


class TestValidateRequest:
    """Test validate_request method"""

    @pytest.mark.asyncio
    async def test_valid_request_no_errors(self):
        """Test validation passes for valid request"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Hello world"}]

        result = await service.validate_request(messages, "en")

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "estimated_tokens" in result

    @pytest.mark.asyncio
    async def test_empty_messages_error(self):
        """Test validation fails with empty messages"""
        service = MockAIService()
        messages = []

        result = await service.validate_request(messages, "en")

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "No messages provided" in result["errors"]

    @pytest.mark.asyncio
    async def test_unsupported_language_warning(self):
        """Test validation warns for unsupported language"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        result = await service.validate_request(messages, "xyz")

        assert result["valid"] is True  # Warning, not error
        assert len(result["warnings"]) > 0
        assert any("xyz" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_token_limit_exceeded_error(self):
        """Test validation fails when tokens exceed limit"""
        service = MockAIService()
        service.max_tokens_per_request = 10

        # Create message that will exceed token limit
        long_content = " ".join(["word"] * 100)
        messages = [{"role": "user", "content": long_content}]

        result = await service.validate_request(messages, "en")

        assert result["valid"] is False
        assert any("too long" in e.lower() for e in result["errors"])

    @pytest.mark.asyncio
    async def test_max_tokens_exceeds_limit_warning(self):
        """Test validation warns when max_tokens exceeds service limit"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        result = await service.validate_request(
            messages,
            "en",
            max_tokens=999999,  # Exceeds limit
        )

        assert len(result["warnings"]) > 0
        assert any("max_tokens" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_invalid_temperature_below_zero_error(self):
        """Test validation fails for temperature < 0"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        result = await service.validate_request(messages, "en", temperature=-0.1)

        assert result["valid"] is False
        assert any("temperature" in e.lower() for e in result["errors"])

    @pytest.mark.asyncio
    async def test_invalid_temperature_above_two_error(self):
        """Test validation fails for temperature > 2.0"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        result = await service.validate_request(messages, "en", temperature=2.1)

        assert result["valid"] is False
        assert any("temperature" in e.lower() for e in result["errors"])

    @pytest.mark.asyncio
    async def test_valid_temperature_range(self):
        """Test validation passes for valid temperature range"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        for temp in [0.0, 0.5, 1.0, 1.5, 2.0]:
            result = await service.validate_request(messages, "en", temperature=temp)
            assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_multiple_errors(self):
        """Test validation can report multiple errors"""
        service = MockAIService()
        messages = []  # Empty messages error

        result = await service.validate_request(
            messages,
            "en",
            temperature=-1.0,  # Invalid temperature error
        )

        assert result["valid"] is False
        assert len(result["errors"]) >= 2

    @pytest.mark.asyncio
    async def test_multiple_warnings(self):
        """Test validation can report multiple warnings"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        result = await service.validate_request(
            messages,
            "xyz",  # Unsupported language warning
            max_tokens=999999,  # Exceeds limit warning
        )

        assert result["valid"] is True
        assert len(result["warnings"]) >= 2

    @pytest.mark.asyncio
    async def test_estimated_tokens_calculation(self):
        """Test estimated_tokens is calculated"""
        service = MockAIService()
        messages = [
            {"role": "user", "content": "This is a test message"},
            {"role": "assistant", "content": "This is a response"},
        ]

        result = await service.validate_request(messages, "en")

        assert "estimated_tokens" in result
        assert result["estimated_tokens"] > 0


# =============================================================================
# Test Class 8: MockAIService
# =============================================================================


class TestMockAIService:
    """Test MockAIService concrete implementation"""

    def test_initialization_service_name(self):
        """Test MockAIService sets service name"""
        service = MockAIService()
        assert service.service_name == "mock"

    def test_initialization_supported_languages(self):
        """Test MockAIService sets supported languages"""
        service = MockAIService()

        assert len(service.supported_languages) == 9
        assert "en" in service.supported_languages
        assert "fr" in service.supported_languages
        assert "es" in service.supported_languages
        assert "de" in service.supported_languages
        assert "it" in service.supported_languages
        assert "pt" in service.supported_languages
        assert "zh" in service.supported_languages
        assert "ja" in service.supported_languages
        assert "ko" in service.supported_languages

    def test_initialization_cost_values(self):
        """Test MockAIService sets cost values"""
        service = MockAIService()

        assert service.cost_per_token_input == 0.0001
        assert service.cost_per_token_output == 0.0003

    @pytest.mark.asyncio
    async def test_generate_response_english(self):
        """Test generate_response for English"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Hello"}]

        response = await service.generate_response(messages, language="en")

        assert isinstance(response, AIResponse)
        assert response.language == "en"
        assert response.provider == "mock"
        assert "Hello" in response.content
        assert "mock response" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_french(self):
        """Test generate_response for French"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Bonjour"}]

        response = await service.generate_response(messages, language="fr")

        assert response.language == "fr"
        assert "Bonjour" in response.content
        assert "Merci" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_spanish(self):
        """Test generate_response for Spanish"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Hola"}]

        response = await service.generate_response(messages, language="es")

        assert response.language == "es"
        assert "Hola" in response.content
        assert "Gracias" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_chinese(self):
        """Test generate_response for Chinese"""
        service = MockAIService()
        messages = [{"role": "user", "content": "你好"}]

        response = await service.generate_response(messages, language="zh")

        assert response.language == "zh"
        assert "你好" in response.content
        assert "谢谢" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_unknown_language_fallback(self):
        """Test generate_response uses English fallback for unknown language"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        response = await service.generate_response(messages, language="xyz")

        assert response.language == "xyz"
        assert "Test" in response.content
        assert "mock response" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_async_behavior(self):
        """Test generate_response is properly async"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        import time

        start = time.time()
        response = await service.generate_response(messages, language="en")
        elapsed = time.time() - start

        # Should have simulated processing time (0.1s)
        assert elapsed >= 0.1
        assert response.processing_time == 0.1

    @pytest.mark.asyncio
    async def test_generate_response_structure(self):
        """Test generate_response returns complete structure"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test message"}]

        response = await service.generate_response(
            messages, language="en", model="custom-model"
        )

        assert response.content != ""
        assert response.model == "custom-model"
        assert response.provider == "mock"
        assert response.language == "en"
        assert response.processing_time > 0
        assert response.cost == 0.001
        assert response.status == AIResponseStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_generate_response_metadata(self):
        """Test generate_response includes metadata"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        response = await service.generate_response(messages, language="en")

        assert "mock_service" in response.metadata
        assert response.metadata["mock_service"] is True
        assert "input_tokens" in response.metadata
        assert "output_tokens" in response.metadata

    @pytest.mark.asyncio
    async def test_generate_response_empty_messages(self):
        """Test generate_response handles empty messages gracefully"""
        service = MockAIService()
        messages = []

        response = await service.generate_response(messages, language="en")

        # Should use "Hello" as fallback for last_message
        assert "Hello" in response.content

    @pytest.mark.asyncio
    async def test_generate_response_model_parameter(self):
        """Test generate_response uses provided model parameter"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        response = await service.generate_response(
            messages, language="en", model="specific-model-v2"
        )

        assert response.model == "specific-model-v2"

    @pytest.mark.asyncio
    async def test_generate_response_model_default(self):
        """Test generate_response uses default model when not specified"""
        service = MockAIService()
        messages = [{"role": "user", "content": "Test"}]

        response = await service.generate_response(messages, language="en")

        assert response.model == "mock-model"
