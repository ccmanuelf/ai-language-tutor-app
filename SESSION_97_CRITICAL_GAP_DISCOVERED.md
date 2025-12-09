# Session 97 - Critical Gap Discovered: No Ollama Model Selection

**Discovered:** 2025-12-09 (Post-Session 97)  
**Reported By:** User  
**Severity:** HIGH - UX Issue  
**Status:** 🔴 **NOT IMPLEMENTED**

---

## 🚨 PROBLEM STATEMENT

### What's Missing
**Users have NO control over which Ollama model to use when falling back to local processing.**

### Current Behavior
When budget is exceeded or cloud providers unavailable:
1. System automatically selects Ollama
2. System calls `ollama_service.get_recommended_model(language)`
3. Model is chosen based ONLY on language (hardcoded logic)
4. **User has zero control over model selection**

### Why This Is Critical
- Users may have multiple Ollama models installed (llama2:7b, mistral:7b, llama2:13b, etc.)
- Different models have different capabilities and resource requirements
- Users may prefer faster models (7b) or higher quality (13b)
- Without control, Ollama fallback becomes inflexible and potentially useless

---

## 📊 CURRENT IMPLEMENTATION ANALYSIS

### Where Model Selection Happens

#### 1. OllamaService.get_recommended_model() (ollama_service.py:178-202)
```python
def get_recommended_model(self, language: str, use_case: str = "conversation") -> str:
    """Get recommended model for specific language and use case"""
    language_models = {
        "en": ["neural-chat:7b", "llama2:7b", "codellama:7b"],  # Hardcoded!
        "fr": ["mistral:7b", "llama2:7b"],                      # Hardcoded!
        "es": ["llama2:7b", "llama2:13b"],                      # Hardcoded!
        "de": ["llama2:7b", "llama2:13b"],                      # Hardcoded!
        "it": ["llama2:7b", "llama2:13b"],                      # Hardcoded!
        "pt": ["llama2:13b", "llama2:7b"],                      # Hardcoded!
    }

    recommended = language_models.get(language, ["llama2:7b"])
    
    # For technical use cases, prefer code-specialized models
    if use_case == "technical" and language == "en":
        return "codellama:7b"  # Hardcoded!
    
    # For advanced grammar, prefer larger models
    if use_case == "grammar" and "llama2:13b" in recommended:
        return "llama2:13b"  # Hardcoded!
    
    return recommended[0]  # Always returns first in list
```

**Issues:**
- ❌ Hardcoded model preferences
- ❌ No user input considered
- ❌ Always returns first model in list
- ❌ Doesn't check what user has installed
- ❌ Ignores user's model preferences

#### 2. AI Router Fallback (ai_router.py:464)
```python
# Get recommended model for language
model = ollama_service.get_recommended_model(language)

return ProviderSelection(
    provider_name="ollama",
    service=ollama_service,
    model=model,  # ❌ No user preference checked
    ...
)
```

**Issues:**
- ❌ No user preferences parameter
- ❌ Doesn't check AIProviderSettings
- ❌ Doesn't allow model override

#### 3. Generate Response (ollama_service.py:204-265)
```python
async def generate_response(
    self,
    messages: List[Dict[str, str]],
    language: str = "en",
    model: Optional[str] = None,  # ✅ Parameter exists but never used!
    **kwargs
) -> AIResponse:
    """Generate response using Ollama"""
    
    # Select model
    if not model:
        model = self.get_recommended_model(language, kwargs.get("use_case", "conversation"))
    
    # ❌ Even though parameter exists, router never passes it
```

**Issues:**
- ✅ `model` parameter exists
- ❌ Router never passes user's preferred model
- ❌ Falls back to hardcoded selection

---

## 🔍 WHAT WAS TESTED (Session 97)

### E2E Tests Created
All 7 Ollama E2E tests validate the **automatic** model selection:

1. ✅ `test_ollama_service_availability` - Service works
2. ✅ `test_ollama_real_conversation_english` - Uses auto-selected model
3. ✅ `test_ollama_multi_language_support` - Auto-selection per language
4. ✅ `test_ollama_model_selection` - Tests `get_recommended_model()` **hardcoded logic**
5. ✅ `test_ollama_budget_exceeded_fallback` - Uses auto-selected model
6. ✅ `test_ollama_response_quality` - Uses auto-selected model
7. ✅ `test_ollama_privacy_mode` - Uses auto-selected model

### What Was NOT Tested
❌ User selecting a specific Ollama model  
❌ User preferences for Ollama models  
❌ Passing preferred model through router  
❌ Different models for same language  
❌ Model selection based on user's installed models  

---

## 💡 WHAT SHOULD BE IMPLEMENTED

### Required Changes

#### 1. Update AIProviderSettings Schema
**File:** `app/models/schemas.py`

```python
class AIProviderSettings(BaseSchema):
    """User settings for AI provider selection and budget control"""
    
    # Existing fields...
    provider_selection_mode: ProviderSelectionMode = ProviderSelectionMode.BALANCED
    default_provider: str = Field("claude", description="Default provider")
    
    # NEW: Ollama model preferences
    preferred_ollama_model: Optional[str] = Field(
        None, 
        description="Preferred Ollama model (e.g., 'llama2:13b', 'mistral:7b')"
    )
    ollama_model_by_language: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Language-specific Ollama models (e.g., {'en': 'neural-chat:7b', 'fr': 'mistral:7b'})"
    )
    ollama_model_by_use_case: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Use-case specific models (e.g., {'technical': 'codellama:7b', 'grammar': 'llama2:13b'})"
    )
```

#### 2. Update Router to Pass User Preferences
**File:** `app/services/ai_router.py`

```python
async def _select_local_provider(
    self, 
    language: str, 
    reason: str,
    user_preferences: Optional[Dict[str, Any]] = None  # NEW parameter
) -> ProviderSelection:
    """Select local Ollama provider"""
    
    if "ollama" not in self.providers:
        self.register_provider("ollama", ollama_service)
    
    ollama_available = await ollama_service.check_availability()
    if not ollama_available:
        raise Exception("Ollama not available")
    
    # NEW: Get user's preferred model
    preferred_model = None
    if user_preferences:
        ai_settings = user_preferences.get("ai_provider_settings", {})
        
        # Check language-specific preference
        model_by_lang = ai_settings.get("ollama_model_by_language", {})
        if language in model_by_lang:
            preferred_model = model_by_lang[language]
        
        # Check general preference
        if not preferred_model:
            preferred_model = ai_settings.get("preferred_ollama_model")
    
    # Fallback to recommended if no preference
    if not preferred_model:
        preferred_model = ollama_service.get_recommended_model(language)
    
    return ProviderSelection(
        provider_name="ollama",
        service=ollama_service,
        model=preferred_model,  # ✅ Now uses user preference!
        reason=f"Local fallback - {reason}",
        confidence=0.7,
        cost_estimate=0.0,
        is_fallback=True,
        fallback_reason=FallbackReason(reason),
    )
```

#### 3. Update Conversation API to Store Model Selection
**File:** `app/api/conversations.py`

Currently, conversations store `ai_model` but it's not used for Ollama selection. Need to:
- Allow users to specify preferred Ollama model in ChatRequest
- Store selected model in conversation history
- Pass model preference to router

#### 4. Add UI for Model Selection
**Frontend Changes Needed:**
- List available Ollama models (via API)
- Allow user to select preferred model
- Save preference in user settings
- Display which model is being used in responses

---

## 📋 IMPLEMENTATION PLAN

### Priority: HIGH (Should be Session 98 or 99)

### Phase 1: Data Model Updates
1. Add Ollama model fields to `AIProviderSettings`
2. Update `User.get_ai_provider_settings()` defaults
3. Create migration if needed

### Phase 2: Router Logic Updates
1. Update `_select_local_provider()` signature to accept `user_preferences`
2. Add model preference extraction logic
3. Update all calls to `_select_local_provider()`
4. Pass `model` parameter to `generate_response()`

### Phase 3: API Endpoints
1. Create endpoint to list available Ollama models
2. Add model selection to user preferences endpoint
3. Update conversation API to accept model preference

### Phase 4: Testing
1. Unit tests for model preference extraction
2. Integration tests for router with model preferences
3. E2E tests for user-specified model selection
4. Test with models that don't exist (error handling)

### Phase 5: Documentation
1. Update API documentation
2. Add model selection to user guide
3. Document available models per language

---

## 🎯 SUCCESS CRITERIA

Implementation is complete when:

1. ✅ User can specify preferred Ollama model in settings
2. ✅ User can set different models per language
3. ✅ User can set different models per use case
4. ✅ Router respects user's model preference
5. ✅ System falls back gracefully if preferred model unavailable
6. ✅ User can see which model is being used in responses
7. ✅ API endpoint exists to list available Ollama models
8. ✅ Comprehensive tests validate user control
9. ✅ Documentation explains model selection

---

## 🧪 TEST CASES NEEDED

### Unit Tests
```python
def test_user_preferred_ollama_model_used():
    """Test router uses user's preferred Ollama model"""
    user_preferences = {
        "ai_provider_settings": {
            "preferred_ollama_model": "llama2:13b"
        }
    }
    # Router should select llama2:13b, not auto-selected model

def test_language_specific_ollama_model():
    """Test language-specific model preferences"""
    user_preferences = {
        "ai_provider_settings": {
            "ollama_model_by_language": {
                "en": "neural-chat:7b",
                "fr": "mistral:7b"
            }
        }
    }
    # English should use neural-chat:7b
    # French should use mistral:7b
```

### Integration Tests
```python
async def test_budget_fallback_respects_user_model():
    """Test budget exceeded fallback uses user's preferred model"""
    # Set budget exceeded
    # Set user preference for llama2:13b
    # Verify fallback uses llama2:13b, not auto-selected
```

### E2E Tests
```python
async def test_user_selects_ollama_model_e2e():
    """Test user can select specific Ollama model end-to-end"""
    # User sets preference for codellama:7b
    # User sends technical question
    # System uses codellama:7b
    # Response includes model information
```

---

## 📊 IMPACT ANALYSIS

### Current State
- ❌ Users cannot choose Ollama model
- ❌ System uses hardcoded model selection
- ❌ Ollama fallback is inflexible
- ⚠️ May render Ollama useless if wrong model selected

### After Implementation
- ✅ Users have full control over model selection
- ✅ Different models per language/use case
- ✅ Flexible fallback configuration
- ✅ Ollama becomes truly useful
- ✅ Better UX for local-first users

---

## 🔗 RELATED ISSUES

### Existing Features That Need Updates
1. **Budget Manager** - Works correctly, no changes needed
2. **Router Fallback** - Needs model preference logic
3. **Ollama Service** - Has model parameter, just not used
4. **User Settings** - Needs new fields for model preferences

### Similar Functionality
- Cloud providers have model selection (Claude, Mistral, etc.)
- Should have parity for Ollama models

---

## 💬 USER QUOTE (Original Discovery)

> "Let me ask you this, if the user fallbacks to Ollama, will the user have the ability to select any of the existing local models? or what model is going to be used? I'm not sure that ability is included into the tested logic, please double check and confirm. If not included, we need to make sure that ability is there otherwise local model might become useless."

**User is 100% correct** - This feature is missing and needs to be implemented.

---

## ⏭️ NEXT STEPS

### Immediate Actions
1. ✅ Document this gap (this file)
2. ⏳ Create GitHub issue with this analysis
3. ⏳ Add to Session 98 objectives (alongside Priority 3)
4. ⏳ Update DAILY_PROMPT_TEMPLATE.md

### Session 98 Options
**Option A:** Tackle both Priority 3 (Qwen cleanup) + Ollama model selection  
**Option B:** Focus only on Ollama model selection (more critical)  
**Option C:** Do Priority 3 first, then Ollama model selection in Session 99  

**Recommendation:** Option A if time permits, otherwise Option C

---

## 📝 LESSONS LEARNED

### What Went Well (Session 97)
✅ E2E tests validated Ollama works  
✅ Fallback mechanism proven  
✅ Documentation comprehensive  

### What Was Missed
❌ Didn't validate user control over model selection  
❌ Assumed automatic selection was sufficient  
❌ Didn't think about UX for users with multiple models  

### Key Insight
> "Testing that something works is different from testing that users have control over how it works."

We validated Ollama **functions**, but didn't validate user **choice**.

---

**Status:** 🔴 Critical Gap Documented  
**Next:** Create GitHub issue and prioritize for Session 98/99  
**Severity:** HIGH - Affects UX and Ollama usefulness  
**Effort:** MEDIUM - ~2-3 hours (data models + router + tests)
