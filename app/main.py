from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.config import settings
from app.utils.logger import get_logger, setup_logging
from app.api.routes import health, verify, process, analytics
from app.api.middleware.logging import LoggingMiddleware, ErrorHandlingMiddleware


# Setup logging
setup_logging()
logger = get_logger("main")

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(verify.router)
app.include_router(process.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup_event():
    """Event executed when the application starts."""
    logger.info(
        "Application started",
        extra={"extra_data": {
            "environment": settings.environment,
            "debug": settings.debug,
            "api_version": settings.api_version
        }}
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Event executed when the application shuts down."""
    logger.info("Application shut down")


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://juscash.com.br/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.environment == "development",
        log_level=settings.log_level.lower(),
    )