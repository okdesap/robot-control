"""
Application entrypoint
"""
from __future__ import annotations

import os
import sys
import uvicorn

# Ensure `python app/main.py` works by adding project root to sys.path
if __package__ is None or __package__ == "":
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from app.core.logging_config import setup_logging

from app.api.app import create_api_app


setup_logging()
app = create_api_app()


def start_server():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    start_server()
