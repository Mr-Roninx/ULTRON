from typing import Dict, List, Any
from synthetic_payment_universe.schema.entities import Customer, Payment, Invoice, Subscription

class CrossOpportunityInterferenceEngine:
    """
    Models multi-opportunity interference on shared customer profiles.
    Actions on one recovery channel increase global customer fatigue and churn risk.
    """
    def __init__(self):
        self._customer_exposures: Dict[str, Dict[str, Any]] = {}

    def register_opportunity(self, customer_id: str, opportunity_type: str, amount: float, reference_id: str):
        if customer_id not in self._customer_exposures:
            self._customer_exposures[customer_id] = {
                "opportunities": [],
                "total_amount": 0.0,
                "global_fatigue_multiplier": 1.0
            }
        self._customer_exposures[customer_id]["opportunities"].append({
            "type": opportunity_type,
            "amount": amount,
            "reference_id": reference_id
        })
        self._customer_exposures[customer_id]["total_amount"] += amount

    def apply_cross_action_interference(self, customer_id: str, action_type: str) -> float:
        """
        Increases global fatigue multiplier when aggressive outreach is used on multi-invoice customer.
        Returns the updated global fatigue multiplier.
        """
        if customer_id not in self._customer_exposures:
            return 1.0

        exp = self._customer_exposures[customer_id]
        opp_count = len(exp["opportunities"])
        
        if opp_count > 1 and action_type in ["SEND_PAYMENT_LINK", "SEND_EMAIL", "VOICE_OUTREACH"]:
            # Aggressive multi-touch penalizes response probability
            exp["global_fatigue_multiplier"] = min(2.5, exp["global_fatigue_multiplier"] + (0.25 * opp_count))

        return exp["global_fatigue_multiplier"]

    def get_customer_summary(self, customer_id: str) -> Dict[str, Any]:
        return self._customer_exposures.get(customer_id, {"opportunities": [], "total_amount": 0.0, "global_fatigue_multiplier": 1.0})

    def reset(self):
        self._customer_exposures.clear()

interference_engine = CrossOpportunityInterferenceEngine()
