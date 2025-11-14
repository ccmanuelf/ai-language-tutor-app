# Session 25 Plan - Achieve 100% Branch Coverage

**Date**: TBD  
**Session Goal**: Fix 12 untested branch paths to achieve 100% branch coverage  
**Priority**: HIGH - Zero Technical Debt Policy  
**Prerequisite**: Session 24 complete (100% statement coverage achieved)

---

## 🎯 Primary Objective

**Achieve 100% branch coverage for `app/services/speech_processor.py`**

Current Status:
- ✅ Statement Coverage: 100% (575/575 lines)
- ❌ Branch Coverage: 98.35% (154 branches, **12 partial**)
- 🎯 Target: 100% branch coverage (0 partial branches)

---

## 📋 12 Untested Branches to Fix

### Category 1: Audio Edge Cases (HIGH Priority - 9 branches)

#### Silent/Zero Audio (5 tests needed)
1. **Branch 844→874**: Audio quality analysis without numpy libraries
2. **Branch 864→874**: Zero signal power or noise floor in SNR calculation
3. **Branch 953→961**: Silent audio (max_val = 0) in speech enhancement
4. **Branch 1203→1208**: Silent audio in noise reduction
5. **Branch 1234→1239**: Non-empty silent audio in normalization

#### Empty/Minimal Audio (4 tests needed)
6. **Branch 939→947**: Single-sample audio (len ≤ 1) skipping pre-emphasis
7. **Branch 947→961**: Empty audio array (len = 0) skipping compression
8. **Branch 1232→1239**: Empty audio in normalization
9. **Branch 1132→1136**: Audio preprocessing without numpy libraries

### Category 2: Format Handling (MEDIUM Priority - 1 branch)

10. **Branch 1139→1142**: Non-WAV formats (MP3, FLAC, WEBM) skipping conversion

### Category 3: Text Processing (LOW Priority - 2 branches)

11. **Branch 1284→1283**: Emphasis words NOT present in text
12. **Branch 1339→1343**: Chinese text with existing prosody markup

---

## 🧪 Test Implementation Strategy

### Phase 1: Audio Edge Cases (Priority 1)
**File**: `tests/test_speech_processor.py`

```python
class TestAudioEdgeCases:
    """Test edge cases for audio processing - branch coverage"""
    
    def test_analyze_audio_quality_without_numpy(self):
        """Branch 844→874: Test without audio libraries"""
        
    def test_analyze_audio_quality_zero_signal_power(self):
        """Branch 864→874: Test with zero signal/noise"""
        
    def test_speech_enhancement_silent_audio(self):
        """Branch 953→961: Test with all-zero audio"""
        
    def test_reduce_noise_silent_audio(self):
        """Branch 1203→1208: Test noise reduction on silence"""
        
    def test_normalize_audio_silent_non_empty(self):
        """Branch 1234→1239: Test normalization with silent audio"""
        
    def test_speech_enhancement_single_sample(self):
        """Branch 939→947: Test with 1-sample audio"""
        
    def test_speech_enhancement_empty_audio(self):
        """Branch 947→961: Test with empty audio"""
        
    def test_normalize_audio_empty(self):
        """Branch 1232→1239: Test normalization with empty audio"""
        
    def test_preprocess_audio_without_libraries(self):
        """Branch 1132→1136: Test preprocessing without numpy"""
```

### Phase 2: Format Handling (Priority 2)
**File**: `tests/test_speech_processor.py`

```python
class TestAudioFormatHandling:
    """Test non-WAV format handling"""
    
    @pytest.mark.parametrize("audio_format", [
        AudioFormat.MP3,
        AudioFormat.FLAC,
        AudioFormat.WEBM
    ])
    def test_preprocess_audio_non_wav_formats(self, audio_format):
        """Branch 1139→1142: Test with non-WAV formats"""
```

### Phase 3: Text Processing (Priority 3)
**File**: `tests/test_speech_processor.py`

```python
class TestTextProcessingEdgeCases:
    """Test text enhancement edge cases"""
    
    def test_apply_word_emphasis_no_matches(self):
        """Branch 1284→1283: Test with words not in text"""
        
    def test_enhance_chinese_text_existing_prosody(self):
        """Branch 1339→1343: Test with existing prosody markup"""
```

---

## 🔧 Implementation Details

### Shared Fixtures Needed
```python
@pytest.fixture
def empty_audio():
    """Empty audio bytes"""
    return b''

@pytest.fixture
def silent_audio():
    """Silent audio (all zeros, 1 second)"""
    return b'\x00\x00' * 8000  # 16kHz, 1 second

@pytest.fixture
def single_sample_audio():
    """Single audio sample (2 bytes for int16)"""
    return b'\x00\x01'
```

### Mocking Strategy
```python
# For AUDIO_LIBS_AVAILABLE mocking
@pytest.fixture
def mock_audio_libs_unavailable(monkeypatch):
    """Mock numpy unavailable"""
    monkeypatch.setattr(
        'app.services.speech_processor.AUDIO_LIBS_AVAILABLE',
        False
    )
```

---

## ✅ Success Criteria

1. **All 12 branches covered**: 0 partial branches remaining
2. **100% branch coverage**: speech_processor.py shows 100.00%
3. **All tests pass**: 196 + 12-15 new tests = ~210 tests passing
4. **No regressions**: Existing tests still pass
5. **Documentation updated**: Coverage analysis and results documented

---

## 📊 Expected Results

### Before Session 25
- Statement Coverage: 100% (575/575)
- Branch Coverage: 98.35% (12 partial branches)
- Total Tests: 196

### After Session 25
- Statement Coverage: 100% (575/575) ✅
- Branch Coverage: 100% (0 partial branches) ✅
- Total Tests: ~210 ✅
- Technical Debt: 0 ✅

---

## 🎯 Session 25 Workflow

1. **Setup** (5 min)
   - Review Session 24 findings
   - Review `docs/BRANCH_COVERAGE_ANALYSIS.md`
   - Confirm test strategy

2. **Phase 1: Audio Edge Cases** (45 min)
   - Implement 9 audio edge case tests
   - Run coverage after each test
   - Verify branches are covered

3. **Phase 2: Format Handling** (15 min)
   - Implement format handling test
   - Verify branch coverage

4. **Phase 3: Text Processing** (15 min)
   - Implement 2 text processing tests
   - Verify branch coverage

5. **Verification** (15 min)
   - Run full test suite
   - Verify 100% branch coverage
   - Check for regressions

6. **Documentation** (15 min)
   - Update SESSION_25_SUMMARY.md
   - Update DAILY_PROMPT.md
   - Commit and push all changes

---

## 📝 Reference Documents

- **Branch Analysis**: `docs/BRANCH_COVERAGE_ANALYSIS.md`
- **Session 24 Summary**: `docs/SESSION_24_SUMMARY.md`
- **Test Files**: 
  - `tests/test_speech_processor.py`
  - `tests/test_speech_processor_integration.py`

---

## 🚀 Next Steps After Session 25

Once 100% branch coverage is achieved:

**Session 26**: Full Voice Validation (original Session 25 plan)
- End-to-end voice conversation testing
- Multi-turn dialogue validation
- Complete Audio Testing Initiative

**Session 27+**: Resume Phase 3A Core Features Testing
- Return to test progression from Session 2
- Continue systematic feature testing

---

**Template Version**: 25.0  
**Status**: 📋 PLANNED - Ready for Session 25  
**Priority**: HIGH - Zero Technical Debt Policy
