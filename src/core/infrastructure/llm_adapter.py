"""
LLM adapter for Claude API integration.
"""
from typing import Optional
import anthropic
from src.core.infrastructure.config import settings
from src.core.infrastructure.logger_service import logger


class LLMAdapter:
    """Adapter for Claude API interaction."""
    
    def __init__(self):
        """Initialize LLM adapter with Anthropic client."""
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info(
                "LLM Adapter initialized",
                extra={"extra_fields": {"model": self.model}}
            )
        else:
            self.client = None
            logger.warning(
                "LLM Adapter initialized without API key (demo mode)",
                extra={"extra_fields": {"model": self.model}}
            )
    
    def analyze_process(
        self,
        process_data: str,
        policy_context: str,
        prompt_template: str
    ) -> str:
        """
        Analyze judicial process using Claude LLM.
        
        Args:
            process_data: Serialized process data
            policy_context: Policy rules context
            prompt_template: Prompt template with placeholders
            
        Returns:
            LLM response (JSON formatted decision)
        """
        prompt = prompt_template.format(
            process_data=process_data,
            policy_context=policy_context
        )
        
        logger.info("Calling Claude API for process analysis")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response = message.content[0].text
            logger.info("LLM analysis completed successfully")
            return response
            
        except anthropic.APIError as e:
            logger.error(
                "Claude API error",
                extra={"extra_fields": {"error": str(e)}}
            )
            raise
    
    def generate_prompt(self, template: str, **kwargs) -> str:
        """
        Generate prompt from template.
        
        Args:
            template: Prompt template string
            **kwargs: Variables for template
            
        Returns:
            Formatted prompt
        """
        return template.format(**kwargs)

