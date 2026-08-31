from typing import Dict, Any, List
from synthetic_payment_universe.world_v14.gateways.competitive_gateways import CompetitiveGatewayEngine

class DynamicRoutingEngine:
    """
    Evaluates optimal and secondary routing paths across competing payment gateways.
    """
    def __init__(self, gateway_engine: CompetitiveGatewayEngine):
        self.gateway_engine = gateway_engine

    def recommend_gateway(self, primary_gateway: str, failover: bool = False) -> str:
        if not failover:
            return primary_gateway
        # Select healthiest alternative
        alternatives = [gw for gid, gw in self.gateway_engine.gateways.items() if gid != primary_gateway]
        best = max(alternatives, key=lambda x: x.current_authorization_rate)
        return best.gateway_id
