from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.domain.policies import Decision


class Documento(BaseModel):
    """Document of a judicial process."""
    id: str
    dataHoraJuntada: datetime
    nome: str
    texto: str


class Movimento(BaseModel):
    """Processual movement."""
    dataHora: datetime
    descricao: str


class Processo(BaseModel):
    """Judicial process entity."""
    numeroProcesso: str
    classe: str
    orgaoJulgador: str
    ultimaDistribuicao: datetime
    assunto: str
    segredoJustica: bool
    justicaGratuita: bool
    siglaTribunal: str
    esfera: str
    documentos: List[Documento] = Field(default_factory=list)
    movimentos: List[Movimento] = Field(default_factory=list)
    valorCausa: Optional[float] = None
    valorCondenacao: Optional[float] = None


class Honorarios(BaseModel):
    """Fees of a process."""
    contratuais: Optional[float] = None
    periciais: Optional[float] = None
    sucumbenciais: Optional[float] = None


class DecisaoJurisdica(BaseModel):
    """Judicial decision of the verification."""
    resultado: Decision
    justificativa: str
    citacoes: List[str] = Field(default_factory=list)
    confianca: Optional[float] = Field(default=None, ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessoVerificacao(BaseModel):
    """Complete result of the process verification."""
    numeroProcesso: str
    decisao: DecisaoJurisdica
    processado_em: datetime = Field(default_factory=datetime.utcnow)
    tempo_processamento_ms: Optional[int] = None
    versao_politica: str = "1.0"
    versao_llm: str = "1.0"