"""
Verification router - main API endpoint.
"""
from fastapi import APIRouter, Depends, status
from typing import Annotated
from src.api.schemas import ProcessVerificationRequest, ProcessVerificationResponse
from src.core.application.services.verification_service import VerificationUseCase

router = APIRouter(prefix="/v1", tags=["Verification"])


def get_verification_use_case() -> VerificationUseCase:
    """Dependency injection for verification use case."""
    return VerificationUseCase()


VerificationService = Annotated[VerificationUseCase, Depends(get_verification_use_case)]


@router.post(
    "/verify",
    response_model=ProcessVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Judicial Process",
    description="Analyzes a judicial process and returns an eligibility decision (approved, rejected, or incomplete)"
)
async def verify_judicial_process(
    request: ProcessVerificationRequest,
    use_case: VerificationService
) -> ProcessVerificationResponse:
    """
    Verify judicial process eligibility for credit purchase.
    
    This endpoint:
    1. Receives complete judicial process data
    2. Validates against company policies
    3. Returns structured decision with rationale and policy references
    """
    return await use_case.execute(request)

