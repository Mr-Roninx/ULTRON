from typing import Dict, List, Any, Set
from pydantic import BaseModel, Field

class CausalEdge(BaseModel):
    source_node: str
    target_node: str
    mechanism: str
    functional_form: str

class UniverseCausalGraph:
    """
    Explicit Directed Acyclic Graph (DAG) defining structural causal relationships in the Synthetic Universe.
    """
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[CausalEdge] = []
        self._build_authoritative_dag()

    def _build_authoritative_dag(self):
        default_edges = [
            CausalEdge(
                source_node="gateway_health",
                target_node="authorization_probability",
                mechanism="Infrastructure availability directly determines bank auth rate",
                functional_form="P(auth) = base_auth * gateway_health"
            ),
            CausalEdge(
                source_node="authorization_probability",
                target_node="payment_outcome",
                mechanism="Bernoulli trial based on calculated authorization probability",
                functional_form="Outcome ~ Bernoulli(P(auth))"
            ),
            CausalEdge(
                source_node="customer_liquidity",
                target_node="payment_probability",
                mechanism="Customer cash availability determines settlement viability",
                functional_form="P(pay) = min(1.0, liquidity_inflow / invoice_amount)"
            ),
            CausalEdge(
                source_node="communication_fatigue",
                target_node="response_probability",
                mechanism="Frequent outreach reduces customer responsiveness and increases opt-out",
                functional_form="P(resp) = max(0.05, base_resp - (fatigue * 0.40))"
            ),
            CausalEdge(
                source_node="agent_action",
                target_node="customer_behavior",
                mechanism="Agent intervention channel triggers customer notification & action",
                functional_form="Behavior = f(ActionType, Fatigue, Liquidity)"
            ),
            CausalEdge(
                source_node="customer_behavior",
                target_node="recovery_outcome",
                mechanism="Customer link completion or bank retry executes recovery",
                functional_form="Recovery = Indicator(Behavior == COMPLETED)"
            )
        ]
        for e in default_edges:
            self.nodes.add(e.source_node)
            self.nodes.add(e.target_node)
            self.edges.append(e)

    def get_upstream_causes(self, target_node: str) -> List[str]:
        return [e.source_node for e in self.edges if e.target_node == target_node]

    def get_downstream_effects(self, source_node: str) -> List[str]:
        return [e.target_node for e in self.edges if e.source_node == source_node]

causal_graph = UniverseCausalGraph()
