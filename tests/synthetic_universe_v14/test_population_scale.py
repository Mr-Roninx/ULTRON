import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_population_scale_entities(tmp_path):
    w = create_emergent_population_world(master_seed=101, profile_name="tiny", storage_dir=str(tmp_path))
    assert len(w.customers) == 100
    assert len(w.merchants) == 10
    assert len(w.relationships) == 100
