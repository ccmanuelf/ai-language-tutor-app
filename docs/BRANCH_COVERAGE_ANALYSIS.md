# Untested Branch Coverage Analysis: speech_processor.py

## Summary
**Total Untested Branches:** 12  
**Analysis Date:** 2025-11-14  
**Target:** 100% branch coverage

---

## Branch Details

### Branch 1: Lines 844 → 874
**Location:** `_analyze_audio_quality()` method  
**Code:**
```python
if AUDIO_LIBS_AVAILABLE and len(audio_data) > 0:
    try:
        # ... audio analysis code ...
    except Exception as e:
        logger.warning(f"Advanced audio quality analysis failed: {e}")

return AudioMetadata(...)  # Line 874
```

**Untested Path:** FALSE branch (when condition is False)  
**Missing Condition:** `not (AUDIO_LIBS_AVAILABLE and len(audio_data) > 0)`

**What's Not Tested:**
- When `AUDIO_LIBS_AVAILABLE` is False OR `len(audio_data) == 0`
- The code path that skips advanced audio quality checks

**Test Scenario Needed:**
```python
# Test with AUDIO_LIBS_AVAILABLE = False
def test_analyze_audio_quality_without_numpy(self, mock_audio_libs):
    """Test audio quality analysis when numpy is not available"""
    mock_audio_libs.return_value = False
    processor = SpeechProcessor()
    
    audio_data = b'\x00\x01' * 1000
    result = await processor._analyze_audio_quality(audio_data, AudioFormat.WAV)
    
    # Should return basic metadata without advanced SNR analysis
    assert result.quality_score > 0
```

---

### Branch 2: Lines 864 → 874
**Location:** `_analyze_audio_quality()` method (nested condition)  
**Code:**
```python
if signal_power > 0 and noise_floor > 0:
    snr_approx = 10 * np.log10(signal_power / (noise_floor**2))
    # ... SNR quality calculation ...
# If condition false, skip to line 874
```

**Untested Path:** FALSE branch  
**Missing Condition:** `not (signal_power > 0 and noise_floor > 0)`

**What's Not Tested:**
- When `signal_power <= 0` OR `noise_floor <= 0`
- Audio with zero signal power or zero noise floor

**Test Scenario Needed:**
```python
def test_analyze_audio_quality_zero_signal_power(self):
    """Test audio quality with zero signal power (silence)"""
    # Create audio that's all zeros or very low amplitude
    audio_data = b'\x00\x00' * 1000  # Silent audio
    
    result = await processor._analyze_audio_quality(audio_data, AudioFormat.WAV)
    
    # Should handle zero signal/noise gracefully
    assert result.quality_score >= 0
```

---

### Branch 3: Lines 939 → 947
**Location:** `_apply_speech_enhancement()` method  
**Code:**
```python
if len(audio_array) > 1:
    # Apply pre-emphasis filter
    pre_emphasis = 0.97
    emphasized = np.copy(audio_array)
    emphasized[1:] = audio_array[1:] - pre_emphasis * audio_array[:-1]
    audio_array = emphasized

# Next section at line 947
if len(audio_array) > 0:
```

**Untested Path:** FALSE branch  
**Missing Condition:** `len(audio_array) <= 1`

**What's Not Tested:**
- Audio arrays with 0 or 1 sample
- Skipping pre-emphasis filter for very short audio

**Test Scenario Needed:**
```python
def test_apply_speech_enhancement_single_sample(self):
    """Test speech enhancement with single audio sample"""
    # Create audio with only 1 sample (2 bytes for int16)
    audio_data = b'\x00\x01'
    
    result = processor._apply_speech_enhancement(audio_data)
    
    # Should skip pre-emphasis but still process
    assert len(result) == len(audio_data)
```

---

### Branch 4: Lines 947 → 961
**Location:** `_apply_speech_enhancement()` method  
**Code:**
```python
if len(audio_array) > 0:
    # Apply dynamic range compression
    float_audio = audio_array.astype(np.float32)
    max_val = np.max(np.abs(float_audio))
    if max_val > 0:
        # ... compression code ...

return audio_array.tobytes()  # Line 961
```

**Untested Path:** FALSE branch  
**Missing Condition:** `len(audio_array) == 0`

**What's Not Tested:**
- Empty audio array (0 samples)
- Code path that skips compression entirely

**Test Scenario Needed:**
```python
def test_apply_speech_enhancement_empty_audio(self):
    """Test speech enhancement with empty audio"""
    audio_data = b''  # Empty audio
    
    result = processor._apply_speech_enhancement(audio_data)
    
    # Should return empty bytes gracefully
    assert result == b''
```

---

### Branch 5: Lines 953 → 961
**Location:** `_apply_speech_enhancement()` method (nested)  
**Code:**
```python
max_val = np.max(np.abs(float_audio))
if max_val > 0:
    # Normalize and apply compression
    normalized = float_audio / max_val
    compressed = np.sign(normalized) * np.power(np.abs(normalized), 0.8)
    audio_array = (compressed * 32767).astype(np.int16)

return audio_array.tobytes()  # Line 961
```

**Untested Path:** FALSE branch  
**Missing Condition:** `max_val == 0`

**What's Not Tested:**
- Audio with all zero amplitude (silence)
- Skipping compression when max_val is 0

**Test Scenario Needed:**
```python
def test_apply_speech_enhancement_silent_audio(self):
    """Test speech enhancement with silent audio (all zeros)"""
    # Create silent audio (all zeros)
    audio_data = b'\x00\x00' * 500
    
    result = processor._apply_speech_enhancement(audio_data)
    
    # Should handle silence without division by zero
    assert len(result) == len(audio_data)
```

---

### Branch 6: Lines 1132 → 1136
**Location:** `_preprocess_audio()` method  
**Code:**
```python
# Apply noise reduction if available
if self.audio_libs_available:
    audio_data = self._reduce_noise(audio_data)

# Normalize audio levels
audio_data = self._normalize_audio(audio_data)  # Line 1136
```

**Untested Path:** FALSE branch  
**Missing Condition:** `not self.audio_libs_available`

**What's Not Tested:**
- When audio libraries are not available
- Skipping noise reduction step

**Test Scenario Needed:**
```python
def test_preprocess_audio_no_audio_libs(self, mock_audio_libs):
    """Test audio preprocessing without numpy/audio libraries"""
    mock_audio_libs.return_value = False
    processor = SpeechProcessor()
    
    audio_data = b'\x00\x01' * 1000
    result = await processor._preprocess_audio(audio_data, AudioFormat.WAV)
    
    # Should skip noise reduction but still normalize
    assert result is not None
```

---

### Branch 7: Lines 1139 → 1142
**Location:** `_preprocess_audio()` method  
**Code:**
```python
# Ensure proper WAV format for Watson STT
if audio_format == AudioFormat.WAV:
    audio_data = await self._ensure_proper_wav_format(audio_data)

return audio_data  # Line 1142
```

**Untested Path:** FALSE branch  
**Missing Condition:** `audio_format != AudioFormat.WAV`

**What's Not Tested:**
- Non-WAV audio formats (MP3, FLAC, WEBM)
- Skipping WAV format conversion

**Test Scenario Needed:**
```python
def test_preprocess_audio_non_wav_format(self):
    """Test audio preprocessing with MP3 format"""
    audio_data = b'\x00\x01' * 1000
    
    result = await processor._preprocess_audio(audio_data, AudioFormat.MP3)
    
    # Should skip WAV format conversion
    assert result is not None
```

---

### Branch 8: Lines 1203 → 1208
**Location:** `_reduce_noise()` method  
**Code:**
```python
max_val = np.max(np.abs(audio_array))
if max_val > 0:  # Avoid division by zero
    threshold = max_val * 0.1
    audio_array[np.abs(audio_array) < threshold] = 0

return audio_array.tobytes()  # Line 1208
```

**Untested Path:** FALSE branch  
**Missing Condition:** `max_val == 0`

**What's Not Tested:**
- Audio with all zero samples (silent audio)
- Skipping noise gate when max_val is 0

**Test Scenario Needed:**
```python
def test_reduce_noise_silent_audio(self):
    """Test noise reduction with silent audio (all zeros)"""
    audio_data = b'\x00\x00' * 500
    
    result = processor._reduce_noise(audio_data)
    
    # Should handle zeros without applying threshold
    assert result == audio_data
```

---

### Branch 9: Lines 1232 → 1239
**Location:** `_normalize_audio()` method  
**Code:**
```python
if len(audio_array) > 0:
    max_val = np.max(np.abs(audio_array))
    if max_val > 0:
        normalized = audio_array.astype(np.float32) * (32767.0 / max_val)
        audio_array = normalized.astype(np.int16)

return audio_array.tobytes()  # Line 1239
```

**Untested Path:** FALSE branch  
**Missing Condition:** `len(audio_array) == 0`

**What's Not Tested:**
- Empty audio array
- Skipping normalization for zero-length audio

**Test Scenario Needed:**
```python
def test_normalize_audio_empty(self):
    """Test audio normalization with empty audio"""
    audio_data = b''
    
    result = processor._normalize_audio(audio_data)
    
    # Should return empty bytes
    assert result == b''
```

---

### Branch 10: Lines 1234 → 1239
**Location:** `_normalize_audio()` method (nested)  
**Code:**
```python
if len(audio_array) > 0:
    max_val = np.max(np.abs(audio_array))
    if max_val > 0:
        normalized = audio_array.astype(np.float32) * (32767.0 / max_val)
        audio_array = normalized.astype(np.int16)

return audio_array.tobytes()  # Line 1239
```

**Untested Path:** FALSE branch  
**Missing Condition:** `max_val == 0` (when len > 0)

**What's Not Tested:**
- Non-empty audio with all zero samples
- Skipping normalization calculation when max is 0

**Test Scenario Needed:**
```python
def test_normalize_audio_zeros(self):
    """Test audio normalization with non-empty silent audio"""
    audio_data = b'\x00\x00' * 500  # Non-empty but all zeros
    
    result = processor._normalize_audio(audio_data)
    
    # Should handle zeros without division by zero
    assert result == audio_data
```

---

### Branch 11: Lines 1284 → 1283 (BACKWARD JUMP)
**Location:** `_apply_word_emphasis()` method  
**Code:**
```python
enhanced_text = text
for word in emphasis_words:  # Line 1283 - loop start
    if word.lower() in enhanced_text.lower():  # Line 1284
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        enhanced_text = pattern.sub(...)
        # Loop continues back to 1283
```

**Untested Path:** FALSE branch (loop iteration when condition is False)  
**Missing Condition:** `word.lower() not in enhanced_text.lower()`

**What's Not Tested:**
- Emphasis words that are NOT present in the text
- Skipping pattern substitution for non-matching words

**Test Scenario Needed:**
```python
def test_apply_word_emphasis_no_matches(self):
    """Test word emphasis when words are not in text"""
    text = "Hello world"
    emphasis_words = ["goodbye", "universe"]  # Not in text
    
    result = processor._apply_word_emphasis(text, emphasis_words)
    
    # Should return unchanged text
    assert result == text
    assert "<emphasis" not in result
```

---

### Branch 12: Lines 1339 → 1343
**Location:** `_enhance_chinese_text()` method  
**Code:**
```python
enhanced_text = text
# Slow down speech for Chinese pronunciation learning
if "<prosody rate=" not in enhanced_text:
    enhanced_text = f'<prosody rate="-30%">{enhanced_text}</prosody>'

# Add pauses between characters
for i, char in enumerate(chinese_chars[:10]):  # Line 1343
```

**Untested Path:** FALSE branch  
**Missing Condition:** `"<prosody rate=" in enhanced_text`

**What's Not Tested:**
- Chinese text that already has prosody rate markup
- Skipping addition of prosody wrapper

**Test Scenario Needed:**
```python
def test_enhance_chinese_text_existing_prosody(self):
    """Test Chinese enhancement when prosody already exists"""
    text = '<prosody rate="-20%">你好世界</prosody>'
    
    result = processor._enhance_chinese_text(text)
    
    # Should NOT add another prosody wrapper
    assert result.count("<prosody rate=") == 1
    assert result.count("</prosody>") == 1
```

---

## Summary of Test Scenarios Needed

### By Category:

**Audio Processing Edge Cases (9 branches):**
1. Audio without numpy libraries available
2. Silent audio (all zeros) - multiple methods
3. Empty audio arrays (zero length)
4. Single-sample audio arrays
5. Audio with zero signal power or noise floor

**Format Handling (1 branch):**
6. Non-WAV audio formats (MP3, FLAC, WEBM)

**Text Processing Edge Cases (2 branches):**
7. Emphasis words not present in text
8. Chinese text with existing prosody markup

### Priority:
- **HIGH**: Branches 1, 6, 7, 8, 9, 10 (core audio processing edge cases)
- **MEDIUM**: Branches 2, 3, 4, 5 (nested audio processing conditions)
- **LOW**: Branches 11, 12 (text enhancement edge cases)

---

## Implementation Notes:

1. **Mocking Strategy**: Several tests require mocking `AUDIO_LIBS_AVAILABLE` global
2. **Empty Audio**: Multiple branches test empty/zero audio - can reuse fixtures
3. **Edge Cases**: Focus on boundary conditions (len=0, len=1, max=0)
4. **Format Testing**: Need to test all AudioFormat enum values
5. **Text Processing**: Test both missing matches and existing markup

---

## Expected Coverage Improvement:
- Current: ~90% branch coverage
- After implementation: 100% branch coverage
- Estimated new tests: 12-15 test cases
