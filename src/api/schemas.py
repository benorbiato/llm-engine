from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.domain.entities import Processo, Honorarios
from src.core.domain.enums.decision_enums import DecisionStatus


class PolicyReference(BaseModel):
    """Reference to a policy rule in the decision."""
    policy_id: str = Field(..., description="Policy rule ID")
    explanation: str = Field(..., description="How this policy applies to the decision")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "POL-1",
                "explanation": "Process is in execution phase and transitado em julgado is verified"
            }
        }


class ProcessVerificationRequest(BaseModel):
    """Request schema for process verification."""
    process: Processo = Field(..., description="Judicial process data")

    class Config:
        json_schema_extra = {
            "example": {
                "process": {
                    "numeroProcesso": "0001234-56.2023.4.05.8100",
                    "classe": "Cumprimento de Sentença contra a Fazenda Pública",
                    "orgaoJulgador": "19ª VARA FEDERAL - SOBRAL/CE",
                    "ultimaDistribuicao": "2024-11-18T23:15:44.130Z",
                    "assunto": "Rural (Art. 48/51)",
                    "segredoJustica": False,
                    "justicaGratuita": True,
                    "siglaTribunal": "TRF5",
                    "esfera": "Federal",
                    "documentos": [],
                    "movimentos": [],
                    "valorCondenacao": 67592
                }
            }
        }


class ProcessVerificationResponse(BaseModel):
    """Response schema for process verification."""
    decision: DecisionStatus = Field(..., description="Decision: approved, rejected, or incomplete")
    rationale: str = Field(..., description="Clear justification for the decision")
    references: List[PolicyReference] = Field(..., description="References to applied policy rules")
    process_number: str = Field(..., description="Process number for reference")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "approved",
                "rationale": "Process meets all eligibility criteria. Transit in judgment verified, execution phase confirmed, and value exceeds minimum threshold.",
                "references": [
                    {
                        "policy_id": "POL-1",
                        "explanation": "Process is in final judgment and execution phase"
                    },
                    {
                        "policy_id": "POL-2",
                        "explanation": "Condemnation value is informed: R$ 67,592"
                    }
                ],
                "process_number": "0001234-56.2023.4.05.8100"
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Check timestamp")

