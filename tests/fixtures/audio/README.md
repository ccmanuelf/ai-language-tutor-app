# Audio Test Fixtures

This directory contains **real audio files** for testing audio processing services.

## ⚠️ CRITICAL: Real Audio Testing Philosophy

**DO NOT USE MOCKED AUDIO DATA** (e.g., `b"fake_audio_data"`) for audio processing tests!

**Why?**
- Mocked audio creates **false positives** - tests pass even when audio processing is broken
- Real audio files ensure we test actual audio signal processing
- We test the **engine**, not just the wrapper

## File Inventory

### Silence Files (Testing silence detection and VAD)
- `silence_1sec_16khz.wav` - 1 second pure silence at 16kHz (mono)
- `silence_1sec_8khz.wav` - 1 second pure silence at 8kHz (mono)
- `silence_1sec_44khz.wav` - 1 second pure silence at 44.1kHz (mono)

### Pure Tones (Testing frequency analysis and audio processing)
- `tone_440hz_1sec_16khz.wav` - 1 second A440 musical note at 16kHz (mono)
- `tone_1000hz_1sec_16khz.wav` - 1 second 1kHz tone at 16kHz (mono)
- `tone_440hz_1sec_8khz.wav` - 1 second A440 at 8kHz (mono)
- `tone_440hz_1sec_44khz.wav` - 1 second A440 at 44.1kHz (mono)

### Noise (Testing noise handling)
- `noise_white_1sec_16khz.wav` - 1 second white noise at 16kHz (mono)

### Speech-Like Signals (Testing speech processing)
- `speech_like_1sec_16khz.wav` - 1 second speech-like signal at 16kHz (mono)
  - Contains formants and pitch modulation similar to human speech
  - Useful for STT preprocessing tests
- `speech_like_2sec_16khz.wav` - 2 seconds speech-like signal at 16kHz (mono)
- `speech_like_1sec_16khz_stereo.wav` - 1 second speech-like signal at 16kHz (stereo)

### Multi-Tone (Testing complex audio)
- `chord_cmajor_1sec_16khz.wav` - 1 second C major chord at 16kHz (mono)
  - Contains C4 (261.63 Hz), E4 (329.63 Hz), G4 (392.00 Hz)

### Short Audio (Testing minimum duration handling)
- `beep_100ms_16khz.wav` - 100ms beep at 16kHz (mono)

## Audio Specifications

All files are in **WAV format** (PCM 16-bit signed integer):

| File | Duration | Sample Rate | Channels | Size | Use Case |
|------|----------|-------------|----------|------|----------|
| silence_1sec_16khz.wav | 1.0s | 16000 Hz | 1 (mono) | ~31 KB | Silence detection, VAD |
| silence_1sec_8khz.wav | 1.0s | 8000 Hz | 1 (mono) | ~16 KB | Low sample rate handling |
| silence_1sec_44khz.wav | 1.0s | 44100 Hz | 1 (mono) | ~86 KB | High sample rate handling |
| tone_440hz_1sec_16khz.wav | 1.0s | 16000 Hz | 1 (mono) | ~31 KB | Frequency analysis |
| tone_1000hz_1sec_16khz.wav | 1.0s | 16000 Hz | 1 (mono) | ~31 KB | Frequency analysis |
| noise_white_1sec_16khz.wav | 1.0s | 16000 Hz | 1 (mono) | ~31 KB | Noise handling |
| speech_like_1sec_16khz.wav | 1.0s | 16000 Hz | 1 (mono) | ~31 KB | STT preprocessing |
| speech_like_2sec_16khz.wav | 2.0s | 16000 Hz | 1 (mono) | ~63 KB | Longer audio processing |
| speech_like_1sec_16khz_stereo.wav | 1.0s | 16000 Hz | 2 (stereo) | ~63 KB | Stereo handling |
| chord_cmajor_1sec_16khz.wav | 1.0s | 16000 Hz | 1 (mono) | ~31 KB | Complex audio |
| beep_100ms_16khz.wav | 0.1s | 16000 Hz | 1 (mono) | ~3 KB | Short audio |
| tone_440hz_1sec_8khz.wav | 1.0s | 8000 Hz | 1 (mono) | ~16 KB | Resampling tests |
| tone_440hz_1sec_44khz.wav | 1.0s | 44100 Hz | 1 (mono) | ~86 KB | Resampling tests |

## Usage in Tests

### Loading Audio Files

Use the fixtures provided in `tests/conftest.py`:

```python
def test_with_real_audio(speech_like_audio_16khz):
    """Test with real speech-like audio."""
    # speech_like_audio_16khz is bytes of actual audio data
    result = process_audio(speech_like_audio_16khz)
    assert result is not None
```

### Custom Loading

```python
def test_custom_audio_loading(load_wav_file):
    """Load any audio file from fixtures."""
    audio_data = load_wav_file("tone_440hz_1sec_16khz.wav")
    assert len(audio_data) > 1000  # Verify it's real audio
```

### Loading with Metadata

```python
def test_audio_with_metadata(load_wav_with_info):
    """Load audio with sample rate and channel info."""
    audio_bytes, sample_rate, channels = load_wav_with_info("speech_like_1sec_16khz.wav")
    assert sample_rate == 16000
    assert channels == 1
```

## Testing Best Practices

### ✅ DO: Use Real Audio

```python
async def test_stt_with_real_audio(speech_like_audio_16khz):
    """Test STT with real audio signal."""
    # Use real audio
    result = await stt_service.transcribe(speech_like_audio_16khz)
    
    # Mock at HTTP level (if needed)
    with httpx_mock.add_response(json={"text": "transcription"}):
        result = await stt_service.transcribe(speech_like_audio_16khz)
    
    # This ensures audio preprocessing is actually tested!
```

### ❌ DON'T: Use Fake Audio Data

```python
# BAD: This is what we're trying to avoid!
async def test_stt_with_fake_audio():
    """This test is worthless - creates false positives!"""
    fake_audio = b"fake_audio_data" * 100  # ❌ NO!
    
    # This mocks the method we're trying to test!
    with patch.object(service, 'transcribe', return_value=mock_result):  # ❌ NO!
        result = await service.transcribe(fake_audio)
```

### ✅ DO: Mock at HTTP Level, Not Method Level

```python
# GOOD: Mock the HTTP call, test the audio processing
import httpx
from pytest_httpx import HTTPXMock

async def test_stt_real_audio_mocked_api(speech_like_audio_16khz, httpx_mock: HTTPXMock):
    """Test with real audio, mock only the API call."""
    # Mock the HTTP response
    httpx_mock.add_response(
        url="https://api.mistral.ai/v1/audio/transcriptions",
        json={
            "text": "hello world",
            "language": "en",
            "duration": 1.0
        }
    )
    
    # Use REAL audio - the preprocessing will be tested!
    result = await stt_service.transcribe(speech_like_audio_16khz)
    
    # Verify the result
    assert result.text == "hello world"
```

## Regenerating Test Audio

If you need to regenerate the audio files:

```bash
cd tests/fixtures/audio
python generate_test_audio.py
```

This will recreate all test audio files with fresh audio signals.

## Audio Signal Characteristics

### Speech-Like Signal
The speech-like signals contain:
- **Fundamental frequency**: ~120 Hz (simulating male voice pitch)
- **Formants**: 700 Hz, 1220 Hz, 2600 Hz (simulating vowel sounds)
- **Envelope modulation**: 4 Hz (simulating syllable rhythm)

These characteristics make the signal realistic enough for STT preprocessing tests without requiring actual speech recordings.

### Silence
Pure digital silence (all samples = 0) for testing:
- Voice Activity Detection (VAD)
- Silence trimming
- Noise floor estimation

### Tones
Pure sine waves at specific frequencies for testing:
- Audio format validation
- Frequency analysis
- Sample rate conversion

## Version History

- **v1.0** (2025-11-21): Initial creation with 13 audio files
  - Added silence, tones, noise, speech-like signals
  - Multiple sample rates: 8kHz, 16kHz, 44.1kHz
  - Stereo and mono variants

---

**Remember**: Real audio testing = Real confidence! 🎯
