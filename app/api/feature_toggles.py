"""
Feature Toggle API Endpoints
Provides REST API for dynamic feature control and management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from fastapi.security import HTTPBearer
from pydantic import ValidationError

from app.models.feature_toggle import (
    FeatureToggle,
    FeatureToggleRequest,
    FeatureToggleUpdateRequest,
    FeatureToggleResponse,
    FeatureToggleListResponse,
    UserFeatureStatusResponse,
    FeatureToggleStatsResponse,
    FeatureToggleScope,
    FeatureToggleStatus,
    FeatureToggleCategory,
)
from app.services.feature_toggle_service import get_feature_toggle_service
from app.core.auth import (
    get_current_admin_user,
    AdminPermission,
    check_admin_permission,
)
from app.models.user import User

router = APIRouter(prefix="/api/admin/feature-toggles", tags=["Feature Toggles"])
security = HTTPBearer()


@router.get(
    "/features",
    response_model=FeatureToggleListResponse,
    summary="List all feature toggles",
    description="Retrieve all feature toggles with optional filtering",
)
async def list_features(
    category: Optional[FeatureToggleCategory] = Query(
        None, description="Filter by category"
    ),
    scope: Optional[FeatureToggleScope] = Query(None, description="Filter by scope"),
    status: Optional[FeatureToggleStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_admin_user),
):
    """List all feature toggles with optional filtering and pagination."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        all_features = await service.get_all_features(category, scope, status)

        # Calculate pagination
        total = len(all_features)
        start = (page - 1) * per_page
        end = start + per_page
        features_page = all_features[start:end]
        has_next = end < total

        return FeatureToggleListResponse(
            features=features_page,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve features: {str(e)}",
        )


@router.get(
    "/features/{feature_id}",
    response_model=FeatureToggle,
    summary="Get specific feature toggle",
    description="Retrieve a specific feature toggle by ID",
)
async def get_feature(
    feature_id: str = Path(..., description="Feature toggle ID"),
    current_user: User = Depends(get_current_admin_user),
):
    """Get a specific feature toggle by ID."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        feature = await service.get_feature(feature_id)

        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        return feature

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feature: {str(e)}",
        )


@router.post(
    "/features",
    response_model=FeatureToggleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new feature toggle",
    description="Create a new feature toggle with specified configuration",
)
async def create_feature(
    feature_request: FeatureToggleRequest,
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new feature toggle."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        feature = await service.create_feature(feature_request, current_user.username)

        return FeatureToggleResponse(
            success=True,
            message=f"Feature toggle '{feature.id}' created successfully",
            feature=feature,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create feature toggle: {str(e)}",
        )


@router.put(
    "/features/{feature_id}",
    response_model=FeatureToggleResponse,
    summary="Update feature toggle",
    description="Update an existing feature toggle configuration",
)
async def update_feature(
    feature_id: str = Path(..., description="Feature toggle ID"),
    update_request: FeatureToggleUpdateRequest = ...,
    current_user: User = Depends(get_current_admin_user),
):
    """Update an existing feature toggle."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        feature = await service.update_feature(
            feature_id, update_request, current_user.username
        )

        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        return FeatureToggleResponse(
            success=True,
            message=f"Feature toggle '{feature_id}' updated successfully",
            feature=feature,
        )

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feature toggle: {str(e)}",
        )


@router.delete(
    "/features/{feature_id}",
    response_model=FeatureToggleResponse,
    summary="Delete feature toggle",
    description="Delete a feature toggle and all associated user access",
)
async def delete_feature(
    feature_id: str = Path(..., description="Feature toggle ID"),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete a feature toggle."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        success = await service.delete_feature(feature_id, current_user.username)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        return FeatureToggleResponse(
            success=True, message=f"Feature toggle '{feature_id}' deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feature toggle: {str(e)}",
        )


@router.post(
    "/features/{feature_id}/enable",
    response_model=FeatureToggleResponse,
    summary="Enable feature toggle",
    description="Quickly enable a feature toggle",
)
async def enable_feature(
    feature_id: str = Path(..., description="Feature toggle ID"),
    current_user: User = Depends(get_current_admin_user),
):
    """Enable a feature toggle."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        update_request = FeatureToggleUpdateRequest(status=FeatureToggleStatus.ENABLED)
        feature = await service.update_feature(
            feature_id, update_request, current_user.username
        )

        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        return FeatureToggleResponse(
            success=True,
            message=f"Feature toggle '{feature_id}' enabled successfully",
            feature=feature,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable feature toggle: {str(e)}",
        )


@router.post(
    "/features/{feature_id}/disable",
    response_model=FeatureToggleResponse,
    summary="Disable feature toggle",
    description="Quickly disable a feature toggle",
)
async def disable_feature(
    feature_id: str = Path(..., description="Feature toggle ID"),
    current_user: User = Depends(get_current_admin_user),
):
    """Disable a feature toggle."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        update_request = FeatureToggleUpdateRequest(status=FeatureToggleStatus.DISABLED)
        feature = await service.update_feature(
            feature_id, update_request, current_user.username
        )

        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        return FeatureToggleResponse(
            success=True,
            message=f"Feature toggle '{feature_id}' disabled successfully",
            feature=feature,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable feature toggle: {str(e)}",
        )


@router.get(
    "/features/{feature_id}/status/{user_id}",
    response_model=UserFeatureStatusResponse,
    summary="Check user feature status",
    description="Check if a feature is enabled for a specific user",
)
async def check_user_feature_status(
    feature_id: str = Path(..., description="Feature toggle ID"),
    user_id: str = Path(..., description="User ID to check"),
    user_roles: Optional[str] = Query(None, description="Comma-separated user roles"),
    current_user: User = Depends(get_current_admin_user),
):
    """Check if a feature is enabled for a specific user."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()

        # Parse user roles
        roles_list = user_roles.split(",") if user_roles else None

        enabled = await service.is_feature_enabled(feature_id, user_id, roles_list)

        # Get feature for additional context
        feature = await service.get_feature(feature_id)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        # Determine reason
        reason = "enabled" if enabled else "disabled"
        if feature.status == FeatureToggleStatus.DISABLED:
            reason = "globally disabled"
        elif feature.requires_admin and (not roles_list or "admin" not in roles_list):
            reason = "requires admin role"
        elif (
            feature.scope == FeatureToggleScope.USER_SPECIFIC
            and user_id not in feature.target_users
        ):
            reason = "not in target users"
        elif feature.scope == FeatureToggleScope.ROLE_BASED and (
            not roles_list
            or not any(role in feature.target_roles for role in roles_list)
        ):
            reason = "role not targeted"

        return UserFeatureStatusResponse(
            user_id=user_id,
            feature_id=feature_id,
            enabled=enabled,
            reason=reason,
            metadata={
                "feature_name": feature.name,
                "feature_category": feature.category.value,
                "feature_scope": feature.scope.value,
                "feature_status": feature.status.value,
                "requires_admin": feature.requires_admin,
                "experimental": feature.experimental,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check user feature status: {str(e)}",
        )


@router.post(
    "/users/{user_id}/features/{feature_id}",
    response_model=FeatureToggleResponse,
    summary="Set user feature access",
    description="Grant or revoke feature access for specific user",
)
async def set_user_feature_access(
    user_id: str = Path(..., description="User ID"),
    feature_id: str = Path(..., description="Feature toggle ID"),
    enabled: bool = Query(..., description="Whether to enable feature for user"),
    override_global: bool = Query(False, description="Override global feature setting"),
    override_reason: Optional[str] = Query(None, description="Reason for override"),
    expires_hours: Optional[int] = Query(
        None, description="Hours until override expires"
    ),
    current_user: User = Depends(get_current_admin_user),
):
    """Set user-specific feature access."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()

        # Calculate expiry if provided
        override_expires = None
        if expires_hours:
            from datetime import timedelta

            override_expires = datetime.now() + timedelta(hours=expires_hours)

        success = await service.set_user_feature_access(
            user_id=user_id,
            feature_id=feature_id,
            enabled=enabled,
            granted_by=current_user.username,
            override_global=override_global,
            override_reason=override_reason,
            override_expires=override_expires,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature toggle '{feature_id}' not found",
            )

        action = "granted" if enabled else "revoked"
        return FeatureToggleResponse(
            success=True,
            message=f"Feature access {action} for user '{user_id}' on feature '{feature_id}'",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set user feature access: {str(e)}",
        )


@router.get(
    "/users/{user_id}/features",
    response_model=Dict[str, bool],
    summary="Get user feature status",
    description="Get all feature statuses for a specific user",
)
async def get_user_features(
    user_id: str = Path(..., description="User ID"),
    user_roles: Optional[str] = Query(None, description="Comma-separated user roles"),
    current_user: User = Depends(get_current_admin_user),
):
    """Get all feature states for a specific user."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()

        # Parse user roles
        roles_list = user_roles.split(",") if user_roles else None

        features = await service.get_user_features(user_id, roles_list)
        return features

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user features: {str(e)}",
        )


@router.get(
    "/statistics",
    response_model=FeatureToggleStatsResponse,
    summary="Get feature toggle statistics",
    description="Get comprehensive statistics about feature toggles",
)
async def get_feature_statistics(current_user: User = Depends(get_current_admin_user)):
    """Get feature toggle statistics."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()
        stats = await service.get_feature_statistics()

        return FeatureToggleStatsResponse(
            total_features=stats["total_features"],
            enabled_features=stats["enabled_features"],
            disabled_features=stats["disabled_features"],
            experimental_features=stats["experimental_features"],
            features_by_category=stats["features_by_category"],
            features_by_scope=stats["features_by_scope"],
            features_by_environment=stats["features_by_environment"],
            recent_changes=[],  # Convert events if needed
            usage_metrics={
                "cache_size": stats["cache_size"],
                "total_users_with_overrides": stats["total_users_with_overrides"],
                "total_events": stats["total_events"],
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature statistics: {str(e)}",
        )


@router.post(
    "/bulk-update",
    response_model=FeatureToggleResponse,
    summary="Bulk update features",
    description="Update multiple features at once",
)
async def bulk_update_features(
    updates: Dict[str, FeatureToggleUpdateRequest],
    current_user: User = Depends(get_current_admin_user),
):
    """Bulk update multiple features."""

    # Check permissions
    await check_admin_permission(current_user, AdminPermission.MANAGE_FEATURES)

    try:
        service = await get_feature_toggle_service()

        updated_count = 0
        errors = []

        for feature_id, update_request in updates.items():
            try:
                feature = await service.update_feature(
                    feature_id, update_request, current_user.username
                )
                if feature:
                    updated_count += 1
                else:
                    errors.append(f"Feature '{feature_id}' not found")
            except Exception as e:
                errors.append(f"Error updating '{feature_id}': {str(e)}")

        return FeatureToggleResponse(
            success=len(errors) == 0,
            message=f"Updated {updated_count} features successfully"
            + (f", {len(errors)} errors" if errors else ""),
            errors=errors,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update features: {str(e)}",
        )


# Public endpoint for checking feature status (for frontend)
@router.get(
    "/public/check/{feature_id}",
    response_model=Dict[str, Any],
    summary="Public feature check",
    description="Check feature status for current user (public endpoint)",
)
async def public_check_feature(
    feature_id: str = Path(..., description="Feature toggle ID"),
    current_user: Optional[User] = Depends(get_current_admin_user),
):
    """Public endpoint to check if a feature is enabled for the current user."""

    try:
        service = await get_feature_toggle_service()

        user_id = current_user.id if current_user else None
        user_roles = current_user.roles if current_user else None

        enabled = await service.is_feature_enabled(feature_id, user_id, user_roles)

        return {
            "feature_id": feature_id,
            "enabled": enabled,
            "user_authenticated": current_user is not None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check feature status: {str(e)}",
        )
