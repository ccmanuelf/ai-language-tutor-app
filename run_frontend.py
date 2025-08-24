#!/usr/bin/env python3
"""
AI Language Tutor App - FastHTML Frontend Runner
Personal Family Educational Tool
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastHTML app
from app.frontend_main import frontend_app

if __name__ == "__main__":
    print("🎯 Starting AI Language Tutor - FastHTML Frontend")
    print("📍 Frontend will be available at: http://localhost:3000")
    print("❤️  Health Check: http://localhost:3000/health")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)

    uvicorn.run(
        "app.frontend_main:frontend_app",
        host="localhost",
        port=3000,
        reload=True,
        log_level="info",
    )
