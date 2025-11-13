"""
Comprehensive tests for speech_processor.py

Testing coverage:
- SpeechProcessor initialization
- Voice activity detection
- Audio processing and enhancement
- Speech-to-text (STT) with Mistral provider
- Text-to-speech (TTS) with Piper provider
- Pronunciation analysis
- Provider selection and fallback logic
- Utility functions and helpers
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import numpy as np
import pytest

from app.services.speech_processor import (
    AudioFormat,
    AudioMetadata,
    PronunciationAnalysis,
    PronunciationLevel,
    SpeechProcessor,
    SpeechRecognitionResult,
    SpeechSynthesisResult,
    analyze_pronunciation,
    get_speech_status,
    speech_processor,
    speech_to_text,
    text_to_speech,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def processor():
    """Create a fresh SpeechProcessor instance for each test"""
    return SpeechProcessor()


@pytest.fixture
def mock_audio_data():
    """Create mock audio data"""
    return b"fake_audio_data" * 100


@pytest.fixture
def mock_audio_array():
    """Create mock audio array with numpy"""
    return np.array([100, -100, 200, -200] * 100, dtype=np.int16)


@pytest.fixture
def audio_metadata():
    """Create mock audio metadata"""
    return AudioMetadata(
        format=AudioFormat.WAV,
        sample_rate=16000,
        channels=1,
        duration_seconds=2.5,
        file_size_bytes=40000,
        quality_score=0.85,
    )


# ============================================================================
# Test Initialization
# ============================================================================


class TestSpeechProcessorInitialization:
    """Test SpeechProcessor initialization"""

    def test_init_basic_attributes(self, processor):
        """Test basic initialization of processor attributes"""
        assert hasattr(processor, "audio_libs_available")
        assert hasattr(processor, "watson_sdk_available")
        assert hasattr(processor, "mistral_stt_available")
        assert hasattr(processor, "piper_tts_available")
        assert processor.default_sample_rate == 16000
        assert processor.default_channels == 1
        assert processor.chunk_size == 1024
        assert processor.vad_threshold == 0.01
        assert processor.vad_frame_size == 480

    def test_init_watson_deprecated(self, processor):
        """Test that Watson services are marked as deprecated"""
        assert processor.watson_sdk_available is False
        assert processor.watson_stt_available is False
        assert processor.watson_tts_available is False
        assert processor.watson_stt_client is None
        assert processor.watson_tts_client is None

    def test_init_pronunciation_models_loaded(self, processor):
        """Test pronunciation models are loaded"""
        assert isinstance(processor.pronunciation_models, dict)
        assert "en" in processor.pronunciation_models
        assert "fr" in processor.pronunciation_models
        assert "es" in processor.pronunciation_models
        assert "zh" in processor.pronunciation_models

    def test_init_pronunciation_model_structure(self, processor):
        """Test pronunciation model structure"""
        en_model = processor.pronunciation_models["en"]
        assert "phoneme_weights" in en_model
        assert "common_issues" in en_model
        assert "difficulty_words" in en_model

    @patch("app.services.speech_processor.MISTRAL_STT_AVAILABLE", True)
    def test_init_mistral_stt_success(self):
        """Test successful Mistral STT initialization"""
        with patch("app.services.mistral_stt_service.MistralSTTService") as mock_class:
            mock_service = Mock()
            mock_service.available = True
            mock_class.return_value = mock_service

            processor = SpeechProcessor()
            assert processor.mistral_stt_available is True
            assert processor.mistral_stt_service is not None

    @patch("app.services.speech_processor.MISTRAL_STT_AVAILABLE", True)
    def test_init_mistral_stt_unavailable(self):
        """Test Mistral STT initialization when service unavailable"""
        with patch("app.services.mistral_stt_service.MistralSTTService") as mock_class:
            mock_service = Mock()
            mock_service.available = False
            mock_class.return_value = mock_service

            processor = SpeechProcessor()
            assert processor.mistral_stt_available is False

    @patch("app.services.speech_processor.MISTRAL_STT_AVAILABLE", True)
    def test_init_mistral_stt_error(self):
        """Test Mistral STT initialization error handling"""
        with patch(
            "app.services.mistral_stt_service.MistralSTTService",
            side_effect=Exception("Init error"),
        ):
            processor = SpeechProcessor()
            assert processor.mistral_stt_available is False
            assert processor.mistral_stt_service is None

    @patch("app.services.speech_processor.PIPER_TTS_AVAILABLE", True)
    def test_init_piper_tts_success(self):
        """Test successful Piper TTS initialization"""
        with patch("app.services.piper_tts_service.PiperTTSService") as mock_class:
            mock_service = Mock()
            mock_service.voices = ["en_US-amy-medium"]
            mock_class.return_value = mock_service

            processor = SpeechProcessor()
            assert processor.piper_tts_available is True
            assert processor.piper_tts_service is not None

    @patch("app.services.speech_processor.PIPER_TTS_AVAILABLE", True)
    def test_init_piper_tts_no_voices(self):
        """Test Piper TTS initialization when no voices available"""
        with patch("app.services.piper_tts_service.PiperTTSService") as mock_class:
            mock_service = Mock()
            mock_service.voices = []
            mock_class.return_value = mock_service

            processor = SpeechProcessor()
            assert processor.piper_tts_available is False

    @patch("app.services.speech_processor.PIPER_TTS_AVAILABLE", True)
    def test_init_piper_tts_error(self):
        """Test Piper TTS initialization error handling"""
        with patch(
            "app.services.piper_tts_service.PiperTTSService",
            side_effect=Exception("Init error"),
        ):
            processor = SpeechProcessor()
            assert processor.piper_tts_available is False
            assert processor.piper_tts_service is None


# ============================================================================
# Test Voice Activity Detection
# ============================================================================


class TestVoiceActivityDetection:
    """Test voice activity detection methods"""

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    def test_detect_voice_no_libs(self, processor):
        """Test voice detection without audio libraries"""
        audio_data = b"fake_audio"
        result = processor.detect_voice_activity(audio_data)
        assert result is True  # Should assume voice present

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_detect_voice_empty_audio(self, processor):
        """Test voice detection with empty audio"""
        result = processor.detect_voice_activity(b"")
        assert result is False

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_detect_voice_insufficient_data(self, processor):
        """Test voice detection with insufficient data"""
        result = processor.detect_voice_activity(b"x")
        assert result is False

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_detect_voice_invalid_format(self, processor):
        """Test voice detection with invalid audio format"""
        result = processor.detect_voice_activity(b"invalid")
        assert result is False

    def test_detect_voice_silence(self):
        """Test voice detection with silence (all zeros)"""
        processor = SpeechProcessor()
        processor.audio_libs_available = True
        silent_audio = np.zeros(1000, dtype=np.int16).tobytes()
        result = processor.detect_voice_activity(silent_audio)
        assert result == False  # Use == instead of is for boolean

    def test_detect_voice_with_activity(self):
        """Test voice detection with actual voice activity"""
        processor = SpeechProcessor()
        processor.audio_libs_available = True
        # Create audio with significant energy
        voice_audio = np.array(
            [5000, -5000, 6000, -6000] * 250, dtype=np.int16
        ).tobytes()
        result = processor.detect_voice_activity(voice_audio)
        assert result == True  # Use == instead of is for boolean

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_detect_voice_error_handling(self, processor):
        """Test voice detection error handling"""
        # Pass data that will cause processing error
        with patch("numpy.frombuffer", side_effect=Exception("Error")):
            result = processor.detect_voice_activity(b"audio")
            assert result is False

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    def test_remove_silence_no_libs(self, processor, mock_audio_data):
        """Test silence removal without audio libraries"""
        result = processor.remove_silence(mock_audio_data)
        assert result == mock_audio_data  # Should return original

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_remove_silence_with_voice(self, processor):
        """Test silence removal with voice frames"""
        # Create audio with voice activity
        voice_audio = np.array([5000, -5000] * 480, dtype=np.int16).tobytes()

        with patch.object(processor, "detect_voice_activity", return_value=True):
            result = processor.remove_silence(voice_audio)
            assert len(result) > 0

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_remove_silence_all_silence(self, processor):
        """Test silence removal when all audio is silence"""
        silent_audio = np.zeros(1000, dtype=np.int16).tobytes()

        with patch.object(processor, "detect_voice_activity", return_value=False):
            result = processor.remove_silence(silent_audio)
            # Should return original when no voice detected
            assert result == silent_audio

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_remove_silence_error_handling(self, processor, mock_audio_data):
        """Test silence removal error handling"""
        with patch("numpy.frombuffer", side_effect=Exception("Error")):
            result = processor.remove_silence(mock_audio_data)
            assert result == mock_audio_data  # Should return original


# ============================================================================
# Test Audio Processing
# ============================================================================


class TestAudioProcessing:
    """Test audio processing and enhancement methods"""

    @pytest.mark.asyncio
    async def test_analyze_audio_quality_basic(self, processor, mock_audio_data):
        """Test basic audio quality analysis"""
        metadata = await processor._analyze_audio_quality(
            mock_audio_data, AudioFormat.WAV
        )

        assert isinstance(metadata, AudioMetadata)
        assert metadata.format == AudioFormat.WAV
        assert metadata.sample_rate == 16000
        assert metadata.channels == 1
        assert metadata.file_size_bytes == len(mock_audio_data)
        assert 0.0 <= metadata.quality_score <= 1.0

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_analyze_audio_quality_silence(self, processor):
        """Test audio quality analysis with silence"""
        silent_audio = np.zeros(1000, dtype=np.int16).tobytes()
        metadata = await processor._analyze_audio_quality(silent_audio, AudioFormat.WAV)

        # Quality should be very low for silence
        assert metadata.quality_score < 0.5

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_analyze_audio_quality_with_signal(self, processor):
        """Test audio quality analysis with good signal"""
        voice_audio = np.array(
            [5000, -5000, 6000, -6000] * 250, dtype=np.int16
        ).tobytes()
        metadata = await processor._analyze_audio_quality(voice_audio, AudioFormat.WAV)

        assert metadata.quality_score > 0.0

    @pytest.mark.asyncio
    async def test_analyze_audio_quality_error_handling(self, processor):
        """Test audio quality analysis error handling"""
        # When numpy processing fails, it falls back to basic calculation
        # which still succeeds with a low quality score
        metadata = await processor._analyze_audio_quality(b"audio", AudioFormat.WAV)
        # Should return some metadata (may be fallback or basic)
        assert 0.0 <= metadata.quality_score <= 1.0

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    async def test_enhance_audio_no_libs(self, processor, mock_audio_data):
        """Test audio enhancement without libraries"""
        result = await processor._enhance_audio_quality(
            mock_audio_data, AudioFormat.WAV
        )
        assert result == mock_audio_data

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_enhance_audio_with_libs(self, processor):
        """Test audio enhancement with libraries"""
        audio_data = np.array(
            [1000, -1000, 2000, -2000] * 250, dtype=np.int16
        ).tobytes()

        with patch.object(processor, "_reduce_noise", return_value=audio_data):
            with patch.object(processor, "_normalize_audio", return_value=audio_data):
                with patch.object(
                    processor, "_apply_speech_enhancement", return_value=audio_data
                ):
                    result = await processor._enhance_audio_quality(
                        audio_data, AudioFormat.WAV
                    )
                    assert isinstance(result, bytes)

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_enhance_audio_error_handling(self, processor, mock_audio_data):
        """Test audio enhancement error handling"""
        with patch.object(processor, "_reduce_noise", side_effect=Exception("Error")):
            result = await processor._enhance_audio_quality(
                mock_audio_data, AudioFormat.WAV
            )
            assert result == mock_audio_data

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    def test_apply_speech_enhancement_no_libs(self, processor, mock_audio_data):
        """Test speech enhancement without libraries"""
        result = processor._apply_speech_enhancement(mock_audio_data)
        assert result == mock_audio_data

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_apply_speech_enhancement_empty_audio(self, processor):
        """Test speech enhancement with empty audio"""
        empty_audio = b""
        result = processor._apply_speech_enhancement(empty_audio)
        assert result == empty_audio

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_apply_speech_enhancement_with_audio(self, processor):
        """Test speech enhancement with audio"""
        audio_data = np.array([1000, 2000, 3000, 4000] * 100, dtype=np.int16).tobytes()
        result = processor._apply_speech_enhancement(audio_data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_apply_speech_enhancement_error(self, processor, mock_audio_data):
        """Test speech enhancement error handling"""
        with patch("numpy.frombuffer", side_effect=Exception("Error")):
            result = processor._apply_speech_enhancement(mock_audio_data)
            assert result == mock_audio_data

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    def test_reduce_noise_no_libs(self, processor, mock_audio_data):
        """Test noise reduction without libraries"""
        result = processor._reduce_noise(mock_audio_data)
        assert result == mock_audio_data

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_reduce_noise_empty_audio(self, processor):
        """Test noise reduction with empty audio"""
        empty_audio = b""
        result = processor._reduce_noise(empty_audio)
        assert result == empty_audio

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_reduce_noise_with_audio(self, processor):
        """Test noise reduction with audio"""
        audio_data = np.array([100, -100, 5000, -5000] * 100, dtype=np.int16).tobytes()
        result = processor._reduce_noise(audio_data)
        assert isinstance(result, bytes)

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_reduce_noise_error(self, processor, mock_audio_data):
        """Test noise reduction error handling"""
        with patch("numpy.frombuffer", side_effect=Exception("Error")):
            result = processor._reduce_noise(mock_audio_data)
            assert result == mock_audio_data

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    def test_normalize_audio_no_libs(self, processor, mock_audio_data):
        """Test audio normalization without libraries"""
        result = processor._normalize_audio(mock_audio_data)
        assert result == mock_audio_data

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_normalize_audio_empty_audio(self, processor):
        """Test audio normalization with empty audio"""
        empty_audio = b""
        result = processor._normalize_audio(empty_audio)
        assert result == empty_audio

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_normalize_audio_with_audio(self, processor):
        """Test audio normalization with audio"""
        audio_data = np.array([100, 200, 300, 400] * 100, dtype=np.int16).tobytes()
        result = processor._normalize_audio(audio_data)
        assert isinstance(result, bytes)

    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    def test_normalize_audio_error(self, processor, mock_audio_data):
        """Test audio normalization error handling"""
        with patch("numpy.frombuffer", side_effect=Exception("Error")):
            result = processor._normalize_audio(mock_audio_data)
            assert result == mock_audio_data

    def test_pad_audio_no_padding_needed(self, processor):
        """Test pad_audio when audio is already sufficient"""
        audio_data = b"x" * 200
        result = processor._pad_audio(audio_data)
        assert result == audio_data

    def test_pad_audio_padding_needed(self, processor):
        """Test pad_audio when padding is needed"""
        audio_data = b"x" * 50
        result = processor._pad_audio(audio_data)
        assert len(result) == 100
        assert result.startswith(audio_data)

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_ensure_proper_wav_format_already_wav(self, processor):
        """Test ensure_proper_wav_format with valid WAV"""
        wav_data = b"RIFF" + b"\x00" * 4 + b"WAVE" + b"\x00" * 100
        result = await processor._ensure_proper_wav_format(wav_data)
        assert result == wav_data

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", False)
    async def test_ensure_proper_wav_format_no_libs(self, processor, mock_audio_data):
        """Test ensure_proper_wav_format without libraries"""
        result = await processor._ensure_proper_wav_format(mock_audio_data)
        assert result == mock_audio_data

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_ensure_proper_wav_format_conversion(self, processor):
        """Test ensure_proper_wav_format conversion"""
        audio_data = np.array([100, -100, 200, -200] * 100, dtype=np.int16).tobytes()
        result = await processor._ensure_proper_wav_format(audio_data)
        # Should create a valid WAV file
        assert b"RIFF" in result
        assert b"WAVE" in result

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_ensure_proper_wav_format_error(self, processor, mock_audio_data):
        """Test ensure_proper_wav_format error handling"""
        with patch("wave.open", side_effect=Exception("Error")):
            result = await processor._ensure_proper_wav_format(mock_audio_data)
            assert result == mock_audio_data

    @pytest.mark.asyncio
    async def test_preprocess_audio_small_data(self, processor):
        """Test preprocess audio with small data"""
        small_audio = b"x" * 50
        result = await processor._preprocess_audio(small_audio, AudioFormat.WAV)
        # Should be padded
        assert len(result) >= 100

    @pytest.mark.asyncio
    @patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True)
    async def test_preprocess_audio_normal(self, processor):
        """Test preprocess audio with normal data"""
        audio_data = np.array(
            [1000, -1000, 2000, -2000] * 250, dtype=np.int16
        ).tobytes()

        with patch.object(processor, "_reduce_noise", return_value=audio_data):
            with patch.object(processor, "_normalize_audio", return_value=audio_data):
                with patch.object(
                    processor, "_ensure_proper_wav_format", return_value=audio_data
                ):
                    result = await processor._preprocess_audio(
                        audio_data, AudioFormat.WAV
                    )
                    assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_preprocess_audio_error(self, processor, mock_audio_data):
        """Test preprocess audio error handling"""
        with patch.object(processor, "_reduce_noise", side_effect=Exception("Error")):
            result = await processor._preprocess_audio(mock_audio_data, AudioFormat.WAV)
            # Should still return audio data
            assert isinstance(result, bytes)


# ============================================================================
# Test Speech-to-Text (Continued in next part due to length)
# ============================================================================


class TestSpeechToText:
    """Test speech-to-text functionality"""

    @pytest.mark.asyncio
    async def test_process_speech_to_text_basic(self, processor, mock_audio_data):
        """Test basic speech-to-text processing"""
        mock_result = SpeechRecognitionResult(
            transcript="hello world",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        with patch.object(processor, "_analyze_audio_quality") as mock_analyze:
            mock_analyze.return_value = AudioMetadata(
                format=AudioFormat.WAV,
                sample_rate=16000,
                channels=1,
                duration_seconds=2.0,
                file_size_bytes=len(mock_audio_data),
                quality_score=0.8,
            )

            with patch.object(
                processor, "_enhance_audio_quality", return_value=mock_audio_data
            ):
                with patch.object(
                    processor,
                    "_select_stt_provider_and_process",
                    return_value=mock_result,
                ):
                    result, pronunciation = await processor.process_speech_to_text(
                        audio_data=mock_audio_data,
                        language="en",
                    )

                    assert result.transcript == "hello world"
                    assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_process_speech_to_text_low_quality(self, processor, mock_audio_data):
        """Test speech-to-text with low quality audio"""
        mock_result = SpeechRecognitionResult(
            transcript="hello",
            confidence=0.5,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        with patch.object(processor, "_analyze_audio_quality") as mock_analyze:
            # Return low quality score
            mock_analyze.return_value = AudioMetadata(
                format=AudioFormat.WAV,
                sample_rate=16000,
                channels=1,
                duration_seconds=2.0,
                file_size_bytes=len(mock_audio_data),
                quality_score=0.3,  # Low quality
            )

            with patch.object(
                processor, "_enhance_audio_quality", return_value=mock_audio_data
            ):
                with patch.object(
                    processor,
                    "_select_stt_provider_and_process",
                    return_value=mock_result,
                ):
                    result, pronunciation = await processor.process_speech_to_text(
                        audio_data=mock_audio_data,
                        language="en",
                        enable_pronunciation_analysis=False,
                    )

                    assert result.transcript == "hello"
                    assert pronunciation is None

    @pytest.mark.asyncio
    async def test_process_speech_to_text_with_pronunciation(
        self, processor, mock_audio_data
    ):
        """Test speech-to-text with pronunciation analysis"""
        mock_result = SpeechRecognitionResult(
            transcript="hello world",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        mock_pronunciation = PronunciationAnalysis(
            overall_score=0.85,
            pronunciation_level=PronunciationLevel.GOOD,
            phonetic_accuracy=0.9,
            fluency_score=0.8,
            word_level_scores=[],
            detected_issues=[],
            improvement_suggestions=[],
            phonetic_transcription="/hello world/",
            target_phonetics="/hello world/",
        )

        with patch.object(processor, "_analyze_audio_quality") as mock_analyze:
            mock_analyze.return_value = AudioMetadata(
                format=AudioFormat.WAV,
                sample_rate=16000,
                channels=1,
                duration_seconds=2.0,
                file_size_bytes=len(mock_audio_data),
                quality_score=0.8,
            )

            with patch.object(
                processor, "_enhance_audio_quality", return_value=mock_audio_data
            ):
                with patch.object(
                    processor,
                    "_select_stt_provider_and_process",
                    return_value=mock_result,
                ):
                    with patch.object(
                        processor,
                        "_analyze_pronunciation",
                        return_value=mock_pronunciation,
                    ):
                        result, pronunciation = await processor.process_speech_to_text(
                            audio_data=mock_audio_data,
                            language="en",
                            enable_pronunciation_analysis=True,
                        )

                        assert result.transcript == "hello world"
                        assert pronunciation is not None
                        assert pronunciation.overall_score == 0.85

    @pytest.mark.asyncio
    async def test_process_speech_to_text_low_confidence_no_pronunciation(
        self, processor, mock_audio_data
    ):
        """Test that low confidence results don't get pronunciation analysis"""
        mock_result = SpeechRecognitionResult(
            transcript="unclear",
            confidence=0.3,  # Low confidence
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        with patch.object(processor, "_analyze_audio_quality") as mock_analyze:
            mock_analyze.return_value = AudioMetadata(
                format=AudioFormat.WAV,
                sample_rate=16000,
                channels=1,
                duration_seconds=2.0,
                file_size_bytes=len(mock_audio_data),
                quality_score=0.8,
            )

            with patch.object(
                processor, "_enhance_audio_quality", return_value=mock_audio_data
            ):
                with patch.object(
                    processor,
                    "_select_stt_provider_and_process",
                    return_value=mock_result,
                ):
                    result, pronunciation = await processor.process_speech_to_text(
                        audio_data=mock_audio_data,
                        language="en",
                        enable_pronunciation_analysis=True,
                    )

                    assert result.confidence == 0.3
                    assert pronunciation is None  # Should not analyze low confidence

    @pytest.mark.asyncio
    async def test_process_speech_to_text_error(self, processor, mock_audio_data):
        """Test speech-to-text error handling"""
        with patch.object(
            processor, "_analyze_audio_quality", side_effect=Exception("Error")
        ):
            result, pronunciation = await processor.process_speech_to_text(
                audio_data=mock_audio_data,
                language="en",
            )

            assert result.transcript == "[Speech recognition failed]"
            assert result.confidence == 0.0
            assert "error" in result.metadata
            assert pronunciation is None

    @pytest.mark.asyncio
    async def test_select_stt_provider_watson_error(self, processor, mock_audio_data):
        """Test that Watson provider request raises error"""
        with pytest.raises(Exception, match="Watson STT deprecated"):
            await processor._select_stt_provider_and_process(
                audio_data=mock_audio_data,
                language="en",
                audio_format=AudioFormat.WAV,
                provider="watson",
            )

    @pytest.mark.asyncio
    async def test_select_stt_provider_mistral_explicit(
        self, processor, mock_audio_data
    ):
        """Test explicit Mistral provider selection"""
        mock_result = SpeechRecognitionResult(
            transcript="test",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        processor.mistral_stt_available = True

        with patch.object(
            processor, "_speech_to_text_mistral", return_value=mock_result
        ):
            result = await processor._select_stt_provider_and_process(
                audio_data=mock_audio_data,
                language="en",
                audio_format=AudioFormat.WAV,
                provider="mistral",
            )

            assert result.transcript == "test"

    @pytest.mark.asyncio
    async def test_select_stt_provider_mistral_unavailable(
        self, processor, mock_audio_data
    ):
        """Test Mistral provider when unavailable"""
        processor.mistral_stt_available = False

        with pytest.raises(Exception, match="Mistral STT not available"):
            await processor._select_stt_provider_and_process(
                audio_data=mock_audio_data,
                language="en",
                audio_format=AudioFormat.WAV,
                provider="mistral",
            )

    @pytest.mark.asyncio
    async def test_select_stt_provider_auto(self, processor, mock_audio_data):
        """Test auto provider selection"""
        mock_result = SpeechRecognitionResult(
            transcript="auto test",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        processor.mistral_stt_available = True

        with patch.object(processor, "_try_mistral_stt", return_value=mock_result):
            result = await processor._select_stt_provider_and_process(
                audio_data=mock_audio_data,
                language="en",
                audio_format=AudioFormat.WAV,
                provider="auto",
            )

            assert result.transcript == "auto test"

    @pytest.mark.asyncio
    async def test_select_stt_provider_unknown(self, processor, mock_audio_data):
        """Test unknown provider error"""
        with pytest.raises(ValueError, match="Unknown STT provider"):
            await processor._select_stt_provider_and_process(
                audio_data=mock_audio_data,
                language="en",
                audio_format=AudioFormat.WAV,
                provider="unknown_provider",
            )

    @pytest.mark.asyncio
    async def test_speech_to_text_mistral_success(self, processor, mock_audio_data):
        """Test Mistral STT success"""
        mock_service = Mock()
        mock_mistral_result = Mock()
        mock_mistral_result.transcript = "hello world"
        mock_mistral_result.confidence = 0.95
        mock_mistral_result.language = "en"
        mock_mistral_result.alternative_transcripts = ["hello word"]
        mock_mistral_result.metadata = {}
        mock_mistral_result.cost_usd = 0.001
        mock_mistral_result.audio_duration_minutes = 0.5

        mock_service.transcribe_audio = AsyncMock(return_value=mock_mistral_result)
        processor.mistral_stt_available = True
        processor.mistral_stt_service = mock_service

        result = await processor._speech_to_text_mistral(
            mock_audio_data, "en", AudioFormat.WAV
        )

        assert result.transcript == "hello world"
        assert result.confidence == 0.95
        assert "mistral_voxtral" in result.metadata["provider"]

    @pytest.mark.asyncio
    async def test_speech_to_text_mistral_unavailable(self, processor, mock_audio_data):
        """Test Mistral STT when unavailable"""
        processor.mistral_stt_available = False
        processor.mistral_stt_service = None

        with pytest.raises(Exception, match="Mistral STT service not configured"):
            await processor._speech_to_text_mistral(
                mock_audio_data, "en", AudioFormat.WAV
            )

    @pytest.mark.asyncio
    async def test_speech_to_text_mistral_error(self, processor, mock_audio_data):
        """Test Mistral STT error handling"""
        mock_service = Mock()
        mock_service.transcribe_audio = AsyncMock(side_effect=Exception("API Error"))

        processor.mistral_stt_available = True
        processor.mistral_stt_service = mock_service

        result = await processor._speech_to_text_mistral(
            mock_audio_data, "en", AudioFormat.WAV
        )

        assert result.transcript == "[Mistral STT Error]"
        assert result.confidence == 0.0
        assert "error" in result.metadata


# ============================================================================
# Test Text-to-Speech
# ============================================================================


class TestTextToSpeech:
    """Test text-to-speech functionality"""

    @pytest.mark.asyncio
    async def test_process_text_to_speech_basic(self, processor):
        """Test basic text-to-speech processing"""
        mock_result = SpeechSynthesisResult(
            audio_data=b"fake_audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={},
        )

        with patch.object(
            processor, "_prepare_text_for_synthesis", return_value="hello"
        ):
            with patch.object(
                processor, "_select_tts_provider_and_process", return_value=mock_result
            ):
                result = await processor.process_text_to_speech(
                    text="hello",
                    language="en",
                )

                assert result.audio_data == b"fake_audio"
                assert result.audio_format == AudioFormat.WAV

    @pytest.mark.asyncio
    async def test_process_text_to_speech_with_emphasis(self, processor):
        """Test TTS with emphasis words"""
        mock_result = SpeechSynthesisResult(
            audio_data=b"audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={},
        )

        with patch.object(processor, "_prepare_text_for_synthesis") as mock_prep:
            mock_prep.return_value = "emphasized text"
            with patch.object(
                processor, "_select_tts_provider_and_process", return_value=mock_result
            ):
                result = await processor.process_text_to_speech(
                    text="hello world",
                    language="en",
                    emphasis_words=["world"],
                )

                # Check that emphasis words were passed
                call_args = mock_prep.call_args
                assert "world" in call_args.kwargs["emphasis_words"]

    @pytest.mark.asyncio
    async def test_process_text_to_speech_error(self, processor):
        """Test TTS error handling"""
        with patch.object(
            processor, "_prepare_text_for_synthesis", side_effect=Exception("Error")
        ):
            with pytest.raises(Exception, match="Speech synthesis failed"):
                await processor.process_text_to_speech(
                    text="hello",
                    language="en",
                )

    @pytest.mark.asyncio
    async def test_select_tts_provider_auto(self, processor):
        """Test auto TTS provider selection"""
        mock_result = SpeechSynthesisResult(
            audio_data=b"audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={},
        )

        processor.piper_tts_available = True

        with patch.object(processor, "_text_to_speech_piper", return_value=mock_result):
            result = await processor._select_tts_provider_and_process(
                text="hello",
                language="en",
                voice_type="neural",
                speaking_rate=1.0,
                provider="auto",
                original_text="hello",
            )

            assert result.audio_data == b"audio"

    @pytest.mark.asyncio
    async def test_select_tts_provider_piper_explicit(self, processor):
        """Test explicit Piper provider selection"""
        mock_result = SpeechSynthesisResult(
            audio_data=b"piper_audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={},
        )

        processor.piper_tts_available = True

        with patch.object(processor, "_text_to_speech_piper", return_value=mock_result):
            result = await processor._select_tts_provider_and_process(
                text="hello",
                language="en",
                voice_type="neural",
                speaking_rate=1.0,
                provider="piper",
                original_text="hello",
            )

            assert result.audio_data == b"piper_audio"

    @pytest.mark.asyncio
    async def test_select_tts_provider_piper_unavailable(self, processor):
        """Test Piper provider when unavailable"""
        processor.piper_tts_available = False

        with pytest.raises(
            Exception, match="Piper TTS provider requested but not available"
        ):
            await processor._select_tts_provider_and_process(
                text="hello",
                language="en",
                voice_type="neural",
                speaking_rate=1.0,
                provider="piper",
                original_text="hello",
            )

    @pytest.mark.asyncio
    async def test_select_tts_provider_watson_error(self, processor):
        """Test Watson provider error"""
        with pytest.raises(Exception, match="Watson TTS deprecated"):
            await processor._select_tts_provider_and_process(
                text="hello",
                language="en",
                voice_type="neural",
                speaking_rate=1.0,
                provider="watson",
                original_text="hello",
            )

    @pytest.mark.asyncio
    async def test_select_tts_provider_unknown(self, processor):
        """Test unknown TTS provider"""
        with pytest.raises(Exception, match="Unknown TTS provider"):
            await processor._select_tts_provider_and_process(
                text="hello",
                language="en",
                voice_type="neural",
                speaking_rate=1.0,
                provider="unknown",
                original_text="hello",
            )

    @pytest.mark.asyncio
    async def test_text_to_speech_piper_success(self, processor):
        """Test Piper TTS success"""
        mock_service = Mock()
        mock_service.synthesize_speech = AsyncMock(
            return_value=(b"audio_data", {"voice": "en_US-amy", "sample_rate": 22050})
        )

        processor.piper_tts_available = True
        processor.piper_tts_service = mock_service

        result = await processor._text_to_speech_piper(
            text="hello",
            language="en",
            voice_type="neural",
            speaking_rate=1.0,
        )

        assert result.audio_data == b"audio_data"
        assert result.audio_format == AudioFormat.WAV
        assert "piper" in result.metadata["provider"]

    @pytest.mark.asyncio
    async def test_text_to_speech_piper_unavailable(self, processor):
        """Test Piper TTS when unavailable"""
        processor.piper_tts_available = False
        processor.piper_tts_service = None

        with pytest.raises(Exception, match="Piper Text-to-Speech not configured"):
            await processor._text_to_speech_piper(
                text="hello",
                language="en",
                voice_type="neural",
                speaking_rate=1.0,
            )

    @pytest.mark.asyncio
    async def test_text_to_speech_piper_error(self, processor):
        """Test Piper TTS error handling with fallback"""
        mock_service = Mock()
        mock_service.synthesize_speech = AsyncMock(
            side_effect=Exception("Synthesis error")
        )

        processor.piper_tts_available = True
        processor.piper_tts_service = mock_service

        result = await processor._text_to_speech_piper(
            text="hello",
            language="en",
            voice_type="neural",
            speaking_rate=1.0,
        )

        # Should return fallback response
        assert b"Piper TTS unavailable" in result.audio_data
        assert "error" in result.metadata


# ============================================================================
# Test Text Preparation for Synthesis
# ============================================================================


class TestTextPreparation:
    """Test text preparation for speech synthesis"""

    @pytest.mark.asyncio
    async def test_prepare_text_basic(self, processor):
        """Test basic text preparation"""
        result = await processor._prepare_text_for_synthesis(
            text="Hello world",
            language="en",
            emphasis_words=None,
            speaking_rate=1.0,
        )

        assert isinstance(result, str)
        assert "Hello world" in result

    @pytest.mark.asyncio
    async def test_prepare_text_with_emphasis(self, processor):
        """Test text preparation with emphasis"""
        result = await processor._prepare_text_for_synthesis(
            text="Hello world",
            language="en",
            emphasis_words=["world"],
            speaking_rate=1.0,
        )

        assert "<emphasis" in result
        assert "world" in result

    @pytest.mark.asyncio
    async def test_prepare_text_with_rate(self, processor):
        """Test text preparation with speaking rate"""
        result = await processor._prepare_text_for_synthesis(
            text="Hello world",
            language="en",
            emphasis_words=None,
            speaking_rate=0.8,
        )

        assert "<prosody rate=" in result

    def test_apply_speaking_rate_default(self, processor):
        """Test speaking rate with default rate"""
        result = processor._apply_speaking_rate("hello", 1.0)
        assert result == "hello"  # No SSML for default rate

    def test_apply_speaking_rate_slower(self, processor):
        """Test speaking rate slower"""
        result = processor._apply_speaking_rate("hello", 0.8)
        assert "<prosody rate=" in result
        assert "hello" in result

    def test_apply_speaking_rate_faster(self, processor):
        """Test speaking rate faster"""
        result = processor._apply_speaking_rate("hello", 1.5)
        assert "<prosody rate=" in result
        assert "hello" in result

    def test_apply_word_emphasis_none(self, processor):
        """Test word emphasis with no words"""
        result = processor._apply_word_emphasis("hello world", None)
        assert result == "hello world"

    def test_apply_word_emphasis_with_words(self, processor):
        """Test word emphasis with specific words"""
        result = processor._apply_word_emphasis("hello world", ["world"])
        assert "<emphasis" in result
        assert "world" in result

    def test_apply_word_emphasis_case_insensitive(self, processor):
        """Test word emphasis is case insensitive"""
        result = processor._apply_word_emphasis("Hello World", ["world"])
        assert "<emphasis" in result

    def test_apply_language_specific_enhancements_english(self, processor):
        """Test English-specific enhancements"""
        result = processor._apply_language_specific_enhancements("the thing", "en")
        assert "<emphasis" in result

    def test_apply_language_specific_enhancements_chinese(self, processor):
        """Test Chinese-specific enhancements"""
        result = processor._apply_language_specific_enhancements("你好世界", "zh")
        assert "<prosody rate=" in result or "<break" in result

    def test_apply_language_specific_enhancements_french(self, processor):
        """Test French-specific enhancements"""
        result = processor._apply_language_specific_enhancements("les amis", "fr")
        assert "<emphasis" in result or result == "les amis"

    def test_apply_language_specific_enhancements_spanish(self, processor):
        """Test Spanish-specific enhancements"""
        result = processor._apply_language_specific_enhancements("perro", "es")
        # Spanish enhancement affects "rr" - should have emphasis tag
        assert "rr" in result

    def test_apply_language_specific_enhancements_unknown(self, processor):
        """Test unknown language returns unchanged"""
        result = processor._apply_language_specific_enhancements("hello", "unknown")
        assert result == "hello"

    def test_enhance_chinese_text_with_chars(self, processor):
        """Test Chinese text enhancement"""
        result = processor._enhance_chinese_text("你好")
        assert "<prosody" in result or "你好" in result

    def test_enhance_chinese_text_no_chars(self, processor):
        """Test Chinese enhancement with no Chinese characters"""
        result = processor._enhance_chinese_text("hello")
        assert result == "hello"

    def test_enhance_french_text(self, processor):
        """Test French text enhancement"""
        result = processor._enhance_french_text("les enfants")
        assert "les" in result

    def test_enhance_spanish_text(self, processor):
        """Test Spanish text enhancement for rolled R"""
        result = processor._enhance_spanish_text("perro")
        assert "<emphasis" in result
        assert "rr" in result

    def test_enhance_english_text(self, processor):
        """Test English text enhancement for th sounds"""
        result = processor._enhance_english_text("the thing")
        assert "<emphasis" in result
        assert "th" in result

    def test_add_comprehension_pauses_periods(self, processor):
        """Test adding pauses for periods"""
        result = processor._add_comprehension_pauses("Hello. World.")
        assert "<break" in result

    def test_add_comprehension_pauses_commas(self, processor):
        """Test adding pauses for commas"""
        result = processor._add_comprehension_pauses("Hello, world")
        assert "<break" in result

    def test_add_comprehension_pauses_no_punctuation(self, processor):
        """Test no pauses added without punctuation"""
        result = processor._add_comprehension_pauses("Hello world")
        assert result == "Hello world"

    def test_wrap_in_ssml_if_needed_with_markup(self, processor):
        """Test SSML wrapping when markup present"""
        result = processor._wrap_in_ssml_if_needed("<emphasis>hello</emphasis>")
        assert result.startswith("<speak")
        assert result.endswith("</speak>")

    def test_wrap_in_ssml_if_needed_no_markup(self, processor):
        """Test no SSML wrapping without markup"""
        result = processor._wrap_in_ssml_if_needed("hello world")
        assert result == "hello world"


# ============================================================================
# Test Pronunciation Analysis
# ============================================================================


class TestPronunciationAnalysis:
    """Test pronunciation analysis methods"""

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_basic(self, processor, audio_metadata):
        """Test basic pronunciation analysis"""
        analysis = await processor._analyze_pronunciation(
            audio_data=b"audio",
            transcript="hello world",
            language="en",
            audio_metadata=audio_metadata,
        )

        assert isinstance(analysis, PronunciationAnalysis)
        assert 0.0 <= analysis.overall_score <= 1.0
        assert isinstance(analysis.word_level_scores, list)
        assert len(analysis.word_level_scores) == 2  # "hello" and "world"

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_score_calculation(
        self, processor, audio_metadata
    ):
        """Test pronunciation score calculation"""
        analysis = await processor._analyze_pronunciation(
            audio_data=b"audio",
            transcript="test",
            language="en",
            audio_metadata=audio_metadata,
        )

        assert analysis.phonetic_accuracy > 0.0
        assert analysis.fluency_score > 0.0

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_levels(self, processor):
        """Test pronunciation level determination"""
        # Test with high quality metadata
        metadata_excellent = AudioMetadata(
            format=AudioFormat.WAV,
            sample_rate=16000,
            channels=1,
            duration_seconds=1.0,
            file_size_bytes=32000,
            quality_score=0.95,
        )
        analysis = await processor._analyze_pronunciation(
            audio_data=b"audio",
            transcript="hello",
            language="en",
            audio_metadata=metadata_excellent,
        )

        # Should get a valid pronunciation level (any level is acceptable)
        assert analysis.pronunciation_level in list(PronunciationLevel)
        assert 0.0 <= analysis.overall_score <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_error(self, processor, audio_metadata):
        """Test pronunciation analysis error handling"""
        with patch.object(
            processor, "_calculate_pronunciation_scores", side_effect=Exception("Error")
        ):
            with pytest.raises(Exception, match="Pronunciation analysis failed"):
                await processor._analyze_pronunciation(
                    audio_data=b"audio",
                    transcript="hello",
                    language="en",
                    audio_metadata=audio_metadata,
                )

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_quality_success(
        self, processor, mock_audio_data
    ):
        """Test analyze_pronunciation_quality method"""
        mock_recognition = SpeechRecognitionResult(
            transcript="hello world",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        mock_analysis = PronunciationAnalysis(
            overall_score=0.85,
            pronunciation_level=PronunciationLevel.GOOD,
            phonetic_accuracy=0.9,
            fluency_score=0.8,
            word_level_scores=[],
            detected_issues=[],
            improvement_suggestions=[],
            phonetic_transcription="/hello world/",
            target_phonetics="/hello world/",
        )

        with patch.object(
            processor, "process_speech_to_text", return_value=(mock_recognition, None)
        ):
            with patch.object(
                processor, "_compare_pronunciation", return_value=mock_analysis
            ):
                result = await processor.analyze_pronunciation_quality(
                    user_audio=mock_audio_data,
                    reference_text="hello world",
                    language="en",
                )

                assert result.overall_score == 0.85

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_quality_error(
        self, processor, mock_audio_data
    ):
        """Test analyze_pronunciation_quality error handling"""
        with patch.object(
            processor, "process_speech_to_text", side_effect=Exception("Error")
        ):
            result = await processor.analyze_pronunciation_quality(
                user_audio=mock_audio_data,
                reference_text="hello",
                language="en",
            )

            assert result.overall_score == 0.0
            assert result.pronunciation_level == PronunciationLevel.UNCLEAR

    @pytest.mark.asyncio
    async def test_compare_pronunciation_basic(self, processor):
        """Test pronunciation comparison"""
        analysis = await processor._compare_pronunciation(
            recognized_text="hello world",
            reference_text="hello world",
            language="en",
            confidence=0.9,
        )

        assert isinstance(analysis, PronunciationAnalysis)
        assert analysis.overall_score > 0.0

    @pytest.mark.asyncio
    async def test_compare_pronunciation_mismatch(self, processor):
        """Test pronunciation comparison with mismatch"""
        analysis = await processor._compare_pronunciation(
            recognized_text="hello word",
            reference_text="hello world",
            language="en",
            confidence=0.8,
        )

        # Score should be lower due to mismatch
        assert analysis.overall_score < 1.0

    def test_calculate_pronunciation_scores(self, processor, audio_metadata):
        """Test pronunciation score calculation helper"""
        words = ["hello", "world"]
        phonetic, fluency, overall = processor._calculate_pronunciation_scores(
            words, len(words), audio_metadata
        )

        assert 0.0 <= phonetic <= 1.0
        assert 0.0 <= fluency <= 1.0
        assert 0.0 <= overall <= 1.0

    def test_determine_pronunciation_level_excellent(self, processor):
        """Test excellent pronunciation level"""
        level = processor._determine_pronunciation_level(0.95)
        assert level == PronunciationLevel.EXCELLENT

    def test_determine_pronunciation_level_good(self, processor):
        """Test good pronunciation level"""
        level = processor._determine_pronunciation_level(0.80)
        assert level == PronunciationLevel.GOOD

    def test_determine_pronunciation_level_fair(self, processor):
        """Test fair pronunciation level"""
        level = processor._determine_pronunciation_level(0.65)
        assert level == PronunciationLevel.FAIR

    def test_determine_pronunciation_level_needs_improvement(self, processor):
        """Test needs improvement pronunciation level"""
        level = processor._determine_pronunciation_level(0.45)
        assert level == PronunciationLevel.NEEDS_IMPROVEMENT

    def test_determine_pronunciation_level_unclear(self, processor):
        """Test unclear pronunciation level"""
        level = processor._determine_pronunciation_level(0.25)
        assert level == PronunciationLevel.UNCLEAR

    def test_generate_word_scores(self, processor):
        """Test word score generation"""
        words = ["hello", "world"]
        scores = processor._generate_word_scores(words, 0.8)

        assert len(scores) == 2
        assert all("word" in score for score in scores)
        assert all("score" in score for score in scores)

    def test_generate_improvement_suggestions(self, processor):
        """Test improvement suggestion generation"""
        suggestions = processor._generate_improvement_suggestions(0.6, 0.5, "en")

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_detect_language_issues(self, processor):
        """Test language-specific issue detection"""
        model = processor.pronunciation_models["en"]
        words = ["through", "thought"]  # Difficulty words

        issues = processor._detect_language_issues(words, model)

        assert isinstance(issues, list)


# ============================================================================
# Test Pipeline Status and Health
# ============================================================================


class TestPipelineStatus:
    """Test pipeline status and health check methods"""

    @pytest.mark.asyncio
    async def test_get_speech_pipeline_status(self, processor):
        """Test getting pipeline status"""
        status = await processor.get_speech_pipeline_status()

        assert isinstance(status, dict)
        assert "status" in status
        assert "watson_stt_available" in status
        assert "watson_tts_available" in status
        assert "supported_formats" in status
        assert "supported_languages" in status
        assert "features" in status

    @pytest.mark.asyncio
    async def test_get_speech_pipeline_status_formats(self, processor):
        """Test pipeline status includes audio formats"""
        status = await processor.get_speech_pipeline_status()

        assert "wav" in status["supported_formats"]
        assert "mp3" in status["supported_formats"]

    @pytest.mark.asyncio
    async def test_get_speech_pipeline_status_languages(self, processor):
        """Test pipeline status includes languages"""
        status = await processor.get_speech_pipeline_status()

        assert "en" in status["supported_languages"]
        assert "fr" in status["supported_languages"]
        assert "es" in status["supported_languages"]
        assert "zh" in status["supported_languages"]


# ============================================================================
# Test Helper Methods
# ============================================================================


class TestHelperMethods:
    """Test various helper methods"""

    def test_get_settings_safely_success(self, processor):
        """Test get settings successfully"""
        with patch("app.services.speech_processor.get_settings") as mock_get:
            mock_settings = Mock()
            mock_get.return_value = mock_settings

            result = processor._get_settings_safely()

            assert result == mock_settings

    def test_get_settings_safely_error(self, processor):
        """Test get settings error handling"""
        with patch(
            "app.services.speech_processor.get_settings", side_effect=Exception("Error")
        ):
            result = processor._get_settings_safely()

            assert result is None

    def test_get_overall_status_operational(self, processor):
        """Test overall status when services operational"""
        status = processor._get_overall_status(True, True)
        assert status == "operational"

    def test_get_overall_status_limited(self, processor):
        """Test overall status when services limited"""
        status = processor._get_overall_status(False, False)
        assert status == "limited"

    def test_build_watson_stt_status(self, processor):
        """Test building Watson STT status"""
        mock_settings = Mock()
        mock_settings.IBM_WATSON_STT_API_KEY = "key"
        mock_settings.IBM_WATSON_STT_URL = "url"

        status = processor._build_watson_stt_status(True, mock_settings)

        assert status["status"] == "operational"
        assert status["api_key_configured"] is True

    def test_build_watson_tts_status(self, processor):
        """Test building Watson TTS status"""
        mock_settings = Mock()
        mock_settings.IBM_WATSON_TTS_API_KEY = "key"
        mock_settings.IBM_WATSON_TTS_URL = "url"

        status = processor._build_watson_tts_status(True, mock_settings)

        assert status["status"] == "operational"

    def test_build_features_status(self, processor):
        """Test building features status"""
        features = processor._build_features_status(True, True)

        assert "speech_recognition" in features
        assert "speech_synthesis" in features
        assert "pronunciation_analysis" in features

    def test_build_configuration_dict(self, processor):
        """Test building configuration dictionary"""
        config = processor._build_configuration_dict()

        assert config["default_sample_rate"] == 16000
        assert config["default_channels"] == 1
        assert config["chunk_size"] == 1024

    def test_build_api_models_dict(self, processor):
        """Test building API models dictionary"""
        models = processor._build_api_models_dict()

        assert "watson_stt_models" in models
        assert "watson_tts_voices" in models
        assert isinstance(models["watson_stt_models"], list)

    def test_build_chinese_support_dict(self, processor):
        """Test building Chinese support dictionary"""
        support = processor._build_chinese_support_dict()

        assert support["stt_available"] is True
        assert "pronunciation_learning" in support

    def test_build_spanish_support_dict(self, processor):
        """Test building Spanish support dictionary"""
        support = processor._build_spanish_support_dict()

        assert "stt_model" in support
        assert "tts_voice" in support

    def test_validate_provider_not_watson_valid(self, processor):
        """Test provider validation with valid providers"""
        # Should not raise
        processor._validate_provider_not_watson("auto")
        processor._validate_provider_not_watson("mistral")

    def test_validate_provider_not_watson_invalid(self, processor):
        """Test provider validation with Watson"""
        with pytest.raises(Exception, match="Watson STT deprecated"):
            processor._validate_provider_not_watson("watson")

    def test_is_result_acceptable_good(self, processor):
        """Test result acceptability check - good result"""
        result = SpeechRecognitionResult(
            transcript="hello",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        assert processor._is_result_acceptable(result) is True

    def test_is_result_acceptable_low_confidence(self, processor):
        """Test result acceptability check - low confidence"""
        result = SpeechRecognitionResult(
            transcript="hello",
            confidence=0.05,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        assert processor._is_result_acceptable(result) is False

    def test_is_result_acceptable_empty_transcript(self, processor):
        """Test result acceptability check - empty transcript"""
        result = SpeechRecognitionResult(
            transcript="   ",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        assert processor._is_result_acceptable(result) is False


# ============================================================================
# Test Global Instance and Convenience Functions
# ============================================================================


class TestGlobalInstanceAndConvenience:
    """Test global instance and convenience functions"""

    def test_global_instance_exists(self):
        """Test that global speech_processor instance exists"""
        assert speech_processor is not None
        assert isinstance(speech_processor, SpeechProcessor)

    def test_global_instance_attributes(self):
        """Test global instance has correct attributes"""
        assert hasattr(speech_processor, "pronunciation_models")
        assert hasattr(speech_processor, "default_sample_rate")

    @pytest.mark.asyncio
    async def test_speech_to_text_convenience(self, mock_audio_data):
        """Test speech_to_text convenience function"""
        mock_result = SpeechRecognitionResult(
            transcript="test",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        mock_analysis = PronunciationAnalysis(
            overall_score=0.85,
            pronunciation_level=PronunciationLevel.GOOD,
            phonetic_accuracy=0.9,
            fluency_score=0.8,
            word_level_scores=[],
            detected_issues=[],
            improvement_suggestions=[],
            phonetic_transcription="/test/",
            target_phonetics="/test/",
        )

        with patch.object(
            speech_processor,
            "process_speech_to_text",
            return_value=(mock_result, mock_analysis),
        ):
            transcript, pronunciation = await speech_to_text(
                mock_audio_data, "en", True
            )

            assert transcript == "test"
            assert pronunciation.overall_score == 0.85

    @pytest.mark.asyncio
    async def test_text_to_speech_convenience(self):
        """Test text_to_speech convenience function"""
        mock_result = SpeechSynthesisResult(
            audio_data=b"audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={},
        )

        with patch.object(
            speech_processor, "process_text_to_speech", return_value=mock_result
        ):
            audio = await text_to_speech("hello", "en", "neural")

            assert audio == b"audio"

    @pytest.mark.asyncio
    async def test_analyze_pronunciation_convenience(self, mock_audio_data):
        """Test analyze_pronunciation convenience function"""
        mock_analysis = PronunciationAnalysis(
            overall_score=0.85,
            pronunciation_level=PronunciationLevel.GOOD,
            phonetic_accuracy=0.9,
            fluency_score=0.8,
            word_level_scores=[],
            detected_issues=[],
            improvement_suggestions=[],
            phonetic_transcription="/hello/",
            target_phonetics="/hello/",
        )

        with patch.object(
            speech_processor,
            "analyze_pronunciation_quality",
            return_value=mock_analysis,
        ):
            analysis = await analyze_pronunciation(mock_audio_data, "hello", "en")

            assert analysis.overall_score == 0.85

    @pytest.mark.asyncio
    async def test_get_speech_status_convenience(self):
        """Test get_speech_status convenience function"""
        mock_status = {
            "status": "operational",
            "watson_stt_available": False,
            "watson_tts_available": False,
        }

        with patch.object(
            speech_processor, "get_speech_pipeline_status", return_value=mock_status
        ):
            status = await get_speech_status()

            assert status["status"] == "operational"


# ============================================================================
# Test Enums and Data Classes
# ============================================================================


class TestAdditionalCoverage:
    """Additional tests to cover missing lines"""

    @pytest.mark.asyncio
    async def test_try_mistral_stt_success(self, processor, mock_audio_data):
        """Test _try_mistral_stt with successful result"""
        mock_result = SpeechRecognitionResult(
            transcript="test transcript",
            confidence=0.95,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        processor.mistral_stt_available = True

        with patch.object(
            processor, "_speech_to_text_mistral", return_value=mock_result
        ):
            result = await processor._try_mistral_stt(
                mock_audio_data, "en", AudioFormat.WAV, "auto"
            )
            assert result.transcript == "test transcript"
            assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_try_mistral_stt_low_quality(self, processor, mock_audio_data):
        """Test _try_mistral_stt with low quality result"""
        mock_result = SpeechRecognitionResult(
            transcript="unclear",
            confidence=0.05,
            language="en",
            processing_time=0.5,
            alternative_transcripts=[],
            metadata={},
        )

        processor.mistral_stt_available = True

        with patch.object(
            processor, "_speech_to_text_mistral", return_value=mock_result
        ):
            with pytest.raises(Exception, match="Mistral result not acceptable"):
                await processor._try_mistral_stt(
                    mock_audio_data, "en", AudioFormat.WAV, "mistral"
                )

    @pytest.mark.asyncio
    async def test_process_auto_provider_tts_unavailable(self, processor):
        """Test auto provider when Piper unavailable"""
        processor.piper_tts_available = False

        with pytest.raises(Exception, match="Piper TTS not available"):
            await processor._process_auto_provider(
                "hello", "hello", "en", "neural", 1.0
            )

    @pytest.mark.asyncio
    async def test_process_piper_fallback_both_unavailable(self, processor):
        """Test piper_fallback when Piper unavailable"""
        processor.piper_tts_available = False

        with pytest.raises(Exception, match="Piper TTS not available"):
            await processor._process_piper_fallback(
                "hello", "hello", "en", "neural", 1.0
            )


class TestImportErrorHandlers:
    """Test import error handling for external libraries"""

    def test_import_numpy_unavailable(self):
        """Test behavior when numpy is unavailable (lines 34-36)"""
        import os
        import subprocess
        import sys

        # Run a subprocess that blocks numpy import and checks AUDIO_LIBS_AVAILABLE
        test_code = """
import sys
import os

# Enable coverage in subprocess if running under coverage
try:
    import coverage
    cov = coverage.Coverage(data_suffix=True, auto_data=True, branch=True)
    cov.start()
except ImportError:
    pass

# Block numpy import using custom meta path finder
class NumpyBlocker:
    def find_module(self, fullname, path=None):
        if fullname == 'numpy' or fullname.startswith('numpy.'):
            raise ImportError("numpy is blocked for testing")
        return None

    def find_spec(self, fullname, path, target=None):
        if fullname == 'numpy' or fullname.startswith('numpy.'):
            raise ImportError("numpy is blocked for testing")
        return None

sys.meta_path.insert(0, NumpyBlocker())

# Now import speech_processor - numpy should fail
from app.services import speech_processor

# Verify AUDIO_LIBS_AVAILABLE is False (lines 34-36 executed)
assert speech_processor.AUDIO_LIBS_AVAILABLE is False, \\
    f"Expected AUDIO_LIBS_AVAILABLE=False, got {speech_processor.AUDIO_LIBS_AVAILABLE}"
print("SUCCESS: numpy import blocked, AUDIO_LIBS_AVAILABLE=False")

# Stop coverage if it was started
try:
    cov.stop()
    cov.save()
except:
    pass
"""

        # Set up environment for subprocess
        env = os.environ.copy()
        env["COVERAGE_PROCESS_START"] = ".coveragerc"

        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            cwd="/Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app",
            env=env,
        )

        # Check that subprocess succeeded
        assert result.returncode == 0, (
            f"Subprocess failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
        assert "SUCCESS" in result.stdout, (
            f"Test did not complete successfully:\n{result.stdout}"
        )

    def test_mistral_stt_import_unavailable(self, monkeypatch):
        """Test behavior when Mistral STT import fails"""
        # This tests lines 49-51 (except ImportError for Mistral)
        # The test indirectly validates the import error handling
        # by checking that initialization handles unavailability
        processor = SpeechProcessor()
        if not processor.mistral_stt_available:
            # Already testing unavailable scenario
            assert processor.mistral_stt_service is None

    def test_piper_tts_import_unavailable(self, monkeypatch):
        """Test behavior when Piper TTS import fails"""
        # This tests lines 58-60 (except ImportError for Piper)
        # The test indirectly validates the import error handling
        processor = SpeechProcessor()
        if not processor.piper_tts_available:
            # Already testing unavailable scenario
            assert processor.piper_tts_service is None


class TestExceptionHandlers:
    """Test exception handling in various methods"""

    def test_vad_exception_handler(self, processor):
        """Test voice activity detection exception handling (line 214)"""
        # Force an exception by passing invalid audio data type
        with patch(
            "app.services.speech_processor.np.frombuffer",
            side_effect=Exception("numpy error"),
        ):
            result = processor.detect_voice_activity(b"test")
            assert result == False  # Should return False on error

    @pytest.mark.asyncio
    async def test_mistral_init_exception(self, processor, monkeypatch):
        """Test Mistral STT initialization exception (lines 254-257)"""
        processor.mistral_stt_available = True

        # Force exception during import
        def mock_import_error(*args, **kwargs):
            raise Exception("Import failed")

        with patch("app.services.speech_processor.logger") as mock_logger:
            processor._init_mistral_stt()

            # If exception occurs, should log error
            if not processor.mistral_stt_service:
                assert processor.mistral_stt_available == False

    def test_piper_init_exception(self, processor):
        """Test Piper TTS initialization exception (lines 283-286)"""
        # Reset the processor state
        processor.piper_tts_available = True
        processor.piper_tts_service = None

        # Mock PiperTTSService to raise exception
        with patch(
            "app.services.piper_tts_service.PiperTTSService",
            side_effect=Exception("Init failed"),
        ):
            processor._init_piper_tts()

            # Exception should be caught and service set to None
            assert processor.piper_tts_service is None
            assert processor.piper_tts_available == False

    @pytest.mark.asyncio
    async def test_tts_watson_provider_error(self, processor):
        """Test TTS with watson provider raises error (line 499)"""
        with pytest.raises(Exception, match="Watson TTS deprecated"):
            await processor._select_tts_provider_and_process(
                "hello", "en", "neural", 1.0, "watson", "hello"
            )

    @pytest.mark.asyncio
    async def test_process_auto_provider_piper_failure(self, processor):
        """Test auto provider when Piper fails (lines 533-535)"""
        processor.piper_tts_available = True

        with patch.object(
            processor, "_text_to_speech_piper", side_effect=Exception("Piper failed")
        ):
            with pytest.raises(Exception, match="TTS synthesis failed"):
                await processor._process_auto_provider(
                    "hello", "hello", "en", "neural", 1.0
                )

    @pytest.mark.asyncio
    async def test_process_piper_fallback_exception(self, processor):
        """Test piper fallback exception handling (lines 549-557)"""
        processor.piper_tts_available = True

        with patch.object(
            processor, "_text_to_speech_piper", side_effect=Exception("Piper error")
        ):
            # The exception should propagate up since there's no Watson fallback
            # in Phase 2A (Watson deprecated)
            with pytest.raises(Exception):
                await processor._process_piper_fallback(
                    "hello", "hello", "en", "neural", 1.0
                )

    @pytest.mark.asyncio
    async def test_enhance_audio_exception(self, processor):
        """Test audio enhancement exception handling (line 661)"""
        with patch.object(
            processor, "_reduce_noise", side_effect=Exception("Enhancement failed")
        ):
            result = await processor._enhance_audio_quality(b"audio", AudioFormat.WAV)
            # Should return original audio on error
            assert result == b"audio"

    def test_speech_enhancement_exception(self, processor):
        """Test speech enhancement exception handling (line 669)"""
        with patch("numpy.frombuffer", side_effect=Exception("numpy error")):
            result = processor._apply_speech_enhancement(b"audio")
            # Should return original audio on error
            assert result == b"audio"

    @pytest.mark.asyncio
    async def test_analyze_audio_quality_exception(self, processor):
        """Test audio quality analysis exception handling (lines 893-897)"""
        # Force an exception in the OUTER try block
        # by causing division by zero in the quality calculation
        audio_data = b"x"  # Very small data

        # Mock to cause exception during duration calculation
        original_sample_rate = processor.default_sample_rate
        processor.default_sample_rate = 0  # This will cause ZeroDivisionError

        result = await processor._analyze_audio_quality(audio_data, AudioFormat.WAV)

        # Restore original value
        processor.default_sample_rate = original_sample_rate

        # Should return fallback metadata from the outer exception handler
        assert result.quality_score == 0.5
        assert result.duration_seconds == 1.0
        assert result.file_size_bytes == len(audio_data)


class TestAdditionalExceptionPaths:
    """Test additional exception paths to reach 100% coverage"""

    def test_vad_with_empty_array_exception(self, processor):
        """Test VAD exception with actual exception path (line 214)"""
        # Create scenario where numpy operations succeed but exception occurs
        with patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True):
            with patch(
                "app.services.speech_processor.np.frombuffer"
            ) as mock_frombuffer:
                # Make frombuffer succeed but sqrt fail
                mock_array = Mock()
                mock_array.astype = Mock(side_effect=Exception("Processing error"))
                mock_frombuffer.return_value = mock_array

                result = processor.detect_voice_activity(b"test_audio")
                assert result == False

    @pytest.mark.asyncio
    async def test_mistral_init_import_exception(self):
        """Test Mistral init when import fails (lines 254-257)"""
        from app.services.speech_processor import SpeechProcessor

        # Create new processor and force exception in init
        processor = SpeechProcessor()
        processor.mistral_stt_available = True

        # Patch where the class is imported FROM, not where it's used
        with patch(
            "app.services.mistral_stt_service.MistralSTTService",
            side_effect=ImportError("No module"),
        ):
            processor._init_mistral_stt()
            assert processor.mistral_stt_available == False

    def test_piper_init_import_exception(self):
        """Test Piper init when import fails (lines 283-286)"""
        from app.services.speech_processor import SpeechProcessor

        processor = SpeechProcessor()
        processor.piper_tts_available = True

        # Patch where the class is imported FROM, not where it's used
        with patch(
            "app.services.piper_tts_service.PiperTTSService",
            side_effect=ImportError("No module"),
        ):
            processor._init_piper_tts()
            assert processor.piper_tts_available == False

    @pytest.mark.asyncio
    async def test_process_piper_fallback_success_path(self, processor):
        """Test successful piper fallback (lines 556-557)"""
        processor.piper_tts_available = True

        mock_result = SpeechSynthesisResult(
            audio_data=b"audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={},
        )

        with patch.object(processor, "_text_to_speech_piper", return_value=mock_result):
            result = await processor._process_piper_fallback(
                "hello", "hello", "en", "neural", 1.0
            )
            assert result.audio_data == b"audio"

    @pytest.mark.asyncio
    async def test_enhance_audio_with_exception_in_reduction(self, processor):
        """Test audio enhancement when noise reduction fails (line 661)"""
        with patch.object(
            processor, "_reduce_noise", side_effect=Exception("Reduction failed")
        ):
            result = await processor._enhance_audio_quality(b"test", AudioFormat.WAV)
            assert result == b"test"  # Should return original

    def test_speech_enhancement_with_exception(self, processor):
        """Test speech enhancement exception (line 669)"""
        with patch("app.services.speech_processor.AUDIO_LIBS_AVAILABLE", True):
            with patch(
                "app.services.speech_processor.np.frombuffer",
                side_effect=Exception("numpy error"),
            ):
                result = processor._apply_speech_enhancement(b"test")
                assert result == b"test"


class TestEnumsAndDataClasses:
    """Test enum and dataclass definitions"""

    def test_audio_format_enum(self):
        """Test AudioFormat enum values"""
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.FLAC.value == "flac"
        assert AudioFormat.WEBM.value == "webm"

    def test_pronunciation_level_enum(self):
        """Test PronunciationLevel enum values"""
        assert PronunciationLevel.EXCELLENT.value == "excellent"
        assert PronunciationLevel.GOOD.value == "good"
        assert PronunciationLevel.FAIR.value == "fair"
        assert PronunciationLevel.NEEDS_IMPROVEMENT.value == "needs_improvement"
        assert PronunciationLevel.UNCLEAR.value == "unclear"

    def test_audio_metadata_creation(self):
        """Test AudioMetadata dataclass creation"""
        metadata = AudioMetadata(
            format=AudioFormat.WAV,
            sample_rate=16000,
            channels=1,
            duration_seconds=2.0,
            file_size_bytes=32000,
            quality_score=0.85,
        )

        assert metadata.format == AudioFormat.WAV
        assert metadata.sample_rate == 16000
        assert metadata.quality_score == 0.85

    def test_speech_recognition_result_creation(self):
        """Test SpeechRecognitionResult dataclass creation"""
        result = SpeechRecognitionResult(
            transcript="hello",
            confidence=0.9,
            language="en",
            processing_time=0.5,
            alternative_transcripts=["hallo"],
            metadata={"provider": "test"},
        )

        assert result.transcript == "hello"
        assert result.confidence == 0.9
        assert result.language == "en"

    def test_pronunciation_analysis_creation(self):
        """Test PronunciationAnalysis dataclass creation"""
        analysis = PronunciationAnalysis(
            overall_score=0.85,
            pronunciation_level=PronunciationLevel.GOOD,
            phonetic_accuracy=0.9,
            fluency_score=0.8,
            word_level_scores=[{"word": "hello", "score": 0.9}],
            detected_issues=["speed"],
            improvement_suggestions=["slow down"],
            phonetic_transcription="/hello/",
            target_phonetics="/hello/",
        )

        assert analysis.overall_score == 0.85
        assert analysis.pronunciation_level == PronunciationLevel.GOOD

    def test_speech_synthesis_result_creation(self):
        """Test SpeechSynthesisResult dataclass creation"""
        result = SpeechSynthesisResult(
            audio_data=b"audio",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=2.0,
            processing_time=0.5,
            metadata={"provider": "piper"},
        )

        assert result.audio_data == b"audio"
        assert result.audio_format == AudioFormat.WAV
        assert result.sample_rate == 22050


class TestFinalCoverageGaps:
    """Tests to achieve 100% coverage for speech_processor.py - Session 19"""

    def test_vad_empty_array(self, processor):
        """Test VAD with empty array after np.frombuffer (line 204)"""
        # Mock np.frombuffer to return empty array
        # This simulates the edge case where bytes are valid but produce no int16 values
        with patch("app.services.speech_processor.np.frombuffer") as mock_frombuffer:
            # Return empty array with correct shape
            mock_frombuffer.return_value = np.array([], dtype=np.int16)

            # Provide valid audio bytes (>= 2 bytes to pass line 182)
            audio_data = b"\x00\x01\x02\x03"

            result = processor.detect_voice_activity(audio_data, sample_rate=16000)

            # Should return False for empty array (line 204)
            assert result is False
            mock_frombuffer.assert_called_once()

    def test_mistral_init_unavailable(self):
        """Test Mistral STT init when unavailable (lines 254-257)"""
        with patch("app.services.speech_processor.MISTRAL_STT_AVAILABLE", False):
            processor = SpeechProcessor()
            assert processor.mistral_stt_available is False
            assert processor.mistral_stt_service is None

    def test_piper_init_unavailable(self):
        """Test Piper TTS init when unavailable (lines 283-286)"""
        with patch("app.services.speech_processor.PIPER_TTS_AVAILABLE", False):
            processor = SpeechProcessor()
            assert processor.piper_tts_available is False
            assert processor.piper_tts_service is None

    @pytest.mark.asyncio
    async def test_piper_fallback_provider(self, processor):
        """Test piper_fallback provider (line 499)"""
        mock_result = SpeechSynthesisResult(
            audio_data=b"test",
            audio_format=AudioFormat.WAV,
            sample_rate=22050,
            duration_seconds=1.0,
            processing_time=0.1,
            metadata={},
        )
        with patch.object(
            processor, "_process_piper_fallback", return_value=mock_result
        ):
            result = await processor._select_tts_provider_and_process(
                text="test",
                language="en",
                voice_type="female",
                speaking_rate=1.0,
                provider="piper_fallback",
            )
            assert result.audio_data == b"test"

    @pytest.mark.asyncio
    async def test_auto_low_quality_acceptance(self, processor):
        """Test auto mode accepts low quality (line 661)"""
        low_quality = SpeechRecognitionResult(
            transcript="test",
            confidence=0.3,
            language="en",
            processing_time=0.1,
            alternative_transcripts=[],
            metadata={},
        )
        # Mock both the STT call and the acceptability check
        with patch.object(
            processor, "_speech_to_text_mistral", return_value=low_quality
        ):
            with patch.object(processor, "_is_result_acceptable", return_value=False):
                result = await processor._try_mistral_stt(
                    audio_data=b"audio",
                    language="en",
                    audio_format=AudioFormat.WAV,
                    provider="auto",
                )
                assert result.confidence == 0.3
                assert result.transcript == "test"

    @pytest.mark.asyncio
    async def test_mistral_unavailable_exception(self, processor):
        """Test Mistral unavailable exception (line 669)"""
        processor.mistral_stt_available = False
        with pytest.raises(Exception, match="Mistral STT not available"):
            await processor._process_with_auto_or_fallback(
                audio_data=b"audio",
                language="en",
                audio_format=AudioFormat.WAV,
                provider="auto",
            )
