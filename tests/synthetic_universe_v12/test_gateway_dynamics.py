import pytest
from synthetic_payment_universe.world_v12.gateways.gateway_world import DynamicGatewayWorld

def test_dynamic_gateway_health_evolution():
    gw_world = DynamicGatewayWorld(subseed=777)
    initial_h = gw_world.get_gateway_health("GATEWAY_A")
    assert initial_h > 0.90

    # Evolve 50 steps
    for step in range(50):
        gw_world.evolve_gateway_states(1760000000 + (step * 3600))

    assert "GATEWAY_A" in gw_world.gateways
