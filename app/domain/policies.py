from enum import Enum
from typing import NamedTuple, List


class Decision(str, Enum):
    """Possible decisions for a process."""
    APPROVED = "approved"
    REJECTED = "rejected"
    INCOMPLETE = "incomplete"


class PolicyRule(NamedTuple):
    """Business policy rule."""
    id: str
    title: str
    description: str
    category: str


POLICIES: List[PolicyRule] = [
    PolicyRule(
        id="POL-1",
        title="Elegibilidade - Trânsito em Julgado",
        description="Só compramos crédito de processos transitados em julgado e em fase de execução",
        category="elegibilidade"
    ),
    PolicyRule(
        id="POL-2",
        title="Elegibilidade - Valor de Condenação",
        description="Exigir valor de condenação informado",
        category="elegibilidade"
    ),
    PolicyRule(
        id="POL-3",
        title="Exclusão - Valor Mínimo",
        description="Valor de condenação < R$ 1.000,00 → não compra",
        category="exclusao"
    ),
    PolicyRule(
        id="POL-4",
        title="Exclusão - Esfera Trabalhista",
        description="Condenações na esfera trabalhista → não compra",
        category="exclusao"
    ),
    PolicyRule(
        id="POL-5",
        title="Exclusão - Óbito do Autor",
        description="Óbito do autor sem habilitação no inventário → não compra",
        category="exclusao"
    ),
    PolicyRule(
        id="POL-6",
        title="Exclusão - Substabelecimento",
        description="Substabelecimento sem reserva de poderes → não compra",
        category="exclusao"
    ),
    PolicyRule(
        id="POL-7",
        title="Documentação - Honorários",
        description="Informar honorários contratuais, periciais e sucumbenciais quando existirem",
        category="honorarios"
    ),
    PolicyRule(
        id="POL-8",
        title="Qualidade - Documentos Essenciais",
        description="Se faltar documento essencial (ex.: trânsito em julgado não comprovado) → incomplete",
        category="documentacao"
    ),
]


def get_policy_by_id(policy_id: str) -> PolicyRule:
    """Retrieve a policy by ID."""
    for policy in POLICIES:
        if policy.id == policy_id:
            return policy
    raise ValueError(f"Policy {policy_id} not found")


def get_policies_by_category(category: str) -> List[PolicyRule]:
    """Retrieve policies by category."""
    return [p for p in POLICIES if p.category == category]