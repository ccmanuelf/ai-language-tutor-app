"""
Scenario-Based Conversation API Endpoints
AI Language Tutor App - RESTful API for Pingo functionality

This module provides API endpoints for managing scenario-based conversations,
allowing users to practice language skills in structured, real-world contexts.

Features:
- List available scenarios by category and difficulty
- Start scenario-based conversations
- Process scenario interactions with progress tracking
- Get scenario progress and completion status
- Integration with conversation management system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from enum import Enum

from app.services.scenario_manager import (
    scenario_manager,
    ScenarioCategory,
    ScenarioDifficulty,
    get_available_scenarios,
    start_scenario,
    process_scenario_interaction,
    get_scenario_status,
    finish_scenario,
)
from app.services.conversation_manager import conversation_manager, LearningFocus
from app.services.auth import get_current_user
from app.models.database import User

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])


# Request/Response Models
class ScenarioListRequest(BaseModel):
    """Request model for listing scenarios"""

    category: Optional[str] = Field(None, description="Filter by category")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty level")
    user_level: Optional[str] = Field(
        "intermediate", description="User's proficiency level"
    )


class StartScenarioRequest(BaseModel):
    """Request model for starting a scenario"""

    scenario_id: str = Field(..., description="ID of the scenario to start")
    language: str = Field("en", description="Target language for learning")
    learning_focus: Optional[str] = Field(
        "conversation", description="Learning focus area"
    )


class ScenarioMessageRequest(BaseModel):
    """Request model for sending messages in scenarios"""

    conversation_id: str = Field(..., description="Conversation ID")
    message: str = Field(..., description="User's message")
    include_speech: Optional[bool] = Field(
        False, description="Include speech synthesis"
    )


class ScenarioResponse(BaseModel):
    """Response model for scenario operations"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# API Endpoints
@router.get("/", response_model=ScenarioResponse)
async def list_scenarios(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    user_level: str = "intermediate",
    current_user: User = Depends(get_current_user),
):
    """
    Get list of available scenarios with optional filtering

    Args:
        category: Filter by scenario category (travel, restaurant, shopping, etc.)
        difficulty: Filter by difficulty level (beginner, intermediate, advanced)
        user_level: User's current proficiency level for recommendations
        current_user: Authenticated user

    Returns:
        List of available scenarios with metadata
    """
    try:
        # Validate category and difficulty if provided
        if category and category not in [cat.value for cat in ScenarioCategory]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Available: {[cat.value for cat in ScenarioCategory]}",
            )

        if difficulty and difficulty not in [diff.value for diff in ScenarioDifficulty]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid difficulty. Available: {[diff.value for diff in ScenarioDifficulty]}",
            )

        # Get scenarios
        scenarios = await get_available_scenarios(
            category=category, difficulty=difficulty
        )

        # Add user-specific recommendations
        for scenario in scenarios:
            scenario["recommended"] = scenario["difficulty"] == user_level or (
                user_level == "beginner" and scenario["difficulty"] == "intermediate"
            )

        logger.info(f"Retrieved {len(scenarios)} scenarios for user {current_user.id}")

        return ScenarioResponse(
            success=True,
            data={
                "scenarios": scenarios,
                "total_count": len(scenarios),
                "categories": [cat.value for cat in ScenarioCategory],
                "difficulties": [diff.value for diff in ScenarioDifficulty],
            },
            message=f"Found {len(scenarios)} available scenarios",
        )

    except Exception as e:
        logger.error(f"Failed to list scenarios for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve scenarios: {str(e)}"
        )


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_details(
    scenario_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific scenario

    Args:
        scenario_id: ID of the scenario
        current_user: Authenticated user

    Returns:
        Detailed scenario information including phases and learning objectives
    """
    try:
        scenario_details = scenario_manager.get_scenario_details(scenario_id)

        if not scenario_details:
            raise HTTPException(
                status_code=404, detail=f"Scenario {scenario_id} not found"
            )

        logger.info(
            f"Retrieved details for scenario {scenario_id} for user {current_user.id}"
        )

        return ScenarioResponse(
            success=True,
            data=scenario_details,
            message="Scenario details retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenario details for {scenario_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve scenario details: {str(e)}"
        )


@router.post("/start", response_model=ScenarioResponse)
async def start_scenario_conversation(
    request: StartScenarioRequest, current_user: User = Depends(get_current_user)
):
    """
    Start a new scenario-based conversation

    Args:
        request: Scenario start request
        current_user: Authenticated user

    Returns:
        Conversation and scenario initialization data
    """
    try:
        # Validate learning focus
        try:
            learning_focus = LearningFocus(request.learning_focus)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid learning focus. Available: {[focus.value for focus in LearningFocus]}",
            )

        # Start conversation with scenario
        conversation_id = await conversation_manager.start_conversation(
            user_id=str(current_user.id),
            language=request.language,
            learning_focus=learning_focus,
            scenario_id=request.scenario_id,
        )

        # Get initial scenario data
        context = conversation_manager.active_conversations[conversation_id]
        scenario_progress = None
        if context.scenario_progress_id:
            scenario_progress = await get_scenario_status(context.scenario_progress_id)

        logger.info(
            f"Started scenario conversation {conversation_id} for user {current_user.id}"
        )

        return ScenarioResponse(
            success=True,
            data={
                "conversation_id": conversation_id,
                "scenario_progress": scenario_progress,
                "language": request.language,
                "learning_focus": request.learning_focus,
                "message": "Scenario conversation started successfully",
            },
            message="Scenario conversation started successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to start scenario conversation for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to start scenario conversation: {str(e)}"
        )


@router.post("/message", response_model=ScenarioResponse)
async def send_scenario_message(
    request: ScenarioMessageRequest, current_user: User = Depends(get_current_user)
):
    """
    Send a message in a scenario conversation

    Args:
        request: Message request
        current_user: Authenticated user

    Returns:
        AI response with scenario progress tracking
    """
    try:
        # Validate conversation belongs to user
        if request.conversation_id not in conversation_manager.active_conversations:
            raise HTTPException(
                status_code=404, detail="Conversation not found or inactive"
            )

        context = conversation_manager.active_conversations[request.conversation_id]
        if context.user_id != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="Access denied to this conversation"
            )

        # Send message and get response
        response = await conversation_manager.send_message(
            conversation_id=request.conversation_id,
            user_message=request.message,
            include_pronunciation_feedback=False,
        )

        logger.info(
            f"Processed scenario message for conversation {request.conversation_id}"
        )

        return ScenarioResponse(
            success=True, data=response, message="Message processed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process scenario message: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process message: {str(e)}"
        )


@router.get("/progress/{conversation_id}", response_model=ScenarioResponse)
async def get_scenario_progress(
    conversation_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get current progress for a scenario conversation

    Args:
        conversation_id: ID of the conversation
        current_user: Authenticated user

    Returns:
        Current scenario progress and statistics
    """
    try:
        # Validate conversation access
        if conversation_id not in conversation_manager.active_conversations:
            raise HTTPException(
                status_code=404, detail="Conversation not found or inactive"
            )

        context = conversation_manager.active_conversations[conversation_id]
        if context.user_id != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="Access denied to this conversation"
            )

        # Get scenario progress
        progress_data = None
        if context.is_scenario_based and context.scenario_progress_id:
            progress_data = await get_scenario_status(context.scenario_progress_id)

        # Get conversation summary
        conversation_summary = await conversation_manager.get_conversation_summary(
            conversation_id
        )

        response_data = {
            "conversation_summary": conversation_summary,
            "scenario_progress": progress_data,
            "is_scenario_based": context.is_scenario_based,
        }

        logger.info(f"Retrieved progress for conversation {conversation_id}")

        return ScenarioResponse(
            success=True, data=response_data, message="Progress retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenario progress: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve progress: {str(e)}"
        )


@router.post("/complete/{conversation_id}", response_model=ScenarioResponse)
async def complete_scenario_conversation(
    conversation_id: str, current_user: User = Depends(get_current_user)
):
    """
    Complete a scenario conversation and get final summary

    Args:
        conversation_id: ID of the conversation to complete
        current_user: Authenticated user

    Returns:
        Final scenario completion summary and achievements
    """
    try:
        # Validate conversation access
        if conversation_id not in conversation_manager.active_conversations:
            raise HTTPException(
                status_code=404, detail="Conversation not found or inactive"
            )

        context = conversation_manager.active_conversations[conversation_id]
        if context.user_id != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="Access denied to this conversation"
            )

        # Complete scenario if applicable
        scenario_summary = None
        if context.is_scenario_based and context.scenario_progress_id:
            try:
                scenario_summary = await finish_scenario(context.scenario_progress_id)
            except Exception as e:
                logger.warning(f"Failed to complete scenario: {e}")

        # End conversation
        conversation_summary = await conversation_manager.end_conversation(
            conversation_id=conversation_id, save_learning_progress=True
        )

        response_data = {
            "conversation_summary": conversation_summary,
            "scenario_summary": scenario_summary,
            "completion_time": datetime.now().isoformat(),
        }

        logger.info(
            f"Completed scenario conversation {conversation_id} for user {current_user.id}"
        )

        return ScenarioResponse(
            success=True,
            data=response_data,
            message="Scenario conversation completed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete scenario conversation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to complete conversation: {str(e)}"
        )


@router.get("/categories", response_model=ScenarioResponse)
async def get_scenario_categories():
    """
    Get list of available scenario categories

    Returns:
        List of scenario categories with descriptions
    """
    try:
        categories = [
            {
                "id": cat.value,
                "name": cat.value.replace("_", " ").title(),
                "description": _get_category_description(cat),
            }
            for cat in ScenarioCategory
        ]

        return ScenarioResponse(
            success=True,
            data={"categories": categories},
            message="Categories retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get scenario categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve categories: {str(e)}"
        )


# Universal Template Endpoints
@router.get("/templates", response_model=ScenarioResponse)
async def get_universal_templates(
    tier: Optional[int] = None, current_user: User = Depends(get_current_user)
):
    """Get all available universal scenario templates"""
    try:
        templates = scenario_manager.get_universal_templates(tier=tier)

        return ScenarioResponse(
            success=True,
            message=f"Retrieved {len(templates)} universal templates"
            + (f" for tier {tier}" if tier else ""),
            data={
                "templates": templates,
                "total_count": len(templates),
                "tier_filter": tier,
            },
        )
    except Exception as e:
        logger.error(f"Failed to get universal templates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve templates: {str(e)}"
        )


@router.get("/templates/tier1", response_model=ScenarioResponse)
async def get_tier1_scenarios(current_user: User = Depends(get_current_user)):
    """Get all Tier 1 (essential) scenario templates"""
    try:
        tier1_scenarios = scenario_manager.get_tier1_scenarios()

        return ScenarioResponse(
            success=True,
            message=f"Retrieved {len(tier1_scenarios)} Tier 1 essential scenarios",
            data={
                "tier1_scenarios": tier1_scenarios,
                "total_count": len(tier1_scenarios),
                "tier": 1,
                "description": "Essential daily interaction scenarios for language learning",
            },
        )
    except Exception as e:
        logger.error(f"Failed to get Tier 1 scenarios: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve Tier 1 scenarios: {str(e)}"
        )


class CreateFromTemplateRequest(BaseModel):
    """Request model for creating scenario from template"""

    template_id: str = Field(..., description="Universal template ID")
    difficulty: str = Field(
        ..., description="Difficulty level (beginner/intermediate/advanced)"
    )
    variation_id: Optional[str] = Field(
        None, description="Specific variation ID (optional)"
    )
    user_role: Optional[str] = Field(
        "student", description="User's role in the scenario"
    )
    ai_role: Optional[str] = Field("teacher", description="AI's role in the scenario")


@router.post("/templates/create", response_model=ScenarioResponse)
async def create_scenario_from_template(
    request: CreateFromTemplateRequest, current_user: User = Depends(get_current_user)
):
    """Create a new scenario instance from a universal template"""
    try:
        # Validate difficulty
        try:
            difficulty = ScenarioDifficulty(request.difficulty.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid difficulty level: {request.difficulty}. Must be beginner, intermediate, or advanced",
            )

        # Import ConversationRole
        from app.services.scenario_manager import ConversationRole

        # Validate roles
        try:
            user_role = ConversationRole(request.user_role.lower())
            ai_role = ConversationRole(request.ai_role.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid role. Available roles: customer, service_provider, friend, colleague, student, teacher, tourist, local",
            )

        # Create scenario from template
        scenario = scenario_manager.create_scenario_from_template(
            template_id=request.template_id,
            difficulty=difficulty,
            user_role=user_role,
            ai_role=ai_role,
            variation_id=request.variation_id,
        )

        if not scenario:
            raise HTTPException(
                status_code=404, detail=f"Template not found: {request.template_id}"
            )

        # Get scenario details
        scenario_details = scenario_manager.get_scenario_details(scenario.scenario_id)

        return ScenarioResponse(
            success=True,
            message=f"Created scenario from template: {scenario.name}",
            data={
                "scenario": scenario_details,
                "template_id": request.template_id,
                "variation_id": request.variation_id,
                "created_at": datetime.utcnow().isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create scenario from template: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create scenario: {str(e)}"
        )


@router.get("/category/{category_name}", response_model=ScenarioResponse)
async def get_scenarios_by_category(
    category_name: str, current_user: User = Depends(get_current_user)
):
    """Get all scenarios and templates for a specific category"""
    try:
        # Validate category
        try:
            category = ScenarioCategory(category_name.lower())
        except ValueError:
            available_categories = [cat.value for cat in ScenarioCategory]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category_name}. Available: {', '.join(available_categories)}",
            )

        category_data = scenario_manager.get_scenarios_by_category(category)

        return ScenarioResponse(
            success=True,
            message=f"Retrieved scenarios for category: {category.value}",
            data=category_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenarios by category: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve category scenarios: {str(e)}"
        )


def _get_category_description(category: ScenarioCategory) -> str:
    """Get description for a scenario category"""
    descriptions = {
        ScenarioCategory.TRAVEL: "Practice conversations for hotels, airports, and tourist situations",
        ScenarioCategory.RESTAURANT: "Learn to order food, make reservations, and dine out",
        ScenarioCategory.SHOPPING: "Practice buying clothes, asking for prices, and retail interactions",
        ScenarioCategory.BUSINESS: "Professional conversations, meetings, and workplace interactions",
        ScenarioCategory.HEALTHCARE: "Medical appointments, pharmacy visits, and health-related conversations",
        ScenarioCategory.SOCIAL: "Social gatherings, making friends, and casual conversations",
        ScenarioCategory.EMERGENCY: "Emergency situations and urgent communication needs",
        ScenarioCategory.EDUCATION: "School, university, and educational environment conversations",
        ScenarioCategory.DAILY_LIFE: "Everyday interactions like banking, post office, and utilities",
        ScenarioCategory.HOBBIES: "Conversations about interests, sports, and recreational activities",
    }
    return descriptions.get(
        category, "Practice structured conversations in this context"
    )


# Include router in main app
def get_scenarios_router():
    """Get the scenarios router for inclusion in main app"""
    return router
