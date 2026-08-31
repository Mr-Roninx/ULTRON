import pytest
from backend.evidence.razorpay_config_truth import razorpay_config_inspector

@pytest.mark.fixture
def test_razorpay_config_safe_metadata():
    report = razorpay_config_inspector.inspect()
    assert report["provider"] == "razorpay"
    assert report["environment"] == "TEST"
    assert "key_id_present" in report
    assert "key_secret_present" in report
    assert "webhook_secret_present" in report
