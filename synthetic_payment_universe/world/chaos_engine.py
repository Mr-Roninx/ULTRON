from typing import Dict, Any, List, Optional
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import ChaosEvent
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.schema.visibility import EventVisibility
from synthetic_payment_universe.world.temporal_engine import temporal_world_engine
from backend.payment_intelligence.rail_health import rail_health_engine

class UniverseChaosEngine:
    """
    Simulates mid-flight environmental turbulence.
    Schedules future chaos perturbations into the temporal queue.
    """
    def __init__(self):
        self.scheduled_chaos: List[ChaosEvent] = []

    def schedule_gateway_chaos(
        self,
        gateway_id: str,
        degraded_health: float,
        scheduled_timestamp: int,
        duration_seconds: int = 7200
    ) -> ChaosEvent:
        cid = f"chaos_gw_{gateway_id}_{scheduled_timestamp}"
        chaos_evt = ChaosEvent(
            chaos_id=cid,
            target_entity=gateway_id,
            perturbation_type="GATEWAY_DEGRADATION",
            scheduled_timestamp=scheduled_timestamp,
            duration_seconds=duration_seconds,
            parameters={"degraded_health": degraded_health, "latency_ms": 4500.0}
        )
        self.scheduled_chaos.append(chaos_evt)

        # Enqueue hidden future event in temporal engine
        temporal_event = UnifiedTemporalEvent(
            event_id=cid,
            event_type="CHAOS_GATEWAY_DEGRADATION",
            entity_id=gateway_id,
            timestamp=scheduled_timestamp,
            source="CHAOS_ENGINE",
            visibility=EventVisibility.HIDDEN,
            payload=chaos_evt.model_dump()
        )
        temporal_world_engine.schedule_event(temporal_event)
        return chaos_evt

    def apply_pending_chaos(self, current_time: int):
        for c in self.scheduled_chaos:
            if not c.applied and c.scheduled_timestamp <= current_time:
                c.applied = True
                if c.perturbation_type == "GATEWAY_DEGRADATION":
                    rail_health_engine.update_gateway_health(
                        gateway_id=c.target_entity,
                        success_probability=c.parameters.get("degraded_health", 0.10),
                        latency_ms=c.parameters.get("latency_ms", 4500.0)
                    )

    def reset(self):
        self.scheduled_chaos.clear()

universe_chaos_engine = UniverseChaosEngine()
