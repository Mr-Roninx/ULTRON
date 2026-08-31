from typing import Dict, List, Set, Any
from pydantic import BaseModel

class CausalEdge(BaseModel):
    source: str
    target: str
    mechanism: str
    functional_form: str

class StructuralCausalGraph:
    """
    Structural Causal Model (SCM) defining explicit cause-and-effect dependencies.
    """
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[CausalEdge] = []
        self._build_scm()

    def _build_scm(self):
        edges = [
            CausalEdge(source="CustomerBehavior", target="PaymentIntent", mechanism="Customer demand drives payment attempts", functional_form="Intent ~ Bernoulli(P(intent | tier, liquidity))"),
            CausalEdge(source="GatewayHealth", target="PaymentOutcome", mechanism="Gateway uptime dictates authorization rate", functional_form="P(auth) = base_auth * health_score"),
            CausalEdge(source="ULTRONAction", target="CustomerResponse", mechanism="Outreach channel delivers payment link or reminder", functional_form="Response = f(channel, fatigue, liquidity)"),
            CausalEdge(source="ULTRONAction", target="CommunicationFatigue", mechanism="Aggressive outreach increases fatigue", functional_form="Fatigue_t+1 = min(1.0, Fatigue_t + delta)"),
            CausalEdge(source="PaymentOutcome", target="LedgerMutation", mechanism="Success triggers balanced double-entry ledger entry", functional_form="Ledger = BalancedJournal(Amount)")
        ]
        for e in edges:
            self.nodes.add(e.source)
            self.nodes.add(e.target)
            self.edges.append(e)

    def get_upstream_causes(self, target: str) -> List[str]:
        return [e.source for e in self.edges if e.target == target]

    def get_downstream_effects(self, source: str) -> List[str]:
        return [e.target for e in self.edges if e.source == source]
