import random
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class GatewayState(BaseModel):
    gateway_id: str
    regime: str = "STABLE" # STABLE, DEGRADING, DEGRADED, RECOVERING, FLAPPING, OUTAGE, LATENCY_SPIKE
    health_score: float = 0.95
    latency_ms: float = 120.0
    failure_rate: float = 0.05
    last_updated: int = 1760000000

class DynamicGatewayWorld:
    """
    Simulates dynamic gateway and rail health state transitions across temporal progression.
    """
    def __init__(self, subseed: int = 12345):
        self.rng = random.Random(subseed)
        self.gateways: Dict[str, GatewayState] = {
            "GATEWAY_A": GatewayState(gateway_id="GATEWAY_A", health_score=0.96, latency_ms=110.0),
            "GATEWAY_B": GatewayState(gateway_id="GATEWAY_B", health_score=0.94, latency_ms=140.0),
            "GATEWAY_C": GatewayState(gateway_id="GATEWAY_C", health_score=0.92, latency_ms=180.0),
            "GATEWAY_D": GatewayState(gateway_id="GATEWAY_D", health_score=0.95, latency_ms=130.0)
        }

    def get_gateway_health(self, gateway_id: str) -> float:
        gw = self.gateways.get(gateway_id)
        return gw.health_score if gw else 0.90

    def evolve_gateway_states(self, timestamp: int):
        for gw in self.gateways.values():
            roll = self.rng.random()
            if gw.regime == "STABLE":
                if roll < 0.03:
                    gw.regime = "DEGRADING"
                    gw.health_score = max(0.20, gw.health_score - 0.40)
                    gw.latency_ms = 1500.0
            elif gw.regime == "DEGRADING":
                if roll < 0.30:
                    gw.regime = "DEGRADED"
                    gw.health_score = 0.10
                elif roll < 0.60:
                    gw.regime = "RECOVERING"
                    gw.health_score = 0.80
            elif gw.regime == "DEGRADED":
                if roll < 0.40:
                    gw.regime = "RECOVERING"
                    gw.health_score = 0.75
            elif gw.regime == "RECOVERING":
                gw.regime = "STABLE"
                gw.health_score = 0.95
                gw.latency_ms = 120.0
            gw.last_updated = timestamp
