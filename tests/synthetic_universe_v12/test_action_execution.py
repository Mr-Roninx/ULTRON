import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world

def test_action_execution_via_registry(tmp_path):
    w = create_world(master_seed=456, profile=WorldProfile.TINY, storage_dir=str(tmp_path))

    # Valid action
    success, res = w.execute_action(customer_id="c_1", payment_id="p_1", action_type="RETRY_GATEWAY_B")
    assert success is True
    assert res["status"] == "EXECUTED"

    # Unauthorized action rejected
    success_bad, res_bad = w.execute_action(customer_id="c_1", payment_id="p_1", action_type="UNAUTHORIZED_ACTION")
    assert success_bad is False
    assert res_bad["status"] == "REJECTED_BY_GUARD"
