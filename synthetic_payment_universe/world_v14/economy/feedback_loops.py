from typing import Dict, Any

class EconomicFeedbackLoops:
    """
    Computes formal closed-loop feedback effects across entities.
    """
    @staticmethod
    def apply_loop_a_relationship(current_trust: float, recovery_success: bool) -> float:
        """Loop A: Recovery outcome updates relationship trust."""
        delta = 0.06 if recovery_success else -0.04
        return max(0.05, min(1.0, round(current_trust + delta, 3)))

    @staticmethod
    def apply_loop_b_congestion(active_traffic: int, gateway_capacity: int, base_health: float) -> float:
        """Loop B: Gateway traffic exceeding capacity degrades authorization rate."""
        if active_traffic <= gateway_capacity:
            return base_health
        overload = (active_traffic - gateway_capacity) / gateway_capacity
        penalty = min(0.70, overload * 0.25)
        return max(0.10, round(base_health - penalty, 3))

    @staticmethod
    def apply_loop_c_fatigue(current_fatigue: float, channel_delta: float) -> float:
        """Loop C: Unnecessary outreach accumulates fatigue."""
        return min(1.0, round(current_fatigue + channel_delta, 3))

    @staticmethod
    def apply_loop_e_merchant_growth(current_volume: float, recovered_revenue: float, lost_revenue: float) -> float:
        """Loop E: Net recovered revenue accelerates merchant growth."""
        net_impact = recovered_revenue - lost_revenue
        growth_delta = net_impact / max(100000.0, current_volume) * 0.05
        return round(current_volume * (1.0 + growth_delta), 2)

    @staticmethod
    def apply_loop_f_churn(current_churn_p: float, repeated_failures: int) -> float:
        """Loop F: Unresolved payment failures accelerate customer churn."""
        delta = repeated_failures * 0.08
        return min(0.99, round(current_churn_p + delta, 3))
