import pytest
from synthetic_payment_universe.world_v13.economy.gateway_economy import GatewayEconomyEngine

def test_gateway_congestion_feedback_loop():
    engine = GatewayEconomyEngine(subseed=999)
    gw = engine.gateways["GATEWAY_A"]
    initial_h = gw.health_score

    # Heavy overload traffic
    engine.route_traffic("GATEWAY_A", count=5000)
    assert gw.health_score < initial_h
    assert gw.latency_ms > 90.0

    # Load decay -> gradual recovery
    engine.decay_load()
    assert gw.active_load < 5000
