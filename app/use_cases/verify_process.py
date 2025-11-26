import uuid
import time
from typing import Dict, Any
from datetime import datetime
from app.external.llm_service import LLMService
from app.external.langsmith_client import langsmith_client
from app.repositories.process_repository import get_repository
from app.schemas.responses import VerificacaoResponseSchema
from app.domain.entities import ProcessoVerificacao, DecisaoJurisdica
from app.utils.logger import get_logger


logger = get_logger("verify_process_use_case")


class VerifyProcessUseCase:
    """Use case for process verification."""
    
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        self.repository = get_repository()
    
    async def execute(
        self,
        processo_data: Dict[str, Any],
        request_id: str = None
    ) -> VerificacaoResponseSchema:
        """
        Execute a process verification.
        
        Args:
            processo_data: Process data
            request_id: Unique request ID
        
        Returns:
            Response with decision
        """
        if not request_id:
            request_id = str(uuid.uuid4())
        
        numero_processo = processo_data.get("numeroProcesso")
        start_time = time.time()
        
        logger.info(
            "Starting use case: process verification",
            extra={"extra_data": {
                "request_id": request_id,
                "numero_processo": numero_processo
            }}
        )
        
        try:
            # Call LLM service
            llm_result = await self.llm_service.verify_process(
                processo_data,
                request_id=request_id
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Create verification entity
            verificacao = ProcessoVerificacao(
                numeroProcesso=numero_processo,
                decisao=DecisaoJurisdica(
                    resultado=llm_result["decision"],
                    justificativa=llm_result["rationale"],
                    citacoes=llm_result["citations"],
                    confianca=llm_result.get("confidence"),
                    metadata={
                        "policy_analysis": llm_result.get("policy_analysis", {}),
                        "request_id": request_id
                    }
                ),
                tempo_processamento_ms=processing_time_ms,
                versao_llm=self.llm_service.get_prompt_version()
            )
            
            self.repository.save(verificacao)
            
            langsmith_client.log_verification(
                numero_processo=numero_processo,
                input_data=processo_data,
                output_data=llm_result,
                model_used=llm_result.get("model_used", "unknown"),
                processing_time_ms=processing_time_ms
            )
            
            response = VerificacaoResponseSchema(
                numeroProcesso=numero_processo,
                decision=llm_result["decision"],
                rationale=llm_result["rationale"],
                citations=llm_result["citations"],
                confidence=llm_result.get("confidence"),
                processingTimeMs=processing_time_ms,
                processedAt=datetime.utcnow()
            )
            
            logger.info(
                "Verification completed successfully",
                extra={"extra_data": {
                    "request_id": request_id,
                    "numero_processo": numero_processo,
                    "decision": response.decision,
                    "processing_time_ms": processing_time_ms
                }}
            )
            
            return response
        
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.error(
                "Error during process verification",
                extra={"extra_data": {
                    "request_id": request_id,
                    "numero_processo": numero_processo,
                    "error": str(e),
                    "processing_time_ms": processing_time_ms
                }}
            )
            
            raise