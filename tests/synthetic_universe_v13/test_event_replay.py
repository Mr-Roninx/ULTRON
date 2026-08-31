import pytest
from synthetic_payment_universe.world_v13.events.event import EconomicEvent
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_event_replay_and_state_hashing(tmp_path):
    w = create_economic_civilization(master_seed=456, profile_name="tiny", storage_dir=str(tmp_path))
    h1 = w.replay_engine.compute_state_hash(1760000000)
    h2 = w.replay_engine.compute_state_hash(1760000000)
    assert h1 == h2
    assert len(h1) == 64
