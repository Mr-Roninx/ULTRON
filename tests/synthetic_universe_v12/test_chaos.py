import pytest
from synthetic_payment_universe.world_v12.gateways.gateway_world import DynamicGatewayWorld
from synthetic_payment_universe.world_v12.gateways.chaos_engine import WorldChaosEngine

def test_chaos_scheduling_and_trigger():
    gw_world = DynamicGatewayWorld(subseed=888)
    chaos_eng = WorldChaosEngine(gw_world)

    c = chaos_eng.schedule_chaos(
        chaos_id="chaos_1",
        chaos_type="GATEWAY_DEGRADATION",
        target_entity="GATEWAY_A",
        scheduled_timestamp=1760007200,
        payload={"degraded_health": 0.10, "latency_ms": 4000.0}
    )
    assert c.applied is False

    # Apply before scheduled time -> No effect
    applied_early = chaos_eng.apply_pending_chaos(1760003600)
    assert len(applied_early) == 0
    assert gw_world.get_gateway_health("GATEWAY_A") > 0.80

    # Apply at scheduled time -> Applied
    applied_time = chaos_eng.apply_pending_chaos(1760007200)
    assert len(applied_time) == 1
    assert gw_world.get_gateway_health("GATEWAY_A") <= 0.10
