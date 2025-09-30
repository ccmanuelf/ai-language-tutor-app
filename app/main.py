"""
FastAPI Backend Server Entry Point
AI Language Tutor App - Personal Family Educational Tool
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

# Import core configuration
from app.core.config import get_settings
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.content import router as content_router
from app.api.scenarios import router as scenarios_router
from app.api.realtime_analysis import router as realtime_router
from app.api.tutor_modes import router as tutor_modes_router
from app.api.feature_toggles import router as feature_toggles_router
from app.api.ai_models import router as ai_models_router
from app.api.scenario_management import router as scenario_management_router
from app.api.visual_learning import router as visual_learning_router


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
    app.include_router(conversations_router)
    app.include_router(content_router, prefix="/api/content", tags=["content"])
    app.include_router(scenarios_router, prefix="/api/scenarios", tags=["scenarios"])
    app.include_router(realtime_router, tags=["realtime-analysis"])
    app.include_router(tutor_modes_router, tags=["tutor-modes"])
    app.include_router(feature_toggles_router, tags=["feature-toggles"])
    app.include_router(ai_models_router, tags=["ai-models"])
    app.include_router(scenario_management_router, tags=["scenario-management"])
    app.include_router(visual_learning_router, tags=["visual-learning"])

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
