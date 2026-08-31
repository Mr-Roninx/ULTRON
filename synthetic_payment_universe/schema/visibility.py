from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class EventVisibility(str, Enum):
    OBSERVABLE = "OBSERVABLE"         # Publicly observable by AgentLoop at timestamp <= simulation_clock
    HIDDEN = "HIDDEN"                 # Latent/Future variables known to the simulation engine but forbidden to AgentLoop
    EVALUATOR_ONLY = "EVALUATOR_ONLY" # Oracle ground truth reserved strictly for post-hoc/counterfactual benchmark evaluation

class VisibilityGuard:
    """
    Enforces strict temporal and privilege boundaries between the Observable World,
    Hidden Simulation World, and Evaluator Oracle.
    """
    @staticmethod
    def is_visible_to_agent(visibility: EventVisibility, event_timestamp: int, current_simulation_time: int) -> bool:
        if visibility != EventVisibility.OBSERVABLE:
            return False
        return event_timestamp <= current_simulation_time

    @staticmethod
    def filter_observable_payload(payload: Dict[str, Any], current_simulation_time: int) -> Dict[str, Any]:
        """Strips any latent, counterfactual, or future lookahead fields."""
        FORBIDDEN_AGENT_KEYS = {
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
        filtered: Dict[str, Any] = {}
        for k, v in payload.items():
            k_lower = k.lower()
            if k in FORBIDDEN_AGENT_KEYS or k_lower.startswith("latent_") or k_lower.startswith("oracle_") or k_lower.startswith("evaluator_") or "ground_truth" in k_lower:
                continue
            if isinstance(v, dict):
                filtered[k] = VisibilityGuard.filter_observable_payload(v, current_simulation_time)
            else:
                filtered[k] = v
        return filtered
