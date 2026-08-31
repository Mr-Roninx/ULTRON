import pytest
from backend.safety.production_gate import production_gate, EnvironmentMode

def test_production_gate_fails_closed():
    # Production live transactions are strictly blocked by default
    ok, reason = production_gate.validate_execution(
        provider="razorpay",
        action_type="SEND_PAYMENT_LINK",
        amount_minor=2470000,
        is_live_request=True
    )
    assert ok is False
    assert "strictly DISABLED" in reason

    # Test kill switch
    production_gate.activate_kill_switch()
    ok_kill, reason_kill = production_gate.validate_execution("razorpay", "SEND_PAYMENT_LINK", 2470000)
    assert ok_kill is False
    assert "kill switch is ACTIVE" in reason_kill
    production_gate.clear_kill_switch()
