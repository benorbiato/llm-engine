from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.domain.policies import Decision


class DocumentoSchema(BaseModel):
    """Document schema."""
    id: str
    dataHoraJuntada: datetime
    nome: str
    texto: str
    
    model_config = ConfigDict(from_attributes=True)


class MovimentoSchema(BaseModel):
    """Processual movement schema."""
    dataHora: datetime
    descricao: str
    
    model_config = ConfigDict(from_attributes=True)


class ProcessoInputSchema(BaseModel):
    """Process input schema."""
    numeroProcesso: str
    classe: str
    orgaoJulgador: str
    ultimaDistribuicao: datetime
    assunto: str
    segredoJustica: bool = False
    justicaGratuita: bool = False
    siglaTribunal: str
    esfera: str
    valorCausa: Optional[float] = None
    valorCondenacao: Optional[float] = None
    documentos: List[DocumentoSchema] = Field(default_factory=list)
    movimentos: List[MovimentoSchema] = Field(default_factory=list)
    honorarios: Optional[Dict[str, Optional[float]]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "numeroProcesso": "0004587-00.2021.4.05.8100",
                "classe": "Cumprimento de Sentença contra a Fazenda Pública",
                "orgaoJulgador": "19ª VARA FEDERAL - SOBRAL/CE",
                "ultimaDistribuicao": "2024-11-18T23:15:44.130Z",
                "assunto": "Rural (Art. 48/51)",
                "segredoJustica": False,
                "justicaGratuita": True,
                "siglaTribunal": "TRF5",
                "esfera": "Federal",
                "valorCausa": 67592,
                "valorCondenacao": 67592,
                "honorarios": {
                    "contratuais": 6000,
                    "periciais": 1200,
                    "sucumbenciais": 3000
                }
            }
        }
    )


class DecisaoSchema(BaseModel):
    """Judicial decision schema."""
    decision: Decision
    rationale: str
    citations: List[str] = Field(default_factory=list)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    
    model_config = ConfigDict(from_attributes=True)


class VerificacaoResponseSchema(BaseModel):
    """Verification response schema."""
    numeroProcesso: str
    decision: Decision
    rationale: str
    citations: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None
    processedAt: datetime = Field(default_factory=datetime.utcnow)
    processingTimeMs: int
    policyVersion: str = "1.0"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "numeroProcesso": "0004587-00.2021.4.05.8100",
                "decision": "approved",
                "rationale": "Processo cumpre todos os requisitos: trânsito em julgado comprovado, fase de execução iniciada, valor de condenação acima do mínimo.",
                "citations": ["POL-1", "POL-2"],
                "confidence": 0.95,
                "processedAt": "2024-11-25T10:30:00Z",
                "processingTimeMs": 2345,
                "policyVersion": "1.0"
            }
        }
    )


class ProcessoHistoricoSchema(BaseModel):
    """Process history schema."""
    numeroProcesso: str
    ultimaVerificacao: Optional[datetime] = None
    verificacoes: int = 0
    ultimaDecisao: Optional[Decision] = None
    historico: List[VerificacaoResponseSchema] = Field(default_factory=list)


class BatchVerificacaoRequestSchema(BaseModel):
    """Batch verification request schema."""
    processos: List[ProcessoInputSchema]
    prioridade: str = "normal"
    
    def __init__(self, **data):
        super().__init__(**data)
        if len(self.processos) == 0:
            raise ValueError("Pelo menos um processo é necessário")


class BatchVerificacaoResponseSchema(BaseModel):
    """Batch verification response schema."""
    batch_id: str
    total: int
    processados: int
    erros: int
    resultados: List[VerificacaoResponseSchema]
    tempo_total_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsSchema(BaseModel):
    """Analytics schema."""
    total_verificacoes: int
    taxa_aprovacao: float
    taxa_rejeicao: float
    taxa_incompletos: float
    tempo_medio_ms: float
    processos_por_esfera: Dict[str, int]
    politicas_mais_citadas: List[tuple[str, int]]
    periodo: Optional[str] = None