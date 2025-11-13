"""
Generate test audio files for audio processing tests.

This script creates various test audio files with real audio signals,
not mocked data, to enable proper testing of audio processing services.
"""

import wave
import numpy as np
from pathlib import Path


def create_wav_file(filename: str, audio_data: np.ndarray, sample_rate: int = 16000, channels: int = 1):
    """Create a WAV file from numpy array."""
    filepath = Path(__file__).parent / filename

    with wave.open(str(filepath), 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    print(f"✓ Created: {filename} ({len(audio_data)} samples, {sample_rate}Hz, {channels} ch)")
    return filepath


def generate_silence(duration_sec: float = 1.0, sample_rate: int = 16000) -> np.ndarray:
    """Generate pure silence."""
    num_samples = int(duration_sec * sample_rate)
    return np.zeros(num_samples, dtype=np.int16)


def generate_sine_wave(frequency: float, duration_sec: float = 1.0,
                       sample_rate: int = 16000, amplitude: float = 0.5) -> np.ndarray:
    """Generate a sine wave tone."""
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    # Convert to 16-bit PCM
    return (wave_data * 32767).astype(np.int16)


def generate_white_noise(duration_sec: float = 1.0, sample_rate: int = 16000,
                         amplitude: float = 0.1) -> np.ndarray:
    """Generate white noise."""
    num_samples = int(duration_sec * sample_rate)
    noise = np.random.normal(0, amplitude, num_samples)
    return (noise * 32767).astype(np.int16)


def generate_speech_like_signal(duration_sec: float = 1.0,
                                sample_rate: int = 16000) -> np.ndarray:
    """
    Generate a speech-like signal with varying frequencies.
    This simulates human speech patterns with formants.
    """
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)

    # Fundamental frequency (pitch) around 120 Hz (male voice)
    fundamental = 120

    # Create formants (resonant frequencies in speech)
    formant1 = 0.3 * np.sin(2 * np.pi * 700 * t)   # First formant
    formant2 = 0.2 * np.sin(2 * np.pi * 1220 * t)  # Second formant
    formant3 = 0.1 * np.sin(2 * np.pi * 2600 * t)  # Third formant

    # Fundamental frequency
    pitch = 0.4 * np.sin(2 * np.pi * fundamental * t)

    # Combine with envelope (speech has varying amplitude)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * 4 * t))  # 4 Hz modulation

    # Combine all components
    signal = (pitch + formant1 + formant2 + formant3) * envelope

    # Normalize and convert to 16-bit PCM
    signal = signal / np.max(np.abs(signal))
    return (signal * 32767 * 0.8).astype(np.int16)


def generate_multi_tone(duration_sec: float = 1.0, sample_rate: int = 16000) -> np.ndarray:
    """Generate a chord with multiple frequencies."""
    # C major chord: C4 (261.63 Hz), E4 (329.63 Hz), G4 (392.00 Hz)
    tone1 = generate_sine_wave(261.63, duration_sec, sample_rate, 0.3)
    tone2 = generate_sine_wave(329.63, duration_sec, sample_rate, 0.3)
    tone3 = generate_sine_wave(392.00, duration_sec, sample_rate, 0.3)

    combined = tone1.astype(np.int32) + tone2.astype(np.int32) + tone3.astype(np.int32)
    # Normalize to prevent clipping
    combined = combined / 3
    return combined.astype(np.int16)


def generate_short_beep(duration_sec: float = 0.1, sample_rate: int = 16000) -> np.ndarray:
    """Generate a short beep tone (for testing short audio)."""
    return generate_sine_wave(1000, duration_sec, sample_rate, 0.7)


def main():
    """Generate all test audio files."""
    print("Generating test audio files...")
    print("=" * 60)

    # 1. Silence files (different durations and sample rates)
    create_wav_file("silence_1sec_16khz.wav",
                   generate_silence(1.0, 16000), 16000)

    create_wav_file("silence_1sec_8khz.wav",
                   generate_silence(1.0, 8000), 8000)

    create_wav_file("silence_1sec_44khz.wav",
                   generate_silence(1.0, 44100), 44100)

    # 2. Pure tones
    create_wav_file("tone_440hz_1sec_16khz.wav",
                   generate_sine_wave(440, 1.0, 16000), 16000)

    create_wav_file("tone_1000hz_1sec_16khz.wav",
                   generate_sine_wave(1000, 1.0, 16000), 16000)

    # 3. White noise
    create_wav_file("noise_white_1sec_16khz.wav",
                   generate_white_noise(1.0, 16000), 16000)

    # 4. Speech-like signal
    create_wav_file("speech_like_1sec_16khz.wav",
                   generate_speech_like_signal(1.0, 16000), 16000)

    create_wav_file("speech_like_2sec_16khz.wav",
                   generate_speech_like_signal(2.0, 16000), 16000)

    # 5. Multi-tone (chord)
    create_wav_file("chord_cmajor_1sec_16khz.wav",
                   generate_multi_tone(1.0, 16000), 16000)

    # 6. Short audio (for testing minimum duration)
    create_wav_file("beep_100ms_16khz.wav",
                   generate_short_beep(0.1, 16000), 16000)

    # 7. Stereo audio (2 channels)
    mono_data = generate_speech_like_signal(1.0, 16000)
    stereo_data = np.column_stack((mono_data, mono_data)).flatten()
    create_wav_file("speech_like_1sec_16khz_stereo.wav",
                   stereo_data, 16000, channels=2)

    # 8. Different sample rates for testing resampling
    create_wav_file("tone_440hz_1sec_8khz.wav",
                   generate_sine_wave(440, 1.0, 8000), 8000)

    create_wav_file("tone_440hz_1sec_44khz.wav",
                   generate_sine_wave(440, 1.0, 44100), 44100)

    print("=" * 60)
    print(f"✓ All test audio files generated successfully!")
    print(f"✓ Location: {Path(__file__).parent}")


if __name__ == "__main__":
    main()
