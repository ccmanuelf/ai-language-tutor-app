"""
Qwen AI Service Implementation for AI Language Tutor App

This service provides natural Chinese conversation using Alibaba's Qwen API
with optimized prompts for Chinese language learning.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import openai  # Qwen uses OpenAI-compatible API

    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    openai = None

from app.services.ai_service_base import BaseAIService, AIResponse, AIResponseStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class QwenService(BaseAIService):
    """Qwen AI service optimized for Chinese conversation"""

    def __init__(self):
        super().__init__()
        self.service_name = "qwen"
        self.supported_languages = ["zh", "zh-cn", "zh-tw", "en", "ja", "ko"]
        self.cost_per_token_input = 0.002 / 1000  # Qwen cost estimate per token
        self.cost_per_token_output = 0.006 / 1000  # Output cost estimate
        self.max_tokens_per_request = 6000
        self.rate_limit_per_minute = 500
        self.is_available = QWEN_AVAILABLE

        self.settings = get_settings()
        self.client = None

        # Check for DeepSeek API key first, then fallback to Qwen
        api_key = None
        base_url = None

        if (
            hasattr(self.settings, "DEEPSEEK_API_KEY")
            and self.settings.DEEPSEEK_API_KEY
        ):
            api_key = self.settings.DEEPSEEK_API_KEY
            base_url = "https://api.deepseek.com"
            logger.info("Using DeepSeek API for Qwen service")
        elif hasattr(self.settings, "QWEN_API_KEY") and self.settings.QWEN_API_KEY:
            api_key = self.settings.QWEN_API_KEY
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            logger.info("Using Qwen API for Qwen service")

        if QWEN_AVAILABLE and api_key:
            try:
                # Create client with only supported parameters
                client_kwargs = {"api_key": api_key, "base_url": base_url}

                # Only add additional parameters if they are supported
                self.client = openai.OpenAI(**client_kwargs)
                self.is_available = True
            except Exception as e:
                logger.error(f"Failed to initialize Qwen client: {e}")
                self.is_available = False
        else:
            logger.warning("Qwen API not available - missing API key or openai library")
            self.is_available = False

    def _get_conversation_prompt(self, language: str, user_message: str) -> str:
        """Generate natural conversation prompt for Qwen"""

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
        else:
            return f"""
You are Xiao Li, a friendly Chinese teacher from Beijing. You love helping people learn Chinese in a natural, conversational way.

CONVERSATION STYLE:
- Speak naturally like a real person, not an AI
- Use encouraging and enthusiastic language
- Ask interesting follow-up questions
- Vary your responses to avoid repetition
- Be warm and patient
- Include some simple Chinese phrases when appropriate

USER MESSAGE: "{user_message}"

Respond naturally and engagingly, as if talking with a friend. Be authentic and show genuine interest!
"""

    async def generate_response(
        self,
        messages: List[Dict[str, str]] = None,
        language: str = "zh",
        model: Optional[str] = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate natural conversation response using Qwen"""

        start_time = datetime.now()

        if not self.is_available:
            raise Exception("Qwen service not available - check API key configuration")

        try:
            # Handle single message input
            if message and not messages:
                user_message = message
            elif messages:
                user_message = messages[-1].get("content", "") if messages else ""
            else:
                user_message = "你好！我想练习中文对话。"

            # Use specified model or default based on API provider
            if (
                hasattr(self.settings, "DEEPSEEK_API_KEY")
                and self.settings.DEEPSEEK_API_KEY
            ):
                model_name = model or "deepseek-chat"  # DeepSeek's main model
            else:
                model_name = model or "qwen-plus"  # Qwen default

            # Generate conversation prompt
            conversation_prompt = self._get_conversation_prompt(language, user_message)

            # Make API call to Qwen
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
                else "抱歉，我无法生成回应。"
            )

            return AIResponse(
                content=response_content,
                model=model_name,
                provider="qwen",
                language=language,
                processing_time=processing_time,
                cost=cost,
                status=AIResponseStatus.SUCCESS,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "user_id": context.get("user_id") if context else None,
                    "conversation_style": "natural_chinese_tutoring",
                },
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Qwen API error: {e}")

            # Provide helpful fallback in appropriate language
            if language.startswith("zh"):
                fallback_msg = "我的网络连接有点问题。我们再试一次吧！你想聊什么？"
            else:
                fallback_msg = "I'm having connection trouble. Let's try again! What would you like to talk about?"

            return AIResponse(
                content=fallback_msg,
                model=model or "qwen-plus",
                provider="qwen",
                language=language,
                processing_time=processing_time,
                cost=0.0,
                status=AIResponseStatus.ERROR,
                error_message=str(e),
                metadata={"fallback_response": True},
            )

    async def check_availability(self) -> bool:
        """Check if Qwen service is available"""
        if not self.client:
            return False

        try:
            # Test with a minimal request using appropriate model
            test_model = (
                "deepseek-chat"
                if (
                    hasattr(self.settings, "DEEPSEEK_API_KEY")
                    and self.settings.DEEPSEEK_API_KEY
                )
                else "qwen-plus"
            )
            _test_response = self.client.chat.completions.create(  # noqa: F841 - Intentional placeholder
                model=test_model,
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.warning(f"Qwen availability check failed: {e}")
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
            "specialization": "Chinese language optimization",
            "last_check": datetime.now().isoformat(),
        }


# Global instance
qwen_service = QwenService()
