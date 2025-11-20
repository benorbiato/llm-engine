from fastapi import APIRouter
from .monitoring_router import router as monitoring_router
from .operations.decisions_router import router as decisions_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(monitoring_router)
v1_router.include_router(decisions_router)

router = v1_router