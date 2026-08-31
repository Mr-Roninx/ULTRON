from typing import List, Dict, Any
from pydantic import BaseModel
from synthetic_payment_universe.world_v14.counterfactual.crn_manager import PopulationCRNManager

CIVILIZATION_FORK_ARMS = ["CONTROL_NO_ULTRON", "RULE_BASED", "ULTRON_LLM_OFF", "ULTRON_LLM_ON", "ULTRON_FULL"]

class CivilizationBranchResult(BaseModel):
    arm_name: str
    decision_id: str
    recovered_revenue: float
    operational_cost: float
    relationship_score: float
    net_economic_value: float

class CivilizationForkEngine:
    """
    Forks civilization state across 5 experimental arms starting from identical pre-decision reality.
    """
    def __init__(self, master_seed: int = 12345):
        self.crn = PopulationCRNManager(master_seed)

    def evaluate_arms(
        self,
        decision_id: str,
        amount: float,
        natural_recovery: bool,
        customer_fatigue: float = 0.0,
        customer_trust: float = 0.90
    ) -> List[CivilizationBranchResult]:
        results: List[CivilizationBranchResult] = []

        for arm in CIVILIZATION_FORK_ARMS:
            rng = self.crn.get_stream(decision_id, arm)
            rec = 0.0
            cost = 0.0
            trust = customer_trust

            if arm == "CONTROL_NO_ULTRON":
                rec = amount if natural_recovery else 0.0
                cost = 0.0
            elif arm == "RULE_BASED":
                cost = 25.0
                # Simple rule: retry if transient, else send link
                p_success = 0.70 - (customer_fatigue * 0.30)
                rec = amount if (natural_recovery or rng.random() < p_success) else 0.0
            elif arm == "ULTRON_LLM_OFF":
                cost = 20.0
                p_success = 0.80 - (customer_fatigue * 0.25)
                rec = amount if (natural_recovery or rng.random() < p_success) else 0.0
            elif arm == "ULTRON_LLM_ON":
                cost = 20.0
                p_success = 0.84 - (customer_fatigue * 0.20)
                rec = amount if (natural_recovery or rng.random() < p_success) else 0.0
            elif arm == "ULTRON_FULL":
                cost = 18.0
                p_success = 0.87 - (customer_fatigue * 0.15)
                rec = amount if (natural_recovery or rng.random() < p_success) else 0.0
                trust = min(1.0, trust + 0.05) if rec > 0 else max(0.10, trust - 0.05)

            nev = round(rec - cost, 2)
            results.append(CivilizationBranchResult(
                arm_name=arm,
                decision_id=decision_id,
                recovered_revenue=round(rec, 2),
                operational_cost=round(cost, 2),
                relationship_score=round(trust, 3),
                net_economic_value=nev
            ))

        return results
