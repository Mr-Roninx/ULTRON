import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_world_health_status(tmp_path):
    w = create_emergent_population_world(master_seed=404, profile_name="tiny", storage_dir=str(tmp_path))
    assert w.ledger.verify_ledger_balance() is True
    assert w.event_queue.size() > 0
    assert len(w.gateway_engine.gateways) == 4
