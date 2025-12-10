"""
Ollama API endpoints for AI Language Tutor App

Provides endpoints for listing and managing Ollama models.
Session 98 - Phase 3
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_auth
from app.services.ollama_service import ollama_service

router = APIRouter()


@router.get("/models", response_model=Dict[str, Any])
async def list_ollama_models(current_user=Depends(require_auth)):
    """
    List all available Ollama models installed on the system.

    Returns:
        Dict containing:
        - available: Whether Ollama service is running
        - models: List of installed models with metadata
        - recommended: Dictionary of recommended models by language/use_case
        - message: Status message

    Example response:
    {
        "available": true,
        "models": [
            {
                "name": "llama2:7b",
                "size": "3.8GB",
                "modified": "2024-01-15T10:30:00Z"
            }
        ],
        "recommended": {
            "en": ["neural-chat:7b", "llama2:7b"],
            "fr": ["mistral:7b", "llama2:7b"]
        },
        "message": "3 Ollama models available"
    }
    """
    try:
        is_available = await ollama_service.check_availability()

        if not is_available:
            return {
                "available": False,
                "models": [],
                "recommended": {},
                "message": "Ollama service not running. Please start Ollama with 'ollama serve'.",
            }

        # Get installed models
        models = await ollama_service.list_models()

        # Phase 5: Build recommendations dynamically from installed models
        # Analyze capabilities of each installed model
        model_capabilities = []
        for model in models:
            model_name = model.get("name", "")
            if model_name:
                caps = ollama_service._analyze_model_capabilities(model_name)
                model_capabilities.append(
                    {
                        "name": model_name,
                        "capabilities": {
                            "is_code_model": caps["is_code_model"],
                            "is_multilingual": caps["is_multilingual"],
                            "is_chat_optimized": caps["is_chat_optimized"],
                            "language_support": caps["language_support"],
                            "size": caps["size_category"],
                        },
                    }
                )

        return {
            "available": True,
            "models": models,
            "model_capabilities": model_capabilities,
            "message": f"{len(models)} Ollama model(s) available",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing Ollama models: {str(e)}"
        )


@router.get("/models/recommended")
async def get_recommended_models(
    language: str = "en",
    use_case: str = "conversation",
    current_user=Depends(require_auth),
):
    """
    Get recommended Ollama model for specific language and use case.

    Phase 4: Now validates against installed models only.

    Args:
        language: Language code (en, fr, es, de, etc.)
        use_case: Use case type (conversation, technical, grammar, etc.)

    Returns:
        Dict containing:
        - language: Requested language
        - use_case: Requested use case
        - recommended_model: The recommended model name (from installed models)
        - alternatives: List of alternative models (only installed)
        - message: Status message

    Example response:
    {
        "language": "en",
        "use_case": "technical",
        "recommended_model": "codellama:7b",
        "alternatives": ["llama2:7b", "neural-chat:7b"],
        "message": "Recommended from 3 installed models"
    }
    """
    try:
        # Phase 4: Get installed models first
        installed_models = await ollama_service.list_models()

        if not installed_models:
            return {
                "language": language,
                "use_case": use_case,
                "recommended_model": None,
                "alternatives": [],
                "message": "No Ollama models installed. Please install models with 'ollama pull <model>'",
            }

        # Get recommendation from installed models only
        recommended = ollama_service.get_recommended_model(
            language, use_case, installed_models=installed_models
        )

        # Get installed model names for alternatives
        installed_names = [m.get("name", "") for m in installed_models]

        # Remove recommended from alternatives
        alternatives = [m for m in installed_names if m != recommended]

        return {
            "language": language,
            "use_case": use_case,
            "recommended_model": recommended,
            "alternatives": alternatives,
            "message": f"Recommended from {len(installed_models)} installed model(s)",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommended model: {str(e)}",
        )


@router.get("/status")
async def get_ollama_status(current_user=Depends(require_auth)):
    """
    Get Ollama service status.

    Returns:
        Dict containing:
        - available: Whether Ollama is running
        - version: Ollama version (if available)
        - models_count: Number of installed models
        - message: Status message

    Example response:
    {
        "available": true,
        "version": "0.1.17",
        "models_count": 3,
        "message": "Ollama is running with 3 models installed"
    }
    """
    try:
        is_available = await ollama_service.check_availability()

        if not is_available:
            return {
                "available": False,
                "version": None,
                "models_count": 0,
                "message": "Ollama service is not running",
            }

        models = await ollama_service.list_models()
        models_count = len(models)

        return {
            "available": True,
            "version": "unknown",  # Ollama doesn't expose version via API easily
            "models_count": models_count,
            "message": f"Ollama is running with {models_count} model(s) installed",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error checking Ollama status: {str(e)}"
        )
