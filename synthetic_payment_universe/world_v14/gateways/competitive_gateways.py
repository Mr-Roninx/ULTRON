from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class CompetitiveGateway(BaseModel):
    gateway_id: str
    base_authorization_rate: float = 0.95
    current_authorization_rate: float = 0.95
    latency_ms: float = 90.0
    active_load: int = 0
    max_capacity: int = 2000
    fee_bps: float = 150.0 # 1.5%

class CompetitiveGatewayEngine:
    """
    Simulates gateway competition, capacity limits, and traffic-induced congestion.
    """
    def __init__(self):
        self.gateways: Dict[str, CompetitiveGateway] = {
            "GATEWAY_A": CompetitiveGateway(gateway_id="GATEWAY_A", base_authorization_rate=0.96, latency_ms=85.0, max_capacity=2500, fee_bps=150.0),
            "GATEWAY_B": CompetitiveGateway(gateway_id="GATEWAY_B", base_authorization_rate=0.92, latency_ms=140.0, max_capacity=1800, fee_bps=135.0),
            "GATEWAY_C": CompetitiveGateway(gateway_id="GATEWAY_C", base_authorization_rate=0.88, latency_ms=210.0, max_capacity=1200, fee_bps=110.0),
            "GATEWAY_D": CompetitiveGateway(gateway_id="GATEWAY_D", base_authorization_rate=0.90, latency_ms=175.0, max_capacity=1000, fee_bps=125.0)
        }

    def route_transaction(self, gateway_id: str, count: int = 1):
        gw = self.gateways.get(gateway_id)
        if gw:
            gw.active_load += count
            if gw.active_load > gw.max_capacity:
                overload = (gw.active_load - gw.max_capacity) / gw.max_capacity
                gw.current_authorization_rate = max(0.20, round(gw.base_authorization_rate - (overload * 0.20), 3))
                gw.latency_ms = round(gw.latency_ms + (overload * 250.0), 1)

    def decay_traffic(self):
        for gw in self.gateways.values():
            gw.active_load = max(0, int(gw.active_load * 0.65))
            if gw.active_load <= gw.max_capacity:
                gw.current_authorization_rate = min(gw.base_authorization_rate, round(gw.current_authorization_rate + 0.02, 3))
                gw.latency_ms = max(85.0, round(gw.latency_ms - 15.0, 1))
