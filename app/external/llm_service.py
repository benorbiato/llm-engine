"""
LLM Service - LangChain wrapper for Claude with structured JSON output
Alternative version using LangChain instead of direct Anthropic
"""
import json
import time
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from app.config import settings
from app.utils.logger import get_logger
from app.domain.policies import POLICIES


logger = get_logger("llm_service")


class LLMService:
    """
    LangChain wrapper around OpenAI for structured verification calls
    """
    
    def __init__(self):
        """
        Initialize LLM Service with LangChain
        """
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.1,
            max_tokens=settings.max_tokens
        )
        self._prompt_version = "1.0-openai"
        self._setup_chain()
    
    def _setup_chain(self):
        """Setup the LangChain prompt and parser"""
        
        prompt_template = """Você é um especialista em análise de crédito judicial. 
Sua tarefa é avaliar se um processo deve ser adquirido de acordo com as políticas da empresa.

# Políticas de Verificação de Crédito Judicial

{policies_context}

## Dados do Processo
```json
{processo_json}
```

## Instruções

1. Analise o processo contra TODAS as políticas acima
2. Determine uma das três decisões: "approved", "rejected" ou "incomplete"
3. Justifique sua decisão de forma clara e concisa
4. Cite as políticas relevantes (IDs: POL-1, POL-2, etc)
5. Estimar confiança de 0 a 1

## Responda APENAS em JSON válido:

{{
  "decision": "approved|rejected|incomplete",
  "rationale": "Justificativa clara da decisão",
  "citations": ["POL-X", "POL-Y"],
  "confidence": 0.95,
  "policy_analysis": {{
    "elegibilidade": {{"cumpre": true, "motivo": "..."}},
    "exclusoes": {{"cumpre": true, "motivo": "..."}},
    "documentacao": {{"cumpre": true, "motivo": "..."}}
  }}
}}
"""
        
        self.prompt = PromptTemplate(
            input_variables=["policies_context", "processo_json"],
            template=prompt_template
        )
        
        self.parser = JsonOutputParser()
        
        # Create chain: prompt -> llm -> parser
        self.chain = self.prompt | self.llm | self.parser
    
    def _build_policies_context(self) -> str:
        """Build policies context in a readable format."""
        context = ""
        
        for policy in POLICIES:
            context += f"## {policy.id}: {policy.title}\n"
            context += f"**Categoria**: {policy.category}\n"
            context += f"**Descrição**: {policy.description}\n\n"
        
        return context
    
    async def verify_process(
        self,
        processo_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a judicial process against policies using LangChain + Anthropic
        
        Args:
            processo_data: Process data
            request_id: Unique request ID
        
        Returns:
            Dictionary with verification result
        """
        start_time = time.time()
        
        try:
            # Format inputs
            policies_context = self._build_policies_context()
            processo_json = json.dumps(processo_data, indent=2, default=str, ensure_ascii=False)
            
            logger.info(
                "Starting LLM verification with OpenAI",
                extra={"extra_data": {
                    "request_id": request_id,
                    "numero_processo": processo_data.get("numeroProcesso"),
                    "llm_framework": "openai"
                }}
            )
            
            # Run chain (invoke is sync, but we're in async context)
            result = self.chain.invoke({
                "policies_context": policies_context,
                "processo_json": processo_json
            })
            
            # Ensure result is a dict (parser returns dict)
            if not isinstance(result, dict):
                result = json.loads(str(result))
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(
                "LLM verification completed successfully",
                extra={"extra_data": {
                    "request_id": request_id,
                    "decision": result.get("decision"),
                    "processing_time_ms": processing_time,
                    "confidence": result.get("confidence"),
                    "llm_framework": "openai"
                }}
            )
            
            return {
                "decision": result.get("decision"),
                "rationale": result.get("rationale"),
                "citations": result.get("citations", []),
                "confidence": result.get("confidence", 0.0),
                "policy_analysis": result.get("policy_analysis", {}),
                "processing_time_ms": processing_time,
                "model_used": settings.openai_model,
                "llm_framework": "openai"
            }
            
        except OutputParserException as e:
            logger.error(
                "Error parsing LLM response with OpenAI",
                extra={"extra_data": {
                    "request_id": request_id,
                    "error": str(e),
                    "llm_framework": "openai"
                }}
            )
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(
                "Unexpected error during LLM verification",
                extra={"extra_data": {
                    "request_id": request_id,
                    "error": str(e),
                    "processing_time_ms": processing_time,
                    "llm_framework": "openai"
                }}
            )
            raise
    
    def get_prompt_version(self) -> str:
        """Return current prompt version."""
        return self._prompt_version