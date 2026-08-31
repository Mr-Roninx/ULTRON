from typing import Dict, Any
from backend.benchmark.firewall import FutureInformationLeakageError

FORBIDDEN_V15_KEYS = {
    "natural_recovery_timestamp",
    "would_recover_naturally",
    "difficulty_category",
    "true_root_cause",
    "oracle_optimal_action",
    "counterfactual_outcomes",
    "shadow_evaluator",
    "cash_reserve",
    "next_salary_date"
}

class BlindObservationFirewall:
    """
    Guarantees blind evaluation: hides difficulty, treatment/control arm tags, and oracle data from agent.
    """
    @staticmethod
    def sanitize(payload: Dict[str, Any], current_time: int) -> Dict[str, Any]:
        # 1. Temporal lookahead check
        for t_key in ["timestamp", "created_at", "settled_at"]:
            if t_key in payload and payload[t_key] is not None and payload[t_key] > current_time:
                raise FutureInformationLeakageError(f"Lookahead violation: {t_key}={payload[t_key]} > {current_time}")

        # 2. Recursive sanitization
        sanitized: Dict[str, Any] = {}
        for k, v in payload.items():
            if k in FORBIDDEN_V15_KEYS or k.startswith("oracle_") or k.startswith("evaluator_"):
                continue
            if isinstance(v, dict):
                sanitized[k] = BlindObservationFirewall.sanitize(v, current_time)
            elif isinstance(v, list):
                sanitized[k] = [BlindObservationFirewall.sanitize(i, current_time) if isinstance(i, dict) else i for i in v]
            else:
                sanitized[k] = v
        return sanitized
