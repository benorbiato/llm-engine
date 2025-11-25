#!/usr/bin/env python3
"""
Main entry point for running the API server locally.
"""

import uvicorn
import sys
from src.entrypoints.main_api import app
from src.core.infrastructure.config import settings
from src.core.infrastructure.logger_service import logger


if __name__ == "__main__":
    logger.info(
        "Starting Judicial Process Verification API",
        extra={"extra_fields": {"host": settings.HOST, "port": settings.PORT}}
    )
    
    try:
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            log_level=settings.LOG_LEVEL.lower(),
            reload=settings.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)

