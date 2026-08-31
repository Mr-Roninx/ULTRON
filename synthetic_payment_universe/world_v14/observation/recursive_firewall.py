from typing import Dict, Any, List
from backend.benchmark.firewall import FutureInformationLeakageError

FORBIDDEN_V14_KEYS = {
    "true_root_cause",
    "future_salary_timestamp",
    "next_inflow_timestamp",
    "cash_reserve",
    "monthly_inflow",
    "oracle_optimal_action",
    "counterfactual_outcomes",
    "eventual_recovery_amount",
    "natural_recovery_timestamp",
    "latent_profile"
}

class RecursiveObservationFirewall:
    """
    Scans dictionaries, lists, and nested objects.
    Enforces that timestamp <= current_time and strips all hidden variables.
    """
    @staticmethod
    def sanitize(payload: Dict[str, Any], current_time: int) -> Dict[str, Any]:
        # 1. Temporal check
        for t_key in ["timestamp", "created_at", "settled_at", "due_timestamp"]:
            if t_key in payload and payload[t_key] is not None and payload[t_key] > current_time:
                raise FutureInformationLeakageError(f"Observation Firewall violation: {t_key}={payload[t_key]} > {current_time}")

        # 2. Recursive sanitization
        sanitized: Dict[str, Any] = {}
        for k, v in payload.items():
            k_lower = k.lower()
            if k in FORBIDDEN_V14_KEYS or k_lower.startswith("latent_") or k_lower.startswith("oracle_") or k_lower.startswith("evaluator_"):
                continue
            if isinstance(v, dict):
                sanitized[k] = RecursiveObservationFirewall.sanitize(v, current_time)
            elif isinstance(v, list):
                sanitized[k] = [RecursiveObservationFirewall.sanitize(item, current_time) if isinstance(item, dict) else item for item in v]
            else:
                sanitized[k] = v
        return sanitized
