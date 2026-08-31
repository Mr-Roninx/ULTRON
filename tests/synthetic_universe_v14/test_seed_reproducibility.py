import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_identical_seed_reproducibility(tmp_path):
    w1 = create_emergent_population_world(master_seed=12345, profile_name="tiny", storage_dir=str(tmp_path / "w1"))
    w2 = create_emergent_population_world(master_seed=12345, profile_name="tiny", storage_dir=str(tmp_path / "w2"))

    assert len(w1.customers) == len(w2.customers)
    assert len(w1.merchants) == len(w2.merchants)

    h1 = w1.replay_engine.compute_state_hash(1760000000)
    h2 = w2.replay_engine.compute_state_hash(1760000000)
    assert h1 == h2
