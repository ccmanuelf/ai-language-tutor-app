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
            "docs": "/api/docs" if settings.DEBUG else "Documentation disabled in production"
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )