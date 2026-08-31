from typing import List, Dict, Any, Tuple
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.schema.visibility import EventVisibility

class UniverseLeakageValidator:
    """
    Automated Temporal Observation Firewall validator.
    Ensures no future timestamps, latent root causes, or counterfactuals appear in observable views.
    """
    PROHIBITED_OBSERVABLE_KEYS = {
        "true_root_cause",
        "future_salary_timestamp",
        "next_liquidity_window",
        "counterfactual_outcomes",
        "eventual_payment",
        "eventual_recovery_amount",
        "natural_recovery_timestamp",
        "oracle_optimal_action"
    }

    @classmethod
    def validate_event_stream(
        cls,
        events: List[UnifiedTemporalEvent],
        evaluation_timestamp: int
    ) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        for e in events:
            if e.visibility == EventVisibility.OBSERVABLE:
                if e.timestamp > evaluation_timestamp:
                    errors.append(f"Temporal Leakage: Observable event {e.event_id} has future timestamp {e.timestamp} > {evaluation_timestamp}")
                
                for k in cls.PROHIBITED_OBSERVABLE_KEYS:
                    if k in e.payload:
                        errors.append(f"Data Leakage: Observable event {e.event_id} contains forbidden oracle key '{k}'")

        return len(errors) == 0, errors
