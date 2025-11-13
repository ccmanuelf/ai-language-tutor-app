"""
Pytest configuration and shared fixtures.

This conftest.py provides fixtures for testing, especially for audio processing tests.
"""

import wave
from pathlib import Path
from typing import Tuple

import pytest

# Audio fixtures directory
AUDIO_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "audio"


@pytest.fixture
def audio_fixtures_dir() -> Path:
    """Return the path to the audio fixtures directory."""
    return AUDIO_FIXTURES_DIR


@pytest.fixture
def load_wav_file():
    """
    Fixture that returns a function to load WAV files.

    Returns a function that takes a filename and returns the audio bytes.
    """

    def _load_wav(filename: str) -> bytes:
        """Load a WAV file and return its bytes."""
        filepath = AUDIO_FIXTURES_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Audio fixture not found: {filepath}")

        with open(filepath, "rb") as f:
            return f.read()

    return _load_wav


@pytest.fixture
def load_wav_with_info():
    """
    Fixture that returns a function to load WAV files with metadata.

    Returns a function that takes a filename and returns (audio_bytes, sample_rate, channels).
    """

    def _load_wav_with_info(filename: str) -> Tuple[bytes, int, int]:
        """Load a WAV file and return bytes along with metadata."""
        filepath = AUDIO_FIXTURES_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Audio fixture not found: {filepath}")

        with wave.open(str(filepath), "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()

        with open(filepath, "rb") as f:
            audio_bytes = f.read()

        return audio_bytes, sample_rate, channels

    return _load_wav_with_info


@pytest.fixture
def silence_audio_16khz(load_wav_file) -> bytes:
    """Load 1-second silence audio at 16kHz."""
    return load_wav_file("silence_1sec_16khz.wav")


@pytest.fixture
def speech_like_audio_16khz(load_wav_file) -> bytes:
    """Load 1-second speech-like audio at 16kHz."""
    return load_wav_file("speech_like_1sec_16khz.wav")


@pytest.fixture
def tone_440hz_audio_16khz(load_wav_file) -> bytes:
    """Load 1-second 440Hz tone at 16kHz."""
    return load_wav_file("tone_440hz_1sec_16khz.wav")


@pytest.fixture
def white_noise_audio_16khz(load_wav_file) -> bytes:
    """Load 1-second white noise at 16kHz."""
    return load_wav_file("noise_white_1sec_16khz.wav")


@pytest.fixture
def short_beep_audio_16khz(load_wav_file) -> bytes:
    """Load 100ms beep audio at 16kHz."""
    return load_wav_file("beep_100ms_16khz.wav")


@pytest.fixture
def stereo_audio_16khz(load_wav_file) -> bytes:
    """Load 1-second stereo speech-like audio at 16kHz."""
    return load_wav_file("speech_like_1sec_16khz_stereo.wav")
