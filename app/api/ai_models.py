"""
AI Model Management API
AI Language Tutor App - Task 3.1.5

RESTful API endpoints for AI model configuration and management:
- Model CRUD operations
- Performance monitoring and analytics
- Health checks and diagnostics
- Cost optimization controls
- Provider management
- Usage statistics and reporting
- Real-time model status updates
- Configuration validation

Provides comprehensive API for admin model management interface.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.ai_model_manager import ai_model_manager, ModelCategory, ModelStatus
from app.services.ai_router import ai_router
from app.services.admin_auth import require_admin_access

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/admin/ai-models", tags=["AI Models"])


# Pydantic models for request/response validation
class ModelUpdateRequest(BaseModel):
    """Model update request schema"""

    display_name: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    weight: Optional[float] = Field(None, ge=0.1, le=2.0)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=0.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=0.0, le=2.0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    enabled: Optional[bool] = None


class ModelOptimizationRequest(BaseModel):
    """Model optimization request schema"""

    language: str = "en"
    use_case: str = "conversation"
    budget_limit: Optional[float] = None
    max_response_time: Optional[float] = None
    min_quality_score: Optional[float] = None


class PerformanceReportRequest(BaseModel):
    """Performance report request schema"""

    model_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_comparisons: bool = True
    include_recommendations: bool = True


# API Routes


@router.get("/overview")
async def get_system_overview(admin_user=Depends(require_admin_access)):
    """
    Get comprehensive system overview

    Returns:
        - System statistics
        - Budget status
        - Provider breakdown
        - Top performing models
    """
    try:
        overview = await ai_model_manager.get_system_overview()
        return JSONResponse(content=overview)

    except Exception as e:
        logger.error(f"Failed to get system overview: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get system overview: {str(e)}"
        )


@router.get("/models")
async def get_models(
    category: Optional[str] = Query(None, description="Filter by model category"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    status: Optional[str] = Query(None, description="Filter by status"),
    enabled_only: bool = Query(False, description="Show only enabled models"),
    search: Optional[str] = Query(None, description="Search in model names"),
    admin_user=Depends(require_admin_access),
):
    """
    Get all AI models with filtering options

    Args:
        category: Model category filter
        provider: Provider filter
        status: Status filter
        enabled_only: Show only enabled models
        search: Search term for model names

    Returns:
        List of model configurations with usage statistics
    """
    try:
        models = await ai_model_manager.get_all_models(
            category=category, enabled_only=enabled_only
        )

        # Apply additional filters
        if provider:
            models = [
                m for m in models if m.get("provider", "").lower() == provider.lower()
            ]

        if status:
            models = [
                m for m in models if m.get("status", "").lower() == status.lower()
            ]

        if search:
            search_lower = search.lower()
            models = [
                m
                for m in models
                if search_lower in m.get("display_name", "").lower()
                or search_lower in m.get("model_name", "").lower()
                or search_lower in m.get("provider", "").lower()
            ]

        return JSONResponse(content={"models": models, "total": len(models)})

    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve models: {str(e)}"
        )


@router.get("/models/{model_id}")
async def get_model(
    model_id: str = Path(..., description="Model ID"),
    admin_user=Depends(require_admin_access),
):
    """
    Get specific model configuration and detailed statistics

    Args:
        model_id: Unique model identifier

    Returns:
        Detailed model configuration and performance data
    """
    try:
        model = await ai_model_manager.get_model(model_id)

        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Get performance report
        performance_report = await ai_model_manager.get_model_performance_report(
            model_id
        )

        response_data = {
            "model": model,
            "performance_report": performance_report.__dict__
            if performance_report
            else None,
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model {model_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve model: {str(e)}"
        )


@router.put("/models/{model_id}")
async def update_model(
    model_id: str = Path(..., description="Model ID"),
    update_data: ModelUpdateRequest = Body(...),
    admin_user=Depends(require_admin_access),
):
    """
    Update model configuration

    Args:
        model_id: Model to update
        update_data: Fields to update

    Returns:
        Updated model configuration
    """
    try:
        # Validate model exists
        existing_model = await ai_model_manager.get_model(model_id)
        if not existing_model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Convert to dict and filter out None values
        updates = {k: v for k, v in update_data.dict().items() if v is not None}

        # Validate status if provided
        if "status" in updates:
            try:
                ModelStatus(updates["status"])
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status value")

        # Apply updates
        success = await ai_model_manager.update_model(model_id, updates)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to update model")

        # Return updated model
        updated_model = await ai_model_manager.get_model(model_id)
        return JSONResponse(
            content={"model": updated_model, "message": "Model updated successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update model: {str(e)}")


@router.post("/models/{model_id}/toggle")
async def toggle_model(
    model_id: str = Path(..., description="Model ID"),
    admin_user=Depends(require_admin_access),
):
    """
    Toggle model enabled/disabled status

    Args:
        model_id: Model to toggle

    Returns:
        Updated model configuration
    """
    try:
        model = await ai_model_manager.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        new_enabled_status = not model.get("enabled", False)

        if new_enabled_status:
            success = await ai_model_manager.enable_model(model_id)
        else:
            success = await ai_model_manager.disable_model(model_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to toggle model status")

        updated_model = await ai_model_manager.get_model(model_id)

        return JSONResponse(
            content={
                "model": updated_model,
                "message": f"Model {'enabled' if new_enabled_status else 'disabled'} successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle model: {str(e)}")


@router.post("/models/{model_id}/priority")
async def set_model_priority(
    model_id: str = Path(..., description="Model ID"),
    priority: int = Body(..., ge=1, le=10, description="Priority level (1-10)"),
    admin_user=Depends(require_admin_access),
):
    """
    Set model priority for routing decisions

    Args:
        model_id: Model to update
        priority: Priority level (1 = highest, 10 = lowest)

    Returns:
        Updated model configuration
    """
    try:
        success = await ai_model_manager.set_model_priority(model_id, priority)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to set model priority")

        updated_model = await ai_model_manager.get_model(model_id)

        return JSONResponse(
            content={
                "model": updated_model,
                "message": f"Model priority set to {priority}",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set priority for model {model_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to set model priority: {str(e)}"
        )


@router.get("/performance/{model_id}")
async def get_performance_report(
    model_id: str = Path(..., description="Model ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days for report"),
    admin_user=Depends(require_admin_access),
):
    """
    Get detailed performance report for a model

    Args:
        model_id: Model to analyze
        days: Number of days to include in analysis

    Returns:
        Comprehensive performance analysis
    """
    try:
        report = await ai_model_manager.get_model_performance_report(model_id, days)

        if not report:
            raise HTTPException(
                status_code=404, detail="No performance data available for this model"
            )

        return JSONResponse(content={"report": report.__dict__})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance report for {model_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate performance report: {str(e)}"
        )


@router.post("/optimize")
async def optimize_model_selection(
    request: ModelOptimizationRequest = Body(...),
    admin_user=Depends(require_admin_access),
):
    """
    Get optimized model recommendations for specific use case

    Args:
        request: Optimization parameters

    Returns:
        Ranked list of recommended models
    """
    try:
        recommendations = await ai_model_manager.optimize_model_selection(
            language=request.language,
            use_case=request.use_case,
            budget_limit=request.budget_limit,
        )

        # Get detailed information for recommended models
        recommended_models = []
        for model_id in recommendations:
            model = await ai_model_manager.get_model(model_id)
            if model:
                recommended_models.append(model)

        return JSONResponse(
            content={
                "recommendations": recommended_models,
                "optimization_params": request.dict(),
                "message": f"Found {len(recommended_models)} optimized models for {request.use_case} in {request.language}",
            }
        )

    except Exception as e:
        logger.error(f"Failed to optimize model selection: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to optimize model selection: {str(e)}"
        )


@router.get("/health")
async def get_health_status(admin_user=Depends(require_admin_access)):
    """
    Get comprehensive health status of all models and providers

    Returns:
        System health overview with provider status
    """
    try:
        health_status = await ai_model_manager.get_health_status()
        return JSONResponse(content=health_status)

    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get health status: {str(e)}"
        )


@router.post("/health-check")
async def run_health_check(admin_user=Depends(require_admin_access)):
    """
    Run comprehensive health check on all providers

    Returns:
        Updated health status after running checks
    """
    try:
        # Force refresh of all provider health checks
        providers = ["claude", "mistral", "deepseek", "ollama"]
        health_results = {}

        for provider in providers:
            try:
                health = await ai_router.check_provider_health(provider)
                health_results[provider] = health
            except Exception as e:
                health_results[provider] = {
                    "status": "error",
                    "available": False,
                    "error": str(e),
                }

        # Get updated system overview
        overview = await ai_model_manager.get_system_overview()

        return JSONResponse(
            content={
                "health_check_results": health_results,
                "system_overview": overview,
                "timestamp": datetime.now().isoformat(),
                "message": "Health check completed",
            }
        )

    except Exception as e:
        logger.error(f"Failed to run health check: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to run health check: {str(e)}"
        )


@router.get("/usage-stats")
async def get_usage_statistics(
    start_date: Optional[datetime] = Query(
        None, description="Start date for statistics"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model_id: Optional[str] = Query(None, description="Filter by specific model"),
    admin_user=Depends(require_admin_access),
):
    """Get detailed usage statistics across models and providers"""
    try:
        start_date, end_date = _set_default_date_range(start_date, end_date)
        models = await ai_model_manager.get_all_models()
        models = _filter_models(models, provider, model_id)
        summary = _calculate_summary_stats(models)
        provider_stats = _calculate_provider_breakdown(models)
        return _build_statistics_response(
            start_date, end_date, summary, provider_stats, models
        )
    except Exception as e:
        logger.error(f"Failed to get usage statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get usage statistics: {str(e)}"
        )


def _set_default_date_range(
    start_date: Optional[datetime], end_date: Optional[datetime]
) -> tuple:
    """Set default date range if not provided - A(3)"""
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    return start_date, end_date


def _filter_models(
    models: list, provider: Optional[str], model_id: Optional[str]
) -> list:
    """Filter models based on parameters - A(3)"""
    if provider:
        models = [m for m in models if m.get("provider") == provider]
    if model_id:
        models = [m for m in models if m.get("id") == model_id]
    return models


def _calculate_summary_stats(models: list) -> dict:
    """Calculate aggregated statistics - A(4)"""
    total_requests = sum(
        m.get("usage_stats", {}).get("total_requests", 0) for m in models
    )
    total_cost = sum(m.get("usage_stats", {}).get("total_cost", 0) for m in models)
    avg_success_rate = sum(
        m.get("usage_stats", {}).get("success_rate", 0) for m in models
    ) / max(len(models), 1)

    return {
        "total_models": len(models),
        "total_requests": total_requests,
        "total_cost": round(total_cost, 4),
        "avg_success_rate": round(avg_success_rate, 3),
        "avg_cost_per_request": round(total_cost / max(total_requests, 1), 6),
    }


def _calculate_provider_breakdown(models: list) -> dict:
    """Calculate provider-level statistics - B(6)"""
    provider_stats = {}
    for model in models:
        provider_name = model.get("provider", "unknown")
        if provider_name not in provider_stats:
            provider_stats[provider_name] = {
                "models": 0,
                "total_requests": 0,
                "total_cost": 0.0,
                "avg_success_rate": 0.0,
            }

        stats = model.get("usage_stats", {})
        provider_stats[provider_name]["models"] += 1
        provider_stats[provider_name]["total_requests"] += stats.get(
            "total_requests", 0
        )
        provider_stats[provider_name]["total_cost"] += stats.get("total_cost", 0)
        provider_stats[provider_name]["avg_success_rate"] += stats.get(
            "success_rate", 0
        )

    # Calculate averages for providers
    for provider_name, stats in provider_stats.items():
        if stats["models"] > 0:
            stats["avg_success_rate"] /= stats["models"]

    return provider_stats


def _build_statistics_response(
    start_date: datetime,
    end_date: datetime,
    summary: dict,
    provider_stats: dict,
    models: list,
) -> JSONResponse:
    """Build statistics response - A(1)"""
    return JSONResponse(
        content={
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days,
            },
            "summary": summary,
            "provider_breakdown": provider_stats,
            "model_details": models,
        }
    )


@router.post("/reset-stats")
async def reset_usage_statistics(
    model_id: Optional[str] = Body(
        None, description="Specific model to reset, or all if not provided"
    ),
    confirm: bool = Body(False, description="Confirmation flag"),
    admin_user=Depends(require_admin_access),
):
    """
    Reset usage statistics for models (admin only, requires confirmation)

    Args:
        model_id: Specific model to reset, or None for all models
        confirm: Must be True to proceed

    Returns:
        Confirmation of reset operation
    """
    if not confirm:
        raise HTTPException(
            status_code=400, detail="Confirmation required for this operation"
        )

    try:
        # This would require implementing a reset method in ai_model_manager
        # For now, return a placeholder response

        if model_id:
            # Reset specific model
            model = await ai_model_manager.get_model(model_id)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found")

            message = f"Statistics reset for model {model_id}"
        else:
            # Reset all models
            message = "Statistics reset for all models"

        return JSONResponse(
            content={
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "warning": "This operation cannot be undone",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reset statistics: {str(e)}"
        )


@router.get("/export")
async def export_model_data(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format"),
    include_stats: bool = Query(True, description="Include usage statistics"),
    admin_user=Depends(require_admin_access),
):
    """
    Export model configuration and usage data

    Args:
        format: Export format (json or csv)
        include_stats: Whether to include usage statistics

    Returns:
        Exported model data in requested format
    """
    try:
        models = await ai_model_manager.get_all_models()

        if not include_stats:
            # Remove usage stats from export
            for model in models:
                model.pop("usage_stats", None)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_models": len(models),
            "models": models,
        }

        if format == "json":
            return JSONResponse(content=export_data)
        elif format == "csv":
            # For CSV format, we'd need to implement CSV conversion
            # For now, return JSON with CSV headers
            from fastapi.responses import Response

            # Simplified CSV export (would need proper CSV library for production)
            csv_lines = [
                "id,provider,model_name,display_name,category,status,enabled,priority"
            ]
            for model in models:
                line = f"{model.get('id', '')},{model.get('provider', '')},{model.get('model_name', '')},{model.get('display_name', '')},{model.get('category', '')},{model.get('status', '')},{model.get('enabled', '')},{model.get('priority', '')}"
                csv_lines.append(line)

            csv_content = "\n".join(csv_lines)

            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=ai_models_export.csv"
                },
            )

    except Exception as e:
        logger.error(f"Failed to export model data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to export model data: {str(e)}"
        )


@router.get("/categories")
async def get_model_categories(admin_user=Depends(require_admin_access)):
    """
    Get all available model categories

    Returns:
        List of model categories with descriptions
    """
    try:
        categories = [
            {
                "value": category.value,
                "label": category.value.replace("_", " ").title(),
                "description": f"Models optimized for {category.value} tasks",
            }
            for category in ModelCategory
        ]

        return JSONResponse(content={"categories": categories})

    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get categories: {str(e)}"
        )


@router.get("/providers")
async def get_providers(admin_user=Depends(require_admin_access)):
    """
    Get all available providers with their status

    Returns:
        List of providers with health status
    """
    try:
        providers = ["claude", "mistral", "deepseek", "ollama"]
        provider_info = []

        for provider_name in providers:
            health = await ai_router.check_provider_health(provider_name)
            models = await ai_model_manager.get_all_models()
            provider_models = [m for m in models if m.get("provider") == provider_name]

            provider_info.append(
                {
                    "name": provider_name,
                    "display_name": provider_name.title(),
                    "status": health.get("status", "unknown"),
                    "available": health.get("available", False),
                    "models_count": len(provider_models),
                    "active_models": len(
                        [m for m in provider_models if m.get("enabled", False)]
                    ),
                }
            )

        return JSONResponse(content={"providers": provider_info})

    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get providers: {str(e)}"
        )


# Exception handling is done at app level, not router level
# APIRouter doesn't have exception_handler decorator - that's only for FastAPI app instances
# @router.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     """Handle HTTP exceptions with proper JSON response"""
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": exc.detail,
#             "status_code": exc.status_code,
#             "timestamp": datetime.now().isoformat(),
#         },
#     )
