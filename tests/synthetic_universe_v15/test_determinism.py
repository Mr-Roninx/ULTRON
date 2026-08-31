import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_identical_seed_determinism(tmp_path):
    w1 = create_adversarial_world(master_seed=777, profile_name="tiny", storage_dir=str(tmp_path / "w1"))
    w2 = create_adversarial_world(master_seed=777, profile_name="tiny", storage_dir=str(tmp_path / "w2"))
    assert len(w1.customers) == len(w2.customers)
    assert len(w1.payments) == len(w2.payments)
