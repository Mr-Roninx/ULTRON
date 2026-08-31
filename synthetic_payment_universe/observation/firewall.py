from typing import Dict, Any, List
from simulator.clock import clock
from backend.benchmark.firewall import TemporalObservationFirewall, FutureInformationLeakageError
from synthetic_payment_universe.schema.visibility import VisibilityGuard, EventVisibility

class UniverseObservationFirewall:
    r"""
    Hard cryptographic/temporal boundary ensuring ULTRON receives only observable,
    strictly historical ($timestamp \le current_time$) information.
    """
    @staticmethod
    def sanitize_for_agent(payload: Dict[str, Any], current_time: int) -> Dict[str, Any]:
        # 1. Check temporal boundary on payload timestamps
        if "created_at" in payload and payload["created_at"] > current_time:
            raise FutureInformationLeakageError(f"Lookahead violation: entity created_at {payload['created_at']} > {current_time}")
        if "timestamp" in payload and payload["timestamp"] > current_time:
            raise FutureInformationLeakageError(f"Lookahead violation: entity timestamp {payload['timestamp']} > {current_time}")

        # 2. Filter hidden/evaluator-only fields
        sanitized = VisibilityGuard.filter_observable_payload(payload, current_time)

        # 3. Apply baseline TemporalObservationFirewall
        return TemporalObservationFirewall.sanitize_agent_context(sanitized)
