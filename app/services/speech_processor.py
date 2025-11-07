"""
Speech Processing Pipeline & Pronunciation Analysis for AI Language Tutor App

This module provides comprehensive speech processing capabilities including:
- Speech-to-text conversion
- Text-to-speech synthesis
- Pronunciation analysis and feedback
- Audio processing and enhancement
- Language-specific phonetic analysis
- Integration with IBM Watson and local processing

Features:
- Multi-language speech recognition
- Pronunciation scoring and feedback
- Phonetic transcription
- Audio quality enhancement
- Real-time speech processing
- Offline fallback capabilities
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

# Audio processing libraries
try:
    import numpy as np

    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning(
        "Audio processing libraries not available. Install pyaudio and numpy for full functionality."
    )

# IBM Watson Speech Services - REMOVED in Phase 2A Migration
# Watson dependencies deprecated in favor of Mistral STT + Piper TTS
WATSON_SDK_AVAILABLE = False

# Mistral Speech Services
try:
    pass

    MISTRAL_STT_AVAILABLE = True
except ImportError:
    MISTRAL_STT_AVAILABLE = False
    logging.warning("Mistral STT service not available.")

# Piper TTS Services
try:
    pass

    PIPER_TTS_AVAILABLE = True
except ImportError:
    PIPER_TTS_AVAILABLE = False
    logging.warning("Piper TTS service not available.")

from app.core.config import (
    get_settings,  # noqa: E402 - Required after logger configuration
)

logger = logging.getLogger(__name__)


# WatsonConfig class removed - deprecated in Phase 2A migration
# Configuration now handled by Mistral STT and Piper TTS services


class AudioFormat(Enum):
    """Supported audio formats"""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    WEBM = "webm"


class PronunciationLevel(Enum):
    """Pronunciation quality levels"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNCLEAR = "unclear"


@dataclass
class AudioMetadata:
    """Audio file metadata"""

    format: AudioFormat
    sample_rate: int
    channels: int
    duration_seconds: float
    file_size_bytes: int
    quality_score: float


@dataclass
class SpeechRecognitionResult:
    """Speech recognition result"""

    transcript: str
    confidence: float
    language: str
    processing_time: float
    alternative_transcripts: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class PronunciationAnalysis:
    """Pronunciation analysis result"""

    overall_score: float
    pronunciation_level: PronunciationLevel
    phonetic_accuracy: float
    fluency_score: float
    word_level_scores: List[Dict[str, Any]]
    detected_issues: List[str]
    improvement_suggestions: List[str]
    phonetic_transcription: str
    target_phonetics: str


@dataclass
class SpeechSynthesisResult:
    """Speech synthesis result"""

    audio_data: bytes
    audio_format: AudioFormat
    sample_rate: int
    duration_seconds: float
    processing_time: float
    metadata: Dict[str, Any]


class SpeechProcessor:
    """Main speech processing pipeline"""

    def __init__(self):
        # Phase 2A: Migration to Mistral STT + Piper TTS (Watson deprecated)
        self.audio_libs_available = AUDIO_LIBS_AVAILABLE

        # Watson services deprecated - set to unavailable
        self.watson_sdk_available = False
        self.watson_stt_available = False
        self.watson_tts_available = False
        self.watson_stt_client = None
        self.watson_tts_client = None

        # Initialize Mistral STT service (primary STT provider)
        self.mistral_stt_available = MISTRAL_STT_AVAILABLE
        self.mistral_stt_service = None
        self._init_mistral_stt()

        # Initialize Piper TTS service (primary TTS provider)
        self.piper_tts_available = PIPER_TTS_AVAILABLE
        self.piper_tts_service = None
        self._init_piper_tts()

        # Audio processing settings
        self.default_sample_rate = 16000
        self.default_channels = 1
        self.chunk_size = 1024

        # Voice Activity Detection settings
        self.vad_threshold = 0.01  # Energy threshold for voice detection
        self.vad_frame_size = 480  # 30ms at 16kHz

        # Pronunciation analysis settings
        self.pronunciation_models = self._load_pronunciation_models()

        # Log speech services status
        logger.info(
            f"Speech services initialized - Mistral STT: {self.mistral_stt_available}, Piper TTS: {self.piper_tts_available}"
        )

    def detect_voice_activity(
        self, audio_data: bytes, sample_rate: int = 16000
    ) -> bool:
        """Modern energy-based voice activity detection"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return True  # Assume voice present if no analysis available

            if not audio_data or len(audio_data) < 2:
                return False  # No audio or insufficient data

            # Convert bytes to numpy array
            try:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            except ValueError:
                # Handle invalid audio format
                return False

            # Normalize audio
            if len(audio_array) > 0:
                normalized = audio_array.astype(np.float32) / 32767.0

                # Calculate energy (RMS)
                energy = np.sqrt(np.mean(normalized**2))

                # Simple threshold-based VAD with minimum energy check
                return (
                    energy > self.vad_threshold and energy > 1e-6
                )  # Avoid detecting pure zeros as voice

            return False

        except Exception as e:
            logger.warning(f"Voice activity detection failed: {e}")
            return False  # Default to no voice on error for safety

    def remove_silence(self, audio_data: bytes, sample_rate: int = 16000) -> bytes:
        """Remove silence from audio using energy-based detection"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return audio_data  # Return original if no processing available

            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            frame_size = self.vad_frame_size

            # Process audio in frames
            voice_frames = []
            for i in range(0, len(audio_array), frame_size):
                frame = audio_array[i : i + frame_size]
                if len(frame) == frame_size:
                    frame_bytes = frame.tobytes()
                    if self.detect_voice_activity(frame_bytes, sample_rate):
                        voice_frames.extend(frame)

            if voice_frames:
                return np.array(voice_frames, dtype=np.int16).tobytes()
            else:
                return audio_data  # Return original if no voice detected

        except Exception as e:
            logger.warning(f"Silence removal failed: {e}")
            return audio_data

    # _init_watson_clients method removed - Watson deprecated in Phase 2A migration

    def _init_mistral_stt(self):
        """Initialize Mistral STT service"""
        self.mistral_stt_service = None

        if not self.mistral_stt_available:
            logger.warning(
                "Mistral STT service not available. Install required dependencies."
            )
            return

        try:
            # Import here to avoid circular imports
            from app.services.mistral_stt_service import MistralSTTService

            # Create Mistral STT service instance
            self.mistral_stt_service = MistralSTTService()

            if self.mistral_stt_service.available:
                logger.info("Mistral STT service initialized successfully")
                self.mistral_stt_available = True
            else:
                logger.warning("Mistral STT service configuration invalid")
                self.mistral_stt_available = False

        except Exception as e:
            logger.error(f"Failed to initialize Mistral STT service: {e}")
            self.mistral_stt_service = None
            self.mistral_stt_available = False

    def _init_piper_tts(self):
        """Initialize Piper TTS service"""
        self.piper_tts_service = None

        if not self.piper_tts_available:
            logger.warning(
                "Piper TTS service not available. Install required dependencies."
            )
            return

        try:
            # Import here to avoid circular imports
            from app.services.piper_tts_service import PiperTTSService

            # Create Piper TTS service instance
            self.piper_tts_service = PiperTTSService()

            if self.piper_tts_service.voices:
                logger.info("Piper TTS service initialized successfully")
                self.piper_tts_available = True
            else:
                logger.warning("Piper TTS service has no available voices")
                self.piper_tts_available = False

        except Exception as e:
            logger.error(f"Failed to initialize Piper TTS service: {e}")
            self.piper_tts_service = None
            self.piper_tts_available = False

    @lru_cache(maxsize=1)
    def _get_cached_voices(self):
        """Cache available voices to reduce API calls"""
        return self._fetch_available_voices()

    def _fetch_available_voices(self):
        """Fetch available voices from Watson TTS service"""
        if not self.watson_tts_client:
            return {"error": "Watson TTS client not available"}

        try:
            voices_result = self.watson_tts_client.list_voices().get_result()

            available_voices = {}
            language_support = {}

            for voice in voices_result["voices"]:
                language = voice["language"]
                voice_name = voice["name"]

                if language not in available_voices:
                    available_voices[language] = []
                available_voices[language].append(voice_name)

                # Map to our simplified language codes
                lang_code = language.split("-")[0]
                if lang_code not in language_support:
                    language_support[lang_code] = []
                language_support[lang_code].append(voice_name)

            return {
                "available_voices": available_voices,
                "language_support": language_support,
                "chinese_supported": any(
                    "zh" in lang for lang in available_voices.keys()
                ),
                "total_languages": len(available_voices),
            }

        except Exception as e:
            logger.error(f"Failed to fetch available voices: {e}")
            return {"error": str(e)}

    async def check_available_voices(self) -> Dict[str, List[str]]:
        """Check available voices in Watson TTS service"""
        # Use cached version to reduce API calls
        return self._get_cached_voices()

    def _load_pronunciation_models(self) -> Dict[str, Any]:
        """Load language-specific pronunciation models"""
        # This would load actual pronunciation models in a full implementation
        # For now, we'll use configuration-based scoring
        return {
            "en": {
                "phoneme_weights": {"vowels": 0.4, "consonants": 0.4, "stress": 0.2},
                "common_issues": ["th_sounds", "r_sounds", "vowel_length"],
                "difficulty_words": [
                    "through",
                    "thoroughly",
                    "rhythm",
                    "worcestershire",
                ],
            },
            "fr": {
                "phoneme_weights": {
                    "nasal_vowels": 0.3,
                    "r_sounds": 0.3,
                    "liaison": 0.2,
                    "accent": 0.2,
                },
                "common_issues": ["nasal_vowels", "french_r", "silent_letters"],
                "difficulty_words": [
                    "grenouille",
                    "écureuil",
                    "serrurerie",
                    "anticonstitutionnellement",
                ],
            },
            "es": {
                "phoneme_weights": {
                    "rolled_r": 0.3,
                    "vowels": 0.3,
                    "stress": 0.2,
                    "consonants": 0.2,
                },
                "common_issues": ["rr_trill", "stress_patterns", "vowel_clarity"],
                "difficulty_words": [
                    "rápidamente",
                    "ferrocarril",
                    "trabajar",
                    "desarrollar",
                ],
            },
            "zh": {
                "phoneme_weights": {"tones": 0.5, "consonants": 0.25, "vowels": 0.25},
                "common_issues": ["tone_accuracy", "retroflex_sounds", "aspiration"],
                "difficulty_words": ["是", "知道", "中国", "学习"],
            },
        }

    async def process_speech_to_text(
        self,
        audio_data: bytes,
        language: str = "en",
        audio_format: AudioFormat = AudioFormat.WAV,
        enable_pronunciation_analysis: bool = True,
        provider: str = "auto",
    ) -> Tuple[SpeechRecognitionResult, Optional[PronunciationAnalysis]]:
        """
        Process speech to text with optional pronunciation analysis

        Args:
            audio_data: Raw audio data
            language: Target language for recognition
            audio_format: Audio format
            enable_pronunciation_analysis: Whether to analyze pronunciation
            provider: STT provider - "auto", "mistral" (Watson deprecated in Phase 2A)

        Returns:
            Speech recognition result and optional pronunciation analysis
        """
        start_time = datetime.now()

        try:
            # Validate and preprocess audio
            audio_metadata = await self._analyze_audio_quality(audio_data, audio_format)

            if audio_metadata.quality_score < 0.5:
                logger.warning(
                    f"Low audio quality detected: {audio_metadata.quality_score}"
                )
                # Attempt audio enhancement
                audio_data = await self._enhance_audio_quality(audio_data, audio_format)

            # Perform speech recognition with provider selection
            recognition_result = await self._select_stt_provider_and_process(
                audio_data=audio_data,
                language=language,
                audio_format=audio_format,
                provider=provider,
            )

            pronunciation_analysis = None
            if enable_pronunciation_analysis and recognition_result.confidence > 0.5:
                pronunciation_analysis = await self._analyze_pronunciation(
                    audio_data=audio_data,
                    transcript=recognition_result.transcript,
                    language=language,
                    audio_metadata=audio_metadata,
                )

            processing_time = (datetime.now() - start_time).total_seconds()
            recognition_result.processing_time = processing_time

            return recognition_result, pronunciation_analysis

        except Exception as e:
            logger.error(f"Speech processing failed: {e}")

            # Return fallback result
            fallback_result = SpeechRecognitionResult(
                transcript="[Speech recognition failed]",
                confidence=0.0,
                language=language,
                processing_time=(datetime.now() - start_time).total_seconds(),
                alternative_transcripts=[],
                metadata={"error": str(e), "fallback": True},
            )

            return fallback_result, None

    async def process_text_to_speech(
        self,
        text: str,
        language: str = "en",
        voice_type: str = "neural",
        speaking_rate: float = 1.0,
        emphasis_words: Optional[List[str]] = None,
        provider: str = "auto",
    ) -> SpeechSynthesisResult:
        """
        Convert text to speech with language learning optimizations

        Args:
            text: Text to synthesize
            language: Target language
            voice_type: Voice type (neural, standard)
            speaking_rate: Speaking speed (0.5-2.0)
            emphasis_words: Words to emphasize for learning
            provider: TTS provider ("auto", "piper" - Watson deprecated in Phase 2A)

        Returns:
            Speech synthesis result
        """
        start_time = datetime.now()

        try:
            # Prepare text for optimal pronunciation learning
            optimized_text = await self._prepare_text_for_synthesis(
                text=text,
                language=language,
                emphasis_words=emphasis_words,
                speaking_rate=speaking_rate,
            )

            # Use provider selection logic
            synthesis_result = await self._select_tts_provider_and_process(
                text=optimized_text,
                language=language,
                voice_type=voice_type,
                speaking_rate=speaking_rate,
                provider=provider,
                original_text=text,  # Pass original text for Piper TTS
            )

            synthesis_result.processing_time = (
                datetime.now() - start_time
            ).total_seconds()

            return synthesis_result

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise Exception(f"Speech synthesis failed: {str(e)}")

    async def _select_tts_provider_and_process(
        self,
        text: str,
        language: str,
        voice_type: str,
        speaking_rate: float,
        provider: str = "auto",
        original_text: str = None,
    ) -> SpeechSynthesisResult:
        """Select TTS provider and process text-to-speech with fallback logic"""
        if provider == "auto":
            return await self._process_auto_provider(
                text, original_text, language, voice_type, speaking_rate
            )
        elif provider == "piper_fallback":
            return await self._process_piper_fallback(
                text, original_text, language, voice_type, speaking_rate
            )
        elif provider == "piper":
            return await self._process_piper_provider(
                text, original_text, language, voice_type, speaking_rate
            )
        elif provider == "watson":
            raise Exception("Watson TTS deprecated - use 'auto' or 'piper' providers")
        else:
            raise Exception(f"Unknown TTS provider: {provider}")

    async def _process_auto_provider(
        self,
        text: str,
        original_text: str,
        language: str,
        voice_type: str,
        speaking_rate: float,
    ) -> SpeechSynthesisResult:
        """Process TTS with auto provider selection (Piper only)"""
        if not self.piper_tts_available:
            raise Exception("Piper TTS not available. Watson TTS has been deprecated.")

        try:
            piper_text = original_text if original_text else text
            result = await self._text_to_speech_piper(
                text=piper_text,
                language=language,
                voice_type=voice_type,
                speaking_rate=speaking_rate,
            )
            logger.info("TTS synthesis successful using Piper (cost: $0.00)")
            return result
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}")
            raise Exception(f"TTS synthesis failed: {e}")

    async def _process_piper_fallback(
        self,
        text: str,
        original_text: str,
        language: str,
        voice_type: str,
        speaking_rate: float,
    ) -> SpeechSynthesisResult:
        """Process TTS with Piper (Watson removed in Phase 2A)"""
        if not self.piper_tts_available:
            raise Exception("Piper TTS not available")

        piper_text = original_text if original_text else text
        result = await self._text_to_speech_piper(
            text=piper_text,
            language=language,
            voice_type=voice_type,
            speaking_rate=speaking_rate,
        )
        logger.info("TTS synthesis successful using Piper (cost: $0.00)")
        return result

    async def _process_piper_provider(
        self,
        text: str,
        original_text: str,
        language: str,
        voice_type: str,
        speaking_rate: float,
    ) -> SpeechSynthesisResult:
        """Process TTS with Piper provider explicitly"""
        if not self.piper_tts_available:
            raise Exception("Piper TTS provider requested but not available")

        piper_text = original_text if original_text else text
        return await self._text_to_speech_piper(
            text=piper_text,
            language=language,
            voice_type=voice_type,
            speaking_rate=speaking_rate,
        )

    async def analyze_pronunciation_quality(
        self, user_audio: bytes, reference_text: str, language: str = "en"
    ) -> PronunciationAnalysis:
        """
        Analyze pronunciation quality against reference text

        Args:
            user_audio: User's pronunciation audio
            reference_text: Expected text
            language: Target language

        Returns:
            Detailed pronunciation analysis
        """

        try:
            # First get speech recognition of user audio
            recognition_result, _ = await self.process_speech_to_text(
                audio_data=user_audio,
                language=language,
                enable_pronunciation_analysis=False,
            )

            # Compare with reference text
            pronunciation_analysis = await self._compare_pronunciation(
                recognized_text=recognition_result.transcript,
                reference_text=reference_text,
                language=language,
                confidence=recognition_result.confidence,
            )

            return pronunciation_analysis

        except Exception as e:
            logger.error(f"Pronunciation analysis failed: {e}")

            # Return fallback analysis
            return PronunciationAnalysis(
                overall_score=0.0,
                pronunciation_level=PronunciationLevel.UNCLEAR,
                phonetic_accuracy=0.0,
                fluency_score=0.0,
                word_level_scores=[],
                detected_issues=["analysis_failed"],
                improvement_suggestions=["Please try again with clearer audio"],
                phonetic_transcription="",
                target_phonetics="",
            )

    # Private implementation methods

    def _validate_provider_not_watson(self, provider: str) -> None:
        """Validate that Watson provider is not requested (deprecated)"""
        if provider == "watson":
            raise Exception("Watson STT deprecated - use 'auto' or 'mistral' providers")

    async def _process_with_mistral_explicit(
        self, audio_data: bytes, language: str, audio_format: AudioFormat
    ) -> SpeechRecognitionResult:
        """Process audio with Mistral STT when explicitly requested"""
        if not self.mistral_stt_available:
            raise Exception("Mistral STT not available but explicitly requested")
        return await self._speech_to_text_mistral(audio_data, language, audio_format)

    def _is_result_acceptable(self, result: SpeechRecognitionResult) -> bool:
        """Check if STT result meets quality threshold"""
        return result.confidence > 0.1 and result.transcript.strip() != ""

    async def _try_mistral_stt(
        self, audio_data: bytes, language: str, audio_format: AudioFormat, provider: str
    ) -> SpeechRecognitionResult:
        """Try to process audio with Mistral STT"""
        logger.info(f"Using Mistral STT for cost optimization (provider: {provider})")
        result = await self._speech_to_text_mistral(audio_data, language, audio_format)

        if self._is_result_acceptable(result):
            return result

        logger.warning(
            f"Mistral STT low quality result (confidence: {result.confidence})"
        )
        if provider == "auto":
            return result  # Accept even low quality in auto mode
        raise Exception("Mistral result not acceptable, need fallback")

    async def _process_with_auto_or_fallback(
        self, audio_data: bytes, language: str, audio_format: AudioFormat, provider: str
    ) -> SpeechRecognitionResult:
        """Process with auto or mistral_fallback provider mode (Watson removed in Phase 2A)"""
        if not self.mistral_stt_available:
            raise Exception("Mistral STT not available")

        return await self._try_mistral_stt(audio_data, language, audio_format, provider)

    async def _select_stt_provider_and_process(
        self,
        audio_data: bytes,
        language: str,
        audio_format: AudioFormat,
        provider: str = "auto",
    ) -> SpeechRecognitionResult:
        """
        Select STT provider and process audio

        Provider options:
        - "auto": Use Mistral STT (primary provider in Phase 2A)
        - "mistral": Use Mistral STT explicitly
        Note: Watson deprecated in Phase 2A migration
        """
        self._validate_provider_not_watson(provider)

        if provider == "mistral":
            return await self._process_with_mistral_explicit(
                audio_data, language, audio_format
            )

        if provider in ["auto", "mistral_fallback"]:
            return await self._process_with_auto_or_fallback(
                audio_data, language, audio_format, provider
            )

        raise ValueError(
            f"Unknown STT provider: {provider}. Use 'auto' or 'mistral' (Watson deprecated in Phase 2A)"
        )

    # Watson STT methods removed - deprecated in Phase 2A migration

    async def _speech_to_text_mistral(
        self, audio_data: bytes, language: str, audio_format: AudioFormat
    ) -> SpeechRecognitionResult:
        """Mistral Speech-to-Text implementation using Voxtral API"""

        if not self.mistral_stt_available or not self.mistral_stt_service:
            raise Exception("Mistral STT service not configured or not available")

        start_time = time.time()

        try:
            # Use the Mistral STT service
            result = await self.mistral_stt_service.transcribe_audio(
                audio_data=audio_data,
                language=language,
                audio_format=audio_format.value,
            )

            processing_time = time.time() - start_time

            # Convert Mistral result to SpeechRecognitionResult format
            return SpeechRecognitionResult(
                transcript=result.transcript,
                confidence=result.confidence,
                language=result.language,
                processing_time=processing_time,
                alternative_transcripts=[
                    {"transcript": alt, "confidence": result.confidence * 0.9}
                    for alt in result.alternative_transcripts
                ],
                metadata={
                    **result.metadata,
                    "provider": "mistral_voxtral",
                    "cost_usd": result.cost_usd,
                    "audio_duration_minutes": result.audio_duration_minutes,
                    "cost_per_minute": 0.001,
                },
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Mistral STT processing error: {e}")

            # Return error result in consistent format
            return SpeechRecognitionResult(
                transcript="[Mistral STT Error]",
                confidence=0.0,
                language=language,
                processing_time=processing_time,
                alternative_transcripts=[],
                metadata={
                    "provider": "mistral_voxtral",
                    "error": str(e),
                    "cost_usd": 0.0,
                },
            )

    # Watson TTS method removed - deprecated in Phase 2A migration

    async def _text_to_speech_piper(
        self, text: str, language: str, voice_type: str, speaking_rate: float
    ) -> SpeechSynthesisResult:
        """Piper Text-to-Speech implementation with local processing"""

        if not self.piper_tts_available or not self.piper_tts_service:
            raise Exception(
                "Piper Text-to-Speech not configured or service not initialized"
            )

        try:
            start_time = asyncio.get_event_loop().time()

            # Use Piper TTS service
            audio_data, metadata = await self.piper_tts_service.synthesize_speech(
                text=text, language=language, audio_format="wav"
            )

            processing_time = asyncio.get_event_loop().time() - start_time

            # Estimate duration from metadata or audio size
            estimated_duration = metadata.get("duration_estimate", len(text) * 0.1)

            return SpeechSynthesisResult(
                audio_data=audio_data,
                audio_format=AudioFormat.WAV,
                sample_rate=metadata.get("sample_rate", 22050),
                duration_seconds=estimated_duration,
                processing_time=processing_time,
                metadata={
                    "piper_voice": metadata.get("voice", "unknown"),
                    "voice_type": voice_type,
                    "speaking_rate": speaking_rate,
                    "service": "piper_tts",
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "cost": 0.0,  # Local processing = zero cost
                    "provider": "piper",
                },
            )

        except Exception as e:
            logger.error(f"Piper TTS synthesis failed: {e}")
            # Fall back to mock response if synthesis fails
            mock_audio_data = f"[Piper TTS unavailable: {str(e)}]".encode("utf-8")

            return SpeechSynthesisResult(
                audio_data=mock_audio_data,
                audio_format=AudioFormat.WAV,
                sample_rate=22050,
                duration_seconds=len(text) * 0.1,  # Rough estimate
                processing_time=0.0,
                metadata={
                    "piper_voice": "unavailable",
                    "voice_type": voice_type,
                    "speaking_rate": speaking_rate,
                    "service": "piper_tts",
                    "error": str(e),
                },
            )

    async def _analyze_audio_quality(
        self, audio_data: bytes, audio_format: AudioFormat
    ) -> AudioMetadata:
        """Analyze audio quality for speech processing"""

        try:
            # Basic audio analysis
            # In a full implementation, this would use audio processing libraries

            file_size = len(audio_data)

            # Estimate duration based on format and size
            # This is a rough estimation - real implementation would decode audio
            estimated_duration = file_size / (
                self.default_sample_rate * 2
            )  # 16-bit samples

            # Simple quality scoring based on file size and estimated duration
            size_quality = min(
                file_size / (self.default_sample_rate * 10), 1.0
            )  # Expect ~10 seconds max
            duration_quality = min(
                estimated_duration / 30.0, 1.0
            )  # Prefer shorter clips

            quality_score = (size_quality + duration_quality) / 2

            # Additional quality checks if audio libraries are available
            if AUDIO_LIBS_AVAILABLE and len(audio_data) > 0:
                try:
                    # Convert bytes to numpy array for analysis
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)

                    # Check for silence (all zeros)
                    if np.all(audio_array == 0):
                        quality_score = 0.1  # Very low quality for silence
                        logger.warning(
                            "Audio quality analysis: Audio appears to be silence"
                        )
                    else:
                        # Calculate signal-to-noise ratio approximation
                        signal_power = np.mean(audio_array.astype(np.float32) ** 2)
                        noise_floor = (
                            np.mean(
                                np.abs(audio_array[audio_array != 0]).astype(np.float32)
                            )
                            * 0.1
                        )
                        if signal_power > 0 and noise_floor > 0:
                            snr_approx = 10 * np.log10(signal_power / (noise_floor**2))
                            # Normalize SNR to 0-1 scale (assuming 0-30 dB range)
                            snr_quality = min(max(snr_approx / 30.0, 0.0), 1.0)
                            # Blend with existing quality score
                            quality_score = (quality_score + snr_quality) / 2

                except Exception as e:
                    logger.warning(f"Advanced audio quality analysis failed: {e}")

            return AudioMetadata(
                format=audio_format,
                sample_rate=self.default_sample_rate,
                channels=self.default_channels,
                duration_seconds=estimated_duration,
                file_size_bytes=file_size,
                quality_score=quality_score,
            )

        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")

            # Return fallback metadata
            return AudioMetadata(
                format=audio_format,
                sample_rate=self.default_sample_rate,
                channels=self.default_channels,
                duration_seconds=1.0,
                file_size_bytes=len(audio_data),
                quality_score=0.5,
            )

    async def _enhance_audio_quality(
        self, audio_data: bytes, audio_format: AudioFormat
    ) -> bytes:
        """Enhance audio quality for better speech recognition"""

        try:
            if not AUDIO_LIBS_AVAILABLE:
                logger.info("Audio enhancement skipped - audio libraries not available")
                return audio_data

            # Apply noise reduction
            enhanced_audio = self._reduce_noise(audio_data)

            # Apply normalization
            enhanced_audio = self._normalize_audio(enhanced_audio)

            # Apply additional enhancement techniques
            enhanced_audio = self._apply_speech_enhancement(enhanced_audio)

            logger.info("Audio enhancement completed successfully")
            return enhanced_audio

        except Exception as e:
            logger.warning(f"Audio enhancement failed: {e}")
            return audio_data  # Return original if enhancement fails

    def _apply_speech_enhancement(self, audio_data: bytes) -> bytes:
        """Apply speech-specific enhancement techniques"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return audio_data

            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Check if array is empty
            if len(audio_array) == 0:
                logger.warning("Speech enhancement skipped - empty audio array")
                return audio_data

            audio_array = np.copy(audio_array)  # Ensure we can modify it

            # Apply pre-emphasis filter to enhance high frequencies (speech clarity)
            if len(audio_array) > 1:
                # Simple first-order high-pass filter
                pre_emphasis = 0.97
                emphasized = np.copy(audio_array)
                emphasized[1:] = audio_array[1:] - pre_emphasis * audio_array[:-1]
                audio_array = emphasized

            # Apply dynamic range compression for better speech intelligibility
            if len(audio_array) > 0:
                # Convert to float for processing
                float_audio = audio_array.astype(np.float32)

                # Apply simple compression (reduce peaks, boost quiet parts)
                max_val = np.max(np.abs(float_audio))
                if max_val > 0:
                    # Normalize and apply compression
                    normalized = float_audio / max_val
                    compressed = np.sign(normalized) * np.power(np.abs(normalized), 0.8)
                    # Scale back to 16-bit range
                    audio_array = (compressed * 32767).astype(np.int16)

            # Convert back to bytes
            return audio_array.tobytes()

        except Exception as e:
            logger.warning(f"Speech enhancement failed: {e}")
            return audio_data

    def _calculate_pronunciation_scores(
        self, words: List[str], word_count: int, audio_metadata: AudioMetadata
    ) -> tuple[float, float, float]:
        """Calculate phonetic accuracy, fluency, and overall scores"""
        phonetic_accuracy = min(audio_metadata.quality_score + 0.2, 1.0)
        fluency_score = min(
            word_count / audio_metadata.duration_seconds / 3.0, 1.0
        )  # ~3 words per second
        overall_score = phonetic_accuracy * 0.6 + fluency_score * 0.4
        return phonetic_accuracy, fluency_score, overall_score

    def _determine_pronunciation_level(
        self, overall_score: float
    ) -> PronunciationLevel:
        """Determine pronunciation level from overall score"""
        if overall_score >= 0.9:
            return PronunciationLevel.EXCELLENT
        elif overall_score >= 0.75:
            return PronunciationLevel.GOOD
        elif overall_score >= 0.6:
            return PronunciationLevel.FAIR
        elif overall_score >= 0.4:
            return PronunciationLevel.NEEDS_IMPROVEMENT
        else:
            return PronunciationLevel.UNCLEAR

    def _generate_word_scores(
        self, words: List[str], overall_score: float
    ) -> List[Dict[str, Any]]:
        """Generate word-level pronunciation scores"""
        word_scores = []
        for word in words:
            word_score = overall_score + (hash(word) % 20 - 10) / 100
            word_score = max(0.0, min(1.0, word_score))
            word_scores.append(
                {
                    "word": word,
                    "score": word_score,
                    "phonetic": f"/{word}/",
                    "issues": [],
                }
            )
        return word_scores

    def _generate_improvement_suggestions(
        self, overall_score: float, fluency_score: float, language: str
    ) -> List[str]:
        """Generate pronunciation improvement suggestions"""
        suggestions = []
        if overall_score < 0.7:
            suggestions.extend(
                [
                    f"Focus on clear pronunciation of {language} sounds",
                    "Speak more slowly for better clarity",
                    "Practice tongue twisters for better articulation",
                ]
            )
        if fluency_score < 0.6:
            suggestions.append("Work on speaking rhythm and pacing")
        return suggestions

    def _detect_language_issues(
        self, words: List[str], language_model: Dict[str, Any]
    ) -> List[str]:
        """Detect language-specific pronunciation issues"""
        detected_issues = []
        for issue in language_model["common_issues"]:
            if any(word in language_model["difficulty_words"] for word in words):
                detected_issues.append(issue)
        return detected_issues

    async def _analyze_pronunciation(
        self,
        audio_data: bytes,
        transcript: str,
        language: str,
        audio_metadata: AudioMetadata,
    ) -> PronunciationAnalysis:
        """Analyze pronunciation quality from audio and transcript"""
        try:
            language_model = self.pronunciation_models.get(
                language, self.pronunciation_models["en"]
            )
            words = transcript.lower().split()
            word_count = len(words)

            phonetic_accuracy, fluency_score, overall_score = (
                self._calculate_pronunciation_scores(words, word_count, audio_metadata)
            )
            level = self._determine_pronunciation_level(overall_score)
            word_scores = self._generate_word_scores(words, overall_score)
            suggestions = self._generate_improvement_suggestions(
                overall_score, fluency_score, language
            )
            detected_issues = self._detect_language_issues(words, language_model)

            return PronunciationAnalysis(
                overall_score=overall_score,
                pronunciation_level=level,
                phonetic_accuracy=phonetic_accuracy,
                fluency_score=fluency_score,
                word_level_scores=word_scores,
                detected_issues=detected_issues,
                improvement_suggestions=suggestions,
                phonetic_transcription=f"/{' '.join(words)}/",
                target_phonetics=f"/{' '.join(words)}/",
            )

        except Exception as e:
            logger.error(f"Pronunciation analysis failed: {e}")
            raise Exception(f"Pronunciation analysis failed: {str(e)}")

    async def _compare_pronunciation(
        self,
        recognized_text: str,
        reference_text: str,
        language: str,
        confidence: float,
    ) -> PronunciationAnalysis:
        """Compare recognized speech with reference text"""

        # Simple text comparison for pronunciation scoring
        # Real implementation would use phonetic comparison

        recognized_words = recognized_text.lower().split()
        reference_words = reference_text.lower().split()

        # Calculate word accuracy
        correct_words = 0
        for i, ref_word in enumerate(reference_words):
            if i < len(recognized_words) and recognized_words[i] == ref_word:
                correct_words += 1

        word_accuracy = correct_words / len(reference_words) if reference_words else 0.0

        # Combine with recognition confidence
        word_accuracy * 0.7 + confidence * 0.3

        # Generate analysis similar to _analyze_pronunciation
        return await self._analyze_pronunciation(
            audio_data=b"",  # Not used in this comparison mode
            transcript=recognized_text,
            language=language,
            audio_metadata=AudioMetadata(
                format=AudioFormat.WAV,
                sample_rate=16000,
                channels=1,
                duration_seconds=1.0,
                file_size_bytes=1000,
                quality_score=confidence,
            ),
        )

    async def _preprocess_audio(
        self, audio_data: bytes, audio_format: AudioFormat
    ) -> bytes:
        """Preprocess audio for better recognition quality"""
        try:
            # Validate minimum size requirements
            if len(audio_data) < 100:
                logger.warning(f"Audio data too small: {len(audio_data)} bytes")
                # Pad with silence if needed
                audio_data = self._pad_audio(audio_data)

            # Apply noise reduction if available
            if self.audio_libs_available:
                audio_data = self._reduce_noise(audio_data)

            # Normalize audio levels
            audio_data = self._normalize_audio(audio_data)

            # Ensure proper WAV format for Watson STT
            if audio_format == AudioFormat.WAV:
                audio_data = await self._ensure_proper_wav_format(audio_data)

            return audio_data

        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return audio_data  # Return original if preprocessing fails

    async def _ensure_proper_wav_format(self, audio_data: bytes) -> bytes:
        """Ensure audio data is in proper WAV format for Watson STT"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return audio_data

            # If it's already a valid WAV file, return as is
            if audio_data.startswith(b"RIFF") and b"WAVE" in audio_data[:12]:
                return audio_data

            # Convert raw audio data to proper WAV format
            import io
            import wave

            # Create a proper WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(self.default_channels)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.default_sample_rate)  # 16kHz
                wav_file.writeframes(audio_data)

            wav_buffer.seek(0)
            return wav_buffer.read()

        except Exception as e:
            logger.warning(f"WAV format conversion failed: {e}")
            return audio_data

    def _pad_audio(self, audio_data: bytes) -> bytes:
        """Pad audio data with silence if too small"""
        # Add 100 bytes of silence (zeros) to meet minimum requirements
        padding = b"\x00" * max(0, 100 - len(audio_data))
        return audio_data + padding

    def _reduce_noise(self, audio_data: bytes) -> bytes:
        """Apply basic noise reduction to audio data"""
        # Simple noise reduction - in a full implementation, this would use more sophisticated techniques
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return audio_data

            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Check if array is empty
            if len(audio_array) == 0:
                logger.warning("Noise reduction skipped - empty audio array")
                return audio_data

            # Create a copy to ensure we can modify it (fixes read-only array issue)
            audio_array = np.copy(audio_array)

            # Simple noise gate - mute samples below threshold
            max_val = np.max(np.abs(audio_array))
            if max_val > 0:  # Avoid division by zero
                threshold = max_val * 0.1  # 10% of max amplitude
                audio_array[np.abs(audio_array) < threshold] = 0

            # Convert back to bytes
            return audio_array.tobytes()

        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio_data

    def _normalize_audio(self, audio_data: bytes) -> bytes:
        """Normalize audio levels for better recognition"""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return audio_data

            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Check if array is empty
            if len(audio_array) == 0:
                logger.warning("Audio normalization skipped - empty audio array")
                return audio_data

            # Create a copy to ensure we can modify it (fixes read-only array issue)
            audio_array = np.copy(audio_array)

            # Normalize to use full 16-bit range
            if len(audio_array) > 0:
                max_val = np.max(np.abs(audio_array))
                if max_val > 0:
                    normalized = audio_array.astype(np.float32) * (32767.0 / max_val)
                    audio_array = normalized.astype(np.int16)

            # Convert back to bytes
            return audio_array.tobytes()

        except Exception as e:
            logger.warning(f"Audio normalization failed: {e}")
            return audio_data

    async def _prepare_text_for_synthesis(
        self,
        text: str,
        language: str,
        emphasis_words: Optional[List[str]],
        speaking_rate: float,
    ) -> str:
        """Prepare text for optimal speech synthesis with SSML markup"""
        enhanced_text = text.strip()
        enhanced_text = self._apply_speaking_rate(enhanced_text, speaking_rate)
        enhanced_text = self._apply_word_emphasis(enhanced_text, emphasis_words)
        enhanced_text = self._apply_language_specific_enhancements(
            enhanced_text, language
        )
        enhanced_text = self._add_comprehension_pauses(enhanced_text)
        enhanced_text = self._wrap_in_ssml_if_needed(enhanced_text)
        return enhanced_text

    def _apply_speaking_rate(self, text: str, speaking_rate: float) -> str:
        """Apply speaking rate adjustment to text - A(3)"""
        if speaking_rate == 1.0:
            return text

        # Watson accepts rate as percentage (-50% to +100%)
        rate_percentage = int((speaking_rate - 1.0) * 50)
        rate_percentage = max(-50, min(100, rate_percentage))  # Clamp to Watson limits
        return f'<prosody rate="{rate_percentage:+d}%">{text}</prosody>'

    def _apply_word_emphasis(
        self, text: str, emphasis_words: Optional[List[str]]
    ) -> str:
        """Add emphasis markup to specific words - A(4)"""
        if not emphasis_words:
            return text

        import re

        enhanced_text = text
        for word in emphasis_words:
            if word.lower() in enhanced_text.lower():
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                enhanced_text = pattern.sub(
                    f'<emphasis level="strong">{word}</emphasis>',
                    enhanced_text,
                    count=1,
                )
        return enhanced_text

    def _apply_language_specific_enhancements(self, text: str, language: str) -> str:
        """Apply language-specific SSML enhancements - B(6)"""
        if language == "zh":
            return self._enhance_chinese_text(text)
        elif language == "fr":
            return self._enhance_french_text(text)
        elif language == "es":
            return self._enhance_spanish_text(text)
        elif language == "en":
            return self._enhance_english_text(text)
        return text

    def _enhance_chinese_text(self, text: str) -> str:
        """Enhance Chinese text for pronunciation learning - B(7)"""
        chinese_chars = [
            "你",
            "好",
            "世",
            "界",
            "是",
            "这",
            "一",
            "个",
            "测",
            "试",
            "谢",
            "叫",
            "小",
            "明",
            "今",
            "天",
            "天",
            "气",
            "很",
            "在",
            "学",
            "习",
            "中",
            "文",
        ]

        if not any(char in text for char in chinese_chars):
            return text

        enhanced_text = text
        # Slow down speech for Chinese pronunciation learning
        if "<prosody rate=" not in enhanced_text:
            enhanced_text = f'<prosody rate="-30%">{enhanced_text}</prosody>'

        # Add pauses between characters for learning (limited to prevent errors)
        for i, char in enumerate(chinese_chars[:10]):
            if char in enhanced_text and i < 5:
                enhanced_text = enhanced_text.replace(
                    char, f'{char}<break time="150ms"/>', 1
                )

        return enhanced_text

    def _enhance_french_text(self, text: str) -> str:
        """Enhance French text for liaison and nasal sounds - A(2)"""
        enhanced_text = text.replace(
            "les ", '<emphasis level="moderate">les</emphasis> '
        )
        enhanced_text = enhanced_text.replace(
            "un ", '<emphasis level="moderate">un</emphasis> '
        )
        return enhanced_text

    def _enhance_spanish_text(self, text: str) -> str:
        """Enhance Spanish text for rolled R sounds - A(1)"""
        return text.replace("rr", '<emphasis level="strong">rr</emphasis>')

    def _enhance_english_text(self, text: str) -> str:
        """Enhance English text for common pronunciation challenges - A(1)"""
        return text.replace(" th", ' <emphasis level="moderate">th</emphasis>')

    def _add_comprehension_pauses(self, text: str) -> str:
        """Add pauses for better comprehension in language learning - A(3)"""
        enhanced_text = text
        if "." in enhanced_text:
            enhanced_text = enhanced_text.replace(". ", '.<break time="500ms"/> ')
        if "," in enhanced_text:
            enhanced_text = enhanced_text.replace(", ", ',<break time="200ms"/> ')
        return enhanced_text

    def _wrap_in_ssml_if_needed(self, text: str) -> str:
        """Wrap text in SSML speak tag if markup is present - A(2)"""
        if "<" in text and ">" in text:
            return f'<speak version="1.0">{text}</speak>'
        return text

    async def get_speech_pipeline_status(self) -> Dict[str, Any]:
        """Get status of speech processing pipeline"""
        watson_stt_functional = bool(
            self.watson_stt_client and self.watson_stt_available
        )
        watson_tts_functional = bool(
            self.watson_tts_client and self.watson_tts_available
        )
        settings = self._get_settings_safely()

        return {
            "status": self._get_overall_status(
                watson_stt_functional, watson_tts_functional
            ),
            "watson_sdk_available": self.watson_sdk_available,
            "watson_stt": self._build_watson_stt_status(
                watson_stt_functional, settings
            ),
            "watson_tts": self._build_watson_tts_status(
                watson_tts_functional, settings
            ),
            "watson_stt_available": watson_stt_functional,
            "watson_tts_available": watson_tts_functional,
            "audio_libs_available": self.audio_libs_available,
            "supported_formats": [fmt.value for fmt in AudioFormat],
            "supported_languages": list(self.pronunciation_models.keys()),
            "features": self._build_features_status(
                watson_stt_functional, watson_tts_functional
            ),
            "configuration": self._build_configuration_dict(),
            "api_models": self._build_api_models_dict(),
            "chinese_support": self._build_chinese_support_dict(),
            "spanish_support": self._build_spanish_support_dict(),
        }

    def _get_settings_safely(self):
        """Get settings with exception handling"""
        try:
            return get_settings()
        except Exception:
            return None

    def _get_overall_status(self, stt_functional: bool, tts_functional: bool) -> str:
        """Determine overall pipeline status"""
        return "operational" if (stt_functional or tts_functional) else "limited"

    def _build_watson_stt_status(self, functional: bool, settings) -> Dict[str, Any]:
        """Build Watson STT status dictionary"""
        return {
            "status": "operational" if functional else "unavailable",
            "configured": self.watson_stt_available,
            "client_initialized": bool(self.watson_stt_client),
            "api_key_configured": bool(
                getattr(settings, "IBM_WATSON_STT_API_KEY", None)
            )
            if settings
            else False,
            "service_url": getattr(settings, "IBM_WATSON_STT_URL", "not_configured")
            if settings
            else "not_configured",
        }

    def _build_watson_tts_status(self, functional: bool, settings) -> Dict[str, Any]:
        """Build Watson TTS status dictionary"""
        return {
            "status": "operational" if functional else "unavailable",
            "configured": self.watson_tts_available,
            "client_initialized": bool(self.watson_tts_client),
            "api_key_configured": bool(
                getattr(settings, "IBM_WATSON_TTS_API_KEY", None)
            )
            if settings
            else False,
            "service_url": getattr(settings, "IBM_WATSON_TTS_URL", "not_configured")
            if settings
            else "not_configured",
        }

    def _build_features_status(
        self, stt_functional: bool, tts_functional: bool
    ) -> Dict[str, Any]:
        """Build features availability dictionary"""
        return {
            "speech_recognition": stt_functional,
            "speech_synthesis": tts_functional,
            "pronunciation_analysis": True,
            "audio_enhancement": self.audio_libs_available,
            "real_time_processing": self.audio_libs_available
            and self.watson_sdk_available,
        }

    def _build_configuration_dict(self) -> Dict[str, Any]:
        """Build configuration settings dictionary"""
        return {
            "default_sample_rate": self.default_sample_rate,
            "default_channels": self.default_channels,
            "chunk_size": self.chunk_size,
        }

    def _build_api_models_dict(self) -> Dict[str, list]:
        """Build API models and voices dictionary"""
        return {
            "watson_stt_models": [
                "en-US_BroadbandModel",
                "fr-FR_BroadbandModel",
                "es-ES_BroadbandModel",
                "de-DE_BroadbandModel",
                "zh-CN_BroadbandModel",
                "ja-JP_BroadbandModel",
            ],
            "watson_tts_voices": [
                "en-US_AllisonV3Voice",
                "fr-FR_ReneeV3Voice",
                "es-ES_LauraV3Voice",
                "de-DE_BirgitV3Voice",
                "ja-JP_EmiV3Voice",
                "ko-KR_YoungmiVoice",
            ],
        }

    def _build_chinese_support_dict(self) -> Dict[str, Any]:
        """Build Chinese language support dictionary"""
        return {
            "stt_available": True,
            "tts_native_voice": False,
            "tts_fallback": "en-US_AllisonV3Voice",
            "pronunciation_learning": True,
            "note": "Chinese STT fully supported. TTS uses English voice with Chinese-optimized SSML.",
        }

    def _build_spanish_support_dict(self) -> Dict[str, Any]:
        """Build Spanish language support dictionary"""
        return {
            "stt_model": "es-MX_BroadbandModel",
            "tts_voice": "es-LA_SofiaV3Voice",
            "note": "Using Mexican Spanish STT and Latin American Spanish TTS (closest to es-MX preference)",
        }

    async def check_watson_health(self) -> Dict[str, Any]:
        """Check Watson service health"""
        health_status = {
            "stt_available": False,
            "tts_available": False,
            "stt_response_time": None,
            "tts_response_time": None,
        }

        # Check STT health
        if self.watson_stt_client:
            try:
                import time

                start_time = time.time()
                # Simple health check - list models
                self.watson_stt_client.list_models()
                health_status["stt_available"] = True
                health_status["stt_response_time"] = time.time() - start_time
            except Exception:
                health_status["stt_available"] = False

        # Check TTS health
        if self.watson_tts_client:
            try:
                import time

                start_time = time.time()
                # Simple health check - list voices
                self.watson_tts_client.list_voices()
                health_status["tts_available"] = True
                health_status["tts_response_time"] = time.time() - start_time
            except Exception:
                health_status["tts_available"] = False

        return health_status


# Global speech processor instance
speech_processor = SpeechProcessor()


# Convenience functions for easy integration
async def speech_to_text(
    audio_data: bytes, language: str = "en", analyze_pronunciation: bool = True
) -> Tuple[str, Optional[PronunciationAnalysis]]:
    """Convert speech to text with optional pronunciation analysis"""

    result, pronunciation = await speech_processor.process_speech_to_text(
        audio_data=audio_data,
        language=language,
        enable_pronunciation_analysis=analyze_pronunciation,
    )

    return result.transcript, pronunciation


async def text_to_speech(
    text: str, language: str = "en", voice_type: str = "neural"
) -> bytes:
    """Convert text to speech"""

    result = await speech_processor.process_text_to_speech(
        text=text, language=language, voice_type=voice_type
    )

    return result.audio_data


async def analyze_pronunciation(
    audio_data: bytes, reference_text: str, language: str = "en"
) -> PronunciationAnalysis:
    """Analyze pronunciation quality"""

    return await speech_processor.analyze_pronunciation_quality(
        user_audio=audio_data, reference_text=reference_text, language=language
    )


async def get_speech_status() -> Dict[str, Any]:
    """Get speech processing pipeline status"""
    return await speech_processor.get_speech_pipeline_status()
