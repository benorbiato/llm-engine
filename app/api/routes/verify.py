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
from app.external.llm_service import LLMService, APICreditsExhaustedError, APIAuthenticationError
from app.repositories.process_repository import get_repository
from app.external.langsmith_client import langsmith_client
from app.utils.logger import get_logger
from app.utils.cache import verification_cache
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
        
        # 🚀 Check cache first to avoid unnecessary API calls
        cached_result = verification_cache.get(processo_dict)
        if cached_result:
            logger.info(
                "Returning cached verification result",
                extra={"extra_data": {
                    "request_id": request_id,
                    "numero_processo": processo.numeroProcesso,
                    "from_cache": True
                }}
            )
            return cached_result
        
        # Execute use case
        resultado = await verify_use_case.execute(
            processo_dict,
            request_id=request_id
        )
        
        # Cache the result for future requests
        verification_cache.set(processo_dict, resultado)
        
        return resultado
    
    except APICreditsExhaustedError as e:
        logger.error(
            "API Credits Exhausted",
            extra={"extra_data": {
                "request_id": request_id,
                "error": str(e)
            }}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "api_credits_exhausted",
                "message": str(e),
                "help": "Adicione créditos à sua conta Groq em https://console.groq.com/"
            }
        )
    
    except APIAuthenticationError as e:
        logger.error(
            "API Authentication Failed",
            extra={"extra_data": {
                "request_id": request_id,
                "error": str(e)
            }}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "api_authentication_failed",
                "message": str(e),
                "help": "Verifique sua chave de API Groq nas variáveis de ambiente"
            }
        )
    
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
    cached_count = 0
    api_calls = 0
    api_error: Optional[str] = None
    
    for processo in batch_request.processos:
        try:
            request_id = f"{batch_id}-{len(resultados)}"
            processo_dict = processo.model_dump()
            
            # 🚀 Check cache first
            cached_result = verification_cache.get(processo_dict)
            if cached_result:
                resultados.append(cached_result)
                cached_count += 1
                continue
            
            # Make API call only if not cached
            api_calls += 1
            resultado = await verify_use_case.execute(
                processo_dict,
                request_id=request_id
            )
            resultados.append(resultado)
            
            # Cache for future use
            verification_cache.set(processo_dict, resultado)
        
        except APICreditsExhaustedError as e:
            logger.error(
                "API Credits Exhausted in batch",
                extra={"extra_data": {
                    "batch_id": batch_id,
                    "erro_indice": len(resultados)
                }}
            )
            api_error = str(e)
            erros += 1
            break  # Stop processing batch when credits are exhausted
        
        except APIAuthenticationError as e:
            logger.error(
                "API Authentication Failed in batch",
                extra={"extra_data": {
                    "batch_id": batch_id,
                    "erro_indice": len(resultados)
                }}
            )
            api_error = str(e)
            erros += 1
            break  # Stop processing batch
        
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
            "cached": cached_count,
            "api_calls": api_calls,
            "tempo_total_ms": tempo_total_ms
        }}
    )
    
    response = BatchVerificacaoResponseSchema(
        batch_id=batch_id,
        total=len(batch_request.processos),
        processados=len(resultados),
        erros=erros,
        resultados=resultados,
        tempo_total_ms=tempo_total_ms
    )
    
    # Add error info if API failed
    if api_error:
        response.api_error = api_error
    
    return response