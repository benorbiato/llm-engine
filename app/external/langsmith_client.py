import os
from typing import Optional, Dict, Any
from datetime import datetime
from app.config import settings
from app.utils.logger import get_logger


logger = get_logger("langsmith")


class LangSmithClient:
    """Client for integration with LangSmith."""
    
    def __init__(self):
        self.enabled = settings.enable_langsmith and bool(settings.langsmith_api_key)
        self.project_name = settings.langsmith_project_name
        
        if self.enabled:
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            
            logger.info(
                "LangSmith habilitado",
                extra={"extra_data": {"project": self.project_name}}
            )
        else:
            logger.info("LangSmith desabilitado")
    
    def log_verification(
        self,
        numero_processo: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        model_used: str,
        processing_time_ms: int
    ) -> Optional[str]:
        """
        Register a verification in LangSmith.
        
        Args:
            numero_processo: Process number
            input_data: Input data
            output_data: Output data
            model_used: LLM model used
            processing_time_ms: Processing time
        
        Returns:
            ID of the run in LangSmith (if enabled)
        """
        if not self.enabled:
            return None
        
        try:
            # Here it would be integrated with LangChain/LangSmith
            # For now, only logging
            logger.info(
                "Verification registered in LangSmith",
                extra={"extra_data": {
                    "numero_processo": numero_processo,
                    "decision": output_data.get("decision"),
                    "model": model_used,
                    "processing_time_ms": processing_time_ms
                }}
            )
            return None  # Placeholder for run ID
        
        except Exception as e:
            logger.error(
                "Error registering in LangSmith",
                extra={"extra_data": {"error": str(e)}}
            )
            return None
    
    def log_batch_verification(
        self,
        batch_id: str,
        total: int,
        processados: int,
        erros: int,
        tempo_total_ms: int
    ) -> None:
        """Register batch verification in LangSmith."""
        if not self.enabled:
            return
        
        try:
            logger.info(
                "Batch registered in LangSmith",
                extra={"extra_data": {
                    "batch_id": batch_id,
                    "total": total,
                    "processados": processados,
                    "erros": erros,
                    "tempo_total_ms": tempo_total_ms
                }}
            )
        except Exception as e:
            logger.error(
                "Error registering batch in LangSmith",
                extra={"extra_data": {"error": str(e)}}
            )


# Global instance
langsmith_client = LangSmithClient()