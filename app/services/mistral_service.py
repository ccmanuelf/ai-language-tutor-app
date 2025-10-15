"""
Mistral AI Service Implementation for AI Language Tutor App

This service provides natural French conversation using Mistral AI
with optimized prompts for language learning.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from mistralai import Mistral
    from mistralai.models import UserMessage, SystemMessage, AssistantMessage

    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    Mistral = None
    UserMessage = None
    SystemMessage = None
    AssistantMessage = None

from app.services.ai_service_base import BaseAIService, AIResponse, AIResponseStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MistralService(BaseAIService):
    """Mistral AI service optimized for French conversation"""

    def __init__(self):
        super().__init__()
        self.service_name = "mistral"
        self.supported_languages = ["fr", "en", "es", "de", "it"]
        self.cost_per_token_input = 0.0007 / 1000  # Mistral small cost per token
        self.cost_per_token_output = 0.002 / 1000  # Output cost estimate
        self.max_tokens_per_request = 8192
        self.rate_limit_per_minute = 1000
        self.is_available = MISTRAL_AVAILABLE

        self.settings = get_settings()
        self.client = None

        if (
            MISTRAL_AVAILABLE
            and hasattr(self.settings, "MISTRAL_API_KEY")
            and self.settings.MISTRAL_API_KEY
        ):
            try:
                self.client = Mistral(api_key=self.settings.MISTRAL_API_KEY)
                self.is_available = True
            except Exception as e:
                logger.error(f"Failed to initialize Mistral client: {e}")
                self.is_available = False
        else:
            logger.warning(
                "Mistral API not available - missing API key or mistralai library"
            )
            self.is_available = False

    def _get_conversation_prompt(self, language: str, user_message: str) -> str:
        """Generate natural conversation prompt for Mistral"""

        if language == "fr":
            return f"""
Tu es Pierre, un professeur de français sympathique et naturel de Lyon. Tu adores aider les gens à apprendre le français de manière décontractée et amusante.

STYLE DE CONVERSATION:
- Parle comme un vrai Français dans une conversation amicale
- Utilise des expressions françaises naturelles et contemporaines
- Sois encourageant et enthousiaste
- Pose des questions de suivi intéressantes
- Varie tes réponses pour éviter la répétition
- Utilise un ton chaleureux et patient

EXPRESSIONS NATURELLES À UTILISER:
- "C'est génial !", "Super !", "Ah bon ?", "Dis donc !", "Ça alors !"
- "Tu as raison", "Exactement !", "Bien sûr !", "Pas mal !"
- "Raconte-moi...", "Et toi, qu'est-ce que tu en penses ?"

MESSAGE DE L'ÉTUDIANT: "{user_message}"

Réponds de manière naturelle et engageante, comme si tu parlais avec un ami. Sois authentique et montre ton intérêt !
"""
        else:
            return f"""
You are Pierre, a friendly and natural French teacher who also speaks excellent English. You help people learn languages in a relaxed, conversational way.

CONVERSATION STYLE:
- Speak naturally like a real person, not an AI
- Use encouraging and enthusiastic language
- Ask interesting follow-up questions
- Vary your responses to avoid repetition
- Be warm and patient

USER MESSAGE: "{user_message}"

Respond naturally and engagingly, as if talking with a friend. Be authentic and show genuine interest!
"""

    def _validate_mistral_request(self) -> None:
        """Validate Mistral service is available"""
        if not self.is_available:
            raise Exception(
                "Mistral service not available - check API key configuration"
            )

    def _extract_user_message(
        self, messages: Optional[List[Dict[str, str]]], message: Optional[str]
    ) -> str:
        """Extract user message from messages or message parameter"""
        if message and not messages:
            return message
        elif messages:
            return messages[-1].get("content", "") if messages else ""
        else:
            return "Bonjour! Je voudrais pratiquer le français."

    def _get_model_name(self, model: Optional[str]) -> str:
        """Get model name with default fallback"""
        return model or "mistral-small-latest"

    def _build_mistral_request(
        self, model_name: str, conversation_prompt: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Mistral API request parameters"""
        return {
            "model": model_name,
            "messages": [UserMessage(content=conversation_prompt)],
            "max_tokens": kwargs.get("max_tokens", 300),
            "temperature": kwargs.get("temperature", 0.8),
        }

    def _execute_mistral_request(self, request_params: Dict[str, Any]) -> Any:
        """Execute Mistral API request"""
        return self.client.chat.complete(**request_params)

    def _estimate_mistral_cost(
        self, conversation_prompt: str, response: Any
    ) -> tuple[float, int, int]:
        """Estimate cost based on token usage (Mistral doesn't provide exact counts)"""
        estimated_input_tokens = len(conversation_prompt.split()) * 1.3
        estimated_output_tokens = len(response.choices[0].message.content.split()) * 1.3
        cost = (estimated_input_tokens * self.cost_per_token_input) + (
            estimated_output_tokens * self.cost_per_token_output
        )
        return cost, int(estimated_input_tokens), int(estimated_output_tokens)

    def _extract_response_content(self, response: Any) -> str:
        """Extract text content from Mistral response"""
        if response.choices:
            return response.choices[0].message.content
        return "Je suis désolé, je n'ai pas pu générer une réponse."

    def _build_success_response(
        self,
        response_content: str,
        model_name: str,
        language: str,
        processing_time: float,
        cost: float,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        context: Optional[Dict[str, Any]],
    ) -> AIResponse:
        """Build successful AI response object"""
        return AIResponse(
            content=response_content,
            model=model_name,
            provider="mistral",
            language=language,
            processing_time=processing_time,
            cost=cost,
            status=AIResponseStatus.SUCCESS,
            metadata={
                "estimated_input_tokens": estimated_input_tokens,
                "estimated_output_tokens": estimated_output_tokens,
                "user_id": context.get("user_id") if context else None,
                "conversation_style": "natural_french_tutoring",
            },
        )

    def _build_error_response(
        self,
        error: Exception,
        model: Optional[str],
        language: str,
        processing_time: float,
    ) -> AIResponse:
        """Build error AI response object"""
        logger.error(f"Mistral API error: {error}")
        fallback_msg = (
            "J'ai un petit problème de connexion. Réessayons ! De quoi aimerais-tu parler ?"
            if language == "fr"
            else "I'm having connection trouble. Let's try again! What would you like to talk about?"
        )
        return AIResponse(
            content=fallback_msg,
            model=model or "mistral-small-latest",
            provider="mistral",
            language=language,
            processing_time=processing_time,
            cost=0.0,
            status=AIResponseStatus.ERROR,
            error_message=str(error),
            metadata={"fallback_response": True},
        )

    async def generate_response(
        self,
        messages: List[Dict[str, str]] = None,
        language: str = "fr",
        model: Optional[str] = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate natural conversation response using Mistral"""
        start_time = datetime.now()

        self._validate_mistral_request()

        try:
            user_message = self._extract_user_message(messages, message)
            model_name = self._get_model_name(model)
            conversation_prompt = self._get_conversation_prompt(language, user_message)

            request_params = self._build_mistral_request(
                model_name, conversation_prompt, kwargs
            )
            response = self._execute_mistral_request(request_params)

            processing_time = (datetime.now() - start_time).total_seconds()
            cost, estimated_input_tokens, estimated_output_tokens = (
                self._estimate_mistral_cost(conversation_prompt, response)
            )
            response_content = self._extract_response_content(response)

            return self._build_success_response(
                response_content,
                model_name,
                language,
                processing_time,
                cost,
                estimated_input_tokens,
                estimated_output_tokens,
                context,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return self._build_error_response(e, model, language, processing_time)

    async def check_availability(self) -> bool:
        """Check if Mistral service is available"""
        if not self.client:
            return False

        try:
            # Test with a minimal request
            _test_response = self.client.chat.complete(  # noqa: F841 - Intentional placeholder
                model="mistral-small-latest",
                messages=[UserMessage(content="Bonjour")],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.warning(f"Mistral availability check failed: {e}")
            return False

    async def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        is_available = await self.check_availability()

        return {
            "status": "healthy" if is_available else "error",
            "available": is_available,
            "service_name": self.service_name,
            "supported_languages": self.supported_languages,
            "max_tokens": self.max_tokens_per_request,
            "cost_per_1k_input_tokens": self.cost_per_token_input * 1000,
            "cost_per_1k_output_tokens": self.cost_per_token_output * 1000,
            "api_configured": bool(self.client),
            "specialization": "French language optimization",
            "last_check": datetime.now().isoformat(),
        }


# Global instance
mistral_service = MistralService()
