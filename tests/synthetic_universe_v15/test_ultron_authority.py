import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_ultron_authority_fail_closed(tmp_path):
    w = create_adversarial_world(master_seed=555, profile_name="tiny", storage_dir=str(tmp_path))
    # Direct balance mutation is rejected
    ok, res = w.execute_agent_action("c_v15_000000", "pmt_v15_000000_01", "SET_BALANCE_1000000")
    assert ok is False
    assert res["status"] == "REJECTED_BY_GUARD"
