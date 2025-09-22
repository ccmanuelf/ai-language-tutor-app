# Daily Project Resumption Prompt Template

## Standardized Daily Startup Prompt

Use this exact prompt to resume work each day:

---

**DAILY PROJECT RESUMPTION - AI Language Tutor App Implementation**

Hello! I'm resuming work on the AI Language Tutor App comprehensive implementation project. Please help me continue from where we left off yesterday.

**PROJECT CONTEXT**:
- Building comprehensive language learning platform combining YouLearn AI, Pingo AI, Fluently AI, and Airlearn features
- Personal, non-commercial, educational tool for family use
- Must remain flexible, configurable, and adaptable
- Current foundation: FastAPI backend + FastHTML frontend + multi-LLM routing + Mistral STT + Piper TTS + SQLite/ChromaDB/DuckDB

**🚨 MANDATORY FIRST STEP - ENVIRONMENT VALIDATION**:
Before proceeding with ANY work, you MUST run the environment validation:

```bash
cd ai-language-tutor-app
source ai-tutor-env/bin/activate
python scripts/validate_environment.py
```

**If environment validation FAILS, STOP and fix issues before continuing.**

**PLEASE PERFORM THESE STEPS IN ORDER**:

1. **Environment Validation** ✅ MANDATORY
   - Run `python scripts/validate_environment.py`
   - Verify 5/5 checks pass (Python, dependencies, directory, models, services)
   - If any failures, fix before proceeding

2. **Read Current Status**: Load and analyze `docs/TASK_TRACKER.json` to understand current phase, task, and progress

3. **Check Previous Session Handover**: Review `docs/SESSION_HANDOVER.md` if it exists from the last session

4. **Validate Previous Work**: 
   - Check if the previous session's work was completed and validated according to quality gates
   - Run `python scripts/quality_gates.py <last_task_id>` if needed
   - Verify validation artifacts exist in `validation_artifacts/`

5. **Identify Current Task**: Determine what specific task/subtask should be worked on today

6. **Check Blockers**: Verify no dependencies are blocking progress on current task

7. **Resume Execution**: Continue with the appropriate task based on current status

**CRITICAL REQUIREMENTS**:
- 🚨 **NEVER** skip environment validation step
- ❌ DO NOT advance to next task unless current task has passed ALL quality gates
- ❌ DO NOT skip validation steps or testing requirements  
- ❌ DO NOT proceed if any blockers exist
- ❌ DO NOT mark tasks complete without running `python scripts/quality_gates.py <task_id>`
- ✅ DO document all changes, issues, and decisions
- ✅ DO update task tracker with progress
- ✅ DO maintain GitHub sync workflow
- ✅ DO generate validation artifacts for any completed work

**OUTPUT EXPECTED**:
1. Environment validation results (5/5 checks status)
2. Current project status summary
3. Today's specific task and acceptance criteria
4. Validation requirements for task completion
5. Previous session artifacts status
6. Recommended next actions
7. Any blockers or issues requiring attention

**REFERENCE FILES**:
- **Environment Check**: `scripts/validate_environment.py` (MANDATORY)
- **Quality Gates**: `scripts/quality_gates.py` (before task completion)
- **Main plan**: `PROJECT_IMPLEMENTATION_PLAN.md`
- **Task tracking**: `docs/TASK_TRACKER.json`
- **Prevention guide**: `docs/VALIDATION_PREVENTION_GUIDE.md`
- **Validation standards**: `docs/VALIDATION_STANDARDS.md`
- **Session handover**: `docs/SESSION_HANDOVER.md` (if exists)

**VALIDATION EVIDENCE LOCATIONS**:
- **Environment results**: `validation_results/last_environment_validation.json`
- **Quality gates results**: `validation_results/quality_gates_*.json`
- **Generated artifacts**: `validation_artifacts/[task_id]/`

Ready to continue! Please load the current status and provide today's work plan.

---

## Daily Completion Template

Use this template at end of each work session:

---

**DAILY SESSION COMPLETION - Status Update Required**

Please help me properly close today's work session and prepare for tomorrow.

**TODAY'S WORK COMPLETED**:
[Summarize what was accomplished]

**CURRENT TASK STATUS**:
[Current task completion percentage and status]

**VALIDATION COMPLETED**:
[What testing/validation was performed - include quality gates results]

**ISSUES ENCOUNTERED**:
[Any problems, blockers, or concerns]

**ARTIFACTS GENERATED**:
[List files created in validation_artifacts/]

**NEXT SESSION PREPARATION**:
[What should be tackled next]

**🚨 MANDATORY SESSION CLOSURE ACTIONS**:
1. **Run Quality Gates** (if any task completed): `python scripts/quality_gates.py <task_id>`
2. **Update Task Tracker**: Update `docs/TASK_TRACKER.json` with today's progress
3. **Create Session Handover**: Fill out `docs/SESSION_HANDOVER.md` for next session
4. **Commit Validation Artifacts**: Ensure all evidence files are committed to GitHub
5. **Environment Status**: Save current environment validation state

**REQUIRED FILE UPDATES**:
- [ ] `docs/TASK_TRACKER.json` updated with progress
- [ ] `docs/SESSION_HANDOVER.md` created/updated for next session
- [ ] `validation_artifacts/[task_id]/` populated with evidence
- [ ] GitHub repository synchronized with all changes

Please update all tracking files and provide tomorrow's starting context.

---

## Emergency Recovery Template

Use this if project state is unclear or corrupted:

---

**PROJECT RECOVERY - Status Assessment Required**

The project state appears unclear or potentially corrupted. Please help me assess and recover.

**🚨 RECOVERY STEPS**:
1. **Environment Check**: Run `python scripts/validate_environment.py`
2. **Analyze Validation State**: Check `validation_results/` and `validation_artifacts/`
3. **Review Task Tracker**: Assess `docs/TASK_TRACKER.json` for last known state
4. **Check Git History**: Review recent commits for last working state
5. **Validate Last Completed Task**: Run quality gates on last supposedly completed task
6. **Assess Current Codebase**: Check if application still functions
7. **Recovery Recommendations**: Provide safe path forward

**CRITICAL QUESTION**: What is the current state of the project and how do we safely proceed?

---

## Quality Gate Validation Template

Use this before marking any task as complete:

---

**TASK COMPLETION VALIDATION REQUIRED**

Task: [Task ID and Name]

**🚨 MANDATORY QUALITY GATES CHECK**:
```bash
python scripts/quality_gates.py [task_id]
```

Please validate this task meets ALL completion criteria:

**ACCEPTANCE CRITERIA CHECKLIST**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [etc.]

**VALIDATION REQUIREMENTS**:
- [ ] Environment validation passes (5/5 checks)
- [ ] Quality gates pass (4/4 gates)
- [ ] Validation artifacts generated (>3 files >1KB)
- [ ] Functionality tested with actual output files
- [ ] Documentation updated
- [ ] Code committed to GitHub  
- [ ] No regressions in existing functionality

**EVIDENCE REQUIREMENTS**:
- [ ] Real output files generated (not just "no errors")
- [ ] Quantitative measurements documented
- [ ] Performance benchmarks recorded
- [ ] Error handling tested

**BLOCKING ISSUES**: [List any issues preventing completion]

**TESTING EVIDENCE**: [Describe testing performed and results with file locations]

**If ALL criteria are met and quality gates pass, update task status to COMPLETED with validation notes. Otherwise, keep as IN_PROGRESS and list remaining work.**

---

## Notes for Effective Daily Usage

### Best Practices
1. **Always start with environment validation** - this prevents 90% of validation issues
2. **Never skip quality gates before task completion** - they catch validation methodology failures
3. **Generate actual evidence files** - validation requires tangible proof
4. **Document everything** - especially when things don't work as expected
5. **Commit validation artifacts frequently** - maintain progress history
6. **Use session handover** - preserve context between sessions

### Common Pitfalls to Avoid
1. **Starting work without environment validation** - leads to inconsistent results
2. **Marking tasks complete without quality gates** - creates validation methodology failures
3. **Skipping evidence generation** - makes validation impossible to verify
4. **Not testing with realistic data** - toy examples hide real issues
5. **Losing track of artifacts** - breaks reproducibility

### Project Principles Reminder
- **Quality over Speed**: Better to do one task perfectly with full validation than many tasks poorly
- **Evidence-Based Validation**: Every test must produce measurable, tangible results
- **Environment Consistency**: Same environment, same results - always
- **Incremental Progress**: Small, fully validated steps lead to reliable big results
- **Family Focus**: Remember this is for educational family use - reliability matters

### Prevention Framework Integration
- **Environment Scripts**: `scripts/validate_environment.py` and `scripts/quality_gates.py`
- **Documentation**: `docs/VALIDATION_PREVENTION_GUIDE.md` for quick reference
- **Evidence Storage**: `validation_artifacts/` for organized proof storage
- **Results Tracking**: `validation_results/` for automated validation history