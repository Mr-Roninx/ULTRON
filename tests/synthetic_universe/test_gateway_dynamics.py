import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.gateway_gen import GatewayRailGenerator

def test_gateway_dynamic_fluctuations():
    mgr = MasterSeedManager(100)
    gw_gen = GatewayRailGenerator(mgr)

    # Initial state
    assert gw_gen.gateways["GATEWAY_A"].current_health > 0.90

    # Evolve through 20 steps
    all_events = []
    for step in range(20):
        evts = gw_gen.evolve_gateway_health(timestamp=1760000000 + (step * 3600), step_index=step)
        all_events.extend(evts)

    # Verify that health changes produce GatewayEvents
    assert len(all_events) > 0
    assert any(g.gateway_id == "GATEWAY_A" for g in all_events)
