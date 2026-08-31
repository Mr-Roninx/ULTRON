import pytest
from backend.evidence.real_to_swu import real_to_swu_converter
from backend.providers.models import CanonicalPaymentEvent

@pytest.mark.fixture
def test_real_event_to_swu_fixture_conversion():
    evt = CanonicalPaymentEvent(
        event_id="evt_real_test_101",
        provider="razorpay",
        provider_event_id="pay_failed_rzp_99",
        event_type="PAYMENT_FAILED",
        timestamp=1760000000,
        payload={"amount": 2470000}
    )
    fix = real_to_swu_converter.convert_event_to_fixture(evt)
    assert fix["source_provider"] == "razorpay"
    assert fix["canonical_event_type"] == "PAYMENT_FAILED"
    assert fix["is_sanitized"] is True
