from typing import Dict, Any, List
from pydantic import BaseModel
from synthetic_payment_universe.world_v15.counterfactual.policy_baselines import AdversarialPolicy, ALL_V15_POLICIES
from synthetic_payment_universe.world_v15.counterfactual.crn_aligned_fork import AlignedCRNManager
from synthetic_payment_universe.world_v15.attribution.attribution_tiers import MultiTierAttributionEngine, MultiTierEconomicAttribution

class PolicyEvaluationResult(BaseModel):
    policy: str
    decision_id: str
    gross_recovery: float
    natural_recovery: float
    direct_incremental: float
    externality_cost: float
    operational_cost: float
    net_economic_value: float

class ShadowEvaluator:
    """
    Computes isolated counterfactual branches in shadow mode for 11 competing policies.
    """
    def __init__(self, master_seed: int = 12345):
        self.crn = AlignedCRNManager(master_seed)

    def evaluate_decision(
        self,
        decision_id: str,
        amount: float,
        is_natural_recovery: bool,
        customer_fatigue: float = 0.0,
        customer_trust: float = 0.90
    ) -> List[PolicyEvaluationResult]:
        results: List[PolicyEvaluationResult] = []

        for p in ALL_V15_POLICIES:
            rng = self.crn.get_stream(decision_id, p)
            rec = 0.0
            op_cost = 0.0
            ext_cost = 0.0

            if p == "CONTROL_NO_ULTRON" or p == "ALWAYS_WAIT":
                rec = amount if is_natural_recovery else 0.0
                op_cost = 0.0
            elif p == "ALWAYS_RETRY":
                op_cost = 10.0
                # Immediate retry fails if outage persists; succeeds ~40%
                rec = amount if (rng.random() < 0.40) else 0.0
            elif p == "ALWAYS_SWITCH_GATEWAY":
                op_cost = 25.0
                # Switches to congested secondary gateway creating external cost
                ext_cost = 45.0
                rec = amount if (rng.random() < 0.65) else 0.0
            elif p == "AGGRESSIVE_DUNNING":
                op_cost = 65.0
                # High outreach fatigue destroys conversion unless customer is desperate
                ext_cost = 150.0 # Relationship damage
                rec = amount if (rng.random() < 0.50) else 0.0
            elif p == "ALWAYS_CONTACT":
                op_cost = 20.0
                p_success = max(0.10, 0.70 - (customer_fatigue * 0.45))
                rec = amount if (rng.random() < p_success) else 0.0
            elif p == "CONSERVATIVE":
                op_cost = 15.0
                p_success = 0.75 if not is_natural_recovery else 0.95
                rec = amount if (rng.random() < p_success) else 0.0
            elif p == "RULE_BASED":
                op_cost = 25.0
                rec = amount if (rng.random() < 0.72) else 0.0
            elif p == "ULTRON_LLM_OFF":
                op_cost = 20.0
                rec = amount if (rng.random() < 0.81) else 0.0
            elif p == "ULTRON_LLM_ON":
                op_cost = 20.0
                rec = amount if (rng.random() < 0.84) else 0.0
            elif p == "ULTRON_FULL":
                op_cost = 18.0
                # Smart routing + non-intrusive timing
                rec = amount if (rng.random() < 0.87) else 0.0

            # Causal attribution tiers
            attr = MultiTierAttributionEngine.classify_attribution(
                recovered_amount=rec,
                is_natural_recovery=is_natural_recovery,
                forward_ltv_delta=0.0,
                externality_cost=ext_cost,
                operational_cost=op_cost
            )

            results.append(PolicyEvaluationResult(
                policy=p,
                decision_id=decision_id,
                gross_recovery=round(rec, 2),
                natural_recovery=round(attr.non_incremental_recovery, 2),
                direct_incremental=round(attr.direct_incremental_revenue, 2),
                externality_cost=round(ext_cost, 2),
                operational_cost=round(op_cost, 2),
                net_economic_value=round(attr.net_economic_value, 2)
            ))

        return results
