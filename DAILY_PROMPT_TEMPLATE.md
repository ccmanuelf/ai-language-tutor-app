# Daily Prompt Template - Comprehensive Validation Phase

**Project:** AI Language Tutor App  
**Phase:** Comprehensive Validation & Production Certification  
**Standard:** No shortcuts, no excuses, no mediocrity disguised as completion

---

## 🎯 SESSION OBJECTIVES

**Current Phase:** [FILL IN: Foundation Repair / Warning Elimination / Comprehensive Testing / Feature Validation / Production Certification]

**Today's Primary Goal:** [FILL IN: Specific measurable goal]

**Success Criteria:**
- [ ] [Specific criterion 1]
- [ ] [Specific criterion 2]
- [ ] [Specific criterion 3]

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
```

**Expected Environment:**
- **Python:** 3.12.3 at `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3`
- **pip:** 25.3 or later
- **Virtual Environment:** NONE (using system Python)
- **python-jose:** 3.5.0 or later
- **App Import Test:** `python3 -c "import app.main; print('✓ OK')"` should succeed

**⚠️ CRITICAL:** If any of these fail, STOP and fix environment before proceeding!

---

## 📊 CURRENT STATE SNAPSHOT

### Test Suite Status
- **Total Tests:** [FILL IN: e.g., 5,705]
- **Collection Errors:** [FILL IN: e.g., 0 → target: 0]
- **Passing:** [FILL IN: e.g., 5,705]
- **Failing:** [FILL IN: e.g., 0]
- **Pass Rate:** [FILL IN: e.g., 100%]

### Warning Status
- **Deprecation Warnings:** [FILL IN: e.g., 8+ → target: 0]
- **Linting Errors:** [FILL IN: e.g., unknown]
- **Type Errors:** [FILL IN: e.g., unknown]
- **Other Warnings:** [FILL IN: e.g., unknown]

### Feature Validation Status
| Feature | Session | Status | Validation % |
|---------|---------|--------|--------------|
| Content Organization | 129 | [FILL IN] | [FILL IN]% |
| Production Scenarios | 130 | [FILL IN] | [FILL IN]% |
| Custom Scenarios | 131 | [FILL IN] | [FILL IN]% |
| Analytics System | 132-134 | [FILL IN] | [FILL IN]% |
| Gamification | 135 | [FILL IN] | [FILL IN]% |

### Technical Debt
- **Known Issues:** [FILL IN: Count]
- **Deferred Items:** [FILL IN: Count → target: 0]
- **Deprecated Code:** [FILL IN: Status]

---

## 🚀 TODAY'S WORK PLAN

### Phase Priority: [Foundation Repair / Warning Elimination / Testing / Validation / Certification]

### Specific Tasks (In Order)
1. **[Task Name]**
   - Objective: [What this accomplishes]
   - Success: [How to measure completion]
   - Estimate: [Time estimate]

2. **[Task Name]**
   - Objective: [What this accomplishes]
   - Success: [How to measure completion]
   - Estimate: [Time estimate]

3. **[Task Name]**
   - Objective: [What this accomplishes]
   - Success: [How to measure completion]
   - Estimate: [Time estimate]

### Acceptance Criteria for Today
- [ ] All planned tasks completed OR honestly re-scoped
- [ ] No new warnings introduced
- [ ] No new test failures introduced
- [ ] All changes tested
- [ ] Documentation updated to match reality

---

## ⚠️ CRITICAL REMINDERS

### Non-Negotiable Standards

**Testing:**
- ✅ Run ALL affected tests, not selective tests
- ✅ Fix failures immediately, don't skip them
- ✅ No flaky tests acceptable
- ✅ Integration tests required for cross-feature changes
- ✅ End-to-end validation for user-facing features

**Code Quality:**
- ✅ Zero new warnings introduced
- ✅ Fix existing warnings when encountered
- ✅ No deprecated code patterns
- ✅ Follow current best practices
- ✅ Type hints where appropriate

**Claims and Labels:**
- ❌ Never claim "complete" without validation proof
- ❌ Never call code "production ready" without end-to-end testing
- ❌ Never report pass rates without coverage context
- ❌ Never dismiss warnings as "non-blocking"
- ❌ Never defer fixes "for later"

**Documentation:**
- ✅ Document reality, not aspirations
- ✅ Update docs after validation, not before
- ✅ Include test results in summaries
- ✅ Label TODOs clearly
- ✅ Be honest about gaps and limitations

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

## 📋 BATCH TESTING GUIDELINES

### When to Batch Test
- ✅ After fixing multiple test collection errors
- ✅ After completing a logical unit of work
- ✅ Before claiming a feature validated
- ✅ At natural break points (end of session)

### How to Batch Test Efficiently
```bash
# Test specific feature/module
pytest tests/test_[feature]*.py -v

# Test entire test suite (when collection is fixed)
pytest -v --tb=short -x  # Stop on first failure

# Test with coverage
pytest --cov=app --cov-report=html

# Parallel testing (when stable)
pytest -n auto  # Only when tests are deterministic
```

### Batch Testing Standards
- ✅ Must test ALL affected areas, not just changed files
- ✅ Must fix failures before moving forward
- ✅ Cannot skip tests to maintain green status
- ✅ Must document test results honestly
- ✅ Must re-run after fixes to verify

---

## 🎓 LESSONS APPLIED

### From Session 136

**Lesson 1: Selective Testing is Self-Deception**
- Action: Test comprehensively, not minimally
- Check: Did I test all code paths?

**Lesson 2: Warnings Are Not "Non-Blocking"**
- Action: Fix warnings immediately
- Check: Are there ANY warnings?

**Lesson 3: "Production Ready" Requires Proof**
- Action: Validate before claiming
- Check: Did I test end-to-end?

**Lesson 4: Test Collection Errors Are Critical**
- Action: Fix infrastructure first
- Check: Can all tests be collected?

**Lesson 5: Documentation Theater is Dishonest**
- Action: Document reality only
- Check: Does documentation match code?

**Lesson 6: Integration Testing is Non-Negotiable**
- Action: Test cross-feature interactions
- Check: Did I validate boundaries?

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

## 🎯 VALIDATION PHASE ROADMAP

### Phase 1: Foundation Repair (CURRENT/PENDING)
**Goal:** Make test suite runnable

**Tasks:**
- [ ] Fix all 43 test collection errors
- [ ] Ensure all tests discoverable
- [ ] Validate test infrastructure

**Success:** `pytest --collect-only` succeeds with 0 errors

### Phase 2: Warning Elimination (PENDING)
**Goal:** Zero technical debt

**Tasks:**
- [ ] Fix all deprecation warnings
- [ ] Update deprecated patterns
- [ ] Eliminate linting errors

**Success:** Zero warnings in test run

### Phase 3: Comprehensive Testing (PENDING)
**Goal:** TRUE 100% pass rate

**Tasks:**
- [ ] Run ALL 4,551+ tests
- [ ] Fix every failure
- [ ] Validate deterministic tests

**Success:** 100% pass rate with full coverage

### Phase 4: Feature Validation (PENDING)
**Goal:** Validate Sessions 129-135

**Tasks:**
- [ ] End-to-end test each feature
- [ ] Integration validation
- [ ] Performance testing

**Success:** All features work end-to-end

### Phase 5: Production Certification (PENDING)
**Goal:** TRUE production readiness

**Tasks:**
- [ ] Deployment rehearsal
- [ ] Load testing
- [ ] Monitoring setup

**Success:** Certified for deployment

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

## 🔧 USEFUL COMMANDS

### Test Collection
```bash
# Check what tests can be collected
pytest --collect-only -q

# Show collection errors in detail
pytest --collect-only -v 2>&1 | grep -A 5 "ERROR"
```

### Running Tests
```bash
# Run specific test file
pytest tests/test_[name].py -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run and stop on first failure
pytest -x -v

# Run tests matching pattern
pytest -k "test_pattern" -v
```

### Finding Issues
```bash
# Find deprecation warnings
pytest -W default 2>&1 | grep -i "deprecat"

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
- **Phase 4 Complete When:** All 5 features validated
- **Phase 5 Complete When:** Production certification achieved

### Overall Success
**We can claim success when:**
- ✅ All 4,551+ tests passing
- ✅ Zero warnings of any kind
- ✅ All Sessions 129-135 validated end-to-end
- ✅ Integration conflicts resolved
- ✅ Performance validated
- ✅ Documentation accurate
- ✅ Deployment rehearsal successful
- ✅ Can deploy with confidence

**Not before. Not with excuses. Not with "good enough."**

---

*Template Version: 1.0*  
*Created: December 23, 2025*  
*Purpose: Maintain discipline and standards during comprehensive validation*  
*Principle: Excellence over comfort, truth over theater, validation over claims*
