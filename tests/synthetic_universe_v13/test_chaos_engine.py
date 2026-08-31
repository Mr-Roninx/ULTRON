import pytest
from synthetic_payment_universe.world_v13.economy.gateway_economy import GatewayEconomyEngine
from synthetic_payment_universe.world_v13.chaos.engine import CivilizationChaosEngine

def test_chaos_scheduling_and_trigger():
    gw_econ = GatewayEconomyEngine(subseed=123)
    chaos = CivilizationChaosEngine(gw_econ)

    chaos.schedule_chaos(
        chaos_id="chaos_1",
        chaos_type="GATEWAY_DEGRADATION",
        target_entity="GATEWAY_A",
        scheduled_timestamp=1760007200,
        payload={"degraded_health": 0.08, "latency_ms": 4000.0}
    )

    # Before scheduled time
    applied_early = chaos.apply_pending_chaos(1760003600)
    assert len(applied_early) == 0
    assert gw_econ.get_gateway_health("GATEWAY_A") > 0.90

    # At scheduled time
    applied_now = chaos.apply_pending_chaos(1760007200)
    assert len(applied_now) == 1
    assert gw_econ.get_gateway_health("GATEWAY_A") == 0.08
