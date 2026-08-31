import pytest
from simulator.clock import clock
from synthetic_payment_universe.world.action_api import universe_action_api

def test_universe_action_execution_api():
    clock.reset(1760000000)

    # Valid action
    success, res = universe_action_api.execute_action(
        customer_id="c_act_test",
        payment_id="p_act_test",
        action_type="RETRY_GATEWAY_A"
    )
    assert success is True
    assert res["status"] == "EXECUTED"

    # Unauthorized action
    success_bad, res_bad = universe_action_api.execute_action(
        customer_id="c_act_test",
        payment_id="p_act_test",
        action_type="UNAUTHORIZED_ACTION"
    )
    assert success_bad is False
    assert res_bad["status"] == "REJECTED_BY_GUARD"
