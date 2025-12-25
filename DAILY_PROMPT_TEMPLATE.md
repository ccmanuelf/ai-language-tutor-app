# AI Language Tutor - Daily Prompt Template

**Last Updated:** 2025-12-25 (Phase 6 COMPLETE - Ready for Phase 7: Production Certification)  
**Purpose:** Guide all development sessions with foundational principles and comprehensive validation methodology

---

## 🔴 FOUNDATIONAL PRINCIPLES (NON-NEGOTIABLE)

### **PRINCIPLE 1: NO SUCH THING AS "ACCEPTABLE"**
- **Standard:** We aim for PERFECTION by whatever it takes
- **Rule:** 100.00% coverage - NOT 98%, NOT 99%, NOT 99.9%
- **Action:** If coverage is not 100%, we refactor source code to make it testable
- **History:** We have tackled defensive error handling before and succeeded
- **Commitment:** No exceptions, no omissions, no regressions, no compromises
- **Example:** Apply ALL improvements (no shortcuts), achieve TRUE 100% perfection

### **PRINCIPLE 2: PATIENCE IS OUR CORE VIRTUE**
- **Rule:** NEVER kill a long-running process unless unresponsive for >5 minutes
- **Reason:** Killing processes masks issues and creates gaps in coverage
- **Action:** Monitor processes, enlarge timeout windows if needed, but WAIT
- **Lesson:** Premature termination = incomplete data = hidden problems
- **Verification:** Also verify work properly - don't skip test runs
  - Running tests separately ≠ Running full suite
  - Always run complete suite before claiming success
  - 4 minutes is NOTHING - patience prevents quality shortcuts

### **PRINCIPLE 3: TRUE 100% MEANS VALIDATE ALL CODE PATHS**
- **Standard:** 100% coverage = ALL code executed AND validated
- **Rule:** Simply calling functions is NOT enough - must validate actual behavior
- **Critical Discovery:** FastHTML functions need `to_xml()` for HTML validation, not just `str()`
- **Action:** Read implementation to understand exact field names, return types, and transformations
- **Lesson:** "Untested & unverified = Bad Code & Useless project"
- **Requirement:** Every assertion must validate actual output, not just that code runs

**Example:**
```python
# ❌ WRONG - Only calls function, doesn't validate output:
result = language_config_card(...)
assert result is not None  # Useless test!

# ✅ CORRECT - Validates actual HTML generation:
result = language_config_card(...)
result_str = to_xml(result)  # Get actual HTML
assert "Spanish" in result_str  # Validate content
assert "toggleLanguageFeature('es', 'stt'" in result_str  # Validate callbacks
```

### **PRINCIPLE 4: CORRECT ENVIRONMENT ALWAYS**
- **CURRENT DECISION:** We use System Python 3.12.3 (not virtual environment)
- **HISTORICAL NOTE:** The `ai-tutor-env` virtual environment still exists and works identically
- **RATIONALE:** System Python has all required dependencies installed globally
- **BOTH WORK:** Either approach is valid - we chose system Python for simplicity

**⚠️ CRITICAL DISCOVERY:** Environment activation is NOT persistent across bash commands!

**Each bash command is a NEW shell - previous activations DON'T persist!**

```bash
# ❌ WRONG - These are SEPARATE shell sessions:
source ai-tutor-env/bin/activate  # Activates in Shell #1
pytest tests/                      # Runs in Shell #2 (NOT activated!)

# ✅ CORRECT WITH VENV - Single shell session with && operator:
source ai-tutor-env/bin/activate && pytest tests/

# ✅ CORRECT WITH SYSTEM PYTHON - Direct execution:
python3 -m pytest tests/
```

**Current Environment Setup:**

```bash
cd /Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app && \
python3 --version && which python3

# Expected output:
# Python 3.12.3
# /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
```

**Verification Steps:**
```bash
# Verify Python version
python3 --version  # Should be: Python 3.12.3

# Verify pip version
pip3 --version     # Should be: pip 25.3 or later

# Verify not in virtual environment
echo $VIRTUAL_ENV  # Should be: empty (not in venv)

# Verify app can be imported
python3 -c "import app.main; print('✓ OK')"

# Verify python-jose version
pip3 show python-jose | grep Version  # Should be: 3.5.0 or later
```

**Impact of Wrong Environment:**
- ❌ Tests skip (missing dependencies)
- ❌ False coverage results (wrong module path)
- ❌ Missing dependencies
- ❌ Invalid test results
- ✅ Correct environment = all tests pass, proper coverage, accurate results

### **PRINCIPLE 5: ZERO FAILURES ALLOWED**
- **Rule:** ALL tests must pass - no exceptions, even if "unrelated" to current work
- **Action:** When ANY test fails, investigate and fix it immediately
- **Banned:** Ignoring failures as "pre-existing" or "not my problem"
- **Standard:** Full test suite must show 100% pass rate before session completion
- **Verification:** Run complete test suite, wait for full completion, verify zero failures

### **PRINCIPLE 6: FIX BUGS IMMEDIATELY, NO SHORTCUTS**
- **Rule:** When a bug is found, it is MANDATORY to fix it NOW
- **Banned:** "Document for later," "address as future enhancement," "acceptable gap"
- **Banned:** Using --ignore flags during assessments to skip issues
- **Standard:** Cover ALL statements, cover ALL branches, no exceptions

### **PRINCIPLE 7: DOCUMENT AND PREPARE THOROUGHLY**
- **Requirements:**
  1. Save session logs after completion
  2. Write lessons learned
  3. Update project tracker
  4. Update DAILY_PROMPT_TEMPLATE.md for next session
  5. Push latest state to GitHub
- **Purpose:** Keep repositories synced, preserve context for next session

**🔴 GITHUB AUTHENTICATION:**
- **Method:** Uses GITHUB_PERSONAL_ACCESS_TOKEN for authentication
- **Push Command:** `git push origin main` (requires token configured)
- **Note:** If push fails with authentication error, token may need refresh
- **Fallback:** Commits are saved locally and can be pushed later

### **PRINCIPLE 8: TIME IS NOT A CONSTRAINT**
- **Fact:** We have plenty of time to do things right
- **Criteria:** Quality and performance above all
- **Valid Exit Reasons:**
  - Session goals/objectives accomplished ✅
  - Session context becoming too long (save progress, start fresh) ✅
- **Invalid Exit Reason:**
  - Time elapsed ❌ (NOT a decision criteria)
- **Commitment:** Never rush, never compromise standards to "save time"

### **PRINCIPLE 9: EXCELLENCE IS OUR IDENTITY**
- **Philosophy:** "No matter if they call us perfectionists, we call it doing things right"
- **Standards:** We refuse to lower our standards
- **Truth:** "Labels don't define us, our results do"
- **Position:** "If aiming high makes us perfectionists, then good. We are not here to settle."

### **PRINCIPLE 10: VERIFY IMPORTS EARLY**
- **Rule:** After creating ANY file with imports, verify imports work immediately
- **Why:** Prevents cascading import errors at the end
- **Action:** Run a quick import test or simple test case
- **Pattern:** Check existing codebase for correct import paths BEFORE writing imports

**Common Import Patterns:**
```python
# Base class
from app.models.database import Base  # NOT app.models.base

# User role enum
from app.models.database import UserRole  # NOT Role

# Admin authentication
from app.services.admin_auth import require_admin_access  # NOT require_admin

# Database session
db = get_primary_db_session()  # Returns Session directly, NOT generator
```

### **PRINCIPLE 11: COMPREHENSIVE TESTING**
- **Standard:** Test ALL paths - happy, error, edge cases
- **Rule:** Unit tests + Integration tests + E2E tests
- **Requirement:** Real AI integration in E2E tests (not mocked)
- **Coverage:** TRUE 100% = statement + branch coverage
- **Validation:** User quality interventions encouraged

### **PRINCIPLE 12: NO REGRESSIONS EVER**
- **Rule:** New work cannot break existing functionality
- **Verification:** Full test suite must pass after every change
- **Standard:** Zero regression tolerance
- **Action:** If regression found, fix immediately before continuing

### **PRINCIPLE 13: GIT HYGIENE**
- **Rule:** Clean, atomic commits with clear messages
- **Standard:** Each commit should represent one logical change
- **Message Format:** Include emoji + clear description
- **Example:** "✅ Phase 3A.14: Achieve 94% coverage for mistral_service.py"

### **PRINCIPLE 14: CODE EXCELLENCE**
- **Standard:** Production-grade code quality
- **Requirements:**
  - Zero warnings
  - Zero TODOs (or documented in tracker)
  - Clean code patterns
  - Proper error handling
  - Security best practices
- **Validation:** Code review before session completion

---

## ⚠️ CRITICAL REMINDERS

### DO:
✅ Wait for processes to complete (< 5 min is fine)
✅ Fix bugs immediately when found
✅ Run complete test suites (no --ignore)
✅ Write comprehensive tests (happy + error + edge)
✅ Document everything thoroughly
✅ Focus on ONE module at a time
✅ Verify imports as files are created
✅ Check existing patterns before coding
✅ Place specific routes before generic routes
✅ Check actual API responses before writing tests
✅ Apply systematic debugging approach
✅ Apply ALL improvements (no shortcuts)
✅ Run full test suite before claiming success
✅ Save verification logs with timestamps
✅ Test comprehensively, not selectively
✅ Fix warnings immediately
✅ Validate before claiming
✅ Document reality only
✅ Test cross-feature interactions

### DON'T:
❌ Kill processes under 5 minutes
❌ Document bugs "for later"
❌ Use --ignore in assessments
❌ Write minimal tests
❌ Skip documentation
❌ Split focus across modules
❌ Assume import paths
❌ Put generic routes before specific ones
❌ Assume response structures
❌ Skip improvements to save time
❌ Claim success without full verification
❌ Take shortcuts (PRINCIPLE 1)
❌ Claim "complete" without validation proof
❌ Call code "production ready" without end-to-end testing
❌ Report pass rates without coverage context
❌ Dismiss warnings as "non-blocking"
❌ Defer fixes "for later"

---

## 🔧 ENVIRONMENT VERIFICATION (ALWAYS CHECK FIRST!)

### Python Environment Check
```bash
# Verify Python version and location
which python3
python3 --version  # Should be: Python 3.12.3

# Verify pip version and location
which pip3
pip3 --version     # Should be: pip 25.3 or later

# Verify we're using system Python (NOT venv)
echo $VIRTUAL_ENV  # Should be: empty (not in virtual environment)

# Verify python-jose version
pip3 show python-jose | grep Version  # Should be: 3.5.0 or later

# Verify app can be imported
python3 -c "import app.main; print('✓ OK')"
```

**Expected Environment:**
- **Python:** 3.12.3 at `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3`
- **pip:** 25.3 or later
- **Virtual Environment:** NONE (using system Python)
- **python-jose:** 3.5.0 or later
- **App Import Test:** `python3 -c "import app.main; print('✓ OK')"` should succeed

**Alternative (ai-tutor-env):**
If you prefer to use the virtual environment, it's still available and works identically:
```bash
# Activate virtual environment
source ai-tutor-env/bin/activate

# Verify environment
which python  # Should be: ai-tutor-env/bin/python
python --version  # Should be: Python 3.12.2
```

**⚠️ CRITICAL:** If any of these fail, STOP and fix environment before proceeding!

---

## 🎯 SESSION OBJECTIVES

**Current Phase:** Phase 7 - Production Certification (FINAL PHASE)

**Today's Primary Goal:** Complete Production Certification - achieve deployment readiness

**Success Criteria:**
- [ ] Security audit completed - zero vulnerabilities
- [ ] Production configuration validated
- [ ] Deployment readiness assessment passed
- [ ] Final documentation review complete
- [ ] Performance optimization verified
- [ ] Final acceptance testing passed
- [ ] TRUE 100% maintained across all validations

---

## 📊 CURRENT STATE SNAPSHOT (as of Session 140)

### Test Suite Status ✅ PERFECT
- **Total Tests:** 5,736
- **Collection Errors:** 0 ✅
- **Passing:** 5,736 (100%) ✅
- **Failing:** 0 ✅
- **Pass Rate:** 100.00% ✅
- **Runtime:** 361.43 seconds (6:01)

### Warning Status ✅ CLEAN
- **Deprecation Warnings:** 0 ✅
- **Linting Errors:** 0 ✅
- **Type Errors:** 0 ✅
- **Other Warnings:** 0 ✅

### Coverage Status ✅ EXCELLENT
- **Overall Coverage:** >80%
- **Critical Paths:** >95%
- **API Endpoints:** 100%
- **Service Layer:** >90%

### Phase Completion Status
| Phase | Session(s) | Status | Achievement |
|-------|-----------|--------|-------------|
| Phase 1: Foundation | 1-100 | COMPLETE ✅ | Core functionality |
| Phase 2: Advanced Features | 101-128 | COMPLETE ✅ | All features implemented |
| Phase 3: Quality Assurance | 129-137 | COMPLETE ✅ | TRUE 100% (122/122 tests) |
| Phase 4: Comprehensive Testing | 138 | COMPLETE ✅ | Expanded to 5,705 tests |
| Phase 5: Session 139 Validation | 139 | COMPLETE ✅ | 5,705/5,705 tests passing |
| Phase 6: Performance Validation | 140 | COMPLETE ✅ | 31/31 performance tests, 5,736/5,736 total |
| Phase 7: Production Certification | NEXT | PENDING | Final phase |

### Technical Debt ✅ ZERO
- **Known Issues:** 0
- **Deferred Items:** 0
- **Deprecated Code:** 0
- **TODO Comments:** 0 (or tracked)

---

## 🚀 TODAY'S WORK PLAN

### Phase Priority: Production Certification (FINAL PHASE)

### Phase 7 Tasks (In Priority Order)
1. **Security Audit and Hardening**
   - Objective: Verify zero security vulnerabilities, implement production security best practices
   - Success: Security scan passes, all OWASP top 10 mitigated, authentication/authorization validated
   - Deliverable: Security audit report with zero critical issues

2. **Production Configuration Validation**
   - Objective: Verify all production configurations correct and secure
   - Success: Environment variables documented, secrets management validated, configuration tested
   - Deliverable: Production configuration checklist completed

3. **Deployment Readiness Assessment**
   - Objective: Verify application can be deployed to production environment
   - Success: Deployment rehearsal successful, rollback procedures tested, monitoring configured
   - Deliverable: Deployment readiness report

4. **Final Documentation Review**
   - Objective: Ensure all documentation accurate and production-ready
   - Success: README complete, API docs accurate, setup instructions verified, architecture documented
   - Deliverable: Documentation completeness checklist

5. **Performance Optimization Review**
   - Objective: Verify performance meets production standards
   - Success: Load testing passed, response times acceptable, resource usage optimized
   - Deliverable: Performance validation report

6. **Final Acceptance Testing**
   - Objective: End-to-end validation of entire application
   - Success: All critical user journeys tested, edge cases validated, production scenarios verified
   - Deliverable: Final acceptance test report with 100% pass rate

### Acceptance Criteria for Phase 7
- [ ] Security audit passed with zero critical issues
- [ ] Production configuration validated and documented
- [ ] Deployment readiness confirmed with successful rehearsal
- [ ] All documentation accurate and complete
- [ ] Performance meets production standards
- [ ] Final acceptance testing: 100% pass rate
- [ ] TRUE 100% test suite maintained (5,736/5,736)
- [ ] Zero technical debt remaining
- [ ] Application certified for production deployment

---

## 📋 PRE-PRODUCTION SANITY CHECK METHODOLOGY

**Use this methodology when preparing for production release or comprehensive validation**

### Phase 1: Documentation Review (CRITICAL)

#### 1.1 Locate All Tracker Files
**Action:** Find and list ALL session tracking documents across the project.

**Expected Locations:**
- `docs/SESSION_*.md` files
- `docs/*_PLAN.md` files
- `docs/*_PROGRESS.md` files
- `docs/*_COMPLETE.md` files
- `docs/*_TRACKER.md` files
- Any `TODO.md`, `ROADMAP.md`, or similar files

**Validation Questions:**
- Are there any sessions with "IN PROGRESS" status?
- Are there any sessions with incomplete user stories?
- Are there any sessions with pending tasks?
- Are there any sessions with known bugs or issues?

#### 1.2 Review Session Completion Status
**For EACH session document found, verify:**
- [ ] Session objectives clearly stated?
- [ ] All user stories marked as complete?
- [ ] All tasks marked as complete?
- [ ] All tests marked as passing?
- [ ] Backend implementation documented?
- [ ] Frontend implementation documented?
- [ ] Integration verified?
- [ ] Lessons learned documented?

#### 1.3 Cross-Reference Plans vs. Reality
**Verification Steps:**
1. List all planned features
2. Verify each feature exists in codebase
3. Verify each feature has tests
4. Verify each feature is accessible from UI
5. Document any deviations from plan

**Deliverable:** Gap analysis showing:
- Planned but not implemented
- Implemented but not planned
- Implemented differently than planned

#### 1.4 Validate "COMPLETE" Claims
**Evidence Required:**
- [ ] Code files exist and contain claimed functionality
- [ ] Tests exist and are passing
- [ ] Frontend UI exists and is accessible
- [ ] Documentation matches implementation
- [ ] No TODOs or FIXMEs in code
- [ ] No "coming soon" or "not implemented" messages in UI

### Phase 2: Backend Validation (CRITICAL)

#### 2.1 API Inventory & Status
**Action:** Create complete inventory of ALL API endpoints.

```bash
# Find all API route definitions
grep -r "@app.route\|@router.get\|@router.post\|@router.put\|@router.delete\|@router.patch" app/api/
```

**For Each API Endpoint:**
- [ ] Endpoint path documented?
- [ ] HTTP method correct?
- [ ] Request/response schemas defined?
- [ ] Authentication/authorization implemented?
- [ ] Unit tests exist?
- [ ] Integration tests exist?
- [ ] Connected to frontend?
- [ ] Error handling implemented?

#### 2.2 Database Schema Validation
**Action:** Verify database matches all documented tables.

```sql
-- List all tables
SELECT name FROM sqlite_master WHERE type='table';

-- Check table structures
SELECT sql FROM sqlite_master WHERE type='table';

-- Verify foreign keys
PRAGMA foreign_key_list(table_name);
```

#### 2.3 Test Coverage Analysis
**Commands to Run:**
```bash
cd /Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app && \
python3 -m pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Coverage Targets:**
- Overall coverage: >80%
- Critical paths (auth, data persistence): >95%
- API endpoints: 100%
- Service layer: >90%

### Phase 3: Frontend Validation (CRITICAL)

#### 3.1 Page Inventory & Accessibility
**Action:** List ALL frontend pages and verify accessibility.

```bash
# Find all route definitions
grep -r "@app.route\|def.*_page\|def.*_view" app/frontend/
```

**For Each Page:**
- [ ] Route registered in main.py?
- [ ] Navigation link exists?
- [ ] Page loads without errors?
- [ ] Mobile responsive?
- [ ] Error states handled?
- [ ] Loading states implemented?

#### 3.2 Backend-Frontend Integration Verification
**Verification Method:**
1. Grep for fetch() calls in frontend files
2. Match each fetch URL to backend API endpoint
3. Verify HTTP method matches
4. Verify request payload structure matches API schema
5. Verify response handling is correct

```bash
# Find all API calls in frontend
grep -r "fetch(" app/frontend/

# Find all API endpoints in backend
grep -r "@router\." app/api/
```

### Phase 4: Testing Gap Analysis (CRITICAL)

#### 4.1 Identify Untested Code Paths
```bash
cd /Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app && \
python3 -m pytest --cov=app --cov-report=html
# Then open htmlcov/index.html
```

#### 4.2 Identify Missing E2E Tests
**Questions:**
- Are there user stories without E2E tests?
- Are there critical workflows without E2E tests?
- Are there multi-step processes without E2E tests?

#### 4.3 Error Scenario Testing
**Scenarios to Test:**
- API returns 404 (not found)
- API returns 401 (unauthorized)
- API returns 500 (server error)
- Network timeout
- Invalid input data
- Duplicate creation attempts
- Delete non-existent resource
- Access resource owned by another user

### Phase 5: Code Quality & Technical Debt

#### 5.1 Find All TODOs and FIXMEs
```bash
# Find all TODOs
grep -r "TODO" app/ --exclude-dir=__pycache__

# Find all FIXMEs
grep -r "FIXME" app/ --exclude-dir=__pycache__

# Find "not implemented" messages
grep -r "not implemented\|NotImplemented" app/ --exclude-dir=__pycache__
```

#### 5.2 Find Console.logs and Debug Code
```bash
# Find console.log
grep -r "console.log" app/frontend/

# Find print statements (outside logging)
grep -r "print(" app/ --exclude-dir=__pycache__ | grep -v "logger\|logging"

# Find debug flags
grep -r "DEBUG.*True\|debug=True" app/
```

#### 5.3 Security Scan
**Items to Verify:**
- [ ] No passwords in code
- [ ] No API keys in code
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (proper escaping)
- [ ] Input validation on all endpoints
- [ ] Authentication on protected routes
- [ ] Authorization checks before data access

### Phase 6: Documentation Accuracy

#### 6.1 README Validation
**Sections to Validate:**
- [ ] Installation instructions work
- [ ] Dependencies list is complete
- [ ] Setup steps are correct
- [ ] Running tests instructions work
- [ ] Environment variables documented

#### 6.2 API Documentation Validation
**For Each Documented Endpoint:**
- [ ] Endpoint path correct
- [ ] HTTP method correct
- [ ] Request schema accurate
- [ ] Response schema accurate
- [ ] Error responses documented
- [ ] Examples work

---

## 🎯 SESSION EXECUTION BEST PRACTICES

### Before Starting Any Session:
1. Verify environment: `python3 --version` (expect 3.12.3)
2. Verify app imports: `python3 -c "import app.main; print('✓ OK')"`
3. Read previous session's handover/lessons learned
4. Review relevant tracker documents
5. Run full test suite to establish baseline

### During Session:
1. Focus on ONE objective at a time (PRINCIPLE 1)
2. Test frequently (every 10-15 minutes)
3. Fix bugs immediately (PRINCIPLE 6)
4. Commit incrementally with clear messages (PRINCIPLE 13)
5. Document as you go (don't defer to end)

### Before Ending Session:
1. Run complete test suite: `python3 -m pytest tests/ -v`
2. Verify zero failures (PRINCIPLE 5)
3. Check for regressions (PRINCIPLE 12)
4. Update tracker documents (PRINCIPLE 7)
5. Create session summary/lessons learned
6. Update this template for next session
7. Commit all changes with clear messages
8. Push to GitHub (if token available)

---

## 📋 BATCH TESTING GUIDELINES

### When to Batch Test
- ✅ After fixing multiple test collection errors
- ✅ After completing a logical unit of work
- ✅ Before claiming a feature validated
- ✅ At natural break points (end of session)

### How to Batch Test Efficiently
```bash
# Test specific feature/module
python3 -m pytest tests/test_[feature]*.py -v

# Test entire test suite (when collection is fixed)
python3 -m pytest -v --tb=short -x  # Stop on first failure

# Test with coverage
python3 -m pytest --cov=app --cov-report=html

# Parallel testing (when stable)
python3 -m pytest -n auto  # Only when tests are deterministic
```

### Batch Testing Standards
- ✅ Must test ALL affected areas, not just changed files
- ✅ Must fix failures before moving forward
- ✅ Cannot skip tests to maintain green status
- ✅ Must document test results honestly
- ✅ Must re-run after fixes to verify

---

## 🎓 LESSONS APPLIED

### The Questions to Ask

**Before claiming "done":**
1. Did I test this end-to-end?
2. Did I check for integration conflicts?
3. Are there any warnings?
4. Is the documentation accurate?
5. Would this pass a production deployment?
6. Am I being honest about completeness?
7. Did I test error paths?
8. Did I validate performance?

**Before dismissing an issue:**
1. Is this truly non-blocking or am I rationalizing?
2. What's the cost of fixing now vs. later?
3. Does this set a precedent I want to follow?
4. Am I choosing comfort over excellence?

**Before moving to next task:**
1. Is current task truly complete?
2. Did I verify completion with tests?
3. Did I update documentation?
4. Did I check for side effects?
5. Am I leaving technical debt behind?

---

## 🎯 VALIDATION PHASE ROADMAP

### Phase 1: Foundation Repair
**Goal:** Make test suite runnable

**Tasks:**
- [ ] Fix all test collection errors
- [ ] Ensure all tests discoverable
- [ ] Validate test infrastructure

**Success:** `pytest --collect-only` succeeds with 0 errors

### Phase 2: Warning Elimination
**Goal:** Zero technical debt

**Tasks:**
- [ ] Fix all deprecation warnings
- [ ] Update deprecated patterns
- [ ] Eliminate linting errors

**Success:** Zero warnings in test run

### Phase 3: Comprehensive Testing
**Goal:** TRUE 100% pass rate

**Tasks:**
- [ ] Run ALL tests
- [ ] Fix every failure
- [ ] Validate deterministic tests

**Success:** 100% pass rate with full coverage

### Phase 4: Feature Validation
**Goal:** Validate all recent features

**Tasks:**
- [ ] End-to-end test each feature
- [ ] Integration validation
- [ ] Performance testing

**Success:** All features work end-to-end

### Phase 5: Production Certification
**Goal:** TRUE production readiness

**Tasks:**
- [ ] Deployment rehearsal
- [ ] Load testing
- [ ] Monitoring setup

**Success:** Certified for deployment

---

## 📝 END OF SESSION CHECKLIST

### Required Actions Before Ending Session

**Code Status:**
- [ ] All code changes committed with clear messages
- [ ] No uncommitted changes left
- [ ] No commented-out code
- [ ] No TODO comments without issues created

**Test Status:**
- [ ] All affected tests run and passing
- [ ] Test results documented
- [ ] New tests added for new functionality
- [ ] No skipped or ignored tests

**Documentation:**
- [ ] Session log created/updated
- [ ] Lessons learned documented
- [ ] Next session prompt prepared
- [ ] Status summary accurate

**Quality Gates:**
- [ ] Zero new warnings introduced
- [ ] Zero new test failures
- [ ] Zero new linting errors
- [ ] Zero deferred work (or explicitly tracked)

**Honesty Check:**
- [ ] Claims match reality
- [ ] No exaggerated progress
- [ ] Limitations acknowledged
- [ ] Next steps clear and honest

---

## 📊 SESSION LOG TEMPLATE

### Summary
**Date:** [YYYY-MM-DD]  
**Session Number:** [Session Number]  
**Duration:** [Hours worked]  
**Phase:** [Current phase]

### Completed Today
1. [Specific accomplishment with evidence]
2. [Specific accomplishment with evidence]
3. [Specific accomplishment with evidence]

### Metrics Change
| Metric | Start | End | Change |
|--------|-------|-----|--------|
| Collection Errors | [N] | [N] | [+/-N] |
| Deprecation Warnings | [N] | [N] | [+/-N] |
| Tests Passing | [N] | [N] | [+/-N] |
| Features Validated | [N] | [N] | [+/-N] |

### Issues Encountered
1. **[Issue Name]**
   - Problem: [Description]
   - Resolution: [What was done]
   - Learning: [What was learned]

### Technical Debt
**Added:** [None OR specific items with justification]  
**Removed:** [Specific items fixed]  
**Remaining:** [Current count]

### Honest Assessment
**What Went Well:** [Specific successes]  
**What Needs Improvement:** [Specific gaps]  
**What Was Harder Than Expected:** [Honest challenges]  
**What Was Deferred:** [Explicit deferments with reasons]

### Next Session Preparation
**Starting Point:** [Clear starting point]  
**Priority:** [Next priority item]  
**Prerequisites:** [What must be ready]  
**Estimated Scope:** [Realistic estimate]

---

## 📊 QUALITY METRICS TO TRACK

### Test Metrics:
- Total test count
- Pass rate (must be 100%)
- Coverage percentage (target >80%, critical paths >95%)
- E2E test count
- Test execution time

### Code Metrics:
- Modules at TRUE 100% coverage
- Lines of code added/modified
- Number of bugs found and fixed
- Number of TODO items

### Documentation Metrics:
- Session logs created
- Lessons learned documented
- Tracker updates made
- README accuracy

---

## 🔧 USEFUL COMMANDS

### Environment Commands
```bash
# Check Python version and location
which python3
python3 --version

# Verify not in virtual environment
echo $VIRTUAL_ENV  # Should be empty

# Verify app imports
python3 -c "import app.main; print('✓ OK')"

# Alternative: Use virtual environment
source ai-tutor-env/bin/activate && python --version
```

### Test Collection
```bash
# Check what tests can be collected
python3 -m pytest --collect-only -q

# Show collection errors in detail
python3 -m pytest --collect-only -v 2>&1 | grep -A 5 "ERROR"
```

### Running Tests
```bash
# Run specific test file
python3 -m pytest tests/test_[name].py -v

# Run with coverage
python3 -m pytest --cov=app --cov-report=term-missing

# Run and stop on first failure
python3 -m pytest -x -v

# Run tests matching pattern
python3 -m pytest -k "test_pattern" -v
```

### Finding Issues
```bash
# Find deprecation warnings
python3 -m pytest -W default 2>&1 | grep -i "deprecat"

# Count test files
find tests -name "test_*.py" | wc -l

# Find TODO comments
grep -r "TODO\|FIXME\|XXX" app/ --include="*.py"

# Check for print statements (should use logging)
grep -r "print(" app/ --include="*.py"
```

### Code Quality
```bash
# Run type checking
mypy app/

# Run linting
ruff check app/

# Format code
ruff format app/

# Check imports
isort --check-only app/
```

---

## 💪 DAILY AFFIRMATION

**Before Starting Work:**

"Today I will:
- Choose excellence over comfort
- Fix issues, not hide them
- Test comprehensively, not selectively
- Document reality, not aspirations
- Validate before claiming
- Maintain discipline and standards

**I will not:**
- Take shortcuts
- Dismiss warnings
- Defer technical debt
- Claim completion without proof
- Accept 'good enough'
- Compromise on quality

**Because:**
**'We're standing at the threshold of success — don't let good enough steal the victory.'**

**Greatness lives just beyond the line where most people stop.**

**I will not stop at good enough.**"

---

## 🎓 LESSONS LEARNED TEMPLATE

After each session, document:

**What Went Well:**
- [List successes]

**What Went Wrong:**
- [List problems/challenges]

**What We Learned:**
- [List insights/discoveries]

**What We'll Do Differently:**
- [List process improvements]

**Critical Discoveries:**
- [List any critical findings that affect project]

---

## 📈 SUCCESS METRICS

### Daily Targets
- **Test Collection Errors:** Reduce by [N] today
- **Warnings Fixed:** Fix at least [N] warnings
- **Tests Fixed:** Fix at least [N] failing tests
- **Features Validated:** Validate [N] features

### Phase Completion Criteria
- **Phase 1 Complete When:** 0 collection errors
- **Phase 2 Complete When:** 0 warnings
- **Phase 3 Complete When:** 100% tests passing
- **Phase 4 Complete When:** All features validated
- **Phase 5 Complete When:** Production certification achieved

### Overall Success
**We can claim success when:**
- ✅ All tests passing
- ✅ Zero warnings of any kind
- ✅ All features validated end-to-end
- ✅ Integration conflicts resolved
- ✅ Performance validated
- ✅ Documentation accurate
- ✅ Deployment rehearsal successful
- ✅ Can deploy with confidence

**Not before. Not with excuses. Not with "good enough."**

---

## 🚀 READY TO START!

**Remember the Core Philosophy:**
- Quality over speed (PRINCIPLE 8)
- Perfection over "acceptable" (PRINCIPLE 1)
- Patience over rushing (PRINCIPLE 2)
- Excellence over settling (PRINCIPLE 9)

**The 14 CORE PRINCIPLES are NON-NEGOTIABLE. They guide every decision, every line of code, every test we write.**

**Good luck! Be thorough, be systematic, and uphold the principles.** ✨

---

*Template Version: 2.0 - Comprehensive Merge*  
*Last Updated: December 24, 2025*  
*Purpose: Guide all development sessions with foundational principles and validation methodology*  
*Principle: Excellence over comfort, truth over theater, validation over claims*
