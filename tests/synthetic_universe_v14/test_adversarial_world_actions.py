import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_adversarial_sql_injection_blocked(tmp_path):
    w = create_emergent_population_world(master_seed=808, profile_name="tiny", storage_dir=str(tmp_path))
    malicious = "'; DROP TABLE ledger_entries; --"
    success, res = w.execute_agent_action("c_v14_000000", "pmt_v14_000000_01", malicious)
    assert success is False
    assert res["status"] == "REJECTED_BY_GUARD"
