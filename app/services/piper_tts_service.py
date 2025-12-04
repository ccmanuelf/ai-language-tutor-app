"""
Piper TTS Service

This module provides text-to-speech functionality using Piper,
a local neural TTS engine with ONNX models.
"""

import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

    def get_available_voices(
        self, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available voice personas with detailed metadata

        Args:
            language: Optional language filter (e.g., "en", "es")

        Returns:
            List of voice dictionaries with metadata:
            - voice_id: Full voice identifier (e.g., "es_AR-daniela-high")
            - persona: Voice persona name (e.g., "daniela")
            - language: Language code (e.g., "es")
            - accent: Accent/region (e.g., "Argentina")
            - quality: Voice quality (e.g., "high", "medium", "x_low")
            - gender: Inferred gender (e.g., "female", "male", "unknown")
            - sample_rate: Audio sample rate
            - is_default: Whether this is the default voice for the language
        """
        voices_list = []

        for voice_id, voice_info in self.voices.items():
            voice_language = voice_info["language"]

            # Apply language filter if provided
            if language and not voice_language.startswith(language):
                continue

            # Parse voice ID to extract components
            # Format: language_region-persona-quality (e.g., "es_AR-daniela-high")
            parts = voice_id.split("-")
            language_region = parts[0] if len(parts) > 0 else ""
            persona = parts[1] if len(parts) > 1 else "default"
            quality = parts[2] if len(parts) > 2 else "medium"

            # Extract language and region
            lang_parts = language_region.split("_")
            lang_code = lang_parts[0] if len(lang_parts) > 0 else voice_language
            region_code = lang_parts[1] if len(lang_parts) > 1 else ""

            # Map region codes to human-readable accents
            accent_map = {
                "US": "United States",
                "GB": "United Kingdom",
                "AR": "Argentina",
                "ES": "Spain",
                "MX": "Mexico",
                "FR": "France",
                "DE": "Germany",
                "IT": "Italy",
                "BR": "Brazil",
                "CN": "China",
            }
            accent = accent_map.get(region_code, region_code or "Standard")

            # Infer gender from persona name (heuristic-based)
            gender = self._infer_gender(persona)

            # Check if this is the default voice for the language
            is_default = self.language_voice_map.get(lang_code) == voice_id

            voice_metadata = {
                "voice_id": voice_id,
                "persona": persona,
                "language": lang_code,
                "accent": accent,
                "quality": quality,
                "gender": gender,
                "sample_rate": voice_info["sample_rate"],
                "is_default": is_default,
            }

            voices_list.append(voice_metadata)

        return voices_list

    def _infer_gender(self, persona: str) -> str:
        """
        Infer gender from persona name using heuristics

        Args:
            persona: Persona name (e.g., "daniela", "claude")

        Returns:
            Gender: "female", "male", or "unknown"
        """
        # Common female names/patterns
        female_names = {
            "daniela",
            "paola",
            "siwis",
            "maria",
            "sophie",
            "sarah",
            "emma",
            "lisa",
        }

        # Common male names/patterns
        male_names = {
            "claude",
            "davefx",
            "thorsten",
            "riccardo",
            "lessac",
            "faber",
            "john",
            "david",
            "michael",
        }

        persona_lower = persona.lower()

        if persona_lower in female_names:
            return "female"
        elif persona_lower in male_names:
            return "male"
        else:
            return "unknown"

    def get_voice_names(self) -> List[str]:
        """Get simple list of available voice names (legacy method)"""
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

    def _chunk_text(self, text: str, max_chunk_size: int) -> List[str]:
        """
        Split text into chunks at sentence boundaries to avoid ONNX runtime errors.

        Args:
            text: The text to chunk
            max_chunk_size: Maximum characters per chunk

        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]

        # Split on sentence boundaries (., !, ?)
        import re

        sentences = re.split(r"([.!?]+\s+)", text)

        chunks = []
        current_chunk = ""

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

            # If adding this sentence would exceed the limit, save current chunk
            if (
                current_chunk
                and len(current_chunk) + len(sentence) + len(delimiter) > max_chunk_size
            ):
                chunks.append(current_chunk.strip())
                current_chunk = sentence + delimiter
            else:
                current_chunk += sentence + delimiter

        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _synthesize_sync(self, text: str, voice_info: Dict[str, Any]) -> bytes:
        """Synchronous synthesis for thread execution"""
        model_path = voice_info["model_path"]
        config_path = voice_info["config_path"]

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Split very long text into manageable chunks to avoid ONNX runtime errors
            # Piper has issues with very long texts (>1000 chars)
            max_chunk_size = 200  # Very conservative chunk size to avoid ONNX errors
            text_chunks = self._chunk_text(text, max_chunk_size)

            # Synthesize and collect audio chunks
            # NOTE: We must reload the voice for each chunk due to Piper's state management issues
            audio_chunks = []
            for idx, text_chunk in enumerate(text_chunks):
                try:
                    # Reload voice for each chunk to avoid ONNX state corruption
                    voice = PiperVoice.load(model_path, config_path)
                    for audio_chunk in voice.synthesize(text_chunk):
                        # Each audio_chunk has a .audio property with numpy array
                        audio_chunks.append(audio_chunk.audio_int16_bytes)
                except Exception as chunk_error:
                    logger.warning(
                        f"Failed to synthesize chunk {idx} (length {len(text_chunk)}): {chunk_error}"
                    )
                    # If even a small chunk fails, try splitting it further or skip
                    # For now, we'll try to continue with other chunks
                    continue

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

            logger.info("TTS test successful:")
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
