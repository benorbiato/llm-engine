from datetime import datetime
from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.core.infrastructure.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="operational",
        version=settings.API_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        llm_provider="Anthropic"
    )

