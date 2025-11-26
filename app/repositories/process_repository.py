from typing import Dict, List, Optional
from datetime import datetime
from app.domain.entities import ProcessoVerificacao, DecisaoJurisdica
from app.utils.logger import get_logger


logger = get_logger("repository")


class ProcessoRepository:
    """Repository to store process verifications (in memory)."""
    
    def __init__(self):
        self._processos: Dict[str, ProcessoVerificacao] = {}
        self._indices_metadata: Dict[str, List[str]] = {}
    
    def save(self, verificacao: ProcessoVerificacao) -> None:
        """Save a process verification."""
        numero = verificacao.numeroProcesso
        self._processos[numero] = verificacao
        
        logger.info(
            "Verification saved in repository",
            extra={"extra_data": {"numero_processo": numero}}
        )
    
    def get_by_numero(self, numero_processo: str) -> Optional[ProcessoVerificacao]:
        """Retrieve a verification by process number."""
        return self._processos.get(numero_processo)
    
    def get_all(self) -> List[ProcessoVerificacao]:
        """Return all verifications."""
        return list(self._processos.values())
    
    def get_by_decision(self, decision: str) -> List[ProcessoVerificacao]:
        """Retrieve verifications by decision type."""
        return [
            v for v in self._processos.values()
            if v.decisao.resultado == decision
        ]
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[ProcessoVerificacao]:
        """Retrieve verifications by date range."""
        return [
            v for v in self._processos.values()
            if start_date <= v.processado_em <= end_date
        ]
    
    def get_statistics(self) -> Dict:
        """Return general statistics."""
        verificacoes = list(self._processos.values())
        
        if not verificacoes:
            return {
                "total": 0,
                "approved": 0,
                "rejected": 0,
                "incomplete": 0,
                "taxa_aprovacao": 0.0,
                "tempo_medio_ms": 0.0
            }
        
        total = len(verificacoes)
        approved = sum(1 for v in verificacoes if v.decisao.resultado == "approved")
        rejected = sum(1 for v in verificacoes if v.decisao.resultado == "rejected")
        incomplete = sum(1 for v in verificacoes if v.decisao.resultado == "incomplete")
        
        tempo_medio = (
            sum(v.tempo_processamento_ms or 0 for v in verificacoes) / total
            if total > 0 else 0
        )
        
        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "incomplete": incomplete,
            "taxa_aprovacao": (approved / total * 100) if total > 0 else 0.0,
            "tempo_medio_ms": tempo_medio
        }
    
    def get_policy_usage(self) -> Dict[str, int]:
        """Return policy usage count."""
        policy_count: Dict[str, int] = {}
        
        for v in self._processos.values():
            for policy_id in v.decisao.citacoes:
                policy_count[policy_id] = policy_count.get(policy_id, 0) + 1
        
        return dict(sorted(
            policy_count.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def count(self) -> int:
        """Return total number of stored verifications."""
        return len(self._processos)
    
    def clear(self) -> None:
        """Clear repository (only for tests)."""
        self._processos.clear()
        logger.info("Repository cleared")


# Singleton instance
_repository_instance: Optional[ProcessoRepository] = None


def get_repository() -> ProcessoRepository:
    """Factory to get singleton instance of the repository."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = ProcessoRepository()
    return _repository_instance