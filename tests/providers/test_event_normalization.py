import pytest
from backend.integrations.webhooks.normalizer import canonical_normalizer

def test_canonical_event_normalization():
    rzp_raw = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {"id": "pay_failed_123", "amount": 2470000}
            }
        }
    }
    evt = canonical_normalizer.normalize("razorpay", rzp_raw)
    assert evt.event_type == "PAYMENT_FAILED"
    assert evt.provider == "razorpay"
    assert evt.provider_payment_id == "pay_failed_123"
