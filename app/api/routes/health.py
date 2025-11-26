from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.utils.logger import get_logger


logger = get_logger("health_route")

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check application health."""
    logger.info("Health check performed")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }