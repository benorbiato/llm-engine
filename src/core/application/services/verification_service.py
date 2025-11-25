"""
Verification use case - orchestrates verification flow with LLM.
"""
import json
from typing import List
from src.core.domain.entities import Processo
from src.core.domain.enums.decision_enums import DecisionStatus
from src.core.domain.policy import BusinessPolicy
from src.core.infrastructure.llm_adapter import LLMAdapter
from src.core.infrastructure.logger_service import logger
from src.core.application.services.policy_service import PolicyVerificationService
from src.api.schemas import PolicyReference, ProcessVerificationResponse, ProcessVerificationRequest


class VerificationUseCase:
    """Use case for judicial process verification with LLM."""
    
    SYSTEM_PROMPT = """You are an expert legal analyst specializing in judicial process verification and credit purchase eligibility.

Your task is to analyze a judicial process and provide a structured decision based on company policies.

IMPORTANT: You MUST respond with ONLY a valid JSON object, no additional text before or after.

Response format:
{{
    "decision": "approved" | "rejected" | "incomplete",
    "rationale": "Clear explanation of the decision",
    "internal_analysis": "Detailed analysis performed"
}}

Apply these policies:
{policy_context}

Process Data:
{process_data}

Analyze the process considering:
1. Judicial sphere (reject if labor/trabalhista)
2. Final judgment status (transitado em julgado)
3. Execution phase confirmation
4. Condemnation value (minimum R$ 1,000)
5. Essential documents presence
6. Any disqualifying factors (death without inventory, delegation without reserve)

Base your decision on facts from the documents and movements provided."""

    def __init__(self):
        """Initialize verification use case."""
        self.llm_adapter = LLMAdapter()
        self.policy_service = PolicyVerificationService()
    
    def _prepare_policy_context(self) -> str:
        """Prepare policy rules as context for LLM."""
        rules = BusinessPolicy.get_all_rules()
        context = "COMPANY POLICIES:\n"
        for rule in rules:
            context += f"- {rule.policy_id}: {rule.description} [Severity: {rule.severity}]\n"
        return context
    
    def _prepare_process_data(self, process: Processo) -> str:
        """Prepare process data for LLM analysis."""
        # Serialize key information
        data = {
            "process_number": process.numeroProcesso,
            "class": process.classe,
            "court": process.orgaoJulgador,
            "sphere": process.esfera,
            "subject": process.assunto,
            "condemnation_value": process.valorCondenacao,
            "free_justice": process.justicaGratuita,
            "documents": [
                {
                    "name": doc.nome,
                    "filing_date": doc.dataHoraJuntada.isoformat(),
                    "preview": doc.texto[:500] if len(doc.texto) > 500 else doc.texto
                }
                for doc in process.documentos
            ],
            "movements": [
                {
                    "date": mov.dataHora.isoformat(),
                    "description": mov.descricao
                }
                for mov in process.movimentos
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _parse_llm_response(self, response: str) -> dict:
        """Parse LLM response."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing LLM response: {e}")
        
        # Fallback if JSON parsing fails
        return {
            "decision": "incomplete",
            "rationale": "Could not parse LLM response",
            "internal_analysis": response
        }
    
    async def execute(self, request: ProcessVerificationRequest) -> ProcessVerificationResponse:
        """
        Execute verification process.
        
        Args:
            request: Process verification request
            
        Returns:
            Process verification response
        """
        process = request.process
        
        logger.info(
            f"Processing verification request",
            extra={"extra_fields": {"process_number": process.numeroProcesso}}
        )
        
        try:
            # First, use policy service for deterministic checks
            decision, rationale, references = self.policy_service.verify_process(process)
            
            # If decision is determined, return it
            # (No need for LLM for clear rejections/incompletions)
            if decision in [DecisionStatus.REJECTED, DecisionStatus.INCOMPLETE]:
                logger.info(
                    "Decision determined by policy rules",
                    extra={"extra_fields": {"decision": decision}}
                )
                return ProcessVerificationResponse(
                    decision=decision,
                    rationale=rationale,
                    references=references,
                    process_number=process.numeroProcesso
                )
            
            # For approved cases, optionally use LLM for detailed analysis
            # (Currently using policy service only for deterministic decisions)
            logger.info(
                "Process verification completed",
                extra={"extra_fields": {"decision": decision}}
            )
            
            return ProcessVerificationResponse(
                decision=decision,
                rationale=rationale,
                references=references,
                process_number=process.numeroProcesso
            )
        
        except Exception as e:
            logger.error(
                f"Error during verification: {str(e)}",
                extra={"extra_fields": {"process_number": process.numeroProcesso}}
            )
            
            # Return incomplete on error
            error_ref = PolicyReference(
                policy_id="ERROR",
                explanation=f"Verification error: {str(e)}"
            )
            
            return ProcessVerificationResponse(
                decision=DecisionStatus.INCOMPLETE,
                rationale=f"Could not complete verification: {str(e)}",
                references=[error_ref],
                process_number=process.numeroProcesso
            )

