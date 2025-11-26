from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Optional
import uuid
from app.schemas.responses import (
    ProcessoInputSchema,
    VerificacaoResponseSchema,
    BatchVerificacaoRequestSchema,
    BatchVerificacaoResponseSchema
)
from app.use_cases.verify_process import VerifyProcessUseCase
from app.external.llm_service import LLMService
from app.repositories.process_repository import get_repository
from app.external.langsmith_client import langsmith_client
from app.utils.logger import get_logger
import time


logger = get_logger("verify_route")

router = APIRouter(prefix="/verify", tags=["verification"])

# Shared instances
llm_service = LLMService()
verify_use_case = VerifyProcessUseCase(llm_service)


@router.post("/", response_model=VerificacaoResponseSchema)
async def verify_process(
    processo: ProcessoInputSchema,
    request_id: Optional[str] = None
) -> VerificacaoResponseSchema:
    """
    Verify a judicial process.
    
    - **numeroProcesso**: Unique process number
    - **esfera**: Federal, State or Labor
    - **valorCondenacao**: Condemnation value in R$
    - **documentos**: List of process documents
    
    Return structured decision (approved, rejected, incomplete)
    with justification based on company policies.
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    
    try:
        logger.info(
            "Verification request received",
            extra={"extra_data": {
                "request_id": request_id,
                "numero_processo": processo.numeroProcesso
            }}
        )
        
        # Convert schema to dict to pass to use case
        processo_dict = processo.model_dump()
        
        # Execute use case
        resultado = await verify_use_case.execute(
            processo_dict,
            request_id=request_id
        )
        
        return resultado
    
    except ValueError as e:
        logger.warning(
            "Validation error during verification",
            extra={"extra_data": {
                "request_id": request_id,
                "error": str(e)
            }}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error during verification",
            extra={"extra_data": {
                "request_id": request_id,
                "error": str(e)
            }}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing verification"
        )


@router.post("/batch", response_model=BatchVerificacaoResponseSchema)
async def verify_batch(
    batch_request: BatchVerificacaoRequestSchema,
    background_tasks: BackgroundTasks
) -> BatchVerificacaoResponseSchema:
    """
    Verify multiple processes in batch.
    
    Process up to 50 processes simultaneously.
    Return aggregated result with statistics.
    """
    batch_id = str(uuid.uuid4())
    
    logger.info(
        "Batch request received",
        extra={"extra_data": {
            "batch_id": batch_id,
            "total": len(batch_request.processos)
        }}
    )
    
    start_time = time.time()
    resultados = []
    erros = 0
    
    for processo in batch_request.processos:
        try:
            request_id = f"{batch_id}-{len(resultados)}"
            processo_dict = processo.model_dump()
            
            resultado = await verify_use_case.execute(
                processo_dict,
                request_id=request_id
            )
            resultados.append(resultado)
        
        except Exception as e:
            logger.error(
                "Error processing process in batch",
                extra={"extra_data": {
                    "batch_id": batch_id,
                    "erro_indice": len(resultados),
                    "error": str(e)
                }}
            )
            erros += 1
    
    tempo_total_ms = int((time.time() - start_time) * 1000)
    
    # Register in LangSmith
    langsmith_client.log_batch_verification(
        batch_id=batch_id,
        total=len(batch_request.processos),
        processados=len(resultados),
        erros=erros,
        tempo_total_ms=tempo_total_ms
    )
    
    logger.info(
        "Batch verification completed",
        extra={"extra_data": {
            "batch_id": batch_id,
            "total": len(batch_request.processos),
            "processados": len(resultados),
            "erros": erros,
            "tempo_total_ms": tempo_total_ms
        }}
    )
    
    return BatchVerificacaoResponseSchema(
        batch_id=batch_id,
        total=len(batch_request.processos),
        processados=len(resultados),
        erros=erros,
        resultados=resultados,
        tempo_total_ms=tempo_total_ms
    )