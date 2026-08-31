from typing import Dict, Any, Optional
from backend.payment_intelligence.schemas import NormalizedFailure, GatewayHealthState, RailHealthState

class RecoverabilityEngine:
    """
    Computes deterministic recoverability estimates (0.0 to 1.0)
    factoring in failure category, attempt decay, customer history, and gateway health.
    """
    def calculate_recoverability(
        self,
        normalized_failure: NormalizedFailure,
        attempt_count: int = 1,
        customer_history_factor: float = 1.0,
        gateway_health_factor: float = 1.0
    ) -> float:
        base = normalized_failure.recoverability

        # Attempt decay penalty (each subsequent failed attempt reduces expected recovery)
        attempt_penalty = max(0.4, 1.0 - (max(0, attempt_count - 1) * 0.15))

        # Bound customer factor (0.5 to 1.3)
        cust_factor = max(0.5, min(1.3, customer_history_factor))

        # Gateway health factor (0.1 to 1.0)
        gw_factor = max(0.1, min(1.0, gateway_health_factor))

        # Final score bounded to [0.0, 1.0]
        final_score = base * attempt_penalty * cust_factor * gw_factor
        return round(max(0.0, min(1.0, final_score)), 4)

recoverability_engine = RecoverabilityEngine()
