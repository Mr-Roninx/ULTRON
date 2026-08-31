import pytest
from simulator.clock import clock
from synthetic_payment_universe.generator.universe_builder import SyntheticUniverseBuilder
from synthetic_payment_universe.world.temporal_engine import temporal_world_engine
from synthetic_payment_universe.world.chaos_engine import universe_chaos_engine
from synthetic_payment_universe.world.action_api import universe_action_api
from synthetic_payment_universe.observation.observation_builder import universe_observation_api

def test_end_to_end_world_simulation_cycle():
    temporal_world_engine.reset()
    universe_chaos_engine.reset()
    universe_observation_api.reset()
    now = 1760000000
    clock.reset(now)

    # 1. Build small test partition
    builder = SyntheticUniverseBuilder(master_seed=808)
    res = builder.build_partition("dev", customer_count=5, payments_per_customer=2)
    assert res["payments_generated"] == 10

    # 2. Schedule Chaos at T+2h
    c_evt = universe_chaos_engine.schedule_gateway_chaos("GATEWAY_A", degraded_health=0.10, scheduled_timestamp=now + 7200)

    # 3. Advance clock and observe events
    processed = temporal_world_engine.advance_to(now + 7200)
    assert len(processed) > 0
    assert clock.now() == now + 7200

    # 4. Apply chaos & execute action
    universe_chaos_engine.apply_pending_chaos(now + 7200)
    assert c_evt.applied is True

    success, act_res = universe_action_api.execute_action(
        customer_id="c_synth_000000",
        payment_id="pmt_synth_000000",
        action_type="RETRY_GATEWAY_B"
    )
    assert success is True
