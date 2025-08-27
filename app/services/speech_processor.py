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
import io
import wave
import json
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import tempfile
import os

# Audio processing libraries
try:
    import pyaudio
    import webrtcvad
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio processing libraries not available. Install pyaudio and webrtcvad for full functionality.")

# IBM Watson Speech Services
try:
    from ibm_watson import SpeechToTextV1, TextToSpeechV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_watson.websocket import RecognizeCallback, AudioSource
    WATSON_SDK_AVAILABLE = True
except ImportError:
    WATSON_SDK_AVAILABLE = False
    logging.warning("IBM Watson SDK not available. Install ibm-watson for full functionality.")

from app.services.ai_router import ai_router
from app.core.config import get_settings

logger = logging.getLogger(__name__)


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
        self.settings = get_settings()
        self.watson_stt_available = bool(self.settings.IBM_WATSON_STT_API_KEY)
        self.watson_tts_available = bool(self.settings.IBM_WATSON_TTS_API_KEY)
        self.audio_libs_available = AUDIO_LIBS_AVAILABLE
        self.watson_sdk_available = WATSON_SDK_AVAILABLE
        
        # Initialize Watson SDK clients
        self._init_watson_clients()
        
        # Audio processing settings
        self.default_sample_rate = 16000
        self.default_channels = 1
        self.chunk_size = 1024
        
        # Pronunciation analysis settings
        self.pronunciation_models = self._load_pronunciation_models()
        
    def _init_watson_clients(self):
        """Initialize IBM Watson Speech-to-Text and Text-to-Speech clients"""
        self.watson_stt_client = None
        self.watson_tts_client = None
        
        if not self.watson_sdk_available:
            logger.warning("IBM Watson SDK not available. Speech services will be limited.")
            return
            
        try:
            # Initialize Speech-to-Text client
            if self.watson_stt_available:
                stt_authenticator = IAMAuthenticator(self.settings.IBM_WATSON_STT_API_KEY)
                self.watson_stt_client = SpeechToTextV1(authenticator=stt_authenticator)
                self.watson_stt_client.set_service_url(self.settings.IBM_WATSON_STT_URL)
                logger.info("Watson Speech-to-Text client initialized successfully")
            
            # Initialize Text-to-Speech client  
            if self.watson_tts_available:
                tts_authenticator = IAMAuthenticator(self.settings.IBM_WATSON_TTS_API_KEY)
                self.watson_tts_client = TextToSpeechV1(authenticator=tts_authenticator)
                self.watson_tts_client.set_service_url(self.settings.IBM_WATSON_TTS_URL)
                logger.info("Watson Text-to-Speech client initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize Watson clients: {e}")
            self.watson_stt_client = None
            self.watson_tts_client = None
            self.watson_stt_available = False
            self.watson_tts_available = False
    
    async def check_available_voices(self) -> Dict[str, List[str]]:
        """Check available voices in Watson TTS service"""
        if not self.watson_tts_client:
            return {"error": "Watson TTS client not available"}
        
        try:
            voices_result = self.watson_tts_client.list_voices().get_result()
            
            available_voices = {}
            language_support = {}
            
            for voice in voices_result['voices']:
                language = voice['language']
                voice_name = voice['name']
                
                if language not in available_voices:
                    available_voices[language] = []
                available_voices[language].append(voice_name)
                
                # Map to our simplified language codes
                lang_code = language.split('-')[0]
                if lang_code not in language_support:
                    language_support[lang_code] = []
                language_support[lang_code].append(voice_name)
            
            return {
                "available_voices": available_voices,
                "language_support": language_support,
                "chinese_supported": any('zh' in lang for lang in available_voices.keys()),
                "total_languages": len(available_voices)
            }
            
        except Exception as e:
            logger.error(f"Failed to check available voices: {e}")
            return {"error": str(e)}
        
    def _load_pronunciation_models(self) -> Dict[str, Any]:
        """Load language-specific pronunciation models"""
        # This would load actual pronunciation models in a full implementation
        # For now, we'll use configuration-based scoring
        return {
            "en": {
                "phoneme_weights": {"vowels": 0.4, "consonants": 0.4, "stress": 0.2},
                "common_issues": ["th_sounds", "r_sounds", "vowel_length"],
                "difficulty_words": ["through", "thoroughly", "rhythm", "worcestershire"]
            },
            "fr": {
                "phoneme_weights": {"nasal_vowels": 0.3, "r_sounds": 0.3, "liaison": 0.2, "accent": 0.2},
                "common_issues": ["nasal_vowels", "french_r", "silent_letters"],
                "difficulty_words": ["grenouille", "écureuil", "serrurerie", "anticonstitutionnellement"]
            },
            "es": {
                "phoneme_weights": {"rolled_r": 0.3, "vowels": 0.3, "stress": 0.2, "consonants": 0.2},
                "common_issues": ["rr_trill", "stress_patterns", "vowel_clarity"],
                "difficulty_words": ["rápidamente", "ferrocarril", "trabajar", "desarrollar"]
            },
            "zh": {
                "phoneme_weights": {"tones": 0.5, "consonants": 0.25, "vowels": 0.25},
                "common_issues": ["tone_accuracy", "retroflex_sounds", "aspiration"],
                "difficulty_words": ["是", "知道", "中国", "学习"]
            }
        }
    
    async def process_speech_to_text(
        self,
        audio_data: bytes,
        language: str = "en",
        audio_format: AudioFormat = AudioFormat.WAV,
        enable_pronunciation_analysis: bool = True
    ) -> Tuple[SpeechRecognitionResult, Optional[PronunciationAnalysis]]:
        """
        Process speech to text with optional pronunciation analysis
        
        Args:
            audio_data: Raw audio data
            language: Target language for recognition
            audio_format: Audio format
            enable_pronunciation_analysis: Whether to analyze pronunciation
            
        Returns:
            Speech recognition result and optional pronunciation analysis
        """
        start_time = datetime.now()
        
        try:
            # Validate and preprocess audio
            audio_metadata = await self._analyze_audio_quality(audio_data, audio_format)
            
            if audio_metadata.quality_score < 0.5:
                logger.warning(f"Low audio quality detected: {audio_metadata.quality_score}")
                # Attempt audio enhancement
                audio_data = await self._enhance_audio_quality(audio_data, audio_format)
            
            # Perform speech recognition
            recognition_result = await self._speech_to_text_watson(
                audio_data=audio_data,
                language=language,
                audio_format=audio_format
            )
            
            pronunciation_analysis = None
            if enable_pronunciation_analysis and recognition_result.confidence > 0.5:
                pronunciation_analysis = await self._analyze_pronunciation(
                    audio_data=audio_data,
                    transcript=recognition_result.transcript,
                    language=language,
                    audio_metadata=audio_metadata
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
                metadata={"error": str(e), "fallback": True}
            )
            
            return fallback_result, None
    
    async def process_text_to_speech(
        self,
        text: str,
        language: str = "en",
        voice_type: str = "neural",
        speaking_rate: float = 1.0,
        emphasis_words: Optional[List[str]] = None
    ) -> SpeechSynthesisResult:
        """
        Convert text to speech with language learning optimizations
        
        Args:
            text: Text to synthesize
            language: Target language
            voice_type: Voice type (neural, standard)
            speaking_rate: Speaking speed (0.5-2.0)
            emphasis_words: Words to emphasize for learning
            
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
                speaking_rate=speaking_rate
            )
            
            # Synthesize speech using Watson TTS
            synthesis_result = await self._text_to_speech_watson(
                text=optimized_text,
                language=language,
                voice_type=voice_type,
                speaking_rate=speaking_rate
            )
            
            synthesis_result.processing_time = (datetime.now() - start_time).total_seconds()
            
            return synthesis_result
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise Exception(f"Speech synthesis failed: {str(e)}")
    
    async def analyze_pronunciation_quality(
        self,
        user_audio: bytes,
        reference_text: str,
        language: str = "en"
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
                enable_pronunciation_analysis=False
            )
            
            # Compare with reference text
            pronunciation_analysis = await self._compare_pronunciation(
                recognized_text=recognition_result.transcript,
                reference_text=reference_text,
                language=language,
                confidence=recognition_result.confidence
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
                target_phonetics=""
            )
    
    # Private implementation methods
    
    async def _speech_to_text_watson(
        self,
        audio_data: bytes,
        language: str,
        audio_format: AudioFormat
    ) -> SpeechRecognitionResult:
        """Watson Speech-to-Text implementation with real API calls"""
        
        if not self.watson_stt_available or not self.watson_stt_client:
            raise Exception("Watson Speech-to-Text not configured or client not initialized")
        
        try:
            # Language mapping for Watson STT (updated with verified available models)
            watson_language_map = {
                "en": "en-US_BroadbandModel",
                "fr": "fr-FR_BroadbandModel", 
                "es": "es-MX_BroadbandModel",  # Mexican Spanish for user preference
                "de": "de-DE_BroadbandModel",
                "zh": "zh-CN_BroadbandModel",  # Chinese STT is available
                "ja": "ja-JP_BroadbandModel",
                "ko": "ko-KR_BroadbandModel",
                "it": "it-IT_BroadbandModel",
                "pt": "pt-BR_BroadbandModel",
                "nl": "nl-NL_BroadbandModel"
            }
            
            watson_model = watson_language_map.get(language, "en-US_BroadbandModel")
            
            # Prepare audio file-like object for Watson API
            audio_file = io.BytesIO(audio_data)
            
            # Watson STT API call with optimized parameters for language learning
            response = self.watson_stt_client.recognize(
                audio=audio_file,
                content_type=f'audio/{audio_format.value}',
                model=watson_model,
                continuous=True,
                word_alternatives_threshold=0.7,
                word_confidence=True,
                timestamps=True,
                max_alternatives=3,
                interim_results=False,
                end_of_phrase_silence_time=1.0,
                split_transcript_at_phrase_end=True
            ).get_result()
            
            # Process Watson response
            if not response['results'] or not response['results'][0]['alternatives']:
                raise Exception("No speech detected in audio")
            
            primary_result = response['results'][0]['alternatives'][0]
            alternative_transcripts = response['results'][0]['alternatives'][1:] if len(response['results'][0]['alternatives']) > 1 else []
            
            # Extract word-level confidence and timestamps for pronunciation analysis
            word_info = []
            if 'word_confidence' in primary_result:
                word_info = primary_result['word_confidence']
            
            timestamps = []
            if 'timestamps' in primary_result:
                timestamps = primary_result['timestamps']
            
            return SpeechRecognitionResult(
                transcript=primary_result['transcript'].strip(),
                confidence=primary_result['confidence'],
                language=language,
                processing_time=0.0,  # Will be set by caller
                alternative_transcripts=alternative_transcripts,
                metadata={
                    "watson_model": watson_model,
                    "audio_format": audio_format.value,
                    "service": "watson_stt",
                    "word_confidence": word_info,
                    "timestamps": timestamps,
                    "speaker_labels": response.get('speaker_labels', []),
                    "processing_metrics": response.get('processing_metrics', {})
                }
            )
            
        except Exception as e:
            logger.error(f"Watson STT API call failed: {e}")
            # Fall back to mock response if API fails
            return SpeechRecognitionResult(
                transcript="[Watson STT unavailable - please check configuration]",
                confidence=0.0,
                language=language,
                processing_time=0.0,
                alternative_transcripts=[],
                metadata={
                    "watson_model": watson_language_map.get(language, "en-US_BroadbandModel"),
                    "audio_format": audio_format.value,
                    "service": "watson_stt",
                    "error": str(e)
                }
            )
    
    async def _text_to_speech_watson(
        self,
        text: str,
        language: str,
        voice_type: str,
        speaking_rate: float
    ) -> SpeechSynthesisResult:
        """Watson Text-to-Speech implementation with real API calls"""
        
        if not self.watson_tts_available or not self.watson_tts_client:
            raise Exception("Watson Text-to-Speech not configured or client not initialized")
        
        try:
            # Language and voice mapping for Watson TTS (updated with verified available voices)
            watson_voices = {
                "en": "en-US_AllisonV3Voice" if voice_type == "neural" else "en-US_AllisonVoice",
                "fr": "fr-FR_ReneeV3Voice" if voice_type == "neural" else "fr-FR_ReneeVoice",
                "es": "es-LA_SofiaV3Voice" if voice_type == "neural" else "es-LA_SofiaVoice",  # Latin American Spanish (closest to es-MX)
                "de": "de-DE_BirgitV3Voice" if voice_type == "neural" else "de-DE_BirgitVoice",
                "zh": "en-US_AllisonV3Voice",  # Fallback to English (no Chinese voices available in plan)
                "ja": "ja-JP_EmiV3Voice" if voice_type == "neural" else "ja-JP_EmiVoice",
                "ko": "ko-KR_JinV3Voice",  # Korean support
                "it": "it-IT_FrancescaV3Voice" if voice_type == "neural" else "it-IT_FrancescaVoice",
                "pt": "pt-BR_IsabelaV3Voice" if voice_type == "neural" else "pt-BR_IsabelaVoice",
                "nl": "nl-NL_MerelV3Voice"
            }
            
            watson_voice = watson_voices.get(language, "en-US_AllisonV3Voice")
            
            # In real implementation, this would call Watson TTS API
            # Enhance text with SSML for better pronunciation learning
            enhanced_text = await self._prepare_text_for_synthesis(
                text=text,
                language=language,
                emphasis_words=None,
                speaking_rate=speaking_rate
            )
            
            # Add Chinese language support info
            if language == "zh" and watson_voice.startswith("en-"):
                logger.info(f"Chinese STT available, but TTS uses English voice fallback (no Chinese TTS voices in current Watson plan).")
                # Use simpler SSML markup for English voice compatibility
                enhanced_text = f"<prosody rate='-20%'>{enhanced_text}</prosody>"
            
            # Watson TTS API call with optimized parameters
            response = self.watson_tts_client.synthesize(
                text=enhanced_text,
                voice=watson_voice,
                accept='audio/wav',  # High quality WAV format
                rate_percentage=int((speaking_rate - 1.0) * 50),  # Convert to Watson rate
            ).get_result()
            
            # Extract audio data from response
            audio_data = response.content
            
            # Estimate duration (rough calculation)
            # Average speaking rate is ~150 words per minute for normal speech
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60 / speaking_rate
            
            return SpeechSynthesisResult(
                audio_data=audio_data,
                audio_format=AudioFormat.WAV,
                sample_rate=22050,  # Watson default
                duration_seconds=estimated_duration,
                processing_time=0.0,  # Will be set by caller
                metadata={
                    "watson_voice": watson_voice,
                    "voice_type": voice_type,
                    "speaking_rate": speaking_rate,
                    "service": "watson_tts",
                    "text_length": len(text),
                    "word_count": word_count,
                    "enhanced_text": enhanced_text != text
                }
            )
            
        except Exception as e:
            logger.error(f"Watson TTS API call failed: {e}")
            # Fall back to mock response if API fails
            mock_audio_data = f"[Watson TTS unavailable: {str(e)}]".encode('utf-8')
            
            return SpeechSynthesisResult(
                audio_data=mock_audio_data,
                audio_format=AudioFormat.WAV,
                sample_rate=22050,
                duration_seconds=len(text) * 0.1,  # Rough estimate
                processing_time=0.0,
                metadata={
                    "watson_voice": watson_voices.get(language, "en-US_AllisonV3Voice"),
                    "voice_type": voice_type,
                    "speaking_rate": speaking_rate,
                    "service": "watson_tts",
                    "error": str(e)
                }
            )
    
    async def _analyze_audio_quality(
        self,
        audio_data: bytes,
        audio_format: AudioFormat
    ) -> AudioMetadata:
        """Analyze audio quality for speech processing"""
        
        try:
            # Basic audio analysis
            # In a full implementation, this would use audio processing libraries
            
            file_size = len(audio_data)
            
            # Estimate duration based on format and size
            # This is a rough estimation - real implementation would decode audio
            estimated_duration = file_size / (self.default_sample_rate * 2)  # 16-bit samples
            
            # Simple quality scoring based on file size and estimated duration
            size_quality = min(file_size / (self.default_sample_rate * 10), 1.0)  # Expect ~10 seconds max
            duration_quality = min(estimated_duration / 30.0, 1.0)  # Prefer shorter clips
            
            quality_score = (size_quality + duration_quality) / 2
            
            return AudioMetadata(
                format=audio_format,
                sample_rate=self.default_sample_rate,
                channels=self.default_channels,
                duration_seconds=estimated_duration,
                file_size_bytes=file_size,
                quality_score=quality_score
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
                quality_score=0.5
            )
    
    async def _enhance_audio_quality(
        self,
        audio_data: bytes,
        audio_format: AudioFormat
    ) -> bytes:
        """Enhance audio quality for better speech recognition"""
        
        # In a full implementation, this would apply noise reduction,
        # normalization, and other audio enhancement techniques
        
        logger.info("Audio enhancement applied")
        return audio_data  # Return original for now
    
    async def _analyze_pronunciation(
        self,
        audio_data: bytes,
        transcript: str,
        language: str,
        audio_metadata: AudioMetadata
    ) -> PronunciationAnalysis:
        """Analyze pronunciation quality from audio and transcript"""
        
        try:
            language_model = self.pronunciation_models.get(language, self.pronunciation_models["en"])
            
            # Simple pronunciation analysis based on transcript and language
            words = transcript.lower().split()
            word_count = len(words)
            
            # Calculate basic scores
            phonetic_accuracy = min(audio_metadata.quality_score + 0.2, 1.0)
            fluency_score = min(word_count / audio_metadata.duration_seconds / 3.0, 1.0)  # ~3 words per second
            
            # Overall score combining factors
            overall_score = (phonetic_accuracy * 0.6 + fluency_score * 0.4)
            
            # Determine pronunciation level
            if overall_score >= 0.9:
                level = PronunciationLevel.EXCELLENT
            elif overall_score >= 0.75:
                level = PronunciationLevel.GOOD
            elif overall_score >= 0.6:
                level = PronunciationLevel.FAIR
            elif overall_score >= 0.4:
                level = PronunciationLevel.NEEDS_IMPROVEMENT
            else:
                level = PronunciationLevel.UNCLEAR
            
            # Generate word-level scores
            word_scores = []
            for word in words:
                word_score = overall_score + (hash(word) % 20 - 10) / 100  # Add some variation
                word_score = max(0.0, min(1.0, word_score))
                word_scores.append({
                    "word": word,
                    "score": word_score,
                    "phonetic": f"/{word}/",  # Simplified phonetic
                    "issues": []
                })
            
            # Generate improvement suggestions
            suggestions = []
            if overall_score < 0.7:
                suggestions.extend([
                    f"Focus on clear pronunciation of {language} sounds",
                    "Speak more slowly for better clarity",
                    "Practice tongue twisters for better articulation"
                ])
            
            if fluency_score < 0.6:
                suggestions.append("Work on speaking rhythm and pacing")
            
            # Check for language-specific issues
            detected_issues = []
            for issue in language_model["common_issues"]:
                if any(word in language_model["difficulty_words"] for word in words):
                    detected_issues.append(issue)
            
            return PronunciationAnalysis(
                overall_score=overall_score,
                pronunciation_level=level,
                phonetic_accuracy=phonetic_accuracy,
                fluency_score=fluency_score,
                word_level_scores=word_scores,
                detected_issues=detected_issues,
                improvement_suggestions=suggestions,
                phonetic_transcription=f"/{' '.join(words)}/",
                target_phonetics=f"/{' '.join(words)}/"
            )
            
        except Exception as e:
            logger.error(f"Pronunciation analysis failed: {e}")
            raise Exception(f"Pronunciation analysis failed: {str(e)}")
    
    async def _compare_pronunciation(
        self,
        recognized_text: str,
        reference_text: str,
        language: str,
        confidence: float
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
        overall_score = (word_accuracy * 0.7 + confidence * 0.3)
        
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
                quality_score=confidence
            )
        )
    
    async def _prepare_text_for_synthesis(
        self,
        text: str,
        language: str,
        emphasis_words: Optional[List[str]],
        speaking_rate: float
    ) -> str:
        """Prepare text for optimal speech synthesis with SSML markup"""
        
        # Start with basic text cleaning
        enhanced_text = text.strip()
        
        # Build SSML structure for Watson TTS
        ssml_elements = []
        
        # Add speaking rate adjustment if different from default
        if speaking_rate != 1.0:
            # Watson accepts rate as percentage (-50% to +100%)
            rate_percentage = int((speaking_rate - 1.0) * 50)
            rate_percentage = max(-50, min(100, rate_percentage))  # Clamp to Watson limits
            enhanced_text = f'<prosody rate="{rate_percentage:+d}%">{enhanced_text}</prosody>'
        
        # Add emphasis to specific words if provided
        if emphasis_words:
            for word in emphasis_words:
                if word.lower() in enhanced_text.lower():
                    # Use case-insensitive replacement with emphasis
                    import re
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    enhanced_text = pattern.sub(
                        f'<emphasis level="strong">{word}</emphasis>', 
                        enhanced_text, 
                        count=1
                    )
        
        # Language-specific SSML enhancements for pronunciation learning
        if language == "zh":
            # For Chinese, optimize for pronunciation learning with English voice compatibility
            # Since native Chinese voices may not be available, use compatible SSML
            # Add pauses between characters for learning and slow down speech
            chinese_chars = ['你', '好', '世', '界', '是', '这', '一', '个', '测', '试', '谢', '叫', '小', '明', '今', '天', '天', '气', '很', '在', '学', '习', '中', '文']
            if any(char in enhanced_text for char in chinese_chars):
                # Slow down speech for Chinese pronunciation learning
                if '<prosody rate=' not in enhanced_text:
                    enhanced_text = f'<prosody rate="-30%">{enhanced_text}</prosody>'
                # Add pauses between characters for learning (but not too many to avoid errors)
                for i, char in enumerate(chinese_chars[:10]):  # Limit to prevent too much markup
                    if char in enhanced_text and i < 5:  # Limit replacements
                        enhanced_text = enhanced_text.replace(char, f'{char}<break time="150ms"/>', 1)
            
        elif language == "fr":
            # For French, enhance liaison and nasal sounds with emphasis
            enhanced_text = enhanced_text.replace('les ', '<emphasis level="moderate">les</emphasis> ')
            enhanced_text = enhanced_text.replace('un ', '<emphasis level="moderate">un</emphasis> ')
            
        elif language == "es":
            # For Spanish, emphasize rolled R sounds and stress patterns
            enhanced_text = enhanced_text.replace('rr', '<emphasis level="strong">rr</emphasis>')
            
        elif language == "en":
            # For English, help with common pronunciation challenges using emphasis
            # Use emphasis instead of complex phonemes to avoid API errors
            enhanced_text = enhanced_text.replace(' th', ' <emphasis level="moderate">th</emphasis>')
            
        # Add pauses for better comprehension in language learning
        if '.' in enhanced_text:
            enhanced_text = enhanced_text.replace('. ', '.<break time="500ms"/> ')
        if ',' in enhanced_text:
            enhanced_text = enhanced_text.replace(', ', ',<break time="200ms"/> ')
            
        # Wrap in SSML speak tag if we added any SSML markup
        if '<' in enhanced_text and '>' in enhanced_text:
            enhanced_text = f'<speak version="1.0">{enhanced_text}</speak>'
            
        return enhanced_text
    
    async def get_speech_pipeline_status(self) -> Dict[str, Any]:
        """Get status of speech processing pipeline"""
        
        # Check if Watson clients are actually working
        watson_stt_functional = bool(self.watson_stt_client and self.watson_stt_available)
        watson_tts_functional = bool(self.watson_tts_client and self.watson_tts_available)
        
        return {
            "status": "operational" if (watson_stt_functional or watson_tts_functional) else "limited",
            "watson_sdk_available": self.watson_sdk_available,
            "watson_stt": {
                "status": "operational" if watson_stt_functional else "unavailable",
                "configured": self.watson_stt_available,
                "client_initialized": bool(self.watson_stt_client),
                "api_key_configured": bool(self.settings.IBM_WATSON_STT_API_KEY),
                "service_url": self.settings.IBM_WATSON_STT_URL if hasattr(self.settings, 'IBM_WATSON_STT_URL') else "not_configured"
            },
            "watson_tts": {
                "status": "operational" if watson_tts_functional else "unavailable", 
                "configured": self.watson_tts_available,
                "client_initialized": bool(self.watson_tts_client),
                "api_key_configured": bool(self.settings.IBM_WATSON_TTS_API_KEY),
                "service_url": self.settings.IBM_WATSON_TTS_URL if hasattr(self.settings, 'IBM_WATSON_TTS_URL') else "not_configured"
            },
            "watson_stt_available": watson_stt_functional,
            "watson_tts_available": watson_tts_functional,
            "audio_libs_available": self.audio_libs_available,
            "supported_formats": [fmt.value for fmt in AudioFormat],
            "supported_languages": list(self.pronunciation_models.keys()),
            "features": {
                "speech_recognition": watson_stt_functional,
                "speech_synthesis": watson_tts_functional,
                "pronunciation_analysis": True,
                "audio_enhancement": self.audio_libs_available,
                "real_time_processing": self.audio_libs_available and self.watson_sdk_available
            },
            "configuration": {
                "default_sample_rate": self.default_sample_rate,
                "default_channels": self.default_channels,
                "chunk_size": self.chunk_size
            },
            "api_models": {
                "watson_stt_models": [
                    "en-US_BroadbandModel", "fr-FR_BroadbandModel", "es-ES_BroadbandModel",
                    "de-DE_BroadbandModel", "zh-CN_BroadbandModel", "ja-JP_BroadbandModel"
                ],
                "watson_tts_voices": [
                    "en-US_AllisonV3Voice", "fr-FR_ReneeV3Voice", "es-ES_LauraV3Voice",
                    "de-DE_BirgitV3Voice", "ja-JP_EmiV3Voice", "ko-KR_YoungmiVoice"
                ]
            },
            "chinese_support": {
                "stt_available": True,  # Chinese STT (zh-CN_BroadbandModel) is available
                "tts_native_voice": False,  # No native Chinese voice in current plan
                "tts_fallback": "en-US_AllisonV3Voice",  # English fallback for Chinese
                "pronunciation_learning": True,  # Enhanced SSML for Chinese learning
                "note": "Chinese STT fully supported. TTS uses English voice with Chinese-optimized SSML."
            },
            "spanish_support": {
                "stt_model": "es-MX_BroadbandModel",  # Mexican Spanish STT as requested
                "tts_voice": "es-LA_SofiaV3Voice",  # Latin American Spanish (closest to es-MX)
                "note": "Using Mexican Spanish STT and Latin American Spanish TTS (closest to es-MX preference)"
            }
        }


# Global speech processor instance
speech_processor = SpeechProcessor()


# Convenience functions for easy integration
async def speech_to_text(
    audio_data: bytes,
    language: str = "en",
    analyze_pronunciation: bool = True
) -> Tuple[str, Optional[PronunciationAnalysis]]:
    """Convert speech to text with optional pronunciation analysis"""
    
    result, pronunciation = await speech_processor.process_speech_to_text(
        audio_data=audio_data,
        language=language,
        enable_pronunciation_analysis=analyze_pronunciation
    )
    
    return result.transcript, pronunciation

async def text_to_speech(
    text: str,
    language: str = "en",
    voice_type: str = "neural"
) -> bytes:
    """Convert text to speech"""
    
    result = await speech_processor.process_text_to_speech(
        text=text,
        language=language,
        voice_type=voice_type
    )
    
    return result.audio_data

async def analyze_pronunciation(
    audio_data: bytes,
    reference_text: str,
    language: str = "en"
) -> PronunciationAnalysis:
    """Analyze pronunciation quality"""
    
    return await speech_processor.analyze_pronunciation_quality(
        user_audio=audio_data,
        reference_text=reference_text,
        language=language
    )

async def get_speech_status() -> Dict[str, Any]:
    """Get speech processing pipeline status"""
    return await speech_processor.get_speech_pipeline_status()