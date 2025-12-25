# Qwen Cleanup Inventory - Session 100

**Generated:** 2025-12-10  
**Status:** Phase 1 - Complete Inventory

---

## EXECUTIVE SUMMARY

**Total References Found:** 100+ across application, tests, and documentation

**Critical Files:**
1. `app/services/qwen_service.py` - Entire 295-line service file (OBSOLETE)
2. `app/services/ai_router.py` - "qwen" alias registration (line 940)
3. `tests/test_qwen_service.py` - Full test file for obsolete service

**Strategy:** Delete `qwen_service.py` and all references, consolidate to DeepSeek

---

## DETAILED INVENTORY

### CATEGORY 1: Core Service Files (CRITICAL)

#### app/services/qwen_service.py (295 lines)
**Status:** OBSOLETE - Can be deleted  
**Reason:** DeepSeek service replaced this functionality  
**Lines:** Entire file  
**Action:** DELETE COMPLETELY

**References within file:**
- Line 31: `self.service_name = "qwen"`
- Line 135: `response = self._call_qwen_api(...)`
- Line 165: `return model or "qwen-plus"`
- Line 167: `def _call_qwen_api(...)`
- Line 208: `provider="qwen"`
- Line 234: `model=model or "qwen-plus"`
- Line 235: `provider="qwen"`
- Line 264: `else "qwen-plus"`
- Line 295: `qwen_service = QwenService()`

---

#### app/services/ai_router.py
**Status:** ACTIVE - Needs updates  
**Action:** REPLACE "qwen" with "deepseek"

**Line 556:** Default models
```python
"qwen": "qwen-plus",  # ❌ REMOVE
```
**Action:** Delete this line entirely

**Line 573:** Cost configuration
```python
"qwen": 0.002,  # Qwen cost (estimated)  # ❌ REMOVE
```
**Action:** Delete this line entirely (DeepSeek has own cost)

**Line 940:** Provider registration ⭐ **CRITICAL**
```python
ai_router.register_provider("qwen", deepseek_service)  # ❌ WRONG ALIAS
```
**Action:** Change to:
```python
ai_router.register_provider("deepseek", deepseek_service)  # ✅ Correct
```

---

#### app/services/budget_manager.py
**Status:** ACTIVE - Needs cleanup  
**Lines 96-99:** Qwen pricing configuration
```python
"qwen": {
    "qwen-turbo": {"input": 0.0001, "output": 0.0002},
    "qwen-plus": {"input": 0.0004, "output": 0.0008},
    "qwen-max": {"input": 0.002, "output": 0.006},
},
```
**Action:** DELETE this entire block (DeepSeek has own pricing)

---

#### app/services/ollama_service.py
**Status:** ACTIVE - References for detection

**Line 235:** Multilingual model detection
```python
multilingual_indicators = ["mistral", "qwen", "gemma", "llama"]
```
**Action:** KEEP "qwen" - This detects Ollama models named "qwen"  
**Reason:** Ollama has qwen models, different from our API service

**Line 258:** Model capability detection
```python
elif "qwen" in name_lower:
```
**Action:** KEEP - Same reason as above

---

### CATEGORY 2: API and Configuration

#### app/core/config.py
**Line 51:** Deprecated environment variable
```python
description="[DEPRECATED] Alibaba Qwen API key - use DEEPSEEK_API_KEY instead",
```
**Action:** KEEP - Marks deprecation clearly

---

#### app/utils/api_key_validator.py
**Lines 126-171:** Qwen API validation
```python
async def validate_qwen_api(self) -> Dict[str, Any]:
    """Validate Qwen API key"""
    # ... implementation ...
```
**Action:** DELETE entire `validate_qwen_api` method

**Line 171:** Validator registration
```python
("qwen", self.validate_qwen_api),
```
**Action:** DELETE this line from validator list

---

#### app/models/database.py
**Line 278:** Database comment
```python
ai_model = Column(String(50), nullable=True)  # claude, qwen, mistral, etc.
```
**Action:** UPDATE comment to:
```python
ai_model = Column(String(50), nullable=True)  # claude, deepseek, mistral, etc.
```

---

#### app/api/conversations.py
**Lines 364-365:** Language option
```python
"providers": ["qwen"],
"display": "Chinese (Qwen)",
```
**Action:** UPDATE to:
```python
"providers": ["deepseek"],
"display": "Chinese (DeepSeek)",
```

---

#### app/frontend/chat.py
**Line 34:** Language selection option
```python
Option("Chinese (Qwen)", value="zh-qwen"),
```
**Action:** UPDATE to:
```python
Option("Chinese (DeepSeek)", value="zh-deepseek"),
```

---

### CATEGORY 3: Test Files (EXTENSIVE)

#### tests/test_qwen_service.py (ENTIRE FILE)
**Status:** OBSOLETE - Full test suite for qwen_service.py  
**Lines:** All ~600 lines  
**Action:** DELETE COMPLETELY

---

#### tests/integration/test_ai_integration.py
**Multiple references:**

**Lines 46-48:** Mock import
```python
"app.services.qwen_service.QwenService.generate_response",
) as mock_qwen,
```
**Action:** REPLACE with:
```python
"app.services.deepseek_service.DeepSeekService.generate_response",
) as mock_deepseek,
```

**Line 53:** Mock return value
```python
mock_qwen.return_value = Mock(content="Qwen response", cost=0.01)
```
**Action:** REPLACE with:
```python
mock_deepseek.return_value = Mock(content="DeepSeek response", cost=0.01)
```

**Line 62:** Comment
```python
# Test Chinese - should prefer Qwen if available
```
**Action:** UPDATE to:
```python
# Test Chinese - should prefer DeepSeek if available
```

**Lines 245-252:** Fallback test
```python
"app.services.qwen_service.QwenService.generate_response",
) as mock_qwen,
mock_qwen.side_effect = Exception("Qwen unavailable")
```
**Action:** REPLACE with DeepSeek references

**Lines 401-407:** Chinese test
```python
"app.services.qwen_service.QwenService.generate_response",
) as mock_qwen,
mock_qwen.return_value = Mock(content="Chinese response", cost=0.01)
```
**Action:** REPLACE with DeepSeek references

**Line 427:** Comment
```python
# Test Chinese with Qwen
```
**Action:** UPDATE to:
```python
# Test Chinese with DeepSeek
```

**Line 430:** Language code
```python
json={"message": "你好", "language": "zh-qwen"},
```
**Action:** UPDATE to:
```python
json={"message": "你好", "language": "zh-deepseek"},
```

---

#### tests/test_api_conversations.py
**Line 22:** Import
```python
get_successful_qwen_mock,
```
**Action:** REPLACE with:
```python
get_successful_deepseek_mock,
```

**Line 772:** Test case
```python
("zh-qwen", get_successful_qwen_mock()),
```
**Action:** REPLACE with:
```python
("zh-deepseek", get_successful_deepseek_mock()),
```

---

#### tests/e2e/test_ai_e2e.py
**Line 177:** Provider assertion
```python
assert selection.provider_name in ["claude", "mistral", "qwen", "ollama"]
```
**Action:** UPDATE to:
```python
assert selection.provider_name in ["claude", "mistral", "deepseek", "ollama"]
```

**Line 351:** Provider validation
```python
assert data["ai_provider"] in ["claude", "mistral", "qwen"], (
```
**Action:** UPDATE to:
```python
assert data["ai_provider"] in ["claude", "mistral", "deepseek"], (
```

**Line 348:** Comment
```python
# Verify using real AI provider (Claude, Mistral, or Qwen - not Ollama fallback)
```
**Action:** UPDATE to:
```python
# Verify using real AI provider (Claude, Mistral, or DeepSeek - not Ollama fallback)
```

**Line 697:** Documentation string
```python
print("  - Make real API calls to Claude, Mistral, Qwen")
```
**Action:** UPDATE to:
```python
print("  - Make real API calls to Claude, Mistral, DeepSeek")
```

---

#### tests/test_helpers/ai_mocks.py
**Line 102:** Docstring
```python
provider: Provider name (claude, mistral, qwen)
```
**Action:** UPDATE to:
```python
provider: Provider name (claude, mistral, deepseek)
```

**Line 206:** Docstring
```python
provider: Provider to simulate (claude, mistral, qwen)
```
**Action:** UPDATE to:
```python
provider: Provider to simulate (claude, mistral, deepseek)
```

**Lines 312-315:** Mock function
```python
def get_successful_qwen_mock() -> Mock:
    """Get mock for successful Qwen AI service"""
    return _create_ai_mock(
        response_content="你好！我是Qwen，你的AI语言导师。", provider="qwen"
```
**Action:** REPLACE with:
```python
def get_successful_deepseek_mock() -> Mock:
    """Get mock for successful DeepSeek AI service"""
    return _create_ai_mock(
        response_content="你好！我是DeepSeek，你的AI语言导师。", provider="deepseek"
```

---

#### tests/test_ai_router.py
**Lines 222-226:** Test method
```python
def test_get_model_for_provider_qwen(self):
    """Test getting model for Qwen provider"""
    router = AIRouter()
    model = router._get_model_for_provider("qwen", "zh")
    assert model == "qwen-plus"
```
**Action:** UPDATE to test DeepSeek:
```python
def test_get_model_for_provider_deepseek(self):
    """Test getting model for DeepSeek provider"""
    router = AIRouter()
    model = router._get_model_for_provider("deepseek", "zh")
    assert model == "deepseek-chat"
```

---

### CATEGORY 4: Documentation Files

#### .env and .env.example
**.env Line 23:**
```
QWEN_API_KEY=***REMOVED***
```
**Action:** DELETE (actual API key, move to DeepSeek)

**.env.example Line 38:**
```
# QWEN_API_KEY=your_qwen_api_key_here
```
**Action:** DELETE (already has DEEPSEEK_API_KEY)

---

#### API_KEYS_SETUP_GUIDE.md
**Multiple references** (Lines 55, 173, 174, 257)
**Action:** UPDATE all to use DEEPSEEK_API_KEY instead

---

#### docs/TESTING_STRATEGY.md
**Lines 281, 464:** References to `get_successful_qwen_mock()`
**Action:** UPDATE to `get_successful_deepseek_mock()`

---

#### docs/architecture/CURRENT_ARCHITECTURE.md
**Multiple references** (Lines 91, 141, 146, 427, 489)
**Action:** UPDATE all "qwen" to "deepseek"

---

#### Other Documentation
**Files with references:**
- `docs/PROJECT_STATUS.md`
- `docs/development/SETUP_GUIDE.md`
- `docs/TEST_FAILURES_ANALYSIS.md`
- `docs/TRUE_100_PERCENT_VALIDATION.md`
- `docs/COMPLEXITY_C_FUNCTIONS_DOCUMENTATION.md`
- `docs/CODE_STYLE_GUIDE.md`
- `docs/PHASE_3A_PROGRESS.md`
- `CONFIGURATION_FIXES_EXPLAINED.md`

**Action:** UPDATE all references from "qwen" to "deepseek"  
**Note:** Historical context (like "we replaced Qwen with DeepSeek") can remain

---

## SPECIAL CASES TO KEEP

### 1. Ollama Service References
**Files:** `app/services/ollama_service.py` (Lines 235, 258)
**Reason:** Detecting Ollama-hosted "qwen" models (different from our API service)
**Action:** KEEP as-is

### 2. Deprecation Notice
**File:** `app/core/config.py` (Line 51)
**Reason:** Marks QWEN_API_KEY as deprecated with migration path
**Action:** KEEP as-is (documents migration)

### 3. Session Documentation
**Files:** `SESSION_*.md`, `DAILY_PROMPT_TEMPLATE.md`
**Reason:** Historical context, lessons learned
**Action:** KEEP all references (historical record)

---

## SUMMARY STATISTICS

**Files to DELETE:**
1. `app/services/qwen_service.py` (295 lines)
2. `tests/test_qwen_service.py` (~600 lines)

**Files to UPDATE:**
1. `app/services/ai_router.py` - 3 changes
2. `app/services/budget_manager.py` - 1 deletion
3. `app/utils/api_key_validator.py` - 2 deletions
4. `app/models/database.py` - 1 comment update
5. `app/api/conversations.py` - 1 update
6. `app/frontend/chat.py` - 1 update
7. `tests/integration/test_ai_integration.py` - ~8 changes
8. `tests/test_api_conversations.py` - 2 changes
9. `tests/e2e/test_ai_e2e.py` - 4 changes
10. `tests/test_helpers/ai_mocks.py` - 3 changes
11. `tests/test_ai_router.py` - 1 method update
12. `.env` - 1 deletion
13. `.env.example` - 1 deletion
14. Multiple documentation files - ~15 updates

**Total Estimated Changes:**
- Files deleted: 2
- Files modified: ~25
- Lines changed: ~50-75
- References updated: 100+

---

## RISK ASSESSMENT

**Risk Level:** LOW

**Reasons:**
1. DeepSeek service already in production (Sessions 96-99)
2. No production code depends on "qwen" name
3. All tests currently passing (4326/4326)
4. Changes are systematic find-replace operations

**Mitigation:**
1. Test after each category of changes
2. Run full test suite before committing
3. Verify no "qwen" references remain (except Ollama detection)

---

## NEXT STEPS (PHASE 2)

Based on this inventory, proceed to Phase 2: Strategy Decision Document
