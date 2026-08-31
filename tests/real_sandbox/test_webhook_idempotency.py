import pytest
import time
from backend.integrations.webhooks.deduplicator import WebhookDeduplicator

@pytest.mark.fixture
def test_idempotency_prevents_duplicate_side_effects():
    dedup = WebhookDeduplicator()
    payload = b'{"event":"payment.captured","id":"evt_rzp_unique_01"}'
    now = int(time.time())

    assert dedup.is_duplicate("razorpay", "evt_rzp_unique_01", payload) is False
    rec = dedup.record_received("razorpay", "evt_rzp_unique_01", payload, now)
    assert rec.status == "VERIFIED"

    # Exact replay of same webhook
    assert dedup.is_duplicate("razorpay", "evt_rzp_unique_01", payload) is True
