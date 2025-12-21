# Daily Session Prompt Template - SANITY CHECK & PRE-PRODUCTION VALIDATION

**Session Type:** COMPREHENSIVE SANITY CHECK  
**Date:** [To be filled]  
**Objective:** Complete validation of all implementation, documentation, and testing before Production Release  
**Status:** NOT STARTED

---

## 🎯 CRITICAL MISSION

Before ANY production release, we MUST verify:
1. ✅ All planned features are 100% implemented (Backend + Frontend)
2. ✅ All tracker files show complete status
3. ✅ All tests are passing with no gaps
4. ✅ All backend APIs are connected to frontend
5. ✅ All documentation is accurate and complete
6. ✅ No assumptions - everything validated from end-user perspective

**Rule:** NO ASSUMPTIONS. Every claim must be verified with evidence.

---

## 📋 PRE-SESSION CHECKLIST

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

**Deliverable:** Complete list of all tracker documents with their current status.

**Validation Questions:**
- Are there any sessions with "IN PROGRESS" status?
- Are there any sessions with incomplete user stories?
- Are there any sessions with pending tasks?
- Are there any sessions with known bugs or issues?

#### 1.2 Review Session Completion Status
**Action:** For EACH session document found, verify:

**Checklist per Session:**
- [ ] Session objectives clearly stated?
- [ ] All user stories marked as complete?
- [ ] All tasks marked as complete?
- [ ] All tests marked as passing?
- [ ] Backend implementation documented?
- [ ] Frontend implementation documented?
- [ ] Integration verified?
- [ ] Lessons learned documented?

**Critical Sessions to Review:**
- Session 129 (Content Organization) - MUST be 100% complete
- Any session with database changes
- Any session with API changes
- Any session with frontend changes
- Any session with authentication/authorization changes

**Deliverable:** Matrix showing completion status of all sessions.

#### 1.3 Cross-Reference Plans vs. Reality
**Action:** For each plan document (e.g., SESSION_129_FRONTEND_PLAN.md):

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
**Action:** For each document claiming "COMPLETE" status:

**Evidence Required:**
- [ ] Code files exist and contain claimed functionality
- [ ] Tests exist and are passing
- [ ] Frontend UI exists and is accessible
- [ ] Documentation matches implementation
- [ ] No TODOs or FIXMEs in code
- [ ] No "coming soon" or "not implemented" messages in UI

**Deliverable:** Verified completion list with evidence links.

---

### Phase 2: Backend Validation (CRITICAL)

#### 2.1 API Inventory & Status
**Action:** Create complete inventory of ALL API endpoints.

**Method:**
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

**Deliverable:** Complete API inventory with test coverage and frontend integration status.

#### 2.2 Database Schema Validation
**Action:** Verify database matches all documented tables.

**Steps:**
1. List all SQLAlchemy models in `app/models/`
2. List all tables in actual database
3. Verify migrations are up-to-date
4. Check for orphaned tables
5. Check for missing foreign keys
6. Validate indexes exist

**SQL Queries to Run:**
```sql
-- List all tables
SELECT name FROM sqlite_master WHERE type='table';

-- Check table structures
SELECT sql FROM sqlite_master WHERE type='table';

-- Verify foreign keys
PRAGMA foreign_key_list(table_name);
```

**Deliverable:** Database schema report with validation status.

#### 2.3 Service Layer Validation
**Action:** Verify all service layer methods are tested and used.

**For Each Service File:**
- [ ] All public methods have unit tests?
- [ ] All public methods called from API layer?
- [ ] No unused/dead code?
- [ ] Error handling comprehensive?
- [ ] Multi-user isolation verified?

**Deliverable:** Service layer coverage report.

#### 2.4 Test Coverage Analysis
**Action:** Run comprehensive test suite and analyze coverage.

**Commands to Run:**
```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Check for test failures
pytest -v --tb=short

# Run only E2E tests
pytest tests/e2e/ -v

# Run only unit tests
pytest tests/ -v --ignore=tests/e2e/
```

**Coverage Targets:**
- Overall coverage: >80%
- Critical paths (auth, data persistence): >95%
- API endpoints: 100%
- Service layer: >90%

**Deliverable:** Coverage report with gaps identified.

---

### Phase 3: Frontend Validation (CRITICAL)

#### 3.1 Page Inventory & Accessibility
**Action:** List ALL frontend pages and verify accessibility.

**Method:**
```bash
# Find all route definitions
grep -r "@app.route\|def.*_page\|def.*_view" app/frontend/
```

**For Each Page:**
- [ ] Route registered in main.py?
- [ ] Navigation link exists?
- [ ] Page loads without errors?
- [ ] All Session 129 features present (if applicable)?
- [ ] Mobile responsive?
- [ ] Error states handled?
- [ ] Loading states implemented?

**Critical Pages to Verify:**
- `/` (Home)
- `/library` (Content Library) - NEW
- `/collections` (Collections List) - NEW
- `/collections/{id}` (Collection Detail) - NEW
- `/favorites` (Favorites) - NEW
- `/content/{id}` (Content View) - ENHANCED
- `/study-stats` (Study Stats) - NEW
- `/chat` (Chat/Upload)
- `/profile` (User Profile)

**Deliverable:** Page accessibility matrix.

#### 3.2 Backend-Frontend Integration Verification
**Action:** For EACH API endpoint, verify frontend integration.

**Verification Method:**
1. Grep for fetch() calls in frontend files
2. Match each fetch URL to backend API endpoint
3. Verify HTTP method matches
4. Verify request payload structure matches API schema
5. Verify response handling is correct

**Commands:**
```bash
# Find all API calls in frontend
grep -r "fetch(" app/frontend/

# Find all API endpoints in backend
grep -r "@router\." app/api/
```

**Deliverable:** API-to-Frontend mapping table showing:
- API endpoint
- Frontend file using it
- Line number
- Integration status (✅ correct, ⚠️ issues, ❌ not used)

#### 3.3 Session 129 Feature Validation
**Action:** Specifically validate ALL Session 129 features from user perspective.

**User Stories to Manually Test:**

**Epic 1: Collections (5 stories)**
- [ ] US-1.1: Navigate to /collections, click "Create Collection", fill form, verify created
- [ ] US-1.2: Open content library, click "Add to Collection" on content, verify added
- [ ] US-1.3: View collections list, see all collections with correct counts
- [ ] US-1.4: Click collection, see all content items in that collection
- [ ] US-1.5: In collection detail, click "Remove" on item, verify removed

**Epic 2: Tags (4 stories)**
- [ ] US-2.1: Open content view, add tag in input field, verify appears
- [ ] US-2.2: View content card, see tags displayed correctly
- [ ] US-2.3: Click tag or use tag filter, verify filtered results
- [ ] US-2.4: Remove tag from content, verify removed

**Epic 3: Favorites (3 stories)**
- [ ] US-3.1: Click favorite heart on content card, verify marked
- [ ] US-3.2: Navigate to /favorites, see only favorited content
- [ ] US-3.3: Click unfavorite, verify removed from favorites page

**Epic 4: Study Tracking (6 stories)**
- [ ] US-4.1: Click "Start Study Session", verify modal opens with timer
- [ ] US-4.2: Fill in items studied/correct, verify inputs work
- [ ] US-4.3: Click "Complete Session", verify mastery updates
- [ ] US-4.4: View content, see correct mastery badge color
- [ ] US-4.5: Navigate to study stats, see recent sessions
- [ ] US-4.6: View study stats dashboard, verify all metrics accurate

**Deliverable:** User story validation checklist with pass/fail status and screenshots/evidence.

#### 3.4 Navigation Flow Validation
**Action:** Verify all navigation paths work correctly.

**Navigation Paths to Test:**
1. Home → Content Library → Content Detail → Back to Library
2. Home → Collections → Collection Detail → Back to Collections
3. Home → Favorites → Content Detail → Back to Favorites
4. Home → Study Stats → Back to Home
5. Content Detail → Add to Collection → Collection Detail
6. Content Library → Filter by Tag → Clear Filter
7. Content Detail → Start Study → Complete Session → View Stats

**Deliverable:** Navigation flow diagram with validation status.

---

### Phase 4: Testing Gap Analysis (CRITICAL)

#### 4.1 Identify Untested Code Paths
**Action:** Find code without test coverage.

**Method:**
1. Run coverage report: `pytest --cov=app --cov-report=html`
2. Open `htmlcov/index.html`
3. Identify files with <80% coverage
4. For each file, identify untested functions/branches

**Deliverable:** List of untested code paths with priority (Critical/High/Medium/Low).

#### 4.2 Identify Missing E2E Tests
**Action:** Compare user stories to E2E test coverage.

**Current E2E Tests:**
- test_content_organization_e2e.py (5 tests for Session 129)
- [List other E2E test files]

**Questions:**
- Are there user stories without E2E tests?
- Are there critical workflows without E2E tests?
- Are there multi-step processes without E2E tests?

**Deliverable:** E2E test gap analysis.

#### 4.3 Error Scenario Testing
**Action:** Verify error handling for all critical paths.

**Scenarios to Test:**
- API returns 404 (not found)
- API returns 401 (unauthorized)
- API returns 500 (server error)
- Network timeout
- Invalid input data
- Duplicate creation attempts
- Delete non-existent resource
- Access resource owned by another user

**Deliverable:** Error scenario test results.

---

### Phase 5: Code Quality & Technical Debt (IMPORTANT)

#### 5.1 Find All TODOs and FIXMEs
**Action:** Search codebase for incomplete work markers.

**Commands:**
```bash
# Find all TODOs
grep -r "TODO" app/ --exclude-dir=__pycache__

# Find all FIXMEs
grep -r "FIXME" app/ --exclude-dir=__pycache__

# Find all XXXs
grep -r "XXX" app/ --exclude-dir=__pycache__

# Find all HACKs
grep -r "HACK" app/ --exclude-dir=__pycache__

# Find "not implemented" messages
grep -r "not implemented\|NotImplemented" app/ --exclude-dir=__pycache__
```

**Deliverable:** List of all TODOs/FIXMEs with priority classification.

#### 5.2 Find Console.logs and Debug Code
**Action:** Remove debugging artifacts.

**Commands:**
```bash
# Find console.log
grep -r "console.log" app/frontend/

# Find print statements (outside logging)
grep -r "print(" app/ --exclude-dir=__pycache__ | grep -v "logger\|logging"

# Find debug flags
grep -r "DEBUG.*True\|debug=True" app/
```

**Deliverable:** List of debug code to clean up.

#### 5.3 Check for Hardcoded Values
**Action:** Find and replace hardcoded configuration.

**Search for:**
- Hardcoded URLs
- Hardcoded API keys
- Hardcoded user IDs
- Hardcoded file paths
- Magic numbers

**Deliverable:** List of hardcoded values to move to configuration.

#### 5.4 Security Scan
**Action:** Check for common security issues.

**Items to Verify:**
- [ ] No passwords in code
- [ ] No API keys in code
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (proper escaping)
- [ ] CSRF protection (if applicable)
- [ ] Input validation on all endpoints
- [ ] Authentication on protected routes
- [ ] Authorization checks before data access

**Deliverable:** Security audit report.

---

### Phase 6: Documentation Accuracy (IMPORTANT)

#### 6.1 README Validation
**Action:** Verify README.md is accurate and complete.

**Sections to Validate:**
- [ ] Installation instructions work
- [ ] Dependencies list is complete
- [ ] Setup steps are correct
- [ ] Running tests instructions work
- [ ] Environment variables documented
- [ ] API documentation link works

**Deliverable:** Updated README.md if needed.

#### 6.2 API Documentation Validation
**Action:** Verify API docs match implementation.

**For Each Documented Endpoint:**
- [ ] Endpoint path correct
- [ ] HTTP method correct
- [ ] Request schema accurate
- [ ] Response schema accurate
- [ ] Error responses documented
- [ ] Examples work

**Deliverable:** API documentation accuracy report.

#### 6.3 Architecture Documentation
**Action:** Verify architecture docs reflect current state.

**Check:**
- Database schema diagrams
- System architecture diagrams
- Data flow diagrams
- Component interaction diagrams

**Deliverable:** Updated architecture documentation if needed.

---

## 🎯 SESSION EXECUTION PLAN

### Step 1: Documentation Audit (2 hours)
1. Find all tracker files
2. Create completion matrix
3. Identify gaps
4. Document findings

**Deliverable:** `SANITY_CHECK_DOCS_AUDIT.md`

### Step 2: Backend Validation (2 hours)
1. API inventory
2. Database validation
3. Service layer review
4. Test coverage analysis

**Deliverable:** `SANITY_CHECK_BACKEND_AUDIT.md`

### Step 3: Frontend Validation (2 hours)
1. Page accessibility check
2. API integration verification
3. Session 129 feature testing
4. Navigation flow testing

**Deliverable:** `SANITY_CHECK_FRONTEND_AUDIT.md`

### Step 4: Testing Gap Analysis (1 hour)
1. Coverage gaps
2. E2E gaps
3. Error scenario gaps

**Deliverable:** `SANITY_CHECK_TEST_GAPS.md`

### Step 5: Code Quality Review (1 hour)
1. TODO/FIXME cleanup
2. Debug code removal
3. Hardcoded value identification
4. Security scan

**Deliverable:** `SANITY_CHECK_CODE_QUALITY.md`

### Step 6: Final Report (1 hour)
1. Consolidate findings
2. Prioritize issues
3. Create action plan
4. Document sign-off criteria

**Deliverable:** `SANITY_CHECK_FINAL_REPORT.md`

---

## 📊 SUCCESS CRITERIA

### Production-Ready Checklist

**Documentation:**
- [ ] All session trackers show 100% completion
- [ ] All planned features implemented
- [ ] All documentation accurate
- [ ] README works for new developers

**Backend:**
- [ ] All APIs have tests (>95% coverage)
- [ ] All APIs documented
- [ ] Database schema validated
- [ ] No orphaned code
- [ ] All TODOs resolved or documented

**Frontend:**
- [ ] All pages accessible via navigation
- [ ] All APIs connected to UI
- [ ] All Session 129 features verified
- [ ] Error handling complete
- [ ] Loading states complete
- [ ] Mobile responsive

**Testing:**
- [ ] Overall coverage >80%
- [ ] Critical path coverage >95%
- [ ] All E2E tests passing
- [ ] No test gaps in user stories
- [ ] Error scenarios covered

**Code Quality:**
- [ ] No console.log or print() statements
- [ ] No hardcoded credentials
- [ ] No security vulnerabilities
- [ ] No linter errors
- [ ] No type errors (if using TypeScript)

**Integration:**
- [ ] All backend APIs used by frontend
- [ ] All frontend features use backend APIs
- [ ] No broken links
- [ ] No 404 errors
- [ ] No CORS issues

---

## 🚨 CRITICAL REMINDERS

1. **NO ASSUMPTIONS** - Every "complete" claim must be verified with evidence
2. **END-USER PERSPECTIVE** - Test as a user, not as a developer
3. **DOCUMENT EVERYTHING** - Create audit trail for all findings
4. **PRIORITIZE ISSUES** - Not everything needs to be fixed, but must be documented
5. **BE THOROUGH** - Better to spend time now than debug in production

---

## 📝 OUTPUT TEMPLATE

For each phase, create a markdown document with:

```markdown
# [Phase Name] Audit Report

**Date:** [Date]
**Auditor:** Claude
**Status:** [Complete/In Progress]

## Summary
[2-3 sentence overview of findings]

## Methodology
[How the audit was conducted]

## Findings

### ✅ Verified Items
- [Item 1] - Evidence: [link/description]
- [Item 2] - Evidence: [link/description]

### ⚠️ Issues Found
- [Issue 1] - Priority: [Critical/High/Medium/Low] - Impact: [description]
- [Issue 2] - Priority: [Critical/High/Medium/Low] - Impact: [description]

### ❌ Gaps Identified
- [Gap 1] - Required Action: [description]
- [Gap 2] - Required Action: [description]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

## Sign-Off Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Next Steps
1. [Step 1]
2. [Step 2]
```

---

## 🎓 LESSONS LEARNED (To Document)

After sanity check, document:
1. What gaps were found?
2. Why were they missed initially?
3. How to prevent in future sessions?
4. What processes need improvement?

---

**Remember: The goal is CONFIDENCE in production readiness, not perfection. Document what you find, prioritize what matters, and create a clear action plan.**

**Good luck! Be thorough, be systematic, and don't skip steps.** 🚀
