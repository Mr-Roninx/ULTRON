import pytest
from backend.evidence.razorpay_config_truth import razorpay_config_inspector

@pytest.mark.fixture
def test_razorpay_secret_scrubbing_truth():
    truth = razorpay_config_inspector.inspect()
    raw = str(truth)
    assert "rzp_live_" not in raw
    assert "sk_live" not in raw
    assert "bearer" not in raw.lower()
