import pytest
from simulator.clock import clock
from synthetic_payment_universe.world.chaos_engine import universe_chaos_engine
from backend.payment_intelligence.rail_health import rail_health_engine

def test_chaos_scheduling_and_application():
    universe_chaos_engine.reset()
    rail_health_engine.reset()
    clock.reset(1760000000)

    # Schedule degradation at T+2h (1760007200)
    c_evt = universe_chaos_engine.schedule_gateway_chaos(
        gateway_id="GATEWAY_A",
        degraded_health=0.10,
        scheduled_timestamp=1760007200
    )
    assert c_evt.applied is False

    # Advance clock to T+1h -> not applied yet
    universe_chaos_engine.apply_pending_chaos(1760003600)
    assert c_evt.applied is False
    assert rail_health_engine.get_gateway_health("GATEWAY_A").success_probability > 0.80

    # Advance clock to T+2h -> applied
    universe_chaos_engine.apply_pending_chaos(1760007200)
    assert c_evt.applied is True
    assert rail_health_engine.get_gateway_health("GATEWAY_A").success_probability <= 0.10
