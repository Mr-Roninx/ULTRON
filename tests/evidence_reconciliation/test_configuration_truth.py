import pytest
from backend.evidence.config_truth import config_truth_reporter

@pytest.mark.fixture
def test_configuration_truth_reports_safe_metadata_only():
    truth = config_truth_reporter.get_truth()
    assert "hf_token_present" in truth
    assert "providers" in truth
    assert "razorpay" in truth["providers"]

    # Invariants: Zero secrets or tokens in report
    raw_str = str(truth)
    assert "sk_live" not in raw_str
    assert "rzp_live" not in raw_str
    assert "bearer" not in raw_str.lower()
