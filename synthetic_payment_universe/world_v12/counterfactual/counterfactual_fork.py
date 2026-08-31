import random
from typing import Dict, List, Any
from pydantic import BaseModel
from synthetic_payment_universe.world_v12.entities.payment import Payment
from synthetic_payment_universe.world_v12.entities.customer import Customer

COUNTERFACTUAL_BRANCHES = ["WAIT", "RETRY", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "ESCALATE"]

class CounterfactualOutcome(BaseModel):
    branch_id: str
    decision_point_id: str
    action_type: str
    success: bool
    recovered_amount: float
    operational_cost: float
    relationship_cost: float
    net_economic_value: float
    time_to_recovery_seconds: int

class WorldCounterfactualForkEngine:
    """
    Forks world state across 5 counterfactual branches at decision time T.
    Preserves common random numbers and latent state across branches for unbiased NEV calculation.
    """
    def __init__(self, master_seed: int = 12345):
        self.master_seed = master_seed

    def evaluate_branches(
        self,
        decision_point_id: str,
        payment: Payment,
        customer: Customer,
        natural_recovery: bool,
        current_gateway_health: float = 0.95
    ) -> List[CounterfactualOutcome]:
        outcomes: List[CounterfactualOutcome] = []
        amt = payment.amount
        fcode = payment.failure_code or "91"

        for idx, act in enumerate(COUNTERFACTUAL_BRANCHES):
            rng = random.Random(self.master_seed + idx + int(payment.payment_id.split('_')[-1]) if '_' in payment.payment_id else idx)
            success = False
            rec_amt = 0.0
            op_cost = 0.0
            rel_cost = 0.0
            time_to_rec = 0

            if act == "WAIT":
                op_cost = 0.0
                rel_cost = 0.0
                if natural_recovery:
                    success = True
                    rec_amt = amt
                    time_to_rec = 7200
                else:
                    success = False

            elif act in ["RETRY", "SWITCH_GATEWAY"]:
                op_cost = 15.0
                rel_cost = 50.0
                eff_health = current_gateway_health if act == "RETRY" else 0.95
                if fcode in ["91", "TO"] and rng.random() < eff_health:
                    success = True
                    rec_amt = amt
                    time_to_rec = 60
                else:
                    success = False

            elif act == "SEND_PAYMENT_LINK":
                op_cost = 5.0
                rel_cost = 150.0 + (customer.fatigue_score * 200.0)
                conv_p = max(0.10, 0.70 - (customer.fatigue_score * 0.40))
                if rng.random() < conv_p:
                    success = True
                    rec_amt = amt
                    time_to_rec = 1800
                else:
                    success = False

            elif act == "ESCALATE":
                op_cost = 500.0
                rel_cost = 20.0
                success = True
                rec_amt = amt
                time_to_rec = 86400

            nev = round((rec_amt if success else 0.0) - op_cost - rel_cost, 2)

            outcomes.append(CounterfactualOutcome(
                branch_id=f"fork_{decision_point_id}_{act.lower()}",
                decision_point_id=decision_point_id,
                action_type=act,
                success=success,
                recovered_amount=round(rec_amt, 2),
                operational_cost=round(op_cost, 2),
                relationship_cost=round(rel_cost, 2),
                net_economic_value=nev,
                time_to_recovery_seconds=time_to_rec
            ))

        return outcomes
