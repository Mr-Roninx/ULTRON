import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.gateway_gen import GatewayRailGenerator
from backend.payment_intelligence.rail_health import rail_health_engine

def test_gateway_health_causal_propagation():
    rail_health_engine.reset()
    mgr = MasterSeedManager(505, partition_name="chaos")
    gw_gen = GatewayRailGenerator(mgr)

    # Initial high health
    gw = gw_gen.gateways["GATEWAY_A"]
    assert gw.current_health > 0.80

    # Inject degradation and propagate to rail health engine
    gw.current_health = 0.15
    rail_health_engine.update_gateway_health("GATEWAY_A", success_probability=0.15, latency_ms=4500.0)

    tracked = rail_health_engine.get_gateway_health("GATEWAY_A")
    assert tracked.success_probability == 0.15
    assert tracked.latency_ms == 4500.0
