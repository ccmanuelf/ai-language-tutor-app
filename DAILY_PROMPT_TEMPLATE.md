# AI Language Tutor - Session 96 Daily Prompt

**Last Updated:** 2025-12-08 (Session 95 Completion)  
**Next Session:** Session 96 - Critical Architecture Fixes

---

## 🚨 CRITICAL ISSUES DISCOVERED IN SESSION 95

Session 95 revealed **THREE MAJOR ARCHITECTURAL GAPS** that affect core functionality:

1. **Missing Ollama E2E Validation** - No test validates local fallback actually works
2. **Qwen/DeepSeek Code Confusion** - Incomplete migration, dead code, bad alias practice
3. **Budget Manager Overrides User Choice** - Users can't select preferred AI provider

**Read:** `SESSION_95_CRITICAL_GAPS_IDENTIFIED.md` for complete analysis

---

## SESSION 96 OBJECTIVES

### PRIORITY 1: Budget Manager User Control (CRITICAL) 🔴

**Problem:** Budget manager blocks cloud providers and forces Ollama without user consent or notification.

**Files to Fix:**
- `app/api/conversations.py` - Pass user's preferred provider to router
- `app/services/ai_router.py` - Respect `preferred_provider` parameter
- `app/models/user.py` - Add AIProviderSettings
- `app/services/budget_manager.py` - Add notification/override mechanism

**Implementation Tasks:**
1. Add `preferred_provider` parameter to `ai_router.select_provider()`
2. Fix `conversations.py::_get_ai_response()` to pass user's choice
3. Create `BudgetExceededWarning` model with override option
4. Add user settings: `provider_selection_mode` (cost_optimized | user_choice | quality_first)
5. Implement budget notification at 80% threshold
6. Add "Continue anyway?" prompt when budget exceeded but user wants premium provider
7. Update frontend to show budget status and provider selection

**Success Criteria:**
- ✅ User selects "en-claude" → gets Claude (not Ollama)
- ✅ Budget exceeded → user gets notification, can override
- ✅ User can configure: enforce budget ON/OFF
- ✅ User can set provider selection mode preference

---

### PRIORITY 2: Ollama E2E Validation (HIGH) 🟠

**Problem:** Ollama is critical fallback but has NO E2E test - never proven to work.

**Files to Create:**
- `tests/e2e/test_ai_e2e.py::TestOllamaE2E` - Real Ollama API validation

**Implementation Tasks:**
1. Create `TestOllamaE2E` class with real Ollama calls
2. Add fixture to check if Ollama is running (skip if not)
3. Test: Real API call to generate response
4. Test: Model availability check (llama2:7b or similar)
5. Test: Language-specific response quality
6. Test: Fallback scenario - all cloud providers "down" → Ollama works
7. Add Ollama setup instructions to `tests/e2e/README.md`

**Success Criteria:**
- ✅ E2E test makes real call to local Ollama service
- ✅ Test validates response quality and structure
- ✅ Test proves fallback mechanism works end-to-end
- ✅ Documentation explains how to set up Ollama for testing

---

### PRIORITY 3: Qwen/DeepSeek Cleanup (MEDIUM) 🟡

**Problem:** Incomplete migration left dead code, confusing aliases, inconsistent naming.

**Files to Modify:**
- `app/services/ai_router.py` - Remove "qwen" alias
- `app/services/qwen_service.py` - DELETE or move to archive
- All test files - Replace "qwen" with "deepseek"
- Documentation files - Update references

**Implementation Tasks:**
1. Remove line in `ai_router.py`: `ai_router.register_provider("qwen", deepseek_service)`
2. Delete `app/services/qwen_service.py` (or move to `archive/`)
3. Search codebase for "qwen" and replace with "deepseek"
4. Search for "QWEN_API_KEY" and remove (already done in Session 95)
5. Update comments/docs that reference Qwen
6. Update README.md to clarify: DeepSeek is the Chinese language provider
7. Run full test suite to ensure no breakage

**Success Criteria:**
- ✅ No "qwen" references in active code
- ✅ qwen_service.py deleted or in archive/
- ✅ All tests pass after cleanup
- ✅ Documentation accurately reflects DeepSeek usage

---

## SESSION 95 ACHIEVEMENTS ✅

**Critical Production Bug Fixed:**
- `app/api/conversations.py` was creating empty router - FIXED

**Tests Fixed:**
- Integration tests now properly validate real router logic
- E2E tests updated for DeepSeek (removed obsolete Qwen references)
- All Pydantic V2 deprecations eliminated
- All 16 deprecation warnings suppressed

**Documentation Created:**
- `SESSION_95_CORRECTED_SUMMARY.md` - Complete session documentation
- `SESSION_95_CRITICAL_GAPS_IDENTIFIED.md` - Architectural issue analysis

**AI Provider Clarification:**
- Confirmed: Claude, Mistral, DeepSeek, Ollama
- Removed: DASHSCOPE_API_KEY, QWEN_API_KEY

---

## PROJECT CONTEXT

### AI Providers in Production
1. **Claude (Anthropic)** - Primary for English - ✅ E2E tested
2. **Mistral** - Cost-effective alternative - ✅ E2E tested
3. **DeepSeek** - Chinese language - ✅ E2E tested
4. **Ollama** - Local fallback - ❌ NO E2E test

### Required API Keys
- ANTHROPIC_API_KEY
- MISTRAL_API_KEY
- DEEPSEEK_API_KEY
- (Ollama runs locally, no key needed)

### Test Architecture
- **Unit Tests:** Mock all external services
- **Integration Tests:** Mock external APIs, test real router logic
- **E2E Tests:** Real API calls, real validation (cost money!)

### Current Test Status
- Total tests: 4,240
- E2E tests for cloud providers: ✅ Passing
- E2E test for Ollama: ❌ MISSING
- Integration tests: ✅ Fixed in Session 95

---

## IMPORTANT REMINDERS

### Testing Philosophy (From Session 95 Lessons)
1. **100% Coverage ≠ 100% Functionality**
   - Must have E2E tests for all critical paths
   - Mocks should be minimal in integration tests
   - Must validate real external services

2. **Integration Tests Must Test Real Integration**
   - Patch service instances, not classes
   - Let router's real selection logic run
   - Only mock external APIs and budget manager

3. **E2E Tests Must Be Comprehensive**
   - Test ALL providers, including fallbacks
   - Validate failure scenarios
   - Prove functionality with real APIs

### Code Quality Principles
1. **No Aliases for Core Functionality** - Creates confusion
2. **Delete Dead Code Immediately** - Don't let it accumulate
3. **Complete Migrations Fully** - No half-finished transitions
4. **User Intent Must Be Respected** - Don't override user choices silently

### Budget Manager Philosophy
- Budget limits should **inform**, not **block** without consent
- Users should **choose** between cost and quality
- Alerts at 80% threshold, override option at 100%
- Configuration per user preference

---

## HOW TO START SESSION 96

### Step 1: Read Context
```bash
cat SESSION_95_CRITICAL_GAPS_IDENTIFIED.md
cat SESSION_95_CORRECTED_SUMMARY.md
```

### Step 2: Priority Decision
Ask user which priority to tackle first:
- Priority 1: Budget Manager fixes (user experience)
- Priority 2: Ollama E2E test (validation)
- Priority 3: Qwen/DeepSeek cleanup (code quality)

Or tackle in order 1 → 2 → 3.

### Step 3: Implement Systematically
- One feature at a time
- Write tests first (TDD when appropriate)
- Validate each change before moving on
- Document decisions in session summary

### Step 4: Validate Everything
- Run E2E tests after each priority
- Ensure no regressions
- Verify user experience improvements

---

## FILES TO REFERENCE

### Critical Production Files
- `app/api/conversations.py` - Conversation endpoints (**recently fixed**)
- `app/services/ai_router.py` - Provider selection logic
- `app/services/budget_manager.py` - Budget tracking
- `app/services/claude_service.py` - Claude integration
- `app/services/mistral_service.py` - Mistral integration
- `app/services/deepseek_service.py` - DeepSeek integration
- `app/services/ollama_service.py` - Ollama local service

### Test Files
- `tests/e2e/test_ai_e2e.py` - End-to-end provider tests
- `tests/integration/test_ai_integration.py` - Integration tests (**recently fixed**)
- `tests/test_ollama_service.py` - Ollama unit tests (all mocked)

### Documentation
- `SESSION_95_CRITICAL_GAPS_IDENTIFIED.md` - **READ THIS FIRST**
- `SESSION_95_CORRECTED_SUMMARY.md` - Session 95 achievements
- `tests/e2e/README.md` - E2E testing guide

---

## GIT WORKFLOW

### Before Starting
```bash
git status
git pull origin main
```

### During Session
Commit frequently with descriptive messages:
```bash
git add [files]
git commit -m "Session 96: [Priority X] - [What was done]"
```

### End of Session
```bash
git push origin main
```

---

## SESSION TEMPLATE

```markdown
# Session 96 Summary

**Date:** [Date]
**Duration:** [Time]
**Priorities Completed:** [1, 2, 3, or subset]

## Work Completed

### Priority 1: Budget Manager User Control
[Details of implementation]

### Priority 2: Ollama E2E Validation
[Details of tests created]

### Priority 3: Qwen/DeepSeek Cleanup
[Details of cleanup]

## Test Results
[Full test suite results]

## Files Modified
1. [File] - [Changes]

## Lessons Learned
[Key insights]

## Next Steps
[What remains for Session 97]
```

---

## MOTIVATION

**From User:**
> "We are in a good path to continue making this project a success, never quit, never give up, never surrender. Time is not restriction, we have plenty of time to do this right. Quality and performance above all by whatever it takes."

**Principles:**
- Quality over speed
- Real validation over test coverage metrics
- User experience over convenience
- Clean code over quick fixes
- Systematic fixes over band-aids

**Goal:** Build a production-ready AI language tutor with rock-solid architecture, comprehensive testing, and exceptional user experience.

---

**Let's make Session 96 count! 🚀**
