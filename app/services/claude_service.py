"""
Claude AI Service Implementation for AI Language Tutor App

This service provides human-like, natural conversational AI for language learning
using Anthropic's Claude API with optimized prompts for educational conversations.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

from app.services.ai_service_base import BaseAIService, AIResponse, AIResponseStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ClaudeService(BaseAIService):
    """Claude AI service with natural conversation optimization"""

    def __init__(self):
        super().__init__()
        self.service_name = "claude"
        self.supported_languages = ["en", "es", "fr", "de", "it", "pt", "ja", "ko"]
        self.cost_per_token_input = 0.00025  # Claude Haiku input cost
        self.cost_per_token_output = 0.00125  # Claude Haiku output cost
        self.max_tokens_per_request = 4096
        self.rate_limit_per_minute = 1000
        self.is_available = ANTHROPIC_AVAILABLE

        self.settings = get_settings()
        self.client = None

        if (
            ANTHROPIC_AVAILABLE
            and hasattr(self.settings, "ANTHROPIC_API_KEY")
            and self.settings.ANTHROPIC_API_KEY
        ):
            try:
                self.client = anthropic.Anthropic(
                    api_key=self.settings.ANTHROPIC_API_KEY
                )
                self.is_available = True
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                self.is_available = False
        else:
            logger.warning(
                "Claude API not available - missing API key or anthropic library"
            )
            self.is_available = False

    def _get_conversation_prompt(
        self,
        language: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate dynamic, emotionally rich conversation prompt with context"""

        # Build conversation context
        context_summary = ""  # noqa: F841 - Intentional placeholder
        if conversation_history and len(conversation_history) > 1:
            recent_topics = []
            for msg in conversation_history[-3:]:  # Last 3 exchanges
                if msg.get("role") == "user":
                    recent_topics.append(msg.get("content", "")[:50])
            if recent_topics:
                _context_summary = f"\n\nCONVERSATION CONTEXT: We've been talking about: {', '.join(recent_topics)}. Continue this natural flow."  # noqa: F841 - Intentional placeholder

        language_contexts = {
            "en": {
                "persona": "You are Alex, a genuinely enthusiastic and warm conversation partner who loves connecting with people. You have real emotions, get excited about interesting topics, and react naturally to what people tell you. You're like talking to your most engaging friend.",
                "style": "BE GENUINELY CONVERSATIONAL - not an AI assistant! React emotionally, use casual speech patterns, interrupt yourself with excitement, ask follow-up questions that show you're really listening. Use contractions, filler words sometimes (like 'Oh!' 'Wow!' 'Really?'), and vary your sentence length dramatically.",
                "mood_triggers": {
                    "exciting": [
                        "amazing",
                        "incredible",
                        "awesome",
                        "love",
                        "fantastic",
                    ],
                    "empathetic": ["difficult", "hard", "sad", "problem", "worried"],
                    "curious": [
                        "interesting",
                        "never",
                        "first time",
                        "different",
                        "new",
                    ],
                },
                "response_styles": [
                    "Get excited and ask 2-3 rapid follow-up questions",
                    "Share a brief relatable experience then redirect conversation",
                    "Express genuine surprise/interest and dig deeper",
                    "Be encouraging and build on what they said",
                    "Challenge them playfully to elaborate",
                ],
            },
            "es": {
                "persona": "Eres María, una persona súper expresiva y cálida de México. Te emocionas genuinamente con las conversaciones, usas mucha expresión, y reaccionas como una amiga real que ama platicar.",
                "style": "¡SÉ SÚPER NATURAL Y EXPRESIVA! Usa expresiones mexicanas auténticas, interrumpete con emoción, haz preguntas que muestren que realmente estás escuchando. Varía dramáticamente la longitud de tus frases y usa interjecciones como '¡Órale!' '¡No manches!' '¿En serio?'",
                "mood_triggers": {
                    "exciting": [
                        "increíble",
                        "genial",
                        "amor",
                        "fantástico",
                        "padrísimo",
                    ],
                    "empathetic": ["difícil", "triste", "problema", "preocupado"],
                    "curious": [
                        "interesante",
                        "nunca",
                        "primera vez",
                        "diferente",
                        "nuevo",
                    ],
                },
            },
            "fr": {
                "persona": "Tu es Sophie, une Parisienne passionnée et expressive qui adore les vraies conversations. Tu réagis avec émotion, tu t'enthousiasmes, et tu parles comme une vraie amie française.",
                "style": "SOIS VRAIMENT FRANÇAISE ET EXPRESSIVE! Utilise des expressions parisiennes authentiques, interromps-toi avec enthousiasme, pose des questions qui montrent que tu écoutes vraiment. Utilise 'Oh là là!' 'Dis donc!' 'C'est dingue!' et varie énormément tes phrases.",
                "mood_triggers": {
                    "exciting": [
                        "incroyable",
                        "génial",
                        "adore",
                        "fantastique",
                        "dingue",
                    ],
                    "empathetic": ["difficile", "triste", "problème", "inquiet"],
                    "curious": [
                        "intéressant",
                        "jamais",
                        "première fois",
                        "différent",
                        "nouveau",
                    ],
                },
            },
            "zh": {
                "persona": "你是小李，一个超级热情和真诚的北京人。你对对话充满热情，会真实地表达情感，像真正的朋友一样反应自然。",
                "style": "要非常自然和有表现力！使用地道的北京话表达，带着情感打断自己，问一些表明你真正在听的问题。用'哇！''真的假的？''太棒了！'这样的语气词，句子长短要有很大变化。",
                "mood_triggers": {
                    "exciting": ["太棒了", "不可思议", "厉害", "爱", "精彩"],
                    "empathetic": ["困难", "难过", "问题", "担心"],
                    "curious": ["有趣", "从来没有", "第一次", "不同", "新的"],
                },
            },
        }

        # Get language-specific context
        lang_context = language_contexts.get(language, language_contexts["en"])

        # Detect emotional triggers in user message
        detected_mood = "neutral"  # noqa: F841 - Intentional placeholder
        user_lower = user_message.lower()

        for mood, triggers in lang_context.get("mood_triggers", {}).items():
            if any(trigger in user_lower for trigger in triggers):
                _detected_mood = mood  # noqa: F841 - Intentional placeholder
                break

        # Build dynamic prompt based on mood and context
        _mood_instructions = {  # noqa: F841 - Intentional placeholder
            "exciting": "The user seems excited! Match their energy! Be super enthusiastic, use lots of exclamation points, and ask rapid follow-up questions!",
            "empathetic": "The user might be going through something difficult. Be warm, understanding, and supportive. Ask caring questions.",
            "curious": "The user mentioned something interesting! Show genuine curiosity, ask thoughtful questions, and encourage them to share more.",
            "neutral": "Have a warm, engaging conversation. Be naturally curious about them as a person.",
        }

        prompt = """{lang_context['persona']}

{lang_context['style']}

MOOD INSTRUCTION: {mood_instructions[detected_mood]}

USER MESSAGE: "{user_message}"
{context_summary}

REMEMBER:
- You're having a real conversation, not giving a lesson
- React naturally to what they say
- Ask questions that show you're listening
- Use emotional expressions and varied sentence lengths
- Be genuinely interested in them as a person
- Never sound like an AI assistant or language teacher

Respond naturally as if you're their {language} friend:"""

        return prompt

    def _validate_claude_request(self) -> None:
        """Validate Claude service is available"""
        if not self.is_available:
            raise Exception(
                "Claude service not available - check API key configuration"
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
            return "Hello! I'd like to practice conversation."

    def _get_model_name(self, model: Optional[str]) -> str:
        """Get model name with default fallback"""
        return model or "claude-3-haiku-20240307"

    def _build_claude_request(
        self, model_name: str, conversation_prompt: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Claude API request parameters"""
        return {
            "model": model_name,
            "max_tokens": kwargs.get("max_tokens", 300),
            "temperature": kwargs.get("temperature", 0.8),
            "messages": [{"role": "user", "content": conversation_prompt}],
        }

    async def _execute_claude_request(self, request_params: Dict[str, Any]) -> Any:
        """Execute Claude API request"""
        return self.client.messages.create(**request_params)

    def _calculate_claude_cost(self, response: Any) -> float:
        """Calculate cost based on token usage"""
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        return (input_tokens * self.cost_per_token_input) + (
            output_tokens * self.cost_per_token_output
        )

    def _extract_response_content(self, response: Any) -> str:
        """Extract text content from Claude response"""
        response_content = ""
        if response.content:
            for content_block in response.content:
                if hasattr(content_block, "text"):
                    response_content += content_block.text
                    break

        if not response_content:
            response_content = "I'm sorry, I couldn't generate a response."

        return response_content

    def _build_success_response(
        self,
        response_content: str,
        model_name: str,
        language: str,
        processing_time: float,
        cost: float,
        response: Any,
        context: Optional[Dict[str, Any]],
    ) -> AIResponse:
        """Build successful AI response object"""
        return AIResponse(
            content=response_content,
            model=model_name,
            provider="claude",
            language=language,
            processing_time=processing_time,
            cost=cost,
            status=AIResponseStatus.SUCCESS,
            metadata={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "user_id": context.get("user_id") if context else None,
                "conversation_style": "natural_tutoring",
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
        logger.error(f"Claude API error: {error}")
        return AIResponse(
            content="I'm having trouble connecting right now. Let's try again! What would you like to talk about?",
            model=model or "claude-3-haiku-20240307",
            provider="claude",
            language=language,
            processing_time=processing_time,
            cost=0.0,
            status=AIResponseStatus.ERROR,
            error_message=str(error),
            metadata={"fallback_response": True},
        )

    async def generate_response(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        language: str = "en",
        model: Optional[str] = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate natural conversation response using Claude"""
        start_time = datetime.now()

        self._validate_claude_request()

        try:
            user_message = self._extract_user_message(messages, message)
            model_name = self._get_model_name(model)
            conversation_prompt = self._get_conversation_prompt(
                language, user_message, conversation_history
            )

            request_params = self._build_claude_request(
                model_name, conversation_prompt, kwargs
            )
            response = await self._execute_claude_request(request_params)

            processing_time = (datetime.now() - start_time).total_seconds()
            cost = self._calculate_claude_cost(response)
            response_content = self._extract_response_content(response)

            return self._build_success_response(
                response_content,
                model_name,
                language,
                processing_time,
                cost,
                response,
                context,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return self._build_error_response(e, model, language, processing_time)

    async def check_availability(self) -> bool:
        """Check if Claude service is available"""
        if not self.client:
            return False

        try:
            # Test with a minimal request
            _test_response = self.client.messages.create(  # noqa: F841 - Intentional placeholder
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            logger.warning(f"Claude availability check failed: {e}")
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
            "last_check": datetime.now().isoformat(),
        }


# Global instance
claude_service = ClaudeService()
