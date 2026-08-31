import pytest
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_identical_seed_world_determinism(tmp_path):
    w1 = create_economic_civilization(master_seed=12345, profile_name="tiny", storage_dir=str(tmp_path / "w1"))
    w2 = create_economic_civilization(master_seed=12345, profile_name="tiny", storage_dir=str(tmp_path / "w2"))

    assert len(w1.customers) == len(w2.customers)
    assert len(w1.payments) == len(w2.payments)
