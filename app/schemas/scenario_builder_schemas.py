"""
Pydantic Schemas for Scenario Builder
AI Language Tutor App - Session 131

Defines request and response models for the Scenario Builder API.
Provides validation, serialization, and documentation for all endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============================================================================
# PHASE SCHEMAS
# ============================================================================


class PhaseRequest(BaseModel):
    """Schema for creating/updating a scenario phase"""

    name: str = Field(..., min_length=3, max_length=255, description="Phase name")
    description: str = Field(
        ..., min_length=10, max_length=1000, description="What happens in this phase"
    )
    expected_duration_minutes: int = Field(
        ..., ge=1, le=30, description="Expected duration in minutes"
    )
    key_vocabulary: List[str] = Field(
        ..., min_length=3, description="Important vocabulary words"
    )
    essential_phrases: List[str] = Field(
        ..., min_length=3, description="Must-know phrases"
    )
    learning_objectives: List[str] = Field(
        ..., min_length=1, description="Learning goals"
    )
    success_criteria: List[str] = Field(
        ..., min_length=1, description="Success indicators"
    )
    cultural_notes: Optional[str] = Field(None, description="Cultural context")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ordering Food",
                "description": "Review the menu and place your order with the server",
                "expected_duration_minutes": 5,
                "key_vocabulary": ["appetizer", "main course", "beverage", "allergies"],
                "essential_phrases": ["I'll have the...", "What do you recommend?"],
                "learning_objectives": [
                    "Order meals confidently",
                    "Ask for recommendations",
                ],
                "success_criteria": ["Place complete order", "Make special request"],
                "cultural_notes": "It's acceptable to ask questions about dishes",
            }
        }
    )


class PhaseResponse(BaseModel):
    """Schema for phase in API responses"""

    id: int
    scenario_id: int
    phase_number: int
    phase_id: str
    name: str
    description: Optional[str]
    expected_duration_minutes: Optional[int]
    key_vocabulary: List[str]
    essential_phrases: List[str]
    learning_objectives: List[str]
    success_criteria: List[str]
    cultural_notes: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SCENARIO SCHEMAS
# ============================================================================


class CreateScenarioRequest(BaseModel):
    """Schema for creating a new scenario"""

    title: str = Field(..., min_length=3, max_length=255, description="Scenario title")
    description: Optional[str] = Field(
        None, max_length=500, description="Scenario description"
    )
    category: str = Field(..., description="Scenario category")
    difficulty: str = Field(
        ...,
        pattern="^(beginner|intermediate|advanced)$",
        description="Difficulty level",
    )
    estimated_duration: int = Field(
        ..., ge=5, le=60, description="Estimated duration in minutes"
    )
    language: Optional[str] = Field(
        "en", min_length=2, max_length=10, description="Target language code"
    )
    user_role: Optional[str] = Field(
        None, max_length=50, description="Role the user plays"
    )
    ai_role: Optional[str] = Field(None, max_length=50, description="Role the AI plays")
    setting: Optional[str] = Field(None, max_length=500, description="Physical setting")
    is_public: Optional[bool] = Field(
        False, description="Make scenario publicly available"
    )

    phases: List[PhaseRequest] = Field(
        ..., min_length=2, max_length=6, description="Scenario phases (2-6)"
    )

    prerequisites: Optional[List[str]] = Field(
        default_factory=lambda: [], description="Required prior knowledge"
    )
    learning_outcomes: Optional[List[str]] = Field(
        default_factory=lambda: [], description="Expected outcomes"
    )
    vocabulary_focus: Optional[List[str]] = Field(
        default_factory=lambda: [], description="Key vocabulary"
    )
    cultural_context: Optional[Dict[str, str]] = Field(
        default_factory=lambda: {}, description="Cultural notes"
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Validate category against known categories"""
        valid_categories = [
            "restaurant",
            "travel",
            "shopping",
            "business",
            "social",
            "healthcare",
            "emergency",
            "daily_life",
            "hobbies",
            "education",
        ]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Coffee Shop Order",
                "description": "Practice ordering coffee and snacks",
                "category": "restaurant",
                "difficulty": "beginner",
                "estimated_duration": 10,
                "language": "en",
                "user_role": "customer",
                "ai_role": "barista",
                "setting": "A busy coffee shop",
                "is_public": False,
                "phases": [
                    {
                        "name": "Ordering",
                        "description": "Place your order at the counter",
                        "expected_duration_minutes": 5,
                        "key_vocabulary": ["coffee", "size", "milk", "sugar"],
                        "essential_phrases": ["I'd like a...", "Can I get..."],
                        "learning_objectives": ["Order drinks confidently"],
                        "success_criteria": ["Place complete order"],
                        "cultural_notes": "Tip jar is optional",
                    },
                    {
                        "name": "Payment",
                        "description": "Pay for your order",
                        "expected_duration_minutes": 2,
                        "key_vocabulary": ["cash", "card", "receipt"],
                        "essential_phrases": ["How much is that?", "Keep the change"],
                        "learning_objectives": ["Handle payment"],
                        "success_criteria": ["Complete transaction"],
                        "cultural_notes": "Tipping is customary",
                    },
                ],
                "prerequisites": ["basic_greetings", "numbers"],
                "learning_outcomes": ["Order coffee independently"],
                "vocabulary_focus": ["coffee", "latte", "cappuccino"],
                "cultural_context": {"tipping": "1-2 dollars is standard"},
            }
        }
    )


class UpdateScenarioRequest(BaseModel):
    """Schema for updating an existing scenario (all fields optional)"""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    difficulty: Optional[str] = Field(
        None, pattern="^(beginner|intermediate|advanced)$"
    )
    estimated_duration: Optional[int] = Field(None, ge=5, le=60)
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    user_role: Optional[str] = Field(None, max_length=50)
    ai_role: Optional[str] = Field(None, max_length=50)
    setting: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None

    phases: Optional[List[PhaseRequest]] = Field(None, min_length=2, max_length=6)

    prerequisites: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    vocabulary_focus: Optional[List[str]] = None
    cultural_context: Optional[Dict[str, str]] = None

    model_config = ConfigDict(from_attributes=True)


class ScenarioResponse(BaseModel):
    """Schema for scenario in API responses"""

    id: int
    scenario_id: str
    title: str
    description: Optional[str]
    category: str
    difficulty: str
    estimated_duration: int
    language: Optional[str]
    user_role: Optional[str]
    ai_role: Optional[str]
    setting: Optional[str]
    created_by: int
    is_system_scenario: bool
    is_public: bool
    prerequisites: List[str]
    learning_outcomes: List[str]
    vocabulary_focus: List[str]
    cultural_context: Dict[str, str]
    phases: List[PhaseResponse]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TEMPLATE SCHEMAS
# ============================================================================


class CreateFromTemplateRequest(BaseModel):
    """Schema for creating scenario from template"""

    template_id: str = Field(..., description="Template identifier")
    customization: Dict[str, Any] = Field(
        default_factory=lambda: {},
        description="Custom overrides (title, description, difficulty)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "template_id": "template_restaurant_basic",
                "customization": {
                    "title": "My Custom Restaurant Scenario",
                    "description": "Personalized restaurant experience",
                    "difficulty": "intermediate",
                },
            }
        }
    )


class TemplateResponse(BaseModel):
    """Schema for template in API responses"""

    template_id: str
    title: str
    description: str
    category: str
    difficulty: str
    estimated_duration: int
    phase_count: int = Field(..., description="Number of phases in template")
    preview_vocabulary: List[str] = Field(
        ..., description="Sample vocabulary from template"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# OTHER REQUEST SCHEMAS
# ============================================================================


class DuplicateScenarioRequest(BaseModel):
    """Schema for duplicating a scenario"""

    new_title: str = Field(
        ..., min_length=3, max_length=255, description="Title for the duplicate"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"new_title": "My Custom Version of Restaurant Scenario"}
        }
    )


class UpdateVisibilityRequest(BaseModel):
    """Schema for changing scenario visibility"""

    is_public: bool = Field(
        ..., description="Make scenario public (true) or private (false)"
    )

    model_config = ConfigDict(json_schema_extra={"example": {"is_public": True}})


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class ScenarioListResponse(BaseModel):
    """Schema for list of scenarios"""

    scenarios: List[ScenarioResponse]
    count: int = Field(..., description="Total number of scenarios")

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Schema for list of templates"""

    templates: List[TemplateResponse]
    count: int = Field(..., description="Total number of templates")

    model_config = ConfigDict(from_attributes=True)


class ScenarioCreateResponse(BaseModel):
    """Schema for scenario creation response"""

    success: bool
    scenario_id: str
    message: str = Field(default="Scenario created successfully")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "scenario_id": "coffee_shop_order_a1b2c3d4",
                "message": "Scenario created successfully",
            }
        }
    )


class ScenarioDeleteResponse(BaseModel):
    """Schema for scenario deletion response"""

    success: bool
    message: str = Field(default="Scenario deleted successfully")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"success": True, "message": "Scenario deleted successfully"}
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    success: bool = False
    error: str
    details: Optional[List[str]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Validation failed",
                "details": [
                    "Title must be at least 3 characters",
                    "Scenario must have at least 2 phases",
                ],
            }
        }
    )
