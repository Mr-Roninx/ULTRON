import pytest
from backend.integrations.webhooks.normalizer import canonical_normalizer

@pytest.mark.fixture
def test_canonical_event_mapping_accuracy():
    payload = {
        "event": "payment.failed",
        "event_id": "evt_norm_101",
        "payload": {
            "payment": {
                "entity": {"id": "pay_test_001", "amount": 2470000}
            }
        }
    }
    evt = canonical_normalizer.normalize("razorpay", payload)
    assert evt.event_type == "PAYMENT_FAILED"
    assert evt.provider == "razorpay"
    assert evt.provider_payment_id == "pay_test_001"
