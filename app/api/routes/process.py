from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timedelta
from app.schemas.responses import (
    VerificacaoResponseSchema,
    ProcessoHistoricoSchema
)
from app.repositories.process_repository import get_repository
from app.utils.logger import get_logger


logger = get_logger("process_route")

router = APIRouter(prefix="/process", tags=["process"])
repository = get_repository()


@router.get("/{numero_processo}", response_model=ProcessoHistoricoSchema)
async def get_process_history(numero_processo: str):
    """
    Return history of all verifications of a process.
    
    Includes:
    - Last verification date
    - Total number of verifications
    - History of all decisions
    """
    verificacao = repository.get_by_numero(numero_processo)
    
    if not verificacao:
        logger.warning(
            "Process not found",
            extra={"extra_data": {"numero_processo": numero_processo}}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification found for {numero_processo}"
        )
    
    response = VerificacaoResponseSchema(
        numeroProcesso=verificacao.numeroProcesso,
        decision=verificacao.decisao.resultado,
        rationale=verificacao.decisao.justificativa,
        citations=verificacao.decisao.citacoes,
        confidence=verificacao.decisao.confianca,
        processingTimeMs=verificacao.tempo_processamento_ms or 0,
        processedAt=verificacao.processado_em
    )
    
    logger.info(
        "Process history consulted",
        extra={"extra_data": {"numero_processo": numero_processo}}
    )
    
    return ProcessoHistoricoSchema(
        numeroProcesso=numero_processo,
        ultimaVerificacao=verificacao.processado_em,
        verificacoes=1,  # Currently one verification per process
        ultimaDecisao=verificacao.decisao.resultado,
        historico=[response]
    )


@router.get("/", response_model=List[VerificacaoResponseSchema])
async def list_processes(
    decision: Optional[str] = Query(None, description="Filter by decision (approved/rejected/incomplete)"),
    limit: int = Query(100, ge=1, le=1000, description="Limit of results"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """
    List verifications with optional filters.
    
    Available filters:
    - **decision**: Decision type (approved, rejected, incomplete)
    - **limit**: Maximum of results
    - **offset**: Page number
    """
    try:
        if decision:
            verificacoes = repository.get_by_decision(decision)
        else:
            verificacoes = repository.get_all()
        
        # Apply pagination
        paginadas = verificacoes[offset:offset + limit]
        
        # Convert to response schemas
        resultados = [
            VerificacaoResponseSchema(
                numeroProcesso=v.numeroProcesso,
                decision=v.decisao.resultado,
                rationale=v.decisao.justificativa,
                citations=v.decisao.citacoes,
                confidence=v.decisao.confianca,
                processingTimeMs=v.tempo_processamento_ms or 0,
                processedAt=v.processado_em
            )
            for v in paginadas
        ]
        
        logger.info(
            "List of processes consulted",
            extra={"extra_data": {
                "total": len(verificacoes),
                "retornados": len(resultados),
                "decision_filter": decision
            }}
        )
        
        return resultados
    
    except ValueError as e:
        logger.warning(
            "Invalid filter in listing",
            extra={"extra_data": {"error": str(e)}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )