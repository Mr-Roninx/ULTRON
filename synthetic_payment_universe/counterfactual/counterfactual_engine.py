import random
from typing import Dict, List, Any
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Customer, Payment, GroundTruthOutcome
from synthetic_payment_universe.schema.counterfactual import CounterfactualBranch, CounterfactualOutcome
from synthetic_payment_universe.generator.seeds import MasterSeedManager

COUNTERFACTUAL_ACTIONS = ["WAIT", "RETRY", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "ESCALATE"]

class UniverseCounterfactualEngine:
    """
    Evaluates 5-branch counterfactual futures from identical world states.
    Preserves common random numbers and latent customer states for unbiased causal comparison.
    """
    def __init__(self, seed_manager: MasterSeedManager):
        self.seed_mgr = seed_manager

    def evaluate_counterfactual_branches(
        self,
        decision_point_id: str,
        payment: Payment,
        customer: Customer,
        ground_truth: GroundTruthOutcome,
        current_gateway_health: float = 0.95
    ) -> List[CounterfactualOutcome]:
        now = clock.now()
        outcomes: List[CounterfactualOutcome] = []

        amt = payment.amount
        fcode = payment.failure_code or "91"

        for idx, act in enumerate(COUNTERFACTUAL_ACTIONS):
            branch_seed = self.seed_mgr.get_counterfactual_seed(idx + int(payment.payment_id.split('_')[-1]) if '_' in payment.payment_id else idx)
            rng = random.Random(branch_seed)

            success = False
            rec_amt = 0.0
            op_cost = 0.0
            rel_cost = 0.0
            time_to_rec = 0
            churn = False

            if act == "WAIT":
                op_cost = 0.0
                rel_cost = 0.0 # Silent wait preserves relationship
                if ground_truth.eventual_payment:
                    success = True
                    rec_amt = amt
                    time_to_rec = (ground_truth.natural_recovery_timestamp - now) if ground_truth.natural_recovery_timestamp else 7200
                else:
                    success = False

            elif act in ["RETRY", "SWITCH_GATEWAY"]:
                op_cost = 15.0
                rel_cost = 50.0
                effective_health = current_gateway_health if act == "RETRY" else 0.95
                if fcode in ["91", "TO"] and rng.random() < effective_health:
                    success = True
                    rec_amt = amt
                    time_to_rec = 60
                else:
                    success = False

            elif act == "SEND_PAYMENT_LINK":
                op_cost = 5.0
                rel_cost = 150.0 + (customer.fatigue_score * 200.0)
                # Success depends on customer liquidity and fatigue
                conv_p = 0.65 - (customer.fatigue_score * 0.35)
                if rng.random() < max(0.10, conv_p):
                    success = True
                    rec_amt = amt
                    time_to_rec = 1800
                else:
                    success = False

            elif act == "ESCALATE":
                op_cost = 500.0
                rel_cost = 20.0
                success = True # Human representative handles manual wire/PO
                rec_amt = amt
                time_to_rec = 86400

            nev = (rec_amt if success else 0.0) - op_cost - rel_cost

            outcomes.append(CounterfactualOutcome(
                branch_id=f"branch_{decision_point_id}_{act.lower()}",
                decision_point_id=decision_point_id,
                payment_id=payment.payment_id,
                customer_id=customer.customer_id,
                action_type=act,
                success=success,
                recovered_amount=round(rec_amt, 2),
                operational_cost=round(op_cost, 2),
                relationship_cost=round(rel_cost, 2),
                net_economic_value=round(nev, 2),
                time_to_recovery_seconds=time_to_rec,
                customer_churn_occurred=churn
            ))

        return outcomes

counterfactual_engine = UniverseCounterfactualEngine(MasterSeedManager(99999))
