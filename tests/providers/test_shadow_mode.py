import pytest
from backend.safety.production_gate import production_gate, EnvironmentMode

def test_shadow_mode_blocks_financial_execution():
    production_gate.set_environment(EnvironmentMode.SHADOW)
    ok, reason = production_gate.validate_execution(
        provider="razorpay",
        action_type="SEND_PAYMENT_LINK",
        amount_minor=2470000
    )
    assert ok is False
    assert "Running in SHADOW mode" in reason
    production_gate.set_environment(EnvironmentMode.SWU)
