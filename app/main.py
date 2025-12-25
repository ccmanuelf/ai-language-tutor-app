"""
FastAPI Backend Server Entry Point
AI Language Tutor App - Personal Family Educational Tool
"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.ai_models import router as ai_models_router
from app.api.auth import router as auth_router
from app.api.budget import router as budget_router
from app.api.content import router as content_router
from app.api.content_collections import router as content_collections_router
from app.api.content_study import router as content_study_router
from app.api.conversations import router as conversations_router
from app.api.feature_toggles import router as feature_toggles_router
from app.api.gamification import router as gamification_router
from app.api.ollama import router as ollama_router
from app.api.personas import router as personas_router
from app.api.realtime_analysis import router as realtime_router
from app.api.scenario_builder import router as scenario_builder_router
from app.api.scenario_management import router as scenario_management_router
from app.api.scenario_organization import router as scenario_organization_router
from app.api.scenarios import router as scenarios_router
from app.api.tutor_modes import router as tutor_modes_router
from app.api.visual_learning import router as visual_learning_router

# Import core configuration
from app.core.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers for production
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title="AI Language Tutor API",
        description="Backend API for AI Language Tutor App - Personal Family Educational Tool",
        version="0.1.0",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Include API routers
    app.include_router(auth_router)
    app.include_router(budget_router, tags=["budget"])
    app.include_router(conversations_router)
    app.include_router(content_router, prefix="/api/content", tags=["content"])
    app.include_router(
        content_collections_router, prefix="/api/content", tags=["content-collections"]
    )
    app.include_router(
        content_study_router, prefix="/api/content", tags=["content-study"]
    )
    app.include_router(personas_router, tags=["personas"])
    app.include_router(scenarios_router)  # Router already has /api/v1/scenarios prefix
    app.include_router(
        scenario_builder_router
    )  # Router already has /api/v1/scenario-builder prefix
    app.include_router(
        scenario_organization_router
    )  # Router already has /api/v1/scenario-organization prefix
    app.include_router(realtime_router, tags=["realtime-analysis"])
    app.include_router(tutor_modes_router, tags=["tutor-modes"])
    app.include_router(feature_toggles_router, tags=["feature-toggles"])
    app.include_router(ai_models_router, tags=["ai-models"])
    app.include_router(scenario_management_router, tags=["scenario-management"])
    app.include_router(visual_learning_router, tags=["visual-learning"])
    app.include_router(ollama_router, prefix="/api/v1/ollama", tags=["ollama"])
    app.include_router(gamification_router, tags=["gamification"])

    # Frontend routes
    from app.frontend.scenario_builder import create_scenario_builder_route
    from app.frontend.scenario_collections import create_collections_route
    from app.frontend.scenario_detail import create_scenario_detail_route
    from app.frontend.scenario_discovery import create_discovery_hub_route

    app.get("/scenario-builder")(create_scenario_builder_route())
    app.get("/my-collections")(create_collections_route())
    app.get("/discover")(create_discovery_hub_route())
    app.get("/scenarios/{scenario_id}")(create_scenario_detail_route())

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "ai-language-tutor-api"}

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "AI Language Tutor API",
            "version": "0.1.0",
            "docs": "/api/docs"
            if settings.DEBUG
            else "Documentation disabled in production",
        }

    return app


# Create app instance
app = create_app()


def run_server():
    """Run the FastAPI server - extracted for testing"""
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )


if __name__ == "__main__":
    run_server()
