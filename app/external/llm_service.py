"""
LLM Service - LangChain wrapper for Groq with structured JSON output
Using Groq API for high-speed LLM inference
"""
import json
import time
from typing import Dict, Any, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from groq import RateLimitError, AuthenticationError

from app.config import settings
from app.utils.logger import get_logger
from app.domain.policies import POLICIES


logger = get_logger("llm_service")


class APICreditsExhaustedError(Exception):
    """Raised when API has exhausted credits/rate limit."""
    pass


class APIAuthenticationError(Exception):
    """Raised when API key is invalid or expired."""
    pass


class LLMService:
    """
    LangChain wrapper around Groq for structured verification calls
    """
    
    def __init__(self):
        """
        Initialize LLM Service with LangChain + Groq
        """
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0.1,
            max_tokens=settings.max_tokens
        )
        self._prompt_version = "1.0-groq"
        self._setup_chain()
    
    def _setup_chain(self):
        """Setup the LangChain prompt and parser"""
        
        # Otimizado: Prompt mais conciso para economizar tokens
        prompt_template = """Você é especialista em análise de crédito judicial.
Avalie se o processo deve ser adquirido conforme políticas.

# Políticas
{policies_context}

## Processo
```json
{processo_json}
```

## Análise Rápida
- Verifique elegibilidade, exclusões, documentação
- Decida: approved|rejected|incomplete
- Justifique brevemente (máx 2-3 frases)
- Cite políticas relevantes (POL-1, etc)
- Confiança de 0 a 1

## Responda em JSON:
{{
  "decision": "approved",
  "rationale": "Justificativa concisa",
  "citations": ["POL-1"],
  "confidence": 0.9,
  "policy_analysis": {{
    "elegibilidade": {{"cumpre": true, "motivo": "Atende critério"}},
    "exclusoes": {{"cumpre": true, "motivo": "Sem exclusões"}},
    "documentacao": {{"cumpre": true, "motivo": "Completa"}}
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
                "Starting LLM verification with Groq",
                extra={"extra_data": {
                    "request_id": request_id,
                    "numero_processo": processo_data.get("numeroProcesso"),
                    "llm_framework": "groq"
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
                    "llm_framework": "groq"
                }}
            )
            
            return {
                "decision": result.get("decision"),
                "rationale": result.get("rationale"),
                "citations": result.get("citations", []),
                "confidence": result.get("confidence", 0.0),
                "policy_analysis": result.get("policy_analysis", {}),
                "processing_time_ms": processing_time,
                "model_used": settings.groq_model,
                "llm_framework": "groq"
            }
            
        except OutputParserException as e:
            logger.error(
                "Error parsing LLM response with Groq",
                extra={"extra_data": {
                    "request_id": request_id,
                    "error": str(e),
                    "llm_framework": "groq"
                }}
            )
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        except RateLimitError as e:
            # Groq rate limit or quota exceeded
            processing_time = int((time.time() - start_time) * 1000)
            error_msg = str(e).lower()
            
            logger.error(
                "Groq Rate Limit/Credits Exceeded",
                extra={"extra_data": {
                    "request_id": request_id,
                    "error": str(e),
                    "processing_time_ms": processing_time,
                    "error_type": "rate_limit"
                }}
            )
            
            raise APICreditsExhaustedError(
                f"API de crédito esgotado. Motivo: {str(e)}. "
                f"Por favor, adicione créditos à sua conta Groq ou aguarde o reset do rate limit."
            )
        
        except AuthenticationError as e:
            # Invalid API key or expired
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(
                "Groq Authentication Failed",
                extra={"extra_data": {
                    "request_id": request_id,
                    "error": "Invalid API key or authentication failed",
                    "processing_time_ms": processing_time,
                    "error_type": "auth_error"
                }}
            )
            
            raise APIAuthenticationError(
                "Falha na autenticação com a API Groq. "
                "Verifique se a chave de API é válida e tem permissões ativas."
            )
        
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_str = str(e).lower()
            
            # Check for common API error patterns
            if "quota" in error_str or "insufficient_quota" in error_str:
                logger.error(
                    "Groq Quota Exceeded",
                    extra={"extra_data": {
                        "request_id": request_id,
                        "error": str(e),
                        "processing_time_ms": processing_time,
                        "error_type": "quota_error"
                    }}
                )
                raise APICreditsExhaustedError(
                    "Sua cota de crédito na API foi excedida. "
                    "Adicione mais créditos ou aguarde a renovação mensal."
                )
            
            logger.error(
                "Unexpected error during LLM verification",
                extra={"extra_data": {
                    "request_id": request_id,
                    "error": str(e),
                    "processing_time_ms": processing_time,
                    "llm_framework": "groq"
                }}
            )
            raise
    
    def get_prompt_version(self) -> str:
        """Return current prompt version."""
        return self._prompt_version