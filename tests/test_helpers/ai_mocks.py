"""
AI Service Mocking Utilities for Unit Tests
Session 82 - AI Testing Architecture

This module provides proper mocking utilities for AI services to ensure
unit tests actually verify AI functionality rather than falling back to
fallback responses.

Usage:
    from tests.test_helpers.ai_mocks import create_mock_ai_response, mock_ai_router

    @patch('app.api.conversations.ai_router', mock_ai_router())
    def test_chat_with_ai(client):
        response = client.post("/api/v1/conversations/chat", ...)
        assert response.status_code == 200
"""

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock


class MockAIResponse:
    """Mock AI response object matching the structure of real AI responses"""

    def __init__(
        self,
        content: str = "This is a mock AI response",
        cost: float = 0.01,
        model: str = "mock-model",
        provider: str = "mock",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.cost = cost
        self.model = model
        self.provider = provider
        self.metadata = metadata or {}


class MockAIService:
    """Mock AI service that simulates real AI service behavior"""

    def __init__(
        self,
        response_content: str = "This is a mock AI response",
        should_fail: bool = False,
        failure_error: Optional[Exception] = None,
    ):
        self.response_content = response_content
        self.should_fail = should_fail
        self.failure_error = failure_error or Exception("AI Service unavailable")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        message: str,
        language: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> MockAIResponse:
        """Mock generate_response method"""
        if self.should_fail:
            raise self.failure_error

        return MockAIResponse(
            content=self.response_content,
            cost=0.01,
            model="mock-model",
            provider="mock",
        )


class MockProviderSelection:
    """Mock provider selection result from AI router"""

    def __init__(
        self,
        service: Optional[MockAIService] = None,
        provider: str = "claude",
        model: str = "mock-model",
        reason: str = "mock selection",
    ):
        self.service = service if service is not None else MockAIService()
        self.provider = provider
        self.model = model
        self.reason = reason


def create_mock_ai_response(
    content: str = "This is a mock AI response",
    cost: float = 0.01,
    model: str = "mock-model",
    provider: str = "mock",
) -> MockAIResponse:
    """
    Create a mock AI response object

    Args:
        content: Response text content
        cost: Estimated cost of the request
        model: Model name used
        provider: Provider name (claude, mistral, deepseek)

    Returns:
        MockAIResponse object

    Example:
        mock_response = create_mock_ai_response(
            content="Hello! How can I help you?",
            cost=0.02,
            provider="claude"
        )
    """
    return MockAIResponse(content=content, cost=cost, model=model, provider=provider)


def create_mock_ai_service(
    response_content: str = "This is a mock AI response",
    should_fail: bool = False,
    failure_error: Optional[Exception] = None,
) -> MockAIService:
    """
    Create a mock AI service

    Args:
        response_content: The text content to return
        should_fail: Whether the service should raise an exception
        failure_error: The exception to raise if should_fail is True

    Returns:
        MockAIService object

    Example:
        # Successful service
        service = create_mock_ai_service(response_content="Hello from AI!")

        # Failing service
        failing_service = create_mock_ai_service(
            should_fail=True,
            failure_error=Exception("API key invalid")
        )
    """
    return MockAIService(
        response_content=response_content,
        should_fail=should_fail,
        failure_error=failure_error,
    )


def create_mock_provider_selection(
    service: Optional[MockAIService] = None,
    provider: str = "claude",
    model: str = "mock-model",
    reason: str = "mock selection",
    should_fail: bool = False,
    failure_error: Optional[Exception] = None,
) -> MockProviderSelection:
    """
    Create a mock provider selection result

    Args:
        service: The mock AI service (creates default if None)
        provider: Provider name
        model: Model name
        reason: Selection reason
        should_fail: Whether the underlying service should fail
        failure_error: Exception to raise on failure

    Returns:
        MockProviderSelection object

    Example:
        # Successful selection
        selection = create_mock_provider_selection(
            provider="claude",
            model="claude-3-sonnet"
        )

        # Failed selection (no service available)
        no_service = create_mock_provider_selection(service=None)
        no_service.service = None  # Simulate no service available
    """
    if service is None and not should_fail:
        service = MockAIService()
    elif service is None and should_fail:
        service = MockAIService(should_fail=True, failure_error=failure_error)

    return MockProviderSelection(
        service=service, provider=provider, model=model, reason=reason
    )


def mock_ai_router(
    response_content: str = "This is a mock AI response",
    provider: str = "claude",
    should_fail: bool = False,
    failure_error: Optional[Exception] = None,
) -> Mock:
    """
    Create a complete mock AI router

    This is the main utility for patching the ai_router in tests.

    Args:
        response_content: AI response text
        provider: Provider to simulate (claude, mistral, deepseek)
        should_fail: Whether AI service should fail
        failure_error: Exception to raise on failure

    Returns:
        Mock object configured as an AI router

    Example:
        @patch('app.api.conversations.ai_router', mock_ai_router(
            response_content="Bonjour!",
            provider="mistral"
        ))
        def test_chat_french(client):
            response = client.post("/api/v1/conversations/chat", ...)
            assert "Bonjour!" in response.json()["response"]
    """
    router = Mock()

    if should_fail and failure_error:
        service = MockAIService(should_fail=True, failure_error=failure_error)
    else:
        service = MockAIService(response_content=response_content)

    selection = MockProviderSelection(service=service, provider=provider)
    router.select_provider = AsyncMock(return_value=selection)

    return router


def mock_failing_ai_service(
    error_message: str = "AI Service unavailable", error_type: type = Exception
) -> Mock:
    """
    Create a mock AI router that always fails

    Useful for testing fallback behavior.

    Args:
        error_message: Error message to raise
        error_type: Type of exception to raise

    Returns:
        Mock AI router that raises exceptions

    Example:
        @patch('app.api.conversations.ai_router',
               mock_failing_ai_service(error_message="API rate limit exceeded"))
        def test_fallback_on_rate_limit(client):
            response = client.post("/api/v1/conversations/chat", ...)
            # Should get fallback response, not AI response
            assert "Hey!" in response.json()["response"]  # Fallback starts with "Hey!"
    """
    router = Mock()

    # Create service that raises on generate_response
    service = MockAIService(should_fail=True, failure_error=error_type(error_message))

    selection = MockProviderSelection(service=service)
    router.select_provider = AsyncMock(return_value=selection)

    return router


def mock_no_ai_service_available() -> Mock:
    """
    Create a mock AI router with no service available

    Simulates the case where select_provider returns None service.

    Returns:
        Mock AI router with service=None

    Example:
        @patch('app.api.conversations.ai_router', mock_no_ai_service_available())
        def test_no_service(client):
            response = client.post("/api/v1/conversations/chat", ...)
            # Should trigger fallback
            assert response.status_code == 200
    """
    router = Mock()

    selection = MockProviderSelection()
    selection.service = None  # No service available

    router.select_provider = AsyncMock(return_value=selection)

    return router


# Convenience fixtures for common test scenarios
def get_successful_claude_mock() -> Mock:
    """Get mock for successful Claude AI service"""
    return mock_ai_router(
        response_content="Hello! I'm Claude, your AI language tutor. How can I help you today?",
        provider="claude",
    )


def get_successful_mistral_mock() -> Mock:
    """Get mock for successful Mistral AI service"""
    return mock_ai_router(
        response_content="Bonjour! Je suis Mistral, votre tuteur de langue IA.",
        provider="mistral",
    )


def get_successful_deepseek_mock() -> Mock:
    """Get mock for successful DeepSeek AI service"""
    return mock_ai_router(
        response_content="你好！我是DeepSeek，你的AI语言导师。", provider="deepseek"
    )
