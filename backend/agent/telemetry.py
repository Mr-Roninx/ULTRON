from typing import Dict, Any, List, Optional
import time
from simulator.clock import clock

TELEMETRY_EVENT_TYPES = [
    "MISSION_CREATED",
    "OBSERVE",
    "INVESTIGATE",
    "DIAGNOSE",
    "LLM_REASON",
    "CANDIDATES_GENERATED",
    "FEASIBILITY_CHECK",
    "NEV_RANKING",
    "AUTHORITY_DECISION",
    "EXECUTE",
    "WAIT",
    "WAKE",
    "ENVIRONMENT_CHANGED",
    "PLAN_INVALIDATED",
    "REPLAN",
    "OUTCOME_OBSERVED",
    "PREDICTION_ERROR",
    "MEMORY_WRITE",
    "MISSION_COMPLETED",
    "ESCALATED"
]

class AgentTelemetry:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def reset(self):
        self.events.clear()

    def log_event(
        self,
        event_type: str = "GENERIC_EVENT",
        mission_id: str = "system",
        payload: Optional[Dict[str, Any]] = None,
        phase: Optional[str] = None
    ):
        # Support positional signature backwards-compatibility (mission_id, phase, payload)
        if phase is not None and payload is None and isinstance(mission_id, str):
            actual_mission_id = event_type
            actual_phase = mission_id
            actual_payload = phase
            event_type = actual_phase
            mission_id = actual_mission_id
            payload = actual_payload

        payload = payload or {}
        event = {
            "timestamp": clock.now(),
            "event_type": event_type,
            "mission_id": mission_id,
            "phase": phase or event_type,
            "payload": payload
        }
        self.events.append(event)

    def log_decision_differential(
        self,
        mission_id: str,
        llm_preferred: str,
        deterministic_selected: str,
        candidate_scores: List[Dict[str, Any]]
    ):
        differential = {
            "llm_preferred": llm_preferred,
            "deterministic_selected": deterministic_selected,
            "match": llm_preferred == deterministic_selected,
            "candidate_scores": candidate_scores
        }
        self.log_event(
            event_type="AUTHORITY_DECISION",
            mission_id=mission_id,
            payload=differential
        )

    def get_events(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if mission_id:
            return [e for e in self.events if e.get("mission_id") == mission_id]
        return list(self.events)

telemetry = AgentTelemetry()