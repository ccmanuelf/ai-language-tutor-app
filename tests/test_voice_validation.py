"""
Voice Validation Test Suite

Tests all installed Piper TTS voice models for functionality and quality.

Available Voices (11 working):
- en_US-lessac-medium (English US)
- de_DE-thorsten-medium (German)
- es_AR-daniela-high (Spanish Argentina)
- es_ES-davefx-medium (Spanish Spain)
- es_MX-ald-medium (Spanish Mexico)
- es_MX-claude-high (Spanish Mexico - currently mapped)
- fr_FR-siwis-medium (French)
- it_IT-paola-medium (Italian - currently mapped)
- it_IT-riccardo-x_low (Italian low quality)
- pt_BR-faber-medium (Portuguese Brazil)
- zh_CN-huayan-medium (Chinese Simplified)
"""

import io
import wave
from pathlib import Path

import pytest

from app.services.piper_tts_service import PiperTTSService

# Test phrases for each language
TEST_PHRASES = {
    "en": "Hello, this is a test of the text to speech system.",
    "de": "Hallo, dies ist ein Test des Text-zu-Sprache-Systems.",
    "es": "Hola, esta es una prueba del sistema de texto a voz.",
    "fr": "Bonjour, ceci est un test du système de synthèse vocale.",
    "it": "Ciao, questo è un test del sistema di sintesi vocale.",
    "pt": "Olá, este é um teste do sistema de conversão de texto em fala.",
    "zh": "你好，这是文本转语音系统的测试。",
}


# Expected voice model sizes (in MB, approximate)
EXPECTED_VOICE_SIZES = {
    "en_US-lessac-medium": (55, 65),  # ~60MB
    "de_DE-thorsten-medium": (55, 65),  # ~60MB
    "es_AR-daniela-high": (100, 120),  # ~109MB (high quality)
    "es_ES-davefx-medium": (55, 65),  # ~60MB
    "es_MX-ald-medium": (55, 65),  # ~60MB
    "es_MX-claude-high": (55, 65),  # ~60MB
    "fr_FR-siwis-medium": (55, 65),  # ~60MB
    "it_IT-paola-medium": (55, 70),  # ~61MB
    "it_IT-riccardo-x_low": (20, 35),  # ~27MB (low quality)
    "pt_BR-faber-medium": (55, 65),  # ~60MB
    "zh_CN-huayan-medium": (55, 65),  # ~60MB
}


@pytest.fixture(scope="module")
def tts_service():
    """Create TTS service instance for tests"""
    service = PiperTTSService()
    return service


@pytest.fixture(scope="module")
def voices_directory():
    """Get path to voices directory"""
    return Path("app/data/piper_voices")


# =============================================================================
# Voice Installation Validation
# =============================================================================


class TestVoiceInstallation:
    """Validate voice model installation and integrity"""

    def test_voices_directory_exists(self, voices_directory):
        """Test that voices directory exists"""
        assert voices_directory.exists(), "Voices directory not found"
        assert voices_directory.is_dir(), "Voices path is not a directory"

    def test_all_voice_models_present(self, voices_directory):
        """Test that all expected voice models are present"""
        onnx_files = list(voices_directory.glob("*.onnx"))
        voice_names = [f.stem for f in onnx_files]

        # Should have 11 voice models (corrupted voice removed)
        assert len(voice_names) == 11, f"Expected 11 voices, found {len(voice_names)}"

        # Check for each expected voice
        expected_voices = list(EXPECTED_VOICE_SIZES.keys())
        for expected_voice in expected_voices:
            assert expected_voice in voice_names, (
                f"Voice model {expected_voice} not found"
            )

    def test_all_voice_configs_present(self, voices_directory):
        """Test that all voice models have corresponding config files"""
        onnx_files = list(voices_directory.glob("*.onnx"))

        for onnx_file in onnx_files:
            config_file = onnx_file.with_suffix(".onnx.json")
            assert config_file.exists(), f"Config file missing for {onnx_file.name}"

    def test_voice_model_sizes(self, voices_directory):
        """Test that voice models have expected file sizes"""
        for voice_name, (min_mb, max_mb) in EXPECTED_VOICE_SIZES.items():
            onnx_file = voices_directory / f"{voice_name}.onnx"
            assert onnx_file.exists(), f"Voice model {voice_name} not found"

            file_size_mb = onnx_file.stat().st_size / (1024 * 1024)
            assert min_mb <= file_size_mb <= max_mb, (
                f"{voice_name}: Size {file_size_mb:.1f}MB outside expected range {min_mb}-{max_mb}MB"
            )


# =============================================================================
# Service Voice Loading
# =============================================================================


class TestServiceVoiceLoading:
    """Test that TTS service correctly loads voices"""

    def test_service_loads_voices(self, tts_service):
        """Test that service successfully loads voices"""
        available_voices = tts_service.get_available_voices()

        # Should load 11 working voices (excluding corrupted es_MX-davefx-medium)
        # Note: Service may skip corrupted voice during loading
        assert len(available_voices) >= 11, (
            f"Expected at least 11 voices, found {len(available_voices)}"
        )

    def test_service_voice_info_complete(self, tts_service):
        """Test that loaded voices have complete information"""
        for voice_name, voice_info in tts_service.voices.items():
            assert "model_path" in voice_info, f"{voice_name}: Missing model_path"
            assert "config_path" in voice_info, f"{voice_name}: Missing config_path"
            assert "language" in voice_info, f"{voice_name}: Missing language"
            assert "sample_rate" in voice_info, f"{voice_name}: Missing sample_rate"
            assert "config" in voice_info, f"{voice_name}: Missing config"

    def test_service_language_mappings(self, tts_service):
        """Test that service has correct language mappings"""
        expected_mappings = {
            "en": "en_US-lessac-medium",
            "es": "es_MX-claude-high",
            "fr": "fr_FR-siwis-medium",
            "de": "de_DE-thorsten-medium",
            "it": "it_IT-paola-medium",
            "pt": "pt_BR-faber-medium",
            "zh": "zh_CN-huayan-medium",
        }

        for lang, expected_voice in expected_mappings.items():
            mapped_voice = tts_service.get_voice_for_language(lang)
            assert mapped_voice == expected_voice, (
                f"Language {lang}: Expected {expected_voice}, got {mapped_voice}"
            )


# =============================================================================
# Individual Voice Testing
# =============================================================================


class TestEnglishVoices:
    """Test English voice models"""

    @pytest.mark.asyncio
    async def test_en_US_lessac_medium(self, tts_service):
        """Test en_US-lessac-medium voice"""
        if "en_US-lessac-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["en"], voice="en_US-lessac-medium"
        )

        # Validate audio
        assert len(audio_data) > 1000, "Audio data too small"
        assert metadata["voice"] == "en_US-lessac-medium"
        assert metadata["sample_rate"] == 22050

        # Validate WAV format
        audio_io = io.BytesIO(audio_data)
        with wave.open(audio_io, "rb") as wav:
            assert wav.getnchannels() == 1  # Mono
            assert wav.getsampwidth() == 2  # 16-bit
            assert wav.getframerate() == 22050


class TestGermanVoices:
    """Test German voice models"""

    @pytest.mark.asyncio
    async def test_de_DE_thorsten_medium(self, tts_service):
        """Test de_DE-thorsten-medium voice"""
        if "de_DE-thorsten-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["de"], voice="de_DE-thorsten-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "de_DE-thorsten-medium"
        assert metadata["sample_rate"] == 22050

        # Validate WAV format
        audio_io = io.BytesIO(audio_data)
        with wave.open(audio_io, "rb") as wav:
            assert wav.getnchannels() == 1
            assert wav.getsampwidth() == 2


class TestSpanishVoices:
    """Test Spanish voice models"""

    @pytest.mark.asyncio
    async def test_es_AR_daniela_high(self, tts_service):
        """Test es_AR-daniela-high voice (high quality)"""
        if "es_AR-daniela-high" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["es"], voice="es_AR-daniela-high"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "es_AR-daniela-high"
        # High quality voice may have different sample rate
        assert metadata["sample_rate"] in [22050, 24000]

        audio_io = io.BytesIO(audio_data)
        with wave.open(audio_io, "rb") as wav:
            assert wav.getnchannels() == 1
            assert wav.getsampwidth() == 2

    @pytest.mark.asyncio
    async def test_es_ES_davefx_medium(self, tts_service):
        """Test es_ES-davefx-medium voice (Spain Spanish)"""
        if "es_ES-davefx-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["es"], voice="es_ES-davefx-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "es_ES-davefx-medium"
        assert metadata["sample_rate"] == 22050

    @pytest.mark.asyncio
    async def test_es_MX_ald_medium(self, tts_service):
        """Test es_MX-ald-medium voice"""
        if "es_MX-ald-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["es"], voice="es_MX-ald-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "es_MX-ald-medium"
        assert metadata["sample_rate"] == 22050

    @pytest.mark.asyncio
    async def test_es_MX_claude_high(self, tts_service):
        """Test es_MX-claude-high voice (currently mapped for Spanish)"""
        if "es_MX-claude-high" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["es"], voice="es_MX-claude-high"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "es_MX-claude-high"
        assert metadata["sample_rate"] == 22050


class TestFrenchVoices:
    """Test French voice models"""

    @pytest.mark.asyncio
    async def test_fr_FR_siwis_medium(self, tts_service):
        """Test fr_FR-siwis-medium voice"""
        if "fr_FR-siwis-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["fr"], voice="fr_FR-siwis-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "fr_FR-siwis-medium"
        assert metadata["sample_rate"] == 22050


class TestItalianVoices:
    """Test Italian voice models"""

    @pytest.mark.asyncio
    async def test_it_IT_paola_medium(self, tts_service):
        """Test it_IT-paola-medium voice (currently mapped)"""
        if "it_IT-paola-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["it"], voice="it_IT-paola-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "it_IT-paola-medium"
        assert metadata["sample_rate"] == 22050

    @pytest.mark.asyncio
    async def test_it_IT_riccardo_x_low(self, tts_service):
        """Test it_IT-riccardo-x_low voice (low quality)"""
        if "it_IT-riccardo-x_low" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["it"], voice="it_IT-riccardo-x_low"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "it_IT-riccardo-x_low"
        # Low quality voice may have different sample rate
        assert metadata["sample_rate"] in [16000, 22050]


class TestPortugueseVoices:
    """Test Portuguese voice models"""

    @pytest.mark.asyncio
    async def test_pt_BR_faber_medium(self, tts_service):
        """Test pt_BR-faber-medium voice"""
        if "pt_BR-faber-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["pt"], voice="pt_BR-faber-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "pt_BR-faber-medium"
        assert metadata["sample_rate"] == 22050


class TestChineseVoices:
    """Test Chinese voice models"""

    @pytest.mark.asyncio
    async def test_zh_CN_huayan_medium(self, tts_service):
        """Test zh_CN-huayan-medium voice"""
        if "zh_CN-huayan-medium" not in tts_service.voices:
            pytest.skip("Voice not available")

        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["zh"], voice="zh_CN-huayan-medium"
        )

        assert len(audio_data) > 1000
        assert metadata["voice"] == "zh_CN-huayan-medium"
        assert metadata["sample_rate"] == 22050


# =============================================================================
# Language-Specific Voice Selection
# =============================================================================


class TestLanguageVoiceSelection:
    """Test automatic voice selection by language"""

    @pytest.mark.asyncio
    async def test_english_language_selection(self, tts_service):
        """Test automatic English voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["en"], language="en"
        )

        assert metadata["voice"] == "en_US-lessac-medium"
        assert metadata["language"] == "en"
        assert len(audio_data) > 1000

    @pytest.mark.asyncio
    async def test_spanish_language_selection(self, tts_service):
        """Test automatic Spanish voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["es"], language="es"
        )

        assert metadata["voice"] == "es_MX-claude-high"
        assert metadata["language"] == "es"
        assert len(audio_data) > 1000

    @pytest.mark.asyncio
    async def test_german_language_selection(self, tts_service):
        """Test automatic German voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["de"], language="de"
        )

        assert metadata["voice"] == "de_DE-thorsten-medium"
        assert metadata["language"] == "de"
        assert len(audio_data) > 1000

    @pytest.mark.asyncio
    async def test_french_language_selection(self, tts_service):
        """Test automatic French voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["fr"], language="fr"
        )

        assert metadata["voice"] == "fr_FR-siwis-medium"
        assert metadata["language"] == "fr"
        assert len(audio_data) > 1000

    @pytest.mark.asyncio
    async def test_italian_language_selection(self, tts_service):
        """Test automatic Italian voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["it"], language="it"
        )

        assert metadata["voice"] == "it_IT-paola-medium"
        assert metadata["language"] == "it"
        assert len(audio_data) > 1000

    @pytest.mark.asyncio
    async def test_portuguese_language_selection(self, tts_service):
        """Test automatic Portuguese voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["pt"], language="pt"
        )

        assert metadata["voice"] == "pt_BR-faber-medium"
        assert metadata["language"] == "pt"
        assert len(audio_data) > 1000

    @pytest.mark.asyncio
    async def test_chinese_language_selection(self, tts_service):
        """Test automatic Chinese voice selection"""
        audio_data, metadata = await tts_service.synthesize_speech(
            TEST_PHRASES["zh"], language="zh"
        )

        assert metadata["voice"] == "zh_CN-huayan-medium"
        assert metadata["language"] == "zh"
        assert len(audio_data) > 1000


# =============================================================================
# Audio Quality Validation
# =============================================================================


class TestAudioQuality:
    """Test audio output quality and characteristics"""

    @pytest.mark.asyncio
    async def test_audio_format_consistency(self, tts_service):
        """Test that all voices produce consistent audio format"""
        # get_available_voices() now returns list of dicts with metadata
        for voice_info in tts_service.get_available_voices():
            voice_name = voice_info["voice_id"]  # Extract voice_id from dict
            audio_data, metadata = await tts_service.synthesize_speech(
                "Test audio format.", voice=voice_name
            )

            # Validate WAV format
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, "rb") as wav:
                assert wav.getnchannels() == 1, f"{voice_name}: Expected mono audio"
                assert wav.getsampwidth() == 2, f"{voice_name}: Expected 16-bit audio"
                assert wav.getframerate() in [
                    16000,
                    22050,
                    24000,
                ], f"{voice_name}: Unexpected sample rate {wav.getframerate()}"

    @pytest.mark.asyncio
    async def test_audio_length_correlation(self, tts_service):
        """Test that longer text produces longer audio"""
        short_text = "Hello."
        long_text = "Hello, this is a much longer sentence with more words to produce more audio output."

        # Use English voice
        short_audio, short_meta = await tts_service.synthesize_speech(
            short_text, language="en"
        )
        long_audio, long_meta = await tts_service.synthesize_speech(
            long_text, language="en"
        )

        # Longer text should produce longer audio
        assert len(long_audio) > len(short_audio)

    @pytest.mark.asyncio
    async def test_audio_minimum_size(self, tts_service):
        """Test that all voices produce reasonable audio size"""
        test_text = "This is a test sentence."

        # get_available_voices() now returns list of dicts with metadata
        for voice_info in tts_service.get_available_voices():
            voice_name = voice_info["voice_id"]  # Extract voice_id from dict
            audio_data, metadata = await tts_service.synthesize_speech(
                test_text, voice=voice_name
            )

            # Should be at least 5KB for this sentence
            assert len(audio_data) > 5000, (
                f"{voice_name}: Audio too small ({len(audio_data)} bytes)"
            )


# =============================================================================
# Service Information
# =============================================================================


class TestServiceInformation:
    """Test service information reporting"""

    def test_service_info_complete(self, tts_service):
        """Test that service info contains all expected fields"""
        info = tts_service.get_service_info()

        assert info["service"] == "piper_tts"
        assert info["status"] == "available"
        assert info["voices_count"] >= 11
        assert len(info["available_voices"]) >= 11
        assert len(info["supported_languages"]) >= 7
        assert info["cost_per_character"] == 0.0

    def test_service_features_listed(self, tts_service):
        """Test that service features are correctly listed"""
        info = tts_service.get_service_info()

        expected_features = [
            "local_processing",
            "no_api_costs",
            "offline_capable",
            "neural_voices",
            "multiple_languages",
        ]

        for feature in expected_features:
            assert feature in info["features"], f"Feature {feature} not listed"
