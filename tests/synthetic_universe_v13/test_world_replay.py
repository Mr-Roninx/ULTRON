import pytest
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_world_replay_stream(tmp_path):
    w = create_economic_civilization(master_seed=555, profile_name="tiny", storage_dir=str(tmp_path))
    events = w.replay_engine.replay_to(1760000000)
    assert len(events) > 0
