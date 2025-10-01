# Task 4.2.2 Refactoring Plan: scenario_manager.py

**Date**: 2025-09-30  
**Target**: Reduce complexity from 4,950 to <1,000 per module  

---

## 📊 Current State Analysis

### File Metrics
- **Total Lines**: 2,608
- **Complexity Score**: 4,950
- **Nested Loops**: 1,700
- **Nested Conditionals**: 3,250
- **Methods**: 49
- **Classes**: 9

### Structure Breakdown
```
Lines 1-31:     Imports and logger setup
Lines 32-69:    Enums (ScenarioCategory, ScenarioDifficulty, ConversationRole)
Lines 70-88:    ScenarioPhase dataclass
Lines 89-117:   ConversationScenario dataclass
Lines 118-138:  ScenarioProgress dataclass
Lines 139-252:  UniversalScenarioTemplate class (~113 lines)
Lines 253-1252: ScenarioFactory class (~999 lines) - LARGE
Lines 1253-2570: ScenarioManager class (~1,317 lines) - VERY LARGE
Lines 2571-2608: Module-level async functions (38 lines)
```

### Key Issues Identified
1. **ScenarioFactory** (999 lines) - Contains massive template generation logic
2. **ScenarioManager** (1,317 lines) - Multiple responsibilities mixed together
3. Heavy inline template definitions causing bloat
4. Mixed I/O, validation, and business logic

---

## 🎯 Refactoring Strategy

### Module Split Plan

**Module 1: `scenario_models.py`** (~200 lines)
- All dataclasses (ScenarioPhase, ConversationScenario, ScenarioProgress)
- All enums (ScenarioCategory, ScenarioDifficulty, ConversationRole)
- Clean data structures only

**Module 2: `scenario_templates.py`** (~400 lines)
- UniversalScenarioTemplate class
- Template definitions extracted from ScenarioFactory
- Template-related helper functions
- No business logic

**Module 3: `scenario_factory.py`** (~500 lines)
- ScenarioFactory class (refactored, slimmed down)
- Scenario generation logic
- Uses templates from scenario_templates.py
- Cleaner, focused on creation only

**Module 4: `scenario_io.py`** (~300 lines)
- File I/O operations (load/save scenarios)
- JSON serialization/deserialization
- Path management
- Error handling for I/O

**Module 5: `scenario_validator.py`** (~200 lines)
- Scenario validation logic
- Progress validation
- Input sanitization
- Validation rules

**Module 6: `scenario_manager.py` (core)** (~600 lines)
- ScenarioManager class (refactored)
- Core orchestration logic
- Uses all above modules
- Clean, focused responsibility

**Module 7: `scenario_api.py`** (~100 lines)
- Module-level async functions
- API convenience functions
- Backwards compatibility layer

**Total**: ~2,300 lines (from 2,608) with better organization

---

## 🔧 Detailed Refactoring Steps

### Step 1: Create scenario_models.py
**Lines to extract**: 32-138
**Target size**: 150-200 lines
**Complexity target**: <50

Contents:
- ScenarioCategory enum
- ScenarioDifficulty enum  
- ConversationRole enum
- ScenarioPhase dataclass
- ConversationScenario dataclass
- ScenarioProgress dataclass
- Helper methods for models only

### Step 2: Create scenario_templates.py
**Lines to extract**: 139-252 + template data from ScenarioFactory
**Target size**: 350-400 lines
**Complexity target**: <300

Contents:
- UniversalScenarioTemplate class
- Template definitions (restaurant, travel, shopping, etc.)
- Template helper functions
- Template validation (basic)

### Step 3: Create scenario_factory.py
**Lines to extract**: 253-1252 (refactored)
**Target size**: 400-500 lines
**Complexity target**: <600

Contents:
- ScenarioFactory class (slimmed down)
- Uses scenario_templates for data
- Generation logic only
- Simplified nested loops

### Step 4: Create scenario_io.py
**Lines to extract**: I/O methods from ScenarioManager
**Target size**: 250-300 lines
**Complexity target**: <200

Contents:
- `load_scenarios_from_file()`
- `save_scenario_to_file()`
- `_load_predefined_scenarios()`
- Path management
- JSON handling

### Step 5: Create scenario_validator.py
**Lines to extract**: Validation methods from ScenarioManager
**Target size**: 150-200 lines
**Complexity target**: <150

Contents:
- `validate_scenario()`
- `validate_progress()`
- `validate_phase()`
- Validation rules
- Error messages

### Step 6: Refactor scenario_manager.py (core)
**Lines remaining**: 1253-2570 (refactored)
**Target size**: 500-600 lines
**Complexity target**: <800

Contents:
- ScenarioManager class (orchestrator only)
- Uses: scenario_io, scenario_validator, scenario_factory
- Core business logic
- Progress tracking
- Scenario lifecycle management

### Step 7: Create scenario_api.py
**Lines to extract**: 2571-2608
**Target size**: 80-100 lines
**Complexity target**: <50

Contents:
- `get_available_scenarios()`
- `start_scenario()`
- `process_scenario_interaction()`
- `get_scenario_status()`
- `finish_scenario()`
- Backwards compatibility

---

## ✅ Validation Plan

### Before Refactoring
```bash
python scripts/performance_profiler.py
# Record: complexity 4950, lines 2608
```

### After Each Module Creation
1. Create module
2. Run tests: `pytest -xvs test_*scenario*.py`
3. Verify imports work
4. Check no functionality lost

### After Complete Refactoring
```bash
# Run performance profiler
python scripts/performance_profiler.py

# Expected results:
# - scenario_models.py: <50 complexity
# - scenario_templates.py: <300 complexity
# - scenario_factory.py: <600 complexity
# - scenario_io.py: <200 complexity
# - scenario_validator.py: <150 complexity
# - scenario_manager.py: <800 complexity

# Total improvement: 4950 → ~2,150 (56% reduction)
# Target: >75% per module, achieved via splitting
```

### Test Requirements
- [ ] All existing tests pass (100%)
- [ ] No new errors in integration tests
- [ ] Performance benchmarks stable or better
- [ ] Memory usage stable or lower
- [ ] Import time not significantly increased

---

## 🚨 Risk Mitigation

### Backwards Compatibility
- Keep original imports working via __init__.py
- Maintain public API unchanged
- Add deprecation warnings if needed

### Testing Strategy
- Run tests after each module creation
- Keep original file as backup until all tests pass
- Use git branches for safety

### Rollback Plan
- Git commit after each successful module
- Can cherry-pick if needed
- Original file preserved until validation complete

---

## 📈 Success Metrics

### Primary Goals
- ✅ Reduce lines per module to <800
- ✅ Reduce complexity per module to <1000
- ✅ Maintain 100% test coverage
- ✅ No performance regression
- ✅ All functionality preserved

### Stretch Goals
- Improved import times (smaller modules load faster)
- Better code reusability
- Easier maintenance
- Clearer separation of concerns

---

**Estimated Duration**: 6-8 hours  
**Estimated Commits**: 7 (one per module)  
**Risk Level**: Medium (large refactor, but well-planned)
