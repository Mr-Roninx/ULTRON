import pytest
from backend.safety.production_gate import production_gate

@pytest.mark.fixture
def test_production_gate_fail_closed():
    assert production_gate.production_enabled is False
    ok, reason = production_gate.validate_execution("razorpay", "REFUND", 100000, is_live_request=True)
    assert ok is False
    assert "strictly DISABLED" in reason
