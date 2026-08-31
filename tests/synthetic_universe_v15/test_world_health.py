import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_adversarial_world_health(tmp_path):
    w = create_adversarial_world(master_seed=666, profile_name="tiny", storage_dir=str(tmp_path))
    assert w.ledger.verify_ledger_balance() is True
    assert len(w.customers) == 100
    assert len(w.payments) == 100
