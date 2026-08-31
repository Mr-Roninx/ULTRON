import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world
from synthetic_payment_universe.world_v12.generator.world_generator import WorldDataPopulator

def test_identical_seed_reproducibility(tmp_path):
    w1 = create_world(master_seed=12345, profile=WorldProfile.TINY, storage_dir=str(tmp_path / "w1"))
    w2 = create_world(master_seed=12345, profile=WorldProfile.TINY, storage_dir=str(tmp_path / "w2"))

    pop1 = WorldDataPopulator(w1)
    pop2 = WorldDataPopulator(w2)

    s1 = pop1.populate()
    s2 = pop2.populate()

    assert s1["payments"] == s2["payments"]
    assert s1["customers"] == s2["customers"]
