from typing import Dict, Any

class MerchantExternalityEngine:
    """
    Evaluates merchant-side support workload, dispute exposure, and operational costs.
    """
    @staticmethod
    def calculate_merchant_burden(action_type: str, count: int = 1) -> float:
        cost_per_action = {
            "WAIT": 0.0,
            "RETRY": 5.0,
            "SEND_PAYMENT_LINK": 15.0,
            "SWITCH_GATEWAY": 20.0,
            "AGGRESSIVE_DUNNING": 80.0,
            "ESCALATE": 120.0
        }
        unit_cost = cost_per_action.get(action_type, 10.0)
        return round(unit_cost * count, 2)
