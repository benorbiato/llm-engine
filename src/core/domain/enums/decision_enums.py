from enum import Enum


class DecisionStatus(str, Enum):
    """Possible decision outcomes for process verification."""
    APPROVED = "approved"
    REJECTED = "rejected"
    INCOMPLETE = "incomplete"


class JudicialSphere(str, Enum):
    """Judicial sphere types."""
    FEDERAL = "Federal"
    ESTADUAL = "Estadual"
    TRABALHISTA = "Trabalhista"


class ProcessPhase(str, Enum):
    """Process phases."""
    TRANSITADO_JULGADO = "Transitado em Julgado"
    EXECUCAO = "Execução"
    CUMPRIMENTO_DEFINITIVO = "Cumprimento Definitivo"
    OUTRO = "Outro"

