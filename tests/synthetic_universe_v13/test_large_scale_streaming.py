import pytest
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_large_scale_batch_creation(tmp_path):
    w = create_economic_civilization(master_seed=999, profile_name="tiny", storage_dir=str(tmp_path))
    assert len(w.customers) == 100
    assert len(w.payments) == 100
    assert w.ledger.verify_ledger_balance() is True
