from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class Document(BaseModel):
    """
    Represents a document (e.g., sentence, certificate, calculations) attached to the process.
    """
    id: str
    
    joined_at: datetime = Field(alias="dataHoraJuntada")
    
    name: str = Field(alias="nome")
    
    text_content: str = Field(alias="texto")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Movement(BaseModel):
    """
    Represents a movement or procedural action in the judicial process.
    """
    occurred_at: datetime = Field(alias="dataHora")
    
    description: str = Field(alias="descricao")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Honoraries(BaseModel):
    """
    Represents the different types of honoraries, required by POL-7.
    """
    contractual: Optional[float] = Field(None, alias="contratuais")
    
    expert_witness: Optional[float] = Field(None, alias="periciais")
    
    success_fees: Optional[float] = Field(None, alias="sucumbenciais")
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Process(BaseModel):
    """
    The main entity representing the judicial process data structure.
    All fields use English snake_case but accept the Portuguese keys from the input schema
    via Pydantic's alias functionality.
    """
    process_number: str = Field(alias="numeroProcesso")
    
    class_name: str = Field(alias="classe")
    
    judgment_body: str = Field(alias="orgaoJulgador")
    
    last_distribution_at: datetime = Field(alias="ultimaDistribuicao")
    
    subject: str = Field(alias="assunto")
    
    is_confidential: bool = Field(alias="segredoJustica")
    
    is_free_justice: bool = Field(alias="justicaGratuita")
    
    court_acronym: str = Field(alias="siglaTribunal")
    
    jurisdiction: str = Field(alias="esfera")
    
    case_value: Optional[float] = Field(None, alias="valorCausa")
    
    condemnation_value: Optional[float] = Field(None, alias="valorCondenacao")
    
    documents: List[Document] = Field(alias="documentos")
    
    movements: List[Movement] = Field(alias="movimentos")
    
    honoraries: Optional[Honoraries] = Field(None, alias="honorarios")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)