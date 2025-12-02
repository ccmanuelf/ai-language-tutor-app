# Lessons Learned - Session 72

**Module**: `app/services/scenario_factory.py`  
**Date**: 2025-12-02  
**Achievement**: TRUE 100% Coverage ✅

---

## 🎯 Top 5 Critical Lessons

### 1. **Test Data Must Be Isolated from Production Data**

**Problem**: Initial tests failed because test template IDs conflicted with default templates loaded from the actual codebase.

**Example of Failure**:
```python
# Test creates template with ID "template_0"
template_data = {"template_id": "template_0", ...}

# But factory also loads 32 default templates including some that might conflict
factory = ScenarioFactory()  
assert "template_0" in factory.universal_templates  # ❌ May fail or pass unexpectedly
```

**Solution**: Use unique, recognizable prefixes for all test data:
```python
# ✅ CORRECT - Unique test identifier
template_data = {"template_id": "json_template_0", ...}
factory = ScenarioFactory()
assert "json_template_0" in factory.universal_templates  # ✅ Always works
```

**Takeaway**: **Always namespace test data to prevent conflicts with production code.**

---

### 2. **Dataclass Optional Fields Still Need Values in Raw Data**

**Problem**: JSON test data was missing optional fields, causing `KeyError` even though the dataclass had defaults.

**Why It Happens**: The `_create_universal_template` method accesses dict fields directly:
```python
def _create_universal_template(self, data: Dict[str, Any]):
    return UniversalScenarioTemplate(
        template_id=data["template_id"],  # Required
        # ...
        scenario_variations=data["scenario_variations"],  # KeyError if missing!
```

Even though `UniversalScenarioTemplate` has `__post_init__` with defaults, we must provide the key in the input dict.

**Solution**: Include all fields in test JSON data:
```python
template_data = {
    # Required fields
    "template_id": "test_id",
    "name": "Test",
    # ... other required fields ...
    
    # Optional fields - MUST INCLUDE even if empty
    "scenario_variations": [],      # Can't omit!
    "difficulty_modifiers": {},     # Can't omit!
    "success_metrics": []           # Can't omit!
}
```

**Takeaway**: **When creating objects from dicts, provide all keys even for optional fields with defaults.**

---

### 3. **Mocking `builtins.__import__` for Fine-Grained Import Control**

**Challenge**: Need to test ImportError fallback when extended templates can't import, but only that specific import should fail.

**Failed Approaches**:
1. ❌ `sys.modules['module'] = None` - Doesn't trigger ImportError during `import`
2. ❌ `patch('module.Class')` - Module already imported, too late
3. ❌ `patch.dict('sys.modules')` - Doesn't control the import statement

**Successful Approach**: Mock `builtins.__import__` with selective behavior:
```python
import builtins

real_import = builtins.__import__

def custom_import(name, *args, **kwargs):
    # Fail only for specific module
    if 'scenario_templates_extended' in name:
        raise ImportError("Cannot import extended templates")
    # Allow all other imports
    return real_import(name, *args, **kwargs)

with patch('builtins.__import__', side_effect=custom_import):
    factory = ScenarioFactory()  # ImportError triggered!
```

**Key Points**:
- Save original `__import__` function
- Selectively raise errors based on module name
- Call original for all other imports
- Restore after test (patch context manager handles this)

**Takeaway**: **For testing import failures, mock `builtins.__import__` with conditional logic.**

---

### 4. **Temporary Paths + `__file__` Patching for Path-Dependent Code**

**Challenge**: Code checks if `Path(__file__).parent.parent / "config" / "scenarios"` exists. Hard to test without modifying actual file system.

**Solution**: Combine `tmp_path` fixture with `__file__` patching:
```python
def test_missing_directory(tmp_path):
    # Create fake module location
    fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
    fake_module_path.parent.mkdir(parents=True)
    
    # Patch __file__ to point to fake location
    with patch('app.services.scenario_factory.__file__', str(fake_module_path)):
        factory = ScenarioFactory()
        # Now code looks for scenarios at tmp_path/app/config/scenarios
        # Which doesn't exist → triggers path-not-found branch
```

**Why This Works**:
1. `tmp_path` is a pytest fixture providing isolated temp directory
2. Create minimal directory structure needed
3. Patch `__file__` to point to fake module file
4. Code now searches for scenarios relative to fake location
5. Scenarios directory doesn't exist → triggers desired branch

**Takeaway**: **Use tmp_path + `__file__` patching to test path-dependent code without touching real file system.**

---

### 5. **Distinguish Between Items Processed vs. Items Stored**

**Problem**: Confusion about whether to expect 32 or 34 templates in tests.

**Reality**:
- **34 templates are loaded** (5 Tier1 + 2 Tier2 + 27 extended)
- **2 templates have duplicate IDs** (`daily_routine`, `basic_conversations`)
- **32 unique templates are stored** (duplicates overwrite earlier ones)
- **34 log messages are created** (one per template processed)

**Testing Implications**:
```python
# Logger sees all 34 templates
template_logs = [r for r in caplog.records if "Created template:" in r.message]
assert len(template_logs) == 34  # ✅ Correct

# Dictionary stores 32 unique
assert len(factory.universal_templates) == 32  # ✅ Correct
```

**General Principle**:
- **Logs/events**: Count all operations performed
- **Storage structures**: Count unique keys/items stored
- These numbers may differ due to deduplication, filtering, or overwrites

**Takeaway**: **Differentiate between processing metrics (all items) and storage metrics (unique items).**

---

## 🔧 Technical Techniques

### Technique 1: Creating Realistic Test JSON Files

**Pattern**:
```python
def test_with_json_file(tmp_path):
    # 1. Create directory structure
    scenarios_dir = tmp_path / "app" / "config" / "scenarios"
    scenarios_dir.mkdir(parents=True)
    
    # 2. Create JSON content
    template_data = {
        "template_id": "test_template",
        # ... all required fields ...
    }
    
    # 3. Write to file
    json_file = scenarios_dir / "test.json"
    json_file.write_text(json.dumps(template_data))
    
    # 4. Point code to tmp location
    fake_module_path = tmp_path / "app" / "services" / "scenario_factory.py"
    fake_module_path.parent.mkdir(parents=True)
    
    with patch('app.services.scenario_factory.__file__', str(fake_module_path)):
        # Code will find and load the JSON file
        factory = ScenarioFactory()
```

### Technique 2: Testing Logger Output with caplog

**Pattern**:
```python
def test_logging(caplog):
    # Set log level and specify logger name
    with caplog.at_level(logging.WARNING, logger='app.services.scenario_factory'):
        # Perform action
        factory = ScenarioFactory()
        
        # Check log messages
        assert any("specific message" in record.message for record in caplog.records)
        
        # Or filter by level
        warnings = [r for r in caplog.records if r.levelname == 'WARNING']
        assert len(warnings) == 1
```

**Key Points**:
- Specify exact logger name (not root logger)
- Set appropriate log level
- Filter by `levelname` or `message` content
- Use `any()` for existence checks

### Technique 3: Module Restoration in Tests

**Pattern**:
```python
def test_with_module_manipulation():
    import sys
    
    # Save current state
    extended_mod = sys.modules.pop('app.services.scenario_templates_extended', None)
    
    try:
        # Test code that modifies sys.modules
        # ...
    finally:
        # Always restore original state
        if extended_mod is not None:
            sys.modules['app.services.scenario_templates_extended'] = extended_mod
```

**Why Important**:
- Tests should not leave side effects
- Other tests may depend on module state
- Prevents test pollution

---

## 📊 Testing Patterns Applied

### Pattern 1: Method Coverage Through Systematic Enumeration

For each public method, test:
1. Happy path (normal inputs)
2. Edge cases (None, empty, boundary values)
3. Error paths (exceptions, invalid inputs)
4. Return type/structure verification

**Example**:
```python
# get_template_by_id coverage
test_valid_id_returns_template()      # Happy path
test_invalid_id_returns_none()        # Edge case
test_exact_template_returned()        # Verification
```

### Pattern 2: Branch Coverage Through Conditional Enumeration

For each `if` statement, create tests for:
1. Condition true
2. Condition false
3. All sub-branches

**Example**:
```python
# if tier is not None:
test_tier_1_filter()          # True, tier=1
test_tier_2_filter()          # True, tier=2
test_no_tier_returns_all()    # False, tier=None
```

### Pattern 3: Exception Coverage Through Controlled Failures

Create specific conditions that trigger exceptions:
- Invalid JSON: `json_file.write_text("{invalid")`
- Import errors: Mock `__import__` to raise ImportError
- Missing files: Don't create expected files

**Example**:
```python
def test_invalid_json_logs_error(caplog):
    json_file.write_text("{not valid json")
    
    with caplog.at_level(logging.ERROR):
        factory = ScenarioFactory()
        assert any("Failed to load template" in r.message for r in caplog.records)
```

---

## 🎓 Generalizable Principles

### Principle 1: **Test Isolation Is Paramount**

Every test should:
- Create its own data (don't share with other tests)
- Use unique identifiers (avoid conflicts)
- Clean up after itself (or use fixtures that do)
- Not depend on execution order

### Principle 2: **Mock at the Right Level**

Choose mocking level based on what you're testing:
- **File operations**: Mock at `Path` or file system level
- **Imports**: Mock at `__import__` level
- **External services**: Mock at API client level
- **Time**: Mock at `datetime` level

**Rule**: Mock the closest boundary to what you're testing.

### Principle 3: **Verify Both Behavior and Side Effects**

Tests should check:
- **Return values**: What the function returns
- **State changes**: How objects/data were modified
- **Side effects**: Logging, file creation, network calls
- **Error handling**: Exceptions raised/caught

**Example**:
```python
def test_comprehensive():
    factory = ScenarioFactory()
    
    # Behavior: method works correctly
    template = factory.get_template_by_id("test_id")
    assert template is not None
    
    # State: dictionary contains template
    assert "test_id" in factory.universal_templates
    
    # Side effect: logging occurred
    assert "Loaded template" in caplog_messages
```

### Principle 4: **Documentation in Tests Is Self-Documenting**

Well-organized tests serve as:
- Usage examples (how to call methods)
- Behavior specification (what to expect)
- Edge case catalog (what can go wrong)
- Regression prevention (captures current behavior)

**Make tests readable**:
- Descriptive test names
- Clear arrange-act-assert structure
- Comments for non-obvious setup
- Grouped by functionality

---

## ⚠️ Pitfalls to Avoid

### Pitfall 1: Assuming Dict Access Works Like Dataclass Access

❌ **Wrong Assumption**:
```python
# Dataclass with defaults
@dataclass
class Template:
    name: str
    optional: List = None
    
    def __post_init__(self):
        if self.optional is None:
            self.optional = []

# This works - uses __post_init__
t = Template(name="test")  # ✅ optional gets set to []

# But this doesn't trigger __post_init__
data = {"name": "test"}  # Missing "optional" key
t = Template(**data)     # ❌ KeyError!
```

**Lesson**: `__post_init__` doesn't help with missing dict keys.

### Pitfall 2: Not Removing Test Data from sys.modules

❌ **Problem**:
```python
def test_imports():
    # Modify sys.modules
    sys.modules['fake_module'] = Mock()
    # ... test code ...
    # Forgot to clean up!
```

This pollutes subsequent tests. Always use try/finally or fixtures.

### Pitfall 3: Mocking Too Early or Too Late

❌ **Too Late**:
```python
from module import Thing  # Already imported!

def test():
    with patch('module.Thing'):  # ❌ Too late, already imported
        # ...
```

✅ **Correct**:
```python
def test():
    with patch('module.Thing'):  # ✅ Before it's used
        from module import use_thing
        use_thing()
```

### Pitfall 4: Not Accounting for Data Deduplication

❌ **Wrong Expectation**:
```python
# Code adds 34 items to dict, but 2 have duplicate keys
factory.add_all_templates(templates)  # Adds 34, stores 32

assert len(factory.templates) == 34  # ❌ Fails! Only 32 stored
```

✅ **Correct**:
```python
# Understand that dict keys must be unique
assert len(factory.templates) == 32  # ✅ Accounts for 2 duplicates
```

---

## 📈 Metrics and Patterns

### Testing Efficiency Metrics (Session 72)

- **Lines of test code per line of production code**: 11.3:1
- **Tests per method**: ~4.4 tests/method (35 tests / 8 methods)
- **Coverage increase per test**: ~1.2% per test (42.67% / 35 tests)
- **Tests per test class**: 3.5 tests/class average
- **Time to TRUE 100%**: ~2 hours

### Common Test Patterns Distribution

| Pattern | Count | Percentage |
|---------|-------|------------|
| Happy path tests | 12 | 34% |
| Edge case tests | 11 | 31% |
| Error handling tests | 7 | 20% |
| Verification tests | 5 | 14% |

This distribution is healthy - good coverage of both normal and exceptional cases.

---

## 🔄 Pattern Evolution Across Sessions

### Sessions 68-72: Consistent Patterns Emerging

1. **Initialization Testing**: All 5 sessions tested initialization thoroughly
2. **Edge Case Focus**: Growing emphasis on boundary conditions
3. **Mock Sophistication**: Increasingly complex mocking (from simple patches to `__import__` mocking)
4. **Temporary Path Usage**: Now standard practice for file system tests
5. **Logger Testing**: Systematic checking of log messages

### New Patterns in Session 72

1. **Import Error Testing**: First time mocking `builtins.__import__`
2. **`__file__` Patching**: New technique for path-dependent code
3. **Deduplication Awareness**: Accounting for dict key uniqueness

---

## 💡 Recommendations for Future Sessions

### Immediate Applications

1. **Always use unique test data prefixes** (json_*, test_*, mock_*)
2. **Include all dict keys** when creating objects from dicts
3. **Mock `__import__`** for import failure testing
4. **Use tmp_path + `__file__` patching** for path tests
5. **Distinguish processing vs. storage counts** in assertions

### Strategic Improvements

1. **Build a testing utilities module** with common patterns:
   - Helper for tmp_path + `__file__` setup
   - Custom import mocker
   - Logger assertion helpers

2. **Document tricky mocking patterns** in shared knowledge base

3. **Create test data generators** for complex structures (like templates)

4. **Consider property-based testing** for data validation (hypothesis library)

---

**Session 72 Lesson Summary**: Successfully achieved TRUE 100% coverage through systematic testing, sophisticated mocking techniques, and careful attention to data isolation and edge cases. ✅
