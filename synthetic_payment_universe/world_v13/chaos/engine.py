from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from synthetic_payment_universe.world_v13.economy.gateway_economy import GatewayEconomyEngine

class ScheduledChaosV13(BaseModel):
    chaos_id: str
    chaos_type: str # GATEWAY_DEGRADATION, OUTAGE, WEBHOOK_DELAY, LIQUIDITY_SHOCK, VOLUME_SPIKE
    target_entity: str
    scheduled_timestamp: int
    payload: Dict[str, Any] = Field(default_factory=dict)
    applied: bool = False

class CivilizationChaosEngine:
    """
    Schedules and injects environmental chaos into the persistent economic world.
    """
    def __init__(self, gateway_economy: GatewayEconomyEngine):
        self.gateway_economy = gateway_economy
        self.scheduled_events: List[ScheduledChaosV13] = []

    def schedule_chaos(
        self,
        chaos_id: str,
        chaos_type: str,
        target_entity: str,
        scheduled_timestamp: int,
        payload: Optional[Dict[str, Any]] = None
    ) -> ScheduledChaosV13:
        c = ScheduledChaosV13(
            chaos_id=chaos_id,
            chaos_type=chaos_type,
            target_entity=target_entity,
            scheduled_timestamp=scheduled_timestamp,
            payload=payload or {}
        )
        self.scheduled_events.append(c)
        return c

    def apply_pending_chaos(self, current_timestamp: int) -> List[ScheduledChaosV13]:
        applied = []
        for c in self.scheduled_events:
            if not c.applied and c.scheduled_timestamp <= current_timestamp:
                if c.chaos_type in ["GATEWAY_DEGRADATION", "OUTAGE"] and c.target_entity in self.gateway_economy.gateways:
                    gw = self.gateway_economy.gateways[c.target_entity]
                    gw.health_score = c.payload.get("degraded_health", 0.10)
                    gw.latency_ms = c.payload.get("latency_ms", 3500.0)
                    gw.state_regime = "DEGRADING" if c.chaos_type == "GATEWAY_DEGRADATION" else "OUTAGE"
                c.applied = True
                applied.append(c)
        return applied
