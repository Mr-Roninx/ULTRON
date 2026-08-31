import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_long_horizon_30_days_advance(tmp_path):
    w = create_emergent_population_world(master_seed=505, profile_name="tiny", storage_dir=str(tmp_path))
    processed = w.advance_days(30)
    assert len(processed) > 0
    assert w.ledger.verify_ledger_balance() is True
