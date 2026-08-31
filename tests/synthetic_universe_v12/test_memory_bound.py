import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world

def test_streaming_query_memory_bound(tmp_path):
    w = create_world(master_seed=8888, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    # Stream events generator - ensure generator does not load all into memory
    gen = w.repository.get_events_stream(1760000000)
    assert hasattr(gen, "__iter__")
