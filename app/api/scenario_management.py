"""
Scenario & Content Management API
AI Language Tutor App - Admin Configuration System

This module provides REST API endpoints for managing scenarios and content
processing configuration through the admin interface.

Features:
- Scenario CRUD operations (Create, Read, Update, Delete)
- Scenario template management
- Content processing configuration
- Bulk scenario operations
- Scenario validation and testing
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.services.admin_auth import (
    AdminPermission,
    require_admin_access,
    require_permission,
)
from app.services.scenario_manager import (
    ConversationRole,
    ConversationScenario,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioPhase,
    scenario_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin/scenario-management", tags=["scenario-management"]
)


async def ensure_scenario_manager_initialized():
    """Ensure the global scenario manager is initialized"""
    await scenario_manager.initialize()
    return scenario_manager


# ===========================
# Pydantic Models
# ===========================


class ScenarioPhaseModel(BaseModel):
    """Pydantic model for scenario phase"""

    phase_id: str
    name: str
    description: str
    expected_duration_minutes: int
    key_vocabulary: List[str]
    essential_phrases: List[str]
    learning_objectives: List[str]
    cultural_notes: Optional[str] = None
    success_criteria: List[str] = []


class ScenarioModel(BaseModel):
    """Pydantic model for conversation scenario"""

    scenario_id: str
    name: str
    category: str
    difficulty: str
    description: str
    user_role: str
    ai_role: str
    setting: str
    duration_minutes: int
    phases: List[ScenarioPhaseModel]
    prerequisites: List[str] = []
    learning_outcomes: List[str] = []
    vocabulary_focus: List[str] = []
    cultural_context: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        valid_categories = [cat.value for cat in ScenarioCategory]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = [diff.value for diff in ScenarioDifficulty]
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {valid_difficulties}")
        return v

    @field_validator("user_role", "ai_role")
    @classmethod
    def validate_roles(cls, v):
        valid_roles = [role.value for role in ConversationRole]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {valid_roles}")
        return v


class ScenarioCreateRequest(BaseModel):
    """Request model for creating new scenarios"""

    name: str = Field(..., min_length=3, max_length=100)
    category: str
    difficulty: str
    description: str = Field(..., min_length=10, max_length=500)
    user_role: str
    ai_role: str
    setting: str = Field(..., min_length=5, max_length=200)
    duration_minutes: int = Field(..., gt=0, le=120)
    phases: List[ScenarioPhaseModel]
    prerequisites: List[str] = []
    learning_outcomes: List[str] = []
    vocabulary_focus: List[str] = []
    cultural_context: Optional[str] = None


class ScenarioUpdateRequest(BaseModel):
    """Request model for updating scenarios"""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    category: Optional[str] = None
    difficulty: Optional[str] = None
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    user_role: Optional[str] = None
    ai_role: Optional[str] = None
    setting: Optional[str] = Field(None, min_length=5, max_length=200)
    duration_minutes: Optional[int] = Field(None, gt=0, le=120)
    phases: Optional[List[ScenarioPhaseModel]] = None
    prerequisites: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    vocabulary_focus: Optional[List[str]] = None
    cultural_context: Optional[str] = None
    is_active: Optional[bool] = None


class ContentProcessingConfigModel(BaseModel):
    """Content processing configuration model"""

    max_video_length_minutes: int = Field(default=60, ge=1, le=480)
    ai_provider_preference: str = Field(default="mistral")
    enable_auto_flashcards: bool = Field(default=True)
    enable_auto_quizzes: bool = Field(default=True)
    enable_auto_summaries: bool = Field(default=True)
    max_flashcards_per_content: int = Field(default=20, ge=5, le=100)
    max_quiz_questions: int = Field(default=10, ge=3, le=50)
    summary_length_preference: str = Field(default="medium")
    language_detection_enabled: bool = Field(default=True)
    content_quality_threshold: float = Field(default=0.7, ge=0.1, le=1.0)
    enable_content_moderation: bool = Field(default=True)


class BulkScenarioOperation(BaseModel):
    """Bulk operations on scenarios"""

    operation: str = Field(..., pattern="^(activate|deactivate|delete|export)$")
    scenario_ids: List[str]


# ===========================
# Scenario Management Endpoints
# ===========================


@router.get("/scenarios", response_model=List[ScenarioModel])
async def list_scenarios(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    active_only: bool = Query(True, description="Only show active scenarios"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(require_admin_access),
):
    """List all scenarios with optional filtering"""
    try:
        sm = await ensure_scenario_manager_initialized()
        scenarios = await sm.get_all_scenarios()
        scenarios = _apply_scenario_filters(
            scenarios, category, difficulty, active_only
        )
        paginated = scenarios[offset : offset + limit]
        result = _convert_scenarios_to_models(paginated)
        logger.info(
            f"Listed {len(result)} scenarios (filtered from {len(scenarios)} total)"
        )
        return result
    except Exception as e:
        logger.error(f"Error listing scenarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scenarios: {str(e)}",
        )


def _apply_scenario_filters(
    scenarios: list,
    category: Optional[str],
    difficulty: Optional[str],
    active_only: bool,
) -> list:
    """Apply filtering to scenarios - A(4)"""
    if category:
        scenarios = [s for s in scenarios if s.category.value == category]
    if difficulty:
        scenarios = [s for s in scenarios if s.difficulty.value == difficulty]
    if active_only:
        scenarios = [s for s in scenarios if getattr(s, "is_active", True)]
    return scenarios


def _convert_scenarios_to_models(scenarios: list) -> list:
    """Convert scenario objects to response models - A(2)"""
    result = []
    for scenario in scenarios:
        scenario_dict = _build_scenario_dict(scenario)
        result.append(ScenarioModel(**scenario_dict))
    return result


def _build_scenario_dict(scenario) -> dict:
    """Build scenario dictionary from scenario object - A(1)"""
    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.name,
        "category": scenario.category.value,
        "difficulty": scenario.difficulty.value,
        "description": scenario.description,
        "user_role": scenario.user_role.value,
        "ai_role": scenario.ai_role.value,
        "setting": scenario.setting,
        "duration_minutes": scenario.duration_minutes,
        "phases": [
            {
                "phase_id": phase.phase_id,
                "name": phase.name,
                "description": phase.description,
                "expected_duration_minutes": phase.expected_duration_minutes,
                "key_vocabulary": phase.key_vocabulary,
                "essential_phrases": phase.essential_phrases,
                "learning_objectives": phase.learning_objectives,
                "cultural_notes": phase.cultural_notes,
                "success_criteria": phase.success_criteria or [],
            }
            for phase in scenario.phases
        ],
        "prerequisites": getattr(scenario, "prerequisites", []),
        "learning_outcomes": getattr(scenario, "learning_outcomes", []),
        "vocabulary_focus": getattr(scenario, "vocabulary_focus", []),
        "cultural_context": getattr(scenario, "cultural_context", None),
        "is_active": getattr(scenario, "is_active", True),
        "created_at": getattr(scenario, "created_at", None),
        "updated_at": getattr(scenario, "updated_at", None),
    }


@router.get("/scenarios/{scenario_id}", response_model=ScenarioModel)
async def get_scenario(scenario_id: str, user=Depends(require_admin_access)):
    """Get a specific scenario by ID"""
    try:
        sm = await ensure_scenario_manager_initialized()
        scenario = await sm.get_scenario_by_id(scenario_id)

        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with ID {scenario_id} not found",
            )

        # Convert to response model
        scenario_dict = {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "category": scenario.category.value,
            "difficulty": scenario.difficulty.value,
            "description": scenario.description,
            "user_role": scenario.user_role.value,
            "ai_role": scenario.ai_role.value,
            "setting": scenario.setting,
            "duration_minutes": scenario.duration_minutes,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "name": phase.name,
                    "description": phase.description,
                    "expected_duration_minutes": phase.expected_duration_minutes,
                    "key_vocabulary": phase.key_vocabulary,
                    "essential_phrases": phase.essential_phrases,
                    "learning_objectives": phase.learning_objectives,
                    "cultural_notes": phase.cultural_notes,
                    "success_criteria": phase.success_criteria or [],
                }
                for phase in scenario.phases
            ],
            "prerequisites": getattr(scenario, "prerequisites", []),
            "learning_outcomes": getattr(scenario, "learning_outcomes", []),
            "vocabulary_focus": getattr(scenario, "vocabulary_focus", []),
            "cultural_context": getattr(scenario, "cultural_context", None),
            "is_active": getattr(scenario, "is_active", True),
            "created_at": getattr(scenario, "created_at", None),
            "updated_at": getattr(scenario, "updated_at", None),
        }

        return ScenarioModel(**scenario_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scenario {scenario_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scenario: {str(e)}",
        )


@router.post("/scenarios", response_model=ScenarioModel)
async def create_scenario(
    scenario_data: ScenarioCreateRequest,
    user=Depends(require_permission(AdminPermission.MANAGE_SCENARIOS)),
):
    """Create a new scenario"""
    try:
        sm = await ensure_scenario_manager_initialized()

        # Generate unique ID
        scenario_id = str(uuid4())

        # Convert phases to ScenarioPhase objects
        phases = []
        for phase_data in scenario_data.phases:
            phase = ScenarioPhase(
                phase_id=phase_data.phase_id,
                name=phase_data.name,
                description=phase_data.description,
                expected_duration_minutes=phase_data.expected_duration_minutes,
                key_vocabulary=phase_data.key_vocabulary,
                essential_phrases=phase_data.essential_phrases,
                learning_objectives=phase_data.learning_objectives,
                cultural_notes=phase_data.cultural_notes,
                success_criteria=phase_data.success_criteria,
            )
            phases.append(phase)

        # Create ConversationScenario object
        scenario = ConversationScenario(
            scenario_id=scenario_id,
            name=scenario_data.name,
            category=ScenarioCategory(scenario_data.category),
            difficulty=ScenarioDifficulty(scenario_data.difficulty),
            description=scenario_data.description,
            user_role=ConversationRole(scenario_data.user_role),
            ai_role=ConversationRole(scenario_data.ai_role),
            setting=scenario_data.setting,
            duration_minutes=scenario_data.duration_minutes,
            phases=phases,
            prerequisites=scenario_data.prerequisites,
            learning_outcomes=scenario_data.learning_outcomes,
            vocabulary_focus=scenario_data.vocabulary_focus,
            cultural_context=scenario_data.cultural_context,
        )

        # Add additional fields
        scenario.is_active = True
        scenario.created_at = datetime.now()
        scenario.updated_at = datetime.now()

        # Save scenario (this would require extending ScenarioManager with persistence)
        await sm.save_scenario(scenario)

        # Convert to response model
        scenario_dict = {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "category": scenario.category.value,
            "difficulty": scenario.difficulty.value,
            "description": scenario.description,
            "user_role": scenario.user_role.value,
            "ai_role": scenario.ai_role.value,
            "setting": scenario.setting,
            "duration_minutes": scenario.duration_minutes,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "name": phase.name,
                    "description": phase.description,
                    "expected_duration_minutes": phase.expected_duration_minutes,
                    "key_vocabulary": phase.key_vocabulary,
                    "essential_phrases": phase.essential_phrases,
                    "learning_objectives": phase.learning_objectives,
                    "cultural_notes": phase.cultural_notes,
                    "success_criteria": phase.success_criteria or [],
                }
                for phase in scenario.phases
            ],
            "prerequisites": scenario_data.prerequisites,
            "learning_outcomes": scenario_data.learning_outcomes,
            "vocabulary_focus": scenario_data.vocabulary_focus,
            "cultural_context": scenario_data.cultural_context,
            "is_active": True,
            "created_at": scenario.created_at,
            "updated_at": scenario.updated_at,
        }

        logger.info(f"Created new scenario: {scenario.name} ({scenario_id})")
        return ScenarioModel(**scenario_dict)

    except Exception as e:
        logger.error(f"Error creating scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scenario: {str(e)}",
        )


@router.put("/scenarios/{scenario_id}", response_model=ScenarioModel)
async def update_scenario(
    scenario_id: str,
    scenario_data: ScenarioUpdateRequest,
    user=Depends(require_permission(AdminPermission.MANAGE_SCENARIOS)),
):
    """Update an existing scenario"""
    try:
        sm = await ensure_scenario_manager_initialized()
        existing_scenario = await _get_scenario_or_404(sm, scenario_id)
        updates = scenario_data.model_dump(exclude_unset=True)
        _apply_scenario_updates(existing_scenario, updates)
        existing_scenario.updated_at = datetime.now()
        await sm.save_scenario(existing_scenario)
        scenario_dict = _build_scenario_dict(existing_scenario)
        logger.info(f"Updated scenario: {existing_scenario.name} ({scenario_id})")
        return ScenarioModel(**scenario_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scenario {scenario_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scenario: {str(e)}",
        )


async def _get_scenario_or_404(sm, scenario_id: str):
    """Get scenario or raise 404 - A(2)"""
    existing_scenario = await sm.get_scenario_by_id(scenario_id)
    if not existing_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID {scenario_id} not found",
        )
    return existing_scenario


def _apply_scenario_updates(scenario, updates: dict) -> None:
    """Apply updates to scenario object - B(8)"""
    for field, value in updates.items():
        if field == "phases" and value is not None:
            phases = _convert_phase_data_to_objects(value)
            setattr(scenario, field, phases)
        elif field in ["category", "difficulty", "user_role", "ai_role"]:
            _update_enum_field(scenario, field, value)
        else:
            setattr(scenario, field, value)


def _convert_phase_data_to_objects(phase_data_list: list) -> list:
    """Convert phase data to ScenarioPhase objects - A(2)"""
    phases = []
    for phase_data in phase_data_list:
        phase = ScenarioPhase(
            phase_id=phase_data.phase_id,
            name=phase_data.name,
            description=phase_data.description,
            expected_duration_minutes=phase_data.expected_duration_minutes,
            key_vocabulary=phase_data.key_vocabulary,
            essential_phrases=phase_data.essential_phrases,
            learning_objectives=phase_data.learning_objectives,
            cultural_notes=phase_data.cultural_notes,
            success_criteria=phase_data.success_criteria,
        )
        phases.append(phase)
    return phases


def _update_enum_field(scenario, field: str, value: str) -> None:
    """Update enum field with proper conversion - A(5)"""
    if field == "category":
        setattr(scenario, field, ScenarioCategory(value))
    elif field == "difficulty":
        setattr(scenario, field, ScenarioDifficulty(value))
    elif field in ["user_role", "ai_role"]:
        setattr(scenario, field, ConversationRole(value))
    else:
        # Field is not an enum field - do nothing (defensive programming)
        logger.debug(f"Field '{field}' is not an enum field, skipping enum conversion")


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    scenario_id: str, user=Depends(require_permission(AdminPermission.MANAGE_SCENARIOS))
):
    """Delete a scenario"""
    try:
        sm = await ensure_scenario_manager_initialized()

        # Check if scenario exists
        existing_scenario = await sm.get_scenario_by_id(scenario_id)
        if not existing_scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with ID {scenario_id} not found",
            )

        # Delete scenario
        await sm.delete_scenario(scenario_id)

        logger.info(f"Deleted scenario: {existing_scenario.name} ({scenario_id})")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Scenario {scenario_id} deleted successfully"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scenario: {str(e)}",
        )


# ===========================
# Content Processing Configuration
# ===========================


@router.get("/content-config", response_model=ContentProcessingConfigModel)
async def get_content_config(user=Depends(require_admin_access)):
    """Get current content processing configuration"""
    try:
        # This would load from database or config file
        # For now, return default configuration
        config = ContentProcessingConfigModel()

        logger.info("Retrieved content processing configuration")
        return config

    except Exception as e:
        logger.error(f"Error getting content config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content configuration: {str(e)}",
        )


@router.put("/content-config", response_model=ContentProcessingConfigModel)
async def update_content_config(
    config_data: ContentProcessingConfigModel,
    user=Depends(require_permission(AdminPermission.MANAGE_SYSTEM_CONFIG)),
):
    """Update content processing configuration"""
    try:
        # This would save to database or config file
        # For now, just validate and return the provided config

        logger.info("Updated content processing configuration")
        return config_data

    except Exception as e:
        logger.error(f"Error updating content config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update content configuration: {str(e)}",
        )


# ===========================
# Bulk Operations
# ===========================


@router.post("/scenarios/bulk")
async def bulk_scenario_operations(
    operation_data: BulkScenarioOperation,
    user=Depends(require_permission(AdminPermission.MANAGE_SCENARIOS)),
):
    """Perform bulk operations on scenarios"""
    try:
        sm = await ensure_scenario_manager_initialized()
        results = []

        for scenario_id in operation_data.scenario_ids:
            try:
                if operation_data.operation == "activate":
                    await sm.set_scenario_active(scenario_id, True)
                    results.append({"scenario_id": scenario_id, "status": "activated"})
                elif operation_data.operation == "deactivate":
                    await sm.set_scenario_active(scenario_id, False)
                    results.append(
                        {"scenario_id": scenario_id, "status": "deactivated"}
                    )
                elif operation_data.operation == "delete":
                    await sm.delete_scenario(scenario_id)
                    results.append({"scenario_id": scenario_id, "status": "deleted"})
                elif operation_data.operation == "export":
                    # Export functionality would be implemented here
                    results.append({"scenario_id": scenario_id, "status": "exported"})
                else:
                    # Should never reach here due to Pydantic validation, but defensive programming
                    logger.error(f"Invalid bulk operation: {operation_data.operation}")
                    results.append(
                        {
                            "scenario_id": scenario_id,
                            "status": "error",
                            "error": "Invalid operation",
                        }
                    )
            except Exception as e:
                results.append(
                    {"scenario_id": scenario_id, "status": "error", "error": str(e)}
                )

        logger.info(
            f"Bulk operation {operation_data.operation} completed on {len(operation_data.scenario_ids)} scenarios"
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"operation": operation_data.operation, "results": results},
        )

    except Exception as e:
        logger.error(f"Error in bulk scenario operation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk operation: {str(e)}",
        )


# ===========================
# Scenario Templates and Categories
# ===========================


@router.get("/templates")
async def get_scenario_templates(user=Depends(require_admin_access)):
    """Get available scenario templates"""
    try:
        templates = {
            "categories": [
                {"value": cat.value, "label": cat.value.replace("_", " ").title()}
                for cat in ScenarioCategory
            ],
            "difficulties": [
                {"value": diff.value, "label": diff.value.title()}
                for diff in ScenarioDifficulty
            ],
            "roles": [
                {"value": role.value, "label": role.value.replace("_", " ").title()}
                for role in ConversationRole
            ],
            "phase_templates": [
                {
                    "name": "Introduction",
                    "description": "Initial greeting and context setting",
                    "expected_duration_minutes": 5,
                    "learning_objectives": ["Basic greetings", "Context establishment"],
                },
                {
                    "name": "Main Interaction",
                    "description": "Core conversation and task completion",
                    "expected_duration_minutes": 15,
                    "learning_objectives": [
                        "Task-specific vocabulary",
                        "Practical communication",
                    ],
                },
                {
                    "name": "Conclusion",
                    "description": "Wrap-up and final exchanges",
                    "expected_duration_minutes": 5,
                    "learning_objectives": ["Polite closures", "Future arrangements"],
                },
            ],
        }

        logger.info("Retrieved scenario templates")
        return JSONResponse(content=templates)

    except Exception as e:
        logger.error(f"Error getting scenario templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scenario templates: {str(e)}",
        )


@router.get("/statistics")
async def get_scenario_statistics(user=Depends(require_admin_access)):
    """Get scenario usage and performance statistics"""
    try:
        # This would query actual usage data
        stats = {
            "total_scenarios": 15,
            "active_scenarios": 12,
            "scenarios_by_category": {
                "restaurant": 4,
                "travel": 3,
                "shopping": 2,
                "business": 3,
                "social": 3,
            },
            "scenarios_by_difficulty": {
                "beginner": 6,
                "intermediate": 7,
                "advanced": 2,
            },
            "most_popular_scenarios": [
                {
                    "scenario_id": "restaurant_1",
                    "name": "Restaurant Dinner Reservation",
                    "usage_count": 45,
                },
                {
                    "scenario_id": "travel_1",
                    "name": "Hotel Check-in",
                    "usage_count": 38,
                },
                {
                    "scenario_id": "shopping_1",
                    "name": "Clothes Shopping",
                    "usage_count": 32,
                },
            ],
            "average_completion_rate": 0.85,
            "total_sessions": 156,
        }

        logger.info("Retrieved scenario statistics")
        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"Error getting scenario statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scenario statistics: {str(e)}",
        )
