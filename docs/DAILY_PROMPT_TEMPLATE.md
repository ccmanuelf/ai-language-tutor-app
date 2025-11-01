# Daily Project Resumption Prompt Template
## AI Language Tutor App - Phase 3A IN PROGRESS

**Last Updated**: 2025-10-31 (Session 4 COMPLETE - ALL 4 MODULES AT 90%+!)  
**Current Phase**: 🚀 Phase 3A - Comprehensive Testing (IN PROGRESS)  
**Current Status**: 12 modules COMPLETE (7 at 100%, 2 at 96%, 2 at 90%+) ✅  
**Next Task**: Continue Phase 3A - AI Services and Processors

---

## Standardized Daily Startup Prompt

**⚡ COPY AND PASTE THIS INTO NEW CHAT SESSION:**

---

**DAILY PROJECT RESUMPTION - AI Language Tutor App Phase 3A**

Hello! I'm resuming work on the AI Language Tutor App, currently in Phase 3A (Comprehensive Testing).

**PROJECT CONTEXT**:
- **Phase**: Phase 3A - Comprehensive Testing (IN PROGRESS - EXCEPTIONAL momentum!)
- **Achievement**: 12 modules tested, 4 completed in Session 4 (ALL at 90%+!)
- **Modules at 100%**: 7 (scenario_models, sr_models, conversation_models, conversation_manager, conversation_state, conversation_messages, conversation_analytics, conversation_prompts)
- **Modules at >90%**: 4 (progress_analytics 96%, auth 96%, scenario_manager 92%, user_management 90%)
- **Overall Coverage**: 50% (up from baseline 44%, targeting >70% critical modules)
- **Tech Stack**: FastAPI + FastHTML + multi-LLM routing + Mistral STT + Piper TTS + SQLite/ChromaDB/DuckDB

**🔥 CRITICAL PROJECT PHILOSOPHY**:
> "Quality and performance above all."
> "Time is not a restriction - let's keep the pace."
> "Test coverage > 90% is the minimum bar to move forward."
> "We have plenty of time to do this right."

**🚨 MANDATORY FIRST STEP - READ STATUS FILES**:
Before ANY work, you MUST read these files IN THIS ORDER:

1. **`docs/PHASE_3A_PROGRESS.md`** ⭐ START HERE
   - Real-time Phase 3A progress tracker
   - 12 modules completed with full details
   - Coverage statistics and lessons learned
   - Next module priorities

2. **`docs/SESSION_4_SUMMARY.md`** ⭐ LATEST SESSION
   - Session 4 EXCEPTIONAL achievements - ALL 4 MODULES AT 90%+
   - 4 modules completed (conversation_messages 100%, conversation_analytics 100%, scenario_manager 92%, user_management 90%)
   - 177 tests created, 3,949 lines of test code
   - Comprehensive results and recommendations

3. **`docs/SESSION_3_CONTINUED_FINAL_SUMMARY.md`** ⭐ PREVIOUS SESSION
   - Session 3 Continued achievements for context
   - Phase 3A.6 and 3A.7 details
   - Testing patterns established
   - Technical insights and process lessons

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
   - Verify tests passing: `./ai-tutor-env/bin/python -m pytest tests/ -q` (323+ tests should pass)
   - Check overall coverage: `./ai-tutor-env/bin/python -m pytest --cov=app --cov-report=term -q | tail -40`

3. **Select Next Module for Phase 3A.13** (Strategic decision)
   
   **Recommended Priority Order**:
   
   **Option A: AI Service Providers (HIGH VALUE)**
   - **ai_router.py** (33% coverage)
     - Pros: Core routing logic, medium effort
     - Critical for multi-LLM functionality
   
   - **claude_service.py** (34% coverage)
     - Pros: Primary AI provider, medium effort
     - Test API calls, error handling, retries
   
   - **mistral_service.py** (40% coverage)
     - Pros: Secondary provider, medium effort
   
   - **deepseek_service.py** (39% coverage)
     - Pros: Third provider, medium effort
   
   **Option B: Processing Services**
   - **speech_processor.py** (58% coverage)
     - Pros: Already halfway there, medium-high effort
     - Audio processing and transcription
   
   - **content_processor.py** (32% coverage)
     - Pros: Content handling, medium effort

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

Modules Completed (12 total):
✅ progress_analytics_service.py: 78% → 96% (+18%) - 12 tests
✅ scenario_models.py: 92% → 100% (+8%) - 17 tests
✅ sr_models.py: 89% → 100% (+11%) - 20 tests
✅ conversation_models.py: 99% → 100% (+1%) - 15 tests
✅ auth.py: 60% → 96% (+36%) - 63 tests ⭐ CRITICAL
✅ conversation_manager.py: 70% → 100% (+30%) - 24 tests
✅ conversation_state.py: 58% → 100% (+42%) - 22 tests
✅ conversation_messages.py: 39% → 100% (+61%) - 31 tests ⭐ SESSION 4
✅ conversation_analytics.py: 27% → 100% (+73%) - 31 tests ⭐ SESSION 4
✅ scenario_manager.py: 23% → 92% (+69%) - 65 tests ⭐ SESSION 4
✅ user_management.py: 12% → 90% (+78%) - 50 tests ⭐ SESSION 4
✅ conversation_prompts.py: 100% - existing coverage

Statistics:
- Total tests: 500+ passing (0 failing, 0 skipped)
- Modules at 100%: 7
- Modules at >90%: 4
- Overall coverage: 50% (up from 44% baseline)
- Test lines written: 7,500+ lines

Quality Metrics:
- All tests passing ✅
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
