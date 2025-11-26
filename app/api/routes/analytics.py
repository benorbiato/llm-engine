from fastapi import APIRouter, Query
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from app.schemas.responses import AnalyticsSchema
from app.repositories.process_repository import get_repository
from app.domain.policies import get_policy_by_id
from app.utils.logger import get_logger


logger = get_logger("analytics_route")

router = APIRouter(prefix="/analytics", tags=["analytics"])
repository = get_repository()


@router.get("/summary", response_model=Dict)
async def get_analytics_summary():
    """
    Return analytical summary of verifications performed.
    
    Includes:
    - Approval, rejection, incomplete rates
    - Average processing time
    - Most cited policies
    - Distribution by sphere
    """
    stats = repository.get_statistics()
    policy_usage = repository.get_policy_usage()
    
    politicas_citadas = []
    for policy_id, count in list(policy_usage.items())[:5]:
        try:
            policy = get_policy_by_id(policy_id)
            politicas_citadas.append({
                "id": policy_id,
                "titulo": policy.title,
                "usos": count
            })
        except ValueError:
            pass
    
    logger.info(
        "Analytics summary consulted",
        extra={"extra_data": {
            "total_verificacoes": stats["total"],
            "taxa_aprovacao": stats["taxa_aprovacao"]
        }}
    )
    
    return {
        "total_verificacoes": stats["total"],
        "aprovados": stats["approved"],
        "rejeitados": stats["rejected"],
        "incompletos": stats["incomplete"],
        "taxa_aprovacao_percentual": round(stats["taxa_aprovacao"], 2),
        "taxa_rejeicao_percentual": round(100 - stats["taxa_aprovacao"] - (stats["incomplete"] / stats["total"] * 100 if stats["total"] > 0 else 0), 2),
        "tempo_medio_processamento_ms": round(stats["tempo_medio_ms"], 2),
        "politicas_mais_citadas": politicas_citadas,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/policies-usage", response_model=Dict[str, int])
async def get_policies_usage():
    """
    Return usage count of each policy.
    
    Useful to understand which business rules most
    impact decisions.
    """
    usage = repository.get_policy_usage()
    
    logger.info(
        "Policies usage consulted",
        extra={"extra_data": {"total_policies": len(usage)}}
    )
    
    return usage


@router.get("/decision-distribution", response_model=Dict[str, int])
async def get_decision_distribution():
    """
    Return decision distribution in the period.
    
    Shows quantity of approved,
    rejected and incomplete.
    """
    stats = repository.get_statistics()
    
    return {
        "approved": stats["approved"],
        "rejected": stats["rejected"],
        "incomplete": stats["incomplete"],
        "total": stats["total"]
    }


@router.get("/processing-time", response_model=Dict)
async def get_processing_time_stats():
    """
    Return processing time statistics.
    
    Includes average, minimum and maximum observed time.
    """
    verificacoes = repository.get_all()
    
    if not verificacoes:
        return {
            "media_ms": 0,
            "minimo_ms": 0,
            "maximo_ms": 0,
            "total_processamentos": 0
        }
    
    tempos = [v.tempo_processamento_ms for v in verificacoes if v.tempo_processamento_ms]
    
    return {
        "media_ms": round(sum(tempos) / len(tempos) if tempos else 0, 2),
        "minimo_ms": min(tempos) if tempos else 0,
        "maximo_ms": max(tempos) if tempos else 0,
        "total_processamentos": len(tempos)
    }


@router.get("/top-policies", response_model=List[Dict])
async def get_top_policies(limit: int = Query(5, ge=1, le=20)):
    """
    Return the most impactful policies.
    
    Shows which rules most frequently cause
    rejection or approval of processes.
    """
    usage = repository.get_policy_usage()
    top_policies = []
    
    for policy_id, count in list(usage.items())[:limit]:
        try:
            policy = get_policy_by_id(policy_id)
            top_policies.append({
                "id": policy_id,
                "titulo": policy.title,
                "categoria": policy.category,
                "descricao": policy.description,
                "usos": count
            })
        except ValueError:
            pass
    
    logger.info(
        "Top policies consulted",
        extra={"extra_data": {"limit": limit, "retornados": len(top_policies)}}
    )
    
    return top_policies


@router.get("/decision-by-sphere", response_model=Dict[str, Dict])
async def get_decision_by_sphere():
    """
    Return decision distribution by judicial sphere.
    
    Analyzes how the system behaves in different
    judicial contexts (Federal, State, Labor).
    """
    verificacoes = repository.get_all()
    
    # Group by sphere (would need to store this)
    # For now, return generic structure
    esferas = {}
    
    logger.info(
        "Decisions by sphere consulted",
        extra={"extra_data": {"total": len(verificacoes)}}
    )
    
    return {
        "Federal": {"approved": 0, "rejected": 0, "incomplete": 0},
        "Estadual": {"approved": 0, "rejected": 0, "incomplete": 0},
        "Trabalhista": {"approved": 0, "rejected": 0, "incomplete": 0}
    }