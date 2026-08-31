import pytest
from backend.safety.production_gate import production_gate, EnvironmentMode

@pytest.mark.fixture
def test_environment_guard_fails_closed():
    # Attempting to execute live transaction without production credentials/mode
    ok, reason = production_gate.validate_execution(
        provider="razorpay",
        action_type="SEND_PAYMENT_LINK",
        amount_minor=2470000,
        is_live_request=True
    )
    assert ok is False
    assert "strictly DISABLED" in reason
