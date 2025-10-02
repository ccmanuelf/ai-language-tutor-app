# Task 4.2.4 Refactoring Plan: conversation_manager.py

**Status**: DEFERRED - Analysis Complete, Implementation Pending  
**Reason**: Task 4.2.5 is simpler and should be completed first  
**Date**: 2025-10-01  

---

## Current Metrics
- **Lines**: 907
- **Complexity Score**: 1,498
- **Nested Loops**: 90
- **Nested Conditionals**: 1,408
- **Target Reduction**: 65% needed (<600 lines, <500 complexity per module)

---

## Proposed 6-Module Architecture

### Module 1: `conversation_state.py` (~180 lines, ~250 complexity)
- State management and lifecycle operations
- `ConversationStateManager` class

### Module 2: `message_handler.py` (~200 lines, ~300 complexity)
- Message processing and context management
- Refactor `send_message` (149 lines) into 5 focused methods

### Module 3: `learning_analytics.py` (~150 lines, ~200 complexity)
- Learning insights and progress tracking
- `LearningAnalyzer` class

### Module 4: `prompt_generator.py` (~120 lines, ~150 complexity)
- System prompt generation
- `PromptGenerator` class with templates

### Module 5: `conversation_persistence.py` (~100 lines, ~100 complexity)
- Database operations (implement stub methods)
- `ConversationPersistence` class

### Module 6: `conversation_manager.py` (~150 lines, ~150 complexity)
- Orchestration facade (refactored)
- Delegates to specialized modules

---

## Critical Priority: Refactor `send_message`

**Current**: 149 lines, highest complexity, 3+ nesting levels

**Split into 5 methods**:
1. `_validate_conversation` (~25 lines)
2. `_process_user_message` (~30 lines)
3. `_get_ai_response` (~35 lines)
4. `_process_scenario_interaction` (~30 lines)
5. `_build_conversation_response` (~29 lines)

---

## Implementation Order

1. ✅ **COMPLETED**: Analysis and planning
2. **DEFERRED**: Extract `prompt_generator.py` (low risk)
3. **DEFERRED**: Extract `learning_analytics.py` (low risk)
4. **DEFERRED**: Refactor `send_message` method (high risk, critical)
5. **DEFERRED**: Extract `message_handler.py` (medium risk)
6. **DEFERRED**: Extract `conversation_state.py` (medium risk)
7. **DEFERRED**: Implement `conversation_persistence.py` (medium risk)
8. **DEFERRED**: Refactor `conversation_manager.py` to facade (final step)

---

## Why Deferred

1. **Task 4.2.5 is simpler**: File splitting without complex refactoring
2. **Proper sequencing**: Complete easier tasks first
3. **Complexity**: conversation_manager requires careful refactoring of critical path
4. **Time management**: Ensure all Task 4.2 subtasks get addressed

---

## Next Steps When Resuming

1. Start with low-risk extractions (prompts, analytics)
2. Add comprehensive tests before touching `send_message`
3. Use feature flags for gradual rollout
4. Keep parallel implementation during transition

---

**To Resume**: See comprehensive analysis in agent output above  
**Estimated Time**: 6-8 hours (when resumed)  
**Risk Level**: High (critical path refactoring)
