"""
Base AI Service Interface for AI Language Tutor App

This module defines the base interface that all AI service providers must implement.
It ensures consistency across different AI providers (Claude, Mistral, DeepSeek, Ollama).

Features:
- Standardized response format
- Cost tracking interface
- Health monitoring
- Streaming support
- Language learning optimizations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional


class AIResponseStatus(Enum):
    """AI response status types"""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    RATE_LIMITED = "rate_limited"
    BUDGET_EXCEEDED = "budget_exceeded"


@dataclass
class AIResponse:
    """Standardized AI response format"""

    content: str
    model: str
    provider: str
    language: str
    processing_time: float
    cost: float
    status: AIResponseStatus = AIResponseStatus.SUCCESS
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StreamingResponse:
    """Streaming response chunk"""

    content: str
    model: str
    provider: str
    language: str
    is_final: bool
    processing_time: float
    cost: float
    status: AIResponseStatus = AIResponseStatus.SUCCESS
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAIService(ABC):
    """
    Base class for all AI service providers

    All AI services (Claude, Mistral, DeepSeek, Ollama) must inherit from this
    class and implement the required methods.
    """

    def __init__(self):
        self.service_name: str = ""
        self.supported_languages: List[str] = []
        self.cost_per_token_input: float = 0.0
        self.cost_per_token_output: float = 0.0
        self.max_tokens_per_request: int = 4096
        self.rate_limit_per_minute: int = 60
        self.is_available: bool = True
        self.last_health_check: Optional[datetime] = None

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """
        Generate AI response for given messages

        Args:
            messages: List of conversation messages
            language: Target language for response
            model: Specific model to use (optional)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            AIResponse object with generated content
        """

    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[StreamingResponse, None]:
        """
        Generate streaming AI response

        Args:
            messages: List of conversation messages
            language: Target language for response
            model: Specific model to use (optional)
            **kwargs: Additional parameters

        Yields:
            StreamingResponse chunks
        """
        # Default implementation: convert non-streaming to streaming
        response = await self.generate_response(messages, language, model, **kwargs)

        yield StreamingResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            language=response.language,
            is_final=True,
            processing_time=response.processing_time,
            cost=response.cost,
            status=response.status,
            metadata={**response.metadata, "converted_from_non_streaming": True},
        )

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get service health status

        Returns:
            Health status information
        """
        return {
            "service_name": self.service_name,
            "status": "healthy" if self.is_available else "unhealthy",
            "supported_languages": self.supported_languages,
            "last_check": self.last_health_check.isoformat()
            if self.last_health_check
            else None,
            "cost_per_1k_tokens_input": self.cost_per_token_input * 1000,
            "cost_per_1k_tokens_output": self.cost_per_token_output * 1000,
            "rate_limit_per_minute": self.rate_limit_per_minute,
        }

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a request

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        input_cost = input_tokens * self.cost_per_token_input
        output_cost = output_tokens * self.cost_per_token_output
        return input_cost + output_cost

    def supports_language(self, language: str) -> bool:
        """
        Check if service supports a specific language

        Args:
            language: Language code (e.g., 'en', 'fr', 'zh')

        Returns:
            True if language is supported
        """
        if not self.supported_languages:
            return True  # Assume all languages supported if not specified

        return language in self.supported_languages

    def get_language_specific_prompt(
        self, messages: List[Dict[str, str]], language: str
    ) -> List[Dict[str, str]]:
        """
        Optimize prompts for specific languages

        Args:
            messages: Original messages
            language: Target language

        Returns:
            Optimized messages for the language
        """
        # Language-specific system prompts for learning
        language_prompts = {
            "en": "You are a helpful English language tutor. Provide clear explanations and gently correct grammar mistakes.",
            "fr": "Tu es un professeur de français serviable. Fournis des explications claires et corrige gentiment les erreurs de grammaire.",
            "es": "Eres un tutor de español útil. Proporciona explicaciones claras y corrige suavemente los errores gramaticales.",
            "de": "Du bist ein hilfreicher Deutschlehrer. Gib klare Erklärungen und korrigiere Grammatikfehler sanft.",
            "it": "Sei un tutor di italiano utile. Fornisci spiegazioni chiare e correggi gentilmente gli errori grammaticali.",
            "pt": "Você é um tutor de português útil. Forneça explicações claras e corrija suavemente os erros gramaticais.",
            "zh": "你是一个有用的中文语言导师。提供清晰的解释并温和地纠正语法错误。",
            "ja": "あなたは親切な日本語の先生です。明確な説明を提供し、文法の間違いを優しく修正してください。",
            "ko": "당신은 도움이 되는 한국어 튜터입니다. 명확한 설명을 제공하고 문법 실수를 부드럽게 수정해주세요.",
        }

        system_prompt = language_prompts.get(
            language,
            f"You are a helpful language tutor for {language}. Provide clear explanations and corrections.",
        )

        # Add or update system message
        optimized_messages = messages.copy()

        # Check if first message is system message
        if optimized_messages and optimized_messages[0].get("role") == "system":
            optimized_messages[0]["content"] = system_prompt
        else:
            # Insert system message at the beginning
            optimized_messages.insert(0, {"role": "system", "content": system_prompt})

        return optimized_messages

    async def validate_request(
        self, messages: List[Dict[str, str]], language: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Validate request parameters

        Args:
            messages: Conversation messages
            language: Target language
            **kwargs: Additional parameters

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        # Validate messages
        if not messages:
            errors.append("No messages provided")

        # Validate language support
        if not self.supports_language(language):
            warnings.append(f"Language '{language}' may not be optimally supported")

        # Validate token limits
        estimated_tokens = sum(
            len(msg.get("content", "").split()) * 1.3 for msg in messages
        )
        if estimated_tokens > self.max_tokens_per_request:
            errors.append(
                f"Request too long: {estimated_tokens} tokens > {self.max_tokens_per_request} limit"
            )

        # Validate parameters
        max_tokens = kwargs.get("max_tokens", 2048)
        if max_tokens > self.max_tokens_per_request:
            warnings.append(
                f"max_tokens ({max_tokens}) exceeds service limit ({self.max_tokens_per_request})"
            )

        temperature = kwargs.get("temperature", 0.7)
        if not 0.0 <= temperature <= 2.0:
            errors.append(f"Invalid temperature: {temperature} (must be 0.0-2.0)")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "estimated_tokens": estimated_tokens,
        }

    def format_error_response(
        self, error_message: str, language: str = "en"
    ) -> AIResponse:
        """
        Create standardized error response

        Args:
            error_message: Error description
            language: Response language

        Returns:
            AIResponse with error information
        """
        return AIResponse(
            content="I'm sorry, I encountered an error processing your request. Please try again.",
            model="error",
            provider=self.service_name,
            language=language,
            processing_time=0.0,
            cost=0.0,
            status=AIResponseStatus.ERROR,
            error_message=error_message,
            metadata={
                "error_type": "service_error",
                "timestamp": datetime.now().isoformat(),
            },
        )


class MockAIService(BaseAIService):
    """Mock AI service for testing purposes"""

    def __init__(self):
        super().__init__()
        self.service_name = "mock"
        self.supported_languages = [
            "en",
            "fr",
            "es",
            "de",
            "it",
            "pt",
            "zh",
            "ja",
            "ko",
        ]
        self.cost_per_token_input = 0.0001
        self.cost_per_token_output = 0.0003

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate mock response for testing"""

        # Simulate processing time
        import asyncio

        await asyncio.sleep(0.1)

        last_message = messages[-1]["content"] if messages else "Hello"

        # Simple mock responses based on language
        responses = {
            "en": f"Thank you for your message: '{last_message}'. This is a mock response for testing.",
            "fr": f"Merci pour votre message : '{last_message}'. Ceci est une réponse fictive pour les tests.",
            "es": f"Gracias por tu mensaje: '{last_message}'. Esta es una respuesta simulada para pruebas.",
            "zh": f"谢谢您的消息：'{last_message}'。这是用于测试的模拟回复。",
        }

        response_text = responses.get(language, responses["en"])

        return AIResponse(
            content=response_text,
            model=model or "mock-model",
            provider="mock",
            language=language,
            processing_time=0.1,
            cost=0.001,
            metadata={
                "mock_service": True,
                "input_tokens": len(last_message.split()),
                "output_tokens": len(response_text.split()),
            },
        )


# Export the main classes and types
__all__ = [
    "BaseAIService",
    "AIResponse",
    "StreamingResponse",
    "AIResponseStatus",
    "MockAIService",
]
