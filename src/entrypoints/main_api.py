"""
Main API application factory.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.core.infrastructure.config import settings
from src.core.infrastructure.logger_service import logger
from src.api.routers import health_router, verification_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Include routers
    app.include_router(health_router.router)
    app.include_router(verification_router.router)
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={"extra_fields": {"path": request.url.path}}
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    @app.on_event("startup")
    async def startup():
        logger.info("Application starting up")
    
    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Application shutting down")
    
    return app


app = create_app()
