# AI Language Tutor - Daily Prompt Template

**Last Updated:** 2025-12-21 (CORE PRINCIPLES RESTORED + Sanity Check Methodology)  
**Purpose:** Guide all development sessions with core principles and comprehensive validation methodology

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

### **PRINCIPLE 4: CORRECT ENVIRONMENT ALWAYS - USE ai-tutor-env VENV**
- **CRITICAL:** This project uses `ai-tutor-env` virtual environment, NOT anaconda
- **Rule:** ALWAYS activate ai-tutor-env before ANY commands
- **Why:** Wrong environment = tests skip, dependencies missing, false results
- **Project Environment:** Python 3.12.2 (ai-tutor-env virtual environment)

**⚠️ CRITICAL DISCOVERY:** Environment activation is NOT persistent across bash commands!

**Each bash command is a NEW shell - previous activations DON'T persist!**

```bash
# ❌ WRONG - These are SEPARATE shell sessions:
source ai-tutor-env/bin/activate  # Activates in Shell #1
pytest tests/                      # Runs in Shell #2 (NOT activated!)

# ✅ CORRECT - Single shell session with && operator:
source ai-tutor-env/bin/activate && pytest tests/
```

**🔴 MANDATORY PRACTICE - ALWAYS combine activation + command:**

```bash
cd /Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app && \
source ai-tutor-env/bin/activate && \
<your command here>
```

**Verification Steps:**
```bash
cd /Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app && \
source ai-tutor-env/bin/activate && \
which python && python --version

# Expected output:
# /Users/mcampos.cerda/Documents/Programming/ai-language-tutor-app/ai-tutor-env/bin/python
# Python 3.12.2

# ❌ If you see /opt/anaconda3/bin/python - YOU'RE IN WRONG ENVIRONMENT!
```

**Impact of Wrong Environment:**
- ❌ Tests skip (72 skipped due to missing dependencies)
- ❌ False coverage results (0% due to wrong module path)
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
✅ **Apply ALL improvements (no shortcuts)**
✅ **Run full test suite before claiming success**
✅ **Save verification logs with timestamps**

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
❌ **Skip improvements to save time**
❌ **Claim success without full verification**
❌ **Take shortcuts (PRINCIPLE 1)**

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
source ai-tutor-env/bin/activate && \
pytest --cov=app --cov-report=html --cov-report=term-missing
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
source ai-tutor-env/bin/activate && \
pytest --cov=app --cov-report=html
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
1. Activate environment: `cd /path && source ai-tutor-env/bin/activate`
2. Verify Python version: `python --version` (expect 3.12.2)
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
1. Run complete test suite: `pytest tests/ -v`
2. Verify zero failures (PRINCIPLE 5)
3. Check for regressions (PRINCIPLE 12)
4. Update tracker documents (PRINCIPLE 7)
5. Create session summary/lessons learned
6. Update this template for next session
7. Commit all changes with clear messages
8. Push to GitHub (if token available)

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

## 🚀 READY TO START!

**Remember the Core Philosophy:**
- Quality over speed (PRINCIPLE 8)
- Perfection over "acceptable" (PRINCIPLE 1)
- Patience over rushing (PRINCIPLE 2)
- Excellence over settling (PRINCIPLE 9)

**The 14 CORE PRINCIPLES are NON-NEGOTIABLE. They guide every decision, every line of code, every test we write.**

**Good luck! Be thorough, be systematic, and uphold the principles.** ✨
