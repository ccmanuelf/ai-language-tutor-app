# Daily Project Resumption Prompt Template
## AI Language Tutor App - Phase 3A IN PROGRESS

**Last Updated**: 2025-11-07 (Session 7 - Fixed 9 skipped tests, 969 tests passing!)  
**Current Phase**: 🚀 Phase 3A - Comprehensive Testing (IN PROGRESS)  
**Current Status**: 13 modules COMPLETE (8 at 100%, 2 at 96%, 1 at 98%, 1 at 93%, 1 at 97%) ✅  
**Next Task**: Continue Phase 3A - Processing Services (content_processor, sr_sessions, sr_algorithm)

---

## Standardized Daily Startup Prompt

**⚡ COPY AND PASTE THIS INTO NEW CHAT SESSION:**

---

**DAILY PROJECT RESUMPTION - AI Language Tutor App Phase 3A**

Hello! I'm resuming work on the AI Language Tutor App, currently in Phase 3A (Comprehensive Testing).

**PROJECT CONTEXT**:
- **Phase**: Phase 3A - Comprehensive Testing (IN PROGRESS - EXCEPTIONAL momentum!)
- **Achievement**: 13 modules tested, Session 7: Fixed 9 skipped tests, 969 tests passing!
- **Modules at 100%**: 8 (scenario_models, sr_models, conversation_models, conversation_manager, conversation_state, conversation_messages, conversation_analytics, scenario_manager, conversation_prompts)
- **Modules at >96%**: 4 (progress_analytics 96%, auth 96%, user_management 98%, qwen_service 97%, speech_processor 93%)
- **Overall Coverage**: 52% (up from baseline 44%, targeting >70% critical modules)
- **Tech Stack**: FastAPI + FastHTML + multi-LLM routing + Mistral STT + Piper TTS + SQLite/ChromaDB/DuckDB
- **Test Suite**: 969 tests passing, 0 skipped, 0 failures ✅

**🔥 CRITICAL PROJECT PHILOSOPHY**:
> "Quality and performance above all."
> "Time is not a restriction - let's keep the pace."
> "Test coverage > 90% is the minimum bar to move forward."
> "We have plenty of time to do this right."
> **"Remove deprecated, non-existent, or unused code immediately - never skip or omit dead code during testing!"** ⚠️

**🚨 MANDATORY FIRST STEP - READ STATUS FILES**:
Before ANY work, you MUST read these files IN THIS ORDER:

1. **`docs/PHASE_3A_PROGRESS.md`** ⭐ START HERE
   - Real-time Phase 3A progress tracker
   - 12 modules completed with full details
   - Coverage statistics and lessons learned
   - Next module priorities

2. **`docs/SESSION_6_FINAL_REPORT.md`** ⭐ LATEST SESSION
   - Session 6 Continued achievements - speech_processor 93%, Watson debt removed, 5 user_management tests fixed!
   - Session 7 achievements - Fixed 9 skipped tests (5 async + 4 integration scripts)
   - 154 speech_processor tests (removed 12 Watson tests for dead code)
   - **CRITICAL**: 27 lines of Watson dead code removed (methods referencing non-existent functions)
   - Fixed 5 pre-existing user_management test failures (mocking issues)
   - Fixed 5 async tests missing @pytest.mark.asyncio decorators
   - Excluded 4 standalone integration scripts from pytest collection
   - Validation: 969 tests pass, 0 skipped, 0 failures ✅
   - **Key Lesson**: Always remove dead/deprecated code during testing, never skip it!

3. **`docs/SESSION_4_SUMMARY.md`** ⭐ PREVIOUS SESSION
   - Session 4 Continued FINAL achievements - 3 at 100%, 1 at 98%, ZERO WARNINGS!
   - 4 modules completed (conversation_messages 100%, conversation_analytics 100%, scenario_manager 100%, user_management 98%)
   - Bug fixes in scenario_manager + Pydantic V2 migration

4. **`docs/PROJECT_STATUS.md`** ⭐ PROJECT OVERVIEW
   - Overall project status
   - All phase summaries
   - Critical metrics

**📋 PLEASE PERFORM THESE STEPS IN ORDER**:

1. **Load Current Status** (5-10 minutes)
   - Read `docs/PHASE_3A_PROGRESS.md` - Check detailed progress
   - Read `docs/SESSION_3_CONTINUED_FINAL_SUMMARY.md` - Latest achievements
   - Read `docs/PROJECT_STATUS.md` - Overall context

2. **Verify Environment** (2-3 minutes)
   - Run validation: `./ai-tutor-env/bin/python scripts/validate_environment.py` (5/5 checks must pass)
   - Check git status: `git status` (should be clean)
   - Verify tests passing: `./ai-tutor-env/bin/python -m pytest tests/ -q` (969 tests should pass, 0 skipped)
   - Check overall coverage: `./ai-tutor-env/bin/python -m pytest --cov=app --cov-report=term -q | tail -40`

3. **Select Next Module for Phase 3A.14** (Strategic decision)
   
   **🎯 RECOMMENDED: Processing Services Track** (Following speech_processor momentum)
   
   **Priority 1: content_processor.py** (32% coverage) ⭐ NEXT
   - Rationale: Content handling is core functionality
   - Effort: Medium (similar to speech_processor)
   - Impact: High - affects all content generation
   - Clean up: Look for deprecated/unused code patterns
   
   **Priority 2: sr_sessions.py** (Spaced Repetition Sessions)
   - Rationale: SR algorithm session management
   - Effort: Medium
   - Impact: High - critical for learning algorithm
   - Clean up: Check for deprecated session handling
   
   **Priority 3: sr_algorithm.py** (Spaced Repetition Core)
   - Rationale: Core SR algorithm implementation
   - Effort: Medium-High (complex logic)
   - Impact: Very High - heart of learning system
   - Clean up: Verify all algorithm paths are reachable
   
   **Alternative: AI Service Providers** (if processor work is blocked)
   - **ai_router.py** (33% coverage)
     - Core routing logic, medium effort
     - Critical for multi-LLM functionality
   
   - **claude_service.py** (34% coverage)
     - Primary AI provider, medium effort

4. **Testing Strategy** (Follow established patterns)
   
   **Patterns Established**:
   - **Security Testing** (auth.py): Comprehensive coverage of authentication flows
   - **Facade Testing** (conversation_manager.py): Test delegation, not implementation
   - **State Management** (conversation_state.py): Test complete lifecycle
   
   **Best Practices**:
   - Use descriptive test class names: `TestMethodNameOrFeature`
   - 2-5 tests per method: happy path, edge cases, error handling
   - Mock external dependencies (DB, API calls, other services)
   - Test both success and failure paths
   - Validate error messages and types
   - Use side effects for stateful operations (DB loads)
   - **⚠️ CRITICAL**: Remove deprecated/dead/unused code immediately during testing
     - Don't skip or ignore methods referencing non-existent functions
     - Don't leave commented-out code
     - Clean up imports that are no longer used
     - Remove entire test classes if testing deleted functionality
   
   **Test Commands**:
   ```bash
   # Run tests for specific file
   ./ai-tutor-env/bin/python -m pytest tests/test_MODULE_NAME.py -v
   
   # Check coverage for specific module
   ./ai-tutor-env/bin/python -m pytest tests/test_MODULE_NAME.py --cov=app.services.MODULE_NAME --cov-report=term-missing
   ```

5. **Track Progress** (Maintain momentum)
   - Commit after reaching coverage target (usually 90%+)
   - Update `docs/PHASE_3A_PROGRESS.md` after each module
   - Create session handover at end if context limit approaching
   - Keep commits atomic with clear messages

**CRITICAL REQUIREMENTS**:
- 🚨 **ALWAYS** use the virtual environment: `./ai-tutor-env/bin/python`
- 🚨 **ALWAYS** run tests after adding them to verify they pass
- 🚨 **TARGET**: >90% coverage minimum per module (100% is achievable!)
- ❌ DO NOT skip error handling tests
- ❌ DO NOT assume function signatures - read the code
- ✅ DO follow established testing patterns
- ✅ DO use comprehensive mocking strategies
- ✅ DO test both success and error paths
- ✅ DO maintain clear test organization

**CURRENT PROGRESS SNAPSHOT**:
```
Phase 3A Progress: Exceptional Momentum! 🚀

Modules Completed (13 total):
✅ progress_analytics_service.py: 78% → 96% (+18%) - 12 tests
✅ scenario_models.py: 92% → 100% (+8%) - 17 tests
✅ speech_processor.py: 58% → 93% (+35%) - 154 tests, 27 lines dead code removed! ⚠️
✅ sr_models.py: 89% → 100% (+11%) - 20 tests
✅ conversation_models.py: 99% → 100% (+1%) - 15 tests
✅ auth.py: 60% → 96% (+36%) - 63 tests ⭐ CRITICAL
✅ conversation_manager.py: 70% → 100% (+30%) - 24 tests
✅ conversation_state.py: 58% → 100% (+42%) - 22 tests
✅ conversation_messages.py: 39% → 100% (+61%) - 31 tests ⭐ SESSION 4
✅ conversation_analytics.py: 27% → 100% (+73%) - 31 tests ⭐ SESSION 4
✅ scenario_manager.py: 23% → 100% (+77%) - 78 tests ⭐⭐ SESSION 4 - PERFECT!
✅ user_management.py: 12% → 98% (+86%) - 65 tests ⭐⭐ SESSION 4 - 98% + ZERO WARNINGS!
✅ conversation_prompts.py: 100% - existing coverage

Statistics:
- Total tests: 528+ (523 passing, 5 documenting future work)
- Modules at 100%: 8 (including scenario_manager!)
- Modules at >96%: 4
- Overall coverage: 50% (up from 44% baseline)
- Test lines written: 8,300+ lines
- Warning count: 0 (eliminated all Pydantic deprecations)

Quality Metrics:
- All tests passing ✅
- Zero warnings ✅
- Bug fixes included ✅
- Comprehensive coverage ✅
- Excellent documentation ✅
- Clean git history ✅
```

**SESSION GOALS**:
1. Select next module (recommendation: AI services - ai_router, claude_service, mistral_service, deepseek_service)
2. Create comprehensive test file
3. Achieve >70% coverage (>90% if achievable)
4. Commit and document progress
5. Update trackers

**Next Modules to Consider**:
- ai_router.py (33%) - Core routing logic, critical functionality
- claude_service.py (34%) - Primary AI provider
- mistral_service.py (40%) - Secondary provider
- deepseek_service.py (39%) - Third provider
- speech_processor.py (58%) - Already halfway, audio processing
- content_processor.py (32%) - Content handling

---

## Quick Reference Commands

**Validation & Testing**:
```bash
# Validate environment
./ai-tutor-env/bin/python scripts/validate_environment.py

# Run all tests (quick)
./ai-tutor-env/bin/python -m pytest tests/ -q

# Run all tests (verbose)
./ai-tutor-env/bin/python -m pytest tests/ -v

# Run specific test file
./ai-tutor-env/bin/python -m pytest tests/test_MODULE_NAME.py -v

# Check coverage for specific module
./ai-tutor-env/bin/python -m pytest tests/test_MODULE_NAME.py --cov=app.services.MODULE_NAME --cov-report=term-missing

# Check overall project coverage
./ai-tutor-env/bin/python -m pytest tests/ --cov=app --cov-report=term -q | tail -40

# Generate HTML coverage report
./ai-tutor-env/bin/python -m pytest tests/ --cov=app --cov-report=html
# Then open: htmlcov/index.html
```

**Git Workflow**:
```bash
# Check status
git status

# Stage and commit
git add tests/test_MODULE_NAME.py
git commit -m "✅ Phase 3A.X: Achieve Y% coverage for MODULE_NAME (X% to Y%)"

# Update docs
git add docs/PHASE_3A_PROGRESS.md
git commit -m "📊 Update Phase 3A progress: 3A.X complete (MODULE_NAME Y%)"

# Push to remote
git push origin main
```

**Coverage Analysis**:
```bash
# Check specific module coverage
./ai-tutor-env/bin/python -m pytest tests/ --cov=app.services.MODULE_NAME --cov-report=term-missing -q

# Get coverage for multiple modules
./ai-tutor-env/bin/python -m pytest tests/ --cov=app.services --cov-report=term -q | grep "app/services"
```

---

## Testing Patterns Reference

### Pattern 1: Facade Testing (conversation_manager.py)
```python
# Test delegation, not implementation
with patch.object(self.manager.state_manager, "method", new_callable=AsyncMock) as mock:
    mock.return_value = expected_value
    result = await self.manager.method(args)
    mock.assert_called_once_with(expected_args)
```

### Pattern 2: State Management (conversation_state.py)
```python
# Use side effects for stateful operations
async def mock_load_side_effect(id):
    self.manager.active_conversations[id] = mock_context
    return True

with patch.object(self.manager, "_load_from_db") as mock:
    mock.side_effect = mock_load_side_effect
    result = await self.manager.resume(id)
```

### Pattern 3: Security Testing (auth.py)
```python
# Test complete flows with real service instances
auth = AuthenticationService()
token = auth.create_access_token(user_data)
result = auth.verify_token(token)
# Validate security properties
```

---

## End of Prompt Template
