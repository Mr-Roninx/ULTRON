import pytest
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_long_horizon_advance_30_days(tmp_path):
    w = create_economic_civilization(master_seed=789, profile_name="tiny", storage_dir=str(tmp_path))
    processed = w.advance_days(30)
    assert len(processed) > 0
    assert w.ledger.verify_ledger_balance() is True
