from typing import Dict, List, Set, Any
from pydantic import BaseModel

class CausalEdgeV13(BaseModel):
    source: str
    target: str
    mechanism: str
    functional_form: str

class CivilizationCausalGraph:
    """
    Structural Causal Model defining macro and micro economic dependencies across entities.
    """
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[CausalEdgeV13] = []
        self._build_graph()

    def _build_graph(self):
        edges = [
            CausalEdgeV13(source="CustomerBehavior", target="PaymentIntent", mechanism="Customer demand drives payment creation", functional_form="Intent ~ Bernoulli(P(intent | tier, liquidity))"),
            CausalEdgeV13(source="GatewayHealth", target="AuthorizationOutcome", mechanism="Gateway health controls success/failure", functional_form="P(auth) = base_rate * health_score"),
            CausalEdgeV13(source="ULTRONIntervention", target="CustomerResponse", mechanism="Outreach channel delivers payment link or reminder", functional_form="Response = f(channel, fatigue, liquidity)"),
            CausalEdgeV13(source="ULTRONIntervention", target="CommunicationFatigue", mechanism="Outreach increases contact fatigue", functional_form="Fatigue_t+1 = min(1.0, Fatigue_t + delta_channel)"),
            CausalEdgeV13(source="CustomerResponse", target="RecoveryOutcome", mechanism="Customer conversion triggers payment recovery", functional_form="Recovery = Link_Paid | Retry_Authorized"),
            CausalEdgeV13(source="RecoveryOutcome", target="CustomerRelationship", mechanism="Successful recovery restores trust; repeated failure degrades", functional_form="Relationship_t+1 = clamp(Relationship_t + delta, 0, 1)"),
            CausalEdgeV13(source="CustomerRelationship", target="FuturePaymentProbability", mechanism="High relationship score increases retention and LTV", functional_form="P(future) = base * relationship_score"),
            CausalEdgeV13(source="RecoveryOutcome", target="MerchantRevenue", mechanism="Recovered funds settle to merchant bank ledger", functional_form="Revenue_t+1 = Revenue_t + Recovered_Amount"),
            CausalEdgeV13(source="ULTRONRouting", target="GatewayCongestion", mechanism="Routing traffic into gateway affects load and health", functional_form="Health_t+1 = Health_t - f(Load/Capacity)")
        ]
        for e in edges:
            self.nodes.add(e.source)
            self.nodes.add(e.target)
            self.edges.append(e)

    def get_upstream_causes(self, target: str) -> List[str]:
        return [e.source for e in self.edges if e.target == target]

    def get_downstream_effects(self, source: str) -> List[str]:
        return [e.target for e in self.edges if e.source == source]
