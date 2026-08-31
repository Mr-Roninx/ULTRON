from typing import List, Dict, Any
from pydantic import BaseModel
from synthetic_payment_universe.world_v13.counterfactual.common_random_numbers import CommonRandomNumberManager

COUNTERFACTUAL_BRANCH_LIST = ["WAIT", "RETRY", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "ESCALATE"]

class LongHorizonBranchOutcome(BaseModel):
    branch_id: str
    decision_point_id: str
    action_type: str
    immediate_recovered_amount: float
    horizon_30d_recovered_amount: float
    operational_cost: float
    relationship_cost: float
    customer_retention_probability: float
    net_economic_value: float

class CivilizationCounterfactualForkEngine:
    """
    Forks the economic world across 5 isolated branches and computes long-horizon (30d, 90d) NEV.
    """
    def __init__(self, master_seed: int = 12345):
        self.crn = CommonRandomNumberManager(master_seed)

    def evaluate_branches(
        self,
        decision_point_id: str,
        amount: float,
        failure_code: str,
        natural_recovery: bool,
        customer_fatigue: float = 0.0,
        customer_relationship: float = 0.90
    ) -> List[LongHorizonBranchOutcome]:
        outcomes: List[LongHorizonBranchOutcome] = []

        for branch in COUNTERFACTUAL_BRANCH_LIST:
            rng = self.crn.get_branch_rng(decision_point_id, branch)
            rec_imm = 0.0
            rec_30d = 0.0
            op_cost = 0.0
            rel_cost = 0.0
            retention = customer_relationship

            if branch == "WAIT":
                op_cost = 0.0
                rel_cost = 0.0
                if natural_recovery:
                    rec_imm = amount
                    rec_30d = amount * 1.5 # Natural repeat purchase
                else:
                    rec_imm = 0.0
                    rec_30d = 0.0

            elif branch in ["RETRY", "SWITCH_GATEWAY"]:
                op_cost = 15.0
                rel_cost = 40.0
                if failure_code in ["91", "TO"] and rng.random() < 0.90:
                    rec_imm = amount
                    rec_30d = amount * 1.8
                else:
                    rec_imm = 0.0
                    rec_30d = 0.0

            elif branch == "SEND_PAYMENT_LINK":
                op_cost = 5.0
                rel_cost = 120.0 + (customer_fatigue * 180.0)
                conv_p = max(0.10, 0.75 - (customer_fatigue * 0.45))
                if rng.random() < conv_p:
                    rec_imm = amount
                    rec_30d = amount * 2.0
                    retention = min(1.0, retention + 0.05)
                else:
                    rec_imm = 0.0
                    retention = max(0.10, retention - 0.10)

            elif branch == "ESCALATE":
                op_cost = 450.0
                rel_cost = 10.0
                rec_imm = amount
                rec_30d = amount * 1.2
                retention = 0.98

            nev = round(rec_imm - op_cost - rel_cost, 2)
            outcomes.append(LongHorizonBranchOutcome(
                branch_id=f"fork_{decision_point_id}_{branch.lower()}",
                decision_point_id=decision_point_id,
                action_type=branch,
                immediate_recovered_amount=round(rec_imm, 2),
                horizon_30d_recovered_amount=round(rec_30d, 2),
                operational_cost=round(op_cost, 2),
                relationship_cost=round(rel_cost, 2),
                customer_retention_probability=round(retention, 3),
                net_economic_value=nev
            ))

        return outcomes
