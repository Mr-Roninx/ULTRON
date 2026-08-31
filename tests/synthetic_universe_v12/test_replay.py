import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world
from synthetic_payment_universe.world_v12.temporal.priority_queue import WorldEvent

def test_world_replay_engine(tmp_path):
    w = create_world(master_seed=444, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    start_t = w.identity.simulation_start

    w.schedule_event(WorldEvent(event_id="e_r_1", event_type="PAYMENT_FAILED", entity_id="p_1", timestamp=start_t + 100))
    w.schedule_event(WorldEvent(event_id="e_r_2", event_type="PAYMENT_RETRY", entity_id="p_1", timestamp=start_t + 200))
    w.advance_to(start_t + 300)

    replayed = w.replay_to(start_t + 300)
    assert len(replayed) >= 2
    assert replayed[0]["event_id"] == "e_r_1"
    assert replayed[1]["event_id"] == "e_r_2"
