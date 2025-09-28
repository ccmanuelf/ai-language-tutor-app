"""
Feature Toggles API

RESTful API endpoints for managing feature toggles in the AI Language Tutor application.
Provides programmatic access to feature toggle configuration and management.

Author: AI Assistant
Date: 2025-09-27
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse
from fasthtml.common import *
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

from ..services.feature_toggle_manager import (
    feature_toggle_manager,
    FeatureToggle,
    FeatureCategory,
    UserRole,
)
from ..frontend.admin_feature_toggles import create_feature_toggles_page
from ..middleware.admin_middleware import require_admin_permission

logger = logging.getLogger(__name__)

# Create router for feature toggle endpoints
router = APIRouter(prefix="/dashboard/admin/feature-toggles", tags=["feature-toggles"])


@router.get("")
async def get_feature_toggles_page(request: Request):
    """Get the feature toggles admin page (HTML)"""
    try:
        # Check admin permissions
        user = getattr(request.state, "user", None)
        if not user or user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Return HTML page
        return create_feature_toggles_page(user_role=user.get("role", "ADMIN"))

    except Exception as e:
        logger.error(f"Error generating feature toggles page: {e}")
        return Div(
            P(
                f"Error loading feature toggles: {e}",
                cls="text-red-600 text-center py-8",
            ),
            id="feature-toggles-container",
        )


@router.get("/api/features")
async def get_all_features(
    category: Optional[str] = None, user_role: str = "ADMIN"
) -> Dict[str, Any]:
    """Get all feature toggles (JSON API)"""
    try:
        if category:
            features = feature_toggle_manager.get_all_features(
                category=category, user_role=user_role
            )
        else:
            features = feature_toggle_manager.get_all_features(user_role=user_role)

        # Convert to serializable format
        result = {}
        for name, feature in features.items():
            result[name] = {
                "id": feature.id,
                "feature_name": feature.feature_name,
                "is_enabled": feature.is_enabled,
                "description": feature.description,
                "category": feature.category,
                "requires_restart": feature.requires_restart,
                "min_role": feature.min_role,
                "configuration": feature.configuration,
                "created_at": feature.created_at,
                "updated_at": feature.updated_at,
            }

        return {"features": result, "count": len(result)}

    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/features/by-category")
async def get_features_by_category(user_role: str = "ADMIN") -> Dict[str, Any]:
    """Get features organized by category (JSON API)"""
    try:
        features_by_category = feature_toggle_manager.get_features_by_category(
            user_role
        )

        # Convert to serializable format
        result = {}
        for category, features in features_by_category.items():
            result[category] = []
            for feature in features:
                result[category].append(
                    {
                        "id": feature.id,
                        "feature_name": feature.feature_name,
                        "is_enabled": feature.is_enabled,
                        "description": feature.description,
                        "category": feature.category,
                        "requires_restart": feature.requires_restart,
                        "min_role": feature.min_role,
                        "configuration": feature.configuration,
                        "created_at": feature.created_at,
                        "updated_at": feature.updated_at,
                    }
                )

        return {"categories": result}

    except Exception as e:
        logger.error(f"Error getting features by category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/features/{feature_name}")
async def get_feature(feature_name: str) -> Dict[str, Any]:
    """Get specific feature toggle (JSON API)"""
    try:
        feature = feature_toggle_manager.get_feature(feature_name)

        if not feature:
            raise HTTPException(
                status_code=404, detail=f"Feature '{feature_name}' not found"
            )

        return {
            "id": feature.id,
            "feature_name": feature.feature_name,
            "is_enabled": feature.is_enabled,
            "description": feature.description,
            "category": feature.category,
            "requires_restart": feature.requires_restart,
            "min_role": feature.min_role,
            "configuration": feature.configuration,
            "created_at": feature.created_at,
            "updated_at": feature.updated_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature '{feature_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{feature_name}/config")
async def get_feature_config(feature_name: str):
    """Get feature configuration for modal (JSON)"""
    try:
        feature = feature_toggle_manager.get_feature(feature_name)

        if not feature:
            return JSONResponse({"error": "Feature not found"}, status_code=404)

        return JSONResponse(
            {
                "feature_name": feature.feature_name,
                "description": feature.description,
                "category": feature.category,
                "min_role": feature.min_role,
                "requires_restart": feature.requires_restart,
                "configuration": feature.configuration,
            }
        )

    except Exception as e:
        logger.error(f"Error getting feature config: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/{feature_name}/details")
async def get_feature_details(feature_name: str):
    """Get complete feature details for modal (JSON)"""
    try:
        feature = feature_toggle_manager.get_feature(feature_name)

        if not feature:
            return JSONResponse({"error": "Feature not found"}, status_code=404)

        return JSONResponse(
            {
                "id": feature.id,
                "feature_name": feature.feature_name,
                "is_enabled": feature.is_enabled,
                "description": feature.description,
                "category": feature.category,
                "requires_restart": feature.requires_restart,
                "min_role": feature.min_role,
                "configuration": feature.configuration,
                "created_at": feature.created_at,
                "updated_at": feature.updated_at,
            }
        )

    except Exception as e:
        logger.error(f"Error getting feature details: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/toggle/{feature_name}")
async def toggle_feature(feature_name: str, request: Request):
    """Toggle a feature on/off (returns updated HTML)"""
    try:
        # Check admin permissions
        user = getattr(request.state, "user", None)
        if not user or user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Get current feature state
        feature = feature_toggle_manager.get_feature(feature_name)
        if not feature:
            raise HTTPException(
                status_code=404, detail=f"Feature '{feature_name}' not found"
            )

        # Toggle the feature
        new_state = not feature.is_enabled
        success = feature_toggle_manager.update_feature(
            feature_name, is_enabled=new_state
        )

        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to toggle feature '{feature_name}'"
            )

        logger.info(
            f"Feature '{feature_name}' {'enabled' if new_state else 'disabled'} by admin {user.get('email')}"
        )

        # Return updated page
        return create_feature_toggles_page(user_role=user.get("role", "ADMIN"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling feature '{feature_name}': {e}")
        return Div(
            P(f"Error toggling feature: {e}", cls="text-red-600 text-center py-4"),
            id="feature-toggles-container",
        )


@router.post("/api/features/{feature_name}/toggle")
async def api_toggle_feature(feature_name: str) -> Dict[str, Any]:
    """Toggle a feature on/off (JSON API)"""
    try:
        # Get current feature state
        feature = feature_toggle_manager.get_feature(feature_name)
        if not feature:
            raise HTTPException(
                status_code=404, detail=f"Feature '{feature_name}' not found"
            )

        # Toggle the feature
        new_state = not feature.is_enabled
        success = feature_toggle_manager.update_feature(
            feature_name, is_enabled=new_state
        )

        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to toggle feature '{feature_name}'"
            )

        return {
            "feature_name": feature_name,
            "previous_state": feature.is_enabled,
            "new_state": new_state,
            "success": True,
            "message": f"Feature '{feature_name}' {'enabled' if new_state else 'disabled'}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling feature '{feature_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configure")
async def configure_feature(
    request: Request,
    feature_name: str = Form(...),
    description: str = Form(""),
    category: str = Form("general"),
    min_role: str = Form("CHILD"),
    requires_restart: bool = Form(False),
    configuration: str = Form("{}"),
):
    """Configure a feature (returns updated HTML)"""
    try:
        # Check admin permissions
        user = getattr(request.state, "user", None)
        if not user or user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Parse configuration JSON
        try:
            config_dict = json.loads(configuration) if configuration else {}
        except json.JSONDecodeError as e:
            return Div(
                P(
                    f"Invalid JSON configuration: {e}",
                    cls="text-red-600 text-center py-4",
                ),
                id="feature-toggles-container",
            )

        # Update feature
        success = feature_toggle_manager.update_feature(
            feature_name,
            description=description if description else None,
            configuration=config_dict,
        )

        if not success:
            return Div(
                P(
                    f"Failed to configure feature '{feature_name}'",
                    cls="text-red-600 text-center py-4",
                ),
                id="feature-toggles-container",
            )

        logger.info(f"Feature '{feature_name}' configured by admin {user.get('email')}")

        # Return updated page
        return create_feature_toggles_page(user_role=user.get("role", "ADMIN"))

    except Exception as e:
        logger.error(f"Error configuring feature '{feature_name}': {e}")
        return Div(
            P(f"Error configuring feature: {e}", cls="text-red-600 text-center py-4"),
            id="feature-toggles-container",
        )


@router.post("/api/features/{feature_name}/configure")
async def api_configure_feature(
    feature_name: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Configure a feature (JSON API)"""
    try:
        # Update feature
        success = feature_toggle_manager.update_feature(
            feature_name,
            description=config.get("description"),
            configuration=config.get("configuration"),
        )

        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to configure feature '{feature_name}'"
            )

        return {
            "feature_name": feature_name,
            "success": True,
            "message": f"Feature '{feature_name}' configured successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring feature '{feature_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-enable")
async def bulk_enable_features(request: Request):
    """Enable all features (returns updated HTML)"""
    try:
        # Check admin permissions
        user = getattr(request.state, "user", None)
        if not user or user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Get all features
        features = feature_toggle_manager.get_all_features(user_role="ADMIN")

        # Enable all features
        updates = {name: True for name in features.keys()}
        results = feature_toggle_manager.bulk_update_features(updates)

        successful_updates = sum(1 for success in results.values() if success)

        logger.info(
            f"Bulk enabled {successful_updates}/{len(updates)} features by admin {user.get('email')}"
        )

        # Return updated page
        return create_feature_toggles_page(user_role=user.get("role", "ADMIN"))

    except Exception as e:
        logger.error(f"Error bulk enabling features: {e}")
        return Div(
            P(
                f"Error bulk enabling features: {e}",
                cls="text-red-600 text-center py-4",
            ),
            id="feature-toggles-container",
        )


@router.post("/bulk-disable")
async def bulk_disable_features(request: Request):
    """Disable all features (returns updated HTML)"""
    try:
        # Check admin permissions
        user = getattr(request.state, "user", None)
        if not user or user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Get all features
        features = feature_toggle_manager.get_all_features(user_role="ADMIN")

        # Disable all features (except critical admin features)
        critical_features = ["user_management", "feature_toggles", "system_monitoring"]
        updates = {
            name: False
            for name, feature in features.items()
            if feature.feature_name not in critical_features
        }

        results = feature_toggle_manager.bulk_update_features(updates)

        successful_updates = sum(1 for success in results.values() if success)

        logger.warning(
            f"Bulk disabled {successful_updates}/{len(updates)} features by admin {user.get('email')} (critical features preserved)"
        )

        # Return updated page
        return create_feature_toggles_page(user_role=user.get("role", "ADMIN"))

    except Exception as e:
        logger.error(f"Error bulk disabling features: {e}")
        return Div(
            P(
                f"Error bulk disabling features: {e}",
                cls="text-red-600 text-center py-4",
            ),
            id="feature-toggles-container",
        )


@router.post("/api/features/bulk-update")
async def api_bulk_update_features(updates: Dict[str, bool]) -> Dict[str, Any]:
    """Bulk update multiple features (JSON API)"""
    try:
        results = feature_toggle_manager.bulk_update_features(updates)

        successful_updates = sum(1 for success in results.values() if success)

        return {
            "total_requested": len(updates),
            "successful_updates": successful_updates,
            "failed_updates": len(updates) - successful_updates,
            "results": results,
            "success": successful_updates > 0,
        }

    except Exception as e:
        logger.error(f"Error bulk updating features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_configuration():
    """Export feature toggle configuration (JSON)"""
    try:
        config = feature_toggle_manager.export_configuration()
        return JSONResponse(config)

    except Exception as e:
        logger.error(f"Error exporting configuration: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/api/import")
async def api_import_configuration(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Import feature toggle configuration (JSON API)"""
    try:
        results = feature_toggle_manager.import_configuration(config_data)

        successful_imports = sum(1 for success in results.values() if success)

        return {
            "total_features": len(results),
            "successful_imports": successful_imports,
            "failed_imports": len(results) - successful_imports,
            "results": results,
            "success": successful_imports > 0,
        }

    except Exception as e:
        logger.error(f"Error importing configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Get feature toggle statistics (JSON API)"""
    try:
        stats = feature_toggle_manager.get_feature_statistics()
        return stats

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/features")
async def api_create_feature(feature_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new feature toggle (JSON API)"""
    try:
        # Create FeatureToggle object
        feature = FeatureToggle(
            feature_name=feature_data.get("feature_name"),
            is_enabled=feature_data.get("is_enabled", True),
            description=feature_data.get("description", ""),
            category=feature_data.get("category", "general"),
            requires_restart=feature_data.get("requires_restart", False),
            min_role=feature_data.get("min_role", "CHILD"),
            configuration=feature_data.get("configuration", {}),
        )

        success = feature_toggle_manager.create_feature(feature)

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create feature '{feature.feature_name}'",
            )

        return {
            "feature_name": feature.feature_name,
            "success": True,
            "message": f"Feature '{feature.feature_name}' created successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/features/{feature_name}")
async def api_delete_feature(feature_name: str) -> Dict[str, Any]:
    """Delete a feature toggle (JSON API)"""
    try:
        success = feature_toggle_manager.delete_feature(feature_name)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Feature '{feature_name}' not found"
            )

        return {
            "feature_name": feature_name,
            "success": True,
            "message": f"Feature '{feature_name}' deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature '{feature_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@router.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check for feature toggle service"""
    try:
        # Test basic functionality
        stats = feature_toggle_manager.get_feature_statistics()

        return {
            "status": "healthy",
            "service": "feature_toggles",
            "timestamp": datetime.now().isoformat(),
            "total_features": stats.get("total_features", 0),
            "cache_status": "operational"
            if hasattr(feature_toggle_manager, "_cache")
            else "error",
        }

    except Exception as e:
        logger.error(f"Feature toggle health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "feature_toggles",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
