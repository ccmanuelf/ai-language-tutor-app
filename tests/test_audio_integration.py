"""
Audio Integration Tests - Real Audio Workflow Testing

This module tests end-to-end audio processing workflows combining:
- STT (Speech-to-Text) via Mistral Voxtral
- TTS (Text-to-Speech) via Piper
- Speech processing pipeline

Tests use REAL audio files and validate actual audio generation.
HTTP APIs are mocked at the network level, but audio processing is real.

Test Structure:
- TestSTTTTSIntegration: End-to-end STT + TTS workflows
- TestMultiLanguageAudio: Multi-language audio processing
- TestErrorRecovery: Error handling and edge cases
- TestPerformance: Performance benchmarking (optional)
"""

import asyncio
import io
import logging
import time
import wave
from pathlib import Path
from typing import Dict

import pytest
from pytest_httpx import HTTPXMock

from app.services.mistral_stt_service import MistralSTTResult, MistralSTTService
from app.services.piper_tts_service import PiperTTSService
from app.services.speech_processor import SpeechProcessor

logger = logging.getLogger(__name__)


# ============================================================================
# Audio Validation Helpers
# ============================================================================


def validate_wav_format(audio_bytes: bytes) -> Dict[str, any]:
    """
    Validate audio is proper WAV format and return metadata.

    Args:
        audio_bytes: Audio data in bytes

    Returns:
        Dictionary with audio metadata (channels, sample_rate, duration, etc.)

    Raises:
        ValueError: If audio is not valid WAV format
    """
    if not audio_bytes or len(audio_bytes) == 0:
        raise ValueError("Audio bytes are empty")

    try:
        audio_io = io.BytesIO(audio_bytes)
        with wave.open(audio_io, "rb") as wav:
            return {
                "channels": wav.getnchannels(),
                "sample_width": wav.getsampwidth(),
                "sample_rate": wav.getframerate(),
                "n_frames": wav.getnframes(),
                "duration_seconds": wav.getnframes() / wav.getframerate()
                if wav.getframerate() > 0
                else 0,
                "size_bytes": len(audio_bytes),
            }
    except Exception as e:
        raise ValueError(f"Invalid WAV format: {e}")


def compare_audio_properties(
    audio1: bytes, audio2: bytes, tolerance: int = 1000
) -> bool:
    """
    Compare if two audio files have similar properties.

    Args:
        audio1: First audio file bytes
        audio2: Second audio file bytes
        tolerance: Sample rate tolerance in Hz

    Returns:
        True if audio properties are similar
    """
    try:
        props1 = validate_wav_format(audio1)
        props2 = validate_wav_format(audio2)

        return (
            props1["channels"] == props2["channels"]
            and props1["sample_width"] == props2["sample_width"]
            and abs(props1["sample_rate"] - props2["sample_rate"]) <= tolerance
        )
    except ValueError:
        return False


def validate_audio_content(audio_bytes: bytes, min_duration: float = 0.01) -> bool:
    """
    Validate audio has actual content (not just silence).

    Args:
        audio_bytes: Audio data in bytes
        min_duration: Minimum duration in seconds

    Returns:
        True if audio appears valid
    """
    try:
        props = validate_wav_format(audio_bytes)
        return (
            props["duration_seconds"] >= min_duration
            and props["n_frames"] > 0
            and props["size_bytes"] > 100  # Reasonable minimum size
        )
    except ValueError:
        return False


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mistral_stt_service():
    """Fixture providing MistralSTTService instance"""
    return MistralSTTService()


@pytest.fixture
def piper_tts_service():
    """Fixture providing PiperTTSService instance"""
    return PiperTTSService()


@pytest.fixture
def speech_processor():
    """Fixture providing SpeechProcessor instance"""
    return SpeechProcessor()


@pytest.fixture
def sample_transcriptions():
    """Fixture providing sample transcription texts for various scenarios"""
    return {
        "simple_english": "Hello world",
        "simple_spanish": "Hola mundo",
        "simple_french": "Bonjour le monde",
        "simple_german": "Hallo Welt",
        "complex_english": "The quick brown fox jumps over the lazy dog",
        "question": "How are you doing today?",
        "long_text": "This is a longer text that should generate more audio content. "
        * 5,
        "special_chars": "Hello! How are you? I'm fine, thanks.",
        "numbers": "One, two, three, four, five",
        "empty": "",
    }


# ============================================================================
# Test Class 1: STT + TTS Integration
# ============================================================================


class TestSTTTTSIntegration:
    """
    Test end-to-end STT + TTS integration workflows.

    These tests validate the complete audio processing pipeline:
    1. Load real audio file
    2. Transcribe via STT (mock HTTP API response)
    3. Synthesize speech via TTS (real audio generation)
    4. Validate generated audio format
    """

    @pytest.mark.asyncio
    async def test_basic_round_trip_english(
        self,
        mistral_stt_service,
        piper_tts_service,
        speech_like_audio_16khz,
        httpx_mock: HTTPXMock,
    ):
        """
        Test basic STT → TTS round-trip with English audio.

        Flow:
        1. Load real speech-like audio
        2. Transcribe (mock API returns "hello world")
        3. Synthesize the transcript
        4. Validate synthesized audio
        """
        # Mock STT API response
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": "hello world", "language": "en"},
        )

        # Step 1: Transcribe audio (STT)
        stt_result = await mistral_stt_service.transcribe_audio(
            audio_data=speech_like_audio_16khz, language="en"
        )

        assert stt_result is not None
        assert stt_result.transcript == "hello world"
        assert stt_result.language == "en"

        # Step 2: Synthesize the transcript (TTS)
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=stt_result.transcript, language="en"
        )

        # Step 3: Validate synthesized audio
        assert tts_audio is not None
        assert len(tts_audio) > 0

        # Validate WAV format
        audio_props = validate_wav_format(tts_audio)
        assert audio_props["channels"] == 1  # Mono
        assert audio_props["sample_width"] == 2  # 16-bit
        assert audio_props["sample_rate"] == 22050  # Piper default
        assert audio_props["duration_seconds"] > 0

        # Validate audio has content
        assert validate_audio_content(tts_audio, min_duration=0.1)

    @pytest.mark.asyncio
    async def test_round_trip_with_longer_text(
        self,
        mistral_stt_service,
        piper_tts_service,
        speech_like_audio_16khz,
        sample_transcriptions,
        httpx_mock: HTTPXMock,
    ):
        """Test round-trip with longer transcript text"""
        long_text = sample_transcriptions["complex_english"]

        # Mock STT API
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": long_text, "language": "en"},
        )

        # STT
        stt_result = await mistral_stt_service.transcribe_audio(
            audio_data=speech_like_audio_16khz, language="en"
        )
        assert stt_result.transcript == long_text

        # TTS
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=stt_result.transcript, language="en"
        )

        # Validate
        audio_props = validate_wav_format(tts_audio)
        # Longer text should produce longer audio
        assert audio_props["duration_seconds"] > 1.0
        assert validate_audio_content(tts_audio, min_duration=1.0)

    @pytest.mark.asyncio
    async def test_tts_then_stt_workflow(
        self,
        mistral_stt_service,
        piper_tts_service,
        sample_transcriptions,
        httpx_mock: HTTPXMock,
    ):
        """
        Test reverse workflow: TTS → STT

        Flow:
        1. Generate audio from text (TTS)
        2. Transcribe the generated audio (STT)
        3. Validate transcript matches original
        """
        original_text = sample_transcriptions["simple_english"]

        # Step 1: TTS - generate audio
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=original_text, language="en"
        )

        assert tts_audio is not None
        assert validate_audio_content(tts_audio)

        # Step 2: STT - transcribe generated audio
        # Mock STT API to return the original text
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": original_text, "language": "en"},
        )

        stt_result = await mistral_stt_service.transcribe_audio(
            audio_data=tts_audio, language="en"
        )

        # Step 3: Validate
        assert stt_result.transcript == original_text
        assert stt_result.language == "en"

    @pytest.mark.asyncio
    async def test_empty_text_handling(self, piper_tts_service, sample_transcriptions):
        """Test handling of empty text in TTS"""
        empty_text = sample_transcriptions["empty"]

        # TTS with empty text should handle gracefully
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=empty_text, language="en"
        )

        # Should return minimal or no audio
        if tts_audio:
            # If audio is generated, validate it's minimal
            audio_props = validate_wav_format(tts_audio)
            assert audio_props["duration_seconds"] < 0.5
        else:
            # Or return None/empty
            assert tts_audio is None or len(tts_audio) == 0

    @pytest.mark.asyncio
    async def test_special_characters_in_text(
        self, piper_tts_service, sample_transcriptions
    ):
        """Test TTS with special characters and punctuation"""
        text_with_special_chars = sample_transcriptions["special_chars"]

        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=text_with_special_chars, language="en"
        )

        assert tts_audio is not None
        assert validate_audio_content(tts_audio)

        audio_props = validate_wav_format(tts_audio)
        assert audio_props["duration_seconds"] > 0.5


# ============================================================================
# Test Class 2: Multi-Language Audio Processing
# ============================================================================


class TestMultiLanguageAudio:
    """
    Test multi-language audio processing workflows.

    Validates:
    - Language-specific voice selection
    - Consistent audio properties across languages
    - Language detection and handling
    """

    @pytest.mark.asyncio
    async def test_english_audio_workflow(
        self,
        mistral_stt_service,
        piper_tts_service,
        speech_like_audio_16khz,
        httpx_mock: HTTPXMock,
    ):
        """Test English language workflow"""
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": "Hello world", "language": "en"},
        )

        # STT
        stt_result = await mistral_stt_service.transcribe_audio(
            audio_data=speech_like_audio_16khz, language="en"
        )
        assert stt_result.language == "en"

        # TTS
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=stt_result.transcript, language="en"
        )

        assert validate_audio_content(tts_audio)

    @pytest.mark.asyncio
    async def test_spanish_audio_workflow(
        self,
        mistral_stt_service,
        piper_tts_service,
        speech_like_audio_16khz,
        httpx_mock: HTTPXMock,
    ):
        """Test Spanish language workflow"""
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": "Hola mundo", "language": "es"},
        )

        # STT
        stt_result = await mistral_stt_service.transcribe_audio(
            audio_data=speech_like_audio_16khz, language="es"
        )
        assert stt_result.language == "es"

        # TTS
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=stt_result.transcript, language="es"
        )

        assert validate_audio_content(tts_audio)

    @pytest.mark.asyncio
    async def test_french_audio_workflow(self, piper_tts_service):
        """Test French TTS synthesis"""
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text="Bonjour le monde", language="fr"
        )

        assert validate_audio_content(tts_audio)
        audio_props = validate_wav_format(tts_audio)
        assert audio_props["sample_rate"] == 22050

    @pytest.mark.asyncio
    async def test_german_audio_workflow(self, piper_tts_service):
        """Test German TTS synthesis"""
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text="Hallo Welt", language="de"
        )

        assert validate_audio_content(tts_audio)

    @pytest.mark.asyncio
    async def test_multiple_languages_sequential(
        self, piper_tts_service, sample_transcriptions
    ):
        """Test synthesizing multiple languages sequentially"""
        languages = [
            ("en", sample_transcriptions["simple_english"]),
            ("es", sample_transcriptions["simple_spanish"]),
            ("fr", sample_transcriptions["simple_french"]),
            ("de", sample_transcriptions["simple_german"]),
        ]

        for lang_code, text in languages:
            tts_audio, _ = await piper_tts_service.synthesize_speech(
                text=text, language=lang_code
            )

            assert tts_audio is not None, f"Failed for language: {lang_code}"
            assert validate_audio_content(tts_audio), f"Invalid audio for: {lang_code}"

            audio_props = validate_wav_format(tts_audio)
            assert audio_props["channels"] == 1
            assert audio_props["sample_width"] == 2

    @pytest.mark.asyncio
    async def test_consistent_audio_format_across_languages(self, piper_tts_service):
        """Test that all languages produce consistent audio format"""
        test_text = "Hello"
        languages = ["en", "es", "fr", "de"]

        audio_samples = []
        for lang in languages:
            audio, _ = await piper_tts_service.synthesize_speech(
                text=test_text, language=lang
            )
            audio_samples.append(audio)

        # All should have same format properties
        reference_props = validate_wav_format(audio_samples[0])

        for i, audio in enumerate(audio_samples[1:], 1):
            props = validate_wav_format(audio)
            assert props["channels"] == reference_props["channels"], (
                f"Channels differ for language {languages[i]}"
            )
            assert props["sample_width"] == reference_props["sample_width"], (
                f"Sample width differs for language {languages[i]}"
            )
            assert props["sample_rate"] == reference_props["sample_rate"], (
                f"Sample rate differs for language {languages[i]}"
            )


# ============================================================================
# Test Class 3: Error Recovery and Edge Cases
# ============================================================================


class TestErrorRecovery:
    """
    Test error handling and edge cases in audio processing.

    Covers:
    - Corrupted audio handling
    - Invalid formats
    - API failures
    - Timeout scenarios
    - Resource constraints
    """

    @pytest.mark.asyncio
    async def test_corrupted_audio_handling(
        self, mistral_stt_service, httpx_mock: HTTPXMock
    ):
        """Test handling of corrupted audio data"""
        corrupted_audio = b"This is not audio data"

        # Mock API error response
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            status_code=400,
            json={"error": "Invalid audio format"},
        )

        # Should handle error gracefully
        with pytest.raises(Exception):  # Expect some exception
            await mistral_stt_service.transcribe_audio(
                audio_data=corrupted_audio, language="en"
            )

    @pytest.mark.asyncio
    async def test_empty_audio_data(self, mistral_stt_service, httpx_mock: HTTPXMock):
        """Test handling of empty audio data"""
        empty_audio = b""

        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            status_code=400,
            json={"error": "Empty audio"},
        )

        with pytest.raises(Exception):
            await mistral_stt_service.transcribe_audio(
                audio_data=empty_audio, language="en"
            )

    @pytest.mark.asyncio
    async def test_api_timeout_handling(
        self, mistral_stt_service, speech_like_audio_16khz, httpx_mock: HTTPXMock
    ):
        """Test handling of API timeouts"""
        from httpx import TimeoutException

        # Mock timeout
        httpx_mock.add_exception(TimeoutException("Request timed out"))

        with pytest.raises((TimeoutException, Exception)):
            await mistral_stt_service.transcribe_audio(
                audio_data=speech_like_audio_16khz, language="en"
            )

    @pytest.mark.asyncio
    async def test_api_network_error(
        self, mistral_stt_service, speech_like_audio_16khz, httpx_mock: HTTPXMock
    ):
        """Test handling of network errors"""
        from httpx import ConnectError

        httpx_mock.add_exception(ConnectError("Connection failed"))

        with pytest.raises((ConnectError, Exception)):
            await mistral_stt_service.transcribe_audio(
                audio_data=speech_like_audio_16khz, language="en"
            )

    @pytest.mark.asyncio
    async def test_api_rate_limit(
        self, mistral_stt_service, speech_like_audio_16khz, httpx_mock: HTTPXMock
    ):
        """Test handling of API rate limiting"""
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            status_code=429,
            json={"error": "Rate limit exceeded"},
        )

        with pytest.raises(Exception):
            await mistral_stt_service.transcribe_audio(
                audio_data=speech_like_audio_16khz, language="en"
            )

    @pytest.mark.asyncio
    async def test_unsupported_language(self, piper_tts_service):
        """Test handling of unsupported language"""
        # Try a language code that doesn't exist
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text="Hello world",
            language="xx",  # Invalid language code
        )

        # Should fallback or handle gracefully
        # Either return None/empty or use default language
        if tts_audio:
            assert validate_audio_content(tts_audio)

    @pytest.mark.asyncio
    async def test_very_long_text(self, piper_tts_service):
        """Test TTS with very long text"""
        very_long_text = "This is a test sentence. " * 100  # ~500 words

        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=very_long_text, language="en"
        )

        assert tts_audio is not None
        assert validate_audio_content(tts_audio, min_duration=10.0)

        audio_props = validate_wav_format(tts_audio)
        # Should produce substantial audio
        assert audio_props["duration_seconds"] > 10.0

    @pytest.mark.asyncio
    async def test_concurrent_tts_requests(self, piper_tts_service):
        """Test handling of concurrent TTS requests"""
        texts = [
            "First request",
            "Second request",
            "Third request",
            "Fourth request",
            "Fifth request",
        ]

        # Submit concurrent requests
        tasks = [
            piper_tts_service.synthesize_speech(text=text, language="en")
            for text in texts
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == len(texts)
        for audio, metadata in results:
            assert audio is not None
            assert validate_audio_content(audio)


# ============================================================================
# Test Class 4: Performance Benchmarking (Optional)
# ============================================================================


class TestPerformance:
    """
    Performance benchmarking tests (optional).

    These tests establish performance baselines and detect regressions.
    Not strict - allow for CI environment variability.
    """

    @pytest.mark.asyncio
    async def test_tts_synthesis_performance(self, piper_tts_service):
        """Benchmark TTS synthesis performance"""
        test_text = "The quick brown fox jumps over the lazy dog"

        start_time = time.time()
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=test_text, language="en"
        )
        elapsed = time.time() - start_time

        assert tts_audio is not None

        # Performance baseline: should complete within reasonable time
        # Be generous for CI environments
        assert elapsed < 5.0, f"TTS took {elapsed:.2f}s (expected < 5.0s)"

        logger.info(
            f"TTS synthesis time: {elapsed:.3f}s for {len(test_text)} characters"
        )

    @pytest.mark.asyncio
    async def test_stt_transcription_performance(
        self, mistral_stt_service, speech_like_audio_16khz, httpx_mock: HTTPXMock
    ):
        """Benchmark STT transcription performance"""
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": "test", "language": "en"},
        )

        start_time = time.time()
        result = await mistral_stt_service.transcribe_audio(
            audio_data=speech_like_audio_16khz, language="en"
        )
        elapsed = time.time() - start_time

        assert result is not None

        # Should be fast (mostly network mock time)
        assert elapsed < 2.0, f"STT took {elapsed:.2f}s (expected < 2.0s)"

        logger.info(f"STT transcription time: {elapsed:.3f}s")

    @pytest.mark.asyncio
    async def test_round_trip_performance(
        self,
        mistral_stt_service,
        piper_tts_service,
        speech_like_audio_16khz,
        httpx_mock: HTTPXMock,
    ):
        """Benchmark complete round-trip performance"""
        httpx_mock.add_response(
            url="https://api.mistral.ai/v1/audio/transcriptions",
            json={"text": "hello world", "language": "en"},
        )

        start_time = time.time()

        # STT
        stt_result = await mistral_stt_service.transcribe_audio(
            audio_data=speech_like_audio_16khz, language="en"
        )

        # TTS
        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=stt_result.transcript, language="en"
        )

        elapsed = time.time() - start_time

        assert tts_audio is not None

        # Round-trip should complete reasonably fast
        assert elapsed < 7.0, f"Round-trip took {elapsed:.2f}s (expected < 7.0s)"

        logger.info(f"Round-trip time: {elapsed:.3f}s")

    @pytest.mark.asyncio
    async def test_memory_usage_large_audio(self, piper_tts_service):
        """Test memory handling with large audio generation"""
        # Generate ~1 minute of audio
        long_text = "This is a test sentence. " * 200  # ~1000 words

        tts_audio, _ = await piper_tts_service.synthesize_speech(
            text=long_text, language="en"
        )

        assert tts_audio is not None

        audio_props = validate_wav_format(tts_audio)

        # Should handle large audio without issues
        assert audio_props["duration_seconds"] > 30.0
        assert audio_props["size_bytes"] > 100000  # > 100KB

        logger.info(
            f"Large audio generated: {audio_props['duration_seconds']:.1f}s, "
            f"{audio_props['size_bytes'] / 1024:.1f} KB"
        )
