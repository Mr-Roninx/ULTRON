import pytest
from backend.safety.kill_switch import kill_switch_controller
from backend.safety.action_guard import action_execution_guard

def test_kill_switch_blocking():
    kill_switch_controller.reset()
    
    # Normally allowed
    allowed, _ = action_execution_guard.validate_and_guard(
        customer_id="c_ks_1", payment_id="p_ks_1", action_type="RETRY_GATEWAY_A"
    )
    assert allowed is True

    # Activate Global Kill Switch
    kill_switch_controller.activate_global()
    allowed_blocked, reason = action_execution_guard.validate_and_guard(
        customer_id="c_ks_1", payment_id="p_ks_1", action_type="RETRY_GATEWAY_A"
    )
    assert allowed_blocked is False
    assert "KILL_SWITCH" in reason

    # Deactivate Global, isolate single customer
    kill_switch_controller.deactivate_global()
    kill_switch_controller.disable_customer("c_ks_1")
    allowed_cust, reason_cust = action_execution_guard.validate_and_guard(
        customer_id="c_ks_1", payment_id="p_ks_1", action_type="RETRY_GATEWAY_A"
    )
    assert allowed_cust is False
