import random
from typing import Dict, Any
from backend.payment_intelligence.schemas import RailHealthStatus
from backend.payment_intelligence.rail_health import rail_health_engine

class GatewayBehaviorSimulator:
    """
    Models realistic gateway dynamics: latency variations, intermittent timeouts,
    webhook delays, and recovery curves.
    """
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def reseed(self, seed: int):
        self.rng = random.Random(seed)

    def simulate_gateway_interaction(self, gateway_id: str) -> Dict[str, Any]:
        gw_state = rail_health_engine.get_gateway_health(gateway_id)
        
        # Base latency with jitter
        base_latency = gw_state.latency_ms
        jitter = self.rng.uniform(-30.0, 50.0)
        actual_latency = max(50.0, base_latency + jitter)

        # Timeout roll
        timed_out = self.rng.random() < gw_state.timeout_rate

        # Webhook delay (seconds)
        if gw_state.status == RailHealthStatus.HEALTHY:
            webhook_delay_sec = self.rng.uniform(1.0, 5.0)
        elif gw_state.status == RailHealthStatus.DEGRADED:
            webhook_delay_sec = self.rng.uniform(15.0, 120.0)
        else: # DOWN
            webhook_delay_sec = self.rng.uniform(300.0, 3600.0)

        return {
            "gateway_id": gateway_id,
            "status": gw_state.status.value,
            "latency_ms": round(actual_latency, 2),
            "timed_out": timed_out,
            "webhook_delay_seconds": round(webhook_delay_sec, 2),
            "success_probability": gw_state.success_probability
        }

gateway_behavior_simulator = GatewayBehaviorSimulator()
