from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from synthetic_payment_universe.world_v12.gateways.gateway_world import DynamicGatewayWorld

class ScheduledChaos(BaseModel):
    chaos_id: str
    chaos_type: str # GATEWAY_OUTAGE, GATEWAY_DEGRADATION, WEBHOOK_DELAY, WEBHOOK_DROP
    target_entity: str
    scheduled_timestamp: int
    payload: Dict[str, Any] = Field(default_factory=dict)
    applied: bool = False

class WorldChaosEngine:
    """
    Schedules and injects mid-flight environmental perturbations into the persistent world.
    """
    def __init__(self, gateway_world: DynamicGatewayWorld):
        self.gw_world = gateway_world
        self.pending_chaos: List[ScheduledChaos] = []

    def schedule_chaos(
        self,
        chaos_id: str,
        chaos_type: str,
        target_entity: str,
        scheduled_timestamp: int,
        payload: Optional[Dict[str, Any]] = None
    ) -> ScheduledChaos:
        c = ScheduledChaos(
            chaos_id=chaos_id,
            chaos_type=chaos_type,
            target_entity=target_entity,
            scheduled_timestamp=scheduled_timestamp,
            payload=payload or {}
        )
        self.pending_chaos.append(c)
        return c

    def apply_pending_chaos(self, current_timestamp: int) -> List[ScheduledChaos]:
        applied = []
        for c in self.pending_chaos:
            if not c.applied and c.scheduled_timestamp <= current_timestamp:
                if c.chaos_type == "GATEWAY_DEGRADATION" and c.target_entity in self.gw_world.gateways:
                    gw = self.gw_world.gateways[c.target_entity]
                    gw.regime = "DEGRADED"
                    gw.health_score = c.payload.get("degraded_health", 0.10)
                    gw.latency_ms = c.payload.get("latency_ms", 4500.0)
                c.applied = True
                applied.append(c)
        return applied
