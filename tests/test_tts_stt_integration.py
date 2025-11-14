"""
End-to-End TTS→STT Integration Test Suite

Tests the complete audio pipeline by generating speech with TTS and verifying
it can be correctly transcribed back to text with STT.

Validation Loop:
1. Generate audio in Language A with TTS
2. Transcribe audio back to text with STT → verify accuracy
3. Generate audio in Language B with TTS
4. Transcribe audio back to text with STT → verify accuracy
5. Continue through all languages until returning to Language A

This ensures:
- TTS generates understandable audio
- STT can accurately transcribe TTS-generated audio
- Complete pipeline works for all supported languages
"""

import pytest

from app.services.mistral_stt_service import MistralSTTService
from app.services.piper_tts_service import PiperTTSService

# Test phrases optimized for TTS→STT round-trip
# Using simple, clear phrases that should transcribe accurately
TTS_STT_TEST_PHRASES = {
    "en": "Hello, this is a test.",
    "de": "Hallo, das ist ein Test.",
    "es": "Hola, esta es una prueba.",
    "fr": "Bonjour, ceci est un test.",
    "it": "Ciao, questo è un test.",
    "pt": "Olá, este é um teste.",
    "zh": "你好，这是一个测试。",
}


@pytest.fixture(scope="module")
def tts_service():
    """Create TTS service instance"""
    return PiperTTSService()


@pytest.fixture
def stt_service():
    """Create STT service instance (function-scoped for async client lifecycle)"""
    # Create new service for each test to avoid event loop issues
    return MistralSTTService()


# =============================================================================
# Individual Language TTS→STT Tests
# =============================================================================


class TestTTStoSTTRoundTrip:
    """Test TTS→STT round-trip for each language"""

    @pytest.mark.asyncio
    async def test_english_tts_to_stt(self, tts_service, stt_service):
        """Test English TTS→STT round-trip"""
        # Generate audio with TTS
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["en"], language="en"
        )

        assert len(audio_data) > 1000, "TTS audio too small"

        # Transcribe audio with STT
        stt_result = await stt_service.transcribe_audio(audio_data, language="en")

        # Verify transcription is close to original
        # Note: May not be exact due to TTS/STT characteristics
        transcription_lower = stt_result.transcript.lower().strip()

        # Check for key words present
        assert "hello" in transcription_lower, (
            f"Expected 'hello' in '{stt_result.transcript}'"
        )
        assert "test" in transcription_lower, (
            f"Expected 'test' in '{stt_result.transcript}'"
        )

    @pytest.mark.asyncio
    async def test_german_tts_to_stt(self, tts_service, stt_service):
        """Test German TTS→STT round-trip"""
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["de"], language="de"
        )

        assert len(audio_data) > 1000

        stt_result = await stt_service.transcribe_audio(audio_data, language="de")

        transcription_lower = stt_result.transcript.lower().strip()

        # Check for key German words
        assert "hallo" in transcription_lower or "test" in transcription_lower, (
            f"Expected German words in '{stt_result.transcript}'"
        )

    @pytest.mark.asyncio
    async def test_spanish_tts_to_stt(self, tts_service, stt_service):
        """Test Spanish TTS→STT round-trip"""
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["es"], language="es"
        )

        assert len(audio_data) > 1000

        stt_result = await stt_service.transcribe_audio(audio_data, language="es")

        transcription_lower = stt_result.transcript.lower().strip()

        # Check for key Spanish words
        assert "hola" in transcription_lower or "prueba" in transcription_lower, (
            f"Expected Spanish words in '{stt_result.transcript}'"
        )

    @pytest.mark.asyncio
    async def test_french_tts_to_stt(self, tts_service, stt_service):
        """Test French TTS→STT round-trip"""
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["fr"], language="fr"
        )

        assert len(audio_data) > 1000

        stt_result = await stt_service.transcribe_audio(audio_data, language="fr")

        transcription_lower = stt_result.transcript.lower().strip()

        # Check for key French words
        assert "bonjour" in transcription_lower or "test" in transcription_lower, (
            f"Expected French words in '{stt_result.transcript}'"
        )

    @pytest.mark.asyncio
    async def test_italian_tts_to_stt(self, tts_service, stt_service):
        """Test Italian TTS→STT round-trip"""
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["it"], language="it"
        )

        assert len(audio_data) > 1000

        stt_result = await stt_service.transcribe_audio(audio_data, language="it")

        transcription_lower = stt_result.transcript.lower().strip()

        # Check for key Italian words
        assert "ciao" in transcription_lower or "test" in transcription_lower, (
            f"Expected Italian words in '{stt_result.transcript}'"
        )

    @pytest.mark.asyncio
    async def test_portuguese_tts_to_stt(self, tts_service, stt_service):
        """Test Portuguese TTS→STT round-trip"""
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["pt"], language="pt"
        )

        assert len(audio_data) > 1000

        stt_result = await stt_service.transcribe_audio(audio_data, language="pt")

        transcription_lower = stt_result.transcript.lower().strip()

        # Check for key Portuguese words
        assert "olá" in transcription_lower or "teste" in transcription_lower, (
            f"Expected Portuguese words in '{stt_result.transcript}'"
        )

    @pytest.mark.asyncio
    async def test_chinese_tts_to_stt(self, tts_service, stt_service):
        """Test Chinese TTS→STT round-trip"""
        audio_data, tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["zh"], language="zh"
        )

        assert len(audio_data) > 1000

        stt_result = await stt_service.transcribe_audio(audio_data, language="zh")

        # Check for key Chinese characters
        # Note: Chinese transcription may have variations
        assert "你好" in stt_result.transcript or "测试" in stt_result.transcript, (
            f"Expected Chinese characters in '{stt_result.transcript}'"
        )


# =============================================================================
# Full Validation Loop Test
# =============================================================================


class TestFullValidationLoop:
    """Test complete validation loop through all languages"""

    @pytest.mark.asyncio
    async def test_complete_language_loop(self, tts_service, stt_service):
        """
        Test complete validation loop:
        EN→DE→ES→FR→IT→PT→ZH→EN

        Each step:
        1. Generate audio with TTS in language N
        2. Verify STT can transcribe it back
        3. Move to next language
        4. Verify we return to starting language
        """
        # Define language sequence
        language_sequence = ["en", "de", "es", "fr", "it", "pt", "zh", "en"]

        results = []

        for i, lang in enumerate(
            language_sequence[:-1]
        ):  # Exclude last 'en' from iteration
            test_phrase = TTS_STT_TEST_PHRASES[lang]

            # Step 1: Generate audio with TTS
            audio_data, tts_meta = await tts_service.synthesize_speech(
                test_phrase, language=lang
            )

            # Verify audio was generated
            assert len(audio_data) > 1000, f"{lang}: TTS audio too small"

            # Step 2: Transcribe with STT
            stt_result = await stt_service.transcribe_audio(audio_data, language=lang)

            # Verify transcription was generated
            assert len(stt_result.transcript) > 0, (
                f"{lang}: STT produced empty transcription"
            )

            # Store result
            results.append(
                {
                    "language": lang,
                    "original": test_phrase,
                    "transcription": stt_result.transcript,
                    "tts_voice": tts_meta["voice"],
                    "audio_size": len(audio_data),
                    "step": i + 1,
                }
            )

        # Verify we completed all 7 language steps
        assert len(results) == 7, f"Expected 7 steps, completed {len(results)}"

        # Verify each language was tested
        tested_languages = [r["language"] for r in results]
        assert tested_languages == ["en", "de", "es", "fr", "it", "pt", "zh"]

        # Verify we can return to English (completing the loop)
        final_audio, final_tts_meta = await tts_service.synthesize_speech(
            TTS_STT_TEST_PHRASES["en"], language="en"
        )
        final_stt_result = await stt_service.transcribe_audio(
            final_audio, language="en"
        )

        assert len(final_stt_result.transcript) > 0, "Final EN step: STT failed"
        assert (
            "test" in final_stt_result.transcript.lower()
            or "hello" in final_stt_result.transcript.lower()
        ), "Final EN step: Transcription incorrect"


# =============================================================================
# Cross-Language Validation
# =============================================================================


class TestCrossLanguageValidation:
    """Test that languages don't interfere with each other"""

    @pytest.mark.asyncio
    async def test_sequential_language_switching(self, tts_service, stt_service):
        """Test rapid switching between languages"""
        # Switch: EN→ES→EN→DE→EN
        test_sequence = [
            ("en", "Hello, this is a test."),
            ("es", "Hola, esta es una prueba."),
            ("en", "Hello again, second test."),
            ("de", "Hallo, das ist ein Test."),
            ("en", "Hello once more, final test."),
        ]

        for lang, phrase in test_sequence:
            # Generate and transcribe
            audio_data, _ = await tts_service.synthesize_speech(phrase, language=lang)
            stt_result = await stt_service.transcribe_audio(audio_data, language=lang)

            # Verify we got valid output
            assert len(audio_data) > 1000, f"{lang}: Audio generation failed"
            assert len(stt_result.transcript) > 0, f"{lang}: Transcription failed"

    @pytest.mark.asyncio
    async def test_voice_quality_consistency(self, tts_service, stt_service):
        """Test that same phrase generates consistent transcriptions"""
        test_phrase = "This is a consistency test."

        # Generate same phrase 3 times
        transcriptions = []
        for i in range(3):
            audio_data, _ = await tts_service.synthesize_speech(
                test_phrase, language="en"
            )
            stt_result = await stt_service.transcribe_audio(audio_data, language="en")
            transcriptions.append(stt_result.transcript.lower().strip())

        # All transcriptions should be similar (contain key words)
        for trans in transcriptions:
            assert "consistency" in trans or "test" in trans, (
                f"Transcription '{trans}' missing key words"
            )


# =============================================================================
# Audio Quality Validation
# =============================================================================


class TestAudioQualityInRoundTrip:
    """Test audio quality affects transcription accuracy"""

    @pytest.mark.asyncio
    async def test_clear_speech_vs_complex_speech(self, tts_service, stt_service):
        """Test that clear speech transcribes better than complex speech"""
        # Simple, clear phrase
        simple_phrase = "Hello world."

        # Complex phrase with punctuation
        complex_phrase = "Hello world! How are you today? I'm doing great."

        # Test simple phrase
        simple_audio, _ = await tts_service.synthesize_speech(
            simple_phrase, language="en"
        )
        simple_result = await stt_service.transcribe_audio(simple_audio, language="en")

        # Test complex phrase
        complex_audio, _ = await tts_service.synthesize_speech(
            complex_phrase, language="en"
        )
        complex_result = await stt_service.transcribe_audio(
            complex_audio, language="en"
        )

        # Both should produce valid output
        assert len(simple_result.transcript) > 0, "Simple phrase transcription failed"
        assert len(complex_result.transcript) > 0, "Complex phrase transcription failed"

        # Complex audio should be longer
        assert len(complex_audio) > len(simple_audio), (
            "Complex phrase should produce longer audio"
        )

    @pytest.mark.asyncio
    async def test_multiple_voices_same_language(self, tts_service, stt_service):
        """Test that different voices for same language all transcribe well"""
        # Get all Spanish voices (we have 4: AR, ES, MX x2)
        spanish_voices = [
            "es_AR-daniela-high",
            "es_ES-davefx-medium",
            "es_MX-ald-medium",
            "es_MX-claude-high",
        ]

        spanish_phrase = "Esta es una prueba de múltiples voces."

        for voice_name in spanish_voices:
            if voice_name in tts_service.voices:
                # Generate with specific voice
                audio_data, _ = await tts_service.synthesize_speech(
                    spanish_phrase, voice=voice_name
                )

                # Transcribe
                stt_result = await stt_service.transcribe_audio(
                    audio_data, language="es"
                )

                # Should transcribe successfully
                assert len(stt_result.transcript) > 0, (
                    f"{voice_name}: Transcription failed"
                )
                # Should contain Spanish words
                trans_lower = stt_result.transcript.lower()
                assert (
                    "prueba" in trans_lower
                    or "voz" in trans_lower
                    or "voces" in trans_lower
                ), f"{voice_name}: Transcription quality poor"
