"""
Domain entities for judicial processes.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Documento(BaseModel):
    """Document entity within a judicial process."""
    id: str = Field(..., description="Unique document identifier")
    dataHoraJuntada: datetime = Field(..., description="Document filing date and time")
    nome: str = Field(..., description="Document name")
    texto: str = Field(..., description="Document content/text")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "DOC-1-1",
                "dataHoraJuntada": "2023-09-10T10:12:05.000",
                "nome": "Sentença de Mérito",
                "texto": "PODER JUDICIÁRIO..."
            }
        }


class Movimento(BaseModel):
    """Movement/action entity within a judicial process."""
    dataHora: datetime = Field(..., description="Date and time of movement")
    descricao: str = Field(..., description="Movement description")

    class Config:
        json_schema_extra = {
            "example": {
                "dataHora": "2024-01-20T11:22:33.000",
                "descricao": "Iniciado cumprimento definitivo de sentença."
            }
        }


class Honorarios(BaseModel):
    """Fees/honorarios entity."""
    contratuais: Optional[float] = Field(None, description="Contractual fees")
    periciais: Optional[float] = Field(None, description="Expert fees")
    sucumbenciais: Optional[float] = Field(None, description="Litigation fees")

    class Config:
        json_schema_extra = {
            "example": {
                "contratuais": 6000,
                "periciais": 1200,
                "sucumbenciais": 3000
            }
        }


class Processo(BaseModel):
    """Judicial process entity - main domain model."""
    numeroProcesso: str = Field(..., description="Judicial process number")
    classe: str = Field(..., description="Process class/type")
    orgaoJulgador: str = Field(..., description="Court/judicial body")
    ultimaDistribuicao: datetime = Field(..., description="Last distribution date/time")
    assunto: str = Field(..., description="Process subject")
    segredoJustica: bool = Field(..., description="Secret justice indicator")
    justicaGratuita: bool = Field(..., description="Free justice indicator")
    siglaTribunal: str = Field(..., description="Court abbreviation")
    esfera: str = Field(..., description="Judicial sphere (Federal, Estadual, Trabalhista)")
    documentos: List[Documento] = Field(..., description="Associated documents")
    movimentos: List[Movimento] = Field(..., description="Process movements")
    valorCondenacao: Optional[float] = Field(None, description="Condemnation value")
    honorarios: Optional[Honorarios] = Field(None, description="Associated fees")
    valorCausa: Optional[float] = Field(None, description="Case value")

    class Config:
        json_schema_extra = {
            "example": {
                "numeroProcesso": "0001234-56.2023.4.05.8100",
                "classe": "Cumprimento de Sentença contra a Fazenda Pública",
                "orgaoJulgador": "19ª VARA FEDERAL - SOBRAL/CE",
                "ultimaDistribuicao": "2024-11-18T23:15:44.130Z",
                "assunto": "Rural (Art. 48/51)",
                "segredoJustica": False,
                "justicaGratuita": True,
                "siglaTribunal": "TRF5",
                "esfera": "Federal",
                "documentos": [],
                "movimentos": [],
                "valorCondenacao": 67592
            }
        }
