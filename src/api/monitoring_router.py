from fastapi import APIRouter, status

router = APIRouter(
    prefix="",
    tags=["Monitoring"]
)

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Mandatory endpoint to check if the API is running and accessible.
    """
    return {"status": "ok", "service": "LLM Engine Verifier"}