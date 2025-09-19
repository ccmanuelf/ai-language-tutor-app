"""
Mistral AI Service Implementation for AI Language Tutor App

This service provides natural French conversation using Mistral AI
with optimized prompts for language learning.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

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
        
        if MISTRAL_AVAILABLE and hasattr(self.settings, 'MISTRAL_API_KEY') and self.settings.MISTRAL_API_KEY:
            try:
                self.client = Mistral(api_key=self.settings.MISTRAL_API_KEY)
                self.is_available = True
            except Exception as e:
                logger.error(f"Failed to initialize Mistral client: {e}")
                self.is_available = False
        else:
            logger.warning("Mistral API not available - missing API key or mistralai library")
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
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]] = None,
        language: str = "fr",
        model: Optional[str] = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate natural conversation response using Mistral"""
        
        start_time = datetime.now()
        
        if not self.is_available:
            raise Exception("Mistral service not available - check API key configuration")
        
        try:
            # Handle single message input
            if message and not messages:
                user_message = message
            elif messages:
                user_message = messages[-1].get("content", "") if messages else ""
            else:
                user_message = "Bonjour! Je voudrais pratiquer le français."
            
            # Use specified model or default
            model_name = model or "mistral-small-latest"
            
            # Generate conversation prompt
            conversation_prompt = self._get_conversation_prompt(language, user_message)
            
            # Prepare messages for Mistral
            chat_messages = [
                UserMessage(content=conversation_prompt)
            ]
            
            # Make API call to Mistral
            response = self.client.chat.complete(
                model=model_name,
                messages=chat_messages,
                max_tokens=kwargs.get("max_tokens", 300),
                temperature=kwargs.get("temperature", 0.8)
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Estimate cost (Mistral doesn't provide token count in response)
            estimated_input_tokens = len(conversation_prompt.split()) * 1.3  # Rough estimate
            estimated_output_tokens = len(response.choices[0].message.content.split()) * 1.3
            cost = (estimated_input_tokens * self.cost_per_token_input) + (estimated_output_tokens * self.cost_per_token_output)
            
            # Extract response content
            response_content = response.choices[0].message.content if response.choices else "Je suis désolé, je n'ai pas pu générer une réponse."
            
            return AIResponse(
                content=response_content,
                model=model_name,
                provider="mistral",
                language=language,
                processing_time=processing_time,
                cost=cost,
                status=AIResponseStatus.SUCCESS,
                metadata={
                    "estimated_input_tokens": int(estimated_input_tokens),
                    "estimated_output_tokens": int(estimated_output_tokens),
                    "user_id": context.get("user_id") if context else None,
                    "conversation_style": "natural_french_tutoring"
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Mistral API error: {e}")
            
            # Provide helpful fallback in appropriate language
            fallback_msg = "J'ai un petit problème de connexion. Réessayons ! De quoi aimerais-tu parler ?" if language == "fr" else "I'm having connection trouble. Let's try again! What would you like to talk about?"
            
            return AIResponse(
                content=fallback_msg,
                model=model or "mistral-small-latest",
                provider="mistral", 
                language=language,
                processing_time=processing_time,
                cost=0.0,
                status=AIResponseStatus.ERROR,
                error_message=str(e),
                metadata={"fallback_response": True}
            )
    
    async def check_availability(self) -> bool:
        """Check if Mistral service is available"""
        if not self.client:
            return False
        
        try:
            # Test with a minimal request
            test_response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=[UserMessage(content="Bonjour")],
                max_tokens=10
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
            "last_check": datetime.now().isoformat()
        }


# Global instance
mistral_service = MistralService()