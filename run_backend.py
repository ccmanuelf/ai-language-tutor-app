#!/usr/bin/env python3
"""
AI Language Tutor App - FastAPI Backend Runner
Personal Family Educational Tool
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting AI Language Tutor - FastAPI Backend")
    print("📍 Backend API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)

    uvicorn.run(
        "app.main:app", host="localhost", port=8000, reload=True, log_level="info"
    )
