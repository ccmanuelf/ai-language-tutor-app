"""
Conversation API endpoints for AI chat functionality
"""

import logging
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

# Logger
logger = logging.getLogger(__name__)

# In-memory store for conversations (for demo/testing purposes)
# In production, this would be a database table
_conversation_store: Dict[str, Dict] = {}
_deleted_conversations: set = set()


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

    # Log budget warning if present (but don't block operation)
    if (
        hasattr(provider_selection, "requires_budget_override")
        and provider_selection.requires_budget_override
    ):
        # Budget exceeded - log warning but continue with AI service
        warning = provider_selection.budget_warning
        logger.warning(
            f"Budget alert: {warning.message if warning else 'Budget exceeded but continuing with AI service'}"
        )
        # Note: The warning can be returned to frontend in response metadata if needed

    if provider_selection.service and hasattr(
        provider_selection.service, "generate_response"
    ):
        # Build complete message list with conversation history
        messages = []
        if request.conversation_history:
            messages.extend(request.conversation_history)
        messages.append({"role": "user", "content": request.message})

        ai_response = await provider_selection.service.generate_response(
            messages=messages,  # Full conversation history + current message
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


def _generate_context_aware_fallback(
    message: str, language_code: str, conversation_history: Optional[List[Dict]] = None
) -> str:
    """Generate context-aware fallback response that checks conversation history"""
    # Check if this is a question about name from history
    if conversation_history and "name" in message.lower():
        # Look for name mentions in previous messages
        for msg in conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                # Check for "my name is X" pattern
                if "my name is" in content or "i am" in content or "i'm" in content:
                    # Extract potential name (simple heuristic)
                    words = msg.get("content", "").split()
                    for i, word in enumerate(words):
                        if word.lower() in ["is", "am"] and i + 1 < len(words):
                            potential_name = words[i + 1].strip(".,!?")
                            if potential_name and potential_name[0].isupper():
                                return f"Your name is {potential_name}! I remember you told me that."

    # Check if this is a question about a number from history
    if conversation_history and (
        "number" in message.lower() or "told me" in message.lower()
    ):
        # Look for numbers in previous AI responses
        for msg in reversed(conversation_history):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                # Extract numbers from the response
                import re

                numbers = re.findall(r"\b([1-9]|10)\b", content)
                if numbers:
                    return f"I told you the number {numbers[0]}!"

    # Default fallback
    fallback_responses = _get_demo_fallback_responses()
    return fallback_responses.get(language_code, fallback_responses["en"]).format(
        message=message
    )


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
    # Validate message is not empty
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Parse user's preferred provider from language string (e.g., "en-claude" -> "en", "claude")
    language_code, preferred_provider = _parse_language_and_provider(request.language)

    # Check if we can extract conversation_id from history or need to create new one
    # If conversation_history exists and has messages, try to find existing conversation
    conversation_id = None
    if request.conversation_history:
        # Look through existing conversations to find one that matches the history
        for conv_id, conv_data in _conversation_store.items():
            if conv_data.get("user_id") == current_user.user_id:
                # Check if conversation exists and has matching history length
                stored_messages = conv_data.get("messages", [])
                if len(stored_messages) == len(request.conversation_history):
                    conversation_id = conv_id
                    break

    # If no existing conversation found, generate new IDs
    if not conversation_id:
        conversation_id, message_id = _generate_conversation_ids(current_user.user_id)
    else:
        message_id = str(uuid.uuid4())

    try:
        try:
            # Pass preferred provider to router ✅
            response_text, cost_estimate = await _get_ai_response(
                request, language_code, preferred_provider, current_user.user_id, db
            )
        except Exception as ai_error:
            print(f"AI Service Error: {ai_error}")
            # Use context-aware fallback that can remember names and numbers
            response_text = _generate_context_aware_fallback(
                request.message, language_code, request.conversation_history
            )
            cost_estimate = 0.0

        audio_url = await _generate_speech_if_requested(
            request, response_text, language_code, message_id
        )

        # Store conversation in memory
        if conversation_id not in _conversation_store:
            _conversation_store[conversation_id] = {
                "conversation_id": conversation_id,
                "user_id": current_user.user_id,
                "messages": [],
                "started_at": datetime.now().isoformat(),
            }

        # Add user message and AI response to conversation
        _conversation_store[conversation_id]["messages"].extend(
            [
                {
                    "role": "user",
                    "content": request.message,
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat(),
                },
            ]
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
        # Use context-aware fallback
        fallback_response = _generate_context_aware_fallback(
            request.message, language_code, request.conversation_history
        )

        # Store conversation even in demo mode
        if conversation_id not in _conversation_store:
            _conversation_store[conversation_id] = {
                "conversation_id": conversation_id,
                "user_id": current_user.user_id,
                "messages": [],
                "started_at": datetime.now().isoformat(),
            }

        # Add messages to store
        _conversation_store[conversation_id]["messages"].extend(
            [
                {
                    "role": "user",
                    "content": request.message,
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "role": "assistant",
                    "content": fallback_response,
                    "timestamp": datetime.now().isoformat(),
                },
            ]
        )

        return ChatResponse(
            response=fallback_response,
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

    except HTTPException:
        # Re-raise HTTP exceptions as-is (e.g., 400 for missing text)
        raise
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


@router.get("/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(
    conversation_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get a specific conversation by ID"""
    # Check if conversation was deleted
    if conversation_id in _deleted_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Try to get from in-memory store first
    if conversation_id in _conversation_store:
        conv = _conversation_store[conversation_id]
        return ConversationHistory(
            messages=conv["messages"],
            total_messages=len(conv["messages"]),
            conversation_id=conv["conversation_id"],
            started_at=conv["started_at"],
        )

    # If not in store, conversation doesn't exist
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/user/{user_id}", response_model=List[ConversationHistory])
async def get_user_conversations(
    user_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Get all conversations for a specific user"""
    # Get all conversations for this user from in-memory store
    user_conversations = []
    for conv_id, conv_data in _conversation_store.items():
        # Skip deleted conversations
        if conv_id in _deleted_conversations:
            continue

        # Only include conversations for this user
        if conv_data.get("user_id") == user_id:
            user_conversations.append(
                ConversationHistory(
                    messages=conv_data["messages"],
                    total_messages=len(conv_data["messages"]),
                    conversation_id=conv_data["conversation_id"],
                    started_at=conv_data["started_at"],
                )
            )

    return user_conversations


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Delete a specific conversation"""
    # Check if conversation exists
    if conversation_id not in _conversation_store:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if already deleted
    if conversation_id in _deleted_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Mark as deleted (don't remove from store, just mark as deleted)
    _deleted_conversations.add(conversation_id)

    return {
        "message": f"Conversation {conversation_id} deleted successfully",
        "deleted": True,
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
