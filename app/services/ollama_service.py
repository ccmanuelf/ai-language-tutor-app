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

import asyncio
import logging
import json
import aiohttp
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.services.ai_service_base import BaseAIService, AIResponse, StreamingResponse
from app.core.config import get_settings

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
                description="Fast, efficient model for basic conversations"
            ),
            "llama2:13b": OllamaModel(
                name="llama2:13b", 
                size=OllamaModelSize.MEDIUM,
                languages=["en", "es", "fr", "de", "it", "pt"],
                use_case="Advanced conversation, grammar correction",
                memory_gb=8.0,
                description="Better quality responses, grammar assistance"
            ),
            "codellama:7b": OllamaModel(
                name="codellama:7b",
                size=OllamaModelSize.SMALL,
                languages=["en"],
                use_case="Technical English, programming terminology",
                memory_gb=4.0,
                description="Specialized for technical language learning"
            ),
            "mistral:7b": OllamaModel(
                name="mistral:7b",
                size=OllamaModelSize.SMALL,
                languages=["en", "fr"],
                use_case="French learning, conversation practice",
                memory_gb=4.0,
                description="Good for French language learning"
            ),
            "neural-chat:7b": OllamaModel(
                name="neural-chat:7b",
                size=OllamaModelSize.SMALL,
                languages=["en"],
                use_case="Conversational practice, dialog training",
                memory_gb=4.0,
                description="Optimized for natural conversations"
            )
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
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
            logger.debug(f"Ollama not available: {e}")
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
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                if response.status == 200:
                    # Stream the download progress
                    async for line in response.content:
                        try:
                            progress = json.loads(line.decode().strip())
                            if "status" in progress:
                                logger.info(f"Pull progress: {progress['status']}")
                        except:
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
    
    def get_recommended_model(self, language: str, use_case: str = "conversation") -> str:
        """Get recommended model for specific language and use case"""
        language_models = {
            "en": ["neural-chat:7b", "llama2:7b", "codellama:7b"],
            "fr": ["mistral:7b", "llama2:7b"],
            "es": ["llama2:7b", "llama2:13b"],
            "de": ["llama2:7b", "llama2:13b"],
            "it": ["llama2:7b", "llama2:13b"],
            "pt": ["llama2:13b", "llama2:7b"],
        }
        
        recommended = language_models.get(language, ["llama2:7b"])
        
        # For technical use cases, prefer code-specialized models
        if use_case == "technical" and language == "en":
            return "codellama:7b"
        
        # For advanced grammar, prefer larger models
        if use_case == "grammar" and "llama2:13b" in recommended:
            return "llama2:13b"
        
        return recommended[0]
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using Ollama"""
        start_time = datetime.now()
        
        try:
            # Select model
            if not model:
                model = self.get_recommended_model(language, kwargs.get("use_case", "conversation"))
            
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
                }
            }
            
            # Make request
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
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
                        "model_size": self.available_models.get(model, {}).memory_gb if model in self.available_models else "unknown",
                        "local_processing": True,
                        "privacy_mode": True,
                        "done": data.get("done", True),
                        "context": data.get("context", []),
                        "total_duration": data.get("total_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                        "eval_count": data.get("eval_count", 0)
                    }
                )
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"Local AI generation failed: {str(e)}")
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Generate streaming response using Ollama"""
        start_time = datetime.now()
        
        try:
            # Select model
            if not model:
                model = self.get_recommended_model(language, kwargs.get("use_case", "conversation"))
            
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
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama streaming error: {response.status} - {error_text}")
                
                async for line in response.content:
                    try:
                        chunk_data = json.loads(line.decode().strip())
                        
                        if "response" in chunk_data:
                            processing_time = (datetime.now() - start_time).total_seconds()
                            
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
                                    "done": chunk_data.get("done", False)
                                }
                            )
                    
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise Exception(f"Local AI streaming failed: {str(e)}")
    
    def _format_prompt_for_language_learning(
        self, 
        messages: List[Dict[str, str]], 
        language: str
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
            "zh": "你是一个有用的中文语言导师。提供清晰、鼓励的回答，并温和地纠正语法错误。"
        }
        
        system_instruction = language_instructions.get(
            language, 
            "You are a helpful language tutor. Provide clear, encouraging responses."
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
                        "Pull a model: 'ollama pull llama2:7b'"
                    ]
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
                "privacy": "Complete - data stays on device"
            }
            
        except Exception as e:
            return {
                "service_name": self.service_name,
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
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
                "instructions": status.get("recommendations", [])
            }
        
        models = await self.service.list_models()
        
        return {
            "installed": True,
            "running": True,
            "models": len(models),
            "model_names": [model.get("name") for model in models],
            "setup_required": len(models) == 0,
            "recommended_setup": self._get_recommended_setup()
        }
    
    def _get_recommended_setup(self) -> List[str]:
        """Get recommended setup steps for optimal language learning"""
        return [
            "ollama pull llama2:7b  # General purpose, 4GB RAM",
            "ollama pull mistral:7b  # Good for French, 4GB RAM", 
            "ollama pull neural-chat:7b  # Conversational, 4GB RAM",
            "ollama pull llama2:13b  # Better quality, 8GB RAM (optional)"
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
                    "3. Try this setup again"
                ]
            }
        
        # Pull essential models
        essential_models = ["llama2:7b", "mistral:7b"]
        results = {}
        
        for model in essential_models:
            logger.info(f"Setting up model: {model}")
            success = await self.service.pull_model(model)
            results[model] = "success" if success else "failed"
        
        successful_models = [model for model, status in results.items() if status == "success"]
        
        return {
            "success": len(successful_models) > 0,
            "models_setup": successful_models,
            "setup_results": results,
            "message": f"Successfully set up {len(successful_models)}/{len(essential_models)} essential models",
            "ready_for_fallback": len(successful_models) > 0
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
    messages: List[Dict[str, str]],
    language: str = "en",
    **kwargs
) -> AIResponse:
    """Generate response using local Ollama"""
    return await ollama_service.generate_response(messages, language, **kwargs)

async def setup_ollama_for_language_learning() -> Dict[str, Any]:
    """Setup Ollama with language learning models"""
    return await ollama_manager.setup_for_language_learning()