import uuid
from typing import Dict, Any, Tuple, Optional
from simulator.clock import clock
from backend.agent.action_registry import action_registry
from backend.safety.action_guard import action_execution_guard
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.schema.visibility import EventVisibility
from synthetic_payment_universe.world.temporal_engine import temporal_world_engine

class UniverseActionAPI:
    """
    Authoritative Action Execution Gateway for the Synthetic Universe.
    Validates permissions, enforces policy/risk guards, and schedules resulting world events.
    """
    @classmethod
    def execute_action(
        cls,
        customer_id: str,
        payment_id: str,
        action_type: str,
        segment: str = "B2B_ENTERPRISE",
        payload: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        payload = payload or {}
        now = clock.now()

        # 1. Action Registry & Safety Guard
        is_allowed, reason = action_execution_guard.validate_and_guard(
            customer_id=customer_id,
            payment_id=payment_id,
            action_type=action_type,
            segment=segment,
            payload=payload
        )
        if not is_allowed:
            return False, {"status": "REJECTED_BY_GUARD", "reason": reason, "timestamp": now}

        # 2. Schedule Event into Temporal World Engine
        evt_id = f"act_{uuid.uuid4().hex[:8]}"
        temporal_event = UnifiedTemporalEvent(
            event_id=evt_id,
            event_type=f"ACTION_EXECUTED_{action_type}",
            entity_id=payment_id,
            timestamp=now,
            source="ULTRON_AGENT",
            visibility=EventVisibility.OBSERVABLE,
            payload={
                "customer_id": customer_id,
                "payment_id": payment_id,
                "action_type": action_type,
                "payload": payload
            }
        )
        temporal_world_engine.schedule_event(temporal_event)

        return True, {
            "status": "EXECUTED",
            "action_id": evt_id,
            "action_type": action_type,
            "timestamp": now
        }

universe_action_api = UniverseActionAPI()
