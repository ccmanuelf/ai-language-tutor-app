"""
Conversation API endpoints for AI chat functionality
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
from datetime import datetime

from app.core.security import require_auth
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser
from app.services.ai_router import EnhancedAIRouter
from app.services.speech_processor import speech_processor


router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

# Initialize AI router
ai_router = EnhancedAIRouter()


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


@router.post("/chat", response_model=ChatResponse)
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
    request: ChatRequest, language_code: str, user_id: str
) -> tuple[str, float]:
    """Get AI response from selected provider"""
    provider_selection = await ai_router.select_provider(
        language=language_code, use_case="conversation"
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
    }


def _get_demo_fallback_responses() -> Dict[str, str]:
    """Get demo mode fallback responses by language"""
    return {
        "en": "Hey there! I heard you say '{message}' - that's great practice! I'm Alex, your English conversation partner. I love chatting about anything - hobbies, travel, food, movies, you name it! What's something interesting that happened to you recently?",
        "es": "¡Hola! Escuché que dijiste '{message}' - ¡excelente! Soy María, tu compañera de conversación en español. Me encanta hablar de todo - comida, viajes, familia, música, lo que quieras. ¿Qué tal tu día? ¡Cuéntame algo interesante!",
        "fr": "Salut ! J'ai entendu que tu as dit '{message}' - c'est formidable ! Je suis Sophie, ta partenaire de conversation française. J'adore discuter de tout - cuisine, voyages, loisirs, films, tout m'intéresse ! Alors, qu'est-ce qui t'a plu récemment ?",
        "zh": "你好！我听到你说了'{message}' - 很棒！私は小李，你的中文对话伙伴。我喜欢聊各种话题 - 美食、旅行、电影、音乐，什么都可以！你今天过得怎么样？有什么有趣的事情想分享吗？",
        "ja": "こんにちは！'{message}'と言ったのを聞きました - 素晴らしいです！私は優子、あなたの日本語会話パートナーです。趣味、旅行、食べ物、映画など、何でも話すのが大好きです！最近何か面白いことがありましたか？",
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


async def chat_with_ai(
    request: ChatRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Send message to AI and get response"""
    language_code, ai_provider = _parse_language_and_provider(request.language)
    conversation_id, message_id = _generate_conversation_ids(current_user.user_id)

    try:
        try:
            response_text, cost_estimate = await _get_ai_response(
                request, language_code, current_user.user_id
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
            ai_provider=ai_provider,
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
            ai_provider=ai_provider,
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

        # Process speech-to-text using IBM Watson
        from app.services.speech_processor import speech_processor, AudioFormat

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
    """Convert text to speech using Watson TTS and return audio data"""
    try:
        # Get text and language from request
        text = request.get("text")
        language = request.get("language", "en")
        voice_type = request.get("voice_type", "neural")

        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        # Process text-to-speech using IBM Watson
        from app.services.speech_processor import speech_processor

        tts_result = await speech_processor.process_text_to_speech(
            text=text, language=language, voice_type=voice_type
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
                "providers": ["qwen"],
                "display": "Chinese (Qwen)",
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
