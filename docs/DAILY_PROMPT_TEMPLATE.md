# Daily Project Resumption Prompt Template
## AI Language Tutor App - Phase 2C Refactoring

**Last Updated**: 2025-10-14 (Session 3 Complete)  
**Current Phase**: Phase 2C - High-Complexity Function Refactoring  
**Current Status**: TIER 3A COMPLETE (60% overall, 27/45 functions)  
**Next Milestone**: TIER 3B (6 functions, C:12 complexity)

---

## Standardized Daily Startup Prompt

**⚡ COPY AND PASTE THIS INTO NEW CHAT SESSION:**

---

**DAILY PROJECT RESUMPTION - AI Language Tutor App Phase 2C Refactoring**

Hello! I'm resuming work on the AI Language Tutor App Phase 2C refactoring project. Please help me continue from where we left off.

**PROJECT CONTEXT**:
- **Phase**: Phase 2C - High-Complexity Function Refactoring
- **Goal**: Refactor all C-level complexity functions (C:11-14) to A-level using Extract Method pattern
- **Status**: TIER 3A COMPLETE ✅ (27/45 functions, 60% complete)
- **Next**: TIER 3B - 6 functions with C:12 complexity
- **Tech Stack**: FastAPI + FastHTML + multi-LLM routing + Mistral STT + Piper TTS + SQLite/ChromaDB/DuckDB

**🔥 CRITICAL PROJECT PHILOSOPHY**:
> "Quality and reliability is our goal by whatever it takes. Time is not a constraint."
> "Do not omit or skip anything - production ready system, fully reliable and maintainable."
> "No need to run at full speed - quality and reliability is our priority, not speed."

**🚨 MANDATORY FIRST STEP - READ STATUS FILES**:
Before ANY work, you MUST read these files IN THIS ORDER:

1. **`docs/PROJECT_STATUS.md`** ⭐ START HERE
   - Current status overview and quick reference
   - Next session plan and immediate actions
   - All critical metrics and file references

2. **`validation_artifacts/4.2.6/SESSION_3_HANDOVER.md`** ⭐ MOST IMPORTANT
   - Complete Session 3 summary and accomplishments
   - TIER 3B detailed plan (6 functions to refactor)
   - Validation commands and reference examples
   - Critical DO/DON'T reminders
   - Proven refactoring patterns with examples

3. **`validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md`**
   - Real-time progress tracker for all tiers
   - Function-by-function refactoring results
   - Git commit log and cumulative statistics

**📋 PLEASE PERFORM THESE STEPS IN ORDER**:

1. **Load Current Status** (5-10 minutes)
   - Read `docs/PROJECT_STATUS.md` - Get high-level overview
   - Read `validation_artifacts/4.2.6/SESSION_3_HANDOVER.md` - Get detailed context
   - Read `validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md` - Verify exact progress
   - Review `validation_artifacts/4.2.6/TIER_3A_COMPLETION_REPORT.md` - See latest patterns

2. **Verify Environment** (2-3 minutes)
   - Run `python scripts/validate_environment.py` (5/5 checks must pass)
   - Check git status: `git status` (should be clean)
   - Verify C-level count: `radon cc app/ -s -n C | wc -l` (should show 18)
   - Verify no D/E level: `radon cc app/ -s -n D | wc -l` and `radon cc app/ -s -n E | wc -l` (should be 0)

3. **Confirm Next Task** (1-2 minutes)
   - Next tier: TIER 3B (6 functions, C:12 complexity)
   - First function: `app/services/mistral_service.py`: `MistralService.generate_response` - C(12)
   - Reference similar refactoring: `app/services/claude_service.py:309` (already refactored C:14→A:2)

4. **Execute Refactoring** (following proven pattern from SESSION_3_HANDOVER.md)
   - Read entire function before refactoring
   - Identify logical sections and decision points
   - Extract helpers using Extract Method pattern
   - Keep main function as orchestrator (target A-level, ≤5 complexity)
   - Ensure all helpers are A-B level (≤10 complexity)
   - Run integration tests: `python -m pytest tests/integration/ -v` (8/8 must pass)
   - Commit atomically with descriptive message
   - Push immediately to GitHub

5. **Track Progress**
   - Update `validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md` after every 2-3 functions
   - Create TIER 3B completion report when tier is done
   - Maintain real-time todo list during session

**CRITICAL REQUIREMENTS**:
- 🚨 **NEVER** skip reading the 3 mandatory status files (PROJECT_STATUS.md, SESSION_3_HANDOVER.md, PHASE_2C_PROGRESS_TRACKER.md)
- 🚨 **ALWAYS** run integration tests after each refactoring (8/8 must pass, zero tolerance for regressions)
- 🚨 **ALWAYS** verify complexity reduction with radon after refactoring
- ❌ DO NOT batch multiple refactorings without testing between them
- ❌ DO NOT skip git commit/push after each function
- ❌ DO NOT create helpers with complexity > 10
- ✅ DO follow proven Extract Method pattern from TIER 3A examples
- ✅ DO use descriptive helper function names (_validate_*, _extract_*, _build_*, etc.)
- ✅ DO cross-reference similar already-refactored functions
- ✅ DO maintain atomic git commits with emoji prefixes (✅ TIER 3B (X/6): ...)

**SUCCESS CRITERIA (Per Function)**:
- ✅ Main function reduced to A-level (complexity ≤5)
- ✅ All helper functions at A-B level (complexity ≤10)
- ✅ Integration tests: 8/8 PASSING (no regressions)
- ✅ Radon complexity verified
- ✅ Git commit with descriptive message
- ✅ Pushed to GitHub origin/main

**OUTPUT EXPECTED**:
1. Confirmation that all 3 mandatory status files have been read
2. Current environment validation results (5/5 checks)
3. Current C-level function count verification (should be 18)
4. Next function to refactor identified (MistralService.generate_response)
5. Reference to similar already-refactored function (ClaudeService.generate_response)
6. Proposed refactoring approach based on proven patterns
7. Confirmation ready to begin refactoring

**REFERENCE FILES HIERARCHY**:

**Tier 1 - MUST READ FIRST** (Critical for resumption):
- `docs/PROJECT_STATUS.md` - Current status dashboard
- `validation_artifacts/4.2.6/SESSION_3_HANDOVER.md` - Latest session handover
- `validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md` - Real-time progress tracker

**Tier 2 - READ FOR CONTEXT** (Deep understanding):
- `validation_artifacts/4.2.6/TIER_3A_COMPLETION_REPORT.md` - Latest tier completion report
- `validation_artifacts/4.2.6/PHASE_2C_REVISED_EXECUTION_PLAN.md` - Full execution plan (45 functions)
- `validation_artifacts/4.2.6/PHASE_2C_REALITY_CHECK_REPORT.md` - Documentation verification

**Tier 3 - READ FOR HISTORY** (Background context):
- `validation_artifacts/4.2.6/PHASE_2C_SESSION_1_PROGRESS_REPORT.md` - Session 1 details
- `validation_artifacts/4.2.6/PHASE_2C_SESSION_2_PROGRESS_REPORT.md` - Session 2 details
- `validation_artifacts/4.2.6/PHASE_2B_FINAL_COMPLETION_REPORT.md` - Phase 2B completion
- `docs/COMPLEXITY_C_FUNCTIONS_DOCUMENTATION.md` - C-level function documentation

**CODE REFERENCE EXAMPLES** (Best refactoring patterns):
- `app/services/claude_service.py:309` - Best Extract Method example (C:14→A:2, 9 helpers, 86% reduction)
- `app/api/ai_models.py:140` - Best filter chain example (C:13→A:2, 4 helpers, 85% reduction)
- `app/services/progress_analytics_service.py:199` - Best dataclass example (C:13→A:3, 2 helpers, 77% reduction)

**VALIDATION COMMANDS**:
```bash
# Environment validation (MANDATORY at session start)
python scripts/validate_environment.py

# Verify C-level function count (should be 18)
radon cc app/ -s -n C | wc -l

# Verify no D/E level functions (should be 0)
radon cc app/ -s -n D | wc -l
radon cc app/ -s -n E | wc -l

# Check specific function complexity (after refactoring)
radon cc app/services/mistral_service.py -s | grep generate_response

# Run integration tests (8/8 must pass)
python -m pytest tests/integration/ -v

# Git workflow (after each function)
git add .
git commit -m "✅ TIER 3B (1/6): Refactor MistralService.generate_response C(12)→A(X) - XX% reduction"
git push origin main
```

Ready to continue! Please confirm you've read the status files and provide today's execution plan.

---

## Daily Session Completion Template

**⚡ USE THIS AT END OF EACH SESSION:**

---

**DAILY SESSION COMPLETION - Phase 2C Refactoring**

Please help me properly close today's work session and prepare for next session.

**SESSION SUMMARY**:
- **Date**: [Today's date]
- **Duration**: [Hours worked]
- **Tier Worked On**: [TIER 3B, 3C, etc.]
- **Functions Completed**: [X/6 or X/12]

**FUNCTIONS REFACTORED TODAY**:
| Function | File | Before | After | Reduction | Helpers | Status |
|----------|------|--------|-------|-----------|---------|--------|
| [name] | [path:line] | C(X) | A(X) | XX% | X | ✅/⏳ |

**VALIDATION RESULTS**:
- **Integration Tests**: [X/8 passing]
- **Radon C-level Count**: [Current count]
- **Radon D/E-level Count**: [Should be 0]
- **Regressions**: [Count, should be 0]
- **Git Commits**: [Number of commits made]
- **GitHub Sync**: [✅ synchronized / ❌ pending]

**QUALITY METRICS**:
- **Average Complexity Reduction**: [XX%]
- **Helper Functions Created**: [Total count]
- **Average Helper Complexity**: [X.X]
- **Test Pass Rate**: [XX%]

**ISSUES ENCOUNTERED**:
- [List any problems, blockers, or concerns]
- [None if session went smoothly]

**NEXT SESSION PLAN**:
- **Resume At**: [Next function to refactor]
- **Remaining in Current Tier**: [X functions]
- **Estimated Time**: [X-Y hours]
- **Reference Function**: [Similar already-refactored function for pattern reference]

**🚨 MANDATORY SESSION CLOSURE TASKS**:
- [ ] All refactored functions committed and pushed to GitHub
- [ ] `validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md` updated with today's progress
- [ ] Integration tests verified: 8/8 passing
- [ ] Radon complexity verified: C-level count correct
- [ ] Session handover document created/updated (if tier complete)
- [ ] `docs/PROJECT_STATUS.md` updated (if significant milestone reached)
- [ ] Git working tree clean (no uncommitted changes)

**TIER COMPLETION CHECKLIST** (if tier complete):
- [ ] Create `TIER_XX_COMPLETION_REPORT.md` with detailed results
- [ ] Update overall statistics in `PHASE_2C_PROGRESS_TRACKER.md`
- [ ] Create session handover document for next session
- [ ] Update `docs/PROJECT_STATUS.md` with new milestone
- [ ] Git commit documentation updates
- [ ] Push all changes to GitHub

**FILES TO UPDATE**:
1. `validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md` - Add today's functions to appropriate tier section
2. `docs/PROJECT_STATUS.md` - Update completion percentage and next milestone (if changed)
3. `validation_artifacts/4.2.6/SESSION_X_HANDOVER.md` - Create new handover document

Please execute all mandatory session closure tasks and provide next session's starting context.

---

## Emergency Recovery Template

**⚡ USE THIS IF PROJECT STATE IS UNCLEAR:**

---

**PROJECT RECOVERY - Status Assessment Required**

The project state appears unclear or I'm unsure how to proceed. Please help me assess and recover.

**🚨 RECOVERY STEPS**:

1. **Read Status Files** (CRITICAL)
   - Read `docs/PROJECT_STATUS.md` - Get current status overview
   - Read latest session handover in `validation_artifacts/4.2.6/SESSION_X_HANDOVER.md`
   - Read `validation_artifacts/4.2.6/PHASE_2C_PROGRESS_TRACKER.md` - Verify exact progress

2. **Verify Environment**
   ```bash
   python scripts/validate_environment.py
   radon cc app/ -s -n C | wc -l  # Should match documented count
   radon cc app/ -s -n D | wc -l  # Should be 0
   radon cc app/ -s -n E | wc -l  # Should be 0
   python -m pytest tests/integration/ -v  # Should be 8/8 passing
   git status  # Check for uncommitted changes
   ```

3. **Cross-Verify Progress**
   - Compare `PHASE_2C_PROGRESS_TRACKER.md` claimed progress vs actual radon output
   - Verify claimed completed functions actually have reduced complexity
   - Check git log matches documented commits

4. **Identify Discrepancies**
   - List any mismatches between documentation and actual code
   - Identify any uncommitted changes
   - Note any failing tests

5. **Recovery Actions**
   - If documentation is ahead of code: Review recent commits, identify missing work
   - If code is ahead of documentation: Update progress tracker and status files
   - If tests are failing: Investigate last commit that passed tests
   - If complexity counts don't match: Run fresh radon analysis and update documentation

**CRITICAL QUESTIONS**:
1. What is the current C-level function count according to radon?
2. What is the current C-level function count according to PHASE_2C_PROGRESS_TRACKER.md?
3. Do integration tests pass? (8/8 expected)
4. What is the last git commit message?
5. Are there uncommitted changes?
6. What tier should we be working on according to documentation?

**EXPECTED RECOVERY OUTPUT**:
- Current verified state of the codebase (radon analysis)
- Discrepancies between documentation and code (if any)
- Recommended safe path forward
- Which files need updating to synchronize state
- Confirmation of what the next task should be

---

## Quick Reference: Validation Commands

### Session Start Validation
```bash
# Environment check (5/5 must pass)
python scripts/validate_environment.py

# Complexity analysis (verify starting state)
radon cc app/ -s -n C | wc -l  # Expected: 18 (or current documented count)
radon cc app/ -s -n D | wc -l  # Expected: 0
radon cc app/ -s -n E | wc -l  # Expected: 0

# Get detailed list of C-level functions
radon cc app/ -s -n C

# Test suite verification (8/8 expected)
python -m pytest tests/integration/ -v

# Git status check
git status
git log --oneline -10
```

### Per-Function Validation (After Each Refactoring)
```bash
# Check specific function complexity
radon cc app/services/[file_name].py -s | grep [function_name]

# Run full integration test suite (8/8 must pass)
python -m pytest tests/integration/ -v

# Static analysis check
python -m pyflakes app/services/[file_name].py

# Git commit
git add app/services/[file_name].py
git commit -m "✅ TIER XB (X/6): Refactor [FunctionName] C(12)→A(X) - XX% reduction"
git push origin main
```

### Session End Validation
```bash
# Verify final C-level count
radon cc app/ -s -n C | wc -l

# Verify no regressions (D/E should still be 0)
radon cc app/ -s -n D | wc -l
radon cc app/ -s -n E | wc -l

# Final test suite run
python -m pytest tests/integration/ -v

# Verify all changes pushed
git status  # Should be clean
git log --oneline -5  # Verify recent commits

# Check remote sync
git fetch origin
git status  # Should show "up to date with origin/main"
```

---

## Notes for Effective Daily Usage

### Pre-Session Checklist (EVERY SESSION)
- [ ] Read `docs/PROJECT_STATUS.md` (2-3 min)
- [ ] Read latest session handover (5-7 min)
- [ ] Read `PHASE_2C_PROGRESS_TRACKER.md` (2-3 min)
- [ ] Run environment validation (1 min)
- [ ] Verify radon counts match documentation (1 min)
- [ ] Run integration tests to confirm baseline (2 min)
- [ ] Review reference examples for today's work (3-5 min)

**Total Pre-Session Time**: ~15-20 minutes (MANDATORY, not optional)

### During Session Best Practices
1. **One Function at a Time**: Complete full cycle before moving to next
2. **Test After Each Function**: Never batch multiple refactorings without testing
3. **Commit Immediately**: Don't accumulate uncommitted changes
4. **Reference Similar Functions**: Use already-refactored functions as templates
5. **Track Progress**: Update mental/written todo list as you work
6. **Take Breaks**: 5-10 min break after every 2-3 functions

### Post-Session Checklist (EVERY SESSION)
- [ ] All functions committed and pushed (0 min - should be already done)
- [ ] Update `PHASE_2C_PROGRESS_TRACKER.md` (5-10 min)
- [ ] Create/update session handover if tier complete (15-20 min)
- [ ] Update `PROJECT_STATUS.md` if milestone reached (5-10 min)
- [ ] Final integration test run (2 min)
- [ ] Final radon verification (2 min)
- [ ] Git working tree clean verification (1 min)

**Total Post-Session Time**: ~10-45 minutes (depending on milestone)

### Common Pitfalls to Avoid
1. **Starting without reading status files** - Leads to duplicate work or wrong task
2. **Batching multiple refactorings** - Makes debugging regressions harder
3. **Skipping integration tests** - Regressions go unnoticed
4. **Generic helper names** - Reduces code readability
5. **Creating high-complexity helpers** - Defeats purpose of refactoring
6. **Not pushing frequently** - Risk of losing work
7. **Skipping documentation updates** - State becomes unclear for next session

### Project Principles Reminder
- **Quality over Speed**: "Time is not a constraint, quality and reliability is our goal"
- **Zero Regressions**: Every refactoring must maintain 8/8 test pass rate
- **Complete Refactoring**: No TODOs, no shortcuts - full production-ready code
- **Proven Patterns**: Extract Method pattern has 100% success rate across 27 functions
- **Evidence-Based Progress**: All claims verified with radon and test results
- **Family Focus**: Personal educational tool requiring absolute reliability

### Refactoring Pattern Quick Reference

**Extract Method Pattern** (Used in all 27 successful refactorings):
1. Read entire function
2. Identify 3-6 logical sections
3. Extract each section as helper with descriptive name
4. Keep main function as orchestrator (5-10 lines, just calls helpers)
5. Verify each helper is ≤10 complexity
6. Run tests, verify, commit

**Helper Naming Conventions**:
- `_validate_*()` - Precondition checks
- `_extract_*()`, `_get_*()` - Data retrieval
- `_build_*()`, `_create_*()` - Object construction
- `_process_*()`, `_analyze_*()` - Core operations
- `_should_*()` - Boolean decision helpers
- `_add_*()` - List/collection modification

**Target Complexity Goals**:
- Main function: A-level (1-5 complexity)
- Helpers: A-B level (1-10 complexity)
- Overall reduction: 70-90% (average 81% achieved so far)

---

## Document Version History

- **v1.0** (2025-10-14): Updated for Phase 2C Session 3 completion
  - Added PROJECT_STATUS.md as primary reference
  - Reorganized file hierarchy (Tier 1/2/3 reading priority)
  - Expanded validation commands with expected outputs
  - Added session checklists with time estimates
  - Included proven patterns and reference examples
  - Updated for TIER 3B as next milestone

- **v0.9** (Previous): Original template for Phase 2C start
- **v0.8**: Phase 2B completion template
- **Earlier versions**: Phase 2 and earlier templates

---

**Template Last Updated**: 2025-10-14 (Session 3 Complete)  
**Next Review Required**: Session 4 Start  
**Template Owner**: AI Language Tutor App Development  
**Status**: CURRENT ✅
