# AI Language Tutor App - Daily Project Resumption Prompt Template

**Project**: AI Language Tutor App  
**Phase**: 3A - Comprehensive Testing (Achieving >90% Coverage)  
**Last Updated**: 2025-11-06 (Session 5 Continued FINAL)  
**Next Session Date**: 2025-11-07

---

## 📋 Quick Status Summary

### Current Project State
- **Overall Coverage**: 55% (up from 44% baseline, +11 percentage points)
- **Modules at 100%**: 9 modules
- **Modules at >90%**: 9 modules ⭐ **+3 from Session 5 Continued**
- **Total Tests**: 854+ passing
- **Warnings**: 0
- **Failing Tests**: 5 (expected, documented in user_management)
- **Environment**: ✅ Production-grade, zero conflicts

### Session 5 Continued Achievements (2025-11-06)
✅ **ollama_service.py**: 76% → 98% (+22pp, 54 tests) - Fixed async mocking  
✅ **qwen_service.py**: 0% → 97% (+97pp, 41 tests) - Chinese-optimized AI  
✅ **ai_router.py**: 41% → 98% (+57pp, 78 tests) - **FIXED PRODUCTION BUG**  
✅ **Environment**: Resolved dependency conflicts, installed anthropic + mistralai  
✅ **Documentation**: Created ENVIRONMENT_SETUP.md, SESSION_6_HANDOVER.md  

**Total Session 5 Continued**: 173 tests created, 2,807 lines of test code, 1 production bug fixed

---

## ⚠️ CRITICAL: Environment Setup

### ALWAYS Use Virtual Environment

**Location**: `ai-tutor-env/`

**Activation**:
```bash
source ai-tutor-env/bin/activate
```

**Why This Matters**:
- Global Python has conflicts (aider-chat, litellm)
- Virtual environment is clean with zero conflicts
- All 247+ AI service tests passing in venv

**Quick Check**:
```bash
# After activation, should show: No broken requirements found
pip check

# Should show all services available
python -c "from app.services.claude_service import claude_service; print('Claude:', claude_service.is_available)"
```

**See**: `ENVIRONMENT_SETUP.md` for complete guide

---

## 🎯 Immediate Next Steps (Priority Order)

### 1. Test speech_processor.py (4-5 hours) ⭐ PRIMARY GOAL
**Status**: 58% coverage (277/660 statements covered)  
**Target**: >90% coverage  
**Priority**: HIGHEST - User's explicit request  
**Complexity**: HIGH - Large module with audio processing  
**File**: `app/services/speech_processor.py`

**Why This Module?**:
- User requested: "ollama, qwen, ai_router, speech_processor"
- 660 statements (largest module yet)
- Critical feature: Speech-to-text and text-to-speech
- Complex: Audio processing, external services

**Recommended Approach**:
1. **Analysis** (30 min): Read file, identify uncovered lines
2. **Infrastructure** (1 hour): Test setup, fixtures, mocks
3. **Core Functionality** (2 hours): STT, TTS, audio handling
4. **Integration** (1 hour): End-to-end, edge cases, >90% coverage

**Alternative** (if too complex):
- content_processor.py (32% coverage, 68 statements)
- sr_sessions.py (15% coverage, 113 statements)
- sr_algorithm.py (17% coverage, 156 statements)

### 2. Continue Phase 3A Testing
Focus on modules with <90% coverage to reach overall 60%+ coverage

---

## 📚 Established Testing Patterns

### AI Service Pattern (Successfully Applied to 5 Services)

**Services**: Claude (96%), Mistral (94%), DeepSeek (97%), Ollama (98%), Qwen (97%)

**Test Structure (35-54 tests typical)**:
1. **Initialization** (3-5 tests)
   - With/without API key
   - With/without library availability
   - Client creation errors

2. **Conversation Prompts** (3-5 tests)
   - Language-specific prompt generation
   - With conversation history
   - Unsupported languages

3. **Helper Methods** (10-13 tests)
   - Message extraction (string, list, default, empty)
   - Model name selection
   - API request building
   - Cost calculation
   - Response content extraction

4. **Response Building** (4 tests)
   - Success with/without context
   - Error with/without model

5. **Generate Response** (4-5 tests)
   - Success case
   - Service unavailable
   - API error
   - With messages/context

6. **Availability & Health** (5-6 tests)
   - Check availability (no client, success, error)
   - Get health status (healthy, error)

7. **Global Instance** (2 tests)
   - Instance exists
   - Correct attributes

### Async Mocking Pattern (aiohttp - Ollama)

```python
# Proper async context manager mocking
mock_response = Mock()
mock_response.status = 200
mock_response.json = AsyncMock(return_value=data)

mock_cm = AsyncMock()
mock_cm.__aenter__.return_value = mock_response
mock_cm.__aexit__.return_value = None

mock_session = Mock()
mock_session.post = Mock(return_value=mock_cm)

async def mock_get_session():
    return mock_session

with patch.object(service, '_get_session', side_effect=mock_get_session):
    result = await service.method()
```

### Router Pattern (ai_router)

**Mock at the right level**:
```python
# Don't mock the entire flow - mock select_provider
selection = ProviderSelection("test", mock_service, "model", "reason", 0.9, 0.01, False)

with patch.object(router, 'select_provider', return_value=selection):
    result = await router.generate_response(messages)
```

---

## 📊 Project Structure Reference

### Key Directories
```
/app
  /services          # AI services, processors, managers
  /core              # Config, models, database
  /api               # FastAPI endpoints
/tests               # All test files
/docs                # Documentation, progress tracking
/data                # Database files, analytics
```

### Critical Files
- `docs/PHASE_3A_PROGRESS.md` - Main testing progress tracker (77 KB)
- `SESSION_6_HANDOVER.md` - Detailed handover for next session (12 KB)
- `ENVIRONMENT_SETUP.md` - Environment setup guide (3.4 KB)
- `tests/test_*_service.py` - AI service tests (247+ tests)
- `pyproject.toml` - Project config, test settings

---

## 🔧 Common Commands

### Environment Setup (CRITICAL - Do First!)

```bash
# Activate virtual environment
source ai-tutor-env/bin/activate

# Verify activation
python -c "import sys; print('In venv:', hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"
# Should show: In venv: True

# Check for conflicts
pip check
# Should show: No broken requirements found
```

### Run Tests with Coverage

```bash
# Specific module with coverage report
pytest tests/test_MODULE.py -v --cov=app.services.MODULE --cov-report=term-missing

# All AI service tests (quick check)
pytest tests/test_*_service.py tests/test_ai_router.py -q
# Should show: 247 passed in ~1.5s

# Full test suite
pytest tests/ -v

# Coverage report (HTML)
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Git Workflow

```bash
# Check recent commits
git log --oneline -n 10

# Check status
git status

# Add and commit
git add [files]
git commit -m "message"
```

---

## 📈 Phase 3A Progress Summary

### Completed Modules (18 at >90%)

**100% Coverage (9 modules)**:
1. scenario_models.py
2. sr_models.py
3. conversation_models.py
4. conversation_manager.py
5. conversation_state.py
6. conversation_messages.py
7. conversation_analytics.py
8. scenario_manager.py
9. conversation_prompts.py

**>90% Coverage (9 modules)**:
10. progress_analytics_service.py (96%)
11. auth.py (96%)
12. user_management.py (98%)
13. claude_service.py (96%)
14. mistral_service.py (94%)
15. deepseek_service.py (97%)
16. ollama_service.py (98%) ⭐ Session 5 Continued
17. qwen_service.py (97%) ⭐ Session 5 Continued
18. ai_router.py (98%) ⭐ Session 5 Continued

### Remaining High-Value Targets
- **speech_processor.py** (58% → >90%) ⭐ NEXT PRIORITY
- content_processor.py (32% → >90%)
- sr_sessions.py (15% → >90%)
- sr_algorithm.py (17% → >90%)

---

## 🐛 Production Bug Fixed in Session 5 Continued

**Critical Bug in ai_router.py**:
```python
# BEFORE (BUG - returned {} instead of False):
def _should_use_local_only(self, force_local, user_preferences):
    return force_local or (user_preferences and user_preferences.get("local_only"))
    # When user_preferences = {}, this returns {} (truthy but not boolean)

# AFTER (FIXED):
def _should_use_local_only(self, force_local, user_preferences):
    if force_local:
        return True
    if user_preferences and user_preferences.get("local_only"):
        return True
    return False  # Now correctly returns False
```

**Impact**: Could have caused routing failures in production when empty user preferences were passed.

---

## 🚀 Daily Session Startup Checklist

### 1. Environment Setup (2 minutes) ⚠️ CRITICAL
- [ ] Activate virtual environment: `source ai-tutor-env/bin/activate`
- [ ] Verify: `pip check` (should show: No broken requirements)
- [ ] Verify Python: `python --version` (should be 3.12.2)
- [ ] Check location: `which python` (should be in ai-tutor-env/)

### 2. Review Previous Session (5 minutes)
- [ ] Read `SESSION_6_HANDOVER.md` (comprehensive guide)
- [ ] Check `docs/PHASE_3A_PROGRESS.md` for current status
- [ ] Review git log: `git log --oneline -n 10`

### 3. Validate Environment (2 minutes)
- [ ] Run quick tests: `pytest tests/test_*_service.py -q`
- [ ] Should show: 247 passed in ~1.5s
- [ ] Check all services available:
  ```bash
  python -c "
  from app.services.claude_service import claude_service
  from app.services.mistral_service import mistral_service
  print('Claude:', claude_service.is_available)
  print('Mistral:', mistral_service.is_available)
  "
  ```

### 4. Plan Session Work (3 minutes)
- [ ] Primary goal: speech_processor.py (58% → >90%)
- [ ] Backup goals: Smaller modules if needed
- [ ] Time estimate: 4-5 hours

### 5. Execute Work
- [ ] Create test file: `tests/test_speech_processor.py`
- [ ] Follow established patterns
- [ ] Run tests frequently
- [ ] Commit incrementally with clear messages

### 6. Wrap Up Session
- [ ] Update `docs/PHASE_3A_PROGRESS.md`
- [ ] Create session summary document
- [ ] Commit all changes
- [ ] Update handover for next session

---

## 🎓 Key Learnings from Session 5 Continued

### Technical Insights
1. **Async mocking requires `__aenter__`/`__aexit__`**: Proper pattern essential for aiohttp
2. **Type checking matters**: Python's truthiness can cause bugs (dict vs bool)
3. **Dataclass constructors**: Must understand exact parameter signatures
4. **Mock at right level**: select_provider mock vs full flow mock
5. **Virtual environment essential**: Global Python has conflicts

### Testing Best Practices
1. **Test helpers individually**: Provides indirect coverage of main methods
2. **Error paths critical**: Always test both success and failure
3. **Pattern reuse accelerates**: Established patterns speed development
4. **98% coverage excellent**: Remaining 2% often defensive code
5. **Zero warnings mandatory**: Production-grade standard

### Process Improvements
1. **Environment documentation prevents errors**: ENVIRONMENT_SETUP.md saves time
2. **Comprehensive handovers enable continuity**: SESSION_6_HANDOVER.md critical
3. **Incremental commits**: Smaller commits easier to review
4. **Testing finds production bugs**: Found boolean return bug in ai_router

---

## 💡 Tips for Success

### Quality Over Speed
- Take time to write comprehensive tests
- Test both success and error paths
- Don't skip edge cases
- Zero warnings is the standard
- 98% coverage is excellent (100% is aspirational)

### Documentation Discipline
- Update progress tracker after each module
- Clear commit messages with statistics
- Create session summaries for continuity
- Document learnings and patterns

### Testing Strategy
- Start with initialization and helpers (easiest)
- Build up to integration tests
- Mock external dependencies
- Use established patterns
- Aim for >90%, celebrate 100%

### Environment Management
- **ALWAYS activate virtual environment first**
- Verify with `pip check` before starting
- Never use global Python for this project
- Reference ENVIRONMENT_SETUP.md if issues

---

## 📞 Quick Reference

### Project Context
- **Purpose**: Comprehensive language learning app with AI tutors
- **Stack**: FastAPI, SQLAlchemy, Pydantic, pytest, multiple AI providers
- **Goal**: >90% test coverage for all critical modules
- **Approach**: Systematic testing, pattern reuse, thorough documentation

### AI Service Providers (All Working!)
1. **Claude** (Anthropic): Primary, general-purpose (96% coverage)
2. **Mistral**: French-optimized, Pierre tutor (94% coverage)
3. **DeepSeek**: Multilingual, Chinese primary, ultra-low cost (97% coverage)
4. **Ollama**: Local, offline, privacy-focused, zero cost (98% coverage)
5. **Qwen**: Chinese-optimized, 小李 tutor (97% coverage)

### Test Coverage Targets
- **Minimum**: 90% statement coverage
- **Aspirational**: 100% coverage
- **Acceptable gaps**: Import error handling, defensive code

---

## 🎯 Session 6 Goals (Next Session)

### Must Complete ⭐
1. **speech_processor.py** (58% → >90%) - Primary goal, user's explicit request

### Success Criteria
- At least 90% coverage for speech_processor.py
- All tests passing, zero warnings
- Documentation fully updated
- Overall project coverage >56%

### Estimated Duration
- **4-5 hours** for speech_processor.py (660 statements, complex)
- **Backup plan**: Test 2-3 smaller modules if speech_processor too complex

---

## 📚 Additional Resources

### Documentation Files
- **SESSION_6_HANDOVER.md** - Complete handover with all context (12 KB)
- **ENVIRONMENT_SETUP.md** - Critical environment setup guide (3.4 KB)
- **docs/PHASE_3A_PROGRESS.md** - Main progress tracker (77 KB)

### Test Files (Reference)
- **tests/test_ollama_service.py** (1,011 lines, 54 tests) - Async pattern
- **tests/test_qwen_service.py** (578 lines, 41 tests) - OpenAI pattern
- **tests/test_ai_router.py** (1,218 lines, 78 tests) - Router pattern
- **tests/test_claude_service.py** (567 lines, 38 tests) - Sync pattern

### Git Commits (Session 5 Continued)
- `7000bc6` - Session 6 handover
- `31e3925` - Environment setup docs
- `460f0a5` - ai_router 98% + bug fix
- `deb5d8c` - qwen 97%
- `e975e12` - ollama 98%

---

**Template Version**: 2.0 (Updated for Session 5 Continued)  
**Last Session**: 5 Continued (2025-11-06)  
**Next Session**: 6 (2025-11-07)  
**Primary Goal**: speech_processor.py testing

---

## ⚠️ REMEMBER: Virtual Environment First!

```bash
# Start EVERY session with:
source ai-tutor-env/bin/activate

# Verify:
pip check  # No broken requirements found
```

**Ready to Continue?** Use this template to resume work efficiently! 🚀
