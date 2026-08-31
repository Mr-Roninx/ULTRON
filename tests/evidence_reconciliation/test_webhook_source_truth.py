import pytest
from backend.providers.models import CanonicalPaymentEvent

@pytest.mark.fixture
def test_webhook_source_classification():
    evt = CanonicalPaymentEvent(
        event_id="evt_test_source_01",
        provider="razorpay",
        provider_event_id="pay_rzp_source_01",
        event_type="PAYMENT_SUCCEEDED",
        timestamp=1760000000,
        payload={"amount": 2470000},
        raw_event_type="payment.captured",
        signature_verified=True
    )
    assert evt.signature_verified is True
    assert evt.provider == "razorpay"
