import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_world_deterministic_state_hash(tmp_path):
    w = create_emergent_population_world(master_seed=42, profile_name="tiny", storage_dir=str(tmp_path))
    h1 = w.replay_engine.compute_state_hash(1760000000)
    h2 = w.replay_engine.compute_state_hash(1760000000)
    assert h1 == h2
    assert len(h1) == 64
