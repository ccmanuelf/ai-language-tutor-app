"""
Scenario Builder API Endpoints
AI Language Tutor App - Session 131

RESTful API for user-generated scenario management.
Enables users to create, edit, share, and manage custom scenarios.

Endpoints:
- GET    /api/v1/scenario-builder/templates
- POST   /api/v1/scenario-builder/scenarios
- POST   /api/v1/scenario-builder/scenarios/from-template
- GET    /api/v1/scenario-builder/scenarios/{scenario_id}
- PUT    /api/v1/scenario-builder/scenarios/{scenario_id}
- DELETE /api/v1/scenario-builder/scenarios/{scenario_id}
- GET    /api/v1/scenario-builder/my-scenarios
- GET    /api/v1/scenario-builder/public-scenarios
- POST   /api/v1/scenario-builder/scenarios/{scenario_id}/duplicate
- PATCH  /api/v1/scenario-builder/scenarios/{scenario_id}/visibility
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import require_auth
from app.database.config import get_db_session
from app.models.simple_user import SimpleUser
from app.schemas.scenario_builder_schemas import (
    CreateFromTemplateRequest,
    CreateScenarioRequest,
    DuplicateScenarioRequest,
    ErrorResponse,
    ScenarioCreateResponse,
    ScenarioDeleteResponse,
    ScenarioListResponse,
    ScenarioResponse,
    TemplateListResponse,
    TemplateResponse,
    UpdateScenarioRequest,
    UpdateVisibilityRequest,
)
from app.services.scenario_builder_service import ScenarioBuilderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scenario-builder", tags=["Scenario Builder"])


# ============================================================================
# TEMPLATES
# ============================================================================


@router.get(
    "/templates",
    response_model=TemplateListResponse,
    summary="Get all scenario templates",
    description="Retrieve all available scenario templates (1 per category)",
)
async def get_templates(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get all scenario templates.

    Templates provide pre-built scenario structures that users can
    customize to create their own scenarios quickly.

    Returns:
        TemplateListResponse with all 10 templates
    """
    try:
        service = ScenarioBuilderService(db)
        templates = await service.get_scenario_templates()

        # Convert to response format
        template_responses = [
            TemplateResponse(
                template_id=t["template_id"],
                title=t["title"],
                description=t["description"],
                category=t["category"],
                difficulty=t["difficulty"],
                estimated_duration=t["estimated_duration"],
                phase_count=len(t["phases"]),
                preview_vocabulary=t["vocabulary_focus"][:5]
                if t.get("vocabulary_focus")
                else [],
            )
            for t in templates
        ]

        return TemplateListResponse(
            templates=template_responses, count=len(template_responses)
        )

    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")


# ============================================================================
# CREATE SCENARIOS
# ============================================================================


@router.post(
    "/scenarios",
    response_model=ScenarioCreateResponse,
    status_code=201,
    summary="Create new custom scenario",
    description="Create a new scenario from scratch with custom content",
    responses={
        201: {"description": "Scenario created successfully"},
        400: {"model": ErrorResponse, "description": "Validation failed"},
        401: {"description": "Authentication required"},
    },
)
async def create_scenario(
    request: CreateScenarioRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Create a new custom scenario.

    The scenario must have:
    - 2-6 phases
    - At least 5 total vocabulary words
    - At least 5 total essential phrases
    - Valid category and difficulty

    Args:
        request: CreateScenarioRequest with scenario details

    Returns:
        ScenarioCreateResponse with new scenario_id
    """
    try:
        service = ScenarioBuilderService(db)

        # Validate scenario data
        is_valid, errors = service.validate_scenario_data(request.model_dump())
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Scenario validation failed",
                    "details": errors,
                },
            )

        # Create scenario
        scenario = await service.create_scenario(
            user_id=current_user.id, scenario_data=request.model_dump()
        )

        logger.info(f"User {current_user.id} created scenario {scenario.scenario_id}")

        return ScenarioCreateResponse(
            success=True,
            scenario_id=scenario.scenario_id,
            message="Scenario created successfully",
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating scenario: {e}")
        raise HTTPException(status_code=500, detail="Failed to create scenario")


@router.post(
    "/scenarios/from-template",
    response_model=ScenarioCreateResponse,
    status_code=201,
    summary="Create scenario from template",
    description="Create a scenario using a pre-built template with optional customization",
    responses={
        201: {"description": "Scenario created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid template"},
        401: {"description": "Authentication required"},
    },
)
async def create_from_template(
    request: CreateFromTemplateRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Create scenario from a template.

    Templates provide a starting point that can be customized with:
    - Custom title
    - Modified description
    - Adjusted difficulty level

    Args:
        request: CreateFromTemplateRequest with template_id and customization

    Returns:
        ScenarioCreateResponse with new scenario_id
    """
    try:
        service = ScenarioBuilderService(db)

        scenario = await service.create_from_template(
            template_id=request.template_id,
            user_id=current_user.id,
            customization=request.customization,
        )

        logger.info(
            f"User {current_user.id} created scenario from template {request.template_id}"
        )

        return ScenarioCreateResponse(
            success=True,
            scenario_id=scenario.scenario_id,
            message=f"Scenario created from template successfully",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating from template: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create scenario from template"
        )


# ============================================================================
# READ SCENARIOS
# ============================================================================


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Get scenario details",
    description="Retrieve full details of a specific scenario",
    responses={
        200: {"description": "Scenario found"},
        404: {"description": "Scenario not found or not accessible"},
        401: {"description": "Authentication required"},
    },
)
async def get_scenario(
    scenario_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get scenario by ID.

    Users can access:
    - Their own scenarios
    - Public scenarios
    - System scenarios

    Args:
        scenario_id: Unique scenario identifier

    Returns:
        ScenarioResponse with full scenario details including phases
    """
    try:
        service = ScenarioBuilderService(db)
        scenario = await service.get_scenario(scenario_id, current_user.id)

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Convert to response format
        scenario_dict = scenario.to_dict()
        return ScenarioResponse(**scenario_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scenario")


@router.get(
    "/my-scenarios",
    response_model=ScenarioListResponse,
    summary="Get user's scenarios",
    description="Retrieve all scenarios created by the current user",
)
async def get_my_scenarios(
    include_public: bool = Query(
        False, description="Also include public scenarios from other users"
    ),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get scenarios created by the current user.

    Optionally includes public scenarios from other users for browsing.

    Args:
        include_public: Whether to include public scenarios

    Returns:
        ScenarioListResponse with user's scenarios
    """
    try:
        service = ScenarioBuilderService(db)
        scenarios = await service.get_user_scenarios(
            user_id=current_user.id, include_public=include_public
        )

        scenario_responses = [ScenarioResponse(**s.to_dict()) for s in scenarios]

        return ScenarioListResponse(
            scenarios=scenario_responses, count=len(scenario_responses)
        )

    except Exception as e:
        logger.error(f"Error fetching user scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch scenarios")


@router.get(
    "/public-scenarios",
    response_model=ScenarioListResponse,
    summary="Get public scenarios",
    description="Browse publicly shared scenarios from all users",
)
async def get_public_scenarios(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Get publicly shared scenarios.

    Allows users to discover and use scenarios created by the community.

    Args:
        category: Optional category filter
        difficulty: Optional difficulty filter (beginner/intermediate/advanced)

    Returns:
        ScenarioListResponse with public scenarios
    """
    try:
        service = ScenarioBuilderService(db)
        scenarios = await service.get_public_scenarios(
            category=category, difficulty=difficulty
        )

        scenario_responses = [ScenarioResponse(**s.to_dict()) for s in scenarios]

        return ScenarioListResponse(
            scenarios=scenario_responses, count=len(scenario_responses)
        )

    except Exception as e:
        logger.error(f"Error fetching public scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch public scenarios")


# ============================================================================
# UPDATE SCENARIOS
# ============================================================================


@router.put(
    "/scenarios/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Update scenario",
    description="Update an existing scenario (user must own it)",
    responses={
        200: {"description": "Scenario updated successfully"},
        403: {"description": "Cannot edit this scenario"},
        404: {"description": "Scenario not found"},
        401: {"description": "Authentication required"},
    },
)
async def update_scenario(
    scenario_id: str,
    request: UpdateScenarioRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Update an existing scenario.

    Only the scenario owner can update it.
    System scenarios cannot be edited.

    Args:
        scenario_id: Scenario identifier
        request: UpdateScenarioRequest with fields to update

    Returns:
        ScenarioResponse with updated scenario
    """
    try:
        service = ScenarioBuilderService(db)

        # Check ownership and edit permission
        if not service.can_edit_scenario(current_user.id, scenario_id):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to edit this scenario",
            )

        # Update scenario
        scenario = await service.update_scenario(
            scenario_id=scenario_id,
            user_id=current_user.id,
            updates=request.model_dump(exclude_unset=True),
        )

        logger.info(f"User {current_user.id} updated scenario {scenario_id}")

        return ScenarioResponse(**scenario.to_dict())

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update scenario")


@router.patch(
    "/scenarios/{scenario_id}/visibility",
    response_model=ScenarioResponse,
    summary="Update scenario visibility",
    description="Make a scenario public or private",
    responses={
        200: {"description": "Visibility updated"},
        403: {"description": "Not your scenario"},
        404: {"description": "Scenario not found"},
        401: {"description": "Authentication required"},
    },
)
async def update_visibility(
    scenario_id: str,
    request: UpdateVisibilityRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Toggle scenario visibility (public/private).

    Public scenarios can be viewed and duplicated by all users.
    Private scenarios are only accessible to the owner.

    Args:
        scenario_id: Scenario identifier
        request: UpdateVisibilityRequest with is_public flag

    Returns:
        ScenarioResponse with updated scenario
    """
    try:
        service = ScenarioBuilderService(db)

        # Check ownership
        if not service.user_owns_scenario(current_user.id, scenario_id):
            raise HTTPException(status_code=403, detail="You don't own this scenario")

        # Update visibility
        scenario = await service.update_scenario(
            scenario_id=scenario_id,
            user_id=current_user.id,
            updates={"is_public": request.is_public},
        )

        visibility = "public" if request.is_public else "private"
        logger.info(f"User {current_user.id} made scenario {scenario_id} {visibility}")

        return ScenarioResponse(**scenario.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating visibility for {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update visibility")


# ============================================================================
# DELETE SCENARIOS
# ============================================================================


@router.delete(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDeleteResponse,
    summary="Delete scenario",
    description="Delete a scenario (user must own it, cannot delete system scenarios)",
    responses={
        200: {"description": "Scenario deleted"},
        403: {"description": "Cannot delete this scenario"},
        404: {"description": "Scenario not found"},
        401: {"description": "Authentication required"},
    },
)
async def delete_scenario(
    scenario_id: str,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Delete a scenario.

    Only the scenario owner can delete it.
    System scenarios cannot be deleted.
    Deleting a scenario also deletes all its phases (cascade).

    Args:
        scenario_id: Scenario identifier

    Returns:
        ScenarioDeleteResponse confirming deletion
    """
    try:
        service = ScenarioBuilderService(db)

        # Check ownership and edit permission
        if not service.can_edit_scenario(current_user.id, scenario_id):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this scenario",
            )

        # Delete scenario
        success = await service.delete_scenario(
            scenario_id=scenario_id, user_id=current_user.id
        )

        if success:
            logger.info(f"User {current_user.id} deleted scenario {scenario_id}")
            return ScenarioDeleteResponse(
                success=True, message="Scenario deleted successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete scenario")

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete scenario")


# ============================================================================
# DUPLICATE SCENARIOS
# ============================================================================


@router.post(
    "/scenarios/{scenario_id}/duplicate",
    response_model=ScenarioCreateResponse,
    status_code=201,
    summary="Duplicate scenario",
    description="Create a copy of an existing scenario for customization",
    responses={
        201: {"description": "Scenario duplicated"},
        404: {"description": "Source scenario not found"},
        401: {"description": "Authentication required"},
    },
)
async def duplicate_scenario(
    scenario_id: str,
    request: DuplicateScenarioRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    Duplicate an existing scenario.

    Users can duplicate:
    - Their own scenarios
    - Public scenarios
    - System scenarios

    The duplicate will be owned by the current user and start as private.

    Args:
        scenario_id: Source scenario identifier
        request: DuplicateScenarioRequest with new title

    Returns:
        ScenarioCreateResponse with new scenario_id
    """
    try:
        service = ScenarioBuilderService(db)

        scenario = await service.duplicate_scenario(
            scenario_id=scenario_id,
            user_id=current_user.id,
            new_title=request.new_title,
        )

        logger.info(f"User {current_user.id} duplicated scenario {scenario_id}")

        return ScenarioCreateResponse(
            success=True,
            scenario_id=scenario.scenario_id,
            message="Scenario duplicated successfully",
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error duplicating scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to duplicate scenario")


# ============================================================================
# AI-POWERED ENHANCEMENTS
# ============================================================================


@router.post("/scenarios/assess-difficulty")
async def assess_scenario_difficulty(
    request: CreateScenarioRequest,
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_db_session),
):
    """
    AI-powered difficulty assessment for scenario content

    Analyzes vocabulary, grammar, phases, and complexity to suggest
    appropriate difficulty level.

    Args:
        request: Scenario data to assess
        current_user: Authenticated user
        db: Database session

    Returns:
        Assessment with difficulty, confidence, reasoning, and recommendations
    """
    try:
        service = ScenarioBuilderService(db)

        # Convert request to dict
        scenario_data = request.dict()

        # Get tutor profile if available (optional - enhance later)
        tutor_profile = None  # TODO: Fetch from user preferences

        # Perform AI assessment
        assessment = await service.assess_difficulty(scenario_data, tutor_profile)

        logger.info(
            f"Difficulty assessment for user {current_user.id}: "
            f"{assessment.get('difficulty')} (confidence: {assessment.get('confidence', 0):.2f})"
        )

        return {"success": True, "assessment": assessment}

    except Exception as e:
        logger.error(f"Error assessing difficulty: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to assess scenario difficulty"
        )
