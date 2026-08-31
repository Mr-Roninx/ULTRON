import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world
from synthetic_payment_universe.world_v12.temporal.priority_queue import WorldEvent

def test_temporal_event_scheduling_and_dispatch(tmp_path):
    world = create_world(master_seed=101, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    start_t = world.identity.simulation_start

    e1 = WorldEvent(event_id="e_test_1", event_type="PAYMENT_FAILED", entity_id="p_1", timestamp=start_t + 100)
    e2 = WorldEvent(event_id="e_test_2", event_type="PAYMENT_RECOVERED", entity_id="p_1", timestamp=start_t + 500)

    world.schedule_event(e1)
    world.schedule_event(e2)

    processed = world.advance_to(start_t + 200)
    assert len(processed) == 1
    assert processed[0].event_id == "e_test_1"
    assert world.identity.current_time == start_t + 200
