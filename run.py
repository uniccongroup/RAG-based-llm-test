#!/usr/bin/env python
"""Application entry point."""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from app.core.config import settings
from app.core.logger import logger

if __name__ == "__main__":
    # Render / Railway / Fly.io inject PORT at runtime
    port = int(os.environ.get("PORT", settings.port))

    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server running at http://{settings.host}:{port}")
    logger.info(f"API documentation at http://{settings.host}:{port}/docs")
    logger.info(f"Chat UI at http://{settings.host}:{port}/ui")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
