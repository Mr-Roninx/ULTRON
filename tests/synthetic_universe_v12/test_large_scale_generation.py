import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world
from synthetic_payment_universe.world_v12.generator.world_generator import WorldDataPopulator

def test_chunked_batch_generation(tmp_path):
    w = create_world(master_seed=7777, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    pop = WorldDataPopulator(w)
    stats = pop.populate()

    assert stats["customers"] == 100
    assert stats["payments"] == 1000
    assert stats["ledger_balanced"] is True
