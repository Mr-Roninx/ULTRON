import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_adversarial_event_stream(tmp_path):
    w = create_adversarial_world(master_seed=321, profile_name="tiny", storage_dir=str(tmp_path))
    events = list(w.repository.get_events_stream(1760000000))
    assert isinstance(events, list)
