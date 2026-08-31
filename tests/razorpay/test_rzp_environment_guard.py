import pytest
from backend.safety.razorpay_guard import razorpay_guard

@pytest.mark.fixture
def test_razorpay_environment_guard_blocks_live():
    ok, reason = razorpay_guard.validate_execution(is_live_attempt=True)
    assert ok is False
    assert "strictly DISABLED" in reason

    ok_test, _ = razorpay_guard.validate_execution(is_live_attempt=False)
    assert ok_test is True
