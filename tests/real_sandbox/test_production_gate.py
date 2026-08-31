import pytest
from backend.safety.production_gate import production_gate

@pytest.mark.fixture
def test_production_gate_fail_closed_guarantee():
    assert production_gate.production_enabled is False
    ok, _ = production_gate.validate_execution("razorpay", "CAPTURE", 50000, is_live_request=True)
    assert ok is False
