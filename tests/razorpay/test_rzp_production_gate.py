import pytest
from backend.safety.razorpay_guard import razorpay_guard

@pytest.mark.fixture
def test_razorpay_production_gate_fail_closed():
    ok, reason = razorpay_guard.validate_execution(is_live_attempt=True)
    assert ok is False
    assert "DISABLED" in reason
