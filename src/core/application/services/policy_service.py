"""
Verification service - core business logic.
"""
import json
from typing import List, Tuple
from datetime import datetime
from src.core.domain.entities import Processo, Documento
from src.core.domain.enums.decision_enums import DecisionStatus, JudicialSphere
from src.core.domain.policy import BusinessPolicy, PolicyRule
from src.core.infrastructure.logger_service import logger
from src.api.schemas import PolicyReference


class PolicyVerificationService:
    """Service for policy-based verification of judicial processes."""
    
    MINIMUM_CONDEMNATION_VALUE = 1000.0
    
    @staticmethod
    def check_sphere_rejection(process: Processo) -> Tuple[bool, List[PolicyReference]]:
        """Check if process is in rejected sphere (labor)."""
        references = []
        if process.esfera == JudicialSphere.TRABALHISTA.value:
            rule = BusinessPolicy.POL_4
            references.append(PolicyReference(
                policy_id=rule.policy_id,
                explanation=f"{rule.description} - Process is in labor sphere"
            ))
            return True, references
        return False, references
    
    @staticmethod
    def check_minimum_value(process: Processo) -> Tuple[bool, List[PolicyReference]]:
        """Check if condemnation value meets minimum threshold."""
        references = []
        if process.valorCondenacao is None:
            rule = BusinessPolicy.POL_2
            references.append(PolicyReference(
                policy_id=rule.policy_id,
                explanation=f"{rule.description} - Condemnation value not informed"
            ))
            return False, references
        
        if process.valorCondenacao < PolicyVerificationService.MINIMUM_CONDEMNATION_VALUE:
            rule = BusinessPolicy.POL_3
            references.append(PolicyReference(
                policy_id=rule.policy_id,
                explanation=f"{rule.description} - Value: R$ {process.valorCondenacao:,.2f}"
            ))
            return False, references
        
        references.append(PolicyReference(
            policy_id="POL-2",
            explanation=f"Condemnation value is informed: R$ {process.valorCondenacao:,.2f}"
        ))
        return True, references
    
    @staticmethod
    def check_document_completeness(process: Processo) -> Tuple[bool, List[PolicyReference]]:
        """Check if essential documents are present."""
        references = []
        required_documents = {
            "Certidão de Trânsito em Julgado": False,
            "Planilha de Cálculos": False,
            "Requisição (RPV)": False,
        }
        
        for doc in process.documentos:
            for required_doc in required_documents:
                if required_doc.lower() in doc.nome.lower():
                    required_documents[required_doc] = True
        
        missing_docs = [doc for doc, present in required_documents.items() if not present]
        
        if missing_docs:
            rule = BusinessPolicy.POL_8
            references.append(PolicyReference(
                policy_id=rule.policy_id,
                explanation=f"{rule.description} - Missing: {', '.join(missing_docs)}"
            ))
            return False, references
        
        references.append(PolicyReference(
            policy_id="POL-8",
            explanation="All essential documents are present"
        ))
        return True, references
    
    @staticmethod
    def check_death_without_inventory(process: Processo) -> Tuple[bool, List[PolicyReference]]:
        """Check for author death without inventory."""
        references = []
        for doc in process.documentos:
            if "óbito" in doc.nome.lower() or "morte" in doc.nome.lower():
                if not any("inventário" in d.nome.lower() or "habilitação" in d.nome.lower() 
                          for d in process.documentos):
                    rule = BusinessPolicy.POL_5
                    references.append(PolicyReference(
                        policy_id=rule.policy_id,
                        explanation=f"{rule.description} - Death document found without inventory"
                    ))
                    return True, references
        
        return False, references
    
    @staticmethod
    def check_delegation_without_reserve(process: Processo) -> Tuple[bool, List[PolicyReference]]:
        """Check for delegation without reserve of powers."""
        references = []
        for doc in process.documentos:
            if "substabelecimento" in doc.nome.lower() and "sem reserva" in doc.nome.lower():
                rule = BusinessPolicy.POL_6
                references.append(PolicyReference(
                    policy_id=rule.policy_id,
                    explanation=f"{rule.description} - Document found: {doc.nome}"
                ))
                return True, references
        
        return False, references
    
    @staticmethod
    def check_execution_phase(process: Processo) -> Tuple[bool, List[PolicyReference]]:
        """Check if process is in execution/final judgment phase."""
        references = []
        
        # Look for indicators of final judgment
        has_transit = any(
            "trânsito" in doc.nome.lower() or "trânsito em julgado" in doc.texto.lower()
            for doc in process.documentos
        )
        
        # Look for execution phase indicators
        has_execution = any(
            "cumprimento" in mov.descricao.lower() or "execução" in mov.descricao.lower()
            for mov in process.movimentos
        )
        
        if not (has_transit and has_execution):
            rule = BusinessPolicy.POL_1
            references.append(PolicyReference(
                policy_id=rule.policy_id,
                explanation=f"{rule.description} - Process not in final judgment + execution phase"
            ))
            return False, references
        
        references.append(PolicyReference(
            policy_id="POL-1",
            explanation="Process is in final judgment (transitado em julgado) and execution phase"
        ))
        return True, references
    
    @staticmethod
    def verify_process(process: Processo) -> Tuple[DecisionStatus, str, List[PolicyReference]]:
        """
        Verify process against all policies.
        
        Returns:
            Tuple of (decision, rationale, references)
        """
        all_references = []
        rejection_reasons = []
        incompleteness_reasons = []
        
        logger.info(f"Starting verification for process: {process.numeroProcesso}")
        
        # Check rejection rules (must reject if any triggered)
        rejection_checks = [
            PolicyVerificationService.check_sphere_rejection(process),
            PolicyVerificationService.check_death_without_inventory(process),
            PolicyVerificationService.check_delegation_without_reserve(process),
        ]
        
        for rejected, refs in rejection_checks:
            all_references.extend(refs)
            if rejected:
                rejection_reasons.extend([r.explanation for r in refs])
        
        # Check incompleteness (incomplete if triggered)
        incomplete, refs = PolicyVerificationService.check_document_completeness(process)
        all_references.extend(refs)
        if not incomplete:
            incompleteness_reasons.extend([r.explanation for r in refs])
        
        # If rejected, return rejection
        if rejection_reasons:
            rationale = f"Process REJECTED due to: {'; '.join(rejection_reasons)}"
            logger.info(f"Process {process.numeroProcesso} rejected", extra={"extra_fields": {"reason": rationale}})
            return DecisionStatus.REJECTED, rationale, all_references
        
        # If incomplete, return incomplete
        if incompleteness_reasons:
            rationale = f"Process INCOMPLETE: {'; '.join(incompleteness_reasons)}"
            logger.info(f"Process {process.numeroProcesso} incomplete", extra={"extra_fields": {"reason": rationale}})
            return DecisionStatus.INCOMPLETE, rationale, all_references
        
        # Check approval criteria
        execution_ok, refs = PolicyVerificationService.check_execution_phase(process)
        all_references.extend(refs)
        
        value_ok, refs = PolicyVerificationService.check_minimum_value(process)
        all_references.extend(refs)
        
        if execution_ok and value_ok:
            rationale = "Process meets all eligibility criteria and is approved for acquisition."
            logger.info(f"Process {process.numeroProcesso} approved", extra={"extra_fields": {"reason": rationale}})
            return DecisionStatus.APPROVED, rationale, all_references
        else:
            rejection_reasons = []
            if not execution_ok:
                rejection_reasons.append("Process not in final judgment + execution phase")
            if not value_ok:
                rejection_reasons.append("Condemnation value criteria not met")
            
            rationale = f"Process REJECTED: {'; '.join(rejection_reasons)}"
            logger.info(f"Process {process.numeroProcesso} rejected", extra={"extra_fields": {"reason": rationale}})
            return DecisionStatus.REJECTED, rationale, all_references

