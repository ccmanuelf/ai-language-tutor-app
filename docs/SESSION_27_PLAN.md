# Session 27 Plan - Voice System Enhancements 🎤🚀

**Session**: 27  
**Focus**: Voice system enhancements and user experience improvements  
**Priority**: High - User-driven feature development  
**Estimated Time**: 2-3 hours

---

## 🎯 Session Objectives

Based on user feedback, Session 27 will focus on voice system enhancements rather than returning to Phase 3A core testing. This approach will:
1. Improve user experience significantly
2. Validate voice system in production scenarios
3. Test voice switching and selection logic
4. Expand language coverage where possible

---

## 📋 Enhancement Tasks

### 1. User Voice Selection Feature 🎙️

**Goal**: Allow users to choose their preferred voice for each language

**Implementation Steps**:
1. **API Endpoint**: Create `GET /api/voices` to list available voices
   - Return voice name, language, quality level, sample rate
   - Include metadata (accent, gender, description)

2. **API Endpoint**: Create `POST /api/user-preferences/voice` to save voice preference
   - Input: user_id, language, voice_name
   - Store in user preferences/database
   - Return confirmation

3. **API Endpoint**: Create `GET /api/user-preferences/voice/{language}` to get user's preferred voice
   - Return selected voice or default if none selected

4. **Service Layer**: Update `piper_tts_service.py`
   - Add method to get voices by language
   - Add method to get voice metadata
   - Ensure voice selection respects user preferences

5. **Tests**: Create comprehensive test suite
   - Test voice listing endpoint
   - Test voice preference setting/getting
   - Test TTS uses user's preferred voice
   - Test fallback to default when preference not set

**Expected Tests**: ~15-20 tests

**User Benefits**:
- Spanish users can choose Argentina vs Spain vs Mexico accent
- Italian users can choose between Paola (medium) vs Riccardo (low quality)
- Personalized experience per user

---

### 2. Voice Quality Tier Settings ⚙️

**Goal**: Allow users to balance voice quality vs performance

**Quality Tiers**:
- **High**: Use high-quality voices (109MB models)
  - Example: es_AR-daniela-high
  - Best quality, slower generation
  
- **Medium**: Use medium-quality voices (60MB models)
  - Example: en_US-lessac-medium
  - Good quality, balanced performance
  
- **Low**: Use low-quality voices (27MB models)
  - Example: it_IT-riccardo-x_low
  - Acceptable quality, fastest generation

**Implementation Steps**:
1. **Service Layer**: Add quality tier logic
   - Map voices to quality tiers
   - Implement tier-based voice selection
   - Fallback logic when tier not available

2. **API Endpoint**: Create `POST /api/user-preferences/voice-quality`
   - Input: user_id, quality_tier
   - Store preference

3. **Integration**: Update synthesis flow
   - Check user's quality preference
   - Select appropriate voice based on tier
   - Log performance metrics per tier

4. **Tests**: Create test suite
   - Test tier classification
   - Test tier-based selection
   - Test performance differences
   - Test fallback logic

**Expected Tests**: ~10-12 tests

**User Benefits**:
- Mobile users can choose lower quality for faster response
- Desktop users can choose high quality for best experience
- Bandwidth-constrained users have options

---

### 3. Japanese and Korean Voice Research 🇯🇵🇰🇷

**Goal**: Expand language coverage to Japanese and Korean

**Research Tasks**:
1. **Piper Voice Catalog**:
   - Check https://rhasspy.github.io/piper-samples/ for available voices
   - Search for Japanese (ja_JP) voices
   - Search for Korean (ko_KR) voices

2. **Voice Evaluation**:
   - If available: download and test sample voices
   - Evaluate quality, naturalness, clarity
   - Compare multiple voices if available

3. **Implementation**:
   - If voices found: Download .onnx and .json files
   - Add to `app/data/piper_voices/` directory
   - Update language mapping in `piper_tts_service.py`
   - Create validation tests

4. **Documentation**:
   - Document available Japanese voices
   - Document available Korean voices
   - Note quality levels and recommendations

**Expected Outcome**:
- ✅ If voices available: Add Japanese and Korean support
- ⚠️ If voices unavailable: Document limitation, plan alternative approach

**Fallback Options** (if no Piper voices available):
1. Continue using English fallback (current behavior)
2. Research alternative TTS engines for JP/KR
3. Plan for future voice development

**Expected Tests**: ~6-8 tests (if voices available)

---

### 4. Additional Accent Options 🌍

**Goal**: Provide multiple accent options for existing languages

**Current State**:
- **Spanish**: 4 voices (Argentina high, Spain, Mexico x2)
- **Italian**: 2 voices (Paola medium, Riccardo low)
- **English**: 1 voice (US)
- **German**: 1 voice (Standard)
- **French**: 1 voice (Standard)
- **Portuguese**: 1 voice (Brazil)
- **Chinese**: 1 voice (Simplified)

**Enhancement Opportunities**:

1. **English Accents**:
   - Research: British (en_GB), Australian (en_AU), Indian (en_IN)
   - Download if available
   - Test and validate

2. **German Accents**:
   - Research: Austrian (de_AT), Swiss (de_CH)
   - Download if available
   - Test and validate

3. **French Accents**:
   - Research: Canadian (fr_CA), Belgian (fr_BE)
   - Download if available
   - Test and validate

4. **Portuguese Accents**:
   - Research: European Portuguese (pt_PT)
   - Download if available
   - Test and validate

5. **Chinese Variants**:
   - Research: Traditional Chinese (zh_TW), Cantonese (yue)
   - Download if available
   - Test and validate

**Implementation**:
- Download available voices
- Add to voice directory
- Update service configuration
- Create validation tests
- Document accent options

**Expected Tests**: ~5-10 tests per accent added

**User Benefits**:
- UK users can choose British English
- European Portuguese speakers have proper accent
- Better representation of language variants

---

## 📊 Success Criteria

### Must Have ✅
1. User voice selection feature implemented and tested
2. Voice quality tier settings implemented and tested
3. Japanese/Korean voice research completed (add if available)
4. All existing tests still passing (no regressions)
5. Comprehensive documentation for new features

### Should Have 🎯
1. At least 2 additional accent options implemented
2. Performance metrics for quality tiers
3. User preference persistence working
4. API endpoints fully documented

### Nice to Have 🌟
1. 5+ additional accent options
2. Voice preview/sample functionality
3. Voice recommendation engine
4. Admin dashboard for voice management

---

## 🧪 Testing Strategy

### Unit Tests
- Voice listing and filtering
- Preference storage and retrieval
- Quality tier logic
- Voice selection algorithms
- Fallback mechanisms

### Integration Tests
- End-to-end voice selection flow
- User preference persistence
- API endpoint functionality
- Multiple voice switching

### Validation Tests
- New voice models (format, quality, functionality)
- Accent accuracy
- Quality tier performance
- Cross-language functionality

**Expected Total New Tests**: ~40-60 tests

---

## 📈 Expected Outcomes

### Test Suite Growth
- **Current**: 1859 tests
- **Expected**: 1899-1919 tests (+40-60)
- **Target**: All passing, zero regressions

### Voice Coverage
- **Current**: 11 voices, 7 languages
- **Target**: 15-20 voices, 7-9 languages
- **Stretch**: 20+ voices, 9+ languages

### User Experience
- ✅ Personalized voice selection
- ✅ Quality/performance balance control
- ✅ Expanded language coverage
- ✅ Multiple accent options

---

## ⚠️ Potential Challenges

### 1. Voice Availability
**Challenge**: Japanese/Korean voices may not exist in Piper catalog  
**Mitigation**: Research thoroughly, document limitations, plan alternatives

### 2. API Dependencies
**Challenge**: TTS→STT tests still blocked by Mistral API  
**Mitigation**: Focus on TTS enhancements (local), defer STT to future

### 3. Storage Requirements
**Challenge**: More voices = more disk space (~60MB per voice)  
**Mitigation**: Document requirements, consider optional downloads

### 4. Performance Impact
**Challenge**: Voice switching may affect performance  
**Mitigation**: Implement caching, lazy loading, preloading strategies

---

## 🎯 Implementation Priorities

### Phase 1: Core Features (High Priority)
1. User voice selection API endpoints
2. Voice quality tier logic
3. Basic preference storage
4. Comprehensive tests

**Time Estimate**: 1-1.5 hours

### Phase 2: Voice Expansion (Medium Priority)
1. Japanese/Korean voice research
2. Download available accent options
3. Validate new voices
4. Update documentation

**Time Estimate**: 0.5-1 hour

### Phase 3: Polish & Documentation (Low Priority)
1. Performance optimization
2. User documentation
3. API documentation
4. Admin tools (if time permits)

**Time Estimate**: 0.5-1 hour

---

## 📋 Deliverables

### Code
1. User voice selection API endpoints
2. Voice quality tier implementation
3. New voice models (if available)
4. Comprehensive test suite
5. Updated service layer

### Documentation
1. SESSION_27_SUMMARY.md - Session achievements
2. API documentation for new endpoints
3. Voice catalog documentation
4. User guide for voice selection
5. Performance benchmarks

### Tests
1. 40-60 new tests
2. All existing tests passing
3. Zero regressions
4. Comprehensive coverage

---

## 🚀 Session 27 Workflow

### Start of Session
1. ✅ Activate virtual environment
2. ✅ Verify current test suite passes (1859 tests)
3. ✅ Review this plan
4. ✅ Create todo list

### During Session
1. Implement Phase 1 (core features)
2. Test and validate
3. Implement Phase 2 (voice expansion)
4. Test and validate
5. Implement Phase 3 (polish)
6. Final testing

### End of Session
1. Run full test suite
2. Verify zero regressions
3. Create session summary
4. Update DAILY_PROMPT_TEMPLATE.md
5. **Push to GitHub** (mandatory!)

---

## 🎯 Success Metrics

### Technical Metrics
- ✅ 40-60 new tests added
- ✅ All tests passing (1899-1919 total)
- ✅ Zero warnings
- ✅ Zero regressions
- ✅ Code pushed to GitHub

### Feature Metrics
- ✅ User voice selection working
- ✅ Quality tiers implemented
- ✅ 2+ new accents added (target)
- ✅ Japanese/Korean researched (add if available)

### Quality Metrics
- ✅ Comprehensive documentation
- ✅ API endpoints tested
- ✅ Performance benchmarked
- ✅ User experience validated

---

## 📚 Resources

### Piper Voice Catalog
- https://rhasspy.github.io/piper-samples/
- https://github.com/rhasspy/piper/blob/master/VOICES.md

### Current Voice Directory
- `/app/data/piper_voices/`

### Service Files
- `app/services/piper_tts_service.py`
- `app/services/mistral_stt_service.py`

### Test Files
- `tests/test_piper_tts_service.py`
- `tests/test_voice_validation.py`
- `tests/test_tts_stt_integration.py`

---

## ✅ Pre-Session Checklist

- [x] Session 26 complete
- [x] All changes pushed to GitHub
- [x] Session 27 plan created
- [x] DAILY_PROMPT_TEMPLATE.md updated
- [x] Assessment document created
- [ ] Virtual environment ready (do at session start)
- [ ] Current tests passing (verify at session start)

---

**Plan Version**: 1.0  
**Created**: 2025-11-14  
**Next Session**: 27 (TBD)  
**Status**: ✅ Ready for implementation

**User Approved**: Yes - Based on user feedback for voice system enhancements before resuming Phase 3A
