import random
from typing import Dict, Any, Tuple
from backend.payment_intelligence.schemas import CustomerResponseCode

class CustomerBehaviorSimulator:
    """
    Simulates customer responses to communication and dunning interventions.
    """
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def reseed(self, seed: int):
        self.rng = random.Random(seed)

    def simulate_response(
        self,
        customer_segment: str,
        channel: str,
        message_type: str,
        recent_contacts: int = 0,
        historical_opt_out: bool = False
    ) -> Tuple[CustomerResponseCode, str]:
        if historical_opt_out:
            return CustomerResponseCode.OPTOUT, "Customer has previously opted out of recovery communications."

        # Fatigue penalty increases NO_RESPONSE or OPTOUT
        fatigue_factor = min(0.5, recent_contacts * 0.12)

        # Baseline response distribution by segment
        if customer_segment == "B2B_ENTERPRISE":
            weights = {
                CustomerResponseCode.PAY_NOW: 0.50 - fatigue_factor,
                CustomerResponseCode.ASKS_FOR_TIME: 0.25,
                CustomerResponseCode.PAYMENT_METHOD_PROBLEM: 0.10,
                CustomerResponseCode.REQUEST_HUMAN: 0.08,
                CustomerResponseCode.NO_RESPONSE: 0.05 + fatigue_factor,
                CustomerResponseCode.DISPUTE: 0.02,
                CustomerResponseCode.OPTOUT: 0.00 if recent_contacts < 4 else 0.05
            }
        elif customer_segment == "SMB":
            weights = {
                CustomerResponseCode.PAY_NOW: 0.40 - fatigue_factor,
                CustomerResponseCode.ASKS_FOR_TIME: 0.20,
                CustomerResponseCode.PAYMENT_METHOD_PROBLEM: 0.15,
                CustomerResponseCode.NO_RESPONSE: 0.18 + fatigue_factor,
                CustomerResponseCode.REQUEST_HUMAN: 0.04,
                CustomerResponseCode.DISPUTE: 0.02,
                CustomerResponseCode.OPTOUT: 0.01 + (0.04 if recent_contacts > 2 else 0)
            }
        else: # CONSUMER
            weights = {
                CustomerResponseCode.PAY_NOW: 0.35 - fatigue_factor,
                CustomerResponseCode.NO_RESPONSE: 0.35 + fatigue_factor,
                CustomerResponseCode.PAYMENT_METHOD_PROBLEM: 0.15,
                CustomerResponseCode.ASKS_FOR_TIME: 0.08,
                CustomerResponseCode.DISPUTE: 0.04,
                CustomerResponseCode.REQUEST_HUMAN: 0.02,
                CustomerResponseCode.OPTOUT: 0.01 + (0.05 if recent_contacts > 3 else 0)
            }

        # Normalize weights
        total = sum(max(0.01, w) for w in weights.values())
        choices = list(weights.keys())
        norm_weights = [max(0.01, weights[c]) / total for c in choices]

        selected: CustomerResponseCode = self.rng.choices(choices, weights=norm_weights, k=1)[0]
        
        message_map = {
            CustomerResponseCode.PAY_NOW: "Customer acknowledged and initiated settlement.",
            CustomerResponseCode.ASKS_FOR_TIME: "Customer requested extension until next billing cycle/payroll.",
            CustomerResponseCode.PAYMENT_METHOD_PROBLEM: "Customer noted issue with primary card and requested alternate link.",
            CustomerResponseCode.DISPUTE: "Customer disputes the billed charge.",
            CustomerResponseCode.NO_RESPONSE: "No response received within timeout window.",
            CustomerResponseCode.REQUEST_HUMAN: "Customer requested assistance from account manager.",
            CustomerResponseCode.OPTOUT: "Customer explicitly requested to stop automated messages."
        }

        return selected, message_map[selected]

customer_behavior_simulator = CustomerBehaviorSimulator()
