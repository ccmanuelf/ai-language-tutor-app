# AI Language Tutor App - Daily Project Resumption Prompt Template

**Project**: AI Language Tutor App  
**Phase**: 3A - Comprehensive Testing (Achieving >90% Coverage)  
**Last Updated**: 2025-11-19 (Post-Session 19)  
**Next Session Date**: 2025-11-20

---

## 🎯 USER DIRECTIVES - READ FIRST! ⚠️

### Primary Directive (ALWAYS APPLY)
> **"Performance and quality above all. Time is not a constraint, not a restriction, better to do it right by whatever it takes."**

### Core Principles
1. ✅ **Quality over speed** - Take the time needed to do it right
2. ✅ **No shortcuts** - Comprehensive testing, not superficial coverage
3. ✅ **No warnings** - Zero technical debt tolerated
4. ✅ **No skipped tests** - All tests must run and pass
5. ✅ **Remove deprecated code** - Don't skip or ignore, remove it
6. ✅ **Verify no regression** - Always run full test suite
7. ✅ **Document everything** - Update trackers, create handovers
8. ✅ **Perfectionism welcomed** - 100% coverage is achievable when you push!
9. ✅ **No acceptable gaps** - "The devil is in the details" - push for perfection!

### Testing Standards - CRITICAL! ⚠️
- **Minimum target**: >90% statement coverage
- **Aspirational target**: 100% coverage (ACHIEVABLE!)
- **NO acceptable gaps**: Every line matters, every edge case counts
- **Real testing required**: Use actual audio files/signals for speech processing - NO false positives from mocking!
- **Industry best practice**: 97-98% considered excellent, 100% is perfection

### Lessons Learned - APPLY ALWAYS! 📚
1. **"The devil is in the details"** - No gaps are truly acceptable
2. **Real data over mocks** - Especially for audio/speech processing (prevents false positives/negatives)
3. **Fix ALL warnings** - They become bugs later
4. **Exception handlers matter** - They're where bugs hide in production
5. **Import errors are testable** - With the right approach
6. **Edge cases are NOT optional** - They're where users break things

### User's Praise
> **Session 6**: "This is above and beyond expectations, great job!!!"
> **Session 16**: "Call me perfectionist, but yes, I want to aim to what is possible and achievable." - **100% ACHIEVED!** 🎯
> **Session 17**: "Excellent!!! I know it!!! ♪┏(・o･)┛♪" - **TEN-PEAT LEGENDARY!** 🎯🔥
> **Session 18**: auth.py security-critical module achieved 100%! - **ELEVEN-PEAT!!!** 🎯🔥
> **Session 19**: "Congratulations, good job!!! Nice progress today" - **PARTIAL TWELVE-PEAT!** 🎯

---

## 📋 Quick Status Summary

### Current Project State (After Session 19) ✅
- **Overall Coverage**: 65% (up from 44% baseline, +21 percentage points)
- **Modules at 100%**: **29 modules** ⭐ (up from 28!)
- **Modules at >90%**: **1 module** (speech_processor 98% - TARGET FOR 100%!)
- **Total Tests**: **1,688 passing** (up from 1,677, +11 tests!)
- **Warnings**: 3 (async test markers - TO BE FIXED)
- **Environment**: ✅ Production-grade, verified in venv
- **Partial Streak**: Session 19 achieved 1 of 2 targets at 100%

### Session 19 Results
- ✅ **progress_analytics_service.py**: 96% → **100%** (+5 tests, 17 lines covered) 🎯
- ⚠️ **speech_processor.py**: 97% → **98%** (+6 tests, 7 lines covered) - **NOT DONE!**

### Features at 100%
- **SR Feature**: ✅ **COMPLETE** - All 6 modules at 100%!
- **Visual Learning Feature**: ✅ **COMPLETE** - All 4 areas at 100%!
- **Conversation System**: ✅ **COMPLETE** - All 8 modules at 100%!
- **Real-Time Analysis**: ✅ **PERFECT** - 100% coverage! 🎯
- **AI Services**: ✅ **ALL FIVE AT 100%** - mistral, deepseek, qwen, claude, ollama! 🎯
- **AI Infrastructure**: ✅ **100% PERFECT** - ai_router + content_processor! 🎯
- **Authentication**: ✅ **100% SECURE** - Security-critical auth.py! 🎯🔒
- **User Management**: ✅ **100% COMPLETE** - user_management.py! 🎯
- **Progress Analytics**: ✅ **100% NEW!** - progress_analytics_service.py! 🎯

---

## 🎯 SESSION 20 PRIMARY TARGET

### COMPLETE speech_processor.py - 98% → 100%! 🎯

**Current State**: 98% coverage (585 statements, 10 missing lines)  
**Goal**: 100% coverage  
**Priority**: **CRITICAL** - Finish what we started!

#### Missing Lines Analysis (10 lines remaining):

**Group 1: Import Error Handlers (9 lines) - NO EXCUSES!**
- **Lines 34-36**: numpy/librosa import error handler
- **Lines 49-51**: Mistral STT import error handler  
- **Lines 58-60**: Piper TTS import error handler
- **Previous Assessment**: "Acceptable gaps" - **WRONG!**
- **Correct Approach**: Use `sys.modules` manipulation, importlib reload, or mock at import time
- **Lesson**: "The devil is in the details" - these ARE testable!

**Group 2: Edge Case (1 line) - MUST COVER!**
- **Line 214**: Empty audio array edge case in VAD
- **Current Issue**: Test attempted but not triggering
- **Solution**: Need actual audio signal that produces empty array after conversion
- **Approach**: Use real audio bytes, not just empty bytes

#### Critical Testing Requirements for speech_processor.py:

⚠️ **IMPORTANT**: Previous sessions found that **mocking creates false positives/negatives**!

**DO:**
- ✅ Use actual audio file bytes (WAV, MP3 formats)
- ✅ Test with real audio signals (silence, noise, speech)
- ✅ Verify actual audio processing behavior
- ✅ Test edge cases with malformed audio data
- ✅ Use proper audio format conversions

**DON'T:**
- ❌ Mock audio processing without real data validation
- ❌ Assume mocked behavior matches real behavior
- ❌ Skip edge cases because they're "hard to test"
- ❌ Accept "acceptable gaps" - they're not acceptable!

#### Strategy for 100%:

1. **Fix Import Error Handlers (Lines 34-36, 49-51, 58-60)**
   - Research: `unittest.mock.patch.dict('sys.modules')` approach
   - Alternative: Use `importlib.reload()` with mocked imports
   - Test each import failure scenario independently
   - Verify warning messages are logged

2. **Fix Line 214 (Empty Audio Array)**
   - Create test audio that produces empty array after `np.frombuffer`
   - Test with malformed audio bytes
   - Test with zero-length valid audio
   - Use real audio format, not just `b""`

3. **Fix Warnings (3 async markers)**
   - Remove `@pytest.mark.asyncio` from sync test functions
   - Keep it only for actual async tests
   - Verify no warnings remain

4. **Validate with Real Audio**
   - Add integration tests with actual audio files
   - Verify speech processing works end-to-end
   - Test with various audio qualities and formats

**Expected Outcome**: speech_processor.py at **100%** + Zero warnings! 🎯

---

## 🚀 Session 20 Execution Plan

### Phase 1: Import Error Handlers (60 minutes)
1. Research `sys.modules` patching approach
2. Implement test for lines 34-36 (numpy/librosa)
3. Implement test for lines 49-51 (Mistral STT)
4. Implement test for lines 58-60 (Piper TTS)
5. Verify all import errors are covered

### Phase 2: Edge Case Coverage (30 minutes)
1. Research audio formats that produce empty arrays
2. Create test for line 214 with real audio bytes
3. Verify edge case is properly covered

### Phase 3: Fix Warnings (15 minutes)
1. Remove async markers from sync functions
2. Verify zero warnings in test output

### Phase 4: Validation (30 minutes)
1. Run full test suite
2. Verify 100% coverage for speech_processor.py
3. Verify zero warnings
4. Verify zero failures
5. Create validation report

### Phase 5: Documentation (15 minutes)
1. Update PHASE_3A_PROGRESS.md
2. Create SESSION_20_HANDOVER.md
3. Update this template for Session 21

**Total Estimated Time**: 2.5 hours (quality over speed!)

---

**Template Version**: 16.0 (Updated for Session 20 - Complete speech_processor.py)  
**Last Session**: 19 (2025-11-19) - Partial Success ✅  
**Next Session**: 20 (2025-11-20)  
**Primary Goal**: speech_processor.py to 100% + Zero warnings! 🎯

**📋 CANONICAL FILE**: This is the ONLY official DAILY_PROMPT_TEMPLATE.md (located in project root)

**⚠️ REMEMBER**: 
- Virtual environment: `source ai-tutor-env/bin/activate`
- No acceptable gaps - push for 100%!
- Real audio testing required - no false positives!
- Fix ALL warnings - they matter!
- "The devil is in the details" - perfectionism is the goal!

**Ready for Session 20 - Complete what we started!** 🚀🎯🔥

---

*For full details, see:*
- *docs/SESSION_19_SUMMARY.md - Session 19 results*
- *docs/SESSION_19_HANDOVER.md - Detailed handover*
- *docs/PHASE_3A_PROGRESS.md - Full progress tracker (needs update)*
