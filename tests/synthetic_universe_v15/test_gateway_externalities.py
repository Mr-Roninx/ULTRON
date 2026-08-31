import pytest
from synthetic_payment_universe.world_v15.externalities.gateway_externalities import GatewayExternalityEngine

def test_gateway_externality_congestion_cost():
    engine = GatewayExternalityEngine()
    # Add traffic within capacity
    cost_low = engine.add_traffic("GATEWAY_B", count=1000)
    assert cost_low == 0.0
    assert engine.gateways["GATEWAY_B"].current_auth_rate == 0.92

    # Add traffic exceeding capacity -> external congestion cost
    cost_high = engine.add_traffic("GATEWAY_B", count=1500)
    assert cost_high > 0.0
    assert engine.gateways["GATEWAY_B"].current_auth_rate < 0.92
