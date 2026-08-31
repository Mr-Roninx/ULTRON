import json
from typing import Dict, Any, List, Optional
from backend.benchmark.firewall import FutureInformationLeakageError

FORBIDDEN_KEYS = {
    "true_root_cause",
    "future_salary_timestamp",
    "next_liquidity_window",
    "counterfactual_outcomes",
    "eventual_payment",
    "eventual_recovery_amount",
    "natural_recovery_timestamp",
    "latent_churn_probability",
    "latent_churn_risk",
    "latent_profile",
    "latent_salary_day",
    "oracle_best_action",
    "oracle_optimal_action"
}

class WorldObservationFirewall:
    r"""
    Strict temporal and privilege firewall for ULTRON-SWU-1.2.
    Guarantees no future timestamps ($timestamp \le current_time$) and strips all hidden oracle variables.
    """
    @staticmethod
    def sanitize(payload: Dict[str, Any], current_time: int) -> Dict[str, Any]:
        # 1. Temporal boundary check
        for time_key in ["timestamp", "created_at", "delivered_at"]:
            if time_key in payload and payload[time_key] is not None and payload[time_key] > current_time:
                raise FutureInformationLeakageError(f"Temporal lookahead violation: {time_key}={payload[time_key]} > current_time={current_time}")

        # 2. Key sanitization
        sanitized: Dict[str, Any] = {}
        for k, v in payload.items():
            k_lower = k.lower()
            if k in FORBIDDEN_KEYS or k_lower.startswith("latent_") or k_lower.startswith("oracle_") or k_lower.startswith("evaluator_") or "ground_truth" in k_lower:
                continue
            if isinstance(v, dict):
                sanitized[k] = WorldObservationFirewall.sanitize(v, current_time)
            elif isinstance(v, list):
                sanitized[k] = [WorldObservationFirewall.sanitize(item, current_time) if isinstance(item, dict) else item for item in v]
            else:
                sanitized[k] = v
        return sanitized
