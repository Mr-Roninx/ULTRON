import random
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class GatewayEconomyState(BaseModel):
    gateway_id: str
    health_score: float = 0.95 # [0.0, 1.0]
    latency_ms: float = 120.0
    active_load: int = 0
    max_capacity: int = 1000
    state_regime: str = "STABLE" # STABLE, DEGRADING, OUTAGE, RECOVERING, FLAPPING

class GatewayEconomyEngine:
    """
    Simulates dynamic gateway health, congestion response, and causal feedback from routing decisions.
    """
    def __init__(self, subseed: int = 12345):
        self.rng = random.Random(subseed)
        self.gateways: Dict[str, GatewayEconomyState] = {
            "GATEWAY_A": GatewayEconomyState(gateway_id="GATEWAY_A", health_score=0.96, latency_ms=90.0, max_capacity=2000),
            "GATEWAY_B": GatewayEconomyState(gateway_id="GATEWAY_B", health_score=0.92, latency_ms=150.0, max_capacity=1500),
            "GATEWAY_C": GatewayEconomyState(gateway_id="GATEWAY_C", health_score=0.88, latency_ms=220.0, max_capacity=800),
            "GATEWAY_D": GatewayEconomyState(gateway_id="GATEWAY_D", health_score=0.90, latency_ms=180.0, max_capacity=1000)
        }

    def route_traffic(self, gateway_id: str, count: int = 1):
        gw = self.gateways.get(gateway_id)
        if gw:
            gw.active_load += count
            # Congestion feedback
            if gw.active_load > gw.max_capacity:
                overload_ratio = (gw.active_load - gw.max_capacity) / gw.max_capacity
                gw.health_score = max(0.20, round(gw.health_score - (overload_ratio * 0.15), 3))
                gw.latency_ms = round(gw.latency_ms + (overload_ratio * 300.0), 1)

    def decay_load(self):
        for gw in self.gateways.values():
            gw.active_load = max(0, int(gw.active_load * 0.70))
            if gw.active_load < gw.max_capacity and gw.state_regime == "STABLE":
                # Gradually recover health towards base
                gw.health_score = min(0.96, round(gw.health_score + 0.02, 3))
                gw.latency_ms = max(90.0, round(gw.latency_ms - 10.0, 1))

    def get_gateway_health(self, gateway_id: str) -> float:
        gw = self.gateways.get(gateway_id)
        return gw.health_score if gw else 0.90
