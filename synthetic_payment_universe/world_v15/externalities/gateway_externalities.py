from typing import Dict, Any, List
from pydantic import BaseModel

class GatewayExternalityState(BaseModel):
    gateway_id: str
    capacity: int = 2000
    current_load: int = 0
    base_auth_rate: float = 0.95
    current_auth_rate: float = 0.95
    congestion_fee_cost: float = 0.0

class GatewayExternalityEngine:
    """
    Simulates shared gateway network externalities where traffic switching by one merchant induces congestion for all.
    """
    def __init__(self):
        self.gateways: Dict[str, GatewayExternalityState] = {
            "GATEWAY_A": GatewayExternalityState(gateway_id="GATEWAY_A", capacity=2500, base_auth_rate=0.96, current_auth_rate=0.96),
            "GATEWAY_B": GatewayExternalityState(gateway_id="GATEWAY_B", capacity=1800, base_auth_rate=0.92, current_auth_rate=0.92),
            "GATEWAY_C": GatewayExternalityState(gateway_id="GATEWAY_C", capacity=1200, base_auth_rate=0.88, current_auth_rate=0.88),
            "GATEWAY_D": GatewayExternalityState(gateway_id="GATEWAY_D", capacity=1000, base_auth_rate=0.90, current_auth_rate=0.90)
        }

    def add_traffic(self, gateway_id: str, count: int = 1) -> float:
        gw = self.gateways.get(gateway_id)
        if not gw:
            return 0.0
        gw.current_load += count
        externality_cost = 0.0

        if gw.current_load > gw.capacity:
            overload = (gw.current_load - gw.capacity) / gw.capacity
            gw.current_auth_rate = max(0.20, round(gw.base_auth_rate - (overload * 0.22), 3))
            # External penalty imposed on the wider network
            externality_cost = round(overload * 250.0, 2)
            gw.congestion_fee_cost += externality_cost

        return externality_cost

    def reset_load(self):
        for gw in self.gateways.values():
            gw.current_load = 0
            gw.current_auth_rate = gw.base_auth_rate
