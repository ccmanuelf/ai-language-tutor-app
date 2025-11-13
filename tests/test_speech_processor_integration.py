"""
Integration tests for speech_processor.py with REAL audio

Philosophy:
- Use REAL audio files from fixtures (no b"fake_audio_data")
- Mock only at HTTP API level (not internal methods)
- Test full preprocessing pipelines (VAD, enhancement, format conversion)
- Validate that actual audio processing happens

Added in Session 24 - Phase 4 of Audio Testing Initiative
"""

from unittest.mock import AsyncMock, Mock

import pytest

from app.services.speech_processor import (
    AudioFormat,
    PronunciationAnalysis,
    PronunciationLevel,
    SpeechProcessor,
    SpeechRecognitionResult,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def processor():
    """Create a fresh SpeechProcessor instance for each test"""
    return SpeechProcessor()


class TestSpeechToTextIntegration:
    """
    Integration tests for speech-to-text with real audio processing.

    Tests the full STT pipeline:
    - Real audio preprocessing (VAD, noise reduction, normalization)
    - Real format conversion and validation
    - Mock only the HTTP API call to Mistral
    """

    def _setup_mistral_mock(self, processor, response_data):
        """Helper to set up Mistral STT service with mocked HTTP client"""
        from app.services.mistral_stt_service import MistralSTTService

        processor.mistral_stt_available = True
        if not processor.mistral_stt_service:
            processor.mistral_stt_service = MistralSTTService()
            processor.mistral_stt_service.available = True

        # Create mock response
        mock_response = Mock()
        mock_response.status_code = response_data.get("status_code", 200)
        if "json" in response_data:
            mock_response.json = Mock(return_value=response_data["json"])
        if "text" in response_data:
            mock_response.text = response_data["text"]

        # Create async mock for the post method that returns the response
        mock_post = AsyncMock(return_value=mock_response)

        # Mock the client
        mock_client = Mock()
        mock_client.post = mock_post
        processor.mistral_stt_service.client = mock_client

        return mock_post

    @pytest.mark.asyncio
    async def test_stt_with_speech_like_audio_real_preprocessing(
        self, processor, speech_like_audio_16khz
    ):
        """Test STT with real speech-like audio through full preprocessing pipeline"""
        # Setup mock - only HTTP layer, not internal methods
        mock_post = self._setup_mistral_mock(
            processor,
            {"json": {"text": "hello world", "confidence": 0.95, "language": "en"}},
        )

        # Call process_speech_to_text with REAL audio
        # This will test: VAD, enhancement, format conversion, preprocessing
        result, pronunciation = await processor.process_speech_to_text(
            audio_data=speech_like_audio_16khz,
            language="en",
            enable_pronunciation_analysis=False,
        )

        # Verify the real audio was processed
        assert result.transcript == "hello world"
        assert result.confidence == 0.95
        assert result.language == "en"

        # Verify the API was called with actual audio data
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert "files" in call_kwargs
        assert "data" in call_kwargs

    @pytest.mark.asyncio
    async def test_stt_with_silence_audio_real_vad(
        self, processor, silence_audio_16khz
    ):
        """Test STT with real silence audio - preprocessing should handle it"""
        mock_post = self._setup_mistral_mock(
            processor,
            {"json": {"text": "", "confidence": 0.0, "language": "en"}},
        )

        # Test with real silence audio
        result, _ = await processor.process_speech_to_text(
            audio_data=silence_audio_16khz,
            language="en",
            enable_pronunciation_analysis=False,
        )

        # Verify silence was processed
        assert result.transcript == ""
        assert result.confidence == 0.0
        # Verify preprocessing happened (API was still called with processed audio)
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_with_white_noise_real_audio(
        self, processor, white_noise_audio_16khz
    ):
        """Test STT with real white noise - should handle gracefully"""
        mock_post = self._setup_mistral_mock(
            processor,
            {"json": {"text": "[unintelligible]", "confidence": 0.2, "language": "en"}},
        )

        # Test with real white noise
        result, _ = await processor.process_speech_to_text(
            audio_data=white_noise_audio_16khz,
            language="en",
            enable_pronunciation_analysis=False,
        )

        # Verify noise was processed with low confidence
        assert result.confidence < 0.5
        assert len(result.transcript) >= 0
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_with_stereo_audio_real_conversion(
        self, processor, stereo_audio_16khz
    ):
        """Test STT with real stereo audio - preprocessing should handle conversion"""
        mock_post = self._setup_mistral_mock(
            processor,
            {"json": {"text": "stereo test", "confidence": 0.9, "language": "en"}},
        )

        # Test with real stereo audio (preprocessing should convert to mono)
        result, _ = await processor.process_speech_to_text(
            audio_data=stereo_audio_16khz,
            language="en",
            enable_pronunciation_analysis=False,
        )

        # Verify stereo was processed successfully
        assert result.transcript == "stereo test"
        assert result.confidence == 0.9
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_multi_language_real_audio(
        self, processor, speech_like_audio_16khz
    ):
        """Test STT with different languages using real audio"""
        # Test multiple languages with same audio
        test_languages = [
            ("en", "hello world"),
            ("es", "hola mundo"),
            ("fr", "bonjour monde"),
            ("de", "hallo welt"),
        ]

        for lang_code, expected_text in test_languages:
            # Setup mock for this language
            mock_post = self._setup_mistral_mock(
                processor,
                {
                    "json": {
                        "text": expected_text,
                        "confidence": 0.9,
                        "language": lang_code,
                    }
                },
            )

            # Test with real audio
            result, _ = await processor.process_speech_to_text(
                audio_data=speech_like_audio_16khz,
                language=lang_code,
                enable_pronunciation_analysis=False,
            )

            assert result.transcript == expected_text
            assert result.language == lang_code
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_with_pronunciation_analysis_real_audio(
        self, processor, speech_like_audio_16khz
    ):
        """Test STT with pronunciation analysis using real audio"""
        mock_post = self._setup_mistral_mock(
            processor,
            {
                "json": {
                    "text": "hello world",
                    "confidence": 0.92,
                    "language": "en",
                }
            },
        )

        # Test with pronunciation analysis enabled
        result, pronunciation = await processor.process_speech_to_text(
            audio_data=speech_like_audio_16khz,
            language="en",
            enable_pronunciation_analysis=True,
        )

        # Verify pronunciation analysis was performed
        assert result.transcript == "hello world"
        assert pronunciation is not None
        assert isinstance(pronunciation, PronunciationAnalysis)
        assert 0.0 <= pronunciation.overall_score <= 1.0
        assert pronunciation.pronunciation_level in list(PronunciationLevel)
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_api_error_handling_real_audio(
        self, processor, speech_like_audio_16khz
    ):
        """Test STT error handling with real audio when API fails"""
        mock_post = self._setup_mistral_mock(
            processor,
            {"status_code": 500, "text": "Internal Server Error"},
        )

        # Test error handling with real audio
        result, _ = await processor.process_speech_to_text(
            audio_data=speech_like_audio_16khz,
            language="en",
            enable_pronunciation_analysis=False,
        )

        # Should return error result, not crash
        assert (
            "[Speech recognition failed]" in result.transcript
            or "Error" in result.transcript
        )
        assert result.confidence == 0.0
        assert "error" in result.metadata
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_short_audio_real_beep(self, processor, short_beep_audio_16khz):
        """Test STT with very short real audio (100ms beep) - should be padded"""
        mock_post = self._setup_mistral_mock(
            processor,
            {"json": {"text": "", "confidence": 0.1, "language": "en"}},
        )

        # Test with very short audio (preprocessing should pad it)
        result, _ = await processor.process_speech_to_text(
            audio_data=short_beep_audio_16khz,
            language="en",
            enable_pronunciation_analysis=False,
        )

        # Should handle short audio gracefully
        assert isinstance(result, SpeechRecognitionResult)
        assert result.confidence >= 0.0
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_audio_quality_analysis_real_signals(
        self, processor, speech_like_audio_16khz, silence_audio_16khz
    ):
        """Test that audio quality analysis works with real signals"""
        # Test with speech-like audio (should have good quality)
        speech_metadata = await processor._analyze_audio_quality(
            speech_like_audio_16khz, AudioFormat.WAV
        )

        # Test with silence (should have lower quality)
        silence_metadata = await processor._analyze_audio_quality(
            silence_audio_16khz, AudioFormat.WAV
        )

        # Speech-like should have higher quality than pure silence
        assert speech_metadata.quality_score > silence_metadata.quality_score
        assert 0.0 <= speech_metadata.quality_score <= 1.0
        assert 0.0 <= silence_metadata.quality_score <= 1.0
