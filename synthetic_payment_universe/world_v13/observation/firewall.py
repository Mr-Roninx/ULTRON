from typing import Dict, Any, List
from backend.benchmark.firewall import FutureInformationLeakageError

FORBIDDEN_V13_KEYS = {
    "true_root_cause",
    "future_salary_timestamp",
    "next_salary_timestamp",
    "latent_profile",
    "latent_liquidity_cycle",
    "oracle_optimal_action",
    "counterfactual_outcomes",
    "natural_recovery_timestamp",
    "eventual_payment",
    "eventual_recovery_amount",
    "current_cash_reserve",
    "monthly_inflow"
}

class CivilizationObservationFirewall:
    """
    Guarantees strict three-domain separation.
    Blocks all future records (timestamp > T) and strips all latent oracle variables.
    """
    @staticmethod
    def sanitize(payload: Dict[str, Any], current_time: int) -> Dict[str, Any]:
        # 1. Temporal boundary check
        for time_key in ["timestamp", "created_at", "delivered_at", "settled_at"]:
            if time_key in payload and payload[time_key] is not None and payload[time_key] > current_time:
                raise FutureInformationLeakageError(f"Lookahead violation: {time_key}={payload[time_key]} > current_time={current_time}")

        # 2. Key sanitization
        sanitized: Dict[str, Any] = {}
        for k, v in payload.items():
            k_lower = k.lower()
            if k in FORBIDDEN_V13_KEYS or k_lower.startswith("latent_") or k_lower.startswith("oracle_") or k_lower.startswith("evaluator_"):
                continue
            if isinstance(v, dict):
                sanitized[k] = CivilizationObservationFirewall.sanitize(v, current_time)
            elif isinstance(v, list):
                sanitized[k] = [CivilizationObservationFirewall.sanitize(item, current_time) if isinstance(item, dict) else item for item in v]
            else:
                sanitized[k] = v
        return sanitized
