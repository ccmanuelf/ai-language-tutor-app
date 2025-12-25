# Session 96 - Priority 1: Budget Manager User Control - Implementation Plan

**Created:** 2025-12-09  
**Status:** Design Phase  
**Goal:** Enable users to select their preferred AI provider and control budget override behavior

---

## Problem Statement

Currently, the budget manager and AI router make provider decisions **without user input or consent**:

1. User selects "en-claude" (wants Claude)
2. Budget manager sees budget exceeded
3. Router **silently** forces Ollama without asking user
4. User gets degraded response without understanding why

**This violates user autonomy and creates poor UX.**

---

## Architecture Analysis

### Current Flow (BROKEN)
```
User Request: "en-claude"
  ↓
conversations.py: _parse_language_and_provider()
  ↓ Extracts: language="en", provider="claude"
  ↓
conversations.py: _get_ai_response()
  ↓ ❌ IGNORES provider! Only passes language="en"
  ↓
ai_router.select_provider(language="en", use_case="conversation")
  ↓ Checks budget → EXCEEDED
  ↓
ai_router._should_use_budget_fallback() → True
  ↓ ❌ NO USER NOTIFICATION
  ↓
ai_router._select_local_provider() → Forces Ollama
  ↓
User gets: Ollama response (not what they asked for!)
```

### Desired Flow (FIXED)
```
User Request: "en-claude"
  ↓
conversations.py: _parse_language_and_provider()
  ↓ Extracts: language="en", preferred_provider="claude"
  ↓
conversations.py: _get_ai_response()
  ↓ ✅ Passes BOTH language AND preferred_provider
  ↓
ai_router.select_provider(
    language="en",
    preferred_provider="claude",
    user_settings=user.ai_provider_settings
)
  ↓ Checks budget → EXCEEDED
  ↓ Checks user settings:
  ↓   - enforce_budget_limits: True/False
  ↓   - budget_override_allowed: True/False
  ↓   - provider_selection_mode: "user_choice" | "cost_optimized" | "quality_first"
  ↓
  ↓ If enforce_budget=False → Use Claude (user choice honored)
  ↓ If enforce_budget=True + override_allowed=True:
  ↓   → Return BudgetExceededWarning with options
  ↓   → User decides: Continue with Claude OR Use free Ollama
  ↓
User gets: Either Claude (their choice) OR informed decision about Ollama
```

---

## Implementation Plan

### Phase 1: Data Models and Settings

#### 1.1 User AI Provider Settings (Pydantic Model)
**File:** `app/models/schemas.py`

```python
from enum import Enum
from pydantic import BaseModel, Field

class ProviderSelectionMode(str, Enum):
    """How the system selects AI providers"""
    USER_CHOICE = "user_choice"          # Always respect user's explicit choice
    COST_OPTIMIZED = "cost_optimized"    # Always choose cheapest available
    QUALITY_FIRST = "quality_first"      # Prefer best quality within budget
    BALANCED = "balanced"                # Balance cost and quality

class AIProviderSettings(BaseModel):
    """User settings for AI provider selection and budget control"""
    
    # Provider Selection
    provider_selection_mode: ProviderSelectionMode = ProviderSelectionMode.BALANCED
    default_provider: str = "claude"  # Default when none specified
    
    # Budget Control
    enforce_budget_limits: bool = True  # Enforce monthly budget
    budget_override_allowed: bool = True  # Allow user to override budget
    alert_on_budget_threshold: float = 0.80  # Alert at 80% usage
    
    # Notifications
    notify_on_provider_change: bool = True  # Notify if provider switched
    notify_on_budget_alert: bool = True  # Notify on budget thresholds
    
    # Fallback Behavior
    auto_fallback_to_ollama: bool = False  # Auto-use Ollama when budget exceeded
    prefer_local_when_available: bool = False  # Prefer Ollama if available
```

#### 1.2 Budget Warning Models
**File:** `app/models/schemas.py`

```python
from typing import Optional

class BudgetExceededWarning(BaseModel):
    """Warning when budget is exceeded but user wants premium provider"""
    
    current_usage: float
    budget_limit: float
    percentage_used: float
    
    requested_provider: str
    estimated_cost: float
    
    alternative_provider: str  # Usually "ollama"
    alternative_cost: float = 0.0
    
    allow_override: bool = True
    message: str
    
    @classmethod
    def create(
        cls,
        budget_status: "BudgetStatus",
        requested_provider: str,
        estimated_cost: float
    ):
        return cls(
            current_usage=budget_status.used_budget,
            budget_limit=budget_status.total_budget,
            percentage_used=budget_status.percentage_used,
            requested_provider=requested_provider,
            estimated_cost=estimated_cost,
            alternative_provider="ollama",
            alternative_cost=0.0,
            allow_override=True,
            message=f"Budget exceeded ({budget_status.percentage_used:.1f}%). "
                   f"Continue with {requested_provider} (${estimated_cost:.4f}) or use free Ollama?"
        )

class BudgetThresholdAlert(BaseModel):
    """Alert when budget reaches threshold (e.g., 80%)"""
    
    threshold_percentage: float
    current_usage: float
    budget_limit: float
    remaining_budget: float
    days_remaining: int
    projected_monthly_cost: float
    
    message: str
    severity: str  # "info", "warning", "critical"
```

#### 1.3 Update User Model
**File:** `app/models/database.py`

Add to User.preferences default structure:
```python
# In User.__init__ or as class-level default
DEFAULT_PREFERENCES = {
    "ai_provider_settings": {
        "provider_selection_mode": "balanced",
        "default_provider": "claude",
        "enforce_budget_limits": True,
        "budget_override_allowed": True,
        "alert_on_budget_threshold": 0.80,
        "notify_on_provider_change": True,
        "notify_on_budget_alert": True,
        "auto_fallback_to_ollama": False,
        "prefer_local_when_available": False
    }
}
```

---

### Phase 2: Enhanced AI Router

#### 2.1 Update select_provider() Signature
**File:** `app/services/ai_router.py`

```python
async def select_provider(
    self,
    language: str = "en",
    use_case: str = "conversation",
    preferred_provider: Optional[str] = None,  # NEW: User's explicit choice
    user_preferences: Optional[Dict[str, Any]] = None,
    force_local: bool = False,
    enforce_budget: bool = True,  # NEW: Whether to enforce budget limits
) -> ProviderSelection:
    """
    Select the best provider for the request
    
    Args:
        language: Target language
        use_case: Type of interaction
        preferred_provider: User's explicitly chosen provider (e.g., "claude")
        user_preferences: User-specific preferences
        force_local: Force use of local models only
        enforce_budget: Whether to enforce budget limits
    
    Returns:
        Provider selection with reasoning
    """
```

#### 2.2 Add User Choice Priority Logic
**File:** `app/services/ai_router.py`

```python
async def select_provider(self, ...):
    # Priority 1: User explicitly chose a provider
    if preferred_provider:
        return await self._select_preferred_provider(
            preferred_provider=preferred_provider,
            language=language,
            enforce_budget=enforce_budget,
            user_preferences=user_preferences
        )
    
    # Priority 2: Continue with existing cost optimization logic
    # (only runs if user didn't specify a provider)
    ...

async def _select_preferred_provider(
    self,
    preferred_provider: str,
    language: str,
    enforce_budget: bool,
    user_preferences: Optional[Dict[str, Any]]
) -> ProviderSelection:
    """Select user's preferred provider, respecting budget settings"""
    
    # Check if provider exists
    if preferred_provider not in self.providers:
        logger.warning(f"Preferred provider '{preferred_provider}' not available, using fallback")
        return await self._select_fallback_provider(language)
    
    # If budget enforcement disabled, use preferred provider regardless of cost
    if not enforce_budget:
        logger.info(f"Budget enforcement disabled, using preferred provider: {preferred_provider}")
        return await self._create_provider_selection(
            provider_name=preferred_provider,
            language=language,
            reason="User preference (budget enforcement disabled)"
        )
    
    # Check budget status
    budget_status = await self.check_budget_status()
    
    # Estimate cost for preferred provider
    cost_estimate = await self._estimate_request_cost(
        preferred_provider, language, "conversation"
    )
    
    # Check if we can afford it
    if budget_status.remaining_budget >= cost_estimate:
        # Can afford, use preferred provider
        return await self._create_provider_selection(
            provider_name=preferred_provider,
            language=language,
            reason="User preference"
        )
    
    # Budget exceeded - check user's override settings
    ai_settings = self._get_ai_provider_settings(user_preferences)
    
    if ai_settings.get("budget_override_allowed", True):
        # Return selection with warning flag
        # Calling code should handle the warning
        selection = await self._create_provider_selection(
            provider_name=preferred_provider,
            language=language,
            reason="User preference (budget exceeded, override needed)"
        )
        selection.requires_budget_override = True
        selection.budget_warning = BudgetExceededWarning.create(
            budget_status=budget_status,
            requested_provider=preferred_provider,
            estimated_cost=cost_estimate
        )
        return selection
    
    # Auto-fallback enabled or override not allowed
    if ai_settings.get("auto_fallback_to_ollama", False):
        logger.info("Budget exceeded, auto-falling back to Ollama per user settings")
        return await self._select_local_provider(language, "budget_exceeded_auto_fallback")
    
    # Default: Return warning that budget exceeded
    raise BudgetExceededError(
        message="Budget exceeded and override not allowed",
        budget_status=budget_status,
        requested_provider=preferred_provider,
        estimated_cost=cost_estimate
    )
```

---

### Phase 3: Update Conversations API

#### 3.1 Pass Preferred Provider to Router
**File:** `app/api/conversations.py`

```python
async def _get_ai_response(
    request: ChatRequest, language_code: str, user_id: str, db: Session
) -> tuple[str, float]:
    """Get AI response from selected provider"""
    
    # Parse user's preferred provider from language string
    language_code, preferred_provider = _parse_language_and_provider(request.language)
    
    # Get user settings from database
    user = db.query(User).filter(User.user_id == user_id).first()
    user_preferences = user.preferences if user else {}
    ai_settings = user_preferences.get("ai_provider_settings", {})
    
    # Determine budget enforcement mode
    enforce_budget = ai_settings.get("enforce_budget_limits", True)
    
    try:
        # Select provider with user's preferences
        provider_selection = await ai_router.select_provider(
            language=language_code,
            use_case="conversation",
            preferred_provider=preferred_provider,  # ✅ NOW PASSED!
            user_preferences=user_preferences,
            enforce_budget=enforce_budget
        )
        
        # Check if budget override is required
        if hasattr(provider_selection, 'requires_budget_override') and provider_selection.requires_budget_override:
            # Return warning to user for confirmation
            # This would need to be handled by a new endpoint or response structure
            raise BudgetExceededError(
                warning=provider_selection.budget_warning
            )
        
        # Generate response
        if provider_selection.service and hasattr(provider_selection.service, "generate_response"):
            ai_response = await provider_selection.service.generate_response(
                messages=[{"role": "user", "content": request.message}],
                message=request.message,
                language=language_code,
                context={"language": language_code, "user_id": user_id},
                conversation_history=request.conversation_history,
            )
            response_text = ai_response.content if hasattr(ai_response, "content") else str(ai_response)
            cost_estimate = ai_response.cost if hasattr(ai_response, "cost") else 0.01
            return response_text, cost_estimate
        else:
            raise Exception("No AI service available")
            
    except BudgetExceededError as e:
        # Re-raise to be handled by endpoint
        raise
    except Exception as e:
        logger.error(f"AI service error: {e}")
        # Fallback to Ollama if all else fails
        return await _get_ollama_fallback_response(request, language_code)
```

#### 3.2 Add Budget Override Endpoint
**File:** `app/api/conversations.py`

```python
class ChatWithOverrideRequest(BaseModel):
    """Chat request with budget override confirmation"""
    message: str
    language: str = "en-claude"
    use_speech: bool = False
    conversation_history: Optional[List[Dict[str, str]]] = None
    override_budget: bool = False  # User confirms override

@router.post("/chat-with-override", response_model=ChatResponse)
async def chat_with_budget_override(
    request: ChatWithOverrideRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """
    Send message to AI with optional budget override
    
    If budget is exceeded and user wants premium provider,
    they must set override_budget=True to confirm
    """
    language_code, ai_provider = _parse_language_and_provider(request.language)
    conversation_id, message_id = _generate_conversation_ids(current_user.user_id)
    
    # Get user settings
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    user_preferences = user.preferences if user else {}
    ai_settings = user_preferences.get("ai_provider_settings", {})
    
    # Override budget enforcement if user confirmed
    enforce_budget = not request.override_budget
    
    try:
        # ... rest of implementation similar to chat_with_ai
        # but with enforce_budget parameter
        ...
```

---

### Phase 4: Budget Notification System

#### 4.1 Add Budget Threshold Monitoring
**File:** `app/services/budget_manager.py`

```python
async def check_budget_threshold_alerts(
    self,
    user_id: Optional[str] = None
) -> List[BudgetThresholdAlert]:
    """Check if budget thresholds have been crossed"""
    
    budget_status = self.get_current_budget_status()
    alerts = []
    
    # 80% threshold
    if budget_status.percentage_used >= 80 and budget_status.percentage_used < 90:
        alerts.append(BudgetThresholdAlert(
            threshold_percentage=80.0,
            current_usage=budget_status.used_budget,
            budget_limit=budget_status.total_budget,
            remaining_budget=budget_status.remaining_budget,
            days_remaining=budget_status.days_remaining,
            projected_monthly_cost=budget_status.projected_monthly_cost,
            message=f"Warning: You've used 80% of your monthly budget. ${budget_status.remaining_budget:.2f} remaining.",
            severity="warning"
        ))
    
    # 90% threshold
    if budget_status.percentage_used >= 90 and budget_status.percentage_used < 100:
        alerts.append(BudgetThresholdAlert(
            threshold_percentage=90.0,
            current_usage=budget_status.used_budget,
            budget_limit=budget_status.total_budget,
            remaining_budget=budget_status.remaining_budget,
            days_remaining=budget_status.days_remaining,
            projected_monthly_cost=budget_status.projected_monthly_cost,
            message=f"Critical: You've used 90% of your monthly budget. Only ${budget_status.remaining_budget:.2f} remaining.",
            severity="critical"
        ))
    
    return alerts
```

#### 4.2 Add Budget Status Endpoint
**File:** `app/api/conversations.py` or new `app/api/budget.py`

```python
@router.get("/budget-status")
async def get_budget_status(
    current_user: SimpleUser = Depends(require_auth),
):
    """Get current budget status and alerts"""
    
    budget_status = budget_manager.get_current_budget_status()
    alerts = await budget_manager.check_budget_threshold_alerts()
    
    return {
        "budget_status": {
            "total_budget": budget_status.total_budget,
            "used_budget": budget_status.used_budget,
            "remaining_budget": budget_status.remaining_budget,
            "percentage_used": budget_status.percentage_used,
            "alert_level": budget_status.alert_level.value,
            "days_remaining": budget_status.days_remaining,
            "projected_monthly_cost": budget_status.projected_monthly_cost,
            "is_over_budget": budget_status.is_over_budget
        },
        "alerts": [alert.dict() for alert in alerts],
        "recommendations": budget_manager.get_optimization_recommendations()
    }
```

---

## Testing Strategy

### Unit Tests
1. Test `AIProviderSettings` validation
2. Test `BudgetExceededWarning.create()`
3. Test `_select_preferred_provider()` with various budget scenarios
4. Test budget threshold alert generation

### Integration Tests
1. Test conversations.py passes preferred_provider to router
2. Test router respects user choice when budget allows
3. Test router returns warning when budget exceeded + override allowed
4. Test router auto-fallbacks when configured
5. Test budget notification endpoint

### E2E Tests
1. User selects "en-claude" with sufficient budget → Gets Claude
2. User selects "en-claude" with exceeded budget + override allowed → Gets warning
3. User selects "en-claude" with exceeded budget + override=True → Gets Claude
4. User with auto_fallback enabled + budget exceeded → Gets Ollama automatically
5. Budget threshold alerts trigger at 80%, 90%, 100%

---

## Success Criteria

✅ User can explicitly select ANY AI provider via language code (e.g., "en-claude")  
✅ Router respects user's choice when budget allows  
✅ User gets notified when budget threshold reached (80%)  
✅ User can choose to override budget and use premium provider  
✅ User can configure provider selection mode (user_choice, cost_optimized, etc.)  
✅ User can disable budget enforcement entirely  
✅ User can enable auto-fallback to Ollama  
✅ All existing tests continue to pass (no regressions)  
✅ New tests achieve 100% coverage of new functionality  
✅ E2E tests validate real user scenarios  

---

## Implementation Order

1. **Data Models** - AIProviderSettings, BudgetExceededWarning, BudgetThresholdAlert
2. **Budget Manager** - Add threshold monitoring and alerts
3. **AI Router** - Add preferred_provider parameter and user choice logic
4. **Conversations API** - Pass preferred_provider, handle budget warnings
5. **Unit Tests** - Test all new components individually
6. **Integration Tests** - Test component interactions
7. **E2E Tests** - Test complete user workflows
8. **Documentation** - Update API docs and user guides

---

**Next Step:** Begin implementation with Phase 1 (Data Models)
