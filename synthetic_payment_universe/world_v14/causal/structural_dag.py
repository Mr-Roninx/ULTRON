from typing import Dict, List, Set
from pydantic import BaseModel

class CausalEdgeV14(BaseModel):
    source: str
    target: str
    mechanism: str

class PopulationCausalDAG:
    """
    Structural Causal Model DAG for Emergent Population Economy.
    """
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[CausalEdgeV14] = []
        self._build_dag()

    def _build_dag(self):
        edges = [
            CausalEdgeV14(source="CustomerCohort", target="PurchaseIntent", mechanism="Cohort spending profile drives purchase frequency"),
            CausalEdgeV14(source="MerchantGrowth", target="TransactionVolume", mechanism="Growing merchants generate more checkout sessions"),
            CausalEdgeV14(source="GatewayCongestion", target="PaymentFailures", mechanism="Traffic exceeding capacity triggers timeouts"),
            CausalEdgeV14(source="ULTRONIntervention", target="CustomerResponse", mechanism="Outreach delivers payment link or prompt"),
            CausalEdgeV14(source="ULTRONIntervention", target="ContactFatigue", mechanism="Outreach accumulates contact fatigue"),
            CausalEdgeV14(source="CustomerResponse", target="RecoveredRevenue", mechanism="Customer conversion recovers funds"),
            CausalEdgeV14(source="RecoveredRevenue", target="CustomerRelationship", mechanism="Recovery preserves relationship trust"),
            CausalEdgeV14(source="CustomerRelationship", target="FuturePurchaseProbability", mechanism="Trust increases future LTV"),
            CausalEdgeV14(source="ContactFatigue", target="CustomerChurn", mechanism="Severe fatigue triggers churn")
        ]
        for e in edges:
            self.nodes.add(e.source)
            self.nodes.add(e.target)
            self.edges.append(e)

    def get_upstream_causes(self, target: str) -> List[str]:
        return [e.source for e in self.edges if e.target == target]

    def get_downstream_effects(self, source: str) -> List[str]:
        return [e.target for e in self.edges if e.source == source]
