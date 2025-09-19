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
- Current foundation: FastAPI backend + FastHTML frontend + multi-LLM routing + Watson speech + SQLite/ChromaDB/DuckDB

**PLEASE PERFORM THESE STEPS IN ORDER**:

1. **Read Current Status**: Load and analyze `docs/TASK_TRACKER.json` to understand current phase, task, and progress

2. **Validate Previous Work**: Check if the previous session's work was completed and validated according to quality gates

3. **Identify Current Task**: Determine what specific task/subtask should be worked on today

4. **Check Blockers**: Verify no dependencies are blocking progress on current task

5. **Resume Execution**: Continue with the appropriate task based on current status

**CRITICAL REQUIREMENTS**:
- ❌ DO NOT advance to next task unless current task has passed ALL quality gates
- ❌ DO NOT skip validation steps or testing requirements  
- ❌ DO NOT proceed if any blockers exist
- ✅ DO document all changes, issues, and decisions
- ✅ DO update task tracker with progress
- ✅ DO maintain GitHub sync workflow

**OUTPUT EXPECTED**:
1. Current project status summary
2. Today's specific task and acceptance criteria
3. Validation requirements for task completion
4. Recommended next actions
5. Any blockers or issues requiring attention

**REFERENCE FILES**:
- Main plan: `PROJECT_IMPLEMENTATION_PLAN.md`
- Task tracking: `docs/TASK_TRACKER.json`
- Daily status: `docs/PROJECT_STATUS.md`
- Quality gates: `docs/QUALITY_GATES.md`

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

**ISSUES ENCOUNTERED**:
[Any problems, blockers, or concerns]

**VALIDATION COMPLETED**:
[What testing/validation was performed]

**NEXT SESSION PREPARATION**:
[What should be tackled next]

**REQUIRED ACTIONS**:
1. Update `docs/TASK_TRACKER.json` with today's progress
2. Update `docs/PROJECT_STATUS.md` with current state
3. Document any issues in execution log
4. Commit changes to GitHub if applicable
5. Prepare tomorrow's starting point

Please update all tracking files and provide tomorrow's starting context.

---

## Emergency Recovery Template

Use this if project state is unclear or corrupted:

---

**PROJECT RECOVERY - Status Assessment Required**

The project state appears unclear or potentially corrupted. Please help me assess and recover.

**RECOVERY STEPS**:
1. Analyze all project documentation files
2. Assess current codebase state
3. Identify last known good state
4. Determine any data loss or corruption
5. Provide recovery recommendations
6. Re-establish proper tracking

**CRITICAL QUESTION**: What is the current state of the project and how do we safely proceed?

---

## Quality Gate Validation Template

Use this before marking any task as complete:

---

**TASK COMPLETION VALIDATION REQUIRED**

Task: [Task ID and Name]

Please validate this task meets ALL completion criteria:

**ACCEPTANCE CRITERIA CHECKLIST**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [etc.]

**VALIDATION REQUIREMENTS**:
- [ ] Functionality tested and working
- [ ] Documentation updated
- [ ] Code committed to GitHub  
- [ ] No regressions in existing functionality
- [ ] All subtasks completed

**BLOCKING ISSUES**: [List any issues preventing completion]

**TESTING EVIDENCE**: [Describe testing performed and results]

If ALL criteria are met, please update task status to COMPLETED with validation notes. Otherwise, keep as IN_PROGRESS and list remaining work.

---

## Notes for Effective Daily Usage

### Best Practices
1. **Always start with the standardized resumption prompt**
2. **Never skip the status loading and validation steps**
3. **Be honest about completion status - partial work is OK**
4. **Document everything, especially when things don't work**
5. **Commit frequently to maintain progress history**

### Common Pitfalls to Avoid
1. **Starting work without checking current status**
2. **Advancing tasks without proper validation**
3. **Skipping documentation updates**
4. **Not testing changes before marking complete**
5. **Losing track of what was accomplished**

### Project Principles Reminder
- **Quality over Speed**: Better to do one task perfectly than many tasks poorly
- **Documentation is Critical**: Future you will thank present you
- **Testing is Non-Negotiable**: Every change must be validated
- **Incremental Progress**: Small, validated steps lead to big results
- **Family Focus**: Remember this is for educational family use