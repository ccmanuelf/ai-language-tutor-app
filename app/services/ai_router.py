"""
Enhanced AI Router with Ollama Fallback for AI Language Tutor App

This router intelligently selects the best AI provider based on:
- Language requirements
- Budget constraints
- Provider availability
- User preferences
- Performance requirements

Features:
- Automatic fallback to Ollama when budget exceeded
- Language-specific provider optimization
- Cost tracking and budget enforcement
- Performance monitoring
- Provider health checking
- Graceful degradation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from app.services.ai_service_base import BaseAIService, AIResponse, StreamingResponse
from app.services.budget_manager import budget_manager, BudgetStatus, BudgetAlert
from app.services.ollama_service import ollama_service
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RouterMode(Enum):
    """AI Router operating modes"""
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_OPTIMIZED = "quality_optimized" 
    SPEED_OPTIMIZED = "speed_optimized"
    LOCAL_ONLY = "local_only"
    HYBRID = "hybrid"


class FallbackReason(Enum):
    """Reasons for falling back to local models"""
    BUDGET_EXCEEDED = "budget_exceeded"
    API_UNAVAILABLE = "api_unavailable"
    RATE_LIMITED = "rate_limited"
    USER_PREFERENCE = "user_preference"
    PRIVACY_MODE = "privacy_mode"
    OFFLINE_MODE = "offline_mode"


@dataclass
class ProviderSelection:
    """AI provider selection result"""
    provider_name: str
    service: BaseAIService
    model: str
    reason: str
    confidence: float
    cost_estimate: float
    is_fallback: bool
    fallback_reason: Optional[FallbackReason] = None


class EnhancedAIRouter:
    """Enhanced AI router with Ollama fallback support"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIService] = {}
        self.provider_health: Dict[str, Dict[str, Any]] = {}
        self.language_preferences: Dict[str, List[str]] = {}
        self.router_mode = RouterMode.HYBRID
        self.fallback_enabled = True
        self.last_health_check = {}
        self._initialize_language_preferences()
    
    def _initialize_language_preferences(self):
        """Initialize language-specific provider preferences"""
        self.language_preferences = {
            "en": ["claude", "ollama", "mistral"],  # English - Claude primary, Ollama fallback
            "fr": ["mistral", "claude", "ollama"],  # French - Mistral primary
            "zh": ["qwen", "claude", "ollama"],     # Chinese - Qwen primary 
            "zh-cn": ["qwen", "claude", "ollama"],  # Simplified Chinese
            "zh-tw": ["qwen", "claude", "ollama"],  # Traditional Chinese
            "es": ["claude", "ollama"],             # Spanish - Claude, Ollama
            "de": ["claude", "ollama"],             # German - Claude, Ollama
            "it": ["claude", "ollama"],             # Italian - Claude, Ollama
            "pt": ["claude", "ollama"],             # Portuguese - Claude, Ollama
            "ja": ["claude", "ollama"],             # Japanese - Claude, Ollama
            "ko": ["claude", "ollama"],             # Korean - Claude, Ollama
        }
    
    def register_provider(self, name: str, service: BaseAIService):
        """Register an AI service provider"""
        self.providers[name] = service
        logger.info(f"Registered AI provider: {name}")
    
    async def check_provider_health(self, provider_name: str) -> Dict[str, Any]:
        """Check health of a specific provider"""
        if provider_name not in self.providers:
            return {"status": "not_registered", "available": False}
        
        try:
            # Use cached health if recent (within 5 minutes)
            cache_key = f"{provider_name}_health"
            if (cache_key in self.last_health_check and 
                datetime.now() - self.last_health_check[cache_key] < timedelta(minutes=5)):
                return self.provider_health.get(provider_name, {"status": "unknown"})
            
            # Check provider health
            service = self.providers[provider_name]
            if hasattr(service, 'get_health_status'):
                health = await service.get_health_status()
            else:
                # Basic availability check
                health = {"status": "available", "available": True}
            
            self.provider_health[provider_name] = health
            self.last_health_check[cache_key] = datetime.now()
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed for {provider_name}: {e}")
            health = {"status": "error", "available": False, "error": str(e)}
            self.provider_health[provider_name] = health
            return health
    
    async def check_budget_status(self) -> BudgetStatus:
        """Check current budget status"""
        return budget_manager.get_current_budget_status()
    
    async def select_provider(
        self,
        language: str = "en",
        use_case: str = "conversation",
        user_preferences: Optional[Dict[str, Any]] = None,
        force_local: bool = False
    ) -> ProviderSelection:
        """
        Select the best provider for the request
        
        Args:
            language: Target language for the conversation
            use_case: Type of interaction (conversation, grammar, pronunciation)
            user_preferences: User-specific preferences
            force_local: Force use of local models only
            
        Returns:
            Provider selection with reasoning
        """
        
        # Check if user wants local-only mode
        if force_local or (user_preferences and user_preferences.get("local_only")):
            return await self._select_local_provider(language, "user_preference")
        
        # Check budget status
        budget_status = await self.check_budget_status()
        
        # If budget exceeded, use local fallback
        if budget_status.alert_level in [BudgetAlert.CRITICAL, BudgetAlert.RED]:
            logger.info(f"Budget {budget_status.alert_level.value}, falling back to local models")
            return await self._select_local_provider(language, "budget_exceeded")
        
        # Get preferred providers for language
        preferred_providers = self.language_preferences.get(language, ["claude", "ollama"])
        
        # Filter out Ollama for now (we'll use it as fallback)
        cloud_providers = [p for p in preferred_providers if p != "ollama"]
        
        # Check cloud provider availability and health
        for provider_name in cloud_providers:
            if provider_name not in self.providers:
                continue
            
            try:
                health = await self.check_provider_health(provider_name)
                
                if health.get("status") == "healthy" or health.get("available", False):
                    # Estimate cost for this request
                    cost_estimate = await self._estimate_request_cost(provider_name, language, use_case)
                    
                    # Check if we can afford this request
                    if budget_status.remaining_budget >= cost_estimate:
                        return ProviderSelection(
                            provider_name=provider_name,
                            service=self.providers[provider_name],
                            model=self._get_model_for_provider(provider_name, language),
                            reason=f"Best available provider for {language}",
                            confidence=0.9,
                            cost_estimate=cost_estimate,
                            is_fallback=False
                        )
                    else:
                        logger.info(f"Provider {provider_name} too expensive (${cost_estimate:.4f} > ${budget_status.remaining_budget:.4f})")
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} check failed: {e}")
                continue
        
        # All cloud providers failed or too expensive - use local fallback
        logger.info("All cloud providers unavailable or too expensive, using local fallback")
        return await self._select_local_provider(language, "api_unavailable")
    
    async def _select_local_provider(
        self, 
        language: str, 
        reason: str
    ) -> ProviderSelection:
        """Select local Ollama provider as fallback"""
        
        # Check if Ollama is available
        if "ollama" not in self.providers:
            self.register_provider("ollama", ollama_service)
        
        ollama_available = await ollama_service.check_availability()
        
        if not ollama_available:
            raise Exception(
                "No AI providers available. Cloud providers unavailable and Ollama not running. "
                "Please start Ollama or check your internet connection."
            )
        
        # Get recommended model for language
        model = ollama_service.get_recommended_model(language)
        
        return ProviderSelection(
            provider_name="ollama",
            service=ollama_service,
            model=model,
            reason=f"Local fallback - {reason}",
            confidence=0.7,  # Lower confidence for fallback
            cost_estimate=0.0,  # Local models are free
            is_fallback=True,
            fallback_reason=FallbackReason(reason)
        )
    
    def _get_model_for_provider(self, provider_name: str, language: str) -> str:
        """Get appropriate model for provider and language"""
        model_mappings = {
            "claude": "claude-3-haiku-20240307",
            "mistral": "mistral-small-latest",
            "qwen": "qwen-plus",
            "ollama": ollama_service.get_recommended_model(language) if hasattr(ollama_service, 'get_recommended_model') else "llama2:7b"
        }
        
        return model_mappings.get(provider_name, "default")
    
    async def _estimate_request_cost(
        self, 
        provider_name: str, 
        language: str, 
        use_case: str
    ) -> float:
        """Estimate cost for a request to a provider"""
        
        # Base cost estimates per provider (per 1K tokens)
        base_costs = {
            "claude": 0.008,   # Claude Haiku input cost
            "mistral": 0.0007, # Mistral small cost
            "qwen": 0.002,     # Qwen cost (estimated)
            "ollama": 0.0      # Local models are free
        }
        
        # Estimate token count based on use case
        token_estimates = {
            "conversation": 150,    # ~150 tokens average
            "grammar": 200,         # Grammar checking needs more context
            "pronunciation": 100,   # Shorter pronunciation feedback
            "translation": 120,     # Translation requests
            "explanation": 250      # Detailed explanations
        }
        
        base_cost = base_costs.get(provider_name, 0.01)
        estimated_tokens = token_estimates.get(use_case, 150)
        
        # Calculate total estimated cost (input + output)
        input_cost = base_cost * (estimated_tokens / 1000)
        output_cost = base_cost * 3 * (100 / 1000)  # Assume 100 token response, 3x cost for output
        
        return input_cost + output_cost
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        use_case: str = "conversation",
        user_preferences: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate AI response using best available provider
        
        Args:
            messages: Conversation messages
            language: Target language
            use_case: Type of interaction
            user_preferences: User preferences
            **kwargs: Additional parameters
            
        Returns:
            AI response with provider information
        """
        
        start_time = datetime.now()
        
        try:
            # Select best provider
            selection = await self.select_provider(
                language=language,
                use_case=use_case,
                user_preferences=user_preferences,
                force_local=kwargs.get("force_local", False)
            )
            
            logger.info(f"Using provider: {selection.provider_name} ({selection.reason})")
            
            # Generate response
            response = await selection.service.generate_response(
                messages=messages,
                language=language,
                model=selection.model,
                **kwargs
            )
            
            # Track cost if not fallback
            if not selection.is_fallback and response.cost > 0:
                budget_manager.track_usage(
                    provider=selection.provider_name,
                    model=selection.model,
                    cost=response.cost,
                    tokens_used=kwargs.get("max_tokens", 150)
                )
            
            # Add router metadata
            response.metadata = response.metadata or {}
            response.metadata.update({
                "router_selection": {
                    "provider": selection.provider_name,
                    "is_fallback": selection.is_fallback,
                    "fallback_reason": selection.fallback_reason.value if selection.fallback_reason else None,
                    "selection_confidence": selection.confidence,
                    "selection_time": (datetime.now() - start_time).total_seconds()
                }
            })
            
            return response
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            
            # Try fallback if not already using it
            if not kwargs.get("_fallback_attempt"):
                logger.info("Attempting fallback to local model")
                kwargs["_fallback_attempt"] = True
                kwargs["force_local"] = True
                return await self.generate_response(messages, language, use_case, user_preferences, **kwargs)
            
            raise Exception(f"All AI providers failed: {str(e)}")
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        use_case: str = "conversation",
        user_preferences: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[StreamingResponse, None]:
        """
        Generate streaming AI response using best available provider
        """
        
        try:
            # Select best provider
            selection = await self.select_provider(
                language=language,
                use_case=use_case,
                user_preferences=user_preferences,
                force_local=kwargs.get("force_local", False)
            )
            
            logger.info(f"Streaming with provider: {selection.provider_name}")
            
            # Check if provider supports streaming
            if hasattr(selection.service, 'generate_streaming_response'):
                async for chunk in selection.service.generate_streaming_response(
                    messages=messages,
                    language=language,
                    model=selection.model,
                    **kwargs
                ):
                    # Add router metadata to chunks
                    chunk.metadata = chunk.metadata or {}
                    chunk.metadata["router_provider"] = selection.provider_name
                    chunk.metadata["is_fallback"] = selection.is_fallback
                    
                    yield chunk
            else:
                # Fallback to non-streaming for providers that don't support it
                response = await selection.service.generate_response(
                    messages=messages,
                    language=language,
                    model=selection.model,
                    **kwargs
                )
                
                # Convert to streaming format
                yield StreamingResponse(
                    content=response.content,
                    model=response.model,
                    provider=response.provider,
                    language=response.language,
                    is_final=True,
                    processing_time=response.processing_time,
                    cost=response.cost,
                    metadata={
                        **response.metadata,
                        "router_provider": selection.provider_name,
                        "is_fallback": selection.is_fallback,
                        "converted_from_non_streaming": True
                    }
                )
                
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            
            # Try fallback if not already using it
            if not kwargs.get("_fallback_attempt"):
                logger.info("Attempting streaming fallback to local model")
                kwargs["_fallback_attempt"] = True
                kwargs["force_local"] = True
                async for chunk in self.generate_streaming_response(messages, language, use_case, user_preferences, **kwargs):
                    yield chunk
            else:
                raise Exception(f"All streaming providers failed: {str(e)}")
    
    async def get_router_status(self) -> Dict[str, Any]:
        """Get comprehensive router status"""
        
        budget_status = await self.check_budget_status()
        
        # Check all provider health
        provider_statuses = {}
        for name in self.providers.keys():
            provider_statuses[name] = await self.check_provider_health(name)
        
        # Check Ollama specifically
        ollama_status = await ollama_service.get_health_status()
        
        return {
            "router_mode": self.router_mode.value,
            "fallback_enabled": self.fallback_enabled,
            "budget_status": {
                "status": budget_status.alert_level.value,
                "remaining": budget_status.remaining_budget,
                "percentage_used": budget_status.percentage_used
            },
            "providers": provider_statuses,
            "fallback_status": {
                "ollama_available": ollama_status.get("status") == "healthy",
                "ollama_models": ollama_status.get("models_installed", 0)
            },
            "language_support": list(self.language_preferences.keys()),
            "total_providers": len(self.providers)
        }
    
    def set_router_mode(self, mode: RouterMode):
        """Set router operating mode"""
        self.router_mode = mode
        logger.info(f"Router mode set to: {mode.value}")
    
    def enable_fallback(self, enabled: bool = True):
        """Enable or disable fallback to local models"""
        self.fallback_enabled = enabled
        logger.info(f"Fallback {'enabled' if enabled else 'disabled'}")


# Global router instance
ai_router = EnhancedAIRouter()

# Register Ollama as fallback provider
ai_router.register_provider("ollama", ollama_service)


# Convenience functions
async def generate_ai_response(
    messages: List[Dict[str, str]],
    language: str = "en",
    **kwargs
) -> AIResponse:
    """Generate AI response using the router"""
    return await ai_router.generate_response(messages, language, **kwargs)

async def generate_streaming_ai_response(
    messages: List[Dict[str, str]],
    language: str = "en",
    **kwargs
) -> AsyncGenerator[StreamingResponse, None]:
    """Generate streaming AI response using the router"""
    async for chunk in ai_router.generate_streaming_response(messages, language, **kwargs):
        yield chunk

async def get_ai_router_status() -> Dict[str, Any]:
    """Get AI router status"""
    return await ai_router.get_router_status()

def register_ai_provider(name: str, service: BaseAIService):
    """Register an AI provider with the router"""
    ai_router.register_provider(name, service)