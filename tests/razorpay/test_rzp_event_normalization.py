import pytest
from backend.integrations.webhooks.normalizer import canonical_normalizer

@pytest.mark.fixture
def test_razorpay_event_normalization():
    raw = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {"id": "pay_fail_01", "amount": 2470000}
            }
        }
    }
    evt = canonical_normalizer.normalize("razorpay", raw)
    assert evt.event_type == "PAYMENT_FAILED"
    assert evt.provider_payment_id == "pay_fail_01"
