"""
Policy entity and business rules definitions.
"""
from typing import List
from dataclasses import dataclass
from enum import Enum


@dataclass
class PolicyRule:
    """Represents a single policy rule."""
    policy_id: str
    description: str
    severity: str  # "error", "warning", "info"


class BusinessPolicy:
    """Centralizes all business policy rules."""
    
    # Base rules (eligibility)
    POL_1 = PolicyRule(
        policy_id="POL-1",
        description="Only buy credit from processes in final judgment (transitado em julgado) and execution phase",
        severity="error"
    )
    
    POL_2 = PolicyRule(
        policy_id="POL-2",
        description="Require condemnation value to be informed",
        severity="error"
    )
    
    # Rejection rules
    POL_3 = PolicyRule(
        policy_id="POL-3",
        description="Condemnation value < R$ 1,000.00 - do not buy",
        severity="error"
    )
    
    POL_4 = PolicyRule(
        policy_id="POL-4",
        description="Labor sphere condemnations - do not buy",
        severity="error"
    )
    
    POL_5 = PolicyRule(
        policy_id="POL-5",
        description="Death of author without habitation in inventory - do not buy",
        severity="error"
    )
    
    POL_6 = PolicyRule(
        policy_id="POL-6",
        description="Delegation without reserve of powers - do not buy",
        severity="error"
    )
    
    # Information rules
    POL_7 = PolicyRule(
        policy_id="POL-7",
        description="Must inform contractual, expert, and litigation fees when applicable",
        severity="warning"
    )
    
    # Completeness rules
    POL_8 = PolicyRule(
        policy_id="POL-8",
        description="Missing essential document (e.g., final judgment certificate not proven) - incomplete",
        severity="error"
    )
    
    @classmethod
    def get_all_rules(cls) -> List[PolicyRule]:
        """Get all policy rules."""
        return [
            cls.POL_1, cls.POL_2, cls.POL_3, cls.POL_4,
            cls.POL_5, cls.POL_6, cls.POL_7, cls.POL_8
        ]
    
    @classmethod
    def get_rule(cls, policy_id: str) -> PolicyRule:
        """Get a specific policy rule by ID."""
        for rule in cls.get_all_rules():
            if rule.policy_id == policy_id:
                return rule
        raise ValueError(f"Policy rule {policy_id} not found")

