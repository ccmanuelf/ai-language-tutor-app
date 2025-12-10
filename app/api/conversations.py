"""
Conversation API endpoints for AI chat functionality
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import require_auth
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser
from app.services.ai_router import (
    ai_router,  # Use global router instance with registered providers
)
from app.services.speech_processor import speech_processor

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


class ChatRequest(BaseModel):
    message: str
    language: str = "en-claude"  # Format: "language-provider"
    use_speech: bool = False
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str
    message_id: str
    conversation_id: str
    audio_url: Optional[str] = None
    language: str
    ai_provider: str
    estimated_cost: float = 0.0


class ConversationHistory(BaseModel):
    messages: List[dict]
    total_messages: int
    conversation_id: str
    started_at: str


def _parse_language_and_provider(language: str) -> tuple[str, str]:
    """Parse language code and AI provider from language string"""
    language_parts = language.split("-")
    language_code = language_parts[0] if language_parts else "en"
    ai_provider = language_parts[1] if len(language_parts) > 1 else "claude"
    return language_code, ai_provider


def _generate_conversation_ids(user_id: str) -> tuple[str, str]:
    """Generate conversation and message IDs"""
    conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    message_id = str(uuid.uuid4())
    return conversation_id, message_id


async def _get_ai_response(
    request: ChatRequest,
    language_code: str,
    preferred_provider: str,
    user_id: str,
    db: Session,
) -> tuple[str, float]:
    """Get AI response from selected provider"""
    from app.models.database import User

    # Get user settings from database
    user = db.query(User).filter(User.user_id == user_id).first()
    user_preferences = user.preferences if user else {}

    # Get AI provider settings
    ai_settings = user.get_ai_provider_settings() if user else {}

    # Determine budget enforcement mode
    enforce_budget = ai_settings.get("enforce_budget_limits", True)

    # Select provider with user's preferences
    provider_selection = await ai_router.select_provider(
        language=language_code,
        use_case="conversation",
        preferred_provider=preferred_provider,  # ✅ NOW PASSED!
        user_preferences=user_preferences,
        enforce_budget=enforce_budget,
    )

    # Check if budget override is required
    if (
        hasattr(provider_selection, "requires_budget_override")
        and provider_selection.requires_budget_override
    ):
        # Budget exceeded but user wants premium provider
        # Return warning message to user
        warning = provider_selection.budget_warning
        raise Exception(
            f"Budget exceeded. {warning.message if warning else 'Please use free Ollama or enable budget override.'}"
        )

    if provider_selection.service and hasattr(
        provider_selection.service, "generate_response"
    ):
        ai_response = await provider_selection.service.generate_response(
            messages=[{"role": "user", "content": request.message}],
            message=request.message,
            language=language_code,
            context={"language": language_code, "user_id": user_id},
            conversation_history=request.conversation_history,
        )
        response_text = (
            ai_response.content if hasattr(ai_response, "content") else str(ai_response)
        )
        cost_estimate = ai_response.cost if hasattr(ai_response, "cost") else 0.01
        return response_text, cost_estimate
    else:
        raise Exception("No AI service available")


def _get_fallback_texts() -> Dict[str, str]:
    """Get fallback conversation texts by language"""
    return {
        "en": "Hey! I heard you say '{message}' - great! I'm your English conversation partner. What would you like to chat about?",
        "es": "¡Hola! Escuché '{message}' - ¡perfecto! Soy tu compañera de conversación en español. ¿De qué quieres hablar?",
        "fr": "Salut ! J'ai entendu '{message}' - super ! Je suis ta partenaire de conversation française. De quoi veux-tu parler ?",
        "zh": "你好！我听到你说了'{message}' - 很好！我是你的中文对话伙伴。你想聊什么？",
        "ja": "こんにちは！'{message}'と言いましたね - いいですね！私はあなたの日本語会話パートナーです。何について話しましょうか？",
        "de": "Hallo! Ich habe gehört, dass du '{message}' gesagt hast - super! Ich bin dein deutscher Gesprächspartner. Worüber möchtest du sprechen?",
    }


def _get_demo_fallback_responses() -> Dict[str, str]:
    """Get demo mode fallback responses by language"""
    return {
        "en": "Hey there! I heard you say '{message}' - that's great practice! I'm Alex, your English conversation partner. I love chatting about anything - hobbies, travel, food, movies, you name it! What's something interesting that happened to you recently?",
        "es": "¡Hola! Escuché que dijiste '{message}' - ¡excelente! Soy María, tu compañera de conversación en español. Me encanta hablar de todo - comida, viajes, familia, música, lo que quieras. ¿Qué tal tu día? ¡Cuéntame algo interesante!",
        "fr": "Salut ! J'ai entendu que tu as dit '{message}' - c'est formidable ! Je suis Sophie, ta partenaire de conversation française. J'adore discuter de tout - cuisine, voyages, loisirs, films, tout m'intéresse ! Alors, qu'est-ce qui t'a plu récemment ?",
        "zh": "你好！我听到你说了'{message}' - 很棒！私は小李，你的中文对话伙伴。我喜欢聊各种话题 - 美食、旅行、电影、音乐，什么都可以！你今天过得怎么样？有什么有趣的事情想分享吗？",
        "ja": "こんにちは！'{message}'と言ったのを聞きました - 素晴らしいです！私は優子、あなたの日本語会話パートナーです。趣味、旅行、食べ物、映画など、何でも話すのが大好きです！最近何か面白いことがありましたか？",
        "de": "Hallo! Ich habe gehört, dass du '{message}' gesagt hast - das ist großartige Übung! Ich bin Klaus, dein deutscher Gesprächspartner. Ich liebe es, über alles zu sprechen - Hobbys, Reisen, Essen, Filme, was auch immer! Was war kürzlich etwas Interessantes, das dir passiert ist?",
    }


async def _generate_speech_if_requested(
    request: ChatRequest, response_text: str, language_code: str, message_id: str
) -> Optional[str]:
    """Generate speech audio if requested"""
    if not request.use_speech:
        return None

    try:
        _tts_result = await speech_processor.process_text_to_speech(
            text=response_text, language=language_code, voice_type="neural"
        )
        return f"/api/v1/audio/{message_id}.wav"
    except Exception as e:
        print(f"TTS Error: {e}")
        return None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Send message to AI and get response"""
    # Parse user's preferred provider from language string (e.g., "en-claude" -> "en", "claude")
    language_code, preferred_provider = _parse_language_and_provider(request.language)
    conversation_id, message_id = _generate_conversation_ids(current_user.user_id)

    try:
        try:
            # Pass preferred provider to router ✅
            response_text, cost_estimate = await _get_ai_response(
                request, language_code, preferred_provider, current_user.user_id, db
            )
        except Exception as ai_error:
            print(f"AI Service Error: {ai_error}")
            fallback_texts = _get_fallback_texts()
            response_text = fallback_texts.get(
                language_code, fallback_texts["en"]
            ).format(message=request.message)
            cost_estimate = 0.0

        audio_url = await _generate_speech_if_requested(
            request, response_text, language_code, message_id
        )

        return ChatResponse(
            response=response_text,
            message_id=message_id,
            conversation_id=conversation_id,
            audio_url=audio_url,
            language=language_code,
            ai_provider=preferred_provider,
            estimated_cost=cost_estimate,
        )

    except Exception as e:
        print(f"AI Service Error: {e}")
        fallback_responses = _get_demo_fallback_responses()
        fallback_response = fallback_responses.get(
            language_code, fallback_responses["en"]
        ).format(message=request.message)

        return ChatResponse(
            response=f"[Demo Mode] {fallback_response}",
            message_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            audio_url=None,
            language=language_code,
            ai_provider=preferred_provider,
            estimated_cost=0.01,
        )


@router.get("/history", response_model=List[ConversationHistory])
async def get_conversation_history(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get user's conversation history"""
    # In a full implementation, this would query the conversations table
    # For now, return demo data
    return [
        ConversationHistory(
            messages=[
                {
                    "role": "user",
                    "content": "Hello!",
                    "timestamp": "2025-08-26T20:00:00Z",
                },
                {
                    "role": "assistant",
                    "content": "Hello! How can I help you practice today?",
                    "timestamp": "2025-08-26T20:00:01Z",
                },
            ],
            total_messages=2,
            conversation_id="demo_conv_001",
            started_at="2025-08-26T20:00:00Z",
        )
    ]


@router.post("/speech-to-text")
async def speech_to_text(
    request: dict, current_user: SimpleUser = Depends(require_auth)
):
    """Convert speech to text using Watson STT"""
    try:
        # Get audio data from request
        audio_data_base64 = request.get("audio_data")
        language = request.get("language", "en")

        if not audio_data_base64:
            return {"text": "No audio data provided"}

        # Decode base64 audio data
        import base64

        audio_data = base64.b64decode(audio_data_base64)

        # Process speech-to-text using Mistral STT
        from app.services.speech_processor import AudioFormat, speech_processor

        recognition_result, _ = await speech_processor.process_speech_to_text(
            audio_data=audio_data, language=language, audio_format=AudioFormat.WAV
        )

        return {
            "text": recognition_result.transcript,
            "confidence": recognition_result.confidence,
            "language": recognition_result.language,
        }

    except Exception as e:
        print(f"Speech-to-text error: {e}")
        # Return fallback text
        return {"text": "Speech recognition failed. Please try again.", "error": str(e)}


@router.post("/text-to-speech")
async def text_to_speech(
    request: dict, current_user: SimpleUser = Depends(require_auth)
):
    """
    Convert text to speech and return audio data

    Args:
        request: Dictionary containing:
            - text: Text to synthesize (required)
            - language: Target language (default: "en")
            - voice_type: Voice type - "neural" or "standard" (default: "neural")
            - voice: Optional specific voice persona (e.g., "es_AR-daniela-high")

    Returns:
        Audio data as base64-encoded string with metadata
    """
    try:
        # Get text and language from request
        text = request.get("text")
        language = request.get("language", "en")
        voice_type = request.get("voice_type", "neural")
        voice = request.get("voice")  # Optional voice persona

        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        # Process text-to-speech with optional voice selection
        from app.services.speech_processor import speech_processor

        tts_result = await speech_processor.process_text_to_speech(
            text=text, language=language, voice_type=voice_type, voice=voice
        )

        # Encode audio data as base64 for transmission
        import base64

        audio_base64 = base64.b64encode(tts_result.audio_data).decode("utf-8")

        return {
            "audio_data": audio_base64,
            "audio_format": tts_result.audio_format.value,
            "sample_rate": tts_result.sample_rate,
            "duration": tts_result.duration_seconds,
        }

    except Exception as e:
        print(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages and AI providers"""
    return {
        "languages": [
            {
                "code": "en",
                "name": "English",
                "providers": ["claude"],
                "display": "English (Claude)",
            },
            {
                "code": "es",
                "name": "Spanish",
                "providers": ["claude"],
                "display": "Spanish (Claude)",
            },
            {
                "code": "fr",
                "name": "French",
                "providers": ["mistral"],
                "display": "French (Mistral)",
            },
            {
                "code": "zh",
                "name": "Chinese",
                "providers": ["deepseek"],
                "display": "Chinese (DeepSeek)",
            },
            {
                "code": "ja",
                "name": "Japanese",
                "providers": ["claude"],
                "display": "Japanese (Claude)",
            },
            {
                "code": "de",
                "name": "German",
                "providers": ["claude"],
                "display": "German (Claude)",
            },
        ]
    }


@router.get("/available-voices")
async def get_available_voices(language: Optional[str] = None):
    """
    Get list of available voice personas for text-to-speech

    Args:
        language: Optional language filter (e.g., "en", "es")

    Returns:
        List of available voices with metadata including:
        - voice_id: Full voice identifier (e.g., "es_AR-daniela-high")
        - persona: Voice persona name (e.g., "daniela")
        - language: Language code (e.g., "es")
        - accent: Accent/region (e.g., "Argentina")
        - quality: Voice quality (e.g., "high", "medium")
        - gender: Inferred gender (e.g., "female", "male")
        - sample_rate: Audio sample rate
        - is_default: Whether this is the default voice for the language
    """
    try:
        # Get voices from Piper TTS service via speech processor
        if not speech_processor.piper_tts_service:
            raise HTTPException(
                status_code=503, detail="Text-to-speech service not available"
            )

        voices = speech_processor.piper_tts_service.get_available_voices(
            language=language
        )

        return {"voices": voices, "count": len(voices)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve voices: {str(e)}"
        )


@router.delete("/clear/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Clear a specific conversation"""
    # In a full implementation, this would delete conversation messages
    return {"message": f"Conversation {conversation_id} cleared successfully"}


@router.get("/stats")
async def get_conversation_stats(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get conversation statistics for the user"""
    return {
        "total_conversations": 5,
        "total_messages": 47,
        "languages_practiced": ["English", "Spanish", "French"],
        "favorite_language": "Spanish",
        "total_practice_time": "2h 34m",
        "this_week": {"conversations": 3, "messages": 22, "practice_time": "45m"},
    }
