# Lessons Learned - Session 74

**Module**: `app/services/scenario_io.py`  
**Date**: 2025-12-02  
**Focus**: File I/O, Serialization, Mock Testing

---

## Key Lessons

### 1. Enum Value Verification - CRITICAL! 🔴

**Issue**: Used incorrect enum attribute names (e.g., `ConversationRole.TRAVELER`)  
**Error**: `AttributeError: type object 'ConversationRole' has no attribute 'TRAVELER'`

**Solution**: Always verify enum values before writing tests

**Verification Command**:
```bash
python -c "from app.services.scenario_models import ConversationRole; \
print([role.name + '=' + role.value for role in ConversationRole])"
```

**Output**:
```
['CUSTOMER=customer', 'SERVICE_PROVIDER=service_provider', 'FRIEND=friend', 
 'COLLEAGUE=colleague', 'STUDENT=student', 'TEACHER=teacher', 
 'TOURIST=tourist', 'LOCAL=local']
```

**Correct Usage**:
```python
# ✅ CORRECT
user_role=ConversationRole.TOURIST  # Not TRAVELER
ai_role=ConversationRole.LOCAL      # Not GUIDE
```

**Prevention**: Always check enum definitions in the source code before use.

---

### 2. Mock Call Arguments Structure

**Issue**: Tried accessing `call_args[1]['mode']` which resulted in `KeyError: 'mode'`

**Root Cause**: `open()` uses positional arguments, not keyword arguments

**Mock Call Structure**:
```python
mock_file.assert_called_once()
# call_args is a tuple: (args, kwargs)
# call_args[0] = tuple of positional arguments
# call_args[1] = dict of keyword arguments
```

**Wrong Approach**:
```python
# ❌ WRONG - assumes keyword argument
call_args = mock_file.call_args
assert call_args[1]['mode'] == 'w'  # KeyError!
```

**Correct Approach**:
```python
# ✅ CORRECT - access positional and keyword separately
call_args = mock_file.call_args[0]    # positional args
call_kwargs = mock_file.call_args[1]  # keyword args
assert 'scenarios.json' in str(call_args[0])
assert call_kwargs['encoding'] == 'utf-8'
```

**Key Learning**: Understand how the actual function is called before mocking it.

---

### 3. Constructor Signature Inspection

**Issue**: Missing required parameters `vocabulary_focus` and `cultural_context`  
**Error**: `TypeError: ConversationScenario.__init__() missing 2 required positional arguments`

**Solution**: Use `inspect.signature()` to check constructor requirements

**Inspection Command**:
```bash
python -c "from app.services.scenario_models import ConversationScenario; \
import inspect; \
print(inspect.signature(ConversationScenario.__init__))"
```

**Output**:
```python
(self, scenario_id: str, name: str, 
 category: ScenarioCategory, difficulty: ScenarioDifficulty, 
 description: str, user_role: ConversationRole, 
 ai_role: ConversationRole, setting: str, 
 duration_minutes: int, phases: List[ScenarioPhase], 
 vocabulary_focus: List[str],      # ← Required!
 cultural_context: Dict[str, Any], # ← Required!
 learning_goals: List[str] = None, 
 learning_outcomes: List[str] = None, 
 prerequisites: List[str] = None)
```

**Fixed Constructor Call**:
```python
scenario = ConversationScenario(
    scenario_id="test_001",
    name="Test",
    # ... other params ...
    phases=[phase],
    vocabulary_focus=[],           # ← Added
    cultural_context={}            # ← Added
)
```

**Prevention**: Always check constructor signatures before creating test objects.

---

### 4. Bulk Code Editing with Python Scripts

**Challenge**: Needed to add same parameters to 7 different ConversationScenario calls

**Manual Approach**: Would require 7 separate edits - error-prone and slow

**Automated Solution**: Python script with regex replacement
```python
import re

with open('tests/test_scenario_io.py', 'r') as f:
    content = f.read()

# Pattern to find ConversationScenario calls
pattern = r'(ConversationScenario\([^)]*phases=\[phase1?\],)\s*\)'

def replacement(match):
    return match.group(1) + '\n            vocabulary_focus=[],\n            cultural_context={}\n        )'

content = re.sub(pattern, replacement, content)

with open('tests/test_scenario_io.py', 'w') as f:
    f.write(content)
```

**Benefits**:
- ✅ Consistent changes across all occurrences
- ✅ No copy-paste errors
- ✅ Faster than manual editing
- ✅ Repeatable and verifiable

**Key Learning**: For repetitive code changes, write a script instead of manual edits.

---

### 5. Test Actual Behavior, Not Assumptions

**Issue**: Test assumed `cultural_context` default would be `None`  
**Actual**: Constructor requires it, so test used `{}`, which is what gets saved

**Wrong Test**:
```python
# ❌ Assumes None for missing cultural_context
assert scenario_dict["cultural_context"] is None
```

**Correct Test**:
```python
# ✅ Tests actual behavior (empty dict provided)
assert scenario_dict["cultural_context"] == {}
```

**Process**:
1. Run test and observe actual behavior
2. Verify behavior is correct
3. Update test to match actual behavior
4. Don't assume defaults - verify them!

**Key Learning**: Tests should validate actual behavior, not assumed behavior.

---

### 6. Small Module, Big Impact

**Observation**: Even small modules (47 statements) can have strategic importance

**scenario_io.py Characteristics**:
- **Size**: Small (47 statements)
- **Complexity**: Medium (serialization logic)
- **Impact**: HIGH (enables scenario persistence)
- **Dependencies**: Critical for scenario management

**Value**: 
- Enables saving custom scenarios
- Allows scenario portability
- Supports backup/restore
- Foundation for scenario sharing

**Key Learning**: Module size ≠ module importance. Small modules can be critical.

---

### 7. Datetime Serialization Patterns

**Complex Logic in Production Code**:
```python
"created_at": getattr(
    scenario, "created_at", datetime.now()
).isoformat()
if hasattr(scenario, "created_at") and scenario.created_at
else datetime.now().isoformat()
```

**What This Does**:
1. Check if attribute exists AND is truthy
2. If yes: use it and convert to ISO format
3. If no: generate current datetime and convert to ISO format

**Test Requirements**:
- ✅ Test with existing, truthy datetime
- ✅ Test with None datetime
- ✅ Test with missing attribute

**Key Learning**: Complex conditional logic requires multiple test cases.

---

### 8. Mock File I/O Best Practices

**Pattern for Testing File Operations**:
```python
with patch('pathlib.Path.mkdir') as mock_mkdir, \
     patch('builtins.open', mock_open()) as mock_file, \
     patch('json.dump') as mock_dump:
    
    await ScenarioIO.save_scenarios_to_file(scenarios)
    
    # Verify directory creation
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    # Verify file opening
    mock_file.assert_called_once()
    assert call_kwargs['encoding'] == 'utf-8'
    
    # Verify JSON dumping
    dumped_data = mock_dump.call_args[0][0]
    # ... assert on dumped_data structure
```

**Benefits**:
- ✅ No actual file I/O (fast tests)
- ✅ No cleanup needed
- ✅ Deterministic behavior
- ✅ Can test error conditions easily

**Key Learning**: Mock all file I/O operations for unit tests.

---

### 9. Error Path Testing Importance

**Both Methods Have Error Handlers**:
```python
try:
    # ... operation ...
except Exception as e:
    logger.error(f"Error saving scenarios to file: {str(e)}")
```

**Test Pattern**:
```python
@pytest.mark.asyncio
async def test_save_scenarios_handles_exception(self):
    """Test that exceptions during save are caught and logged"""
    scenarios = {}
    
    with patch('pathlib.Path.mkdir', side_effect=Exception("Disk error")), \
         patch('app.services.scenario_io.logger') as mock_logger:
        
        # Should not raise, just log
        await ScenarioIO.save_scenarios_to_file(scenarios)
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Disk error" in mock_logger.error.call_args[0][0]
```

**Coverage Impact**:
- Without error tests: Missing exception branches
- With error tests: TRUE 100% branch coverage

**Key Learning**: Always test exception handlers, even if they just log.

---

### 10. Serialization/Deserialization Symmetry

**Best Practice**: Test round-trip conversion

**Pattern**:
```python
# Test 1: Serialization
scenario_object → save → JSON data
assert JSON structure is correct

# Test 2: Deserialization  
JSON data → load → scenario_object
assert object attributes are correct

# Implicit Round-Trip Verification:
If both pass, round-trip works!
```

**Our Coverage**:
- ✅ Save tests verify correct JSON structure
- ✅ Load tests verify correct object reconstruction
- ✅ Together they ensure round-trip fidelity

**Key Learning**: Comprehensive serialization testing requires both directions.

---

## Patterns to Reuse

### Pattern 1: Mock File I/O
```python
with patch('pathlib.Path.exists', return_value=True), \
     patch('builtins.open', mock_open(read_data=json.dumps(data))):
    result = await load_function()
```

### Pattern 2: Enum Handling
```python
# In production: enum.value
category = scenario.category.value  # "travel"

# In tests: Enum(string)
category = ScenarioCategory("travel")  # ScenarioCategory.TRAVEL
```

### Pattern 3: Logger Verification
```python
with patch('module.logger') as mock_logger:
    # ... operation ...
    mock_logger.error.assert_called_once()
    assert "expected message" in mock_logger.error.call_args[0][0]
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Assuming Enum Names
```python
# ❌ DON'T assume enum names
user_role = ConversationRole.TRAVELER  # Might not exist!

# ✅ DO verify enum names first
# Check source code or use introspection
```

### Anti-Pattern 2: Assuming Mock Call Structure
```python
# ❌ DON'T assume all args are keyword args
assert call_args[1]['mode'] == 'w'  # Might be KeyError

# ✅ DO check actual function signature
call_kwargs = mock_file.call_args[1]
assert call_kwargs.get('encoding') == 'utf-8'
```

### Anti-Pattern 3: Skipping Error Paths
```python
# ❌ DON'T skip exception handlers
# Missing: Test for exception case

# ✅ DO test all exception handlers
with patch('func', side_effect=Exception("error")):
    # ... test error handling ...
```

---

## Tools & Commands

### Useful Introspection Commands
```bash
# Check enum values
python -c "from module import Enum; print(list(Enum))"

# Check class signature
python -c "from module import Class; import inspect; print(inspect.signature(Class.__init__))"

# Check class attributes
python -c "from module import Class; print(dir(Class))"
```

### Coverage Commands
```bash
# Module-specific coverage
pytest tests/test_module.py --cov=app.services.module --cov-report=term-missing -v

# Full test suite
pytest tests/ -q --tb=no

# Coverage with branch details
pytest tests/ --cov=app --cov-branch --cov-report=term-missing
```

---

## Success Factors

### What Went Well ✅
1. **Systematic Approach**: Method-by-method test design
2. **Quick Iteration**: Fixed issues rapidly
3. **Tool Usage**: Used introspection to verify assumptions
4. **Automation**: Script for bulk edits saved time
5. **Documentation**: Clear test docstrings

### What Could Improve 🔄
1. **Upfront Verification**: Check enums/signatures before writing tests
2. **Mock Understanding**: Study actual function calls before mocking
3. **Test Planning**: Map out all branches before implementing

---

## Applicability to Future Sessions

### These Lessons Apply To:
- ✅ Any module with file I/O operations
- ✅ Modules with serialization/deserialization
- ✅ Classes using enums extensively
- ✅ Static method classes
- ✅ Error-handled operations

### Preparation Checklist for Similar Modules:
- [ ] Verify enum values used in module
- [ ] Check constructor signatures for test objects
- [ ] Understand file I/O patterns
- [ ] Identify all exception handlers
- [ ] Plan both success and error path tests

---

## Strategic Insights

### Module Selection Validation
**scenario_io.py** was an excellent choice because:
1. ✅ Small scope (47 statements) - manageable
2. ✅ Clear functionality - well-defined I/O
3. ✅ Low coverage (25%) - high impact
4. ✅ Strategic importance - enables persistence

**Lesson**: Small, focused modules are great targets for quick wins.

### Test Organization Success
4 test classes provided clear structure:
- Separate success/error cases
- Separate save/load operations
- Easy to navigate and maintain

**Lesson**: Organize tests by operation type and outcome.

---

**Session 74 Lessons**: Successfully applied and documented! 📚

**Key Takeaway**: Verify assumptions, test actual behavior, automate repetitive tasks! 🎯
