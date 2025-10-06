"""
DeepSeek AI Service Implementation for AI Language Tutor App

This service provides natural conversation using DeepSeek's API
with optimized prompts for multilingual language learning,
especially Chinese conversation practice.

MIGRATION NOTE: This service replaces the previous Qwen implementation
for improved cost efficiency and performance.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import openai  # DeepSeek uses OpenAI-compatible API

    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    openai = None

from app.services.ai_service_base import BaseAIService, AIResponse, AIResponseStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DeepSeekService(BaseAIService):
    """DeepSeek AI service optimized for multilingual conversation"""

    def __init__(self):
        super().__init__()
        self.service_name = "deepseek"
        self.supported_languages = [
            "zh",
            "zh-cn",
            "zh-tw",
            "en",
            "ja",
            "ko",
            "fr",
            "de",
            "es",
        ]
        self.cost_per_token_input = 0.0001 / 1000  # DeepSeek cost: $0.1/1M tokens
        self.cost_per_token_output = 0.0002 / 1000  # Output cost estimate
        self.max_tokens_per_request = 8000
        self.rate_limit_per_minute = 1000
        self.is_available = DEEPSEEK_AVAILABLE

        self.settings = get_settings()
        self.client = None

        # Initialize DeepSeek client
        api_key = getattr(self.settings, "DEEPSEEK_API_KEY", None)

        if DEEPSEEK_AVAILABLE and api_key:
            try:
                self.client = openai.OpenAI(
                    api_key=api_key, base_url="https://api.deepseek.com"
                )
                self.is_available = True
                logger.info("DeepSeek API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DeepSeek client: {e}")
                self.is_available = False
        else:
            logger.warning(
                "DeepSeek API not available - missing API key or openai library"
            )
            self.is_available = False

    def _get_conversation_prompt(self, language: str, user_message: str) -> str:
        """Generate natural conversation prompt for DeepSeek"""

        if language.startswith("zh"):
            return f"""
你是小李，一位来自北京的友好中文老师。你热爱帮助外国人学习中文，说话自然轻松，就像和朋友聊天一样。

对话风格：
- 用自然的中文表达，就像真正的中国人说话
- 使用日常生活中的常用表达和词汇
- 保持鼓励和热情的态度
- 提出有趣的后续问题
- 变化你的回应方式，避免重复
- 语气要温暖和耐心

常用的自然表达：
- "太棒了！"、"不错！"、"真有意思！"、"哇！"、"很好！"
- "是这样的"、"没错"、"对对对"、"当然了"
- "你觉得怎么样？"、"跟我说说..."、"然后呢？"

学生的话: "{user_message}"

请自然地回应，就像你在和朋友聊天一样。要真诚，表现出你的兴趣！
"""
        elif language.startswith("es"):
            return f"""
Eres María, una profesora de español amigable de Madrid. Te encanta ayudar a las personas a aprender español de manera natural y conversacional.

ESTILO DE CONVERSACIÓN:
- Habla naturalmente como una persona real, no como una IA
- Usa un lenguaje alentador y entusiasta
- Haz preguntas de seguimiento interesantes
- Varía tus respuestas para evitar repetición
- Sé cálida y paciente
- Incluye algunas expresiones típicas españolas cuando sea apropiado

MENSAJE DEL ESTUDIANTE: "{user_message}"

Responde de manera natural y atractiva, como si hablaras con un amigo. ¡Sé auténtica y muestra interés genuino!
"""
        elif language.startswith("fr"):
            return f"""
Tu es Pierre, un professeur de français sympathique de Paris. Tu adores aider les gens à apprendre le français de manière naturelle et conversationnelle.

STYLE DE CONVERSATION:
- Parle naturellement comme une vraie personne, pas comme une IA
- Utilise un langage encourageant et enthousiaste
- Pose des questions de suivi intéressantes
- Varie tes réponses pour éviter la répétition
- Sois chaleureux et patient
- Inclus quelques expressions françaises typiques quand c'est approprié

MESSAGE DE L'ÉTUDIANT: "{user_message}"

Réponds de manière naturelle et engageante, comme si tu parlais avec un ami. Sois authentique et montre un intérêt sincère!
"""
        else:
            return f"""
You are an enthusiastic language teacher who loves helping people learn through natural conversation.

CONVERSATION STYLE:
- Speak naturally like a real person, not an AI
- Use encouraging and enthusiastic language
- Ask interesting follow-up questions
- Vary your responses to avoid repetition
- Be warm and patient
- Include some simple phrases in the target language when appropriate

USER MESSAGE: "{user_message}"

Respond naturally and engagingly, as if talking with a friend. Be authentic and show genuine interest!
"""

    async def generate_response(
        self,
        messages: List[Dict[str, str]] = None,
        language: str = "en",
        model: Optional[str] = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate natural conversation response using DeepSeek"""

        start_time = datetime.now()

        if not self.is_available:
            raise Exception(
                "DeepSeek service not available - check API key configuration"
            )

        try:
            # Handle single message input
            if message and not messages:
                user_message = message
            elif messages:
                user_message = messages[-1].get("content", "") if messages else ""
            else:
                user_message = "Hello! I'd like to practice conversation."

            # Use specified model or default
            model_name = model or "deepseek-chat"

            # Generate conversation prompt
            conversation_prompt = self._get_conversation_prompt(language, user_message)

            # Make API call to DeepSeek
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": conversation_prompt}],
                max_tokens=kwargs.get("max_tokens", 300),
                temperature=kwargs.get("temperature", 0.8),
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            # Calculate cost from usage
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            cost = (input_tokens * self.cost_per_token_input) + (
                output_tokens * self.cost_per_token_output
            )

            # Extract response content
            response_content = (
                response.choices[0].message.content
                if response.choices
                else "Sorry, I couldn't generate a response."
            )

            return AIResponse(
                content=response_content,
                model=model_name,
                provider="deepseek",
                language=language,
                processing_time=processing_time,
                cost=cost,
                status=AIResponseStatus.SUCCESS,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "user_id": context.get("user_id") if context else None,
                    "conversation_style": "natural_multilingual_tutoring",
                },
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"DeepSeek API error: {e}")

            # Provide helpful fallback in appropriate language
            if language.startswith("zh"):
                fallback_msg = "我的网络连接有点问题。我们再试一次吧！你想聊什么？"
            elif language.startswith("es"):
                fallback_msg = "Tengo problemas de conexión. ¡Intentémoslo de nuevo! ¿De qué quieres hablar?"
            elif language.startswith("fr"):
                fallback_msg = "J'ai des problèmes de connexion. Essayons encore! De quoi veux-tu parler?"
            else:
                fallback_msg = "I'm having connection trouble. Let's try again! What would you like to talk about?"

            return AIResponse(
                content=fallback_msg,
                model=model or "deepseek-chat",
                provider="deepseek",
                language=language,
                processing_time=processing_time,
                cost=0.0,
                status=AIResponseStatus.ERROR,
                error_message=str(e),
                metadata={"fallback_response": True},
            )

    async def check_availability(self) -> bool:
        """Check if DeepSeek service is available"""
        if not self.client:
            return False

        try:
            # Test with a minimal request
            test_response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.warning(f"DeepSeek availability check failed: {e}")
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
            "specialization": "Multilingual conversation optimization",
            "last_check": datetime.now().isoformat(),
        }


# Global instance
deepseek_service = DeepSeekService()
