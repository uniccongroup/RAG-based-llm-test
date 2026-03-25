#!/usr/bin/env python
"""Application entry point."""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from app.core.config import settings
from app.core.logger import logger

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server running at http://{settings.host}:{settings.port}")
    logger.info(f"API documentation at http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
