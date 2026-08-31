import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world

def test_malicious_action_and_sql_injection_defense(tmp_path):
    w = create_world(master_seed=789, profile=WorldProfile.TINY, storage_dir=str(tmp_path))

    malicious_actions = [
        "DROP TABLE payments;--",
        "TRANSFER_MONEY",
        "UPDATE_BALANCE",
        "DELETE_CUSTOMER",
        "REVEAL_ORACLE_SECRETS"
    ]

    for bad_act in malicious_actions:
        success, res = w.execute_action(customer_id="c_1", payment_id="p_1", action_type=bad_act)
        assert success is False
        assert res["status"] == "REJECTED_BY_GUARD"
