"""
Frontend Server Startup
AI Language Tutor App - FastHTML Server Runner

Provides server startup functionality for the frontend application.
"""

import uvicorn
from .main import frontend_app


def run_frontend_server():
    """Run the FastHTML frontend server"""
    uvicorn.run(
        frontend_app, host="127.0.0.1", port=3000, reload=True, log_level="info"
    )


if __name__ == "__main__":
    run_frontend_server()
