"""
Ollama Local LLM Service for AI Language Tutor App

This service provides local LLM capabilities using Ollama as a fallback when:
- Budget limits are exceeded
- Internet connectivity is unavailable
- User prefers offline operation
- API services are temporarily unavailable

Features:
- Local model management
- Conversation handling
- Language learning optimization
- Cost-free operation
- Privacy-focused (no data leaves device)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp

from app.core.config import get_settings
from app.services.ai_service_base import AIResponse, BaseAIService, StreamingResponse

logger = logging.getLogger(__name__)


class OllamaModelSize(Enum):
    """Available Ollama model sizes"""

    SMALL = "7b"
    MEDIUM = "13b"
    LARGE = "70b"


@dataclass
class OllamaModel:
    """Ollama model configuration"""

    name: str
    size: OllamaModelSize
    languages: List[str]
    use_case: str
    memory_gb: float
    description: str


class OllamaService(BaseAIService):
    """Ollama local LLM service implementation"""

    def __init__(self):
        super().__init__()
        self.service_name = "ollama"
        self.base_url = get_settings().OLLAMA_HOST or "http://localhost:11434"
        self.default_model = "llama2:7b"  # Default model since not in config
        self.available_models = self._get_available_models()
        self.session: Optional[aiohttp.ClientSession] = None

    def _get_available_models(self) -> Dict[str, OllamaModel]:
        """Get available Ollama models optimized for language learning"""
        return {
            "llama2:7b": OllamaModel(
                name="llama2:7b",
                size=OllamaModelSize.SMALL,
                languages=["en", "es", "fr", "de", "it"],
                use_case="General conversation, English learning",
                memory_gb=4.0,
                description="Fast, efficient model for basic conversations",
            ),
            "llama2:13b": OllamaModel(
                name="llama2:13b",
                size=OllamaModelSize.MEDIUM,
                languages=["en", "es", "fr", "de", "it", "pt"],
                use_case="Advanced conversation, grammar correction",
                memory_gb=8.0,
                description="Better quality responses, grammar assistance",
            ),
            "codellama:7b": OllamaModel(
                name="codellama:7b",
                size=OllamaModelSize.SMALL,
                languages=["en"],
                use_case="Technical English, programming terminology",
                memory_gb=4.0,
                description="Specialized for technical language learning",
            ),
            "mistral:7b": OllamaModel(
                name="mistral:7b",
                size=OllamaModelSize.SMALL,
                languages=["en", "fr"],
                use_case="French learning, conversation practice",
                memory_gb=4.0,
                description="Good for French language learning",
            ),
            "neural-chat:7b": OllamaModel(
                name="neural-chat:7b",
                size=OllamaModelSize.SMALL,
                languages=["en"],
                use_case="Conversational practice, dialog training",
                memory_gb=4.0,
                description="Optimized for natural conversations",
            ),
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        # Check if session is invalid (closed or from different event loop)
        need_new_session = False

        if self.session is None or self.session.closed:
            need_new_session = True
        else:
            # Check if the session's event loop is closed (happens in tests)
            try:
                import asyncio

                current_loop = asyncio.get_running_loop()
                if self.session._loop != current_loop or self.session._loop.is_closed():
                    need_new_session = True
                    # Close the old session properly
                    await self.session.close()
            except RuntimeError:
                # No running loop - session is definitely stale
                need_new_session = True

        if need_new_session:
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes for model loading
            self.session = aiohttp.ClientSession(timeout=timeout)

        return self.session

    async def check_availability(self) -> bool:
        """Check if Ollama server is running and accessible"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ollama availability check failed: {type(e).__name__}: {e}")
            logger.error(
                f"Session state: closed={self.session.closed if self.session else 'None'}"
            )
            return False

    async def list_models(self) -> List[Dict[str, Any]]:
        """List installed models on Ollama server"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model to Ollama server"""
        try:
            logger.info(f"Pulling Ollama model: {model_name}")
            session = await self._get_session()

            payload = {"name": model_name}

            async with session.post(
                f"{self.base_url}/api/pull", json=payload
            ) as response:
                if response.status == 200:
                    # Stream the download progress
                    async for line in response.content:
                        try:
                            progress = json.loads(line.decode().strip())
                            if "status" in progress:
                                logger.info(f"Pull progress: {progress['status']}")
                        except (json.JSONDecodeError, TypeError, ValueError):
                            continue
                    return True
                return False

        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False

    async def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a model is available, pull if necessary"""
        installed_models = await self.list_models()
        installed_names = [model.get("name", "") for model in installed_models]

        if model_name not in installed_names:
            logger.info(f"Model {model_name} not found, attempting to pull...")
            return await self.pull_model(model_name)

        return True

    def _analyze_model_capabilities(self, model_name: str) -> Dict[str, Any]:
        """
        Phase 5: Analyze model capabilities based on its name and characteristics.

        This uses naming conventions and known patterns to infer capabilities.
        No hardcoded preferences - pure capability detection.

        Args:
            model_name: The model name (e.g., "codellama:7b", "mistral:7b")

        Returns:
            Dict with capability scores and metadata
        """
        name_lower = model_name.lower()

        capabilities = {
            "name": model_name,
            "is_code_model": False,
            "is_multilingual": False,
            "is_chat_optimized": False,
            "is_reasoning_model": False,
            "language_support": [],
            "use_case_scores": {},
            "size_category": "unknown",
        }

        # Detect code-specialized models
        code_indicators = ["code", "coder", "codellama", "deepseek-coder", "deepcoder"]
        if any(indicator in name_lower for indicator in code_indicators):
            capabilities["is_code_model"] = True
            capabilities["use_case_scores"]["technical"] = 10
            capabilities["use_case_scores"]["conversation"] = 5
            capabilities["use_case_scores"]["grammar"] = 3

        # Detect multilingual models by common indicators
        # Note: Most modern LLMs have some multilingual capability
        multilingual_keywords = ["multilingual", "multi", "llama", "mistral", "gemma"]
        if any(keyword in name_lower for keyword in multilingual_keywords):
            capabilities["is_multilingual"] = True
        # Also check for specific language codes in model name (e.g., "zh", "fr")
        if any(
            lang in name_lower
            for lang in [
                "zh",
                "cn",
                "chinese",
                "fr",
                "french",
                "de",
                "german",
                "es",
                "spanish",
            ]
        ):
            capabilities["is_multilingual"] = True

        # Detect chat-optimized models
        chat_indicators = ["chat", "instruct", "neural-chat"]
        if any(indicator in name_lower for indicator in chat_indicators):
            capabilities["is_chat_optimized"] = True
            capabilities["use_case_scores"]["conversation"] = 10
            capabilities["use_case_scores"]["grammar"] = 7
            capabilities["use_case_scores"]["technical"] = 5

        # Detect reasoning models
        reasoning_indicators = ["deepseek-r1", "thinking", "reasoning"]
        if any(indicator in name_lower for indicator in reasoning_indicators):
            capabilities["is_reasoning_model"] = True
            capabilities["use_case_scores"]["technical"] = 9
            capabilities["use_case_scores"]["grammar"] = 8
            capabilities["use_case_scores"]["conversation"] = 6

        # Language-specific models - detected dynamically from model name
        # Default to English support for all models
        capabilities["language_support"] = ["en"]

        # Detect additional language support from model name
        lang_indicators = {
            "zh": ["zh", "cn", "chinese", "qwen"],
            "fr": ["fr", "french", "mistral"],
            "de": ["de", "german"],
            "es": ["es", "spanish"],
            "it": ["it", "italian"],
            "pt": ["pt", "portuguese"],
            "ja": ["ja", "japanese"],
            "ko": ["ko", "korean"],
        }

        for lang_code, keywords in lang_indicators.items():
            if any(keyword in name_lower for keyword in keywords):
                if lang_code not in capabilities["language_support"]:
                    capabilities["language_support"].append(lang_code)

        # Well-known multilingual models get broad support
        if "llama" in name_lower or "mistral" in name_lower:
            # These families are known to handle multiple European languages
            for lang in ["es", "fr", "de", "it", "pt"]:
                if lang not in capabilities["language_support"]:
                    capabilities["language_support"].append(lang)

        # Default scores for general models
        if not capabilities["use_case_scores"]:
            capabilities["use_case_scores"] = {
                "conversation": 7,
                "technical": 7,
                "grammar": 7,
            }

        # Extract size category (check larger sizes first to avoid substring matches)
        if "70b" in name_lower or "65b" in name_lower or "30b" in name_lower:
            capabilities["size_category"] = "xlarge"
        elif "13b" in name_lower or "14b" in name_lower or "16b" in name_lower:
            capabilities["size_category"] = "large"
        elif "7b" in name_lower or "8b" in name_lower:
            capabilities["size_category"] = "medium"
        elif (
            "1b" in name_lower
            or "2b" in name_lower
            or "3b" in name_lower
            or "4b" in name_lower
        ):
            capabilities["size_category"] = "small"

        return capabilities

    def get_recommended_model(
        self,
        language: str,
        use_case: str = "conversation",
        installed_models: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Get recommended model for specific language and use case.

        Phase 5: PURE CAPABILITY-BASED SELECTION - NO HARDCODED PREFERENCES.
        Analyzes actual installed models and selects based on their capabilities.

        Args:
            language: Target language code
            use_case: Use case type (conversation, technical, grammar, etc.)
            installed_models: List of installed models from list_models()

        Returns:
            Model name that is actually installed and best suited for the task
        """
        if installed_models is None:
            logger.warning(
                "get_recommended_model called without installed_models. Cannot recommend."
            )
            return "llama2:7b"  # Fallback for backward compatibility

        installed_names = [m.get("name", "") for m in installed_models]

        if not installed_names:
            logger.error("No Ollama models installed!")
            return "llama2:7b"

        # Phase 5: Analyze capabilities of ALL installed models
        analyzed_models = []
        for model_name in installed_names:
            capabilities = self._analyze_model_capabilities(model_name)
            analyzed_models.append(capabilities)

        # Score each model for the requested use case and language
        scored_models = []
        for model in analyzed_models:
            score = 0

            # Use case score
            use_case_score = model["use_case_scores"].get(use_case, 5)
            score += use_case_score * 2  # Weight use case heavily

            # Language support score
            if model["language_support"] and language in model["language_support"]:
                score += 5
            elif model["is_multilingual"]:
                score += 2  # Multilingual models can handle most languages

            # Prefer larger models for complex tasks
            if use_case in ["technical", "grammar"]:
                size_bonus = {
                    "small": 0,
                    "medium": 2,
                    "large": 4,
                    "xlarge": 3,  # Very large might be slow
                    "unknown": 1,
                }
                score += size_bonus.get(model["size_category"], 0)

            # Prefer chat-optimized for conversation
            if use_case == "conversation" and model["is_chat_optimized"]:
                score += 3

            scored_models.append((model["name"], score))

        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)

        recommended = scored_models[0][0]
        logger.info(
            f"Capability-based selection: {recommended} "
            f"(score: {scored_models[0][1]}) for {use_case}/{language} "
            f"from {len(installed_names)} installed models"
        )

        return recommended

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate response using Ollama"""
        start_time = datetime.now()

        try:
            # Select model
            if not model:
                model = self.get_recommended_model(
                    language, kwargs.get("use_case", "conversation")
                )

            # Ensure model is available
            if not await self.ensure_model_available(model):
                raise Exception(f"Model {model} not available and cannot be pulled")

            # Format prompt for Ollama
            prompt = self._format_prompt_for_language_learning(messages, language)

            # Prepare request
            session = await self._get_session()
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            }

            # Make request
            async with session.post(
                f"{self.base_url}/api/generate", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Ollama API error: {response.status} - {error_text}"
                    )

                data = await response.json()
                response_text = data.get("response", "")

                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()

                return AIResponse(
                    content=response_text,
                    model=model,
                    provider="ollama",
                    language=language,
                    processing_time=processing_time,
                    cost=0.0,  # Local models are free
                    metadata={
                        "model_size": self.available_models.get(model, {}).memory_gb
                        if model in self.available_models
                        else "unknown",
                        "local_processing": True,
                        "privacy_mode": True,
                        "done": data.get("done", True),
                        "context": data.get("context", []),
                        "total_duration": data.get("total_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                        "eval_count": data.get("eval_count", 0),
                    },
                )

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"Local AI generation failed: {str(e)}")

    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Generate streaming response using Ollama"""
        start_time = datetime.now()

        try:
            # Select model
            if not model:
                model = self.get_recommended_model(
                    language, kwargs.get("use_case", "conversation")
                )

            # Ensure model is available
            if not await self.ensure_model_available(model):
                raise Exception(f"Model {model} not available and cannot be pulled")

            # Format prompt
            prompt = self._format_prompt_for_language_learning(messages, language)

            # Prepare streaming request
            session = await self._get_session()
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            }

            async with session.post(
                f"{self.base_url}/api/generate", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Ollama streaming error: {response.status} - {error_text}"
                    )

                async for line in response.content:
                    try:
                        chunk_data = json.loads(line.decode().strip())

                        if "response" in chunk_data:
                            processing_time = (
                                datetime.now() - start_time
                            ).total_seconds()

                            yield StreamingResponse(
                                content=chunk_data["response"],
                                model=model,
                                provider="ollama",
                                language=language,
                                is_final=chunk_data.get("done", False),
                                processing_time=processing_time,
                                cost=0.0,
                                metadata={
                                    "local_processing": True,
                                    "privacy_mode": True,
                                    "context": chunk_data.get("context", []),
                                    "done": chunk_data.get("done", False),
                                },
                            )

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise Exception(f"Local AI streaming failed: {str(e)}")

    def _format_prompt_for_language_learning(
        self, messages: List[Dict[str, str]], language: str
    ) -> str:
        """Format messages into a prompt optimized for language learning"""

        # Language-specific instructions
        language_instructions = {
            "en": "You are a helpful English language tutor. Provide clear, encouraging responses and gently correct any grammar mistakes.",
            "fr": "Tu es un professeur de français serviable. Réponds clairement et corrige gentiment les erreurs de grammaire.",
            "es": "Eres un tutor de español útil. Proporciona respuestas claras y alentadoras y corrige suavemente los errores gramaticales.",
            "de": "Du bist ein hilfreicher Deutschlehrer. Gib klare, ermutigende Antworten und korrigiere Grammatikfehler sanft.",
            "it": "Sei un tutor di italiano utile. Fornisci risposte chiare e incoraggianti e correggi gentilmente gli errori grammaticali.",
            "pt": "Você é um tutor de português útil. Forneça respostas claras e encorajadoras e corrija suavemente os erros gramaticais.",
            "zh": "你是一个有用的中文语言导师。提供清晰、鼓励的回答，并温和地纠正语法错误。",
        }

        system_instruction = language_instructions.get(
            language,
            "You are a helpful language tutor. Provide clear, encouraging responses.",
        )

        # Build conversation prompt
        prompt_parts = [f"System: {system_instruction}\n"]

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "user":
                prompt_parts.append(f"Student: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Tutor: {content}\n")

        prompt_parts.append("Tutor: ")

        return "".join(prompt_parts)

    async def get_health_status(self) -> Dict[str, Any]:
        """Get Ollama service health status"""
        try:
            is_available = await self.check_availability()

            if not is_available:
                return {
                    "service_name": self.service_name,
                    "status": "unavailable",
                    "message": "Ollama server not running",
                    "models": [],
                    "recommendations": [
                        "Install Ollama from https://ollama.ai/",
                        "Start Ollama server: 'ollama serve'",
                        "Pull a model: 'ollama pull llama2:7b'",
                    ],
                }

            models = await self.list_models()

            return {
                "service_name": self.service_name,
                "status": "healthy",
                "message": "Ollama server running",
                "server_url": self.base_url,
                "models_installed": len(models),
                "available_models": [model.get("name") for model in models],
                "recommended_models": list(self.available_models.keys()),
                "memory_usage": "Local processing - no API costs",
                "privacy": "Complete - data stays on device",
            }

        except Exception as e:
            return {
                "service_name": self.service_name,
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "error": str(e),
            }

    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Ollama Management Functions
class OllamaManager:
    """Manages Ollama installation and model management"""

    def __init__(self):
        self.service = OllamaService()

    async def check_installation(self) -> Dict[str, Any]:
        """Check if Ollama is properly installed and configured"""
        status = await self.service.get_health_status()

        if status["status"] == "unavailable":
            return {
                "installed": False,
                "running": False,
                "models": [],
                "setup_required": True,
                "instructions": status.get("recommendations", []),
            }

        models = await self.service.list_models()

        return {
            "installed": True,
            "running": True,
            "models": len(models),
            "model_names": [model.get("name") for model in models],
            "setup_required": len(models) == 0,
            "recommended_setup": self._get_recommended_setup(),
        }

    def _get_recommended_setup(self) -> List[str]:
        """Get recommended setup steps for optimal language learning"""
        return [
            "ollama pull llama2:7b  # General purpose, 4GB RAM",
            "ollama pull mistral:7b  # Good for French, 4GB RAM",
            "ollama pull neural-chat:7b  # Conversational, 4GB RAM",
            "ollama pull llama2:13b  # Better quality, 8GB RAM (optional)",
        ]

    async def setup_for_language_learning(self) -> Dict[str, Any]:
        """Setup Ollama with recommended models for language learning"""
        if not await self.service.check_availability():
            return {
                "success": False,
                "message": "Ollama server not available. Please install and start Ollama first.",
                "instructions": [
                    "1. Install from https://ollama.ai/",
                    "2. Run 'ollama serve' to start server",
                    "3. Try this setup again",
                ],
            }

        # Pull essential models
        essential_models = ["llama2:7b", "mistral:7b"]
        results = {}

        for model in essential_models:
            logger.info(f"Setting up model: {model}")
            success = await self.service.pull_model(model)
            results[model] = "success" if success else "failed"

        successful_models = [
            model for model, status in results.items() if status == "success"
        ]

        return {
            "success": len(successful_models) > 0,
            "models_setup": successful_models,
            "setup_results": results,
            "message": f"Successfully set up {len(successful_models)}/{len(essential_models)} essential models",
            "ready_for_fallback": len(successful_models) > 0,
        }


# Global instances
ollama_service = OllamaService()
ollama_manager = OllamaManager()


# Convenience functions
async def get_ollama_status() -> Dict[str, Any]:
    """Get Ollama service status"""
    return await ollama_service.get_health_status()


async def is_ollama_available() -> bool:
    """Check if Ollama is available for fallback"""
    return await ollama_service.check_availability()


async def generate_local_response(
    messages: List[Dict[str, str]], language: str = "en", **kwargs
) -> AIResponse:
    """Generate response using local Ollama"""
    return await ollama_service.generate_response(messages, language, **kwargs)


async def setup_ollama_for_language_learning() -> Dict[str, Any]:
    """Setup Ollama with language learning models"""
    return await ollama_manager.setup_for_language_learning()
