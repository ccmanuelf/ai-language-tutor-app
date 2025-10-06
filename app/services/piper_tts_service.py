"""
Piper TTS Service

This module provides text-to-speech functionality using Piper,
a local neural TTS engine with ONNX models.
"""

import asyncio
import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
import json

from piper import PiperVoice


logger = logging.getLogger(__name__)


@dataclass
class PiperTTSConfig:
    """Configuration for Piper TTS service"""

    voices_dir: str = "app/data/piper_voices"
    default_voice: str = "en_US-lessac-medium"
    default_language: str = "en"
    sample_rate: int = 22050
    noise_scale: float = 0.667
    noise_w: float = 0.8
    length_scale: float = 1.0

    def __post_init__(self):
        """Ensure voices directory exists"""
        Path(self.voices_dir).mkdir(parents=True, exist_ok=True)


class PiperTTSService:
    """
    Piper TTS Service for local text-to-speech synthesis

    Features:
    - Local TTS processing (no API calls)
    - Multiple language support
    - High-quality neural voices
    - Zero ongoing costs
    - ONNX-based models
    """

    def __init__(self):
        self.config = PiperTTSConfig()
        self.voices: Dict[str, Any] = {}
        self.language_voice_map = {
            "en": "en_US-lessac-medium",
            "es": "es_MX-claude-high",  # Mexican Spanish (Latin American accent)
            "fr": "fr_FR-siwis-medium",
            "de": "de_DE-thorsten-medium",
            "it": "it_IT-paola-medium",  # Italian - Medium quality (upgraded from x_low)
            "pt": "pt_BR-faber-medium",
            "zh": "zh_CN-huayan-medium",  # Chinese (Simplified) - Native voice
            # Fallback to English for languages without native voices
            "ja": "en_US-lessac-medium",  # No Japanese voice available yet
            "ko": "en_US-lessac-medium",  # No Korean voice available yet
        }
        self._initialize_voices()

    def _initialize_voices(self):
        """Initialize available Piper voices"""
        voices_dir = Path(self.config.voices_dir)

        if not voices_dir.exists():
            logger.warning(f"Voices directory not found: {voices_dir}")
            return

        # Find all .onnx model files
        for onnx_file in voices_dir.glob("*.onnx"):
            voice_name = onnx_file.stem
            config_file = onnx_file.with_suffix(".onnx.json")

            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        voice_config = json.load(f)

                    self.voices[voice_name] = {
                        "model_path": str(onnx_file),
                        "config_path": str(config_file),
                        "config": voice_config,
                        "language": voice_config.get("language", {}).get("code", "en"),
                        "sample_rate": voice_config.get("audio", {}).get(
                            "sample_rate", 22050
                        ),
                    }

                    logger.info(f"Loaded voice: {voice_name}")
                except Exception as e:
                    logger.error(f"Failed to load voice config {config_file}: {e}")

    def get_available_voices(self) -> List[str]:
        """Get list of available voice names"""
        return list(self.voices.keys())

    def get_voice_for_language(self, language: str) -> Optional[str]:
        """Get appropriate voice for language"""
        # First try direct mapping
        if language in self.language_voice_map:
            voice_name = self.language_voice_map[language]
            if voice_name in self.voices:
                return voice_name

        # Try to find any voice for the language
        for voice_name, voice_info in self.voices.items():
            if voice_info["language"].startswith(language):
                return voice_name

        # Fallback to default
        if self.config.default_voice in self.voices:
            return self.config.default_voice

        # Return first available voice
        return next(iter(self.voices.keys())) if self.voices else None

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        audio_format: str = "wav",
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Synthesize speech from text using Piper TTS

        Args:
            text: Text to synthesize
            language: Target language code
            voice: Specific voice to use (optional)
            audio_format: Output audio format

        Returns:
            Tuple of (audio_bytes, metadata)
        """
        if not self.voices:
            raise RuntimeError(
                "No Piper voices available. Please download voice models."
            )

        # Select voice
        if voice and voice in self.voices:
            selected_voice = voice
        else:
            selected_voice = self.get_voice_for_language(language)
            if not selected_voice:
                raise RuntimeError(f"No voice available for language: {language}")

        voice_info = self.voices[selected_voice]

        try:
            # Run synthesis in thread pool to avoid blocking
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, self._synthesize_sync, text, voice_info
            )

            metadata = {
                "voice": selected_voice,
                "language": language,
                "text_length": len(text),
                "sample_rate": voice_info["sample_rate"],
                "duration_estimate": len(text) * 0.1,  # Rough estimate
                "cost": 0.0,  # Local processing = zero cost
                "provider": "piper",
            }

            return audio_data, metadata

        except Exception as e:
            logger.error(f"Piper TTS synthesis failed: {e}")
            raise RuntimeError(f"TTS synthesis failed: {e}")

    def _synthesize_sync(self, text: str, voice_info: Dict[str, Any]) -> bytes:
        """Synchronous synthesis for thread execution"""
        model_path = voice_info["model_path"]
        config_path = voice_info["config_path"]

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Initialize Piper voice
            voice = PiperVoice.load(model_path, config_path)

            # Synthesize and collect audio chunks
            audio_chunks = []
            for audio_chunk in voice.synthesize(text):
                # Each audio_chunk has a .audio property with numpy array
                audio_chunks.append(audio_chunk.audio_int16_bytes)

            if not audio_chunks:
                raise RuntimeError("No audio data generated")

            # Combine audio chunks into single byte string

            combined_audio_bytes = b"".join(audio_chunks)

            # Convert to 16-bit PCM and create WAV file
            import wave

            with wave.open(temp_path, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(voice_info["sample_rate"])

                # Write the already converted 16-bit PCM data
                wav_file.writeframes(combined_audio_bytes)

            # Read the generated WAV file
            with open(temp_path, "rb") as wav_file:
                audio_data = wav_file.read()

            return audio_data

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    async def test_synthesis(
        self, test_text: str = "Hello, this is a test of Piper text-to-speech."
    ) -> bool:
        """Test TTS synthesis functionality"""
        try:
            audio_data, metadata = await self.synthesize_speech(test_text)

            logger.info(f"TTS test successful:")
            logger.info(f"  Voice: {metadata['voice']}")
            logger.info(f"  Audio size: {len(audio_data)} bytes")
            logger.info(f"  Sample rate: {metadata['sample_rate']} Hz")

            return True

        except Exception as e:
            logger.error(f"TTS test failed: {e}")
            return False

    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status"""
        return {
            "service": "piper_tts",
            "status": "available" if self.voices else "no_voices",
            "voices_count": len(self.voices),
            "available_voices": list(self.voices.keys()),
            "supported_languages": list(self.language_voice_map.keys()),
            "voices_directory": self.config.voices_dir,
            "cost_per_character": 0.0,  # Local = free
            "features": [
                "local_processing",
                "no_api_costs",
                "offline_capable",
                "neural_voices",
                "multiple_languages",
            ],
        }
